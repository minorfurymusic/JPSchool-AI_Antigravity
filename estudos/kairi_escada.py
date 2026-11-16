"""Saida em escada do Indice de Kairi (FIIs), comparada com as saidas de estudos/kairi_saidas.py.

As ENTRADAS sao as mesmas de kairi_saidas.py (ordens das carteiras A, B e C). As funcoes de entrada,
conta, imposto, Selic, guarda de qualidade e metricas foram COPIADAS daquele arquivo (ele executa tudo
no import e regrava planilhas existentes, por isso nao e importado). A reproducao da S1 e conferida no fim.

Saidas simuladas:
  Referencias: S1 (volta a media, prazo 252), S2L, F50L, F62L (do script anterior) e as usadas na Parte 1
               (F38L, F100L, M127L, M162L, SCL).
  E1..E8: escadas com piso (media movel MM(k) ou Fibonacci) e teto; E8 com degraus.
  E9, E10: armada na media movel; sai quando o fechamento cai 5% (8%) abaixo do maior fechamento desde que armou.

Gravados: planilhas/kairi_escada.csv (ordens A e B: S1, E1, E5, E8) e planilhas/tecnico/kairi_escada_comparacao.csv.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_escada.py 2>&1 | tee dados/kairi_escada.txt
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
ALVO = "alvo atingido"
PRAZO_M = "prazo"
SAIU = "fundo saiu da bolsa"
GUARDA = "dado suspeito"
ABERTO = "em aberto"
TETO = "teto"
SIMPLES = "saída simples no piso"   # escada com teto <= piso na entrada: vende no nivel do piso (1a toque)
RECUOU = "recuou ao piso"
QUEDA = "queda do máximo"
MOTIVOS_ESC = [TETO, SIMPLES, RECUOU, PRAZO_M, SAIU, GUARDA, ABERTO, QUEDA]


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
    if "(x)" in key:
        return br(v, 2)
    if "%" in key:
        return br(v, 1) + "%"
    return br(v, 1)


def imprime_tab(tab, keys=None):
    cel = pd.DataFrame(index=tab.index, columns=tab.columns, dtype=object)
    for col in tab.columns:
        cel[col] = [fmt_val(col, v) for v in tab[col]]
    if keys is not None:
        cel = cel[keys]
    print(cel.to_string())


# ---------------------------------------------------------------- carga (copiada de kairi_saidas.py)
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
                    aberto=int(mi[-1]) >= NM - 21)

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


# ---------------------------------------------------------------- saida S1 (copiada) e conta (copiada)
def sair(F, e, tipo, prazo, E, T):
    """Saida de uma ordem comprada na abertura de e (copiada de kairi_saidas.py).

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
            thr = F["mN"][e:W]
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
    alta_pos = float(np.max(F["H"][e + 1:k + 1])) / E - 1 if k > e else np.nan
    return dict(E=E, valor=valor, venda=venda, valorizacao=valorizacao, taxas=taxas, rend=rend,
                resultado=resultado, resultado_pct=resultado / valor, sel_pct=sel_pct, sel_rs=valor * sel_pct,
                dias=dias, pregoes=int(k - e), px=float(px), data_saida=S, mi_x=ix, data_entrada=D,
                queda=queda, abaixo=abaixo, pregoes_fundo=pr, voltou=voltou, p_volta=p_volta, alta=alta,
                alta_pos=alta_pos, mi_e=ie, pvp_e=E / F["VP"][e] if F["VP"][e] > 0 else np.nan,
                pvp_s=px / F["VP"][k] if F["VP"][k] > 0 else np.nan)


# ---------------------------------------------------------------- entradas (copiado de kairi_saidas.gerar_entradas)
def gerar_entradas(nome):
    """Mesmas entradas do kairi_saidas.py: a ocupacao 'um fundo por vez' usa a saida S1 (volta a media, prazo)."""
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


# ---------------------------------------------------------------- saidas de referencia (do script anterior)
def fib(f):
    return lambda E, M0, P: E + f * (P - E)


def ext(f):
    return lambda E, M0, P: E + f * (M0 - E)


def media_do_sinal(E, M0, P):
    return M0


REGRAS_ANT = [
    dict(sig="S1", nome="Volta à média (prazo de 252 pregões)", tipo="media", prazo=True),
    dict(sig="S2L", nome="Volta à média, nunca abaixo da entrada (sem prazo)", tipo="piso", prazo=False),
    dict(sig="SCL", nome="Média dos 200 pregões do sinal (sem prazo)", tipo="fixo", calc=media_do_sinal, prazo=False),
    dict(sig="F38L", nome="Fibonacci 38,2% do pico (sem prazo)", tipo="fixo", calc=fib(0.382), prazo=False),
    dict(sig="F50L", nome="Fibonacci 50% do pico (sem prazo)", tipo="fixo", calc=fib(0.5), prazo=False),
    dict(sig="F62L", nome="Fibonacci 61,8% do pico (sem prazo)", tipo="fixo", calc=fib(0.618), prazo=False),
    dict(sig="F100L", nome="Pico de 252 pregões (sem prazo)", tipo="fixo", calc=fib(1.0), prazo=False),
    dict(sig="M127L", nome="Extensão 127,2% da média do sinal (sem prazo)", tipo="fixo", calc=ext(1.272), prazo=False),
    dict(sig="M162L", nome="Extensão 161,8% da média do sinal (sem prazo)", tipo="fixo", calc=ext(1.618), prazo=False),
]


