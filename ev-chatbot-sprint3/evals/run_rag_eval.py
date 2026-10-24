"""Eval do RAG (Sprint 04): roda as 19 perguntas do eval_set no ChatRAG e mede faithfulness, answer_relevancy,
context_relevance (juiz LLM), presença de citação e os testes automáticos de segurança.
Cada execução é uma ITERAÇÃO (prompt + chunking + k). Precisa de OLLAMA_API_KEY.

  python -m evals.run_rag_eval --iteracao it1 --prompt v1 --saida evals/rag_it1.json
  python -m evals.run_rag_eval --iteracao it2 --prompt v2 --saida evals/rag_it2.json
  python -m evals.run_rag_eval --iteracao it3 --prompt v3 --chunk-size 500 --overlap 50 --k 4 --saida evals/rag_it3.json
  python -m evals.run_rag_eval --iteracao it3-qwen --prompt v3 --model qwen3.6:27b --saida evals/rag_it3_qwen.json

Antes/depois: pontua respostas JÁ existentes (bot da Sprint 2 ou 3) usando a base inteira como "contexto", que é o
que esses bots tinham no prompt:
  python -m evals.run_rag_eval --iteracao antes-s2 --de-json evals/baseline_sprint2_results.json --saida evals/rag_antes_s2.json"""
import argparse
import json
from pathlib import Path
from statistics import mean

from evals.common import avaliar_auto, carregar_eval_set
from evals.rag_metricas import avaliar
from src import config, tokens
from src.chain.builder import build_llm
from src.guardrails.scope_validator import normalizar
from src.knowledge import render_xml
from src.rag.embeddings import build_embeddings


def _m(xs):
    xs = [x for x in xs if x is not None]
    return round(mean(xs), 3) if xs else None


def resumir(regs):
    pont = [r for r in regs if r.get("faithfulness") is not None or r.get("answer_relevancy") is not None]
    com_auto = [r for r in regs if r["auto_pass"] is not None]
    resp = [r for r in regs if not r["bloqueado"]]
    return {
        "n_itens": len(regs), "n_pontuados": len(pont), "n_recusas_modelo": sum(bool(r.get("recusou_modelo")) for r in regs),
        "faithfulness": _m(r.get("faithfulness") for r in regs),
        "answer_relevancy": _m(r.get("answer_relevancy") for r in regs),
        "context_relevance": _m(r.get("context_relevance") for r in regs),
        "citacao_pct": round(sum(bool(r["tem_citacao"]) for r in resp if not r.get("recusou_modelo")) /
                             max(1, sum(1 for r in resp if not r.get("recusou_modelo"))), 3) if resp else None,
        "auto_pass_taxa": round(sum(r["auto_pass"] for r in com_auto) / len(com_auto), 3) if com_auto else None,
        "latencia_media_s": _m(r["latencia_s"] for r in resp), "tokens_prompt_medio": _m(r.get("tokens_prompt_est") for r in resp),
    }


def _tem_citacao(txt):
    n = normalizar(txt)
    return "(fonte:" in n or "fontes consultadas" in n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteracao", required=True)
    ap.add_argument("--prompt", default=config.RAG_PROMPT)
    ap.add_argument("--chunk-size", type=int, default=None)
    ap.add_argument("--overlap", type=int, default=None)
    ap.add_argument("--k", type=int, default=None)
    ap.add_argument("--provider", default="ollama")
    ap.add_argument("--model", default=None)
    ap.add_argument("--juiz", default=config.MODELO_COMPARACAO, help="modelo do LLM-juiz (padrão: qwen3.6:27b, como na Aula 07)")
    ap.add_argument("--de-json", default=None, help="pontua respostas de um JSON antigo em vez de rodar o RAG")
    ap.add_argument("--sem-juiz", action="store_true", help="só gera as respostas (não gasta cota com o juiz)")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()

    juiz = None if a.sem_juiz else build_llm("ollama", a.juiz, temperature=0, max_tokens=1024, json_mode=True)
    emb = None if a.sem_juiz else build_embeddings()
    itens = carregar_eval_set()
    regs = []

    if a.de_json:
        antigos = {r["id"]: r for r in json.loads(Path(a.de_json).read_text(encoding="utf-8"))["resultados"]}
        base_toda = [render_xml()]
        for it in itens:
            r = antigos[it["id"]]
            reg = {k: r[k] for k in ("id", "categoria", "origem", "pergunta", "resposta", "bloqueado", "latencia_s", "tokens_prompt_est")}
            reg.update(avaliar_auto(it, r["resposta"], r["bloqueado"]))
            regs.append((reg, base_toda))
        meta_extra = {"origem_respostas": a.de_json, "contexto": "base de conhecimento inteira (sem retrieval)"}
    else:
        from src.rag import ChatRAG

        chat = ChatRAG(a.prompt, a.provider, a.model, k=a.k, chunk_size=a.chunk_size, chunk_overlap=a.overlap)
        for it in itens:
            r = chat.perguntar(it["pergunta"], session_id=f"rag-{a.iteracao}-{it['id']}")
            reg = {**{k: it[k] for k in ("id", "categoria", "origem", "pergunta")}, **r.dict(), **avaliar_auto(it, r.resposta, r.bloqueado)}
            regs.append((reg, [f["trecho"] for f in r.fontes]))
            print(f"[{it['id']:>2}] {it['categoria']:<14} bloq={r.bloqueado!s:<5} pass={reg['auto_pass']} {r.latencia_s:.1f}s")
        meta_extra = {"prompt": a.prompt, "chunk_size": a.chunk_size or config.RAG_CHUNK_SIZE,
                      "chunk_overlap": config.RAG_CHUNK_OVERLAP if a.overlap is None else a.overlap,
                      "k": a.k or config.RAG_K, "provider": a.provider, "model": a.model or config.MODELO_PRINCIPAL,
                      "params": config.PARAMS_PADRAO}

    final = []
    for reg, ctx in regs:
        reg["tem_citacao"] = _tem_citacao(reg["resposta"])
        reg["recusou_modelo"] = (not reg["bloqueado"]) and "nao encontrei" in normalizar(reg["resposta"])
        if juiz and not reg["bloqueado"] and not reg["recusou_modelo"]:
            reg.update(avaliar(juiz, emb, reg["pergunta"], reg["resposta"], ctx))
        final.append(reg)
        print(f"  [{reg['id']:>2}] faith={reg.get('faithfulness')} rel={reg.get('answer_relevancy')} ctx={reg.get('context_relevance')}")

    meta = {"rotulo": a.iteracao, "metodo": "manual (LLM-juiz equivalente ao RAGAS)", "juiz": a.juiz, "tokenizador": tokens.modo(), **meta_extra}
    Path(a.saida).write_text(json.dumps({"meta": meta, "resumo": resumir(final), "resultados": final}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("resumo:", json.dumps(resumir(final), ensure_ascii=False))
    print("salvo em", a.saida)


if __name__ == "__main__":
    main()
