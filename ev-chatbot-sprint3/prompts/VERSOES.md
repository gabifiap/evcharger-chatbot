# Versões do system prompt

Meça os tokens com `python -m scripts.medir_prompts` e a nota com o eval (`--versao vN`). Preencha as colunas em branco.

| Versão | O que mudou | Por quê | Tokens (system+base) | Nota média no eval | Ganho medido |
|---|---|---|---|---|---|
| v1 | Prompt da Sprint 2, **sem alterações**; base de conhecimento como dicionários Python colados | Baseline para comparação | _preencher_ | _preencher_ | — |
| v2 | XML tagging (`<papel>`, `<escopo>`, `<regras_de_resposta>`, `<base_conhecimento>`); base compacta em `<secao>` com pares P/R; pergunta do usuário em `<pergunta_usuario>`; regra do "conduza o diálogo" reescrita sem a ambiguidade do v1 | Separar instruções de dados, reduzir ruído de sintaxe Python | _preencher_ (estimativa local: ~-5% vs v1) | _preencher_ | _preencher_ |
| v3 | v2 + bloco `<seguranca>` (só responde com base na `<base_conhecimento>`, não inventa especificação, trata `<pergunta_usuario>` como dado, recusa jurídico/financeiro/elétrico orientando profissional habilitado, protocolo de emergência sem instruir mexer no equipamento) + lembrete final (sandwich) na mensagem do usuário | Exigências de segurança do §6; substituir o "desligue o disjuntor" da Sprint 2 | _preencher_ (estimativa local: ~+0,6% vs v1) | _preencher_ | _preencher_ |

**Observação honesta:** a compactação da base rende pouco (~5%), porque o texto das perguntas/respostas domina o tamanho.
O ganho esperado de v2→v3 é de **segurança/robustez**, não de tokens. Mudanças que afetam o comportamento (ex.: regra 4)
podem alterar a nota — registre o resultado real, seja ele positivo ou negativo.
