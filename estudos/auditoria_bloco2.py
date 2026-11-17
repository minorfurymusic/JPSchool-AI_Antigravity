"""Auditoria do Kairi, BLOCO 2: funil das quedas (item 4) e regra de "virada" (item 5).

Le so planilhas/ (nada de dados/). Copia a logica de estudos/kairi_ordens.py (universo, guarda de dados,
sinais, rendimento mantido, saida na volta a media com prazo de 252, tamanho da ordem, taxas) sem alterar
aquele arquivo. Regua: 105% do CDI (planilhas/cdi.csv), liquido de IR regressivo e IOF.

Rodar com:
    cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/auditoria_bloco2.py
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
SCRATCH = Path("/tmp/claude-0/-home-user-JPSchool-AI-Antigravity/fd72a53f-617a-5c36-a0e6-2a1ebd0f529f/scratchpad")
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

INICIO_D = np.datetime64("2018-01-01", "D")
CORTE_22 = pd.Timestamp("2022-12-31")
B3 = 0.0003
IR_OP = 0.20
EXCLUIDOS = {"XPPR11", "CARE11"}
N = 200
PRAZO = 252
LAG_REND = 126
K_REND = 0.95
ORDEM_MAX = 3000.0
PCT_VOL = 0.05
ORDEM_MIN = 1000.0
VOLTA, PRAZO_M, SAIU, GUARDA, ABERTO = "volta à média", "prazo", "fundo saiu da bolsa", "dado suspeito", "em aberto"
JAN_VIRADA = 60
GATILHOS = [0.10, 0.15, 0.20, 0.30]
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]
PER = ["Escolha 2018–2022", "Conferência 2023–2026", "Total"]


# ---------------------------------------------------------------- formatacao
def isnan(x):
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


def br(x, d=2):
    if isnan(x):
        return "nd"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x, d=0):
    return "nd" if isnan(x) else "R$ " + br(x, d)


def pct(x, d=1):
    return "nd" if isnan(x) else br(100 * x, d) + "%"


def md_tab(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------- carga (copiada de kairi_ordens.py)
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
RD = carregar("rendimentos").dropna(subset=["data_base"]).reset_index(drop=True)
FU = carregar("fundos")
CDI = carregar("cdi")
C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG, C_REND, C_PVP, C_PAT = "negociou (1/0)", "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL, C_AMO = "volume_medio_60 (R$)", "amortizacao_12m (1/0)"
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
MD = MK["data"].to_numpy("datetime64[D]")
TS = list(MK["data"])
NM = len(MD)
I0 = int(np.searchsorted(MD, INICIO_D))
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))
CD_D = CDI["data"].to_numpy("datetime64[D]")
CD_I = CDI["indice_105_do_cdi"].to_numpy(float)
assert CD_D[-1] >= MD[-1], "cdi.csv nao cobre a ultima data da base"


def aliq_rf(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


def cdi_liq(D, S, V):
    """105% do CDI liquido (IOF e IR) de V aplicado em D e resgatado em S. Data fora do arquivo: ultimo dia util anterior."""
    i0 = int(np.searchsorted(CD_D, D, "right")) - 1
    i1 = int(np.searchsorted(CD_D, S, "right")) - 1
    bruto = V * (CD_I[i1] / CD_I[i0] - 1)
    dias = int((S - D) / np.timedelta64(1, "D"))
    iof = IOF[dias - 1] / 100 if 1 <= dias <= 29 else (1.0 if dias <= 0 else 0.0)
    return bruto * (1 - iof) * (1 - aliq_rf(dias))


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
    kE = C / mN - 1                                              # kairi com a media ate o proprio dia (usado so na virada, como em kairi_expandido.py)
    m10 = Cs.rolling(10, min_periods=10).mean().shift(1).to_numpy()   # media dos 10 fechamentos anteriores
    sim = np.zeros(n, bool)
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= K_REND * R[:-LAG_REND]
    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome
    FD[nome] = dict(nome=nome, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, R=R, PVP=PVP, VOL=VOL, NEG=NEG,
                    univ=univ, bad=bad, cbad=cbad, mN=mN, mP=mP, k200=k200, kE=kE, m10=m10, sim=sim,
                    aberto=int(mi[-1]) >= NM - 21)

RDF = {}
for f_, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f_] = (bd, cs)


def rend_val(f, D, S, incl):
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


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


CAND = {}
for X in GATILHOS:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if I0 <= md + 1 < NM:
                lst[md + 1].append((F, int(s), md))
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


def conta(F, legs, k, mot, pxs):
    """legs = [(linha de entrada, cotas), ...]; todas vendem na linha k a pxs. Resultado ANTES do imposto do FII
    (valorizacao + rendimentos - taxas); imposto_op = regra por ordem de kairi_ordens.py (so para conferir)."""
    S = F["dates"][k]
    incl = mot in (PRAZO_M, ABERTO)
    valor = venda = rend = cdi = 0.0
    for e, cot in legs:
        v = cot * float(F["A"][e])
        valor += v
        venda += cot * pxs
        rend += rend_val(F["nome"], F["dates"][e], S, incl) * cot
        cdi += cdi_liq(F["dates"][e], S, v)
    valorizacao = venda - valor
    taxas = B3 * valor + B3 * venda
    antes = valorizacao + rend - taxas
    imposto_op = IR_OP * max(valorizacao - taxas, 0.0)
    e0 = legs[0][0]
    t = np.arange(e0, k + 1)
    vt = np.zeros(len(t))
    ct = np.zeros(len(t))
    for e, cot in legs:
        m = t >= e
        vt[m] += cot * F["L"][t[m]]
        ct[m] += cot * float(F["A"][e])
    queda = min(0.0, float((vt / ct).min()) - 1)
    D0 = F["dates"][e0]
    return dict(valor=valor, valorizacao=valorizacao, rend=rend, taxas=taxas, antes=antes, imposto_op=imposto_op,
                resultado_op=antes - imposto_op, cdi=cdi, exc=antes - cdi, pct=antes / valor, queda=queda,
                dias=int((S - D0) / np.timedelta64(1, "D")), pregoes=int(k - e0), motivo=mot, px_s=float(pxs),
                data_saida=pd.Timestamp(S), mi_x=int(np.searchsorted(MD, S, "left")),
                px_e=legs[0][1] * float(F["A"][e0]) / legs[0][1] if len(legs) == 1 else
                valor / sum(c for _, c in legs), cotas=sum(c for _, c in legs), k=int(k))


def tamanho(F, s, px):
    vol = float(F["VOL"][s])
    lim = min(ORDEM_MAX, PCT_VOL * vol) if np.isfinite(vol) else 0.0
    return int(np.floor(lim / px + 1e-9)), lim


def gatilho_virada(F, s):
    """Regra E2 de kairi_expandido.py (Parte 4): primeiro dia j em s+1..s+60 com fechamento > media dos 10 fechamentos
    anteriores e kairi (com a media ate o proprio dia j) <= -0,05; compra na abertura de j+1, se negociou."""
    last = F["n"] - 1
    lo, hi = s + 1, min(s + JAN_VIRADA, last - 1)
    if lo > hi:
        return "sem", None
    js = np.arange(lo, hi + 1)
    cond = (F["C"][js] > F["m10"][js]) & (F["kE"][js] <= -0.05)
    if not cond.any():
        return "sem", None
    e = int(js[int(np.argmax(cond))]) + 1
    if F["NEG"][e] == 1 and np.isfinite(F["A"][e]) and F["A"][e] > 0:
        return "ok", e
    return "inv", None


def finaliza(rec, F, s, md, c, tipo):
    rec.update(c)
    rec["fundo"] = F["nome"]
    rec["tipo"] = TIPO.get(F["nome"], "sem tipo")
    rec["sinal"] = TS[md]
    rec["data_sinal_entrada_direta"] = TS[md + 1]
    rec["md"] = md
    rec["s"] = s
    rec["c_sinal"] = float(F["C"][s])
    prof = -np.nanmin(F["k200"][s:c["k"] + 1])
    rec["prof"] = float(prof)
    rec["aberto"] = c["motivo"] == ABERTO
    return rec


def simular(X, modo):
    """modo: 'direto' (regra de kairi_ordens.py), 'virada' (E2), 'duas' (metade direta + metade na virada).
    Retorna (ordens, status por sinal (md, fundo) -> texto)."""
    cands = CAND[X]
    busy = {}
    ordens, status = [], {}
    if modo == "virada":
        lst = []
        for ex in range(I0, NM):
            for F, s, md in cands[ex]:
                st, e = gatilho_virada(F, s)
                if st == "sem":
                    status[(md, F["nome"])] = "não virou em 60 pregões"
                elif st == "inv":
                    status[(md, F["nome"])] = "virou, mas sem negociação na abertura seguinte"
                else:
                    lst.append((int(F["mi"][e]), F["nome"], F, s, md, e))
        lst.sort(key=lambda t: (t[0], t[1]))
        for _, f, F, s, md, e in lst:
            if f in busy and busy[f] >= e:
                status[(md, f)] = "bloqueado (fundo já em carteira)"
                continue
            px = float(F["A"][e])
            cot, _ = tamanho(F, s, px)
            if cot <= 0 or cot * px < ORDEM_MIN:
                status[(md, f)] = "ordem menor que R$ 1.000"
                continue
            k, mot, pxs = saida_volta(F, e)
            busy[f] = k
            c = conta(F, [(e, cot)], k, mot, pxs)
            c["dias_ate_virar"] = int(e - (s + 1))
            ordens.append(finaliza(dict(modo=modo, X=X), F, s, md, c, modo))
            status[(md, f)] = "virou e virou ordem"
        return pd.DataFrame(ordens), status

    for ex in range(I0, NM):
        for F, s, md in sorted(cands[ex], key=lambda t: t[0]["nome"]):
            f = F["nome"]
            d_ex = MD[ex]
            r = int(np.searchsorted(F["dates"], d_ex))
            if r >= F["n"] or F["dates"][r] != d_ex or F["NEG"][r] != 1 or not np.isfinite(F["A"][r]) or F["A"][r] <= 0:
                status[(md, f)] = "sem negociação na entrada direta"
                continue
            if f in busy and busy[f] >= r:
                status[(md, f)] = "bloqueado (fundo já em carteira)"
                continue
            px = float(F["A"][r])
            cot, lim = tamanho(F, s, px)
            if cot <= 0 or cot * px < ORDEM_MIN:
                status[(md, f)] = "ordem menor que R$ 1.000"
                continue
            k, mot, pxs = saida_volta(F, r)
            busy[f] = k
            if modo == "direto":
                c = conta(F, [(r, cot)], k, mot, pxs)
                ordens.append(finaliza(dict(modo=modo, X=X), F, s, md, c, modo))
                status[(md, f)] = "ordem direta"
                continue
            half = cot * px / 2
            c1 = int(np.floor(half / px + 1e-9))
            if c1 <= 0:
                status[(md, f)] = "metade menor que uma cota"
                continue
            legs = [(r, c1)]
            st, e2 = gatilho_virada(F, s)
            comprou2 = False
            if st == "ok" and e2 < k:
                px2 = float(F["A"][e2])
                c2 = int(np.floor(half / px2 + 1e-9))
                if c2 > 0:
                    legs.append((e2, c2))
                    comprou2 = True
            c = conta(F, legs, k, mot, pxs)
            c["comprou2"] = comprou2
            c["metade_parada"] = 0.0 if comprou2 else half
            c["cdi_parada"] = 0.0 if comprou2 else cdi_liq(F["dates"][r], F["dates"][k], half)
            c["pct_pretendido"] = (c["antes"] + c["cdi_parada"]) / (c["valor"] + c["metade_parada"])
            c["exc_pretendido_pp"] = c["pct_pretendido"]
            ordens.append(finaliza(dict(modo=modo, X=X), F, s, md, c, modo))
            status[(md, f)] = "duas partes (2ª comprada)" if comprou2 else "duas partes (2ª não comprada)"
    return pd.DataFrame(ordens), status


def periodo(df, col):
    return np.where(df[col] <= CORTE_22, PER[0], PER[1])


def imposto_fii_mensal(df):
    """FII: ganho na venda (valorizacao - taxas) tributado a 20% por mes de venda; prejuizo abate os ganhos seguintes.
    Ordens em aberto nao pagam (nao venderam). O DARF e pago no mes seguinte; essa defasagem nao entra (lacuna)."""
    f = df[~df["aberto"]].copy()
    f["mes"] = f["data_saida"].dt.to_period("M")
    saldo = 0.0
    tot = 0.0
    for _, g in f.groupby("mes", sort=True):
        ganho = float((g["valorizacao"] - g["taxas"]).sum())
        liq = ganho + saldo
        if liq > 0:
            tot += IR_OP * liq
            saldo = 0.0
        else:
            saldo = liq
    return tot


def estat(d, extra=False):
    n = len(d)
    if n == 0:
        return dict(n=0)
    ap = float(d["valor"].sum())
    res = float(d["antes"].sum())
    cdi = float(d["cdi"].sum())
    p = d["pct"].to_numpy(float)
    kq = max(1, int(round(0.10 * n)))
    imp = imposto_fii_mensal(d)
    o = dict(n=n, abertas=int(d["aberto"].sum()), aplicado=ap, res=res, res_pct=res / ap, cdi=cdi, exc=res - cdi,
             exc_pp=(res - cdi) / ap, pos=float((d["antes"] > 0).mean()), med=float(np.median(p)), media=float(p.mean()),
             dp=float(p.std(ddof=1)) if n > 1 else np.nan, dp_perdas=float(np.sqrt(np.mean(np.minimum(p, 0) ** 2))),
             pior=float(p.min()), pior_rs=float(d.loc[d["pct"].idxmin(), "antes"]),
             pior10=float(np.sort(p)[:kq].mean()), q05=float(np.quantile(p, 0.05)), q95=float(np.quantile(p, 0.95)),
             queda_med=float(d["queda"].mean()), queda_pior=float(d["queda"].min()), dias=float(d["dias"].mean()),
             imp_fii=imp, res_pos_imp=res - imp, exc_pos_imp=res - imp - cdi, n_exc_pos=int((d["exc"] > 0).sum()))
    return o


def por_per(df, col="periodo"):
    return [(PER[0], df[df[col] == PER[0]]), (PER[1], df[df[col] == PER[1]]), (PER[2], df)]


def pico_dinheiro(df):
    ap = np.zeros(NM + 2)
    for r in df.itertuples(index=False):
        mx = NM if r.motivo == ABERTO else r.mi_x
        ap[r.mi_e] += r.valor
        ap[mx] -= r.valor
    apd = np.cumsum(ap)[I0:NM]
    j = int(np.argmax(apd))
    return float(apd[j]), pd.Timestamp(MD[I0 + j])


# ================================================================ geracao
print("== CARGA ==")
print(f"fundos: {len(FD)}; pregoes do mercado: {NM} ({TS[0]:%d/%m/%Y} a {TS[-1]:%d/%m/%Y}); cdi.csv ate {pd.Timestamp(CD_D[-1]):%d/%m/%Y}")

ORD = {}
for X in GATILHOS:
    o, st = simular(X, "direto")
    o["mi_e"] = [int(np.searchsorted(MD, np.datetime64(d, "D"))) for d in o["data_sinal_entrada_direta"]]
    o["data_entrada"] = o["data_sinal_entrada_direta"]
    o["periodo"] = periodo(o, "data_entrada")
    ORD[X] = (o, st)
    print(f"gatilho {int(X * 100)}%: {len(o)} ordens diretas")

# ================================================================ CONFERENCIA 1: reproduz kairi_ordens.csv (A e B)
print("\n== CONFERENCIA 1 - minha cópia reproduz as carteiras A (15%) e B (20%) de planilhas/kairi_ordens.csv ==")
KO = pd.read_csv(PL / "kairi_ordens.csv", sep=";", decimal=",", encoding="utf-8-sig")
for c in ["Data do sinal", "Data de entrada", "Data de saída (ou do último preço)"]:
    KO[c] = pd.to_datetime(KO[c], format="%d/%m/%Y")
OKREP = True
for cart, X in [("A", 0.15), ("B", 0.20)]:
    ref = KO[KO["Carteira"] == cart].sort_values(["Data de entrada", "Fundo"]).reset_index(drop=True)
    mine = ORD[X][0].sort_values(["data_entrada", "fundo"]).reset_index(drop=True)
    ok_n = len(ref) == len(mine)
    ok = ok_n
    if ok_n:
        ok_f = (ref["Fundo"].values == mine["fundo"].values).all()
        ok_de = (ref["Data de entrada"].values == mine["data_entrada"].values).all()
        ok_ds = (ref["Data de saída (ou do último preço)"].values == mine["data_saida"].values).all()
        d_pe = float(np.abs(ref["Preço de entrada (R$)"].values - mine["px_e"].round(2).values).max())
        d_ps = float(np.abs(ref["Preço de saída (ou atual) (R$)"].values - mine["px_s"].round(2).values).max())
        d_cot = float(np.abs(ref["Cotas"].values - mine["cotas"].values).max())
        d_res = float(np.abs(ref["Resultado (R$)"].values - mine["resultado_op"].round(2).values).max())
        ok_mot = (ref["Motivo da saída"].values == mine["motivo"].values).all()
        ok = bool(ok_f and ok_de and ok_ds and ok_mot and d_pe < 1e-9 and d_ps < 1e-9 and d_cot == 0 and d_res <= 0.011)
        print(f"carteira {cart}: ordens csv={len(ref)} minha={len(mine)}; fundos/datas de entrada/datas de saída/motivos iguais: "
              f"{bool(ok_f)}/{bool(ok_de)}/{bool(ok_ds)}/{bool(ok_mot)}; dif máx preço entrada={d_pe:.4f}, saída={d_ps:.4f}, cotas={d_cot:.0f}, "
              f"resultado R$ (com imposto por ordem)={d_res:.4f}; soma resultado csv={ref['Resultado (R$)'].sum():,.2f} "
              f"minha={mine['resultado_op'].sum():,.2f} -> {'REPRODUZ' if ok else 'NÃO REPRODUZ'}")
    else:
        print(f"carteira {cart}: número de ordens difere csv={len(ref)} minha={len(mine)}")
    OKREP &= ok
assert OKREP, "a cópia não reproduz kairi_ordens.csv"
pk15, d15 = pico_dinheiro(ORD[0.15][0])
pk20, d20 = pico_dinheiro(ORD[0.20][0])
print(f"dinheiro do pico: A {brl(pk15)} (esperado R$ 262.698), B {brl(pk20)} (esperado R$ 151.506)")
assert round(pk15) == 262698 and round(pk20) == 151506

# ================================================================ ITEM 4
TAB = {}
print("\n================ ITEM 4 - FUNIL DAS QUEDAS ================")

# 4a) carteira por gatilho
rows = []
for X in GATILHOS:
    o = ORD[X][0]
    pk, dpk = pico_dinheiro(o)
    for lab, d in por_per(o):
        e = estat(d)
        rows.append(dict(gatilho=f"{int(X * 100)}%", periodo=lab, ordens=e["n"], abertas=e["abertas"], aplicado=e["aplicado"],
                         res=e["res"], res_pct=e["res_pct"], cdi=e["cdi"], exc=e["exc"], exc_pp=e["exc_pp"], pos=e["pos"],
                         pior=e["pior"], pior_rs=e["pior_rs"], dias=e["dias"], pico=pk if lab == PER[2] else np.nan,
                         imp=e["imp_fii"], exc_imp=e["exc_pos_imp"], n_exc_pos=e["n_exc_pos"]))
G = pd.DataFrame(rows)
G.to_csv(PL / "auditoria_bloco2_gatilhos.csv", **OPC)
TAB["gatilhos"] = md_tab(pd.DataFrame({
    "Gatilho": G["gatilho"], "Período": G["periodo"], "Ordens (em aberto)": [f"{a} ({b})" for a, b in zip(G["ordens"], G["abertas"])],
    "Aplicado": G["aplicado"].map(brl), "Resultado R$": G["res"].map(brl), "Resultado %": G["res_pct"].map(pct),
    "105% CDI líq. R$": G["cdi"].map(brl), "Excesso R$": G["exc"].map(brl), "Excesso (pp do aplicado)": G["exc_pp"].map(lambda v: br(100 * v, 1)),
    "% positivas": G["pos"].map(pct), "Pior ordem": G["pior"].map(pct), "Dias médios": G["dias"].map(lambda v: br(v, 0)),
    "Dinheiro do pico": G["pico"].map(brl)}))
print(G.to_string(index=False))

# 4b) funil
funil_rows = []
for X, ups in [(0.10, [0.15, 0.20, 0.30]), (0.15, [0.20, 0.30])]:
    o = ORD[X][0]
    for lab, d in por_per(o):
        r = dict(gatilho=f"{int(X * 100)}%", periodo=lab, sinais_com_ordem=len(d))
        for u in [0.15, 0.20, 0.30]:
            r[f"chegou_{int(u * 100)}"] = int((d["prof"] >= u - 1e-12).sum()) if u in ups else np.nan
        funil_rows.append(r)
FN = pd.DataFrame(funil_rows)
FN.to_csv(PL / "auditoria_bloco2_funil.csv", **OPC)
TAB["funil"] = md_tab(pd.DataFrame({
    "Gatilho": FN["gatilho"], "Período": FN["periodo"], "Ordens (sinais)": FN["sinais_com_ordem"],
    "Chegaram a 15%": [("-" if isnan(v) else f"{int(v)} ({100 * v / n:.0f}%)") for v, n in zip(FN["chegou_15"], FN["sinais_com_ordem"])],
    "Chegaram a 20%": [("-" if isnan(v) else f"{int(v)} ({100 * v / n:.0f}%)") for v, n in zip(FN["chegou_20"], FN["sinais_com_ordem"])],
    "Chegaram a 30%": [("-" if isnan(v) else f"{int(v)} ({100 * v / n:.0f}%)") for v, n in zip(FN["chegou_30"], FN["sinais_com_ordem"])]}))
print(FN.to_string(index=False))

# 4c) faixas de profundidade maxima
FAIXAS = {0.10: [(0.10, 0.15), (0.15, 0.20), (0.20, 0.30), (0.30, 9)], 0.15: [(0.15, 0.20), (0.20, 0.30), (0.30, 9)]}


def nome_faixa(a, b):
    return f"{int(round(a * 100))}–{int(round(b * 100))}%" if b < 9 else f"mais de {int(round(a * 100))}%"


fx_rows = []
for X, fxs in FAIXAS.items():
    o = ORD[X][0]
    for lab, d in por_per(o):
        for a, b in fxs:
            sub = d[(d["prof"] >= a - 1e-12) & (d["prof"] < b - 1e-12)]
            e = estat(sub)
            fx_rows.append(dict(gatilho=f"{int(X * 100)}%", periodo=lab, faixa=nome_faixa(a, b), ordens=e["n"],
                                media=e.get("media", np.nan), mediana=e.get("med", np.nan), pos=e.get("pos", np.nan),
                                exc_pp=e.get("exc_pp", np.nan), exc=e.get("exc", 0.0), res=e.get("res", 0.0),
                                abertas=e.get("abertas", 0)))
FX = pd.DataFrame(fx_rows)
FX.to_csv(PL / "auditoria_bloco2_faixas.csv", **OPC)
TAB["faixas"] = md_tab(pd.DataFrame({
    "Entrada em": FX["gatilho"], "Período": FX["periodo"], "Profundidade máxima": FX["faixa"], "Ordens": FX["ordens"],
    "Resultado médio": FX["media"].map(pct), "Mediana": FX["mediana"].map(pct), "% positivas": FX["pos"].map(pct),
    "Excesso sobre 105% CDI (pp, média)": FX["exc_pp"].map(lambda v: "nd" if isnan(v) else br(100 * v, 1)),
    "Excesso R$": FX["exc"].map(brl), "Resultado R$": FX["res"].map(brl)}))
print(FX.to_string(index=False))

# 4d) lucrativas perdidas ao subir o gatilho
pd_rows = []
for lo, hi in [(0.10, 0.15), (0.15, 0.20), (0.20, 0.30)]:
    o = ORD[lo][0]
    sup = {}
    for r in ORD[hi][0].itertuples(index=False):
        sup.setdefault(r.fundo, []).append(r.md)
    for lab, d in por_per(o):
        nunca = d[d["prof"] < hi - 1e-12]
        chegou = d[d["prof"] >= hi - 1e-12]
        luc, prej = nunca[nunca["antes"] > 0], nunca[nunca["antes"] <= 0]
        # confere com ordem real da carteira superior (mesmo fundo, sinal dentro do episodio)
        tem = sum(any(r_.md <= m <= r_.mi_x for m in sup.get(r_.fundo, [])) for r_ in chegou.itertuples(index=False))
        tem_nunca = sum(any(r_.md <= m <= r_.mi_x for m in sup.get(r_.fundo, [])) for r_ in nunca.itertuples(index=False))
        pd_rows.append(dict(de=f"{int(lo * 100)}%", para=f"{int(hi * 100)}%", periodo=lab, ordens=len(d),
                            nunca_chegou=len(nunca), luc_perdidas_n=len(luc), luc_perdidas_rs=float(luc["antes"].sum()),
                            prej_evitados_n=len(prej), prej_evitados_rs=float(prej["antes"].sum()),
                            saldo_rs=float(nunca["antes"].sum()), luc_perdidas_exc=float(luc["exc"].sum()),
                            prej_evitados_exc=float(prej["exc"].sum()), exc_nunca=float(nunca["exc"].sum()),
                            chegou_n=len(chegou), chegou_rs=float(chegou["antes"].sum()),
                            chegou_com_ordem_sup=tem, nunca_com_ordem_sup=tem_nunca))
PDD = pd.DataFrame(pd_rows)
PDD.to_csv(PL / "auditoria_bloco2_perdidas.csv", **OPC)
TAB["perdidas"] = md_tab(pd.DataFrame({
    "Subir de → para": PDD["de"] + " → " + PDD["para"], "Período": PDD["periodo"], "Ordens do gatilho menor": PDD["ordens"],
    "Nunca chegaram ao maior": PDD["nunca_chegou"],
    "Lucrativas perdidas (n)": PDD["luc_perdidas_n"], "Lucrativas perdidas (R$)": PDD["luc_perdidas_rs"].map(brl),
    "Prejuízos evitados (n)": PDD["prej_evitados_n"], "Prejuízos evitados (R$)": PDD["prej_evitados_rs"].map(brl),
    "Saldo do que a carteira maior não tem (R$)": PDD["saldo_rs"].map(brl),
    "Excesso s/ CDI do que não tem (R$)": PDD["exc_nunca"].map(brl)}))
print(PDD.to_string(index=False))

# planilha com todas as ordens diretas dos gatilhos
todas = []
for X in GATILHOS:
    o = ORD[X][0]
    todas.append(pd.DataFrame({
        "Gatilho": f"{int(X * 100)}%", "Fundo": o["fundo"], "Data do sinal": o["sinal"], "Data de entrada": o["data_entrada"],
        "Período": o["periodo"], "Preço de entrada (R$)": o["px_e"].round(2), "Cotas": o["cotas"].astype(int),
        "Valor (R$)": o["valor"].round(2), "Data de saída": o["data_saida"], "Preço de saída (R$)": o["px_s"].round(2),
        "Motivo": o["motivo"], "Dias": o["dias"], "Resultado antes do imposto (R$)": o["antes"].round(2),
        "Resultado (%)": (100 * o["pct"]).round(2), "105% CDI líquido (R$)": o["cdi"].round(2),
        "Excesso (R$)": o["exc"].round(2), "Maior queda abaixo da entrada (%)": (100 * o["queda"]).round(1),
        "Profundidade máxima no episódio (%)": (100 * o["prof"]).round(1)}))
pd.concat(todas).to_csv(PL / "auditoria_bloco2_ordens_gatilhos.csv", **OPC)

# ================================================================ ITEM 5
print("\n================ ITEM 5 - VIRADA (E2) CONTRA ENTRADA DIRETA ================")
V5 = {}
for X in [0.15, 0.20]:
    dire, st_d = ORD[X]
    vir, st_v = simular(X, "virada")
    duas, st_2 = simular(X, "duas")
    for o in (vir, duas):
        o["mi_e"] = [int(np.searchsorted(MD, np.datetime64(d, "D"))) for d in o["data_sinal_entrada_direta"]]
        o["data_entrada"] = o["data_sinal_entrada_direta"]        # periodo pela data da entrada direta do sinal (mesma chave nos tres)
        o["periodo"] = periodo(o, "data_entrada")
    V5[X] = (dire, vir, duas, st_v)
    print(f"gatilho {int(X * 100)}%: direta {len(dire)}, virada {len(vir)}, duas partes {len(duas)}")

# rel. de preco de entrada
def rel_entrada(o, F_col="c_sinal"):
    return float((o["px_e"] / o["c_sinal"] - 1).mean())


# direta nos mesmos sinais de cada comparacao
def so_sinais(o, ref):
    chaves = set(zip(ref["md"], ref["fundo"]))
    return o[[(m, f) in chaves for m, f in zip(o["md"], o["fundo"])]]


def med_virada(d, nome, total_sinais=None, nao_viraram=None, ref_direta=None):
    e = estat(d)
    if e["n"] == 0:
        return dict(metodo=nome, ordens=0)
    out = dict(metodo=nome, ordens=e["n"], sinais_sem_ordem=nao_viraram, preco_vs_fech_sinal=rel_entrada(d),
               res=e["res"], res_pct=e["res_pct"], cdi=e["cdi"], exc=e["exc"], exc_pp=e["exc_pp"], pos=e["pos"],
               dp=e["dp"], dp_perdas=e["dp_perdas"], pior=e["pior"], pior10=e["pior10"], queda_med=e["queda_med"],
               queda_pior=e["queda_pior"], q05=e["q05"], q95=e["q95"], dias=e["dias"], aplicado=e["aplicado"],
               imp=e["imp_fii"], exc_imp=e["exc_pos_imp"], abertas=e["abertas"], media=e["media"])
    return out


V_ROWS = []
PARES = []
for X in [0.15, 0.20]:
    dire, vir, duas, st_v = V5[X]
    for lab, _ in por_per(dire):
        sel = (lambda df: df) if lab == PER[2] else (lambda df, l=lab: df[df["periodo"] == l])
        d_, v_, t_ = sel(dire), sel(vir), sel(duas)
        # sinais da carteira direta que nao viraram ordem na virada
        chaves_v = set(zip(v_["md"], v_["fundo"]))
        nao = [(m, f) for m, f in zip(d_["md"], d_["fundo"]) if (m, f) not in chaves_v]
        d_sem = d_[[(m, f) not in chaves_v for m, f in zip(d_["md"], d_["fundo"])]]
        d_com = d_[[(m, f) in chaves_v for m, f in zip(d_["md"], d_["fundo"])]]
        # direta e virada nos mesmos sinais
        chaves_d = set(zip(d_["md"], d_["fundo"]))
        v_par = v_[[(m, f) in chaves_d for m, f in zip(v_["md"], v_["fundo"])]]
        base = [
            med_virada(d_, "Entrada direta", nao_viraram=0),
            med_virada(v_, "Virada (E2, até 60 pregões)", nao_viraram=len(nao)),
            med_virada(t_, "Duas partes (½ direta + ½ virada)", nao_viraram=int((~t_["comprou2"]).sum()) if len(t_) else 0),
            med_virada(so_sinais(d_, t_), "Direta nos mesmos sinais das duas partes", nao_viraram=0),
        ]
        for b in base:
            b.update(gatilho=f"{int(X * 100)}%", periodo=lab)
            V_ROWS.append(b)
        # perdas evitadas e ganhos perdidos (ordens diretas cujo sinal nao virou ordem)
        motivos = {}
        for m, f in nao:
            motivos[st_v.get((m, f), "?")] = motivos.get(st_v.get((m, f), "?"), 0) + 1
        perd = d_sem[d_sem["antes"] < 0]
        gan = d_sem[d_sem["antes"] > 0]
        PARES.append(dict(gatilho=f"{int(X * 100)}%", periodo=lab, ordens_diretas=len(d_), sem_ordem_na_virada=len(d_sem),
                          nao_virou=motivos.get("não virou em 60 pregões", 0),
                          sem_negociacao=motivos.get("virou, mas sem negociação na abertura seguinte", 0),
                          bloqueado=motivos.get("bloqueado (fundo já em carteira)", 0),
                          menor_1000=motivos.get("ordem menor que R$ 1.000", 0),
                          perda_evitada_n=len(perd), perda_evitada_rs=float(perd["antes"].sum()),
                          perda_evitada_exc=float(perd["exc"].sum()),
                          ganho_perdido_n=len(gan), ganho_perdido_rs=float(gan["antes"].sum()),
                          ganho_perdido_exc=float(gan["exc"].sum()),
                          saldo_sem_ordem_rs=float(d_sem["antes"].sum()), exc_sem_ordem=float(d_sem["exc"].sum()),
                          pos_sem_ordem=float((d_sem["antes"] > 0).mean()) if len(d_sem) else np.nan,
                          ordens_virada_sem_direta=int(len(v_) - len(v_par)),
                          direta_nos_sinais_com_virada_rs=float(d_com["antes"].sum()),
                          virada_nos_sinais_com_direta_rs=float(v_par["antes"].sum()),
                          direta_nos_sinais_com_virada_exc=float(d_com["exc"].sum()),
                          virada_nos_sinais_com_direta_exc=float(v_par["exc"].sum()),
                          n_pares=len(v_par),
                          dias_ate_virar_med=float(v_["dias_ate_virar"].mean()) if len(v_) else np.nan,
                          entrada_vs_direta=float((v_par.set_index(["md", "fundo"])["px_e"] /
                                                   d_.set_index(["md", "fundo"])["px_e"].reindex(v_par.set_index(["md", "fundo"]).index) - 1).mean())
                          if len(v_par) else np.nan))
VR = pd.DataFrame(V_ROWS)
VR.to_csv(PL / "auditoria_bloco2_virada_resumo.csv", **OPC)
PA = pd.DataFrame(PARES)
PA.to_csv(PL / "auditoria_bloco2_virada_evitadas.csv", **OPC)

# planilha de ordens (direta, virada, duas partes)
lst = []
for X in [0.15, 0.20]:
    dire, vir, duas, _ = V5[X]
    for nm, o in [("direta", dire), ("virada", vir), ("duas partes", duas)]:
        lst.append(pd.DataFrame({"Gatilho": f"{int(X * 100)}%", "Método": nm, "Fundo": o["fundo"], "Data do sinal": o["sinal"],
                                 "Data da entrada direta (chave do período)": o["data_entrada"], "Período": o["periodo"],
                                 "Preço médio de entrada (R$)": o["px_e"].round(4), "Fechamento do sinal (R$)": o["c_sinal"].round(4),
                                 "Valor aplicado (R$)": o["valor"].round(2), "Data de saída": o["data_saida"], "Motivo": o["motivo"],
                                 "Resultado antes do imposto (R$)": o["antes"].round(2), "Resultado (%)": (100 * o["pct"]).round(2),
                                 "105% CDI líquido (R$)": o["cdi"].round(2), "Excesso (R$)": o["exc"].round(2),
                                 "Maior queda abaixo da entrada (%)": (100 * o["queda"]).round(1)}))
pd.concat(lst).to_csv(PL / "auditoria_bloco2_virada_ordens.csv", **OPC)


def tab_virada(g):
    t = VR[VR["gatilho"] == g]
    return pd.DataFrame({
        "Método": t["metodo"], "Período": t["periodo"], "Ordens": t["ordens"],
        "Sinais sem ordem": t["sinais_sem_ordem"].map(lambda v: "-" if isnan(v) else int(v)),
        "Entrada vs fech. do sinal": t["preco_vs_fech_sinal"].map(pct),
        "Resultado R$": t["res"].map(brl), "Resultado %": t["res_pct"].map(pct),
        "105% CDI R$": t["cdi"].map(brl), "Excesso R$": t["exc"].map(brl), "% positivas": t["pos"].map(pct)})


def tab_virada_risco(g):
    t = VR[VR["gatilho"] == g]
    return pd.DataFrame({
        "Método": t["metodo"], "Período": t["periodo"], "Desvio padrão": t["dp"].map(pct), "Desvio das perdas": t["dp_perdas"].map(pct),
        "Pior ordem": t["pior"].map(pct), "Média dos 10% piores": t["pior10"].map(pct),
        "Queda abaixo da entrada (média)": t["queda_med"].map(pct), "Queda (pior)": t["queda_pior"].map(pct),
        "Quantil 5%": t["q05"].map(pct), "Quantil 95%": t["q95"].map(pct), "Dias médios": t["dias"].map(lambda v: br(v, 0))})


for g in ["15%", "20%"]:
    TAB[f"v_{g}"] = md_tab(tab_virada(g))
    TAB[f"vr_{g}"] = md_tab(tab_virada_risco(g))
    print(f"\n-- gatilho {g}")
    print(tab_virada(g).to_string(index=False))
    print(tab_virada_risco(g).to_string(index=False))
TAB["evitadas"] = md_tab(pd.DataFrame({
    "Gatilho": PA["gatilho"], "Período": PA["periodo"], "Ordens diretas": PA["ordens_diretas"],
    "Sem ordem na virada": PA["sem_ordem_na_virada"],
    "(não virou / sem negoc. / bloqueado / <R$ 1.000)": [f"{a} / {b} / {c} / {d}" for a, b, c, d in zip(PA["nao_virou"], PA["sem_negociacao"], PA["bloqueado"], PA["menor_1000"])],
    "Perda evitada (n)": PA["perda_evitada_n"], "Perda evitada (R$)": PA["perda_evitada_rs"].map(brl),
    "Ganho perdido (n)": PA["ganho_perdido_n"], "Ganho perdido (R$)": PA["ganho_perdido_rs"].map(brl),
    "Saldo (R$)": PA["saldo_sem_ordem_rs"].map(brl), "Excesso s/ CDI dessas (R$)": PA["exc_sem_ordem"].map(brl)}))
TAB["pares"] = md_tab(pd.DataFrame({
    "Gatilho": PA["gatilho"], "Período": PA["periodo"], "Sinais com as duas ordens": PA["n_pares"],
    "Direta nesses (R$)": PA["direta_nos_sinais_com_virada_rs"].map(brl),
    "Virada nesses (R$)": PA["virada_nos_sinais_com_direta_rs"].map(brl),
    "Excesso direta (R$)": PA["direta_nos_sinais_com_virada_exc"].map(brl),
    "Excesso virada (R$)": PA["virada_nos_sinais_com_direta_exc"].map(brl),
    "Entrada da virada vs direta (média)": PA["entrada_vs_direta"].map(pct),
    "Pregões até virar (média)": PA["dias_ate_virar_med"].map(lambda v: br(v, 1)),
    "Ordens da virada sem ordem direta": PA["ordens_virada_sem_direta"]}))
print(PA.T.to_string())

# duas partes: dinheiro parado no CDI e % sobre o valor pretendido
dp_rows = []
for X in [0.15, 0.20]:
    for lab, t_ in por_per(V5[X][2]):
        if not len(t_):
            continue
        nao2 = t_[~t_["comprou2"]]
        tot_res = float((t_["antes"] + t_["cdi_parada"]).sum())
        tot_base = float((t_["valor"] + t_["metade_parada"]).sum())
        dp_rows.append(dict(gatilho=f"{int(X * 100)}%", periodo=lab, ordens=len(t_), segunda_comprada=int(t_["comprou2"].sum()),
                            segunda_nao=len(nao2), parado=float(nao2["metade_parada"].sum()), cdi_parado=float(nao2["cdi_parada"].sum()),
                            res_com_cdi=tot_res, base=tot_base, pct_pretendido=tot_res / tot_base,
                            res_antes=float(t_["antes"].sum()), exc=float(t_["exc"].sum())))
DP = pd.DataFrame(dp_rows)
DP.to_csv(PL / "auditoria_bloco2_duas_partes.csv", **OPC)
TAB["duas"] = md_tab(pd.DataFrame({
    "Gatilho": DP["gatilho"], "Período": DP["periodo"], "Ordens": DP["ordens"], "2ª metade comprada": DP["segunda_comprada"],
    "2ª metade não comprada": DP["segunda_nao"], "Dinheiro que ficou no CDI": DP["parado"].map(brl),
    "Rendimento líq. desse CDI": DP["cdi_parado"].map(brl), "Resultado só do comprado": DP["res_antes"].map(brl),
    "Resultado + CDI parado": DP["res_com_cdi"].map(brl), "Base (comprado + parado)": DP["base"].map(brl),
    "Resultado % da base": DP["pct_pretendido"].map(pct), "Excesso R$ (só comprado)": DP["exc"].map(brl)}))
print(DP.to_string(index=False))

# ================================================================ CONFERENCIAS FINAIS (a mao)
print("\n================ CONFERENCIA 2 - duas contas refeitas a mão (lendo as planilhas brutas) ================")
ref_o = ORD[0.15][0].sort_values("data_entrada")
ref_o = ref_o[~ref_o["aberto"]]
uma = ref_o[ref_o["antes"] > 0].iloc[5]
f = uma["fundo"]
g = PR[PR["fundo"] == f].reset_index(drop=True)
ie = int(np.flatnonzero(g["data"].to_numpy("datetime64[D]") == np.datetime64(pd.Timestamp(uma["data_entrada"]), "D"))[0])
iss = int(np.flatnonzero(g["data"].to_numpy("datetime64[D]") == np.datetime64(pd.Timestamp(uma["data_saida"]), "D"))[0])
px_e, cot = float(g.loc[ie, C_AB]), int(uma["cotas"])
px_s = float(uma["px_s"])
valor, venda = cot * px_e, cot * px_s
tx = 0.0003 * (valor + venda)
incl = uma["motivo"] in (PRAZO_M, ABERTO)
av = RD[(RD["fundo"] == f) & (RD["data_base"] >= g.loc[ie, "data"]) &
        ((RD["data_base"] <= g.loc[iss, "data"]) if incl else (RD["data_base"] < g.loc[iss, "data"]))]
rend = float(av["valor (R$/cota)"].sum()) * cot
antes = venda - valor + rend - tx
print(f"ORDEM {f}: entrada {g.loc[ie, 'data']:%d/%m/%Y} abertura {px_e:.4f} x {cot} cotas = {valor:.2f}; saída {g.loc[iss, 'data']:%d/%m/%Y} "
      f"({uma['motivo']}) a {px_s:.4f} -> venda {venda:.2f}")
print(f"  valorização = {venda - valor:.2f}; rendimentos (avisos com data_base na janela: {len(av)}) = {rend:.2f}; taxas = 0,03% x ({valor:.2f}+{venda:.2f}) = {tx:.4f}")
print(f"  resultado antes do imposto = {venda - valor:.2f} + {rend:.2f} - {tx:.4f} = {antes:.4f}; programa = {uma['antes']:.4f}")
assert abs(antes - uma["antes"]) < 1e-6
# CDI na mao, a partir do csv cru
cd = pd.read_csv(PL / "cdi.csv", sep=";", decimal=",", encoding="utf-8-sig")
cd["data"] = pd.to_datetime(cd["data"], format="%d/%m/%Y")
d0, d1 = pd.Timestamp(g.loc[ie, "data"]), pd.Timestamp(g.loc[iss, "data"])
i0 = cd[cd["data"] <= d0].iloc[-1]
i1 = cd[cd["data"] <= d1].iloc[-1]
bruto = valor * (i1["indice_105_do_cdi"] / i0["indice_105_do_cdi"] - 1)
dias = (d1 - d0).days
iof = IOF[dias - 1] / 100 if 1 <= dias <= 29 else 0.0
liq = bruto * (1 - iof) * (1 - aliq_rf(dias))
print(f"CDI: índice 105% em {i0['data']:%d/%m/%Y} = {i0['indice_105_do_cdi']:.8f}; em {i1['data']:%d/%m/%Y} = {i1['indice_105_do_cdi']:.8f}; "
      f"bruto = {valor:.2f} x ({i1['indice_105_do_cdi']:.8f}/{i0['indice_105_do_cdi']:.8f} - 1) = {bruto:.4f}; {dias} dias corridos, IOF {100 * iof:.0f}%, "
      f"IR {100 * aliq_rf(dias):.1f}% -> líquido {liq:.4f}; programa = {uma['cdi']:.4f}")
assert abs(liq - uma["cdi"]) < 1e-6
print(f"  excesso = {antes:.2f} - {liq:.2f} = {antes - liq:.2f}; programa = {uma['exc']:.2f}")
print("  ASSERT PASSOU (ordem e CDI batem)")

# uma ordem de duas partes refeita a mao (a primeira com 2a metade comprada)
du = V5[0.15][2]
du = du[du["comprou2"] & (~du["aberto"])].sort_values("data_entrada").iloc[0]
F = FD[du["fundo"]]
s = int(du["s"])
st, e2 = gatilho_virada(F, s)
print(f"\nDUAS PARTES {du['fundo']}: sinal {du['sinal']:%d/%m/%Y}; 1ª metade na abertura de {F['dates'][s + 1]}; virada (E2) em j={F['dates'][e2 - 1]}: "
      f"fech {F['C'][e2 - 1]:.4f} > média 10 anteriores {F['C'][e2 - 11:e2 - 1].mean():.4f} e fech/média200(até j) - 1 = {F['C'][e2 - 1] / F['C'][e2 - 200:e2].mean() - 1:.4f} <= -0,05; "
      f"2ª metade na abertura de {F['dates'][e2]} = {F['A'][e2]:.4f}")
assert F["C"][e2 - 1] > F["C"][e2 - 11:e2 - 1].mean() and F["C"][e2 - 1] / F["C"][e2 - 200:e2].mean() - 1 <= -0.05
print("  ASSERT PASSOU (regra E2 conferida à mão para esse sinal)")

print(f"\nTempo total: {time.time() - T0:.1f} s")

with open(SCRATCH / "bloco2_tabelas.md", "w", encoding="utf-8") as fh:
    for k_, v_ in TAB.items():
        fh.write(f"<!--{k_}-->\n{v_}\n<!--/{k_}-->\n\n")
