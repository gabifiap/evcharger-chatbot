"""Etapa 4 do RAG (Aula 05/06): ChromaDB persistente. Cada combinação de chunking tem a sua coleção
(kb_cs800_ov100...), assim as iterações da Aula 07 podem ser comparadas sem apagar uma à outra."""
from src import config
from src.rag.chunking import construir_chunks
from src.rag.embeddings import build_embeddings


def nome_colecao(chunk_size=None, chunk_overlap=None) -> str:
    cs = chunk_size or config.RAG_CHUNK_SIZE
    ov = config.RAG_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
    return f"kb_cs{cs}_ov{ov}"


def _chroma(colecao, embeddings, persist_dir=None):
    from langchain_chroma import Chroma

    return Chroma(collection_name=colecao, embedding_function=embeddings,
                  persist_directory=str(persist_dir or config.CHROMA_DIR),
                  collection_metadata={"hnsw:space": "cosine"})  # similaridade cosseno (erro comum da Aula 05)


def total(db) -> int:
    return db._collection.count()


def indexar(chunks, colecao, embeddings=None, persist_dir=None, lote=64):
    """Recria a coleção do zero e indexa os chunks (idempotente: rodar de novo não duplica)."""
    embeddings = embeddings or build_embeddings()
    db = _chroma(colecao, embeddings, persist_dir)
    db.delete_collection()
    db = _chroma(colecao, embeddings, persist_dir)
    for i in range(0, len(chunks), lote):
        parte = chunks[i:i + lote]
        db.add_documents(parte, ids=[c.metadata["chunk_id"] for c in parte])
    return db


def obter_vector_store(chunk_size=None, chunk_overlap=None, embeddings=None, persist_dir=None, forcar=False):
    """Carrega a coleção do disco; se não existir (ou forcar=True), indexa a base de conhecimento agora."""
    embeddings = embeddings or build_embeddings()
    colecao = nome_colecao(chunk_size, chunk_overlap)
    if not forcar:
        db = _chroma(colecao, embeddings, persist_dir)
        if total(db) > 0:
            return db
    chunks, _ = construir_chunks(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return indexar(chunks, colecao, embeddings, persist_dir)
