# EV Challenge — GoodWe · Sprint 03

Chatbot de suporte técnico para carregadores de carros elétricos da GoodWe (plataforma ChargeGrid). Ele responde dúvidas sobre potência, faturamento, instalação e diagnóstico de erros.

Nesta sprint refizemos o núcleo do chatbot com **LangChain** (modelo principal: `gpt-oss:120b`, pelo Ollama Cloud).

**Turma:** 1CCPH · **Grupo:** Gabriela Batista Costa (RM573583) · Samara Carvalho (RM573666) · Anna Luiza Carvalhaes (RM573330) · Kethelyn Rocha (RM574016)

---

## Interface visual

Dá para conversar com o chatbot pelo navegador, sem instalar nada:

[**https://evcharger-chatbot-myr9jlfkrlhachympyhbn5.streamlit.app/**](https://evcharger-chatbot-myr9jlfkrlhachympyhbn5.streamlit.app/)

A página usa a cota gratuita do Ollama Cloud do grupo. Se ela não responder, a cota pode ter acabado; nesse caso, rode o projeto no seu computador (veja abaixo).

---

## O que o projeto tem de novo nesta sprint

- **Conversa com memória**, com limite de tamanho (medido em tokens, que são pedaços de palavras).
- **Saída organizada**: um formato fixo (`ConsultaRecarga`, feito com Pydantic) para extrair os dados da pergunta.
- **Prompt em 3 versões** (`prompts/`), organizado com etiquetas XML.
- **Proteções (guardrails)** que bloqueiam pedidos para "enganar" o bot, assuntos fora do tema e conselhos jurídicos, financeiros ou de mexer na parte elétrica.
- **Teste com 19 perguntas** (`evals/`), feito no bot antigo (Sprint 2) e no novo.

---

## Como rodar no seu computador

Precisa de **Python 3.12 ou 3.13** e de uma chave do Ollama Cloud (crie em ollama.com/settings, aba *Keys*).

### 1. Abra um terminal na pasta do projeto

A pasta que tem o arquivo `main.py`.

### 2. Crie o ambiente e instale as bibliotecas

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
