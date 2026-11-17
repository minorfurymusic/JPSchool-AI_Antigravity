"""O rendimento instável antes da compra piora o resultado? (ideia do dono, 2026-11-17)

Para cada operação (planilhas/kairi_fundamentos_entrada.xlsx, gerada por estudos/kairi_fundamentos_entrada.py), olha os
avisos de rendimento com data-base nos 12 meses até o dia do sinal (planilhas/rendimentos_pagamentos.csv) e mede:
  oscilacao  = desvio padrão ÷ média dos valores mensais (quanto o valor muda de um mês para o outro)
  cortes     = meses em que o valor caiu mais de 5% contra o mês anterior
  pior_queda = maior queda de um mês para o seguinte
  tendencia  = média dos últimos 3 meses ÷ média dos 3 primeiros − 1
Só usa dados até o dia do sinal. Testa limites nos três grupos de operações e mostra os 11 fundos da carteira de um fundo só.

    PYTHONPATH=. python3 estudos/kairi_constancia_rendimento.py
"""
import numpy as np
import pandas as pd

R = pd.read_csv("planilhas/rendimentos_pagamentos.csv", sep=";", decimal=",", encoding="utf-8-sig")
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
RF = {f: x.sort_values("data_base") for f, x in R.groupby("fundo")}


def medidas(f, d):
    d = pd.Timestamp(d)
    x = RF.get(f)
    if x is None:
        return dict(meses=0)
    x = x[(x["data_base"] <= d) & (x["data_base"] > d - pd.Timedelta(days=365))]
    x = x.groupby(x["data_base"].dt.to_period("M"))["valor (R$/cota)"].sum()   # um valor por mês
    v = x.to_numpy(float)
    if len(v) < 6:
        return dict(meses=len(v))
    var = v[1:] / v[:-1] - 1
    return dict(meses=len(v), oscilacao=float(v.std() / v.mean()), cortes=int((var < -0.05).sum()),
                pior_queda=float(var.min()), tendencia=float(v[-3:].mean() / v[:3].mean() - 1))


X = pd.ExcelFile("planilhas/kairi_fundamentos_entrada.xlsx")
pd.set_option("display.width", 250)
TODAS = []
for sh in X.sheet_names:
    d = pd.read_excel(X, sheet_name=sh)
    m = pd.DataFrame([medidas(r.fundo, r.sinal) for r in d.itertuples()], index=d.index)
    d = pd.concat([d, m], axis=1)
    d["planilha"] = sh
    TODAS.append(d)
    if sh.startswith("Um fundo"):
        print(f"\n== {sh}")
        print(d[["fundo", "sinal", "res", "meses", "oscilacao", "cortes", "pior_queda", "tendencia", "rend_12m"]]
              .to_string(index=False, float_format=lambda v: f"{v:.3f}"))
        continue
    d = d[d["meses"] >= 6]
    print(f"\n== {sh}: {len(d)} operações fechadas com 6+ meses de rendimento")
    for nome, cond in [("oscilação > 0,15", d["oscilacao"] > 0.15), ("oscilação > 0,20", d["oscilacao"] > 0.20),
                       ("3 ou mais cortes", d["cortes"] >= 3), ("4 ou mais cortes", d["cortes"] >= 4),
                       ("pior queda < −20%", d["pior_queda"] < -0.20), ("tendência < −10%", d["tendencia"] < -0.10),
                       ("rendimento 12m < −10%", d["rend_12m"] < -0.10)]:
        a, b = d[cond], d[~cond]
        print(f"  tira {nome:24s}: {len(a):3d} ops, média {a['res'].mean():+.3f}, prejuízo {(a['res'] < 0).mean():.0%} "
              f"| ficam {len(b):3d}, média {b['res'].mean():+.3f}, prejuízo {(b['res'] < 0).mean():.0%}")
pd.concat(TODAS).to_csv("planilhas/tecnico/kairi_constancia_rendimento.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
