"""Tipo 1 — Descontado saudável com rendimento constante (Skill `descontado-saudavel`). Regras fixadas em 18/11/2026,
ANTES de rodar (docs/FILTRO_DESCONTADOS.md + régua do Focus). Não ajustar depois de ver o resultado.

Entrada (revisão no último pregão de cada mês, só com dado publicado até o dia):
  1  patrimônio >= R$ 100 mi
  2  negociação típica (mediana de 60 pregões) >= R$ 250 mil/dia
  3  sem amortização relevante em 12 meses; sem bloqueio do Kairi (liquidação, incorporação, fusão, cisão, venda de todos
     os ativos, ida para o balcão)
  4  cota caiu de 10% a 25% em 6 meses (queda maior é terreno do Kairi)
  5  preço entre 0,60 e 0,90 do patrimônio
  6  patrimônio por cota não caiu mais de 5% em 12 meses
  7  rendimento do ano sobre o preço >= mediana do próprio tipo de fundo + 2 pontos
  7b rendimento do ano sobre o preço >= Selic esperada para o fim do ano seguinte (Focus, mediana) × 0,825 (líquida de IR)
  8  constância em 12 meses: pagou em pelo menos 11 meses; no máximo 1 mês com queda de mais de 2%; oscilação
     (desvio ÷ média) <= 0,03; média dos 3 últimos meses >= média dos 3 primeiros
  9  cobertura do rendimento (estudos/cobertura_rendimento.py) >= 1,0; fundo sem a medida não entra
  10 avaliação de saúde (estudos/saude_fundo.py) diferente de NÃO COMPRAR
Nota: média das posições em (rendimento − mediana do tipo), desconto e oscilação. Até 5 fundos, partes iguais do caixa.
Compra na abertura do 1º pregão do mês seguinte. Caixa em 105% do CDI (IR aproximado de 17,5%).
Saída (decidida na revisão, executada na abertura seguinte):
  a  doença confirmada em 2 revisões seguidas (renda_descontada.doente)
  b  corte de rendimento: rendimento do último mês mais de 5% abaixo do mês anterior
  c  preço >= 0,95 do patrimônio
Custos: 0,03% por operação; imposto de 20% sobre ganho de venda do mês, prejuízo abatendo; rendimento isento.
Medidas: período completo, 2018–2022 e 2023–11/2026 (período de conferência). Cada operação comparada com 105% do CDI
líquido no mesmo intervalo.

    PYTHONPATH=. python3 estudos/descontado_saudavel.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

import estudos.renda_descontada as RD
from estudos.cobertura_rendimento import cobertura
from estudos.saude_fundo import saude

with contextlib.redirect_stdout(io.StringIO()):
    _G = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="biblioteca")["simular"].__globals__
BLOQUEIO = _G["bloqueio"]

FOC = pd.read_csv("planilhas/focus_selic_fim_de_ano.csv", sep=";", decimal=",", encoding="utf-8-sig")
FOC["data_coleta"] = pd.to_datetime(FOC["data_coleta"], dayfirst=True)
FOC = FOC[FOC["base_calculo"] == 0]
P, PF, RF, TIPO = RD.P, RD.PF, RD.RF, RD.TIPO
B3, IR_FII, IR_CX, N = 0.0003, 0.20, 0.175, 5
CORTE_PERIODO = pd.Timestamp("2023-01-01")


def focus_selic(d):
    """Mediana do Focus (última coleta até d) para a Selic no fim do ano seguinte, em fração."""
    x = FOC[(FOC["data_coleta"] <= d) & (FOC["ano_referencia"] == d.year + 1)]
    return float(x.sort_values("data_coleta")["mediana (%)"].iloc[-1]) / 100 if len(x) else np.nan


def meses_rend(f, d):
    r = RF.get(f)
    if r is None:
        return None
    r = r[(r["data_base"] <= d) & (r["data_base"] > d - pd.Timedelta(days=365))]
    return r.groupby(r["data_base"].dt.to_period("M"))["valor (R$/cota)"].sum()


def constancia(f, d):
    m = meses_rend(f, d)
    if m is None or len(m) < 11:
        return None
    v = m.to_numpy(float)
    var = v[1:] / v[:-1] - 1
    return dict(meses=len(v), quedas2=int((var < -0.02).sum()), osc=float(v.std() / v.mean()),
                tend=float(v[-3:].mean() / v[:3].mean() - 1))


def queda6(f, d):
    s = PF[f].loc[:d, "fechamento"]
    a = s.loc[:d - pd.DateOffset(months=6)]
    return float(s.iloc[-1] / a.iloc[-1] - 1) if len(a) else np.nan


FUNIL = []


def candidatos(d, registrar=False):
    x = P[P["data"] == d]
    x = x.assign(tipo=x["fundo"].map(TIPO).fillna("Outros"))
    x = x[x["rendimento_ano_sobre_preco (%)"] > 0]
    med = x[(x["patrimonio (R$)"] >= 100e6) & (x["mediana60"] >= 250e3)].groupby("tipo")["rendimento_ano_sobre_preco (%)"].median()
    fs = focus_selic(d) * 0.825
    etapas = {}

    def passa(nome, df):
        etapas[nome] = len(df)
        return df
    x = passa("1-2 tamanho e negociação", x[(x["patrimonio (R$)"] >= 100e6) & (x["mediana60"] >= 250e3)])
    x = passa("3a sem amortização", x[x["amortizacao_12m (1/0)"] == 0])
    x = x.assign(q6=[queda6(f, d) for f in x["fundo"]])
    x = passa("4 queda de 10% a 25% em 6 meses", x[x["q6"].between(-0.25, -0.10)])
    x = passa("5 preço 0,60–0,90 do patrimônio", x[x["preco_sobre_valor_patrimonial"].between(0.60, 0.90)])
    x = passa("6 patrimônio por cota >= -5%", x[x["vp12"] >= -0.05])
    x = x.assign(acima_tipo=x["rendimento_ano_sobre_preco (%)"] - x["tipo"].map(med))
    x = passa("7 rendimento >= tipo + 2", x[x["acima_tipo"] >= 2])
    x = passa("7b rendimento >= Focus líquido", x[x["rendimento_ano_sobre_preco (%)"] / 100 >= fs])
    L = []
    for r in x.itertuples():
        L.append((r, constancia(r.fundo, d)))
    L = [(r, c) for r, c in L if c and c["quedas2"] <= 1 and c["osc"] <= 0.03 and c["tend"] >= 0]
    etapas["8 constância"] = len(L)
    L2 = []
    for r, c in L:
        cb = cobertura(r.fundo, d)
        if cb is None or cb["cobertura"] < 1.0:
            continue
        L2.append((r, c, cb))
    etapas["9 cobertura >= 1,0"] = len(L2)
    L3 = []
    for r, c, cb in L2:
        if BLOQUEIO(r.fundo, d):
            continue
        sv = saude(r.fundo, d)
        if sv["veredito"] == "NÃO COMPRAR":
            continue
        L3.append(dict(fundo=r.fundo, tipo=r.tipo, preco=r.fechamento, pvp=r.preco_sobre_valor_patrimonial,
                       queda_6m=r.q6, vp_12m=r.vp12, acima_tipo=r.acima_tipo / 100, focus_liq=fs, oscilacao=c["osc"],
                       quedas_2pct=c["quedas2"], tendencia=c["tend"], cobertura=cb["cobertura"], janela_cvm=cb["janela"],
                       saude=sv["veredito"]))
    etapas["3b-10 sem bloqueio e saúde"] = len(L3)
    if registrar:
        FUNIL.append(dict(dia=d, **etapas))
    C = pd.DataFrame(L3)
    if C.empty:
        return C
    C["dy"] = [float(P[(P["data"] == d) & (P["fundo"] == f)]["rendimento_ano_sobre_preco (%)"].iloc[0]) / 100 for f in C["fundo"]]
    C["nota"] = (C["acima_tipo"].rank(ascending=False) + C["pvp"].rank() + C["oscilacao"].rank()) / 3
    return C.sort_values("nota").reset_index(drop=True)


def corte(f, d):
    m = meses_rend(f, d)
    return m is not None and len(m) >= 2 and m.iloc[-1] < 0.95 * m.iloc[-2]


def rodar():
    caixa, pos, ops, ganhos, pool = 10000.0, {}, [], {}, 0.0
    serie, ult, plano, alerta = {}, None, None, {}
    rev = set(RD.FIM_MES)
    for d in RD.DIAS:
        if ult is not None:
            caixa *= 1 + (RD.I105.loc[:d].iloc[-1] / RD.I105.loc[:ult].iloc[-1] - 1) * (1 - IR_CX)
        prev, ult = ult, d
        for f, p in pos.items():
            r = RF.get(f)
            if r is not None:
                pg = r[(r["data_pagamento"] <= d) & (r["data_pagamento"] > (prev if prev is not None else d))
                       & (r["data_base"] >= p["entrada"])]
                v = float(pg["valor (R$/cota)"].sum()) * p["cotas"]
                caixa += v
                p["rend"] += v
        if plano is not None:
            vendas, compras = plano
            for f, mot in vendas:
                px = RD.preco(f, d, "abertura")
                p = pos.pop(f)
                v = p["cotas"] * px * (1 - B3)
                caixa += v
                ganhos[(d.year, d.month)] = ganhos.get((d.year, d.month), 0.0) + v - p["custo"]
                ops.append(dict(fundo=f, entrada=p["entrada"], saida=d, motivo=mot, custo=p["custo"], venda=v, rendimentos=p["rend"],
                                resultado=v - p["custo"] + p["rend"], resultado_pct=(v - p["custo"] + p["rend"]) / p["custo"],
                                cdi_pct=RD.cdi_liq(p["entrada"], d, 1.0) - 1, em_aberto=False))
            vagas = N - len(pos)
            alvo = caixa / vagas if vagas else 0
            for f in compras[:vagas]:
                px = RD.preco(f, d, "abertura")
                cot = int(alvo / (px * (1 + B3))) if px > 0 else 0
                if cot <= 0:
                    continue
                custo = cot * px * (1 + B3)
                caixa -= custo
                pos[f] = dict(cotas=cot, custo=custo, entrada=d, rend=0.0)
            plano = None
        if d in rev:
            ant = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
            if ant in ganhos:
                g = ganhos.pop(ant)
                if g >= 0:
                    usa = min(pool, g)
                    pool -= usa
                    caixa -= IR_FII * (g - usa)
                else:
                    pool += -g
            C = candidatos(d, registrar=True)
            vendas = []
            for f in pos:
                mot = RD.doente(f, d)
                alerta[f] = alerta.get(f, 0) + 1 if mot else 0
                if mot and alerta[f] >= 2:
                    vendas.append((f, mot + " (2 meses seguidos)"))
                elif corte(f, d):
                    vendas.append((f, "corte de rendimento de mais de 5%"))
                elif PF[f].loc[:d, "preco_sobre_valor_patrimonial"].iloc[-1] >= 0.95:
                    vendas.append((f, "preço chegou a 0,95 do patrimônio"))
            fica = [f for f in pos if f not in {v[0] for v in vendas}]
            compras = [f for f in C["fundo"] if f not in fica][: N - len(fica)] if len(C) else []
            plano = (vendas, compras)
        serie[d] = caixa + sum(p["cotas"] * RD.preco(f, d) for f, p in pos.items())
    S = pd.Series(serie)
    fim = S.index[-1]
    for f, p in pos.items():
        v = p["cotas"] * RD.preco(f, fim)
        ops.append(dict(fundo=f, entrada=p["entrada"], saida=fim, motivo="em aberto", custo=p["custo"], venda=v, rendimentos=p["rend"],
                        resultado=v - p["custo"] + p["rend"], resultado_pct=(v - p["custo"] + p["rend"]) / p["custo"],
                        cdi_pct=RD.cdi_liq(p["entrada"], fim, 1.0) - 1, em_aberto=True))
    return S, pd.DataFrame(ops)


def resumo(S, O, ini, fim, nome):
    s = S[(S.index >= ini) & (S.index <= fim)]
    base = S[S.index < ini].iloc[-1] if (S.index < ini).any() else 10000.0
    i0 = S[S.index < ini].index[-1] if (S.index < ini).any() else S.index[0]
    anos = (s.index[-1] - i0).days / 365.25
    ret = s.iloc[-1] / base - 1
    cdi = RD.cdi_liq(i0, s.index[-1], 1.0) - 1
    curva = pd.concat([pd.Series({i0: base}), s])
    o = O[(O["entrada"] >= ini) & (O["entrada"] <= fim)]
    exc = (o["resultado_pct"] - o["cdi_pct"]).to_numpy()
    t = exc.mean() / (exc.std(ddof=1) / np.sqrt(len(exc))) if len(exc) > 2 and exc.std(ddof=1) > 0 else np.nan
    rng = np.random.default_rng(1)
    boot = [rng.choice(exc, len(exc)).mean() for _ in range(5000)] if len(exc) > 2 else []
    return {"Período": nome, "Operações (fechadas)": int((~o["em_aberto"]).sum()), "Operações (abertas)": int(o["em_aberto"].sum()),
            "Com lucro": (o["resultado"] > 0).mean() if len(o) else np.nan,
            "Bateram o CDI": (o["resultado_pct"] > o["cdi_pct"]).mean() if len(o) else np.nan,
            "Resultado médio por operação": o["resultado_pct"].mean() if len(o) else np.nan,
            "Pior operação": o["resultado_pct"].min() if len(o) else np.nan,
            "Carteira: retorno": ret, "Carteira: ao ano": (1 + ret) ** (1 / anos) - 1, "105% CDI líquido: retorno": cdi,
            "105% CDI líquido: ao ano": (1 + cdi) ** (1 / anos) - 1, "Maior queda da carteira": float((curva / curva.cummax() - 1).min()),
            "Dias médios por operação": float((o["saida"] - o["entrada"]).dt.days.mean()) if len(o) else np.nan,
            "Excesso médio sobre o CDI por operação": exc.mean() if len(exc) else np.nan, "t do excesso": t,
            "Chance de o excesso ser <= 0 (reamostragem)": float(np.mean(np.array(boot) <= 0)) if len(boot) else np.nan}


def diagnostico(d):
    """Fundos que passam nas regras 1 a 3 no dia d: valor de cada medida e a primeira regra em que param."""
    x = P[P["data"] == d]
    x = x.assign(tipo=x["fundo"].map(TIPO).fillna("Outros"))
    x = x[(x["rendimento_ano_sobre_preco (%)"] > 0) & (x["patrimonio (R$)"] >= 100e6) & (x["mediana60"] >= 250e3)
          & (x["amortizacao_12m (1/0)"] == 0)]
    med = x.groupby("tipo")["rendimento_ano_sobre_preco (%)"].median()
    fs = focus_selic(d) * 0.825
    L = []
    for r in x.itertuples():
        c = constancia(r.fundo, d) or {}
        cb = cobertura(r.fundo, d)
        q6 = queda6(r.fundo, d)
        dy = float(x.loc[r.Index, "rendimento_ano_sobre_preco (%)"]) / 100
        ac = dy - med[r.tipo] / 100
        regras = [("4 queda 10–25% em 6 meses", -0.25 <= q6 <= -0.10), ("5 preço 0,60–0,90", 0.60 <= r.preco_sobre_valor_patrimonial <= 0.90),
                  ("6 patrimônio/cota >= -5%", r.vp12 >= -0.05), ("7 rendimento >= tipo + 2", ac >= 0.02), ("7b rendimento >= Focus líquido", dy >= fs),
                  ("8 constância", bool(c) and c["quedas2"] <= 1 and c["osc"] <= 0.03 and c["tend"] >= 0),
                  ("9 cobertura >= 1,0", cb is not None and cb["cobertura"] >= 1.0)]
        para = next((n for n, ok in regras if not ok), None)
        if para is None:
            sv = saude(r.fundo, d)["veredito"]
            para = "bloqueio do Kairi" if BLOQUEIO(r.fundo, d) else ("10 saúde: NÃO COMPRAR" if sv == "NÃO COMPRAR" else "PASSA EM TUDO")
        L.append(dict(fundo=r.fundo, tipo=r.tipo, queda_6m=q6, pvp=r.preco_sobre_valor_patrimonial, vp_12m=r.vp12, rendimento_ano=dy,
                      acima_do_tipo=ac, regua_focus=fs, meses_pagos=c.get("meses"), quedas_de_2pct=c.get("quedas2"),
                      oscilacao=c.get("osc"), tendencia=c.get("tend"), cobertura=cb["cobertura"] if cb else np.nan,
                      regras_que_passa=sum(ok for _, ok in regras), parou_em=para))
    return pd.DataFrame(L).sort_values(["regras_que_passa", "rendimento_ano"], ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    S, O = rodar()
    # exposição média: parte do patrimônio aplicada em fundos
    R = pd.DataFrame([resumo(S, O, pd.Timestamp("2018-01-01"), pd.Timestamp("2022-12-31"), "2018–2022 (escolha)"),
                      resumo(S, O, CORTE_PERIODO, S.index[-1], "2023–11/2026 (conferência)"),
                      resumo(S, O, pd.Timestamp("2018-01-01"), S.index[-1], "Completo 2018–11/2026")])
    print(f"Valor final: R$ {S.iloc[-1]:,.2f}  |  105% CDI líquido: R$ {RD.cdi_liq(RD.DIAS[0], RD.DIAS[-1]):,.2f}")
    print(R.T.to_string(header=False, float_format=lambda v: f"{v:,.3f}"))
    print("\nOPERAÇÕES")
    print(O.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    F = pd.DataFrame(FUNIL)
    print("\nFUNIL (média de fundos por revisão mensal)")
    print(F.drop(columns="dia").mean().to_string(float_format=lambda v: f"{v:,.1f}"))
    hoje = RD.DIAS[-1]
    C = candidatos(hoje)
    print(f"\nFocus (fim de {hoje.year + 1}) em {hoje:%d/%m/%Y}: {focus_selic(hoje):.2%}; régua líquida {focus_selic(hoje) * 0.825:.2%}")
    print(f"ELEGÍVEIS EM {hoje:%d/%m/%Y}: {len(C)}")
    if len(C):
        print(C.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    DG = diagnostico(hoje)
    print("\nHOJE: ONDE CADA FUNDO PAROU (os 25 mais perto de passar)")
    print(DG.head(25).to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print(DG["parou_em"].value_counts().to_string())
    with pd.ExcelWriter("planilhas/descontado_saudavel.xlsx") as w:
        R.to_excel(w, sheet_name="Resumo", index=False)
        O.to_excel(w, sheet_name="Operações", index=False)
        S.rename("patrimonio").to_frame().to_excel(w, sheet_name="Patrimônio dia a dia")
        F.to_excel(w, sheet_name="Funil por revisão", index=False)
        C.to_excel(w, sheet_name="Elegíveis hoje", index=False)
        DG.to_excel(w, sheet_name="Hoje - onde cada fundo parou", index=False)
    print("gravado: planilhas/descontado_saudavel.xlsx")
