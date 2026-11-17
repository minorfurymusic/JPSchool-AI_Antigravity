"""Simulacao de uma carteira de R$ 20.000 com a estrategia do Kairi, de 02/01/2026 (1o pregao do ano) a 09/11/2026.

Duas sub-carteiras independentes, cada uma com caixa proprio de R$ 10.000:
    CONSERVADORA: gatilho 20% abaixo da media de 200 pregoes, rendimento mantido.
    AGRESSIVA:    gatilho 15% abaixo da media de 200 pregoes, rendimento mantido.
    Variante extra da conservadora: gatilho 30%.
Mesmas regras de universo, filtros, guarda de dados, entrada (abertura do pregao seguinte ao sinal) e saida (volta a
media, prazo de 252 pregoes) de estudos/auditoria_bloco2.py (copia verificada de estudos/kairi_ordens.py). As funcoes de
carga, sinais e saida foram COPIADAS para ca; nenhum arquivo existente e alterado. A logica de caixa limitado vem de
estudos/kairi_carteira.py (vende antes de comprar; maior volume de 60 dias primeiro; limite de 2% do negociado).

Diferencas deliberadas em relacao ao motor antigo (pedido do dono):
  - ordem de R$ 1.000 (variantes R$ 500 e R$ 2.000); minimo de R$ 200;
  - rendimentos entram no caixa na data de PAGAMENTO (planilhas/rendimentos_pagamentos.csv), com direito pela
    data-base (mesma regra de kairi_ordens.py: cotas em carteira no fechamento da data-base);
  - caixa parado em 105% do CDI (planilhas/cdi.csv), em lotes, com IR regressivo e IOF por lote;
  - imposto do FII: 20% sobre o ganho liquido do mes, prejuizo abate; DARF no ultimo dia util do mes seguinte.

Rodar com:
    cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/kairi_carteira_2026.py
Saidas: planilhas/kairi_carteira_2026.xlsx e docs/SIMULACAO_KAIRI_2026.md (os dois sao gerados a cada rodada).
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

np.seterr(all="ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 80)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
SAIDA_XLSX = PL / "kairi_carteira_2026.xlsx"

INICIO_SIM = pd.Timestamp("2026-01-02")
CAP_SUB = 10000.0
B3 = 0.0003
IR_OP = 0.20
EXCLUIDOS = {"XPPR11", "CARE11"}
N = 200
PRAZO = 252
LAG_REND = 126
K_REND = 0.95
PCT_VOL = 0.02
MIN_OP = 200.0
ORDEM_BASE = 1000.0
ORDENS = [500.0, 1000.0, 2000.0]
VOLTA, PRAZO_M, SAIU, GUARDA, ABERTO = "volta à média", "prazo", "fundo saiu da bolsa", "dado suspeito", "em aberto"
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]
# (nome, gatilho)
SUBS = {"Conservadora": 0.20, "Agressiva": 0.15}
CONS30 = ("Conservadora 30%", 0.30)
GATILHOS = [0.15, 0.20, 0.30]


# ---------------------------------------------------------------- formatacao
def isnan(x):
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


def br(x, d=2):
    if isnan(x):
        return "nd"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x, d=2):
    return "nd" if isnan(x) else "R$ " + br(x, d)


def pct(x, d=1):
    return "nd" if isnan(x) else br(100 * x, d) + "%"


def dt(x):
    return "" if x is None or pd.isna(x) else pd.Timestamp(x).strftime("%d/%m/%Y")


# ---------------------------------------------------------------- carga (copiada de auditoria_bloco2.py)
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base", "data_pagamento"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
PG = carregar("rendimentos_pagamentos").dropna(subset=["data_base"]).reset_index(drop=True)
FU = carregar("fundos")
CDI = carregar("cdi")
AMZ = carregar("amortizacoes")
C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG, C_REND, C_PVP, C_PAT = "negociou (1/0)", "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL, C_AMO = "volume_medio_60 (R$)", "amortizacao_12m (1/0)"
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
MD = MK["data"].to_numpy("datetime64[D]")
TS = list(MK["data"])
NM = len(MD)
IDX = MK["indice_mercado"].to_numpy(float)
J0 = int(np.searchsorted(MD, np.datetime64(INICIO_SIM, "D")))
assert TS[J0] == INICIO_SIM, "02/01/2026 deveria ser pregao"
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))
CD_D = CDI["data"].to_numpy("datetime64[D]")
CD_I = CDI["indice_105_do_cdi"].to_numpy(float)
assert CD_D[-1] >= MD[-1], "cdi.csv nao cobre a ultima data da base"
_pos = np.searchsorted(CD_D, MD)
assert (CD_D[_pos] == MD).all(), "todo pregao do mercado deveria estar no cdi.csv"
CIDX = CD_I[_pos]                                   # indice 105% CDI alinhado aos pregoes de mercado
LASTM = np.array([(mi == NM - 1) or (TS[mi + 1].month != TS[mi].month) for mi in range(NM)])
ULT_MES = {}                                        # (ano, mes) -> ultimo pregao (indice) do mes
for _mi in range(NM):
    ULT_MES[(TS[_mi].year, TS[_mi].month)] = _mi


def aliq_rf(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


FD = {}
for nome, g in PR.groupby("fundo", sort=False):
    dates = g["data"].to_numpy("datetime64[D]")
    n = len(dates)
    A, H, L, C = (g[c].to_numpy(float) for c in [C_AB, C_MX, C_MN, C_FE])
    R, PVP, VOL = (g[c].to_numpy(float) for c in [C_REND, C_PVP, C_VOL])
    AMO, NEG, PAT = (g[c].to_numpy(float) for c in [C_AMO, C_NEG, C_PAT])
    univ = (PAT >= 50e6) & (VOL >= 25000) & (R > 0) & (AMO == 0) & (PVP >= 0.30) & (PVP <= 3.0)
    if nome in EXCLUIDOS:
        univ[:] = False
    bad = np.zeros(n, bool)
    if n > 1:
        gap = np.diff(dates).astype("timedelta64[D]").astype(int)
        ret = C[1:] / C[:-1] - 1
        bad[1:] = (gap > 15) | (ret > 0.60) | (ret < -0.45)
    cbad = np.r_[0, np.cumsum(bad)]
    Cs = pd.Series(C)
    mN = Cs.rolling(N, min_periods=N).mean().to_numpy()
    mP = np.r_[np.nan, mN[:-1]]
    k200 = C / mP - 1
    sim = np.zeros(n, bool)
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= K_REND * R[:-LAG_REND]
    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome
    FD[nome] = dict(nome=nome, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, VOL=VOL, NEG=NEG,
                    univ=univ, bad=bad, cbad=cbad, mN=mN, mP=mP, k200=k200, sim=sim,
                    aberto=int(mi[-1]) >= NM - 21)

# direitos de rendimento por fundo: data-base, valor por cota, data de pagamento (pode faltar)
PGF = {}
for f_, g in PG.sort_values(["data_base", "data_pagamento"]).groupby("fundo"):
    PGF[f_] = (g["data_base"].to_numpy("datetime64[D]"), g["valor (R$/cota)"].to_numpy(float),
               g["data_pagamento"].to_numpy("datetime64[D]"))


def direitos(f, D, S, incl):
    """Avisos com data-base em [D, S) (ou [D, S] se incl): lista de (data_base, valor/cota, data_pagamento ou NaT)."""
    if f not in PGF:
        return []
    bd, v, pg = PGF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return [(bd[i], v[i], pg[i]) for i in range(a, b)]


def sinais(F, X):
    n = F["n"]
    k = F["k200"]
    cross = np.zeros(n, bool)
    cross[1:] = (k[1:] <= -X) & (k[:-1] > -X)
    base = cross & F["univ"] & F["sim"]
    base[:N] = False
    idx = np.flatnonzero(base)
    ok = np.zeros(n, bool)
    if idx.size:
        jan = (F["cbad"][idx + 1] - F["cbad"][idx - N + 1]) > 0
        ok[idx[~jan]] = True
    return ok


# candidatos por pregao de execucao; so sinais com data >= 02/01/2026 (carteira comeca vazia)
CAND = {}
for X in GATILHOS:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if md >= J0 and md + 1 < NM:
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VOL"][s])))
    CAND[X] = lst


def regra_fim(F, e):
    last = F["n"] - 1
    if e + PRAZO <= last:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO])
    if F["aberto"]:
        return last, ABERTO, float(F["C"][last])
    return last, SAIU, float(F["C"][last])


def saida_volta(F, e):
    last = F["n"] - 1
    jan = min(e + PRAZO, last)
    kg = kv = None
    if jan > e:
        w = np.flatnonzero(F["bad"][e + 1:jan + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        h = np.flatnonzero(F["H"][e + 1:jan + 1] >= F["mN"][e:jan])
        if h.size:
            kv = e + 1 + int(h[0])
    if kg is not None and (kv is None or kg <= kv):
        k = kg - 1
        return k, GUARDA, float(F["C"][k])
    if kv is not None:
        media = float(F["mN"][kv - 1])
        a = float(F["A"][kv])
        return kv, VOLTA, (max(a, media) if np.isfinite(a) else media)
    return regra_fim(F, e)


# ---------------------------------------------------------------- caixa em 105% do CDI, em lotes
def lote_liq(mi0, p, ref_mi, data_res):
    """Valor liquido de um lote de principal p aplicado no pregao mi0, resgatado em data_res com o indice do pregao ref_mi.
    Bruto = p*(I[ref]/I[mi0]-1); IOF regressivo (dias corridos < 30) sobre o rendimento; IR regressivo sobre o que sobra."""
    ref = max(ref_mi, mi0)
    bruto = p * (CIDX[ref] / CIDX[mi0] - 1)
    dias = int((data_res - MD[mi0]) / np.timedelta64(1, "D"))
    iof = IOF[dias - 1] / 100 if 1 <= dias <= 29 else 0.0
    iofv = bruto * iof
    irv = (bruto - iofv) * aliq_rf(dias)
    return p + bruto - iofv - irv, bruto, iofv, irv, dias


class Caixa:
    def __init__(self):
        self.lots = []          # [pregao de entrada, principal restante], em ordem cronologica (mais antigo primeiro)
        self.log = []           # resgates (para conferencia)
        self.iof = 0.0
        self.ir = 0.0

    def add(self, mi, v):
        if v > 1e-12:
            self.lots.append([mi, v])

    def saldo(self, ref_mi, data):
        return sum(lote_liq(l[0], l[1], ref_mi, data)[0] for l in self.lots)

    def resgatar(self, valor, ref_mi, data, motivo):
        """Tira `valor` liquido do caixa, do lote mais antigo para o mais novo (resgate parcial proporcional)."""
        rem = valor
        for l in list(self.lots):
            if rem <= 1e-9:
                break
            net, bruto, iofv, irv, dias = lote_liq(l[0], l[1], ref_mi, data)
            if net <= 1e-12:
                self.lots.remove(l)
                continue
            f = 1.0 if net <= rem + 1e-9 else rem / net
            self.log.append(dict(data=pd.Timestamp(data), motivo=motivo, lote_data=TS[l[0]], ref_data=TS[max(ref_mi, l[0])],
                                 principal=l[1] * f, bruto=bruto * f, iof=iofv * f, ir=irv * f, liquido=net * f,
                                 dias=dias))
            self.iof += iofv * f
            self.ir += irv * f
            rem -= net * f
            l[1] *= (1 - f)
            if l[1] < 1e-9:
                self.lots.remove(l)
        assert rem < 1e-6, ("caixa insuficiente", rem)


def serie_cdi(V, mi0):
    """Valor liquido (se resgatado no dia) de V aplicado no fechamento do pregao mi0, para cada pregao de mi0 ate o fim."""
    return np.array([lote_liq(mi0, V, mi, MD[mi])[0] for mi in range(mi0, NM)])


# ---------------------------------------------------------------- simulacao de uma sub-carteira
def imposto_mes(ganho_mes, pool):
    if ganho_mes >= 0:
        usa = min(pool, ganho_mes)
        base = ganho_mes - usa
        return IR_OP * base, pool - usa
    return 0.0, pool - ganho_mes


def simular(nome, X, ordem):
    cands = CAND[X]
    cx = Caixa()
    pos, ops, sched = {}, [], {}
    ganhos, devidos, due, futuro = {}, [], {}, []
    pool = 0.0
    pend = 0.0
    darf_pagos, diario, sinais_log, rend_log = [], [], [], []

    def vender(mi, t):
        for nm in sorted(p for p, P in pos.items() if P["mi_s"] == mi):
            P = pos.pop(nm)
            op = P["op"]
            vv = P["cotas"] * P["px_s"]
            tv = B3 * vv
            cx.add(mi, vv - tv)
            ganho = (vv - tv) - (op["valor_compra"] + op["taxa_compra"])
            ym = (t.year, t.month)
            ganhos[ym] = ganhos.get(ym, 0.0) + ganho
            op.update(saida=t, preco_saida=P["px_s"], taxa_venda=tv, valor_venda=vv, ganho_trib=ganho, status="Fechada",
                      mi_s=mi)

    for mi in range(J0, NM):
        t = TS[mi]
        if mi == J0:
            cx.add(mi, CAP_SUB)
        # 1. DARF que vence hoje (e eventual pendencia) sai do caixa antes das compras
        for ym, dv in due.get(mi, []):
            pend += dv
        if pend > 1e-9:
            pg = min(pend, cx.saldo(mi - 1, MD[mi]))
            if pg > 1e-9:
                cx.resgatar(pg, mi - 1, MD[mi], "DARF")
                pend -= pg
                darf_pagos.append(dict(data=t, pago=pg))
        # 2. saidas do dia: o dinheiro da venda vira um lote novo
        vender(mi, t)
        # 3. entradas: sinais do pregao anterior, na abertura de hoje; maior volume de 60 dias primeiro
        for c in sorted(cands[mi], key=lambda c: (-c["vol"], c["F"]["nome"])):
            F = c["F"]
            nm = F["nome"]
            base = dict(carteira=nome, gatilho=X, ordem=ordem, fundo=nm, sinal=TS[c["md"]], execucao=t)
            r = int(np.searchsorted(F["dates"], MD[mi]))
            if r >= F["n"] or F["dates"][r] != MD[mi] or F["NEG"][r] != 1 or not np.isfinite(F["A"][r]) or F["A"][r] <= 0:
                sinais_log.append(dict(base, resultado="sem negociação na abertura"))
                continue
            if nm in pos:
                sinais_log.append(dict(base, resultado="fundo já em carteira"))
                continue
            px = float(F["A"][r])
            pc_ = px * (1 + B3)
            vol = c["vol"]
            lim = min(ordem, PCT_VOL * vol) if np.isfinite(vol) else 0.0
            n_full = int(np.floor(lim / pc_ + 1e-9))
            caixa = cx.saldo(mi - 1, MD[mi])
            n_c = int(np.floor(min(lim, caixa) / pc_ + 1e-9))
            if n_c * px < MIN_OP:
                if n_full * px >= MIN_OP:
                    sinais_log.append(dict(base, resultado="sem dinheiro", pretendido=n_full * px, caixa=caixa, preco=px))
                else:
                    sinais_log.append(dict(base, resultado="ordem abaixo de R$ 200 (limite do negociado)"))
                continue
            val = n_c * px
            fee = B3 * val
            cx.resgatar(val + fee, mi - 1, MD[mi], "compra")
            k, mot, pxs = saida_volta(F, r)
            op = dict(carteira=nome, gatilho=X, ordem=ordem, fundo=nm, tipo=TIPO.get(nm, "sem tipo"), sinal=TS[c["md"]],
                      entrada=t, preco_entrada=px, cotas=n_c, valor_compra=val, taxa_compra=fee, motivo=mot,
                      status="Em aberto" if mot == ABERTO else "Em curso", saida=pd.NaT, preco_saida=np.nan,
                      taxa_venda=0.0, valor_venda=np.nan, ganho_trib=np.nan, rend_direito=0.0, rend_recebido=0.0,
                      rend_a_receber=0.0, rend_sem_data=0.0, e=r, k=k, mi_e=mi, mi_d=c["md"], mi_s=None,
                      pretendido=n_full * px, F=F)
            S = F["dates"][k]
            for dbase, v, pgd in direitos(nm, F["dates"][r], S, mot in (PRAZO_M, ABERTO)):
                amt = n_c * v
                op["rend_direito"] += amt
                if np.isnat(pgd):
                    op["rend_sem_data"] += amt
                    continue
                mpay = int(np.searchsorted(MD, pgd, "left"))
                if mpay >= NM:
                    op["rend_a_receber"] += amt
                else:
                    sched.setdefault(mpay, []).append((op, amt, dbase, pgd, v))
            ops.append(op)
            pos[nm] = dict(F=F, op=op, cotas=n_c, k=k, mot=mot, px_s=pxs,
                           mi_s=int(F["mi"][k]) if mot != ABERTO else None)
            sinais_log.append(dict(base, resultado="comprado" if n_c == n_full else "comprado (reduzido pelo caixa)",
                                   pretendido=n_full * px, caixa=caixa, preco=px, valor=val))
        # 3b. posicao comprada hoje cuja saida e neste mesmo pregao (guarda no 1o dia)
        vender(mi, t)
        # 4. rendimentos pagos hoje entram no caixa (data de PAGAMENTO; fim de semana/feriado = proximo pregao)
        for op, amt, dbase, pgd, v in sched.pop(mi, []):
            cx.add(mi, amt)
            op["rend_recebido"] += amt
            rend_log.append(dict(carteira=nome, data=t, fundo=op["fundo"], data_base=pd.Timestamp(dbase),
                                 data_pagamento=pd.Timestamp(pgd), valor_cota=v, cotas=op["cotas"], recebido=amt))
        # 5. imposto do FII no ultimo pregao do mes; DARF vence no ultimo pregao do mes seguinte
        if LASTM[mi]:
            ym = (t.year, t.month)
            dv, pool = imposto_mes(ganhos.get(ym, 0.0), pool)
            nxt = (ym[0] + (ym[1] == 12), ym[1] % 12 + 1)
            vm = ULT_MES.get(nxt) if nxt < (TS[-1].year, TS[-1].month) else None   # mes seguinte ainda nao terminou na base
            devidos.append(dict(mes=ym, ganho=ganhos.get(ym, 0.0), devido=dv, vence=TS[vm] if vm is not None else None))
            if dv > 0:
                if vm is not None:
                    due.setdefault(vm, []).append((ym, dv))
                else:
                    futuro.append((ym, dv))
        # 6. patrimonio no fechamento: caixa liquido de IR/IOF + cotas x ultimo fechamento - DARF vencido nao pago
        caixa_liq = cx.saldo(mi, MD[mi])
        assert caixa_liq >= -1e-6, (nome, t, caixa_liq)
        pv = 0.0
        for P in pos.values():
            F = P["F"]
            rr = int(np.searchsorted(F["dates"], MD[mi], "right") - 1)
            assert np.isfinite(F["C"][rr])
            pv += P["cotas"] * float(F["C"][rr])
        pat = caixa_liq + pv - pend
        diario.append(dict(data=t, caixa=caixa_liq, posicoes=pv, pendente=pend, patrimonio=pat, n_pos=len(pos),
                           aplicado=pv / pat))

    # posicoes abertas no fim: preco do ultimo fechamento conhecido
    for nm, P in pos.items():
        op, F = P["op"], P["F"]
        rr = int(np.searchsorted(F["dates"], MD[NM - 1], "right") - 1)
        assert P["mot"] == ABERTO, (nome, nm, P["mot"])   # so 'em aberto' pode sobrar no fim
        op.update(saida=pd.NaT, preco_saida=float(F["C"][rr]), status="Em aberto", rr=rr)
    # imposto hipotetico se vendesse tudo no ultimo dia (so o ganho do mes final muda)
    gh = 0.0
    for nm, P in pos.items():
        op = P["op"]
        vv = P["cotas"] * op["preco_saida"]
        gh += (vv - B3 * vv) - (op["valor_compra"] + op["taxa_compra"])
    ym_f = (TS[-1].year, TS[-1].month)
    # recalcula todos os meses com o ganho hipotetico somado ao ultimo mes
    pool2, tot_real, tot_hip = 0.0, 0.0, 0.0
    for ym in sorted(ganhos.keys() | {ym_f}):
        g_ = ganhos.get(ym, 0.0)
        d_real, pool_r = imposto_mes(g_, pool2)
        d_hip, pool_h = imposto_mes(g_ + (gh if ym == ym_f else 0.0), pool2)
        if ym == ym_f:
            tot_real, tot_hip = d_real, d_hip
        pool2 = pool_r
    imp_hipotetico = tot_hip - tot_real
    dia = pd.DataFrame(diario)
    a_pagar = float(sum(v for _, v in futuro))        # DARFs que vencem depois de 09/11 (outubro e novembro)
    return dict(nome=nome, X=X, ordem=ordem, dia=dia, ops=pd.DataFrame([{k: v for k, v in o.items() if k != "F"} for o in ops]),
                ops_raw=ops, sinais=pd.DataFrame(sinais_log), rend=pd.DataFrame(rend_log), darf=pd.DataFrame(darf_pagos),
                devidos=pd.DataFrame(devidos), caixa=cx, pos=pos, ganhos=ganhos, imp_hipotetico=imp_hipotetico,
                ganho_hipotetico=gh, darf_a_pagar=a_pagar, pend=pend)


print(f"base: {NM} pregoes ({TS[0].date()} a {TS[-1].date()}); carteira de 02/01/2026 a {TS[-1].date()} "
      f"({NM - J0} pregoes); fundos com precos: {len(FD)}")
for X in GATILHOS:
    print(f"  sinais (data >= 02/01/2026) com gatilho {int(X * 100)}%: {sum(len(x) for x in CAND[X])}")

RES = {}
for nome, X in list(SUBS.items()) + [CONS30]:
    for ordem in ORDENS:
        RES[(nome, ordem)] = simular(nome, X, ordem)
print(f"simulacoes rodadas: {len(RES)}; tempo: {time.time() - T0:.1f} s")


# ================================================================ PARTE 2: numeros, conferencias, planilha
DATAS = TS[J0:]
NDIA = len(DATAS)
CDI10 = serie_cdi(CAP_SUB, J0)
CDI20 = 2 * CDI10
MERC20 = 2 * CAP_SUB * IDX[J0:] / IDX[J0]


def prep_ops(R):
    o = R["ops"].copy()
    fech = o["status"] == "Fechada"
    o["valorizacao"] = np.where(fech, o["valor_venda"] - o["valor_compra"], o["cotas"] * o["preco_saida"] - o["valor_compra"])
    o["taxas"] = o["taxa_compra"] + o["taxa_venda"].fillna(0.0)
    o["resultado"] = o["valorizacao"] + o["rend_direito"] - o["taxas"]
    o["resultado_pct"] = o["resultado"] / o["valor_compra"]
    o["valorizacao_pct"] = o["valorizacao"] / o["valor_compra"]
    fim = pd.Series(TS[-1], index=o.index)
    o["dias"] = ((o["saida"].where(fech, fim)) - o["entrada"]).dt.days
    return o


for R in RES.values():
    R["o"] = prep_ops(R)
    R["pat"] = R["dia"]["patrimonio"].to_numpy()
    R["pos_val"] = R["dia"]["posicoes"].to_numpy()


def queda_max(p, base):
    b = np.r_[base, p]
    pico = np.maximum.accumulate(b)[1:]
    dd = p / pico - 1
    j = int(np.argmin(dd))
    ipk = np.flatnonzero(p[:j + 1] == pico[j])
    d_pico = DATAS[ipk[-1]] if ipk.size else TS[J0]
    return float(dd[j]), d_pico, DATAS[j]


def metricas(rs, nome):
    """rs: lista de resultados (1 = sub-carteira; 2 = total)."""
    cap = CAP_SUB * len(rs)
    pat = sum(R["pat"] for R in rs)
    pos = sum(R["pos_val"] for R in rs)
    o = pd.concat([R["o"] for R in rs], ignore_index=True)
    fech = o[o["status"] == "Fechada"]
    ab = o[o["status"] != "Fechada"]
    pf = float(pat[-1])
    a_pagar = sum(R["darf_a_pagar"] for R in rs)
    hip = sum(R["imp_hipotetico"] for R in rs)
    pliq = pf - a_pagar - hip
    q, dp, df_ = queda_max(pat, cap)
    mel = o.loc[o["resultado_pct"].idxmax()] if len(o) else None
    pio = o.loc[o["resultado_pct"].idxmin()] if len(o) else None
    sin = pd.concat([R["sinais"] for R in rs], ignore_index=True)
    return dict(
        nome=nome, cap=cap, pat=pat, p_ini=cap, p_fim=pf, ret=pf / cap - 1, p_liq=pliq, ret_liq=pliq / cap - 1,
        queda=q, d_pico=dp, d_fundo=df_, n_ab=len(ab), n_fe=len(fech),
        luc_fe=float((fech["resultado"] > 0).mean()) if len(fech) else np.nan,
        luc_todas=float((o["resultado"] > 0).mean()) if len(o) else np.nan,
        pior=float(pio["resultado_pct"]), pior_f=f"{pio['fundo']} ({'em aberto' if pio['status'] != 'Fechada' else 'fechada'})",
        melhor=float(mel["resultado_pct"]), melhor_f=f"{mel['fundo']} ({'em aberto' if mel['status'] != 'Fechada' else 'fechada'})",
        rend=float(sum(R["rend"]["recebido"].sum() for R in rs if len(R["rend"]))),
        rend_a_receber=float(o["rend_a_receber"].sum()), rend_sem_data=float(o["rend_sem_data"].sum()),
        imposto=float(sum(R["darf"]["pago"].sum() for R in rs if len(R["darf"]))),
        imp_devido=float(a_pagar + sum(R["pend"] for R in rs)), imp_hip=float(hip),
        ir_iof=float(sum(R["caixa"].ir + R["caixa"].iof for R in rs)),
        taxas=float(o["taxas"].sum()), sem_din=int((sin["resultado"] == "sem dinheiro").sum()),
        giro=float(o["valor_compra"].sum() / pat.mean()), tempo=float(fech["dias"].mean()) if len(fech) else np.nan,
        tempo_todas=float(o["dias"].mean()) if len(o) else np.nan,
        aplicado=float(pos.sum() / pat.sum()), comprado=float(o["valor_compra"].sum()),
        res_ops=float(o["resultado"].sum()), n=len(o))


def metricas_ref(serie, cap, nome):
    q, dp, df_ = queda_max(serie, cap)
    return dict(nome=nome, cap=cap, pat=serie, p_ini=cap, p_fim=float(serie[-1]), ret=float(serie[-1] / cap - 1),
                p_liq=float(serie[-1]), ret_liq=float(serie[-1] / cap - 1), queda=q, d_pico=dp, d_fundo=df_)


BASE = {n: RES[(n, ORDEM_BASE)] for n in list(SUBS) + [CONS30[0]]}
M = {n: metricas([BASE[n]], n) for n in BASE}
M["Total"] = metricas([BASE["Conservadora"], BASE["Agressiva"]], "Total")
M["CDI"] = metricas_ref(CDI20, 2 * CAP_SUB, "105% do CDI")
M["Mercado"] = metricas_ref(MERC20, 2 * CAP_SUB, "Mercado")
TOTAL_PAT = BASE["Conservadora"]["pat"] + BASE["Agressiva"]["pat"]
APLIC = {n: BASE[n]["pos_val"] / BASE[n]["pat"] for n in BASE}
APLIC["Total"] = (BASE["Conservadora"]["pos_val"] + BASE["Agressiva"]["pos_val"]) / TOTAL_PAT

# mercado aberto no CDI: imposto do CDI no fim
cdi_bruto_fim = 2 * CAP_SUB * (CIDX[NM - 1] / CIDX[J0] - 1)
cdi_ir_fim = cdi_bruto_fim - (CDI20[-1] - 2 * CAP_SUB)

# ---------------------------------------------------------------- conferencias (impressas)
print("\n" + "=" * 100)
print("CONFERENCIAS")
print("=" * 100)
min_cx = min(float(R["dia"]["caixa"].min()) for R in RES.values())
assert min_cx >= -1e-6
print(f"1) caixa liquido nunca negativo: menor caixa em qualquer dia das {len(RES)} simulacoes = {brl(min_cx)} "
      f"(assert dentro do laco, a cada dia: PASSOU)")
viol = 0
for R in RES.values():
    for o in R["ops_raw"]:
        if not (o["entrada"] > o["sinal"] and o["mi_e"] > o["mi_d"]):
            viol += 1
assert viol == 0
print(f"2) nenhuma compra no dia do sinal: {sum(len(R['ops_raw']) for R in RES.values())} compras, todas com entrada "
      f"estritamente depois da data do sinal: PASSOU")
assert all(o["sinal"] >= INICIO_SIM for R in RES.values() for o in R["ops_raw"])
print(f"   e todas as datas de sinal sao >= 02/01/2026: PASSOU")


def conferir_op(R, escolha, rotulo):
    o = R["o"]
    c = o[(o["status"] == "Fechada") & (o["rend_recebido"] > 0) & (o["motivo"] == VOLTA)]
    if c.empty:
        c = o[o["status"] == "Fechada"]
    op = c.iloc[0] if escolha == "primeira" else c.iloc[-1]
    f = op["fundo"]
    g = PR[PR["fundo"] == f].reset_index(drop=True)
    e = int(g.index[g["data"] == op["entrada"]][0])
    k = int(g.index[g["data"] == op["saida"]][0])
    ab = float(g.loc[e, C_AB])
    compra = op["cotas"] * ab
    taxa_c = B3 * compra
    if op["motivo"] == VOLTA:
        media = float(g[C_FE].iloc[k - N:k].mean())
        ps = max(float(g.loc[k, C_AB]), media)
        txt_s = f"max(abertura {g.loc[k, C_AB]:.2f}; media dos 200 fechamentos anteriores {media:.4f}) = {ps:.4f}"
    else:
        ps = float(g.loc[k, C_FE])
        txt_s = f"fechamento {ps:.2f}"
    venda = op["cotas"] * ps
    taxa_v = B3 * venda
    incl = op["motivo"] == PRAZO_M
    msk = (PG["fundo"] == f) & (PG["data_base"] >= op["entrada"]) & ((PG["data_base"] <= op["saida"]) if incl else (PG["data_base"] < op["saida"]))
    av = PG[msk]
    rend = float(av["valor (R$/cota)"].sum()) * op["cotas"]
    res = venda - compra + rend - taxa_c - taxa_v
    print(f"\n  [{rotulo}] {f}: sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])} (depois do sinal), saida {dt(op['saida'])} ({op['motivo']})")
    print(f"    compra: {int(op['cotas'])} cotas x abertura {ab:.2f} = {compra:.2f}; taxa 0,03% = {taxa_c:.4f}")
    for _, a in av.iterrows():
        print(f"    rendimento: data-base {dt(a['data_base'])}, {a['valor (R$/cota)']:.4f}/cota x {int(op['cotas'])} = "
              f"{a['valor (R$/cota)'] * op['cotas']:.4f}; pago em {dt(a['data_pagamento'])}")
    print(f"    venda: {int(op['cotas'])} cotas x {txt_s} = {venda:.2f}; taxa 0,03% = {taxa_v:.4f}")
    print(f"    resultado = {venda:.2f} - {compra:.2f} + {rend:.4f} - {taxa_c:.4f} - {taxa_v:.4f} = {res:.4f}"
          f" ({100 * res / compra:.4f}% da compra)")
    print(f"    programa: compra {op['valor_compra']:.2f}, venda {op['valor_venda']:.2f}, rendimentos {op['rend_direito']:.4f}, "
          f"taxas {op['taxas']:.4f}, resultado {op['resultado']:.4f} ({100 * op['resultado_pct']:.4f}%)")
    assert abs(compra - op["valor_compra"]) < 1e-6 and abs(venda - op["valor_venda"]) < 1e-6
    assert abs(rend - op["rend_direito"]) < 1e-6 and abs(res - op["resultado"]) < 1e-6
    rl = R["rend"]
    rl = rl[(rl["fundo"] == f) & (rl["data_base"] >= op["entrada"])]
    for _, a in av.iterrows():
        if pd.notna(a["data_pagamento"]):
            q = R["rend"][(R["rend"]["fundo"] == f) & (R["rend"]["data_base"] == a["data_base"])]
            assert len(q) >= 1, "pagamento nao entrou no caixa"
            dpay = q.iloc[0]["data"]
            esperado = TS[int(np.searchsorted(MD, np.datetime64(a["data_pagamento"], "D"), "left"))]
            assert dpay == esperado
            print(f"    rendimento caiu no caixa em {dt(dpay)} (pagamento {dt(a['data_pagamento'])}; "
                  f"se nao era pregao, vai ao pregao seguinte): PASSOU")
    print("    ASSERT PASSOU (compra, rendimento, venda, taxas e resultado batem com o programa)")
    return (f"{rotulo}, {f} (sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])}, saída {dt(op['saida'])}): compra {int(op['cotas'])} cotas × "
            f"R$ {br(ab)} = {brl(compra)}; rendimentos {brl(rend)}; venda {brl(venda)}; taxas {brl(taxa_c + taxa_v, 2)}; "
            f"resultado {brl(res)} ({pct(res / compra)}). O programa deu o mesmo valor.")


print("\n3) Operacoes refeitas a mao a partir dos arquivos de entrada (precos_*.csv e rendimentos_pagamentos.csv):")
CONF_TXT = [conferir_op(BASE["Conservadora"], "primeira", "Conservadora"),
            conferir_op(BASE["Agressiva"], "primeira", "Agressiva")]

print("\n4) Resgate do caixa com IR (refeito a mao com cdi.csv):")


def conferir_resgate(R, cond, rotulo):
    lg = [x for x in R["caixa"].log if cond(x)]
    x = lg[0]
    i0 = float(CDI.loc[CDI["data"] == x["lote_data"], "indice_105_do_cdi"].iloc[0])
    i1 = float(CDI.loc[CDI["data"] == x["ref_data"], "indice_105_do_cdi"].iloc[0])
    dias = (x["data"] - x["lote_data"]).days
    # x guarda a parte do lote efetivamente resgatada
    p = x["principal"]
    bruto = p * (i1 / i0 - 1)
    iof = IOF[dias - 1] / 100 if 1 <= dias <= 29 else 0.0
    ir_aliq = aliq_rf(dias)
    liq = p + bruto * (1 - iof) * (1 - ir_aliq)
    print(f"  [{rotulo}] {x['motivo']} em {dt(x['data'])}: lote aplicado em {dt(x['lote_data'])} ({dias} dias corridos), "
          f"principal resgatado {p:.4f}")
    print(f"    indice 105% CDI: {i0:.6f} (aplicacao) -> {i1:.6f} ({dt(x['ref_data'])}); bruto = {p:.4f} x ({i1:.6f}/{i0:.6f} - 1) = {bruto:.4f}")
    print(f"    IOF {100 * iof:.0f}% = {bruto * iof:.4f}; IR {100 * ir_aliq:.1f}% sobre {bruto * (1 - iof):.4f} = "
          f"{bruto * (1 - iof) * ir_aliq:.4f}; liquido = {p:.4f} + {bruto:.4f} - {bruto * iof:.4f} - {bruto * (1 - iof) * ir_aliq:.4f} = {liq:.4f}")
    print(f"    programa: bruto {x['bruto']:.4f}, IOF {x['iof']:.4f}, IR {x['ir']:.4f}, liquido {x['liquido']:.4f}")
    assert abs(liq - x["liquido"]) < 1e-6 and abs(bruto - x["bruto"]) < 1e-6
    print("    ASSERT PASSOU")
    return (f"{rotulo}: {x['motivo']} em {dt(x['data'])}; lote de {dt(x['lote_data'])} ({dias} dias corridos); parte resgatada {brl(p)}; "
            f"rendimento bruto {brl(bruto)}; IOF {brl(bruto * iof)}; IR de {br(100 * ir_aliq, 1)}% = {brl(bruto * (1 - iof) * ir_aliq)}; "
            f"líquido {brl(liq)}. O programa deu o mesmo valor.")


CONF_TXT.append(conferir_resgate(BASE["Agressiva"], lambda x: x["dias"] >= 30 and x["bruto"] > 1, "Resgate do caixa (Agressiva), só IR"))
iof_lg = [R for R in BASE.values() if any(1 <= x["dias"] <= 29 and x["bruto"] > 0.01 for x in R["caixa"].log)]
if iof_lg:
    CONF_TXT.append(conferir_resgate(iof_lg[0], lambda x: 1 <= x["dias"] <= 29 and x["bruto"] > 0.01, f"Resgate do caixa ({iof_lg[0]['nome']}), IOF + IR"))

# CDI de R$ 20 mil como resgatado em 09/11/2026 (conta direta)
v_cdi = 2 * CAP_SUB * (CIDX[NM - 1] / CIDX[J0] - 1)
dias_cdi = (TS[-1] - TS[J0]).days
liq_cdi = 2 * CAP_SUB + v_cdi * (1 - aliq_rf(dias_cdi))
print(f"\n5) R$ 20.000 em 105% do CDI de {dt(TS[J0])} a {dt(TS[-1])} ({dias_cdi} dias corridos, IR {100 * aliq_rf(dias_cdi):.1f}%): "
      f"bruto {v_cdi:.2f}; liquido {liq_cdi:.2f}; serie do programa {CDI20[-1]:.2f}")
assert abs(liq_cdi - CDI20[-1]) < 1e-6

# imposto do FII refeito por fora
print("\n6) Imposto do FII (20% sobre o ganho liquido do mes; prejuizo abate):")
for nm_, R in BASE.items():
    o = R["o"]
    f_ = o[o["status"] == "Fechada"].copy()
    f_["mes"] = f_["saida"].dt.to_period("M")
    pool, tot, lin = 0.0, 0.0, []
    for mes, gg in f_.groupby("mes", sort=True):
        gm = float(gg["ganho_trib"].sum())
        liq = gm - pool if gm >= 0 else 0.0
        if gm >= 0:
            base_ = max(gm - pool, 0.0)
            pool = max(pool - gm, 0.0)
        else:
            base_ = 0.0
            pool += -gm
        tot += IR_OP * base_
        lin.append(f"{mes}: ganho {gm:.2f} -> imposto {IR_OP * base_:.2f}")
    devidos = float(R["devidos"]["devido"].sum())
    pago = float(R["darf"]["pago"].sum()) if len(R["darf"]) else 0.0
    print(f"  {nm_}: " + "; ".join(lin) if lin else f"  {nm_}: sem vendas")
    print(f"    soma devida (por fora) {tot:.2f} = soma devida pelo programa {devidos:.2f}; paga ate 09/11 {pago:.2f}; "
          f"vencida e pendente {R['pend']:.2f}; a vencer depois de 09/11 {R['darf_a_pagar']:.2f}")
    assert abs(tot - devidos) < 1e-6
    assert abs(devidos - (pago + R["pend"] + R["darf_a_pagar"])) < 1e-6
print("   ASSERT PASSOU (devido = pago + pendente + a vencer)")

# ---------------------------------------------------------------- tabelas impressas
print("\n" + "=" * 100)
print("RESUMO (ordem R$ 1.000)")
print("=" * 100)
linhas = [
    ("Patrimonio inicial (R$)", lambda m: brl(m["p_ini"])),
    ("Patrimonio final, preco de 09/11 (R$)", lambda m: brl(m["p_fim"])),
    ("Retorno no periodo", lambda m: pct(m["ret"])),
    ("Patrimonio final liquido do imposto (R$)", lambda m: brl(m["p_liq"])),
    ("Retorno liquido", lambda m: pct(m["ret_liq"])),
    ("Retorno liquido contra o CDI (pontos)", lambda m: br(100 * (m["ret_liq"] - M["CDI"]["ret_liq"]), 1)),
    ("Maior queda no caminho", lambda m: pct(m["queda"]) + f" ({dt(m['d_pico'])} a {dt(m['d_fundo'])})"),
]
cols = ["Conservadora", "Agressiva", "Total", "CDI", "Mercado"]
print(" | ".join(["indicador"] + cols))
for nome_l, fn in linhas:
    print(" | ".join([nome_l] + [fn(M[c]) for c in cols]))
for c in ["Conservadora", "Agressiva", "Total"]:
    m = M[c]
    print(f"\n{c}: operacoes {m['n']} (abertas {m['n_ab']}, fechadas {m['n_fe']}); com lucro entre fechadas {pct(m['luc_fe'])}; "
          f"pior {pct(m['pior'])} {m['pior_f']}; melhor {pct(m['melhor'])} {m['melhor_f']}")
    print(f"  rendimentos recebidos {brl(m['rend'])}; a receber {brl(m['rend_a_receber'])}; imposto FII pago {brl(m['imposto'])}; "
          f"imposto devido ainda nao pago {brl(m['imp_devido'])}; imposto se vendesse tudo {brl(m['imp_hip'])}; "
          f"IR+IOF do caixa {brl(m['ir_iof'])}; taxas {brl(m['taxas'])}; sinais sem dinheiro {m['sem_din']}; "
          f"giro {br(m['giro'], 2)}; tempo medio {br(m['tempo'], 1)} dias; aplicado em fundos (media) {pct(m['aplicado'])}")
print(f"\n105% do CDI: R$ 20.000 -> {brl(CDI20[-1])} (bruto {brl(2 * CAP_SUB + cdi_bruto_fim)}; IR {brl(cdi_ir_fim)}). "
      f"Mercado: {brl(MERC20[-1])}.")

print("\nVARIANTES (retorno liquido do imposto; patrimonio inicial R$ 10.000 por sub-carteira)")
VAR = []
for nome, X in list(SUBS.items()) + [CONS30]:
    for ordem in ORDENS:
        m = metricas([RES[(nome, ordem)]], nome)
        VAR.append(dict(m, X=X, ordem=ordem))
        print(f"  {nome:18s} ordem {brl(ordem, 0):>10s}: final {brl(m['p_fim'])}; liquido {brl(m['p_liq'])}; retorno liq {pct(m['ret_liq'])}; "
              f"queda {pct(m['queda'])}; operacoes {m['n']}; giro {br(m['giro'], 2)}; sem dinheiro {m['sem_din']}")
print(f"  105% do CDI (R$ 10.000): {brl(CDI10[-1])} ({pct(CDI10[-1] / CAP_SUB - 1)})")

# lacunas mensuraveis
f_saiu = sum(int((R["o"]["motivo"] == SAIU).sum()) for R in BASE.values())
f_guarda = sum(int((R["o"]["motivo"] == GUARDA).sum()) for R in BASE.values())
n_sem_data_all = int(PG[(PG["data_base"] >= INICIO_SIM)]["data_pagamento"].isna().sum())
amz26 = AMZ[(AMZ["data_base"] >= INICIO_SIM) & (AMZ["fundo"].isin({o["fundo"] for R in BASE.values() for o in R["ops_raw"]}))]
print(f"\nLacunas: ordens fechadas por 'fundo saiu da bolsa' (preco acabou antes do fim): {f_saiu}; por dado suspeito: {f_guarda}; "
      f"avisos de 2026 sem data de pagamento (todos os fundos): {n_sem_data_all}; amortizacoes de 2026 em fundos comprados: {len(amz26)}")
dup26 = int(PG[PG["data_base"] >= INICIO_SIM].duplicated(["fundo", "data_base", "valor (R$/cota)"]).sum())
print(f"avisos de rendimento duplicados com data-base em 2026: {dup26}")

# ---------------------------------------------------------------- lacunas medidas
LAC = {}
ops_all = pd.concat([R["o"] for R in (BASE["Conservadora"], BASE["Agressiva"])], ignore_index=True)
saiu = ops_all[ops_all["motivo"] == SAIU]
LAC["saiu_n"] = len(saiu)
LAC["saiu_valor"] = float(saiu["valor_compra"].sum())
LAC["saiu_res"] = float(saiu["resultado"].sum())
amz_rows = []
for r_ in ops_all.itertuples():
    fim_ = r_.saida if r_.status == "Fechada" else TS[-1]
    a = AMZ[(AMZ["fundo"] == r_.fundo) & (AMZ["data_base"] >= r_.entrada) & (AMZ["data_base"] <= fim_)]
    for x in a.itertuples():
        amz_rows.append(dict(carteira=r_.carteira, fundo=r_.fundo, data_base=x.data_base, valor=x[5] * r_.cotas))
AMZ_DF = pd.DataFrame(amz_rows)
LAC["amz_n"] = len(AMZ_DF)
LAC["amz_valor"] = float(AMZ_DF["valor"].sum()) if len(AMZ_DF) else 0.0
stale = 0
for R in (BASE["Conservadora"], BASE["Agressiva"]):
    for nm_, P in R["pos"].items():
        F = P["F"]
        rr = int(np.searchsorted(F["dates"], MD[NM - 1], "right") - 1)
        stale += int(F["NEG"][rr] != 1)
LAC["abertas_sem_negocio_hoje"] = stale
LAC["rend_sem_data_2026"] = n_sem_data_all
LAC["rend_a_receber"] = M["Total"]["rend_a_receber"]
LAC["rend_sem_data_valor"] = M["Total"]["rend_sem_data"]
LAC["pend"] = {n: BASE[n]["pend"] for n in ("Conservadora", "Agressiva")}
print(f"lacunas medidas: {LAC['saiu_n']} ordens fechadas por 'fundo saiu da bolsa' (comprado R$ {br(LAC['saiu_valor'])}, resultado "
      f"R$ {br(LAC['saiu_res'])}); amortizacoes durante posicoes (conservadora+agressiva): {LAC['amz_n']} eventos, "
      f"R$ {br(LAC['amz_valor'])} nao creditados; posicoes abertas sem negociacao no ultimo dia: {LAC['abertas_sem_negocio_hoje']}")
if len(AMZ_DF):
    print(AMZ_DF.assign(data_base=AMZ_DF["data_base"].map(dt)).to_string(index=False))

# ================================================================ PLANILHA EXCEL
from openpyxl import Workbook
from openpyxl.chart import AreaChart, BarChart, LineChart, Reference
from openpyxl.chart.axis import DateAxis
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

COR = dict(cons="0072B2", agr="D55E00", tot="222222", cdi="009E73", merc="9A9A9A")
F_BRL = '"R$" #,##0.00'
F_BRL0 = '"R$" #,##0'
F_PCT = '0.0%'
F_DATA = 'dd/mm/yyyy'
HDR_FILL = PatternFill("solid", fgColor="E8EEF4")
HDR_FONT = Font(bold=True, color="1B2733")
THIN = Side(style="thin", color="C9D1D9")
BORDA = Border(bottom=THIN)

wb = Workbook()


def cab(ws, row, titulos, larg=None):
    for j, t in enumerate(titulos, 1):
        c = ws.cell(row=row, column=j, value=t)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BORDA
    if larg:
        for j, w in enumerate(larg, 1):
            ws.column_dimensions[get_column_letter(j)].width = w


def eixos(ch, xt, yt, yfmt, xfmt=None):
    ch.x_axis.title = xt
    ch.y_axis.title = yt
    ch.y_axis.number_format = yfmt
    ch.y_axis.majorGridlines = ch.y_axis.majorGridlines
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.tickLblPos = "low"
    ch.legend.position = "b"
    if xfmt:
        ch.x_axis.number_format = xfmt


def estilo_linha(s, cor, larg=22000, tracejada=False):
    s.smooth = False
    s.marker.symbol = "none"
    s.graphicalProperties.line.solidFill = cor
    s.graphicalProperties.line.width = larg
    if tracejada:
        s.graphicalProperties.line.dashStyle = "dash"


def arred_min(v, passo):
    return float(np.floor(v / passo) * passo)


# ------------------------------------------------ Resumo
ws = wb.active
ws.title = "Resumo"
ws["A1"] = "Carteira Kairi de R$ 20.000 em 2026: resumo"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = (f"De {dt(TS[J0])} (1º pregão do ano) a {dt(TS[-1])} (último preço da base). Duas sub-carteiras de R$ 10.000, "
            f"ordem de R$ 1.000. Conservadora = cota 20% abaixo da média de 200 pregões; Agressiva = 15% abaixo. "
            f"Um ano só não prova nada: leia a aba 'Legenda e avisos'.")
ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A2:F2")
ws.row_dimensions[2].height = 48
cab(ws, 4, ["Indicador", "Conservadora (20%)", "Agressiva (15%)", "Total (R$ 20 mil)", "105% do CDI (R$ 20 mil)",
            "Mercado (R$ 20 mil)"], [84, 22, 22, 22, 24, 22])
ws.row_dimensions[4].height = 32
cols_m = ["Conservadora", "Agressiva", "Total", "CDI", "Mercado"]
ND = "—"
LIN = [
    ("Patrimônio inicial (R$)", lambda m: m["p_ini"], F_BRL),
    ("Patrimônio final, ações a preço de 09/11 (R$)", lambda m: m["p_fim"], F_BRL),
    ("Retorno no período", lambda m: m["ret"], F_PCT),
    ("Patrimônio final líquido (descontando o imposto que seria devido se vendesse tudo) (R$)", lambda m: m["p_liq"], F_BRL),
    ("Retorno líquido no período", lambda m: m["ret_liq"], F_PCT),
    ("Retorno líquido contra o CDI (pontos percentuais)", lambda m: 100 * (m["ret_liq"] - M["CDI"]["ret_liq"]), '0.0'),
    ("Maior queda do patrimônio no caminho (%)", lambda m: m["queda"], F_PCT),
    ("  ... do pico em", lambda m: m["d_pico"] if m["queda"] < 0 else ND, F_DATA),
    ("  ... até o ponto mais baixo em", lambda m: m["d_fundo"] if m["queda"] < 0 else ND, F_DATA),
    ("Operações abertas (preço de 09/11)", lambda m: m.get("n_ab", ND), '0'),
    ("Operações fechadas", lambda m: m.get("n_fe", ND), '0'),
    ("Operações fechadas com lucro (%)", lambda m: m.get("luc_fe", ND), F_PCT),
    ("Todas as operações com lucro (%), abertas a preço de 09/11", lambda m: m.get("luc_todas", ND), F_PCT),
    ("Pior operação (%)", lambda m: m.get("pior", ND), F_PCT),
    ("  ... fundo", lambda m: m.get("pior_f", ND), "@"),
    ("Melhor operação (%)", lambda m: m.get("melhor", ND), F_PCT),
    ("  ... fundo", lambda m: m.get("melhor_f", ND), "@"),
    ("Rendimentos recebidos no caixa (R$)", lambda m: m.get("rend", ND), F_BRL),
    ("Rendimentos já declarados, ainda a receber (R$)", lambda m: m.get("rend_a_receber", ND), F_BRL),
    ("Imposto do FII pago (R$)", lambda m: m.get("imposto", ND), F_BRL),
    ("Imposto do FII devido e ainda não pago (R$)", lambda m: m.get("imp_devido", ND), F_BRL),
    ("Imposto que seria devido se vendesse as posições abertas em 09/11 (R$)", lambda m: m.get("imp_hip", ND), F_BRL),
    ("IR e IOF retidos do caixa em 105% do CDI (R$)", lambda m: m["ir_iof"] if "ir_iof" in m else (cdi_ir_fim if m["nome"] == "105% do CDI" else ND), F_BRL),
    ("Taxas de compra e venda (R$)", lambda m: m.get("taxas", ND), F_BRL),
    ("Sinais que ficaram sem dinheiro", lambda m: m.get("sem_din", ND), '0'),
    ("Total comprado em fundos (R$)", lambda m: m.get("comprado", ND), F_BRL),
    ("Giro (total comprado ÷ patrimônio médio)", lambda m: m.get("giro", ND), '0.00'),
    ("Tempo médio por operação fechada (dias corridos)", lambda m: m.get("tempo", ND), '0.0'),
    ("Parte do dinheiro aplicada em fundos, em média (%)", lambda m: m.get("aplicado", ND), F_PCT),
]
for i, (nome_l, fn, fmt) in enumerate(LIN, 5):
    ws.cell(row=i, column=1, value=nome_l)
    for j, k in enumerate(cols_m, 2):
        v = fn(M[k])
        if isinstance(v, (float, np.floating)) and np.isnan(v):
            v = ND
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
        c = ws.cell(row=i, column=j, value=v)
        c.number_format = fmt
        c.alignment = Alignment(horizontal="right")
    ws.cell(row=i, column=1).border = BORDA
r_fim = 5 + len(LIN) + 1
ws.cell(row=r_fim, column=1, value=("Observação: 'Patrimônio final' soma o caixa (líquido de IR e IOF do 105% do CDI) com as cotas a preço de "
                                    "09/11/2026. O 'líquido' ainda desconta o imposto do FII que seria devido ao vender tudo. "
                                    "Em 105% do CDI o imposto já está descontado, como se fosse resgatado em 09/11.")).alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells(start_row=r_fim, start_column=1, end_row=r_fim, end_column=6)
ws.row_dimensions[r_fim].height = 48
ws.freeze_panes = "B5"

# ------------------------------------------------ Patrimonio dia a dia
wp = wb.create_sheet("Patrimônio dia a dia")
cab(wp, 1, ["Data", "Conservadora (R$)", "Agressiva (R$)", "Total (R$)", "105% do CDI, R$ 20 mil (R$)",
            "Mercado, R$ 20 mil (R$)", "105% do CDI, R$ 10 mil (R$)"], [13, 18, 18, 18, 24, 22, 24])
wp.row_dimensions[1].height = 45
for i in range(NDIA):
    r = i + 2
    wp.cell(row=r, column=1, value=DATAS[i].to_pydatetime()).number_format = F_DATA
    for j, v in enumerate([BASE["Conservadora"]["pat"][i], BASE["Agressiva"]["pat"][i], TOTAL_PAT[i], CDI20[i], MERC20[i], CDI10[i]], 2):
        wp.cell(row=r, column=j, value=float(v)).number_format = F_BRL
wp.freeze_panes = "B2"
nr = NDIA + 1


def grafico_linhas(ws_, titulo, colunas, cores, ymin, ymax, anchor, dash=()):
    ch = LineChart()
    ch.title = titulo
    ch.height, ch.width = 9.5, 24
    for col in colunas:
        ch.add_data(Reference(ws_, min_col=col, min_row=1, max_row=nr), titles_from_data=True)
    ch.x_axis = DateAxis(crossAx=100)
    ch.y_axis.crossAx = 500
    ch.x_axis.majorTimeUnit = "months"
    ch.x_axis.majorUnit = 1
    eixos(ch, "Data", "Patrimônio (R$)", '"R$" #,##0', "mmm/yy")
    ch.set_categories(Reference(ws_, min_col=1, min_row=2, max_row=nr))
    for s, cor, d in zip(ch.series, cores, [i in dash for i in range(len(colunas))]):
        estilo_linha(s, cor, tracejada=d)
    ch.y_axis.scaling.min = ymin
    ch.y_axis.scaling.max = ymax
    ws_.add_chart(ch, anchor)


ymin1 = arred_min(min(TOTAL_PAT.min(), CDI20.min(), MERC20.min()) * 0.99, 500)
ymax1 = float(np.ceil(max(TOTAL_PAT.max(), CDI20.max(), MERC20.max()) * 1.01 / 500) * 500)
grafico_linhas(wp, "Total de R$ 20 mil: carteira, 105% do CDI e mercado", [4, 5, 6], [COR["tot"], COR["cdi"], COR["merc"]],
               ymin1, ymax1, "I2")
allsub = np.r_[BASE["Conservadora"]["pat"], BASE["Agressiva"]["pat"], CDI10]
ymin2 = arred_min(allsub.min() * 0.99, 250)
ymax2 = float(np.ceil(allsub.max() * 1.01 / 250) * 250)
grafico_linhas(wp, "Cada sub-carteira (R$ 10 mil) contra 105% do CDI", [2, 3, 7], [COR["cons"], COR["agr"], COR["cdi"]],
               ymin2, ymax2, "I23")

# ------------------------------------------------ Quanto estava aplicado
wa = wb.create_sheet("Quanto estava aplicado")
cab(wa, 1, ["Data", "Conservadora (% em fundos)", "Agressiva (% em fundos)", "Total (% em fundos)"], [13, 24, 24, 22])
wa.row_dimensions[1].height = 32
for i in range(NDIA):
    wa.cell(row=i + 2, column=1, value=DATAS[i].to_pydatetime()).number_format = F_DATA
    for j, k in enumerate(["Conservadora", "Agressiva", "Total"], 2):
        wa.cell(row=i + 2, column=j, value=float(APLIC[k][i])).number_format = F_PCT
wa.freeze_panes = "B2"
ch = LineChart()
ch.title = "Quanto do dinheiro estava em fundos (o resto ficava no 105% do CDI)"
ch.height, ch.width = 9.5, 24
for col in (2, 3, 4):
    ch.add_data(Reference(wa, min_col=col, min_row=1, max_row=nr), titles_from_data=True)
ch.x_axis = DateAxis(crossAx=100)
ch.y_axis.crossAx = 500
ch.x_axis.majorTimeUnit = "months"
ch.x_axis.majorUnit = 1
eixos(ch, "Data", "Parte do patrimônio em fundos (%)", '0%', "mmm/yy")
ch.set_categories(Reference(wa, min_col=1, min_row=2, max_row=nr))
for s, cor in zip(ch.series, [COR["cons"], COR["agr"], COR["tot"]]):
    estilo_linha(s, cor)
ch.y_axis.scaling.min = 0
ch.y_axis.scaling.max = 1
wa.add_chart(ch, "F2")

# ------------------------------------------------ Mes a mes
wm = wb.create_sheet("Mês a mês")
cab(wm, 1, ["Mês", "Conservadora", "Agressiva", "Total", "105% do CDI", "Mercado"], [16, 16, 16, 16, 16, 16])
meses = sorted({(d.year, d.month) for d in DATAS})
NOMES_MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
idx_fim = {}
for i, d in enumerate(DATAS):
    idx_fim[(d.year, d.month)] = i
MM = {}
series_m = {"Conservadora": BASE["Conservadora"]["pat"], "Agressiva": BASE["Agressiva"]["pat"], "Total": TOTAL_PAT,
            "CDI": CDI20, "Mercado": MERC20}
base_ini = {"Conservadora": CAP_SUB, "Agressiva": CAP_SUB, "Total": 2 * CAP_SUB, "CDI": 2 * CAP_SUB, "Mercado": 2 * CAP_SUB}
for i, ym in enumerate(meses, 2):
    rot = f"{NOMES_MES[ym[1] - 1]}/{str(ym[0])[2:]}" + (" (até 09/11)" if ym == (TS[-1].year, TS[-1].month) else "")
    wm.cell(row=i, column=1, value=rot)
    for j, k in enumerate(["Conservadora", "Agressiva", "Total", "CDI", "Mercado"], 2):
        ant = base_ini[k] if i == 2 else series_m[k][idx_fim[meses[i - 3]]]
        v = float(series_m[k][idx_fim[ym]] / ant - 1)
        MM[(ym, k)] = v
        wm.cell(row=i, column=j, value=v).number_format = '0.0%'
wm.cell(row=len(meses) + 3, column=1, value="Janeiro conta a partir do fechamento de 02/01/2026 (dia em que o caixa começa).")
nm_ = len(meses) + 1
ch = BarChart()
ch.type = "col"
ch.grouping = "clustered"
ch.title = "Retorno de cada mês"
ch.height, ch.width = 9.5, 24
for col in range(2, 7):
    ch.add_data(Reference(wm, min_col=col, min_row=1, max_row=nm_), titles_from_data=True)
ch.set_categories(Reference(wm, min_col=1, min_row=2, max_row=nm_))
eixos(ch, "Mês de 2026", "Retorno no mês (%)", '0%')
for s, cor in zip(ch.series, [COR["cons"], COR["agr"], COR["tot"], COR["cdi"], COR["merc"]]):
    s.graphicalProperties.solidFill = cor
    s.graphicalProperties.line.solidFill = cor
    s.invertIfNegative = False
ch.gapWidth = 60
wm.add_chart(ch, "H2")

# ------------------------------------------------ Operacoes
wo = wb.create_sheet("Operações")
ORD = ["Conservadora", "Agressiva"]
OPS = pd.concat([BASE[n]["o"] for n in ORD], ignore_index=True)
OPS["ordc"] = OPS["carteira"].map({n: i for i, n in enumerate(ORD)})
OPS = OPS.sort_values(["ordc", "entrada", "fundo"]).reset_index(drop=True)
TIT = ["Sub-carteira", "Fundo", "Tipo do fundo", "Data do sinal", "Data de entrada", "Preço de entrada (R$)", "Cotas",
       "Valor da compra (R$)", "Data de saída (vazio = em aberto)", "Preço de saída ou de 09/11 (R$)", "Situação",
       "Motivo da saída", "Dias corridos", "Valorização (R$)", "Valorização (%)", "Rendimentos (R$)",
       "Rendimentos já recebidos (R$)", "Taxas (R$)", "Resultado (R$)", "Resultado (%)", "Rótulo do gráfico",
       "Resultado Conservadora (R$)", "Resultado Agressiva (R$)"]
cab(wo, 1, TIT, [14, 10, 20, 12, 12, 12, 8, 14, 14, 14, 11, 28, 9, 14, 12, 13, 14, 10, 13, 11, 18, 14, 14])
wo.row_dimensions[1].height = 62
for i, r in OPS.iterrows():
    rr = i + 2
    mot = "em aberto (preço de 09/11)" if r["status"] != "Fechada" else r["motivo"]
    vals = [r["carteira"], r["fundo"], r["tipo"], r["sinal"].to_pydatetime(), r["entrada"].to_pydatetime(), float(r["preco_entrada"]),
            int(r["cotas"]), float(r["valor_compra"]), None if r["status"] != "Fechada" else r["saida"].to_pydatetime(),
            float(r["preco_saida"]), "Fechada" if r["status"] == "Fechada" else "Em aberto", mot, int(r["dias"]),
            float(r["valorizacao"]), float(r["valorizacao_pct"]), float(r["rend_direito"]), float(r["rend_recebido"]),
            float(r["taxas"]), float(r["resultado"]), float(r["resultado_pct"]),
            f"{r['fundo']} {r['entrada']:%d/%m}", float(r["resultado"]) if r["carteira"] == "Conservadora" else None,
            float(r["resultado"]) if r["carteira"] == "Agressiva" else None]
    fm = [None, None, None, F_DATA, F_DATA, '#,##0.00', '0', F_BRL, F_DATA, '#,##0.00', None, None, '0', F_BRL, F_PCT, F_BRL,
          F_BRL, F_BRL, F_BRL, F_PCT, None, F_BRL, F_BRL]
    for j, (v, f) in enumerate(zip(vals, fm), 1):
        c = wo.cell(row=rr, column=j, value=v)
        if f:
            c.number_format = f
wo.freeze_panes = "C2"
wo.auto_filter.ref = f"A1:W{len(OPS) + 1}"
nop = len(OPS) + 1
ch = BarChart()
ch.type = "col"
ch.grouping = "clustered"
ch.overlap = 100
ch.title = "Resultado de cada operação (R$): fechadas e abertas a preço de 09/11"
ch.height, ch.width = 11, 30
for col in (22, 23):
    ch.add_data(Reference(wo, min_col=col, min_row=1, max_row=nop), titles_from_data=True)
ch.set_categories(Reference(wo, min_col=21, min_row=2, max_row=nop))
eixos(ch, "Fundo e data de entrada", "Resultado da operação (R$)", '"R$" #,##0')
for s, cor in zip(ch.series, [COR["cons"], COR["agr"]]):
    s.graphicalProperties.solidFill = cor
    s.graphicalProperties.line.solidFill = cor
    s.invertIfNegative = False
ch.gapWidth = 40
wo.add_chart(ch, f"A{nop + 3}")

# ------------------------------------------------ Variantes
wv = wb.create_sheet("Variantes")
TV = ["Sub-carteira", "Gatilho", "Ordem (R$)", "Patrimônio final, preço de 09/11 (R$)", "Patrimônio final líquido do imposto (R$)",
      "Retorno líquido", "Maior queda (%)", "Operações", "Giro", "Sinais sem dinheiro", "Rótulo do gráfico"]
cab(wv, 1, TV, [20, 9, 11, 20, 22, 12, 12, 11, 9, 13, 24])
wv.row_dimensions[1].height = 48
for i, v in enumerate(VAR, 2):
    vals = [v["nome"], v["X"], v["ordem"], v["p_fim"], v["p_liq"], v["ret_liq"], v["queda"], v["n"], v["giro"], v["sem_din"],
            f"{v['nome'].replace('Conservadora', 'Cons.').replace('Agressiva', 'Agr.')} R$ {int(v['ordem'])}"]
    fm = [None, '0%', F_BRL0, F_BRL, F_BRL, F_PCT, F_PCT, '0', '0.00', '0', None]
    for j, (x, f) in enumerate(zip(vals, fm), 1):
        c = wv.cell(row=i, column=j, value=x)
        if f:
            c.number_format = f
rv = len(VAR) + 2
wv.cell(row=rv, column=1, value="105% do CDI (R$ 10 mil)")
wv.cell(row=rv, column=4, value=float(CDI10[-1])).number_format = F_BRL
wv.cell(row=rv, column=5, value=float(CDI10[-1])).number_format = F_BRL
wv.cell(row=rv, column=6, value=float(CDI10[-1] / CAP_SUB - 1)).number_format = F_PCT
wv.cell(row=rv, column=11, value="105% do CDI")
wv.cell(row=rv, column=7, value=0.0).number_format = F_PCT
wv.cell(row=rv + 2, column=1, value=("Cada linha parte de R$ 10.000. 'Giro' = total comprado ÷ patrimônio médio. As ordens de R$ 500 e R$ 2.000 são "
                                    "testes de sensibilidade; a carteira principal usa R$ 1.000."))
ch = BarChart()
ch.type = "col"
ch.title = "Retorno líquido por variante (R$ 10 mil em cada)"
ch.height, ch.width = 9.5, 24
ch.add_data(Reference(wv, min_col=6, min_row=1, max_row=rv), titles_from_data=True)
ch.set_categories(Reference(wv, min_col=11, min_row=2, max_row=rv))
eixos(ch, "Variante", "Retorno líquido no período (%)", '0%')
ch.legend = None
ch.series[0].graphicalProperties.solidFill = COR["tot"]
ch.series[0].invertIfNegative = False
ch.gapWidth = 50
wv.add_chart(ch, f"A{rv + 5}")

# ------------------------------------------------ Sinais
wsg = wb.create_sheet("Sinais sem dinheiro")
SIN = pd.concat([BASE[n]["sinais"] for n in list(BASE)], ignore_index=True)
funil = SIN.groupby(["carteira", "resultado"]).size().unstack(fill_value=0)
wsg["A1"] = "O que aconteceu com cada sinal (ordem de R$ 1.000)"
wsg["A1"].font = Font(bold=True, size=12)
ncol = ["Sub-carteira"] + list(funil.columns) + ["Total de sinais"]
cab(wsg, 2, ncol, [20] + [22] * (len(ncol) - 1))
wsg.row_dimensions[2].height = 45
for i, (cart, row) in enumerate(funil.iterrows(), 3):
    wsg.cell(row=i, column=1, value=cart)
    for j, v in enumerate(row, 2):
        wsg.cell(row=i, column=j, value=int(v))
    wsg.cell(row=i, column=len(ncol), value=int(row.sum()))
r0 = len(funil) + 5
wsg.cell(row=r0 - 1, column=1, value="Sinais que ficaram sem dinheiro (a ordem era possível pelo negociado, mas o caixa não bastava)").font = Font(bold=True, size=12)
cab(wsg, r0, ["Sub-carteira", "Fundo", "Data do sinal", "Data de execução", "Preço de abertura (R$)", "Valor pretendido (R$)", "Caixa disponível (R$)"])
sd = SIN[SIN["resultado"] == "sem dinheiro"].sort_values(["carteira", "execucao", "fundo"])
for i, r in enumerate(sd.itertuples(), r0 + 1):
    for j, (v, f) in enumerate(zip([r.carteira, r.fundo, r.sinal.to_pydatetime(), r.execucao.to_pydatetime(), float(r.preco), float(r.pretendido), float(r.caixa)],
                                  [None, None, F_DATA, F_DATA, '#,##0.00', F_BRL, F_BRL]), 1):
        c = wsg.cell(row=i, column=j, value=v)
        if f:
            c.number_format = f
wsg.freeze_panes = "A3"

# ------------------------------------------------ Legenda e avisos
wl = wb.create_sheet("Legenda e avisos")
wl.column_dimensions["A"].width = 38
wl.column_dimensions["B"].width = 120
wl["A1"] = "Legenda: o que significa cada coluna"
wl["A1"].font = Font(bold=True, size=13)
LEG = [
    ("Aba Resumo", ""),
    ("Patrimônio inicial / final", "Quanto dinheiro havia no começo (R$ 10 mil por sub-carteira) e no fim, somando o caixa e as cotas a preço de 09/11/2026."),
    ("Retorno no período", "Patrimônio final dividido pelo inicial, menos 1. É o ganho do período todo, não por ano."),
    ("Patrimônio final líquido", "O patrimônio final menos o imposto de 20% que seria cobrado se as cotas abertas fossem vendidas no último dia e menos o imposto de vendas já feitas e ainda não pago."),
    ("Retorno contra o CDI (pontos)", "Retorno líquido da carteira menos o retorno líquido de deixar tudo em 105% do CDI, em pontos percentuais. Negativo = perdeu do CDI."),
    ("Maior queda no caminho", "A maior distância, em %, entre um valor mais alto do patrimônio e o valor mais baixo que veio depois. Mostra o susto que se passaria."),
    ("Operações abertas / fechadas", "Aberta = ainda tem as cotas em 09/11/2026 (valor a preço do último pregão). Fechada = já vendeu."),
    ("Com lucro (%)", "Parte das operações cujo resultado (valorização + rendimentos − taxas) é positivo."),
    ("Pior / melhor operação", "Menor e maior resultado em % do valor comprado, contando as abertas a preço de 09/11."),
    ("Rendimentos recebidos", "Dinheiro que o fundo pagou por cota e entrou no caixa até 09/11, na data de pagamento. Não paga imposto."),
    ("Imposto do FII pago / devido", "Imposto de 20% sobre o ganho das vendas no mês (prejuízo de um mês abate o ganho dos próximos). Vence no último dia útil do mês seguinte."),
    ("IR e IOF do caixa", "Imposto retido quando o dinheiro parado em 105% do CDI é resgatado para comprar cotas ou pagar imposto (IR de 22,5% a 15% conforme os dias; IOF só nos primeiros 30 dias)."),
    ("Taxas", "0,03% sobre o valor de cada compra e de cada venda."),
    ("Sinais sem dinheiro", "Dias em que o fundo deu sinal, a compra era possível pelo volume negociado, mas o caixa não tinha R$ 200 livres."),
    ("Giro", "Total comprado em fundos dividido pelo patrimônio médio. Giro 1 = comprou, ao longo do período, o equivalente a uma vez o patrimônio."),
    ("Tempo médio por operação", "Dias corridos entre a compra e a venda, só das operações fechadas."),
    ("% aplicado em fundos", "Em média, que parte do patrimônio estava em cotas de fundos (o resto ficou em 105% do CDI)."),
    ("Aba Patrimônio dia a dia", "Valor de cada carteira no fechamento de cada pregão. O caixa entra já descontado de IR e IOF (como se resgatasse naquele dia). 105% do CDI R$ 20 mil = tudo parado no CDI desde 02/01. Mercado = índice do fundo imobiliário do meio (planilhas/mercado.csv)."),
    ("Aba Quanto estava aplicado", "Valor das cotas dividido pelo patrimônio, dia a dia, em cada sub-carteira."),
    ("Aba Mês a mês", "Retorno de cada mês, do último fechamento do mês anterior ao último fechamento do mês. Janeiro parte de 02/01. Novembro vai até 09/11."),
    ("Aba Operações", "Uma linha por compra. Sinal = dia em que a cota caiu abaixo do gatilho; Entrada = dia seguinte, preço de abertura. Valorização = venda − compra. Rendimentos = o que o fundo pagou por cota enquanto se tinha a cota (inclui os que ainda serão pagos). Resultado = valorização + rendimentos − taxas, antes do imposto do FII (que é cobrado por mês, não por operação). Resultado (%) = resultado ÷ valor da compra. As duas colunas finais servem ao gráfico."),
    ("Motivo da saída", "Volta à média = a cota subiu até a média dos últimos 200 pregões (vende por esse preço, ou pela abertura se for maior). Prazo = 252 pregões sem voltar. Fundo saiu da bolsa = os preços acabaram antes do fim da base; vendido ao último preço. Em aberto = ainda comprado em 09/11."),
    ("Aba Variantes", "Mesmas regras com ordem de R$ 500, R$ 1.000 e R$ 2.000 e a conservadora com gatilho 30%. Cada linha parte de R$ 10.000."),
    ("Aba Sinais sem dinheiro", "Resumo do destino de cada sinal e lista dos que não puderam ser comprados por falta de caixa."),
]
r = 3
for a, b in LEG:
    wl.cell(row=r, column=1, value=a).font = Font(bold=(b == ""))
    cb = wl.cell(row=r, column=2, value=b)
    cb.alignment = Alignment(wrap_text=True, vertical="top")
    wl.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
r += 1
wl.cell(row=r, column=1, value="Avisos").font = Font(bold=True, size=13)
r += 1
AVISOS = [
    ("2026 já foi visto", "A estratégia (média de 200 pregões, gatilhos de 15% e 20%, saída na volta à média) foi estudada com dados de 2018 a 2026; o período de conferência (2023 a 2026) já foi visto em estudos anteriores. Portanto 2026 NÃO é um teste novo: já fazia parte do período de conferência."),
    ("Um ano só não prova nada", "São menos de 10 meses e poucas operações (a conservadora fez 13 compras com ordem de R$ 1.000, só 2 já fechadas). Uma ou duas operações mudam o resultado inteiro. Não tire conclusão sobre a estratégia a partir desta aba."),
    ("Compra na abertura e venda pelo preço da média", "Compra-se no preço de abertura do dia seguinte ao sinal e vende-se pelo preço da média quando a máxima do dia a toca. Em fundo pouco negociado, ninguém garante esse preço. O resultado é otimista nesses casos. O dinheiro de uma venda também é usado já na abertura do mesmo dia."),
    ("Ordem de R$ 1.000 e cotas inteiras", "Com cotas inteiras, a ordem real fica um pouco abaixo do valor pretendido (veja 'Valor da compra' na aba Operações). O limite é 2% do negociado médio de 60 dias e o caixa disponível; abaixo de R$ 200 não compra."),
    ("Fundos que sumiram da base", "Alguns fundos deixam de ter preços no meio do período (parou de negociar, foi incorporado ou liquidado). A simulação vende pelo último preço, mas ninguém sabe se esse valor seria obtido (lacuna)."),
    ("Amortizações", f"Se o fundo devolver parte do capital (amortização) enquanto se tem a cota, esse dinheiro NÃO é creditado no caixa (lacuna). Nas posições de 2026 desta simulação foram {LAC['amz_n']} eventos desse tipo (R$ {br(LAC['amz_valor'])})."),
    ("Saltos de preço", f"Saltos acima de 60% para cima, 45% para baixo ou buracos de mais de 15 dias nos preços fazem a ordem ser encerrada pela guarda de dados. Ordens encerradas assim nesta simulação (conservadora e agressiva, ordem de R$ 1.000): {f_guarda}."),
    ("Rendimentos sem data", "Avisos sem data de pagamento no arquivo não entram no caixa (não foi estimada data). Rendimentos pagos depois de 09/11 aparecem como 'a receber' e não entram no patrimônio."),
    ("Imposto do FII", "O imposto é calculado sobre o ganho de cada mês, não por operação. Quando o caixa estava todo aplicado no dia do vencimento, o imposto fica pendente e é pago com o primeiro dinheiro que entra (descontado do patrimônio enquanto isso)."),
]
for a, b in AVISOS:
    wl.cell(row=r, column=1, value=a).alignment = Alignment(wrap_text=True, vertical="top")
    wl.cell(row=r, column=2, value=b).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
for rr_ in range(3, r):
    txt = wl.cell(row=rr_, column=2).value or ""
    wl.row_dimensions[rr_].height = max(18, 15 * (len(txt) // 115 + 1))

from openpyxl.worksheet.properties import PageSetupProperties
for ws_ in wb.worksheets:
    ws_.page_setup.orientation = "landscape"
    ws_.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws_.page_setup.fitToWidth = 1
    ws_.page_setup.fitToHeight = 0
wb.save(SAIDA_XLSX)
print(f"\nPlanilha salva em {SAIDA_XLSX}")

# ================================================================ TEXTO EM MARKDOWN
def md_tab(cab_, linhas):
    out = ["| " + " | ".join(cab_) + " |", "|" + "|".join("---" for _ in cab_) + "|"]
    for l_ in linhas:
        out.append("| " + " | ".join(str(x) for x in l_) + " |")
    return "\n".join(out)


mc, ma, mt, mcdi, mmer = M["Conservadora"], M["Agressiva"], M["Total"], M["CDI"], M["Mercado"]
i_pico = int(np.argmax(TOTAL_PAT))
pico_tot, d_pico_tot = float(TOTAL_PAT[i_pico]), DATAS[i_pico]
ops_c, ops_a = BASE["Conservadora"]["o"], BASE["Agressiva"]["o"]
res_ab = float(pd.concat([ops_c, ops_a]).query("status != 'Fechada'")["resultado"].sum())
res_fe = float(pd.concat([ops_c, ops_a]).query("status == 'Fechada'")["resultado"].sum())
sobrep = len(set(zip(ops_c["fundo"], ops_c["entrada"])) & set(zip(ops_a["fundo"], ops_a["entrada"])))
meses_ganha = sum(1 for ym in meses if MM[(ym, "Total")] > MM[(ym, "CDI")])
ret_tot_mes_pior = min(meses, key=lambda ym: MM[(ym, "Total")])
V = {(v["nome"], v["ordem"]): v for v in VAR}
_ab = pd.concat([ops_c, ops_a]).query("status != 'Fechada'").sort_values("resultado").drop_duplicates("fundo").head(3)
piores_ab = ", ".join(f"{r.fundo} ({pct(r.resultado_pct)})" for r in _ab.itertuples())
_vo = pd.concat([ops_c, ops_a]).query("status == 'Fechada' and motivo == @VOLTA")
_sa = pd.concat([ops_c, ops_a]).query("status == 'Fechada' and motivo != @VOLTA")
meses_abaixo = [f"{NOMES_MES[ym[1] - 1]}/{str(ym[0])[2:]}" for ym in meses if MM[(ym, "Total")] < MM[(ym, "CDI")]]
_sd = SIN[(SIN["resultado"] == "sem dinheiro") & (SIN["carteira"] == "Agressiva")]
d_sem_din = dt(_sd["execucao"].min()) if len(_sd) else "—"
comuns = sorted(set(ops_c["fundo"]) & set(ops_a["fundo"]))
fundos_saiu = ", ".join(sorted(set(pd.concat([ops_c, ops_a]).query("motivo == @SAIU")["fundo"])))


def f_pct1(x):
    return pct(x, 1)


linhas_res = [
    ("Patrimônio inicial", [brl(M[k]["p_ini"]) for k in cols_m]),
    ("Patrimônio final (cotas a preço de 09/11)", [brl(M[k]["p_fim"]) for k in cols_m]),
    ("Retorno no período", [pct(M[k]["ret"]) for k in cols_m]),
    ("Patrimônio final líquido do imposto que seria devido", [brl(M[k]["p_liq"]) for k in cols_m]),
    ("Retorno líquido", [pct(M[k]["ret_liq"]) for k in cols_m]),
    ("Retorno líquido contra o CDI (pontos)", [br(100 * (M[k]["ret_liq"] - mcdi["ret_liq"]), 1) for k in cols_m]),
    ("Maior queda no caminho", [pct(M[k]["queda"]) for k in cols_m]),
    ("... do pico em / até", [f"{dt(M[k]['d_pico'])} / {dt(M[k]['d_fundo'])}" if M[k]["queda"] < 0 else "—" for k in cols_m]),
    ("Operações abertas / fechadas", [f"{M[k]['n_ab']} / {M[k]['n_fe']}" if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Fechadas com lucro", [pct(M[k]["luc_fe"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Todas com lucro (abertas a preço de 09/11)", [pct(M[k]["luc_todas"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Pior operação", [f"{pct(M[k]['pior'])} {M[k]['pior_f'].split(' ')[0]}" if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Melhor operação", [f"{pct(M[k]['melhor'])} {M[k]['melhor_f'].split(' ')[0]}" if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Rendimentos recebidos", [brl(M[k]["rend"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Imposto do FII pago", [brl(M[k]["imposto"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Imposto do FII devido e não pago", [brl(M[k]["imp_devido"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Imposto se vendesse as abertas em 09/11", [brl(M[k]["imp_hip"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("IR e IOF retidos do caixa", [brl(M[k]["ir_iof"]) if "n_ab" in M[k] else (brl(cdi_ir_fim) if k == "CDI" else "—") for k in cols_m]),
    ("Taxas de compra e venda", [brl(M[k]["taxas"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Sinais sem dinheiro", [str(M[k]["sem_din"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Giro", [br(M[k]["giro"], 2) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Tempo médio por operação fechada (dias)", [br(M[k]["tempo"], 1) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Dinheiro aplicado em fundos, em média", [pct(M[k]["aplicado"]) if "n_ab" in M[k] else "—" for k in cols_m]),
]
T_RES = md_tab(["Indicador", "Conservadora (20%)", "Agressiva (15%)", "Total (R$ 20 mil)", "105% do CDI (R$ 20 mil)", "Mercado (R$ 20 mil)"],
               [[a] + b for a, b in linhas_res])

T_MES = md_tab(["Mês", "Conservadora", "Agressiva", "Total", "105% do CDI", "Mercado"],
               [[f"{NOMES_MES[ym[1] - 1]}/{str(ym[0])[2:]}" + (" (até 09/11)" if ym == (TS[-1].year, TS[-1].month) else "")] +
                [pct(MM[(ym, k)]) for k in ["Conservadora", "Agressiva", "Total", "CDI", "Mercado"]] for ym in meses])

T_VAR = md_tab(["Sub-carteira", "Gatilho", "Ordem", "Patrimônio final (preço de 09/11)", "Patrimônio final líquido", "Retorno líquido",
                "Maior queda", "Operações", "Giro", "Sinais sem dinheiro"],
               [[v["nome"], f"{int(v['X'] * 100)}%", brl(v["ordem"], 0), brl(v["p_fim"]), brl(v["p_liq"]), pct(v["ret_liq"]), pct(v["queda"]),
                 v["n"], br(v["giro"], 2), v["sem_din"]] for v in VAR] +
               [["105% do CDI (R$ 10 mil)", "—", "—", brl(CDI10[-1]), brl(CDI10[-1]), pct(CDI10[-1] / CAP_SUB - 1), "0,0%", "—", "—", "—"]])

fech_all = pd.concat([ops_c, ops_a]).query("status == 'Fechada'").sort_values(["carteira", "saida"])
T_FEC = md_tab(["Sub-carteira", "Fundo", "Entrada", "Saída", "Motivo", "Valor da compra", "Rendimentos", "Resultado", "Resultado (%)"],
               [[r.carteira, r.fundo, dt(r.entrada), dt(r.saida), r.motivo, brl(r.valor_compra), brl(r.rend_direito), brl(r.resultado),
                 pct(r.resultado_pct)] for r in fech_all.itertuples()])
ab_all = pd.concat([ops_c, ops_a]).query("status != 'Fechada'")
T_ABR = md_tab(["Sub-carteira", "Posições abertas", "Valor comprado", "Resultado hoje (com rendimentos)", "Em prejuízo", "Pior"],
               [[n, len(g), brl(g["valor_compra"].sum()), brl(g["resultado"].sum()), int((g["resultado"] < 0).sum()),
                 f"{g.loc[g['resultado_pct'].idxmin(), 'fundo']} {pct(g['resultado_pct'].min())}"]
                for n, g in ab_all.groupby("carteira", sort=False)])
funil_md = funil.copy()
T_FUN = md_tab(["Sub-carteira (ordem R$ 1.000)"] + list(funil_md.columns) + ["Total de sinais"],
               [[c] + [int(v) for v in r] + [int(r.sum())] for c, r in funil_md.iterrows()])
T_CONF = "\n".join(f"- {t}" for t in CONF_TXT)

T_LAC = md_tab(["Dado ou regra", "Situação", "Efeito no resultado"], [
    [f"Fundos cujos preços acabam no meio do período ({fundos_saiu})",
     f"Em {LAC['saiu_n']} ordens (conservadora + agressiva) o fundo parou de ter preço antes de 09/11 (as últimas linhas têm 'negociou = 0'). Vendido ao último preço registrado. Não há dado do que realmente aconteceu (liquidação, incorporação, suspensão).",
     f"Comprado nessas ordens: {brl(LAC['saiu_valor'])}; resultado simulado: {brl(LAC['saiu_res'])} (a maior parte é MCEM11, que caiu de 62 para 26,97). O resultado real pode ser pior ou melhor."],
    ["Amortizações (devolução de capital)", f"{LAC['amz_n']} eventos nas posições de 2026; não são creditadas no caixa se existirem.", f"Hoje: {brl(LAC['amz_valor'])}."],
    ["Rendimentos sem data de pagamento", f"{LAC['rend_sem_data_2026']} avisos de 2026 (todos os fundos) sem data de pagamento; nas posições simuladas, {brl(LAC['rend_sem_data_valor'])}. Não foi estimada data.", "Esse dinheiro não entra no caixa."],
    ["Rendimentos que vão ser pagos depois de 09/11", f"{brl(LAC['rend_a_receber'])} já declarados nas posições (conservadora + agressiva).", "Não entram no patrimônio de 09/11 (entrariam nos dias seguintes)."],
    ["Compra na abertura e venda pelo preço da média", "Ninguém garante esses preços em fundo pouco negociado; o limite de 2% do negociado médio reduz, mas não elimina, o problema.", "Resultado otimista, não medido."],
    ["Dinheiro da venda usado na mesma abertura", "O motor usa o dinheiro de uma venda do dia para comprar na abertura do mesmo dia.", "Pequeno ganho de tempo a favor da carteira; não medido."],
    ["Preço de 09/11 de fundos sem negociação no dia", f"{LAC['abertas_sem_negocio_hoje']} posições abertas (conservadora + agressiva) não tiveram negociação em 09/11; usa-se o último fechamento.", "Valor das posições pode estar defasado."],
    ["DARF vencido sem caixa para pagar", f"Agressiva: {brl(LAC['pend']['Agressiva'])} de imposto vencido em 30/10 ficou pendente (caixa todo aplicado). Foi descontado do patrimônio.", "Já considerado no patrimônio."],
    ["Outros custos", "Só a taxa de 0,03% por compra e por venda. Não há corretagem, custódia nem diferença entre preço de compra e de venda.", "Resultado real um pouco menor."],
    ["Prejuízo de anos anteriores", "A carteira nasce vazia em 02/01/2026; não há prejuízo acumulado de 2025 para abater.", "Nenhum."],
    ["Mercado (índice do fundo do meio)", "Índice sem custos nem imposto, calculado a partir do fechamento de 02/01/2026.", "Comparação apenas de referência."],
    ["Sinais de 20% e de 15% repetem", f"Um fundo que cai 20% abaixo da média antes passou pelos 15%, então os mesmos fundos aparecem nas duas sub-carteiras ({len(comuns)} fundos em comum: {', '.join(comuns)}); {sobrep} compras são idênticas (mesmo fundo e mesmo dia).", "As duas sub-carteiras não são apostas independentes; a mesma perda (ex.: MCEM11 em 12/05) conta duas vezes no total."],
])

DOC = f"""# Simulação do Kairi em 2026: carteira de R$ 20.000

