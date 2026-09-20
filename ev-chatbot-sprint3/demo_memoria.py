"""Evidência de memória (rubrica A: 3+ turnos). Uso: python demo_memoria.py [--limite 250]
Com --limite baixo dá para VER a janela deslizante descartando mensagens antigas."""
import argparse

from src.chat import ChatEV

TURNOS = [
    "Meu posto tem 3 carregadores GW11K-HCA-20 e o disjuntor geral é limitado.",
    "O que o controle dinâmico de carga faz nessa situação?",
    "E se um deles mostrar uma luz vermelha piscando?",
    "Qual era o modelo dos carregadores que eu citei no início da conversa?",
]

ap = argparse.ArgumentParser()
ap.add_argument("--versao", default="v3")
ap.add_argument("--provider", default="ollama")
ap.add_argument("--model", default=None)
ap.add_argument("--limite", type=int, default=None)
a = ap.parse_args()

chat = ChatEV(a.versao, a.provider, a.model, max_tokens_historico=a.limite)
for i, t in enumerate(TURNOS, 1):
    r = chat.perguntar(t, "demo")
    print(f"\n--- turno {i} ---\nuser: {t}\nbot: {r.resposta}")
    print(f"[histórico: {r.historico_msgs} msgs, {r.historico_tokens} tok / limite {chat.memoria.max_token_limit} | "
          f"prompt {r.tokens_prompt} tok | {r.latencia_s:.1f}s]")
