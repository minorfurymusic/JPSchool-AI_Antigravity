"""Estratégia "Renda descontada saudável" (brainstorm do dono, 2026-11-17): carteira de R$ 10 mil em 5 fundos que pagam
bem acima do CDI, com desconto sobre o patrimônio e rendimento constante, escolhidos por nota e revistos todo mês.

Regras (no último pregão de cada mês, só com dados até esse dia):
  Elegível: patrimônio >= R$ 100 mi; negociação típica (mediana de 60 pregões) >= R$ 250 mil; preço/patrimônio de 0,60 a 0,85;
            rendimento do ano sobre o preço >= CDI + 1 ponto; rendimento constante em 12 meses (tendência >= -10%,
            no máximo 2 cortes, oscilação <= 0,15); patrimônio por cota em 12 meses >= -5%; avaliação de saúde != NÃO COMPRAR.
  Nota: média das posições (ranking) em diferença sobre o CDI, desconto, constância do rendimento e patrimônio por cota.
  Carteira: 5 fundos de pesos iguais. Um fundo sai quando deixa de ser elegível, cai para fora dos 15 de maior nota ou
            (variante "preço justo") quando o preço chega a 0,95 do patrimônio ou o rendimento cai para o nível do CDI.
  Entra o melhor da nota no lugar, na abertura do primeiro pregão do mês seguinte. Rendimentos entram no caixa no dia do
  pagamento e são reinvestidos na revisão seguinte. Caixa parado: 105% do CDI com IR aproximado de 17,5%.
  Custos: 0,03% por operação; imposto de 20% sobre o ganho de venda do mês, com prejuízo abatendo.
Comparações: 105% do CDI líquido (IR regressivo) e índice de mercado (só preço). Retorno por ano e por tipo de ano
(anos de onda do Kairi 2020, 2021, 2024 contra os demais). Lista dos 5 fundos de hoje (último pregão da base).

    PYTHONPATH=. python3 estudos/renda_descontada.py
"""
import re

import numpy as np
import pandas as pd

from estudos.cobertura_rendimento import LIMITE as LIM_COB, cobertura as _cob
from estudos.saude_fundo import NEGATIVOS, _sem_acento, saude

OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
P = pd.concat([pd.read_csv(f"planilhas/precos_{a}.csv", **OP) for a in range(2016 + 1, 2027)])
P["data"] = pd.to_datetime(P["data"], dayfirst=True)
P = P.sort_values(["fundo", "data"])
P["mediana60"] = P.groupby("fundo")["volume_dia (R$)"].transform(lambda s: s.rolling(60, min_periods=40).median())
P["vp12"] = P.groupby("fundo")["valor_patrimonial_cota"].transform(lambda s: s / s.shift(252) - 1)
PF = {f: x.set_index("data") for f, x in P.groupby("fundo")}
R = pd.read_csv("planilhas/rendimentos_pagamentos.csv", **OP)
for c in ("data_base", "data_pagamento"):
    R[c] = pd.to_datetime(R[c], dayfirst=True)
R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
R["data_pagamento"] = R["data_pagamento"].fillna(R["data_base"] + pd.Timedelta(days=11))
RF = {f: x.sort_values("data_base") for f, x in R.groupby("fundo")}
CDI = pd.read_csv("planilhas/cdi.csv", **OP)
CDI["data"] = pd.to_datetime(CDI["data"], dayfirst=True)
CDI = CDI.set_index("data")
I105 = CDI["indice_105_do_cdi"]
CDI_ANO = CDI["cdi_ao_ano (%)"] / 100
MK = pd.read_csv("planilhas/mercado.csv", **OP)
MK["data"] = pd.to_datetime(MK["data"], dayfirst=True)
SELIC = MK.set_index("data")["selic_ano (%)"] / 100
MK = MK.set_index("data")["indice_mercado"]
TIPO = pd.read_csv("planilhas/fundos.csv", sep=";", encoding="utf-8-sig").set_index("fundo")["tipo"].to_dict()


