"""Simulação de carteira: R$ 10.000 seguindo os gatilhos, em três perfis.

Os perfis foram escritos ANTES de rodar 2026 e não foram ajustados pelo resultado.
As mesmas regras rodam em 2018-2025 para mostrar se 2026 foi regra ou acaso.

Gatilhos de compra (todos conhecidos na véspera; compra na ABERTURA do pregão seguinte):
  FR_AUMENTO        fato relevante em que o fundo declara aumento de rendimento
  FR_VALOR          fato relevante "bom" que informa valor por cota de 3% do preço ou mais
  FR_ASSUNTO        fato relevante "bom" pelo assunto (venda com ganho, locação nova...), sem declaração
  AVISO_SALTO       aviso de rendimento 25% ou mais acima da mediana dos 6 anteriores
  AVISO_CONFIRMADO  o aviso seguinte ao salto continuou alto
Gatilho de saída antecipada: fato relevante em que o fundo declara REDUÇÃO de rendimento (vende na abertura seguinte).

Execução: ordem de venda no alvo é executada se a máxima do dia tocar o preço; o limite de perda,
se a mínima tocar. Se os dois forem tocados no mesmo dia, vale a perda (não sei a ordem dentro do dia).
Abertura além do preço da ordem executa na abertura.

Custos: corretagem zero; taxas da B3 de 0,03% por operação; imposto de 20% sobre o ganho líquido do mês
em vendas de FII, com prejuízo compensando ganhos futuros; rendimentos isentos. Caixa parado rende a
Selic do dia, descontados 22,5% de imposto (aproximação de um fundo de liquidez diária).

Uso: PYTHONPATH=. .venv/bin/python estudos/simulacao.py
"""
import json
import warnings

import duckdb
import numpy as np
import pandas as pd

from estudos import dias as D
from fii import config, fnet

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
CAPITAL = 10_000.0
TAXA_B3 = 0.0003
IMPOSTO = 0.20
IMPOSTO_CAIXA = 0.225
ESPERA = 20  # pregões sem recomprar o mesmo fundo depois de vender

PERFIS = {
    "conservador": {"gatilhos": ["FR_AUMENTO", "AVISO_CONFIRMADO"], "liquidez": 1_000_000, "fatia": 0.10, "maximo": 5,
                    "alvo": 0.03, "perda": -0.03, "prazo": 15,
                    "descricao": "só o sinal mais forte, fundos grandes, 10% por operação, sai cedo"},
    "moderado": {"gatilhos": ["FR_AUMENTO", "FR_VALOR", "AVISO_CONFIRMADO", "AVISO_SALTO"], "liquidez": 300_000, "fatia": 0.20, "maximo": 5,
                 "alvo": 0.05, "perda": -0.05, "prazo": 20,
                 "descricao": "sinais fortes e aviso de salto, 20% por operação"},
    "agressivo": {"gatilhos": ["FR_AUMENTO", "FR_VALOR", "AVISO_SALTO", "AVISO_CONFIRMADO", "FR_ASSUNTO"], "liquidez": 200_000, "fatia": 0.33,
                  "maximo": 3, "alvo": 0.10, "perda": -0.08, "prazo": 30,
                  "descricao": "qualquer sinal, 33% por operação, alvo alto e prazo longo"},
}
BONS = ["rendimento_aumento", "venda_com_ganho", "recebimento", "locacao_nova"]


