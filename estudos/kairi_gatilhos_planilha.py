"""Planilha com gráficos: comparação dos gatilhos do Kairi (10%, 15%, 20%, 30%).

Pedido do dono (2026-11-17). Lê só as planilhas geradas por estudos/auditoria_bloco2.py
e grava planilhas/kairi_gatilhos.xlsx. Nenhuma conta nova: só organiza e desenha.

    PYTHONPATH=. python3 estudos/kairi_gatilhos_planilha.py
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

PL = Path("planilhas")
SAIDA = PL / "kairi_gatilhos.xlsx"
PER = {"Escolha 2018–2022": "2018 a 2022", "Conferência 2023–2026": "2023 a 2026", "Total": "Total"}


def ler(nome):
    return pd.read_csv(PL / f"auditoria_bloco2_{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")


G, FU, FA, PE = ler("gatilhos"), ler("funil"), ler("faixas"), ler("perdidas")

wb = Workbook()
NEG = Font(bold=True)
CAB = PatternFill("solid", fgColor="DDEBF7")


def escreve(ws, linha, cab, linhas, formatos):
    for j, c in enumerate(cab, 1):
        cel = ws.cell(linha, j, c)
        cel.font, cel.fill = NEG, CAB
        cel.alignment = Alignment(wrap_text=True, vertical="top")
    for i, row in enumerate(linhas, linha + 1):
        for j, v in enumerate(row, 1):
            cel = ws.cell(i, j, v)
            if formatos[j - 1]:
                cel.number_format = formatos[j - 1]
    for j in range(1, len(cab) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 16 if j > 1 else 14
    ws.row_dimensions[linha].height = 48
    return linha + 1, linha + len(linhas)


def barras(ws, titulo, eixo_y, ref_dados, ref_cat, onde, fmt=None, largura=17, altura=8.5):
    ch = BarChart()
    ch.type = "col"
    ch.title = titulo
    ch.y_axis.title = eixo_y
    ch.add_data(ref_dados, titles_from_data=True)
    ch.set_categories(ref_cat)
    ch.width, ch.height = largura, altura
    ch.y_axis.delete = False
    ch.x_axis.delete = False
    if fmt:
        ch.y_axis.number_format = fmt
    ch.x_axis.tickLblPos = "low"          # rótulos embaixo, fora das barras negativas
    ws.add_chart(ch, onde)


PCT, RS, INT = "0.0%", '"R$" #,##0', "0"

# ------------------------------------------------------------------ 1. Resumo
ws = wb.active
ws.title = "Resumo"
ws["A1"] = "Kairi: comparação dos gatilhos (cota 10%, 15%, 20% ou 30% abaixo da média de 200 pregões)"
ws["A1"].font = Font(bold=True, size=13)
cab = ["Gatilho", "Período", "Ordens", "Ordens com lucro (%)", "Resultado médio por ordem (%)",
       "Ganho acima do CDI (R$)", "Ganho acima do CDI por real aplicado (%)", "Pior ordem (%)",
       "Dias médios por ordem", "Dinheiro necessário no pico (R$)"]
linhas = []
for _, r in G.iterrows():
    linhas.append([r.gatilho, PER[r.periodo], int(r.ordens), r.pos, r.res_pct, round(r.exc, 0),
                   r.exc_pp, r.pior, round(r.dias, 0), (round(r.pico, 0) if pd.notna(r.pico) else None)])
linhas.sort(key=lambda x: (list(PER.values()).index(x[1]), x[0]))
i0, i1 = escreve(ws, 3, cab, linhas, [None, None, INT, PCT, PCT, RS, PCT, PCT, INT, RS])

# tabela auxiliar para gráficos: uma linha por gatilho, colunas por período
ws2 = wb.create_sheet("Dados dos gráficos")
ws2["A1"] = "Tabela de apoio dos gráficos (mesmos números da aba Resumo)."
blocos = [("Ordens com lucro (%)", "pos", PCT), ("Ganho acima do CDI (R$)", "exc", RS),
          ("Ordens", "ordens", INT), ("Pior ordem (%)", "pior", PCT)]
lin = 3
refs = {}
for titulo, col, fmt in blocos:
    ws2.cell(lin, 1, titulo).font = NEG
    ws2.cell(lin + 1, 1, "Gatilho").font = NEG
    for j, p in enumerate(PER.values(), 2):
        ws2.cell(lin + 1, j, p).font = NEG
    for k, gat in enumerate(["10%", "15%", "20%", "30%"]):
        ws2.cell(lin + 2 + k, 1, gat)
        for j, (pk, pv) in enumerate(PER.items(), 2):
            v = G[(G.gatilho == gat) & (G.periodo == pk)][col].iloc[0]
            c = ws2.cell(lin + 2 + k, j, float(v))
            c.number_format = fmt
    refs[col] = (Reference(ws2, min_col=2, max_col=4, min_row=lin + 1, max_row=lin + 5),
                 Reference(ws2, min_col=1, min_row=lin + 2, max_row=lin + 5), fmt)
    lin += 8
ws2.column_dimensions["A"].width = 26

barras(ws, "Ordens com lucro, por gatilho", "% das ordens", *refs["pos"][:2], "A20", PCT)
barras(ws, "Ganho acima do 105% do CDI, por gatilho", "R$", *refs["exc"][:2], "G20", RS)
barras(ws, "Quantas ordens cada gatilho faz", "ordens", *refs["ordens"][:2], "A38", INT)
barras(ws, "Pior ordem de cada gatilho", "% da ordem", *refs["pior"][:2], "G38", PCT)

leit = i1 + 2
for k, t in enumerate([
    "Leitura prática:",
    "• O gatilho de 15% é o que mais ganha em reais no total (R$ 68,5 mil acima do CDI). O de 20% ganha um pouco menos (R$ 60,7 mil), mas com bem menos dinheiro (R$ 151 mil no pico contra R$ 263 mil).",
    "• Quanto mais fundo o gatilho, maior a parte de ordens com lucro (78% → 86% → 86% → 92%) e menor a pior ordem; mas o número de ordens cai muito (582 → 341 → 175 → 37).",
    "• De 2023 a 2026 isso não se repetiu: o 30% teve só 9 ordens e 67% com lucro.",
]):
    ws.cell(leit + k, 1, t).font = NEG if k == 0 else Font()

# ------------------------------------------------------------------ 2. Funil
ws = wb.create_sheet("Funil")
ws["A1"] = "Funil: das ordens abertas a 10% e a 15% abaixo da média, quantas caíram até 15%, 20% e 30%"
ws["A1"].font = Font(bold=True, size=13)
f10 = FU[(FU.gatilho == "10%") & (FU.periodo == "Total")].iloc[0]
f15 = FU[(FU.gatilho == "15%") & (FU.periodo == "Total")].iloc[0]
linhas = [["Chegou a 10%", int(f10.sinais_com_ordem), None],
          ["Chegou a 15%", int(f10.chegou_15), int(f15.sinais_com_ordem)],
          ["Chegou a 20%", int(f10.chegou_20), int(f15.chegou_20)],
          ["Chegou a 30%", int(f10.chegou_30), int(f15.chegou_30)]]
a, b = escreve(ws, 3, ["Profundidade", "Partindo do gatilho de 10%", "Partindo do gatilho de 15%"],
               linhas, [None, INT, INT])
barras(ws, "Quantas ordens continuaram caindo", "ordens",
       Reference(ws, min_col=2, max_col=3, min_row=3, max_row=b), Reference(ws, min_col=1, min_row=a, max_row=b),
       "E3", INT)
ws.cell(b + 2, 1, "Leitura prática: das 341 ordens a 15%, 169 chegaram a 20% e só 45 chegaram a 30%.")

# ------------------------------------------------------------------ 3. Profundidade
ws = wb.create_sheet("Até onde caiu")
ws["A1"] = "Ordens abertas a 15%: resultado conforme o ponto mais fundo que a cota atingiu depois (total 2018 a 2026)"
ws["A1"].font = Font(bold=True, size=13)
linhas = []
for _, r in FA[(FA.gatilho == "15%") & (FA.periodo == "Total")].iterrows():
    linhas.append([r.faixa, int(r.ordens), r.media, r.pos])
a, b = escreve(ws, 3, ["Caiu até", "Ordens", "Resultado médio (%)", "Ordens com lucro (%)"],
               linhas, [None, INT, PCT, PCT])
barras(ws, "Resultado médio conforme a profundidade", "% da ordem",
       Reference(ws, min_col=3, min_row=3, max_row=b), Reference(ws, min_col=1, min_row=a, max_row=b), "F3", PCT)
barras(ws, "Ordens com lucro conforme a profundidade", "% das ordens",
       Reference(ws, min_col=4, min_row=3, max_row=b), Reference(ws, min_col=1, min_row=a, max_row=b), "F21", PCT)
linhas = []
for _, r in FA[(FA.gatilho == "15%") & (FA.periodo != "Total")].iterrows():
    linhas.append([PER[r.periodo], r.faixa, int(r.ordens), r.media, r.pos])
escreve(ws, b + 3, ["Período", "Caiu até", "Ordens", "Resultado médio (%)", "Ordens com lucro (%)"],
        linhas, [None, None, INT, PCT, PCT])
ws.cell(b + 11, 1, "Leitura prática: as ordens que caíram mais de 30% são as que dão prejuízo. "
        "De 2023 a 2026 elas perderam 23,8% em média, com só 3 de 16 no lucro.")

# ------------------------------------------------------------------ 4. Perdidas x evitadas
ws = wb.create_sheet("Subir o gatilho")
ws["A1"] = "Se eu esperar uma queda maior: lucros que deixo de ter contra prejuízos que evito (total 2018 a 2026)"
ws["A1"].font = Font(bold=True, size=13)
linhas = []
for _, r in PE[PE.periodo == "Total"].iterrows():
    linhas.append([f"De {r.de} para {r['para']}", int(r.luc_perdidas_n), round(r.luc_perdidas_rs, 0),
                   int(r.prej_evitados_n), round(-r.prej_evitados_rs, 0)])
a, b = escreve(ws, 3, ["Mudança", "Ordens com lucro que deixo de fazer", "Lucro que deixo de ter (R$)",
                       "Ordens com prejuízo que evito", "Prejuízo que evito (R$)"],
               linhas, [None, INT, RS, INT, RS])
ch = BarChart()
ch.type, ch.title = "col", "Lucro perdido contra prejuízo evitado"
ch.y_axis.title = "R$"
ch.add_data(Reference(ws, min_col=3, min_row=3, max_row=b), titles_from_data=True)
ch.add_data(Reference(ws, min_col=5, min_row=3, max_row=b), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=a, max_row=b))
ch.width, ch.height = 17, 8.5
ch.y_axis.delete = ch.x_axis.delete = False
ch.y_axis.number_format = RS
ws.add_chart(ch, "G3")
ws.cell(b + 2, 1, "Leitura prática: subir o gatilho evita só 6 prejuízos pequenos em cada mudança, "
        "e deixa de fazer de 125 a 241 ordens com lucro.")

# ------------------------------------------------------------------ 5. Legenda
ws = wb.create_sheet("Legenda e avisos")
for k, t in enumerate([
    "Legenda",
    "Gatilho: quanto a cota precisa estar abaixo da média dos últimos 200 pregões para comprar. Rendimento mantido em todos.",
    "Saída: quando a cota volta à média, ou depois de 252 pregões.",
    "Ordem: o menor valor entre R$ 3.000 e 5% do negociado no dia. Taxa de 0,03% na compra e na venda.",
    "Resultado da ordem: valorização + rendimentos − taxas, antes do imposto do fundo.",
    "Ganho acima do CDI: resultado da ordem menos o que o mesmo dinheiro, nas mesmas datas, renderia a 105% do CDI já descontado o imposto da renda fixa.",
    "Ganho acima do CDI por real aplicado: ganho acima do CDI dividido pelo total aplicado.",
    "Dinheiro necessário no pico: o maior valor que chegou a estar aplicado ao mesmo tempo, comprando todos os sinais.",
    "2018 a 2022 = período em que as regras foram escolhidas. 2023 a 2026 = período de conferência.",
    "Ordens em aberto entram pelo preço de 09/11/2026.",
    "",
    "Avisos",
    "1. O fundo está antes do imposto e o CDI depois do imposto: o ganho acima do CDI desta planilha fica um pouco maior que o real. A comparação entre gatilhos não muda.",
    "2. A auditoria (docs/AUDITORIA_KAIRI.md) mostrou que o ganho do Kairi sobre o CDI ainda não está provado contra sorte: vem de poucas ondas de queda (2020 e 2024).",
    "3. Amortizações e saltos de preço sem ajuste não foram corrigidos (ver tabela de lacunas da auditoria).",
    "Fonte: planilhas/auditoria_bloco2_*.csv, geradas por estudos/auditoria_bloco2.py.",
]):
    ws.cell(k + 1, 1, t).font = NEG if t in ("Legenda", "Avisos") else Font()
ws.column_dimensions["A"].width = 150

wb.save(SAIDA)
print(f"gravado: {SAIDA} (abas: {', '.join(wb.sheetnames)})")
