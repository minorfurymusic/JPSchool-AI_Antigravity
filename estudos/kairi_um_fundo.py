"""Carteira de R$ 10.000 com UM fundo de cada vez (todo o dinheiro na operação), 02/01/2018 a 09/11/2026.
Pedido do dono (2026-11-17).

Sinais: Conservadora 1 = gatilho 25% com mediana de negociação de 60 pregões de R$ 500 mil a R$ 1 milhão;
        Conservadora 2 = gatilho 20% (ou 15%, segunda versão) com mediana de R$ 1 milhão ou mais.
Regras da versão 3 (estudos/kairi_carteira_anos.py, reaproveitado): rendimento mantido, bloqueio de fundo que vai sair
da bolsa, rendimento zero, saída no fechamento acima da média de 200 pregões, prazo de 252 pregões, saída antecipada
por aviso, guarda de dado suspeito, CDI de 105% em lotes com IR e IOF, imposto de 20% do fundo com abatimento,
taxa de 0,03%.

Modos:
  segurar             fica no fundo até a saída; ao sair, segunda entrada: se algum sinal perdido no caminho ainda
                      estiver 15% ou mais abaixo da média (e sem ter voltado à média desde o sinal), compra o de maior
                      negociação na abertura seguinte.
  troca L / F         igual, mas com sinal novo e o fundo atual com lucro >= L e cota a no máximo F da média
                      (F = None: não olha a média), vende o atual na abertura e compra o novo na mesma abertura.
Vários sinais no mesmo dia: entra o de maior negociação típica (mediana de 60 pregões).

    PYTHONPATH=. python3 estudos/kairi_um_fundo.py
"""
import contextlib
import io
import runpy

import numpy as np
import pandas as pd

with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("estudos/kairi_carteira_anos.py", run_name="__main__")
G = g["simular"].__globals__
CAND, FD, MD, TS, NM, JA = G["CAND"], G["FD"], G["MD"], G["TS"], G["NM"], G["JA"]
saida_volta, saida_antecipada, direitos = G["saida_volta"], G["saida_antecipada"], G["direitos"]
Caixa, lote_liq, imposto_mes, serie_cdi = G["Caixa"], G["lote_liq"], G["imposto_mes"], G["serie_cdi"]
bloqueio = G["bloqueio"]
B3, CAP = G["B3"], 10000.0
FIM = NM - 1

# candidatos do gatilho de 25% (mesma construção do motor)
if 0.25 not in CAND:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(G["sinais"](F, 0.25)):
            md = int(F["mi"][s])
            if md >= JA and md + 1 < NM:
                d_ini = F["dates"][s - G["LAG_REND"]]
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VMED"][s]), vol_media=float(F["VOL"][s]),
                                        bloq=bloqueio(F["nome"], MD[md]),
                                        cut=G["corte_rendimento"](F["nome"], MD[md], d_ini), d_ini=d_ini))
    CAND[0.25] = lst


def sinais_do_dia(mi, X2):
    """Sinais cujo dia de ação (abertura) é o pregão mi: C1 (25%, 500 mil a 1 mi) e C2 (X2, >= 1 mi). Sem bloqueados."""
    out = []
    for c in CAND[0.25][mi]:
        if 500e3 <= c["vol"] < 1e6 and not c["bloq"] and not c["cut"]:
            out.append(dict(c, cart="C1"))
    for c in CAND[X2][mi]:
        if c["vol"] >= 1e6 and not c["bloq"] and not c["cut"]:
            out.append(dict(c, cart="C2"))
    return sorted(out, key=lambda c: (-c["vol"], c["F"]["nome"]))


def idx_fundo(F, mi):
    """Índice do fundo no pregão de mercado mi (ou -1)."""
    r = int(np.searchsorted(F["dates"], MD[mi]))
    return r if r < F["n"] and F["dates"][r] == MD[mi] else -1


def ultimo_idx(F, mi):
    return int(np.searchsorted(F["dates"], MD[mi], "right")) - 1