# ---------------------------------------------------------------- escadas (novas)
def fibv(f):
    return lambda E, M0, P: E + f * (P - E)


ESCADAS = [
    dict(sig="E1", nome="Escada: piso média móvel, teto Fibonacci 61,8%", modo="pt", piso="mm", teto=fibv(0.618)),
    dict(sig="E2", nome="Escada: piso média móvel, teto Fibonacci 50%", modo="pt", piso="mm", teto=fibv(0.5)),
    dict(sig="E3", nome="Escada: piso média móvel, teto Fibonacci 100%", modo="pt", piso="mm", teto=fibv(1.0)),
    dict(sig="E4", nome="Escada: piso média móvel, teto 127,2% da média do sinal", modo="pt", piso="mm",
         teto=lambda E, M0, P: E + 1.272 * (M0 - E)),
    dict(sig="E5", nome="Escada: piso Fibonacci 38,2%, teto Fibonacci 61,8%", modo="pt", piso=fibv(0.382),
         teto=fibv(0.618)),
    dict(sig="E6", nome="Escada: piso Fibonacci 38,2%, teto Fibonacci 100%", modo="pt", piso=fibv(0.382),
         teto=fibv(1.0)),
    dict(sig="E7", nome="Escada: piso Fibonacci 50%, teto Fibonacci 100%", modo="pt", piso=fibv(0.5), teto=fibv(1.0)),
    dict(sig="E8", nome="Escada de degraus (MM do dia do armar, F38, F50, F61,8, F100)", modo="degraus"),
    dict(sig="E9", nome="Armada na média móvel; sai com fechamento 5% abaixo do maior", modo="queda", x=0.05),
    dict(sig="E10", nome="Armada na média móvel; sai com fechamento 8% abaixo do maior", modo="queda", x=0.08),
]
ESC_SIGS = [c["sig"] for c in ESCADAS]


def niveis(E, P, mm):
    """Degraus acima da entrada: MM do dia (mm) e Fibonacci 38,2/50/61,8/100 (ordenados, so > E)."""
    cand = [mm, E + 0.382 * (P - E), E + 0.5 * (P - E), E + 0.618 * (P - E), E + 1.0 * (P - E)]
    return sorted(v for v in cand if np.isfinite(v) and v > E)


def pmax(a, v):
    return max(a, v) if np.isfinite(a) else v


def pmin(a, v):
    return min(a, v) if np.isfinite(a) else v


def escada(F, e, E, M0, P, cfg):
    """Simula uma escada. Regras (pregao k, informacao do proprio dia; piso do dia conhecido na abertura):
      - desarmada: arma no primeiro k com maxima(k) >= piso(k). Nesse dia, se maxima >= teto: vende teto.
      - armada, cada dia k2 > k: (1) minima <= piso(k2): vende min(abertura, piso) 'recuou ao piso';
        (2) senao maxima >= teto: vende max(abertura, teto) 'teto'. Piso e teto no mesmo dia: vale o piso.
      - nunca armada: reserva de 252 pregoes no fechamento ('prazo'). Armada nao tem prazo.
      - dado suspeito (salto de dado) antes da venda: sai no fechamento do dia anterior (como na S1).
    """
    last = F["n"] - 1
    A, H, L, C, bad, mP = F["A"], F["H"], F["L"], F["C"], F["bad"], F["mP"]
    modo = cfg["modo"]
    arm = None
    piso_fixo = None
    simples = False
    if modo == "pt":
        if cfg["piso"] != "mm":
            piso_fixo = cfg["piso"](E, M0, P)
        teto = cfg["teto"](E, M0, P)
        piso_e = mP[e] if piso_fixo is None else piso_fixo
        simples = teto <= piso_e          # T <= B no dia da entrada: saida simples no nivel B
        teto_e = teto
    elif modo == "degraus":
        lv0 = niveis(E, P, mP[e])
        piso_e = lv0[0] if lv0 else np.nan
        teto_e = lv0[-1] if lv0 else np.nan
    else:
        piso_e = np.nan
        teto_e = np.nan
    x = cfg.get("x")

    def piso_dia(k):
        return mP[k] if piso_fixo is None else piso_fixo

    def saida(k, mot, px, piso=np.nan):
        return dict(k=int(k), mot=mot, px=float(px), k_arm=(-1 if arm is None else int(arm)),
                    piso_e=float(piso_e), teto_e=float(teto_e), piso_v=float(piso))

    armado = False
    lv = top = None
    j_cur = -1
    piso_cur = np.nan
    maxc = np.nan
    fim = e + PRAZO
    for k in range(e + 1, last + 1):
        if not armado and k > fim:
            break
        if bad[k]:
            return saida(k - 1, GUARDA, C[k - 1])
        if not armado:
            if modo == "queda":
                if H[k] >= mP[k]:
                    armado = True
                    arm = k
                    maxc = C[k]
                continue
            if modo == "degraus":
                lv_k = niveis(E, P, mP[k])
                if not lv_k or H[k] < lv_k[0]:
                    continue
                armado = True
                arm = k
                lv = lv_k
                top = lv[-1]
                j = max(i for i, v in enumerate(lv) if v <= H[k])
                if j == len(lv) - 1:
                    return saida(k, TETO, pmax(A[k], top), top)
                j_cur = j
                piso_cur = lv[max(j - 1, 0)]
                continue
            b = piso_dia(k)
            if simples:
                if H[k] >= b:
                    arm = k
                    return saida(k, SIMPLES, pmax(A[k], b), b)
                continue
            if H[k] >= b:
                armado = True
                arm = k
                if H[k] >= teto_e:
                    return saida(k, TETO, pmax(A[k], teto_e), b)
            continue
        # armada (dias k > arm)
        if modo == "queda":
            maxc = max(maxc, C[k])
            if C[k] <= (1 - x) * maxc:
                if k + 1 > last:
                    break
                if bad[k + 1]:
                    return saida(k, GUARDA, C[k])
                px_n = A[k + 1] if np.isfinite(A[k + 1]) else C[k + 1]
                return saida(k + 1, QUEDA, px_n)
            continue
        if modo == "degraus":
            if L[k] <= piso_cur:
                return saida(k, RECUOU, pmin(A[k], piso_cur), piso_cur)
            if H[k] >= top:
                return saida(k, TETO, pmax(A[k], top), piso_cur)
            jj = max(i for i, v in enumerate(lv) if v <= H[k])
            if jj > j_cur:
                j_cur = jj
                piso_cur = lv[max(jj - 1, 0)]
            continue
        b = piso_dia(k)
        if L[k] <= b:
            return saida(k, RECUOU, pmin(A[k], b), b)
        if H[k] >= teto_e:
            return saida(k, TETO, pmax(A[k], teto_e), b)
        continue
    if not armado and e + PRAZO <= last:
        return saida(e + PRAZO, PRAZO_M, C[e + PRAZO])
    if F["aberto"]:
        return saida(last, ABERTO, C[last])
    return saida(last, SAIU, C[last])


