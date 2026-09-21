# Evidência da memória da conversa

O enunciado pede que a memória funcione em pelo menos 3 turnos. Fizemos uma conversa de 4 perguntas na mesma sessão, com o prompt v3 e o modelo gpt-oss:120b (comando `python demo_memoria.py`).
A 4ª pergunta testa se o bot lembra do que foi dito na 1ª. Repetimos a conversa com dois limites de memória, medidos em tokens (pedaços de palavras).

**As 4 perguntas:**
1. "Meu posto tem 3 carregadores GW11K-HCA-20 e o disjuntor geral é limitado."
2. "O que o controle dinâmico de carga faz nessa situação?"
3. "E se um deles mostrar uma luz vermelha piscando?"
4. "Qual era o modelo dos carregadores que eu citei no início da conversa?" ← testa a memória do turno 1

## Execução A: limite de 1.000 tokens (o bot esqueceu)
| Turno | Memória depois da resposta | Texto enviado ao modelo | Tempo |
|---|---|---|---|
| 1 | 2 mensagens · 603 tokens | 4.690 tokens | 3,7 s |
| 2 | 4 mensagens · 749 tokens | 5.282 tokens | 1,1 s |
| 3 | **2 mensagens** · 862 tokens (os turnos 1 e 2 foram apagados) | 5.429 tokens | 3,4 s |
| 4 | 4 mensagens · 962 tokens | 5.544 tokens | 4,1 s |

**Resposta real no turno 4:** "Não foi mencionado nenhum modelo de carregador na sua mensagem anterior. Caso precise de informações sobre os modelos disponíveis (por exemplo, GW7K‑HCA‑20, GW11K‑HCA‑20 ou GW22K‑HCA‑20), […]"

**O que isso mostra:** quando a memória passou de 1.000 tokens, as mensagens mais antigas foram apagadas e o bot esqueceu o turno 1. O limite funciona, mas 1.000 tokens é pouco para respostas de 400 a 800 tokens.

## Execução B: limite de 3.000 tokens (o bot lembrou)
| Turno | Memória depois da resposta | Texto enviado ao modelo | Tempo |
|---|---|---|---|
| 1 | 2 mensagens · 155 tokens | 4.690 tokens | 2,3 s |
| 2 | 4 mensagens · 400 tokens | 4.834 tokens | 2,1 s |
| 3 | 6 mensagens · 1.224 tokens | 5.080 tokens | 4,1 s |
| 4 | 8 mensagens · 1.268 tokens | 5.910 tokens | 0,9 s |

**Resposta real no turno 4:** "Os carregadores citados são do modelo **GW11K‑HCA‑20**."

**O que isso mostra:** com 3.000 tokens o bot recuperou a informação do turno 1. O custo é que o texto enviado cresce a cada turno (de 4.690 para 5.910 tokens), porque o histórico é reenviado inteiro.

## Conclusão
- A memória por sessão funciona em 4 turnos, com limite de tokens que realmente apaga as mensagens antigas (execução A).
- Limite maior significa mais contexto, mas também mais tokens por pergunta.
- As respostas mudam de uma execução para outra (temperature 0,2, sem semente fixa): o turno 1 foi longo na execução A e curto na B.

*As respostas completas do bot foram resumidas; as medidas e o turno 4 são as saídas reais. Na execução A, a linha do usuário do turno 4 saiu cortada na cópia do terminal e foi restaurada a partir do arquivo `demo_memoria.py`.*