def rodar(X2, modo, L=None, Fg=None):
    cx = Caixa()
    cx.add(JA, CAP)
    pos = None                 # dict do fundo em carteira
    perdidos = []              # sinais que chegaram com dinheiro ocupado
    pend_rend = []             # (pregão de pagamento, valor)
    ganhos, pool, darf = {}, 0.0, []
    ops, diario = [], []
    a_receber = 0.0
    n_troca = n_seg = 0

    def comprar(c, mi, como):
        nonlocal pos
        F = c["F"]
        r = idx_fundo(F, mi)
        if r < 0 or F["NEG"][r] != 1 or not np.isfinite(F["A"][r]) or F["A"][r] <= 0:
            return False
        px = float(F["A"][r])
        liq = cx.saldo(mi - 1, MD[mi])
        reserva, pl = 0.0, pool          # guarda o imposto ainda não pago das vendas anteriores
        for m_ in sorted(ganhos):
            i_, pl = imposto_mes(ganhos[m_], pl)
            reserva += i_
        liq -= reserva * 1.01
        cot = int(liq / (px * (1 + B3)))
        if cot <= 0:
            return False
        custo = cot * px * (1 + B3)
        cx.resgatar(custo, mi - 1, MD[mi], "compra")
        k, mot, pxs = saida_volta(F, r)
        sinal_dia = MD[c["md"]]
        ra, doc = saida_antecipada(F, F["nome"], sinal_dia, mi, k, FIM)
        if ra is not None:
            k, mot, pxs = ra, "saída antecipada (aviso)", float(F["A"][ra])
            anteci = True
        else:
            anteci = False
        pos = dict(F=F, nome=F["nome"], cart=c["cart"], r=r, mi_e=mi, px=px, cot=cot, custo=custo, k=k, mot=mot, pxs=pxs,
                   mi_s=int(F["mi"][k]) if k < F["n"] else FIM, anteci=anteci, sinal=TS[c["md"]], como=como)
        return True

    def vender(mi, preco, motivo):
        nonlocal pos, a_receber
        F = pos["F"]
        bruto = pos["cot"] * preco
        liquido = bruto * (1 - B3)
        cx.add(mi, liquido)
        ganho = liquido - pos["custo"]
        mes = (pd.Timestamp(TS[mi]).year, pd.Timestamp(TS[mi]).month)
        ganhos[mes] = ganhos.get(mes, 0.0) + ganho
        # rendimentos com data-base de [entrada, venda)
        rend = 0.0
        for db, v, pg in direitos(pos["nome"], MD[pos["mi_e"]], MD[mi], False):
            val = v * pos["cot"]
            rend += val
            if pd.isna(pg):
                pg = db + np.timedelta64(11, "D")
            mp = int(np.searchsorted(MD, pg, "left"))
            if mp > FIM:
                a_receber += val
            else:
                pend_rend.append((max(mp, mi), val))
        ops.append(dict(carteira=pos["cart"], fundo=pos["nome"], como_entrou=pos["como"], sinal=pos["sinal"],
                        entrada=TS[pos["mi_e"]], preco_entrada=pos["px"], cotas=pos["cot"], valor_entrada=pos["custo"],
                        saida=TS[mi], preco_saida=preco, valor_saida=liquido, motivo=motivo, rendimentos=rend,
                        resultado=liquido - pos["custo"] + rend, resultado_pct=(liquido - pos["custo"] + rend) / pos["custo"],
                        dias=(pd.Timestamp(TS[mi]) - pd.Timestamp(TS[pos["mi_e"]])).days))
        pos = None

    def valor_pos(mi):
        F = pos["F"]
        r = ultimo_idx(F, mi)
        return pos["cot"] * float(F["C"][r])

    def vivo(c, mi):
        """Sinal perdido ainda serve para segunda entrada no fechamento de mi: cota >= 15% abaixo da média e sem ter
        tocado a média desde o sinal; até 252 pregões do sinal."""
        F = c["F"]
        if mi - c["md"] > 252:
            return False
        r = ultimo_idx(F, mi)
        s = int(np.searchsorted(F["dates"], MD[c["md"]]))
        if r <= s or not np.isfinite(F["mP"][r]):
            return False
        if (F["C"][s + 1:r + 1] >= F["mP"][s + 1:r + 1]).any():
            return False
        if bloqueio(F["nome"], MD[mi]):
            return False
        return F["C"][r] / F["mP"][r] - 1 <= -0.15

    seg_amanha = None
    for mi in range(JA, NM):
        dia = pd.Timestamp(TS[mi])
        # 1) rendimentos pagos hoje
        for p in [p for p in pend_rend if p[0] == mi]:
            cx.add(mi, p[1])
            pend_rend.remove(p)
        # 2) imposto do fundo: no último pregão de cada mês, paga o do mês anterior
        if mi == FIM or pd.Timestamp(TS[mi + 1]).month != dia.month:
            ant = (dia.year, dia.month - 1) if dia.month > 1 else (dia.year - 1, 12)
            if ant in ganhos:
                imp, pool = imposto_mes(ganhos.pop(ant), pool)
                if imp > 0:
                    cx.resgatar(imp, mi, MD[mi], "imposto")
                    darf.append(imp)
        # 3) abertura: segunda entrada decidida ontem, sinais do dia, troca
        hoje = sinais_do_dia(mi, X2)
        if pos is None and seg_amanha is not None:
            if comprar(seg_amanha, mi, "segunda entrada"):
                n_seg += 1
                perdidos = [p for p in perdidos if p["F"]["nome"] != seg_amanha["F"]["nome"]]
            seg_amanha = None
        for c in hoje:
            if pos is not None and c["F"]["nome"] == pos["nome"]:
                continue
            if pos is None:
                if comprar(c, mi, "sinal"):
                    continue
            elif modo == "troca":
                F = pos["F"]
                r = ultimo_idx(F, mi - 1)
                rend_ate = sum(v for db, v, pg in direitos(pos["nome"], MD[pos["mi_e"]], MD[mi - 1], True))
                lucro = (F["C"][r] + rend_ate) / pos["px"] - 1
                folga = F["mN"][r] / F["C"][r] - 1
                if lucro >= L and (Fg is None or folga <= Fg):
                    rr = idx_fundo(F, mi)
                    if rr >= 0 and F["NEG"][rr] == 1 and F["A"][rr] > 0:
                        vender(mi, float(F["A"][rr]), f"troca (lucro {lucro:.0%}, a {folga:.0%} da média)")
                        if comprar(c, mi, "troca"):
                            n_troca += 1
                            continue
            perdidos.append(c)
        # 4) fechamento: saída natural (ou antecipada na abertura) hoje
        if pos is not None and pos["mi_s"] == mi and pos["mot"] != G["ABERTO"]:
            if pos["anteci"]:
                vender(mi, pos["pxs"], pos["mot"])
            elif pos["k"] < pos["F"]["n"] and int(pos["F"]["mi"][pos["k"]]) == mi:
                vender(mi, pos["pxs"], pos["mot"])
            if pos is None and modo in ("segurar", "troca"):
                vivos = [c for c in perdidos if vivo(c, mi)]
                if vivos:
                    seg_amanha = sorted(vivos, key=lambda c: -c["vol"])[0]
        perdidos = [c for c in perdidos if mi - c["md"] <= 252]
        # 5) patrimônio do dia
        v = cx.saldo(mi, MD[mi]) + (valor_pos(mi) if pos is not None else 0.0)
        diario.append((dia, v))
    # fim: posição aberta a preço do último fechamento, imposto devido descontado
    aberto = None
    if pos is not None:
        aberto = dict(fundo=pos["nome"], entrada=TS[pos["mi_e"]], preco_entrada=pos["px"], valor=valor_pos(FIM))
    devido = 0.0
    for m in sorted(ganhos):
        imp, pool = imposto_mes(ganhos[m], pool)
        devido += imp
    serie = pd.Series(dict(diario))
    final = serie.iloc[-1] - devido + a_receber + sum(p[1] for p in pend_rend)
    O = pd.DataFrame(ops)
    return dict(serie=serie, final=final, ops=O, aberto=aberto, n_troca=n_troca, n_seg=n_seg,
                imposto=sum(darf) + devido, a_receber=a_receber)


