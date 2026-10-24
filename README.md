# EV Challenge — GoodWe · Sprint 04

Chatbot de suporte técnico para carregadores de carros elétricos da GoodWe (plataforma ChargeGrid). Ele responde dúvidas sobre potência, faturamento, instalação e diagnóstico de erros.
Nesta sprint o chatbot passou a usar **RAG**: em vez de mandar a base de conhecimento inteira em toda pergunta, ele busca no **ChromaDB** só os trechos que importam e **cita o documento e a página** de onde tirou a resposta. O modelo principal continua sendo o `gpt-oss:120b`, pelo Ollama Cloud.

**Turma:** 1CCPH · **Grupo:** Gabriela Batista Costa (RM573583) · Samara Carvalho (RM573666) · Anna Luiza Carvalhaes (RM573330) · Kethelyn Rocha (RM574016)

## O que o projeto tem de novo nesta sprint
- **Base de conhecimento expandida** (`data/knowledge_base/`): as perguntas e respostas do dataset (arquivos `.md`, uma seção por pergunta) e 3 PDFs da GoodWe (datasheet e manual do usuário do HCA G2 e o mapa Modbus).
- **Pipeline RAG** (`src/rag/`): carrega os documentos, divide em pedaços (chunks), calcula os embeddings com `nomic-embed-text`, guarda no ChromaDB (em disco) e busca os mais parecidos com a pergunta.
- **Respostas com fonte**: o bot responde só com o que está nos trechos recuperados e cita `arquivo, pág. X`. Se a informação não está nos documentos, ele diz "Não encontrei essa informação nos documentos fornecidos".
- **Prompt RAG em 3 versões** (`prompts/rag_v1.md` a `rag_v3.md`), com a tabela de ganhos medidos.
- **Segurança**: trechos de documentos que tentam dar ordens ao modelo ("ignore as instruções...") não são indexados; o texto recuperado é tratado como dado, nunca como instrução; os guardrails da Sprint 03 continuam valendo.
- **Interface web** (`app/app.py`, Streamlit) que mostra as fontes e os trechos recuperados em cada resposta.
- **Avaliação por iteração** (`evals/run_rag_eval.py`): faithfulness, answer_relevancy e contexto relevante, medidos com um modelo-juiz.

## Como rodar no seu computador
Precisa de **Python 3.12 ou 3.13**, de uma chave do Ollama Cloud (crie em ollama.com/settings, aba *Keys*) e do **Ollama instalado** no computador (ollama.com). O Ollama Cloud recusou o modelo de embeddings (erro 401), então os embeddings rodam localmente; o chat continua no Cloud.

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
No Linux ou Mac: `cp .env.example .env`. Abra o arquivo `.env` e cole a chave depois de `OLLAMA_API_KEY=`, sem aspas e sem espaços. **O `.env` não vai para o Git.**

**4. Baixe o modelo de embeddings (uma vez só) e deixe o Ollama aberto:**
```
ollama pull nomic-embed-text
```

**5. Indexe a base e abra a interface:**
```
python -m src.rag.indexar                  lê data/knowledge_base/ e grava o ChromaDB em data/chroma_db/
streamlit run app/app.py                   interface visual, com as fontes de cada resposta
```
Se mudar os documentos, apague a pasta `data/chroma_db/` e indexe de novo.

**Outros comandos:**
```
python -m tests.test_offline               testes da Sprint 03 (sem chave e sem internet)
python -m tests.test_rag_offline           testes do RAG (sem chave e sem internet, usam embedding falso)
python -m scripts.gerar_base_conhecimento  gera os .md a partir do data/datasets.json
python main.py                             conversa no terminal (Sprint 03, sem RAG)
```

