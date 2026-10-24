"""Etapa 6 do RAG (Aula 06): chain LCEL  retriever -> contexto -> prompt | llm | parser.
A saída é um dict (docs, contexto e resposta) para a interface poder mostrar as fontes."""
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.rag.prompt_rag import formatar_contexto, montar_prompt_rag


def build_rag_chain(llm, retriever, versao="v3", prompt=None):
    gerar = (prompt or montar_prompt_rag(versao)) | llm | StrOutputParser()
    return (
        RunnablePassthrough.assign(docs=itemgetter("pergunta") | retriever)
        .assign(contexto=lambda x: formatar_contexto(x["docs"]))
        .assign(resposta=gerar)
    )
