"""Orquestra um turno: guardrail de entrada -> chain LCEL com memória -> guardrail de saída."""
import time
import warnings
from dataclasses import asdict, dataclass, field
from typing import Optional

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import ValidationError

from src import config
from src.chain.builder import build_chat_chain, build_consulta_chain, build_llm, montar_prompt
from src.chain.memoria import MemoriaSessoes
from src.guardrails import validar_entrada, verificar_saida
from src.tokens import contar, contar_mensagens


@dataclass
class Resultado:
    pergunta: str
    resposta: str
    bloqueado: bool = False
    categoria_bloqueio: Optional[str] = None  
    ajustes: list = field(default_factory=list)  
    latencia_s: float = 0.0
    tokens_prompt: int = 0                  
    fonte_tokens: str = "guardrail"
    tokens_prompt_est: int = 0              
    tokens_resposta_est: int = 0
    historico_msgs: int = 0
    historico_tokens: int = 0
    extra_1: any = None  # Campo extra para alinhar a contagem
    extra_2: any = None  # Campo extra para alinhar a contagem

    def dict(self):
        return asdict(self)
    

class ChatEV:
    def __init__(self, versao="v3", provider="ollama", model=None, llm=None, llm_json=None,
                 max_tokens_historico=None, **params):
        self.versao, self.provider, self.model, self.params = versao, provider, model, params
        self.llm = llm or build_llm(provider, model, **params)
        self._llm_json = llm_json
        self.prompt = montar_prompt(versao)
        self.memoria = MemoriaSessoes(self.llm, max_tokens_historico or config.MAX_TOKENS_HISTORICO)
        base = build_chat_chain(self.llm, versao, prompt=self.prompt).with_retry(stop_after_attempt=3)
        with warnings.catch_warnings(): 
            warnings.simplefilter("ignore")
            self.chain = RunnableWithMessageHistory(
                base, self.memoria.get_history, input_messages_key="pergunta", history_messages_key="history"
            )
        self._chain_consulta = None

    # -- chat com memória ---------------------------------------------------------------------
    def perguntar(self, texto: str, session_id: str = "default") -> Resultado:
        t0 = time.perf_counter()
        entrada = validar_entrada(texto)
        if not entrada.permitido:
            # Bloqueios NÃO entram na memória: evita "envenenar" o histórico com a tentativa de injeção.
            return Resultado(texto, entrada.resposta, True, entrada.categoria,
                             latencia_s=time.perf_counter() - t0,
                             historico_msgs=len(self.memoria.mensagens(session_id)),
                             historico_tokens=self.memoria.tokens(session_id))

        hist_antes = self.memoria.mensagens(session_id)
        est_prompt = contar_mensagens(self.prompt.format_messages(pergunta=texto, history=hist_antes))
        handler = UsageMetadataCallbackHandler()
        bruta = self.chain.invoke(
            {"pergunta": texto}, config={"configurable": {"session_id": session_id}, "callbacks": [handler]}
        )
        latencia = time.perf_counter() - t0

        saida = verificar_saida(bruta, entrada.sinalizadores, texto)
        if saida.resposta != bruta:
            self.memoria.substituir_ultima_resposta(session_id, saida.resposta)
        self.memoria.podar(session_id)

        usage = handler.usage_metadata or {}
        real_in = sum(u.get("input_tokens", 0) for u in usage.values())
        real_out = sum(u.get("output_tokens", 0) for u in usage.values())
        est_resp = contar(saida.resposta)
        return Resultado(
            texto, saida.resposta, False, None, saida.ajustes, latencia,
            real_in or est_prompt, real_out or est_resp, "usage_metadata" if real_in else "estimado_tiktoken",
            est_prompt, est_resp,
            len(self.memoria.mensagens(session_id)), self.memoria.tokens(session_id),
        )

    # -- extração estruturada (Pydantic) ------------------------------------------------------
    def consultar(self, texto: str):
        """Retorna (ConsultaRecarga | None, erro | None). Nunca levanta: o eval mede a taxa de validade."""
        if self._chain_consulta is None:
            llm_json = self._llm_json or build_llm(self.provider, self.model, json_mode=True, **self.params)
            self._chain_consulta = build_consulta_chain(llm_json)
        try:
            return self._chain_consulta.invoke({"pergunta": texto}), None
        except (ValidationError, OutputParserException) as e:
            return None, f"schema_invalido: {str(e)[:300]}"
        except Exception as e:  # rede, quota...
            return None, f"{type(e).__name__}: {str(e)[:300]}"
