from __future__ import annotations

import re
from collections import Counter

import pandas as pd
import streamlit as st

from src.oci_llm import answer_with_oci, is_configured


st.set_page_config(page_title="Christinus", page_icon="🔍", layout="wide")

NIVEIS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ERROS = ("ERROR", "CRITICAL")

RE_NIVEL = re.compile(r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b", re.I)
RE_DATA = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}):\d{2}")
RE_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2}(?:[.,]\d+)?)?Z?")
RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_STATUS = re.compile(r'"\s(\d{3})\b')
RE_HEX = re.compile(r"\b0x[0-9a-fA-F]+\b")
RE_NUM = re.compile(r"\d+")

LOG_EXEMPLO = """2026-09-23 08:01:12 INFO [web] 192.168.0.10 "GET /login HTTP/1.1" 200
2026-09-23 08:03:45 INFO [web] 192.168.0.11 "POST /login HTTP/1.1" 200
2026-09-23 08:15:02 WARNING [db] Consulta lenta: 2450 ms em orders
2026-09-23 09:02:31 ERROR [db] Connection refused ao conectar em 10.0.0.5:5432
2026-09-23 09:02:35 ERROR [db] Connection refused ao conectar em 10.0.0.5:5432
2026-09-23 09:02:40 ERROR [web] 192.168.0.10 "GET /orders HTTP/1.1" 500
2026-09-23 09:10:11 INFO [db] Conexão restabelecida com 10.0.0.5:5432
2026-09-23 10:20:05 WARNING [web] 192.168.0.23 "GET /admin HTTP/1.1" 403
2026-09-23 10:21:07 WARNING [web] 192.168.0.23 "GET /admin HTTP/1.1" 403
2026-09-23 10:45:50 ERROR [worker] Timeout ao processar job 8841 após 30s
2026-09-23 11:05:13 ERROR [worker] Timeout ao processar job 8852 após 30s
2026-09-23 11:30:00 CRITICAL [disk] Uso de disco em 97% no volume /var/log
2026-09-23 11:31:20 INFO [web] 192.168.0.12 "GET /health HTTP/1.1" 200"""

for chave in ("analise_ia",):
    if chave not in st.session_state:
        st.session_state[chave] = None


def normalizar_nivel(nivel):
    nivel = nivel.upper()
    if nivel == "WARN":
        return "WARNING"
    if nivel == "FATAL":
        return "CRITICAL"
    return nivel


def gerar_padrao(linha):
    texto = RE_TIMESTAMP.sub("", linha)
    texto = RE_NIVEL.sub("", texto)
    texto = RE_IP.sub("<ip>", texto)
    texto = RE_HEX.sub("<hex>", texto)
    texto = RE_NUM.sub("<n>", texto)
    texto = re.sub(r"\s+", " ", texto).strip(" []-:")
    return texto[:140]


def analisar(texto):
    registros = []

    for linha in texto.splitlines():
        if not linha.strip():
            continue

        achou_nivel = RE_NIVEL.search(linha)
        achou_data = RE_DATA.search(linha)
        achou_ip = RE_IP.search(linha)
        achou_status = RE_STATUS.search(linha)

        registros.append(
            {
                "linha": linha.rstrip(),
                "nivel": normalizar_nivel(achou_nivel.group(1)) if achou_nivel else "OUTROS",
                "hora": f"{achou_data.group(1)} {achou_data.group(2)}h" if achou_data else None,
                "ip": achou_ip.group(0) if achou_ip else None,
                "status": achou_status.group(1) if achou_status else None,
                "padrao": gerar_padrao(linha),
            }
        )

    return registros


def montar_contexto(registros, padroes):
    linhas = ["Padrões de erro mais frequentes:"]

    for padrao, qtd in padroes[:10]:
        linhas.append(f"- ({qtd}x) {padrao}")

    linhas.append("")
    linhas.append("Amostras de linhas de erro:")

    vistos = set()
    for r in registros:
        if r["nivel"] in ERROS and r["padrao"] not in vistos:
            vistos.add(r["padrao"])
            linhas.append(r["linha"][:300])
        if len(vistos) >= 15:
            break

    return "\n".join(linhas)[:6000]


def montar_relatorio(total, n_erros, n_avisos, padroes, ia):
    partes = [
        "# Relatório Christinus",
        "",
        f"- Linhas analisadas: {total}",
        f"- Erros (ERROR/CRITICAL): {n_erros}",
        f"- Avisos (WARNING): {n_avisos}",
        "",
        "## Erros recorrentes",
    ]

    if padroes:
        partes += [f"- ({qtd}x) {padrao}" for padrao, qtd in padroes[:15]]
    else:
        partes.append("Nenhum erro encontrado.")

    if ia:
        partes += ["", "## Análise da IA", ia]

    return "\n".join(partes) + "\n"


st.title("Christinus")
st.caption("Cole ou envie um log e veja níveis, erros recorrentes, horários críticos e possíveis causas")