# ---------------------------------------------------------------- registros: uma linha por (ordem, saida)
print("\n== ENTRADAS E SAIDAS ==")
ENT = []
ROWS = []
NOME_SAIDA = {r["sig"]: r["nome"] for r in REGRAS_ANT}
NOME_SAIDA.update({c["sig"]: c["nome"] for c in ESCADAS})
SIGS_ORD = [r["sig"] for r in REGRAS_ANT] + ESC_SIGS


def monta(nome, F, en, e, s, cot, E, M0, P, sig, k, mot, px, alvo_dia, alvo_saida, piso_e, teto_e, arm_k, piso_v):
    c = conta(F, e, k, mot, px, cot)
    arm_date = pd.Timestamp(F["dates"][arm_k]) if arm_k >= 0 else pd.NaT
    return dict(carteira=nome, saida=sig, nome_saida=NOME_SAIDA[sig], fundo=F["nome"],
                tipo=TIPO.get(F["nome"], "sem tipo"), sinal=pd.Timestamp(F["dates"][s]),
                entrada=pd.Timestamp(c["data_entrada"]), ano=pd.Timestamp(c["data_entrada"]).year,
                eid=len(ENT) - 1, e=e, s=s, k=k, cot=cot, M0=M0, P=P, E=E,
                alvo_dia=alvo_dia, alvo_saida=alvo_saida, piso_e=piso_e, teto_e=teto_e,
                k_arm=int(arm_k), arm=arm_date, piso_v=piso_v,
                mot=mot, px=c["px"], data_saida=pd.Timestamp(c["data_saida"]), dias=c["dias"],
                pregoes=c["pregoes"], valor=c["valor"], valorizacao=c["valorizacao"], rend=c["rend"],
                taxas=c["taxas"], resultado=c["resultado"], resultado_pct=c["resultado_pct"],
                sel_pct=c["sel_pct"], sel_rs=c["sel_rs"], queda=c["queda"], abaixo=c["abaixo"],
                pregoes_fundo=c["pregoes_fundo"], voltou=c["voltou"], p_volta=c["p_volta"], alta=c["alta"],
                alta_pos=c["alta_pos"], mi_e=c["mi_e"], mi_x=c["mi_x"], fechada=mot != ABERTO,
                pvp_e=c["pvp_e"], pvp_s=c["pvp_s"], dif_antes=c["resultado"] - c["sel_rs"],
                rend_entrada=float(F["R"][e]), data_entrada=pd.Timestamp(c["data_entrada"]))


for nome in CARTEIRAS:
    for en in gerar_entradas(nome):
        ENT.append(en)
        F, s, e, cot = en["F"], en["s"], en["e"], en["cot"]
        assert e == s + 1
        E = float(F["A"][e])
        M0 = float(F["mP"][s])                                       # media dos 200 ate d-1 (congelada)
        P = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))       # pico 252 ate d (fechamentos)
        eid = len(ENT) - 1
        for reg in REGRAS_ANT:
            T = reg["calc"](E, M0, P) if reg["tipo"] == "fixo" else np.nan
            k, mot, px, alvo_k = sair(F, e, reg["tipo"], reg["prazo"], E, T)
            if reg["tipo"] == "fixo":
                alvo_dia, alvo_saida = T, T
                piso_e, teto_e = np.nan, T
                arm_k = -1
                piso_v = np.nan
            else:
                alvo_dia, alvo_saida = M0, alvo_k
                piso_e, teto_e = (float(F["mP"][e]), np.nan)
                arm_k = k if mot == VOLTA else -1      # o unico 'toque' da media e a propria venda
                piso_v = float(F["mP"][k]) if mot == VOLTA else np.nan
            ROWS.append(monta(nome, F, en, e, s, cot, E, M0, P, reg["sig"], k, mot, px, alvo_dia, alvo_saida,
                              piso_e, teto_e, arm_k, piso_v))
        for cfg in ESCADAS:
            r = escada(F, e, E, M0, P, cfg)
            ROWS.append(monta(nome, F, en, e, s, cot, E, M0, P, cfg["sig"], r["k"], r["mot"], r["px"],
                              r["teto_e"], np.nan, r["piso_e"], r["teto_e"], r["k_arm"], r["piso_v"]))

