"""Configuração central. Credenciais SOMENTE via variável de ambiente / .env (gitignored)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
DATA_DIR = ROOT / "data"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.com")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODELO_PRINCIPAL = os.getenv("MODELO_PRINCIPAL", "gpt-oss:120b")
MODELO_COMPARACAO = os.getenv("MODELO_COMPARACAO", "qwen3.6:27b")
GEMINI_MODEL = "gemini-2.5-flash"

# Parâmetros documentados no relatorio_modelos.md (Sprint 2 usava temperature=0.2, max=2048, sem top_p)
PARAMS_PADRAO = {"temperature": 0.2, "top_p": 0.9, "max_tokens": 1024}
MAX_TOKENS_HISTORICO = int(os.getenv("MAX_TOKENS_HISTORICO", "1000"))
