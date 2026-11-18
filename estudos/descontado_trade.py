"""Tipo 1 como TRADE (pedido do dono, 18/11/2026): comprar, receber o rendimento e vender quando subir 10% ou 15%.
Não é carteira parada: mede operação por operação. Regras fixadas antes de rodar.

Entradas: em cada fim de mês (01/2018 a 10/2026), os 5 de maior nota da versão 2 (descontado_saudavel.candidatos_v2).
  Compra na abertura do pregão seguinte. Um fundo só entra de novo depois que a operação anterior nele terminar.
Saída: no fechamento do primeiro dia em que (fechamento + rendimentos recebidos desde a compra) ÷ preço de compra − 1
  >= alvo (10% ou 15%). Rendimento conta no dia do pagamento, com data-base a partir do dia da compra.
  Prazo máximo: 252 pregões (vende no fechamento do 252º). Sem stop. Taxa de 0,03% na compra e na venda.
  Operação sem 252 pregões até o fim da base e sem alvo = "em andamento".
Medidas: % que chegou ao alvo; pregões até o alvo; resultado das que não chegaram (no prazo); pior momento durante a
  operação (fechamento + rendimentos ÷ preço de compra − 1, o menor); 105% do CDI líquido no mesmo período (referência).
  Resultado antes do imposto de 20% sobre o ganho de cota (rendimento é isento).

    PYTHONPATH=. python3 estudos/descontado_trade.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saudavel as DS

RD, PF, RF = DS.RD, DS.RD.PF, DS.RD.RF
ALVOS = [0.10, 0.15]
PRAZO = 252
B3 = 0.0003


def operar(f, d_sinal, alvo):
    x = PF[f].loc[d_sinal + pd.Timedelta(days=1):]
    x = x[x["negociou (1/0)"] == 1]
    if x.empty:
        return None
    ent_dia, px0 = x.index[0], float(x["abertura"].iloc[0])
    if not px0 > 0:
        return None
    custo = px0 * (1 + B3)
    r = RF.get(f)
    pg = r[r["data_base"] >= ent_dia][["data_pagamento", "valor (R$/cota)"]] if r is not None else pd.DataFrame(columns=["data_pagamento", "valor (R$/cota)"])
    y = PF[f].loc[ent_dia:]
    y = y[y["negociou (1/0)"] == 1].iloc[:PRAZO]
    rend = np.array([float(pg.loc[pg["data_pagamento"] <= dd, "valor (R$/cota)"].sum()) for dd in y.index])
    tot = (y["fechamento"].to_numpy(float) * (1 - B3) + rend) / custo - 1
    hit = np.flatnonzero(tot >= alvo)
    if len(hit):
        k, sit = hit[0], "atingiu o alvo"
    elif len(y) >= PRAZO:
        k, sit = len(y) - 1, "prazo de 1 ano"
    else:
        k, sit = len(y) - 1, "em andamento"
    saida = y.index[k]
    return dict(fundo=f, sinal=d_sinal, entrada=ent_dia, preco_entrada=px0, saida=saida, preco_saida=float(y["fechamento"].iloc[k]),
                situacao=sit, pregoes=k + 1, rendimentos=float(rend[k]) / custo, resultado=float(tot[k]),
                pior_momento=float(tot[: k + 1].min()), cdi_mesmo_periodo=RD.cdi_liq(ent_dia, saida, 1.0) - 1, ano_entrada=ent_dia.year)


def estudo(alvo, sinais):
    ops, livre = [], {}
    for d, fundos in sinais:
        for f in fundos:
            if livre.get(f, pd.Timestamp.min) > d:
                continue
            o = operar(f, d, alvo)
            if o is None:
                continue
            o["alvo"] = alvo
            ops.append(o)
            livre[f] = o["saida"]
    return pd.DataFrame(ops)


def resumo(O):
    fe = O[O["situacao"] != "em andamento"]
    h = fe[fe["situacao"] == "atingiu o alvo"]
    n = fe[fe["situacao"] == "prazo de 1 ano"]
    return {"Operações encerradas": len(fe), "Em andamento": int((O["situacao"] == "em andamento").sum()),
            "Chegaram ao alvo": len(h) / len(fe) if len(fe) else np.nan,
            "Chegaram em até 60 pregões (~3 meses)": (h["pregoes"] <= 60).sum() / len(fe) if len(fe) else np.nan,
            "Chegaram em até 120 pregões (~6 meses)": (h["pregoes"] <= 120).sum() / len(fe) if len(fe) else np.nan,
            "Pregões até o alvo (mediana)": h["pregoes"].median(),
            "Parte do ganho que veio de rendimento (mediana, das que chegaram)": (h["rendimentos"] / h["resultado"]).median(),
            "Não chegaram: resultado no fim do prazo (média)": n["resultado"].mean(),
            "Não chegaram: pior resultado": n["resultado"].min(),
            "Não chegaram: com prejuízo": (n["resultado"] < 0).mean() if len(n) else np.nan,
            "Pior momento durante a operação (mediana)": fe["pior_momento"].median(),
            "Pior momento: 1 em cada 10 operações passou de": fe["pior_momento"].quantile(0.10),
            "Resultado médio de todas as encerradas": fe["resultado"].mean(),
            "105% do CDI no mesmo período (média, referência)": fe["cdi_mesmo_periodo"].mean(),
            "Pregões médios por operação": fe["pregoes"].mean()}


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    sinais = []
    for d in RD.FIM_MES:
        if d >= RD.DIAS[-1]:
            continue
        C = DS.candidatos_v2(d)
        sinais.append((d, list(C["fundo"].head(5)) if len(C) else []))
    print(f"meses com sinal: {sum(1 for _, f in sinais if f)} de {len(sinais)}", flush=True)
    RES, TODAS, ANO = [], [], []
    for a in ALVOS:
        O = estudo(a, sinais)
        TODAS.append(O)
        RES.append(dict({"Alvo": f"+{a:.0%}"}, **resumo(O)))
        fe = O[O["situacao"] != "em andamento"]
        g = fe.groupby("ano_entrada").agg(operacoes=("fundo", "size"),
                                          chegaram=("situacao", lambda s: (s == "atingiu o alvo").mean()),
                                          pregoes_medianos=("pregoes", "median"), resultado_medio=("resultado", "mean"),
                                          pior_momento_mediano=("pior_momento", "median"))
        ANO.append(g.assign(alvo=f"+{a:.0%}").reset_index())
    R = pd.DataFrame(RES).set_index("Alvo").T
    print(R.to_string(float_format=lambda v: f"{v:,.3f}"))
    A = pd.concat(ANO)
    print("\nPOR ANO DE ENTRADA")
    print(A.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    T = pd.concat(TODAS)
    with pd.ExcelWriter("planilhas/descontado_trade.xlsx") as w:
        R.reset_index().rename(columns={"index": "Medida"}).to_excel(w, sheet_name="Resumo", index=False)
        A.to_excel(w, sheet_name="Por ano de entrada", index=False)
        for a in ALVOS:
            T[T["alvo"] == a].to_excel(w, sheet_name=f"Operações alvo {a:.0%}", index=False)
    print("gravado: planilhas/descontado_trade.xlsx")
