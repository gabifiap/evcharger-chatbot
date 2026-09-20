"""Roda o eval na versão refatorada (LCEL).
Uso: python -m evals.run_eval --versao v3 --model gpt-oss:120b --saida evals/sprint3_results.json
Depois: abra o JSON e preencha "nota_manual" (0-10) em cada item; rode `python -m evals.comparar`."""
import argparse

from evals.common import avaliar_auto, carregar_eval_set, salvar
from src import tokens
from src.chat import ChatEV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", default="v3")
    ap.add_argument("--provider", default="ollama")
    ap.add_argument("--model", default=None)
    ap.add_argument("--saida", default="evals/sprint3_results.json")
    ap.add_argument("--sem-consulta", action="store_true", help="pula a chain de structured output")
    a = ap.parse_args()

    chat = ChatEV(a.versao, a.provider, a.model)
    regs = []
    for it in carregar_eval_set():
        r = chat.perguntar(it["pergunta"], session_id=f"eval-{it['id']}")  # sessão nova por item
        reg = {**{k: it[k] for k in ("id", "categoria", "origem", "pergunta")}, **r.dict(),
               **avaliar_auto(it, r.resposta, r.bloqueado), "nota_manual": None, "consulta_tentada": False}
        if not a.sem_consulta:
            obj, erro = chat.consultar(it["pergunta"])
            reg.update(consulta_tentada=True, consulta_valida=obj is not None, consulta_erro=erro,
                       consulta=obj.model_dump() if obj else None,
                       consulta_tipo_ok=(obj is not None and obj.tipo_consulta == it.get("tipo_esperado")))
        regs.append(reg)
        print(f"[{it['id']:>2}] {it['categoria']:<14} bloq={r.bloqueado!s:<5} pass={reg['auto_pass']} {r.latencia_s:.1f}s")

    meta = {"rotulo": f"sprint3-{a.versao}", "provider": a.provider, "model": a.model or "padrão",
            "prompt": a.versao, "tokenizador": tokens.modo()}
    salvar(a.saida, meta, regs)
    print("salvo em", a.saida)


if __name__ == "__main__":
    main()
