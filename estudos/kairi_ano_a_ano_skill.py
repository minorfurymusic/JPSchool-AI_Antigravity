"""Carteira de R$ 10 mil, um fundo de cada vez, com a avaliação de saúde da Skill "avaliar-fundo" antes de cada compra,
troca quando o fundo atual tem lucro >= 15% e está a no máximo 5% da média, e segunda entrada. 02/01/2018 a 09/11/2026,
sem zerar a cada ano. Tabelas por ano: operações (entrada, saída, dias, lucro, rendimentos) e, no fim de cada ano,
a comparação com 105% do CDI no ano inteiro e o que rendeu o dinheiro que ficou parado.

    PYTHONPATH=. python3 estudos/kairi_ano_a_ano_skill.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_um_fundo.py", run_name="biblioteca")
rodar, G = g["rodar"], g["G"]
CIDX, MD, TS, JA, FIM, lote_liq = G["CIDX"], G["MD"], G["TS"], G["JA"], g["FIM"], G["lote_liq"]
IDX = pd.Series(CIDX[JA:], index=pd.to_datetime(TS[JA:]))
CAP = 10000.0

RUNS = {
    "C2 15% + avaliação de saúde": rodar(0.15, "troca", 0.15, 0.05, filtro=True),
    "C2 20% + avaliação de saúde": rodar(0.20, "troca", 0.15, 0.05, filtro=True),
    "C2 15% sem avaliação": rodar(0.15, "troca", 0.15, 0.05, filtro=False),
    "C2 20% sem avaliação": rodar(0.20, "troca", 0.15, 0.05, filtro=False),
}


def por_ano(r):
    s, cx, cp = r["serie"], r["caixa"], r["com_pos"]
    o = r["ops"].copy()
    o["entrada"], o["saida"] = pd.to_datetime(o["entrada"]), pd.to_datetime(o["saida"])
    # rendimento bruto do dinheiro parado no dia = caixa do dia anterior x variação do índice de 105% do CDI
    ganho_cx = (cx.shift(1) * (IDX / IDX.shift(1) - 1)).fillna(0.0)
    linhas = []
    for a in sorted(set(s.index.year)):
        sa = s[s.index.year == a]
        ini_dia = s[s.index.year < a].index[-1] if a > 2018 else sa.index[0]
        ini = s.loc[ini_dia] if a > 2018 else CAP
        fim = sa.iloc[-1]
        i0, i1 = int(np.searchsorted(MD, np.datetime64(ini_dia, "D"))), int(np.searchsorted(MD, np.datetime64(sa.index[-1], "D")))
        cdi_ano = lote_liq(i0, ini, i1, MD[i1])[0] - ini
        dias = len(sa)
        parado = int((~cp[cp.index.year == a]).sum())
        fe = o[o["saida"].dt.year == a]
        linhas.append({"Ano": a, "Patrimônio no início (R$)": ini, "Patrimônio no fim (R$)": fim,
                       "Ganho no ano (R$)": fim - ini, "Retorno no ano": fim / ini - 1,
                       "105% CDI no ano inteiro, líquido (R$)": cdi_ano, "105% CDI no ano (%)": cdi_ano / ini,
                       "Diferença para o CDI (R$)": fim - ini - cdi_ano,
                       "Operações encerradas no ano": len(fe), "Lucro das encerradas (R$)": fe["resultado"].sum(),
                       "Rendimentos dessas operações (R$)": fe["rendimentos"].sum(),
                       "Pregões no ano": dias, "Pregões sem fundo (dinheiro parado)": parado,
                       "Rendimento do dinheiro parado, bruto (R$)": float(ganho_cx[ganho_cx.index.year == a].sum())})
    return pd.DataFrame(linhas), o


pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 30)
fmt = lambda v: f"{v:,.2f}"
SAI = {}
for nome, r in RUNS.items():
    A, o = por_ano(r)
    ab = r["aberto"]
    print(f"\n{'=' * 110}\n{nome}: R$ 10.000 -> R$ {r['final']:,.2f} (líquido do imposto devido) | trocas {r['n_troca']} | "
          f"segundas entradas {r['n_seg']} | compras barradas pela avaliação {len(r['barrados'])}")
    if len(r["barrados"]):
        print(r["barrados"].to_string(index=False))
    cols = ["fundo", "como_entrou", "sinal", "entrada", "preco_entrada", "saida", "preco_saida", "motivo", "dias",
            "valor_entrada", "rendimentos", "resultado", "resultado_pct"]
    print(o[cols].to_string(index=False, float_format=fmt))
    if ab:
        print(f"em aberto em 09/11/2026: {ab['fundo']} comprado em {pd.Timestamp(ab['entrada']):%d/%m/%Y} a R$ {ab['preco_entrada']:.2f}, "
              f"valor hoje R$ {ab['valor']:,.2f}")
    print(A.to_string(index=False, float_format=fmt))
    SAI[nome] = (A, o, r)

with pd.ExcelWriter("planilhas/kairi_ano_a_ano_skill.xlsx") as w:
    pd.DataFrame([{"Simulação": n, "Valor final (R$)": r["final"], "Retorno": r["final"] / CAP - 1,
                   "105% CDI no período, líquido (R$)": lote_liq(JA, CAP, FIM, MD[FIM])[0],
                   "Maior queda no caminho": float((r["serie"] / r["serie"].cummax() - 1).min()), "Trocas": r["n_troca"],
                   "Segundas entradas": r["n_seg"], "Compras barradas": len(r["barrados"])} for n, (A, o, r) in SAI.items()]
                 ).to_excel(w, sheet_name="Resumo", index=False)
    for i, (n, (A, o, r)) in enumerate(SAI.items(), 1):
        A.assign(Simulação=n).to_excel(w, sheet_name=f"Por ano {i}", index=False)
        o.assign(Simulação=n).to_excel(w, sheet_name=f"Operações {i}", index=False)
        if len(r["barrados"]):
            r["barrados"].assign(Simulação=n).to_excel(w, sheet_name=f"Barrados {i}", index=False)
print("gravado: planilhas/kairi_ano_a_ano_skill.xlsx")
