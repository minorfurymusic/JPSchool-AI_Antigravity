"""Rotina diária do mercado de FIIs (roda no GitHub Actions, à noite, depois do fechamento da B3) — 23/11/2026.

Cada etapa roda separada: erro numa não para as outras. A saída literal de cada rodada fica em
docs/rotina_ultima_execucao.md e o resumo de todas as rodadas em docs/rotina_historico.csv.

Etapas e tabelas (nesta ordem: o rendimento novo entra na base antes dos preços do dia):
  1 documentos dos FIIs (FNET)                        -> planilhas/rotina/fnet_documentos_AAAA-MM.csv
                                                         planilhas/rotina/fnet_rendimentos_AAAA.csv
                                                         planilhas/rotina/fnet_textos/AAAA-MM-DD.csv.gz (texto dos PDFs do dia)
  2 rendimentos novos na base de preços               -> planilhas/rendimentos.csv (acrescenta) e precos_AAAA.csv (corrige)
  3 preços dos FIIs (arquivo diário COTAHIST da B3)  -> planilhas/precos_AAAA.csv      (estudos/atualizar_precos.py)
                                                         planilhas/tecnico/b3_cotahist_fii_diario.csv (TODOS os FIIs negociados,
                                                         inclusive os fora da base; continua o b3_cotahist_fii_2019_2026.csv.gz)
  4 mercado de fundos e CDI                           -> planilhas/mercado.csv, cdi.csv (estudos/atualizar_mercado_cdi.py)
  5 dólar, IFIX e Ibovespa (diário)                   -> planilhas/rotina/indicadores_diarios.csv
  6 IPCA e IGP-M (mensal)                             -> planilhas/rotina/indicadores_mensais.csv
  7 Boletim Focus (Selic, IPCA, câmbio)               -> planilhas/rotina/focus.csv
  8 juros dos títulos públicos (NTN-B = IPCA+)        -> planilhas/rotina/titulos_publicos_anbima.csv, juro_real_10_anos.csv

Fontes, todas oficiais: B3 (COTAHIST e estatísticas históricas dos índices), FNET, CVM, Banco Central (SGS e Focus), ANBIMA.
Os PDFs do FNET não são guardados no repositório (ficam no FNET; a tabela traz o link). O texto extraído é guardado.

    PYTHONPATH=. python3 estudos/rotina_diaria.py
"""
from __future__ import annotations

import datetime as dt
import io
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
ROT = RAIZ / "planilhas" / "rotina"
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
GRAVA = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False)
UA = {"User-Agent": "Mozilla/5.0 (rotina JPSchool-AI_Antigravity)"}
TMP = Path(tempfile.mkdtemp(prefix="rotina_"))
INICIO_HIST = dt.date(2017, 1, 1)


def hoje_brasil() -> dt.date:
    return (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - dt.timedelta(hours=3)).date()


def get(url: str, timeout: int = 90, **kw) -> requests.Response:
    r = requests.get(url, timeout=timeout, headers=UA, **kw)
    r.raise_for_status()
    return r


def ler(caminho: Path) -> pd.DataFrame | None:
    return pd.read_csv(caminho, **OP) if caminho.exists() else None


