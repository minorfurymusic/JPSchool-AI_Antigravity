"""Estudo: quais sinais, conhecidos no fim de um mês, separaram os FIIs que
renderam mais dos que renderam menos no mês seguinte (2017-2026).

Método: em cada mês, ordena os fundos pelo sinal e divide em 5 grupos. Mede o
retorno do mês seguinte (cota + rendimento, entrando no 1º pregão) de cada
grupo, sempre em relação à mediana do mercado. Um sinal só é levado a sério se
funcionar nas duas metades do período.

Cuidado contra "olhar o futuro": valor patrimonial e cotistas entram com 2
meses de atraso, que é quando o informe da CVM já está publicado.

Uso: .venv/bin/python estudos/relacoes.py
"""
import json
import warnings

import duckdb
import numpy as np
import pandas as pd

from fii import aprendizado as ap
from fii import config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 230)
pd.set_option("display.max_columns", 30)
LIQ = 200_000
CORTE = "2022-01-01"


def tstat(s):
    s = s.dropna()
    return s.mean() / (s.std(ddof=1) / np.sqrt(len(s))) if len(s) > 5 and s.std() > 0 else np.nan


def painel(con):
    m = ap.retornos_mensais(con.execute("select * from mensal").df())
    mk = ap.mercado(m)
    m = m.merge(mk, left_on="mes", right_index=True, how="left").sort_values(["ticker", "mes"]).reset_index(drop=True)
    g = m.groupby("ticker")
    m["exc"] = m["tr"] - m["mkt_tr"]
    # alvo: retorno do mês seguinte, entrando no 1º pregão, acima do mercado
    m["alvo"] = g["tr_ini"].shift(-1) - g["mkt_tr_ini"].shift(-1)
    m["alvo3"] = sum(g["exc"].shift(-k) for k in (2, 3)) + m["alvo"]
    # robustez: entrar só no 10º pregão do mês seguinte; e pular o mês seguinte inteiro
    m["alvo_d10"] = g["tr_d10"].shift(-1) - g["mkt_tr_d10"].shift(-1)
    m["alvo_m2a3"] = g["exc"].shift(-2) + g["exc"].shift(-3)
    seguido = (g["mes"].shift(-1).dt.to_period("M").astype("int64") - m["mes"].dt.to_period("M").astype("int64")) == 1
    m.loc[~seguido.fillna(False), ["alvo", "alvo3"]] = np.nan
    lr = np.log1p(m["tr"].clip(-0.6, 0.6))
    m["_lr"] = lr
    g = m.groupby("ticker")
    rend = m["rend_aj"].where(m["rend_aj"] > 0)
    m["_rend"] = rend
    g = m.groupby("ticker")
    S = {}
    S["queda_no_mes (retorno do mês acima do mercado)"] = m["exc"]
    S["tendencia_12m (retorno de 12 meses, sem o último)"] = g["_lr"].transform(lambda s: s.shift(1).rolling(11, min_periods=9).sum())
    S["tendencia_3m (retorno dos 3 meses anteriores)"] = g["_lr"].transform(lambda s: s.shift(1).rolling(3, min_periods=3).sum())
    S["preco_sobre_vp (com 2 meses de atraso)"] = m["preco_fim"] / g["vp_aj"].shift(2)
    S["rendimento_12m_sobre_preco"] = g["_rend"].transform(lambda s: s.rolling(12, min_periods=10).sum()) / m["preco_fim"]
    S["rendimento_do_mes_sobre_preco"] = rend / m["preco_fim"]
    S["rendimento_vs_6m (salto ou queda)"] = rend / g["_rend"].transform(lambda s: s.shift(1).rolling(6, min_periods=4).median())
    S["volume_fora_do_normal (mês ÷ média de 6)"] = m["vol_medio"] / g["vol_medio"].transform(lambda s: s.shift(1).rolling(6, min_periods=4).mean())
    S["cotistas_crescendo (3 meses, com atraso)"] = g["cotistas"].shift(2) / g["cotistas"].shift(5) - 1
    S["tamanho (patrimônio, com atraso)"] = g["pl"].shift(2)
    S["oscilacao_12m (desvio do retorno mensal)"] = g["_lr"].transform(lambda s: s.rolling(12, min_periods=9).std())
    S["liquidez (volume diário médio)"] = m["vol_medio"]
    S["vp_crescendo (6 meses, com atraso)"] = g["vp_aj"].shift(2) / g["vp_aj"].shift(8) - 1
    for k, v in S.items():
        m[k] = v.replace([np.inf, -np.inf], np.nan)
    return m[(m["vol_medio"] >= LIQ) & (m["alvo"].abs() < 0.5)], list(S)


