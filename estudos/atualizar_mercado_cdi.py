"""Estende planilhas/mercado.csv e planilhas/cdi.csv até o último pregão de planilhas/precos_AAAA.csv (18/11/2026).

Mesmas contas da montagem original (estudos/planilhas.py e estudos/desconto.preparar):
  mercado: indice_mercado(t) = indice(t−1) × (1 + mediana da variação do dia dos fundos com volume_medio_60 >= R$ 100 mil e
           |variação| < 20% + mediana de (rendimento_mensal × 12 ÷ fechamento) desses fundos ÷ 252);
           fundos_negociados = soma de "negociou"; mediana de preço ÷ patrimônio com volume_medio_60 >= R$ 10 mil e razão de
           0,2 a 3; Selic meta (Banco Central, série 432); Selic líquida = Selic × 0,825.
  cdi:     CDI do dia (Banco Central, série 12, % ao dia); ao ano = ((1 + dia)^252 − 1); índice 100% e 105% acumulados.

    PYTHONPATH=. python3 estudos/atualizar_mercado_cdi.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")


def sgs(c, ini):
    r = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{c}/dados?formato=json&dataInicial={ini:%d/%m/%Y}", timeout=120)
    r.raise_for_status()
    d = pd.DataFrame(r.json())
    d["data"] = pd.to_datetime(d["data"], dayfirst=True)
    return d.set_index("data")["valor"].astype(float)


if __name__ == "__main__":
    a = pd.Timestamp.today().year
    P = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{x}.csv", **OP) for x in (a - 1, a)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    M = pd.read_csv(RAIZ / "planilhas/mercado.csv", **OP)
    M["data"] = pd.to_datetime(M["data"], dayfirst=True)
    C = pd.read_csv(RAIZ / "planilhas/cdi.csv", **OP)
    C["data"] = pd.to_datetime(C["data"], dayfirst=True)
    dias = sorted(d for d in P["data"].unique() if d > M["data"].max())
    selic = sgs(432, M["data"].max())
    F = P.pivot(index="data", columns="fundo", values="fechamento").sort_index().ffill()
    novas = []
    ind = float(M["indice_mercado"].iloc[-1])
    for d in dias:
        x = P[P["data"] == d].set_index("fundo")
        ant = F.index[F.index.get_loc(d) - 1]
        ret = F.loc[d] / F.loc[ant] - 1
        liq = x["volume_medio_60 (R$)"] >= 100_000
        r = ret.reindex(x.index)[liq]
        med = float(r[r.abs() < 0.2].median())
        dy = float((x.loc[liq, "rendimento_mensal (R$/cota)"] * 12 / x.loc[liq, "fechamento"]).median())
        ind *= 1 + (0 if np.isnan(med) else med) + (0.10 if np.isnan(dy) else dy) / 252
        ratio = x["fechamento"] / x["valor_patrimonial_cota"]
        ok = (x["volume_medio_60 (R$)"] >= 10_000) & ratio.between(0.2, 3)
        s = float(selic.loc[:d].iloc[-1])
        novas.append({"data": d, "selic_ano (%)": s, "selic_liquida_ano (%)": round(s * 0.825, 4), "indice_mercado": round(ind, 4),
                      "fundos_negociados": int(x["negociou (1/0)"].sum()), "mediana_preco_sobre_valor_patrimonial": round(float(ratio[ok].median()), 4)})
    N = pd.DataFrame(novas)
    N["data"] = N["data"].dt.strftime("%d/%m/%Y")
    N.to_csv(RAIZ / "planilhas/mercado.csv", mode="a", header=False, index=False, sep=";", decimal=",", encoding="utf-8")
    print(f"mercado.csv: +{len(N)} dias", N.to_string(index=False))
    cdi = sgs(12, C["data"].max() + pd.Timedelta(days=1))
    cdi = cdi[(cdi.index > C["data"].max()) & (cdi.index <= P["data"].max())]
    i100, i105 = float(C["indice_100_do_cdi"].iloc[-1]), float(C["indice_105_do_cdi"].iloc[-1])
    L = []
    for d, v in cdi.items():
        i100 *= 1 + v / 100
        i105 *= 1 + 1.05 * v / 100
        L.append({"data": d.strftime("%d/%m/%Y"), "cdi_ao_dia (%)": v, "cdi_ao_ano (%)": round(((1 + v / 100) ** 252 - 1) * 100, 2),
                  "indice_100_do_cdi": round(i100, 8), "indice_105_do_cdi": round(i105, 8)})
    pd.DataFrame(L).to_csv(RAIZ / "planilhas/cdi.csv", mode="a", header=False, index=False, sep=";", decimal=",", encoding="utf-8")
    print(f"cdi.csv: +{len(L)} dias", pd.DataFrame(L).to_string(index=False))
