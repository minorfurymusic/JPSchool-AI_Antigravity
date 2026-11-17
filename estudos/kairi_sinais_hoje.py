"""Sinais do molde Kairi Padrão nos últimos pregões da base, com a avaliação de saúde de cada um.
Molde: C1 = cota 25% abaixo da média de 200 pregões, mediana de negociação de 60 pregões de R$ 500 mil a R$ 1 milhão;
       C2 = cota 20% abaixo, mediana de R$ 1 milhão ou mais. Rendimento mantido, universo e bloqueios da versão 3.

    PYTHONPATH=. python3 estudos/kairi_sinais_hoje.py [pregões]      (padrão: 10)
"""
import contextlib
import io
import runpy
import sys

import numpy as np
import pandas as pd

from estudos.saude_fundo import saude

N_ULT = int(sys.argv[1]) if len(sys.argv) > 1 else 10
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="biblioteca")
G = g["simular"].__globals__
FD, MD, NM = G["FD"], G["MD"], G["NM"]
FAIXAS = [("C1", 0.25, 500e3, 1e6), ("C2", 0.20, 1e6, np.inf)]
linhas = []
for F in FD.values():
    for cart, X, lo, hi in FAIXAS:
        for s in np.flatnonzero(G["sinais"](F, X)):
            md = int(F["mi"][s])
            if md < NM - N_ULT or not (lo <= F["VMED"][s] < hi):
                continue
            dia = MD[md]
            bl = G["bloqueio"](F["nome"], dia)
            cut = G["corte_rendimento"](F["nome"], dia, F["dates"][s - G["LAG_REND"]])
            sv = saude(F["nome"], dia)
            linhas.append(dict(dia=pd.Timestamp(dia), carteira=cart, fundo=F["nome"], negociacao_mediana=F["VMED"][s],
                               preco=F["C"][s], media_200=F["mP"][s],
                               bloqueio="sim: " + bl[-1]["padrao"] if bl else ("rendimento zero" if cut else "não"),
                               veredito=sv["veredito"], problemas="; ".join(sv.get("problemas", [])),
                               queda_so_do_fundo_6m=sv.get("individual_6m")))
T = pd.DataFrame(linhas)
print(f"Últimos {N_ULT} pregões da base (até {pd.Timestamp(MD[NM - 1]):%d/%m/%Y}): {len(T)} sinais")
if len(T):
    pd.set_option("display.width", 250)
    print(T.sort_values(["dia", "negociacao_mediana"], ascending=[True, False]).to_string(index=False))
    print("\nPara cada sinal SAUDÁVEL ou ATENÇÃO: rodar a ficha (estudos/ficha_fundo.py) e ler os documentos (Skill avaliar-fundo).")