Programa: `estudos/kairi_carteira_2026.py` (rodada do zero em poucos segundos). Planilha com gráficos: `planilhas/kairi_carteira_2026.xlsx`.
Gerado automaticamente; os números abaixo vêm da rodada do programa.

## Resultado em uma frase

De {dt(TS[J0])} a {dt(TS[-1])}, a carteira total de R$ 20.000 foi para {brl(mt['p_fim'])} ({pct(mt['ret'])}; {pct(mt['ret_liq'])} descontando o imposto que seria devido ao vender tudo), contra {brl(mcdi['p_fim'])} ({pct(mcdi['ret'])}) de deixar tudo em 105% do CDI e {brl(mmer['p_fim'])} ({pct(mmer['ret'])}) do mercado de fundos. Perdeu do CDI nas duas sub-carteiras.

## O que foi simulado

- **Duas sub-carteiras independentes**, cada uma com caixa próprio de R$ 10.000 em {dt(TS[J0])} (primeiro pregão do ano). Começam vazias: só valem sinais com data a partir de 02/01/2026.
- **Conservadora:** compra quando a cota fecha 20% ou mais abaixo da média dos últimos 200 pregões (o "gatilho"), com rendimento do fundo mantido. **Agressiva:** gatilho de 15%. **Variante extra:** conservadora com gatilho de 30%.
- **Mesmas regras das ordens já estudadas** (`estudos/auditoria_bloco2.py`, cópia verificada de `kairi_ordens.py`): universo de fundos, filtros (patrimônio, negociado, rendimento, preço sobre valor patrimonial), guarda de dados com saltos e buracos, entrada na abertura do pregão seguinte ao sinal, saída quando a máxima do dia toca a média de 200 pregões (vende pelo preço da média, ou pela abertura se for maior) ou no prazo de 252 pregões.
- **Tamanho da ordem:** R$ 1.000 (testes com R$ 500 e R$ 2.000), cotas inteiras, no máximo 2% do negociado médio do fundo em 60 dias e no máximo o caixa disponível. Abaixo de R$ 200 não compra. O mesmo fundo não pode ser comprado de novo enquanto já está na sub-carteira. Se há mais sinais que dinheiro no mesmo dia, compra primeiro o fundo mais negociado.
- **Taxa:** 0,03% na compra e 0,03% na venda.
- **Rendimentos** (isentos) entram no caixa na **data de pagamento** (`rendimentos_pagamentos.csv`). Tem direito quem estava com a cota no fechamento da data de corte do aviso (a "data-base"), a mesma regra de `kairi_ordens.py`. Pagamento em dia sem pregão entra no pregão seguinte.
- **Caixa parado** rende 105% do CDI com liquidez diária (`cdi.csv`), em lotes: cada entrada de dinheiro é um lote; as compras resgatam do lote mais antigo, com IR regressivo (22,5% até 180 dias corridos; 20% de 181 a 360; 17,5% de 361 a 720; 15% acima) e IOF nos primeiros 29 dias, por lote. O caixa que aparece no patrimônio diário já é líquido de IR e IOF.
- **Imposto do FII:** 20% sobre o ganho líquido das vendas de cada mês (prejuízo abate os ganhos seguintes). O DARF sai do caixa no último dia útil do mês seguinte. Posições abertas no fim ficam a preço de 09/11/2026; mostramos também o valor líquido do imposto que seria devido se fossem vendidas.
- **Comparações:** R$ 20.000 todo em 105% do CDI (líquido de IR, como resgatado em 09/11/2026) e o índice "mercado" (`mercado.csv`, fundo imobiliário do meio).

