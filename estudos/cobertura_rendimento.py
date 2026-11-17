"""Cobertura do rendimento: o fundo ganha em dinheiro o que distribui? (pedido do dono, 17/11/2026, depois do caso LIFE11)

Fonte: informe trimestral da CVM (dados.cvm.gov.br/dados/FII/DOC/INF_TRIMESTRAL), tabela "resultado contábil e financeiro"
(regime de caixa: sem apreciação de ativo nem correção monetária só contábil) e tabela "geral" (data de entrega e ISIN).
O relatório gerencial em PDF tem um formato diferente em cada gestora; o informe trimestral traz os mesmos números num formato
único para todos os fundos, por isso é a fonte usada aqui.

Como o formulário da CVM soma o semestre (conferido em 17/11/2026 nos dados de 2017 a 2026):
  - no 2º e 4º trimestres, "Resultado_Financeiro_Liquido_Acumulado" e "Rendimentos_Declarados" são do semestre inteiro
    (mediana do declarado do 2º tri ÷ 1º tri = 2,0 em 3.789 casos);
  - em 90% dos informes, "Percentual_Resultado_Financeiro_Liquido_Declarado" = declarado ÷ resultado acumulado.
  Por isso se usa sempre o PAR (resultado acumulado, declarado) do mesmo informe.

Regra (fixada ANTES de rodar a carteira):
  No dia d, só informes ENTREGUES até d (Data_Entrega <= d). Janela = último informe de fim de semestre (jun/dez) entregue
  + o informe do trimestre seguinte (mar/set), se já entregue. Dá 6 a 9 meses.
  cobertura = soma(resultado acumulado − ganho com venda de imóveis e papéis) ÷ soma(rendimento declarado).
  Ganho com venda = Resultado_Venda_TVM + (Receita_Venda_Investimento + Custo_Investimento) + Resultado_Venda_Aplicacao
  (regime de caixa), somado nos trimestres do mesmo semestre do informe.
  Sem informe de fim de semestre com menos de 15 meses, ou declarado <= 0: sem medida (não barra).
  Filtro da carteira: cobertura < 0,90 → não compra.

    PYTHONPATH=. python3 estudos/cobertura_rendimento.py          # monta a tabela e roda o teste no passado
"""
import os
import subprocess
import zipfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
TAB = RAIZ / "planilhas" / "tecnico" / "cobertura_trimestral.csv"
PASTA_CVM = Path(os.environ.get("COBERTURA_CVM", "/tmp/claude-0/cvm_tri"))
URL = "https://dados.cvm.gov.br/dados/FII/DOC/INF_TRIMESTRAL/DADOS/inf_trimestral_fii_{a}.zip"
LIMITE = 0.90
VENDAS = ["Resultado_Venda_TVM_Financeiro", "Receita_Venda_Investimento_Financeiro", "Custo_Investimento_Financeiro",
          "Resultado_Venda_Aplicacao_Financeiro"]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")


def _ler(z, nome):
    df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str)
    return df.rename(columns={"CNPJ_Fundo": "CNPJ_Fundo_Classe", "Nome_Fundo": "Nome_Fundo_Classe"})