def preparar():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    cf = duckdb.connect(str(fnet.BANCO), read_only=True)
    P = D.Precos(con)
    vol = con.execute("select c.ticker, c.data, c.volume from cotacoes c join (select distinct ticker from mensal) using(ticker)").df()
    vol = vol.pivot(index="data", columns="ticker", values="volume").reindex(index=P.datas, columns=P.tickers).fillna(0)
    P.vol60 = vol.rolling(60, min_periods=20).mean().shift(1).to_numpy()  # liquidez conhecida até a véspera

    f = pd.read_parquet(config.DADOS / "fatos_classificados.parquet")
    f = f[~f["repetido"]]
    sinais = []
    for r in f.itertuples():
        bom = r.tipo in BONS and r.sentido == "alta"
        if r.imp_direcao == 1:
            sinais.append((r.i0, r.ticker, "FR_AUMENTO", r.quando))
        elif bom and pd.notna(r.pct_cota) and r.pct_cota >= 0.03:
            sinais.append((r.i0, r.ticker, "FR_VALOR", r.quando))
        elif bom:
            sinais.append((r.i0, r.ticker, "FR_ASSUNTO", r.quando))
        if r.imp_direcao == -1:
            sinais.append((r.i0, r.ticker, "FR_REDUCAO", r.quando))
    s = pd.read_parquet(config.DADOS / "saltos_anunciados.parquet")
    for r in s.itertuples():
        sinais.append((P.pregao_seguinte(r.entrega), r.ticker, "AVISO_SALTO", r.entrega))
        if r.alto_1 and pd.notna(r.entrega_1):
            sinais.append((P.pregao_seguinte(r.entrega_1), r.ticker, "AVISO_CONFIRMADO", r.entrega_1))
    sinais = pd.DataFrame(sinais, columns=["i0", "ticker", "gatilho", "quando"])
    sinais = sinais[sinais["ticker"].isin(P.col)]

    # rendimentos e amortizações por papel: quem tem a cota no fechamento da data-base recebe na data de pagamento
    r = cf.execute("select isin, tipo, data_base, valor, data_pagamento, versao, doc_id from rendimentos_fnet where valor > 0 and data_base is not null").df()
    isin = con.execute("select isin, last(ticker order by data) ticker from cotacoes group by 1").df()
    r = r.merge(isin, on="isin")
    ult = r.groupby(["ticker", "data_base", "tipo"])["versao"].transform("max")
    r = r[r["versao"] == ult].groupby(["ticker", "data_base", "tipo"]).agg(valor=("valor", "sum"), pagamento=("data_pagamento", "max")).reset_index()
    prov = {}
    for x in r.itertuples():
        ib = P.datas.searchsorted(pd.Timestamp(x.data_base))
        if ib < len(P.datas) and P.datas[ib] == pd.Timestamp(x.data_base) and x.ticker in P.col:
            ip = P.datas.searchsorted(pd.Timestamp(x.pagamento)) if pd.notna(x.pagamento) else ib
            prov.setdefault(ib, []).append((x.ticker, x.valor, max(ip, ib), x.tipo))
    sel = pd.DataFrame(json.load(open(config.DADOS / "bruto" / "sgs_432.json")))
    sel["data"] = pd.to_datetime(sel["data"], dayfirst=True)
    sel = sel.set_index("data")["valor"].astype(float).reindex(P.datas, method="ffill").to_numpy()
    P.caixa_dia = ((1 + sel / 100) ** (1 / 252) - 1) * (1 - IMPOSTO_CAIXA)
    return P, sinais, prov