## Tabela 1. Resumo (ordem de R$ 1.000)

{T_RES}

**Legenda.** *Patrimônio* = caixa (líquido de IR e IOF) + cotas ao último preço, em R$. *Retorno* = final ÷ inicial − 1, no período todo (não por ano). *Líquido* = patrimônio final menos o imposto do FII devido (de vendas já feitas e do que seria cobrado se as cotas abertas fossem vendidas em 09/11). *Contra o CDI* = retorno líquido menos o retorno líquido do 105% do CDI, em pontos percentuais. *Maior queda* = maior distância, em %, de um valor alto do patrimônio até o ponto mais baixo seguinte. *Operações abertas* = ainda com cotas em 09/11. *Com lucro* = resultado (valorização + rendimentos − taxas) maior que zero. *Pior/melhor* = em % do valor comprado. *Imposto do FII pago* = DARF efetivamente pago até 09/11. *IR e IOF retidos do caixa* = imposto cobrado nos resgates do dinheiro parado (no 105% do CDI de R$ 20 mil, o IR do fim). *Sinais sem dinheiro* = sinais em que a compra era possível pelo negociado, mas o caixa não tinha R$ 200 livres. *Giro* = total comprado em fundos ÷ patrimônio médio. *Dinheiro aplicado em fundos* = média diária de (valor das cotas ÷ patrimônio).