CDI = pd.Series(serie_cdi(CAP, JA, FIM), index=pd.to_datetime(TS[JA:]))
ANOS_DIAS = (pd.Timestamp(TS[FIM]) - pd.Timestamp(TS[JA])).days / 365.25


def resumo(nome, r):
    s = r["serie"]
    dd = (s / s.cummax() - 1).min()
    o = r["ops"]
    fe = o[~o["motivo"].str.startswith("troca")] if len(o) else o
    anos = {a: s[s.index.year == a].iloc[-1] / (s[s.index.year < a].iloc[-1] if a > 2018 else CAP) - 1 for a in range(2018, 2027)}
    cdi_a = {a: CDI[CDI.index.year == a].iloc[-1] / (CDI[CDI.index.year < a].iloc[-1] if a > 2018 else CAP) - 1 for a in range(2018, 2027)}
    return dict(Simulação=nome, **{"Valor final (R$)": r["final"], "Retorno total": r["final"] / CAP - 1,
                                   "Ao ano": (r["final"] / CAP) ** (1 / ANOS_DIAS) - 1,
                                   "105% CDI no mesmo período": CDI.iloc[-1] / CAP - 1,
                                   "Maior queda no caminho": dd, "Operações": len(o) + (1 if r["aberto"] else 0),
                                   "Trocas": r["n_troca"], "Segundas entradas": r["n_seg"],
                                   "Operações com lucro": float((o["resultado"] > 0).mean()) if len(o) else np.nan,
                                   "Resultado médio por operação": float(o["resultado_pct"].mean()) if len(o) else np.nan,
                                   "Pior operação": float(o["resultado_pct"].min()) if len(o) else np.nan,
                                   "Imposto do fundo (R$)": r["imposto"],
                                   "Anos que ganhou do CDI": sum(anos[a] > cdi_a[a] for a in anos)}), anos, cdi_a


