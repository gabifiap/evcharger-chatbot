"""Etapa 5 do RAG (Aula 05/06): busca dos k chunks mais parecidos com a pergunta."""
from src import config


def get_retriever(db, k=None):
    return db.as_retriever(search_type="similarity", search_kwargs={"k": k or config.RAG_K})


def buscar_com_score(db, pergunta: str, k=None) -> list:
    """Para depuração e para o relatório: (Document, similaridade 0-1). O Chroma devolve distância cosseno."""
    return [(d, round(1 - dist, 3)) for d, dist in db.similarity_search_with_score(pergunta, k=k or config.RAG_K)]