**Leitura prática.** A carteira ficou {br(-100 * (mt['ret_liq'] - mcdi['ret_liq']), 1)} pontos abaixo do CDI: ganhou {pct(mt['ret_liq'])} contra {pct(mcdi['ret_liq'])}. Até {dt(d_pico_tot)} o total chegou a {brl(pico_tot)}; de {dt(mt['d_pico'])} a {dt(mt['d_fundo'])} caiu {pct(-mt['queda'])}. As {mt['n_ab']} posições ainda abertas somam resultado de {brl(res_ab)} (as piores: {piores_ab}); as fechadas somam {brl(res_fe)}. Os rendimentos recebidos ({brl(mt['rend'])}) não cobriram essas perdas.

## Tabela 2. Retorno mês a mês

{T_MES}

**Legenda.** Retorno de cada mês = patrimônio do último pregão do mês ÷ patrimônio do último pregão do mês anterior − 1. Janeiro parte do fechamento de 02/01/2026; novembro vai até 09/11. "Total" = as duas sub-carteiras somadas.

**Leitura prática.** O total ganhou do 105% do CDI em {meses_ganha} dos {len(meses)} meses. O pior mês foi {NOMES_MES[ret_tot_mes_pior[1] - 1]}/26 ({pct(MM[(ret_tot_mes_pior, 'Total')])}), junto com a queda do mercado. Os meses em que ficou abaixo do CDI foram: {", ".join(meses_abaixo)}.

