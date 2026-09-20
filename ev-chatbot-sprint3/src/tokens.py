"""Medição de tokens com tiktoken (item 4 do enunciado).

ATENÇÃO: tiktoken usa vocabulários da OpenAI. Para modelos servidos pelo Ollama
(gpt-oss, qwen...) a contagem é uma APROXIMAÇÃO — registre isso no relatório.
Usamos `o200k_base` (família do gpt-oss). Se o vocabulário não puder ser baixado
(sem internet), cai para uma estimativa por caracteres e `modo()` informa isso.
"""
from typing import Iterable

_enc = None
_modo = None


def _carregar():
    global _enc, _modo
    if _modo is not None:
        return
    try:
        import tiktoken

        _enc = tiktoken.get_encoding("o200k_base")
        _modo = "tiktoken:o200k_base"
    except Exception:  # sem rede / sem pacote
        _enc = None
        _modo = "aproximado:caracteres/3.5"


def modo() -> str:
    _carregar()
    return _modo


def contar(texto: str) -> int:
    _carregar()
    if not texto:
        return 0
    if _enc is not None:
        return len(_enc.encode(texto, disallowed_special=()))
    return max(1, round(len(texto) / 3.5))


def _texto(msg) -> str:
    c = getattr(msg, "content", msg)
    return c if isinstance(c, str) else str(c)


def contar_mensagens(msgs: Iterable) -> int:
    """Soma tokens das mensagens + pequeno overhead por mensagem (formato de chat)."""
    msgs = list(msgs)
    return sum(contar(_texto(m)) + 4 for m in msgs) + (2 if msgs else 0)