def testar(m, sinal, alvo="alvo", grupos=5):
    linhas = []
    for mes, d in m.groupby("mes"):
        d = d[[sinal, alvo]].dropna()
        if len(d) < 40:
            continue
        q = pd.qcut(d[sinal].rank(method="first"), grupos, labels=False)
        med = d.groupby(q)[alvo].mean()
        linhas.append({"mes": mes, "baixo": med[0], "alto": med[grupos - 1], "dif": med[grupos - 1] - med[0],
                       "ic": d[sinal].rank().corr(d[alvo].rank()), "n": len(d), **{f"g{i+1}": med[i] for i in range(grupos)}})
    return pd.DataFrame(linhas)


def resumo(m, sinais, alvo="alvo"):
    out = []
    for s in sinais:
        t = testar(m, s, alvo)
        if t.empty:
            continue
        a, b = t[t["mes"] < CORTE], t[t["mes"] >= CORTE]
        out.append({"sinal": s, "meses": len(t), "fundos/mês": int(t["n"].median()),
                    "grupo baixo %": t["baixo"].mean() * 100, "grupo alto %": t["alto"].mean() * 100,
                    "alto-baixo %": t["dif"].mean() * 100, "t": tstat(t["dif"]), "meses a favor": (np.sign(t["dif"]) == np.sign(t["dif"].mean())).mean(),
                    "1ª metade %": a["dif"].mean() * 100, "t1": tstat(a["dif"]), "2ª metade %": b["dif"].mean() * 100, "t2": tstat(b["dif"]),
                    "monotônico": " ".join(f"{t[f'g{i}'].mean()*100:+.2f}" for i in range(1, 6))})
    return pd.DataFrame(out)


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    m, sinais = painel(con)
    print(f"Painel: {m['mes'].min():%m/%Y} a {m['mes'].max():%m/%Y}, {m['ticker'].nunique()} fundos, {len(m)} fundo-meses com liquidez >= R$ {LIQ:,}/dia\n")
    print("=== 1. SINAIS E O RETORNO DO MÊS SEGUINTE (acima do mercado) ===")
    r1 = resumo(m, sinais)
    print(r1.round(2).to_string(index=False))
    print("\n=== 2. MESMOS SINAIS, RETORNO DOS 3 MESES SEGUINTES ===")
    r3 = resumo(m, sinais, "alvo3")
    print(r3[["sinal", "meses", "alto-baixo %", "t", "meses a favor", "1ª metade %", "t1", "2ª metade %", "t2", "monotônico"]].round(2).to_string(index=False))

    print("\n=== 2b. OS SINAIS FORTES RESISTEM A ENTRAR MAIS TARDE? ===")
    fortes = [x for x in sinais if x.startswith(("rendimento_vs_6m", "rendimento_do_mes", "tendencia_12m", "vp_crescendo"))]
    for alvo, rot in (("alvo_d10", "entrando no 10º pregão do mês seguinte (retorno do resto do mês)"), ("alvo_m2a3", "pulando o mês seguinte inteiro (retorno dos meses 2 e 3)")):
        print(rot)
        print(resumo(m[m[alvo].abs() < 0.6], fortes, alvo)[["sinal", "meses", "alto-baixo %", "t", "meses a favor", "1ª metade %", "t1", "2ª metade %", "t2", "monotônico"]].round(2).to_string(index=False))
    # os sinais fortes são a mesma coisa ou somam?
    cc = m[fortes].rank(pct=True).corr().round(2)
    cc.index = cc.columns = [c.split(" ")[0] for c in cc.columns]
    print("Correlação entre os sinais fortes (posição no ranking):")
    print(cc.to_string())
    m2 = m.copy()
    m2["combinado"] = m2.groupby("mes")[fortes].rank(pct=True).mean(axis=1, skipna=False)
    print("Sinal combinado (média da posição nos 4 sinais):")
    print(resumo(m2, ["combinado"])[["meses", "fundos/mês", "grupo baixo %", "grupo alto %", "alto-baixo %", "t", "meses a favor", "1ª metade %", "t1", "2ª metade %", "t2", "monotônico"]].round(2).to_string(index=False))
    t = testar(m2, "combinado")
    t["ano"] = t["mes"].dt.year
    print("Sinal combinado, ano a ano (grupo alto acima do mercado, % ao mês | alto menos baixo):")
    print(t.groupby("ano").agg(meses=("dif", "size"), alto=("alto", lambda s: s.mean() * 100), dif=("dif", lambda s: s.mean() * 100), a_favor=("dif", lambda s: (s > 0).mean())).round(2).T.to_string())

    print("\n=== 3. O PREÇO JÁ SE MEXE ANTES DO SALTO DE RENDIMENTO? ===")
    ev = con.execute("select ticker, mes, evento, razao from eventos where evento in ('salto','queda')").df()
    base = m.set_index(["ticker", "mes"])
    for nome in ("salto", "queda"):
        lin = []
        for e in ev[ev["evento"] == nome].itertuples():
            reg = {}
            for k in (-3, -2, -1, 0):
                ch = (e.ticker, e.mes + pd.DateOffset(months=k))
                reg[f"exc_{k}"] = base.at[ch, "exc"] if ch in base.index else np.nan
                reg[f"vol_{k}"] = base.at[ch, "volume_fora_do_normal (mês ÷ média de 6)"] if ch in base.index else np.nan
            lin.append(reg)
        d = pd.DataFrame(lin)
        print(f"{nome}: {len(d)} casos | retorno acima do mercado (média %, estatística t) e volume relativo (mediana):")
        for k in (-3, -2, -1, 0):
            rot = "mês do evento" if k == 0 else f"{-k} mês(es) antes"
            print(f"   {rot:16s} retorno {d[f'exc_{k}'].mean()*100:+.2f}% (t {tstat(d[f'exc_{k}']):+.1f}, {(d[f'exc_{k}']>0).mean():.0%} positivos) | volume {d[f'vol_{k}'].median():.2f}x")

    print("\n=== 4. DATA LIMITE DO RENDIMENTO (\"data com\"): o que a cota faz em volta ===")
    c = con.execute("select ticker, data, fechamento, isin from cotacoes where data >= '2025-06-01'").df()
    p = c.pivot(index="data", columns="ticker", values="fechamento").sort_index()
    rd = p.pct_change(fill_method=None)
    rd = rd.where(rd.abs() < 0.2)
    mkt_d = rd.median(axis=1)
    isin = c.groupby("ticker")["isin"].last()
    from fii import coleta
    lin = []
    datas = p.index
    for cod, dado in coleta.ler_fundos_b3().items():
        for tk in [t for t in p.columns if t.startswith(cod)]:
            for r in dado["rendimentos"]:
                if r["isin"] != isin.get(tk) or r["tipo"] != "RENDIMENTO" or not r["valor"] or not r["data_com"]:
                    continue
                d0 = pd.Timestamp(r["data_com"])
                if d0 not in datas:
                    continue
                i = datas.get_loc(d0)
                if i < 11 or i + 11 >= len(datas) or pd.isna(p[tk].iloc[i]):
                    continue
                px = p[tk]
                exc = (rd[tk] - mkt_d)
                lin.append({"ticker": tk, "dy": r["valor"] / px.iloc[i],
                            "antes_10": exc.iloc[i - 9:i + 1].sum(), "antes_3": exc.iloc[i - 2:i + 1].sum(),
                            "dia_ex_preco": exc.iloc[i + 1], "dia_ex_total": exc.iloc[i + 1] + r["valor"] / px.iloc[i],
                            "depois_5_total": exc.iloc[i + 1:i + 6].sum() + r["valor"] / px.iloc[i],
                            "depois_10_total": exc.iloc[i + 1:i + 11].sum() + r["valor"] / px.iloc[i]})
    d = pd.DataFrame(lin).dropna()
    d = d[d["dy"].between(0.002, 0.05)]
    print(f"{len(d)} pagamentos de {d['ticker'].nunique()} fundos (jun/2025 em diante). Rendimento médio: {d['dy'].mean()*100:.2f}% da cota.")
    for col, rot in [("antes_10", "10 pregões até a data limite (só cota)"), ("antes_3", "3 pregões até a data limite (só cota)"),
                     ("dia_ex_preco", "1º pregão sem direito (só cota)"), ("dia_ex_total", "1º pregão sem direito (cota + rendimento)"),
                     ("depois_5_total", "comprar na data limite, vender 5 pregões depois (cota + rendimento)"),
                     ("depois_10_total", "comprar na data limite, vender 10 pregões depois (cota + rendimento)")]:
        print(f"   {rot:70s} {d[col].mean()*100:+.2f}% acima do mercado (t {tstat(d[col]):+.1f}, {(d[col]>0).mean():.0%} positivos)")

    print("\n=== 5. JUROS (SELIC) E O MERCADO DE FIIs ===")
    sel = pd.DataFrame(json.load(open(config.DADOS / "bruto" / "sgs_432.json")))
    sel["data"] = pd.to_datetime(sel["data"], dayfirst=True)
    sel = sel[sel["data"] <= pd.Timestamp("2026-11-09")].set_index("data")["valor"].astype(float).resample("MS").last()
    mk = ap.mercado(ap.retornos_mensais(con.execute("select * from mensal").df()))["mkt_tr"]
    z = pd.DataFrame({"fii": mk, "selic": sel}).dropna()
    z["d3"] = z["selic"] - z["selic"].shift(3)
    z["fase"] = np.where(z["d3"] < -0.1, "Selic caindo", np.where(z["d3"] > 0.1, "Selic subindo", "Selic parada"))
    z["fii_seg"] = z["fii"].shift(-1)
    print(z.groupby("fase").agg(meses=("fii", "size"), retorno_no_mes=("fii", lambda s: s.mean() * 100),
                                retorno_mes_seguinte=("fii_seg", lambda s: s.mean() * 100), positivos=("fii_seg", lambda s: (s > 0).mean())).round(2).to_string())
    # os saltos de rendimento rendem mais em alguma fase?
    evm = con.execute("select mes, exc_ini_3, exc_ini_6 from eventos where evento='salto'").df().merge(z[["fase"]], left_on="mes", right_index=True)
    print("Saltos de rendimento por fase dos juros (retorno acima do mercado, mediana %):")
    print(evm.groupby("fase").agg(casos=("exc_ini_3", "size"), em_3m=("exc_ini_3", lambda s: s.median() * 100), em_6m=("exc_ini_6", lambda s: s.median() * 100),
                                  acerto_3m=("exc_ini_3", lambda s: (s.dropna() > 0).mean())).round(2).to_string())

    print("\n=== 6. A BOLSA DE HOJE AVISA O FII DE AMANHÃ? (diário) ===")
    c2 = con.execute("select ticker, data, fechamento, volume from cotacoes c join (select distinct ticker from mensal) using(ticker)").df()
    p2 = c2.pivot(index="data", columns="ticker", values="fechamento").sort_index()
    v2 = c2.pivot(index="data", columns="ticker", values="volume").sort_index()
    r2 = p2.pct_change(fill_method=None)
    r2 = r2.where(r2.abs() < 0.2).where(v2.rolling(20, min_periods=5).mean() >= LIQ)
    fd = r2.median(axis=1).rename("fii")
    bova = pd.read_parquet(config.DADOS / "bruto" / "bova.parquet").set_index("data")["bova"].pct_change().rename("bolsa")
    dol = pd.DataFrame(json.load(open(config.DADOS / "bruto" / "sgs_1.json")))
    dol["data"] = pd.to_datetime(dol["data"], dayfirst=True)
    dol = dol.set_index("data")["valor"].astype(float).pct_change().rename("dolar")
    x = pd.concat([fd, bova, dol], axis=1).dropna()
    print(f"{len(x)} pregões. Correlação do FII de hoje com: bolsa de hoje {x.fii.corr(x.bolsa):+.2f} | bolsa de ontem {x.fii.corr(x.bolsa.shift(1)):+.2f} | "
          f"bolsa de anteontem {x.fii.corr(x.bolsa.shift(2)):+.2f} | FII de ontem {x.fii.corr(x.fii.shift(1)):+.2f} | dólar de ontem {x.fii.corr(x.dolar.shift(1)):+.2f}")
    for nome, cond in [("bolsa caiu mais de 2% ontem", x.bolsa.shift(1) < -0.02), ("bolsa subiu mais de 2% ontem", x.bolsa.shift(1) > 0.02),
                       ("FII caiu mais de 0,5% ontem", x.fii.shift(1) < -0.005), ("FII subiu mais de 0,5% ontem", x.fii.shift(1) > 0.005)]:
        for per, xx in (("2017-21", x[:"2021-12-31"]), ("2022-26", x["2022-01-01":])):
            s = xx.fii[cond.reindex(xx.index).fillna(False)]
            print(f"   {nome:30s} {per}: {len(s):4d} dias | FII hoje {s.mean()*100:+.3f}% (t {tstat(s):+.1f}, {(s>0).mean():.0%} positivos) | dia comum {xx.fii.mean()*100:+.3f}%")


if __name__ == "__main__":
    main()