## Tabela 3. Variantes (cada linha parte de R$ 10.000)

{T_VAR}

**Legenda.** *Gatilho* = queda abaixo da média de 200 pregões que dispara a compra. *Ordem* = valor pretendido por compra. *Patrimônio final líquido* = descontado o imposto do FII devido e o que seria devido ao vender as posições abertas. *Retorno líquido* = patrimônio final líquido ÷ R$ 10.000 − 1. *Giro* = total comprado ÷ patrimônio médio. A última linha é R$ 10.000 em 105% do CDI.

**Leitura prática.** Todas as variantes ficaram abaixo do 105% do CDI ({pct(CDI10[-1] / CAP_SUB - 1)}). Quanto maior a ordem, pior o resultado neste ano; ordens maiores esgotam o caixa mais cedo (deixam passar sinais) e fazem as perdas de fundos como MCEM11 pesarem mais. Com apenas esta amostra, isso não é uma regra. A conservadora de 30% quase não operou (2 compras): a queda foi pequena, mas o dinheiro ficou parado no CDI.

## Tabela 4. Operações fechadas (ordem de R$ 1.000)

{T_FEC}

**Legenda.** *Motivo:* volta à média = a cota subiu até a média de 200 pregões; fundo saiu da bolsa = os preços acabaram antes de 09/11 (vendido ao último preço). *Rendimentos* = o que o fundo pagou por cota enquanto se tinha a cota (inclui os ainda a receber). *Resultado* = valorização + rendimentos − taxas, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor da compra.

