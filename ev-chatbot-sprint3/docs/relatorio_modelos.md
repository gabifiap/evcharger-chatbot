# Relatório de uso de modelos e parâmetros

Mesmo eval (`evals/eval_set.json`), mesmo prompt (v3), mesma chain. Preencha com os JSON de `evals/`.

## Parâmetros documentados
| Parâmetro | Sprint 2 (Gemini) | Sprint 03 | Efeito / justificativa |
|---|---|---|---|
| temperature | 0.2 | 0.2 | Baixa: respostas técnicas devem ser consistentes e factuais |
| top_p | não configurado (padrão da API) | 0.9 | Corta a cauda improvável sem engessar o texto |
| max_tokens | `max_output_tokens=2048` | `num_predict=1024` (Ollama) | Respostas devem ser sucintas; limita custo e latência |

## Comparativo de modelos
| Modelo | Provider | Nota manual média | Auto-pass (guardrails) | Structured: válidas | Structured: tipo correto | Tokens prompt/turno | Latência média (s) |
|---|---|---|---|---|---|---|---|
| gpt-oss:120b | Ollama Cloud | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ |
| qwen3.6:27b | Ollama Cloud | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ |
| gemini-2.5-flash (bônus) | Google | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ | _preencher_ |

## Análise (preencher)
- Qual modelo seguiu melhor o schema? Houve `OutputParserException` (ex.: JSON com markdown)?
- Diferença de latência: lembre que Gemini (Google) e Ollama Cloud têm infraestruturas diferentes; a comparação de latência **não é** só do modelo.
- Bônus multi-provider (+1): rodar **mais de um modelo e mais de um prompt** (ex.: {gpt-oss, gemini} × {v2, v3}) e citar a tabela.