RUNS = {}
for X2, rot in ((0.20, "C2 20%"), (0.15, "C2 15%")):
    RUNS[f"{rot} | segurar + segunda entrada"] = rodar(X2, "segurar")
    RUNS[f"{rot} | troca: lucro ≥15% e a ≤5% da média"] = rodar(X2, "troca", 0.15, 0.05)
    RUNS[f"{rot} | troca: lucro ≥20%"] = rodar(X2, "troca", 0.20, None)
    RUNS[f"{rot} | troca: lucro ≥10% e a ≤10% da média"] = rodar(X2, "troca", 0.10, 0.10)

LIN, ANO = [], []
for nome, r in RUNS.items():
    l, anos, cdi_a = resumo(nome, r)
    LIN.append(l)
    ANO.append(dict(Simulação=nome, **{str(a): anos[a] for a in anos}))
ANO.append(dict(Simulação="105% do CDI (R$ 10 mil)", **{str(a): cdi_a[a] for a in cdi_a}))
T = pd.DataFrame(LIN)
A = pd.DataFrame(ANO)
pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 30)
print(T.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print(A.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

# conferências
for nome, r in RUNS.items():
    s = r["serie"]
    assert s.min() > 0, nome
    o = r["ops"]
    if len(o):
        assert (pd.to_datetime(o["entrada"]) > pd.to_datetime(o["sinal"])).all(), "compra no dia do sinal"
print("conferências: patrimônio sempre positivo; nenhuma compra no dia do sinal: PASSOU")

with pd.ExcelWriter("planilhas/kairi_um_fundo.xlsx") as w:
    T.to_excel(w, sheet_name="Resumo", index=False)
    A.to_excel(w, sheet_name="Ano a ano", index=False)
    for i, (nome, r) in enumerate(RUNS.items(), 1):
        o = r["ops"].copy()
        if r["aberto"]:
            o = pd.concat([o, pd.DataFrame([dict(fundo=r["aberto"]["fundo"], entrada=r["aberto"]["entrada"],
                                                 preco_entrada=r["aberto"]["preco_entrada"], motivo="em aberto em 09/11/2026",
                                                 valor_saida=r["aberto"]["valor"])])], ignore_index=True)
        o.insert(0, "Simulação", nome)
        o.to_excel(w, sheet_name=f"Operações {i}", index=False)
    pd.DataFrame({n: r["serie"] for n, r in RUNS.items()}).assign(**{"105% CDI": CDI}).to_excel(w, sheet_name="Patrimônio dia a dia")
print("gravado: planilhas/kairi_um_fundo.xlsx")
