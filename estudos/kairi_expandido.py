"""Estudo expandido do Indice de Kairi em FIIs (base B15/B20, cortes, grade, saidas, entradas).

Regras copiadas de estudos/kairi.py (aquele modulo executa tudo no import e grava CSVs de
planilhas/tecnico, por isso nao e importado). Universo, guarda de qualidade, convencoes de prazo
e de rendimento, "um fundo por vez" e medias so com operacoes fechadas sao as mesmas.

ESCOLHA = entradas ate 31/12/2022; CONFERENCIA = entradas a partir de 01/01/2023.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_expandido.py 2>&1 | tee dados/kairi_expandido.txt
"""
import random
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
np.seterr(all="ignore")
pd.set_option("display.width", 400)
pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 40)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
TEC = PL / "tecnico"
TEC.mkdir(parents=True, exist_ok=True)
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

CORTE = pd.Timestamp("2022-12-31")
INICIO_D = np.datetime64("2018-01-01", "D")
B3 = 0.0006
EXCLUIDOS = {"XPPR11", "CARE11"}
NS = [100, 150, 200, 250]
GRADE_X = [0.12, 0.15, 0.18, 0.20, 0.25]
CORTE_REND = 0.85
PRAZO_S1, PRAZO_S2 = 252, 120
LAG_REND = 126
ABERTO = "em aberto"
SAIU = "fundo saiu da bolsa"
VOLTA = "voltou à média"
CORTADO = "rendimento cortado"
PRAZO = "prazo"
ALVO = "alvo atingido"
LIMITE = "limite de perda"
FAIXAS = ["0,30–0,60", "0,60–0,75", "0,75–0,90", "acima de 0,90"]
PCT_SUF = {"%alta", "valor", "rend", "liq", "selic", "exc", "excmed", "%ganh", "menor"}


def pc(x):
    return "nd" if x is None or pd.isna(x) else f"{x * 100:.2f}%".replace(".", ",")


def nu(x, d=2):
    return "nd" if x is None or pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def imprime(df):
    d = df.copy()
    for c in d.columns:
        suf = str(c).split(".")[-1]
        if suf == "n":
            d[c] = d[c].map(lambda v: str(int(v)))
        elif suf == "preg":
            d[c] = d[c].map(lambda v: nu(v, 1))
        elif suf in PCT_SUF:
            d[c] = d[c].map(pc)
    print(d.to_string(index=False))


def primeiro(cond):
    if cond.size == 0 or not cond.any():
        return None
    return int(np.argmax(cond))


def imposto(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


# ================================================================ carga
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
RD = carregar("rendimentos")
FU = carregar("fundos")

C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG, C_REND, C_PVP = "negociou (1/0)", "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial"
C_PAT, C_VOL, C_AMO, C_VD = "patrimonio (R$)", "volume_medio_60 (R$)", "amortizacao_12m (1/0)", "volume_dia (R$)"
for c in [C_AB, C_MX, C_MN, C_FE, C_NEG, C_REND, C_PVP, C_PAT, C_VOL, C_AMO, C_VD]:
    assert c in PR.columns, c

PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
RD = RD.dropna(subset=["data_base"])
MD = MK["data"].to_numpy("datetime64[D]")
SEL = MK["selic_ano (%)"].to_numpy(float)
IM = MK["indice_mercado"].to_numpy(float)
CUM = np.concatenate([[0.0], np.cumsum(np.log1p(np.nan_to_num(SEL) / 100) / 252)])
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))
D_ALL = np.unique(PR["data"].to_numpy("datetime64[D]"))
ULT_BASE = D_ALL[-1]

# indice do mercado: kairi_mercado(d) = indice(d) / media dos 200 valores ate d-1 - 1
KM = IM / pd.Series(IM).rolling(200).mean().shift(1).to_numpy() - 1
# regime da selic: selic(d) - selic 126 pregoes antes (linhas do mercado)
_sel_s = pd.Series(SEL)
DIF = (_sel_s - _sel_s.shift(LAG_REND)).to_numpy()
REG = np.where(np.isfinite(DIF), np.where(DIF >= 0.5, "subiu", np.where(DIF <= -0.5, "caiu", "parada")),
               "sem dado")

print("== CARGA ==")
print(f"precos: {PR.shape}, fundos: {PR.fundo.nunique()}, pregoes no painel: {len(D_ALL)}; "
      f"mercado: {len(MK)} linhas ({MK.data.iloc[0].date()} a {MK.data.iloc[-1].date()})")
print(f"selic NaN: {int(np.isnan(SEL).sum())}; indice_mercado NaN: {int(np.isnan(IM).sum())}")