{T_ABR}

**Legenda.** *Resultado hoje* = valorização a preço de 09/11 + rendimentos − taxa de compra. *Em prejuízo* = posições abertas com resultado negativo.

**Leitura prática.** Das {len(fech_all)} operações fechadas, as {len(_vo)} de volta à média tiveram resultado entre {pct(_vo['resultado_pct'].min())} e {pct(_vo['resultado_pct'].max())}; as {len(_sa)} que fecharam por 'fundo saiu da bolsa' ficaram entre {pct(_sa['resultado_pct'].min())} e {pct(_sa['resultado_pct'].max())}. Entre as abertas, {int((ab_all['resultado'] < 0).sum())} de {len(ab_all)} estão no prejuízo, e a conta final depende de elas voltarem à média ou não.

## Tabela 5. O que aconteceu com cada sinal (ordem de R$ 1.000)

{T_FUN}

**Legenda.** *Comprado* = ordem executada com o valor pretendido. *Reduzido pelo caixa* = comprou menos que o pretendido, mas pelo menos R$ 200. *Fundo já em carteira* = o mesmo fundo já estava na sub-carteira. *Sem dinheiro* = faltou caixa. *Sem negociação na abertura* = o fundo não negociou no dia da entrada.

**Leitura prática.** A agressiva ficou sem dinheiro em {ma['sem_din']} sinais, o primeiro em {d_sem_din} (caixa todo aplicado). A conservadora teve poucos sinais e não faltou dinheiro para nenhum.

