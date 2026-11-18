"""Casos do passado parecidos tecnicamente com um fundo hoje (pedido do dono, 18/11/2026, para o TRXF11).

Evento: fechamento 30% ou mais abaixo da média de 200 pregões (média até a véspera) E IFR 14 <= 25 E negociação típica
(mediana de 60 pregões) >= R$ 1 mi/dia; fundos da base (preços ajustados); um evento por fundo a cada 3 meses.
Mede, a partir do fechamento do dia: variação do preço em 20, 60 e 126 pregões; com rendimentos (data-com) em 126;
menor preço em 60 pregões; e o mesmo separando os casos que cortaram o rendimento em até 6 meses.

    PYTHONPATH=. python3 estudos/analogos_tecnicos.py
"""
import numpy as np
import pandas as pd

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", **OP) for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P[P["negociou (1/0)"] == 1].sort_values(["fundo", "data"])
R = pd.read_csv("planilhas/rendimentos.csv", **OP)
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
RF = {f: x for f, x in R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"]).groupby("fundo")}
L = []
for f, x in P.groupby("fundo"):
    x = x.set_index("data")
    c = x["fechamento"]
    mm = c.rolling(200).mean().shift(1)
    d = c.diff()
    rs = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean() / (-d).clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    ifr = 100 - 100 / (1 + rs)
    med = x["volume_dia (R$)"].rolling(60).median()
    ok = (c / mm - 1 <= -0.30) & (ifr <= 25) & (med >= 1e6)
    ult = pd.Timestamp("1900-01-01")
    cv = c.to_numpy()
    for t in np.flatnonzero(ok.to_numpy()):
        dia = c.index[t]
        if dia < ult + pd.DateOffset(months=3) or t + 126 >= len(c):
            continue
        ult = dia
        r = RF.get(f)
        rend = float(r[(r["data_base"] > dia) & (r["data_base"] <= c.index[t + 126])]["valor (R$/cota)"].sum()) if r is not None else 0.0
        r0 = x["rendimento_mensal (R$/cota)"].iloc[t]
        corte = bool((x["rendimento_mensal (R$/cota)"].iloc[t:t + 126] < 0.95 * r0).any()) if r0 == r0 and r0 > 0 else False
        L.append(dict(fundo=f, dia=dia, dist_200=float(cv[t] / mm.iloc[t] - 1), ifr=float(ifr.iloc[t]),
                      v20=cv[t + 20] / cv[t] - 1, v60=cv[t + 60] / cv[t] - 1, v126=cv[t + 126] / cv[t] - 1,
                      total126=(cv[t + 126] + rend) / cv[t] - 1, menor60=cv[t:t + 61].min() / cv[t] - 1, cortou=corte))
E = pd.DataFrame(L)
if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(f"casos: {len(E)} em {E['fundo'].nunique()} fundos")
    c = ["v20", "v60", "v126", "total126", "menor60"]
    for nome, x in [("TODOS", E), ("não cortaram o rendimento em 6 meses", E[~E["cortou"]]), ("cortaram", E[E["cortou"]])]:
        print(f"\n== {nome} ({len(x)})")
        print(pd.concat({"mediana": x[c].median(), "1 em 4 pior": x[c].quantile(.25), "1 em 4 melhor": x[c].quantile(.75),
                         "subiu (%)": (x[c] > 0).mean()}, axis=1).to_string(float_format=lambda v: f"{v:+.3f}"))
    print(E.sort_values("dia")[["fundo", "dia", "dist_200", "ifr", "v20", "v60", "v126", "total126", "menor60", "cortou"]].to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    E.to_csv("planilhas/analogos_tecnicos_trxf11.csv", index=False, date_format="%d/%m/%Y", float_format="%.4f", **OP)