def simular(P, sinais, prov, perfil, inicio, fim, capital=CAPITAL):
    cfg = PERFIS[perfil]
    i_ini, i_fim = P.datas.searchsorted(pd.Timestamp(inicio)), P.datas.searchsorted(pd.Timestamp(fim), side="right") - 1
    por_dia = {i: g for i, g in sinais[(sinais["i0"] >= i_ini) & (sinais["i0"] <= i_fim)].groupby("i0")}
    ordem = {g: k for k, g in enumerate(cfg["gatilhos"])}
    caixa, pos, ops, a_receber, curva = capital, {}, [], [], []
    ultimo_fim, mes_ganho, prejuizo, imposto_total, recebido, ignorados = {}, 0.0, 0.0, 0.0, 0.0, 0

    def vender(tk, i, preco, motivo):
        nonlocal caixa, mes_ganho
        p = pos.pop(tk)
        bruto = p["qtd"] * preco
        taxa = bruto * TAXA_B3
        caixa += bruto - taxa
        ganho = bruto - taxa - p["custo"]
        mes_ganho += ganho
        ultimo_fim[tk] = i
        ops.append({"fundo": tk, "gatilho": p["gatilho"], "anuncio": str(p["quando"])[:16], "entrada": str(P.datas[p["i"]].date()), "cotas": p["qtd"],
                    "preco_entrada": round(p["preco"], 2), "aplicado": round(p["custo"], 2), "saida": str(P.datas[i].date()), "preco_saida": round(preco, 2),
                    "pregoes": i - p["i"], "motivo": motivo, "ganho_na_cota": round(ganho, 2), "rendimento_recebido": round(p["rend"], 2),
                    "resultado": round(ganho + p["rend"], 2), "resultado_pct": round((ganho + p["rend"]) / p["custo"] * 100, 2)})

    for i in range(i_ini, i_fim + 1):
        caixa *= 1 + P.caixa_dia[i]
        for x in [x for x in a_receber if x[0] == i]:  # rendimentos caem na conta na data de pagamento
            caixa += x[1]
            recebido += x[1]
        a_receber = [x for x in a_receber if x[0] != i]
        hoje = por_dia.get(i)
        # 1) saída por notícia de redução: na abertura
        if hoje is not None:
            for r in hoje[hoje["gatilho"] == "FR_REDUCAO"].itertuples():
                if r.ticker in pos and not np.isnan(P.A[i, P.col[r.ticker]]):
                    vender(r.ticker, i, P.A[i, P.col[r.ticker]], "fundo declarou redução de rendimento")
        # 2) ordens que estavam abertas: salto na abertura, depois limite de perda, depois alvo
        for tk in list(pos):
            j, p = P.col[tk], pos[tk]
            a, h, l = P.A[i, j], P.H[i, j], P.L[i, j]
            if np.isnan(a):
                continue
            if a <= p["perda"]:
                vender(tk, i, a, "abriu abaixo do limite de perda")
            elif a >= p["alvo"]:
                vender(tk, i, a, "abriu acima do alvo")
            elif l <= p["perda"]:
                vender(tk, i, p["perda"], "limite de perda")
            elif h >= p["alvo"]:
                vender(tk, i, p["alvo"], "alvo atingido")
        # 3) compras do dia, na abertura, por ordem de força do gatilho
        if hoje is not None:
            cand = hoje[hoje["gatilho"].isin(ordem)].assign(o=lambda d: d["gatilho"].map(ordem)).sort_values("o").drop_duplicates("ticker")
            for r in cand.itertuples():
                j = P.col[r.ticker]
                a = P.A[i, j]
                if r.ticker in pos or i - ultimo_fim.get(r.ticker, -999) < ESPERA or np.isnan(a) or a <= 0 or not P.negociou[i, j]:
                    continue
                if not (P.vol60[i, j] >= cfg["liquidez"]):
                    continue
                patrimonio = caixa + sum(q["qtd"] * q["ult"] for q in pos.values())
                qtd = int(min(cfg["fatia"] * patrimonio, caixa * 0.999) // (a * (1 + TAXA_B3)))
                if len(pos) >= cfg["maximo"] or qtd < 1:
                    ignorados += 1
                    continue
                custo = qtd * a * (1 + TAXA_B3)
                caixa -= custo
                pos[r.ticker] = {"i": i, "qtd": qtd, "preco": a, "custo": custo, "gatilho": r.gatilho, "quando": r.quando,
                                 "alvo": a * (1 + cfg["alvo"]), "perda": a * (1 + cfg["perda"]), "rend": 0.0, "ult": a}
                # no dia da compra a ordem já está no livro: vale máxima e mínima do próprio dia
                h, l = P.H[i, j], P.L[i, j]
                if l <= pos[r.ticker]["perda"]:
                    vender(r.ticker, i, pos[r.ticker]["perda"], "limite de perda")
                elif h >= pos[r.ticker]["alvo"]:
                    vender(r.ticker, i, pos[r.ticker]["alvo"], "alvo atingido")
        for tk, q in pos.items():  # último preço conhecido (dia sem negócio mantém o anterior)
            if not np.isnan(P.F[i, P.col[tk]]):
                q["ult"] = P.F[i, P.col[tk]]
        # 4) fechamento: direito a rendimento e prazo
        for tk, valor, ipag, tipo in prov.get(i, []):
            if tk in pos:
                pos[tk]["rend"] += pos[tk]["qtd"] * valor
                a_receber.append((min(ipag, i_fim), pos[tk]["qtd"] * valor))
        for tk in list(pos):
            if i - pos[tk]["i"] >= cfg["prazo"] and not np.isnan(P.F[i, P.col[tk]]):
                vender(tk, i, P.F[i, P.col[tk]], "prazo esgotado")
        if i == i_fim:
            for tk in list(pos):
                vender(tk, i, pos[tk]["ult"], "fim do período")
            caixa += sum(x[1] for x in a_receber)
            recebido += sum(x[1] for x in a_receber)
        # 5) imposto do mês: 20% do ganho líquido, compensando prejuízo anterior
        if i == i_fim or P.datas[i + 1].month != P.datas[i].month:
            base = mes_ganho - prejuizo
            if base > 0:
                caixa -= base * IMPOSTO
                imposto_total += base * IMPOSTO
                prejuizo = 0.0
            else:
                prejuizo = -base
            mes_ganho = 0.0
        curva.append((P.datas[i], caixa + sum(q["qtd"] * q["ult"] for q in pos.values())))
    ops = pd.DataFrame(ops)
    curva = pd.Series(dict(curva))
    return {"final": caixa, "ops": ops, "curva": curva, "imposto": imposto_total, "recebido": recebido, "ignorados": ignorados,
            "prejuizo_a_compensar": prejuizo, "pior_queda": float((curva / curva.cummax() - 1).min())}


def referencias(P, prov, inicio, fim, capital=CAPITAL):
    """Duas comparações: deixar tudo no caixa; comprar os 30 fundos mais negociados e não mexer."""
    i_ini, i_fim = P.datas.searchsorted(pd.Timestamp(inicio)), P.datas.searchsorted(pd.Timestamp(fim), side="right") - 1
    caixa = capital * np.prod(1 + P.caixa_dia[i_ini:i_fim + 1])
    liq = [(P.vol60[i_ini, j], t) for t, j in P.col.items() if not np.isnan(P.A[i_ini, j]) and not np.isnan(P.F[i_fim, j]) and P.vol60[i_ini, j] > 0]
    top = [t for _, t in sorted(liq, reverse=True)[:30]]
    total = 0.0
    for t in top:
        j = P.col[t]
        q = (capital / len(top)) / P.A[i_ini, j]
        rend = sum(q * v for i in range(i_ini, i_fim + 1) for tk, v, _, _ in prov.get(i, []) if tk == t)
        total += q * P.F[i_fim, j] + rend
    return caixa, total


def resumo(nome, r, capital=CAPITAL):
    o = r["ops"]
    return {"perfil": nome, "final R$": r["final"], "resultado %": (r["final"] / capital - 1) * 100, "operações": len(o),
            "com ganho": (o["resultado"] > 0).mean() if len(o) else np.nan, "resultado médio por operação %": o["resultado_pct"].mean() if len(o) else np.nan,
            "pregões por operação": o["pregoes"].median() if len(o) else np.nan, "rendimentos recebidos R$": r["recebido"], "imposto pago R$": r["imposto"],
            "pior queda do patrimônio %": r["pior_queda"] * 100, "sinais sem dinheiro ou vaga": r["ignorados"]}


def main():
    P, sinais, prov = preparar()
    print("PERFIS (definidos antes de rodar):")
    for n, c in PERFIS.items():
        print(f"  {n}: {c['descricao']} | compra em: {', '.join(c['gatilhos'])} | liquidez mínima R$ {c['liquidez']:,.0f}/dia | {c['fatia']:.0%} do patrimônio por operação, "
              f"até {c['maximo']} ao mesmo tempo | ordem de venda em +{c['alvo']:.0%} | limite de perda {c['perda']:.0%} | prazo {c['prazo']} pregões")
    ini, fim = "2026-01-01", "2026-10-31"
    s26 = sinais[(sinais["quando"] >= ini) & (sinais["quando"] <= fim)]
    print(f"\nSinais em 2026 ({ini} a {fim}): {s26['gatilho'].value_counts().to_dict()}")
    print("\n" + "=" * 110 + f"\nR$ {CAPITAL:,.0f} DE {ini} A {fim}\n" + "=" * 110)
    res = {n: simular(P, sinais, prov, n, ini, fim) for n in PERFIS}
    cx, cesta = referencias(P, prov, ini, fim)
    print(pd.DataFrame([resumo(n, r) for n, r in res.items()]).round(2).to_string(index=False))
    print(f"Comparações: tudo no caixa R$ {cx:,.2f} ({(cx/CAPITAL-1)*100:+.2f}%) | 30 fundos mais negociados, comprados em {ini[:4]} e mantidos, com rendimentos: R$ {cesta:,.2f} ({(cesta/CAPITAL-1)*100:+.2f}%)")
    for n, r in res.items():
        o = r["ops"]
        print(f"\n--- {n.upper()}: operações ---")
        if len(o):
            print(o.to_string(index=False))
            print("Por gatilho:"); print(o.groupby("gatilho").agg(operações=("resultado", "size"), com_ganho=("resultado", lambda s: (s > 0).mean()), resultado_R=("resultado", "sum"), médio_pct=("resultado_pct", "mean")).round(2).to_string())
            print("Por motivo de saída:"); print(o.groupby("motivo").agg(operações=("resultado", "size"), resultado_R=("resultado", "sum"), médio_pct=("resultado_pct", "mean")).round(2).to_string())
            o.to_csv(config.RAIZ / "docs" / f"simulacao_2026_{n}.csv", index=False)
        m = r["curva"].resample("ME").last()
        print("Patrimônio no fim de cada mês: " + " | ".join(f"{d:%m/%y} {v:,.0f}" for d, v in m.items()))

    print("\n" + "=" * 110 + "\nMESMAS REGRAS, ANO A ANO (R$ 10.000 em 1º de janeiro, até 31 de dezembro)\n" + "=" * 110)
    lin = []
    for ano in range(2018, 2026):
        a, b = f"{ano}-01-01", f"{ano}-12-31"
        cx, cesta = referencias(P, prov, a, b)
        l = {"ano": ano, "caixa %": (cx / CAPITAL - 1) * 100, "30 fundos mantidos %": (cesta / CAPITAL - 1) * 100}
        for n in PERFIS:
            r = simular(P, sinais, prov, n, a, b)
            l[f"{n} %"] = (r["final"] / CAPITAL - 1) * 100
            l[f"{n} ops"] = len(r["ops"])
            l[f"{n} pior queda %"] = r["pior_queda"] * 100
        lin.append(l)
    t = pd.DataFrame(lin)
    print(t.round(1).to_string(index=False))
    print("Média dos 8 anos: " + " | ".join(f"{c}: {t[c].mean():+.1f}" for c in t.columns if c.endswith("%") and "queda" not in c))
    print("Anos em que o perfil rendeu mais que o caixa: " + " | ".join(f"{n}: {(t[f'{n} %'] > t['caixa %']).sum()} de {len(t)}" for n in PERFIS))
    print("Anos em que o perfil rendeu mais que os 30 fundos mantidos: " + " | ".join(f"{n}: {(t[f'{n} %'] > t['30 fundos mantidos %']).sum()} de {len(t)}" for n in PERFIS))


if __name__ == "__main__":
    main()
