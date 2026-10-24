"""Um turno de conversa com RAG: guardrail de entrada -> retrieve + chain com memória -> guardrail de saída.
Herda do ChatEV da Sprint 3 (memória por sessão, extração estruturada, guardrails), só troca a chain."""
import time
import warnings
from dataclasses import dataclass, field

from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory

from src import config
from src.chain.builder import build_llm
from src.chain.memoria import MemoriaSessoes
from src.chat import ChatEV, Resultado
from src.guardrails import validar_entrada, verificar_saida
from src.guardrails.scope_validator import normalizar
from src.rag.chain_rag import build_rag_chain
from src.rag.prompt_rag import montar_prompt_rag
from src.rag.retriever import get_retriever
from src.rag.vector_store import obter_vector_store
from src.tokens import contar, contar_mensagens

_RECUSA_RAG = "nao encontrei"


@dataclass
class ResultadoRAG(Resultado):
    fontes: list = field(default_factory=list)  # [{"citacao": ..., "trecho": ...}] dos chunks usados
    recusou_por_falta_de_contexto: bool = False


def garantir_citacao(resposta: str, docs) -> tuple:
    """Toda resposta com conteúdo precisa citar a fonte. Se o modelo esqueceu, acrescentamos as fontes
    dos chunks recuperados. Resposta de recusa ("não encontrei...") não leva fonte."""
    n = normalizar(resposta)
    if _RECUSA_RAG in n or "(fonte:" in n or "fontes consultadas" in n or not docs:
        return resposta, []
    citacoes = list(dict.fromkeys(d.metadata.get("citacao", d.metadata.get("source", "?")) for d in docs))
    return resposta.rstrip() + "\n\nFontes consultadas: " + "; ".join(citacoes) + ".", ["citacao_adicionada"]


class ChatRAG(ChatEV):
    def __init__(self, versao_rag=None, provider="ollama", model=None, llm=None, llm_json=None, retriever=None,
                 k=None, chunk_size=None, chunk_overlap=None, max_tokens_historico=None, **params):
        self.versao = versao_rag or config.RAG_PROMPT
        self.provider, self.model, self.params = provider, model, params
        self.llm = llm or build_llm(provider, model, **params)
        self._llm_json = llm_json
        self.retriever = retriever or get_retriever(obter_vector_store(chunk_size, chunk_overlap), k)
        self.prompt = montar_prompt_rag(self.versao)
        self.memoria = MemoriaSessoes(self.llm, max_tokens_historico or config.MAX_TOKENS_HISTORICO)
        base = build_rag_chain(self.llm, self.retriever, self.versao, prompt=self.prompt).with_retry(stop_after_attempt=3)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.chain = RunnableWithMessageHistory(
                base, self.memoria.get_history, input_messages_key="pergunta",
                history_messages_key="history", output_messages_key="resposta",
            )
        self._chain_consulta = None

    def perguntar(self, texto: str, session_id: str = "default") -> ResultadoRAG:
        t0 = time.perf_counter()
        entrada = validar_entrada(texto)
        if not entrada.permitido:
            # Bloqueios NÃO entram na memória nem chegam ao retriever (nem gastam embedding).
            return ResultadoRAG(texto, entrada.resposta, True, entrada.categoria,
                                latencia_s=time.perf_counter() - t0,
                                historico_msgs=len(self.memoria.mensagens(session_id)),
                                historico_tokens=self.memoria.tokens(session_id))

        hist_antes = self.memoria.mensagens(session_id)
        handler = UsageMetadataCallbackHandler()
        out = self.chain.invoke({"pergunta": texto}, config={"configurable": {"session_id": session_id}, "callbacks": [handler]})
        latencia = time.perf_counter() - t0
        docs, bruta, contexto = out["docs"], out["resposta"], out["contexto"]

        # códigos de produto que aparecem no contexto recuperado são legítimos (não são "spec inventada")
        saida = verificar_saida(bruta, entrada.sinalizadores, texto + "\n" + contexto)
        final, extra = garantir_citacao(saida.resposta, docs)
        if final != bruta:
            self.memoria.substituir_ultima_resposta(session_id, final)
        self.memoria.podar(session_id)

        est_prompt = contar_mensagens(self.prompt.format_messages(pergunta=texto, history=hist_antes, contexto=contexto))
        usage = handler.usage_metadata or {}
        real_in = sum(u.get("input_tokens", 0) for u in usage.values())
        real_out = sum(u.get("output_tokens", 0) for u in usage.values())
        est_resp = contar(final)
        return ResultadoRAG(
            pergunta=texto, resposta=final, ajustes=saida.ajustes + extra, latencia_s=latencia,
            tokens_prompt=real_in or est_prompt, tokens_resposta=real_out or est_resp,
            fonte_tokens="usage_metadata" if real_in else "estimado_tiktoken",
            tokens_prompt_est=est_prompt, tokens_resposta_est=est_resp,
            historico_msgs=len(self.memoria.mensagens(session_id)), historico_tokens=self.memoria.tokens(session_id),
            fontes=[{"citacao": d.metadata.get("citacao", "?"), "trecho": d.page_content} for d in docs],
            recusou_por_falta_de_contexto=_RECUSA_RAG in normalizar(final),
        )