# ================================================================ arrays por fundo
FD = {}
for nome, g in PR.groupby("fundo", sort=False):
    dates = g["data"].to_numpy("datetime64[D]")
    n = len(dates)
    A, H, L, C = (g[c].to_numpy(float) for c in [C_AB, C_MX, C_MN, C_FE])
    R, PVP, PAT, VOL = (g[c].to_numpy(float) for c in [C_REND, C_PVP, C_PAT, C_VOL])
    VD = g[C_VD].to_numpy(float)
    AMO, NEG = g[C_AMO].to_numpy(float), g[C_NEG].to_numpy(float)

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
    mN = {N: Cs.rolling(N, min_periods=N).mean().to_numpy() for N in NS}
    kair = {N: C / mN[N] - 1 for N in NS}
    m10 = Cs.rolling(10, min_periods=10).mean().shift(1).to_numpy()

    sim = np.zeros(n, bool)
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= 0.95 * R[:-LAG_REND]

    last_pos = int(np.searchsorted(MD, dates[-1], "left"))
    FD[nome] = dict(nome=nome, n=n, dates=dates, A=A, H=H, L=L, C=C, R=R, PVP=PVP, VOL=VOL, VD=VD, NEG=NEG,
                    univ=univ, cbad=cbad, mN=mN, kair=kair, m10=m10, sim=sim,
                    aberto=last_pos >= len(MD) - 21,
                    pos=np.searchsorted(D_ALL, dates),
                    mrow=np.searchsorted(MD, dates, "right") - 1)

# painel por dia: amplitude e mediana do kairi_200 do universo
NP, NF = len(D_ALL), len(FD)
K200 = np.full((NP, NF), np.nan)
UNV = np.zeros((NP, NF), bool)
for j, F in enumerate(FD.values()):
    K200[F["pos"], j] = F["kair"][200]
    UNV[F["pos"], j] = F["univ"]
CNT_V = (UNV & np.isfinite(K200)).sum(1)
CNT_LE = (UNV & (K200 <= -0.10)).sum(1)
AMP = np.where(CNT_V > 0, CNT_LE / np.maximum(CNT_V, 1), np.nan)
MED = np.nanmedian(np.where(UNV, K200, np.nan), axis=1)

RDF = {}
for f, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f] = (bd, cs)


def rend_soma(f, D, S, incl):
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


# ================================================================ sinais (regra da kairi.py)
def sinais(F, N, X):
    n = F["n"]
    k = F["kair"][N]
    cross = np.zeros(n, bool)
    cross[1:] = (k[1:] <= -X) & (k[:-1] > -X)
    base = cross & F["univ"]
    base[:N] = False
    idx = np.flatnonzero(base)
    ent_ok = np.zeros(n, bool)
    ent_ok[:-1] = (F["NEG"][1:] == 1) & np.isfinite(F["A"][1:])
    jan = np.zeros(n, bool)
    jan[idx] = (F["cbad"][idx + 1] - F["cbad"][idx - N]) > 0
    return base & ent_ok & ~jan


SIGC = {}


def sigs(N, X):
    key = (N, X)
    if key not in SIGC:
        lst = []
        for F in FD.values():
            for s in np.flatnonzero(sinais(F, N, X)):
                lst.append((F, int(s)))
        SIGC[key] = lst
    return SIGC[key]


# ================================================================ gatilhos de entrada
def gatilho(F, s, X, regra):
    """E2: primeiro dia j em s+1..s+60 com fechamento > media dos 10 anteriores e kairi200 <= -0,05.
    E3: primeiro dia j em s+1..s+60 em que kairi200 cruza para baixo de -(X+0,05).
    Entrada na abertura de j+1 (precisa ser negociada)."""
    C, A, NEG = F["C"], F["A"], F["NEG"]
    K = F["kair"][200]
    last = F["n"] - 1
    lo, hi = s + 1, min(s + 60, last - 1)
    if lo > hi:
        return "sem", None
    js = np.arange(lo, hi + 1)
    if regra == "E2":
        cond = (C[js] > F["m10"][js]) & (K[js] <= -0.05)
    else:
        thr = -(X + 0.05)
        cond = (K[js] <= thr) & (K[js - 1] > thr)
    i = primeiro(cond)
    if i is None:
        return "sem", None
    e = int(js[i]) + 1
    if NEG[e] == 1 and np.isfinite(A[e]):
        return "ok", e
    return "inv", None


# ================================================================ simulador de saida
def fim_motivo(F):
    return ABERTO if F["aberto"] else SAIU


