"""Tipo 1 trade: o caminho de cada operação depois da compra, por tipo de venda (perguntas do dono, 18/11/2026).

Mesmos sinais e compra "A" (abertura seguinte) de estudos/descontado_saidas.py; prazo de 1 ano.
Por operação ("ret" = (fechamento + rendimentos recebidos) ÷ custo − 1, dia a dia):
  pregões; resultado; pior momento (menor ret até a venda) e em que pregão; pico (maior ret até a venda) e em que
  pregão; devolvido = pico − resultado; ret com 20, 40 e 60 pregões.
  "Continuou caindo" = ret ficou abaixo de 0 em algum dia; também abaixo de −5%.
  "Chegou perto do alvo e recuou": alvos fixos (+10%, +15%) e Fibonacci: pico >= 70% do caminho até o alvo sem atingir;
  vendas sem alvo (médias, Bollinger): pico >= +5% e venda abaixo da metade do pico.
  "Subiu e entregou": pico >= +5% e resultado < 0.
Características na compra (do sinal do mês): classe, preço/patrimônio, rendimento, rendimento acima da classe,
  cobertura, oscilação, queda em 6 meses, nota; fase da Selic (subindo/parada/caindo, 90 dias).
Cortes de proteção (EXPLORATÓRIOS, regras novas aplicadas sobre cada venda; vale o que acontecer primeiro):
  Z zero a zero: depois de o ret chegar a +5%, sai no primeiro fechamento com ret <= 0.
  M protege metade: depois de o ret chegar a +8%, sai quando o ret cair para a metade do pico.
  T tempo: no 60º pregão, se o ret estiver abaixo de −5%, sai.

    PYTHONPATH=. python3 estudos/descontado_caminho.py
"""
import numpy as np
import pandas as pd

import estudos.descontado_saidas as SA

DS, RD, RF, SER = SA.DS, SA.RD, SA.RF, SA.SER
PRAZO, B3 = 252, 0.0003


def caminho(f, ent):
    s = SER[f]
    px0 = float(s.loc[ent, "abertura"])
    if not px0 > 0:
        return None
    custo = px0 * (1 + B3)
    y = s.loc[ent:].iloc[:PRAZO]
    r = RF.get(f)
    pg = r[r["data_base"] >= ent] if r is not None else None
    rend = np.array([float(pg.loc[pg["data_pagamento"] <= dd, "valor (R$/cota)"].sum()) if pg is not None else 0.0 for dd in y.index])
    c = y["fechamento"].to_numpy(float)
    return dict(y=y, c=c, ret=(c * (1 - B3) + rend) / custo - 1, rend=rend / custo, px0=px0, T=float(s.loc[ent, "topo252"]))


def regra(cm, venda):
    """Índice de venda pela regra (ou None) e o alvo em ret quando existe."""
    y, c, ret, px0 = cm["y"], cm["c"], cm["ret"], cm["px0"]
    alvo = None
    if venda in ("alvo10", "alvo15"):
        alvo = 0.10 if venda == "alvo10" else 0.15
        ok = ret >= alvo
    elif venda in ("mm21x70", "mm21x90"):
        lg = y["mm70" if venda == "mm21x70" else "mm90"].to_numpy(float)
        cu = y["mm21"].to_numpy(float)
        ok = np.zeros(len(y), bool)
        ok[1:] = (cu[:-1] >= lg[:-1]) & (cu[1:] < lg[1:])
    elif venda.startswith("fib"):
        if not cm["T"] > px0:
            return "sem_topo", None
        pr = px0 + {"fib38": 0.382, "fib50": 0.5, "fib62": 0.618}[venda] * (cm["T"] - px0)
        alvo = pr / px0 - 1
        ok = c >= pr
    else:
        ok = c >= y["bb_sup"].to_numpy(float)
    h = np.flatnonzero(ok)
    return (int(h[0]) if len(h) else None), alvo


def protecao(ret, k_base, tipo):
    """Índice de saída com o corte de proteção (o que vier primeiro com a venda base)."""
    n = k_base + 1
    if tipo == "Z":
        arm = np.flatnonzero(ret[:n] >= 0.05)
        if len(arm):
            z = np.flatnonzero(ret[arm[0]:n] <= 0)
            if len(z):
                return arm[0] + z[0]
    elif tipo == "M":
        arm = np.flatnonzero(ret[:n] >= 0.08)
        if len(arm):
            pico = np.maximum.accumulate(ret[:n])
            z = np.flatnonzero((np.arange(n) >= arm[0]) & (ret[:n] <= pico / 2))
            if len(z):
                return z[0]
    elif tipo == "T":
        if n > 60 and ret[59] < -0.05:
            return 59
    return k_base


