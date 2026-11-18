"""Quadro mensal do país (Banco Central, api.bcb.gov.br, séries SGS) + Boletim Focus, 01/2017 a 11/2026.

Séries: 432 Selic meta (% ao ano, diária -> último valor do mês); 13522 IPCA acumulado em 12 meses (%);
3698 dólar, média mensal de venda (R$); 13762 dívida bruta do governo geral (% do PIB);
5793 necessidade de financiamento do setor público, primário, 12 meses (% do PIB; POSITIVO = DÉFICIT).
Focus: mediana da Selic esperada para o fim do ano seguinte (planilhas/focus_selic_fim_de_ano.csv, última coleta do mês).
Saída: planilhas/macro_mensal.csv (uma linha por mês; célula vazia = o Banco Central ainda não publicou o mês).

    PYTHONPATH=. python3 estudos/macro_mensal.py
"""
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{c}/dados?formato=json&dataInicial=01/01/2017&dataFinal=31/12/2026"
SERIES = {432: "selic (% ano)", 13522: "ipca 12 meses (%)", 3698: "dolar medio (R$)", 13762: "divida bruta (% PIB)",
          5793: "deficit primario 12 meses (% PIB)"}


def serie(c):
    r = requests.get(URL.format(c=c), timeout=120)
    r.raise_for_status()
    d = pd.DataFrame(r.json())
    d["data"] = pd.to_datetime(d["data"], dayfirst=True)
    d["valor"] = pd.to_numeric(d["valor"])
    return d.groupby(d["data"].dt.to_period("M"))["valor"].last()


if __name__ == "__main__":
    M = pd.DataFrame({n: serie(c) for c, n in SERIES.items()})
    M = M[M.index <= pd.Timestamp.today().to_period("M")]       # a série da Selic meta vem com datas futuras
    F = pd.read_csv(RAIZ / "planilhas/focus_selic_fim_de_ano.csv", sep=";", decimal=",", encoding="utf-8-sig")
    F["data_coleta"] = pd.to_datetime(F["data_coleta"], dayfirst=True)
    F = F[(F["base_calculo"] == 0) & (F["ano_referencia"] == F["data_coleta"].dt.year + 1)]
    M["focus selic fim do ano seguinte (%)"] = F.groupby(F["data_coleta"].dt.to_period("M"))["mediana (%)"].last()
    M["mercado espera (focus - selic, pontos)"] = M["focus selic fim do ano seguinte (%)"] - M["selic (% ano)"]
    M["selic: variação em 6 meses (pontos)"] = M["selic (% ano)"] - M["selic (% ano)"].shift(6)
    M["dolar: variação em 6 meses"] = M["dolar medio (R$)"] / M["dolar medio (R$)"].shift(6) - 1
    M["divida bruta: variação em 12 meses (pontos)"] = M["divida bruta (% PIB)"] - M["divida bruta (% PIB)"].shift(12)
    M.index = M.index.strftime("%m/%Y")
    M.index.name = "mes"
    M.to_csv(RAIZ / "planilhas/macro_mensal.csv", sep=";", decimal=",", encoding="utf-8-sig", float_format="%.4f")
    print(f"gravado: planilhas/macro_mensal.csv ({len(M)} meses); meses sem dado por coluna:")
    print(M.isna().sum().to_string())
