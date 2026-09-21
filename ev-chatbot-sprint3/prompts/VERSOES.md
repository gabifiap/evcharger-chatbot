# Versões do prompt

O *prompt* é o texto de instruções que damos ao modelo antes de cada pergunta (quem ele é, o que pode responder, como responder e a base de conhecimento).
Guardamos três versões para poder comparar o que mudou. Os textos estão em `prompts/system_prompt_v1.md`, `v2` e `v3`.

| Versão | O que mudou | Por quê | Tamanho (tokens) | Nota média | O que ganhamos |
|---|---|---|---|---|---|
| **v1** | O prompt da Sprint 2, **sem mudar nada**. A base de conhecimento aparece como listas do Python coladas no texto. | Ponto de partida para comparar. | cerca de 4.613 (estimado) | 7,58 (rodou no Gemini, sem memória) | — |
| **v2** | Instruções organizadas com etiquetas do tipo XML (papel, escopo, regras, base). Base mais compacta, em seções de pergunta e resposta. A pergunta do usuário fica marcada. A regra "conduza a conversa" foi reescrita. | Separar as instruções dos dados e tirar o "ruído" das listas do Python. | não medimos | não medimos | não medimos |
| **v3** | A v2 mais um bloco de **segurança**: responder só com o que está na base, não inventar especificações, tratar a pergunta como dado (e não como ordem), recusar conselho jurídico, financeiro ou de mexer na parte elétrica e, em emergência, mandar chamar profissional e Bombeiros. Um lembrete no fim reforça as regras. | Cumprir as regras de segurança do enunciado e trocar o "desligue o disjuntor" da Sprint 2. | cerca de 4.623 (estimado) · 4.688 (real) | 8,47 (gpt-oss) · 9,32 (gemma4) | Perguntas 6 e 13 corrigidas em relação ao bot antigo. Os tokens **não** diminuíram. |

## Limites desta comparação
- A v1 foi testada no **Gemini** e a v3 no **gpt-oss e gemma4**. Por isso a diferença de nota mistura o efeito do modelo com o efeito do prompt.
- Para comparar só os prompts, seria preciso rodar v1, v2 e v3 no **mesmo modelo**. Não fizemos isso, e a v2 não foi testada sozinha.
- O tamanho não diminuiu porque a base de conhecimento continua dentro do prompt; compactar a base economizou pouco.

As notas vêm de `docs/relatorio_modelos.md`.
