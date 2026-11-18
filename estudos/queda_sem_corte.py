"""Fundos que caíram muito SEM cortar o rendimento: o que fizeram nos 6 meses seguintes (pedido do dono, 18/11/2026,
para o cenário do TRXF11 com rendimento mantido em R$ 0,93).

Evento (último pregão de cada mês, 2018–2026): cota caiu 25% ou mais em 6 meses; caiu 20 pontos ou mais além do índice
de mercado; rendimento mensal do dia >= 95% do de 6 meses antes; volume_medio_60 >= R$ 1 mi; um evento por fundo a cada
6 meses. Compra na abertura do pregão seguinte. Medidas: menor fechamento em 126 pregões; preço em 63 e 126 pregões;
resultado em 126 pregões com rendimentos (data-com), antes de imposto; se o rendimento foi cortado depois.

    PYTHONPATH=. python3 estudos/queda_sem_corte.py
"""
import numpy as np
import pandas as pd

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", **OP) for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P.sort_values(["fundo", "data"])
M = pd.read_csv("planilhas/mercado.csv", **OP)
M["data"] = pd.to_datetime(M["data"], dayfirst=True)
M = M.set_index("data")["indice_mercado"]
R = pd.read_csv("planilhas/rendimentos.csv", **OP)
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
RF = {f: x for f, x in R.groupby("fundo")}
dias = pd.Series(sorted(P["data"].unique()))
fims = dias.groupby(dias.dt.to_period("M")).max()
L, ult = [], {}
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
for d in fims:
    x = P[(P["data"] == d) & (P["volume_medio_60 (R$)"] >= 1e6)]
    m6 = float(M.loc[:d].iloc[-1] / M.loc[:d - pd.DateOffset(months=6)].iloc[-1] - 1) if len(M.loc[:d - pd.DateOffset(months=6)]) else np.nan
    for r in x.itertuples():
        f = r.fundo
        if f in ult and d < ult[f] + pd.DateOffset(months=6):
            continue
        s = PF[f]
        a = s.loc[:d - pd.DateOffset(months=6)]
        if a.empty:
            continue
        q6 = r.fechamento / a["fechamento"].iloc[-1] - 1
        rend0, rend6 = r._10, a["rendimento_mensal (R$/cota)"].iloc[-1]
        if not (q6 <= -0.25 and q6 - m6 <= -0.20 and rend6 > 0 and rend0 >= 0.95 * rend6):
            continue
        y = s.loc[d + pd.Timedelta(days=1):]
        y = y[y["negociou (1/0)"] == 1].iloc[:126]
        if len(y) < 126:
            continue
        ult[f] = d
        p0 = float(y["abertura"].iloc[0])
        rr = RF.get(f)
        rend = float(rr[(rr["data_base"] >= y.index[0]) & (rr["data_base"] <= y.index[-1])]["valor (R$/cota)"].sum()) if rr is not None else 0
        corte = bool((y["rendimento_mensal (R$/cota)"] < 0.95 * rend0).any())
        L.append(dict(fundo=f, sinal=d, queda_6m=q6, mercado_6m=m6, pvp=r.preco_sobre_valor_patrimonial, rendimento_ano=r._11 / 100,
                      menor_126=float(y["fechamento"].min() / p0 - 1), preco_63=float(y["fechamento"].iloc[62] / p0 - 1),
                      preco_126=float(y["fechamento"].iloc[-1] / p0 - 1), resultado_126=float((y["fechamento"].iloc[-1] + rend) / p0 - 1),
                      cortou_depois=corte))
E_ = pd.DataFrame(L)
if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(f"eventos: {len(E_)} em {E_['fundo'].nunique()} fundos")
    c = ["menor_126", "preco_63", "preco_126", "resultado_126"]
    for nome, x in [("TODOS", E_), ("não cortou o rendimento depois", E_[~E_["cortou_depois"]]), ("cortou depois", E_[E_["cortou_depois"]])]:
        print(f"\n== {nome} ({len(x)})")
        print(pd.concat({"mediana": x[c].median(), "1 em 4 pior": x[c].quantile(.25), "1 em 4 melhor": x[c].quantile(.75)}, axis=1).to_string(float_format=lambda v: f"{v:+.3f}"))
        print(f"com lucro em 6 meses: {(x['resultado_126'] > 0).mean():.0%}")
    print(E_.sort_values("sinal")[["fundo", "sinal", "queda_6m", "pvp", "rendimento_ano", "menor_126", "preco_126", "resultado_126", "cortou_depois"]].to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    E_.to_csv("planilhas/queda_sem_corte.csv", index=False, date_format="%d/%m/%Y", float_format="%.4f", **OP)