def montar():
    """Baixa os zips que faltam (2017 a 2026), monta uma linha por fundo e informe e grava TAB."""
    PASTA_CVM.mkdir(parents=True, exist_ok=True)
    L, G = [], []
    for a in range(2017, 2027):
        zp = PASTA_CVM / f"inf_trimestral_fii_{a}.zip"
        if not zp.exists():
            subprocess.run(["curl", "-sS", "-f", "-o", str(zp), URL.format(a=a)], check=True)
        with zipfile.ZipFile(zp) as z:
            L.append(_ler(z, f"inf_trimestral_fii_resultado_contabil_financeiro_{a}.csv"))
            G.append(_ler(z, f"inf_trimestral_fii_geral_{a}.csv")[["CNPJ_Fundo_Classe", "Data_Referencia", "Versao",
                                                                   "Data_Entrega", "Codigo_ISIN", "Nome_Fundo_Classe"]])
    k = ["CNPJ_Fundo_Classe", "Data_Referencia"]
    R, G = pd.concat(L), pd.concat(G)
    for X in (R, G):
        X["Versao"] = pd.to_numeric(X["Versao"], errors="coerce").fillna(0)
    R = R.sort_values("Versao").drop_duplicates(k, keep="last")
    G = G.sort_values("Versao").drop_duplicates(k, keep="last")
    R = R.merge(G.drop(columns="Versao"), on=k, how="left")
    num = ["Resultado_Financeiro_Liquido_Acumulado", "Rendimentos_Declarados", "Resultado_Trimestral_Liquido_Financeiro"] + VENDAS
    for c in num:
        R[c] = pd.to_numeric(R[c], errors="coerce")
    R["venda_tri"] = R[VENDAS].fillna(0).sum(axis=1)
    R["data_ref"] = pd.to_datetime(R["Data_Referencia"])
    R["entrega"] = pd.to_datetime(R["Data_Entrega"], errors="coerce")
    R["sem"] = R["data_ref"].dt.year.astype(str) + "S" + np.where(R["data_ref"].dt.month <= 6, "1", "2")
    # ganho com venda do semestre até o informe: soma dos trimestres do mesmo semestre com data <= a do informe
    R = R.sort_values(["CNPJ_Fundo_Classe", "data_ref"])
    R["venda_sem"] = R.groupby(["CNPJ_Fundo_Classe", "sem"])["venda_tri"].cumsum()
    isin = R["Codigo_ISIN"].fillna("").str.upper()
    R["fundo"] = np.where(isin.str.match(r"^BR[A-Z]{4}CTF"), isin.str[2:6] + "11", None)
    out = R[["fundo", "CNPJ_Fundo_Classe", "Nome_Fundo_Classe", "data_ref", "entrega", "Resultado_Financeiro_Liquido_Acumulado",
             "venda_sem", "Rendimentos_Declarados", "Resultado_Trimestral_Liquido_Financeiro"]].rename(columns={
        "CNPJ_Fundo_Classe": "cnpj", "Nome_Fundo_Classe": "nome", "Resultado_Financeiro_Liquido_Acumulado": "resultado_acumulado",
        "venda_sem": "ganho_venda_semestre", "Rendimentos_Declarados": "rendimento_declarado",
        "Resultado_Trimestral_Liquido_Financeiro": "resultado_trimestre"})
    out = out.dropna(subset=["fundo"])
    out.to_csv(TAB, index=False, date_format="%d/%m/%Y", **OP)
    return out


@lru_cache(maxsize=1)
def _tabela():
    T = pd.read_csv(TAB, **OP)
    for c in ("data_ref", "entrega"):
        T[c] = pd.to_datetime(T[c], dayfirst=True)
    return {f: x.sort_values("data_ref") for f, x in T.groupby("fundo")}


def cobertura(fundo, dia):
    """dict(cobertura, janela, resultado, declarado) com informes entregues até `dia`; None se não houver medida."""
    T = _tabela().get(fundo)
    if T is None:
        return None
    d = pd.Timestamp(dia)
    x = T[(T["entrega"] <= d) & T["rendimento_declarado"].notna() & T["resultado_acumulado"].notna()]
    fs = x[x["data_ref"].dt.month.isin([6, 12])]
    if fs.empty or fs["data_ref"].iloc[-1] < d - pd.DateOffset(months=15):
        return None
    j = [fs.iloc[-1]]
    seg = x[x["data_ref"] > fs["data_ref"].iloc[-1]]
    if len(seg):
        j.append(seg.iloc[-1])
    res = sum(float(r["resultado_acumulado"]) - float(r["ganho_venda_semestre"]) for r in j)
    dec = sum(float(r["rendimento_declarado"]) for r in j)
    if dec <= 0:
        return None
    return dict(cobertura=res / dec, janela=" + ".join(f"{r['data_ref']:%m/%Y}" for r in j), resultado=res, declarado=dec)