def sair(F, s, e, saida, N):
    """Retorna (indice da saida k, motivo, preco de saida). Convencoes da kairi.py: S1 testa a media
    ate k-1 a partir de e+1. S4-S7 testam alvo/limite a partir de e (abertura da entrada ja conhecida)."""
    last = F["n"] - 1
    C, A, H, L = F["C"], F["A"], F["H"], F["L"]
    if saida == "S2":
        k = e + PRAZO_S2
        if k <= last:
            return k, PRAZO, C[k]
        return last, fim_motivo(F), C[last]

    if saida in ("S1", "S3", "S8"):
        hz = PRAZO_S2 if saida == "S8" else PRAZO_S1
        fim = min(e + hz, last)
        if fim > e:
            mp = F["mN"][N][e:fim]                       # mp[i] = media ate k-1, k = e+1+i
            kv = primeiro(H[e + 1:fim + 1] >= mp)
            kc = None
            if saida == "S3" and np.isfinite(F["R"][e]):
                kc = primeiro(F["R"][e + 1:fim + 1] <= CORTE_REND * F["R"][e])
            if kc is not None and (kv is None or kc <= kv):
                k = e + 1 + kc
                return k, CORTADO, A[k]
            if kv is not None:
                k = e + 1 + kv
                return k, VOLTA, max(A[k], mp[kv])
        if e + hz <= last:
            return e + hz, PRAZO, C[e + hz]
        return last, fim_motivo(F), C[last]

    # S4 a S7: alvo e limite a partir do dia da entrada
    fim = min(e + PRAZO_S1, last)
    Hh, Ll, Aa = H[e:fim + 1], L[e:fim + 1], A[e:fim + 1]
    ent = A[e]
    if saida in ("S4", "S5"):
        if saida == "S4":
            m200 = F["mN"][200][s]
            tgt = ent + 0.5 * (m200 - ent)
        else:
            tgt = 1.10 * ent
        if np.isfinite(tgt):
            i = primeiro(Hh >= tgt)
            if i is not None:
                return e + i, ALVO, max(Aa[i], tgt)
    else:
        stop = (0.80 if saida == "S6" else 0.70) * ent
        mkf = np.full(fim - e + 1, np.nan)               # mkf[i] = media ate k-1, k = e+i
        if fim > e:
            mkf[1:] = F["mN"][N][e:fim]
        mm = np.zeros(fim - e + 1, bool)
        mm[1:] = Hh[1:] >= mkf[1:]
        stp = Ll <= stop
        i = primeiro(stp | mm)
        if i is not None:
            if stp[i]:                                   # limite e alvo no mesmo dia: vale o limite
                return e + i, LIMITE, min(Aa[i], stop)
            return e + i, VOLTA, max(Aa[i], mkf[i])
    if e + PRAZO_S1 <= last:
        return e + PRAZO_S1, PRAZO, C[e + PRAZO_S1]
    return last, fim_motivo(F), C[last]


# ================================================================ atributos do sinal (so dados ate d)
def group_amp(v):
    if not np.isfinite(v):
        return "sem dado"
    return "queda geral" if v >= 0.15 else "intermediária" if v >= 0.05 else "queda isolada"


def group_km(v):
    if not np.isfinite(v):
        return "sem dado"
    return "<= -0,05" if v <= -0.05 else "-0,05 a 0" if v <= 0 else "> 0"


def group_qrel(v):
    if not np.isfinite(v):
        return "sem dado"
    return "<= -0,15" if v <= -0.15 else "-0,15 a -0,08" if v <= -0.08 else "> -0,08"


def group_pvp(v):
    if not np.isfinite(v):
        return "sem dado"
    return FAIXAS[0] if v < 0.60 else FAIXAS[1] if v < 0.75 else FAIXAS[2] if v < 0.90 else FAIXAS[3]


def group_ordem(v):
    if not np.isfinite(v):
        return "sem dado"
    return "500–2.000" if v < 2000 else "2.000–4.000" if v < 4000 else "4.000 ou mais"


FEATC = {}


def feats(F, s):
    key = (F["nome"], s)
    if key in FEATC:
        return FEATC[key]
    p, r = F["pos"][s], F["mrow"][s]
    amp, med = AMP[p], MED[p]
    k200 = F["kair"][200][s]
    km = KM[r] if r >= 0 else np.nan
    reg = REG[r] if r >= 0 else "sem dado"
    ordv = 0.02 * F["VOL"][s]
    rs = F["R"][s] * 12 / F["C"][s]
    sl = SEL[r] / 100 * 0.825 if r >= 0 else np.nan
    rs_g = "sem dado" if not (np.isfinite(rs) and np.isfinite(sl)) else \
        ("acima da Selic líquida" if rs > sl else "abaixo")
    out = dict(amplitude=group_amp(amp), kairi_mercado=group_km(km), queda_relativa=group_qrel(k200 - med),
               faixa_pvp=group_pvp(F["PVP"][s]), tipo=TIPO.get(F["nome"], "sem tipo"), selic_regime=reg,
               faixa_ordem=group_ordem(ordv), rendimento_sobre_preco=rs_g,
               amp_v=amp, med_v=med, k200_v=k200, km_v=km, ord_v=ordv)
    FEATC[key] = out
    return out


