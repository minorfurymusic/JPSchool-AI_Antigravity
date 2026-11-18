"""Boletim Focus (Banco Central, olinda.bcb.gov.br): expectativa do mercado para a Selic, 2017 em diante.

Gera duas tabelas (separador ;, decimal ,):
  planilhas/focus_selic_fim_de_ano.csv  expectativa da Selic no FIM de cada ano, coletada em cada dia útil
  planilhas/focus_selic_reuniao.csv     expectativa da Selic em cada reunião do Copom, coletada em cada dia útil
Colunas: data da coleta, ano (ou reunião) da expectativa, mediana, média, desvio padrão, mínimo, máximo, respondentes,
base de cálculo (0 = todas as respostas dos últimos 30 dias; 1 = só as atualizadas nos últimos 5 dias úteis).
Conferido em 18/11/2026: sem buraco maior que 5 dias (só carnaval e feriados); 100 linhas de 06/2017 sem número de
respondentes (o próprio Banco Central não publicou).

    PYTHONPATH=. python3 estudos/focus.py
"""
import urllib.parse as up

import pandas as pd
import requests

B = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
NOMES = {"Data": "data_coleta", "DataReferencia": "ano_referencia", "Reuniao": "reuniao_copom", "Mediana": "mediana (%)",
         "Media": "media (%)", "DesvioPadrao": "desvio_padrao", "Minimo": "minimo (%)", "Maximo": "maximo (%)",
         "numeroRespondentes": "respondentes", "baseCalculo": "base_calculo"}


def baixa(recurso, filtro):
    out, skip = [], 0
    while True:
        q = f"{B}{recurso}?$filter={up.quote(filtro)}&$format=json&$top=10000&$skip={skip}"
        r = requests.get(q, timeout=180)
        r.raise_for_status()
        v = r.json()["value"]
        out += v
        skip += len(v)
        if len(v) < 10000:
            return pd.DataFrame(out)


def gravar(df, cols, arq):
    df = df.rename(columns=NOMES)[cols].sort_values(cols[:2])
    df["data_coleta"] = pd.to_datetime(df["data_coleta"]).dt.strftime("%d/%m/%Y")
    df.to_csv(arq, sep=";", decimal=",", encoding="utf-8-sig", index=False)
    print(f"gravado: {arq} ({len(df)} linhas, {df['data_coleta'].nunique()} dias)")


if __name__ == "__main__":
    base = ["mediana (%)", "media (%)", "desvio_padrao", "minimo (%)", "maximo (%)", "respondentes", "base_calculo"]
    A = baixa("ExpectativasMercadoAnuais", "Indicador eq 'Selic' and Data ge '2017-01-01'")
    gravar(A, ["data_coleta", "ano_referencia"] + base, "planilhas/focus_selic_fim_de_ano.csv")
    R = baixa("ExpectativasMercadoSelic", "Data ge '2017-01-01'")
    gravar(R, ["data_coleta", "reuniao_copom"] + base, "planilhas/focus_selic_reuniao.csv")
