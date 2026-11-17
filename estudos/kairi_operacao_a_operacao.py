"""Operação a operação da simulação contínua (02/01/2018 a 09/11/2026) das 4 carteiras da versão 3.

Lê planilhas/kairi_carteira_anos.xlsx (gerada por estudos/kairi_carteira_anos.py) e planilhas/cdi.csv.
Para cada operação: o mesmo valor, nas mesmas datas, em 105% do CDI com IR regressivo e IOF,
e a diferença. Ordens em aberto: até o último preço (09/11/2026), sem venda.
Grava planilhas/kairi_operacao_a_operacao.xlsx.

    PYTHONPATH=. python3 estudos/kairi_operacao_a_operacao.py
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment

PL = Path("planilhas")
ORIGEM = PL / "kairi_carteira_anos.xlsx"
SAIDA = PL / "kairi_operacao_a_operacao.xlsx"
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]

cdi = pd.read_csv(PL / "cdi.csv", sep=";", decimal=",", encoding="utf-8-sig")
cdi["data"] = pd.to_datetime(cdi["data"], dayfirst=True)
I105 = cdi.set_index("data")["indice_105_do_cdi"]


def indice(d):
    return float(I105.loc[:pd.Timestamp(d)].iloc[-1])   # último dia útil até d


def cdi_liquido(valor, d0, d1):
    dias = (pd.Timestamp(d1) - pd.Timestamp(d0)).days
    bruto = valor * (indice(d1) / indice(d0) - 1)
    iof = bruto * IOF[dias - 1] / 100 if 1 <= dias <= 29 else 0.0
    ir = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
    return (bruto - iof) * (1 - ir)


def ler(aba):
    return pd.read_excel(ORIGEM, sheet_name=aba, header=2)


F = ler("Operações fechadas")
F = F[F["Rodada"].astype(str).str.startswith("Cont")].copy()
F["Situação"] = "fechada"
A = ler("Posições abertas no fim do ano")
A = A[A["Rodada"].astype(str).str.startswith("Cont")].copy()
A = A.rename(columns={"Data do último preço": "Saída", "Último preço (R$)": "Preço de saída (R$)",
                      "Valor atual (R$)": "Valor de saída (R$)", "Rendimentos pagos (R$)": "Rendimentos recebidos (R$)"})
A["Situação"] = "em aberto"
A["Motivo da saída"] = "em aberto (preço de 09/11/2026)"
col = ["Sub-carteira", "Fundo", "Situação", "Entrada", "Preço de entrada (R$)", "Cotas", "Valor de entrada (R$)",
       "Saída", "Preço de saída (R$)", "Valor de saída (R$)", "Motivo da saída", "Rendimentos recebidos (R$)",
       "Resultado (R$)", "Resultado (%)"]
O = pd.concat([F[col], A[col]], ignore_index=True).sort_values(["Entrada", "Sub-carteira"]).reset_index(drop=True)
O["Dias"] = (O["Saída"] - O["Entrada"]).dt.days
O["105% CDI no mesmo período, líquido (R$)"] = [cdi_liquido(v, a, b) for v, a, b in
                                               zip(O["Valor de entrada (R$)"], O["Entrada"], O["Saída"])]
O["105% CDI (%)"] = O["105% CDI no mesmo período, líquido (R$)"] / O["Valor de entrada (R$)"]
O["Acima do CDI (R$)"] = O["Resultado (R$)"] - O["105% CDI no mesmo período, líquido (R$)"]
O["Ganhou do CDI"] = O["Acima do CDI (R$)"].gt(0).map({True: "sim", False: "não"})
O["Acumulado acima do CDI na carteira (R$)"] = O.groupby("Sub-carteira")["Acima do CDI (R$)"].cumsum()
O.insert(0, "Nº", range(1, len(O) + 1))

# conferência: uma operação refeita à mão
r = O.iloc[0]
d = (r["Saída"] - r["Entrada"]).days
b = r["Valor de entrada (R$)"] * (indice(r["Saída"]) / indice(r["Entrada"]) - 1)
print(f"conferência nº1 {r['Fundo']} {r['Entrada']:%d/%m/%Y}→{r['Saída']:%d/%m/%Y}: {d} dias, bruto {b:.2f}, "
      f"líquido {cdi_liquido(r['Valor de entrada (R$)'], r['Entrada'], r['Saída']):.2f}")
assert len(F) == 169 and len(A) == 14, (len(F), len(A))

RES = O.groupby("Sub-carteira").agg(
    Operações=("Fundo", "size"), Fechadas=("Situação", lambda s: (s == "fechada").sum()),
    Ganharam_do_CDI=("Ganhou do CDI", lambda s: (s == "sim").sum()),
    Aplicado=("Valor de entrada (R$)", "sum"), Resultado=("Resultado (R$)", "sum"),
    CDI=("105% CDI no mesmo período, líquido (R$)", "sum"), Acima=("Acima do CDI (R$)", "sum"),
    Dias_medios=("Dias", "mean"))
RES.loc["Total"] = [RES[c].sum() if c != "Dias_medios" else O["Dias"].mean() for c in RES.columns]
print(RES.round(2).to_string())

# ------------------------------------------------------------------ planilha
wb = Workbook()
NEG, CAB = Font(bold=True), PatternFill("solid", fgColor="DDEBF7")
FMT = {"Entrada": "dd/mm/yyyy", "Data de entrada": "dd/mm/yyyy", "Saída": "dd/mm/yyyy", "Resultado (%)": "0.0%", "105% CDI (%)": "0.0%"}


def tabela(ws, df, linha=3):
    for j, c in enumerate(df.columns, 1):
        x = ws.cell(linha, j, c)
        x.font, x.fill, x.alignment = NEG, CAB, Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[x.column_letter].width = 14
    ws.row_dimensions[linha].height = 45
    for i, row in enumerate(df.itertuples(index=False), linha + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v.to_pydatetime() if isinstance(v, pd.Timestamp) else v)
            nome = df.columns[j - 1]
            c.number_format = FMT.get(nome, '#,##0.00' if isinstance(v, float) else "General")
    ws.freeze_panes = ws.cell(linha + 1, 4)


ws = wb.active
ws.title = "Resumo"
ws["A1"] = "Operação a operação, simulação contínua 02/01/2018 a 09/11/2026 (R$ 10 mil por carteira, ordem de R$ 1.000)"
ws["A1"].font = Font(bold=True, size=13)
R = RES.reset_index().rename(columns={"Ganharam_do_CDI": "Ganharam do CDI", "Aplicado": "Total aplicado (R$)",
                                      "Resultado": "Resultado das operações (R$)", "CDI": "105% CDI no mesmo período (R$)",
                                      "Acima": "Acima do CDI (R$)", "Dias_medios": "Dias médios"})
tabela(ws, R)
for k, t in enumerate([
    "Resultado = venda (ou valor em 09/11/2026) − compra + rendimentos recebidos − taxas, antes do imposto do fundo.",
    "105% CDI = o mesmo valor, nas mesmas datas, em 105% do CDI, já descontados IR regressivo e IOF.",
    "Acima do CDI = resultado − 105% CDI. Imposto do fundo (20% sobre o ganho do mês) não está aqui; ele é cobrado no total do mês.",
]):
    ws.cell(len(R) + 6 + k, 1, t)

ws = wb.create_sheet("Operações")
ws["A1"] = "Todas as operações em ordem de entrada. Em aberto = avaliada pelo último preço de 09/11/2026."
tabela(ws, O)

ws = wb.create_sheet("Acumulado")
ws["A1"] = "Quanto cada carteira acumulou acima do CDI, operação após operação (R$)"
P = O.pivot_table(index="Nº", columns="Sub-carteira", values="Acumulado acima do CDI na carteira (R$)").ffill().fillna(0)
P.insert(0, "Data de entrada", O.set_index("Nº")["Entrada"])
tabela(ws, P.reset_index(drop=True))
ch = LineChart()
ch.title, ch.y_axis.title, ch.x_axis.title = "Acumulado acima do CDI, operação após operação", "R$", "operação (em ordem de entrada)"
ch.add_data(Reference(ws, min_col=2, max_col=P.shape[1], min_row=3, max_row=3 + len(P)), titles_from_data=True)
ch.width, ch.height = 26, 12
ch.y_axis.delete = ch.x_axis.delete = False
ch.y_axis.number_format = '"R$" #,##0'
ch.x_axis.tickLblPos = "low"
ws.add_chart(ch, "H3")
wb.save(SAIDA)
print(f"gravado: {SAIDA} ({len(O)} operações)")