def operar(F, s, e, saida, N):
    k, mot, px = sair(F, s, e, saida, N)
    ent = float(F["A"][e])
    D, S = F["dates"][e], F["dates"][k]
    val = px / ent - 1
    incl = mot in (PRAZO, ABERTO)
    rend = rend_soma(F["nome"], D, S, incl) / ent
    liq = val - B3 - 0.20 * max(val - B3, 0) + rend
    ie = np.searchsorted(MD, D, "left")
    isx = np.searchsorted(MD, S, "left")
    dias = int((S - D) / np.timedelta64(1, "D"))
    selic = (np.exp(CUM[isx] - CUM[ie]) - 1) * (1 - imposto(dias))
    menor = float(F["L"][e:k + 1].min() / ent - 1)
    desc = bool(F["cbad"][k + 1] - F["cbad"][e + 1] > 0)
    r = dict(fundo=F["nome"], sinal=pd.Timestamp(F["dates"][s]), entrada=pd.Timestamp(D),
             saida_data=pd.Timestamp(S), motivo=mot, pregoes=int(k - e), preco_entrada=ent,
             preco_saida=float(px), valorizacao=val, rendimento=rend, liquido=liq, selic=selic,
             excesso=liq - selic, menor_preco=menor, descartada=desc, dias=dias,
             k_idx=int(k), s_idx=int(s), e_idx=int(e), pvp_sinal=float(F["PVP"][s]))
    r.update(feats(F, s))
    return r


GER = {}


def gerar(N, X, mant, saida, regra="E1"):
    """Operacoes de uma configuracao, com 'um fundo por vez' (ordem de entrada) e contadores."""
    key = (N, X, mant, saida, regra)
    if key in GER:
        return GER[key]
    cont = dict(considerados=0, sem_gatilho=0, entrada_invalida=0, bloqueados=0)
    cands = []
    for F, s in sigs(N, X):
        if mant == "sim" and not F["sim"][s]:
            continue
        if F["dates"][s + 1] < INICIO_D:
            continue
        cont["considerados"] += 1
        if regra == "E1":
            e = s + 1
        else:
            st, e = gatilho(F, s, X, regra)
            if st == "sem":
                cont["sem_gatilho"] += 1
                continue
            if st == "inv":
                cont["entrada_invalida"] += 1
                continue
        cands.append((F, s, e))
    cands.sort(key=lambda t: (t[0]["nome"], t[2]))
    busy, recs = {}, []
    for F, s, e in cands:
        if busy.get(F["nome"], -1) > e - 1:
            cont["bloqueados"] += 1
            continue
        r = operar(F, s, e, saida, N)
        busy[F["nome"]] = r["k_idx"]
        recs.append(r)
    ops = pd.DataFrame(recs)
    ops["N"], ops["X"], ops["mantido"], ops["saida"], ops["regra"] = N, X, mant, saida, regra
    ops["fechada"] = (ops["motivo"] != ABERTO) & (~ops["descartada"])
    ops["periodo"] = np.where(ops["entrada"] <= CORTE, "ESCOLHA", "CONFERENCIA")
    ops["ano"] = ops["entrada"].dt.year
    GER[key] = (ops, cont)
    return GER[key]


# ================================================================ estatisticas e formatos
def stats(d):
    if len(d) == 0:
        return dict(n=0, preg=np.nan, alta=np.nan, val=np.nan, rend=np.nan, liq=np.nan, selic=np.nan,
                    exc=np.nan, exc_med=np.nan, pos=np.nan, menor=np.nan)
    return dict(n=int(len(d)), preg=float(d.pregoes.mean()), alta=float((d.valorizacao > 0).mean()),
                val=float(d.valorizacao.mean()), rend=float(d.rendimento.mean()),
                liq=float(d.liquido.mean()), selic=float(d.selic.mean()), exc=float(d.excesso.mean()),
                exc_med=float(d.excesso.median()), pos=float((d.excesso > 0).mean()),
                menor=float(d.menor_preco.mean()))


def bloco(d_e, d_c):
    out = {}
    for pref, d in (("E.", d_e), ("C.", d_c)):
        st = stats(d)
        out[pref + "n"] = st["n"]
        out[pref + "preg"] = st["preg"]
        out[pref + "%alta"] = st["alta"]
        out[pref + "valor"] = st["val"]
        out[pref + "rend"] = st["rend"]
        out[pref + "liq"] = st["liq"]
        out[pref + "selic"] = st["selic"]
        out[pref + "exc"] = st["exc"]
        out[pref + "excmed"] = st["exc_med"]
        out[pref + "%ganh"] = st["pos"]
        out[pref + "menor"] = st["menor"]
    return out


def por_periodo(ops):
    fe = ops[ops.fechada]
    return fe[fe.periodo == "ESCOLHA"], fe[fe.periodo == "CONFERENCIA"]


def tabela_dim(ops, col, ordem, titulo):
    """Uma linha por grupo; ESCOLHA e CONFERENCIA lado a lado. Confere soma dos n com o total."""
    print(f"\n{titulo}")
    rows = []
    fe = ops[ops.fechada]
    for g in ordem:
        m = fe[col] == g
        rows.append(dict(grupo=str(g), **bloco(fe[m & (fe.periodo == "ESCOLHA")],
                                               fe[m & (fe.periodo == "CONFERENCIA")])))
    df = pd.DataFrame(rows)
    tot_e = int((fe.periodo == "ESCOLHA").sum())
    tot_c = int((fe.periodo == "CONFERENCIA").sum())
    print(f"   soma n grupos: ESCOLHA {int(df['E.n'].sum())} de {tot_e} | CONFERENCIA {int(df['C.n'].sum())} de {tot_c}"
          + ("  (OK)" if df["E.n"].sum() == tot_e and df["C.n"].sum() == tot_c else "  (DIFERENCA)"))
    imprime(df)


