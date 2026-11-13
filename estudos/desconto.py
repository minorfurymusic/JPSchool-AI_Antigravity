"""Estratégia "desconto com renda estável", testada DIA A DIA (2018-2026).

Ideia do dono: comprar fundo com cota bem abaixo do valor patrimonial, rendimento estável e acima da Selic,
sem notícia ruim interna; não vender por queda de preço; vender quando a cota sobe a ponto de o rendimento
sobre o preço atual encostar na Selic, ou quando o fundo piora por dentro.

Tudo é decidido só com o que era conhecido no dia:
  * rendimento: último aviso do FNET, valendo a partir do pregão seguinte à entrega;
  * valor patrimonial e patrimônio: informe mensal da CVM, usado só 75 dias depois do mês de referência;
  * liquidez: média de 60 pregões até a véspera; Selic: meta do dia.

Entrada: na abertura do pregão seguinte ao dia em que todas as condições valem.
Saída (o que vier primeiro):
  * ALVO: ordem de venda no preço em que rendimento x 12 / preço = Selic + margem de saída
          (recalculada quando o rendimento ou a Selic mudam; executa se a máxima do dia tocar);
  * CORTE: novo aviso 15% ou mais abaixo do rendimento da entrada -> vende na abertura seguinte;
  * NOTÍCIA: fato relevante em que o fundo declara redução de rendimento -> vende na abertura seguinte;
  * PRAZO: 2 anos.
Não há limite de perda pelo preço.

Uso: PYTHONPATH=. .venv/bin/python estudos/desconto.py
"""
import json
import warnings

import duckdb
import numpy as np
import pandas as pd

from estudos import dias as D
from estudos.anuncio_real import anuncios
from fii import config, fnet

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# margens em pontos percentuais ao ano sobre a Selic do dia.
# Preço sobre valor patrimonial abaixo de 0,30 é tratado como dado suspeito (HSAF11 apareceu com 0,08) e fica de fora.
PERFIS = {
    "conservador": {"pl_min": 400e6, "liq": 500_000, "pvp": (0.80, 1.00), "avisos": 12, "variacao": 1.10, "entrada": 1.0, "saida": -1.0,
                    "descricao": "fundo grande, rendimento muito regular, desconto moderado"},
    "moderado": {"pl_min": 100e6, "liq": 200_000, "pvp": (0.30, 0.90), "avisos": 6, "variacao": 1.15, "entrada": 2.0, "saida": 0.0,
                 "descricao": "fundo médio, rendimento regular, desconto de 10% ou mais"},
    "agressivo": {"pl_min": 50e6, "liq": 100_000, "pvp": (0.30, 0.75), "avisos": 6, "variacao": 1.15, "entrada": 4.0, "saida": 0.0,
                  "descricao": "fundo menor, desconto de 25% ou mais, rendimento bem acima da Selic"},
}
CORTE = 0.85
PRAZO = 504
INICIO = "2018-01-01"