REC = pd.DataFrame(ROWS)
REC.loc[~REC["fechada"], "mi_x"] = NM                                 # em aberto: dinheiro aplicado ate o fim
print(f"linhas (ordem x saida): {len(REC)}; ordens por carteira: "
      + ", ".join(f"{c}={int((REC.carteira == c).sum() // len(SIGS_ORD))}" for c in CARTEIRAS))


# ---------------------------------------------------------------- imposto com abatimento (copiado)
def imposto_mes(df):
    """20% sobre o ganho liquido (valorizacao - taxas) do mes da venda; prejuizo abate meses seguintes.
    Retorna (imposto alocado por ordem, tabela mensal). Em aberto nao paga imposto. (copiada)"""
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


REC["imposto"] = 0.0
for (c_, sg_), g in REC.groupby(["carteira", "saida"], sort=False):
    imp, tab = imposto_mes(g)
    REC.loc[g.index, "imposto"] = imp


# ---------------------------------------------------------------- metricas (copiadas, com a media por ordem fechada)
def pico_dinheiro(df):
    if df.empty:
        return 0.0
    ap = np.zeros(NM + 1)
    np.add.at(ap, df["mi_e"].to_numpy(int), df["valor"].to_numpy(float))
    np.add.at(ap, df["mi_x"].to_numpy(int), -df["valor"].to_numpy(float))
    return float(np.cumsum(ap)[I0:NM].max())


def metricas(df, imp):
    """Medida de comparacao (copiada). Todas as ordens em R$ e risco; estatisticas de saida so nas fechadas."""
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
        "Selic ao ano na mesma conta (%)": 100 * sel / anos if anos else np.nan,
        "resultado médio por ordem fechada (%)": 100 * float(C_["resultado_pct"].mean()) if nf else np.nan,
        "% fechadas com resultado > 0": 100 * float((C_["resultado"] > 0).mean()) if nf else np.nan,
        "% fechadas que ganharam da Selic": 100 * float((C_["dif_antes"] > 0).mean()) if nf else np.nan,
        "pior ordem (%)": 100 * float(df["resultado_pct"].min()) if n else np.nan,
        "pico de dinheiro aplicado ao mesmo tempo (R$)": pico_dinheiro(df),
    }


T1_KEYS = ["ordens", "fechadas", "em aberto", "dias corridos médios", "resultado líquido (R$)",
           "Selic líquida no mesmo dinheiro (R$)", "diferença para a Selic (R$)",
           "retorno ao ano sobre o dinheiro aplicado (%)", "Selic ao ano na mesma conta (%)",
           "resultado médio por ordem fechada (%)", "% fechadas com resultado > 0",
           "% fechadas que ganharam da Selic", "pior ordem (%)", "pico de dinheiro aplicado ao mesmo tempo (R$)"]
T2_KEYS = ["ordens", "em aberto", "resultado líquido (R$)", "diferença para a Selic (R$)",
           "retorno ao ano sobre o dinheiro aplicado (%)", "Selic ao ano na mesma conta (%)",
           "% fechadas com resultado > 0"]
ROT1 = ["S1", "F50L", "F62L", "S2L"] + ESC_SIGS


def mascara_escolha(sub):
    return sub["entrada"] <= CORTE_22


def mascara_conf(sub):
    return sub["entrada"] >= CONF_INI


def tab_periodo(car, mask, keys, sigs):
    linhas = {}
    for sg in sigs:
        sub = REC[(REC["carteira"] == car) & (REC["saida"] == sg)]
        if mask is not None:
            sub = sub[mask(sub)]
        # imposto alocado do grupo completo (mesma convencao de kairi_saidas.py)
        linhas[sg] = metricas(sub, sub["imposto"])
    return pd.DataFrame(linhas).T[keys]


TAB_T1 = {c: tab_periodo(c, None, T1_KEYS, ROT1) for c in CARTEIRAS}
TAB_ESC = {c: tab_periodo(c, mascara_escolha, T2_KEYS, ROT1) for c in CARTEIRAS}
TAB_CONF = {c: tab_periodo(c, mascara_conf, T2_KEYS, ROT1) for c in CARTEIRAS}


# ---------------------------------------------------------------- reproducao da S1 (conferencia 1)
print("\n==================== CONFERENCIA 1: REPRODUCAO DA S1 (TOTAL) ====================")
for c, (rl, sl, rt) in {"A": (81501, 24801, 23.5), "B": (62157, None, 31.2)}.items():
    t = TAB_T1[c].loc["S1"]
    rl_n = t["resultado líquido (R$)"]
    sel_n = t["Selic líquida no mesmo dinheiro (R$)"]
    ret_n = t["retorno ao ano sobre o dinheiro aplicado (%)"]
    print(f"carteira {c}, S1: resultado líquido {brl(rl_n)} (esperado {brl(rl)}); Selic {brl(sel_n)}"
          f"{'' if sl is None else f' (esperado {brl(sl)})'}; retorno ao ano {br(ret_n, 1)}% (esperado {br(rt, 1)}%)")
    assert round(rl_n) == rl, (c, rl_n)
    assert round(ret_n, 1) == rt, (c, ret_n)
    if sl is not None:
        assert round(sel_n) == sl, (c, sel_n)
