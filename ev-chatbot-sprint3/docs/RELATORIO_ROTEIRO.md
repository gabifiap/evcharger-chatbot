# Roteiro do relatório de evolução (PDF, até 5 páginas) — §8 do enunciado

1. **Resumo da evolução** (½ pág.): Sprint 1 = Colab + Ollama local; Sprint 2 = Streamlit + Gemini (SDK direto), base colada no prompt,
   **sem memória real** (chat novo a cada mensagem; o histórico do Streamlit era só visual). Sprint 03 = LCEL + memória + Pydantic + guardrails.
2. **Refatoração — decisões e trade-offs** (1 pág.): SDK -> `ChatOllama`; `prompt | llm | parser`; duas chains (chat e extração estruturada);
   `RunnableWithMessageHistory` + TokenBuffer com poda própria; contagem com tiktoken (aproximação); APIs *deprecated* exigidas pelo enunciado.
3. **Tabela antes/depois (OBRIGATÓRIA)** (1 pág.): saída de `python -m evals.comparar ...` + os critérios da nota manual.
4. **Problemas encontrados e soluções** (1–1,5 pág.) — candidatos reais deste projeto:
   - Sprint 2 sem memória (nova sessão a cada chamada) -> memória por sessão + teste de 3+ turnos (`demo_memoria.py`).
   - `langchain.memory` não existe no LangChain 1.x -> `langchain-classic`.
   - `RunnableWithMessageHistory` **não aplica** o limite do TokenBuffer (grava direto no histórico) -> `podar()` após cada turno.
   - `ChatOllama` não conta tokens (exige `transformers`) -> tiktoken.
   - Instrução insegura no prompt (`desligar o disjuntor`) vs. exigência de orientar profissional habilitado -> prompt v3 + rodapé de emergência.
   - `.env` com chave commitado no histórico da Sprint 2 -> chave revogada, repositório limpo/novo, `.gitignore`.
   - (Se ocorrer) modelo devolvendo JSON com markdown / `format="json"` com gpt-oss -> parser tolerante / retry.
5. **Equipe e divisão de trabalho**: nome, RM, tarefa principal de cada integrante.

Também: `prompts/VERSOES.md` preenchido (bloco B), `docs/relatorio_modelos.md` preenchido (bloco B), commits regulares de cada integrante,
`.txt` com nome, RM e turma. Antes de entregar: conferir que o histórico do Git não contém chaves.
