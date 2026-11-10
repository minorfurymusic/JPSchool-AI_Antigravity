"""Estudo com a DATA REAL do anúncio (avisos de rendimento do FNET, desde 2017).

Responde, dia a dia e contra um grupo de controle:
  1. O que a cota faz a partir do dia em que o aumento de rendimento é anunciado.
  2. Vale entrar tarde? (1, 3 e 5 meses depois, quando o rendimento continua alto)
  3. O que a cota faz quando o rendimento alto acaba (a devolução).

Entrada: fechamento do primeiro pregão em que o mercado pôde reagir. Aviso entregue
até as 17h vale o fechamento do mesmo dia; depois disso, o do pregão seguinte.
(O FNET não informa o fuso da hora de entrega; presume-se horário de Brasília.)

Uso: PYTHONPATH=. .venv/bin/python estudos/anuncio_real.py
"""
import warnings

import duckdb
import numpy as np
import pandas as pd

from estudos.caminho_diario import caminhos, medidas, precos_diarios
from fii import base, config, fnet

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
SALTO, ALTO, VOLTOU = 1.25, 1.15, 1.10
JANELAS = {"1 mês": 21, "3 meses": 63, "6 meses": 126}
CHAVES = ["casos", "pico (mediana) %", "fundo (mediana) %", "fim da janela (mediana) %", "dia do pico (mediano)",
          "tocou +5%", "tocou +10%", "tocou +15%", "tocou -5%", "tocou -10%", "+10% antes de -10%"]


def anuncios(con_app, con_fnet):
    """Um anúncio por papel e data-base, na última versão entregue, com o valor na base de cotas de hoje."""
    r = con_fnet.execute("select * from rendimentos_fnet where tipo='Rendimento' and valor > 0 and data_base is not null and entrega is not null").df()
    isin = con_app.execute("select isin, last(ticker order by data) ticker from cotacoes group by 1").df()
    com_dados = set(con_app.execute("select distinct ticker from mensal").df()["ticker"])
    r = r.merge(isin, on="isin")
    r = r[r["ticker"].isin(com_dados)]
    primeira = r.groupby(["ticker", "data_base"])["entrega"].transform("min")  # a notícia saiu na 1ª versão
    r = r.sort_values("versao").drop_duplicates(["ticker", "data_base", "doc_id"], keep="last")
    ult = r.groupby(["ticker", "data_base"])["versao"].transform("max")
    r = r.assign(entrega=primeira)[r["versao"] == ult]
    a = r.groupby(["ticker", "data_base"]).agg(valor=("valor", "sum"), entrega=("entrega", "min"), pagamento=("data_pagamento", "max")).reset_index()
    q = con_app.execute("select * from quebras where confirmada").df()
    partes = []
    for tk, g in a.groupby("ticker"):
        g = g.sort_values("entrega").copy()
        g["valor_aj"] = g["valor"] * base.fator_de_ajuste(pd.to_datetime(g["data_base"]), q[q["ticker"] == tk])
        partes.append(g)
    return pd.concat(partes, ignore_index=True)


def dia_de_entrada(datas, entrega):
    d = pd.Timestamp(entrega)
    i = datas.searchsorted(d.normalize())
    if i < len(datas) and datas[i] == d.normalize() and d.hour < 17:
        return i
    return datas.searchsorted(d.normalize() + pd.Timedelta(days=1))


def detectar(a):
    """Salto anunciado e o que veio depois dele, usando só os anúncios do próprio fundo."""
    evs = []
    for tk, g in a.groupby("ticker"):
        g = g.reset_index(drop=True)
        gap = g["entrega"].diff().dt.days.median()
        if len(g) < 8 or not (15 <= gap <= 45):
            continue  # só fundos que anunciam todo mês
        v = g["valor_aj"].to_numpy()
        ultimo = -99
        for i in range(6, len(g)):
            b = np.median(v[i - 6:i])
            if b <= 0 or v[i] / b < SALTO or v[i] / b > 10 or i - ultimo <= 6:
                continue
            ultimo = i
            depois = v[i + 1:i + 19] / b
            n_alto = 0
            for x in depois:  # anúncios seguidos ainda altos
                if x >= ALTO:
                    n_alto += 1
                else:
                    break
            fim = i + 1 + n_alto if n_alto < len(depois) else None  # índice do anúncio em que voltou
            visto = len(depois)
            classe = ("isolado (voltou no anúncio seguinte)" if n_alto == 0 and visto >= 1 else
                      "temporário (2 a 11 anúncios altos e voltou)" if 1 <= n_alto < 11 and fim is not None else
                      "longo (12 ou mais anúncios altos)" if n_alto >= 11 else "ainda sem dados para classificar")
            evs.append({"ticker": tk, "entrega": g.at[i, "entrega"], "razao": v[i] / b, "base": b, "valor": v[i], "classe": classe,
                        "n_alto": n_alto, "entrega_volta": g.at[fim, "entrega"] if fim is not None and fim < len(g) else pd.NaT,
                        "razao_volta": v[fim] / b if fim is not None and fim < len(g) else np.nan,
                        # ainda alto 1, 3 e 5 anúncios depois? (o que dá para saber na hora de entrar tarde)
                        **{f"alto_{k}": bool(len(depois) >= k and (depois[:k] >= ALTO).all()) for k in (1, 3, 5)},
                        **{f"entrega_{k}": g.at[i + k, "entrega"] if i + k < len(g) else pd.NaT for k in (1, 3, 5)}})
    return pd.DataFrame(evs)