def resumo_linha(label, d_e, d_c):
    return dict(grupo=label, **bloco(d_e, d_c))


# ================================================================ BASE: B15 e B20
print("\n== BASE B15 (N 200, X 0,15, mantido sim, S1) e B20 (N 200, X 0,20) ==")
t0 = time.time()
OPS15, C15 = gerar(200, 0.15, "sim", "S1", "E1")
OPS20, C20 = gerar(200, 0.20, "sim", "S1", "E1")
print(f"B15: considerados {C15['considerados']}, bloqueados (fundo ocupado) {C15['bloqueados']}, "
      f"operacoes {len(OPS15)}, descartadas {int(OPS15.descartada.sum())}, em aberto {int((OPS15.motivo == ABERTO).sum())}")
print(f"B20: considerados {C20['considerados']}, bloqueados (fundo ocupado) {C20['bloqueados']}, "
      f"operacoes {len(OPS20)}, descartadas {int(OPS20.descartada.sum())}, em aberto {int((OPS20.motivo == ABERTO).sum())}")
print(f"(tempo base: {time.time() - t0:.1f} s)")

# ---------------- conferencia 2: reproduz o estudo anterior
print("\n== CONFERENCIA 2 - reproducao do estudo anterior (S1) ==")
alvo = {"B15": (OPS15, (161, 0.0656, 147, 0.0474)), "B20": (OPS20, (94, 0.1205, 66, 0.0621))}
ok_rep = True
for nome, (ops, (nE, eE, nC, eC)) in alvo.items():
    fe, fc = por_periodo(ops)
    st_e, st_c = stats(fe), stats(fc)
    okk = (st_e["n"] == nE and round(st_e["exc"], 4) == eE and st_c["n"] == nC and round(st_c["exc"], 4) == eC)
    ok_rep &= okk
    print(f"{nome}: ESCOLHA n {st_e['n']} (esperado {nE}), excesso {pc(st_e['exc'])} (esperado {eE * 100:.2f}%) | "
          f"CONFERENCIA n {st_c['n']} (esperado {nC}), excesso {pc(st_c['exc'])} (esperado {eC * 100:.2f}%) -> "
          f"{'REPRODUZ' if okk else 'NAO REPRODUZ'}")
if not ok_rep:
    print("PARADA: a base nao reproduz o estudo anterior. Diferenca acima; nada mais foi calculado.")
    sys.exit(1)

# ================================================================ PARTE 1
print("\n" + "=" * 120)
print("PARTE 1 - BASE CORTADA POR UMA DIMENSAO DE CADA VEZ (B15 e B20, saida S1)")
print("=" * 120)
ORD = dict(
    amplitude=["queda geral", "intermediária", "queda isolada", "sem dado"],
    kairi_mercado=["<= -0,05", "-0,05 a 0", "> 0", "sem dado"],
    queda_relativa=["<= -0,15", "-0,15 a -0,08", "> -0,08", "sem dado"],
    faixa_pvp=FAIXAS + ["sem dado"],
    tipo=sorted(set(TIPO.values())) + ["sem tipo"],
    selic_regime=["subiu", "parada", "caiu", "sem dado"],
    faixa_ordem=["500–2.000", "2.000–4.000", "4.000 ou mais", "sem dado"],
    rendimento_sobre_preco=["acima da Selic líquida", "abaixo", "sem dado"],
    ano=list(range(2018, 2027)),
)
DIMS = [("amplitude", "amplitude de queda (fração do universo com kairi200 <= -0,10)"),
        ("kairi_mercado", "kairi do índice de mercado"),
        ("queda_relativa", "queda relativa (kairi200 do fundo − mediana do universo)"),
        ("faixa_pvp", "faixa de preço sobre valor patrimonial no sinal"),
        ("tipo", "tipo do fundo (fundos.csv)"),
        ("selic_regime", "regime da Selic (126 pregões)"),
        ("faixa_ordem", "tamanho da ordem (2% do volume médio 60)"),
        ("rendimento_sobre_preco", "rendimento em vigor×12/preço vs Selic líquida"),
        ("ano", "ano de entrada")]
for nome, ops in [("B15", OPS15), ("B20", OPS20)]:
    for col, titulo in DIMS:
        tabela_dim(ops, col, ORD[col], f"-- {nome} por {titulo}")

# ================================================================ PARTE 2
print("\n" + "=" * 120)
print("PARTE 2 - GRADE EM VOLTA DA BASE (saida S1)")
print("=" * 120)
linhas2 = []
for N in NS:
    for X in GRADE_X:
        for mant in ["sim", "qualquer"]:
            ops, _ = gerar(N, X, mant, "S1", "E1")
            fe, fc = por_periodo(ops)
            row = dict(N=str(N), X=nu(X, 2), mantido=mant)
            row.update(bloco(fe, fc))
            linhas2.append(row)
