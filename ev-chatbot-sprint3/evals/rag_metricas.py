"""Métricas do RAG (Aula 07), 0 a 1. Implementação manual equivalente ao RAGAS (fallback aceito no enunciado):

- faithfulness: o LLM-juiz decompõe a resposta em afirmações isoladas e checa cada uma contra o contexto
  recuperado; score = afirmações sustentadas / total (é o mecanismo do RAGAS, ver Aula 07).
- answer_relevancy: o juiz gera 3 perguntas que a resposta responderia; score = média da similaridade cosseno
  (embedding nomic) entre elas e a pergunta original (também o mecanismo do RAGAS).
- context_relevance: o juiz marca quais chunks recuperados são úteis para a pergunta; score = úteis / recuperados.
Respostas de recusa ("não encontrei...") ficam fora das médias (não há afirmação para checar)."""
import json
import math
import re

from langchain_core.messages import HumanMessage, SystemMessage

_P_AFIRMACOES = ("Extraia da RESPOSTA as afirmações factuais isoladas (uma ideia por item, sem citações de fonte). "
                 'Responda SOMENTE JSON: {"afirmacoes": ["...", "..."]}')
_P_SUSTENTADAS = ("Para cada afirmação, diga se ela pode ser deduzida APENAS do CONTEXTO (true) ou não (false). "
                  'Responda SOMENTE JSON: {"sustentadas": [true, false, ...]} na mesma ordem e quantidade.')
_P_PERGUNTAS = ('Escreva 3 perguntas diferentes que a RESPOSTA abaixo responderia. Responda SOMENTE JSON: {"perguntas": ["...", "...", "..."]}')
_P_CONTEXTO = ("Para cada trecho numerado, diga se ele ajuda a responder a PERGUNTA (true) ou não (false). "
               'Responda SOMENTE JSON: {"uteis": [true, false, ...]} na mesma ordem e quantidade.')


def _json(llm, sistema: str, usuario: str) -> dict:
    texto = llm.invoke([SystemMessage(sistema), HumanMessage(usuario)]).content
    m = re.search(r"\{.*\}", texto, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def _cos(a, b) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def faithfulness(llm_juiz, resposta: str, contextos: list):
    afirm = _json(llm_juiz, _P_AFIRMACOES, f"<resposta>{resposta}</resposta>").get("afirmacoes") or []
    if not afirm:
        return None
    ctx = "\n\n".join(contextos)
    lista = "\n".join(f"{i}. {a}" for i, a in enumerate(afirm, 1))
    ok = _json(llm_juiz, _P_SUSTENTADAS, f"<contexto>{ctx}</contexto>\n<afirmacoes>\n{lista}\n</afirmacoes>").get("sustentadas") or []
    ok = (list(ok) + [False] * len(afirm))[:len(afirm)]  # faltou item na resposta do juiz = não sustentada
    return round(sum(1 for x in ok if x is True) / len(afirm), 3)


def answer_relevancy(llm_juiz, embeddings, pergunta: str, resposta: str):
    gen = [q for q in (_json(llm_juiz, _P_PERGUNTAS, f"<resposta>{resposta}</resposta>").get("perguntas") or []) if isinstance(q, str)]
    if not gen:
        return None
    vp = embeddings.embed_query(pergunta)
    vs = embeddings.embed_documents(gen)
    return round(sum(_cos(vp, v) for v in vs) / len(vs), 3)


def context_relevance(llm_juiz, pergunta: str, contextos: list):
    if not contextos:
        return None
    lista = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contextos, 1))
    uteis = _json(llm_juiz, _P_CONTEXTO, f"<pergunta>{pergunta}</pergunta>\n<trechos>\n{lista}\n</trechos>").get("uteis") or []
    uteis = (list(uteis) + [False] * len(contextos))[:len(contextos)]
    return round(sum(1 for x in uteis if x is True) / len(contextos), 3)


def avaliar(llm_juiz, embeddings, pergunta: str, resposta: str, contextos: list) -> dict:
    return {
        "faithfulness": faithfulness(llm_juiz, resposta, contextos),
        "answer_relevancy": answer_relevancy(llm_juiz, embeddings, pergunta, resposta),
        "context_relevance": context_relevance(llm_juiz, pergunta, contextos),
    }