def controle(p, liq, posicoes, fora, rng, n=25):
    ent = []
    for i0 in posicoes:
        if i0 >= len(p):
            continue
        cand = [t for t in p.columns[liq.iloc[i0].to_numpy()] if t not in fora]
        ent += [(t, i0) for t in (rng.choice(cand, size=min(n, len(cand)), replace=False) if cand else [])]
    return ent


def comparar(p, liq, entradas, fora, rng, titulo, janelas=JANELAS):
    print(f"\n--- {titulo}: {len(entradas)} casos ---")
    if len(entradas) < 8:
        print("   poucos casos")
        return
    ct = controle(p, liq, [i for _, i in entradas], fora, rng)
    for nome, w in janelas.items():
        me, mc = medidas(caminhos(p, entradas, w)), medidas(caminhos(p, ct, w))
        if not me or not mc:
            continue
        t = pd.DataFrame({"caso": {k: me[k] for k in CHAVES}, "controle": {k: mc[k] for k in CHAVES}}).T
        print(f"  janela de {nome}:")
        print(t.round(3).to_string())


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    cf = duckdb.connect(str(fnet.BANCO), read_only=True)
    a = anuncios(con, cf)
    print(f"Anúncios de rendimento com data real: {len(a)} de {a['ticker'].nunique()} fundos, de {a['entrega'].min():%d/%m/%Y} a {a['entrega'].max():%d/%m/%Y}")
    h = pd.to_datetime(a["entrega"]).dt.hour
    print(f"Hora de entrega: até 10h {(h < 10).mean():.0%} | 10h às 17h {((h >= 10) & (h < 17)).mean():.0%} | 17h em diante {(h >= 17).mean():.0%}")
    dias = (pd.to_datetime(a["data_base"]) - pd.to_datetime(a["entrega"]).dt.normalize()).dt.days
    print(f"Dias entre o anúncio e a data-base: mediana {dias.median():.0f} | no mesmo dia {(dias == 0).mean():.0%} | 1 a 5 dias depois {((dias >= 1) & (dias <= 5)).mean():.0%} | anúncio depois da data-base {(dias < 0).mean():.0%}")

    ev = detectar(a)
    p, liq = precos_diarios(con)
    datas = p.index
    ev = ev[ev["ticker"].isin(p.columns)].reset_index(drop=True)
    ev["i0"] = [dia_de_entrada(datas, e) for e in ev["entrega"]]
    ev = ev[[i < len(datas) and bool(liq.iloc[i][t]) for i, t in zip(ev["i0"], ev["ticker"])]].reset_index(drop=True)
    fora = set(ev["ticker"])  # controle: fundos sem nenhum salto anunciado
    rng = np.random.default_rng(11)
    print(f"\nSaltos anunciados (>= {SALTO - 1:.0%} sobre a mediana dos 6 anúncios anteriores), fundos com liquidez: {len(ev)} em {ev['ticker'].nunique()} fundos")
    print(ev.groupby("classe").agg(casos=("ticker", "size"), salto_mediano=("razao", lambda s: (s.median() - 1) * 100),
                                   anuncios_altos=("n_alto", "median")).round(1).to_string())

    print("\n=== 1. A PARTIR DO DIA DO ANÚNCIO ===")
    # o que a cota fez ANTES do anúncio (alguém já sabia?) e no próprio dia
    arr = p.to_numpy()
    col = {t: i for i, t in enumerate(p.columns)}
    mk = np.nanmedian(np.where(liq.to_numpy(), p.pct_change(fill_method=None).to_numpy(), np.nan), axis=1)
    lin = []
    for e in ev.itertuples():
        s = arr[:, col[e.ticker]]
        if e.i0 < 12 or np.isnan(s[e.i0 - 11:e.i0 + 1]).any():
            continue
        acum = lambda a_, b_: s[b_] / s[a_] - 1 - (np.prod(1 + np.nan_to_num(mk[a_ + 1:b_ + 1])) - 1)
        lin.append({"10 pregões antes até a véspera": acum(e.i0 - 11, e.i0 - 1), "da véspera ao fechamento de entrada": acum(e.i0 - 1, e.i0)})
    d = pd.DataFrame(lin)
    for c in d:
        print(f"   {c}: média {d[c].mean()*100:+.2f}% acima do mercado, mediana {d[c].median()*100:+.2f}%, positivos {(d[c] > 0).mean():.0%} ({len(d)} casos)")
    comparar(p, liq, list(zip(ev["ticker"], ev["i0"])), fora, rng, "todos os saltos anunciados")
    for cl in sorted(ev["classe"].unique()):
        s = ev[ev["classe"] == cl]
        comparar(p, liq, list(zip(s["ticker"], s["i0"])), fora, rng, f"classe (só se sabe depois): {cl}", {"3 meses": 63, "6 meses": 126})
    for nome, m in (("salto de 25 a 50%", ev["razao"] < 1.5), ("salto acima de 50%", ev["razao"] >= 1.5),
                    ("até 2021", ev["entrega"] < "2022-01-01"), ("2022 em diante", ev["entrega"] >= "2022-01-01")):
        s = ev[m]
        comparar(p, liq, list(zip(s["ticker"], s["i0"])), fora, rng, nome, {"3 meses": 63})

    print("\n=== 2. ENTRAR TARDE: o rendimento continua alto N anúncios depois. E a cota, dali em diante? ===")
    for k, rot in ((1, "1 mês depois"), (3, "3 meses depois"), (5, "5 meses depois")):
        s = ev[ev[f"alto_{k}"] & ev[f"entrega_{k}"].notna()]
        ent = [(t, dia_de_entrada(datas, e)) for t, e in zip(s["ticker"], s[f"entrega_{k}"])]
        ent = [(t, i) for t, i in ent if i < len(datas)]
        comparar(p, liq, ent, fora, rng, f"entrada {rot} (rendimento alto em todos os {k} anúncios seguintes)", {"1 mês": 21, "3 meses": 63})

    print("\n=== 3. A DEVOLUÇÃO: a partir do anúncio em que o rendimento voltou ao nível antigo ===")
    s = ev[ev["entrega_volta"].notna() & (ev["n_alto"] >= 1)]
    ent = [(t, dia_de_entrada(datas, e)) for t, e in zip(s["ticker"], s["entrega_volta"])]
    ent = [(t, i) for t, i in ent if i < len(datas)]
    print(f"Rendimento no anúncio da volta, em relação ao nível anterior ao salto: mediana {s['razao_volta'].median():.2f} | abaixo do nível antigo em {(s['razao_volta'] < 1).mean():.0%} | 10% ou mais abaixo em {(s['razao_volta'] <= 0.9).mean():.0%}")
    comparar(p, liq, ent, fora, rng, "depois que o rendimento alto acabou (salto durou 2 anúncios ou mais)", {"1 mês": 21, "3 meses": 63})
    # do salto até a volta: quanto a cota andou no período inteiro
    lin = []
    for e in s.itertuples():
        i1 = dia_de_entrada(datas, e.entrega_volta)
        if i1 >= len(datas) or i1 <= e.i0:
            continue
        serie = arr[e.i0:i1 + 1, col[e.ticker]]
        if np.isnan(serie).any():
            continue
        lin.append({"pico": serie.max() / serie[0] - 1, "na_volta": serie[-1] / serie[0] - 1, "dias": i1 - e.i0, "dia_pico": int(serie.argmax())})
    d = pd.DataFrame(lin)
    if len(d):
        print(f"Do anúncio do salto até o anúncio da volta ({len(d)} casos, {d['dias'].median():.0f} pregões na mediana): pico mediano {d['pico'].median()*100:+.1f}% no {d['dia_pico'].median():.0f}º pregão | "
              f"cota no dia da volta {d['na_volta'].median()*100:+.1f}% | pico de 10% ou mais em {(d['pico'] >= .10).mean():.0%} | terminou abaixo da entrada em {(d['na_volta'] < 0).mean():.0%}")
    ev.to_parquet(config.DADOS / "saltos_anunciados.parquet")


if __name__ == "__main__":
    main()
