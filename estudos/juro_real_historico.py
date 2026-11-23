"""Histórico do juro dos títulos públicos a partir da planilha do Tesouro Transparente (23/11/2026).

O site do Tesouro recusa conexões do GitHub, então a planilha foi baixada uma vez pelo navegador do dono
(https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto, CSV de 14 MiB,
2002–19/11/2026, preços e taxas da manhã). Daqui para a frente a rotina diária usa a ANBIMA.

Saídas:
  planilhas/rotina/tesouro_direto_taxas.csv  — todos os títulos, de 2017 em diante, como vieram do Tesouro
  planilhas/rotina/juro_real_10_anos.csv     — um número por dia: NTN-B (Tesouro IPCA+ com Juros Semestrais) que vence
                                               mais perto de 10 anos depois; taxa = média de compra e venda da manhã
                                               (nos 5 dias em comum, 13–19/11/2026, ficou 0,04 ponto em média da taxa
                                               indicativa da ANBIMA; compra sozinha −0,05; venda sozinha +0,07).
                                               Dias da ANBIMA (rotina) prevalecem sobre os do Tesouro.

    PYTHONPATH=. python3 estudos/juro_real_historico.py CAMINHO/precotaxatesourodireto.csv
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rotina_diaria import GRAVA, INICIO_HIST, OP, ROT, juntar, juro_real_10_anos  # noqa: E402

T = pd.read_csv(sys.argv[1], sep=";", decimal=",", encoding="latin-1")
T["d"] = pd.to_datetime(T["Data Base"], dayfirst=True)
T = T[T["d"] >= pd.Timestamp(INICIO_HIST)].sort_values(["d", "Tipo Titulo", "Data Vencimento"])
S = pd.DataFrame({"data": T["Data Base"], "titulo": T["Tipo Titulo"], "vencimento": T["Data Vencimento"],
                  "taxa_compra (% ao ano)": T["Taxa Compra Manha"], "taxa_venda (% ao ano)": T["Taxa Venda Manha"],
                  "pu_compra (R$)": T["PU Compra Manha"], "pu_venda (R$)": T["PU Venda Manha"], "pu_base (R$)": T["PU Base Manha"]})
ROT.mkdir(parents=True, exist_ok=True)
S.to_csv(ROT / "tesouro_direto_taxas.csv", **GRAVA)
print(f"tesouro_direto_taxas.csv: {len(S)} linhas, {S['data'].iloc[0]} a {S['data'].iloc[-1]}")

B = T[T["Tipo Titulo"] == "Tesouro IPCA+ com Juros Semestrais"]
J = juro_real_10_anos(pd.DataFrame({"data": B["Data Base"], "vencimento": B["Data Vencimento"],
                                    "taxa": (B["Taxa Compra Manha"] + B["Taxa Venda Manha"]) / 2}),
                      "Tesouro Direto (média compra/venda, manhã)")
arq = ROT / "juro_real_10_anos.csv"
velho = pd.read_csv(arq, **OP) if arq.exists() else None
if velho is not None:  # ANBIMA prevalece: tira do Tesouro os dias que a rotina já tem
    J = J[~J["data"].isin(velho["data"])]
a, b = juntar(arq, J, ["data"], ["data"])
an = ROT / "titulos_publicos_anbima.csv"
if an.exists():  # dias que a rotina já trouxe da ANBIMA entram por cima
    A = pd.read_csv(an, **OP).rename(columns={"taxa_indicativa (% ao ano)": "taxa"})
    _, b = juntar(arq, juro_real_10_anos(A[A["titulo"] == "NTN-B"], "ANBIMA (taxa indicativa)"), ["data"], ["data"])
print(f"juro_real_10_anos.csv: {a} -> {b} linhas")
x = pd.read_csv(arq, **OP)
x["ano"] = x["data"].str[6:]
print(x.groupby("ano")["juro_real (% ao ano + IPCA)"].agg(["min", "mean", "max", "count"]).round(2).to_string())
print(x.tail(8).to_string(index=False))
