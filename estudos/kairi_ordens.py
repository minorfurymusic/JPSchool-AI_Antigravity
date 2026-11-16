"""Carteira INFINITA do Indice de Kairi em FIIs: todo sinal vira ordem (sem limite de dinheiro).

Sinal em d: kairi_200(d) = fechamento(d) / media dos 200 fechamentos ate d-1 - 1 cruza para baixo de -X
(kairi(d-1) > -X e kairi(d) <= -X), com universo em d, rendimento mantido e guarda de janela.
Compra na abertura do pregao seguinte ao sinal, tamanho min(R$ 3.000; 5% do volume medio 60 em d),
cotas inteiras, minimo R$ 1.000. Um fundo por vez por carteira.
Saida 'volta a media' (maxima(k) >= media dos 200 fechamentos ate k-1; vende max(abertura, media)),
prazo de 252 linhas, fundo saiu da bolsa, dado suspeito (guarda) e em aberto.

Carteiras: A: X=0,15; B: X=0,20; C: X=0,15 so com amplitude(d) >= 0,15.

Le so as planilhas de planilhas/. Copia a carga, o universo, a guarda e os sinais de
estudos/kairi.py e estudos/kairi_carteira.py (esses scripts executam tudo no import).
Diferenca deliberada: aqui a media do kairi e ate d-1 (como pedido), e kairi.py usa ate d.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_ordens.py 2>&1 | tee dados/kairi_ordens.txt
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

np.seterr(all="ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 60)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
TEC = PL / "tecnico"
TEC.mkdir(parents=True, exist_ok=True)
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

INICIO_D = np.datetime64("2018-01-01", "D")
CORTE_22 = pd.Timestamp("2022-12-31")
CONF_INI = pd.Timestamp("2023-01-01")
B3 = 0.0003                 # taxa de 0,03% por lado
IR_OP = 0.20                # imposto sobre ganho de operacoes (por ordem)
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
FIBO = [("38,2%", 0.382, "f1_"), ("50%", 0.5, "f2_"), ("61,8%", 0.618, "f3_")]
VOLTA = "volta à média"
PRAZO_M = "prazo"
SAIU = "fundo saiu da bolsa"
GUARDA = "dado suspeito"
ABERTO = "em aberto"
MOTIVOS = [VOLTA, PRAZO_M, SAIU, GUARDA, ABERTO]


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


# ---------------------------------------------------------------- carga (copiada de kairi.py / kairi_carteira.py)
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
for c in [C_AB, C_MX, C_MN, C_FE, C_NEG, C_REND, C_PVP, C_PAT, C_VOL, C_AMO]:
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
print(f"selic NaN em mercado: {int(np.isnan(SEL).sum())} (tratada como 0 no acumulado)")
CUM = np.concatenate([[0.0], np.cumsum(np.log1p(np.nan_to_num(SEL) / 100) / 252)])
I0 = int(np.searchsorted(MD, INICIO_D))
assert TS[I0] == pd.Timestamp("2018-01-02"), TS[I0]
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))


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

    univ = (PAT >= 50e6) & (VOL >= 25000) & (R > 0) & (AMO == 0) & (PVP >= 0.30) & (PVP <= 3.0)
    if nome in EXCLUIDOS:
        univ[:] = False

    bad = np.zeros(n, bool)                  # bad[j] trata o par (j-1, j)
    if n > 1:
        gap = np.diff(dates).astype("timedelta64[D]").astype(int)
        ret = C[1:] / C[:-1] - 1
        bad[1:] = (gap > 15) | (ret > 0.60) | (ret < -0.45)
    cbad = np.r_[0, np.cumsum(bad)]

    mN = pd.Series(C).rolling(N, min_periods=N).mean().to_numpy()   # mN[i] = media de C[i-199..i]
    mP = np.r_[np.nan, mN[:-1]]                                     # mP[d] = media dos 200 ate d-1
    k200 = C / mP - 1                                               # kairi_200(d)

    sim = np.zeros(n, bool)                  # rendimento em d >= 0,95 x rendimento 126 linhas antes
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= K_REND * R[:-LAG_REND]

    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome
    FD[nome] = dict(nome=nome, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, R=R, PVP=PVP, VOL=VOL, NEG=NEG,
                    univ=univ, bad=bad, cbad=cbad, mN=mN, mP=mP, k200=k200, sim=sim,
                    aberto=int(mi[-1]) >= NM - 21)       # ultimo dado nos ultimos 20 pregoes da base

RDF = {}
for f_, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f_] = (bd, cs)


def rend_val(f, D, S, incl):
    """Soma de valor por cota dos avisos com data_base >= D e < S (<= S se incl)."""
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


# amplitude(d): fracao dos fundos do universo em d com kairi_200 <= -0,10 (so dados ate d)
AMP_NUM = np.zeros(NM)
AMP_DEN = np.zeros(NM)
for F in FD.values():
    valid = F["univ"] & np.isfinite(F["k200"])
    hit = valid & (F["k200"] <= AMP_K)
    np.add.at(AMP_DEN, F["mi"][valid], 1)
    np.add.at(AMP_NUM, F["mi"][hit], 1)
AMP = np.where(AMP_DEN > 0, AMP_NUM / np.where(AMP_DEN > 0, AMP_DEN, 1), np.nan)


# ---------------------------------------------------------------- sinais
def sinais(F, X):
    """Sinal em d: cruza para baixo de -X, universo em d, rendimento mantido, janela sem dado ruim."""
    n = F["n"]
    k = F["k200"]
    cross = np.zeros(n, bool)
    cross[1:] = (k[1:] <= -X) & (k[:-1] > -X)
    base = cross & F["univ"] & F["sim"]
    base[:N] = False
    idx = np.flatnonzero(base)
    ok = np.zeros(n, bool)
    if idx.size:
        # pares j em [d-199, d] => fechamentos d-200..d usados no kairi de d
        jan = (F["cbad"][idx + 1] - F["cbad"][idx - N + 1]) > 0
        ok[idx[~jan]] = True
    return ok


# candidatos por pregao de ENTRADA: sinal em d -> compra na abertura do pregao seguinte
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


# ---------------------------------------------------------------- saidas
def regra_fim(F, e):
    """Sem saida por media/alvo: prazo 252 linhas, ou fundo saiu da bolsa, ou em aberto."""
    last = F["n"] - 1
    if e + PRAZO <= last:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO])
    if F["aberto"]:
        return last, ABERTO, float(F["C"][last])
    return last, SAIU, float(F["C"][last])


def saida_volta(F, e):
    """Volta a media. Retorna (linha k, motivo, preco de saida, media usada)."""
    last = F["n"] - 1
    jan = min(e + PRAZO, last)
    kg = kv = None
    if jan > e:
        w = np.flatnonzero(F["bad"][e + 1:jan + 1])
        if w.size:
            kg = e + 1 + int(w[0])                     # par (kg-1, kg) ruim: vende no fechamento de kg-1
        h = np.flatnonzero(F["H"][e + 1:jan + 1] >= F["mN"][e:jan])   # maxima(k) >= media ate k-1
        if h.size:
            kv = e + 1 + int(h[0])
    if kg is not None and (kv is None or kg <= kv):
        k = kg - 1
        return k, GUARDA, float(F["C"][k]), np.nan
    if kv is not None:
        media = float(F["mN"][kv - 1])
        a = float(F["A"][kv])
        px = max(a, media) if np.isfinite(a) else media
        return kv, VOLTA, px, media
    k, mot, px = regra_fim(F, e)
    return k, mot, px, np.nan


def saida_alvo(F, e, T, mot_alvo):
    """Saida alternativa (Fibonacci): primeira maxima >= T; senao as mesmas regras de fim."""
    last = F["n"] - 1
    jan = min(e + PRAZO, last)
    kg = kt = None
    if jan > e:
        w = np.flatnonzero(F["bad"][e + 1:jan + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        h = np.flatnonzero(F["H"][e + 1:jan + 1] >= T)
        if h.size:
            kt = e + 1 + int(h[0])
    if kg is not None and (kt is None or kg <= kt):
        k = kg - 1
        return k, GUARDA, float(F["C"][k])
    if kt is not None:
        a = float(F["A"][kt])
        px = max(a, T) if np.isfinite(a) else T
        return kt, mot_alvo, px
    return regra_fim(F, e)


def contas(F, e, k, mot, pxs, cot):
    """Conta de uma ordem: compra na abertura de e, venda na linha k a pxs."""
    px_e = float(F["A"][e])
    D = F["dates"][e]
    S = F["dates"][k]
    valor = cot * px_e
    venda = cot * pxs
    valorizacao = venda - valor
    taxas = B3 * valor + B3 * venda
    incl = mot in (PRAZO_M, ABERTO)
    rend = rend_val(F["nome"], D, S, incl) * cot
    imposto = IR_OP * max(valorizacao - taxas, 0.0)
    resultado = valorizacao + rend - taxas - imposto
    dias = int((S - D) / np.timedelta64(1, "D"))
    ie = int(np.searchsorted(MD, D, "left"))
    ix = int(np.searchsorted(MD, S, "left"))
    sel_pct = (np.exp(CUM[ix] - CUM[ie]) - 1) * (1 - aliq_rf(dias))
    L = F["L"][e:k + 1]
    pr = int(np.argmin(L))
    p = e + pr
    queda = min(0.0, float(L[pr]) / px_e - 1)
    abaixo = queda < 0
    if abaixo:
        volt = np.flatnonzero(F["H"][p + 1:k + 1] >= px_e)
        voltou = "sim" if volt.size else "não"
        p_volta = float(volt[0] + 1) if volt.size else np.nan
    else:
        voltou = "não caiu"
        p_volta = np.nan
    return dict(valor=valor, px_e=px_e, px_s=float(pxs), cotas=cot, valorizacao=valorizacao, rend=rend,
                taxas=taxas, imposto=imposto, resultado=resultado, resultado_pct=resultado / valor,
                valorizacao_pct=valorizacao / valor, rend_pct=rend / valor, sel_pct=sel_pct,
                sel_rs=valor * sel_pct, dif_rs=resultado - valor * sel_pct, dias=dias, pregoes=int(k - e),
                motivo=mot, data_saida=S, mi_x=ix, queda=queda, abaixo=abaixo, pregoes_fundo=int(pr),
                voltou=voltou, p_volta=p_volta, pregoes_fundo_saida=int(k - p),
                alta=float(np.max(F["H"][e:k + 1])) / px_e - 1, k=int(k), e=int(e))


# ---------------------------------------------------------------- simulacao (sem limite de dinheiro)
def simular(nome):
    cfg = CARTEIRAS[nome]
    cands = CAND[cfg["X"]]
    busy = {}
    ordens, nao = [], []
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
                nao.append(dict(carteira=nome, ano=TS[ex].year, fundo=f, sinal=TS[md], data_entrada=TS[ex],
                                valor_possivel=cot * px))
                continue
            st["aceitos"] += 1
            k, mot, pxs, media = saida_volta(F, r)
            busy[f] = k
            c = contas(F, r, k, mot, pxs, cot)
            c["media_saida"] = media
            # alternativas Fibonacci sobre a MESMA entrada e cotas
            pico = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))
            queda_f = pico - c["px_e"]
            rec = dict(carteira=nome, fundo=f, tipo=TIPO.get(f, "sem tipo"), sinal=TS[md], data_entrada=TS[ex],
                       ano=TS[ex].year, s=int(s), md=int(md), mi_e=int(ex),
                       kairi_sinal=float(F["k200"][s]), mP_sinal=float(F["mP"][s]), pvp_sinal=float(F["PVP"][s]),
                       amp_sinal=float(AMP[md]), vol60=vol, pico252=pico,
                       dist_media200=float(F["mP"][s]) / c["px_e"] - 1)
            rec.update(c)
            for rot, fr, pref in FIBO:
                T = c["px_e"] + fr * queda_f
                k2, m2, p2 = saida_alvo(F, r, T, "alvo " + rot)
                c2 = contas(F, r, k2, m2, p2, cot)
                rec[pref + "alvo"] = T
                rec[pref + "dist"] = T / c["px_e"] - 1
                for kk_ in ["motivo", "pregoes", "resultado_pct", "sel_pct", "dif_rs", "resultado", "valor"]:
                    rec[pref + kk_] = c2[kk_]
            ordens.append(rec)
    ops = pd.DataFrame(ordens)
    ops["situacao"] = np.where(ops["motivo"] == ABERTO, "Em aberto", "Fechada")
    ops["fechada"] = ops["motivo"] != ABERTO
    print(f"carteira {nome}: {st}")
    return ops, pd.DataFrame(nao), st


print("\n== ORDENS (carteira infinita, cada sinal com ordem) ==")
OPS_L, NAO_L, STATS = [], [], {}
for nome in CARTEIRAS:
    o, na, st = simular(nome)
    OPS_L.append(o)
    NAO_L.append(na)
    STATS[nome] = st
OPS = pd.concat(OPS_L, ignore_index=True)
NAO = pd.concat(NAO_L, ignore_index=True)
assert (OPS["valor"] >= ORDEM_MIN - 1e-9).all()
print(f"ordens geradas: {len(OPS)} (A={int((OPS.carteira == 'A').sum())}, B={int((OPS.carteira == 'B').sum())}, "
      f"C={int((OPS.carteira == 'C').sum())}); em aberto: {int((OPS.motivo == ABERTO).sum())}; "
      f"sinais nao aceitos por ordem menor que R$ 1.000: {len(NAO)}")


# ---------------------------------------------------------------- balanco ano a ano
def media_ou_nan(s):
    return float(s.mean()) if len(s) else np.nan


def bloco(A_, nao_):
    C_ = A_[A_["fechada"]]
    n, nf, na = len(A_), len(C_), len(A_) - len(C_)
    ap_all = float(A_["valor"].sum())
    ap = float(C_["valor"].sum())
    out = {}
    out["ordens"] = n
    out["fechadas"] = nf
    out["em aberto"] = na
    out["sinais nao aceitos (< R$ 1.000)"] = len(nao_)
    out["total aplicado (R$)"] = ap_all
    out["valor medio da ordem (R$)"] = ap_all / n if n else np.nan
    out["dias corridos medios"] = media_ou_nan(C_["dias"])
    out["pregoes medios"] = media_ou_nan(C_["pregoes"])
    out["valorizacao (R$)"] = float(C_["valorizacao"].sum())
    out["valorizacao (%)"] = 100 * float(C_["valorizacao"].sum()) / ap if ap else np.nan
    out["rendimentos recebidos (R$)"] = float(C_["rend"].sum())
    out["rendimentos (%)"] = 100 * float(C_["rend"].sum()) / ap if ap else np.nan
    out["taxas (R$)"] = float(C_["taxas"].sum())
    out["imposto (R$)"] = float(C_["imposto"].sum())
    res = float(C_["resultado"].sum())
    sel = float(C_["sel_rs"].sum())
    out["resultado total (R$)"] = res
    out["resultado total (%)"] = 100 * res / ap if ap else np.nan
    out["Selic liquida no mesmo dinheiro (R$)"] = sel
    out["Selic liquida no mesmo dinheiro (%)"] = 100 * sel / ap if ap else np.nan
    out["diferenca para a Selic (R$)"] = float(C_["dif_rs"].sum())
    out["diferenca para a Selic (pontos)"] = (100 * res / ap - 100 * sel / ap) if ap else np.nan
    out["% com resultado > 0"] = 100 * float((C_["resultado"] > 0).mean()) if nf else np.nan
    out["% que ganharam da Selic"] = 100 * float((C_["dif_rs"] > 0).mean()) if nf else np.nan
    ganho = C_[C_["resultado"] > 0]
    perda = C_[C_["resultado"] <= 0]
    out["valorizacao media dos com ganho (%)"] = 100 * media_ou_nan(ganho["valorizacao_pct"])
    out["n com ganho"] = len(ganho)
    out["valorizacao media dos com perda (%)"] = 100 * media_ou_nan(perda["valorizacao_pct"])
    out["n com perda"] = len(perda)
    q = C_["queda"].to_numpy(float)
    out["% que ficaram abaixo da entrada"] = 100 * float((q < 0).mean()) if nf else np.nan
    out["queda media (%)"] = 100 * float(q.mean()) if nf else np.nan
    if nf:
        j = int(np.argmin(q))
        out["queda maxima (%)"] = 100 * float(q[j])
        out["fundo da queda maxima"] = f"{C_.iloc[j]['fundo']} (entrada {C_.iloc[j]['data_entrada']:%d/%m/%Y})"
        qm = float(q.mean())
        m10 = q <= qm - 0.10
        m20 = q <= qm - 0.20
        out["queda media, >= 10 pts (%)"] = 100 * float(q[m10].mean()) if m10.any() else np.nan
        out["n >= 10 pts"] = int(m10.sum())
        out["queda media, >= 20 pts (%)"] = 100 * float(q[m20].mean()) if m20.any() else np.nan
        out["n >= 20 pts"] = int(m20.sum())
        kq = max(1, int(round(0.10 * nf)))
        out["media dos 10% piores (%)"] = 100 * float(np.sort(q)[:kq].mean())
    else:
        for k_ in ["queda maxima (%)", "fundo da queda maxima", "queda media, >= 10 pts (%)", "n >= 10 pts",
                   "queda media, >= 20 pts (%)", "n >= 20 pts", "media dos 10% piores (%)"]:
            out[k_] = np.nan
    ab = C_[C_["abaixo"]]
    vb = ab[ab["voltou"] == "sim"]
    out["pregoes entrada ate o fundo"] = media_ou_nan(ab["pregoes_fundo"])
    out["% que voltou ao preco de entrada"] = 100 * len(vb) / len(ab) if len(ab) else np.nan
    out["pregoes fundo ate voltar"] = media_ou_nan(vb["p_volta"])
    out["pregoes fundo ate a saida"] = media_ou_nan(ab["pregoes_fundo_saida"])
    for m in MOTIVOS:
        out[f"saida: {m}"] = int((A_["motivo"] == m).sum())
    return out


def tabela_balanco(nome):
    sub = OPS[OPS["carteira"] == nome]
    nao = NAO[NAO["carteira"] == nome] if len(NAO) else NAO
    cols = {}
    for ano in sorted(sub["ano"].unique()):
        cols[str(int(ano))] = bloco(sub[sub["ano"] == ano], nao[nao["ano"] == ano] if len(nao) else nao)
    cols["TOTAL"] = bloco(sub, nao)
    return pd.DataFrame(cols)


TABS = {}
for nome in CARTEIRAS:
    tab = tabela_balanco(nome)
    TABS[nome] = tab
    cel = pd.DataFrame({c: [fmt_val(k_, tab.loc[k_, c]) for k_ in tab.index] for c in tab.columns}, index=tab.index)
    print(f"\n==================== CARTEIRA {nome} - BALANCO ANO A ANO (pelo ano da ENTRADA) ====================")
    print(f"(linhas de 3 a 13: so fechadas; 'total aplicado' e 'valor medio' incluem as em aberto)")
    print(cel.to_string())
    ab = OPS[(OPS["carteira"] == nome) & (~OPS["fechada"])]
    print(f"\nEM ABERTO carteira {nome}: {len(ab)} ordens (avaliadas pelo ultimo fechamento)")
    if len(ab):
        t = ab.assign(entrada=ab["data_entrada"].dt.strftime("%d/%m/%Y"))
        show = pd.DataFrame({
            "fundo": t["fundo"], "entrada": t["entrada"], "valor": t["valor"].map(brl),
            "preco entrada": t["px_e"].map(lambda v: br(v, 4)), "preco atual": t["px_s"].map(lambda v: br(v, 4)),
            "dias": t["dias"], "valorizacao": (100 * t["valorizacao_pct"]).map(lambda v: br(v, 1) + "%"),
            "rendimentos": t["rend"].map(brl), "queda max": (100 * t["queda"]).map(lambda v: br(v, 1) + "%")})
        print(show.to_string(index=False))


# ---------------------------------------------------------------- dinheiro necessario
print("\n==================== DINHEIRO NECESSARIO ====================")
print("(custo das ordens abertas em cada pregao, de 02/01/2018 ao fim da base; conta aproximada)")
for nome in CARTEIRAS:
    sub = OPS[OPS["carteira"] == nome]
    ap = np.zeros(NM + 1)
    cnt = np.zeros(NM + 1)
    for r in sub.itertuples(index=False):
        mx = NM if r.motivo == ABERTO else r.mi_x          # em aberto: o dinheiro segue aplicado ate o fim
        ap[r.mi_e] += r.valor
        ap[mx] -= r.valor
        cnt[r.mi_e] += 1
        cnt[mx] -= 1
    apd = np.cumsum(ap)[I0:NM]
    cntd = np.cumsum(cnt)[I0:NM]
    dias_d = MD[I0:NM]
    j = int(np.argmax(apd))
    res_fech = float(sub.loc[sub["fechada"], "resultado"].sum())
    media = float(apd.mean())
    print(f"\n--- carteira {nome}")
    print(f"maior valor aplicado ao mesmo tempo: {brl(apd[j])} em {pd.Timestamp(dias_d[j]):%d/%m/%Y}")
    print(f"valor medio aplicado por pregao: {brl(media)}")
    print(f"maior numero de ordens abertas ao mesmo tempo: {int(cntd.max())} "
          f"(em {pd.Timestamp(dias_d[int(np.argmax(cntd))]):%d/%m/%Y})")
    print(f"resultado total das fechadas: {brl(res_fech)}; dividido pelo pico: {br(100 * res_fech / apd[j], 1)}%; "
          f"dividido pelo valor medio aplicado: {br(100 * res_fech / media, 1)}%  (conta aproximada)")
    anos = pd.Series([pd.Timestamp(x).year for x in dias_d])
    linhas = []
    for ano in sorted(anos.unique()):
        msk = (anos == ano).to_numpy()
        jj = int(np.argmax(np.where(msk, apd, -np.inf)))
        linhas.append(dict(ano=str(ano), pico_no_ano=brl(apd[jj]), data_do_pico=f"{pd.Timestamp(dias_d[jj]):%d/%m/%Y}",
                           max_ordens_no_ano=int(cntd[msk].max()), media_aplicado_no_ano=brl(apd[msk].mean())))
    print(pd.DataFrame(linhas).to_string(index=False))


# ---------------------------------------------------------------- Fibonacci contra volta a media
def linha_fibo(d, pref, nome_saida):
    cl = d[d[pref + "motivo"] != ABERTO]
    if len(cl) == 0:
        return dict(saida=nome_saida, n=0)
    res = cl[pref + "resultado_pct"] if pref else cl["resultado_pct"]
    sel = cl[pref + "sel_pct"] if pref else cl["sel_pct"]
    dif = cl[pref + "dif_rs"] if pref else cl["dif_rs"]
    pr_ = cl[pref + "pregoes"] if pref else cl["pregoes"]
    return dict(saida=nome_saida, n=len(cl), pregoes=float(pr_.mean()),
                resultado=100 * float(res.mean()), selic=100 * float(sel.mean()),
                diferenca_pts=100 * float((res - sel).mean()),
                pct_ganho=100 * float((res > 0).mean()), pct_ganhou_selic=100 * float((dif > 0).mean()))


print("\n==================== FIBONACCI CONTRA VOLTA A MEDIA ====================")
print("(mesmas entradas da carteira; so fechadas; resultado com a mesma formula; distancias da entrada)")
FIBO_ROWS = []
for nome in CARTEIRAS:
    sub = OPS[OPS["carteira"] == nome]
    periodos = [("TOTAL", sub), ("entradas ate 31/12/2022", sub[sub["data_entrada"] <= CORTE_22]),
                ("entradas de 01/01/2023", sub[sub["data_entrada"] >= CONF_INI])]
    print(f"\n--- carteira {nome}")
    for pn, d in periodos:
        rows = [linha_fibo(d, "", "volta a media")] + [linha_fibo(d, pref, "Fibo " + rot) for rot, _, pref in FIBO]
        for r_ in rows:
            r_["carteira"] = nome
            r_["periodo"] = pn
            FIBO_ROWS.append(r_)
        dist = dict(media200=100 * float(d["dist_media200"].mean()),
                    f382=100 * float(d["f1_dist"].mean()), f50=100 * float(d["f2_dist"].mean()),
                    f618=100 * float(d["f3_dist"].mean()))
        print(f"[{pn}]  distancia media da entrada ate: media 200 {br(dist['media200'], 1)}% | alvo 38,2% "
              f"{br(dist['f382'], 1)}% | alvo 50% {br(dist['f50'], 1)}% | alvo 61,8% {br(dist['f618'], 1)}%")
        tdf = pd.DataFrame(rows)
        print(pd.DataFrame({
            "saida": tdf["saida"], "n fechadas": tdf["n"],
            "pregoes medios": tdf.get("pregoes", pd.Series(dtype=float)).map(lambda v: br(v, 1) if not isnan(v) else "nd"),
            "resultado medio": tdf.get("resultado", pd.Series(dtype=float)).map(lambda v: br(v, 1) + "%" if not isnan(v) else "nd"),
            "Selic media": tdf.get("selic", pd.Series(dtype=float)).map(lambda v: br(v, 1) + "%" if not isnan(v) else "nd"),
            "diferenca media (pp)": tdf.get("diferenca_pts", pd.Series(dtype=float)).map(lambda v: br(v, 1) if not isnan(v) else "nd"),
            "% com resultado > 0": tdf.get("pct_ganho", pd.Series(dtype=float)).map(lambda v: br(v, 1) + "%" if not isnan(v) else "nd"),
            "% ganharam da Selic": tdf.get("pct_ganhou_selic", pd.Series(dtype=float)).map(lambda v: br(v, 1) + "%" if not isnan(v) else "nd"),
        }).to_string(index=False))


# ---------------------------------------------------------------- planilhas
OPS_ORD = OPS.sort_values(["carteira", "data_entrada", "fundo"]).reset_index(drop=True)
o = OPS_ORD
csv_df = pd.DataFrame({
    "Carteira": o["carteira"],
    "Fundo": o["fundo"],
    "Tipo do fundo": o["tipo"],
    "Data do sinal": pd.to_datetime(o["sinal"]),
    "Data de entrada": pd.to_datetime(o["data_entrada"]),
    "Preço de entrada (R$)": o["px_e"].round(2),
    "Cotas": o["cotas"].astype(int),
    "Valor da ordem (R$)": o["valor"].round(2),
    "Situação": o["situacao"],
    "Data de saída (ou do último preço)": pd.to_datetime(o["data_saida"]),
    "Preço de saída (ou atual) (R$)": o["px_s"].round(2),
    "Motivo da saída": o["motivo"],
    "Dias corridos": o["dias"],
    "Pregões": o["pregoes"],
    "Valorização (R$)": o["valorizacao"].round(2),
    "Valorização (%)": (100 * o["valorizacao_pct"]).round(1),
    "Rendimentos recebidos (R$)": o["rend"].round(2),
    "Rendimentos (%)": (100 * o["rend_pct"]).round(1),
    "Taxas (R$)": o["taxas"].round(2),
    "Imposto (R$)": o["imposto"].round(2),
    "Resultado (R$)": o["resultado"].round(2),
    "Resultado (%)": (100 * o["resultado_pct"]).round(1),
    "Selic líquida no mesmo período (R$)": o["sel_rs"].round(2),
    "Selic líquida (%)": (100 * o["sel_pct"]).round(1),
    "Diferença para a Selic (R$)": o["dif_rs"].round(2),
    "Ganhou da Selic (sim/não)": np.where(o["dif_rs"] > 0, "sim", "não"),
    "Maior queda abaixo da entrada (%)": (100 * o["queda"]).round(1),
    "Pregões até o ponto mais baixo": o["pregoes_fundo"].where(o["abaixo"]).astype("Int64"),
    "Voltou ao preço de entrada (sim/não/não caiu)": o["voltou"],
    "Pregões do ponto mais baixo até voltar ao preço de entrada": o["p_volta"].round(0).astype("Int64"),
    "Maior alta acima da entrada (%)": (100 * o["alta"]).round(1),
    "Afastamento da média no sinal (%)": (100 * o["kairi_sinal"]).round(1),
    "Cota sobre valor patrimonial no sinal": o["pvp_sinal"].round(2),
    "Fundos caídos no dia (%)": (100 * o["amp_sinal"]).round(1),
})
csv_df.to_csv(PL / "kairi_ordens.csv", **OPC)

LONGO = []
for nome, tab in TABS.items():
    for c in tab.columns:
        for k_ in tab.index:
            LONGO.append(dict(Carteira=nome, Ano=c, Indicador=k_, Valor=tab.loc[k_, c]))
pd.DataFrame(LONGO).to_csv(TEC / "kairi_ordens_por_ano.csv", **OPC)
print(f"\ngravados: planilhas/kairi_ordens.csv ({len(csv_df)} linhas), "
      f"planilhas/tecnico/kairi_ordens_por_ano.csv ({len(LONGO)} linhas)")


# ---------------------------------------------------------------- CONFERENCIAS
print("\n==================== CONFERENCIAS ====================")
# 3) soma dos anos = TOTAL
for nome, tab in TABS.items():
    anos = [c for c in tab.columns if c != "TOTAL"]
    for k_ in ["ordens", "fechadas", "total aplicado (R$)", "resultado total (R$)", "Selic liquida no mesmo dinheiro (R$)",
               "sinais nao aceitos (< R$ 1.000)"]:
        soma = sum(float(tab.loc[k_, a]) for a in anos)
        assert abs(soma - float(tab.loc[k_, "TOTAL"])) < 1e-6, (nome, k_, soma, tab.loc[k_, "TOTAL"])
    print(f"3) carteira {nome}: soma dos anos = TOTAL (ordens, fechadas, aplicado, resultado R$, Selic R$, nao aceitos) ASSERT PASSOU")


# 4) regras do codigo: compra no pregao seguinte; media da saida ate k-1; pico252 ate d
def conferir_codigo():
    n_comp = n_med = 0
    for r in OPS.itertuples(index=False):
        F = FD[r.fundo]
        assert r.md + 1 == r.mi_e and TS[r.md + 1] == r.data_entrada and TS[r.md] == r.sinal
        assert r.sinal < r.data_entrada
        n_comp += 1
        if r.motivo == VOLTA:
            k = r.k
            media = float(F["C"][k - N:k].mean())                      # fechamentos k-200..k-1
            assert abs(media - r.media_saida) < 1e-9
            assert F["H"][k] >= media
            # nenhuma linha antes de k (apos a entrada) tinha maxima >= media de SEU k-1
            for kk in range(r.e + 1, k):
                assert F["H"][kk] < float(F["C"][kk - N:kk].mean()) or np.isnan(float(F["C"][kk - N:kk].mean())), (r.fundo, kk)
            n_med += 1
        s = r.s
        pico_manual = float(np.max(F["C"][max(0, s - PRAZO + 1):s + 1]))  # so ate o dia do sinal
        assert abs(pico_manual - r.pico252) < 1e-12
    print(f"4) ASSERT PASSOU: sinal em d -> compra na abertura de d+1 ({n_comp} ordens); "
          f"saida 'volta' com media dos 200 ate k-1 e primeira maxima >= media ({n_med} ordens); "
          f"pico252 usa so dados ate o dia do sinal.")


conferir_codigo()


# 2) refazer a mao duas ordens da carteira A (uma com ganho e uma com perda)
def refazer(o_):
    f = o_["fundo"]
    g = PR[PR["fundo"] == f].reset_index(drop=True)
    ds = np.datetime64(pd.Timestamp(o_["sinal"]), "D")
    s = int(np.flatnonzero(g["data"].to_numpy("datetime64[D]") == ds)[0])
    C = g[C_FE].to_numpy(float)
    A_ = g[C_AB].to_numpy(float)
    H_ = g[C_MX].to_numpy(float)
    L_ = g[C_MN].to_numpy(float)
    V_ = g[C_VOL].to_numpy(float)
    dts = g["data"]
    last = len(g) - 1
    X = CARTEIRAS["A"]["X"]
    print(f"\n--- {f}: sinal em {pd.Timestamp(ds):%d/%m/%Y} (linha {s} de {last})")
    kd = C[s] / C[s - N:s].mean() - 1
    kd1 = C[s - 1] / C[s - N - 1:s - 1].mean() - 1
    print(f"  kairi(d) = {C[s]:.4f} / media({N} fech. ate d-1) - 1 = {kd:.6f} (<= -{X}: {kd <= -X}); "
          f"kairi(d-1) = {kd1:.6f} (> -{X}: {kd1 > -X})")
    assert kd <= -X and kd1 > -X
    e = s + 1
    print(f"  entrada {dts[e]:%d/%m/%Y} (pregao seguinte), abertura = {A_[e]:.4f}, negociou = {g.loc[e, C_NEG]:.0f}")
    lim = min(ORDEM_MAX, PCT_VOL * V_[s])
    cot = int(np.floor(lim / A_[e]))
    print(f"  volume medio 60 em d = {V_[s]:,.0f}; min(3000; 5% x vol) = {lim:.2f}; cotas = floor(lim/abertura) = {cot}")
    assert cot == o_["cotas"]
    kk = mot = px = media = None
    for k in range(e + 1, min(e + PRAZO, last) + 1):
        gap = (dts[k] - dts[k - 1]).days
        ret = C[k] / C[k - 1] - 1
        if gap > 15 or ret > 0.60 or ret < -0.45:
            kk, mot, px = k - 1, GUARDA, C[k - 1]
            break
        m_ = C[k - N:k].mean()
        if H_[k] >= m_:
            kk, mot, px, media = k, VOLTA, max(A_[k], m_), m_
            break
    if kk is None:
        if e + PRAZO <= last:
            kk, mot, px = e + PRAZO, PRAZO_M, C[e + PRAZO]
        else:
            kk, mot, px = last, (ABERTO if (MK.index[MK["data"] == dts[last]][0] >= NM - 21) else SAIU), C[last]
    print(f"  saida {dts[kk]:%d/%m/%Y} ({kk - e} pregoes depois): {mot}; preco = {px:.4f}"
          + (f"; maxima do dia = {H_[kk]:.4f}; abertura = {A_[kk]:.4f}; media ate k-1 = {media:.4f}" if media is not None else ""))
    valor = cot * A_[e]
    venda = cot * px
    val = venda - valor
    tx = 0.0003 * valor + 0.0003 * venda
    incl = mot in (PRAZO_M, ABERTO)
    av = RD[(RD["fundo"] == f) & (RD["data_base"] >= dts[e]) &
            ((RD["data_base"] <= dts[kk]) if incl else (RD["data_base"] < dts[kk]))]
    print(f"  avisos com data_base {'em [entrada; saida]' if incl else 'em [entrada; saida)'}:")
    for _, rr in av.iterrows():
        print(f"    data_base {rr['data_base']:%d/%m/%Y}: {rr['valor (R$/cota)']:.4f} x {cot} cotas = {rr['valor (R$/cota)'] * cot:.2f}")
    rend = float(av["valor (R$/cota)"].sum()) * cot
    imp = 0.20 * max(val - tx, 0)
    res = val + rend - tx - imp
    print(f"  compra {cot} x {A_[e]:.4f} = {valor:.2f}; venda {cot} x {px:.4f} = {venda:.2f}; valorizacao = {val:.2f}")
    print(f"  taxas = 0,03% x {valor:.2f} + 0,03% x {venda:.2f} = {tx:.4f}; imposto = 20% x max({val:.2f} - {tx:.4f}; 0) = {imp:.4f}")
    print(f"  rendimentos = {rend:.4f}; resultado = {val:.4f} + {rend:.4f} - {tx:.4f} - {imp:.4f} = {res:.4f} "
          f"({100 * res / valor:.4f}% do valor)")
    mk = MK[(MK["data"] >= dts[e]) & (MK["data"] < dts[kk])]
    prod = 1.0
    for sv in mk["selic_ano (%)"].fillna(0):
        prod *= (1 + sv / 100) ** (1 / 252)
    dias = (dts[kk] - dts[e]).days
    sel_liq = (prod - 1) * (1 - aliq_rf(dias))
    print(f"  Selic: {len(mk)} pregoes em [entrada; saida), dias corridos = {dias}, IR = {aliq_rf(dias)}; "
          f"acumulada bruta = {100 * (prod - 1):.4f}%; liquida = {100 * sel_liq:.4f}%; em R$ = {valor * sel_liq:.2f}")
    print(f"  diferenca (resultado - Selic) = {res - valor * sel_liq:.2f} R$")
    Lp = L_[e:kk + 1]
    pmin = int(np.argmin(Lp))
    queda = min(0, Lp[pmin] / A_[e] - 1)
    print(f"  menor minima entre entrada e saida = {Lp[pmin]:.4f} em {dts[e + pmin]:%d/%m/%Y} (pregao {pmin} da entrada); "
          f"queda maxima = {100 * queda:.2f}%; ficou abaixo: {queda < 0}")
    pico = float(np.max(C[max(0, s - PRAZO + 1):s + 1]))
    print(f"  pico252 (maior fechamento de {dts[max(0, s - PRAZO + 1)]:%d/%m/%Y} a {dts[s]:%d/%m/%Y}) = {pico:.4f}; "
          f"queda = pico - entrada = {pico - A_[e]:.4f}")
    for rot, fr, pref in FIBO:
        T = A_[e] + fr * (pico - A_[e])
        k2 = None
        for k in range(e + 1, min(e + PRAZO, last) + 1):
            gap = (dts[k] - dts[k - 1]).days
            ret = C[k] / C[k - 1] - 1
            if gap > 15 or ret > 0.60 or ret < -0.45:
                k2 = k - 1
                break
            if H_[k] >= T:
                k2 = k
                break
        print(f"  alvo {rot} = {A_[e]:.4f} + {fr} x {pico - A_[e]:.4f} = {T:.4f} (dist. da entrada {100 * (T / A_[e] - 1):.2f}%)")
    print(f"  SCRIPT: resultado_pct = {100 * o_['resultado_pct']:.4f}%; sel_rs = {o_['sel_rs']:.4f}; "
          f"rend = {o_['rend']:.4f}; pico252 = {o_['pico252']:.4f}")
    assert abs(res / valor - o_["resultado_pct"]) < 1e-9
    assert abs(valor * sel_liq - o_["sel_rs"]) < 1e-6
    assert abs(rend - o_["rend"]) < 1e-6
    assert abs(pico - o_["pico252"]) < 1e-12
    print("  ASSERT PASSOU: resultado %, Selic R$, rendimentos e pico252 batem com o script")


A_ord = OPS[(OPS["carteira"] == "A") & (OPS["fechada"])].sort_values("data_entrada")
ganho_a = A_ord[A_ord["resultado"] > 0].iloc[0]
perda_a = A_ord[A_ord["resultado"] < 0].iloc[0]
print("\n2) CARTEIRA A: duas ordens refeitas a mao (lendo as planilhas brutas, sem FD nem simular)")
refazer(ganho_a)
refazer(perda_a)

# 5) ordens com resultado pior que -30%
print("\n5) ORDENS COM RESULTADO PIOR QUE -30% (fechadas)")
pior = OPS[(OPS["fechada"]) & (OPS["resultado_pct"] < -0.30)].sort_values("resultado_pct")
print(f"total: {len(pior)} (A={int((pior.carteira == 'A').sum())}, B={int((pior.carteira == 'B').sum())}, "
      f"C={int((pior.carteira == 'C').sum())})")
if len(pior):
    print(pd.DataFrame({
        "carteira": pior["carteira"], "fundo": pior["fundo"],
        "entrada": pior["data_entrada"].dt.strftime("%d/%m/%Y"),
        "saida": pior["data_saida"].dt.strftime("%d/%m/%Y"),
        "motivo": pior["motivo"],
        "resultado %": (100 * pior["resultado_pct"]).map(lambda v: br(v, 1) + "%"),
        "queda max %": (100 * pior["queda"]).map(lambda v: br(v, 1) + "%"),
    }).to_string(index=False))

print("\nRESUMO DOS SINAIS (por carteira):")
for nome, st in STATS.items():
    print(f"  {nome}: " + ", ".join(f"{k_}={v}" for k_, v in st.items()))
print(f"ordens sem limite de dinheiro; sinais nao aceitos (ordem < R$ 1.000): {len(NAO)}")

print(f"\nTempo total: {time.time() - T0:.1f} s")
print("1) Roda sem erro.")