G2 = pd.DataFrame(linhas2)
G2.to_csv(TEC / "kairi_exp_grade.csv", **OPC)
print("\n-- Grade 40 linhas (E. = ESCOLHA, C. = CONFERÊNCIA)")
imprime(G2)
dois = int(((G2["E.exc"] > 0) & (G2["C.exc"] > 0)).sum())
e_pos = int((G2["E.exc"] > 0).sum())
c_pos = int((G2["C.exc"] > 0).sum())
rho_all = G2["E.exc"].rank().corr(G2["C.exc"].rank())
ok30 = (G2["E.n"] >= 30) & (G2["C.n"] >= 30)
rho30 = G2.loc[ok30, "E.exc"].rank().corr(G2.loc[ok30, "C.exc"].rank())
print(f"\nlinhas com excesso medio > 0 nos DOIS periodos: {dois} de 40 (ESCOLHA: {e_pos}; CONFERENCIA: {c_pos})")
print(f"correlacao de postos (pandas rank) ESCOLHA x CONFERENCIA, 40 linhas: {nu(rho_all, 3)}")
print(f"  mesma correlacao so com n >= 30 nos dois periodos ({int(ok30.sum())} linhas): {nu(rho30, 3)}")

# ================================================================ PARTE 3
print("\n" + "=" * 120)
print("PARTE 3 - SAIDAS ALTERNATIVAS (B15 e B20, entrada E1)")
print("=" * 120)
MOTIVOS = [VOLTA, PRAZO, ALVO, LIMITE, CORTADO, SAIU, ABERTO]
SAIDAS = [("S1", "volta à média (referência)"), ("S2", "prazo fixo 120"),
          ("S3", "volta à média ou corte de rendimento"), ("S4", "meio caminho (alvo)"),
          ("S5", "alvo fixo +10%"), ("S6", "volta à média + limite -20%"),
          ("S7", "volta à média + limite -30%"), ("S8", "volta à média, prazo 120")]
for nome, X in [("B15", 0.15), ("B20", 0.20)]:
    print(f"\n-- {nome}: uma linha por saída")
    rows, motivos = [], []
    for sid, desc in SAIDAS:
        ops, cont = gerar(200, X, "sim", sid, "E1")
        fe, fc = por_periodo(ops)
        rows.append(dict(saida=f"{sid} {desc}", **bloco(fe, fc)))
        cnt = {m: int((ops.motivo == m).sum()) for m in MOTIVOS}
        cnt_desc = int(ops.descartada.sum())
        motivos.append(dict(saida=sid, **{m: cnt[m] for m in MOTIVOS}, descartadas=cnt_desc))
    imprime(pd.DataFrame(rows).rename(columns={"saida": "grupo"}))
    print(f"   contagem por motivo de saída (todas as operações da configuração, inclui em aberto e descartadas):")
    print(pd.DataFrame(motivos).to_string(index=False))

# ================================================================ PARTE 4
print("\n" + "=" * 120)
print("PARTE 4 - ENTRADA COM CONFIRMAÇÃO (saída S1)")
print("=" * 120)
REG4 = [("E1", "referência: abertura seguinte ao cruzamento"), ("E2", "esperar virar (até 60 pregões)"),
        ("E3", "segundo degrau (até 60 pregões)")]
for nome, X in [("B15", 0.15), ("B20", 0.20)]:
    print(f"\n-- {nome}")
    rows, contagens = [], []
    for reg, desc in REG4:
        ops, cont = gerar(200, X, "sim", "S1", reg)
        fe, fc = por_periodo(ops)
        rows.append(dict(entrada=f"{reg} {desc}", **bloco(fe, fc)))
        nao = cont["sem_gatilho"] + cont["entrada_invalida"] + cont["bloqueados"]
        contagens.append(dict(regra=reg, sinais=cont["considerados"], operacoes=len(ops),
                              sem_gatilho=cont["sem_gatilho"], entrada_invalida=cont["entrada_invalida"],
                              bloqueados_fundo_ocupado=cont["bloqueados"], nao_viraram_total=nao))
    imprime(pd.DataFrame(rows).rename(columns={"entrada": "grupo"}))
    print("   sinais que não viraram operação:")
    print(pd.DataFrame(contagens).to_string(index=False))

# ================================================================ PARTE 5
print("\n" + "=" * 120)
print("PARTE 5 - COMBINAÇÕES DEFINIDAS ANTES (B15 e B20, saída S1)")
print("=" * 120)
COMBOS = [
    ("(a) só queda geral", lambda o: o.amplitude == "queda geral"),
    ("(b) só queda isolada", lambda o: o.amplitude == "queda isolada"),
    ("(c) queda geral + pvp 0,30–0,75", lambda o: (o.amplitude == "queda geral") & o.faixa_pvp.isin(FAIXAS[:2])),
    ("(d) queda geral + pvp >= 0,75", lambda o: (o.amplitude == "queda geral") & o.faixa_pvp.isin(FAIXAS[2:])),
    ("(e) tudo menos queda isolada", lambda o: o.amplitude != "queda isolada"),
]
for nome, ops in [("B15", OPS15), ("B20", OPS20)]:
    print(f"\n-- {nome}")
    rows = []
    for lab, fn in COMBOS:
        sub = ops[fn(ops)]
        fe, fc = por_periodo(sub)
        rows.append(dict(combo=lab, **bloco(fe, fc)))
    imprime(pd.DataFrame(rows).rename(columns={"combo": "grupo"}))
    for lab, fn in [COMBOS[0], COMBOS[4]]:
        sub = ops[fn(ops)]
        print(f"   por ano de entrada - {lab}:")
        rows_a = []
        for ano in range(2018, 2027):
            fe = sub[sub.fechada & (sub.ano == ano)]
            rows_a.append(dict(grupo=str(ano), **bloco(fe[fe.periodo == "ESCOLHA"], fe[fe.periodo == "CONFERENCIA"])))
        imprime(pd.DataFrame(rows_a))

