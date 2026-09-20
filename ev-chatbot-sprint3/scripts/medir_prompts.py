"""Mede tokens de cada versão de prompt (system + base de conhecimento) -> preencher prompts/VERSOES.md.
Uso: python -m scripts.medir_prompts"""
from src import prompts, tokens


def main():
    print(f"Tokenizador: {tokens.modo()}\n")
    print("| Versão | Tokens (system + base) | Δ vs v1 |\n|---|---|---|")
    base = None
    for v in prompts.VERSOES:
        cfg = prompts.carregar(v)
        n = tokens.contar(cfg["sistema"].replace("{base_conhecimento}", cfg["conhecimento"])) + tokens.contar(cfg["humano"])
        base = base or n
        print(f"| {v} | {n} | {(n - base) / base:+.1%} |")


if __name__ == "__main__":
    main()