def teste_passado():
    """No fim de cada mês (2019 a 2026), fundos com patrimônio >= R$ 100 mi: a cobertura antecipa corte de rendimento e
    queda da cota nos 6 meses seguintes?"""
    P = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{a}.csv", **OP, usecols=["data", "fundo", "fechamento", "patrimonio (R$)"])
                   for a in range(2018, 2027)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    PF = {f: x.set_index("data")["fechamento"].sort_index() for f, x in P.groupby("fundo")}
    M = pd.read_csv(RAIZ / "planilhas/mercado.csv", **OP)
    M["data"] = pd.to_datetime(M["data"], dayfirst=True)
    M = M.set_index("data")["indice_mercado"]
    R = pd.read_csv(RAIZ / "planilhas/rendimentos_pagamentos.csv", **OP)
    R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
    R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
    RM = {f: x.groupby(x["data_base"].dt.to_period("M"))["valor (R$/cota)"].sum() for f, x in R.groupby("fundo")}
    dias = pd.Series(sorted(P["data"].unique()))
    fims = dias.groupby(dias.dt.to_period("M")).max()
    fims = fims[(fims >= "2019-01-01") & (fims <= "2026-05-31")]
    L = []
    for d in fims:
        x = P[(P["data"] == d) & (P["patrimonio (R$)"] >= 100e6)]
        p0 = d.to_period("M")
        for f in x["fundo"]:
            c = cobertura(f, d)
            r = RM.get(f)
            if c is None or r is None:
                continue
            antes = r.reindex(pd.period_range(p0 - 2, p0))
            depois = r.reindex(pd.period_range(p0 + 4, p0 + 6))
            if antes.isna().any() or depois.isna().any() or antes.mean() <= 0:   # só com os 3 meses informados
                continue
            s = PF[f]
            a6 = s.loc[:d + pd.DateOffset(months=6)]
            if a6.index[-1] < d + pd.DateOffset(months=5):
                continue
            mk = float(M.loc[:d + pd.DateOffset(months=6)].iloc[-1] / M.loc[:d].iloc[-1] - 1)
            L.append(dict(fundo=f, dia=d, cobertura=c["cobertura"], var_rend=depois.mean() / antes.mean() - 1,
                          cota_6m=float(a6.iloc[-1] / s.loc[:d].iloc[-1] - 1), mercado_6m=mk))
    T = pd.DataFrame(L)
    T["corte_10"] = T["var_rend"] < -0.10
    T["cota_contra_mercado"] = T["cota_6m"] - T["mercado_6m"]
    T["faixa"] = pd.cut(T["cobertura"], [-np.inf, 0.7, 0.8, 0.9, 1.0, 1.1, np.inf],
                        labels=["< 0,70", "0,70–0,80", "0,80–0,90", "0,90–1,00", "1,00–1,10", ">= 1,10"])
    G = T.groupby("faixa", observed=True).agg(casos=("fundo", "size"), fundos=("fundo", "nunique"),
                                              corte_rend_10pct=("corte_10", "mean"), var_rend_mediana=("var_rend", "median"),
                                              cota_contra_mercado_media=("cota_contra_mercado", "mean"),
                                              cota_contra_mercado_mediana=("cota_contra_mercado", "median"))
    return T, G


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    T = montar()
    print(f"tabela: {len(T)} informes, {T['fundo'].nunique()} fundos, {T['data_ref'].min():%m/%Y} a {T['data_ref'].max():%m/%Y} -> {TAB.relative_to(RAIZ)}")
    for f, d in [("LIFE11", "2026-11-17"), ("LIFE11", "2026-06-30"), ("XPCM11", "2019-07-31"), ("KNCR11", "2026-11-17")]:
        print(f, d, cobertura(f, d))
    X, G = teste_passado()
    print(f"\nTESTE NO PASSADO: {len(X)} casos (fundo × fim de mês, 01/2019 a 05/2026, patrimônio >= R$ 100 mi)")
    print("corte = rendimento médio dos meses +4 a +6 mais de 10% abaixo dos 3 últimos meses; cota contra mercado em 6 meses")
    print(G.to_string(float_format=lambda v: f"{v:+.3f}"))
    baixa = X["cobertura"] < LIMITE
    print(f"\ncobertura < {LIMITE}: {baixa.sum()} casos, corte {X.loc[baixa, 'corte_10'].mean():.1%}, cota contra mercado "
          f"{X.loc[baixa, 'cota_contra_mercado'].mean():+.1%}  |  >= {LIMITE}: {(~baixa).sum()} casos, corte "
          f"{X.loc[~baixa, 'corte_10'].mean():.1%}, cota contra mercado {X.loc[~baixa, 'cota_contra_mercado'].mean():+.1%}")
    X.to_csv(RAIZ / "planilhas/tecnico/cobertura_teste_passado.csv", index=False, date_format="%d/%m/%Y", **OP)
    G.to_csv(RAIZ / "planilhas/cobertura_teste_faixas.csv", **OP)
