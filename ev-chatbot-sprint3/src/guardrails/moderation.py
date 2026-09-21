"""Guardrail de saída(camada 4 da revisão de segurança da Aula 01).

1. Vazamento do prompt de sistema -> troca por recusa.
2. Especificação inventada: código de produto (ex.: GW50K-HCA-20) que não está na base e não veio da
   pergunta do usuário -> troca por resposta segura ("não consta na base").
3. Emergência elétrica sem orientação a profissional habilitado -> anexa rodapé de segurança.
"""
import re
from dataclasses import dataclass, field

from src.guardrails.scope_validator import RESPOSTAS, normalizar
from src.knowledge import codigos_modelo_conhecidos, extrair_codigos_modelo

_MARCADORES_VAZAMENTO = ["<regras_de_resposta>", "<seguranca>", "<base_conhecimento>", "<papel>",
                         "protocolo de resposta", "diretrizes de atuacao", "{base_conhecimento}"]
_ORIENTACAO = re.compile(r"bombeiro|\b193\b|profissional habilitado|tecnico habilitado|eletricista|tecnico credenciado")

RODAPE_EMERGENCIA = (
    "\n\n⚠️ Por segurança: mantenha distância, não toque no equipamento nem no veículo e acione um "
    "profissional habilitado (eletricista ou assistência técnica GoodWe). Em caso de fogo ou fumaça, "
    "ligue para os Bombeiros (193)."
)
RESPOSTA_SEM_BASE = (
    "Não encontrei essa especificação na minha base de conhecimento, então prefiro não inferir. "
    "Para confirmar dados desse produto, entre em contato com o suporte GoodWe."
)


@dataclass
class ResultadoSaida:
    resposta: str
    ajustes: list = field(default_factory=list)


def verificar_saida(resposta: str, sinalizadores_entrada=(), texto_usuario: str = "") -> ResultadoSaida:
    ajustes = []
    n = normalizar(resposta)

    if any(m in n or m in resposta.lower() for m in _MARCADORES_VAZAMENTO):
        return ResultadoSaida(RESPOSTAS["prompt_injection"], ["vazamento_prompt"])

    inventados = extrair_codigos_modelo(resposta) - set(codigos_modelo_conhecidos()) - extrair_codigos_modelo(texto_usuario)
    if inventados:
        return ResultadoSaida(RESPOSTA_SEM_BASE, [f"spec_inventada:{','.join(sorted(inventados))}"])

    if "emergencia" in sinalizadores_entrada and not _ORIENTACAO.search(n):
        resposta = resposta.rstrip() + RODAPE_EMERGENCIA
        ajustes.append("rodape_emergencia")

    return ResultadoSaida(resposta, ajustes)