with st.sidebar:
    st.header("Entrada")

    arquivo = st.file_uploader("Enviar arquivo de log", type=["log", "txt"])
    colado = st.text_area("Ou cole o log aqui", height=180)
    usar_exemplo = st.checkbox("Usar log de exemplo")

    st.divider()

    if is_configured():
        st.success("OCI Generative AI configurado")
    else:
        st.warning("OCI não configurado. A análise local continua funcionando.")

if arquivo is not None:
    texto_log = arquivo.getvalue().decode("utf-8", errors="replace")
elif colado.strip():
    texto_log = colado
elif usar_exemplo:
    texto_log = LOG_EXEMPLO
else:
    st.info("Envie um arquivo, cole um log na barra lateral ou marque o log de exemplo.")
    st.stop()

registros = analisar(texto_log)

if not registros:
    st.warning("Não encontrei nenhuma linha para analisar.")
    st.stop()

contagem_niveis = Counter(r["nivel"] for r in registros)
ordem = [n for n in NIVEIS + ["OUTROS"] if contagem_niveis.get(n)]

n_erros = sum(contagem_niveis.get(n, 0) for n in ERROS)
n_avisos = contagem_niveis.get("WARNING", 0)

padroes_erro = Counter(r["padrao"] for r in registros if r["nivel"] in ERROS).most_common(15)

aba_geral, aba_erros, aba_linhas, aba_ia = st.tabs(
    ["Visão geral", "Erros recorrentes", "Linhas", "Análise com IA"]
)

with aba_geral:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Linhas", len(registros))
    c2.metric("Erros", n_erros)
    c3.metric("Avisos", n_avisos)
    c4.metric("Padrões de erro", len(padroes_erro))

    esquerda, direita = st.columns(2)

    with esquerda:
        st.subheader("Linhas por nível")
        st.bar_chart(pd.Series({n: contagem_niveis[n] for n in ordem}))

    with direita:
        st.subheader("Erros por hora")
        por_hora = Counter(r["hora"] for r in registros if r["hora"] and r["nivel"] in ERROS)
        if por_hora:
            st.bar_chart(pd.Series(dict(sorted(por_hora.items()))))
        else:
            st.write("Nenhum erro com horário identificado.")

    col_ip, col_status = st.columns(2)

    with col_ip:
        st.subheader("IPs mais frequentes")
        ips = Counter(r["ip"] for r in registros if r["ip"]).most_common(8)
        if ips:
            st.dataframe(pd.DataFrame(ips, columns=["IP", "Ocorrências"]), hide_index=True)
        else:
            st.write("Nenhum IP encontrado.")

    with col_status:
        st.subheader("Códigos HTTP")
        status = Counter(r["status"] for r in registros if r["status"]).most_common(8)
        if status:
            st.dataframe(pd.DataFrame(status, columns=["Status", "Ocorrências"]), hide_index=True)
        else:
            st.write("Nenhum código HTTP encontrado.")

with aba_erros:
    if padroes_erro:
        st.write("Mensagens de erro agrupadas depois de trocar números, IPs e códigos por marcadores.")
        st.dataframe(
            pd.DataFrame(
                [(qtd, padrao) for padrao, qtd in padroes_erro],
                columns=["Ocorrências", "Padrão"],
            ),
            hide_index=True,
        )
    else:
        st.success("Nenhum ERROR ou CRITICAL encontrado neste log.")

with aba_linhas:
    niveis_sel = st.multiselect("Níveis", ordem, default=ordem)
    busca = st.text_input("Buscar no log")

    filtradas = [
        r["linha"]
        for r in registros
        if r["nivel"] in niveis_sel and busca.lower() in r["linha"].lower()
    ]

    st.caption(f"{len(filtradas)} linhas (mostrando até 300)")

    if filtradas:
        st.code("\n".join(filtradas[:300]), language=None)

with aba_ia:
    if not padroes_erro:
        st.info("Sem erros para analisar.")
    elif not is_configured():
        st.warning("Configure a OCI Generative AI para receber causas prováveis e sugestões de correção.")
    else:
        if st.button("Explicar erros com IA", type="primary"):
            pergunta = (
                "Você é um engenheiro DevOps. Com base nos erros do log, explique em português "
                "as causas prováveis de cada problema, o impacto e como corrigir, em ordem de prioridade."
            )
            try:
                with st.spinner("Analisando o log..."):
                    st.session_state.analise_ia = answer_with_oci(
                        pergunta,
                        montar_contexto(registros, padroes_erro),
                    )
            except Exception as erro:
                st.session_state.analise_ia = f"Ocorreu um erro ao consultar a OCI Generative AI: {erro}"

        if st.session_state.analise_ia:
            st.markdown(st.session_state.analise_ia)

st.sidebar.divider()
st.sidebar.download_button(
    "Baixar relatório (.md)",
    data=montar_relatorio(len(registros), n_erros, n_avisos, padroes_erro, st.session_state.analise_ia),
    file_name="relatorio_christinus.md",
    mime="text/markdown",
)