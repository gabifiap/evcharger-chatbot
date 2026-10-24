"""Etapa 3 do RAG (Aula 05): nomic-embed-text pelo Ollama.
O Ollama Cloud recusa o modelo de embeddings (401), então por padrão usa o Ollama instalado no computador
(http://localhost:11434, depois de "ollama pull nomic-embed-text"). Para outro servidor, defina OLLAMA_EMBED_HOST no .env."""
import os

from langchain_ollama import OllamaEmbeddings

from src import config


def build_embeddings(model=None):
    host = os.getenv("OLLAMA_EMBED_HOST", "http://localhost:11434")
    kw = dict(model=model or config.MODELO_EMBEDDING, base_url=host)
    if "ollama.com" in host and config.OLLAMA_API_KEY:  # só o Cloud pede a chave
        kw["client_kwargs"] = {"headers": {"Authorization": f"Bearer {config.OLLAMA_API_KEY}"}}
    return OllamaEmbeddings(**kw)