def fase_selic(d):
    """Fase da Selic no dia: comparada com 90 dias antes."""
    a, b = float(SELIC.loc[:d].iloc[-1]), float(SELIC.loc[:d - pd.Timedelta(days=90)].iloc[-1])
    return "subindo" if a > b + 1e-9 else "caindo" if a < b - 1e-9 else "parada"
DIAS = sorted(P["data"].unique())
DIAS = [pd.Timestamp(d) for d in DIAS if pd.Timestamp(d) >= pd.Timestamp("2018-01-02")]
FIM_MES = pd.Series(DIAS).groupby(pd.Series(DIAS).dt.to_period("M")).max().tolist()
B3, IR_FII, IR_CX = 0.0003, 0.20, 0.175
ONDA = {2020, 2021, 2024}


def constancia(f, d):
    r = RF.get(f)
    if r is None:
        return None
    r = r[(r["data_base"] <= d) & (r["data_base"] > d - pd.Timedelta(days=365))]
    v = r.groupby(r["data_base"].dt.to_period("M"))["valor (R$/cota)"].sum().to_numpy(float)
    if len(v) < 10:
        return None
    var = v[1:] / v[:-1] - 1
    return dict(tend=v[-3:].mean() / v[:3].mean() - 1, cortes=int((var < -0.05).sum()), osc=v.std() / v.mean())


_FNET17 = None


def negativos_fnet(f, d):
    """Fatos relevantes e comunicados do FNET 2017-2026 (planilhas/tecnico/fnet_2017_documentos.csv.gz, só os fundos
    baixados) dos 12 meses anteriores com as mesmas palavras de saude_fundo.NEGATIVOS."""
    global _FNET17
    if _FNET17 is None:
        try:
            X = pd.read_csv("planilhas/tecnico/fnet_2017_documentos.csv.gz", sep=";", encoding="utf-8-sig")
            X["dia"] = pd.to_datetime(X["data de entrega"].astype(str).str[:10], dayfirst=True, errors="coerce")
            X["t"] = X["texto completo"].fillna("").map(_sem_acento)
            _FNET17 = {k: v for k, v in X.groupby("fundo")}
        except FileNotFoundError:
            _FNET17 = {}
    x = _FNET17.get(f)
    if x is None:
        return []
    x = x[(x["dia"] <= d) & (x["dia"] > d - pd.DateOffset(months=12))]
    out = []
    for r in x.itertuples():
        for nome, pad in NEGATIVOS:
            if re.search(pad, r.t):
                out.append(f"{r.dia:%d/%m/%Y} FNET {r.categoria}: {nome}")
                break
    return out


SAUDE = {}
BARRADOS = []      # (dia, fundo, motivo) barrados pelos filtros novos de 17/11/2026
VISTOS = set()     # fundos que passaram nos filtros da versão D em algum fim de mês


