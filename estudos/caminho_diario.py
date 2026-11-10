"""Estudo do CAMINHO da cota, dia a dia, depois de um salto de rendimento.

Medir só "preço na entrada x preço N meses depois" esconde o que aconteceu no
meio. Aqui, para cada salto, a cota é seguida pregão a pregão: até onde subiu
(pico), até onde caiu (fundo), em que dia, e o que teria rendido vender num alvo.

Como qualquer cota oscila, o pico de qualquer fundo em 3 meses é sempre positivo.
Por isso cada salto é comparado com um CONTROLE: os outros fundos com liquidez,
comprados no mesmo dia, sem salto recente.

Uso: PYTHONPATH=. .venv/bin/python estudos/caminho_diario.py
"""
import warnings

import duckdb
import numpy as np
import pandas as pd

from fii import aprendizado as ap
from fii import base, config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
JANELAS = {"1 mês": 21, "3 meses": 63, "6 meses": 126}
LIQ = 200_000


def precos_diarios(con):
    c = con.execute("select c.ticker, c.data, c.fechamento, c.volume from cotacoes c join (select distinct ticker from mensal) using(ticker)").df()
    q = con.execute("select * from quebras").df()
    conf = q[q["confirmada"]]
    ruins = q[~q["confirmada"]]
    partes = []
    for tk, g in c.groupby("ticker", sort=False):
        g = g.sort_values("data").copy()
        g["aj"] = g["fechamento"] * base.fator_de_ajuste(g["data"], conf[conf["ticker"] == tk])
        partes.append(g)
    c = pd.concat(partes)
    p = c.pivot(index="data", columns="ticker", values="aj").sort_index()
    v = c.pivot(index="data", columns="ticker", values="volume").sort_index()
    liq = v.fillna(0).rolling(60, min_periods=20).mean() >= LIQ
    p = p.ffill(limit=5)  # dia sem negócio: vale o último fechamento (até 5 pregões)
    # salto de preço sem explicação: apaga 130 pregões em volta para não contaminar pico/fundo
    for r in ruins.itertuples():
        if r.ticker in p.columns:
            i = p.index.searchsorted(r.data)
            p.iloc[max(0, i - 130):i + 130, p.columns.get_loc(r.ticker)] = np.nan
    return p, liq


def caminhos(p, entradas, w):
    """entradas: lista de (ticker, posição do dia de entrada). Devolve matriz [caso, dia] da variação desde a entrada."""
    out = np.full((len(entradas), w), np.nan)
    arr = p.to_numpy()
    col = {t: i for i, t in enumerate(p.columns)}
    for n, (tk, i0) in enumerate(entradas):
        if i0 + w >= len(arr):
            continue
        serie = arr[i0:i0 + w + 1, col[tk]]
        if np.isnan(serie).any() or serie[0] <= 0:
            continue
        out[n] = serie[1:] / serie[0] - 1
    return out


def medidas(c):
    c = c[~np.isnan(c).any(axis=1)]
    if not len(c):
        return {}
    pico, fundo = c.max(axis=1), c.min(axis=1)
    dia_pico = c.argmax(axis=1) + 1
    antes = lambda alvo, perda: np.array([(np.argmax(l >= alvo) if (l >= alvo).any() else 10**6) < (np.argmax(l <= perda) if (l <= perda).any() else 10**6) for l in c])
    return {"casos": len(c), "pico (mediana) %": np.median(pico) * 100, "fundo (mediana) %": np.median(fundo) * 100,
            "fim da janela (mediana) %": np.median(c[:, -1]) * 100, "dia do pico (mediano)": np.median(dia_pico),
            "tocou +5%": (pico >= .05).mean(), "tocou +10%": (pico >= .10).mean(), "tocou +15%": (pico >= .15).mean(),
            "tocou -5%": (fundo <= -.05).mean(), "tocou -10%": (fundo <= -.10).mean(),
            "+10% antes de -10%": antes(.10, -.10).mean(), "+5% antes de -5%": antes(.05, -.05).mean(),
            "devolveu (pico >= 6% e fim <= metade do pico)": ((pico >= .06) & (c[:, -1] <= pico / 2)).mean()}


