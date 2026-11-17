"""Os fundos comprados eram bons ou ruins? Indicadores conhecidos no dia do sinal (sem olhar o futuro) contra o resultado.

Indicadores (de planilhas/precos_*.csv; valor patrimonial e patrimônio já com o atraso de 75 dias):
  preço sobre valor patrimonial; rendimento do ano sobre o preço (12 x mensal) e a distância para o CDI do dia;
  variação do valor patrimonial por cota em 12 meses; variação do rendimento mensal em 12 meses;
  patrimônio; tipo do fundo (planilhas/fundos.csv).
Depois do sinal (só para explicar, não para regra): o rendimento foi cortado durante a operação? o valor patrimonial caiu?
Operações: dinheiro à vontade, regras da versão 3; grupos Conservadoras (C1 25% + C2 20%), Conservadoras (C1 25% + C2 15%)
e Todos os fundos a 15% (mais casos). Grava planilhas/kairi_fundamentos_entrada.xlsx.

    PYTHONPATH=. python3 estudos/kairi_fundamentos_entrada.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_um_fundo.py", run_name="kairi_um_fundo")
G = g["G"]
sim = G["simular"]
G["CAP_SUB"] = 1e9
UM = g["RUNS"]

GRUPOS = {"Conservadoras (C1 25% + C2 20%)": [(0.25, 500e3, 1e6), (0.20, 1e6, np.inf)],
          "Conservadoras (C1 25% + C2 15%)": [(0.25, 500e3, 1e6), (0.15, 1e6, np.inf)],
          "Todos os fundos, gatilho 15%": [(0.15, 0.0, np.inf)]}
OPS = {n: pd.concat([sim(n, X, lo, hi, G["JA"], G["NM"] - 1)["ops"] for X, lo, hi in p], ignore_index=True) for n, p in GRUPOS.items()}

P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", sep=";", decimal=",", encoding="utf-8-sig") for a in range(2017, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P.sort_values(["fundo", "data"])
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
TIPO = pd.read_csv("planilhas/fundos.csv", sep=";", encoding="utf-8-sig").set_index("fundo")["tipo"].to_dict()
MK = pd.read_csv("planilhas/mercado.csv", sep=";", decimal=",", encoding="utf-8-sig")
MK["data"] = pd.to_datetime(MK["data"], dayfirst=True)
CDI = pd.read_csv("planilhas/cdi.csv", sep=";", decimal=",", encoding="utf-8-sig")
CDI["data"] = pd.to_datetime(CDI["data"], dayfirst=True)
CDI = CDI.set_index("data")["cdi_ao_ano (%)"]


def no_dia(f, d, col, atras=0):
    x = PF[f].loc[:pd.Timestamp(d)]
    if len(x) <= atras:
        return np.nan
    return float(x[col].iloc[-1 - atras])


def indicadores(f, sinal, entrada, saida):
    d = pd.Timestamp(sinal)
    pvp = no_dia(f, d, "preco_sobre_valor_patrimonial")
    dy = no_dia(f, d, "rendimento_ano_sobre_preco (%)") / 100
    cdi = float(CDI.loc[:d].iloc[-1]) / 100
    vp, vp12 = no_dia(f, d, "valor_patrimonial_cota"), no_dia(f, d, "valor_patrimonial_cota", 252)
    r, r12 = no_dia(f, d, "rendimento_mensal (R$/cota)"), no_dia(f, d, "rendimento_mensal (R$/cota)", 252)
    pat = no_dia(f, d, "patrimonio (R$)")
    # depois (explicação): rendimento e valor patrimonial na saída contra a entrada
    fim = pd.Timestamp(saida) if pd.notna(saida) else pd.Timestamp("2026-11-09")
    r_fim = no_dia(f, fim, "rendimento_mensal (R$/cota)")
    vp_fim = no_dia(f, fim, "valor_patrimonial_cota")
    return dict(tipo=TIPO.get(f, "?"), pvp=pvp, dy=dy, dy_menos_cdi=dy - cdi, vp_12m=vp / vp12 - 1 if vp12 else np.nan,
                rend_12m=r / r12 - 1 if r12 else np.nan, patrimonio_mi=pat / 1e6,
                depois_rend=r_fim / r - 1 if r else np.nan, depois_vp=vp_fim / vp - 1 if vp else np.nan)


def montar(o):
    o = o.copy()
    o["res"] = np.where(o["status"] == "Fechada",
                        (o["valor_venda"].fillna(0) - o["valor_compra"] + o["rend_direito"].fillna(0)) / o["valor_compra"], np.nan)
    ind = pd.DataFrame([indicadores(r.fundo, r.sinal, r.entrada, r.saida) for r in o.itertuples()], index=o.index)
    return pd.concat([o[["fundo", "sinal", "entrada", "saida", "motivo", "status", "res"]], ind], axis=1)


COLS = {"pvp": "Preço / valor patrimonial", "dy": "Rendimento do ano sobre o preço", "dy_menos_cdi": "Rendimento menos CDI",
        "vp_12m": "Valor patrimonial em 12 meses", "rend_12m": "Rendimento mensal em 12 meses", "patrimonio_mi": "Patrimônio (R$ mi)",
        "depois_rend": "DEPOIS: rendimento na saída contra a entrada", "depois_vp": "DEPOIS: valor patrimonial na saída contra a entrada"}
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
SAIDA = {}
for nome, o in OPS.items():
    D = montar(o)
    F = D[D["status"] == "Fechada"].copy()
    F["grupo"] = np.where(F["res"] < 0, "prejuízo", np.where(F["res"] < 0.10, "lucro até 10%", "lucro de 10% ou mais"))
    t = F.groupby("grupo")[list(COLS)].median().rename(columns=COLS).T
    t["casos"] = ""
    cont = F["grupo"].value_counts()
    print(f"\n== {nome}: {len(F)} fechadas ({cont.to_dict()}); medianas dos indicadores")
    print(t.drop(columns="casos").to_string(float_format=lambda v: f"{v:.3f}"))
    print("tipo do fundo: % com prejuízo por tipo")
    print(F.groupby("tipo").agg(casos=("res", "size"), prejuizo=("res", lambda s: (s < 0).mean()), media=("res", "mean")).round(3).to_string())
    SAIDA[nome] = F

# fundos da carteira de um fundo só
for nome, r in UM.items():
    if not nome.endswith("segurar + segunda entrada"):
        continue
    o = r["ops"].rename(columns={"resultado_pct": "res"})
    rows = []
    for x in o.itertuples():
        rows.append(dict(fundo=x.fundo, sinal=x.sinal, entrada=x.entrada, saida=x.saida, res=x.res, **indicadores(x.fundo, x.sinal, x.entrada, x.saida)))
    if r["aberto"]:
        a = r["aberto"]
        rows.append(dict(fundo=a["fundo"], sinal=a["entrada"], entrada=a["entrada"], saida=pd.NaT,
                         res=a["valor"] / (a["preco_entrada"] * (a["valor"] / a["valor"])) and np.nan,
                         **indicadores(a["fundo"], a["entrada"], a["entrada"], pd.NaT)))
    U = pd.DataFrame(rows)
    print(f"\n== Carteira de um fundo só: {nome}")
    print(U.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    SAIDA["Um fundo: " + nome.split(" |")[0]] = U

with pd.ExcelWriter("planilhas/kairi_fundamentos_entrada.xlsx") as w:
    for nome, d in SAIDA.items():
        d.to_excel(w, sheet_name=nome[:31].replace(":", ""), index=False)
print("gravado: planilhas/kairi_fundamentos_entrada.xlsx")
