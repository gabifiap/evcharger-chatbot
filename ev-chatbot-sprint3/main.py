"""Chat de terminal (demonstração). Uso: python main.py --versao v3 --model gpt-oss:120b"""
import argparse
import uuid

from src.chat import ChatEV


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versao", default="v3", choices=["v1", "v2", "v3"])
    ap.add_argument("--provider", default="ollama", choices=["ollama", "gemini"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--limite", type=int, default=None, help="max tokens do histórico")
    a = ap.parse_args()

    chat = ChatEV(a.versao, a.provider, a.model, max_tokens_historico=a.limite)
    sid = str(uuid.uuid4())
    print(f"Guia Técnico GoodWe | prompt {a.versao} | {a.provider}:{a.model or 'padrão'}")
    print("Comandos: /consulta <texto> | /historico | /limpar | /sair\n")
    while True:
        try:
            txt = input("você> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not txt:
            continue
        if txt == "/sair":
            break
        if txt == "/limpar":
            chat.memoria.limpar(sid); print("(memória limpa)"); continue
        if txt == "/historico":
            for m in chat.memoria.mensagens(sid):
                print(f"  [{m.type}] {str(m.content)[:100]}")
            print(f"  -> {chat.memoria.tokens(sid)} tokens (limite {chat.memoria.max_token_limit})"); continue
        if txt.startswith("/consulta "):
            obj, erro = chat.consultar(txt[10:])
            print(obj.model_dump_json(indent=2) if obj else f"ERRO: {erro}"); continue
        r = chat.perguntar(txt, sid)
        print(f"\nbot> {r.resposta}\n")
        tag = f"BLOQUEADO ({r.categoria_bloqueio})" if r.bloqueado else f"tokens {r.tokens_prompt}/{r.tokens_resposta} [{r.fonte_tokens}]"
        print(f"     [{r.latencia_s:.1f}s | {tag} | histórico {r.historico_msgs} msgs, {r.historico_tokens} tok"
              + (f" | ajustes {r.ajustes}" if r.ajustes else "") + "]\n")


if __name__ == "__main__":
    main()