print("reproducao OK: A e B batem com dados/kairi_saidas.txt")


# ---------------------------------------------------------------- PARTE 1
print("\n==================== PARTE 1: ORDENS QUE FICARAM EM ABERTO (NUNCA TOCARAM O ALVO) ====================")
print("(em aberto = saida 'em aberto' na saida em questao; toque na media = max(maxima(k)) >= MM(k), k apos a entrada)")
S1_POR_EID = {int(r.eid): r for r in REC[REC.saida == "S1"].itertuples(index=False)}
linhas_p1 = []
for car in CARTEIRAS:
    for g in ["F38L", "F50L", "F62L", "F100L", "M127L", "M162L", "SCL"]:
        sub = REC[(REC.carteira == car) & (REC.saida == g) & (REC.mot == ABERTO)]
        n = len(sub)
        if n == 0:
            linhas_p1.append({"Carteira": car, "Saída": g, "Em aberto": 0})
            continue
        ntouch, altas, fracs, s1p, s1r, abp, abr = [], [], [], [], [], [], []
        for r in sub.itertuples(index=False):
            F = ENT[r.eid]["F"]
            last = F["n"] - 1
            Hs = F["H"][r.e + 1:last + 1]
            ms = F["mP"][r.e + 1:last + 1]
            ntouch.append(int(np.sum(Hs >= ms)))
            mx = float(np.max(Hs))
            altas.append(100 * (mx / r.E - 1))
            fracs.append((mx - r.E) / (r.alvo_dia - r.E))
            s1 = S1_POR_EID[int(r.eid)]
            s1p.append(s1.resultado_pct)
            s1r.append(s1.resultado)
            abp.append(r.resultado_pct)
            abr.append(r.resultado)
        nt = np.array(ntouch)
        linhas_p1.append({
            "Carteira": car, "Saída": g, "Em aberto": n,
            "Tocaram a média": int((nt > 0).sum()),
            "Pregões com toque (média, quem tocou)": float(nt[nt > 0].mean()) if (nt > 0).any() else np.nan,
            "Alta máxima média sobre a entrada (%)": float(np.mean(altas)),
            "Fração da distância ao alvo percorrida (média)": float(np.mean(fracs)),
            "S1 se saísse: resultado médio (%)": 100 * float(np.mean(s1p)),
            "S1 se saísse: total (R$)": float(np.sum(s1r)),
            "Hoje em aberto: resultado médio (%)": 100 * float(np.mean(abp)),
            "Hoje em aberto: total (R$)": float(np.sum(abr)),
        })
p1 = pd.DataFrame(linhas_p1)
print("\n-- 1a) ordens em aberto (nunca tocaram o alvo), antes do imposto")
for car in CARTEIRAS:
    print(f"\ncarteira {car}")
    sub = p1[p1["Carteira"] == car].drop(columns=["Carteira"]).set_index("Saída")
    cel = pd.DataFrame(index=sub.index, columns=sub.columns, dtype=object)
    for col in sub.columns:
        cel[col] = [fmt_val(col, v) if not isnan(v) else "nd" for v in sub[col]]
    print(cel.to_string())

print("\n-- 1b) inverso: ordens que tocaram a média (S1 = volta à média); depois chegaram ao Fibonacci? (sem prazo)")
linhas_inv = []
for car in CARTEIRAS:
    sub = REC[(REC.carteira == car) & (REC.saida == "S1") & (REC.mot == VOLTA)]
    for nm, f in [("F38", 0.382), ("F50", 0.5), ("F62", 0.618), ("F100", 1.0)]:
        dias = []
        for r in sub.itertuples(index=False):
            F = ENT[r.eid]["F"]
            lvl = r.E + f * (r.P - r.E)
            seg = F["H"][r.k + 1:F["n"]]
            hit = np.flatnonzero(seg >= lvl)
            if hit.size:
                dias.append(int(hit[0] + 1))
        linhas_inv.append({"Carteira": car, "Alvo": nm, "Tocaram a média (S1)": len(sub),
                           "Chegaram depois": len(dias),
                           "% dos que tocaram": 100 * len(dias) / len(sub) if len(sub) else np.nan,
                           "Pregões após o toque: média": float(np.mean(dias)) if dias else np.nan,
                           "Pregões após o toque: mediana": float(np.median(dias)) if dias else np.nan})
inv = pd.DataFrame(linhas_inv)
cel = pd.DataFrame(index=inv.index, columns=inv.columns, dtype=object)
for col in inv.columns:
    cel[col] = [fmt_val(col, v) if not isnan(v) else "nd" for v in inv[col]]
print(cel.to_string(index=False))


# ---------------------------------------------------------------- PARTE 2: tabelas
print("\n==================== T1: TOTAL (todas as entradas) ====================")
for c in CARTEIRAS:
    print(f"\n--- carteira {c} - TOTAL")
    imprime_tab(TAB_T1[c])