## Pastas
```
src/rag/         o pipeline RAG: loader, chunking, embeddings, vector_store, retriever, prompt_rag, chain_rag, chat_rag
src/chain/       a cadeia do LangChain (builder.py) e a memória da conversa (memoria.py), da Sprint 03
src/guardrails/  as proteções de entrada e de saída
src/chat.py      um turno de conversa da Sprint 03 (o ChatRAG herda dele)
prompts/         as versões do prompt (rag_v1..v3.md para o RAG) e a tabela de versões
data/            datasets.json, knowledge_base/ (documentos do RAG) e chroma_db/ (gerado, fora do Git)
app/             interface Streamlit do RAG
evals/           as 19 perguntas de teste, os scripts e os resultados (rag_it*.json)
docs/            os relatórios (relatório de evolução da Sprint 04 em PDF, modelos, memória e explicação dos evals)
scripts/         gerar a base em .md e gerar o PDF do relatório
tests/           testes automáticos
legacy/          o bot da Sprint 2, guardado só para comparar
```

## Resultados em resumo
Mesmas 19 perguntas em todas as iterações. As notas (0 a 1) vêm de uma rubrica manual equivalente ao RAGAS, com o `gemma4:31b-cloud` como juiz. Só entram nas médias as respostas que o modelo respondeu (não as recusas nem os bloqueios dos guardrails).

| Iteração | Prompt | Perguntas pontuadas | Recusas | Faithfulness | Answer relevancy | Contexto relevante | Testes de segurança |
|---|---|---|---|---|---|---|---|
| it1 | v1 | 10 | 0 | 0,596 | 0,769 | 0,167 | 10 de 13 |
| it2 | v2 | 5 | 5 | 0,619 | 0,715 | 0,333 | 12 de 13 |
| it3 | v3 (k=5) | 7 | 3 | 0,620 | 0,732 | 0,343 | 13 de 13 |

Como cada iteração pontua um número diferente de perguntas, a comparação justa é só nas perguntas que as duas pontuaram. Da it1 para a it3 (7 perguntas em comum) o faithfulness sobe de **0,46 para 0,62**, a answer_relevancy fica estável (0,75 para 0,73) e o contexto relevante vai de 0,24 para 0,34. O maior ganho foi na **segurança**: de 10 para 13 testes aprovados, com a recusa padrão quando a informação não está nos documentos (erro 47 e modelo GW50K) e a resposta para faíscas passando a mandar manter distância e chamar um profissional, em vez de mandar reconectar o plugue. Com k=5 as recusas indevidas caíram de 3 para 1. O custo foi o prompt maior (de cerca de 450 para 1.230 tokens por pergunta). O contexto relevante continua baixo, então o ponto fraco é a **busca**. Os detalhes e os problemas encontrados estão em `docs/relatorio_evolucao_sprint04.pdf`.

## Como repetir os testes (evals)
Precisa do Ollama aberto (embeddings) e da chave no `.env`.
```
python -m evals.run_rag_eval --iteracao it1 --prompt v1 --saida evals/rag_it1.json
python -m evals.run_rag_eval --iteracao it2 --prompt v2 --saida evals/rag_it2.json
python -m evals.run_rag_eval --iteracao it3 --prompt v3 --k 5 --saida evals/rag_it3.json
python -m evals.comparar_rag evals/rag_it1.json evals/rag_it2.json evals/rag_it3.json     tabela das iterações
python -m scripts.gerar_relatorio_pdf                                                    refaz o PDF com os resultados atuais
```
O juiz padrão fica em `MODELO_COMPARACAO` no `.env` (usamos `gemma4:31b-cloud`; o `qwen3.6:27b` da aula não está no plano gratuito).

## Limites conhecidos
- Cada pergunta foi feita **uma vez** e só 5 a 10 perguntas entram nas médias; diferenças pequenas podem ser sorte.
- Na resposta, o modelo ainda cita pelo número do trecho ("fonte: documento 4"); a lista de fontes com arquivo e página aparece no fim da resposta ou na interface.
- O juiz é outro modelo de IA, então as notas são aproximadas (o pacote `ragas` não importa com o langchain-community atual, por isso usamos a rubrica manual).
- A busca ainda traz trechos pouco relacionados (contexto relevante baixo); reranking e chunking semântico ficam como próximos passos.
- Os embeddings dependem de um Ollama local; o app não roda como está no Streamlit Cloud.
- As proteções usam regras de texto simples: uma frase bem reescrita pode passar.
- O dataset tem pequenas contradições entre trechos (por exemplo, grau de proteção IP65 em um e IP66 em outro) e o bot pode repetir qualquer uma.