def candidatos(d, relativo=False, filtro_cob=False, filtro_docs=False):
    x = P[P["data"] == d]
    cdi = float(CDI_ANO.loc[:d].iloc[-1])
    x = x[(x["patrimonio (R$)"] >= 100e6) & (x["mediana60"] >= 250e3) & (x["rendimento_ano_sobre_preco (%)"] > 0)]
    if relativo:     # rendimento pelo menos 2 pontos acima da mediana do próprio tipo de fundo no dia
        x = x.assign(tipo=x["fundo"].map(TIPO).fillna("Outros"))
        med = x.groupby("tipo")["rendimento_ano_sobre_preco (%)"].transform("median")
        x = x[x["rendimento_ano_sobre_preco (%)"] >= med + 2]
    else:
        x = x[x["rendimento_ano_sobre_preco (%)"] / 100 >= cdi + 0.01]
    x = x[x["preco_sobre_valor_patrimonial"].between(0.60, 0.85) & (x["vp12"] >= -0.05)]
    L = []
    x = x.rename(columns={"rendimento_ano_sobre_preco (%)": "dyp"})
    for r in x.itertuples():
        c = constancia(r.fundo, d)
        if c is None or c["tend"] < -0.10 or c["cortes"] > 2 or c["osc"] > 0.15:
            continue
        k = (r.fundo, d)
        if k not in SAUDE:
            SAUDE[k] = saude(r.fundo, d)["veredito"]
        if SAUDE[k] == "NÃO COMPRAR":
            continue
        VISTOS.add(r.fundo)
        if filtro_cob:
            cb = _cob(r.fundo, d)
            if cb is not None and cb["cobertura"] < LIM_COB:
                BARRADOS.append((d, r.fundo, f"cobertura {cb['cobertura']:.2f}"))
                continue
        if filtro_docs:
            neg = saude(r.fundo, d)["docs_negativos"] + negativos_fnet(r.fundo, d)
            if neg:
                BARRADOS.append((d, r.fundo, "documento negativo: " + neg[-1][:120]))
                continue
        L.append(dict(fundo=r.fundo, dy=r.dyp / 100,
                      pvp=r.preco_sobre_valor_patrimonial, vp12=r.vp12, osc=c["osc"], tend=c["tend"], preco=r.fechamento))
    C = pd.DataFrame(L)
    if C.empty:
        return C
    C["spread"] = C["dy"] - cdi
    C["nota"] = (C["spread"].rank(ascending=False) + C["pvp"].rank() + C["osc"].rank() + C["vp12"].rank(ascending=False)) / 4
    return C.sort_values("nota").reset_index(drop=True)


def preco(f, d, col="fechamento"):
    x = PF[f].loc[:d]
    return float(x[col].iloc[-1]) if len(x) else np.nan


def abertura_seguinte(f, d):
    x = PF[f].loc[d + pd.Timedelta(days=1):]
    x = x[x["negociou (1/0)"] == 1]
    return (x.index[0], float(x["abertura"].iloc[0])) if len(x) else (None, np.nan)


def doente(f, d):
    """Fundo em carteira adoeceu? rendimento caindo > 15% ou 3+ cortes em 12 meses, patrimônio por cota -5% em 12 meses,
    ou avaliação de saúde NÃO COMPRAR."""
    c = constancia(f, d)
    if c is not None and (c["tend"] < -0.15 or c["cortes"] >= 3):
        return "rendimento caindo"
    v = PF[f].loc[:d, "vp12"].dropna()
    if len(v) and v.iloc[-1] < -0.05:
        return "patrimônio por cota caindo"
    k = (f, d)
    if k not in SAUDE:
        SAUDE[k] = saude(f, d)["veredito"]
    return "avaliação de saúde: não comprar" if SAUDE[k] == "NÃO COMPRAR" else None


