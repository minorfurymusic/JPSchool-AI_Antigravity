"""Papel Padrão: formas de COMPRAR (pedido do dono, 18/11/2026). Regras fixadas antes de rodar.

Sinal: em cada fim de mês, os 5 de maior nota da classe Papel (descontado_saudavel.candidatos_v2). Venda: alvo +10%
(preço + rendimentos com data-com desde a compra, sobre o custo médio), prazo de 252 pregões contados da 1ª compra.
Contas: data-com, 20% de IR sobre ganho na cota, taxa de 0,03%. Avisos de rendimento suspeitos
(estudos/rendimentos_suspeitos.py: > 10% do preço sem queda compatível da cota) são ignorados. Fundo só entra de novo depois de sair.
Compras (todas na abertura do pregão seguinte ao gatilho; gatilho procurado do 1º pregão depois do sinal até o último
pregão do mês seguinte; sem gatilho = não compra, dinheiro fica no CDI):
  A          sem gatilho (abertura do pregão seguinte ao sinal)
  9.1        média exponencial de 9 fechamentos sobe hoje e tinha caído ontem (virada para cima)
  IFR2       IFR de 2 períodos (Wilder) < 10
  reversao   fechamento > máxima do dia anterior, com a mínima de 20 pregões feita nos últimos 5 pregões
  Dois passos (18/11/2026; atenção = fundo no sinal do mês; referência = fechamento do dia do sinal; gatilho procurado
  em até 60 pregões depois do sinal):
  q3 / q5    compra quando o fechamento cair 3% / 5% abaixo da referência
  q3r / q5r  depois de cair 3% / 5%, compra quando o fechamento subir 1% acima da menor mínima desde o sinal (repique)
  duas       metade na abertura seguinte ao sinal; a outra metade na abertura seguinte ao 1º fechamento 5% abaixo do
             preço da 1ª compra, em até 60 pregões (se não cair, fica só a metade e a outra metade no CDI)

    PYTHONPATH=. python3 estudos/papel_entradas.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saidas as SA
from estudos.rendimentos_suspeitos import suspeitos

DS, RD, RF, SER = SA.DS, SA.RD, SA.RF, SA.SER
PRAZO, B3, IR, ALVO = 252, 0.0003, 0.20, 0.10

# indicadores extras sobre a série dos pregões com negócio
for f, s in SER.items():
    c = s["fechamento"]
    s["mme9"] = c.ewm(span=9, adjust=False).mean()
    d = c.diff()
    up, dn = d.clip(lower=0), (-d).clip(lower=0)
    rs = up.ewm(alpha=1 / 2, adjust=False).mean() / dn.ewm(alpha=1 / 2, adjust=False).mean()
    s["ifr2"] = 100 - 100 / (1 + rs)
    mx = x = None
    P = RD.PF[f]
    P = P[P["negociou (1/0)"] == 1]
    s["maxima"] = P["maxima"].reindex(s.index)
    s["minima"] = P["minima"].reindex(s.index)
    s["min20"] = s["minima"].rolling(20).min()


def gatilho_queda(s, d_sinal, tipo):
    ref = float(s.loc[:d_sinal, "fechamento"].iloc[-1])
    z = s.loc[d_sinal + pd.Timedelta(days=1):].iloc[:60]
    if z.empty:
        return None
    x = 0.03 if tipo.startswith("q3") else 0.05
    caiu = np.flatnonzero(z["fechamento"].to_numpy(float) <= ref * (1 - x))
    if not len(caiu):
        return None
    k = caiu[0]
    if tipo.endswith("r"):
        mn = np.minimum.accumulate(z["minima"].to_numpy(float))
        c = z["fechamento"].to_numpy(float)
        rep = np.flatnonzero((np.arange(len(z)) > k) & (c >= mn * 1.01))
        if not len(rep):
            return None
        k = rep[0]
    j = s.index.get_loc(z.index[k])
    return s.index[j + 1] if j + 1 < len(s) else None


def gatilho(s, ini, fim, tipo):
    z = s.loc[ini:fim]
    if z.empty:
        return None
    if tipo == "A":
        return z.index[0]
    full = s.loc[:fim]
    if tipo == "9.1":
        m = full["mme9"]
        ok = (m > m.shift(1)) & (m.shift(1) < m.shift(2))
    elif tipo == "IFR2":
        ok = full["ifr2"] < 10
    else:  # reversao
        fez_min = (full["minima"] <= full["min20"]).rolling(5).max() > 0
        ok = (full["fechamento"] > full["maxima"].shift(1)) & fez_min
    ok = ok.loc[ini:fim]
    t = ok.index[ok.to_numpy(bool)]
    if len(t) == 0:
        return None
    k = s.index.get_loc(t[0])
    return s.index[k + 1] if k + 1 < len(s) else None


def operar(f, compras):
    """compras: [(dia, fração do dinheiro)]. Devolve dict da operação (alvo +10% sobre o custo médio)."""
    s = SER[f]
    ent = compras[0][0]
    y = s.loc[ent:].iloc[:PRAZO]
    r = RF.get(f)
    n = len(y)
    cotas, custo = np.zeros(n), np.zeros(n)
    for dia, fr in compras:
        k = y.index.get_loc(dia) if dia in y.index else None
        if k is None:
            continue
        px = float(s.loc[dia, "abertura"])
        cotas[k:] += fr / (px * (1 + B3))
        custo[k:] += fr
    if r is not None:
        rr = r[r["data_base"] >= ent]
        rr = rr[np.array([(f, db) not in suspeitos() for db in rr["data_base"]], dtype=bool)]   # avisos suspeitos ignorados
        rr = rr.groupby("data_base")["valor (R$/cota)"].sum()
        div = np.zeros(n)
        for db, v in rr.items():
            k = y.index.searchsorted(db)
            if k < n:
                div[k] += v * cotas[k]          # rendimento sobre as cotas que tinha na data-com
        rend = np.cumsum(div)
    else:
        rend = np.zeros(n)
    c = y["fechamento"].to_numpy(float)
    ret = (c * (1 - B3) * cotas + rend) / custo - 1
    h = np.flatnonzero(ret >= ALVO)
    if len(h):
        k, sit = h[0], "alvo"
    elif n >= PRAZO:
        k, sit = n - 1, "prazo de 1 ano"
    else:
        return None                                   # em andamento
    venda = c[k] * (1 - B3) * cotas[k]
    imp = IR * max(venda - custo[k], 0)
    res = (venda - imp + rend[k]) / custo[k] - 1
    usado = custo[k]                                   # fração do dinheiro que entrou (duas partes pode ser 0,5)
    return dict(fundo=f, entrada=ent, saida=y.index[k], situacao=sit, pregoes=k + 1, resultado=res, fracao_aplicada=usado,
                pior_momento=float(ret[: k + 1].min()), cdi=RD.cdi_liq(ent, y.index[k], 1.0) - 1)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    SIN = []
    for i, d in enumerate(fms):
        C = DS.candidatos_v2(d)
        if C.empty:
            continue
        prox = fms[i + 1] if i + 1 < len(fms) else RD.DIAS[-1]
        SIN.append((d, prox, list(C[C["tipo"] == "Papel"]["fundo"].head(5))))
    print("sinais prontos", flush=True)
    RES, OPS = [], []
    for tipo in ("A", "9.1", "IFR2", "reversao", "duas", "q3", "q5", "q3r", "q5r"):
        livre, ops, sem = {}, [], 0
        for d, prox, fundos in SIN:
            for f in fundos:
                if f not in SER or livre.get(f, pd.Timestamp.min) > d:
                    continue
                s = SER[f]
                ini = d + pd.Timedelta(days=1)
                if tipo == "duas":
                    e1 = gatilho(s, ini, prox, "A")
                    if e1 is None:
                        continue
                    p1 = float(s.loc[e1, "abertura"])
                    z = s.loc[e1:].iloc[:60]
                    t = z.index[(z["fechamento"] <= 0.95 * p1).to_numpy()]
                    compras = [(e1, 0.5)]
                    if len(t):
                        k = s.index.get_loc(t[0])
                        if k + 1 < len(s):
                            compras.append((s.index[k + 1], 0.5))
                elif tipo.startswith("q"):
                    e1 = gatilho_queda(s, d, tipo)
                    if e1 is None:
                        sem += 1
                        continue
                    compras = [(e1, 1.0)]
                else:
                    e1 = gatilho(s, ini, prox, tipo)
                    if e1 is None:
                        sem += 1
                        continue
                    compras = [(e1, 1.0)]
                o = operar(f, compras)
                if o is None:
                    livre[f] = RD.DIAS[-1]
                    continue
                o["compra"] = tipo
                ops.append(o)
                livre[f] = o["saida"]
        O = pd.DataFrame(ops)
        OPS.append(O)
        w = O["fracao_aplicada"]
        RES.append({"Compra": tipo, "Operações": len(O), "Sinais sem gatilho (não comprou)": sem,
                    "Com lucro": (O["resultado"] > 0).mean(), "Bateram o CDI do mesmo período": (O["resultado"] > O["cdi"]).mean(),
                    "Resultado médio": O["resultado"].mean(), "Pregões médios": O["pregoes"].mean(),
                    "Chegaram ao alvo": (O["situacao"] == "alvo").mean(),
                    "Queda média depois da compra": O["pior_momento"].mean(),
                    "Perdas de mais de 10%": (O["resultado"] < -0.10).mean(),
                    "Prejuízo e 1 ano parado": ((O["resultado"] < 0) & (O["situacao"] == "prazo de 1 ano")).mean(),
                    "Ganho por mês aplicado": (O["resultado"] * w).sum() / (O["pregoes"] * w).sum() * 21,
                    "CDI por mês aplicado": (O["cdi"] * w).sum() / (O["pregoes"] * w).sum() * 21,
                    "Ganho total em reais por R$ 1.000 em cada sinal": float((O["resultado"] * w).sum() * 1000)})
        print(tipo, "pronto", flush=True)
    R = pd.DataFrame(RES)
    R["Ganho − CDI por mês (pontos)"] = (R["Ganho por mês aplicado"] - R["CDI por mês aplicado"]) * 100
    print(R.set_index("Compra").T.to_string(float_format=lambda v: f"{v:,.3f}"))
    with pd.ExcelWriter("planilhas/papel_entradas.xlsx") as w:
        R.to_excel(w, sheet_name="Resumo", index=False)
        pd.concat(OPS).to_excel(w, sheet_name="Operações", index=False)
    print("gravado: planilhas/papel_entradas.xlsx")
