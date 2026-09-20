"""Base de conhecimento (datasets da Sprint 2), renderizada de duas formas:
- `repr`: idêntica à Sprint 2 (dicionários Python colados no prompt) -> baseline / prompt v1
- `xml` : compacta, em seções com tags -> prompts v2/v3 (menos tokens, mais legível para o modelo)
"""
import json
import re
from functools import lru_cache

from src.config import DATA_DIR


@lru_cache(maxsize=1)
def _dados() -> dict:
    with open(DATA_DIR / "datasets.json", encoding="utf-8") as f:
        return json.load(f)


def render_repr() -> str:
    d = _dados()
    txt = "\n--- BASES DE CONHECIMENTO DO PROJETO ---\n"
    for k in d["_ordem"]:
        txt += f"\n {d['_titulos'][k].upper()}:\n{d[k]}\n"
    return txt


def _pares(obj):
    """Normaliza os formatos de dataset em lista de (pergunta, resposta)."""
    if isinstance(obj, list):
        return [(x["pergunta"], x["resposta"]) for x in obj]
    return list(zip(obj["pergunta"], obj["resposta"]))


def render_xml() -> str:
    d = _dados()
    partes = []
    for k in d["_ordem"]:
        obj, titulo = d[k], d["_titulos"][k]
        if k == "data_erros_tecnicos":
            linhas = [
                f"E{c} | {f} | causa: {ct} | solução: {s}"
                for c, f, ct, s in zip(obj["codigo"], obj["falha"], obj["causa_tecnica"], obj["solucao_chatbot"])
            ]
            partes.append(f'<secao nome="{titulo}">\n' + "\n".join(linhas) + "\n</secao>")
        else:
            ctx = f' contexto="{obj["contexto"]}"' if isinstance(obj, dict) and "contexto" in obj else ""
            linhas = [f"P: {p}\nR: {r}" for p, r in _pares(obj)]
            partes.append(f'<secao nome="{titulo}"{ctx}>\n' + "\n".join(linhas) + "\n</secao>")
    return "\n".join(partes)


_COD_MODELO = re.compile(r"\bGW\d+K?(?:-[A-Z0-9]+)+\b")


@lru_cache(maxsize=1)
def codigos_modelo_conhecidos() -> frozenset:
    """Códigos completos de produto (ex.: GW7K-HCA-20) que existem na base."""
    return frozenset(_COD_MODELO.findall(json.dumps(_dados(), ensure_ascii=False)))


def extrair_codigos_modelo(texto: str) -> set:
    return set(_COD_MODELO.findall(texto or ""))
