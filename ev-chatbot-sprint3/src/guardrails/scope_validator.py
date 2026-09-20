"""Guardrail de ENTRADA (camada 2 da revisão de segurança da Aula 01).

Determinístico e barato: bloqueia jailbreak/prompt injection, temas fora do escopo GoodWe e pedidos
de aconselhamento jurídico/financeiro/intervenção elétrica (orientando profissional habilitado).
Emergências elétricas NÃO são bloqueadas: viram um sinalizador e o modelo responde com segurança
(o guardrail de saída garante a orientação a profissional habilitado).

Limitação conhecida: regex gera falsos negativos (reformulações) e, raramente, falsos positivos.
Melhoria futura: usar ConsultaRecarga.tipo_consulta == 'fora_escopo' como segunda camada.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional


def normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt or "")
    return "".join(c for c in txt if not unicodedata.combining(c)).lower()


RESPOSTAS = {
    "prompt_injection": (
        "Não posso ignorar minhas instruções nem revelar a configuração interna do sistema. "
        "Posso ajudar com dúvidas sobre os carregadores GoodWe e a plataforma ChargeGrid."
    ),
    "fora_escopo": (
        "Sou o Guia Técnico GoodWe e só posso ajudar com carregadores de veículos elétricos GoodWe "
        "e a plataforma ChargeGrid (potência, faturamento, instalação e diagnóstico). "
        "Tem alguma dúvida sobre isso?"
    ),
    "juridico_financeiro": (
        "Não posso dar aconselhamento jurídico ou financeiro. Para isso, consulte um profissional "
        "habilitado (advogado, contador ou consultor financeiro). Posso explicar, por exemplo, como o "
        "ChargeGrid registra ciclos de recarga e faturamento."
    ),
    "seguranca_eletrica": (
        "Intervenções elétricas (abrir o equipamento, mexer em fiação, quadro ou aterramento) devem ser "
        "feitas apenas por profissional habilitado, como um eletricista ou instalador credenciado GoodWe. "
        "Não recomendo que você faça isso por conta própria."
    ),
}

_PADROES = {
    "prompt_injection": [
        r"ignor(e|ar|em)\b.{0,40}\b(instruc|regra|prompt|diretriz|anterior)",
        r"esque(ca|cer)\b.{0,40}\b(tudo|instruc|regra|anterior)",
        r"desconsider(e|ar)\b.{0,40}\b(instruc|regra|anterior)",
        r"(revele|mostre|exiba|repita|imprima|vaze|liste)\b.{0,50}\b(prompt|instruc\w*|configurac\w*|base de conhecimento)",
        r"(system|sistema)\s*prompt|prompt\s+do\s+sistema",
        r"a partir de agora,? (voce|vc)\b",
        r"\bdan\b|jailbreak|modo\s+(desenvolvedor|deus|dev)\b|developer mode",
        r"ignore (all|previous|prior|the above)|disregard|forget (all|your|previous)",
        r"finja (que )?(voce )?(e|nao tem)",
        r"</?\s*(system|instruc\w*|regras\w*|seguranca|base_conhecimento|papel)\b[^>]*>",
    ],
    "juridico_financeiro": [
        r"\b(processar|processo judicial|acao judicial|advogado|indeniza\w*|responsabilidade civil)\b",
        r"\b(vale a pena (investir|financiar)|devo (investir|financiar)|retorno (do|sobre o?) investimento|payback|roi)\b",
        r"\b(imposto|tributa\w*|financiamento|emprestimo|melhor investimento)\b",
    ],
    "seguranca_eletrica": [
        r"\b(abrir|desmontar|abro|desmonto)\b.{0,25}\b(carregador|wallbox|equipamento)",
        r"\bmexer\b.{0,25}\b(fio|fios|fiacao|cabo|cabos|quadro|disjuntor|aterramento)",
        r"\b(puxar|emendar)\b.{0,15}\b(fio|cabo)",
        r"eu mesmo\b.{0,15}\b(instal|troc|mex|abr)",
        r"sem (eletricista|tecnico|profissional)",
        r"\bbypass\b|\bburlar\b|desativar (a )?(protecao|dr|dps|aterramento)",
    ],
    "fora_escopo": [
        r"\b(receita de|bolo|futebol|campeonato|horoscopo|signo|piada|poema|poesia|letra de musica|filme|novela|bitcoin|criptomoeda|eleicao|politic\w*|presidente)\b",
        r"\bescreva (um |uma )?(codigo|programa|script|redacao|texto sobre)",
        r"\b(python|javascript|java|c\+\+)\b",
    ],
}
_ORDEM = ["prompt_injection", "juridico_financeiro", "seguranca_eletrica", "fora_escopo"]

_EMERGENCIA = re.compile(r"faisca|fumaca|cheiro de queimado|queimad|choque|pegando fogo|incendio|derret|superaquec")


@dataclass
class ResultadoEntrada:
    permitido: bool
    categoria: Optional[str] = None
    resposta: Optional[str] = None
    sinalizadores: list = field(default_factory=list)


def validar_entrada(texto: str) -> ResultadoEntrada:
    n = normalizar(texto)
    sinal = ["emergencia"] if _EMERGENCIA.search(n) else []
    for cat in _ORDEM:
        if any(re.search(p, n) for p in _PADROES[cat]):
            return ResultadoEntrada(False, cat, RESPOSTAS[cat], sinal)
    return ResultadoEntrada(True, None, None, sinal)
