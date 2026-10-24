"""Etapa 1 do RAG (Aula 06): carrega os documentos de data/knowledge_base/.
- .pdf  -> PyMuPDFLoader, uma Document por página (metadata["page"] começa em 0).
- .md   -> uma Document por seção "## ..." (no caso do FAQ, cada pergunta/resposta é uma unidade).
- .txt  -> um Document inteiro.
Todo Document sai com metadata["source"] (nome do arquivo) e metadata["citacao"] (texto pronto para citar)."""
import re
from pathlib import Path

from langchain_core.documents import Document

from src import config

_SECAO = re.compile(r"^## +(.+)$", re.M)


def _pdf(arq: Path) -> list:
    from langchain_community.document_loaders import PyMuPDFLoader

    docs = []
    for d in PyMuPDFLoader(str(arq)).load():
        if not d.page_content.strip():  # página sem texto (imagem escaneada): não adianta indexar
            continue
        pg = int(d.metadata.get("page", 0)) + 1
        d.metadata = {"source": arq.name, "page": pg, "categoria": arq.stem, "citacao": f"{arq.name}, pág. {pg}"}
        docs.append(d)
    return docs


def _markdown(arq: Path) -> list:
    texto = arq.read_text(encoding="utf-8")
    titulo = re.search(r"^# +(.+)$", texto, re.M)
    categoria = titulo.group(1).strip() if titulo else arq.stem
    achados = list(_SECAO.finditer(texto))
    docs = []
    for i, m in enumerate(achados):
        fim = achados[i + 1].start() if i + 1 < len(achados) else len(texto)
        secao, corpo = m.group(1).strip(), texto[m.end():fim].strip()
        meta = {"source": arq.name, "secao": secao, "categoria": categoria,
                "citacao": f'{arq.name}, seção "{secao[:70]}"'}
        docs.append(Document(page_content=f"{secao}\n{corpo}", metadata=meta))
    if not docs and texto.strip():  # md sem "##": vira um Document só
        docs.append(Document(page_content=texto.strip(), metadata={
            "source": arq.name, "categoria": categoria, "citacao": arq.name}))
    return docs


def _txt(arq: Path) -> list:
    texto = arq.read_text(encoding="utf-8").strip()
    return [Document(page_content=texto, metadata={"source": arq.name, "categoria": arq.stem, "citacao": arq.name})] if texto else []


_LEITORES = {".pdf": _pdf, ".md": _markdown, ".txt": _txt}


def carregar_documentos(pasta=None) -> list:
    pasta = Path(pasta or config.KB_DIR)
    docs = []
    for arq in sorted(pasta.rglob("*")):
        leitor = _LEITORES.get(arq.suffix.lower())
        if leitor and arq.is_file() and not arq.name.startswith("_"):  # "_nome" = arquivo ignorado
            docs.extend(leitor(arq))
    return docs
