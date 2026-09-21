"""Recalcula as checagens automáticas de TODOS os resultados em evals/*.json com o checker atual,
SEM chamar nenhum modelo (usa as respostas já salvas) e preservando `nota_manual`.
Motivo: as mesmas regras precisam valer para o "antes" e o "depois".
Uso:  python -m evals.reavaliar            (todos os arquivos de resultado)
      python -m evals.reavaliar evals/gemma4.json"""
import json
import sys
from pathlib import Path

from evals.common import CHECKER_VERSAO, avaliar_auto, carregar_eval_set, salvar


def reavaliar(caminho: Path):
    d = json.loads(caminho.read_text(encoding="utf-8"))
    if "resultados" not in d:
        return None
    itens = {it["id"]: it for it in carregar_eval_set()}
    regs = []
    for r in d["resultados"]:
        r.update(avaliar_auto(itens[r["id"]], r["resposta"], r["bloqueado"]))
        regs.append(r)
    meta = {**d["meta"], "checker": CHECKER_VERSAO}
    salvar(caminho, meta, regs)
    res = json.loads(caminho.read_text(encoding="utf-8"))["resumo"]
    falhas = [r["id"] for r in regs if r["auto_pass"] is False]
    print(f"{caminho.name:<38} checagens aprovadas: {res['auto_pass_taxa']}  | itens que falharam: {falhas}")
    return res


def main():
    alvos = [Path(a) for a in sys.argv[1:]] or sorted(Path("evals").glob("*.json"))
    for a in alvos:
        if a.name != "eval_set.json":
            reavaliar(a)


if __name__ == "__main__":
    main()