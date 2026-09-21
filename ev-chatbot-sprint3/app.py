"""Front simples em Streamlit 
Uso:  pip install streamlit   e depois   streamlit run app.py
Usa a mesma ChatEV do terminal: guardrails + memória por sessão + prompt versionado."""
import uuid
 
import streamlit as st
 
from src import config
from src.chat import ChatEV
 
st.set_page_config(page_title="Guia Técnico GoodWe", page_icon="⚡")
 
 
@st.cache_resource(show_spinner=False)
def obter_chat(versao, provider, modelo, limite):
    return ChatEV(versao, provider, modelo or None, max_tokens_historico=limite)
 
 
def nova_conversa():
    st.session_state.msgs = []
    st.session_state.sid = str(uuid.uuid4())
 
 
# ---------------- barra lateral ----------------
with st.sidebar:
    st.header("⚙️ Configuração")
    versao = st.selectbox("Versão do prompt", ["v3", "v2", "v1"], help="v3 = com regras de segurança")
    provider = st.selectbox("Provider", ["ollama", "gemini"])
    padrao = config.MODELO_PRINCIPAL if provider == "ollama" else config.GEMINI_MODEL
    modelo = st.text_input("Modelo", value=padrao)
    limite = st.slider("Limite de tokens do histórico", 200, 4000, config.MAX_TOKENS_HISTORICO, step=100)
    extrair = st.checkbox("Mostrar extração estruturada (Pydantic)", value=False,
                          help="Faz uma 2ª chamada ao modelo por pergunta (consome mais cota).")
    if st.button("🗑️ Nova conversa", use_container_width=True):
        nova_conversa()
        st.rerun()
 
# mudou a configuração -> conversa nova (a memória do backend é reiniciada junto)
cfg = (versao, provider, modelo, limite)
if "msgs" not in st.session_state or st.session_state.get("cfg") != cfg:
    nova_conversa()
    st.session_state.cfg = cfg
 
chave_ok = bool(config.OLLAMA_API_KEY if provider == "ollama" else config.GEMINI_API_KEY)
if not chave_ok:
    nome = "OLLAMA_API_KEY" if provider == "ollama" else "GEMINI_API_KEY"
    st.error(f"Defina {nome} no arquivo .env e reinicie o app.")
    st.stop()
 
chat = obter_chat(*cfg)
 
# ---------------- cabeçalho e memória ----------------
st.title("⚡ Guia Técnico GoodWe")
st.caption("Carregadores de veículos elétricos · ChargeGrid Intelligence")
with st.sidebar:
    st.divider()
    st.subheader("🧠 Memória da sessão")
    c1, c2 = st.columns(2)
    c1.metric("Mensagens", len(chat.memoria.mensagens(st.session_state.sid)))
    c2.metric("Tokens", chat.memoria.tokens(st.session_state.sid))
    st.caption(f"Limite: {limite} tokens (janela deslizante).")
 
 
def _legenda(m):
    if m.get("bloqueado"):
        return f"🛡️ bloqueado pelo guardrail ({m['categoria']}) · {m['latencia']:.2f}s"
    ajustes = f" · ajustes: {', '.join(m['ajustes'])}" if m.get("ajustes") else ""
    return f"⏱ {m['latencia']:.1f}s · tokens {m['tokens_prompt']}/{m['tokens_resposta']} ({m['fonte']}){ajustes}"
 
 
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            st.caption(_legenda(m))
            if m.get("consulta") is not None or m.get("consulta_erro"):
                with st.expander("📋 Extração estruturada (ConsultaRecarga)"):
                    if m.get("consulta") is not None:
                        st.json(m["consulta"])
                    else:
                        st.warning(m["consulta_erro"])
 
# ---------------- entrada ----------------
if pergunta := st.chat_input("Pergunte sobre carregadores, erros, potência, faturamento..."):
    st.session_state.msgs.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Consultando o Guia Técnico..."):
                r = chat.perguntar(pergunta, st.session_state.sid)
                obj, erro = chat.consultar(pergunta) if extrair else (None, None)
            msg = {"role": "assistant", "content": r.resposta, "bloqueado": r.bloqueado,
                   "categoria": r.categoria_bloqueio, "latencia": r.latencia_s, "ajustes": r.ajustes,
                   "tokens_prompt": r.tokens_prompt, "tokens_resposta": r.tokens_resposta, "fonte": r.fonte_tokens,
                   "consulta": obj.model_dump() if obj else None, "consulta_erro": erro}
            st.session_state.msgs.append(msg)
        except Exception as e:  # autenticação, cota, rede...
            st.error(f"Erro ao consultar o modelo: {type(e).__name__}: {str(e)[:300]}")
            st.stop()
    st.rerun()
 







