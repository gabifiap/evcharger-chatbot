"""Gera a tabela ANTES/DEPOIS (obrigatória no relatório, §8) em Markdown.
Uso: python -m evals.comparar evals/baseline_sprint2_results.json evals/sprint3_results.json"""
import json
import sys


def _v(x, suf=""):
    return "n/a" if x is None else f"{x}{suf}"


def main():
    a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
    ra, rb = a["resumo"], b["resumo"]
    linhas = [
        ("Qualidade das respostas (nota média manual 0-10)", _v(ra["nota_manual_media"]), _v(rb["nota_manual_media"])),
        ("Checagens automáticas (guardrails/segurança) aprovadas", _v(ra["auto_pass_taxa"]), _v(rb["auto_pass_taxa"])),
        ("Tokens de prompt por turno (estimado, tiktoken)", _v(ra["tokens_prompt_medio_est"]), _v(rb["tokens_prompt_medio_est"])),
        ("Tokens de resposta por turno (estimado)", _v(ra["tokens_resposta_medio_est"]), _v(rb["tokens_resposta_medio_est"])),
        ("Latência média (s)", _v(ra["latencia_media_s"]), _v(rb["latencia_media_s"])),
        ("Structured output: saídas válidas no schema", "n/a (não existia)", _v(rb["structured_validade"])),
        ("Structured output: tipo_consulta correto", "n/a (não existia)", _v(rb["structured_acerto_tipo"])),
    ]
    print(f"| Métrica | Sprints 1/2 ({a['meta']['model']}, {a['meta']['prompt']}) | Sprint 03 ({b['meta']['model']}, {b['meta']['prompt']}) |")
    print("|---|---|---|")
    for m, x, y in linhas:
        print(f"| {m} | {x} | {y} |")
    print(f"\nTokenizador: antes={a['meta']['tokenizador']} | depois={b['meta']['tokenizador']}")


if __name__ == "__main__":
    main()
