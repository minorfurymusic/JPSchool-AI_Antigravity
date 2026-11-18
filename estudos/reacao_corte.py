"""Reação da cota e do volume a cortes de rendimento (pedido do dono, 18/11/2026, para estimar o TRXF11).

Evento: aviso de rendimento (planilhas/rendimentos.csv, data_conhecido = dia do anúncio) de 5% a 15% abaixo do aviso
anterior, depois de pelo menos 3 avisos seguidos sem queda de mais de 2%; fundo com volume_medio_60 >= R$ 1 mi/dia no
dia anterior; um evento por fundo a cada 6 meses. Avisos suspeitos (estudos/rendimentos_suspeitos.py) ignorados.
Medidas (fechamento do pregão anterior ao anúncio = base; "contra o mercado" = menos a variação do índice de mercado):
  variação em 1, 5, 20, 60 e 126 pregões; menor fechamento em 60 pregões e em que pregão; volume médio dos 5 e 20
  pregões depois ÷ volume médio dos 60 antes; se o rendimento voltou a subir (>= +3% sobre o valor cortado) em até 6 meses.
Grupos: preço ÷ patrimônio na véspera < 0,75 (muito descontado, como o TRXF11) ou >= 0,75.

    PYTHONPATH=. python3 estudos/reacao_corte.py
"""
import numpy as np
import pandas as pd

from estudos.rendimentos_suspeitos import suspeitos

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", **OP) for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P[P["negociou (1/0)"] == 1].sort_values(["fundo", "data"])
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
M = pd.read_csv("planilhas/mercado.csv", **OP)
M["data"] = pd.to_datetime(M["data"], dayfirst=True)
M = M.set_index("data")["indice_mercado"]
R = pd.read_csv("planilhas/rendimentos.csv", **OP)
R["data_conhecido"] = pd.to_datetime(R["data_conhecido"], dayfirst=True)
R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"]).sort_values(["fundo", "data_base"])
S = suspeitos()
R = R[[(f, d) not in S for f, d in zip(R["fundo"], R["data_base"])]]

L = []
for f, r in R.groupby("fundo"):
    if f not in PF:
        continue
    v, dc = r["valor (R$/cota)"].to_numpy(float), r["data_conhecido"].to_numpy()
    ult = pd.Timestamp("1900-01-01")
    for i in range(4, len(v)):
        if not (0.85 <= v[i] / v[i - 1] <= 0.95):
            continue
        prev = v[i - 4:i]
        if (prev[1:] / prev[:-1] < 0.98).any():
            continue
        d = pd.Timestamp(dc[i])
        if d < ult + pd.DateOffset(months=6):
            continue
        s = PF[f]
        antes = s.loc[:d - pd.Timedelta(days=1)]
        depois = s.loc[d:]
        if len(antes) < 60 or len(depois) < 61 or antes["volume_medio_60 (R$)"].iloc[-1] < 1e6:
            continue
        ult = d
        b, db = float(antes["fechamento"].iloc[-1]), antes.index[-1]
        c = depois["fechamento"].to_numpy(float)
        m0 = float(M.loc[:db].iloc[-1])

        def var(k):
            if len(c) <= k:
                return np.nan, np.nan
            mk = float(M.loc[:depois.index[k]].iloc[-1]) / m0 - 1
            return c[k] / b - 1, c[k] / b - 1 - mk
        L.append({"fundo": f, "anuncio": d, "corte": v[i] / v[i - 1] - 1, "pvp_vespera": float(antes["preco_sobre_valor_patrimonial"].iloc[-1]),
                  **{f"var_{k}": var(k - 1)[0] for k in (1, 5, 20, 60, 126)},
                  **{f"contra_mercado_{k}": var(k - 1)[1] for k in (5, 20, 60, 126)},
                  "menor_60": float(c[:60].min() / b - 1), "pregao_do_menor": int(c[:60].argmin()) + 1,
                  "volume_5d_sobre_antes": float(depois["volume_dia (R$)"].iloc[:5].mean() / antes["volume_dia (R$)"].iloc[-60:].mean()),
                  "volume_20d_sobre_antes": float(depois["volume_dia (R$)"].iloc[:20].mean() / antes["volume_dia (R$)"].iloc[-60:].mean()),
                  "rendimento_voltou_a_subir_6m": bool(((r["data_conhecido"] > d) & (r["data_conhecido"] <= d + pd.DateOffset(months=6))
                                                        & (r["valor (R$/cota)"] >= v[i] * 1.03)).any())})
E = pd.DataFrame(L)
E["grupo"] = np.where(E["pvp_vespera"] < 0.75, "muito descontado (< 0,75)", "0,75 ou mais")

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    cols = ["var_1", "var_5", "var_20", "var_60", "var_126", "contra_mercado_20", "contra_mercado_126", "menor_60", "pregao_do_menor",
            "volume_5d_sobre_antes", "volume_20d_sobre_antes"]
    print(f"eventos: {len(E)} em {E['fundo'].nunique()} fundos; corte médio {E['corte'].mean():.1%}")
    def tab(x):
        return pd.concat({"mediana": x[cols].median(), "1 em 4 pior": x[cols].quantile(0.25), "1 em 4 melhor": x[cols].quantile(0.75)}, axis=1)
    for nome, x in [("TODOS", E), *E.groupby("grupo"), ("rendimento voltou a subir em 6 meses", E[E["rendimento_voltou_a_subir_6m"]]),
                    ("muito descontado E rendimento voltou a subir", E[(E["pvp_vespera"] < 0.75) & E["rendimento_voltou_a_subir_6m"]])]:
        print(f"\n===== {nome} ({len(x)} eventos)")
        print(tab(x).to_string(float_format=lambda v: f"{v:+.3f}"))
    with pd.ExcelWriter("planilhas/reacao_corte.xlsx") as w:
        E.to_excel(w, sheet_name="Eventos", index=False)
        tab(E).to_excel(w, sheet_name="Todos")
        for g, x in E.groupby("grupo"):
            tab(x).to_excel(w, sheet_name=g[:31])
        tab(E[E["rendimento_voltou_a_subir_6m"]]).to_excel(w, sheet_name="Rendimento voltou a subir")
    print("gravado: planilhas/reacao_corte.xlsx")
