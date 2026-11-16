"""Comparacao de regras de saida do Indice de Kairi em FIIs, sobre as MESMAS entradas.

Entradas: copiadas de estudos/kairi_ordens.py (sem importar, pois aquele script executa tudo no import
e regrava planilhas existentes). Universo, guarda, sinais, tamanho da ordem e a definicao do Kairi
(media dos 200 fechamentos ate d-1) sao os mesmos. A entrada 'um fundo por vez' usa a saida S1.

Saidas comparadas (todas sobre as mesmas entradas):
  S1 (volta a media, prazo 252), S1L (sem prazo), S2L (media, piso na entrada), SCL (media congelada no sinal),
  F38L/F50L/F62L/F100L (Fibonacci sobre o pico de 252 pregoes), M127L/M162L (extensoes sobre a media do sinal),
  F50P e M127P (as duas com prazo de 252 pregoes).

Imposto: 20% sobre o ganho liquido (valorizacao - taxas) do mes da venda, prejuizo abate meses seguintes.
Rendimentos isentos. O resultado por ordem fica antes do imposto; o imposto entra nos totais.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_saidas.py 2>&1 | tee dados/kairi_saidas.txt
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
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

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
ALVO = "alvo atingido"
PRAZO_M = "prazo"
SAIU = "fundo saiu da bolsa"
GUARDA = "dado suspeito"
ABERTO = "em aberto"
MOTIVOS = [VOLTA, ALVO, PRAZO_M, SAIU, GUARDA, ABERTO]
LIMITE_SALTO = 0.25


# ---------------------------------------------------------------- formatacao
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
    if "(x)" in key:
        return br(v, 2)
    if "%" in key:
        return br(v, 1) + "%"
    return br(v, 1)


# ---------------------------------------------------------------- carga (copiada de kairi_ordens.py)
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
print(f"linhas de precos com fechamento NaN: {int(PR[C_FE].isna().sum())}")
RD_NA = int(RD_BRUTO["data_base"].isna().sum())
RD = RD_BRUTO.dropna(subset=["data_base"]).reset_index(drop=True)
print(f"rendimentos com data_base NaN (removidos): {RD_NA}; avisos duplicados mantidos: "
      f"{int(RD.duplicated(['fundo', 'data_base', 'valor (R$/cota)']).sum())}")

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

# anuncios (fatos relevantes), so para o cruzamento com cortes
AN = pd.read_csv(PL / "anuncios.csv", sep=";", decimal=",", encoding="utf-8-sig")
AN["data"] = pd.to_datetime(AN["data_anuncio"].str.slice(0, 10), format="%d/%m/%Y")
ANF = {f: g.reset_index(drop=True) for f, g in AN.groupby("fundo")}


def aliq_rf(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


# ---------------------------------------------------------------- arrays por fundo
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
                    aberto=int(mi[-1]) >= NM - 21)

RDF = {}
for f_, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f_] = (bd, cs)

# avisos ordenados por data_conhecido (mantem duplicatas, como o script de ordens)
RDC = {}
for f_, g in RD.sort_values("data_conhecido", kind="mergesort").groupby("fundo", sort=False):
    RDC[f_] = (g["data_conhecido"].to_numpy("datetime64[D]"), g["data_base"].to_numpy("datetime64[D]"),
               g["valor (R$/cota)"].to_numpy(float))


def rend_val(f, D, S, incl):
    """Soma de valor por cota dos avisos com data_base >= D e < S (<= S se incl)."""
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


# ---------------------------------------------------------------- regras de saida
def sair(F, e, tipo, prazo, E, T):
    """Saida de uma ordem comprada na abertura de e.

    tipo 'media': alvo = media dos 200 fechamentos ate k-1 (threshold mN[k-1]).
    tipo 'piso' : alvo = max(media ate k-1, E).
    tipo 'fixo' : alvo = T (constante, calculado no dia do sinal).
    Venda na primeira maxima(k) >= alvo, a max(abertura(k), alvo). Guarda antes do alvo no mesmo pregao.
    Sem alvo: prazo de 252 (se prazo), fundo saiu da bolsa, ou em aberto.
    Retorna (k, motivo, preco, alvo usado em k).
    """
    last = F["n"] - 1
    W = min(e + PRAZO, last) if prazo else last
    kg = kv = None
    thr = None
    if W > e:
        w = np.flatnonzero(F["bad"][e + 1:W + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        if tipo == "fixo":
            h = np.flatnonzero(F["H"][e + 1:W + 1] >= T)
        else:
            thr = F["mN"][e:W]                       # thr[i] = mN[k-1] para k = e+1+i
            if tipo == "piso":
                thr = np.maximum(thr, E)
            h = np.flatnonzero(F["H"][e + 1:W + 1] >= thr)
        if h.size:
            kv = e + 1 + int(h[0])
    if kg is not None and (kv is None or kg <= kv):
        k = kg - 1
        return k, GUARDA, float(F["C"][k]), np.nan
    if kv is not None:
        alvo_k = T if tipo == "fixo" else float(thr[kv - e - 1])
        a = float(F["A"][kv])
        px = max(a, alvo_k) if np.isfinite(a) else alvo_k
        mot = VOLTA if tipo in ("media", "piso") else ALVO
        return kv, mot, px, alvo_k
    last_ = F["n"] - 1
    if prazo and e + PRAZO <= last_:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO]), np.nan
    if F["aberto"]:
        return last_, ABERTO, float(F["C"][last_]), np.nan
    return last_, SAIU, float(F["C"][last_]), np.nan


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
    p = e + pr
    queda = min(0.0, float(L[pr]) / E - 1)
    abaixo = queda < 0
    if abaixo:
        volt = np.flatnonzero(F["H"][p + 1:k + 1] >= E)
        voltou = "sim" if volt.size else "não"
        p_volta = float(volt[0] + 1) if volt.size else np.nan
    else:
        voltou = "não caiu"
        p_volta = np.nan
    alta = float(np.max(F["H"][e:k + 1])) / E - 1
    alta_pos = float(np.max(F["H"][e + 1:k + 1])) / E - 1 if k > e else np.nan   # so dias apos a entrada
    return dict(E=E, valor=valor, venda=venda, valorizacao=valorizacao, taxas=taxas, rend=rend,
                resultado=resultado, resultado_pct=resultado / valor, sel_pct=sel_pct, sel_rs=valor * sel_pct,
                dias=dias, pregoes=int(k - e), px=float(px), data_saida=S, mi_x=ix, data_entrada=D,
                queda=queda, abaixo=abaixo, pregoes_fundo=pr, voltou=voltou, p_volta=p_volta, alta=alta,
                alta_pos=alta_pos, mi_e=ie, pvp_e=E / F["VP"][e] if F["VP"][e] > 0 else np.nan,
                pvp_s=px / F["VP"][k] if F["VP"][k] > 0 else np.nan)


def salto_info(F, s, k):
    """Variacao diaria acima de 25% (em modulo) entre 200 pregoes antes do sinal e a saida."""
    a = max(1, s - 199)
    if k < a:
        return False, pd.NaT, np.nan
    v = F["VAR"][a:k + 1]
    j = int(np.nanargmax(np.abs(v)))
    if abs(v[j]) > LIMITE_SALTO:
        return True, pd.Timestamp(F["dates"][a + j]), float(v[j])
    return False, pd.NaT, np.nan


# ---------------------------------------------------------------- entradas (copiado de kairi_ordens.simular)
def gerar_entradas(nome):
    """Mesmas entradas do kairi_ordens.py: a ocupacao 'um fundo por vez' usa a saida S1 (volta a media, prazo)."""
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
            k, _, _, _ = sair(F, r, "media", True, px, np.nan)
            busy[f] = k
            out.append(dict(nome=nome, F=F, fundo=f, s=s, md=md, ex=ex, e=r, cot=cot, vol=vol))
    print(f"carteira {nome}: {st}")
    return out


# ---------------------------------------------------------------- definicao das saidas
def fib(f):
    return lambda E, M0, P: E + f * (P - E)


def ext(f):
    return lambda E, M0, P: E + f * (M0 - E)


def media_do_sinal(E, M0, P):
    return M0


REGRAS = [
    dict(sig="S1", nome="Volta à média (prazo de 252 pregões)", tipo="media", prazo=True),
    dict(sig="S1L", nome="Volta à média (sem prazo)", tipo="media", prazo=False),
    dict(sig="S2L", nome="Volta à média, nunca abaixo da entrada (sem prazo)", tipo="piso", prazo=False),
    dict(sig="SCL", nome="Média dos 200 pregões do sinal (sem prazo)", tipo="fixo", calc=media_do_sinal, prazo=False),
    dict(sig="F38L", nome="Fibonacci 38,2% do pico (sem prazo)", tipo="fixo", calc=fib(0.382), prazo=False),
    dict(sig="F50L", nome="Fibonacci 50% do pico (sem prazo)", tipo="fixo", calc=fib(0.5), prazo=False),
    dict(sig="F62L", nome="Fibonacci 61,8% do pico (sem prazo)", tipo="fixo", calc=fib(0.618), prazo=False),
    dict(sig="F100L", nome="Pico de 252 pregões (sem prazo)", tipo="fixo", calc=fib(1.0), prazo=False),
    dict(sig="M127L", nome="Extensão 127,2% da média do sinal (sem prazo)", tipo="fixo", calc=ext(1.272), prazo=False),
    dict(sig="M162L", nome="Extensão 161,8% da média do sinal (sem prazo)", tipo="fixo", calc=ext(1.618), prazo=False),
    dict(sig="F50P", nome="Fibonacci 50% do pico (prazo de 252 pregões)", tipo="fixo", calc=fib(0.5), prazo=True),
    dict(sig="M127P", nome="Extensão 127,2% da média do sinal (prazo de 252 pregões)", tipo="fixo",
         calc=ext(1.272), prazo=True),
]
SIGS = [r["sig"] for r in REGRAS]
NOME_SAIDA = {r["sig"]: r["nome"] for r in REGRAS}


# ---------------------------------------------------------------- registros: uma linha por (ordem, saida)
print("\n== ENTRADAS E SAIDAS ==")
ENT = []
ROWS = []
for nome in CARTEIRAS:
    for en in gerar_entradas(nome):
        ENT.append(en)
        F, s, e, cot = en["F"], en["s"], en["e"], en["cot"]
        assert e == s + 1
        E = float(F["A"][e])
        M0 = float(F["mP"][s])                                       # media dos 200 ate d-1 (congelada)
        P = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))       # pico 252 ate d
        eid = len(ENT) - 1
        for reg in REGRAS:
            T = reg["calc"](E, M0, P) if reg["tipo"] == "fixo" else np.nan
            k, mot, px, alvo_k = sair(F, e, reg["tipo"], reg["prazo"], E, T)
            c = conta(F, e, k, mot, px, cot)
            sal, sal_d, sal_v = salto_info(F, s, k)
            if reg["tipo"] == "fixo":
                alvo_dia, alvo_saida = T, T
            else:
                alvo_dia, alvo_saida = M0, alvo_k
            row = dict(carteira=nome, saida=reg["sig"], nome_saida=reg["nome"], fundo=F["nome"],
                       tipo=TIPO.get(F["nome"], "sem tipo"), sinal=pd.Timestamp(F["dates"][s]),
                       entrada=pd.Timestamp(c["data_entrada"]), ano=pd.Timestamp(c["data_entrada"]).year,
                       eid=eid, e=e, s=s, k=k,
                       cot=cot, valor_pre=None, M0=M0, P=P, alvo_dia=alvo_dia, alvo_saida=alvo_saida,
                       kairi_sinal=float(F["k200"][s]), amp_sinal=float(AMP[en["md"]]), vol60=en["vol"],
                       rend_entrada=float(F["R"][e]), pvp_e=c["pvp_e"], pvp_s=c["pvp_s"],
                       salto=sal, salto_data=sal_d, salto_var=sal_v, mot=mot, px=c["px"],
                       data_saida=pd.Timestamp(c["data_saida"]), dias=c["dias"], pregoes=c["pregoes"],
                       valor=c["valor"], valorizacao=c["valorizacao"], rend=c["rend"], taxas=c["taxas"],
                       resultado=c["resultado"], resultado_pct=c["resultado_pct"], sel_pct=c["sel_pct"],
                       sel_rs=c["sel_rs"], queda=c["queda"], abaixo=c["abaixo"],
                       pregoes_fundo=c["pregoes_fundo"], voltou=c["voltou"], p_volta=c["p_volta"],
                       alta=c["alta"], alta_pos=c["alta_pos"], mi_e=c["mi_e"], mi_x=c["mi_x"],
                       fechada=mot != ABERTO,
                       E=E, data_entrada=pd.Timestamp(c["data_entrada"]))
            ROWS.append(row)
REC = pd.DataFrame(ROWS).drop(columns=["valor_pre"])
REC["dif_antes"] = REC["resultado"] - REC["sel_rs"]
REC.loc[~REC["fechada"], "mi_x"] = NM                                 # em aberto: dinheiro aplicado ate o fim
print(f"linhas (ordem x saida): {len(REC)}; ordens por carteira: "
      + ", ".join(f"{c}={int((REC.carteira == c).sum() // len(SIGS))}" for c in CARTEIRAS))


# ---------------------------------------------------------------- imposto com abatimento
def imposto_mes(df):
    """20% sobre o ganho liquido (valorizacao - taxas) do mes da venda; prejuizo abate meses seguintes.
    Retorna (imposto alocado por ordem, tabela mensal). Em aberto nao paga imposto."""
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
    tab["prejuízo acumulado usado (R$)"] = pd.Series(usado)
    tab["prejuízo acumulado restante (R$)"] = pd.Series(sobra)
    tab["imposto do mês (R$)"] = pd.Series(taxa)
    for m, grp in vend.groupby(mes):
        b = float(tab.loc[m, "ganho do mês (R$)"])
        t = float(tab.loc[m, "imposto do mês (R$)"])
        if t > 0:
            out.loc[grp.index] = t * (grp["valorizacao"] - grp["taxas"]) / b
    assert abs(out.sum() - tab["imposto do mês (R$)"].sum()) < 1e-6
    return out, tab


IMP_TAB = {}
REC["imposto"] = 0.0
for (c_, sg_), g in REC.groupby(["carteira", "saida"], sort=False):
    imp, tab = imposto_mes(g)
    REC.loc[g.index, "imposto"] = imp
    IMP_TAB[(c_, sg_)] = tab


# ---------------------------------------------------------------- metricas
def pico_dinheiro(df):
    if df.empty:
        return 0.0
    ap = np.zeros(NM + 1)
    np.add.at(ap, df["mi_e"].to_numpy(int), df["valor"].to_numpy(float))
    np.add.at(ap, df["mi_x"].to_numpy(int), -df["valor"].to_numpy(float))
    return float(np.cumsum(ap)[I0:NM].max())


COMP_KEYS = ["ordens", "fechadas", "em aberto", "pregões médios das fechadas", "dias corridos médios",
             "total aplicado (R$)", "valorização (R$)", "rendimentos (R$)", "taxas (R$)", "imposto (R$)",
             "resultado líquido (R$)", "Selic líquida no mesmo dinheiro (R$)", "diferença para a Selic (R$)",
             "dinheiro x dias (milhões R$.dia)", "retorno ao ano sobre o dinheiro aplicado (%)",
             "Selic ao ano na mesma conta (%)", "% fechadas com resultado > 0", "% fechadas que ganharam da Selic",
             "média das 10% piores quedas máximas (%)", "pior ordem (%)",
             "pico de dinheiro aplicado ao mesmo tempo (R$)", "resultado em aberto (R$)"]
REDUZ_KEYS = ["ordens", "em aberto", "resultado líquido (R$)", "diferença para a Selic (R$)",
              "retorno ao ano sobre o dinheiro aplicado (%)", "Selic ao ano na mesma conta (%)",
              "% fechadas com resultado > 0", "pico de dinheiro aplicado ao mesmo tempo (R$)"]


def metricas(df, imp):
    """Medida de comparacao. TODAS as ordens nos valores em R$ e risco; estatisticas de saida so nas fechadas."""
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
    q = np.sort(df["queda"].to_numpy(float))
    kq = max(1, int(round(0.10 * n))) if n else 1
    C_ = df[fe]
    out = {
        "ordens": n,
        "fechadas": nf,
        "em aberto": n - nf,
        "pregões médios das fechadas": float(C_["pregoes"].mean()) if nf else np.nan,
        "dias corridos médios": float(C_["dias"].mean()) if nf else np.nan,
        "total aplicado (R$)": aplic,
        "valorização (R$)": float(df["valorizacao"].sum()),
        "rendimentos (R$)": float(df["rend"].sum()),
        "taxas (R$)": float(df["taxas"].sum()),
        "imposto (R$)": imposto,
        "resultado líquido (R$)": res_liq,
        "Selic líquida no mesmo dinheiro (R$)": sel,
        "diferença para a Selic (R$)": res_liq - sel,
        "dinheiro x dias (milhões R$.dia)": dd / 1e6,
        "retorno ao ano sobre o dinheiro aplicado (%)": 100 * res_liq / anos if anos else np.nan,
        "Selic ao ano na mesma conta (%)": 100 * sel / anos if anos else np.nan,
        "% fechadas com resultado > 0": 100 * float((C_["resultado"] > 0).mean()) if nf else np.nan,
        "% fechadas que ganharam da Selic": 100 * float((C_["dif_antes"] > 0).mean()) if nf else np.nan,
        "média das 10% piores quedas máximas (%)": 100 * float(q[:kq].mean()) if n else np.nan,
        "pior ordem (%)": 100 * float(df["resultado_pct"].min()) if n else np.nan,
        "pico de dinheiro aplicado ao mesmo tempo (R$)": pico_dinheiro(df),
        "resultado em aberto (R$)": float(df.loc[~fe, "resultado"].sum()),
    }
    return out


def tabela_saidas(c, mask_periodo=None):
    linhas = {}
    for sg in SIGS:
        sub = REC[(REC["carteira"] == c) & (REC["saida"] == sg)]
        if mask_periodo is not None:
            sub = sub[mask_periodo(sub)]
        linhas[sg] = metricas(sub, sub["imposto"])
    return pd.DataFrame(linhas).T[COMP_KEYS]


def mascara_escolha(sub):
    return sub["entrada"] <= CORTE_22


def mascara_conf(sub):
    return sub["entrada"] >= CONF_INI


TAB_TOTAL, TAB_ESC, TAB_CONF = {}, {}, {}
for c in CARTEIRAS:
    TAB_TOTAL[c] = tabela_saidas(c)
    TAB_ESC[c] = tabela_saidas(c, mascara_escolha)
    TAB_CONF[c] = tabela_saidas(c, mascara_conf)

ESCOLHIDA = {c: str(TAB_ESC[c]["retorno ao ano sobre o dinheiro aplicado (%)"].astype(float).idxmax())
             for c in CARTEIRAS}


# ---------------------------------------------------------------- impressao: comparacao
def imprime_tab(tab, keys=None):
    cel = pd.DataFrame(index=tab.index, columns=tab.columns, dtype=object)
    for col in tab.columns:
        cel[col] = [fmt_val(col, v) for v in tab[col]]
    if keys is not None:
        cel = cel[keys]
    print(cel.to_string())


print("\n==================== COMPARACAO ENTRE SAIDAS (TOTAL: todas as entradas) ====================")
print("(ordens em aberto entram pelo ultimo preco; % e pior/queda so de fechadas ou de todas, como indicado no nome)")
for c in CARTEIRAS:
    print(f"\n--- carteira {c} - TOTAL")
    imprime_tab(TAB_TOTAL[c])

print("\n==================== COMPARACAO REDUZIDA: ESCOLHA (entradas ate 31/12/2022) ====================")
for c in CARTEIRAS:
    print(f"\n--- carteira {c} - ESCOLHA")
    imprime_tab(TAB_ESC[c], REDUZ_KEYS)
print("\n==================== COMPARACAO REDUZIDA: CONFERENCIA (entradas de 01/01/2023) ====================")
for c in CARTEIRAS:
    print(f"\n--- carteira {c} - CONFERÊNCIA")
    imprime_tab(TAB_CONF[c], REDUZ_KEYS)

print("\n==================== MELHOR SAIDA PELA ESCOLHA ====================")
for c in CARTEIRAS:
    sg = ESCOLHIDA[c]
    ret_e = TAB_ESC[c].loc[sg, "retorno ao ano sobre o dinheiro aplicado (%)"]
    ret_c = TAB_CONF[c].loc[sg, "retorno ao ano sobre o dinheiro aplicado (%)"]
    res_c = TAB_CONF[c].loc[sg, "resultado líquido (R$)"]
    dif_c = TAB_CONF[c].loc[sg, "diferença para a Selic (R$)"]
    print(f"carteira {c}: melhor saida na ESCOLHA = {sg} ({NOME_SAIDA[sg]}); retorno ao ano ESCOLHA = {br(ret_e, 1)}%; "
          f"CONFERÊNCIA: resultado liquido {brl(res_c)}, diferenca para a Selic {brl(dif_c)}, retorno ao ano {br(ret_c, 1)}%")


# ---------------------------------------------------------------- pergunta do dono sobre a S1
print("\n==================== PERGUNTA SOBRE A S1 (volta à média) ====================")
for c in CARTEIRAS:
    sub = REC[(REC["carteira"] == c) & (REC["saida"] == "S1")]
    vol = sub[sub["mot"] == VOLTA]
    ab = vol[vol["px"] < vol["E"]]
    ab_alta = ab[ab["alta_pos"] >= 0]
    prz = sub[sub["mot"] == PRAZO_M]
    prz_alta = prz[prz["alta_pos"] >= 0]
    print(f"\ncarteira {c}: saidas por volta à média = {len(vol)}; com preço de saída ABAIXO da entrada = {len(ab)}")
    print(f"  dessas, com alguma máxima >= entrada nos dias depois da entrada, ate a saida = {len(ab_alta)}; "
          f"maior alta média delas (maxima depois da entrada, acima da entrada) = {br(100 * ab['alta_pos'].mean(), 1) if len(ab) else 'nd'}% ; "
          f"resultado médio das {len(ab)} (antes do imposto) = {br(100 * ab['resultado_pct'].mean(), 1) if len(ab) else 'nd'}%")
    print(f"  saidas por prazo = {len(prz)}; com alguma máxima >= entrada depois da entrada = {len(prz_alta)}")


# ---------------------------------------------------------------- balanco ano a ano
def balanco(df):
    fe = df["fechada"]
    C_ = df[fe]
    aplic = float(df["valor"].sum())
    res = float(df["resultado"].sum())
    sel = float(df["sel_rs"].sum())
    out = {}
    out["ordens"] = len(df)
    out["fechadas"] = len(C_)
    out["em aberto"] = len(df) - len(C_)
    out["total aplicado (R$)"] = aplic
    out["dias corridos médios (fechadas)"] = float(C_["dias"].mean()) if len(C_) else np.nan
    out["pregões médios (fechadas)"] = float(C_["pregoes"].mean()) if len(C_) else np.nan
    out["valorização (R$)"] = float(df["valorizacao"].sum())
    out["valorização %"] = 100 * out["valorização (R$)"] / aplic
    out["rendimentos (R$)"] = float(df["rend"].sum())
    out["rendimentos %"] = 100 * out["rendimentos (R$)"] / aplic
    out["taxas (R$)"] = float(df["taxas"].sum())
    out["resultado antes do imposto (R$)"] = res
    out["resultado antes do imposto %"] = 100 * res / aplic
    out["Selic líquida no mesmo dinheiro (R$)"] = sel
    out["Selic líquida %"] = 100 * sel / aplic
    out["diferença antes do imposto (R$)"] = res - sel
    out["diferença antes do imposto (pontos)"] = 100 * (res - sel) / aplic
    out["% com resultado > 0 (fechadas)"] = 100 * float((C_["resultado"] > 0).mean()) if len(C_) else np.nan
    out["% que ganharam da Selic (fechadas)"] = 100 * float((C_["dif_antes"] > 0).mean()) if len(C_) else np.nan
    g = C_[C_["resultado_pct"] > 0]
    p = C_[C_["resultado_pct"] <= 0]
    out["lucro médio das com ganho %"] = 100 * float(g["resultado_pct"].mean()) if len(g) else np.nan
    out["n com ganho"] = len(g)
    out["prejuízo médio das com perda %"] = 100 * float(p["resultado_pct"].mean()) if len(p) else np.nan
    out["n com perda"] = len(p)
    out["preço sobre valor patrimonial médio na entrada (x)"] = float(C_["pvp_e"].mean()) if len(C_) else np.nan
    out["preço sobre valor patrimonial médio na saída (x)"] = float(C_["pvp_s"].mean()) if len(C_) else np.nan
    q = C_["queda"].to_numpy(float)
    out["queda média %"] = 100 * float(q.mean()) if len(q) else np.nan
    if len(C_):
        j = int(np.argmin(q))
        out["pior queda (com o fundo) %"] = (f"{br(100 * q[j], 1)}% ({C_.iloc[j]['fundo']}, "
                                             f"entrada {C_.iloc[j]['entrada']:%d/%m/%Y})")
        kq = max(1, int(round(0.10 * len(q))))
        out["média das 10% piores quedas %"] = 100 * float(np.sort(q)[:kq].mean())
    else:
        out["pior queda (com o fundo) %"] = "nd"
        out["média das 10% piores quedas %"] = np.nan
    ab = C_[C_["abaixo"]]
    vb = ab[ab["voltou"] == "sim"]
    out["pregões da entrada até o ponto mais baixo (das que caíram)"] = float(ab["pregoes_fundo"].mean()) if len(ab) else np.nan
    out["% que voltou ao preço de entrada (das que caíram) %"] = 100 * len(vb) / len(ab) if len(ab) else np.nan
    out["pregões do ponto mais baixo até voltar"] = float(vb["p_volta"].mean()) if len(vb) else np.nan
    for m in MOTIVOS:
        out[f"saída: {m}"] = int((df["mot"] == m).sum())
    return out


def tabela_balanco(c, sg):
    sub = REC[(REC["carteira"] == c) & (REC["saida"] == sg)]
    cols = {}
    for ano in sorted(sub["ano"].unique()):
        cols[str(int(ano))] = balanco(sub[sub["ano"] == ano])
    cols["TOTAL"] = balanco(sub)
    return pd.DataFrame(cols)


def imprime_balanco(tab):
    cel = pd.DataFrame(index=tab.index, columns=tab.columns, dtype=object)
    for col in tab.columns:
        cel[col] = [fmt_val(k_, v) for k_, v in tab[col].items()]
    print(cel.to_string())


COMBOS = []
for c in ["A", "B"]:
    COMBOS.append((c, "S1"))
    if ESCOLHIDA[c] != "S1":
        COMBOS.append((c, ESCOLHIDA[c]))
print("\n==================== BALANÇO ANO A ANO (ano da ENTRADA) ====================")
print("(valores em R$ e % incluem em aberto avaliado pelo ultimo preco; estatisticas de saida so fechadas)")
BAL = {}
for c, sg in COMBOS:
    BAL[(c, sg)] = tabela_balanco(c, sg)
    print(f"\n--- carteira {c}, saida {sg} ({NOME_SAIDA[sg]})" + ("  [melhor da ESCOLHA]" if sg == ESCOLHIDA[c] and sg != "S1" else ""))
    imprime_balanco(BAL[(c, sg)])

print("\n==================== IMPOSTO POR ANO CIVIL DA VENDA (com abatimento) ====================")
IMP_ANO = {}
for c, sg in COMBOS:
    sub = REC[(REC["carteira"] == c) & (REC["saida"] == sg) & (REC["fechada"])]
    IMP_ANO[(c, sg)] = sub.groupby(sub["data_saida"].dt.year)["imposto"].sum()
anos_all = sorted(set().union(*[set(s.index) for s in IMP_ANO.values()]))
imp_df = pd.DataFrame({f"{c}/{sg}": IMP_ANO[(c, sg)].reindex(anos_all).fillna(0.0) for c, sg in COMBOS})
imp_df.index = [str(a) for a in imp_df.index]
imp_df.loc["TOTAL"] = imp_df.sum()
print(pd.DataFrame({col: [brl(v) for v in imp_df[col]] for col in imp_df.columns}, index=imp_df.index).to_string())


# ---------------------------------------------------------------- sensibilidade a dados suspeitos
print("\n==================== SENSIBILIDADE A DADOS SUSPEITOS (salto de preço acima de 25% em um pregão) ====================")
SENS_LISTA = []
for c in ["A", "B", "C"]:
    for sg in sorted({"S1", ESCOLHIDA[c]}, key=SIGS.index):
        sub = REC[(REC["carteira"] == c) & (REC["saida"] == sg)]
        com = metricas(sub, sub["imposto"])
        sem_df = sub[~sub["salto"]]
        sem = metricas(sem_df, imposto_mes(sem_df)[0])
        n_s = int(sub["salto"].sum())
        print(f"\ncarteira {c}, saida {sg}: ordens com salto25 = {n_s} de {len(sub)}")
        print(f"  COM todas:  resultado liquido {brl(com['resultado líquido (R$)'])}; diferença para a Selic "
              f"{brl(com['diferença para a Selic (R$)'])}; retorno ao ano {br(com['retorno ao ano sobre o dinheiro aplicado (%)'], 1)}%")
        print(f"  SEM salto25: resultado liquido {brl(sem['resultado líquido (R$)'])}; diferença para a Selic "
              f"{brl(sem['diferença para a Selic (R$)'])}; retorno ao ano {br(sem['retorno ao ano sobre o dinheiro aplicado (%)'], 1)}%")
        for r in sub[sub["salto"]].itertuples(index=False):
            SENS_LISTA.append(dict(carteira=c, saida=sg, fundo=r.fundo, entrada=r.entrada, data_salto=r.salto_data,
                                   variacao=r.salto_var))
if SENS_LISTA:
    sl = pd.DataFrame(SENS_LISTA)
    print("\nFundos com salto25 (carteira, saida, fundo, entrada, data do salto, variacao do fechamento):")
    for r in sl.itertuples(index=False):
        print(f"  {r.carteira} {r.saida} {r.fundo}: entrada {r.entrada:%d/%m/%Y}, salto em {r.data_salto:%d/%m/%Y}, "
              f"variacao {br(100 * r.variacao, 1)}%")
else:
    print("nenhum salto25 encontrado")


# ---------------------------------------------------------------- cortes de rendimento (carteira A e B, saida S1L)
def primeiro_corte(F, rec):
    """Primeiro aviso com data_conhecido em (entrada; saida] e valor <= 0,85 x rendimento da entrada."""
    f = F["nome"]
    re_ = rec["rend_entrada"]
    if f not in RDC or not (re_ > 0):
        return None
    dc, bd, vl = RDC[f]
    D = F["dates"][rec["e"]]
    S = np.datetime64(pd.Timestamp(rec["data_saida"]).date(), "D")
    a = int(np.searchsorted(dc, D, "right"))
    b = int(np.searchsorted(dc, S, "right"))
    if b <= a:
        return None
    idx = np.flatnonzero(vl[a:b] <= 0.85 * re_)
    if not idx.size:
        return None
    j = a + int(idx[0])
    seg = vl[j + 1:j + 7]
    hit = np.flatnonzero(seg >= 0.95 * re_)
    dcorte = dc[j]
    cidx = int(np.searchsorted(F["dates"], dcorte, "left"))
    preco_c = float(F["A"][cidx]) if cidx < F["n"] else np.nan
    dia_c = F["dates"][cidx] if cidx < F["n"] else None
    res_c = np.nan
    if cidx < F["n"] and cidx > rec["e"] and np.isfinite(preco_c):
        cot, valor = rec["cot"], rec["valor"]
        venda = cot * preco_c
        rend_ate = rend_val(f, D, dia_c, False) * cot
        taxas = B3 * valor + B3 * venda
        res_c = (venda - valor + rend_ate - taxas) / valor
    return dict(data_corte=pd.Timestamp(dcorte), valor_corte=float(vl[j]), queda_rend=float(vl[j] / re_ - 1),
                seguintes=[float(x) for x in seg] + [np.nan] * (6 - len(seg)),
                voltou=bool(hit.size), em_quantos=int(hit[0] + 1) if hit.size else np.nan,
                preco_corte=preco_c, res_corte_pct=res_c)


def fato_proximo(f, dc):
    g = ANF.get(f)
    if g is None:
        return None
    dd = (g["data"] - dc).dt.days.to_numpy()
    m = (dd >= -20) & (dd <= 10)
    if not m.any():
        return None
    j = int(np.flatnonzero(m)[np.argmin(np.abs(dd[m]))])
    return g.iloc[j]


CORTE_INFO = {}
for i, r in REC.iterrows():
    F = ENT[r["eid"]]["F"]
    rec = dict(rend_entrada=r["rend_entrada"], e=r["e"], cot=r["cot"], valor=r["valor"],
               data_saida=r["data_saida"], fundo=r["fundo"])
    CORTE_INFO[i] = primeiro_corte(F, rec)
REC["corte"] = [CORTE_INFO[i] is not None for i in REC.index]

print("\n==================== CORTES DE RENDIMENTO (saida S1L) ====================")
print("(corte = primeiro aviso com data_conhecido apos a entrada e ate a saida, com valor <= 85% do rendimento da entrada)")
CORTE_ROWS = []
for c in ["A", "B"]:
    sub = REC[(REC["carteira"] == c) & (REC["saida"] == "S1L")]
    print(f"\n--- carteira {c}: ordens S1L = {len(sub)}")
    sub_c = sub[sub["corte"]]
    tot_c = len(sub_c)
    por_ano = pd.DataFrame({"com corte": sub.groupby("ano")["corte"].sum(), "sem corte": sub.groupby("ano")["corte"].apply(lambda s: int((~s).sum())),
                            "total": sub.groupby("ano").size()})
    print(por_ano.to_string())
    print(f"total com corte = {tot_c}; sem corte = {len(sub) - tot_c}")
    voltaram = []
    for i, r in sub_c.iterrows():
        ci = CORTE_INFO[i]
        fato = fato_proximo(r["fundo"], ci["data_corte"])
        CORTE_ROWS.append(dict(
            carteira=c, fundo=r["fundo"], tipo=r["tipo"], entrada=r["entrada"], rend_e=r["rend_entrada"],
            data_corte=ci["data_corte"], valor_corte=ci["valor_corte"], queda_rend=ci["queda_rend"],
            seguintes=ci["seguintes"], voltou=ci["voltou"], em_quantos=ci["em_quantos"],
            preco_corte=ci["preco_corte"], res_corte=ci["res_corte_pct"],
            situacao="Em aberto" if r["mot"] == ABERTO else "Fechada", res_s1l=r["resultado_pct"],
            data_saida=r["data_saida"], fato_tipo=(fato["tipo"] if fato is not None else "nenhum"),
            fato_data=(fato["data"] if fato is not None else pd.NaT),
            fato_texto=(str(fato["inicio_do_texto"])[:160] if fato is not None else "")))
        voltaram.append(ci["voltou"])
    cr = pd.DataFrame([x for x in CORTE_ROWS if x["carteira"] == c])
    if len(cr):
        print(f"% dos cortes em que o rendimento voltou (>= 95% em 6 avisos seguintes): {br(100 * cr['voltou'].mean(), 1)}%")
        for flag, nome in [(True, "voltou"), (False, "não voltou")]:
            m = cr[cr["voltou"] == flag]
            if len(m):
                print(f"  {nome} (n={len(m)}): resultado médio de quem segurou (S1L) = {br(100 * m['res_s1l'].mean(), 1)}%; "
                      f"resultado médio se saísse no corte = {br(100 * m['res_corte'].mean(), 1)}%")
        print("fato relevante mais próximo (janela de 20 dias antes a 10 dias depois do corte):")
        print(cr["fato_tipo"].value_counts().to_string())

print("\nLista de cortes gravada em planilhas/kairi_cortes.csv (carteiras A e B).")
cort_df = pd.DataFrame(CORTE_ROWS)
if len(cort_df):
    lista = pd.DataFrame({
        "Carteira": cort_df["carteira"],
        "Fundo": cort_df["fundo"],
        "Tipo do fundo": cort_df["tipo"],
        "Data de entrada": pd.to_datetime(cort_df["entrada"]),
        "Rendimento mensal na entrada (R$/cota)": cort_df["rend_e"].round(4),
        "Data do corte (aviso)": pd.to_datetime(cort_df["data_corte"]),
        "Valor do corte (R$/cota)": cort_df["valor_corte"].round(4),
        "Queda do rendimento no corte (%)": (100 * cort_df["queda_rend"]).round(1),
    })
    for j_ in range(6):
        lista[f"Aviso seguinte {j_ + 1} (R$/cota)"] = [x["seguintes"][j_] if not isnan(x["seguintes"][j_]) else np.nan
                                                       for x in cort_df.to_dict("records")]
        lista[f"Aviso seguinte {j_ + 1} (R$/cota)"] = lista[f"Aviso seguinte {j_ + 1} (R$/cota)"].round(4)
    lista["Voltou a 95% do rendimento nos 6 avisos seguintes (sim/não)"] = np.where(cort_df["voltou"], "sim", "não")
    lista["Em quantos avisos voltou"] = cort_df["em_quantos"].astype("Int64")
    lista["Preço na abertura do dia do corte (R$)"] = cort_df["preco_corte"].round(2)
    lista["Resultado (%) se saísse na abertura do corte"] = (100 * cort_df["res_corte"]).round(1)
    lista["Situação na S1L"] = cort_df["situacao"]
    lista["Resultado (%) na S1L (ou atual, se em aberto)"] = (100 * cort_df["res_s1l"]).round(1)
    lista["Data de saída na S1L (ou do último preço)"] = pd.to_datetime(cort_df["data_saida"])
    lista["Fato relevante próximo: tipo"] = cort_df["fato_tipo"]
    lista["Fato relevante próximo: data"] = pd.to_datetime(cort_df["fato_data"])
    lista["Fato relevante próximo: início do texto (160 caracteres)"] = cort_df["fato_texto"]
    lista.to_csv(PL / "kairi_cortes.csv", **OPC)


# ---------------------------------------------------------------- planilha de ordens por saida
PLAN_SIGS = ["S1", "S1L", "S2L", "SCL", "F50L", "F62L", "M127L"]
pl = REC[REC["carteira"].isin(["A", "B"]) & REC["saida"].isin(PLAN_SIGS)].copy()
pl["ordem_saida"] = pl["saida"].map({s: i for i, s in enumerate(PLAN_SIGS)})
pl = pl.sort_values(["carteira", "ordem_saida", "entrada", "fundo"]).reset_index(drop=True)
pl_out = pd.DataFrame({
    "Carteira": pl["carteira"],
    "Regra de saída": pl["nome_saida"],
    "Fundo": pl["fundo"],
    "Tipo do fundo": pl["tipo"],
    "Data do sinal": pl["sinal"],
    "Data de entrada": pl["entrada"],
    "Preço de entrada (R$)": pl["E"].round(2),
    "Cotas": pl["cot"].astype(int),
    "Valor da ordem (R$)": pl["valor"].round(2),
    "Cota sobre valor patrimonial na entrada": pl["pvp_e"].round(2),
    "Alvo da saída no dia da entrada (R$)": pl["alvo_dia"].round(2),
    "Distância do alvo (%)": (100 * (pl["alvo_dia"] / pl["E"] - 1)).round(1),
    "Situação": np.where(pl["mot"] == ABERTO, "Em aberto", "Fechada"),
    "Data de saída (ou do último preço)": pl["data_saida"],
    "Preço de saída (ou atual) (R$)": pl["px"].round(2),
    "Cota sobre valor patrimonial na saída": pl["pvp_s"].round(2),
    "Motivo da saída": pl["mot"],
    "Dias corridos": pl["dias"],
    "Pregões": pl["pregoes"],
    "Valorização (R$)": pl["valorizacao"].round(2),
    "Valorização (%)": (100 * pl["valorizacao"] / pl["valor"]).round(1),
    "Rendimentos recebidos (R$)": pl["rend"].round(2),
    "Rendimentos (%)": (100 * pl["rend"] / pl["valor"]).round(1),
    "Taxas (R$)": pl["taxas"].round(2),
    "Resultado antes do imposto (R$)": pl["resultado"].round(2),
    "Resultado antes do imposto (%)": (100 * pl["resultado_pct"]).round(1),
    "Selic líquida no mesmo período (R$)": pl["sel_rs"].round(2),
    "Selic líquida (%)": (100 * pl["sel_pct"]).round(1),
    "Diferença para a Selic (R$)": pl["dif_antes"].round(2),
    "Ganhou da Selic (sim/não)": np.where(pl["dif_antes"] > 0, "sim", "não"),
    "Maior queda abaixo da entrada (%)": (100 * pl["queda"]).round(1),
    "Pregões até o ponto mais baixo": pl["pregoes_fundo"].where(pl["abaixo"]).astype("Int64"),
    "Voltou ao preço de entrada (sim/não/não caiu)": pl["voltou"],
    "Maior alta acima da entrada (%)": (100 * pl["alta"]).round(1),
    "Teve corte de rendimento (sim/não)": np.where(pl["corte"], "sim", "não"),
    "Dado suspeito (sim/não)": np.where(pl["mot"] == GUARDA, "sim", "não"),
})
pl_out.to_csv(PL / "kairi_ordens_saidas.csv", **OPC)
print(f"\ngravados: planilhas/kairi_ordens_saidas.csv ({len(pl_out)} linhas); cortes em planilhas/kairi_cortes.csv")

# comparacao gravada em tecnico
comp_rows = []
for c in CARTEIRAS:
    for per, tab in [("TOTAL", TAB_TOTAL[c]), ("ESCOLHA", TAB_ESC[c]), ("CONFERÊNCIA", TAB_CONF[c])]:
        t = tab.copy()
        t.insert(0, "Período", per)
        t.insert(0, "Carteira", c)
        t.insert(2, "Saída", t.index)
        t.insert(3, "Regra de saída", [NOME_SAIDA[s] for s in t.index])
        comp_rows.append(t.reset_index(drop=True))
comp_df = pd.concat(comp_rows, ignore_index=True)
for col in comp_df.columns:
    if comp_df[col].dtype.kind == "f":
        comp_df[col] = comp_df[col].round(1 if "%" in col else 2)
comp_df.to_csv(TEC / "kairi_saidas_comparacao.csv", **OPC)
print(f"gravado: planilhas/tecnico/kairi_saidas_comparacao.csv ({len(comp_df)} linhas)")


# ---------------------------------------------------------------- CONFERENCIAS
print("\n==================== CONFERÊNCIAS ====================")

# 1) reproduz as entradas e a S1 de kairi_ordens.py (planilha existente, so leitura)
print("\n1) reproducao das entradas e da S1 frente a planilhas/kairi_ordens.csv (lida, nao regravada)")
print("   (o TOTAL do kairi_ordens.py soma so as FECHADAS: resultado com imposto por ordem e Selic)")
for c in CARTEIRAS:
    print(f"   carteira {c}: ordens = {int((REC[(REC.carteira == c) & (REC.saida == 'S1')]).shape[0])}; "
          f"fechadas S1 = {int(((REC.carteira == c) & (REC.saida == 'S1') & REC.fechada).sum())}")
old = pd.read_csv(PL / "kairi_ordens.csv", sep=";", decimal=",", encoding="utf-8-sig")
_oa = old[(old["Carteira"] == "A") & (old["Situação"] == "Fechada")]
_na = REC[(REC.carteira == "A") & (REC.saida == "S1") & REC.fechada]
print(f"   A/S1 fechadas: resultado com imposto por ordem (antigo) = {brl(_oa['Resultado (R$)'].sum(), 0)} "
      f"(esperado R$ 78.052); Selic = {brl(_na['sel_rs'].sum(), 0)} (esperado R$ 23.592)")
print(f"   A/S1 fechadas: resultado ANTES do imposto (novo) = {brl(_na['resultado'].sum(), 0)}; "
      f"antigo antes do imposto = {brl(_oa['Resultado (R$)'].sum() + _oa['Imposto (R$)'].sum(), 0)}")
old["Data de entrada"] = pd.to_datetime(old["Data de entrada"], format="%d/%m/%Y")
old["Data de saída (ou do último preço)"] = pd.to_datetime(old["Data de saída (ou do último preço)"], format="%d/%m/%Y")
new = REC[REC["saida"] == "S1"].copy()
new["Data de entrada"] = new["entrada"]
mrg = old.merge(new, left_on=["Carteira", "Fundo", "Data de entrada"], right_on=["carteira", "fundo", "Data de entrada"],
                how="outer", indicator=True)
print(f"   linhas da planilha antiga = {len(old)}; novas = {len(new)}; cruzadas = {int((mrg['_merge'] == 'both').sum())}")
ok = mrg[mrg["_merge"] == "both"]
diff_exit = ok[(ok["Data de saída (ou do último preço)"] != ok["data_saida"]) | (ok["Motivo da saída"] != ok["mot"]) |
               ((ok["Preço de saída (ou atual) (R$)"] - ok["px"]).abs() > 0.006)]
diff_cot = ok[ok["Cotas"] != ok["cot"]]
diff_res = ok[((ok["Resultado (R$)"] + ok["Imposto (R$)"]) - ok["resultado"]).abs() > 0.02]
print(f"   saidas S1 diferentes (data, motivo ou preco): {len(diff_exit)}; cotas diferentes: {len(diff_cot)}; "
      f"resultado antes do imposto diferente (antigo resultado + imposto antigo vs novo): {len(diff_res)}")
for c in ["A", "B", "C"]:
    o_ = old[old["Carteira"] == c]
    n_ = new[new["carteira"] == c]
    print(f"   carteira {c}: total S1 antigo: resultado com imposto por ordem {brl(o_['Resultado (R$)'].sum(), 0)}; "
          f"imposto por ordem {brl(o_['Imposto (R$)'].sum(), 0)}; antes do imposto (soma) {brl(o_['Resultado (R$)'].sum() + o_['Imposto (R$)'].sum(), 0)}")
    print(f"           novo S1: resultado antes do imposto {brl(n_['resultado'].sum(), 0)}; Selic {brl(n_['sel_rs'].sum(), 0)}; "
          f"imposto com abatimento {brl(n_['imposto'].sum(), 0)}; resultado liquido {brl(n_['resultado'].sum() - n_['imposto'].sum(), 0)}")
if len(diff_exit):
    print(diff_exit[["Carteira", "Fundo", "Data de entrada"]].head(5).to_string(index=False))

# 2) uma ordem da carteira B: E, M0, P e alvos
print("\n2) ordem da carteira B (primeira com saida S1 por volta a media):")
b_ex = REC[(REC.carteira == "B") & (REC.saida == "S1") & (REC.mot == VOLTA)].iloc[0]
print(f"   fundo {b_ex['fundo']}; sinal {b_ex['sinal']:%d/%m/%Y}; entrada {b_ex['entrada']:%d/%m/%Y} a R$ {br(b_ex['E'], 4)}; "
      f"cotas {int(b_ex['cot'])}")
print(f"   M0 (media dos 200 fechamentos ate d-1, congelada) = {br(b_ex['M0'], 4)}; P (pico de 252 pregoes ate d) = {br(b_ex['P'], 4)}")
for r in REC[(REC.carteira == "B") & (REC.fundo == b_ex["fundo"]) & (REC.entrada == b_ex["entrada"])].itertuples(index=False):
    alvo_txt = f"alvo na saida {br(r.alvo_saida, 4)}" if not isnan(r.alvo_saida) else "sem alvo"
    print(f"   {r.saida:<6} alvo no dia da entrada {br(r.alvo_dia, 4)}; {alvo_txt}; saida {r.data_saida:%d/%m/%Y} "
          f"a R$ {br(r.px, 4)} ({r.mot}); pregoes {r.pregoes}")

# 3) imposto: 6 primeiros meses com venda, carteira B, S1
print("\n3) imposto: carteira B, saida S1, primeiros 6 meses com venda")
tb = IMP_TAB[("B", "S1")].head(6).copy()
tb.index = tb.index.astype(str)
print(pd.DataFrame({col: [brl(v) for v in tb[col]] for col in tb.columns}, index=tb.index).to_string())

# 4) alvos usam so informacao ate o dia do sinal (ou ate k-1 na media)
print("\n4) conferencia por codigo dos alvos (todas as ordens x saidas):")
n_med = n_fix = 0
for idx_en, en in enumerate(ENT):
    F, s, e = en["F"], en["s"], en["e"]
    assert e == s + 1
    E = float(F["A"][e])
    M0_dir = float(F["C"][s - N:s].mean())                             # fechamentos s-200..s-1
    P_dir = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))         # fechamentos s-251..s
    assert abs(M0_dir - float(F["mP"][s])) < 1e-9
    for sub in REC[REC["eid"] == idx_en].itertuples(index=False):
        reg = next(r for r in REGRAS if r["sig"] == sub.saida)
        k = int(sub.k)
        if reg["tipo"] == "fixo":
            T = reg["calc"](E, M0_dir, P_dir)
            assert abs(T - sub.alvo_saida) < 1e-9
            if sub.mot == ALVO:
                assert F["H"][k] >= T
            # nenhuma maxima tocou o alvo antes de k
            assert not np.any(F["H"][e + 1:k] >= T)
            n_fix += 1
        elif sub.mot == VOLTA:
            # media usada na venda = media dos fechamentos k-200..k-1; primeira maxima >= media
            thr = float(F["C"][k - N:k].mean())
            if reg["tipo"] == "piso":
                thr = max(thr, E)
            assert F["H"][k] >= thr - 1e-9
            assert abs(float(sub.alvo_saida) - thr) < 1e-9
            for kk in range(e + 1, k):
                tk = float(F["C"][kk - N:kk].mean())
                if reg["tipo"] == "piso":
                    tk = max(tk, E)
                assert F["H"][kk] < tk, (en["fundo"], kk)
            n_med += 1
print(f"   ASSERTS PASSARAM: alvos fixos com dados ate o sinal ({n_fix} ordens x saidas fixas); saidas por media "
      f"com media dos 200 ate k-1 e primeira maxima >= alvo ({n_med} ordens x saidas por media). "
      "Entrada = abertura de s+1, depois do sinal.")

# 5) saidas sem prazo: ordens em aberto ha mais de 252 pregoes
print("\n5) saidas sem prazo: ordens em aberto ha mais de 252 pregoes")
for c in CARTEIRAS:
    for sg in [r["sig"] for r in REGRAS if not r["prazo"]]:
        sub = REC[(REC.carteira == c) & (REC.saida == sg) & (~REC.fechada) & (REC.pregoes > PRAZO)]
        if len(sub):
            print(f"   carteira {c}, {sg}: {len(sub)} ordens; valorizacao media {br(100 * sub['valorizacao'].div(sub['valor']).mean(), 1)}%")
            if sg == "S1L" or sg == "S2L":
                for r in sub[sub["valorizacao"].div(sub["valor"]) < -0.5].itertuples(index=False):
                    print(f"      {r.fundo}: entrada {r.entrada:%d/%m/%Y}, ultimo preco {br(r.px, 4)}, "
                          f"valorizacao {br(100 * r.valorizacao / r.valor, 1)}% ; verificar preco final (sem negociacao recente?)")

print("\n==================== RESUMO DE ENTRADAS ====================")
for c in CARTEIRAS:
    print(f"carteira {c}: ordens = {int((REC.carteira == c).sum() // len(SIGS))}; "
          f"em aberto na S1 = {int(((REC.carteira == c) & (REC.saida == 'S1') & (~REC.fechada)).sum())}")
print(f"\nTempo total: {time.time() - T0:.1f} s")
