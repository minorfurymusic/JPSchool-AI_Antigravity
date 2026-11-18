"""Tipo 1 trade: resultado por período de entrada, cruzado com o quadro do país (planilhas/macro_mensal.csv),
e ranking por fundo dentro de Papel (pedido do dono, 18/11/2026).

Usa as operações de planilhas/descontado_classes.xlsx (contas corrigidas). Em cada operação, o quadro do país é o do
MÊS ANTERIOR à compra (o que se sabia no dia do sinal).
Grupos por "o que o mercado esperava" = Focus para o fim do ano seguinte − Selic do mês:
  espera queda forte (<= −1 ponto); espera estabilidade (−1 a +1); espera alta (>= +1).
Dólar: subiu mais de 10% em 6 meses / não. Dívida bruta: subiu mais de 2 pontos do PIB em 12 meses / não.

    PYTHONPATH=. python3 estudos/descontado_periodos.py
"""
import numpy as np
import pandas as pd

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
CASOS = [("Papel", "Alvo +10%"), ("Papel", "Média 21 cruza abaixo da 70"), ("Tijolo", "Alvo +10%"),
         ("Fundo de fundos", "Alvo +10%"), ("Todos", "Alvo +10%")]


def stats(x):
    return pd.Series({"Operações": len(x), "Com lucro": (x["resultado_liquido"] > 0).mean(),
                      "Bateram o CDI": (x["resultado_liquido"] > x["cdi"]).mean(), "Resultado médio": x["resultado_liquido"].mean(),
                      "Pregões médios": x["pregoes"].mean(),
                      "Ganho − CDI por mês (pontos)": (x["resultado_liquido"].sum() - x["cdi"].sum()) / x["pregoes"].sum() * 21 * 100})


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    O = pd.read_excel("planilhas/descontado_classes.xlsx", sheet_name="Operações")
    M = pd.read_csv("planilhas/macro_mensal.csv", **OP)
    M["mes"] = pd.PeriodIndex(pd.to_datetime("01/" + M["mes"], dayfirst=True), freq="M")
    M = M.set_index("mes")
    O["mes_info"] = (pd.to_datetime(O["entrada"]).dt.to_period("M") - 1)
    O = O.join(M, on="mes_info")
    esp = O["mercado espera (focus - selic, pontos)"]
    O["expectativa"] = np.select([esp <= -1, esp >= 1], ["espera queda forte da Selic", "espera alta da Selic"], "espera Selic estável")
    O["dolar"] = np.where(O["dolar: variação em 6 meses"] > 0.10, "dólar subiu mais de 10% em 6 meses", "dólar sem disparada")
    O["divida"] = np.where(O["divida bruta: variação em 12 meses (pontos)"] > 2, "dívida subiu mais de 2 pontos em 12 meses",
                           "dívida estável ou caindo")
    O["semestre"] = pd.to_datetime(O["entrada"]).dt.year.astype(str) + "-S" + np.where(pd.to_datetime(O["entrada"]).dt.month <= 6, "1", "2")
    SAI = {}
    for cl, v in CASOS:
        x = O[(O["classe"] == cl) & (O["venda"] == v)]
        nome = f"{cl} | {v}"
        S = x.groupby("semestre").apply(stats, include_groups=False)
        mac = x.groupby("semestre")[["selic (% ano)", "mercado espera (focus - selic, pontos)", "ipca 12 meses (%)", "dolar medio (R$)",
                                     "divida bruta (% PIB)", "deficit primario 12 meses (% PIB)"]].mean()
        S = S.join(mac)
        G = pd.concat([x.groupby(c).apply(stats, include_groups=False).assign(tema=c) for c in ("expectativa", "dolar", "divida")])
        SAI[nome] = (S, G)
        print(f"\n================ {nome}")
        print(S.to_string(float_format=lambda v: f"{v:,.2f}"))
        print(G.to_string(float_format=lambda v: f"{v:,.2f}"))
    # ranking por fundo dentro de Papel, alvo +10% e média 21x70
    F = []
    for v in ("Alvo +10%", "Média 21 cruza abaixo da 70"):
        x = O[(O["classe"] == "Papel") & (O["venda"] == v)]
        g = x.groupby("fundo").apply(stats, include_groups=False).assign(venda=v)
        F.append(g[g["Operações"] >= 2])
    F = pd.concat(F).reset_index().sort_values(["venda", "Ganho − CDI por mês (pontos)"], ascending=[True, False])
    print("\n================ PAPEL: por fundo (2 ou mais operações)")
    print(F.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    with pd.ExcelWriter("planilhas/descontado_periodos.xlsx") as w:
        for i, (nome, (S, G)) in enumerate(SAI.items(), 1):
            S.reset_index().to_excel(w, sheet_name=f"{i} por semestre", index=False)
            G.reset_index().rename(columns={"index": "grupo"}).to_excel(w, sheet_name=f"{i} por cenário", index=False)
        pd.DataFrame({"aba": [f"{i}" for i in range(1, len(SAI) + 1)], "caso": list(SAI)}).to_excel(w, sheet_name="Legenda", index=False)
        F.to_excel(w, sheet_name="Papel por fundo", index=False)
        O.to_excel(w, sheet_name="Operações com o país", index=False)
    print("gravado: planilhas/descontado_periodos.xlsx")
