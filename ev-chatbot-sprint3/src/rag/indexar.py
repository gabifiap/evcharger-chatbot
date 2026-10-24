"""Indexa a base de conhecimento no ChromaDB (persistente). Precisa de OLLAMA_API_KEY (embeddings).
Uso: python -m src.rag.indexar                      (800/100, padrão)
     python -m src.rag.indexar --chunk-size 500 --overlap 50
     python -m src.rag.indexar --so-chunks          (não usa rede: só mostra os chunks e os descartados)"""
import argparse
import statistics

from src.rag.chunking import construir_chunks
from src.rag.vector_store import indexar, nome_colecao


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk-size", type=int, default=None)
    ap.add_argument("--overlap", type=int, default=None)
    ap.add_argument("--so-chunks", action="store_true")
    a = ap.parse_args()

    chunks, descartados = construir_chunks(chunk_size=a.chunk_size, chunk_overlap=a.overlap)
    tam = [len(c.page_content) for c in chunks]
    print(f"chunks: {len(chunks)} | tamanho médio {statistics.mean(tam):.0f} (mín {min(tam)}, máx {max(tam)})")
    for c in descartados:
        print(f"DESCARTADO (suspeita de injection) {c.metadata['chunk_id']}: {c.page_content[:80]!r}")
    if a.so_chunks:
        return
    nome = nome_colecao(a.chunk_size, a.overlap)
    db = indexar(chunks, nome)
    print(f"coleção '{nome}' indexada: {db._collection.count()} chunks")


if __name__ == "__main__":
    main()
