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

# --- RAG (Sprint 04) ---
KB_DIR = DATA_DIR / "knowledge_base"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(DATA_DIR / "chroma_db")))
MODELO_EMBEDDING = os.getenv("MODELO_EMBEDDING", "nomic-embed-text")
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "800"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))
RAG_K = int(os.getenv("RAG_K", "3"))
RAG_PROMPT = os.getenv("RAG_PROMPT", "v3")