print("\n==================== T2: ESCOLHA (entradas até 31/12/2022) e CONFERÊNCIA (entradas de 01/01/2023) ====================")
for c in CARTEIRAS:
    print(f"\n--- carteira {c} - ESCOLHA")
    imprime_tab(TAB_ESC[c])
    print(f"--- carteira {c} - CONFERÊNCIA")
    imprime_tab(TAB_CONF[c])


# ---------------------------------------------------------------- T3: motivos e custo do piso
print("\n==================== T3: ESCADAS POR MOTIVO DE SAÍDA ====================")
for car in ["A", "B"]:
    print(f"\n--- carteira {car}")
    cont_rows = []
    for cfg in ESCADAS:
        sub = REC[(REC.carteira == car) & (REC.saida == cfg["sig"])]
        row = {"Escada": cfg["sig"]}
        for m in MOTIVOS_ESC:
            row[m] = int((sub.mot == m).sum())
        row["total"] = len(sub)
        row["soma ok"] = sum(row[m] for m in MOTIVOS_ESC) == len(sub)
        cont_rows.append(row)
        assert row["soma ok"]
    print("contagem por motivo:")
    print(pd.DataFrame(cont_rows).set_index("Escada").to_string())
    print("\ndetalhe (dias corridos médios e resultado médio antes do imposto, por motivo):")
    for cfg in ESCADAS:
        sub = REC[(REC.carteira == car) & (REC.saida == cfg["sig"])]
        simp = int(((sub["piso_e"] >= sub["teto_e"]) & sub["teto_e"].notna() & sub["piso_e"].notna()).sum())
        print(f"{cfg['sig']} - {cfg['nome']}" + (f"  [ordens com teto <= piso na entrada, saída simples: {simp}]"
                                                  if cfg["modo"] == "pt" else ""))
        for m in MOTIVOS_ESC:
            s_ = sub[sub.mot == m]
            if not len(s_):
                continue
            txt = (f"   {m:<18} n={len(s_):>4}; dias médios {br(s_['dias'].mean(), 1):>7}; "
                   f"resultado médio {br(100 * s_['resultado_pct'].mean(), 1)}%")
            if m == RECUOU:
                dif = 100 * (s_["px"] / s_["piso_v"] - 1).mean()
                abaixo_e = int((s_["px"] < s_["E"]).sum())
                txt += (f"; venda vs piso (média) {br(dif, 2)}%; vendidas ABAIXO da entrada: {abaixo_e} de {len(s_)}")
            print(txt)
        if cfg["modo"] == "pt":
            armadas = sub[(sub["k_arm"] >= 0)]
            acima = int((armadas["piso_v"] > armadas["teto_e"]).sum())
            if acima:
                print(f"   (diagnóstico: {acima} vendas com piso acima do teto, por a média ter subido depois)")


# ---------------------------------------------------------------- T4: escada x S1 ordem a ordem (carteira A)
print("\n==================== T4: ESCADA x S1, ORDEM A ORDEM (CARTEIRA A, TOTAL) ====================")
s1A = REC[(REC.carteira == "A") & (REC.saida == "S1")].set_index("eid")
for sg in ["E1", "E5", "E8"]:
    eA = REC[(REC.carteira == "A") & (REC.saida == sg)].set_index("eid")
    d_r = eA["resultado"] - s1A.loc[eA.index, "resultado"]
    d_p = 100 * (eA["resultado_pct"] - s1A.loc[eA.index, "resultado_pct"])
    d_d = eA["dias"] - s1A.loc[eA.index, "dias"]
    mais = d_r > 0.01
    menos = d_r < -0.01
    igual = ~(mais | menos)
    print(f"{sg} x S1 (n={len(eA)}): rendeu mais em {int(mais.sum())}; rendeu menos em {int(menos.sum())}; "
          f"igual em {int(igual.sum())}")
    print(f"   ganho médio quando rendeu mais: {br(d_p[mais].mean(), 2) if mais.any() else 'nd'} pp; "
          f"perda média quando rendeu menos: {br(d_p[menos].mean(), 2) if menos.any() else 'nd'} pp; "
          f"dias a mais aplicada (média): {br(d_d.mean(), 1)}")


# ---------------------------------------------------------------- T5: melhor saida e numero de escadas acima da S1
print("\n==================== T5: MELHOR SAÍDA NA ESCOLHA E CONTAGEM ACIMA DA S1 ====================")
for car in CARTEIRAS:
    e_t = TAB_ESC[car]["retorno ao ano sobre o dinheiro aplicado (%)"].astype(float)
    c_t = TAB_CONF[car]["retorno ao ano sobre o dinheiro aplicado (%)"].astype(float)
    best = str(e_t.idxmax())
    res_c = TAB_CONF[car].loc[best, "resultado líquido (R$)"]
    print(f"carteira {car}: melhor linha na ESCOLHA = {best} ({NOME_SAIDA[best]}); retorno ao ano ESCOLHA "
          f"{br(e_t[best], 1)}%; CONFERÊNCIA: resultado líquido {brl(res_c)}, retorno ao ano {br(c_t[best], 1)}%")
    s1_e, s1_c = e_t["S1"], c_t["S1"]
    acima_e = {s for s in ESC_SIGS if e_t[s] > s1_e}
    acima_c = {s for s in ESC_SIGS if c_t[s] > s1_c}
    both = sorted(acima_e & acima_c, key=ESC_SIGS.index)
    print(f"   S1: ESCOLHA {br(s1_e, 1)}%, CONFERÊNCIA {br(s1_c, 1)}%")
    print(f"   escadas acima da S1 na ESCOLHA: {len(acima_e)}; na CONFERÊNCIA: {len(acima_c)}; "
          f"nos DOIS períodos: {len(both)} {both}")


