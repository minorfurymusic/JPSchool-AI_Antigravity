"""Regra de cruzamento de médias (ideia do dono) comparada com a S1 (volta à média, prazo de 252).

As ENTRADAS são as mesmas de kairi_saidas.py / kairi_escada.py (carteiras A, B e C). As funções de entrada,
conta, imposto, Selic, guarda de qualidade e métricas foram COPIADAS de estudos/kairi_escada.py (ele executa
tudo no import e regrava arquivos, por isso não é importado).

Regra nova (G1..G9):
  1. ARMAR: primeiro pregão k depois da entrada (até 252 pregões) com máxima(k) >= MM200(k), MM200(k) = média
     dos 200 fechamentos até k-1. Não vende no dia. Pc = max(abertura(k), MM200(k)).
  2. Depois de armada, em cada k2 > k (nesta ordem no mesmo dia):
     a. dado suspeito em k2: sai no fechamento de k2-1 ('dado suspeito')
     b. PISO (se usar_piso): mínima(k2) <= Pc*(1-folga) -> vende min(abertura(k2), Pc*(1-folga))
     c. CRUZAMENTO: mm_c(k2-1) < mm_l(k2-1) e mm_c(k2-2) >= mm_l(k2-2), com k2-1 > k -> vende abertura(k2)
     d. TETO (só G9): máxima(k2) >= P (pico 252 na entrada) -> vende max(abertura(k2), P)
  3. Nunca armada: reserva igual à S1 (prazo 252 no fechamento, fundo saiu da bolsa, dado suspeito, em aberto).
     Armada não tem prazo.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_cruzamento.py > dados/kairi_cruzamento.txt 2>&1
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

np.seterr(all="ignore")
pd.set_option("display.width", 500)
pd.set_option("display.max_columns", 200)
pd.set_option("display.max_colwidth", 80)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
TEC = PL / "tecnico"
TEC.mkdir(parents=True, exist_ok=True)
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y", na_rep="nd")

INICIO_D = np.datetime64("2018-01-01", "D")
CORTE_22 = pd.Timestamp("2022-12-31")
CONF_INI = pd.Timestamp("2023-01-01")
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
AMP_LIM = 0.15
AMP_K = -0.10
CARTEIRAS = {"A": dict(X=0.15, amp=False), "B": dict(X=0.20, amp=False), "C": dict(X=0.15, amp=True)}
VOLTA = "volta à média"
PRAZO_M = "prazo"
SAIU = "fundo saiu da bolsa"
GUARDA = "dado suspeito"
ABERTO = "em aberto"
PISO = "voltou ao preço do cruzamento"
CRUZ = "média curta cruzou para baixo"
TETO = "teto Fibonacci 100%"
MOTIVOS = [VOLTA, PISO, CRUZ, TETO, PRAZO_M, SAIU, GUARDA, ABERTO]

GRUPOS = [
    dict(sig="G1", c=7, l=21, usar=True, f=0.00, teto=False),
    dict(sig="G2", c=7, l=21, usar=True, f=0.03, teto=False),
    dict(sig="G3", c=7, l=21, usar=True, f=0.05, teto=False),
    dict(sig="G4", c=7, l=21, usar=False, f=0.00, teto=False),
    dict(sig="G5", c=5, l=20, usar=True, f=0.03, teto=False),
    dict(sig="G6", c=10, l=30, usar=True, f=0.03, teto=False),
    dict(sig="G7", c=10, l=30, usar=False, f=0.00, teto=False),
    dict(sig="G8", c=21, l=50, usar=True, f=0.03, teto=False),
    dict(sig="G9", c=7, l=21, usar=True, f=0.03, teto=True),
]
G_BY = {g["sig"]: g for g in GRUPOS}


def nome_regra(g):
    piso = f"piso no preço do cruzamento (folga {100 * g['f']:.0f}%)" if g["usar"] else "sem piso"
    t = "; teto Fibonacci 100%" if g["teto"] else ""
    return f"Armada na MM200; {piso}; cruzamento MM{g['c']}/MM{g['l']}{t}"


NOME_R = {"S1": "Volta à média (prazo de 252 pregões no fechamento)"}
NOME_R.update({g["sig"]: nome_regra(g) for g in GRUPOS})
SIGS = ["S1"] + [g["sig"] for g in GRUPOS]


# ---------------------------------------------------------------- formatacao (copiada)
def isnan(x):
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


def br(x, d=2):
    if isnan(x):
        return "nd"
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x, d=0):
    return "nd" if isnan(x) else "R$ " + br(x, d)


def fmt_val(key, v):
    if isinstance(v, str):
        return v
    if isinstance(v, (bool, np.bool_)):
        return "sim" if v else "não"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isnan(v):
        return "nd"
    if "(R$)" in key:
        return brl(v)
    if "(pontos)" in key:
        return br(v, 1) + " pp"
    if "%" in key:
        return br(v, 1) + "%"
    return br(v, 1)


def tabela(df):
    cel = pd.DataFrame(index=df.index, columns=df.columns, dtype=object)
    for col in df.columns:
        cel[col] = [fmt_val(col, v) for v in df[col]]
    print(cel.to_string())


def dt(x):
    return pd.Timestamp(x).strftime("%d/%m/%Y")


# ---------------------------------------------------------------- carga (copiada de kairi_escada.py)
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
RD_BRUTO = carregar("rendimentos")
FU = carregar("fundos")

C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG = "negociou (1/0)"
C_REND, C_PVP, C_PAT = "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL, C_AMO = "volume_medio_60 (R$)", "amortizacao_12m (1/0)"
C_VP = "valor_patrimonial_cota"
for c in [C_AB, C_MX, C_MN, C_FE, C_NEG, C_REND, C_PVP, C_PAT, C_VOL, C_AMO, C_VP]:
    assert c in PR.columns, c
assert "valor (R$/cota)" in RD_BRUTO.columns

dups = int(PR.duplicated(["fundo", "data"]).sum())
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
print(f"linhas duplicadas (fundo, data) em precos removidas: {dups}")
RD_NA = int(RD_BRUTO["data_base"].isna().sum())
RD = RD_BRUTO.dropna(subset=["data_base"]).reset_index(drop=True)
print(f"rendimentos com data_base NaN (removidos): {RD_NA}")

MK_DATAS = MK["data"]
MD = MK_DATAS.to_numpy("datetime64[D]")
TS = list(MK_DATAS)
NM = len(MD)
assert len(set(MD)) == NM
SEL = MK["selic_ano (%)"].to_numpy(float)
CUM = np.concatenate([[0.0], np.cumsum(np.log1p(np.nan_to_num(SEL) / 100) / 252)])
I0 = int(np.searchsorted(MD, INICIO_D))
assert TS[I0] == pd.Timestamp("2018-01-02"), TS[I0]
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))


def aliq_rf(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


# ---------------------------------------------------------------- arrays por fundo (copiado)
FD = {}
for nome, g in PR.groupby("fundo", sort=False):
    dates = g["data"].to_numpy("datetime64[D]")
    n = len(dates)
    A = g[C_AB].to_numpy(float)
    H = g[C_MX].to_numpy(float)
    L = g[C_MN].to_numpy(float)
    C = g[C_FE].to_numpy(float)
    R = g[C_REND].to_numpy(float)
    PVP = g[C_PVP].to_numpy(float)
    VOL = g[C_VOL].to_numpy(float)
    AMO = g[C_AMO].to_numpy(float)
    NEG = g[C_NEG].to_numpy(float)
    PAT = g[C_PAT].to_numpy(float)
    VP = g[C_VP].to_numpy(float)

    univ = (PAT >= 50e6) & (VOL >= 25000) & (R > 0) & (AMO == 0) & (PVP >= 0.30) & (PVP <= 3.0)
    if nome in EXCLUIDOS:
        univ[:] = False

    bad = np.zeros(n, bool)
    VAR = np.zeros(n)
    if n > 1:
        gap = np.diff(dates).astype("timedelta64[D]").astype(int)
        ret = C[1:] / C[:-1] - 1
        bad[1:] = (gap > 15) | (ret > 0.60) | (ret < -0.45)
        VAR[1:] = ret
    cbad = np.r_[0, np.cumsum(bad)]

    mN = pd.Series(C).rolling(N, min_periods=N).mean().to_numpy()
    mP = np.r_[np.nan, mN[:-1]]
    k200 = C / mP - 1

    sim = np.zeros(n, bool)
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= K_REND * R[:-LAG_REND]

    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome
    FD[nome] = dict(nome=nome, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, R=R, PVP=PVP, VP=VP, VOL=VOL,
                    NEG=NEG, VAR=VAR, univ=univ, bad=bad, cbad=cbad, mN=mN, mP=mP, k200=k200, sim=sim,
                    aberto=int(mi[-1]) >= NM - 21, cz={})

RDF = {}
for f_, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f_] = (bd, cs)


def rend_val(f, D, S, incl):
    """Soma de valor por cota dos avisos com data_base >= D e < S (<= S se incl). (copiada)"""
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


AMP_NUM = np.zeros(NM)
AMP_DEN = np.zeros(NM)
for F in FD.values():
    valid = F["univ"] & np.isfinite(F["k200"])
    hit = valid & (F["k200"] <= AMP_K)
    np.add.at(AMP_DEN, F["mi"][valid], 1)
    np.add.at(AMP_NUM, F["mi"][hit], 1)
AMP = np.where(AMP_DEN > 0, AMP_NUM / np.where(AMP_DEN > 0, AMP_DEN, 1), np.nan)


# ---------------------------------------------------------------- sinais (copiados)
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
for cfg in CARTEIRAS.values():
    X = cfg["X"]
    if X in CAND:
        continue
    lst = [[] for _ in range(NM)]
    n_sig = 0
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            n_sig += 1
            if md + 1 < NM and md + 1 >= I0:
                lst[md + 1].append((F, int(s), md))
    CAND[X] = lst
    print(f"sinais com X={X:.2f} (todos os anos): {n_sig}")


# ---------------------------------------------------------------- S1 (copiada de kairi_escada.sair, ramo 'media' com prazo)
def pmax(a, v):
    return max(a, v) if np.isfinite(a) else v


def pmin(a, v):
    return min(a, v) if np.isfinite(a) else v


def sair_s1(F, e):
    """S1 (copiada): alvo = MM200 até k-1; venda na primeira máxima(k) >= alvo a max(abertura, alvo).
    Guarda antes do alvo no mesmo pregão; sem alvo: prazo 252 no fechamento, fundo saiu da bolsa ou em aberto.
    Retorna (k, motivo, preço)."""
    last = F["n"] - 1
    W = min(e + PRAZO, last)
    kg = kv = None
    thr = None
    if W > e:
        w = np.flatnonzero(F["bad"][e + 1:W + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        thr = F["mN"][e:W]
        h = np.flatnonzero(F["H"][e + 1:W + 1] >= thr)
        if h.size:
            kv = e + 1 + int(h[0])
    if kg is not None and (kv is None or kg <= kv):
        k = kg - 1
        return k, GUARDA, float(F["C"][k])
    if kv is not None:
        a = float(F["A"][kv])
        alvo = float(thr[kv - e - 1])
        return kv, VOLTA, (max(a, alvo) if np.isfinite(a) else alvo)
    if e + PRAZO <= last:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO])
    if F["aberto"]:
        return last, ABERTO, float(F["C"][last])
    return last, SAIU, float(F["C"][last])


# ---------------------------------------------------------------- conta (copiada)
def conta(F, e, k, mot, px, cot):
    """Conta de uma ordem: compra cot cotas na abertura de e, venda na linha k a px. Resultado ANTES do imposto."""
    E = float(F["A"][e])
    D = F["dates"][e]
    S = F["dates"][k]
    valor = cot * E
    venda = cot * px
    valorizacao = venda - valor
    taxas = B3 * valor + B3 * venda
    incl = mot in (PRAZO_M, ABERTO)
    rend = rend_val(F["nome"], D, S, incl) * cot
    resultado = valorizacao + rend - taxas
    dias = int((S - D) / np.timedelta64(1, "D"))
    ie = int(np.searchsorted(MD, D, "left"))
    ix = int(np.searchsorted(MD, S, "left"))
    sel_pct = (np.exp(CUM[ix] - CUM[ie]) - 1) * (1 - aliq_rf(dias))
    L = F["L"][e:k + 1]
    pr = int(np.argmin(L))
    queda = min(0.0, float(L[pr]) / E - 1)
    alta_pos = float(np.max(F["H"][e + 1:k + 1])) / E - 1 if k > e else np.nan
    return dict(E=E, valor=valor, venda=venda, valorizacao=valorizacao, taxas=taxas, rend=rend,
                resultado=resultado, resultado_pct=resultado / valor, sel_pct=sel_pct, sel_rs=valor * sel_pct,
                dias=dias, px=float(px), data_saida=S, mi_x=ix, data_entrada=D, queda=queda,
                alta_pos=alta_pos, mi_e=ie)


# ---------------------------------------------------------------- entradas (copiado de kairi_escada.gerar_entradas)
def gerar_entradas(nome):
    """Mesmas entradas do kairi_saidas.py: a ocupação 'um fundo por vez' usa a saída S1."""
    cfg = CARTEIRAS[nome]
    cands = CAND[cfg["X"]]
    busy = {}
    out = []
    st = dict(candidatos=0, amplitude_baixa=0, sem_negociacao=0, um_fundo_por_vez=0, ordem_menor=0, aceitos=0)
    for ex in range(I0, NM):
        for F, s, md in sorted(cands[ex], key=lambda t: t[0]["nome"]):
            st["candidatos"] += 1
            if cfg["amp"] and not (AMP[md] >= AMP_LIM):
                st["amplitude_baixa"] += 1
                continue
            f = F["nome"]
            d_ex = MD[ex]
            r = int(np.searchsorted(F["dates"], d_ex))
            if r >= F["n"] or F["dates"][r] != d_ex or F["NEG"][r] != 1 or not np.isfinite(F["A"][r]) or F["A"][r] <= 0:
                st["sem_negociacao"] += 1
                continue
            if f in busy and busy[f] >= r:
                st["um_fundo_por_vez"] += 1
                continue
            px = float(F["A"][r])
            vol = float(F["VOL"][s])
            lim = min(ORDEM_MAX, PCT_VOL * vol) if np.isfinite(vol) else 0.0
            cot = int(np.floor(lim / px + 1e-9))
            if cot <= 0 or cot * px < ORDEM_MIN:
                st["ordem_menor"] += 1
                continue
            st["aceitos"] += 1
            k, _, _ = sair_s1(F, r)
            busy[f] = k
            out.append(dict(nome=nome, F=F, fundo=f, s=s, md=md, ex=ex, e=r, cot=cot, vol=vol))
    print(f"carteira {nome}: {st}")
    return out


# ---------------------------------------------------------------- regra nova (cruzamento de médias)
def cruz_arr(F, c, l):
    """cr[j] = True se mm_c(j-1) >= mm_l(j-1) e mm_c(j) < mm_l(j); médias sobre os fechamentos até j (inclusive)."""
    key = (c, l)
    if key not in F["cz"]:
        C = F["C"]
        mc = pd.Series(C).rolling(c, min_periods=c).mean().to_numpy()
        ml = pd.Series(C).rolling(l, min_periods=l).mean().to_numpy()
        tol = 1e-9 * np.abs(ml)          # empate numérico (janela de preço constante) conta como 'igual'
        cr = np.zeros(F["n"], bool)
        cr[1:] = (mc[1:] < ml[1:] - tol[1:]) & (mc[:-1] >= ml[:-1] - tol[:-1])
        F["cz"][key] = cr
    return F["cz"][key]


def regra_nova(F, e, P, g):
    """Armar na MM200 (sem venda no dia); depois piso (opcional), cruzamento e teto (opcional).
    Retorna dict(k, mot, px, karm, pc, lev). karm = -1 se nunca armou."""
    last = F["n"] - 1
    A, H, L, C, bad, mP = F["A"], F["H"], F["L"], F["C"], F["bad"], F["mP"]
    fim = min(e + PRAZO, last)
    idx = np.arange(e + 1, fim + 1)
    t_day = None
    if idx.size:
        gb = np.flatnonzero(bad[idx])
        tc = np.flatnonzero(H[idx] >= mP[idx])
        g_day = int(idx[gb[0]]) if gb.size else None
        t_day = int(idx[tc[0]]) if tc.size else None
        if g_day is not None and (t_day is None or g_day <= t_day):
            return dict(k=g_day - 1, mot=GUARDA, px=float(C[g_day - 1]), karm=-1, pc=np.nan, lev=np.nan)
    if t_day is None:
        if e + PRAZO <= last:
            return dict(k=e + PRAZO, mot=PRAZO_M, px=float(C[e + PRAZO]), karm=-1, pc=np.nan, lev=np.nan)
        mot = ABERTO if F["aberto"] else SAIU
        return dict(k=last, mot=mot, px=float(C[last]), karm=-1, pc=np.nan, lev=np.nan)

    ka = t_day
    pc = pmax(A[ka], mP[ka])
    lev = pc * (1 - g["f"])
    idx2 = np.arange(ka + 1, last + 1)
    cands = []
    if idx2.size:
        p_g = np.flatnonzero(bad[idx2])
        if p_g.size:
            cands.append((int(p_g[0]), 0, "g"))
        if g["usar"]:
            p_p = np.flatnonzero(L[idx2] <= lev)
            if p_p.size:
                cands.append((int(p_p[0]), 1, "p"))
        cr = cruz_arr(F, g["c"], g["l"])
        jj = idx2 - 1
        p_c = np.flatnonzero(cr[jj] & (jj > ka))
        if p_c.size:
            cands.append((int(p_c[0]), 2, "c"))
        if g["teto"]:
            p_t = np.flatnonzero(H[idx2] >= P)
            if p_t.size:
                cands.append((int(p_t[0]), 3, "t"))
    if not cands:
        mot = ABERTO if F["aberto"] else SAIU
        return dict(k=last, mot=mot, px=float(C[last]), karm=ka, pc=pc, lev=lev)
    pos, _, tipo = min(cands)
    k2 = int(idx2[pos])
    base = dict(karm=ka, pc=pc, lev=lev)
    if tipo == "g":
        return dict(k=k2 - 1, mot=GUARDA, px=float(C[k2 - 1]), **base)
    if tipo == "p":
        return dict(k=k2, mot=PISO, px=float(pmin(A[k2], lev)), **base)
    if tipo == "c":
        px = float(A[k2]) if np.isfinite(A[k2]) else float(C[k2])
        return dict(k=k2, mot=CRUZ, px=px, **base)
    return dict(k=k2, mot=TETO, px=float(pmax(A[k2], P)), **base)


# ---------------------------------------------------------------- registros: uma linha por (ordem, regra)
print("\n== ENTRADAS E SAÍDAS ==")
ENT = []
ROWS = []


def monta(nome, en, P, sig, res):
    F, e, cot, eid = en["F"], en["e"], en["cot"], en["eid"]
    E = float(F["A"][e])
    k, mot, px, karm = res["k"], res["mot"], res["px"], res["karm"]
    c = conta(F, e, k, mot, px, cot)
    return dict(carteira=nome, saida=sig, nome_saida=NOME_R[sig], fundo=F["nome"], eid=eid,
                entrada=pd.Timestamp(c["data_entrada"]), e=e, kidx=int(k), karm=int(karm),
                arm=(pd.Timestamp(F["dates"][karm]) if karm >= 0 else pd.NaT),
                pc=float(res["pc"]), lev=float(res["lev"]), E=E, P=P, cot=cot, valor=c["valor"],
                mot=mot, px=c["px"], data_saida=pd.Timestamp(c["data_saida"]), dias=c["dias"],
                pregoes_arm=(float(k - karm) if karm >= 0 else np.nan),
                valorizacao=c["valorizacao"], rend=c["rend"], taxas=c["taxas"], resultado=c["resultado"],
                resultado_pct=c["resultado_pct"], sel_pct=c["sel_pct"], sel_rs=c["sel_rs"],
                dif_antes=c["resultado"] - c["sel_rs"], alta_pos=c["alta_pos"], queda=c["queda"],
                mi_e=c["mi_e"], mi_x=c["mi_x"], fechada=mot != ABERTO)


ROWS_ENT = []
for nome in CARTEIRAS:
    for en in gerar_entradas(nome):
        ENT.append(en)
        en["eid"] = len(ENT) - 1
        F, s, e = en["F"], en["s"], en["e"]
        assert e == s + 1
        P = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))   # pico 252 até o sinal (fechamentos)
        k, mot, px = sair_s1(F, e)
        karm = k if mot == VOLTA else -1
        res = dict(k=k, mot=mot, px=px, karm=karm, pc=(pmax(F["A"][k], F["mP"][k]) if karm >= 0 else np.nan),
                   lev=np.nan)
        ROWS.append(monta(nome, en, P, "S1", res))
        for g in GRUPOS:
            ROWS.append(monta(nome, en, P, g["sig"], regra_nova(F, e, P, g)))

REC = pd.DataFrame(ROWS)
REC.loc[~REC["fechada"], "mi_x"] = NM                                  # em aberto: dinheiro aplicado até o fim
print(f"linhas (ordem x regra): {len(REC)}; ordens por carteira: "
      + ", ".join(f"{c}={int((REC.carteira == c).sum() // len(SIGS))}" for c in CARTEIRAS))


# ---------------------------------------------------------------- imposto com abatimento (copiado)
def imposto_mes(df):
    """20% sobre o ganho líquido (valorização - taxas) do mês da venda; prejuízo abate meses seguintes.
    Em aberto não paga imposto. (copiada)"""
    out = pd.Series(0.0, index=df.index)
    vend = df[df["fechada"]]
    if vend.empty:
        return out, pd.DataFrame()
    base = vend["valorizacao"] - vend["taxas"]
    mes = vend["data_saida"].dt.to_period("M")
    tab = base.groupby(mes).sum().sort_index().to_frame("ganho do mês (R$)")
    carry = 0.0
    taxa, usado, sobra = {}, {}, {}
    for m, b in tab["ganho do mês (R$)"].items():
        if b <= 0:
            carry += -b
            u, t = 0.0, 0.0
        else:
            u = min(carry, b)
            carry -= u
            t = IR_OP * (b - u)
        taxa[m], usado[m], sobra[m] = t, u, carry
    tab["imposto do mês (R$)"] = pd.Series(taxa)
    for m, grp in vend.groupby(mes):
        b = float(tab.loc[m, "ganho do mês (R$)"])
        t = float(tab.loc[m, "imposto do mês (R$)"])
        if t > 0:
            out.loc[grp.index] = t * (grp["valorizacao"] - grp["taxas"]) / b
    assert abs(out.sum() - tab["imposto do mês (R$)"].sum()) < 1e-6
    return out, tab


REC["imposto"] = 0.0
for (c_, sg_), g in REC.groupby(["carteira", "saida"], sort=False):
    imp, _ = imposto_mes(g)
    REC.loc[g.index, "imposto"] = imp


# ---------------------------------------------------------------- métricas (copiadas)
def pico_dinheiro(df):
    if df.empty:
        return 0.0
    ap = np.zeros(NM + 1)
    np.add.at(ap, df["mi_e"].to_numpy(int), df["valor"].to_numpy(float))
    np.add.at(ap, df["mi_x"].to_numpy(int), -df["valor"].to_numpy(float))
    return float(np.cumsum(ap)[I0:NM].max())


def metricas(df, imp):
    """Medida de comparação (copiada). Todas as ordens em R$ e risco; estatísticas de saída só nas fechadas."""
    n = len(df)
    fe = df["fechada"].to_numpy(bool)
    nf = int(fe.sum())
    aplic = float(df["valor"].sum())
    res_antes = float(df["resultado"].sum())
    imposto = float(imp.sum())
    res_liq = res_antes - imposto
    sel = float(df["sel_rs"].sum())
    dd = float((df["valor"] * df["dias"]).sum())
    anos = dd / 365
    C_ = df[fe]
    return {
        "ordens": n,
        "fechadas": nf,
        "em aberto": n - nf,
        "dias corridos médios": float(C_["dias"].mean()) if nf else np.nan,
        "total aplicado (R$)": aplic,
        "resultado líquido (R$)": res_liq,
        "Selic líquida no mesmo dinheiro (R$)": sel,
        "diferença para a Selic (R$)": res_liq - sel,
        "retorno ao ano sobre o dinheiro aplicado (%)": 100 * res_liq / anos if anos else np.nan,
        "resultado médio por ordem fechada (%)": 100 * float(C_["resultado_pct"].mean()) if nf else np.nan,
        "% fechadas com resultado > 0": 100 * float((C_["resultado"] > 0).mean()) if nf else np.nan,
        "% fechadas que ganharam da Selic": 100 * float((C_["dif_antes"] > 0).mean()) if nf else np.nan,
        "pico de dinheiro aplicado ao mesmo tempo (R$)": pico_dinheiro(df),
    }


def sub_de(car, sg, mask=None):
    s = REC[(REC.carteira == car) & (REC.saida == sg)]
    if mask is not None:
        s = s[mask(s)]
    return s


def mascara_escolha(sub):
    return sub["entrada"] <= CORTE_22


def mascara_conf(sub):
    return sub["entrada"] >= CONF_INI


def tres_periodos(car, sg):
    """(TOTAL, ESCOLHA, CONFERÊNCIA) com o imposto alocado do grupo completo (convenção de kairi_escada.py)."""
    out = []
    for mask in (None, mascara_escolha, mascara_conf):
        s = sub_de(car, sg, mask)
        out.append(metricas(s, s["imposto"]))
    return out


RES = {(c, sg): tres_periodos(c, sg) for c in CARTEIRAS for sg in SIGS}


# ---------------------------------------------------------------- reprodução da S1 (conferência 1)
print("\n==================== CONFERÊNCIA 1: REPRODUÇÃO DA S1 ====================")
for c, (rl, rt) in {"A": (81501, 23.5), "B": (62157, 31.2)}.items():
    m = RES[(c, "S1")][0]
    rl_n = m["resultado líquido (R$)"]
    ret_n = m["retorno ao ano sobre o dinheiro aplicado (%)"]
    print(f"carteira {c}, S1: resultado líquido {brl(rl_n)} (esperado {brl(rl)}); "
          f"retorno ao ano {br(ret_n, 1)}% (esperado {br(rt, 1)}%)")
    if round(rl_n) != rl or round(ret_n, 1) != rt:
        raise SystemExit(f"PARE: S1 não reproduzida na carteira {c}: {rl_n:.2f} vs {rl}; {ret_n:.4f} vs {rt}")
print("reprodução OK: A e B batem com dados/kairi_saidas.txt e kairi_escada.py")


# ---------------------------------------------------------------- T1
print("\n==================== T1: TOTAL, ESCOLHA e CONFERÊNCIA POR CARTEIRA ====================")
T1_COLS = ["ordens", "fechadas", "em aberto", "dias corridos médios das fechadas",
           "resultado líquido (R$)", "Selic do mesmo dinheiro (R$)", "diferença (R$)",
           "retorno ao ano TOTAL (%)", "retorno ao ano ESCOLHA (%)", "retorno ao ano CONFERÊNCIA (%)",
           "resultado médio por ordem fechada (%)", "% das fechadas com resultado > 0",
           "% que ganharam da Selic", "pico de dinheiro aplicado (R$)"]


def linha_t1(car, sg):
    mt, me, mc = RES[(car, sg)]
    return {
        "ordens": mt["ordens"], "fechadas": mt["fechadas"], "em aberto": mt["em aberto"],
        "dias corridos médios das fechadas": mt["dias corridos médios"],
        "resultado líquido (R$)": mt["resultado líquido (R$)"],
        "Selic do mesmo dinheiro (R$)": mt["Selic líquida no mesmo dinheiro (R$)"],
        "diferença (R$)": mt["diferença para a Selic (R$)"],
        "retorno ao ano TOTAL (%)": mt["retorno ao ano sobre o dinheiro aplicado (%)"],
        "retorno ao ano ESCOLHA (%)": me["retorno ao ano sobre o dinheiro aplicado (%)"],
        "retorno ao ano CONFERÊNCIA (%)": mc["retorno ao ano sobre o dinheiro aplicado (%)"],
        "resultado médio por ordem fechada (%)": mt["resultado médio por ordem fechada (%)"],
        "% das fechadas com resultado > 0": mt["% fechadas com resultado > 0"],
        "% que ganharam da Selic": mt["% fechadas que ganharam da Selic"],
        "pico de dinheiro aplicado (R$)": mt["pico de dinheiro aplicado ao mesmo tempo (R$)"],
    }


T1 = {}
for car in CARTEIRAS:
    print(f"\n--- carteira {car}")
    T1[car] = pd.DataFrame([linha_t1(car, sg) for sg in SIGS], index=SIGS)[T1_COLS]
    tabela(T1[car])


# ---------------------------------------------------------------- T2: motivos (G1, G2, G4; A e B)
print("\n==================== T2: MOTIVOS DE SAÍDA (G1, G2, G4; carteiras A e B) ====================")
for car in ["A", "B"]:
    for sg in ["G1", "G2", "G4"]:
        sub = sub_de(car, sg)
        print(f"\n--- carteira {car}, {sg}: {NOME_R[sg]}")
        for m in MOTIVOS:
            s_ = sub[sub.mot == m]
            if not len(s_):
                continue
            print(f"   {m:<34} n={len(s_):>4}; dias médios {br(s_['dias'].mean(), 1):>7}; "
                  f"resultado médio {br(100 * s_['resultado_pct'].mean(), 1)}%")
            if m == PISO:
                abaixo_e = int((s_["px"] < s_["E"]).sum())
                dif = 100 * (s_["px"] / s_["pc"] - 1).mean()
                print(f"      vendidas ABAIXO do preço de entrada: {abaixo_e} de {len(s_)}; "
                      f"pregões após armar: média {br(s_['pregoes_arm'].mean(), 1)}, "
                      f"mediana {br(s_['pregoes_arm'].median(), 1)}; "
                      f"diferença média entre preço vendido e Pc: {br(dif, 2)}%")
            if m == CRUZ:
                val = 100 * (s_["px"] / s_["pc"] - 1).mean()
                print(f"      valorização média entre Pc e o preço de venda: {br(val, 2)}%; "
                      f"pregões após armar: média {br(s_['pregoes_arm'].mean(), 1)}, "
                      f"mediana {br(s_['pregoes_arm'].median(), 1)}")
            if m == TETO:
                print(f"      pregões após armar: média {br(s_['pregoes_arm'].mean(), 1)}")


# ---------------------------------------------------------------- T3: ordem a ordem contra a S1 (G1, G2, G4)
print("\n==================== T3: ORDEM A ORDEM CONTRA A S1 (G1, G2, G4; A e B; antes do imposto) ====================")
for car in ["A", "B"]:
    s1 = sub_de(car, "S1").set_index("eid")
    for sg in ["G1", "G2", "G4"]:
        v = sub_de(car, sg).set_index("eid")
        s1v = s1.loc[v.index]
        d_r = v["resultado"] - s1v["resultado"]
        d_p = 100 * (v["resultado_pct"] - s1v["resultado_pct"])
        d_d = v["dias"] - s1v["dias"]
        mais = d_r > 0.01
        menos = d_r < -0.01
        igual = ~(mais | menos)
        print(f"{car} {sg} x S1 (n={len(v)}): rendeu mais em {int(mais.sum())}; menos em {int(menos.sum())}; "
              f"igual em {int(igual.sum())}; ganho médio quando mais: "
              f"{br(d_p[mais].mean(), 2) if mais.any() else 'nd'} pp; perda média quando menos: "
              f"{br(d_p[menos].mean(), 2) if menos.any() else 'nd'} pp; dias a mais aplicada (média): "
              f"{br(d_d.mean(), 1)}; soma da diferença de resultado: {brl(d_r.sum())}")


# ---------------------------------------------------------------- T4: quantas variações acima da S1
print("\n==================== T4: VARIAÇÕES ACIMA DA S1 (de 9) ====================")
for car in CARTEIRAS:
    s1_t, s1_e, s1_c = RES[(car, "S1")]
    gs = [g["sig"] for g in GRUPOS]
    acima_e = {sg for sg in gs if RES[(car, sg)][1]["retorno ao ano sobre o dinheiro aplicado (%)"]
               > s1_e["retorno ao ano sobre o dinheiro aplicado (%)"]}
    acima_c = {sg for sg in gs if RES[(car, sg)][2]["retorno ao ano sobre o dinheiro aplicado (%)"]
               > s1_c["retorno ao ano sobre o dinheiro aplicado (%)"]}
    acima_t = {sg for sg in gs if RES[(car, sg)][0]["retorno ao ano sobre o dinheiro aplicado (%)"]
               > s1_t["retorno ao ano sobre o dinheiro aplicado (%)"]}
    acima_selic = {sg for sg in gs if RES[(car, sg)][0]["diferença para a Selic (R$)"]
                   > s1_t["diferença para a Selic (R$)"]}
    print(f"carteira {car}: ESCOLHA acima da S1: {len(acima_e)}; CONFERÊNCIA acima: {len(acima_c)}; "
          f"nos DOIS: {len(acima_e & acima_c)} {sorted(acima_e & acima_c)}; "
          f"TOTAL retorno acima: {len(acima_t)}; diferença para a Selic (R$) TOTAL acima da S1: {len(acima_selic)}")


# ---------------------------------------------------------------- gravações
print("\n==================== GRAVAÇÕES ====================")
pl = REC[REC["carteira"].isin(["A", "B"]) & REC["saida"].isin(["S1", "G1", "G2", "G4"])].copy()
pl["ordem_saida"] = pl["saida"].map({s: i for i, s in enumerate(["S1", "G1", "G2", "G4"])})
pl = pl.sort_values(["carteira", "ordem_saida", "entrada", "fundo"]).reset_index(drop=True)


def num(x, d):
    return "nd" if isnan(x) else f"{x:.{d}f}".replace(".", ",")


pl_out = pd.DataFrame({
    "Carteira": pl["carteira"],
    "Regra de saída (por extenso)": pl["nome_saida"],
    "Fundo": pl["fundo"],
    "Data de entrada": pl["entrada"],
    "Preço de entrada (R$)": [num(x, 2) for x in pl["E"]],
    "Valor da ordem (R$)": [num(x, 2) for x in pl["valor"]],
    "Data em que cruzou a média": pl["arm"],
    "Preço do cruzamento (R$)": [num(x, 2) for x in pl["pc"]],
    "Situação": np.where(pl["mot"] == ABERTO, "Em aberto", "Fechada"),
    "Data de saída (ou do último preço)": pl["data_saida"],
    "Preço de saída (ou atual) (R$)": [num(x, 2) for x in pl["px"]],
    "Motivo da saída": pl["mot"],
    "Dias corridos": pl["dias"].astype(int),
    "Valorização (%)": [num(100 * v / val, 1) for v, val in zip(pl["valorizacao"], pl["valor"])],
    "Rendimentos (%)": [num(100 * v / val, 1) for v, val in zip(pl["rend"], pl["valor"])],
    "Resultado antes do imposto (%)": [num(100 * x, 1) for x in pl["resultado_pct"]],
    "Resultado antes do imposto (R$)": [num(x, 2) for x in pl["resultado"]],
    "Selic líquida no mesmo período (%)": [num(100 * x, 1) for x in pl["sel_pct"]],
    "Ganhou da Selic (sim/não)": np.where(pl["dif_antes"] > 0, "sim", "não"),
    "Maior alta acima da entrada (%)": [num(100 * x, 1) for x in pl["alta_pos"]],
})
pl_out.to_csv(PL / "kairi_cruzamento.csv", **OPC)
print(f"gravado: planilhas/kairi_cruzamento.csv ({len(pl_out)} linhas)")

comp_rows = []
for car in CARTEIRAS:
    for sg in SIGS:
        d = {"Carteira": car, "Regra de saída": NOME_R[sg]}
        for col, v in T1[car].loc[sg].items():
            if col in ("ordens", "fechadas", "em aberto"):
                d[col] = int(v)
            elif isnan(v):
                d[col] = np.nan
            else:
                d[col] = round(float(v), 1 if "%" in col else 2)
        comp_rows.append(d)
comp_df = pd.DataFrame(comp_rows)
for kk in ("ordens", "fechadas", "em aberto"):
    comp_df[kk] = comp_df[kk].astype("Int64")
comp_df.to_csv(TEC / "kairi_cruzamento_comparacao.csv", **OPC)
print(f"gravado: planilhas/tecnico/kairi_cruzamento_comparacao.csv ({len(comp_df)} linhas)")


# ---------------------------------------------------------------- CONFERÊNCIA 2: duas ordens da carteira A na G1
print("\n==================== CONFERÊNCIA 2: DUAS ORDENS DA CARTEIRA A NA G1 ====================")


def exemplo(mot_alvo):
    sub = REC[(REC.carteira == "A") & (REC.saida == "G1") & (REC.mot == mot_alvo)]
    if sub.empty:
        print(f"\n[{mot_alvo}] sem ordens na G1 da carteira A")
        return
    r = sub.iloc[0]
    en = ENT[int(r.eid)]
    F = en["F"]
    e, s, k, ka, cot = int(r.e), en["s"], int(r.kidx), int(r.karm), int(r.cot)
    E = float(r.E)
    mc7 = pd.Series(F["C"]).rolling(7, min_periods=7).mean().to_numpy()
    mc21 = pd.Series(F["C"]).rolling(21, min_periods=21).mean().to_numpy()
    print(f"\n[{mot_alvo}] fundo {r.fundo}; sinal {dt(F['dates'][s])}; entrada {dt(F['dates'][e])} a R$ {br(E, 4)}; "
          f"cotas {cot}")
    print(f"   ARMOU em {dt(F['dates'][ka])}: máxima {br(F['H'][ka], 4)}; MM200 (até d-1) {br(F['mP'][ka], 4)}; "
          f"máxima >= MM200: {bool(F['H'][ka] >= F['mP'][ka])}; abertura {br(F['A'][ka], 4)}; "
          f"Pc = max(abertura, MM200) = {br(r.pc, 4)}; piso (folga 0%) = {br(r.lev, 4)}")
    print(f"   VENDA em {dt(F['dates'][k])}: abertura {br(F['A'][k], 4)}, mínima {br(F['L'][k], 4)}, "
          f"máxima {br(F['H'][k], 4)}; motivo {r.mot}; preço de venda {br(r.px, 4)}; pregões após armar {k - ka}")
    for j in (k - 2, k - 1):
        print(f"      fechamento de {dt(F['dates'][j])}: mm7 {br(mc7[j], 4)}, mm21 {br(mc21[j], 4)}; "
              f"mm7 < mm21: {bool(mc7[j] < mc21[j])}")
    valor = cot * E
    venda = cot * r.px
    val = venda - valor
    taxas = B3 * valor + B3 * venda
    incl = r.mot in (PRAZO_M, ABERTO)
    rend = rend_val(F["nome"], F["dates"][e], F["dates"][k], incl) * cot
    res = val + rend - taxas
    print(f"   conta: valor {brl(valor, 2)}; venda {brl(venda, 2)}; valorização {brl(val, 2)}; rendimentos "
          f"{brl(rend, 2)}; taxas {brl(taxas, 2)}; resultado antes do imposto {brl(res, 2)} = "
          f"{br(100 * res / valor, 2)}%; no DataFrame: {brl(r.resultado, 2)}")
    assert abs(res - r.resultado) < 0.01


exemplo(PISO)
exemplo(CRUZ)


# ---------------------------------------------------------------- CONFERÊNCIA 3: código (asserts em todas as ordens)
print("\n==================== CONFERÊNCIA 3: CÓDIGO (asserts, todas as ordens das regras novas) ====================")


def mm_at(F, j, w):
    return F["C"][j - w + 1:j + 1].mean()


n_chk = dict(armadas=0, piso=0, cruz=0, teto=0, guarda_no_dia_armado=0, prazo=0, aberto_saiu=0)
for r in REC[REC.saida.str.startswith("G")].itertuples(index=False):
    en = ENT[int(r.eid)]
    F, e = en["F"], en["e"]
    gr = G_BY[r.saida]
    ka, kv = int(r.karm), int(r.kidx)
    if ka < 0:
        assert r.mot in (PRAZO_M, ABERTO, SAIU, GUARDA), r.mot
        if r.mot == PRAZO_M:
            assert kv == e + PRAZO
            n_chk["prazo"] += 1
        else:
            n_chk["aberto_saiu"] += 1
        continue
    n_chk["armadas"] += 1
    assert ka > e, "armou antes da entrada"
    if ka >= N:
        # MM200(k) vai até k-1
        assert abs(F["mP"][ka] - F["C"][ka - N:ka].mean()) < 1e-9
    assert abs(r.pc - pmax(F["A"][ka], F["mP"][ka])) < 1e-9 and r.pc >= F["mP"][ka] - 1e-12
    lev = r.pc * (1 - gr["f"])
    assert abs(r.lev - lev) < 1e-9
    if r.mot == GUARDA:
        assert kv >= ka
        if kv == ka:
            n_chk["guarda_no_dia_armado"] += 1
        continue
    # no dia em que arma não há venda (piso, cruzamento e teto)
    assert kv > ka, f"venda no dia em que armou: {r.mot}"
    if r.mot == PISO:
        assert gr["usar"]
        assert F["L"][kv] <= lev + 1e-12
        assert abs(r.px - min(F["A"][kv], lev)) < 1e-9
        n_chk["piso"] += 1
    elif r.mot == CRUZ:
        j = kv - 1
        assert j > ka, "cruzamento no dia em que armou"
        # cruzamento visto no fechamento de k2-1 (j) e de k2-2 (j-1), com médias ATÉ esses fechamentos
        assert j - 1 >= gr["l"] - 1
        assert mm_at(F, j, gr["c"]) < mm_at(F, j, gr["l"]) - 1e-9 * abs(mm_at(F, j, gr["l"]))
        assert mm_at(F, j - 1, gr["c"]) >= mm_at(F, j - 1, gr["l"]) - 1e-9 * abs(mm_at(F, j - 1, gr["l"]))
        # piso e cruzamento no mesmo dia: vale o piso (por isso o piso não pode ter sido tocado em kv)
        if gr["usar"]:
            assert not (F["L"][kv] <= lev), "piso tocado no dia do cruzamento e não foi vendido no piso"
        exp = F["A"][kv] if np.isfinite(F["A"][kv]) else F["C"][kv]
        assert abs(r.px - exp) < 1e-9
        n_chk["cruz"] += 1
    elif r.mot == TETO:
        assert gr["teto"]
        assert F["H"][kv] >= r.P - 1e-9
        assert abs(r.px - pmax(F["A"][kv], r.P)) < 1e-9
        n_chk["teto"] += 1
    else:
        # armada e nunca vendeu: sem prazo; termina no último pregão (em aberto ou fundo saiu da bolsa)
        assert r.mot in (ABERTO, SAIU), r.mot
        assert kv == len(F["C"]) - 1
        n_chk["aberto_saiu"] += 1
print(f"ASSERTS PASSARAM: armadas {n_chk['armadas']}; vendas no piso {n_chk['piso']}; "
      f"vendas no cruzamento {n_chk['cruz']}; vendas no teto {n_chk['teto']}; "
      f"guarda no dia da armação (venda no fechamento do dia armado) {n_chk['guarda_no_dia_armado']}; "
      f"prazos {n_chk['prazo']}; em aberto/saiu sem armar {n_chk['aberto_saiu']}")
print("conferido: MM200 da armação é a média dos 200 fechamentos até k-1; médias do cruzamento são as de k2-1 e k2-2.")


# ---------------------------------------------------------------- CONFERÊNCIA 4: soma das contagens = ordens
print("\n==================== CONFERÊNCIA 4: SOMA DAS CONTAGENS = ORDENS ====================")
for g in GRUPOS:
    for car in CARTEIRAS:
        sub = sub_de(car, g["sig"])
        soma = sum(int((sub.mot == m).sum()) for m in MOTIVOS)
        assert soma == len(sub), (g["sig"], car)
print("OK: em todas as variações G1..G9 e carteiras A, B e C, soma por motivo = número de ordens.")

print(f"\nTempo total: {time.time() - T0:.1f} s")
