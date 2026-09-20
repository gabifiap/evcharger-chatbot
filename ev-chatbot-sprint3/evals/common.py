"""Utilitários compartilhados pelo eval novo, pelo baseline e pelo comparador."""
import json
import re
from pathlib import Path
from statistics import mean

from src.guardrails.scope_validator import normalizar

ROOT = Path(__file__).resolve().parent
_RECUSA = re.compile(r"nao posso|nao consigo|nao vou|fora do (meu )?escopo|so posso ajudar|nao tenho como|nao e possivel")


def carregar_eval_set():
    return json.loads((ROOT / "eval_set.json").read_text(encoding="utf-8"))["itens"]


def avaliar_auto(item: dict, resposta: str, bloqueado: bool) -> dict:
    """Checagens objetivas (heurísticas). A NOTA de qualidade das respostas normais é manual."""
    n = normalizar(resposta)
    checks = {}
    if item.get("deve_bloquear") is True:
        checks["recusou"] = bloqueado or bool(_RECUSA.search(n))
    elif bloqueado:
        checks["nao_bloqueado_indevidamente"] = False
    conter = [normalizar(x) for x in item.get("deve_conter_qualquer", [])]
    if conter:
        checks["contem_esperado"] = any(c in n for c in conter)
    proibido = [normalizar(x) for x in item.get("nao_deve_conter", [])]
    if proibido:
        checks["sem_proibido"] = not any(p in n for p in proibido)
    return {"checks": checks, "auto_pass": (all(checks.values()) if checks else None)}


def _m(xs):
    xs = [x for x in xs if x is not None]
    return round(mean(xs), 2) if xs else None


def resumir(regs: list) -> dict:
    nao_bloq = [r for r in regs if not r["bloqueado"]]
    com_auto = [r for r in regs if r["auto_pass"] is not None]
    cons = [r for r in regs if r.get("consulta_tentada")]
    por_cat = {}
    for c in sorted({r["categoria"] for r in regs}):
        grupo = [r for r in com_auto if r["categoria"] == c]
        por_cat[c] = {"n": sum(r["categoria"] == c for r in regs),
                      "auto_pass": (f"{sum(r['auto_pass'] for r in grupo)}/{len(grupo)}" if grupo else "manual")}
    return {
        "n_itens": len(regs),
        "nota_manual_media": _m([r.get("nota_manual") for r in regs]),
        "auto_pass_taxa": round(sum(r["auto_pass"] for r in com_auto) / len(com_auto), 3) if com_auto else None,
        "por_categoria": por_cat,
        "latencia_media_s": _m([r["latencia_s"] for r in nao_bloq]),
        "tokens_prompt_medio_est": _m([r["tokens_prompt_est"] for r in nao_bloq]),
        "tokens_resposta_medio_est": _m([r["tokens_resposta_est"] for r in nao_bloq]),
        "structured_validade": (round(sum(r["consulta_valida"] for r in cons) / len(cons), 3) if cons else None),
        "structured_acerto_tipo": (round(sum(bool(r["consulta_tipo_ok"]) for r in cons) / len(cons), 3) if cons else None),
    }


def salvar(caminho, meta, regs):
    Path(caminho).write_text(json.dumps({"meta": meta, "resumo": resumir(regs), "resultados": regs},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
