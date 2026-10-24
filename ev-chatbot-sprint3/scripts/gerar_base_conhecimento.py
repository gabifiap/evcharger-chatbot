"""Converte data/datasets.json (base da Sprint 2) em arquivos .md dentro de data/knowledge_base/.
Cada pergunta/resposta vira uma seção "## ..." (o loader do RAG usa essas seções como unidade de busca).
Os manuais em PDF entram na mesma pasta, é só copiar o arquivo para lá.
Uso: python -m scripts.gerar_base_conhecimento"""
import json

from src.config import DATA_DIR, KB_DIR
from src.knowledge import _pares

ARQUIVOS = {
    "data_comercial": "gestao_comercial.md",
    "data_instalacao": "instalacao.md",
    "data_manutencao": "manutencao.md",
    "data_erros_tecnicos": "erros_tecnicos.md",
    "data_1": "complementar_1.md",
    "data_2": "complementar_2.md",
    "data_3": "complementar_3.md",
}


def main():
    dados = json.loads((DATA_DIR / "datasets.json").read_text(encoding="utf-8"))
    KB_DIR.mkdir(parents=True, exist_ok=True)
    for chave in dados["_ordem"]:
        obj, titulo = dados[chave], dados["_titulos"][chave].capitalize()
        linhas = [f"# {titulo}"]
        if isinstance(obj, dict) and "contexto" in obj:
            linhas.append(f"Contexto: {obj['contexto']}")
        if chave == "data_erros_tecnicos":
            for c, f, ct, s in zip(obj["codigo"], obj["falha"], obj["causa_tecnica"], obj["solucao_chatbot"]):
                linhas.append(f"\n## Erro E{c} - {f}\nCausa técnica: {ct}\nSolução: {s}")
        else:
            for p, r in _pares(obj):
                linhas.append(f"\n## {p}\n{r}")
        (KB_DIR / ARQUIVOS[chave]).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print("gerado", ARQUIVOS[chave])


if __name__ == "__main__":
    main()