## Conferências feitas pelo programa

Todas passaram (asserts dentro do programa; veja a saída impressa):

- O caixa nunca ficou negativo em nenhum dia, nas {len(RES)} simulações (menor caixa: {brl(min_cx)}).
- Nenhuma compra no dia do sinal ({sum(len(R['ops_raw']) for R in RES.values())} compras, todas depois) e nenhum sinal anterior a 02/01/2026.
- O imposto do FII refeito por fora (mês a mês, com prejuízo abatendo) bate com o do programa; devido = pago + pendente + a vencer.
- R$ 20.000 em 105% do CDI refeitos à mão: {brl(CDI20[-1])} líquido (IR de 20%, {dias_cdi} dias).
{T_CONF}

## O que foi confirmado por execução e o que é interpretação

**Confirmado por execução (rodou e conferiu):** todos os números das tabelas; o caixa nunca negativo; entrada sempre depois do sinal; compra, rendimento, venda, taxa e resultado de uma operação de cada sub-carteira refeitos a partir dos arquivos de entrada; um resgate do caixa com IR (e outro com IOF + IR) refeitos com `cdi.csv`; imposto do FII refeito por fora.

**Interpretação (decisão minha, onde o pedido não dizia):**
- "Um fundo por vez" foi lido como: o mesmo fundo não pode ser comprado duas vezes ao mesmo tempo na mesma sub-carteira (como em `kairi_carteira.py`). Cada sub-carteira pode ter vários fundos diferentes.
- Compras na abertura resgatam o caixa com o índice do CDI do pregão anterior (o dia de hoje ainda não rendeu); os dias corridos para IR/IOF contam até a data do resgate. A venda de um fundo vira um lote novo no mesmo dia.
- Direito ao rendimento: data-base entre a entrada e a saída (inclusive a data de saída só quando a saída é no fechamento, no prazo ou posição aberta), como em `kairi_ordens.py`.
- Pagamento em fim de semana ou feriado entra no pregão seguinte. Avisos sem data de pagamento não entram (nada foi estimado).
- Para o retorno e a comparação, usei o patrimônio líquido do imposto do FII que seria devido ao vender tudo (o CDI também está líquido). O patrimônio diário não desconta imposto ainda não vencido.
- Resultado de cada operação = valorização + rendimentos (inclusive os ainda a receber) − taxas, antes do imposto, que é cobrado por mês.
- Total = soma simples das duas sub-carteiras (R$ 10.000 + R$ 10.000); elas compram, em parte, os mesmos fundos.

## Lacunas

{T_LAC}

## Avisos

- **2026 não é um teste novo.** O período de conferência (2023 a 2026) já foi visto em estudos anteriores; esta simulação usa dados que já entraram nas escolhas.
- **Um ano só não prova nada.** São {NM - J0} pregões e {mt['n']} compras no total; a conservadora fez {mc['n']} e só {mc['n_fe']} já fecharam. Dois ou três fundos explicam quase toda a diferença para o CDI.
- **Compras na abertura e vendas pelo preço da média são otimistas** em fundo pouco negociado.
"""
Path(RAIZ / "docs" / "SIMULACAO_KAIRI_2026.md").write_text(DOC, encoding="utf-8")
print(f"Texto salvo em {RAIZ / 'docs' / 'SIMULACAO_KAIRI_2026.md'}")
print(f"\nTempo total: {time.time() - T0:.1f} s")
