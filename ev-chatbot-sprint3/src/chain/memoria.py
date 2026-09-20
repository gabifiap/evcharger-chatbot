"""Memória por sessão: RunnableWithMessageHistory + ConversationTokenBufferMemory (Aula 02).

DUAS ARMADILHAS RESOLVIDAS AQUI (documentar no relatório):
1. RunnableWithMessageHistory grava direto em `chat_memory` e NÃO passa por
   ConversationTokenBufferMemory.save_context, então o limite de tokens não é aplicado sozinho.
   Por isso `podar()` reproduz a lógica da janela deslizante após cada turno.
2. O ChatOllama não implementa contagem de tokens (cai num tokenizer GPT-2 que exige `transformers`).
   A poda usa tiktoken (src/tokens.py) — aproximação para modelos do Ollama.

ConversationTokenBufferMemory e RunnableWithMessageHistory estão marcados como deprecated
(o caminho novo é LangGraph). São exigidos pelo enunciado; registrar o trade-off no relatório.
"""
import warnings

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage

from src.tokens import contar_mensagens

try:  # LangChain 1.x
    from langchain_classic.memory import ConversationTokenBufferMemory
except ImportError:  # LangChain 0.3.x
    from langchain.memory import ConversationTokenBufferMemory


class MemoriaSessoes:
    def __init__(self, llm, max_token_limit: int = 1000):
        self.llm = llm
        self.max_token_limit = max_token_limit
        self._memorias = {}

    def _mem(self, session_id: str):
        if session_id not in self._memorias:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._memorias[session_id] = ConversationTokenBufferMemory(
                    llm=self.llm,
                    max_token_limit=self.max_token_limit,
                    return_messages=True,
                    chat_memory=InMemoryChatMessageHistory(),
                )
        return self._memorias[session_id]

    def get_history(self, session_id: str):
        """Passe esta função ao RunnableWithMessageHistory."""
        return self._mem(session_id).chat_memory

    def podar(self, session_id: str) -> int:
        """Janela deslizante: descarta as mensagens mais antigas até caber em max_token_limit.
        Nunca deixa o histórico começando por uma resposta (AIMessage) órfã."""
        msgs = self._mem(session_id).chat_memory.messages
        removidas = 0
        while msgs and contar_mensagens(msgs) > self.max_token_limit:
            msgs.pop(0)
            removidas += 1
        while msgs and not isinstance(msgs[0], HumanMessage):
            msgs.pop(0)
            removidas += 1
        return removidas

    def mensagens(self, session_id: str) -> list:
        return list(self._mem(session_id).chat_memory.messages)

    def tokens(self, session_id: str) -> int:
        return contar_mensagens(self._mem(session_id).chat_memory.messages)

    def limpar(self, session_id: str):
        self._memorias.pop(session_id, None)

    def substituir_ultima_resposta(self, session_id: str, texto: str) -> None:
        """Se o guardrail de saída trocou a resposta, o histórico não pode guardar a versão bruta."""
        from langchain_core.messages import AIMessage

        msgs = self._mem(session_id).chat_memory.messages
        if msgs and isinstance(msgs[-1], AIMessage):
            msgs[-1] = AIMessage(content=texto)