def preparar():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    cf = duckdb.connect(str(fnet.BANCO), read_only=True)
    P = D.Precos(con)
    N, T = len(P.datas), len(P.tickers)
    vol = con.execute("select c.ticker, c.data, c.volume from cotacoes c join (select distinct ticker from mensal) using(ticker)").df()
    vol = vol.pivot(index="data", columns="ticker", values="volume").reindex(index=P.datas, columns=P.tickers).fillna(0)
    P.vol60 = vol.rolling(60, min_periods=20).mean().shift(1).to_numpy()
    sel = pd.DataFrame(json.load(open(config.DADOS / "bruto" / "sgs_432.json")))
    sel["data"] = pd.to_datetime(sel["data"], dayfirst=True)
    P.selic = sel.set_index("data")["valor"].astype(float).reindex(P.datas, method="ffill").to_numpy()

    # rendimento conhecido em cada dia e regularidade dos últimos avisos
    a = anuncios(con, cf)
    a = a[a["ticker"].isin(P.col)].sort_values(["ticker", "entrega"])
    P.div = np.full((N, T), np.nan)
    P.var6 = np.full((N, T), np.nan)
    P.var12 = np.full((N, T), np.nan)
    P.avisos = {}
    for tk, g in a.groupby("ticker"):
        j = P.col[tk]
        g = g.reset_index(drop=True)
        v = g["valor_aj"].to_numpy()
        conhecido = [P.pregao_seguinte(e) for e in g["entrega"]]
        base = [P.datas.searchsorted(pd.Timestamp(d)) for d in g["data_base"]]
        gaps = g["entrega"].diff().dt.days
        P.avisos[tk] = list(zip(conhecido, base, v))
        for k in range(len(g)):
            i0 = conhecido[k]
            i1 = conhecido[k + 1] if k + 1 < len(g) else N
            if i0 >= N:
                continue
            P.div[i0:i1, j] = v[k]
            for n, alvo in ((6, P.var6), (12, P.var12)):
                if k + 1 >= n and gaps.iloc[k - n + 2:k + 1].between(15, 45).all() and v[k - n + 1:k + 1].min() > 0:
                    alvo[i0:i1, j] = v[k - n + 1:k + 1].max() / v[k - n + 1:k + 1].min()
    # valor patrimonial e patrimônio, disponíveis 75 dias depois do mês de referência
    m = con.execute("select ticker, mes, vp_aj, pl from mensal where vp_aj is not null and pl is not null order by ticker, mes").df()
    P.vp = np.full((N, T), np.nan)
    P.pl = np.full((N, T), np.nan)
    for tk, g in m.groupby("ticker"):
        if tk not in P.col:
            continue
        j = P.col[tk]
        ini = [P.datas.searchsorted(x + pd.Timedelta(days=75)) for x in g["mes"]]
        for k in range(len(g)):
            i0, i1 = ini[k], (ini[k + 1] if k + 1 < len(g) else min(N, ini[k] + 130))  # informe velho demais deixa de valer
            if i0 < N:
                P.vp[i0:i1, j] = g["vp_aj"].iloc[k]
                P.pl[i0:i1, j] = g["pl"].iloc[k]
    # amortização relevante nos últimos 12 meses (fundo devolvendo patrimônio) e fato relevante de redução
    am = cf.execute("select isin, data_base, valor from rendimentos_fnet where tipo='Amortizacao' and valor > 0 and data_base is not null").df()
    isin = con.execute("select isin, last(ticker order by data) ticker from cotacoes group by 1").df()
    am = am.merge(isin, on="isin")
    P.amort = np.zeros((N, T), bool)
    for r in am.itertuples():
        if r.ticker in P.col:
            i = P.datas.searchsorted(pd.Timestamp(r.data_base))
            j = P.col[r.ticker]
            preco = P.F[min(i, N - 1), j]
            if i < N and preco and r.valor / preco >= 0.05:
                P.amort[i:i + 252, j] = True
    f = pd.read_parquet(config.DADOS / "fatos_classificados.parquet")
    P.ruim = {}
    for r in f[f["imp_direcao"] == -1].itertuples():
        P.ruim.setdefault(r.ticker, []).append(int(r.i0))
    # mercado: mediana do retorno diário dos fundos com liquidez, mais o rendimento mediano do dia
    ret = P.F[1:] / P.F[:-1] - 1
    liq = P.vol60[1:] >= 100_000
    med = np.nanmedian(np.where(liq & (np.abs(ret) < 0.2), ret, np.nan), axis=1)
    dy = np.nanmedian(np.where(liq, P.div[1:] * 12 / P.F[1:], np.nan), axis=1)
    P.mercado = np.concatenate([[1.0], np.cumprod(1 + np.nan_to_num(med) + np.nan_to_num(dy, nan=0.10) / 252)])
    return P


