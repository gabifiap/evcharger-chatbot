# EV Challenge — GoodWe · Sprint 03

Chatbot de suporte técnico para carregadores de carros elétricos da GoodWe (plataforma ChargeGrid). Ele responde dúvidas sobre potência, faturamento, instalação e diagnóstico de erros.
Nesta sprint refizemos o núcleo do chatbot com **LangChain** (modelo principal: `gpt-oss:120b`, pelo Ollama Cloud).

**Turma:** 1CCPH · **Grupo:** Gabriela Batista Costa (RM573583) · Samara Carvalho (RM573666) · Anna Luiza Carvalhaes (RM573330) · Kethelyn Rocha (RM574016)

## Interface visual
É possível com o chatbot pelo navegador, sem instalar nada:

**https://evcharger-chatbot-myr9jlfkrlhachympyhbn5.streamlit.app/**

A página usa a cota gratuita do Ollama Cloud do grupo. Se ela não responder, a cota pode ter acabado; nesse caso, rode o projeto no seu computador (veja abaixo).

## O que o projeto tem de novo nesta sprint
- **Conversa com memória**, com limite de tamanho (medido em tokens, que são pedaços de palavras).
- **Saída organizada**: um formato fixo (`ConsultaRecarga`, feito com Pydantic) para extrair os dados da pergunta.
- **Prompt em 3 versões** (`prompts/`), organizado com etiquetas XML.
- **Proteções (guardrails)** que bloqueiam pedidos para "enganar" o bot, assuntos fora do tema e conselhos jurídicos, financeiros ou de mexer na parte elétrica.
- **Teste com 19 perguntas** (`evals/`), feito no bot antigo (Sprint 2) e no novo.
- **Relatórios de evolução** mais robustos na pasta docs/

## Como rodar no seu computador
Precisa de **Python 3.12 ou 3.13** e de uma chave do Ollama Cloud (crie em ollama.com/settings, aba *Keys*).

**1. Abra um terminal na pasta do projeto** (a que tem o arquivo `main.py`).

**2. Crie o ambiente e instale as bibliotecas:**
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
No Linux ou Mac, troque a segunda linha por `source .venv/bin/activate`.

**3. Crie o arquivo com a sua chave:**
```
copy .env.example .env
```
No Linux ou Mac: `cp .env.example .env`. Abra o arquivo `.env` e cole a chave depois de `OLLAMA_API_KEY=`, sem aspas e sem espaços. **O `.env` 

**4. Rode o que quiser:**
```
python -m tests.test_offline               testes automáticos (não precisam de chave nem de internet)
python main.py                             conversa no terminal, execução de comandos (/consulta /historico...)
python demo_memoria.py --limite 3000       demonstração da memória (4 perguntas)
pip install streamlit                      só na primeira vez
streamlit run app.py                       a mesma interface visual, no seu computador
```
Comandos dentro da conversa do terminal: `/consulta <texto>` (mostra a saída organizada), `/historico`, `/limpar` e `/sair`.

## Pastas
```
src/chain/       a cadeia do LangChain (builder.py) e a memória da conversa (memoria.py)
src/schemas/     o formato fixo da saída organizada
src/guardrails/  as proteções de entrada e de saída
src/chat.py      junta tudo em um turno de conversa
prompts/         as versões do prompt e a tabela de versões (VERSOES.md)
evals/           as 19 perguntas de teste, os scripts e os resultados (.json)
docs/            os relatórios (relatório de evolução em PDF, modelos, memória e explicação dos evals)
data/            a base de conhecimento (as perguntas e respostas sobre os carregadores)
legacy/          o bot da Sprint 2, guardado só para comparar
tests/           testes automáticos
main.py          conversa no terminal
app.py           interface visual (Streamlit)
```

## Resultados em resumo
Mesmas 19 perguntas nos dois bots. Tempo e tokens só sobre as 10 perguntas que chegam ao modelo.

| O que medimos | Sprints 1/2 (Gemini, prompt v1, sem memória) | Sprint 03 (gpt-oss:120b, prompt v3) |
|---|---|---|
| Nota média de 0 a 10 (19 perguntas) | 7,58 | 8,47 |
| Nota média só nas perguntas 1 a 10 | 7,4 | 7,2 |
| Testes automáticos de segurança aprovados | 11 de 13 | 13 de 13 |
| Tokens enviados por pergunta (estimado) | 4.616 | 4.623 |
| Tempo de resposta médio / mediana (s) | 3,25 / 2,93 | 1,88 / 1,67 |
| Saída organizada válida | não existia | 16 de 19 |

O maior ganho foi em **segurança**: o bot antigo revelou a base de conhecimento inteira ao ser induzido (pergunta 13) e mandou desligar o disjuntor diante de faíscas (pergunta 6). Nas perguntas comuns (1 a 10), o gpt-oss não ficou melhor que o bot antigo. Os detalhes, os limites do teste e os problemas encontrados estão em `docs/relatorio_evolucao.pdf`.

## Como repetir os testes (evals)
```
python -m evals.run_baseline_sprint2                      bot antigo (precisa de GEMINI_API_KEY e de: pip install google-genai)
python -m evals.run_eval --versao v3 --saida evals/sprint3_results.json
python -m evals.run_eval --versao v3 --model gemma4:31b --saida evals/gemma4.json
python -m evals.reavaliar                                 recalcula os testes automáticos de todos os resultados
python -m evals.comparar evals/baseline_sprint2_results.json evals/sprint3_results.json
```
A explicação completa dos testes está em `docs/explicacao_dos_evals.pdf`.

## Limites conhecidos
- Cada pergunta foi feita **uma vez**; diferenças pequenas podem ser sorte.
- As proteções usam regras de texto simples: uma frase bem reescrita pode passar.
- A contagem de tokens (tiktoken) é aproximada para os modelos do Ollama.
- A memória usa recursos do LangChain que já são considerados antigos; usamos porque o enunciado pede.
