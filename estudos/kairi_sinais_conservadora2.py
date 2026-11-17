"""Sinais da Conservadora 2 (gatilho 20%, mediana de negociação de 60 pregões >= R$ 1 milhão), 2018 a 09/11/2026.

Usa o motor de estudos/kairi_carteira_anos.py com dinheiro à vontade (nenhum sinal fica sem caixa), para ver
TODOS os sinais e a saída de cada um. Ordem de R$ 1.000 (o tamanho não muda datas de entrada e saída).
Grava planilhas/kairi_sinais_conservadora2.xlsx.

    PYTHONPATH=. python3 estudos/kairi_sinais_conservadora2.py
"""
import contextlib
import io
import runpy

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="__main__")
sim = g["simular"]
G = sim.__globals__
G["CAP_SUB"] = 1e9                                     # dinheiro à vontade
X, lo, hi = G["SUBS"]["Conservadora 2"]
r = sim("Conservadora 2", X, lo, hi, G["JA"], G["NM"] - 1)
S, O = r["sinais"].copy(), r["ops"].copy()

# um sinal por queda: repetição do mesmo fundo enquanto ele já está comprado não conta de novo
rep = int((S["resultado"] == "fundo já em carteira").sum())
S = S[S["resultado"] != "fundo já em carteira"].copy()
S["sinal"] = pd.to_datetime(S["sinal"])
S["ano"], S["mes"] = S["sinal"].dt.year, S["sinal"].dt.month
O["entrada"], O["saida"] = pd.to_datetime(O["entrada"]), pd.to_datetime(O["saida"])
F = O[O["status"] == "Fechada"].copy()
ANOS, MES = range(2018, 2027), ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

ENT = pd.crosstab(S["ano"], S["mes"]).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
SAI = pd.crosstab(F["saida"].dt.year, F["saida"].dt.month).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
assert ENT.values.sum() == len(S) and SAI.values.sum() == len(F)
print(f"sinais: {len(S)} (+{rep} repetições do mesmo fundo já comprado, não contadas); compras {len(O)}; "
      f"fechadas {len(F)}; abertas {len(O) - len(F)}; bloqueados {int(S['resultado'].str.startswith('bloq').sum())}")

wb = Workbook()
NEG, CAB = Font(bold=True), PatternFill("solid", fgColor="DDEBF7")


def cab(ws, linha, nomes, largura=9):
    for j, n in enumerate(nomes, 1):
        c = ws.cell(linha, j, n)
        c.font, c.fill, c.alignment = NEG, CAB, Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[c.column_letter].width = largura
    ws.column_dimensions["A"].width = 12


def barras(ws, titulo, ref, cat, onde, empilhado=False):
    ch = BarChart()
    ch.type, ch.title, ch.y_axis.title = "col", titulo, "quantidade"
    if empilhado:
        ch.grouping, ch.overlap = "stacked", 100
    ch.add_data(ref, titles_from_data=True)
    ch.set_categories(cat)
    ch.width, ch.height = 22, 9
    ch.y_axis.delete = ch.x_axis.delete = False
    ch.x_axis.tickLblPos = "low"
    ws.add_chart(ch, onde)


# aba 1: meses, anos juntos
ws = wb.active
ws.title = "Sinais por mês"
ws["A1"] = "Conservadora 2: sinais de 2018 a 09/11/2026 agrupados pelo mês (o ano não importa). * = bloqueado (fundo ia sair da bolsa)"
ws["A1"].font = Font(bold=True, size=12)
cab(ws, 3, ["Mês", "Sinais", "Fundos (data do sinal)"])
ws.column_dimensions["C"].width = 140
for i, m in enumerate(range(1, 13), 4):
    s = S[S["mes"] == m].sort_values("sinal")
    ws.cell(i, 1, MES[m - 1])
    ws.cell(i, 2, len(s))
    ws.cell(i, 3, ", ".join(f"{x.fundo} {x.sinal:%d/%m/%Y}{'*' if x.resultado.startswith('bloq') else ''}"
                            for x in s.itertuples())).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[i].height = 15 * max(1, -(-len(s) // 6))
ws.cell(16, 1, "Total").font = NEG
ws.cell(16, 2, len(S)).font = NEG
barras(ws, "Sinais por mês (2018 a 2026 somados)", Reference(ws, min_col=2, min_row=3, max_row=15),
       Reference(ws, min_col=1, min_row=4, max_row=15), "E18")


def ano_mes(ws, titulo, T, onde):
    ws["A1"] = titulo
    ws["A1"].font = Font(bold=True, size=12)
    cab(ws, 3, ["Ano"] + MES + ["Total"])
    for i, a in enumerate(ANOS, 4):
        ws.cell(i, 1, a)
        for j, m in enumerate(range(1, 13), 2):
            v = int(T.loc[a, m])
            ws.cell(i, j, v if v else None)
        ws.cell(i, 14, int(T.loc[a].sum())).font = NEG
    # gráfico: meses no eixo, um bloco por ano (empilhado)
    barras(ws, titulo, Reference(ws, min_col=1, max_col=13, min_row=4, max_row=4 + len(ANOS) - 1),
           Reference(ws, min_col=2, max_col=13, min_row=3), onde, empilhado=True)


ws = wb.create_sheet("Entradas por ano e mês")
ano_mes(ws, "Conservadora 2: sinais de entrada por ano e mês (quantidade)", ENT, "A15")
ws = wb.create_sheet("Saídas por ano e mês")
ano_mes(ws, "Conservadora 2: saídas por ano e mês (quantidade, operações fechadas)", SAI, "A15")

# a série de cada ano vira uma linha do gráfico: precisa ser por linha
for nome in ("Entradas por ano e mês", "Saídas por ano e mês"):
    ch = wb[nome]._charts[0]
    ch.series.clear()
    ws = wb[nome]
    from openpyxl.chart import Series
    for i, a in enumerate(ANOS, 4):
        se = Series(Reference(ws, min_col=2, max_col=13, min_row=i), title=str(a))
        ch.series.append(se)
    ch.set_categories(Reference(ws, min_col=2, max_col=13, min_row=3))
    for linha in ws.iter_rows(min_row=3, max_row=3 + len(ANOS), max_col=14):
        for c in linha:
            c.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

ws = wb.create_sheet("Operações")
cols = ["fundo", "sinal", "entrada", "preco_entrada", "saida", "preco_saida", "motivo", "status"]
cab(ws, 1, ["Fundo", "Sinal", "Entrada", "Preço de entrada (R$)", "Saída", "Preço de saída (R$)", "Motivo", "Situação"], 14)
for i, x in enumerate(O[cols].itertuples(index=False), 2):
    for j, v in enumerate(x, 1):
        c = ws.cell(i, j, None if (isinstance(v, float) and pd.isna(v)) or v is pd.NaT else
                    (v.to_pydatetime() if isinstance(v, pd.Timestamp) else v))
        if isinstance(v, pd.Timestamp):
            c.number_format = "dd/mm/yyyy"
wb.save("planilhas/kairi_sinais_conservadora2.xlsx")
print("gravado: planilhas/kairi_sinais_conservadora2.xlsx")
