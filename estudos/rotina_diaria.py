"""Rotina diária do mercado de FIIs (roda no GitHub Actions, à noite, depois do fechamento da B3) — 23/11/2026.

Cada etapa roda separada: erro numa não para as outras. A saída literal de cada rodada fica em
docs/rotina_ultima_execucao.md e o resumo de todas as rodadas em docs/rotina_historico.csv.

Etapas e tabelas:
  1 preços dos FIIs (arquivo diário COTAHIST da B3)  -> planilhas/precos_AAAA.csv      (estudos/atualizar_precos.py)
  2 mercado de fundos e CDI                           -> planilhas/mercado.csv, cdi.csv (estudos/atualizar_mercado_cdi.py)
  3 documentos dos FIIs (FNET)                        -> planilhas/rotina/fnet_documentos_AAAA-MM.csv
                                                         planilhas/rotina/fnet_rendimentos_AAAA.csv
                                                         planilhas/rotina/fnet_textos/AAAA-MM-DD.csv.gz (texto dos PDFs do dia)
  4 dólar, IFIX e Ibovespa (diário)                   -> planilhas/rotina/indicadores_diarios.csv
  5 IPCA e IGP-M (mensal)                             -> planilhas/rotina/indicadores_mensais.csv
  6 Boletim Focus (Selic, IPCA, câmbio)               -> planilhas/rotina/focus.csv
  7 juros futuros da B3 (DI x pré e DI x IPCA)        -> planilhas/rotina/juros_b3.csv

Fontes: B3 (COTAHIST, taxas referenciais), FNET, CVM, Banco Central (SGS e Focus) — oficiais.
IFIX e Ibovespa: Yahoo Finance (não oficial; a B3 não tem histórico diário aberto que funcionou no teste de 23/11/2026).
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
    return (dt.datetime.utcnow() - dt.timedelta(hours=3)).date()


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


# ---------------------------------------------------------------- 1 preços
def etapa_precos() -> str:
    ult = ultima_data_precos()
    zips, faltam = [], []
    d = ult + dt.timedelta(days=1)
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


def yahoo(simbolo: str, ini: dt.date) -> pd.Series:
    p1 = int(dt.datetime(ini.year, ini.month, ini.day, tzinfo=dt.timezone.utc).timestamp())
    p2 = int(dt.datetime.now(dt.timezone.utc).timestamp())
    j = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}?period1={p1}&period2={p2}&interval=1d").json()
    r = j["chart"]["result"][0]
    datas = pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/Sao_Paulo").tz_localize(None).normalize()
    s = pd.Series(r["indicators"]["quote"][0]["close"], index=datas, dtype=float).dropna()
    return s[~s.index.duplicated(keep="last")].round(2)


def etapa_diarios() -> str:
    arq = ROT / "indicadores_diarios.csv"
    velho = ler(arq)
    ini = INICIO_HIST if velho is None else (pd.to_datetime(velho["data"], dayfirst=True).max() - pd.Timedelta(days=10)).date()
    s = {"dolar_ptax_venda (R$)": sgs(1, ini), "ifix (pontos)": yahoo("IFIX.SA", ini), "ibovespa (pontos)": yahoo("%5EBVSP", ini)}
    N = pd.DataFrame(s).sort_index()
    N = N[N.index.dayofweek < 5].dropna(how="all")
    N.insert(0, "data", N.index.strftime("%d/%m/%Y"))
    a, b = juntar(arq, N.reset_index(drop=True), ["data"], ["data"])
    ult = N.tail(3).to_string(index=False)
    return f"indicadores_diarios.csv: {a} -> {b} linhas (desde {ini:%d/%m/%Y}; IFIX e Ibovespa pelo Yahoo Finance)\núltimos dias:\n{ult}"


# ---------------------------------------------------------------- 5 IPCA e IGP-M
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
        r = get(base, params={"$filter": filtro, "$select": "Indicador,Data,DataReferencia,Mediana", "$format": "json",
                              "$top": 5000, "$skip": pulo, "$orderby": "Data"})
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
def etapa_juros() -> str:
    arq = ROT / "juros_b3.csv"
    velho = ler(arq)
    p = ultima_data_precos()
    if velho is None:
        dias = [p]
    else:
        u = pd.to_datetime(velho["data"], dayfirst=True).max().date()
        dias = sorted({d.date() for d in pd.bdate_range(u + dt.timedelta(days=1), p)})[-10:]
    L, linhas = [], []
    for d in dias:
        for codigo, nome in (("PRE", "DI x pré"), ("DIC", "DI x IPCA")):
            url = (f"https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?"
                   f"Data={d:%d/%m/%Y}&Data1={d:%Y%m%d}&slcTaxa={codigo}")
            try:
                html = get(url, timeout=60).content.decode("latin-1")
                tabs = pd.read_html(io.StringIO(html), decimal=",", thousands=".")
            except Exception as e:  # noqa: BLE001
                linhas.append(f"{d:%d/%m} {nome}: sem resposta ({type(e).__name__})")
                continue
            t = next((t for t in tabs if t.shape[1] >= 2 and t.shape[0] > 3), None)
            if t is None:
                linhas.append(f"{d:%d/%m} {nome}: página sem tabela")
                continue
            t.columns = [" ".join(str(x) for x in (c if isinstance(c, tuple) else (c,))).strip() for c in t.columns]
            t = t.rename(columns={t.columns[0]: "dias_corridos"})
            t = t.melt(id_vars="dias_corridos", var_name="coluna", value_name="taxa (% ao ano)")
            t["taxa (% ao ano)"] = pd.to_numeric(t["taxa (% ao ano)"], errors="coerce")
            t = t.dropna(subset=["taxa (% ao ano)"])
            t.insert(0, "curva", nome)
            t.insert(0, "data", f"{d:%d/%m/%Y}")
            L.append(t)
            linhas.append(f"{d:%d/%m} {nome}: {len(t)} pontos")
    if not L:
        return "\n".join(linhas or ["nada novo"])
    N = pd.concat(L, ignore_index=True)
    N["dias_corridos"] = pd.to_numeric(N["dias_corridos"], errors="coerce")
    N = N.dropna(subset=["dias_corridos"])
    N["dias_corridos"] = N["dias_corridos"].astype(int)
    a, b = juntar(arq, N, ["data", "curva", "coluna", "dias_corridos"], ["data", "curva", "dias_corridos"])
    return "\n".join([f"juros_b3.csv: {a} -> {b} linhas"] + linhas)


ETAPAS = [("1 preços dos FIIs (B3)", etapa_precos), ("2 mercado de fundos e CDI", etapa_mercado),
          ("3 documentos dos FIIs (FNET)", etapa_fnet), ("4 dólar, IFIX e Ibovespa", etapa_diarios),
          ("5 IPCA e IGP-M", etapa_mensais), ("6 Boletim Focus", etapa_focus), ("7 juros futuros da B3", etapa_juros)]


def main() -> int:
    inicio = dt.datetime.utcnow() - dt.timedelta(hours=3)
    so = set(sys.argv[1:])
    blocos, hist, falhas = [], [], 0
    for nome, f in ETAPAS:
        if so and nome[0] not in so:
            continue
        t = dt.datetime.utcnow()
        try:
            saida, status = f(), "OK"
        except Exception:  # noqa: BLE001
            saida, status = traceback.format_exc()[-3000:], "ERRO"
            falhas += 1
        seg = (dt.datetime.utcnow() - t).total_seconds()
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
