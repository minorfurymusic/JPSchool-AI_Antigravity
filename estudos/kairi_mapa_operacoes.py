"""Mapa das oportunidades do molde atual (C1 25% com mediana de R$ 500 mil a 1 mi + C2 20% acima de R$ 1 mi,
aprovadas pela avaliação de saúde), 2018 a 09/11/2026, com dinheiro à vontade (todas as oportunidades).
Lê planilhas/kairi_oportunidades.xlsx (aba "Operações 1", gerada por estudos/kairi_oportunidades.py).
Grava planilhas/kairi_mapa_operacoes.xlsx e o gráfico planilhas/kairi_mapa_operacoes.png.

    PYTHONPATH=. python3 estudos/kairi_mapa_operacoes.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

FIM = pd.Timestamp("2026-11-09")
O = pd.read_excel("planilhas/kairi_oportunidades.xlsx", sheet_name="Operações 1")
O = O[O["veredito"] != "NÃO COMPRAR"].copy()
for c in ("sinal", "entrada", "saida"):
    O[c] = pd.to_datetime(O[c])
O["fim"] = O["saida"].fillna(FIM)
O["dias"] = (O["fim"] - O["entrada"]).dt.days
O["situacao"] = O["status"].map({"Fechada": "fechada"}).fillna("em aberto")
O["ano"] = O["entrada"].dt.year
O = O.sort_values("entrada").reset_index(drop=True)
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ANOS = range(2018, 2027)

# por ano
A = O.groupby("ano").agg(Oportunidades=("fundo", "size"), Fechadas=("situacao", lambda s: (s == "fechada").sum()),
                         Dias_medios=("dias", "mean"), Dias_mediana=("dias", "median"),
                         Resultado_medio=("res", "mean"), Com_prejuizo=("res", lambda s: (s < 0).sum())
                         ).reindex(ANOS).fillna(0)
# entradas e saídas por mês
ENT = pd.crosstab(O["entrada"].dt.year, O["entrada"].dt.month).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
f = O[O["situacao"] == "fechada"]
SAI = pd.crosstab(f["saida"].dt.year, f["saida"].dt.month).reindex(index=ANOS, columns=range(1, 13), fill_value=0)
# ativas ao mesmo tempo: máximo de cada mês
dias = pd.date_range("2018-01-02", FIM, freq="D")
ativas = pd.Series([int(((O["entrada"] <= d) & (O["fim"] > d)).sum()) for d in dias], index=dias)
ATV = ativas.groupby([ativas.index.year, ativas.index.month]).max().unstack().reindex(index=ANOS, columns=range(1, 13))
for T in (ENT, SAI, ATV):
    T.columns = MES

pd.set_option("display.width", 250)
print("POR ANO\n" + A.round(3).to_string())
print(f"\nTotal: {len(O)} oportunidades; prazo médio {O['dias'].mean():.0f} dias (mediana {O['dias'].median():.0f}); "
      f"fechadas {len(f)}, resultado médio {f['res'].mean():+.1%}")
print(f"Ativas ao mesmo tempo: máximo {ativas.max()} em {ativas.idxmax():%d/%m/%Y}; dias com nenhuma: {100 * (ativas == 0).mean():.0f}%; "
      f"com 1 ou 2: {100 * ativas.between(1, 2).mean():.0f}%; com 3 ou mais: {100 * (ativas >= 3).mean():.0f}%")
print("\nENTRADAS POR MÊS\n" + ENT.to_string())
print("\nSAÍDAS POR MÊS\n" + SAI.to_string())
print("\nMÁXIMO DE OPERAÇÕES ATIVAS AO MESMO TEMPO, POR MÊS\n" + ATV.fillna(0).astype(int).to_string())
print("\nOPERAÇÕES\n" + O[["fundo", "carteira" if "carteira" in O else "fundo", "entrada", "fim", "dias", "situacao", "res"]]
      .to_string(index=False, float_format=lambda v: f"{v:+.1%}"))

# gráfico: uma barra por operação, do dia da compra ao da venda
fig, ax = plt.subplots(2, 1, figsize=(14, 11), gridspec_kw=dict(height_ratios=[3, 1]), sharex=True)
for i, r in O.iterrows():
    cor = "#2e7d32" if (r["situacao"] == "fechada" and r["res"] >= 0) else "#c62828" if r["situacao"] == "fechada" else "#757575"
    ax[0].barh(i, (r["fim"] - r["entrada"]).days, left=r["entrada"], color=cor, height=0.7)
    ax[0].text(r["fim"] + pd.Timedelta(days=8), i, f"{r['fundo']} {'' if pd.isna(r['res']) else format(r['res'], '+.0%')}",
               va="center", fontsize=7)
ax[0].invert_yaxis()
ax[0].set_yticks([])
ax[0].set_title("Operações do molde atual (C1 25% + C2 20%, aprovadas pela avaliação): verde = lucro, vermelho = prejuízo, cinza = em aberto")
ax[1].fill_between(ativas.index, ativas.values, step="post", color="#1565c0")
ax[1].set_ylabel("ativas ao mesmo tempo")
ax[1].grid(alpha=0.3)
ax[0].grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("planilhas/kairi_mapa_operacoes.png", dpi=110)

with pd.ExcelWriter("planilhas/kairi_mapa_operacoes.xlsx") as w:
    A.to_excel(w, sheet_name="Por ano")
    ENT.to_excel(w, sheet_name="Entradas por mês")
    SAI.to_excel(w, sheet_name="Saídas por mês")
    ATV.to_excel(w, sheet_name="Ativas ao mesmo tempo")
    O.drop(columns=[c for c in ("e", "k", "mi_e", "mi_d", "mi_s", "rr") if c in O.columns]).to_excel(w, sheet_name="Operações", index=False)
print("gravado: planilhas/kairi_mapa_operacoes.xlsx e planilhas/kairi_mapa_operacoes.png")