if __name__ == "__main__":
    pd.set_option("display.width", 300)
    pd.set_option("display.max_columns", 40)
    fms = [d for d in RD.FIM_MES if d < RD.DIAS[-1]]
    sinais = []
    for d in fms:
        C = DS.candidatos_v2(d)
        sinais.append((d, C.head(5).assign(sinal=d) if len(C) else pd.DataFrame()))
    print("sinais prontos", flush=True)
    LIN, PROT = [], []
    for v in SA.VENDAS:
        livre = {}
        for d, C in sinais:
            for r in C.itertuples():
                f = r.fundo
                if livre.get(f, pd.Timestamp.min) > d:
                    continue
                ent = SA.dia_compra(f, d, "A", None)
                if ent is None:
                    continue
                cm = caminho(f, ent)
                if cm is None:
                    continue
                k, alvo = regra(cm, v)
                if k == "sem_topo":
                    continue
                ret, n = cm["ret"], len(cm["ret"])
                if k is None:
                    if n < PRAZO:
                        livre[f] = cm["y"].index[-1]
                        continue                       # em andamento: fica fora das contas
                    k, sit = n - 1, "prazo de 1 ano"
                else:
                    sit = "vendeu pela regra"
                livre[f] = cm["y"].index[k]
                a = ret[: k + 1]
                pico, ipico = float(a.max()), int(a.argmax())
                perto = (alvo is not None and sit != "vendeu pela regra" and pico >= 0.7 * alvo) if alvo is not None else \
                    (pico >= 0.05 and a[-1] < pico / 2)
                LIN.append(dict(venda=SA.NOMES[v], fundo=f, entrada=ent, saida=cm["y"].index[k], situacao=sit, pregoes=k + 1,
                                resultado=float(a[-1]), pior_momento=float(a.min()), pregao_do_pior=int(a.argmin()) + 1,
                                pico=pico, pregao_do_pico=ipico + 1, devolvido=pico - float(a[-1]),
                                ret20=float(ret[19]) if n > 19 else np.nan, ret40=float(ret[39]) if n > 39 else np.nan,
                                ret60=float(ret[59]) if n > 59 else np.nan, chegou_perto_e_recuou=bool(perto),
                                subiu_e_entregou=bool(pico >= 0.05 and a[-1] < 0),
                                cdi=RD.cdi_liq(ent, cm["y"].index[k], 1.0) - 1, classe=r.tipo, pvp=r.pvp, rendimento=r.dy,
                                acima_classe=r.acima_tipo, cobertura=r.cobertura, oscilacao=r.oscilacao, queda_6m=r.queda_6m,
                                nota=r.nota, selic=RD.fase_selic(ent)))
                for t in ("Z", "M", "T"):
                    kp = protecao(ret, k, t)
                    PROT.append(dict(venda=SA.NOMES[v], corte=t, resultado=float(ret[kp]), pregoes=kp + 1, mudou=kp != k,
                                     cdi=RD.cdi_liq(ent, cm["y"].index[kp], 1.0) - 1))
                PROT.append(dict(venda=SA.NOMES[v], corte="sem corte", resultado=float(a[-1]), pregoes=k + 1, mudou=False,
                                 cdi=RD.cdi_liq(ent, cm["y"].index[k], 1.0) - 1))
        print(f"{v} pronto", flush=True)
    O, PR = pd.DataFrame(LIN), pd.DataFrame(PROT)

    def q1(x):
        cai = x["pior_momento"] < 0
        sub = x["pico"] > 0
        return pd.Series({
            "Operações": len(x), "Pregões médios": x["pregoes"].mean(), "Pregões medianos": x["pregoes"].median(),
            "Venderam pela regra (pregões médios)": x.loc[x["situacao"] == "vendeu pela regra", "pregoes"].mean(),
            "Continuaram caindo depois da compra (ret < 0 algum dia)": cai.mean(),
            "Queda média depois da compra (das que caíram)": x.loc[cai, "pior_momento"].mean(),
            "Caíram mais de 5%": (x["pior_momento"] < -0.05).mean(),
            "Pregão médio do pior momento": x["pregao_do_pior"].mean(),
            "Subiram depois da compra (pico > 0)": sub.mean(), "Subida média (pico das que subiram)": x.loc[sub, "pico"].mean(),
            "Chegaram perto do alvo e recuaram": x["chegou_perto_e_recuou"].mean(),
            "Quanto tinham subido (pico médio dessas)": x.loc[x["chegou_perto_e_recuou"], "pico"].mean(),
            "Subiram +5% ou mais e terminaram negativas": x["subiu_e_entregou"].mean(),
            "Com prejuízo": (x["resultado"] < 0).mean(), "Prejuízo médio": x.loc[x["resultado"] < 0, "resultado"].mean(),
            "Prejuízo e 1 ano parado": ((x["resultado"] < 0) & (x["situacao"] == "prazo de 1 ano")).mean(),
            "Resultado médio": x["resultado"].mean(),
            "Ganho por mês aplicado": x["resultado"].sum() / x["pregoes"].sum() * 21,
            "CDI por mês aplicado": x["cdi"].sum() / x["pregoes"].sum() * 21})
    R1 = O.groupby("venda", sort=False).apply(q1, include_groups=False)
    print("1) CAMINHO DEPOIS DA COMPRA, POR VENDA")
    print(R1.T.to_string(float_format=lambda v: f"{v:,.3f}"))

    def q2(x):
        L, G = x[x["resultado"] < 0], x[x["resultado"] >= 0]
        out = {}
        for c in ("pvp", "rendimento", "acima_classe", "cobertura", "oscilacao", "queda_6m", "nota"):
            out[f"{c}: prejuízo / lucro"] = f"{L[c].median():.3f} / {G[c].median():.3f}"
        for s in ("subindo", "parada", "caindo"):
            k = x["selic"] == s
            out[f"prejuízo com Selic {s}"] = f"{(x.loc[k, 'resultado'] < 0).mean():.0%} de {k.sum()}"
        for cl in ("Papel", "Tijolo", "Fundo de fundos", "Híbrido"):
            k = x["classe"] == cl
            out[f"prejuízo em {cl}"] = f"{(x.loc[k, 'resultado'] < 0).mean():.0%} de {k.sum()}"
        for c, nome in (("ret20", "20"), ("ret40", "40"), ("ret60", "60")):
            k = x[c] < -0.05
            out[f"abaixo de −5% com {nome} pregões: terminaram no prejuízo"] = f"{(x.loc[k, 'resultado'] < 0).mean():.0%} de {k.sum()}"
            k2 = x[c] >= 0
            out[f"positivas com {nome} pregões: terminaram no prejuízo"] = f"{(x.loc[k2, 'resultado'] < 0).mean():.0%} de {k2.sum()}"
        return pd.Series(out)
    R2 = O.groupby("venda", sort=False).apply(q2, include_groups=False)
    print("\n2) PREJUÍZO x LUCRO: características na compra (mediana) e sinais no caminho")
    print(R2.T.to_string())

    def q3(x):
        return pd.Series({"Com prejuízo": (x["resultado"] < 0).mean(), "Perdas de mais de 10%": (x["resultado"] < -0.10).mean(),
                          "Resultado médio": x["resultado"].mean(), "Pregões médios": x["pregoes"].mean(),
                          "Ganho por mês aplicado": x["resultado"].sum() / x["pregoes"].sum() * 21,
                          "CDI por mês aplicado": x["cdi"].sum() / x["pregoes"].sum() * 21, "Operações em que o corte agiu": x["mudou"].mean()})
    R3 = PR.groupby(["venda", "corte"], sort=False).apply(q3, include_groups=False)
    print("\n3) CORTES DE PROTEÇÃO (exploratório): Z zero a zero depois de +5%; M protege metade depois de +8%; T tempo (60 pregões abaixo de −5%)")
    print(R3.to_string(float_format=lambda v: f"{v:,.3f}"))
    with pd.ExcelWriter("planilhas/descontado_caminho.xlsx") as w:
        R1.T.reset_index().rename(columns={"index": "Medida"}).to_excel(w, sheet_name="1 Caminho por venda", index=False)
        R2.T.reset_index().rename(columns={"index": "Medida"}).to_excel(w, sheet_name="2 Prejuízo x lucro", index=False)
        R3.reset_index().to_excel(w, sheet_name="3 Cortes de proteção", index=False)
        O.to_excel(w, sheet_name="Operações", index=False)
        O[O["resultado"] < 0].sort_values(["venda", "resultado"]).to_excel(w, sheet_name="Só as com prejuízo", index=False)
    print("gravado: planilhas/descontado_caminho.xlsx")
