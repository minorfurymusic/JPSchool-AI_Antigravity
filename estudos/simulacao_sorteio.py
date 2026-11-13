"""Teste de sanidade da simulação: os mesmos dias de compra e as mesmas regras de saída,
mas com o FUNDO SORTEADO entre os que têm liquidez naquele dia.
Se o sorteio render parecido com os sinais, o ganho vem das regras de saída ou do mercado, não dos sinais.

Uso: PYTHONPATH=. .venv/bin/python estudos/simulacao_sorteio.py
"""
import warnings

import numpy as np
import pandas as pd

from estudos import simulacao as S

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
N = 30


def sortear(P, sinais, perfil, rng):
    cfg = S.PERFIS[perfil]
    s = sinais[sinais["gatilho"].isin(cfg["gatilhos"])].copy()
    novos = []
    for i0 in s["i0"]:
        if i0 >= len(P.datas):
            novos.append(None)
            continue
        cand = [t for t, j in P.col.items() if P.vol60[i0, j] >= cfg["liquidez"] and not np.isnan(P.A[i0, j])]
        novos.append(rng.choice(cand) if cand else None)
    s["ticker"] = novos
    return s.dropna(subset=["ticker"])


def main():
    P, sinais, prov = S.preparar()
    lin = []
    for ano, (a, b) in {**{y: (f"{y}-01-01", f"{y}-12-31") for y in range(2018, 2026)}, 2026: ("2026-01-01", "2026-10-31")}.items():
        for perfil in S.PERFIS:
            real = S.simular(P, sinais, prov, perfil, a, b)
            sub = sinais[(sinais["i0"] >= P.datas.searchsorted(pd.Timestamp(a)) - 5) & (sinais["i0"] <= P.datas.searchsorted(pd.Timestamp(b)))]
            res = []
            for k in range(N):
                rng = np.random.default_rng(1000 * ano + k)
                res.append((S.simular(P, sortear(P, sub, perfil, rng), prov, perfil, a, b)["final"] / S.CAPITAL - 1) * 100)
            res = np.array(res)
            r = (real["final"] / S.CAPITAL - 1) * 100
            lin.append({"ano": ano, "perfil": perfil, "com os sinais %": r, "sorteio: típico %": np.median(res), "sorteio: pior %": res.min(), "sorteio: melhor %": res.max(),
                        "sorteios que renderam mais que os sinais": int((res > r).sum())})
            print(lin[-1], flush=True)
    t = pd.DataFrame(lin)
    print(t.round(1).to_string(index=False))
    for perfil in S.PERFIS:
        x = t[t["perfil"] == perfil]
        print(f"{perfil}: média com os sinais {x['com os sinais %'].mean():+.1f}% | média do sorteio típico {x['sorteio: típico %'].mean():+.1f}% | "
              f"anos em que os sinais ficaram acima do sorteio típico: {(x['com os sinais %'] > x['sorteio: típico %']).sum()} de {len(x)} | "
              f"sorteios que bateram os sinais: {x['sorteios que renderam mais que os sinais'].sum()} de {len(x) * N}")


if __name__ == "__main__":
    main()