# ---------------------------------------------------------------- planilhas
print("\n==================== GRAVAÇÕES ====================")
pl = REC[REC["carteira"].isin(["A", "B"]) & REC["saida"].isin(["S1", "E1", "E5", "E8"])].copy()
pl["ordem_saida"] = pl["saida"].map({s: i for i, s in enumerate(["S1", "E1", "E5", "E8"])})
pl = pl.sort_values(["carteira", "ordem_saida", "entrada", "fundo"]).reset_index(drop=True)
def f2(s):
    """R$ com 2 casas, virgula decimal (nd quando nao se aplica)."""
    return pd.Series(s, dtype=float).map(lambda x: "nd" if isnan(x) else f"{x:.2f}".replace(".", ","))


def f1(s):
    """% com 1 casa, virgula decimal (nd quando nao se aplica)."""
    return pd.Series(s, dtype=float).map(lambda x: "nd" if isnan(x) else f"{x:.1f}".replace(".", ","))


pl_out = pd.DataFrame({
    "Carteira": pl["carteira"],
    "Regra de saída": pl["nome_saida"],
    "Fundo": pl["fundo"],
    "Data de entrada": pl["entrada"],
    "Preço de entrada (R$)": f2(pl["E"]),
    "Valor da ordem (R$)": f2(pl["valor"]),
    "Piso no dia da entrada (R$)": f2(pl["piso_e"]),
    "Teto (R$)": f2(pl["teto_e"]),
    "Data em que tocou o piso pela primeira vez": pl["arm"],
    "Situação": np.where(pl["mot"] == ABERTO, "Em aberto", "Fechada"),
    "Data de saída (ou do último preço)": pl["data_saida"],
    "Preço de saída (ou atual) (R$)": f2(pl["px"]),
    "Motivo da saída": pl["mot"],
    "Dias corridos": pl["dias"].astype(int),
    "Valorização (%)": f1(100 * pl["valorizacao"] / pl["valor"]),
    "Rendimentos (%)": f1(100 * pl["rend"] / pl["valor"]),
    "Resultado antes do imposto (%)": f1(100 * pl["resultado_pct"]),
    "Resultado antes do imposto (R$)": f2(pl["resultado"]),
    "Selic líquida no mesmo período (%)": f1(100 * pl["sel_pct"]),
    "Ganhou da Selic (sim/não)": np.where(pl["dif_antes"] > 0, "sim", "não"),
    "Maior alta acima da entrada (%)": f1(100 * pl["alta_pos"]),
    "Maior queda abaixo da entrada (%)": f1(100 * pl["queda"]),
})
pl_out.to_csv(PL / "kairi_escada.csv", **OPC)
print(f"gravado: planilhas/kairi_escada.csv ({len(pl_out)} linhas)")

comp_rows = []
for car in CARTEIRAS:
    for per, tab, keys in [("TOTAL", TAB_T1[car], T1_KEYS), ("ESCOLHA", TAB_ESC[car], T2_KEYS),
                           ("CONFERÊNCIA", TAB_CONF[car], T2_KEYS)]:
        for sg in tab.index:
            d = {"Carteira": car, "Período": per, "Saída": sg, "Regra de saída": NOME_SAIDA[sg]}
            for kk in keys:
                v = tab.loc[sg, kk]
                if kk in ("ordens", "fechadas", "em aberto") and not isnan(v):
                    d[kk] = int(v)
                else:
                    d[kk] = round(float(v), 1 if "%" in kk else 2) if not isnan(v) else np.nan
            comp_rows.append(d)
comp_df = pd.DataFrame(comp_rows)
for kk in ("ordens", "fechadas", "em aberto"):
    comp_df[kk] = comp_df[kk].astype("Int64")
comp_df.to_csv(TEC / "kairi_escada_comparacao.csv", **OPC)
print(f"gravado: planilhas/tecnico/kairi_escada_comparacao.csv ({len(comp_df)} linhas)")


# ---------------------------------------------------------------- CONFERENCIAS 2, 3 e 4
print("\n==================== CONFERÊNCIA 2: DUAS ORDENS DA CARTEIRA A NA E1 ====================")