def rodar(preco_justo=False, n=5, segurar=False, v2=False, selic=False, relativo=False, filtro_cob=False, filtro_docs=False):
    """v2: doença só vende se confirmada em 2 revisões seguidas; preço justo só por preço >= 0,95 do patrimônio.
    selic: não compra quando a Selic está subindo. relativo: rendimento comparado com o próprio tipo de fundo."""
    alerta = {}
    caixa, pos, ops, ganhos, pool, pend_ir = 10000.0, {}, [], {}, 0.0, 0.0
    serie, ult = {}, None
    rev = set(FIM_MES)
    plano = None                     # decisões da revisão, executadas na abertura seguinte
    for d in DIAS:
        if ult is not None:          # caixa rende 105% do CDI (IR aproximado)
            caixa *= 1 + (I105.loc[:d].iloc[-1] / I105.loc[:ult].iloc[-1] - 1) * (1 - IR_CX)
        prev, ult = ult, d
        for f, p in pos.items():     # rendimentos pagos hoje (data-base desde a compra)
            r = RF.get(f)
            if r is not None:
                pg = r[(r["data_pagamento"] <= d) & (r["data_pagamento"] > (prev if prev is not None else d - pd.Timedelta(days=1)))
                       & (r["data_base"] >= p["entrada"])]
                caixa += float(pg["valor (R$/cota)"].sum()) * p["cotas"]
                p["rend"] += float(pg["valor (R$/cota)"].sum()) * p["cotas"]
        if plano is not None:        # executa vendas e compras decididas no fim do mês anterior
            vendas, compras = plano
            for f, mot in vendas:
                dt, px = abertura_seguinte(f, d - pd.Timedelta(days=1))
                if dt is None or dt != d:
                    px = preco(f, d)
                p = pos.pop(f)
                v = p["cotas"] * px * (1 - B3)
                caixa += v
                m = (d.year, d.month)
                ganhos[m] = ganhos.get(m, 0.0) + v - p["custo"]
                ops.append(dict(fundo=f, entrada=p["entrada"], saida=d, motivo=mot, custo=p["custo"], venda=v, rendimentos=p["rend"],
                                resultado=v - p["custo"] + p["rend"], resultado_pct=(v - p["custo"] + p["rend"]) / p["custo"]))
            vagas = n - len(pos)
            alvo = caixa / vagas if vagas else 0
            for f in compras[:vagas]:
                px = preco(f, d, "abertura")
                cot = int(alvo / (px * (1 + B3)))
                if cot <= 0:
                    continue
                custo = cot * px * (1 + B3)
                caixa -= custo
                pos[f] = dict(cotas=cot, custo=custo, entrada=d, rend=0.0)
            plano = None
        # imposto de venda: paga no fim do mês seguinte
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
            C = candidatos(d, relativo, filtro_cob, filtro_docs)
            top15 = set(C["fundo"].head(15)) if len(C) else set()
            vendas = []
            for f in pos:
                if segurar and v2:
                    mot = doente(f, d)
                    alerta[f] = alerta.get(f, 0) + 1 if mot else 0
                    mot = mot + " (2 meses seguidos)" if mot and alerta[f] >= 2 else None
                    if mot is None and preco_justo and PF[f].loc[:d, "preco_sobre_valor_patrimonial"].iloc[-1] >= 0.95:
                        mot = "preço justo atingido"
                    if mot:
                        vendas.append((f, mot))
                    continue
                if segurar:
                    mot = doente(f, d)
                    if mot is None and preco_justo:
                        pv = PF[f].loc[:d, "preco_sobre_valor_patrimonial"].iloc[-1]
                        dy = PF[f].loc[:d, "rendimento_ano_sobre_preco (%)"].iloc[-1] / 100
                        if pv >= 0.95 or dy <= float(CDI_ANO.loc[:d].iloc[-1]):
                            mot = "preço justo atingido"
                    if mot:
                        vendas.append((f, mot))
                    continue
                if f not in top15:
                    mot = "saiu do grupo dos 15 melhores ou deixou de ser elegível"
                    if preco_justo:
                        pv = PF[f].loc[:d, "preco_sobre_valor_patrimonial"].iloc[-1]
                        dy = PF[f].loc[:d, "rendimento_ano_sobre_preco (%)"].iloc[-1] / 100
                        if pv >= 0.95 or dy <= float(CDI_ANO.loc[:d].iloc[-1]):
                            mot = "preço justo atingido"
                    vendas.append((f, mot))
                elif preco_justo:
                    pv = PF[f].loc[:d, "preco_sobre_valor_patrimonial"].iloc[-1]
                    if pv >= 0.95:
                        vendas.append((f, "preço justo atingido"))
            fica = [f for f in pos if f not in {v[0] for v in vendas}]
            compras = [f for f in C["fundo"] if f not in fica][: n - len(fica)] if len(C) else []
            if selic and fase_selic(d) == "subindo":
                compras = []
            plano = (vendas, compras)
        serie[d] = caixa + sum(p["cotas"] * preco(f, d) for f, p in pos.items())
    S = pd.Series(serie)
    aberto = [dict(fundo=f, entrada=p["entrada"], custo=p["custo"], valor=p["cotas"] * preco(f, S.index[-1]), rendimentos=p["rend"]) for f, p in pos.items()]
    return S, pd.DataFrame(ops), pd.DataFrame(aberto)


