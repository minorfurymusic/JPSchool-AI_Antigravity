"""Monta a base de trabalho a partir dos arquivos oficiais já baixados.

Saída: tabelas no banco local.
  cotacoes        preço diário oficial de cada papel de FII
  fundos          cadastro (CVM) de cada fundo
  vinculo         papel da bolsa <-> CNPJ na CVM (só quando o ISIN bate sem ambiguidade)
  sem_vinculo     papéis que precisam de revisão manual
  quebras         saltos de preço (desdobramento/grupamento) e se foram confirmados
  mensal          uma linha por fundo e mês: preço, valor patrimonial, rendimento por cota...
  vendas, compras imóveis vendidos/comprados (informe trimestral)
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from . import b3_cotacoes, config, cvm

LIMITE_QUEBRA = (0.55, 1.8)


def conectar(caminho: Path | None = None) -> duckdb.DuckDBPyConnection:
    caminho = caminho or config.BANCO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(caminho))


def gravar(con, nome: str, df: pd.DataFrame) -> None:
    con.register("_tmp", df)
    con.execute(f"create or replace table {nome} as select * from _tmp")
    con.unregister("_tmp")


# ---------------------------------------------------------------- cotações
def carregar_cotacoes(pasta: Path, cache: Path) -> pd.DataFrame:
    """Lê todos os arquivos da B3 da pasta. Guarda cada arquivo já lido para não reler."""
    cache.mkdir(parents=True, exist_ok=True)
    partes = []
    for zp in sorted(pasta.glob("COTAHIST_*.ZIP")):
        pq = cache / (zp.stem + ".parquet")
        if not pq.exists() or pq.stat().st_mtime < zp.stat().st_mtime:
            b3_cotacoes.ler_arquivo(zp).to_parquet(pq, index=False)
        partes.append(pd.read_parquet(pq))
    df = pd.concat(partes, ignore_index=True)
    # o mesmo pregão pode vir no arquivo anual e no diário: fica um só
    df = df.drop_duplicates(subset=["ticker", "data"], keep="last")
    return df.sort_values(["ticker", "data"]).reset_index(drop=True)


# ---------------------------------------------------------------- vínculo
def montar_vinculo(cot: pd.DataFrame, geral: pd.DataFrame):
    """Liga papel a CNPJ pelo ISIN, usando todo ISIN que o fundo já informou à CVM.
    Um papel pode apontar para mais de um CNPJ (fundo que trocou de CNPJ ao virar
    "classe"). Se os dois informam os mesmos meses, é ambíguo: ver `resolver_conflitos`."""
    isins = geral[["CNPJ_Fundo_Classe", "Codigo_ISIN"]].dropna()
    isins = isins.assign(Codigo_ISIN=isins["Codigo_ISIN"].str.strip())
    isins = isins[isins["Codigo_ISIN"].str.len() == 12].drop_duplicates()
    ult = cot.sort_values("data").groupby("ticker").tail(1)[["ticker", "isin", "nome", "data"]]
    ult = ult.rename(columns={"data": "ultimo_pregao"})
    vinc = ult.merge(isins.rename(columns={"Codigo_ISIN": "isin", "CNPJ_Fundo_Classe": "cnpj"}), on="isin", how="left")
    sem = vinc[vinc["cnpj"].isna()][["ticker", "isin", "nome", "ultimo_pregao"]].assign(
        motivo="ISIN não encontrado nos informes da CVM")
    return vinc.dropna(subset=["cnpj"]).reset_index(drop=True), sem.reset_index(drop=True)


MAX_MESES_EM_CONFLITO = 6


def resolver_conflitos(linhas: pd.DataFrame):
    """`linhas`: informes mensais já ligados a um papel (colunas ticker, cnpj, mes, pl).
    Papel ligado a 2 CNPJs que informam os mesmos meses por muito tempo é ambíguo e sai."""
    dup = linhas.groupby(["ticker", "mes"])["cnpj"].nunique()
    conflitos = dup[dup > 1].groupby("ticker").size()
    ambiguos = set(conflitos[conflitos > MAX_MESES_EM_CONFLITO].index)
    boas = linhas[~linhas["ticker"].isin(ambiguos)].sort_values(["ticker", "mes", "pl"])
    boas = boas.drop_duplicates(subset=["ticker", "mes"], keep="last")
    return boas, ambiguos


# ---------------------------------------------------------------- quebras de preço
def achar_quebras(cot: pd.DataFrame, cotas_mes: pd.DataFrame, vinc: pd.DataFrame, desdobramentos: dict | None = None) -> pd.DataFrame:
    """Salto de preço de um pregão para o outro grande demais para ser mercado.
    Confirmado quando o número de cotas na CVM muda na proporção inversa."""
    c = cot[["ticker", "data", "fechamento"]].copy()
    c["ant"] = c.groupby("ticker")["fechamento"].shift()
    c["data_ant"] = c.groupby("ticker")["data"].shift()
    c["razao"] = c["fechamento"] / c["ant"]
    q = c[(c["razao"] < LIMITE_QUEBRA[0]) | (c["razao"] > LIMITE_QUEBRA[1])].copy()
    q = q[(q["data"] - q["data_ant"]).dt.days <= 15]
    if q.empty:
        return q.assign(confirmada=False, confirmada_cvm=False, confirmada_b3=False, fator_cotas=np.nan)
    cm = cotas_mes.merge(vinc[["ticker", "cnpj"]], on="cnpj").groupby(["ticker", "mes"])["cotas"].max()
    desdobramentos = desdobramentos or {}

    def razao_cotas(l):
        m = l["data"].to_period("M")
        antes = [cm.get((l["ticker"], (m - k).to_timestamp())) for k in (1, 2)]
        depois = [cm.get((l["ticker"], (m + k).to_timestamp())) for k in (0, 1)]
        antes = next((x for x in antes if x and x > 0), None)
        depois = next((x for x in depois if x and x > 0), None)
        return depois / antes if antes and depois else np.nan

    def b3_confirma(l):
        for d in desdobramentos.get(l["ticker"][:4], []):
            if d.get("data_com") and abs((pd.Timestamp(d["data_com"]) - l["data"]).days) <= 10:
                return True
        return False

    q["fator_cotas"] = q.apply(razao_cotas, axis=1)
    esperado = 1 / q["razao"]
    q["confirmada_cvm"] = (q["fator_cotas"] / esperado).between(0.75, 1.35)
    q["confirmada_b3"] = q.apply(b3_confirma, axis=1)
    q["confirmada"] = q["confirmada_cvm"] | q["confirmada_b3"]
    return q[["ticker", "data", "ant", "fechamento", "razao", "fator_cotas", "confirmada_cvm", "confirmada_b3", "confirmada"]]


def fator_de_ajuste(datas: pd.Series, quebras_ticker: pd.DataFrame) -> np.ndarray:
    """Fator que leva preços antigos para a base de cotas de hoje."""
    f = np.ones(len(datas))
    for _, q in quebras_ticker.iterrows():
        f[(datas < q["data"]).to_numpy()] *= q["razao"]
    return f


# ---------------------------------------------------------------- painel mensal
def montar_mensal(cot, vinc, comp, ap, quebras, rend_b3: dict | None = None):
    comp = comp.copy()
    for col in ["Total_Numero_Cotistas", "Patrimonio_Liquido", "Cotas_Emitidas", "Valor_Patrimonial_Cotas",
                "Percentual_Dividend_Yield_Mes", "Percentual_Amortizacao_Cotas_Mes"]:
        comp[col] = cvm.numero(comp[col])
    ap = ap.copy()
    for col in ["Rendimentos_Distribuir", "Total_Investido", "Direitos_Bens_Imoveis", "CRI", "FII", "Total_Passivo"]:
        ap[col] = cvm.numero(ap[col])
    f = comp.merge(ap, on=["CNPJ_Fundo_Classe", "Data_Referencia"], how="left", suffixes=("", "_ap"))
    f = f.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Data_Referencia": "mes", "Cotas_Emitidas": "cotas",
                          "Valor_Patrimonial_Cotas": "vp_cota", "Patrimonio_Liquido": "pl",
                          "Total_Numero_Cotistas": "cotistas", "Percentual_Dividend_Yield_Mes": "dy_cvm"})
    f = f.sort_values(["cnpj", "mes"])
    f["rend_a"] = np.where(f["cotas"] > 0, f["Rendimentos_Distribuir"] / f["cotas"], np.nan)
    f["rend_b"] = f["dy_cvm"] * f["vp_cota"]
    cotas_ant = f.groupby("cnpj")["cotas"].shift()
    # mês com emissão de cotas distorce o rendimento por cota: marcar para não gerar alarme falso
    f["emissao"] = ((f["cotas"] / cotas_ant - 1).abs() > 0.02).fillna(False)
    f["pct_imoveis"] = f["Direitos_Bens_Imoveis"] / f["Total_Investido"]
    f["pct_papel"] = (f["CRI"].fillna(0)) / f["Total_Investido"]
    f["pct_fundos"] = (f["FII"].fillna(0)) / f["Total_Investido"]

    fund = f[["cnpj", "mes", "cotas", "vp_cota", "pl", "cotistas", "dy_cvm", "rend_a", "rend_b", "emissao",
              "pct_imoveis", "pct_papel", "pct_fundos"]].merge(vinc[["ticker", "cnpj"]], on="cnpj")
    fund, ambiguos = resolver_conflitos(fund)

    c = cot[cot["ticker"].isin(set(vinc["ticker"]) - ambiguos)]
    conf = quebras[quebras["confirmada"]] if len(quebras) else quebras
    partes = []
    for tk, g in c.groupby("ticker", sort=False):
        g = g.sort_values("data").copy()
        g["fator"] = fator_de_ajuste(g["data"], conf[conf["ticker"] == tk]) if len(conf) else 1.0
        g["fech_aj"] = g["fechamento"] * g["fator"]
        partes.append(g)
    c = pd.concat(partes, ignore_index=True)
    c["mes"] = c["data"].dt.to_period("M").dt.to_timestamp()
    ag = c.groupby(["ticker", "mes"]).agg(
        preco_fim=("fech_aj", "last"), preco_ini=("fech_aj", "first"),
        preco_d10=("fech_aj", lambda s: s.iloc[min(9, len(s) - 1)]),
        vol_medio=("volume", "mean"), pregoes=("data", "count"), fator=("fator", "last"),
        data_fim=("data", "last")).reset_index()
    m = ag.merge(fund, on=["ticker", "mes"], how="left")

    # meses que a CVM ainda não publicou: rendimento anunciado na B3
    isin_de = cot.sort_values("data").groupby("ticker")["isin"].last()
    linhas_b3 = []
    for tk in m["ticker"].unique():
        dado = (rend_b3 or {}).get(tk[:4])
        if not dado:
            continue
        for r in dado["rendimentos"]:
            if r["isin"] != isin_de.get(tk) or r["tipo"] != "RENDIMENTO" or not r["valor"]:
                continue
            ref = mes_da_data_com(r)
            if ref is not None:
                linhas_b3.append({"ticker": tk, "mes": ref, "rend_b3": r["valor"], "anuncio_b3": r["anuncio"],
                                  "data_com_b3": r["data_com"], "pagamento_b3": r["pagamento"]})
    if linhas_b3:
        b3 = pd.DataFrame(linhas_b3).groupby(["ticker", "mes"]).agg(
            rend_b3=("rend_b3", "sum"), anuncio_b3=("anuncio_b3", "max"), data_com_b3=("data_com_b3", "max"),
            pagamento_b3=("pagamento_b3", "max")).reset_index()
        m = m.merge(b3, on=["ticker", "mes"], how="left")
    else:
        m = m.assign(rend_b3=np.nan, anuncio_b3=None, data_com_b3=None, pagamento_b3=None)
    m["emissao"] = m["emissao"].fillna(False).astype(bool)
    m = m.sort_values(["ticker", "mes"]).reset_index(drop=True)
    m["rend_cota"], m["origem_rend"], m["regra_rend"] = np.nan, None, None
    for tk, g in m.groupby("ticker", sort=False):
        final, origem, regra = escolher_serie(g)
        m.loc[g.index, "rend_cota"] = final
        m.loc[g.index, "origem_rend"] = origem
        m.loc[g.index, "regra_rend"] = regra
    # rendimento e valor patrimonial antigos na base de cotas de hoje
    m["rend_aj"] = m["rend_cota"] * m["fator"]
    m["vp_aj"] = m["vp_cota"] * m["fator"]
    m["pvp"] = m["preco_fim"] / m["vp_aj"]
    return m.sort_values(["ticker", "mes"]).reset_index(drop=True), ambiguos


def mes_da_data_com(r: dict):
    """Mês em que o rendimento passa a ser do cotista. O texto de referência da B3
    vem em formatos demais ("OUTUBRO/2026", "Setembro-2026/2026", "4º QUADRIMESTRE 2025/2026")
    e nem sempre é o mês em que o dinheiro é anunciado; a data limite é inequívoca."""
    if r.get("data_com"):
        return pd.Timestamp(r["data_com"]).to_period("M").to_timestamp()
    return None


TOLERANCIA_SERIE = 0.08
MIN_ACORDO = 0.85


def escolher_serie(g: pd.DataFrame) -> tuple[pd.Series, pd.Series, str]:
    """Escolhe, para um fundo, de onde vem o rendimento por cota de cada mês.

    A B3 publica o valor anunciado (confiável), mas só dos últimos ~12 meses.
    Para trás, o informe da CVM permite duas contas, e cada fundo preenche de um jeito:
      A = rendimentos a distribuir / cotas        B = rendimento do mês (%) x valor patrimonial
    Vale a conta que bate com a B3 nos meses em que há os dois. Se nenhuma bate,
    o histórico antigo desse fundo não é usado.
    """
    a, b, b3 = g["rend_a"], g["rend_b"], g["rend_b3"]
    tem = b3.notna() & (b3 > 0) & ~g["emissao"]
    acordo = {}
    for nome, serie in (("A", a), ("B", b)):
        comp = tem & serie.notna()
        acordo[nome] = float(((serie[comp] / b3[comp] - 1).abs() < TOLERANCIA_SERIE).mean()) if comp.sum() >= 4 else None
    if any(v is not None for v in acordo.values()):
        nome = max((k for k in acordo if acordo[k] is not None), key=lambda k: acordo[k])
        if acordo[nome] >= MIN_ACORDO:
            antiga, regra = (a if nome == "A" else b), f"CVM conta {nome} (bate com a B3 em {acordo[nome]:.0%} dos meses)"
        else:
            antiga, regra = pd.Series(np.nan, index=g.index), "histórico da CVM não bate com a B3: só meses da B3"
    else:
        # sem B3 para conferir (fundo que saiu da bolsa ou sem anúncio recente): exige que A e B concordem entre si
        comp = a.notna() & b.notna() & (a > 0) & (b > 0)
        if comp.sum() >= 6 and float(((a[comp] / b[comp] - 1).abs() < 0.10).mean()) >= MIN_ACORDO:
            antiga, regra = a, "CVM conta A (sem B3 para conferir; as duas contas da CVM concordam)"
        else:
            antiga, regra = pd.Series(np.nan, index=g.index), "sem B3 e as contas da CVM não concordam: sem histórico"
    final = b3.where(b3.notna(), antiga)
    origem = pd.Series(np.where(b3.notna(), "B3", np.where(antiga.notna(), "CVM", None)), index=g.index)
    return final, origem, regra


def montar_fundos(geral: pd.DataFrame) -> pd.DataFrame:
    g = geral.sort_values("Data_Referencia").groupby("CNPJ_Fundo_Classe").tail(1)
    return g.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Nome_Fundo_Classe": "nome_cvm",
                             "Segmento_Atuacao": "segmento", "Mandato": "mandato", "Tipo_Gestao": "gestao",
                             "Nome_Administrador": "administrador", "Data_Referencia": "ultimo_informe",
                             "Data_Entrega": "entrega"})[
        ["cnpj", "nome_cvm", "segmento", "mandato", "gestao", "administrador", "ultimo_informe", "entrega"]]


def montar_vendas(alien: pd.DataFrame) -> pd.DataFrame:
    v = alien.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Data_Referencia": "trimestre", "Nome_Imovel": "imovel",
                              "Data_Alienacao": "data_venda", "Percentual_Imovel_PL": "pct_pl"}).copy()
    v["data_venda"] = pd.to_datetime(v["data_venda"], errors="coerce")
    v["pct_pl"] = cvm.numero(v["pct_pl"])
    # a CVM pede fração (0,02 = 2%), mas parte dos fundos informa em pontos (2 = 2%)
    v.loc[v["pct_pl"] > 1.5, "pct_pl"] = v["pct_pl"] / 100
    return v[["cnpj", "trimestre", "imovel", "data_venda", "pct_pl"]].dropna(subset=["data_venda"]).drop_duplicates()


def montar(con=None, pasta_b3=None, pasta_cvm=None) -> dict:
    con = con or conectar()
    pasta_b3 = pasta_b3 or config.BRUTO_B3
    pasta_cvm = pasta_cvm or config.BRUTO_CVM
    cot = carregar_cotacoes(pasta_b3, config.DADOS / "cache")
    geral = cvm.ler_tabela(pasta_cvm, "inf_mensal_fii_geral")
    comp = cvm.ler_tabela(pasta_cvm, "inf_mensal_fii_complemento")
    ap = cvm.ler_tabela(pasta_cvm, "inf_mensal_fii_ativo_passivo")
    alien = cvm.ler_tabela(pasta_cvm, "inf_trimestral_fii_alienacao_imovel")
    imov = cvm.ler_tabela(pasta_cvm, "inf_trimestral_fii_imovel")

    from . import coleta
    rend_b3 = coleta.ler_fundos_b3() if config.BRUTO_FUNDOS.exists() else {}
    vinc, sem = montar_vinculo(cot, geral)
    cotas_mes = comp.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Data_Referencia": "mes"})[["cnpj", "mes"]].assign(
        cotas=cvm.numero(comp["Cotas_Emitidas"]))
    quebras = achar_quebras(cot, cotas_mes, vinc, {k: v["desdobramentos"] for k, v in rend_b3.items()})
    mensal, ambiguos = montar_mensal(cot, vinc, comp, ap, quebras, rend_b3)
    if ambiguos:
        amb = vinc[vinc["ticker"].isin(ambiguos)].drop_duplicates("ticker")[["ticker", "isin", "nome", "ultimo_pregao"]]
        sem = pd.concat([sem, amb.assign(motivo="dois CNPJs na CVM informam o mesmo ISIN nos mesmos meses")], ignore_index=True)
        vinc = vinc[~vinc["ticker"].isin(ambiguos)]
    # CNPJ atual de cada papel: o do informe mais recente
    atual = mensal.dropna(subset=["cnpj"]).sort_values("mes").groupby("ticker")["cnpj"].last()
    mensal["cnpj"] = mensal["ticker"].map(atual)
    fundos = montar_fundos(geral)
    vendas = montar_vendas(alien).merge(vinc[["ticker", "cnpj"]].drop_duplicates(), on="cnpj")

    iv = imov.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Data_Referencia": "trimestre"}).copy()
    for col in ["Percentual_Vacancia", "Percentual_Inadimplencia", "Percentual_Receitas_FII"]:
        iv[col] = cvm.numero(iv[col])
    iv = iv.rename(columns={"Nome_Imovel": "imovel", "Percentual_Vacancia": "vacancia",
                            "Percentual_Inadimplencia": "inadimplencia", "Percentual_Receitas_FII": "peso_receita"})
    iv = iv[["cnpj", "trimestre", "imovel", "vacancia", "inadimplencia", "peso_receita"]]
    iv = iv.merge(vinc[["ticker", "cnpj"]].drop_duplicates(), on="cnpj")

    for nome, df in [("cotacoes", cot), ("vinculo", vinc), ("sem_vinculo", sem), ("quebras", quebras),
                     ("mensal", mensal), ("fundos", fundos), ("vendas", vendas), ("imoveis", iv)]:
        gravar(con, nome, df)
    return {"cotacoes": len(cot), "papeis": cot["ticker"].nunique(), "vinculados": vinc["ticker"].nunique(), "sem_vinculo": len(sem),
            "quebras": len(quebras), "quebras_confirmadas": int(quebras["confirmada"].sum()) if len(quebras) else 0,
            "mensal": len(mensal), "fundos_no_mensal": mensal["ticker"].nunique(), "vendas": len(vendas),
            "primeiro_pregao": str(cot["data"].min().date()), "ultimo_pregao": str(cot["data"].max().date())}
