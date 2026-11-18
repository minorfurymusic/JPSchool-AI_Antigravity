"""Papel Padrão com análise gráfica: confluência de sinais para ENTRAR e para SAIR (pedido do dono, 18/11/2026).
Regras fixadas ANTES de rodar; nada é ajustado depois. Resultados separados em 2018–2022 e 2023–11/2026.

Atenção: fundo nos 5 de maior nota da classe Papel no sinal do mês (descontado_saudavel.candidatos_v2); observado do
1º pregão depois do sinal até o último pregão do mês seguinte. Sem compra na janela = dinheiro no CDI.
Indicadores (só pregões com negócio; tudo calculado com dados até o dia):
  IFR 14 (Wilder); estocástico %K 14 suavizado 3 e %D 3; MACD 12/26/9 (histograma); Bollinger 20/2; médias 21;
  volume médio de 20; mínima e máxima de 60 pregões.
Candles (corpo = |fechamento − abertura|, faixa = máxima − mínima):
  martelo: corpo <= 1/3 da faixa, sombra de baixo >= 2 × corpo, sombra de cima <= corpo, fechamento < média de 21
  engolfo de alta: ontem fechou em baixa, hoje em alta, corpo de hoje cobre o de ontem
  piercing: ontem baixa com corpo >= 1/2 da faixa; hoje abre abaixo da mínima de ontem e fecha acima do meio do corpo de ontem
  estrela da manhã: anteontem baixa grande (corpo >= 1/2 da faixa), ontem corpo pequeno (<= 1/3), hoje alta fechando
    acima do meio do corpo de anteontem
  estrela cadente: corpo <= 1/3 da faixa, sombra de cima >= 2 × corpo, sombra de baixo <= corpo, fechamento > média de 21
  engolfo de baixa: espelho do de alta; nuvem negra: espelho do piercing
Confirmações de COMPRA (cada uma vale 1):
  C1 candle de alta (martelo, engolfo de alta, piercing ou estrela da manhã)
  C2 suporte: mínima <= 1,02 × mínima de 60 pregões, ou fechamento <= banda inferior em algum dos últimos 3 pregões
  C3 IFR 14 abaixo de 35 em algum dos últimos 3 pregões e subindo hoje
  C4 estocástico: %K cruza acima de %D hoje, com %K < 30
  C5 MACD: histograma < 0 e subindo há 2 pregões
  C6 volume > 1,2 × média de 20 e fechamento > abertura
Confirmações de VENDA (espelho):
  V1 candle de baixa (estrela cadente, engolfo de baixa, nuvem negra)
  V2 resistência: máxima >= 0,98 × máxima de 60 pregões, ou fechamento >= banda superior em algum dos últimos 3 pregões
  V3 IFR 14 acima de 65 em algum dos últimos 3 pregões e caindo hoje
  V4 estocástico: %K cruza abaixo de %D hoje, com %K > 70
  V5 MACD: histograma > 0 e caindo há 2 pregões
  V6 volume > 1,2 × média de 20 e fechamento < abertura
Compras: "sinal" (abertura seguinte ao sinal do mês, regra atual) ou "conf2/conf3/conf4" (abertura seguinte ao 1º dia
  com 2/3/4 ou mais confirmações de compra).
Vendas (no fechamento; prazo de 252 pregões em todas):
  "alvo"  preço + rendimentos (data-com) >= +10% sobre o custo
  "tec"   3 ou mais confirmações de venda no dia E resultado bruto >= 0 (não vende no prejuízo por sinal gráfico)
  "ambos" o que vier primeiro entre "alvo" e "tec"
Contas: 20% de IR sobre ganho na cota, taxa de 0,03%, avisos de rendimento suspeitos ignorados.

    PYTHONPATH=. python3 estudos/papel_tecnico.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saidas as SA
from estudos.rendimentos_suspeitos import suspeitos

DS, RD, RF, SER = SA.DS, SA.RD, SA.RF, SA.SER
PRAZO, B3, IR, ALVO = 252, 0.0003, 0.20, 0.10


def indicadores(f):
    s = SER[f].copy()
    P = RD.PF[f]
    P = P[P["negociou (1/0)"] == 1]
    s["maxima"], s["minima"], s["volume"] = P["maxima"].reindex(s.index), P["minima"].reindex(s.index), P["volume_dia (R$)"].reindex(s.index)
    o, h, l, c = s["abertura"], s["maxima"], s["minima"], s["fechamento"]
    d = c.diff()
    rs = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean() / (-d).clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    s["ifr14"] = 100 - 100 / (1 + rs)
    ll, hh = l.rolling(14).min(), h.rolling(14).max()
    s["estK"] = (100 * (c - ll) / (hh - ll)).rolling(3).mean()
    s["estD"] = s["estK"].rolling(3).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    s["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
    s["vol20"] = s["volume"].rolling(20).mean()
    s["min60"], s["max60"] = l.rolling(60).min(), h.rolling(60).max()
    corpo, faixa = (c - o).abs(), (h - l).replace(0, np.nan)
    sb, sc = np.minimum(o, c) - l, h - np.maximum(o, c)
    alta, baixa = c > o, c < o
    s["martelo"] = (corpo <= faixa / 3) & (sb >= 2 * corpo) & (sc <= corpo) & (c < s["mm21"])
    s["engolfo_alta"] = baixa.shift(1) & alta & (c >= o.shift(1)) & (o <= c.shift(1))
    s["piercing"] = baixa.shift(1) & (corpo.shift(1) >= faixa.shift(1) / 2) & (o < l.shift(1)) & (c > (o.shift(1) + c.shift(1)) / 2) & alta
    s["estrela_manha"] = (baixa.shift(2) & (corpo.shift(2) >= faixa.shift(2) / 2) & (corpo.shift(1) <= faixa.shift(1) / 3) & alta
                          & (c > (o.shift(2) + c.shift(2)) / 2))
    s["estrela_cadente"] = (corpo <= faixa / 3) & (sc >= 2 * corpo) & (sb <= corpo) & (c > s["mm21"])
    s["engolfo_baixa"] = alta.shift(1) & baixa & (c <= o.shift(1)) & (o >= c.shift(1))
    s["nuvem_negra"] = alta.shift(1) & (corpo.shift(1) >= faixa.shift(1) / 2) & (o > h.shift(1)) & (c < (o.shift(1) + c.shift(1)) / 2) & baixa
    fb = (c <= s["bb_inf"]).astype(int).rolling(3).max() > 0
    fu = (c >= s["bb_sup"]).astype(int).rolling(3).max() > 0
    hi = s["macd_hist"]
    s["C1"] = s["martelo"] | s["engolfo_alta"] | s["piercing"] | s["estrela_manha"]
    s["C2"] = (l <= 1.02 * s["min60"]) | fb
    s["C3"] = ((s["ifr14"] < 35).astype(int).rolling(3).max() > 0) & (s["ifr14"] > s["ifr14"].shift(1))
    s["C4"] = (s["estK"] > s["estD"]) & (s["estK"].shift(1) <= s["estD"].shift(1)) & (s["estK"] < 30)
    s["C5"] = (hi < 0) & (hi > hi.shift(1)) & (hi.shift(1) > hi.shift(2))
    s["C6"] = (s["volume"] > 1.2 * s["vol20"]) & alta
    s["V1"] = s["estrela_cadente"] | s["engolfo_baixa"] | s["nuvem_negra"]
    s["V2"] = (h >= 0.98 * s["max60"]) | fu
    s["V3"] = ((s["ifr14"] > 65).astype(int).rolling(3).max() > 0) & (s["ifr14"] < s["ifr14"].shift(1))
    s["V4"] = (s["estK"] < s["estD"]) & (s["estK"].shift(1) >= s["estD"].shift(1)) & (s["estK"] > 70)
    s["V5"] = (hi > 0) & (hi < hi.shift(1)) & (hi.shift(1) < hi.shift(2))
    s["V6"] = (s["volume"] > 1.2 * s["vol20"]) & baixa
    for k in ["C1", "C2", "C3", "C4", "C5", "C6", "V1", "V2", "V3", "V4", "V5", "V6"]:
        s[k] = s[k].fillna(False).astype(bool)
    s["compra_n"] = s[["C1", "C2", "C3", "C4", "C5", "C6"]].sum(axis=1)
    s["venda_n"] = s[["V1", "V2", "V3", "V4", "V5", "V6"]].sum(axis=1)
    return s


def operar(f, s, ent, venda):
    y = s.loc[ent:].iloc[:PRAZO]
    n = len(y)
    px0 = float(s.loc[ent, "abertura"])
    custo = px0 * (1 + B3)
    r = RF.get(f)
    rend = np.zeros(n)
    if r is not None:
        rr = r[r["data_base"] >= ent]
        rr = rr[np.array([(f, db) not in suspeitos() for db in rr["data_base"]], dtype=bool)]
        for db, v in rr.groupby("data_base")["valor (R$/cota)"].sum().items():
            k = y.index.searchsorted(db)
            if k < n:
                rend[k] += v
        rend = np.cumsum(rend)
    c = y["fechamento"].to_numpy(float)
    ret = (c * (1 - B3) + rend) / custo - 1
    ok_alvo = ret >= ALVO
    ok_tec = (y["venda_n"].to_numpy() >= 3) & (ret >= 0)
    ok = ok_alvo if venda == "alvo" else ok_tec if venda == "tec" else (ok_alvo | ok_tec)
    h = np.flatnonzero(ok)
    if len(h):
        k, sit = h[0], ("alvo" if ok_alvo[h[0]] else "sinal gráfico de venda")
    elif n >= PRAZO:
        k, sit = n - 1, "prazo de 1 ano"
    else:
        return None
    venda_liq = c[k] * (1 - B3)
    res = (venda_liq - IR * max(venda_liq - custo, 0) + rend[k]) / custo - 1
    return dict(fundo=f, entrada=ent, saida=y.index[k], situacao=sit, pregoes=k + 1, resultado=res,
                pior_momento=float(ret[: k + 1].min()), pico=float(ret[: k + 1].max()), cdi=RD.cdi_liq(ent, y.index[k], 1.0) - 1)


def resumo(O, sem):
    if O.empty:
        return {}
    return {"Operações": len(O), "Sinais sem compra": sem, "Com lucro": (O["resultado"] > 0).mean(),
            "Bateram o CDI": (O["resultado"] > O["cdi"]).mean(), "Resultado médio": O["resultado"].mean(),
            "Pregões médios": O["pregoes"].mean(), "Saíram pelo alvo": (O["situacao"] == "alvo").mean(),
            "Saíram pelo sinal gráfico": (O["situacao"] == "sinal gráfico de venda").mean(),
            "Saíram no prazo de 1 ano": (O["situacao"] == "prazo de 1 ano").mean(),
            "Queda média depois da compra": O["pior_momento"].mean(), "Perdas de mais de 10%": (O["resultado"] < -0.10).mean(),
            "Ganho − CDI por mês (pontos)": (O["resultado"].sum() - O["cdi"].sum()) / O["pregoes"].sum() * 21 * 100,
            "Ganho total por R$ 1.000 em cada sinal": float(O["resultado"].sum() * 1000)}


if __name__ == "__main__":
    pd.set_option("display.width", 300)
    pd.set_option("display.max_columns", 40)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    SIN = []
    for i, d in enumerate(fms):
        C = DS.candidatos_v2(d)
        if C.empty:
            continue
        prox = fms[i + 1] if i + 1 < len(fms) else RD.DIAS[-1]
        SIN.append((d, prox, list(C[C["tipo"] == "Papel"]["fundo"].head(5))))
    fundos = sorted({f for *_, fs in SIN for f in fs if f in SER})
    IND = {f: indicadores(f) for f in fundos}
    print(f"sinais prontos; {len(fundos)} fundos de Papel com indicadores", flush=True)
    RES, OPS = [], []
    for compra in ("sinal", "conf2", "conf3", "conf4"):
        for venda in ("alvo", "tec", "ambos"):
            livre, ops, sem = {}, [], 0
            for d, prox, fs in SIN:
                for f in fs:
                    if f not in IND or livre.get(f, pd.Timestamp.min) > d:
                        continue
                    s = IND[f]
                    z = s.loc[d + pd.Timedelta(days=1):prox]
                    if z.empty:
                        continue
                    if compra == "sinal":
                        ent = z.index[0]
                    else:
                        t = z.index[(z["compra_n"] >= int(compra[-1])).to_numpy()]
                        if len(t) == 0:
                            sem += 1
                            continue
                        k = s.index.get_loc(t[0])
                        if k + 1 >= len(s):
                            continue
                        ent = s.index[k + 1]
                    o = operar(f, s, ent, venda)
                    if o is None:
                        livre[f] = RD.DIAS[-1]
                        continue
                    ops.append(dict(o, compra=compra, venda=venda))
                    livre[f] = o["saida"]
            O = pd.DataFrame(ops)
            OPS.append(O)
            for per, (a, b) in {"2018–2022": ("2018-01-01", "2022-12-31"), "2023–11/2026": ("2023-01-01", "2026-12-31"),
                                "Completo": ("2018-01-01", "2026-12-31")}.items():
                x = O[(O["entrada"] >= a) & (O["entrada"] <= b)] if len(O) else O
                RES.append(dict({"Compra": compra, "Venda": venda, "Período": per}, **resumo(x, sem if per == "Completo" else np.nan)))
            print(compra, venda, "pronto", flush=True)
    R = pd.DataFrame(RES)
    cols = ["Operações", "Sinais sem compra", "Com lucro", "Bateram o CDI", "Resultado médio", "Pregões médios", "Saíram pelo alvo",
            "Saíram pelo sinal gráfico", "Queda média depois da compra", "Perdas de mais de 10%", "Ganho − CDI por mês (pontos)",
            "Ganho total por R$ 1.000 em cada sinal"]
    for per in ("2018–2022", "2023–11/2026", "Completo"):
        print(f"\n===== {per}")
        print(R[R["Período"] == per].set_index(["Compra", "Venda"])[cols].to_string(float_format=lambda v: f"{v:,.3f}"))
    with pd.ExcelWriter("planilhas/papel_tecnico.xlsx") as w:
        R.to_excel(w, sheet_name="Resumo", index=False)
        pd.concat(OPS).to_excel(w, sheet_name="Operações", index=False)
    T = pd.concat([v.assign(fundo=f) for f, v in IND.items()]).reset_index().rename(columns={"index": "data"})
    T.to_csv("planilhas/tecnico/papel_indicadores_diarios.csv.gz", index=False, sep=";", decimal=",", encoding="utf-8-sig",
             date_format="%d/%m/%Y", float_format="%.4f")
    print("gravado: planilhas/papel_tecnico.xlsx e planilhas/tecnico/papel_indicadores_diarios.csv.gz")
