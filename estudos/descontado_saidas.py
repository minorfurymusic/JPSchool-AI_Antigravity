"""Tipo 1 como trade: formas de comprar e de vender (pedido do dono, 18/11/2026). Regras fixadas antes de rodar.

Sinal: em cada fim de mês (01/2018 a 10/2026), os 5 de maior nota da versão 2 (descontado_saudavel.candidatos_v2).
Compra:
  A  abertura do pregão seguinte ao fim do mês.
  B  dentro do mês seguinte, primeiro fechamento <= banda inferior de Bollinger (20 pregões, 2 desvios); compra na
     abertura do pregão seguinte. Se não tocar até o fim do mês seguinte, não compra.
  Um fundo só entra de novo depois que a operação anterior nele terminar (vale para cada par compra × venda).
Venda (no fechamento; prazo máximo de 252 pregões; sem stop; taxa de 0,03% na compra e na venda):
  alvo10 / alvo15   (fechamento + rendimentos recebidos) ÷ custo − 1 >= 10% / 15%
  mm21x70 / mm21x90 média de 21 pregões cruza para baixo a de 70 / 90 (ontem >=, hoje <) depois da compra
  fib38 / fib50 / fib62  fechamento >= E + p × (T − E), E = preço de compra, T = maior fechamento dos 252 pregões
                    antes da compra (mesma conta do estudo do Kairi); se T <= E, a operação fica fora dessa venda
  bb_sup            fechamento >= banda superior de Bollinger (20 pregões, 2 desvios)
Resultado sempre com os rendimentos recebidos (pagamento até o dia da venda, data-base a partir da compra), antes do
imposto de 20% sobre ganho de cota. 105% do CDI líquido no mesmo período só como referência.

    PYTHONPATH=. python3 estudos/descontado_saidas.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saudavel as DS

RD, RF = DS.RD, DS.RD.RF
PRAZO, B3 = 252, 0.0003
VENDAS = ["alvo10", "alvo15", "mm21x70", "mm21x90", "fib38", "fib50", "fib62", "bb_sup"]
NOMES = {"alvo10": "Alvo +10%", "alvo15": "Alvo +15%", "mm21x70": "Média 21 cruza abaixo da 70", "mm21x90": "Média 21 cruza abaixo da 90",
         "fib38": "Fibonacci 38,2%", "fib50": "Fibonacci 50%", "fib62": "Fibonacci 61,8%", "bb_sup": "Banda superior de Bollinger"}

# séries diárias só com pregões em que o fundo negociou
SER = {}
for f, x in RD.P.groupby("fundo"):
    x = x[x["negociou (1/0)"] == 1].set_index("data").sort_index()
    c = x["fechamento"]
    m20, s20 = c.rolling(20).mean(), c.rolling(20).std()
    SER[f] = pd.DataFrame({"abertura": x["abertura"], "fechamento": c, "mm21": c.rolling(21).mean(), "mm70": c.rolling(70).mean(),
                           "mm90": c.rolling(90).mean(), "bb_inf": m20 - 2 * s20, "bb_sup": m20 + 2 * s20,
                           "topo252": c.rolling(252, min_periods=60).max().shift(1)})


def dia_compra(f, d, modo, fim_mes_seguinte):
    s = SER.get(f)
    if s is None:
        return None
    y = s.loc[d + pd.Timedelta(days=1):]
    if y.empty:
        return None
    if modo == "A":
        return y.index[0]
    z = y.loc[:fim_mes_seguinte]
    t = z.index[(z["fechamento"] <= z["bb_inf"]).to_numpy()]
    if len(t) == 0:
        return None
    k = y.index.get_loc(t[0])
    return y.index[k + 1] if k + 1 < len(y) else None


def operar(f, ent, venda):
    s = SER[f]
    px0 = float(s.loc[ent, "abertura"])
    if not px0 > 0:
        return None
    custo = px0 * (1 + B3)
    y = s.loc[ent:].iloc[:PRAZO]
    r = RF.get(f)
    pg = r[r["data_base"] >= ent] if r is not None else None
    rend = np.array([float(pg.loc[pg["data_pagamento"] <= dd, "valor (R$/cota)"].sum()) if pg is not None else 0.0 for dd in y.index])
    c = y["fechamento"].to_numpy(float)
    tot = (c * (1 - B3) + rend) / custo - 1
    if venda in ("alvo10", "alvo15"):
        ok = tot >= (0.10 if venda == "alvo10" else 0.15)
    elif venda in ("mm21x70", "mm21x90"):
        lg = y["mm70" if venda == "mm21x70" else "mm90"].to_numpy(float)
        cu = y["mm21"].to_numpy(float)
        ok = np.zeros(len(y), bool)
        ok[1:] = (cu[:-1] >= lg[:-1]) & (cu[1:] < lg[1:])
    elif venda.startswith("fib"):
        T = float(s.loc[ent, "topo252"])
        if not T > px0:
            return "sem_topo"
        alvo = px0 + {"fib38": 0.382, "fib50": 0.5, "fib62": 0.618}[venda] * (T - px0)
        ok = c >= alvo
    else:
        ok = c >= y["bb_sup"].to_numpy(float)
    hit = np.flatnonzero(ok)
    if len(hit):
        k, sit = hit[0], "vendeu pela regra"
    elif len(y) >= PRAZO:
        k, sit = len(y) - 1, "prazo de 1 ano"
    else:
        k, sit = len(y) - 1, "em andamento"
    saida = y.index[k]
    return dict(fundo=f, entrada=ent, preco_entrada=px0, saida=saida, preco_saida=float(c[k]), situacao=sit, pregoes=k + 1,
                rendimentos=float(rend[k]) / custo, resultado=float(tot[k]), pior_momento=float(tot[: k + 1].min()),
                cdi_mesmo_periodo=RD.cdi_liq(ent, saida, 1.0) - 1)


def resumo(O, sem_topo):
    fe = O[O["situacao"] != "em andamento"]
    pz = fe[fe["situacao"] == "prazo de 1 ano"]
    return {"Operações encerradas": len(fe), "Em andamento": int((O["situacao"] == "em andamento").sum()),
            "Fora (Fibonacci sem topo acima da compra)": sem_topo,
            "Com lucro": (fe["resultado"] > 0).mean(), "Resultado médio": fe["resultado"].mean(),
            "Resultado mediano": fe["resultado"].median(), "Pior operação": fe["resultado"].min(),
            "Pregões médios": fe["pregoes"].mean(),
            "Ganho médio por mês aplicado (resultado ÷ pregões × 21)": (fe["resultado"] / fe["pregoes"] * 21).mean(),
            "Venderam pela regra": (fe["situacao"] == "vendeu pela regra").mean(),
            "Venderam pela regra: resultado médio": fe.loc[fe["situacao"] == "vendeu pela regra", "resultado"].mean(),
            "Saíram por prazo: resultado médio": pz["resultado"].mean(),
            "Pior momento (mediana)": fe["pior_momento"].median(), "Pior momento: 1 em cada 10 passou de": fe["pior_momento"].quantile(0.10),
            "105% do CDI no mesmo período (média, referência)": fe["cdi_mesmo_periodo"].mean(),
            "CDI por mês aplicado (referência)": (fe["cdi_mesmo_periodo"] / fe["pregoes"] * 21).mean()}


if __name__ == "__main__":
    pd.set_option("display.width", 300)
    pd.set_option("display.max_columns", 40)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    sinais = []
    for i, d in enumerate(fms):
        C = DS.candidatos_v2(d)
        prox = fms[i + 1] if i + 1 < len(fms) else RD.DIAS[-1]
        sinais.append((d, prox, list(C["fundo"].head(5)) if len(C) else []))
    print(f"meses com sinal: {sum(1 for *_, f in sinais if f)} de {len(sinais)}", flush=True)
    RES, OPS = [], []
    for modo in ("A", "B"):
        for v in VENDAS:
            ops, livre, fora = [], {}, 0
            for d, prox, fundos in sinais:
                for f in fundos:
                    if livre.get(f, pd.Timestamp.min) > d:
                        continue
                    ent = dia_compra(f, d, modo, prox)
                    if ent is None:
                        continue
                    o = operar(f, ent, v)
                    if o == "sem_topo":
                        fora += 1
                        continue
                    if o is None:
                        continue
                    ops.append(dict(o, compra=modo, venda=NOMES[v]))
                    livre[f] = o["saida"]
            O = pd.DataFrame(ops)
            OPS.append(O)
            RES.append(dict({"Compra": "A abertura seguinte" if modo == "A" else "B banda inferior de Bollinger", "Venda": NOMES[v]},
                            **resumo(O, fora)))
            print(f"{modo} {v}: {len(O)} operações", flush=True)
    R = pd.DataFrame(RES)
    cols = ["Compra", "Venda", "Operações encerradas", "Com lucro", "Resultado médio", "Resultado mediano", "Pregões médios",
            "Ganho médio por mês aplicado (resultado ÷ pregões × 21)", "Venderam pela regra", "Saíram por prazo: resultado médio",
            "Pior momento (mediana)", "Pior momento: 1 em cada 10 passou de", "CDI por mês aplicado (referência)"]
    print(R[cols].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    with pd.ExcelWriter("planilhas/descontado_saidas.xlsx") as w:
        R.to_excel(w, sheet_name="Resumo", index=False)
        pd.concat(OPS).to_excel(w, sheet_name="Operações", index=False)
    print("gravado: planilhas/descontado_saidas.xlsx")
