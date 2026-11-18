"""Avisos de rendimento suspeitos em planilhas/rendimentos_pagamentos.csv (achado em 18/11/2026: VCRI11 com R$ 36,85 por
cota numa cota de R$ 6, sem queda do preço).

Regra (fixada antes de usar): aviso com valor > 10% do fechamento da data-base (ou do último pregão antes dela) é
"grande". Grande E o fechamento do pregão seguinte à data-base NÃO caiu pelo menos metade do valor do aviso = SUSPEITO
(provável erro de extração ou valor em outra unidade). Grande com queda compatível = provável distribuição real
(venda de imóvel, amortização). Sem nenhum preço depois da data-base = categoria à parte (fundo saiu da bolsa?),
não é tratado como suspeito. Saída: planilhas/tecnico/rendimentos_suspeitos.csv; função `suspeitos()`.

    PYTHONPATH=. python3 estudos/rendimentos_suspeitos.py
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
SAIDA = RAIZ / "planilhas" / "tecnico" / "rendimentos_suspeitos.csv"


def montar():
    R = pd.read_csv(RAIZ / "planilhas/rendimentos_pagamentos.csv", **OP)
    R["db"] = pd.to_datetime(R["data_base"], dayfirst=True)
    P = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{a}.csv", **OP, usecols=["data", "fundo", "fechamento", "negociou (1/0)"])
                   for a in range(2017, 2027)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    P = P[P["negociou (1/0)"] == 1].sort_values("data")
    A = pd.merge_asof(R.sort_values("db"), P.rename(columns={"data": "db", "fechamento": "preco_data_base"})[["db", "fundo", "preco_data_base"]],
                      on="db", by="fundo", direction="backward")
    B = pd.merge_asof(A.assign(db1=A["db"] + pd.Timedelta(days=1)).sort_values("db1"),
                      P.rename(columns={"data": "db1", "fechamento": "preco_dia_seguinte"})[["db1", "fundo", "preco_dia_seguinte"]],
                      on="db1", by="fundo", direction="forward")
    B["valor_sobre_preco"] = B["valor (R$/cota)"] / B["preco_data_base"]
    B["queda_no_dia_seguinte"] = B["preco_data_base"] - B["preco_dia_seguinte"]
    g = B[B["valor_sobre_preco"] > 0.10].copy()
    g["situacao"] = "SUSPEITO (sem queda compatível)"
    g.loc[g["queda_no_dia_seguinte"] >= 0.5 * g["valor (R$/cota)"], "situacao"] = "grande, com queda compatível (provável real)"
    g.loc[g["preco_dia_seguinte"].isna(), "situacao"] = "sem preço depois (fundo saiu da bolsa? conferir)"
    g = g[["fundo", "data_base", "data_pagamento", "valor (R$/cota)", "preco_data_base", "preco_dia_seguinte", "valor_sobre_preco",
           "situacao"]].sort_values(["situacao", "valor_sobre_preco"], ascending=[False, False])
    g.to_csv(SAIDA, index=False, float_format="%.4f", **OP)
    return g


@lru_cache(maxsize=1)
def suspeitos():
    """Conjunto de (fundo, data-base) suspeitos."""
    g = pd.read_csv(SAIDA, **OP)
    g = g[g["situacao"].str.startswith("SUSPEITO")]
    return set(zip(g["fundo"], pd.to_datetime(g["data_base"], dayfirst=True)))


if __name__ == "__main__":
    g = montar()
    print(f"gravado: {SAIDA.relative_to(RAIZ)} ({len(g)} avisos grandes)")
    print(g["situacao"].value_counts().to_string())
    print(g[g["situacao"].str.startswith("SUSPEITO")].head(15).to_string(index=False))
