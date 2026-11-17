"""Ficha de saúde de um fundo num dia, para a Skill "avaliar-fundo".

    PYTHONPATH=. python3 estudos/ficha_fundo.py TGAR11 13/10/2026
"""
import sys

import pandas as pd

from estudos.saude_fundo import _dados, saude


def ficha(fundo, dia):
    s = saude(fundo, dia)
    d = pd.Timestamp(dia)
    PF, M, RF, DOC = _dados()
    print(f"FICHA {fundo} em {d:%d/%m/%Y}  ->  {s['veredito']}")
    if s["veredito"] == "SEM DADOS":
        return s
    print(f"  queda 6 meses: fundo {s['queda_fundo_6m']:+.1%} | mercado {s['queda_mercado_6m']:+.1%} | diferença {s['individual_6m']:+.1%}")
    print(f"  queda 12 meses: fundo {s['queda_fundo_12m']:+.1%} | mercado {s['queda_mercado_12m']:+.1%}")
    print(f"  preço/valor patrimonial {s['pvp']:.2f} | rendimento do ano sobre o preço {s['rend_ano_sobre_preco']:.1%} | patrimônio R$ {s['patrimonio_mi']:.0f} mi")
    print(f"  valor patrimonial por cota em 12 meses {s['vp_12m']:+.1%}")
    print(f"  rendimento 12 meses: tendência {s['tendencia_rend']:+.0%} | cortes {s['cortes_rend']} | oscilação {s['oscilacao_rend']:.2f}")
    r = RF.get(fundo)
    if r is not None:
        r = r[(r["data_base"] <= d) & (r["data_base"] > d - pd.DateOffset(months=24))]
        print("  rendimento mês a mês (24 meses): " + " ".join(f"{x:%m/%y}:{v:.3f}" for x, v in zip(r["data_base"], r["valor (R$/cota)"])))
    print("  problemas: " + ("; ".join(s["problemas"]) if s["problemas"] else "nenhum"))
    docs = DOC.get(fundo)
    if docs is not None:
        docs = docs[(docs["dia"] <= d) & (docs["dia"] > d - pd.DateOffset(months=12))]
        print(f"  documentos dos 12 meses anteriores: {len(docs)} (ler todos antes de decidir)")
        for x in docs.itertuples():
            print(f"    {x.dia:%d/%m/%Y} [{x.fonte}] {' '.join(str(x.texto).split())[:300]}")
    for a in s["docs_negativos"]:
        print("  NEGATIVO: " + a)
    return s


if __name__ == "__main__":
    ficha(sys.argv[1], pd.to_datetime(sys.argv[2], dayfirst=True))
