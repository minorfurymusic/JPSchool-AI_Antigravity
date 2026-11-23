"""Motor de análise gráfica + fundamentos de um fundo imobiliário (Skill `analise-grafica`, 18/11/2026).
O mesmo cálculo serve às conversas (linha de comando) e à página do artefato "Radar Gráfico de FIIs".

    PYTHONPATH=. python3 estudos/analise_grafica.py TRXF11 [OUTRO11 ...]     leitura item por item no terminal
    PYTHONPATH=. python3 estudos/analise_grafica.py --todos --saida PASTA     dados de todos os fundos para a página
    PYTHONPATH=. python3 estudos/analise_grafica.py --pine TRXF11 --entrada 53,99   script do TradingView (radar/pine/TRXF11.pine)

Fontes: fundos da base = planilhas/precos_AAAA.csv (preços ajustados por desdobramento); fundos fora da base =
planilhas/tecnico/b3_cotahist_fii_2019_2026.csv.gz (arquivo oficial da B3, preços SEM ajuste: um salto de mais de 35% num
dia é marcado como possível desdobramento). Mercado de fundos = planilhas/mercado.csv.
Itens (todos só com dados até o último pregão):
  1 suportes e resistências: pivôs de 5% em todo o histórico agrupados em faixas de 2,5%; nível com 2+ toques
  2 médias 21/50/200, inclinação de 20 pregões, cruzamento 21×50
  3 IFR 14 e 2 (Wilder); divergência de alta/baixa nos 2 últimos fundos/topos de 5%
  4 MACD 12/26/9 (histograma, cruzamento, divergência)
  5 estocástico 14/3/3
  6 Bollinger 20/2 (posição e largura contra a média de 120 pregões)
  7 candles dos últimos 10 pregões (martelo, engolfo, piercing, estrela da manhã, estrela cadente, engolfo de baixa,
    nuvem negra, doji) e saltos de preço (gap) abertos
  8 volume: dias de volume >= 2× a média de 60 (clímax), OBV (inclinação de 20 pregões)
  9 volume por faixa de preço (252 pregões, 30 faixas): faixa de maior volume e faixa de 70% do volume; preço médio
    ponderado pelo volume (VWAP) desde o topo e desde o fundo dos últimos 252 pregões
  10 Fibonacci da queda (ou da alta) dos últimos 252 pregões
  11 força relativa contra o mercado de fundos (20 e 60 pregões)
  12 zonas de liquidez (deduzidas do desenho do preço, sem livro de ofertas): fundos/topos iguais (pivôs a até 1%),
    varridas (mínima fura um fundo anterior e o fechamento volta acima), vazios de preço não preenchidos, último bloco
    de alta antes de uma queda de 8%+ em 10 pregões
  13 ondas de Elliott (SUBJETIVO): pivôs de 8%; teste das regras de impulso (onda 2 não passa da origem; onda 3 não é a
    menor; onda 4 não entra na 1) e de correção A-B-C; preço que invalida
Fundamentos: classe pela carteira, preço ÷ patrimônio, rendimento, cobertura, avaliação de saúde, distância da média
de 200 (Kairi Padrão), candidato do Papel Padrão.
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
JANELA = 750          # pregões mostrados no gráfico (~3 anos)


@lru_cache(maxsize=1)
def _base():
    P = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{a}.csv", **OP) for a in range(2017, 2027)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    return {f: x.set_index("data").sort_index() for f, x in P.groupby("fundo")}


@lru_cache(maxsize=1)
def _b3():
    X = pd.read_csv(RAIZ / "planilhas/tecnico/b3_cotahist_fii_2019_2026.csv.gz", **OP)
    X["data"] = pd.to_datetime(X["data"])
    return {f: x.set_index("data").sort_index() for f, x in X.groupby("ticker")}


@lru_cache(maxsize=1)
def _mercado():
    M = pd.read_csv(RAIZ / "planilhas/mercado.csv", **OP)
    M["data"] = pd.to_datetime(M["data"], dayfirst=True)
    return M.set_index("data")["indice_mercado"]


def serie(f):
    """(DataFrame com abertura, maxima, minima, fechamento, volume só dos pregões com negócio, fonte, avisos)."""
    B = _base()
    if f in B:
        x = B[f]
        x = x[x["negociou (1/0)"] == 1]
        s = x[["abertura", "maxima", "minima", "fechamento", "volume_dia (R$)"]].rename(columns={"volume_dia (R$)": "volume"})
        return s.astype(float), "base (preço ajustado por desdobramento)", []
    X = _b3()
    if f not in X:
        return None, None, [f"{f} não encontrado na base nem no arquivo da B3"]
    s = X[f][["abertura", "maxima", "minima", "fechamento", "volume"]].astype(float)
    v = s["fechamento"].pct_change()
    av = [f"salto de {x:+.0%} em {d:%d/%m/%Y}: possível desdobramento ou grupamento (preço da B3 sem ajuste)"
          for d, x in v[(v > 0.35) | (v < -0.35)].items()]
    return s, "arquivo da B3 (preço sem ajuste de desdobramento)", av


def indicadores(s):
    c, h, l, v = s["fechamento"], s["maxima"], s["minima"], s["volume"]
    I = pd.DataFrame(index=s.index)
    for n in (21, 50, 200):
        I[f"mm{n}"] = c.rolling(n).mean()
    m20, d20 = c.rolling(20).mean(), c.rolling(20).std()
    I["bb_sup"], I["bb_med"], I["bb_inf"] = m20 + 2 * d20, m20, m20 - 2 * d20
    d = c.diff()
    for n in (14, 2):
        rs = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean() / (-d).clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
        I[f"ifr{n}"] = 100 - 100 / (1 + rs)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    I["macd"], I["macd_sinal"] = macd, macd.ewm(span=9, adjust=False).mean()
    I["macd_hist"] = I["macd"] - I["macd_sinal"]
    ll, hh = l.rolling(14).min(), h.rolling(14).max()
    I["est_k"] = (100 * (c - ll) / (hh - ll).replace(0, np.nan)).rolling(3).mean()
    I["est_d"] = I["est_k"].rolling(3).mean()
    I["obv"] = (np.sign(d).fillna(0) * v).cumsum()
    I["vol60"] = v.rolling(60).mean()
    return I


def pivos(s, pct):
    """Zigue-zague pelas máximas e mínimas: lista de (data, preço, 'topo'|'fundo')."""
    h, l, idx = s["maxima"].to_numpy(), s["minima"].to_numpy(), s.index
    out, modo, ext, iext = [], None, None, 0
    for i in range(len(s)):
        if modo is None:
            modo, ext, iext = "sobe", h[i], i
            lo, ilo = l[i], i
            continue
        if modo == "sobe":
            if h[i] >= ext:
                ext, iext = h[i], i
            elif l[i] <= ext * (1 - pct):
                out.append((idx[iext], float(ext), "topo"))
                modo, ext, iext = "desce", l[i], i
        else:
            if l[i] <= ext:
                ext, iext = l[i], i
            elif h[i] >= ext * (1 + pct):
                out.append((idx[iext], float(ext), "fundo"))
                modo, ext, iext = "sobe", h[i], i
    out.append((idx[iext], float(ext), "topo" if modo == "sobe" else "fundo"))   # extremo ainda em formação
    return out


def niveis(s, pv, preco):
    pr = sorted(p for _, p, _ in pv[:-1])
    grupos, atual = [], []
    for p in pr:
        if atual and p > atual[0] * 1.025:
            grupos.append(atual)
            atual = []
        atual.append(p)
    if atual:
        grupos.append(atual)
    L = []
    for g in grupos:
        if len(g) < 2:
            continue
        nv = float(np.mean(g))
        datas = [d for d, p, _ in pv[:-1] if abs(p / nv - 1) <= 0.025]
        L.append(dict(preco=round(nv, 2), toques=len(g), ultimo=max(datas).strftime("%d/%m/%Y"),
                      tipo="suporte" if nv < preco else "resistência", distancia=round(nv / preco - 1, 4)))
    sup = sorted([x for x in L if x["tipo"] == "suporte"], key=lambda x: -x["preco"])[:4]
    res = sorted([x for x in L if x["tipo"] == "resistência"], key=lambda x: x["preco"])[:4]
    return sup + res


CANDLES = ["martelo", "engolfo de alta", "piercing", "estrela da manhã", "estrela cadente", "engolfo de baixa", "nuvem negra", "doji"]


def candles(s, n=10):
    o, h, l, c = (s[k].to_numpy() for k in ("abertura", "maxima", "minima", "fechamento"))
    mm21 = s["fechamento"].rolling(21).mean().to_numpy()
    L = []
    for i in range(max(2, len(s) - n), len(s)):
        corpo, faixa = abs(c[i] - o[i]), (h[i] - l[i]) or np.nan
        sb, sc = min(o[i], c[i]) - l[i], h[i] - max(o[i], c[i])
        alta, baixa = c[i] > o[i], c[i] < o[i]
        p1 = (o[i - 1], c[i - 1], h[i - 1], l[i - 1])
        nomes = []
        if corpo <= faixa / 3 and sb >= 2 * corpo and sc <= corpo and c[i] < mm21[i]:
            nomes.append("martelo")
        if p1[1] < p1[0] and alta and c[i] >= p1[0] and o[i] <= p1[1]:
            nomes.append("engolfo de alta")
        if p1[1] < p1[0] and abs(p1[1] - p1[0]) >= (p1[2] - p1[3]) / 2 and o[i] < p1[3] and c[i] > (p1[0] + p1[1]) / 2 and alta:
            nomes.append("piercing")
        if (c[i - 2] < o[i - 2] and abs(c[i - 2] - o[i - 2]) >= (h[i - 2] - l[i - 2]) / 2 and abs(p1[1] - p1[0]) <= (p1[2] - p1[3]) / 3
                and alta and c[i] > (o[i - 2] + c[i - 2]) / 2):
            nomes.append("estrela da manhã")
        if corpo <= faixa / 3 and sc >= 2 * corpo and sb <= corpo and c[i] > mm21[i]:
            nomes.append("estrela cadente")
        if p1[1] > p1[0] and baixa and c[i] <= p1[0] and o[i] >= p1[1]:
            nomes.append("engolfo de baixa")
        if p1[1] > p1[0] and abs(p1[1] - p1[0]) >= (p1[2] - p1[3]) / 2 and o[i] > p1[2] and c[i] < (p1[0] + p1[1]) / 2 and baixa:
            nomes.append("nuvem negra")
        if not nomes and corpo <= 0.1 * faixa:
            nomes.append("doji")
        for nm in nomes:
            L.append(dict(data=s.index[i].strftime("%d/%m/%Y"), padrao=nm,
                          sentido="alta" if nm in CANDLES[:4] else "baixa" if nm in CANDLES[4:7] else "indecisão"))
    return L


def liquidez(s, pv5, n=250):
    t0 = s.index[max(0, len(s) - n)]
    h, l, c, o = s["maxima"].to_numpy(), s["minima"].to_numpy(), s["fechamento"].to_numpy(), s["abertura"].to_numpy()
    idx = s.index
    rec = [p for p in pv5[:-1] if p[0] >= t0]
    Z = []
    for tipo, nome in (("fundo", "fundos iguais (stops abaixo)"), ("topo", "topos iguais (ordens acima)")):
        ps = [p for p in rec if p[2] == tipo]
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if abs(ps[j][1] / ps[i][1] - 1) <= 0.01:
                    Z.append(dict(tipo=nome, preco=round(min(ps[i][1], ps[j][1]) if tipo == "fundo" else max(ps[i][1], ps[j][1]), 2),
                                  datas=f"{ps[i][0]:%d/%m/%Y} e {ps[j][0]:%d/%m/%Y}"))
    fundos = [p for p in pv5[:-1] if p[2] == "fundo"]
    for k in range(max(1, len(s) - 120), len(s)):
        ant = [p for p in fundos if p[0] < idx[k] - pd.Timedelta(days=7)]
        if ant:
            nv = ant[-1][1]
            if l[k] < nv < c[k]:
                Z.append(dict(tipo="varrida de fundo (furou e voltou)", preco=round(nv, 2), datas=f"{idx[k]:%d/%m/%Y}"))
    for k in range(max(2, len(s) - n), len(s)):
        if l[k] > h[k - 2] and (l[k + 1:] > h[k - 2]).all():
            Z.append(dict(tipo="vazio de preço de alta (não preenchido)", preco=round(float(h[k - 2]), 2), ate=round(float(l[k]), 2),
                          datas=f"{idx[k]:%d/%m/%Y}"))
        if h[k] < l[k - 2] and (h[k + 1:] < l[k - 2]).all():
            Z.append(dict(tipo="vazio de preço de baixa (não preenchido)", preco=round(float(h[k]), 2), ate=round(float(l[k - 2]), 2),
                          datas=f"{idx[k]:%d/%m/%Y}"))
    blocos = []
    for k in range(max(1, len(s) - n), len(s) - 10):
        if c[k:k + 10].min() <= c[k] * 0.92:
            j = k
            while j > 0 and not (c[j] > o[j]):
                j -= 1
            if c[j] > o[j] and (c[j + 1:] <= h[j]).all():
                blocos.append(dict(tipo="último bloco de alta antes de queda forte (resistência)", preco=round(float(l[j]), 2),
                                   ate=round(float(h[j]), 2), datas=f"{idx[j]:%d/%m/%Y}"))
    vistos, U = set(), []
    for b in blocos[::-1]:
        if b["datas"] not in vistos:
            vistos.add(b["datas"])
            U.append(b)
    return Z + U[:3]


def perfil_volume(s, n=252, faixas=30):
    x = s.iloc[-n:]
    tp = (x["maxima"] + x["minima"] + x["fechamento"]) / 3
    b = np.linspace(x["minima"].min(), x["maxima"].max(), faixas + 1)
    vol, _ = np.histogram(tp, bins=b, weights=x["volume"])
    i = int(vol.argmax())
    ordem, acum, area = np.argsort(vol)[::-1], 0.0, []
    for k in ordem:
        area.append(k)
        acum += vol[k]
        if acum >= 0.7 * vol.sum():
            break
    return dict(faixas=[dict(de=round(float(b[k]), 2), ate=round(float(b[k + 1]), 2), volume=round(float(vol[k]))) for k in range(faixas)],
                maior_volume=dict(de=round(float(b[i]), 2), ate=round(float(b[i + 1]), 2)),
                area_70=dict(de=round(float(b[min(area)]), 2), ate=round(float(b[max(area) + 1]), 2)))


def vwap(s, desde):
    x = s.loc[desde:]
    tp = (x["maxima"] + x["minima"] + x["fechamento"]) / 3
    return round(float((tp * x["volume"]).sum() / x["volume"].sum()), 2)


def fibonacci(s, n=252):
    x = s["fechamento"].iloc[-n:]
    dt, dm = x.idxmax(), x.idxmin()
    topo, fundo = float(x.max()), float(x.min())
    if dt < dm:    # queda: retração de volta
        lv = {f"{p:.1%}".replace(".", ","): round(fundo + p * (topo - fundo), 2) for p in (0.236, 0.382, 0.5, 0.618, 0.786)}
        return dict(movimento="queda", de=round(topo, 2), ate=round(fundo, 2), data_topo=f"{dt:%d/%m/%Y}", data_fundo=f"{dm:%d/%m/%Y}", niveis=lv)
    lv = {f"{p:.1%}".replace(".", ","): round(topo - p * (topo - fundo), 2) for p in (0.236, 0.382, 0.5, 0.618, 0.786)}
    return dict(movimento="alta", de=round(fundo, 2), ate=round(topo, 2), data_topo=f"{dt:%d/%m/%Y}", data_fundo=f"{dm:%d/%m/%Y}", niveis=lv)


def elliott(pv8):
    P = pv8[-9:]
    if len(P) < 5:
        return dict(contagem="pivôs insuficientes", rotulos=[], invalida=None)
    pr = [p for _, p, _ in P]
    for n in (6, 4):
        if len(P) < n:
            continue
        q = pr[-n:]
        desce = q[1] < q[0]
        sgn = -1 if desce else 1
        if n == 6:
            w1, w2, w3, w4, w5 = (q[1] - q[0]) * sgn, (q[1] - q[2]) * sgn, (q[3] - q[2]) * sgn, (q[3] - q[4]) * sgn, (q[5] - q[4]) * sgn
            ok = (w2 < w1 and w3 > 0 and not (w3 < w1 and w3 < w5) and ((q[4] - q[1]) * sgn > 0))
            if ok:
                rot = [dict(data=f"{P[-n + k][0]:%d/%m/%Y}", preco=round(q[k], 2), onda=r) for k, r in enumerate(["0", "1", "2", "3", "4", "5"])]
                tot = q[5] - q[0]
                a1, a2 = q[5] - 0.382 * tot, q[5] - 0.618 * tot
                return dict(contagem=f"impulso de {'baixa' if desce else 'alta'} em 5 ondas, possivelmente completo",
                            rotulos=rot, invalida=None, alvos=[round(a1, 2), round(a2, 2)],
                            leitura=(f"se a onda 5 terminou em {q[5]:.2f}, a expectativa é de correção contrária, com alvos em "
                                     f"{a1:.2f} (38,2%) e {a2:.2f} (61,8%) do impulso; um novo {'fundo abaixo' if desce else 'topo acima'} "
                                     f"de {q[5]:.2f} indica que a onda 5 ainda está em andamento"))
        else:
            a, b, c = (q[1] - q[0]) * sgn, (q[1] - q[2]) * sgn, (q[3] - q[2]) * sgn
            if 0 < b < a and c > 0:
                rot = [dict(data=f"{P[-n + k][0]:%d/%m/%Y}", preco=round(q[k], 2), onda=r) for k, r in enumerate(["início", "A", "B", "C"])]
                return dict(contagem=f"correção A-B-C de {'baixa' if desce else 'alta'}",
                            rotulos=rot, invalida=round(q[2], 2),
                            leitura=(f"onda C com {abs(c / a):.0%} do tamanho da onda A; "
                                     f"a correção perde validade se o preço voltar além de {q[2]:.2f}"))
    return dict(contagem="sem contagem válida pelas regras (movimento lateral ou confuso)", rotulos=[], invalida=None)


def projecao(pv8, niveis_, preco):
    """Zonas de alvo do repique (ou da correção) pelas ondas e Fibonacci, juntadas com as resistências/suportes.
    Última perna = do penúltimo ao último pivô de 8%; impulso = do início da contagem de Elliott (se houver) ao último
    pivô. Níveis: 23,6/38,2/50/61,8% da última perna e 23,6/38,2% do impulso; resistências (ou suportes) a até 2%
    entram na mesma zona. Zonas = níveis a até 2% uns dos outros; ordem pela distância do preço."""
    if len(pv8) < 3:
        return None
    (d1, p1, _), (d2, p2, t2) = pv8[-2], pv8[-1]
    sobe = t2 == "fundo"                         # último pivô é fundo -> alvos para cima
    L = [(p2 + f * (p1 - p2), f"{f:.1%} da última perna".replace(".", ",")) for f in (0.236, 0.382, 0.5, 0.618)]
    el = elliott(pv8)
    if el.get("rotulos"):
        p0 = el["rotulos"][0]["preco"]
        L += [(p2 + f * (p0 - p2), f"{f:.1%} do movimento desde a onda 0".replace(".", ",")) for f in (0.236, 0.382)]
    tipo = "resistência" if sobe else "suporte"
    L += [(n["preco"], f"{tipo} {n['toques']} toques") for n in niveis_ if n["tipo"] == tipo]
    L = sorted([x for x in L if (x[0] > preco) == sobe], key=lambda x: abs(x[0] - preco))
    Z = []
    for v, nome in L:
        if Z and abs(v / Z[-1]["niveis"][0] - 1) <= 0.02:
            Z[-1]["niveis"].append(v)
            Z[-1]["motivos"].append(nome)
        else:
            Z.append(dict(niveis=[v], motivos=[nome]))
    out = []
    for z in Z[:4]:
        alvo = round(float(np.mean(z["niveis"])), 2)
        out.append(dict(alvo=alvo, de=round(min(z["niveis"]), 2), ate=round(max(z["niveis"]), 2), motivos=z["motivos"],
                        confluencia=len(z["motivos"]), variacao=round(alvo / preco - 1, 4)))
    return dict(sentido="alta" if sobe else "baixa", ultima_perna=dict(de=round(p1, 2), ate=round(p2, 2), data_ini=f"{d1:%Y-%m-%d}",
                data_fim=f"{d2:%Y-%m-%d}"), invalida=round(p2, 2), zonas=out,
                leitura=(f"{'novo fundo abaixo' if sobe else 'novo topo acima'} de {p2:.2f} indica que a perna ainda não terminou "
                         f"(na leitura de Elliott: ainda na onda 3, ou a onda 5 em andamento)"))


def pine(A, entrada=None):
    """Script Pine (TradingView, versão 5) que desenha a projeção, as ondas e os níveis do motor no gráfico do fundo."""
    P, E = A["projecao"] or {}, A["elliott"]
    ent = entrada or A["preco"]
    zs = (P.get("zonas") or [])[:4]
    inval = P.get("invalida", A["preco"])
    sobe = P.get("sentido", "alta") == "alta"
    L = [f"// Radar Gráfico de FIIs · {A['fundo']} · dados até {A['ultimo_pregao']} · gerado por estudos/analise_grafica.py",
         "// Zonas, preço que invalida e ondas vêm do motor do projeto. Os caminhos são ILUSTRATIVOS: mostram a ordem, não o prazo.",
         "//@version=5",
         f'indicator("Radar FII · {A["fundo"]}", overlay=true, max_lines_count=100, max_labels_count=100)',
         f'entrada = input.float({ent:.2f}, "Preço de entrada")',
         f'inval = input.float({inval:.2f}, "Preço que invalida")',
         'mostrarCaminhos = input.bool(true, "Mostrar caminhos ilustrativos")',
         'mostrarNiveis = input.bool(true, "Mostrar suportes e resistências")',
         'mostrarOndas = input.bool(true, "Mostrar ondas de Elliott")']
    for i, z in enumerate(zs, 1):
        L.append(f'z{i} = input.float({z["alvo"]:.2f}, "Zona {i}")')
    L += ["pct(x) => str.tostring((x / entrada - 1) * 100, '+#.0;-#.0') + '%'",
          "var bool feito = false",
          "if barstate.islast and not feito",
          "    feito := true",
          "    ini = bar_index - 120",
          "    fim = bar_index + 80",
          "    line.new(ini, entrada, fim, entrada, color=color.gray, style=line.style_dotted)",
          "    label.new(fim, entrada, 'Entrada ' + str.tostring(entrada, '#.00'), style=label.style_label_left, color=color.new(color.gray, 80), textcolor=color.gray, size=size.small)",
          "    line.new(ini, inval, fim, inval, color=color.red, style=line.style_dashed, width=2)",
          f"    label.new(fim, inval, '{'Abaixo: queda continua' if sobe else 'Acima: alta continua'} ' + str.tostring(inval, '#.00') + ' (' + pct(inval) + ')', style=label.style_label_left, color=color.new(color.red, 80), textcolor=color.red, size=size.small)"]
    for i, z in enumerate(zs, 1):
        L += [f"    line.new(ini, z{i}, fim, z{i}, color=color.teal, width=2)",
              f"    label.new(fim, z{i}, 'Zona {i} ' + str.tostring(z{i}, '#.00') + ' (' + pct(z{i}) + ')', style=label.style_label_left, color=color.new(color.teal, 75), textcolor=color.teal, size=size.small)"]
    if zs:
        za = zs[1]["alvo"] if len(zs) > 1 else zs[0]["alvo"]
        n1 = "z2" if len(zs) > 1 else "z1"
        nmax = f"z{len(zs)}"
        fundo = "inval * 0.95" if sobe else "inval * 1.05"
        L += ["    if mostrarCaminhos",
              f"        line.new(bar_index, close, bar_index + 24, {n1}, color=color.green, style=line.style_dashed, width=2)",
              f"        line.new(bar_index + 24, {n1}, bar_index + 39, z1, color=color.green, style=line.style_dashed, width=2)",
              f"        line.new(bar_index + 39, z1, bar_index + 74, {nmax}, color=color.green, style=line.style_dashed, width=2)",
              f"        label.new(bar_index + 74, {nmax}, 'Caminho: onda 5 completa', style=label.style_label_down, color=color.new(color.green, 80), textcolor=color.green, size=size.small)",
              "        line.new(bar_index, close, bar_index + 14, z1, color=color.orange, style=line.style_dashed, width=2)",
              f"        line.new(bar_index + 14, z1, bar_index + 44, {fundo}, color=color.orange, style=line.style_dashed, width=2)",
              f"        label.new(bar_index + 44, {fundo}, 'Caminho: ainda na onda 3', style=label.style_label_up, color=color.new(color.orange, 80), textcolor=color.orange, size=size.small)"]
    L.append("    if mostrarNiveis")
    for n in A["niveis"]:
        cor = "color.green" if n["tipo"] == "suporte" else "color.maroon"
        L.append(f"        line.new(ini, {n['preco']:.2f}, bar_index, {n['preco']:.2f}, color=color.new({cor}, 40), style=line.style_solid)")
    L.append("    if mostrarOndas")
    for r in E.get("rotulos") or []:
        d, m, a = r["data"].split("/")
        L.append(f"        label.new(timestamp('America/Sao_Paulo', {int(a)}, {int(m)}, {int(d)}, 10, 0), {r['preco']:.2f}, 'Onda {r['onda']}', "
                 f"xloc=xloc.bar_time, style=label.style_label_down, color=color.new(color.blue, 75), textcolor=color.blue, size=size.small)")
    if not (E.get("rotulos")):
        L.append("        na")
    return "\n".join(L) + "\n"


@lru_cache(maxsize=1)
def _papel_hoje():
    import estudos.descontado_saudavel as DS
    d = DS.RD.DIAS[-1]
    C = DS.candidatos_v2(d)
    C["pos"] = C.groupby("tipo").cumcount() + 1
    return C


def fundamentos(f, s):
    out = {}
    d = s.index[-1]
    try:
        from estudos.classificacao_carteira import classe
        out["classe"] = classe(f, d)
    except Exception:  # noqa: BLE001
        out["classe"] = "sem informe"
    B = _base()
    if f in B:
        x = B[f].loc[:d]
        out["preco_sobre_patrimonio"] = round(float(x["preco_sobre_valor_patrimonial"].iloc[-1]), 3)
        out["rendimento_mensal"] = float(x["rendimento_mensal (R$/cota)"].iloc[-1])
        out["rendimento_ano"] = round(float(x["rendimento_ano_sobre_preco (%)"].iloc[-1]) / 100, 4)
        try:
            from estudos.cobertura_rendimento import cobertura
            cb = cobertura(f, d)
            out["cobertura"] = round(cb["cobertura"], 3) if cb else None
        except Exception:  # noqa: BLE001
            out["cobertura"] = None
        try:
            from estudos.saude_fundo import saude
            sv = saude(f, d)
            out["saude"] = sv["veredito"]
            out["problemas"] = sv.get("problemas", [])
        except Exception:  # noqa: BLE001
            out["saude"] = None
        try:
            C = _papel_hoje()
            r = C[C["fundo"] == f]
            out["papel_padrao"] = (f"candidato, {int(r['pos'].iloc[0])}º da classe {r['tipo'].iloc[0]}" if len(r) else "fora do corte essencial")
        except Exception:  # noqa: BLE001
            out["papel_padrao"] = None
    else:
        out["aviso"] = "fundo fora da base: sem rendimento, cobertura e avaliação de saúde"
    c = s["fechamento"]
    mm200 = c.iloc[-201:-1].mean() if len(c) > 200 else np.nan
    med60 = s["volume"].iloc[-60:].median()
    dist = float(c.iloc[-1] / mm200 - 1) if mm200 == mm200 else None
    out["distancia_media_200"] = round(dist, 4) if dist is not None else None
    out["negociacao_tipica"] = round(float(med60))
    if dist is None:
        out["kairi"] = "sem 200 pregões"
    else:
        lim = 0.20 if med60 >= 1e6 else 0.25 if med60 >= 5e5 else None
        out["kairi"] = ("negociação abaixo de R$ 500 mil/dia (fora do Kairi Padrão)" if lim is None else
                        f"abaixo da linha de −{lim:.0%} (zona de sinal; o sinal é o dia do cruzamento)" if dist <= -lim else
                        f"acima da linha de −{lim:.0%}")
    return out


def analisar(f):
    f = f.upper()
    s, fonte, avisos = serie(f)
    if s is None or len(s) < 60:
        return dict(fundo=f, erro=avisos[0] if avisos else "menos de 60 pregões")
    I = indicadores(s)
    c = s["fechamento"]
    preco, d = float(c.iloc[-1]), s.index[-1]
    pv5, pv8 = pivos(s, 0.05), pivos(s, 0.08)
    M = _mercado()
    m = M.reindex(s.index).ffill()
    rel = c / m
    fu = fundamentos(f, s)
    L = []

    def item(n, nome, valor, leitura, conf="descritivo"):
        L.append(dict(item=n, nome=nome, valor=valor, leitura=leitura, confianca=conf))
    nv = niveis(s, pv5, preco)
    sp = [x for x in nv if x["tipo"] == "suporte"]
    rs = [x for x in nv if x["tipo"] == "resistência"]
    item(1, "Suportes e resistências", f"suporte {sp[0]['preco']:.2f} ({sp[0]['toques']} toques)" if sp else "nenhum suporte com 2+ toques abaixo",
         ("resistências: " + ", ".join(f"{x['preco']:.2f}" for x in rs[:3])) if rs else "sem resistência com 2+ toques acima")
    last = I.iloc[-1]
    inc = lambda k: float(I[k].iloc[-1] / I[k].iloc[-21] - 1) if I[k].iloc[-21] == I[k].iloc[-21] else np.nan  # noqa: E731
    item(2, "Médias 21 / 50 / 200", f"{last['mm21']:.2f} / {last['mm50']:.2f} / {last['mm200']:.2f}",
         f"preço {'acima' if preco > last['mm21'] else 'abaixo'} da 21; média de 21 {'subindo' if inc('mm21') > 0 else 'caindo'} "
         f"({inc('mm21'):+.1%} em 20 pregões); 21 {'acima' if last['mm21'] > last['mm50'] else 'abaixo'} da 50; "
         f"distância da 200: {preco / last['mm200'] - 1:+.1%}" if last["mm200"] == last["mm200"] else "menos de 200 pregões")
    fs = [p for p in pv5[:-1] if p[2] == "fundo"][-2:]
    div = ""
    if len(fs) == 2:
        i1, i2 = s.index.get_loc(fs[0][0]), s.index.get_loc(fs[1][0])
        if fs[1][1] < fs[0][1] and I["ifr14"].iloc[i2] > I["ifr14"].iloc[i1]:
            div = f"; divergência de alta (preço fez fundo mais baixo em {fs[1][0]:%d/%m}, IFR fez fundo mais alto)"
    item(3, "IFR 14 / IFR 2", f"{last['ifr14']:.0f} / {last['ifr2']:.0f}",
         ("sobrevendido" if last["ifr14"] < 30 else "sobrecomprado" if last["ifr14"] > 70 else "neutro") + div)
    h = I["macd_hist"]
    item(4, "MACD (histograma)", f"{h.iloc[-1]:+.3f}",
         ("negativo" if h.iloc[-1] < 0 else "positivo") + (", ganhando força para cima" if h.iloc[-1] > h.iloc[-2] > h.iloc[-3] else
                                                           ", ganhando força para baixo" if h.iloc[-1] < h.iloc[-2] < h.iloc[-3] else ""))
    item(5, "Estocástico %K / %D", f"{last['est_k']:.0f} / {last['est_d']:.0f}",
         ("abaixo de 20 (exagero de queda)" if last["est_k"] < 20 else "acima de 80 (exagero de alta)" if last["est_k"] > 80 else "meio da faixa")
         + ("; %K cruzou para cima" if I["est_k"].iloc[-1] > I["est_d"].iloc[-1] and I["est_k"].iloc[-2] <= I["est_d"].iloc[-2] else ""))
    larg = (I["bb_sup"] - I["bb_inf"]) / I["bb_med"]
    item(6, "Bandas de Bollinger", f"{last['bb_inf']:.2f} a {last['bb_sup']:.2f}",
         ("preço abaixo da banda de baixo" if preco < last["bb_inf"] else "preço acima da banda de cima" if preco > last["bb_sup"] else "preço dentro das bandas")
         + f"; largura {larg.iloc[-1] / larg.iloc[-120:].mean():.1f}× a média de 120 pregões")
    cd = candles(s)
    item(7, "Candles (10 pregões)", ", ".join(f"{x['padrao']} {x['data'][:5]}" for x in cd) or "nenhum padrão",
         "último padrão de " + cd[-1]["sentido"] if cd else "sem sinal de reversão nos candles")
    vr = s["volume"] / I["vol60"]
    clim = vr.iloc[-20:][vr.iloc[-20:] >= 2]
    obv_inc = float(I["obv"].iloc[-1] - I["obv"].iloc[-21])
    item(8, "Volume e OBV", f"volume de hoje {vr.iloc[-1]:.1f}× a média de 60",
         (f"{len(clim)} dia(s) de volume 2× ou mais em 20 pregões ({', '.join(f'{d:%d/%m}' for d in clim.index)}); " if len(clim) else "sem dia de volume extremo em 20 pregões; ")
         + f"OBV {'subindo (mais volume nos dias de alta)' if obv_inc > 0 else 'caindo (mais volume nos dias de queda)'}")
    pf = perfil_volume(s)
    i252 = s["fechamento"].iloc[-252:]
    vw_t, vw_f = vwap(s, i252.idxmax()), vwap(s, i252.idxmin())
    item(9, "Volume por faixa de preço", f"maior volume {pf['maior_volume']['de']:.2f}–{pf['maior_volume']['ate']:.2f}",
         f"70% do volume entre {pf['area_70']['de']:.2f} e {pf['area_70']['ate']:.2f}; preço médio pago desde o topo de 12 meses "
         f"{vw_t:.2f} ({preco / vw_t - 1:+.1%} hoje); desde o fundo {vw_f:.2f}")
    fb = fibonacci(s)
    item(10, "Fibonacci (12 meses)", f"{fb['movimento']} de {fb['de']:.2f} a {fb['ate']:.2f}",
         "níveis: " + ", ".join(f"{k} {v:.2f}" for k, v in fb["niveis"].items()))
    r20, r60 = float(rel.iloc[-1] / rel.iloc[-21] - 1), float(rel.iloc[-1] / rel.iloc[-61] - 1)
    item(11, "Força relativa contra o mercado", f"{r20:+.1%} em 20 pregões / {r60:+.1%} em 60",
         "mais fraco que o mercado" if r20 < 0 else "mais forte que o mercado")
    lq = liquidez(s, pv5)
    abaixo = [z for z in lq if z["preco"] < preco]
    acima = [z for z in lq if z["preco"] > preco]
    item(12, "Zonas de liquidez (deduzidas)", f"{len(lq)} zonas",
         (f"mais próxima abaixo: {max(abaixo, key=lambda z: z['preco'])['tipo']} em {max(z['preco'] for z in abaixo):.2f}; " if abaixo else "nenhuma abaixo; ")
         + (f"acima: {min(acima, key=lambda z: z['preco'])['tipo']} em {min(z['preco'] for z in acima):.2f}" if acima else "nenhuma acima"),
         "descritivo (sem livro de ofertas)")
    el = elliott(pv8)
    item(13, "Ondas de Elliott", el["contagem"], el.get("leitura", "") + (f"; invalida em {el['invalida']:.2f}" if el.get("invalida") else ""),
         "subjetivo")
    J = s.iloc[-JANELA:]
    IJ = I.loc[J.index]
    r2 = lambda a: [None if a_ != a_ else round(float(a_), 2) for a_ in a]  # noqa: E731
    dados = dict(t=[d.strftime("%Y-%m-%d") for d in J.index], o=r2(J["abertura"]), h=r2(J["maxima"]), l=r2(J["minima"]), c=r2(J["fechamento"]),
                 v=[round(float(x)) for x in J["volume"]], **{k: r2(IJ[k]) for k in ["mm21", "mm50", "mm200", "bb_sup", "bb_inf", "ifr14", "macd",
                                                                                   "macd_sinal", "macd_hist", "est_k", "est_d"]},
                 obv=[round(float(x)) for x in IJ["obv"]], rel=r2(rel.loc[J.index] / rel.loc[J.index].iloc[0] * 100))
    return dict(fundo=f, ultimo_pregao=f"{d:%d/%m/%Y}", preco=round(preco, 2), fonte=fonte, avisos=avisos, fundamentos=fu, leitura=L,
                niveis=nv, liquidez=lq, perfil=pf, vwap=dict(desde_topo=vw_t, desde_fundo=vw_f), fibonacci=fb, elliott=el,
                candles=cd, projecao=projecao(pv8, nv, preco), pivos=[dict(data=f"{d_:%Y-%m-%d}", preco=round(p, 2), tipo=t) for d_, p, t in pv5 if d_ >= J.index[0]], serie=dados)


def limpo(o):
    """Troca NaN/infinito por None em qualquer nível (JSON válido para o navegador)."""
    if isinstance(o, dict):
        return {k: limpo(v) for k, v in o.items()}
    if isinstance(o, list):
        return [limpo(v) for v in o]
    if isinstance(o, float) and not np.isfinite(o):
        return None
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def imprimir(A):
    if "erro" in A:
        print(A["fundo"], A["erro"])
        return
    fu = A["fundamentos"]
    print(f"\n=== {A['fundo']}  {A['ultimo_pregao']}  R$ {A['preco']:.2f}  ({A['fonte']})")
    for a in A["avisos"]:
        print("  aviso:", a)
    print("  fundamentos:", ", ".join(f"{k}: {v}" for k, v in fu.items() if k != "problemas"))
    if fu.get("problemas"):
        print("  problemas:", "; ".join(fu["problemas"]))
    T = pd.DataFrame(A["leitura"])[["item", "nome", "valor", "leitura", "confianca"]]
    with pd.option_context("display.max_colwidth", 200, "display.width", 300):
        print(T.to_string(index=False))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--todos" in args:
        saida = Path(args[args.index("--saida") + 1])
        (saida / "dados").mkdir(parents=True, exist_ok=True)
        ult = max(x.index[-1] for x in _base().values())
        cand = sorted({f for f, x in _base().items() if x.index[-1] >= ult - pd.Timedelta(days=20) and (x["negociou (1/0)"] == 1).sum() >= 120}
                      | {f for f, x in _b3().items() if f.endswith("11") and x.index[-1] >= ult - pd.Timedelta(days=20) and len(x) >= 120})
        grupos, indice, erros = {}, [], []
        for k, f in enumerate(cand, 1):
            try:
                A = analisar(f)
            except Exception as e:  # noqa: BLE001
                erros.append((f, repr(e)))
                continue
            if "erro" in A:
                erros.append((f, A["erro"]))
                continue
            grupos.setdefault(f[0], {})[f] = limpo(A)
            indice.append(dict(fundo=f, classe=A["fundamentos"].get("classe"), preco=A["preco"], fonte=A["fonte"].split(" ")[0]))
            if k % 50 == 0:
                print(f"{k}/{len(cand)}", flush=True)
        for g, D in grupos.items():
            (saida / "dados" / f"{g}.json").write_text(json.dumps(D, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
        (saida / "dados" / "indice.json").write_text(json.dumps(dict(gerado=f"{ult:%d/%m/%Y}", fundos=indice), ensure_ascii=False,
                                                                separators=(",", ":")), encoding="utf-8")
        print(f"gravado em {saida}/dados: {len(indice)} fundos em {len(grupos)} arquivos; erros: {len(erros)} {erros[:5]}")
    elif "--pine" in args:
        f = args[args.index("--pine") + 1].upper()
        ent = float(args[args.index("--entrada") + 1].replace(",", ".")) if "--entrada" in args else None
        A = analisar(f)
        arq = RAIZ / "radar" / "pine" / f"{f}.pine"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(pine(A, ent), encoding="utf-8")
        print(f"gravado: {arq.relative_to(RAIZ)}")
    else:
        for f in args:
            imprimir(analisar(f))
