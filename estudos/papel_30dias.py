"""Papel Padrão: os primeiros 30 pregões depois do sinal e o que tem relação com a queda (pedido do dono, 18/11/2026).

Sinais: 5 de maior nota da classe Papel em cada fim de mês (descontado_saudavel.candidatos_v2). Compra de referência:
abertura do pregão seguinte ao sinal. "ret" do dia t = (fechamento + rendimentos com data-com desde a compra) ÷ preço
de compra − 1 (avisos suspeitos ignorados), antes de imposto e taxa. Mercado = planilhas/mercado.csv (índice).
Partes:
  1 caminho dia a dia (1 a 30): média, mediana, % abaixo de 0 / −3% / −5% / −8%; mercado no mesmo dia
  2 menor ret em 30 pregões e em que pregão
  3 relação da queda em 30 pregões (menor ret) e do resultado final (alvo +10%, prazo 1 ano) com: ano, mês do ano,
    cenário do país (Focus − Selic; dívida), mercado nos mesmos 30 pregões, desconto, rendimento, cobertura, queda
    em 6 meses, posição no ranking do mês; e se os fundos do mesmo mês caem juntos
  4 esperar cair 3% / 5% / 8% do preço de referência (fechamento do dia do sinal) em até 60 pregões e comprar na abertura
    seguinte; venda no alvo +10% sobre o novo preço; e o que fizeram os sinais que não caíram isso
Saída: planilhas/papel_30dias.xlsx (todas as tabelas + caminho dia a dia de cada operação).

    PYTHONPATH=. python3 estudos/papel_30dias.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saidas as SA
from estudos.rendimentos_suspeitos import suspeitos

DS, RD, RF, SER = SA.DS, SA.RD, SA.RF, SA.SER
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
B3, IR, ALVO, PRAZO = 0.0003, 0.20, 0.10, 252
MK = pd.read_csv("planilhas/mercado.csv", **OP)
MK["data"] = pd.to_datetime(MK["data"], dayfirst=True)
MK = MK.set_index("data")["indice_mercado"]
MAC = pd.read_csv("planilhas/macro_mensal.csv", **OP)
MAC["mes"] = pd.PeriodIndex(pd.to_datetime("01/" + MAC["mes"], dayfirst=True), freq="M")
MAC = MAC.set_index("mes")


def caminho(f, ent):
    s = SER[f]
    y = s.loc[ent:].iloc[:PRAZO]
    px0 = float(s.loc[ent, "abertura"])
    r = RF.get(f)
    rend = np.zeros(len(y))
    if r is not None:
        rr = r[r["data_base"] >= ent]
        rr = rr[np.array([(f, db) not in suspeitos() for db in rr["data_base"]], dtype=bool)]
        for db, v in rr.groupby("data_base")["valor (R$/cota)"].sum().items():
            k = y.index.searchsorted(db)
            if k < len(y):
                rend[k] += v
    rend = np.cumsum(rend)
    return y, (y["fechamento"].to_numpy(float) + rend) / px0 - 1, px0, rend


def resultado_alvo(y, ret, px0, rend):
    h = np.flatnonzero(ret >= ALVO + 2 * B3)
    if len(h):
        k, sit = h[0], "alvo"
    elif len(y) >= PRAZO:
        k, sit = len(y) - 1, "prazo"
    else:
        return None, None, None
    custo, venda = px0 * (1 + B3), y["fechamento"].iloc[k] * (1 - B3)
    return (venda - IR * max(venda - custo, 0) + rend[k]) / custo - 1, sit, k + 1


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    L, CAM, ESP = [], [], []
    for d in fms:
        C = DS.candidatos_v2(d)
        if C.empty:
            continue
        C = C[C["tipo"] == "Papel"].head(5).reset_index(drop=True)
        for pos, r in C.iterrows():
            f = r["fundo"]
            if f not in SER:
                continue
            s = SER[f]
            z = s.loc[d + pd.Timedelta(days=1):]
            if len(z) < 31:
                continue
            ent = z.index[0]
            y, ret, px0, rend = caminho(f, ent)
            res, sit, preg = resultado_alvo(y, ret, px0, rend)
            m30 = ret[:30]
            mk = MK.reindex(y.index[:30]).ffill()
            mk0 = float(MK.loc[:ent].iloc[-2]) if len(MK.loc[:ent]) > 1 else np.nan
            mes_info = d.to_period("M")
            mac = MAC.loc[:mes_info].iloc[-1]
            L.append(dict(sinal=d, fundo=f, posicao=pos + 1, entrada=ent, ano=ent.year, mes=ent.month, pvp=r["pvp"], rendimento=r["dy"],
                          acima_classe=r["acima_tipo"], cobertura=r["cobertura"], queda_6m_antes=r["queda_6m"], nota=r["nota"],
                          menor_30=float(m30.min()), pregao_do_menor=int(m30.argmin()) + 1, ret_30=float(m30[-1]),
                          mercado_30=float(mk.iloc[-1] / mk0 - 1) if mk0 == mk0 else np.nan,
                          mercado_menor_30=float(mk.min() / mk0 - 1) if mk0 == mk0 else np.nan,
                          focus_menos_selic=mac["mercado espera (focus - selic, pontos)"],
                          divida_12m=mac["divida bruta: variação em 12 meses (pontos)"],
                          resultado_alvo=res, saida=sit, pregoes=preg))
            CAM.append(pd.Series(m30, index=range(1, 31), name=(f, ent)))
            ref = float(s.loc[:d, "fechamento"].iloc[-1])
            for x in (0.03, 0.05, 0.08):
                zz = z.iloc[:60]
                hit = np.flatnonzero(zz["fechamento"].to_numpy(float) <= ref * (1 - x))
                if len(hit) and s.index.get_loc(zz.index[hit[0]]) + 1 < len(s):
                    e2 = s.index[s.index.get_loc(zz.index[hit[0]]) + 1]
                    y2, r2, p2, rd2 = caminho(f, e2)
                    res2, sit2, preg2 = resultado_alvo(y2, r2, p2, rd2)
                    ESP.append(dict(espera=f"cair {x:.0%}", fundo=f, sinal=d, caiu=True, pregao_que_caiu=int(hit[0]) + 1,
                                    resultado=res2, saida=sit2, pregoes=preg2, resultado_se_comprasse_no_sinal=res,
                                    queda_depois_da_2a_compra=float(r2[:30].min())))
                else:
                    ESP.append(dict(espera=f"cair {x:.0%}", fundo=f, sinal=d, caiu=False, resultado=np.nan,
                                    resultado_se_comprasse_no_sinal=res, pregoes_se_comprasse=preg))
    O = pd.DataFrame(L)
    CM = pd.DataFrame(CAM)
    print(f"operações com 30 pregões: {len(O)}")
    # 1 caminho
    P1 = pd.DataFrame({"média": CM.mean(), "mediana": CM.median(), "abaixo de 0": (CM < 0).mean(), "abaixo de −3%": (CM < -0.03).mean(),
                       "abaixo de −5%": (CM < -0.05).mean(), "abaixo de −8%": (CM < -0.08).mean()})
    print("\n1) CAMINHO NOS 30 PRIMEIROS PREGÕES (ret com rendimento)")
    print(P1.iloc[[0, 1, 2, 4, 9, 14, 19, 24, 29]].to_string(float_format=lambda v: f"{v:+.3f}"))
    # 2 menor
    print("\n2) MENOR RET EM 30 PREGÕES")
    print(O["menor_30"].describe(percentiles=[.1, .25, .5, .75, .9]).to_string(float_format=lambda v: f"{v:+.3f}"))
    print("pregão do menor ret:", O["pregao_do_menor"].describe(percentiles=[.25, .5, .75]).round(1).to_dict())
    for x in (0, -0.03, -0.05, -0.08):
        print(f"caíram abaixo de {x:+.0%} em 30 pregões: {(O['menor_30'] < x).mean():.0%}")
    # 3 relações
    def grupo(col, bins=None, labels=None):
        g = O[col] if bins is None else pd.qcut(O[col], 4, duplicates="drop") if bins == "q" else pd.cut(O[col], bins, labels=labels)
        return O.groupby(g, observed=True).agg(operacoes=("fundo", "size"), menor_30_medio=("menor_30", "mean"),
                                                caiu_5pct=("menor_30", lambda s: (s < -0.05).mean()),
                                                mercado_30_medio=("mercado_30", "mean"),
                                                resultado_final_medio=("resultado_alvo", "mean"),
                                                chegou_ao_alvo=("saida", lambda s: (s == "alvo").mean()))
    REL = {"ano": grupo("ano"), "mês do ano": grupo("mes"), "posição no ranking": grupo("posicao"),
           "Focus − Selic": grupo("focus_menos_selic", [-10, -1, 1, 10], ["espera queda forte", "estável", "espera alta"]),
           "dívida 12 meses": grupo("divida_12m", [-50, 2, 50], ["estável ou caindo", "subiu mais de 2 pontos"]),
           "mercado nos 30 pregões": grupo("mercado_30", [-1, -0.03, 0, 0.03, 1], ["caiu mais de 3%", "caiu até 3%", "subiu até 3%", "subiu mais de 3%"]),
           "preço ÷ patrimônio": grupo("pvp", "q"), "rendimento": grupo("rendimento", "q"), "cobertura": grupo("cobertura", "q"),
           "queda em 6 meses antes": grupo("queda_6m_antes", "q")}
    for k, v in REL.items():
        print(f"\n3) {k}")
        print(v.to_string(float_format=lambda x: f"{x:+.3f}"))
    co = O[["menor_30", "ret_30", "mercado_30", "mercado_menor_30", "pvp", "rendimento", "acima_classe", "cobertura", "queda_6m_antes",
            "nota", "focus_menos_selic", "divida_12m", "resultado_alvo"]].corr()[["menor_30", "resultado_alvo"]]
    print("\n3) correlação (−1 a +1)")
    print(co.to_string(float_format=lambda x: f"{x:+.2f}"))
    J = O.groupby("sinal").agg(fundos=("fundo", "size"), cairam_5pct=("menor_30", lambda s: (s < -0.05).sum()), mercado_30=("mercado_30", "first"))
    print(f"\n3) os do mesmo mês caem juntos? meses com 5 fundos: {int((J['fundos'] == 5).sum())}; "
          f"quantos caíram mais de 5% no mesmo mês: {J['cairam_5pct'].value_counts().sort_index().to_dict()}")
    print(f"   correlação entre a queda do fundo e a do mercado nos mesmos 30 pregões: {O['menor_30'].corr(O['mercado_menor_30']):+.2f}")
    # 4 esperar cair
    E = pd.DataFrame(ESP)
    R4 = []
    for e, x in E.groupby("espera", sort=False):
        c, n = x[x["caiu"]], x[~x["caiu"]]
        cf = c.dropna(subset=["resultado"])
        R4.append({"Espera": e, "Sinais": len(x), "Caíram e compraram": len(c), "Pregão em que caiu (mediana)": c["pregao_que_caiu"].median(),
                   "Depois de comprar: queda a mais em 30 pregões (média)": c["queda_depois_da_2a_compra"].mean(),
                   "Resultado das compras (alvo +10%)": cf["resultado"].mean(), "Com lucro": (cf["resultado"] > 0).mean(),
                   "Chegaram ao alvo": (cf["saida"] == "alvo").mean(), "Pregões médios": cf["pregoes"].mean(),
                   "As mesmas, se comprasse no sinal": c["resultado_se_comprasse_no_sinal"].mean(),
                   "Não caíram: resultado se comprasse no sinal (perdido)": n["resultado_se_comprasse_no_sinal"].mean(),
                   "Não caíram: quantos": len(n)})
    R4 = pd.DataFrame(R4)
    print("\n4) ESPERAR CAIR DEPOIS DO SINAL")
    print(R4.set_index("Espera").T.to_string(float_format=lambda v: f"{v:,.3f}"))
    with pd.ExcelWriter("planilhas/papel_30dias.xlsx") as w:
        P1.reset_index().rename(columns={"index": "pregão"}).to_excel(w, sheet_name="1 Caminho dia a dia", index=False)
        O.to_excel(w, sheet_name="Operações", index=False)
        for i, (k, v) in enumerate(REL.items(), 1):
            v.reset_index().astype({v.index.name or "index": str} if v.index.name else {}).to_excel(w, sheet_name=f"3.{i} {k}"[:31], index=False)
        co.reset_index().to_excel(w, sheet_name="3 Correlações", index=False)
        J.reset_index().to_excel(w, sheet_name="3 Mesmo mês", index=False)
        R4.to_excel(w, sheet_name="4 Esperar cair", index=False)
        E.to_excel(w, sheet_name="4 Esperar cair - operações", index=False)
        CM.reset_index(drop=True).assign(fundo=[i[0] for i in CM.index], entrada=[i[1] for i in CM.index]).to_excel(
            w, sheet_name="Caminho de cada operação", index=False)
    print("gravado: planilhas/papel_30dias.xlsx")