def regra(c, alvo, perda, rend_dia):
    """Vende no alvo, ou na perda máxima, ou no fim da janela. Soma o rendimento recebido enquanto segurou."""
    c = c[~np.isnan(c).any(axis=1)]
    res, dias = [], []
    for l in c:
        ia = np.argmax(l >= alvo) if (l >= alvo).any() else None
        ip = np.argmax(l <= perda) if perda is not None and (l <= perda).any() else None
        if ia is not None and (ip is None or ia <= ip):
            k, r = ia, alvo
        elif ip is not None:
            k, r = ip, perda
        else:
            k, r = len(l) - 1, l[-1]
        res.append(r + rend_dia * (k + 1))
        dias.append(k + 1)
    return np.array(res), np.array(dias)


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    p, liq = precos_diarios(con)
    datas = p.index
    ev = con.execute("select ticker, mes, razao, tipo_fundo, com_venda, dy_antes, anuncio from eventos where evento='salto'").df()
    todos = con.execute("select ticker, mes from eventos where evento in ('salto','salto mantido')").df()
    rng = np.random.default_rng(7)
    ent_ev, ent_ct, meta = [], [], []
    for e in ev.itertuples():
        i0 = datas.searchsorted(e.mes + pd.DateOffset(months=1))  # 1º pregão do mês seguinte ao do salto
        if i0 >= len(datas) or e.ticker not in p.columns:
            continue
        ent_ev.append((e.ticker, i0))
        meta.append(e)
        com_evento = set(todos[(todos["mes"] >= e.mes - pd.DateOffset(months=6)) & (todos["mes"] <= e.mes + pd.DateOffset(months=6))]["ticker"])
        cand = [t for t in p.columns[liq.iloc[i0].to_numpy()] if t not in com_evento]
        for t in rng.choice(cand, size=min(25, len(cand)), replace=False) if cand else []:
            ent_ct.append((t, i0))
    meta = pd.DataFrame(meta)
    print(f"{len(ent_ev)} saltos de rendimento (2017-2026), comprando no fechamento do 1º pregão do mês seguinte. Controle: {len(ent_ct)} compras de outros fundos nos mesmos dias.\n")

    print("=== 1. ATÉ ONDE A COTA FOI, DIA A DIA (só preço, sem rendimento) ===")
    cam = {}
    for nome, w in JANELAS.items():
        cam[nome] = (caminhos(p, ent_ev, w), caminhos(p, ent_ct, w))
        t = pd.DataFrame({"depois de salto": medidas(cam[nome][0]), "controle (outros fundos, mesmo dia)": medidas(cam[nome][1])})
        print(f"--- janela de {nome} ({w} pregões) ---")
        print(t.round(3).to_string())

    print("\n=== 2. POR GRUPO, JANELA DE 3 MESES (salto x controle do mesmo grupo de datas) ===")
    ce, cc = cam["3 meses"]
    grupos = {"papel": meta["tipo_fundo"] == "papel", "tijolo": meta["tipo_fundo"] == "tijolo", "com venda de imóvel": meta["com_venda"],
              "salto de 25 a 50%": meta["razao"] < 1.5, "salto acima de 50%": meta["razao"] >= 1.5,
              "rendia >= 10% ao ano": meta["dy_antes"] * 12 >= 0.10, "rendia < 10% ao ano": meta["dy_antes"] * 12 < 0.10,
              "até 2021": meta["mes"] < "2022-01-01", "2022 em diante": meta["mes"] >= "2022-01-01"}
    lin = []
    for nome, mask in grupos.items():
        m = medidas(ce[mask.to_numpy()])
        if m:
            lin.append({"grupo": nome, **{k: m[k] for k in ("casos", "pico (mediana) %", "fundo (mediana) %", "fim da janela (mediana) %", "dia do pico (mediano)", "tocou +10%", "tocou -10%", "+10% antes de -10%")}})
    print(pd.DataFrame(lin).round(3).to_string(index=False))

    print("\n=== 3. VENDER NUM ALVO: resultado por operação, com rendimento recebido (janela máxima de 6 meses) ===")
    ce, cc = cam["6 meses"]
    rd_ev = float(np.nanmedian(meta["dy_antes"] * meta["razao"])) / 21  # rendimento por pregão depois do salto
    rd_ct = float(con.execute("select median(rend_ret/preco_fim) from mensal where vol_medio>=200000 and rend_ret>0").fetchone()[0]) / 21
    print(f"(rendimento considerado por mês: {rd_ev*21*100:.2f}% da cota depois de salto; {rd_ct*21*100:.2f}% no controle)")
    lin = []
    for alvo, perda in [(.05, None), (.08, None), (.10, None), (.15, None), (.05, -.05), (.08, -.08), (.10, -.10), (.10, -.05), (None, None)]:
        a = 9.99 if alvo is None else alvo
        re, de = regra(ce, a, perda, rd_ev)
        rc, dc = regra(cc, a, perda, rd_ct)
        lin.append({"regra": ("segurar 6 meses" if alvo is None else f"vender em +{alvo:.0%}") + ("" if perda is None else f" ou em {perda:.0%}"),
                    "salto: média %": re.mean() * 100, "salto: mediana %": np.median(re) * 100, "salto: ganhou": (re > 0).mean(),
                    "salto: resultado >= alvo": (re >= a).mean() if alvo else np.nan, "salto: dias (mediana)": np.median(de),
                    "controle: média %": rc.mean() * 100, "controle: ganhou": (rc > 0).mean(), "controle: resultado >= alvo": (rc >= a).mean() if alvo else np.nan,
                    "vantagem (média) %": (re.mean() - rc.mean()) * 100,
                    "vantagem ao ano %": ((re.mean() / np.mean(de)) - (rc.mean() / np.mean(dc))) * 252 * 100})
    print(pd.DataFrame(lin).round(2).to_string(index=False))

    print("\n=== 4. \"SOBE 6-10% NUM MÊS E DEVOLVE NO SEGUINTE\": com que frequência, em qualquer fundo? ===")
    m = ap.retornos_mensais(con.execute("select * from mensal").df())
    m = m[m["vol_medio"] >= LIQ].sort_values(["ticker", "mes"])
    m["seg"] = m.groupby("ticker")["pr"].shift(-1)
    m = m.dropna(subset=["pr", "seg"])
    m = m[m["pr"].abs() < 0.5]
    print(f"{len(m)} fundo-meses. Subiu 6% ou mais no mês: {(m.pr >= .06).mean():.1%} | caiu 6% ou mais: {(m.pr <= -.06).mean():.1%}")
    for nome, cond in [("depois de subir 6% ou mais", m.pr >= .06), ("depois de subir 3 a 6%", (m.pr >= .03) & (m.pr < .06)), ("mês comum (entre -3 e +3%)", m.pr.abs() < .03),
                       ("depois de cair 3 a 6%", (m.pr <= -.03) & (m.pr > -.06)), ("depois de cair 6% ou mais", m.pr <= -.06)]:
        s = m[cond]
        print(f"   {nome:30s} {len(s):5d} casos | mês seguinte: média {s.seg.mean()*100:+.2f}%, mediana {s.seg.median()*100:+.2f}% | devolveu metade ou mais: {((s.seg * np.sign(s.pr)) <= -s.pr.abs() / 2).mean():.0%}")
    # dentro do mês: amplitude típica
    amp = con.execute("""select median(mx/mn-1), avg(case when mx/mn-1>=0.06 then 1.0 else 0 end), avg(case when mx/mn-1>=0.10 then 1.0 else 0 end) from
        (select ticker, date_trunc('month',data) m, max(fechamento) mx, min(fechamento) mn, avg(volume) v, count(*) n from cotacoes group by 1,2) where v>=200000 and n>=15 and mx/mn<2""").fetchone()
    print(f"Dentro de um mês, distância entre o menor e o maior fechamento: mediana {amp[0]*100:.1f}% | 6% ou mais em {amp[1]:.0%} dos meses | 10% ou mais em {amp[2]:.0%}")


    print("\n=== 5. A PARTIR DA ENTRADA: sobe nos primeiros 30 dias e devolve nos 30 seguintes? (21 pregões = ~30 dias) ===")
    ce, cc = cam["3 meses"]
    for nome, c in (("depois de salto", ce), ("controle", cc)):
        c = c[~np.isnan(c).any(axis=1)]
        pico1 = c[:, :21].max(axis=1)      # maior alta nos primeiros ~30 dias
        d21, d42 = c[:, 20], c[:, 41]      # onde estava no 21º e no 42º pregão
        print(f"{nome}: {len(c)} casos")
        for lo, hi in ((0.03, 0.06), (0.06, 0.10), (0.10, 9)):
            m = (pico1 >= lo) & (pico1 < hi)
            if m.sum() < 5:
                print(f"   pico de {lo:.0%} a {hi:.0%} nos primeiros 30 dias: {m.sum()} casos (poucos)")
                continue
            dia = np.median(c[m, :21].argmax(axis=1) + 1)
            apos = np.array([l[np.argmax(l[:21]):np.argmax(l[:21]) + 22].min() - l[:21].max() for l in c[m]])  # pior ponto nos 21 pregões depois do pico
            rot = f"{lo:.0%} a {hi:.0%}" if hi < 1 else f"{lo:.0%} ou mais"
            print(f"   pico de {rot} nos primeiros 30 dias: {m.sum()} casos ({m.mean():.0%}) | dia do pico {dia:.0f}º | "
                  f"no 21º pregão estava em {np.median(d21[m])*100:+.1f}% | no 42º em {np.median(d42[m])*100:+.1f}% | "
                  f"devolveu metade ou mais do pico até o 42º: {(d42[m] <= pico1[m] / 2).mean():.0%} | devolveu tudo (voltou ao preço de entrada ou abaixo): {(d42[m] <= 0).mean():.0%} | "
                  f"queda a partir do pico nos 30 dias seguintes (mediana): {np.median(apos)*100:+.1f}%")


if __name__ == "__main__":
    main()