def operar(P, perfil):
    c = PERFIS[perfil]
    N = len(P.datas)
    i_ini = P.datas.searchsorted(pd.Timestamp(INICIO))
    var = P.var12 if c["avisos"] == 12 else P.var6
    ops = []
    for tk, j in P.col.items():
        if tk not in P.avisos:
            continue
        ontem = np.roll(P.F[:, j], 1)
        dy = P.div[:, j] * 12 / ontem
        pvp = ontem / P.vp[:, j]
        cond = ((dy * 100 >= P.selic + c["entrada"]) & (pvp >= c["pvp"][0]) & (pvp <= c["pvp"][1]) & (var[:, j] <= c["variacao"])
                & (P.pl[:, j] >= c["pl_min"]) & (P.vol60[:, j] >= c["liq"]) & ~P.amort[:, j])
        ruins = sorted(P.ruim.get(tk, []))
        i = max(i_ini, 1)
        while i < N:
            if not cond[i] or np.isnan(P.A[i, j]) or not P.negociou[i, j] or any(i - 60 <= r <= i for r in ruins):
                i += 1
                continue
            ent, div0, k = P.A[i, j], P.div[i, j], i
            motivo, saida = None, None
            while k < N:
                if k > i:
                    a = P.A[k, j]
                    if not np.isnan(a):
                        if k in ruins:
                            motivo, saida = "fundo declarou redução de rendimento", a
                        elif P.div[k, j] <= CORTE * div0:
                            motivo, saida = "rendimento cortado 15% ou mais", a
                        if motivo:
                            break
                if not np.isnan(P.H[k, j]) and not np.isnan(P.div[k, j]):
                    alvo = P.div[k, j] * 12 / ((P.selic[k] + c["saida"]) / 100)
                    if k > i and P.A[k, j] >= alvo:
                        # o preço não precisa ter subido: a Selic subindo ou o rendimento caindo um pouco também derrubam o alvo
                        motivo = "alvo: cota subiu até o rendimento encostar na Selic" if P.A[k, j] > ent else "rendimento ficou abaixo da Selic sem a cota subir"
                        saida = P.A[k, j]
                        break
                    if P.H[k, j] >= alvo and alvo > ent:
                        motivo, saida = "alvo: cota subiu até o rendimento encostar na Selic", alvo
                        break
                if k - i >= PRAZO and not np.isnan(P.F[k, j]):
                    motivo, saida = "prazo de 2 anos", P.F[k, j]
                    break
                k += 1
            if motivo is None:
                k = N - 1
                ult = P.F[:, j][~np.isnan(P.F[:, j])]
                motivo, saida = "ainda aberta", float(ult[-1])
            fim_direito = k if motivo.startswith("prazo") or motivo == "ainda aberta" else k - 1  # vendeu no dia k: não tem o direito do dia k
            rend = sum(v for conhecido, base, v in P.avisos[tk] if i <= base <= fim_direito)
            trecho_h, trecho_l = P.H[i:k + 1, j], P.L[i:k + 1, j]
            ops.append({"fundo": tk, "entrada": P.datas[i], "preco_entrada": ent, "rend_anual_entrada": div0 * 12 / ent, "pvp_entrada": ent / P.vp[i, j],
                        "selic_entrada": P.selic[i], "saida": P.datas[k], "preco_saida": saida, "pregoes": k - i, "motivo": motivo,
                        "cota": saida / ent - 1, "rendimentos": rend / ent, "total": saida / ent - 1 + rend / ent,
                        "mercado": P.mercado[k] / P.mercado[i] - 1, "maior_preco": np.nanmax(trecho_h) / ent - 1, "menor_preco": np.nanmin(trecho_l) / ent - 1,
                        "dia_do_maior": int(np.nanargmax(trecho_h)), "maior_60_depois": (np.nanmax(P.H[k:k + 61, j]) / saida - 1) if k + 1 < N and not np.all(np.isnan(P.H[k:k + 61, j])) else np.nan})
            i = k + 60  # dois meses antes de voltar ao mesmo fundo
    return pd.DataFrame(ops)


