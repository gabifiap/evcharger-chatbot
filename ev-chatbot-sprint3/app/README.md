# Interface do RAG (Sprint 04)

Chat em Streamlit que consulta a base `data/knowledge_base/` pelo ChromaDB e mostra, em cada resposta, de qual documento
e página veio a informação (linha "Fontes" e, abaixo, os trechos recuperados).

## Como rodar

Na pasta do projeto (a que tem o `main.py`), com o `.env` preenchido (`OLLAMA_API_KEY`):

```
pip install -r requirements.txt
python -m scripts.gerar_base_conhecimento     só se mudar o data/datasets.json
python -m src.rag.indexar                     indexa no ChromaDB (data/chroma_db/); o app também indexa sozinho na 1ª vez
streamlit run app/app.py
```

Para publicar no Streamlit Cloud: arquivo principal `ev-chatbot-sprint3/app/app.py` e `OLLAMA_API_KEY` em *Secrets*
(no formato `OLLAMA_API_KEY = "..."`). Na primeira abertura o app indexa a base (alguns segundos).
