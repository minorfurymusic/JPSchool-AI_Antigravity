"""Quantas oportunidades por ano, e de que qualidade, com a avaliação de saúde (Skill avaliar-fundo)? (pedido do dono)

1) Validação da avaliação: em cada grupo, operações aprovadas contra barradas (dinheiro à vontade, todo sinal vira
   operação; resultado = venda + rendimentos − compra, antes de taxas e imposto).
2) Configurações de gatilho e de negociação mínima (mediana de 60 pregões): oportunidades aprovadas por ano.
3) Carteira de R$ 10 mil dividida em 1, 2 e 5 partes (ordem de R$ 10.000, R$ 5.000 e R$ 2.000) com a avaliação:
   motor de estudos/kairi_carteira_anos.py, com os sinais barrados retirados antes.

    PYTHONPATH=. python3 estudos/kairi_oportunidades.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

from estudos.saude_fundo import saude

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="biblioteca")
sim = g["simular"]
G = sim.__globals__
CAND, FD, MD, TS, NM, JA = G["CAND"], G["FD"], G["MD"], G["TS"], G["NM"], G["JA"]


def candidatos(X):
    if X in CAND:
        return
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(G["sinais"](F, X)):
            md = int(F["mi"][s])
            if md >= JA and md + 1 < NM:
                d_ini = F["dates"][s - G["LAG_REND"]]
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VMED"][s]), vol_media=float(F["VOL"][s]),
                                        bloq=G["bloqueio"](F["nome"], MD[md]),
                                        cut=G["corte_rendimento"](F["nome"], MD[md], d_ini), d_ini=d_ini))
    CAND[X] = lst


def combinar(chave, partes):
    """Lista única de candidatos de várias faixas (X, lo, hi), para o motor tratar como um gatilho só."""
    for X, lo, hi in partes:
        candidatos(X)
    CAND[chave] = [[c for X, lo, hi in partes for c in CAND[X][mi] if lo <= c["vol"] < hi] for mi in range(NM)]


VERED = {}


def veredito(fundo, sinal):
    k = (fundo, pd.Timestamp(sinal))
    if k not in VERED:
        VERED[k] = saude(fundo, sinal)
    return VERED[k]


CONFIGS = {
    "Atual: C1 25% (R$ 0,5–1 mi) + C2 20% (> R$ 1 mi)": [(0.25, 500e3, 1e6), (0.20, 1e6, np.inf)],
    "C1 20% + C2 15%": [(0.20, 500e3, 1e6), (0.15, 1e6, np.inf)],
    "≥ R$ 500 mil, gatilho 15%": [(0.15, 500e3, np.inf)],
    "≥ R$ 500 mil, gatilho 12%": [(0.12, 500e3, np.inf)],
    "≥ R$ 500 mil, gatilho 10%": [(0.10, 500e3, np.inf)],
    "≥ R$ 250 mil, gatilho 15%": [(0.15, 250e3, np.inf)],
    "≥ R$ 250 mil, gatilho 12%": [(0.12, 250e3, np.inf)],
    "Todos os fundos, gatilho 15% (validação)": [(0.15, 0.0, np.inf)],
}
G["CAP_SUB"] = 1e9
LIN, ANOS, OPS = [], [], {}
for i, (nome, partes) in enumerate(CONFIGS.items()):
    chave = f"cfg{i}"
    combinar(chave, partes)
    o = sim(nome, chave, 0.0, np.inf, JA, NM - 1)["ops"]
    v = [veredito(r.fundo, r.sinal) for r in o.itertuples()]
    o["veredito"] = [x["veredito"] for x in v]
    o["motivo"] = ["; ".join(x.get("problemas", [])) for x in v]
    o["res"] = np.where(o["status"] == "Fechada",
                        (o["valor_venda"] - o["valor_compra"] + o["rend_direito"].fillna(0)) / o["valor_compra"], np.nan)
    o["ano"] = pd.to_datetime(o["sinal"]).dt.year
    OPS[nome] = o
    f = o[o["status"] == "Fechada"]
    ap, ba = f[f["veredito"] != "NÃO COMPRAR"], f[f["veredito"] == "NÃO COMPRAR"]
    apr_ano = o[o["veredito"] != "NÃO COMPRAR"].groupby("ano").size().reindex(range(2018, 2027), fill_value=0)
    LIN.append({"Configuração": nome, "Operações": len(o), "Aprovadas": int((o["veredito"] != "NÃO COMPRAR").sum()),
                "Barradas": int((o["veredito"] == "NÃO COMPRAR").sum()),
                "Aprovadas fechadas: resultado médio": ap["res"].mean(), "Aprovadas: com prejuízo": (ap["res"] < 0).mean(),
                "Aprovadas: pior": ap["res"].min(),
                "Barradas fechadas: resultado médio": ba["res"].mean() if len(ba) else np.nan,
                "Barradas: com prejuízo": (ba["res"] < 0).mean() if len(ba) else np.nan,
                "Anos com 3+ aprovadas (de 9)": int((apr_ano >= 3).sum()),
                "Meses diferentes com sinal aprovado": int(pd.to_datetime(o.loc[o["veredito"] != "NÃO COMPRAR", "sinal"]).dt.to_period("M").nunique())})
    ANOS.append(dict(Configuração=nome, **{str(a): int(n) for a, n in apr_ano.items()}))
    print(f"{nome}: {len(o)} operações", flush=True)

T, A = pd.DataFrame(LIN), pd.DataFrame(ANOS)
pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 30)
print("\n1-2) VALIDAÇÃO E OPORTUNIDADES\n" + T.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
print("\nOportunidades aprovadas por ano (ano do sinal)\n" + A.to_string(index=False))

# 3) carteira dividida, com os barrados retirados
G["CAP_SUB"] = 10000.0
CART = []
for nome in [n for n in CONFIGS if not n.startswith("Todos")]:
    chave = f"cfg{list(CONFIGS).index(nome)}"
    filtrada = f"{chave}_saude"
    CAND[filtrada] = [[c for c in CAND[chave][mi] if veredito(c["F"]["nome"], MD[c["md"]])["veredito"] != "NÃO COMPRAR"]
                      for mi in range(NM)]
    for ordem in (10000.0, 5000.0, 2000.0):
        r = sim(nome, filtrada, 0.0, np.inf, JA, NM - 1, ordem=ordem)
        d = r["dia"]
        pat = d["patrimonio"].to_numpy(float)
        o = r["ops"]
        f = o[o["status"] == "Fechada"]
        CART.append({"Configuração": nome, "Ordem (R$)": ordem, "Valor final (R$)": float(pat[-1]),
                     "Maior queda no caminho": float((pat / np.maximum.accumulate(pat) - 1).min()),
                     "Operações": len(o), "Fechadas com lucro": float((f["valor_venda"] + f["rend_direito"].fillna(0) > f["valor_compra"]).mean()) if len(f) else np.nan,
                     "Dinheiro aplicado em média": float(d["aplicado"].mean()),
                     "Sinais sem dinheiro": int((r["sinais"]["resultado"] == "sem dinheiro").sum()) if len(r["sinais"]) else 0})
        print(f"carteira {nome} ordem {ordem:.0f}: R$ {pat[-1]:,.2f}", flush=True)
C = pd.DataFrame(CART)
cdi = G["lote_liq"](JA, 10000.0, NM - 1, MD[NM - 1])[0]
print(f"\n3) CARTEIRA DE R$ 10 MIL (patrimônio final, antes do imposto ainda a vencer); 105% CDI líquido: R$ {cdi:,.2f}\n"
      + C.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
with pd.ExcelWriter("planilhas/kairi_oportunidades.xlsx") as w:
    T.to_excel(w, sheet_name="Validação e oportunidades", index=False)
    A.to_excel(w, sheet_name="Aprovadas por ano", index=False)
    C.to_excel(w, sheet_name="Carteira dividida", index=False)
    for i, (n, o) in enumerate(OPS.items(), 1):
        o.drop(columns=[c for c in ("e", "k", "mi_e", "mi_d", "mi_s", "rr") if c in o.columns]).assign(Configuração=n).to_excel(
            w, sheet_name=f"Operações {i}", index=False)
print("gravado: planilhas/kairi_oportunidades.xlsx")
