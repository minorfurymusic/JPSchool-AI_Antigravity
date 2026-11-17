"""Teste rápido (brainstorm): fundos com rendimento >= 15% ao ano sobre o preço e preço <= 0,85 do patrimônio.
No último pregão de cada mês, 2018 a 2025: retorno total em 12 meses (preço + rendimentos com data-base no período),
contra os demais fundos do universo e contra o CDI. Separa por rendimento estável ou caindo nos 12 meses anteriores.

    PYTHONPATH=. python3 estudos/dividendo_alto_rapido.py
"""
import numpy as np
import pandas as pd

O = dict(sep=";", decimal=",", encoding="utf-8-sig")
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", **O) for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P.sort_values(["fundo", "data"])
R = pd.read_csv("planilhas/rendimentos_pagamentos.csv", **O)
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
CDI = pd.read_csv("planilhas/cdi.csv", **O)
CDI["data"] = pd.to_datetime(CDI["data"], dayfirst=True)
I = CDI.set_index("data")["indice_105_do_cdi"]
T = pd.read_csv("planilhas/fundos.csv", sep=";", encoding="utf-8-sig").set_index("fundo")["tipo"]
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
RF = {f: x.set_index("data_base")["valor (R$/cota)"].sort_index() for f, x in R.groupby("fundo")}
datas = P.groupby(P["data"].dt.to_period("M"))["data"].max()
datas = datas[(datas >= "2018-01-01") & (datas <= "2025-10-31")]
L = []
for d in datas:
    fim = d + pd.DateOffset(months=12)
    cdi = I.loc[:fim].iloc[-1] / I.loc[:d].iloc[-1] - 1
    x = P[P["data"] == d]
    x = x[(x["patrimonio (R$)"] >= 50e6) & (x["volume_medio_60 (R$)"] >= 100e3) & (x["rendimento_mensal (R$/cota)"] > 0)]
    for r in x.itertuples():
        p = PF[r.fundo]
        depois = p.loc[d + pd.Timedelta(days=1):fim]
        if len(depois) < 150:
            continue
        rend = RF.get(r.fundo, pd.Series(dtype=float))
        div = rend.loc[d + pd.Timedelta(days=1):fim].sum()
        ant = rend.loc[d - pd.DateOffset(months=12):d]
        a3, p3 = ant.iloc[-3:].mean() if len(ant) >= 6 else np.nan, ant.iloc[:3].mean() if len(ant) >= 6 else np.nan
        L.append(dict(data=d, fundo=r.fundo, tipo=T.get(r.fundo, "?"), dy=r._11 / 100 if False else getattr(r, "_11", np.nan),
                      ret=(depois["fechamento"].iloc[-1] + div) / r.fechamento - 1, preco=depois["fechamento"].iloc[-1] / r.fechamento - 1,
                      cdi=cdi, tend=a3 / p3 - 1 if p3 else np.nan))
D = pd.DataFrame(L)
X = P.set_index(["data", "fundo"])[["rendimento_ano_sobre_preco (%)", "preco_sobre_valor_patrimonial"]]
D = D.join(X, on=["data", "fundo"])
D["dy"] = D["rendimento_ano_sobre_preco (%)"] / 100
D["pvp"] = D["preco_sobre_valor_patrimonial"]
D["grupo"] = np.where((D["dy"] >= 0.15) & (D["pvp"] <= 0.85), "rend. >= 15% e P/VP <= 0,85", "demais fundos")
D["saude"] = np.where(D["tend"] < -0.10, "rendimento caindo > 10%", "rendimento estável ou subindo")
agg = dict(casos=("ret", "size"), fundos=("fundo", "nunique"), retorno_12m=("ret", "mean"), mediana=("ret", "median"),
           so_preco=("preco", "mean"), cdi=("cdi", "mean"), perdeu_do_cdi=("ret", lambda s: np.nan),
           prejuizo=("ret", lambda s: (s < 0).mean()))
pd.set_option("display.width", 250)
def tab(g):
    t = D.groupby(g).agg(**{k: v for k, v in agg.items() if k != "perdeu_do_cdi"})
    t["ganhou_do_cdi"] = D.groupby(g).apply(lambda x: (x["ret"] > x["cdi"]).mean())
    return t.round(3)
print(tab("grupo").to_string())
print(tab(["grupo", "saude"]).to_string())
H = D[D["grupo"] != "demais fundos"]
print(H.groupby("tipo").agg(casos=("ret", "size"), retorno=("ret", "mean"), prejuizo=("ret", lambda s: (s < 0).mean())).round(3).to_string())
print(H.groupby(H["data"].dt.year).agg(casos=("ret", "size"), fundos=("fundo", "nunique"), retorno=("ret", "mean"),
                                       cdi=("cdi", "mean")).round(3).to_string())
D.to_csv("planilhas/tecnico/dividendo_alto_rapido.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
