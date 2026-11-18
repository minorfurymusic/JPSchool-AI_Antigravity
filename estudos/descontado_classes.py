"""Tipo 1 trade separado por classe de fundo (pedido do dono, 18/11/2026), com as contas corrigidas.

Correções (pedido do dono, 18/11/2026):
  1. rendimento conta pela data-com: tem direito quem está com o fundo no fim do dia da data-base; vale para
     entrada <= data-base <= dia da venda, mesmo que o pagamento seja depois da venda.
  2. imposto de 20% sobre o ganho na cota de cada operação com lucro na cota (sem abater prejuízo de outras operações,
     o que deixa a conta um pouco pior que a real); rendimento isento.
  O CDI de comparação continua sendo 105% do CDI líquido de IR, do dia da compra ao dia da venda.
Sinais: em cada fim de mês, candidatos da versão 2 (descontado_saudavel.candidatos_v2); "Todos" = os 5 de maior nota;
  cada classe (classificacao_carteira: Papel, Tijolo, Desenvolvimento, Fundo de fundos, Híbrido) = os 5 de maior nota
  DENTRO da classe. Compra na abertura do pregão seguinte. Fundo só entra de novo depois de sair.
Vendas: as 8 de estudos/descontado_saidas.py (alvo +10/+15%, médias 21×70 e 21×90, Fibonacci 38,2/50/61,8%, banda
  superior de Bollinger), decididas pelo caminho bruto (o que o investidor vê); prazo de 252 pregões; sem stop.

    PYTHONPATH=. python3 estudos/descontado_classes.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_caminho as CA
import estudos.descontado_saidas as SA

DS, RD, RF, SER = SA.DS, SA.RD, SA.RF, SA.SER
PRAZO, B3, IR = 252, 0.0003, 0.20
CLASSES = ["Todos", "Papel", "Tijolo", "Fundo de fundos", "Híbrido", "Desenvolvimento"]


def caminho(f, ent):
    s = SER[f]
    px0 = float(s.loc[ent, "abertura"])
    if not px0 > 0:
        return None
    custo = px0 * (1 + B3)
    y = s.loc[ent:].iloc[:PRAZO]
    r = RF.get(f)
    if r is not None:
        r = r[r["data_base"] >= ent]
        acum = r.groupby("data_base")["valor (R$/cota)"].sum().reindex(y.index.union(r["data_base"])).fillna(0).cumsum()
        rend = acum.reindex(y.index, method="ffill").fillna(0).to_numpy(float)
    else:
        rend = np.zeros(len(y))
    c = y["fechamento"].to_numpy(float)
    return dict(y=y, c=c, ret=(c * (1 - B3) + rend) / custo - 1, rend=rend, custo=custo, px0=px0, T=float(s.loc[ent, "topo252"]))


def liquido(cm, k):
    venda = cm["c"][k] * (1 - B3)
    ganho_cota = venda - cm["custo"]
    imposto = IR * ganho_cota if ganho_cota > 0 else 0.0
    return (venda - imposto + cm["rend"][k]) / cm["custo"] - 1, imposto / cm["custo"]


if __name__ == "__main__":
    pd.set_option("display.width", 300)
    pd.set_option("display.max_columns", 40)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    CAND = [(d, DS.candidatos_v2(d)) for d in fms]
    print("sinais prontos", flush=True)
    LIN = []
    for cl in CLASSES:
        for v in SA.VENDAS:
            livre = {}
            for d, C in CAND:
                if C.empty:
                    continue
                X = C if cl == "Todos" else C[C["tipo"] == cl]
                for r in X.head(5).itertuples():
                    f = r.fundo
                    if livre.get(f, pd.Timestamp.min) > d:
                        continue
                    ent = SA.dia_compra(f, d, "A", None)
                    if ent is None:
                        continue
                    cm = caminho(f, ent)
                    if cm is None:
                        continue
                    k, alvo = CA.regra(cm, v)
                    if k == "sem_topo":
                        continue
                    n = len(cm["ret"])
                    if k is None:
                        livre[f] = cm["y"].index[-1]
                        if n < PRAZO:
                            continue
                        k, sit = n - 1, "prazo de 1 ano"
                    else:
                        sit = "vendeu pela regra"
                    livre[f] = cm["y"].index[k]
                    res, imp = liquido(cm, k)
                    a = cm["ret"][: k + 1]
                    LIN.append(dict(classe=cl, venda=SA.NOMES[v], fundo=f, classe_do_fundo=r.tipo, entrada=ent, saida=cm["y"].index[k],
                                    situacao=sit, pregoes=k + 1, resultado_liquido=res, imposto=imp, rendimentos=cm["rend"][k] / cm["custo"],
                                    pior_momento=float(a.min()), pico=float(a.max()),
                                    cdi=RD.cdi_liq(ent, cm["y"].index[k], 1.0) - 1, selic=RD.fase_selic(ent)))
        print(f"{cl} pronto", flush=True)
    O = pd.DataFrame(LIN)

    def q(x):
        return pd.Series({
            "Operações": len(x), "Com lucro": (x["resultado_liquido"] > 0).mean(),
            "Bateram o CDI do mesmo período": (x["resultado_liquido"] > x["cdi"]).mean(),
            "Resultado médio (líquido)": x["resultado_liquido"].mean(), "Resultado mediano": x["resultado_liquido"].median(),
            "Pregões médios": x["pregoes"].mean(),
            "Ganho por mês aplicado": x["resultado_liquido"].sum() / x["pregoes"].sum() * 21,
            "CDI por mês aplicado": x["cdi"].sum() / x["pregoes"].sum() * 21,
            "Perdas de mais de 10%": (x["resultado_liquido"] < -0.10).mean(),
            "Prejuízo e 1 ano parado": ((x["resultado_liquido"] < 0) & (x["situacao"] == "prazo de 1 ano")).mean(),
            "Queda média depois da compra": x["pior_momento"].mean(),
            "Prejuízo com Selic subindo": (x.loc[x["selic"] == "subindo", "resultado_liquido"] < 0).mean(),
            "Prejuízo com Selic parada": (x.loc[x["selic"] == "parada", "resultado_liquido"] < 0).mean(),
            "Prejuízo com Selic caindo": (x.loc[x["selic"] == "caindo", "resultado_liquido"] < 0).mean()})
    R = O.groupby(["classe", "venda"], sort=False).apply(q, include_groups=False).reset_index()
    R["Ganho menos CDI por mês"] = R["Ganho por mês aplicado"] - R["CDI por mês aplicado"]
    for cl in CLASSES:
        x = R[R["classe"] == cl].drop(columns="classe").set_index("venda")
        if len(x):
            print(f"\n===== {cl}")
            print(x[["Operações", "Com lucro", "Bateram o CDI do mesmo período", "Resultado médio (líquido)", "Pregões médios",
                     "Ganho por mês aplicado", "CDI por mês aplicado", "Ganho menos CDI por mês", "Perdas de mais de 10%",
                     "Prejuízo e 1 ano parado"]].to_string(float_format=lambda v: f"{v:,.3f}"))
    M = R.pivot(index="venda", columns="classe", values="Ganho menos CDI por mês")[[c for c in CLASSES if c in R["classe"].unique()]]
    N = R.pivot(index="venda", columns="classe", values="Operações")[M.columns]
    print("\nGANHO MENOS CDI POR MÊS APLICADO (pontos percentuais), por classe e venda")
    print((M * 100).to_string(float_format=lambda v: f"{v:+.2f}"))
    print("\nOPERAÇÕES por classe e venda")
    print(N.to_string(float_format=lambda v: f"{v:.0f}"))
    with pd.ExcelWriter("planilhas/descontado_classes.xlsx") as w:
        R.to_excel(w, sheet_name="Resumo por classe e venda", index=False)
        (M * 100).reset_index().to_excel(w, sheet_name="Ganho menos CDI (p.p. mês)", index=False)
        N.reset_index().to_excel(w, sheet_name="Operações por classe", index=False)
        O.to_excel(w, sheet_name="Operações", index=False)
    print("gravado: planilhas/descontado_classes.xlsx")