def juntar(caminho: Path, novo: pd.DataFrame, chaves: list[str], ordem: list[str]) -> tuple[int, int]:
    """Acrescenta sem apagar: linha com a mesma chave é trocada pela nova. Devolve (antes, depois)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    velho = ler(caminho)
    antes = 0 if velho is None else len(velho)
    if velho is not None:
        tipos = {c: t for c, t in novo.dtypes.items() if c in velho.columns}
        novo = pd.concat([velho.astype(tipos, errors="ignore"), novo], ignore_index=True)
    novo = novo.drop_duplicates(chaves, keep="last").reset_index(drop=True)
    k = pd.DataFrame({f"k{i}": (pd.to_datetime(novo[c], dayfirst=True, errors="coerce") if c.startswith(("data", "entrega")) else novo[c])
                      for i, c in enumerate(ordem)})
    novo = novo.loc[k.sort_values(list(k.columns), kind="stable").index]
    novo.to_csv(caminho, **GRAVA)
    return antes, len(novo)


def rodar(args: list[str], env_extra: dict | None = None) -> str:
    env = {**os.environ, "PYTHONPATH": str(RAIZ), **(env_extra or {})}
    r = subprocess.run([sys.executable, *args], cwd=RAIZ, env=env, capture_output=True, text=True, timeout=1800)
    saida = (r.stdout + r.stderr).strip()
    if r.returncode != 0 and "nada novo" not in saida:
        raise RuntimeError(f"saiu com código {r.returncode}:\n{saida[-3000:]}")
    return saida


def ultima_data_precos() -> dt.date:
    ano = hoje_brasil().year
    for a in (ano, ano - 1):
        arq = RAIZ / f"planilhas/precos_{a}.csv"
        if arq.exists():
            return pd.to_datetime(pd.read_csv(arq, usecols=[0], **OP).iloc[:, 0], dayfirst=True).max().date()
    raise RuntimeError("não achei planilhas/precos_AAAA.csv")


# ---------------------------------------------------------------- rendimentos do FNET na base de preços
FECHAMENTO = dt.time(18, 0)
INT_COLS = ("volume_dia (R$)", "volume_medio_60 (R$)", "patrimonio (R$)", "negociou (1/0)", "amortizacao_12m (1/0)")


def data_conhecido(entrega: pd.Timestamp) -> pd.Timestamp:
    """Regra do dono (23/11/2026): o rendimento novo vale a partir do dia em que o aviso sai no FNET, para ver o preço
    reagir já nesse momento. Aviso entregue depois do fechamento da B3 (18h) só pode mexer no preço do pregão seguinte."""
    d = entrega.normalize()
    return d + pd.offsets.BDay(1) if entrega.time() >= FECHAMENTO else d


def etapa_rendimentos() -> str:
    arqs = sorted(ROT.glob("fnet_rendimentos_*.csv"))
    if not arqs:
        return "nada novo: ainda não há avisos do FNET guardados"
    F = pd.concat([ler(a) for a in arqs], ignore_index=True)
    F = F[(F["tipo"] == "Rendimento") & F["cod_negociacao"].astype(str).str.fullmatch(r"[A-Z]{4}\d{2}")].copy()
    F["ent"] = pd.to_datetime(F["entrega"], dayfirst=True)
    F = F.sort_values(["ent", "versao"]).drop_duplicates(["cod_negociacao", "data_base"], keep="last")  # vale a última versão
    arq_r = RAIZ / "planilhas/rendimentos.csv"
    R = pd.read_csv(arq_r, **OP)
    ja = set(zip(R["fundo"], R["data_base"]))
    N = F[[(f, b) not in ja for f, b in zip(F["cod_negociacao"], F["data_base"])]]
    if N.empty:
        return f"nada novo: os {len(F)} avisos do FNET já estão em planilhas/rendimentos.csv"
    N = pd.DataFrame({"fundo": N["cod_negociacao"].values,
                      "data_conhecido": [data_conhecido(e) for e in N["ent"]],
                      "data_base": N["data_base"].values, "valor (R$/cota)": N["valor (R$/cota)"].round(4).values})
    N = N.sort_values(["data_conhecido", "fundo"])
    N["data_conhecido"] = N["data_conhecido"].dt.strftime("%d/%m/%Y")
    # acrescenta no fim, sem reescrever o que já existe
    N.to_csv(arq_r, mode="a", header=False, index=False, sep=";", decimal=",", encoding="utf-8")
    linhas = [f"planilhas/rendimentos.csv: +{len(N)} avisos novos do FNET (data conhecida = dia da entrega; depois das 18h, "
              f"pregão seguinte)"]
    # refaz o rendimento das linhas de preço já gravadas a partir do dia em que o aviso ficou conhecido
    R = pd.concat([R, N], ignore_index=True)
    R["dc"] = pd.to_datetime(R["data_conhecido"], dayfirst=True)
    ano = hoje_brasil().year
    arq_p = RAIZ / f"planilhas/precos_{ano}.csv"
    P = pd.read_csv(arq_p, **OP)
    for c in INT_COLS:
        P[c] = P[c].astype("Int64")
    dp = pd.to_datetime(P["data"], dayfirst=True)
    mudou = []
    for f, x in N.groupby("fundo"):
        ini = pd.to_datetime(x["data_conhecido"], dayfirst=True).min()
        sel = (P["fundo"] == f) & (dp >= ini)
        if not sel.any():
            continue
        rf = R[R["fundo"] == f].sort_values("dc")
        for i in P.index[sel]:
            r = rf[rf["dc"] <= dp[i]]
            if not len(r):
                continue
            v = float(r["valor (R$/cota)"].iloc[-1])
            antes = P.at[i, "rendimento_mensal (R$/cota)"]
            if pd.isna(antes) or abs(antes - v) > 1e-9:
                P.at[i, "rendimento_mensal (R$/cota)"] = v
                fe = P.at[i, "fechamento"]
                P.at[i, "rendimento_ano_sobre_preco (%)"] = round(v * 12 / fe * 100, 2) if fe else float("nan")
                mudou.append((f, P.at[i, "data"], antes, v))
    if mudou:
        P.to_csv(arq_p, sep=";", decimal=",", encoding="utf-8-sig", index=False)
        M = pd.DataFrame(mudou, columns=["fundo", "data", "rendimento antes", "rendimento novo"])
        linhas.append(f"{arq_p.relative_to(RAIZ)}: rendimento corrigido em {len(M)} linhas já gravadas:\n"
                      + M.drop_duplicates("fundo", keep="last").to_string(index=False))
    return "\n".join(linhas)


# ---------------------------------------------------------------- preços
# Arquivo da B3 com TODOS os FIIs (inclusive os que não estão na base). O grande (2019 até 17/11/2026) não é regravado
# todo dia (11 MB compactado incharia o repositório); os dias seguintes vão para um arquivo pequeno, só acrescentado.
# Pedido do dono em 25/11/2026: fundos fora da base (ex.: TRXF11) estavam parados em 17/11 no Radar.
ARQ_B3 = RAIZ / "planilhas/tecnico/b3_cotahist_fii_2019_2026.csv.gz"
ARQ_B3_NOVO = RAIZ / "planilhas/tecnico/b3_cotahist_fii_diario.csv"


def ultima_data_arquivo_b3() -> dt.date:
    p = ARQ_B3_NOVO if ARQ_B3_NOVO.exists() else ARQ_B3
    return pd.to_datetime(pd.read_csv(p, usecols=[0], **OP).iloc[:, 0], format="%Y-%m-%d").max().date()


def gravar_arquivo_b3(zips: list[str]) -> str:
    from fii.b3_cotacoes import ler_arquivo

    ult = ultima_data_arquivo_b3()
    N = pd.concat([ler_arquivo(Path(z)) for z in zips], ignore_index=True)
    N = N[N["data"].dt.date > ult]
    if N.empty:
        return f"{ARQ_B3_NOVO.relative_to(RAIZ)}: nada novo (vai até {ult:%d/%m/%Y})"
    dias = sorted(N["data"].dt.date.unique())
    N["data"] = N["data"].dt.strftime("%Y-%m-%d")
    a, b = juntar(ARQ_B3_NOVO, N, ["data", "ticker"], ["data", "ticker"])
    return (f"{ARQ_B3_NOVO.relative_to(RAIZ)}: {a} -> {b} linhas; ia até {ult:%d/%m/%Y}; pregões acrescentados: "
            f"{', '.join(f'{x:%d/%m}' for x in dias)}; {N['ticker'].nunique()} códigos")


def etapa_precos() -> str:
    ult = ultima_data_precos()
    ult_b3 = ultima_data_arquivo_b3()
    zips, faltam = [], []
    d = min(ult, ult_b3) + dt.timedelta(days=1)
    while d <= hoje_brasil():
        if d.weekday() < 5:
            r = requests.get(f"https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D{d:%d%m%Y}.ZIP", timeout=120, headers=UA)
            if r.status_code == 200 and r.content[:2] == b"PK":
                arq = TMP / f"COTAHIST_D{d:%d%m%Y}.ZIP"
                arq.write_bytes(r.content)
                zips.append(str(arq))
            else:
                faltam.append(f"{d:%d/%m} ({r.status_code})")
        d += dt.timedelta(days=1)
    linhas = [f"tabela ia até {ult:%d/%m/%Y}; arquivos da B3 baixados: {len(zips)}; sem arquivo (feriado ou ainda não publicado): "
              + (", ".join(faltam) or "nenhum")]
    if not zips:
        return linhas[0]
    linhas.append(gravar_arquivo_b3(zips))
    cvm = TMP / "cvm_men"
    cvm.mkdir(exist_ok=True)
    for a in (2025, 2026):  # os anos que estudos/atualizar_precos.py lê
        (cvm / f"inf_mensal_fii_{a}.zip").write_bytes(
            get(f"https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/inf_mensal_fii_{a}.zip", timeout=300).content)
    linhas.append(rodar(["estudos/atualizar_precos.py", *zips], {"CVM_MEN": str(cvm)}))
    return "\n".join(linhas)


# ---------------------------------------------------------------- 2 mercado e CDI
def etapa_mercado() -> str:
    m = pd.to_datetime(pd.read_csv(RAIZ / "planilhas/mercado.csv", usecols=[0], **OP).iloc[:, 0], dayfirst=True).max().date()
    p = ultima_data_precos()
    if p <= m:
        return f"nada novo: mercado.csv já vai até {m:%d/%m/%Y} (preços até {p:%d/%m/%Y})"
    return rodar(["estudos/atualizar_mercado_cdi.py"])


# ---------------------------------------------------------------- 3 FNET
def etapa_fnet() -> str:
    sys.path.insert(0, str(RAIZ))
    from fii import fnet

    docs_ant = sorted(ROT.glob("fnet_documentos_*.csv"))
    if docs_ant:
        e = pd.to_datetime(ler(docs_ant[-1])["entrega"], dayfirst=True, errors="coerce").max()
        desde = e.date() - dt.timedelta(days=3)
    else:
        desde = hoje_brasil() - dt.timedelta(days=7)
    con = fnet.conectar(TMP / "fnet.duckdb")
    res = fnet.coletar(con, hoje_brasil(), desde=desde, pasta=TMP / "fnet")
    D = con.execute("""select id, fundo, nome_pregao, categoria, tipo, especie, data_referencia, entrega, versao, situacao,
                       cnpj, formato, estado, erro, arquivo from documentos""").df()
    if D.empty:
        return f"{res}"
    D["link"] = "https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=" + D["id"].astype(str)
    D["entrega_dt"] = pd.to_datetime(D["entrega"])
    textos = []
    for _, x in D[D["estado"] == "texto"].iterrows():
        t = Path(x["arquivo"]).with_suffix(".txt")
        if t.exists():
            textos.append({"id": x["id"], "fundo": x["fundo"], "categoria": x["categoria"], "tipo": x["tipo"],
                           "entrega": x["entrega_dt"].strftime("%d/%m/%Y %H:%M"), "texto": t.read_text(encoding="utf-8")})
    D["entrega"] = D["entrega_dt"].dt.strftime("%d/%m/%Y %H:%M")
    linhas = [f"período {res['periodo']}: {res['listados']} documentos listados, {res['novos']} novos; resultado: {res['tratados']}"]
    cols = ["id", "fundo", "nome_pregao", "categoria", "tipo", "especie", "data_referencia", "entrega", "versao", "situacao",
            "cnpj", "formato", "estado", "erro", "link"]
    for mes, x in D.dropna(subset=["entrega_dt"]).groupby(D["entrega_dt"].dt.strftime("%Y-%m")):
        a, b = juntar(ROT / f"fnet_documentos_{mes}.csv", x[cols].copy(), ["id"], ["entrega", "id"])
        linhas.append(f"fnet_documentos_{mes}.csv: {a} -> {b} linhas")
    R = con.execute("select * from rendimentos_fnet").df()
    if not R.empty:
        for c in ("data_base", "data_pagamento"):
            R[c] = pd.to_datetime(R[c]).dt.strftime("%d/%m/%Y")
        R["entrega"] = pd.to_datetime(R["entrega"]).dt.strftime("%d/%m/%Y %H:%M")
        R = R.rename(columns={"valor": "valor (R$/cota)"})
        for ano, x in R.groupby(R["entrega"].str[6:10]):
            a, b = juntar(ROT / f"fnet_rendimentos_{ano}.csv", x.copy(), ["doc_id", "cod_negociacao", "data_base"], ["entrega", "cod_negociacao"])
            linhas.append(f"fnet_rendimentos_{ano}.csv: {a} -> {b} linhas")
    if textos:
        T = pd.DataFrame(textos)
        pasta = ROT / "fnet_textos"
        pasta.mkdir(parents=True, exist_ok=True)
        for dia, x in T.groupby(pd.to_datetime(T["entrega"], dayfirst=True).dt.strftime("%Y-%m-%d")):
            arq = pasta / f"{dia}.csv.gz"
            if arq.exists():
                x = pd.concat([pd.read_csv(arq, sep=";", encoding="utf-8"), x]).drop_duplicates("id", keep="last")
            x.to_csv(arq, sep=";", index=False, encoding="utf-8", compression={"method": "gzip", "mtime": 0})
        linhas.append(f"textos de PDF guardados: {len(T)} documentos")
    sem = D[D["estado"].isin(["sem_texto", "erro"])]
    if len(sem):
        linhas.append(f"pendências (PDF só imagem ou erro): {len(sem)} — ids {', '.join(sem['id'].astype(str).head(20))}")
    return "\n".join(linhas)


# ---------------------------------------------------------------- 4 dólar, IFIX, Ibovespa
def sgs(serie: int, ini: dt.date) -> pd.Series:
    r = get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json&dataInicial={ini:%d/%m/%Y}"
            f"&dataFinal={hoje_brasil():%d/%m/%Y}")
    d = pd.DataFrame(r.json())
    if d.empty:
        return pd.Series(dtype=float)
    return pd.Series(d["valor"].astype(float).values, index=pd.to_datetime(d["data"], dayfirst=True))


def b3_historico(codigo: str, anos: range) -> pd.Series:
    """Fechamento de cada pregão de um índice da B3 (IFIX, IBOV), ano a ano — a mesma tabela da página
    "Estatísticas históricas" do site da B3 (achado em 23/11/2026)."""
    vals = {}
    for ano in anos:
        q = b64json({"index": codigo, "language": "pt-br", "year": str(ano)})
        j = get(f"https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetPortfolioDay/{q}").json()
        for linha in j.get("results", []):
            for mes in range(1, 13):
                v = linha.get(f"rateValue{mes}")
                if v:
                    try:
                        vals[pd.Timestamp(ano, mes, int(linha["day"]))] = float(v.replace(".", "").replace(",", "."))
                    except ValueError:
                        pass
    return pd.Series(vals, dtype=float).sort_index()


def b64json(d: dict) -> str:
    import base64
    import json
    return base64.b64encode(json.dumps(d, separators=(",", ":")).encode()).decode()


def etapa_diarios() -> str:
    """Dólar PTAX (Banco Central) e fechamento do IFIX e do Ibovespa (B3), oficiais. Os índices são relidos inteiros
    desde 2017 a cada rodada (são 20 consultas pequenas e corrigem qualquer buraco). Valor já gravado não é apagado
    por um vazio novo."""
    arq = ROT / "indicadores_diarios.csv"
    velho = ler(arq)
    ini = INICIO_HIST if velho is None else (pd.to_datetime(velho["data"], dayfirst=True).max() - pd.Timedelta(days=10)).date()
    anos = range(INICIO_HIST.year, hoje_brasil().year + 1)
    s = {"dolar_ptax_venda (R$)": sgs(1, ini), "ifix (pontos)": b3_historico("IFIX", anos),
         "ibovespa (pontos)": b3_historico("IBOV", anos)}
    N = pd.DataFrame(s).sort_index()
    N = N[(N.index >= pd.Timestamp(INICIO_HIST)) & (N.index.dayofweek < 5)].dropna(how="all")
    antes = 0
    if velho is not None:
        antes = len(velho)
        V = velho.assign(data=pd.to_datetime(velho["data"], dayfirst=True)).set_index("data")[["dolar_ptax_venda (R$)"]]
        N = N.combine_first(V)[list(s)]  # índices: só a B3 (relidos inteiros); dólar: o já gravado fica
    N = N.sort_index()
    N.insert(0, "data", N.index.strftime("%d/%m/%Y"))
    arq.parent.mkdir(parents=True, exist_ok=True)
    N.to_csv(arq, **GRAVA)
    vazios = {c: int(N[c].isna().sum()) for c in s}
    return (f"indicadores_diarios.csv: {antes} -> {len(N)} linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); "
            f"dias sem valor: {vazios}\núltimos dias:\n{N.tail(3).to_string(index=False)}")


def etapa_mensais() -> str:
    ini = dt.date(2015, 1, 1)
    M = pd.DataFrame({"ipca_mes (%)": sgs(433, ini), "igpm_mes (%)": sgs(189, ini)}).sort_index()
    for c, n in (("ipca_mes (%)", "ipca_12_meses (%)"), ("igpm_mes (%)", "igpm_12_meses (%)")):
        M[n] = ((1 + M[c] / 100).rolling(12).apply(lambda x: x.prod(), raw=True) - 1).mul(100).round(2)
    M = M[M.index >= pd.Timestamp(INICIO_HIST)]
    M.insert(0, "mes", M.index.strftime("%m/%Y"))
    arq = ROT / "indicadores_mensais.csv"
    arq.parent.mkdir(parents=True, exist_ok=True)
    M.to_csv(arq, **GRAVA)  # tabela inteira refeita do Banco Central a cada rodada (o BC corrige meses antigos)
    return f"indicadores_mensais.csv: {len(M)} meses, último {M['mes'].iloc[-1]}\n{M.tail(2).to_string(index=False)}"


# ---------------------------------------------------------------- 6 Focus
def etapa_focus() -> str:
    arq = ROT / "focus.csv"
    velho = ler(arq)
    ini = INICIO_HIST if velho is None else (pd.to_datetime(velho["data"], dayfirst=True).max() - pd.Timedelta(days=10)).date()
    base = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais"
    filtro = (f"(Indicador eq 'Selic' or Indicador eq 'IPCA' or Indicador eq 'Câmbio') and Data ge '{ini:%Y-%m-%d}' and baseCalculo eq 0")
    L, pulo = [], 0
    while True:
        r = get(f"{base}?$filter={quote(filtro)}&$select=Indicador,Data,DataReferencia,Mediana&$format=json"
                f"&$top=5000&$skip={pulo}&$orderby=Data")
        v = r.json()["value"]
        L += v
        if len(v) < 5000:
            break
        pulo += 5000
    F = pd.DataFrame(L)
    if F.empty:
        return f"Focus: nada novo desde {ini:%d/%m/%Y}"
    F["Data"] = pd.to_datetime(F["Data"])
    F["DataReferencia"] = pd.to_numeric(F["DataReferencia"], errors="coerce")
    F = F[F["DataReferencia"].between(F["Data"].dt.year, F["Data"].dt.year + 1)]
    F = F.assign(data=F["Data"].dt.strftime("%d/%m/%Y"), indicador=F["Indicador"], ano_referencia=F["DataReferencia"].astype(int),
                 mediana=F["Mediana"].round(4))[["data", "indicador", "ano_referencia", "mediana"]]
    a, b = juntar(arq, F, ["data", "indicador", "ano_referencia"], ["data", "indicador", "ano_referencia"])
    return f"focus.csv: {a} -> {b} linhas (desde {ini:%d/%m/%Y})\n{F.tail(6).to_string(index=False)}"


# ---------------------------------------------------------------- 7 juros da B3
def juro_real_10_anos(ntnb: pd.DataFrame, fonte: str) -> pd.DataFrame:
    """Um número por dia: a NTN-B (IPCA+ com juros semestrais) que vence mais perto de 10 anos depois do dia.
    Colunas de entrada: data, vencimento (dd/mm/aaaa), taxa."""
    x = ntnb.assign(d=pd.to_datetime(ntnb["data"], dayfirst=True), v=pd.to_datetime(ntnb["vencimento"], dayfirst=True))
    x["dist"] = (x["v"] - (x["d"] + pd.DateOffset(years=10))).abs()
    x = x.sort_values(["d", "dist"]).drop_duplicates("d")
    return pd.DataFrame({"data": x["d"].dt.strftime("%d/%m/%Y"), "vencimento": x["vencimento"],
                         "juro_real (% ao ano + IPCA)": x["taxa"].round(4), "fonte": fonte})


def etapa_juros() -> str:
    """Taxas dos títulos públicos do dia (ANBIMA, arquivo diário público): NTN-B = juro real (IPCA+), LTN e NTN-F =
    prefixado, LFT = Selic. A ANBIMA só deixa os arquivos recentes no ar (o de 19/11/2021 deu 404 em 23/11/2026):
    a rotina pega os dias que faltam, até 15 dias úteis para trás. O histórico antigo vem do Tesouro (pendência)."""
    arq = ROT / "titulos_publicos_anbima.csv"
    velho = ler(arq)
    fim = hoje_brasil()
    ini = fim - dt.timedelta(days=21) if velho is None else pd.to_datetime(velho["data"], dayfirst=True).max().date() + dt.timedelta(days=1)
    dias = [d.date() for d in pd.bdate_range(ini, fim)][-15:]
    L, faltam = [], []
    for d in dias:
        r = requests.get(f"https://www.anbima.com.br/informacoes/merc-sec/arqs/ms{d:%y%m%d}.txt", timeout=60, headers=UA)
        if r.status_code != 200 or not r.content.startswith(b"ANBIMA"):
            faltam.append(f"{d:%d/%m} ({r.status_code})")
            continue
        t = pd.read_csv(io.StringIO(r.content.decode("latin-1")), sep="@", skiprows=2, decimal=",", thousands=".", dtype={"Data Referencia": str, "Data Vencimento": str})
        t = t[t["Titulo"].notna() & t["Data Vencimento"].notna()]
        L.append(pd.DataFrame({"data": pd.to_datetime(t["Data Referencia"], format="%Y%m%d").dt.strftime("%d/%m/%Y"),
                               "titulo": t["Titulo"].str.strip(),
                               "vencimento": pd.to_datetime(t["Data Vencimento"], format="%Y%m%d").dt.strftime("%d/%m/%Y"),
                               "taxa_indicativa (% ao ano)": pd.to_numeric(t["Tx. Indicativas"], errors="coerce").round(4),
                               "pu (R$)": pd.to_numeric(t["PU"], errors="coerce").round(6)}))
    linhas = [f"arquivos da ANBIMA lidos: {len(L)}; sem arquivo: {', '.join(faltam) or 'nenhum'}"]
    if not L:
        if faltam and velho is None:
            raise RuntimeError("\n".join(linhas))
        return linhas[0]
    N = pd.concat(L, ignore_index=True)
    a, b = juntar(arq, N, ["data", "titulo", "vencimento"], ["data", "titulo", "vencimento"])
    linhas.insert(0, f"titulos_publicos_anbima.csv: {a} -> {b} linhas")
    J = juro_real_10_anos(N.rename(columns={"taxa_indicativa (% ao ano)": "taxa"}).query("titulo == 'NTN-B'"), "ANBIMA (taxa indicativa)")
    a2, b2 = juntar(ROT / "juro_real_10_anos.csv", J, ["data"], ["data"])
    linhas.append(f"juro_real_10_anos.csv: {a2} -> {b2} linhas")
    u = N[N["data"] == N["data"].iloc[-1]]
    linhas.append(f"NTN-B (juro real, IPCA+) em {u['data'].iloc[0]}:\n" + u[u["titulo"] == "NTN-B"].to_string(index=False))
    return "\n".join(linhas)


ETAPAS = [("1 documentos dos FIIs (FNET)", etapa_fnet), ("2 rendimentos novos na base de preços", etapa_rendimentos),
          ("3 preços dos FIIs (B3)", etapa_precos), ("4 mercado de fundos e CDI", etapa_mercado),
          ("5 dólar, IFIX e Ibovespa", etapa_diarios), ("6 IPCA e IGP-M", etapa_mensais), ("7 Boletim Focus", etapa_focus),
          ("8 juros dos títulos públicos (ANBIMA)", etapa_juros)]


def main() -> int:
    inicio = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - dt.timedelta(hours=3)
    so = set(sys.argv[1:])
    blocos, hist, falhas = [], [], 0
    for nome, f in ETAPAS:
        if so and nome[0] not in so:
            continue
        t = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
        try:
            saida, status = f(), "OK"
        except Exception:  # noqa: BLE001
            saida, status = traceback.format_exc()[-3000:], "ERRO"
            falhas += 1
        seg = (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - t).total_seconds()
        print(f"== {nome}: {status} ({seg:.0f}s)\n{saida}\n", flush=True)
        blocos.append(f"## {nome} — {status} ({seg:.0f}s)\n\n```\n{saida}\n```\n")
        hist.append({"rodada": f"{inicio:%d/%m/%Y %H:%M}", "etapa": nome, "status": status, "segundos": round(seg),
                     "resumo": saida.splitlines()[0][:200] if saida else ""})
    doc = RAIZ / "docs"
    (doc / "rotina_ultima_execucao.md").write_text(
        f"# Rotina diária — rodada de {inicio:%d/%m/%Y %H:%M} (horário de Brasília)\n\n"
        f"Etapas com erro: {falhas}. Saída literal de cada etapa abaixo.\n\n" + "\n".join(blocos), encoding="utf-8")
    H = pd.DataFrame(hist)
    arq = doc / "rotina_historico.csv"
    H.to_csv(arq, mode="a", header=not arq.exists(), sep=";", index=False, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