# ================================================================ PARTE 6
print("\n" + "=" * 120)
print("PARTE 6 - CONFERÊNCIA DAS PERDAS GRANDES (B15)")
print("=" * 120)
fe15 = OPS15[OPS15.fechada].sort_values("excesso").reset_index(drop=True)
piores = fe15.head(12)
cols6 = ["fundo", "sinal", "entrada", "saida_data", "motivo", "preco_entrada", "menor_preco", "preco_saida",
         "valorizacao", "rendimento", "amplitude", "tipo_fundo"]
p6 = piores.copy()
p6["tipo_fundo"] = p6["tipo"]
p6["sinal"] = p6.sinal.dt.strftime("%d/%m/%Y")
p6["entrada"] = p6.entrada.dt.strftime("%d/%m/%Y")
p6["saida_data"] = p6.saida_data.dt.strftime("%d/%m/%Y")
p6["excesso"] = p6.excesso
print("\n-- 12 piores operações da B15 por excesso (fechadas):")
imprime(p6[cols6 + ["excesso"]].rename(columns={"valorizacao": "valor", "rendimento": "rend",
                                                 "menor_preco": "menor", "excesso": "exc"}).assign(
    preco_entrada=lambda d: d.preco_entrada.map(lambda v: nu(v, 4)),
    preco_saida=lambda d: d.preco_saida.map(lambda v: nu(v, 4))))

alvo6 = []
for f in ["CACR11", "MGHT11", "MCEM11"]:
    sub = fe15[fe15.fundo == f]
    if len(sub):
        alvo6.append((f, sub.iloc[0]))
    else:
        print(f"\n{f}: sem operação fechada na B15")
for i, r in piores.head(3).iterrows():
    if r["fundo"] not in [a[0] for a in alvo6]:
        alvo6.append((f"{r['fundo']} (top {i + 1})", r))
    else:
        alvo6.append((f"{r['fundo']} (top {i + 1}, repetido)", r))

print("\n-- Fechamentos e volumes em torno da MAIOR queda de um dia dentro de cada operação")
print("   (queda = fechamento(t)/fechamento(t-1) - 1, para t de e+1 até a saída k; janela de 3 pregões antes e depois)")
for rotulo, r in alvo6:
    F = FD[r["fundo"]]
    e, k = int(r["e_idx"]), int(r["k_idx"])
    print(f"\n### {rotulo}: operação sinal {r['sinal'].date()} entrada {r['entrada'].date()} "
          f"saída {r['saida_data'].date()} ({r['motivo']}), excesso {pc(r['excesso'])}, "
          f"amplitude {r['amplitude']}")
    ts = np.arange(e + 1, k + 1)
    if len(ts) == 0:
        print("   operação sem dia de permanência; nada a checar")
        continue
    ret = F["C"][ts] / F["C"][ts - 1] - 1
    tq = int(ts[int(np.argmin(ret))])
    print(f"   maior queda diária dentro da operação: {pc(float(ret.min()))} em {F['dates'][tq]}")
    lo, hi = max(0, tq - 3), min(F["n"] - 1, tq + 3)
    rows = []
    for t in range(lo, hi + 1):
        marca = ""
        if t == tq:
            marca = "<< maior queda"
        if t == e:
            marca += " [entrada]"
        if t == k:
            marca += " [saída]"
        rows.append(dict(data=pd.Timestamp(F["dates"][t]).strftime("%d/%m/%Y"),
                         fechamento=nu(F["C"][t], 4), abertura=nu(F["A"][t], 4), minima=nu(F["L"][t], 4),
                         volume_dia_R=f"{F['VD'][t]:,.0f}".replace(",", "."), negociou=int(F["NEG"][t]),
                         marca=marca.strip()))
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"   volume_medio_60 (R$) medio nesta janela: "
          f"{F['VOL'][lo:hi + 1].mean():,.0f}".replace(",", "."))
    print(f"   ultimo preco do fundo: {F['dates'][-1]} (base vai ate {ULT_BASE}): "
          f"{'tem linha de preço até o fim da base' if F['dates'][-1] == ULT_BASE else 'NÃO tem linha até o fim da base'}")

