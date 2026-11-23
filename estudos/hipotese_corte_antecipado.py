"""Hipóteses do dono sobre o RBRX11 (23/11/2026):
  H1 "o mercado já esperava o corte": a cota cai ANTES do aviso de corte de rendimento?
  H2 "a receita é concentrada em certas épocas": o resultado do fundo vem em ondas (alguns trimestres pagam o resto)?

Parte A — RBRX11 trimestre a trimestre (informe trimestral da CVM, planilhas/tecnico/cobertura_trimestral.csv):
  resultado do trimestre por cota × rendimento distribuído por cota (planilhas/rendimentos.csv, data-base no trimestre).
  Cotas = patrimônio ÷ valor patrimonial por cota (planilhas/precos_AAAA.csv, último dia do trimestre).
Parte B — RBRX11: caminho da cota antes e depois do aviso de 16/11/2026, contra o índice de mercado de FIIs.
Parte C — todos os fundos: os 184 cortes de estudos/reacao_corte.py (corte de 5% a 15% depois de 3+ avisos estáveis,
  negociação >= R$ 1 mi/dia). Variação da cota contra o mercado nos 20, 60 e 126 pregões ANTES do aviso, comparada com
  a de qualquer janela igual dos mesmos fundos (amostra a cada 20 pregões, mesma regra de negociação).

    PYTHONPATH=. python3 estudos/hipotese_corte_antecipado.py
"""
import numpy as np
import pandas as pd

from estudos.reacao_corte import E, M, PF, R

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
pd.set_option("display.width", 220)
F = "RBRX11"

# ---------------------------------------------------------------- A
T = pd.read_csv("planilhas/tecnico/cobertura_trimestral.csv", **OP)
T = T[T["fundo"] == F].copy()
T["fim"] = pd.to_datetime(T["data_ref"], dayfirst=True)
P = PF[F]
Rf = R[R["fundo"] == F]
linhas = []
for _, t in T.iterrows():
    p = P.loc[:t["fim"]]
    if p.empty or pd.isna(p["valor_patrimonial_cota"].iloc[-1]):
        continue
    cotas = p["patrimonio (R$)"].iloc[-1] / p["valor_patrimonial_cota"].iloc[-1]
    ini = t["fim"] - pd.offsets.QuarterBegin(startingMonth=1)
    dist = Rf[(Rf["data_base"] > t["fim"] - pd.DateOffset(months=3)) & (Rf["data_base"] <= t["fim"])]["valor (R$/cota)"].sum()
    res = t["resultado_trimestre"] / cotas
    linhas.append({"trimestre": f"{t['fim']:%m/%Y}", "resultado por cota (R$)": round(res, 3), "distribuído por cota (R$)": round(dist, 3),
                   "resultado ÷ distribuído": round(res / dist, 2) if dist else np.nan,
                   "parte do resultado que veio de venda de ativos": round(t["ganho_venda_semestre"] / t["resultado_acumulado"], 2)
                   if t["resultado_acumulado"] else np.nan, "cotas (milhões)": round(cotas / 1e6, 1)})
A = pd.DataFrame(linhas)
print(f"===== A. {F}: resultado × distribuído, trimestre a trimestre")
print(A.to_string(index=False))
A["tri"] = A["trimestre"].str[:2]
print("\nmédia de resultado ÷ distribuído por trimestre do ano (2022 em diante):")
print(A[A["trimestre"].str[3:] >= "2022"].groupby("tri")["resultado ÷ distribuído"].agg(["mean", "min", "max", "count"]).round(2).to_string())

# ---------------------------------------------------------------- B
d = pd.Timestamp("2026-11-16")
antes = P.loc[:d - pd.Timedelta(days=1)]
b, db = float(antes["fechamento"].iloc[-1]), antes.index[-1]
m0 = float(M.loc[:db].iloc[-1])
print(f"\n===== B. {F}: cota antes do aviso de corte (16/11/2026; base = fechamento de {db:%d/%m/%Y}, R$ {b:.2f})")
for k in (126, 60, 20, 5):
    if len(antes) > k:
        c0, d0 = float(antes["fechamento"].iloc[-1 - k]), antes.index[-1 - k]
        mm = m0 / float(M.loc[:d0].iloc[-1]) - 1
        print(f"  {k:>3} pregões antes ({d0:%d/%m/%Y}): R$ {c0:.2f} -> variação até a véspera {b / c0 - 1:+.1%}; mercado {mm:+.1%}; "
              f"contra o mercado {b / c0 - 1 - mm:+.1%}")
dep = P.loc[d:]
print("  depois do aviso:", ", ".join(f"{i:%d/%m} R$ {v:.2f}" for i, v in dep["fechamento"].items()))

# ---------------------------------------------------------------- C
def antes_de(f, d, k):
    s = PF[f].loc[:d - pd.Timedelta(days=1)]
    if len(s) <= k:
        return np.nan
    c1, d1, c0, d0 = s["fechamento"].iloc[-1], s.index[-1], s["fechamento"].iloc[-1 - k], s.index[-1 - k]
    return c1 / c0 - 1 - (float(M.loc[:d1].iloc[-1]) / float(M.loc[:d0].iloc[-1]) - 1)

for k in (20, 60, 126):
    E[f"antes_{k}"] = [antes_de(f, d, k) for f, d in zip(E["fundo"], E["anuncio"])]
base = {k: [] for k in (20, 60, 126)}
for f in E["fundo"].unique():
    s = PF[f]
    for j in range(126, len(s), 20):
        if s["volume_medio_60 (R$)"].iloc[j] < 1e6:
            continue
        for k in base:
            c1, d1, c0, d0 = s["fechamento"].iloc[j], s.index[j], s["fechamento"].iloc[j - k], s.index[j - k]
            base[k].append(c1 / c0 - 1 - (float(M.loc[:d1].iloc[-1]) / float(M.loc[:d0].iloc[-1]) - 1))
print(f"\n===== C. Todos os fundos: {len(E)} cortes de rendimento em {E['fundo'].nunique()} fundos (2017–2026)")
print("Variação da cota CONTRA O MERCADO antes do aviso (mediana; entre parênteses, 1 em 4 pior / 1 em 4 melhor):")
for k in (20, 60, 126):
    x, y = E[f"antes_{k}"].dropna(), pd.Series(base[k])
    print(f"  {k:>3} pregões antes: cortes {x.median():+.1%} ({x.quantile(.25):+.1%} / {x.quantile(.75):+.1%}), n={len(x)} | "
          f"qualquer janela dos mesmos fundos {y.median():+.1%} ({y.quantile(.25):+.1%} / {y.quantile(.75):+.1%}), n={len(y)} | "
          f"cortes que já tinham caído 5%+ contra o mercado: {(x <= -0.05).mean():.0%} contra {(y <= -0.05).mean():.0%}")
print("Depois do aviso (mesmo estudo): mediana contra o mercado em 20 pregões "
      f"{E['contra_mercado_20'].median():+.1%}; em 126 pregões {E['contra_mercado_126'].median():+.1%}")
