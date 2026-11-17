"""Sinais das conservadoras juntas, 2018 a 09/11/2026 (pedido do dono):
    Conservadora 1: gatilho 25%, mediana de negociação de 60 pregões de R$ 500 mil a R$ 1 milhão
    Conservadora 2: gatilho 20%, mediana de R$ 1 milhão ou mais

Motor de estudos/kairi_carteira_anos.py, com dinheiro à vontade (nenhum sinal fica sem caixa): mostra TODOS os
sinais e a saída de cada um. Repetição do mesmo fundo enquanto ele já está comprado não conta como sinal novo.
Grava planilhas/kairi_sinais_conservadoras.xlsx.

    PYTHONPATH=. python3 estudos/kairi_sinais_conservadoras.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference, Series
from openpyxl.styles import Alignment, Font, PatternFill

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="__main__")
sim = g["simular"]
G = sim.__globals__
G["CAP_SUB"] = 1e9                                     # dinheiro à vontade

# candidatos do gatilho de 25% (mesma construção de kairi_carteira_anos.py, linhas "CANDIDATOS")
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

CART = {"Conservadora 1 (25%; R$ 500 mil–1 mi)": (0.25, 500e3, 1e6),
        "Conservadora 2 (20%; > R$ 1 mi)": (0.20, 1e6, float("inf"))}
SIN, OPS = [], []
for nome, (X, lo, hi) in CART.items():
    r = sim(nome, X, lo, hi, G["JA"], G["NM"] - 1)
    s, o = r["sinais"].copy(), r["ops"].copy()
    s["carteira"], o["carteira"] = nome, nome
    SIN.append(s)
    OPS.append(o)
S = pd.concat(SIN, ignore_index=True)
O = pd.concat(OPS, ignore_index=True)
rep = S[S["resultado"] == "fundo já em carteira"].groupby("carteira").size()
S = S[S["resultado"] != "fundo já em carteira"].copy()
S["sinal"] = pd.to_datetime(S["sinal"])
S["ano"], S["mes"] = S["sinal"].dt.year, S["sinal"].dt.month
O["entrada"], O["saida"] = pd.to_datetime(O["entrada"]), pd.to_datetime(O["saida"])
O["resultado_pct"] = (O["valor_venda"].fillna(0) - O["valor_compra"] + O["rend_direito"].fillna(0)
                      - O["taxa_compra"] - O["taxa_venda"].fillna(0)) / O["valor_compra"]
F = O[O["status"] == "Fechada"].copy()

ANOS, MES = range(2018, 2027), ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
GRUPOS = {nome: (S[S["carteira"] == nome], F[F["carteira"] == nome], O[O["carteira"] == nome]) for nome in CART}
GRUPOS["As duas juntas"] = (S, F, O)

for nome, (s, f, o) in GRUPOS.items():
    print(f"{nome}: sinais {len(s)} (repetições não contadas: {int(rep.get(nome, rep.sum() if nome == 'As duas juntas' else 0))}); "
          f"compras {len(o)}; fechadas {len(f)}; abertas {len(o) - len(f)}; bloqueados {int(s['resultado'].str.startswith('bloq').sum())}; "
          f"fechadas com lucro {(f['resultado_pct'] > 0).mean():.0%}; resultado médio das fechadas {f['resultado_pct'].mean():.1%}; "
          f"dias medianos {(f['saida'] - f['entrada']).dt.days.median():.0f}")

# posições abertas ao mesmo tempo (as duas juntas)
dias = pd.date_range("2018-01-02", "2026-11-09")
fim = O["saida"].fillna(pd.Timestamp("2026-11-09"))
abertas = pd.Series([int(((O["entrada"] <= d) & (fim > d)).sum()) for d in dias], index=dias)
print(f"juntas: máximo de posições abertas ao mesmo tempo {abertas.max()} em {abertas.idxmax():%d/%m/%Y}; "
      f"dias sem nenhuma posição {100 * (abertas == 0).mean():.0f}%")

wb = Workbook()
NEG, CAB = Font(bold=True), PatternFill("solid", fgColor="DDEBF7")
CENTRO = Alignment(horizontal="center", vertical="top", wrap_text=True)


def cab(ws, linha, nomes, largura=9):
    for j, n in enumerate(nomes, 1):
        c = ws.cell(linha, j, n)
        c.font, c.fill, c.alignment = NEG, CAB, CENTRO
        ws.column_dimensions[c.column_letter].width = largura
    ws.column_dimensions["A"].width = 12


def grafico(ws, titulo, linhas_series, cat, onde, empilhado):
    ch = BarChart()
    ch.type, ch.title, ch.y_axis.title = "col", titulo, "quantidade"
    if empilhado:
        ch.grouping, ch.overlap = "stacked", 100
    for ref, nome in linhas_series:
        ch.series.append(Series(ref, title=nome))
    ch.set_categories(cat)
    ch.width, ch.height = 22, 9
    ch.y_axis.delete = ch.x_axis.delete = False
    ch.x_axis.tickLblPos = "low"
    ws.add_chart(ch, onde)


def aba_meses(nome, s):
    ws = wb.create_sheet(f"Por mês - {nome[:14]}")
    ws["A1"] = f"{nome}: sinais de 2018 a 09/11/2026 agrupados pelo mês (o ano não importa). * = bloqueado; C1/C2 = qual carteira"
    ws["A1"].font = Font(bold=True, size=12)
    cab(ws, 3, ["Mês", "Sinais", "Fundos (data do sinal)"])
    ws.column_dimensions["C"].width = 140
    for i, m in enumerate(range(1, 13), 4):
        x = s[s["mes"] == m].sort_values("sinal")
        ws.cell(i, 1, MES[m - 1]).alignment = CENTRO
        ws.cell(i, 2, len(x)).alignment = CENTRO
        txt = ", ".join(f"{r.fundo} {r.sinal:%d/%m/%Y}{'*' if r.resultado.startswith('bloq') else ''}"
                        f"{' (C1)' if r.carteira.startswith('Conservadora 1') and nome == 'As duas juntas' else ''}"
                        f"{' (C2)' if r.carteira.startswith('Conservadora 2') and nome == 'As duas juntas' else ''}"
                        for r in x.itertuples())
        ws.cell(i, 3, txt).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[i].height = 15 * max(1, -(-len(x) // 6))
    ws.cell(16, 1, "Total").font = NEG
    ws.cell(16, 2, len(s)).font = NEG
    grafico(ws, f"Sinais por mês, anos somados — {nome}", [(Reference(ws, min_col=2, min_row=4, max_row=15), "Sinais")],
            Reference(ws, min_col=1, min_row=4, max_row=15), "E18", False)


def aba_ano_mes(titulo, T, curto):
    ws = wb.create_sheet(curto)
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=12)
    cab(ws, 3, ["Ano"] + MES + ["Total"])
    for i, a in enumerate(ANOS, 4):
        ws.cell(i, 1, a).alignment = CENTRO
        for j, m in enumerate(range(1, 13), 2):
            v = int(T.loc[a, m])
            ws.cell(i, j, v if v else None).alignment = CENTRO
        c = ws.cell(i, 14, int(T.loc[a].sum()))
        c.font, c.alignment = NEG, CENTRO
    grafico(ws, titulo, [(Reference(ws, min_col=2, max_col=13, min_row=i), str(a)) for i, a in enumerate(ANOS, 4)],
            Reference(ws, min_col=2, max_col=13, min_row=3), "A15", True)


wb.remove(wb.active)
ws = wb.create_sheet("Resumo")
ws["A1"] = "Conservadoras juntas, 2018 a 09/11/2026, dinheiro à vontade (todos os sinais viram compra, salvo bloqueio)"
ws["A1"].font = Font(bold=True, size=12)
cab(ws, 3, ["Carteira", "Sinais", "Compras", "Fechadas", "Abertas", "Bloqueados", "Fechadas com lucro",
            "Resultado médio das fechadas", "Dias medianos"], 14)
ws.column_dimensions["A"].width = 38
for i, (nome, (s, f, o)) in enumerate(GRUPOS.items(), 4):
    vals = [nome, len(s), len(o), len(f), len(o) - len(f), int(s["resultado"].str.startswith("bloq").sum()),
            float((f["resultado_pct"] > 0).mean()), float(f["resultado_pct"].mean()),
            float((f["saida"] - f["entrada"]).dt.days.median())]
    for j, v in enumerate(vals, 1):
        c = ws.cell(i, j, v)
        c.number_format = "0%" if j == 7 else "0.0%" if j == 8 else "0"
ws.cell(8, 1, f"Máximo de posições abertas ao mesmo tempo (juntas): {abertas.max()} em {abertas.idxmax():%d/%m/%Y}; "
              f"dias sem nenhuma posição: {100 * (abertas == 0).mean():.0f}%.")
ws.cell(9, 1, "Resultado = venda − compra + rendimentos − taxas, antes do imposto do fundo, sobre o valor comprado.")

for nome, (s, f, o) in GRUPOS.items():
    aba_meses(nome, s)
for nome, (s, f, o) in GRUPOS.items():
    curto = "C1" if nome.startswith("Conservadora 1") else "C2" if nome.startswith("Conservadora 2") else "Juntas"
    ENT = pd.crosstab(s["ano"], s["mes"]).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
    SAI = pd.crosstab(f["saida"].dt.year, f["saida"].dt.month).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
    assert ENT.values.sum() == len(s) and SAI.values.sum() == len(f)
    aba_ano_mes(f"{nome}: entradas (sinais) por ano e mês", ENT, f"Entradas {curto}")
    aba_ano_mes(f"{nome}: saídas por ano e mês (fechadas)", SAI, f"Saídas {curto}")

ws = wb.create_sheet("Operações")
cols = ["carteira", "fundo", "sinal", "entrada", "preco_entrada", "saida", "preco_saida", "motivo", "status", "resultado_pct"]
cab(ws, 1, ["Carteira", "Fundo", "Sinal", "Entrada", "Preço de entrada (R$)", "Saída", "Preço de saída (R$)", "Motivo",
            "Situação", "Resultado (%)"], 14)
ws.column_dimensions["A"].width = 36
for i, x in enumerate(O.sort_values("entrada")[cols].itertuples(index=False), 2):
    for j, v in enumerate(x, 1):
        v = None if (isinstance(v, float) and pd.isna(v)) or v is pd.NaT else v
        c = ws.cell(i, j, v.to_pydatetime() if isinstance(v, pd.Timestamp) else v)
        if isinstance(v, pd.Timestamp):
            c.number_format = "dd/mm/yyyy"
        if j == 10:
            c.number_format = "0.0%"
wb.save("planilhas/kairi_sinais_conservadoras.xlsx")
print("gravado: planilhas/kairi_sinais_conservadoras.xlsx")
for nome, (s, f, o) in GRUPOS.items():
    ENT = pd.crosstab(s["ano"], s["mes"]).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
    SAI = pd.crosstab(f["saida"].dt.year, f["saida"].dt.month).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
    print(f"\n== {nome}: por mês (anos somados)")
    for m in range(1, 13):
        x = s[s["mes"] == m].sort_values("sinal")
        print(f"{MES[m - 1]} {len(x)}: " + ", ".join(f"{r.fundo} {r.sinal:%d/%m/%y}{'*' if r.resultado.startswith('bloq') else ''}"
                                                   f"{'(C1)' if r.carteira.startswith('Conservadora 1') else '(C2)'}" for r in x.itertuples()))
    ENT.columns = SAI.columns = MES
    print("entradas\n" + ENT.assign(total=ENT.sum(axis=1)).to_string())
    print("saídas\n" + SAI.assign(total=SAI.sum(axis=1)).to_string())
