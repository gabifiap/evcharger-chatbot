"""Interface do RAG em Streamlit, com as fontes (documento e página) visíveis em cada resposta.
Uso (na pasta do projeto, a que tem o main.py):  streamlit run app/app.py
Usa a mesma ChatRAG do eval: retriever + guardrails + memória por sessão + prompt RAG versionado."""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # para achar o pacote src/ ao rodar de app/

import streamlit as st

from src import config
from src.rag import ChatRAG
from src.rag.prompt_rag import VERSOES_RAG

st.set_page_config(page_title="Guia Técnico GoodWe (RAG)", page_icon="⚡")


@st.cache_resource(show_spinner="Carregando a base de conhecimento...")
def obter_chat(versao, provider, modelo, k, limite):
    return ChatRAG(versao, provider, modelo or None, k=k, max_tokens_historico=limite)


def nova_conversa():
    st.session_state.msgs = []
    st.session_state.sid = str(uuid.uuid4())


with st.sidebar:
    st.header("⚙️ Configuração")
    versao = st.selectbox("Versão do prompt RAG", list(VERSOES_RAG)[::-1], help="v3 = grounding + segurança")
    provider = st.selectbox("Provider", ["ollama", "gemini"])
    padrao = config.MODELO_PRINCIPAL if provider == "ollama" else config.GEMINI_MODEL
    modelo = st.text_input("Modelo", value=padrao)
    k = st.slider("Trechos recuperados (k)", 1, 8, config.RAG_K)
    limite = st.slider("Limite de tokens do histórico", 200, 4000, config.MAX_TOKENS_HISTORICO, step=100)
    if st.button("🗑️ Nova conversa", use_container_width=True):
        nova_conversa()
        st.rerun()

cfg = (versao, provider, modelo, k, limite)
if "msgs" not in st.session_state or st.session_state.get("cfg") != cfg:
    nova_conversa()
    st.session_state.cfg = cfg

if not config.OLLAMA_API_KEY:  # embeddings e modelo principal usam o Ollama Cloud
    st.error("Defina OLLAMA_API_KEY no arquivo .env (ou nos secrets do Streamlit) e reinicie o app.")
    st.stop()

chat = obter_chat(*cfg)
st.title("⚡ Guia Técnico GoodWe")
st.caption("Carregadores de veículos elétricos · respostas com citação dos documentos")


def _fontes(m):
    if m.get("bloqueado") or not m.get("fontes"):
        return
    citacoes = list(dict.fromkeys(f["citacao"] for f in m["fontes"]))
    st.caption("📚 Fontes: " + " · ".join(citacoes))
    with st.expander("Trechos recuperados"):
        for f in m["fontes"]:
            st.markdown(f"**{f['citacao']}**")
            st.text(f["trecho"])


def _legenda(m):
    if m.get("bloqueado"):
        return f"🛡️ bloqueado pelo guardrail ({m['categoria']}) · {m['latencia']:.2f}s"
    return f"⏱ {m['latencia']:.1f}s · tokens {m['tokens_prompt']}/{m['tokens_resposta']}"


for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            _fontes(m)
            st.caption(_legenda(m))

if pergunta := st.chat_input("Pergunte sobre carregadores, erros, potência, faturamento..."):
    st.session_state.msgs.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Buscando nos documentos..."):
                r = chat.perguntar(pergunta, st.session_state.sid)
            st.session_state.msgs.append({
                "role": "assistant", "content": r.resposta, "bloqueado": r.bloqueado, "categoria": r.categoria_bloqueio,
                "latencia": r.latencia_s, "tokens_prompt": r.tokens_prompt, "tokens_resposta": r.tokens_resposta,
                "fontes": r.fontes})
        except Exception as e:  # autenticação, cota, rede...
            st.error(f"Erro ao consultar o modelo: {type(e).__name__}: {str(e)[:300]}")
            st.stop()
    st.rerun()
