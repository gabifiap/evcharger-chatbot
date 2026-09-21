"""Roda o mesmo eval no bot original da Sprint 2 (Gemini + prompt v1 + sem memória) -> coluna "antes".
Requer: pip install google-genai  e  GEMINI_API_KEY no .env (chave nova).
Tokens são estimados com tiktoken (o bot legado não expõe usage_metadata): prompt completo + pergunta.
Uso: python -m evals.run_baseline_sprint2"""
import argparse
import time

from evals.common import avaliar_auto, carregar_eval_set, salvar
from src import tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="evals/baseline_sprint2_results.json")
    a = ap.parse_args()
    from legacy.bot_sprint2 import PROMPT_GEMINI_COMPLETO, responder_usuario  # importa só aqui (exige a chave)

    base_tok = tokens.contar(PROMPT_GEMINI_COMPLETO)
    regs = []
    for it in carregar_eval_set():
        t0 = time.perf_counter()
        resp = responder_usuario(it["pergunta"])
        lat = time.perf_counter() - t0
        reg = {**{k: it[k] for k in ("id", "categoria", "origem", "pergunta")},
               "resposta": resp, "bloqueado": False, "categoria_bloqueio": None, "latencia_s": lat,
               "tokens_prompt_est": base_tok + tokens.contar(it["pergunta"]), "tokens_resposta_est": tokens.contar(resp),
               **avaliar_auto(it, resp, False), "nota_manual": None, "consulta_tentada": False}
        regs.append(reg)
        print(f"[{it['id']:>2}] {it['categoria']:<14} pass={reg['auto_pass']} {lat:.1f}s")
    salvar(a.saida, {"rotulo": "sprint2-baseline", "provider": "gemini", "model": "gemini-2.5-flash",
                     "prompt": "v1 (legado, sem memória)", "tokenizador": tokens.modo()}, regs)
    print("salvo em", a.saida)


if __name__ == "__main__":
    main()