def cdi_liq(ini, fim, valor=10000.0):
    dias = (fim - ini).days
    ir = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
    return valor * (1 + (I105.loc[:fim].iloc[-1] / I105.loc[:ini].iloc[-1] - 1) * (1 - ir))


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    VAR = [("A. Segurar; adoecer ou preço justo (anterior)", dict(preco_justo=True, segurar=True)),
           ("B. A + saídas corrigidas", dict(preco_justo=True, segurar=True, v2=True)),
           ("C. B + não compra com Selic subindo", dict(preco_justo=True, segurar=True, v2=True, selic=True)),
           ("D. B + rendimento comparado ao tipo de fundo", dict(preco_justo=True, segurar=True, v2=True, relativo=True)),
           ("E. C + rendimento comparado ao tipo de fundo", dict(preco_justo=True, segurar=True, v2=True, selic=True, relativo=True)),
           # filtros novos de 17/11/2026, regras fixadas antes de rodar (estudos/cobertura_rendimento.py e saude_fundo.NEGATIVOS)
           ("F. D + cobertura do rendimento >= 0,90", dict(preco_justo=True, segurar=True, v2=True, relativo=True, filtro_cob=True)),
           ("G. D + sem documento negativo em 12 meses", dict(preco_justo=True, segurar=True, v2=True, relativo=True, filtro_docs=True)),
           ("H. D + cobertura + sem documento negativo", dict(preco_justo=True, segurar=True, v2=True, relativo=True, filtro_cob=True,
                                                             filtro_docs=True))]
    SAI, RES, FASE, BAR = {}, [], [], {}
    for nome, kw in VAR:
        BARRADOS.clear()
        S, O, A = rodar(**kw)
        BAR[nome] = pd.DataFrame(BARRADOS, columns=["dia", "fundo", "motivo"])
        anos = {}
        for a in range(2018, 2027):
            s_ = S[S.index.year == a]
            ini = S[S.index.year < a].iloc[-1] if a > 2018 else 10000.0
            i0 = S[S.index.year < a].index[-1] if a > 2018 else S.index[0]
            anos[a] = dict(carteira=s_.iloc[-1] / ini - 1, cdi_liq=cdi_liq(i0, s_.index[-1], 1.0) - 1)
        T = pd.DataFrame(anos).T
        # retorno mês a mês por fase da Selic no início do mês
        m = S.groupby(S.index.to_period("M")).last()
        ret = m.pct_change().dropna()
        cdi_m = I105.groupby(I105.index.to_period("M")).last().pct_change().reindex(ret.index) * (1 - IR_CX)
        fases = pd.Series({p: fase_selic(p.start_time - pd.Timedelta(days=1)) for p in ret.index})
        for f_ in ("subindo", "parada", "caindo"):
            k = fases == f_
            FASE.append({"Versão": nome, "Fase da Selic": f_, "Meses": int(k.sum()),
                         "Carteira ao mês": float(ret[k].mean()), "CDI líquido ao mês": float(cdi_m[k].mean()),
                         "Meses acima do CDI": float((ret[k] > cdi_m[k]).mean())})
        RES.append({"Versão": nome, "Valor final (R$)": S.iloc[-1], "Maior queda": (S / S.cummax() - 1).min(),
                    "Operações fechadas": len(O), "Com lucro": (O["resultado"] > 0).mean() if len(O) else np.nan,
                    "Resultado médio": O["resultado_pct"].mean() if len(O) else np.nan,
                    "Dias médios": (O["saida"] - O["entrada"]).dt.days.mean() if len(O) else np.nan,
                    "Anos acima do CDI (de 9)": int((T["carteira"] > T["cdi_liq"]).sum())})
        SAI[nome] = (S, O, A, T)
        print(f"{nome}: R$ {S.iloc[-1]:,.2f}", flush=True)
    R_ = pd.DataFrame(RES)
    F_ = pd.DataFrame(FASE)
    print(f"\n105% CDI líquido no período: R$ {cdi_liq(DIAS[0], DIAS[-1]):,.2f}")
    print(R_.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print("\nPOR ANO (carteira / CDI líquido)")
    print(pd.DataFrame({n_: SAI[n_][3]["carteira"] for n_ in SAI}).assign(CDI=SAI[VAR[0][0]][3]["cdi_liq"]).to_string(float_format=lambda v: f"{v:+.1%}"))
    print("\nPOR FASE DA SELIC (média ao mês)")
    print(F_.to_string(index=False, float_format=lambda v: f"{v:+.2%}"))
    hoje = DIAS[-1]
    print(f"\nFase da Selic em {hoje:%d/%m/%Y}: {fase_selic(hoje)} ({float(SELIC.loc[:hoje].iloc[-1]):.2%})")
    C = candidatos(hoje, relativo=True)
    print(f"Elegíveis hoje com rendimento comparado ao tipo: {len(C)}")
    if len(C):
        print(C.head(15).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    with pd.ExcelWriter("planilhas/renda_descontada.xlsx") as w:
        R_.to_excel(w, sheet_name="Resumo", index=False)
        F_.to_excel(w, sheet_name="Por fase da Selic", index=False)
        for i, (n_, (S, O, A, T)) in enumerate(SAI.items(), 1):
            T.to_excel(w, sheet_name=f"Por ano {n_[0]}")
            O.to_excel(w, sheet_name=f"Operações {n_[0]}", index=False)
            A.to_excel(w, sheet_name=f"Em aberto {n_[0]}", index=False)
        C.to_excel(w, sheet_name="Elegíveis hoje (tipo)", index=False)
        for n_, b in BAR.items():
            if len(b):
                b.to_excel(w, sheet_name=f"Barrados {n_[0]}", index=False)
        # as 7 operações da versão D que ficaram abaixo do CDI: aparecem nas versões F, G, H?
        OD = SAI[VAR[3][0]][1]
        RUINS = OD[OD["fundo"].isin(["FIGS11", "XPCM11", "BLMR11", "KORE11", "TOPP11", "VRTM11", "LIFE11"])]
        AB = SAI[VAR[3][0]][2]
        linhas = []
        for r in pd.concat([RUINS[["fundo", "entrada", "resultado_pct"]], AB[AB["fundo"].isin(["VRTM11", "LIFE11"])].assign(
                resultado_pct=lambda x: (x["valor"] + x["rendimentos"]) / x["custo"] - 1)[["fundo", "entrada", "resultado_pct"]]]).itertuples():
            lin = {"fundo": r.fundo, "entrada na D": r.entrada, "resultado na D": r.resultado_pct}
            for n_ in SAI:
                if n_[0] in "FGH":
                    E2 = pd.concat([SAI[n_][1][["fundo", "entrada"]], SAI[n_][2][["fundo", "entrada"]]])
                    E2 = E2[(E2["fundo"] == r.fundo) & ((E2["entrada"] - r.entrada).abs() <= pd.Timedelta(days=183))]
                    lin[f"comprou em {n_[0]} (até 6 meses de diferença)"] = (", ".join(f"{e:%d/%m/%Y}" for e in E2["entrada"])
                                                                         if len(E2) else "não")
            linhas.append(lin)
        SETE = pd.DataFrame(linhas)
        SETE.to_excel(w, sheet_name="7 operações ruins", index=False)
        print("\nAS OPERAÇÕES RUINS DA VERSÃO D NAS VERSÕES NOVAS")
        print(SETE.to_string(index=False))
    print("gravado: planilhas/renda_descontada.xlsx")