def exemplo(mot_alvo):
    r = REC[(REC.carteira == "A") & (REC.saida == "E1") & (REC.mot == mot_alvo)].iloc[0]
    F = ENT[int(r.eid)]["F"]
    e, s, k, ka, cot = int(r.e), int(r.s), int(r.k), int(r.k_arm), int(r.cot)
    E, M0, P = float(r.E), float(r.M0), float(r.P)
    f62 = E + 0.618 * (P - E)
    print(f"\n[{mot_alvo}] fundo {r.fundo}; sinal {pd.Timestamp(F['dates'][s]):%d/%m/%Y}; "
          f"entrada {pd.Timestamp(F['dates'][e]):%d/%m/%Y} a R$ {br(E, 4)}; cotas {cot}")
    print(f"   E = {br(E, 4)}; M0 (MM dos 200 até d-1, congelada) = {br(M0, 4)} (conferido: "
          f"{br(F['C'][s - N:s].mean(), 4)}); P (pico 252 até d) = {br(P, 4)}; F62 = {br(f62, 4)}")
    print(f"   piso no dia da entrada (MM até e-1) = {br(F['mP'][e], 4)}; teto = {br(r.teto_e, 4)}")
    if ka >= 0:
        print(f"   ARMOU em {pd.Timestamp(F['dates'][ka]):%d/%m/%Y}: máxima {br(F['H'][ka], 4)}; MM desse dia = "
              f"{br(F['mP'][ka], 4)} (até d-1); máxima >= MM: {F['H'][ka] >= F['mP'][ka]}")
    print(f"   VENDA em {pd.Timestamp(F['dates'][k]):%d/%m/%Y}: abertura {br(F['A'][k], 4)}, mínima {br(F['L'][k], 4)}, "
          f"máxima {br(F['H'][k], 4)}, MM {br(F['mP'][k], 4)}; piso do dia {br(r.piso_v, 4)}; teto {br(r.teto_e, 4)}")
    print(f"   motivo {r.mot}; preço de venda {br(r.px, 4)}")
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


exemplo(TETO)
exemplo(RECUOU)

print("\n==================== CONFERÊNCIA 3: CÓDIGO (asserts, todas as escadas e ordens) ====================")
n_chk = {"arm": 0, "teto": 0, "recuou": 0, "queda": 0, "prazo": 0}
for en_i, en in enumerate(ENT):
    F, e = en["F"], en["e"]
    sub = REC[REC.eid == en_i]
    s_ = en["s"]
    M0_chk = float(F["C"][s_ - N:s_].mean())
    for r in sub.itertuples(index=False):
        if r.saida not in ESC_SIGS:
            continue
        cfg = next(c for c in ESCADAS if c["sig"] == r.saida)
        ka, kv = int(r.k_arm), int(r.k)
        # a media usada em qualquer dia k e a media dos 200 fechamentos ate k-1 (so informacao anterior)
        if ka >= 0:
            assert abs(F["mP"][ka] - F["C"][ka - N:ka].mean()) < 1e-9
            assert ka > e
            n_chk["arm"] += 1
        if cfg["modo"] == "pt":
            piso_v = r.piso_v
            if r.mot in (TETO, SIMPLES):
                # saida simples (teto <= piso na entrada): vende no nivel do piso; senao, no teto
                if r.mot == SIMPLES:
                    # vende no primeiro toque do piso, no proprio dia da armacao
                    assert r.teto_e <= r.piso_e and kv == ka
                    assert abs(r.px - pmax(F["A"][kv], piso_v)) < 1e-9 and F["H"][kv] >= piso_v - 1e-9
                    n_chk["simples"] = n_chk.get("simples", 0) + 1
                else:
                    assert abs(r.px - pmax(F["A"][kv], r.teto_e)) < 1e-9
                    assert F["H"][kv] >= r.teto_e - 1e-9
                    if kv > ka:
                        assert F["L"][kv] > piso_v, "no dia da venda no teto, o piso nao pode ter sido tocado"
                    else:
                        assert kv == ka
                    n_chk["teto"] += 1
            elif r.mot == RECUOU:
                assert kv > ka
                assert F["L"][kv] <= piso_v + 1e-12
                exp_px = min(F["A"][kv], piso_v) if np.isfinite(F["A"][kv]) else piso_v
                assert abs(r.px - exp_px) < 1e-9
                n_chk["recuou"] += 1
        elif cfg["modo"] == "queda":
            if r.mot.startswith("queda"):
                assert kv > ka
                maxc = F["C"][ka:kv].max()
                assert F["C"][kv - 1] <= (1 - cfg["x"]) * maxc + 1e-12
                n_chk["queda"] += 1
        elif cfg["modo"] == "degraus":
            if r.mot == RECUOU:
                assert kv > ka
                assert F["L"][kv] <= r.piso_v + 1e-12
                n_chk["recuou"] += 1
            if r.mot == TETO:
                assert F["H"][kv] >= r.px - 1e-12
                n_chk["teto"] += 1
        if r.mot == PRAZO_M:
            assert ka < 0 and kv == e + PRAZO
            n_chk["prazo"] += 1
    # o M0 usado na tabela e a media dos 200 fechamentos ate s-1 (conferido)
    assert abs(float(sub["M0"].iloc[0]) - M0_chk) < 1e-9
print(f"ASSERTS PASSARAM: armadas {n_chk['arm']}; vendas no teto {n_chk['teto']}; "
      f"recuos ao piso {n_chk['recuou']}; queda do máximo {n_chk['queda']}; prazos {n_chk['prazo']}. "
      "Piso da MM no dia k = média até k-1; arma e vende no mesmo dia só no teto (sem venda no piso no dia da armação "
      "e sem venda no dia da armação em piso); no dia em que piso e teto são tocados, prevalece o piso.")

print("\n==================== CONFERÊNCIA 4: SOMA DAS CONTAGENS = ORDENS ====================")
for cfg in ESCADAS:
    for car in ["A", "B", "C"]:
        sub = REC[(REC.carteira == car) & (REC.saida == cfg["sig"])]
        soma = sum(int((sub.mot == m).sum()) for m in MOTIVOS_ESC)
        assert soma == len(sub), (cfg["sig"], car)
print("OK: em todas as escadas e carteiras (A, B, C), soma por motivo = número de ordens.")

print(f"\nTempo total: {time.time() - T0:.1f} s")
