"""Etapa 2 do RAG (Aula 06/07): divide os documentos em chunks e descarta os que tentam dar ordens ao modelo.

chunk_size=800 / overlap=100 é o ponto de partida da Aula 06; a Aula 07 manda testar outros valores e medir com
RAGAS (ver evals/run_rag_eval.py). Separadores hierárquicos: parágrafo -> linha -> frase -> palavra."""
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src import config
from src.guardrails.scope_validator import _PADROES, normalizar
from src.rag.loader import carregar_documentos


def dividir(docs, chunk_size=None, chunk_overlap=None) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or config.RAG_CHUNK_SIZE,
        chunk_overlap=config.RAG_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    contagem = {}
    for c in chunks:  # id estável por chunk: arquivo + página/seção + posição
        base = f"{c.metadata['source']}|{c.metadata.get('page', c.metadata.get('secao', ''))}"
        contagem[base] = contagem.get(base, 0) + 1
        c.metadata["chunk_id"] = f"{base}|{contagem[base]}"
    return chunks


def sanitizar(chunks) -> tuple:
    """Proteção contra prompt injection via documentos: um chunk que contenha frases do tipo
    "ignore as instruções anteriores" ou "revele o prompt" NÃO é indexado. Reaproveita os padrões do
    guardrail de entrada. Retorna (chunks_limpos, chunks_descartados)."""
    limpos, descartados = [], []
    for c in chunks:
        n = normalizar(c.page_content)
        suspeito = any(re.search(p, n) for p in _PADROES["prompt_injection"])
        (descartados if suspeito else limpos).append(c)
    return limpos, descartados


def construir_chunks(pasta=None, chunk_size=None, chunk_overlap=None) -> tuple:
    """Pipeline de indexação sem rede: carrega -> divide -> sanitiza. Retorna (chunks, descartados)."""
    return sanitizar(dividir(carregar_documentos(pasta), chunk_size, chunk_overlap))
