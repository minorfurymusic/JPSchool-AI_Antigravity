"""Duas perguntas do dono (2026-11-17), com as regras da versão 3 (venda no fechamento acima da média de 200 pregões,
prazo de 252 pregões, rendimento mantido, bloqueios) e dinheiro à vontade (todo sinal vira operação):

A) Depois que a operação já subiu X% (5, 10, 14, 15, 16, 18%), qual a chance de chegar a +20% antes da saída?
   Quanto ainda rende até a saída e quanto pode devolver? Vender ao tocar X% contra esperar a média.
B) Segunda entrada: entrar no mesmo fundo k pregões depois da primeira entrada (10, 20, 30, 45, 60), só se a operação
   ainda não terminou e a cota ainda estiver Z% ou mais abaixo da média de 200 (um "segundo sinal").
   Quanto rende, com que risco, contra a entrada no primeiro dia.

Três grupos: Conservadoras (C1 25% com mediana de R$ 500 mil a 1 mi + C2 20% com mediana acima de R$ 1 mi),
Todos os fundos a 20% e Todos a 15% (sem faixa de negociação; os dois últimos dão mais casos).
Resultado de cada operação = (preço + rendimentos com data-base desde a entrada) ÷ preço de entrada − 1,
antes de taxas e imposto. Grava planilhas/kairi_alvo_segunda_entrada.xlsx.

    PYTHONPATH=. python3 estudos/kairi_alvo_segunda_entrada.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="__main__")
sim = g["simular"]
G = sim.__globals__
G["CAP_SUB"] = 1e9

X25 = 0.25
lst = [[] for _ in range(G["NM"])]
for F in G["FD"].values():
    for s in np.flatnonzero(G["sinais"](F, X25)):
        md = int(F["mi"][s])
        if md >= G["JA"] and md + 1 < G["NM"]:
            bl = G["bloqueio"](F["nome"], G["MD"][md])
            d_ini = F["dates"][s - G["LAG_REND"]]
            cut = G["corte_rendimento"](F["nome"], G["MD"][md], d_ini)
            lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VMED"][s]), vol_media=float(F["VOL"][s]),
                                    bloq=bl, cut=cut, d_ini=d_ini))
G["CAND"][X25] = lst

GRUPOS = {
    "Conservadoras (C1 25% + C2 20%)": [(0.25, 500e3, 1e6), (0.20, 1e6, np.inf)],
    "Todos os fundos, gatilho 20%": [(0.20, 0.0, np.inf)],
    "Todos os fundos, gatilho 15%": [(0.15, 0.0, np.inf)],
}
OPS = {}
for nome, partes in GRUPOS.items():
    o = pd.concat([sim(nome, X, lo, hi, G["JA"], G["NM"] - 1)["ops"] for X, lo, hi in partes], ignore_index=True)
    OPS[nome] = o
    print(f"{nome}: {len(o)} operações, {int((o['status'] == 'Fechada').sum())} fechadas")

# preços e média de 200 (até o dia anterior, como na regra de saída)
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", sep=";", decimal=",", encoding="utf-8-sig",
                           usecols=["data", "fundo", "abertura", "fechamento"]) for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P.sort_values(["fundo", "data"])
P["mm"] = P.groupby("fundo")["fechamento"].transform(lambda s: s.rolling(200, min_periods=200).mean().shift(1))
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
R = pd.read_csv("planilhas/rendimentos_pagamentos.csv", sep=";", decimal=",", encoding="utf-8-sig")
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
RF = {f: x.sort_values("data_base") for f, x in R.groupby("fundo")}


def caminho(o):
    """Série diária de (preço de fechamento + rendimentos acumulados desde a entrada) da entrada até a saída."""
    x = PF[o.fundo].loc[pd.Timestamp(o.entrada):pd.Timestamp(o.saida)].copy()
    r = RF.get(o.fundo)
    if r is not None:
        r = r[r["data_base"] >= pd.Timestamp(o.entrada)]
        x["rend"] = [float(r.loc[r["data_base"] <= d, "valor (R$/cota)"].sum()) for d in x.index]
    else:
        x["rend"] = 0.0
    return x


TAB_A, TAB_B, LIN = [], [], []
LIMIARES = [0.05, 0.10, 0.14, 0.15, 0.16, 0.18]
ESPERAS = [10, 20, 30, 45, 60]
FOLGAS = [0.0, 0.10, 0.15]
for nome, o in OPS.items():
    f = o[o["status"] == "Fechada"].copy()
    paths = []
    for op in f.itertuples():
        x = caminho(op)
        if len(x) < 2:
            continue
        ret = (x["fechamento"] + x["rend"]) / op.preco_entrada - 1
        ret.iloc[-1] = (op.preco_saida + x["rend"].iloc[-1]) / op.preco_entrada - 1   # saída pelo preço da regra
        paths.append((op, x, ret))
    # ---------------------------------------------------------------- A
    for L in LIMIARES:
        cas = []
        for op, x, ret in paths:
            antes = ret.iloc[:-1]                         # dias antes do dia de saída
            hit = np.flatnonzero(antes.values >= L)
            if len(hit) == 0:
                continue
            i = hit[0]
            final = ret.iloc[-1]
            depois = ret.iloc[i:]
            cas.append(dict(final=final, no_toque=ret.iloc[i], resto=(1 + final) / (1 + ret.iloc[i]) - 1,
                            chegou20=bool((depois.values >= 0.20).any()), dias_resto=(x.index[-1] - x.index[i]).days,
                            pior_depois=float(depois.min()), devolveu=final < L))
        c = pd.DataFrame(cas)
        n_tot = len(paths)
        TAB_A.append({"Grupo": nome, "Já subiu": f"{L:.0%}", "Operações fechadas": n_tot,
                      "Chegaram a esse ponto": len(c),
                      "Dessas, chegaram a +20%": float(c["chegou20"].mean()) if len(c) else np.nan,
                      "Terminaram abaixo desse ponto (devolveram)": float(c["devolveu"].mean()) if len(c) else np.nan,
                      "Resultado final médio": float(c["final"].mean()) if len(c) else np.nan,
                      "Vender ao tocar (médio)": float(c["no_toque"].mean()) if len(c) else np.nan,
                      "Ganho de esperar a média, médio (pontos)": float((c["final"] - c["no_toque"]).mean()) if len(c) else np.nan,
                      "Esperar foi melhor em": float((c["final"] > c["no_toque"]).mean()) if len(c) else np.nan,
                      "Pior resultado final": float(c["final"].min()) if len(c) else np.nan,
                      "Dias até a saída (mediana)": float(c["dias_resto"].median()) if len(c) else np.nan})
    # ---------------------------------------------------------------- B
    base = pd.DataFrame([dict(final=ret.iloc[-1], queda=float(ret.min()), dias=(x.index[-1] - x.index[0]).days)
                         for op, x, ret in paths])
    TAB_B.append({"Grupo": nome, "Entrada": "1º dia (regra atual)", "Exigência": "—", "Operações possíveis": len(base),
                  "Resultado médio": base["final"].mean(), "Mediana": base["final"].median(),
                  "Com lucro": (base["final"] > 0).mean(), "Pior": base["final"].min(),
                  "Queda média depois da entrada": base["queda"].mean(), "Pior queda depois da entrada": base["queda"].min(),
                  "Dias até a saída (mediana)": base["dias"].median()})
    for k in ESPERAS:
        for z in FOLGAS:
            cas = []
            for op, x, ret in paths:
                if k >= len(x) - 1:
                    continue                              # a operação já terminou: não há segunda entrada
                d = x.index[k]
                mm = x["mm"].iloc[k]
                ab = x["abertura"].iloc[k]
                if not np.isfinite(mm) or x["fechamento"].iloc[k - 1] / mm - 1 > -z:
                    continue                              # cota (no fechamento anterior) não está Z% abaixo da média
                rend_ate = x["rend"].iloc[k - 1]
                r2 = (x["fechamento"].iloc[k:] + x["rend"].iloc[k:] - rend_ate) / ab - 1
                r2.iloc[-1] = (op.preco_saida + x["rend"].iloc[-1] - rend_ate) / ab - 1
                cas.append(dict(final=r2.iloc[-1], queda=float(r2.min()), dias=(x.index[-1] - d).days))
            c = pd.DataFrame(cas)
            TAB_B.append({"Grupo": nome, "Entrada": f"{k} pregões depois",
                          "Exigência": "nenhuma" if z == 0 else f"cota ainda {z:.0%} ou mais abaixo da média",
                          "Operações possíveis": len(c),
                          "Resultado médio": c["final"].mean() if len(c) else np.nan,
                          "Mediana": c["final"].median() if len(c) else np.nan,
                          "Com lucro": (c["final"] > 0).mean() if len(c) else np.nan,
                          "Pior": c["final"].min() if len(c) else np.nan,
                          "Queda média depois da entrada": c["queda"].mean() if len(c) else np.nan,
                          "Pior queda depois da entrada": c["queda"].min() if len(c) else np.nan,
                          "Dias até a saída (mediana)": c["dias"].median() if len(c) else np.nan})

A = pd.DataFrame(TAB_A)
B = pd.DataFrame(TAB_B)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)
fmt = lambda df: df.to_string(index=False, float_format=lambda v: f"{v:.3f}")
print("\nA) DEPOIS DE SUBIR X%\n" + fmt(A))
print("\nB) SEGUNDA ENTRADA\n" + fmt(B))
with pd.ExcelWriter("planilhas/kairi_alvo_segunda_entrada.xlsx") as w:
    A.to_excel(w, sheet_name="A - depois de subir X%", index=False)
    B.to_excel(w, sheet_name="B - segunda entrada", index=False)
print("gravado: planilhas/kairi_alvo_segunda_entrada.xlsx")