def resumo(o, titulo):
    if o.empty:
        print(f"\n--- {titulo}: nenhuma operação ---")
        return
    q = lambda s, p: s.quantile(p) * 100
    ano = (1 + o["total"]) ** (252 / o["pregoes"].clip(lower=5)) - 1
    print(f"\n--- {titulo}: {len(o)} operações em {o['fundo'].nunique()} fundos ---")
    print(f"Na entrada (típico): rendimento {o['rend_anual_entrada'].median():.1%} ao ano, Selic {o['selic_entrada'].median():.2f}%, preço sobre valor patrimonial {o['pvp_entrada'].median():.2f}")
    print(f"Tempo na operação: típico {o['pregoes'].median():.0f} pregões (pessimista {o['pregoes'].quantile(.75):.0f}, otimista {o['pregoes'].quantile(.25):.0f})")
    print(f"Resultado total (cota + rendimentos): pessimista {q(o['total'], .25):+.1f}% | típico {q(o['total'], .5):+.1f}% | otimista {q(o['total'], .75):+.1f}% | pior 1 em 10 {q(o['total'], .1):+.1f}% | com ganho {(o['total'] > 0).mean():.0%}")
    print(f"   só a cota: típico {q(o['cota'], .5):+.1f}% | só rendimentos: típico {q(o['rendimentos'], .5):+.1f}% | ao ano (típico): {ano.median()*100:+.1f}%")
    print(f"   mercado no mesmo período: típico {q(o['mercado'], .5):+.1f}% | operações que renderam mais que o mercado: {(o['total'] > o['mercado']).mean():.0%} | diferença típica {((o['total'] - o['mercado']).median())*100:+.1f} pontos")
    print(f"No caminho: maior preço típico {q(o['maior_preco'], .5):+.1f}% no {o['dia_do_maior'].median():.0f}º pregão | menor preço típico {q(o['menor_preco'], .5):+.1f}% | pior 1 em 10 chegou a {q(o['menor_preco'], .1):+.1f}%")
    t = o.groupby("motivo").agg(operações=("total", "size"), pregões=("pregoes", "median"), total_típico=("total", lambda s: s.median() * 100), cota_típica=("cota", lambda s: s.median() * 100),
                                com_ganho=("total", lambda s: (s > 0).mean()), acima_do_mercado=("total", lambda s: ((s - o.loc[s.index, "mercado"]) > 0).mean()),
                                subiu_mais_depois=("maior_60_depois", lambda s: s.median() * 100)).round(2)
    print(t.to_string())
    a = o.assign(ano=o["entrada"].dt.year).groupby("ano").agg(operações=("total", "size"), total_típico=("total", lambda s: s.median() * 100),
                                                             mercado=("mercado", lambda s: s.median() * 100), com_ganho=("total", lambda s: (s > 0).mean()),
                                                             pregões=("pregoes", "median")).round(1)
    print("Por ano de entrada:")
    print(a.T.to_string())


def main():
    P = preparar()
    print("PERFIS:")
    for n, c in PERFIS.items():
        print(f"  {n}: {c['descricao']} | patrimônio >= R$ {c['pl_min']/1e6:.0f} mi | liquidez >= R$ {c['liq']:,.0f}/dia | preço sobre valor patrimonial de {c['pvp'][0]:.2f} a {c['pvp'][1]:.2f} | "
              f"últimos {c['avisos']} avisos com variação até {c['variacao']-1:.0%} | entra com rendimento >= Selic {c['entrada']:+.0f} pt | ordem de venda onde o rendimento = Selic {c['saida']:+.0f} pt")
    for n in PERFIS:
        o = operar(P, n)
        resumo(o, n.upper())
        if len(o):
            o.round(4).to_csv(config.RAIZ / "docs" / f"desconto_{n}.csv", index=False)
            v = o[o["entrada"] >= "2026-01-01"]
            if len(v):
                print("Operações com entrada em 2026:")
                print(v[["fundo", "entrada", "preco_entrada", "rend_anual_entrada", "pvp_entrada", "saida", "preco_saida", "pregoes", "motivo", "cota", "rendimentos", "total", "maior_preco", "menor_preco"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
