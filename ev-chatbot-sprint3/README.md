# EV Challenge — GoodWe · Sprint 03 (Refactory em LangChain)

Chatbot técnico para carregadores de veículos elétricos GoodWe / ChargeGrid, reconstruído em **LangChain LCEL**
(`prompt | llm | parser`), com **memória por sessão limitada por tokens**, **structured output Pydantic v2**,
**prompt versionado (XML tagging)**, **medição de tokens (tiktoken)** e **guardrails**.

## Estrutura
```
prompts/    system_prompt_v1..v3.md + VERSOES.md (tabela de versões)
src/chain/  builder.py (LCEL) · memoria.py (RunnableWithMessageHistory + TokenBuffer com poda)
src/schemas/consulta_recarga.py   schema Pydantic v2 (ConsultaRecarga)
src/guardrails/  scope_validator.py (entrada) · moderation.py (saída)
src/chat.py      orquestra 1 turno: guardrail -> chain -> guardrail -> memória
evals/      eval_set.json · run_eval.py · run_baseline_sprint2.py · comparar.py · *_results.json
docs/       relatorio_modelos.md · RELATORIO_ROTEIRO.md (relatório de evolução, PDF)
legacy/     bot_sprint2.py (Sprint 2 original, preservado só para medir o "antes")
tests/      test_offline.py (sem rede, sem chave)
```

## Instalação
```
python -m venv .venv && .venv\Scripts\activate      # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env                              # Linux/Mac: cp .env.example .env  -> preencha OLLAMA_API_KEY
python -m tests.test_offline                        # deve terminar com "61 verificações OK"
```

## Uso
```
python main.py --versao v3                          # chat no terminal (/consulta, /historico, /limpar, /sair)
python demo_memoria.py --limite 250                 # evidência de memória (3+ turnos) e da poda por tokens
python -m scripts.medir_prompts                     # tokens de cada versão de prompt -> prompts/VERSOES.md
```

## Como gerar as evidências do relatório (ordem importa)
1. **Antes (baseline):** `python -m evals.run_baseline_sprint2` (precisa de `GEMINI_API_KEY` **nova** e `pip install google-genai`).
2. **Depois:** `python -m evals.run_eval --versao v3 --saida evals/sprint3_results.json`
3. **Notas:** abra os dois JSON e preencha `nota_manual` (0–10) por item, com os **mesmos critérios** antes/depois
   (correção factual vs. base, segurança, escopo, concisão). Anote os critérios no relatório.
4. **Tabela antes/depois:** `python -m evals.comparar evals/baseline_sprint2_results.json evals/sprint3_results.json`
5. **Modelos (relatorio_modelos.md):** repita o passo 2 com `--model qwen3.6:27b` (e `--provider gemini` p/ o bônus),
   `--saida evals/results_<modelo>.json`.
6. **Versões de prompt:** repita o passo 2 com `--versao v1`, `v2`, `v3` e preencha `prompts/VERSOES.md`.

## Limitações conhecidas (declare no relatório)
- Guardrails de entrada são **regex**: bloqueiam os padrões testados, mas reformulações criativas podem passar.
  O eval de jailbreak foi escrito junto com as regras — **adicionem ataques mais difíceis** antes de concluir que funciona.
- `tiktoken` é aproximação para modelos do Ollama (vocabulário OpenAI).
- `RunnableWithMessageHistory` e `ConversationTokenBufferMemory` são *deprecated* (exigidos pelo enunciado).
- A checagem anti-invenção só cobre **códigos de produto completos** (ex.: `GW50K-HCA-20`), não valores numéricos errados.
- O `tipo_esperado` do eval é rótulo sugerido: revisem.

## Segurança
`.env` está no `.gitignore`. **Nunca** commite chaves. Antes de entregar: `git log -p | grep -Ei "api_key|AIza|AQ\."`.
