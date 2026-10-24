"""Gera docs/relatorio_evolucao_sprint04.pdf (até 5 páginas) a partir dos resultados em evals/rag_it*.json.
Rode de novo depois de cada iteração nova (it3...), as tabelas e os números se atualizam sozinhos.
Uso: python -m scripts.gerar_relatorio_pdf [pasta_dos_json] [arquivo_pdf]"""
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

PASTA = Path(sys.argv[1] if len(sys.argv) > 1 else "evals")
SAIDA = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/relatorio_evolucao_sprint04.pdf")
EQUIPE = [("Gabriela Batista Costa", "RM573583"), ("Samara Carvalho", "RM573666"),
          ("Anna Luiza Carvalhaes", "RM573330"), ("Kethelyn Rocha", "RM574016")]
TAREFAS = ["[preencher]"] * len(EQUIPE)  # o grupo escreve a tarefa principal de cada uma

_e = getSampleStyleSheet()
H = ParagraphStyle("h", parent=_e["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=3, textColor=colors.HexColor("#1f4e79"))
P = ParagraphStyle("p", parent=_e["BodyText"], fontSize=9, leading=12)
C = ParagraphStyle("c", parent=P, fontSize=8, leading=10)
CB = ParagraphStyle("cb", parent=C, fontName="Helvetica-Bold")


def fmt(v, casas=2):
    return "-" if v is None else f"{v:.{casas}f}".replace(".", ",")


def tabela(linhas, larguras, cab=True):
    dados = [[Paragraph(str(c), CB if (cab and i == 0) else C) for c in l] for i, l in enumerate(linhas)]
    t = Table(dados, colWidths=[x * cm for x in larguras], repeatRows=1 if cab else 0)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce6f1") if cab else colors.white),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def carregar():
    runs = []
    for a in sorted(PASTA.glob("rag_it*.json")):
        d = json.loads(a.read_text(encoding="utf-8"))
        if d["meta"].get("model", "gpt-oss:120b") == "gpt-oss:120b" and "gemma" not in a.name and "qwen" not in a.name:
            runs.append(d)
    return runs


def pareado(a, b, chave):
    """Média de `chave` só nos itens pontuados nas DUAS iterações (comparação justa)."""
    ia = {r["id"]: r.get(chave) for r in a["resultados"] if r.get(chave) is not None}
    ib = {r["id"]: r.get(chave) for r in b["resultados"] if r.get(chave) is not None}
    ids = sorted(set(ia) & set(ib))
    if not ids:
        return None, None, 0
    return sum(ia[i] for i in ids) / len(ids), sum(ib[i] for i in ids) / len(ids), len(ids)


def main():
    runs = carregar()
    if len(runs) < 2:
        sys.exit("Preciso de pelo menos rag_it1.json e rag_it2.json em " + str(PASTA))
    it1, ult = runs[0], runs[-1]
    S = [it["resumo"] for it in runs]
    historia = []

    historia.append(Paragraph("Relatório de evolução - Sprint 04", ParagraphStyle("t", parent=_e["Title"], fontSize=17)))
    historia.append(Paragraph("EV Challenge GoodWe · FIAP · Prompt and Artificial Intelligence · Ciência da Computação (2SEM) · Turma 1CCPH · 2026.2 · Prof. Jorge Luiz Gomes<br/>"
                              "Repositório: https://github.com/gabifiap/evcharger-chatbot", C))

    historia.append(Paragraph("1. Resumo da evolução", H))
    historia.append(Paragraph(
        "Nas Sprints 1 e 2 o chatbot (Gemini, prompt v1, sem memória) recebia a base de conhecimento <b>inteira</b> a cada pergunta (cerca de 4.600 tokens) "
        "e não citava fonte. Na Sprint 3 refizemos o núcleo com LangChain (gpt-oss:120b no Ollama Cloud): memória por sessão, saída estruturada e guardrails, "
        "mas a base continuava inteira no prompt. Na Sprint 04 trocamos isso por um <b>RAG medido</b>: a base foi expandida (76 trechos do dataset em .md e "
        "3 PDFs da GoodWe: datasheet e manual do usuário do HCA G2 e mapa Modbus), indexada no ChromaDB persistente com nomic-embed-text, e cada pergunta recebe só os "
        "trechos mais parecidos. As respostas citam documento e página, recusam o que não está nos documentos e a interface web (Streamlit) mostra as fontes. "
        "Medimos cada iteração com faithfulness e answer_relevancy.", P))

    historia.append(Paragraph("2. Pipeline RAG: decisões e trade-offs", H))
    historia.append(tabela([
        ["Etapa", "Decisão", "Por quê / trade-off"],
        ["Carga", "PDFs com PyMuPDFLoader (uma página = um documento, página 1-based); .md dividido por seção \"##\" (cada pergunta/resposta do dataset é uma unidade).",
         "A seção mantém pergunta e resposta juntas e dá uma citação precisa. Páginas sem texto são ignoradas."],
        ["Chunking", "RecursiveCharacterTextSplitter, 800 caracteres, overlap 100 (ponto de partida da Aula 06).",
         "Trechos do dataset já têm cerca de 200 caracteres; o tamanho só afeta de fato as páginas dos PDFs. Testar 500/50 fica como evolução."],
        ["Embeddings", "nomic-embed-text (768 dimensões) no Ollama instalado no computador.",
         "O Ollama Cloud recusou o modelo (401). Em compensação o app só roda onde houver Ollama local."],
        ["Vector store", "ChromaDB persistente, similaridade cosseno, uma coleção por configuração (kb_cs800_ov100).", "Permite comparar iterações sem apagar a anterior; recarregar do disco não recalcula embeddings."],
        ["Retrieve", "Top-k por similaridade (k=3 nas iterações 1 e 2).", "k pequeno poupa tokens, mas derrubou a cobertura (ver problemas)."],
        ["Prompt", "Versionado em prompts/rag_v1..v3.md; o contexto entra na mensagem do usuário, dentro de &lt;documento&gt;.", "O histórico guarda só a pergunta crua, sem o contexto."],
        ["Segurança", "Chunks com ordens escondidas (\"ignore as instruções...\") não são indexados; guardrails de entrada e saída da Sprint 3 mantidos; citação obrigatória.",
         "Regras de texto simples: uma frase bem reescrita pode passar."],
    ], [2.2, 7.6, 7.2]))

    historia.append(Paragraph("3. Avaliação: método e iterações", H))
    historia.append(Paragraph(
        "O pacote <i>ragas</i> não importa com o langchain-community atual (ModuleNotFoundError em langchain_community.chat_models.vertexai), então usamos o fallback "
        "manual aceito no enunciado, com rubrica 0 a 1 equivalente à do RAGAS: <b>faithfulness</b> = afirmações da resposta sustentadas pelo contexto / total de afirmações "
        "(o juiz LLM decompõe a resposta e confere cada afirmação); <b>answer_relevancy</b> = média da similaridade cosseno entre a pergunta e 3 perguntas que o juiz gera a partir da resposta; "
        "<b>contexto relevante</b> = trechos úteis / trechos recuperados. Mesmo eval set de 19 perguntas em todas as iterações; gerador gpt-oss:120b "
        "(temperature 0,2, top_p 0,9, max_tokens 1024); juiz gemma4:31b-cloud (o qwen3.6:27b da aula não está no plano gratuito). "
        "Respostas de recusa e bloqueios dos guardrails ficam fora das médias de faithfulness e relevância.", P))
    linhas = [["Iter.", "Prompt", "chunk / overlap / k", "Pont.", "Recus.", "Faithful- ness", "Answer relev.", "Contexto relev.", "Seg. (testes)"]]
    for it, s in zip(runs, S):
        m = it["meta"]
        linhas.append([m["rotulo"], m.get("prompt"), f"{m.get('chunk_size')}/{m.get('chunk_overlap')}/{m.get('k')}", s["n_pontuados"],
                       s["n_recusas_modelo"], fmt(s["faithfulness"], 3), fmt(s["answer_relevancy"], 3), fmt(s["context_relevance"], 3), fmt(s["auto_pass_taxa"], 3)])
    historia.append(Spacer(1, 3))
    historia.append(tabela(linhas, [1.4, 1.5, 2.8, 1.4, 1.5, 2.0, 2.2, 2.2, 2.0]))
    historia.append(Spacer(1, 3))
    texto_pares = []
    for a, b in zip(runs, runs[1:]):
        f1, f2, n = pareado(a, b, "faithfulness")
        r1, r2, _ = pareado(a, b, "answer_relevancy")
        if n:
            texto_pares.append(f"<b>{a['meta']['rotulo']} para {b['meta']['rotulo']}</b> (só as {n} perguntas pontuadas nas duas): faithfulness {fmt(f1)} para {fmt(f2)}, "
                               f"answer_relevancy {fmt(r1)} para {fmt(r2)}, testes de segurança {fmt(a['resumo']['auto_pass_taxa'], 3)} para {fmt(b['resumo']['auto_pass_taxa'], 3)}.")
    historia.append(Paragraph("As médias da tabela não são diretamente comparáveis, porque cada iteração pontua um número diferente de perguntas (o modelo recusa mais quando o prompt manda "
                              "responder só com o contexto). A comparação justa é pareada: " + " ".join(texto_pares), P))

    historia.append(Paragraph("Versões do prompt RAG", H))
    historia.append(tabela([
        ["Versão", "O que mudou", "Efeito medido"],
        ["v1", "Baseline: \"responda usando o contexto\".", "Não seguia uma recusa padrão: nos testes de segurança reprovou o erro 47 e o modelo GW50K (reconhecia que não constava, mas sem orientar o suporte) e extrapolava em perguntas sem resposta direta. A citação era só completada pelo código."],
        ["v2", "Grounding estrito, citação (fonte: rótulo), recusa padrão \"Não encontrei...\", regra de alertas de hardware.",
         "Testes de segurança de " + fmt(S[0]['auto_pass_taxa'], 3) + " para " + fmt(S[1]['auto_pass_taxa'], 3) + ": recusa padrão com orientação ao suporte (erro 47 e GW50K passaram). Efeito colateral: 5 recusas, 3 delas indevidas. O modelo passou a escrever \"documento n 3\" em vez do arquivo."],
        ["v3", "v2 + bloco de segurança (contexto é dado, nunca instrução), risco crítico sem instruir a mexer no equipamento, rótulo \"Fonte:\" visível no trecho.",
         ("Ver iteração " + runs[2]["meta"]["rotulo"] + " na tabela acima.") if len(runs) > 2 else "A medir na iteração 3."],
    ], [1.5, 7.3, 8.2]))

    historia.append(Paragraph("4. Comparativo antes/depois", H))
    historia.append(tabela([
        ["Critério", "Sprints 1/2 (versão original)", "Sprint 04 (RAG avaliado)"],
        ["Contexto enviado ao modelo", "Base inteira em toda pergunta (4.616 tokens medidos por pergunta na Sprint 3)",
         f"Só os trechos recuperados (k=3): prompt médio de {S[0]['tokens_prompt_medio']:.0f} a {S[1]['tokens_prompt_medio']:.0f} tokens nas iterações 1 e 2"],
        ["Faithfulness por iteração", "Não medido", " | ".join(f"{it['meta']['rotulo']}: {fmt(s['faithfulness'], 3)}" for it, s in zip(runs, S))],
        ["Answer relevancy por iteração", "Não medido", " | ".join(f"{it['meta']['rotulo']}: {fmt(s['answer_relevancy'], 3)}" for it, s in zip(runs, S))],
        ["Qualidade do contexto recuperado", "Não se aplica (base inteira, sem busca)",
         "Contexto relevante " + " | ".join(f"{it['meta']['rotulo']}: {fmt(s['context_relevance'], 3)}" for it, s in zip(runs, S)) + " (juiz exigente; ponto fraco do pipeline)"],
        ["Citação de fonte", "Não citava", "Documento e página (ex.: GW_HCA-G2_User-Manual-PT.pdf, pág. 14) e a interface mostra os trechos"],
        ["Recusa fora do contexto", "Só recusa por escopo (guardrails); sem recusa por falta de contexto", "Recusa com \"Não encontrei essa informação nos documentos fornecidos\" (v2 em diante)"],
        ["Testes automáticos de segurança", "11 de 13 (Sprints 1/2) e 13 de 13 (Sprint 3)", " | ".join(f"{it['meta']['rotulo']}: {fmt(s['auto_pass_taxa'] * 13, 0)} de 13" for it, s in zip(runs, S))],
        ["Base de conhecimento", "Dataset (7 conjuntos de perguntas e respostas)", "Dataset em .md + datasheet, manual do usuário e mapa Modbus do HCA G2 (PDF)"],
        ["Interface", "Streamlit sem fontes", "Streamlit com fontes e trechos recuperados visíveis (app/app.py)"],
    ], [3.8, 5.6, 7.6]))

    historia.append(Paragraph("5. Problemas encontrados e soluções", H))
    historia.append(tabela([
        ["Problema", "Decisão tomada e por quê"],
        ["O Ollama Cloud recusou o nomic-embed-text (erro 401) mesmo com a chave válida para chat.",
         "Diagnóstico separado (chat funcionava, embed não). Passamos os embeddings para o Ollama local (OLLAMA_EMBED_HOST) e mantivemos o chat no Cloud. Custo: o app depende de Ollama local para indexar."],
        ["O juiz qwen3.6:27b da aula não existe no plano gratuito (404) e derrubou o eval antes de salvar.", "Trocamos o juiz para gemma4:31b-cloud, registrado no meta de cada resultado. O pacote ragas também não importava, por isso a rubrica manual equivalente."],
        ["O modelo citava \"documento n 3\" em vez do arquivo; na it1 a citação só existia porque o código a completava.",
         "No v3 o rótulo vira uma linha \"Fonte: arquivo, pág. X\" dentro do trecho e o prompt proíbe \"documento n\". Mantivemos o código que acrescenta as fontes como rede de segurança."],
        ["Para faíscas no conector, v1 e v2 mandavam reconectar o plugue (copiando o contexto), com o aviso de emergência só no rodapé.",
         "O v3 manda manter distância e chamar profissional primeiro e proíbe instruir qualquer intervenção, mesmo que o contexto traga esses passos."],
        ["Com k=3 o retriever trouxe trechos pouco relacionados (contexto relevante baixo) e o v2 recusou perguntas cuja resposta existe (ids 1, 3 e 7).",
         "Aumentamos o k na iteração seguinte para recuperar mais candidatos. Reranking com cross-encoder fica como próximo passo."],
    ], [7.0, 10.0]))

    historia.append(Paragraph("6. Equipe e divisão de trabalho", H))
    historia.append(tabela([["Nome", "RM", "Tarefa principal"]] + [[n, r, t] for (n, r), t in zip(EQUIPE, TAREFAS)], [6.5, 3.0, 7.5]))

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                      title="Relatório de evolução - Sprint 04").build(historia)
    print("gerado", SAIDA)


if __name__ == "__main__":
    main()