# ================================================================ CONFERENCIAS
print("\n" + "=" * 120)
print("CONFERÊNCIAS OBRIGATÓRIAS")
print("=" * 120)
print(f"1) roda sem erro; tempo até aqui: {time.time() - T0:.1f} s")
print("2) reprodução do estudo anterior: ver bloco CONFERENCIA 2 acima (REPRODUZ para B15 e B20)")

print("3) soma dos n nos grupos das tabelas da Parte 1 = n total da base: ver linhas 'soma n grupos' acima")
ok3 = True
print("4) confirmação de que as medidas usam só dados até o dia do sinal (naive com dados truncados):")
PRG = {nome: dict(dates=g["data"].to_numpy("datetime64[D]"), C=g[C_FE].to_numpy(float),
                  PAT=g[C_PAT].to_numpy(float), VOL=g[C_VOL].to_numpy(float), R=g[C_REND].to_numpy(float),
                  PVP=g[C_PVP].to_numpy(float), AMO=g[C_AMO].to_numpy(float))
       for nome, g in PR.groupby("fundo", sort=False)}
MD64 = MD


def univ_row(G, i, nome):
    return bool((G["PAT"][i] >= 50e6) and (G["VOL"][i] >= 25000) and (G["R"][i] > 0) and (G["AMO"][i] == 0)
                and (0.30 <= G["PVP"][i] <= 3.0) and nome not in EXCLUIDOS)


def naive(d64):
    """Recalcula amplitude, mediana e kairi200 de cada fundo e o indice de mercado so com dados ate d."""
    ks, us = {}, {}
    for nome, G in PRG.items():
        t = np.searchsorted(G["dates"], d64, "right")
        if t == 0 or G["dates"][t - 1] != d64:
            continue
        i = t - 1
        ks[nome] = G["C"][i] / G["C"][t - 200:t].mean() - 1 if t >= 200 else np.nan
        us[nome] = univ_row(G, i, nome)
    valid = [ks[n] for n in ks if us[n] and np.isfinite(ks[n])]
    amp = float(np.mean([k <= -0.10 for k in valid])) if valid else np.nan
    med = float(np.median(valid)) if valid else np.nan
    t = np.searchsorted(MD64, d64, "right")
    km = IM[t - 1] / IM[t - 201:t - 1].mean() - 1 if t >= 201 else np.nan
    reg = "sem dado"
    if t >= LAG_REND + 1:
        dif = SEL[t - 1] - SEL[t - 1 - LAG_REND]
        if np.isfinite(dif):
            reg = "subiu" if dif >= 0.5 else "caiu" if dif <= -0.5 else "parada"
    return ks, amp, med, km, reg


rng = random.Random(7)
amostra = rng.sample(list(OPS15.itertuples()), 20) + rng.sample(list(OPS20.itertuples()), 20)
difs = []
for op in amostra:
    d64 = np.datetime64(op.sinal, "D")
    ks, amp, med, km, reg = naive(d64)
    f = op.fundo
    pair = [("amp", amp, op.amp_v), ("med", med, op.med_v), ("k200", ks.get(f, np.nan), op.k200_v),
            ("km", km, op.km_v), ("ord", 0.02 * PRG[f]["VOL"][np.searchsorted(PRG[f]["dates"], d64)], op.ord_v)]
    for nm, a, b in pair:
        if not (np.isclose(a, b, equal_nan=True, rtol=1e-9, atol=1e-12)):
            difs.append((f, str(op.sinal.date()), nm, a, b))
    if reg != op.selic_regime:
        difs.append((f, str(op.sinal.date()), "regime", reg, op.selic_regime))
print(f"   amostra de {len(amostra)} sinais (20 B15 + 20 B20): divergências entre naive (dados até d) e vetorizado: {len(difs)}")
for x in difs[:10]:
    print("   ", x)
print("   os cortes amplitude, kairi_mercado, queda_relativa, selic_regime e faixa_ordem usam só dados até d:")
print("   - amplitude/mediana: kairi200 de cada fundo com janela até d (kair[N] do dia d) e universo medido em d;")
print("   - kairi_mercado: indice(d) / media dos 200 valores ate d-1; selic_regime: selic(d) - selic 126 linhas antes;")
print("   - queda_relativa e faixa_ordem: kairi200 do fundo em d e volume_medio_60 em d.")
print("   (todas as janelas usam linhas com data <= d; o naive acima confirma numericamente)")

# ================================================================ GRAVACAO
OUT = pd.concat([OPS15.assign(config="B15"), OPS20.assign(config="B20")], ignore_index=True)
OUT = OUT.drop(columns=["k_idx", "s_idx", "e_idx", "amp_v", "med_v", "k200_v", "km_v", "ord_v"], errors="ignore")
OUT.to_csv(TEC / "kairi_exp_operacoes.csv", **OPC)
print(f"\ngravados: planilhas/tecnico/kairi_exp_operacoes.csv ({len(OUT)} linhas), "
      f"planilhas/tecnico/kairi_exp_grade.csv ({len(G2)} linhas)")
print(f"Tempo total: {time.time() - T0:.1f} s")
