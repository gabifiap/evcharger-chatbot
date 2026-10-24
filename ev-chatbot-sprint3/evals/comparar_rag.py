"""Monta a tabela de iterações (markdown) a partir dos JSON do run_rag_eval. Cole em docs/relatorio_rag.md.
Uso: python -m evals.comparar_rag evals/rag_antes_s2.json evals/rag_it1.json evals/rag_it2.json evals/rag_it3.json"""
import json
import sys
from pathlib import Path

COLS = [("faithfulness", "faithfulness"), ("answer_relevancy", "answer_relevancy"), ("context_relevance", "contexto relevante"),
        ("citacao_pct", "com citação"), ("auto_pass_taxa", "testes de segurança"), ("latencia_media_s", "latência (s)")]


def main(caminhos):
    runs = [json.loads(Path(c).read_text(encoding="utf-8")) for c in caminhos]
    print("| Iteração | Prompt | chunk/overlap/k | " + " | ".join(n for _, n in COLS) + " |")
    print("|---|---|---|" + "---|" * len(COLS))
    ant = None
    for r in runs:
        m, s = r["meta"], r["resumo"]
        cfg = f"{m.get('chunk_size', '-')}/{m.get('chunk_overlap', '-')}/{m.get('k', '-')}"
        cel = []
        for k, _ in COLS:
            v = s.get(k)
            d = f" ({v - ant[k]:+.2f})" if ant and v is not None and ant.get(k) is not None and k != "latencia_media_s" else ""
            cel.append("-" if v is None else f"{v}{d}")
        print(f"| {m['rotulo']} | {m.get('prompt', 'sem RAG')} | {cfg} | " + " | ".join(cel) + " |")
        ant = s


if __name__ == "__main__":
    main(sys.argv[1:])
