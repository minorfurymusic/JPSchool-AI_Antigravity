"""Simulacao de uma carteira de R$ 20.000 com a estrategia do Kairi, de 02/01/2026 (1o pregao do ano) a 09/11/2026.
VERSAO 2 (2026-11-17): regras novas decididas pelo dono (a versao 1 e recalculada no mesmo programa, so para comparacao).

Duas sub-carteiras independentes, cada uma com caixa proprio de R$ 10.000:
    CONSERVADORA: gatilho 20% abaixo da media de 200 pregoes, rendimento mantido, SO fundos com volume medio de 60 dias
                  (so dados ate o dia do sinal) >= R$ 500.000.
    AGRESSIVA:    gatilho 15% abaixo da media de 200 pregoes, rendimento mantido (igual a versao 1).
    Variante extra da conservadora: gatilho 30%, tambem com volume >= R$ 500.000.
    NAS DUAS (regra 1): nao compra fundo que vai sair da bolsa. No dia do sinal, bloqueia o fundo que teve, nos 365 dias
    corridos ate o dia do sinal (inclusive), fato relevante do proprio fundo (planilhas/tecnico/fatos_textos.csv.gz e
    planilhas/anuncios.csv) tratando de liquidacao/dissolucao/encerramento do fundo, incorporacao, fusao, cisao ou venda
    da totalidade dos ativos. So fatos com data <= dia do sinal.
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
Imagens de conferencia (fora do repositorio): soffice --headless --convert-to pdf ... ; pdftoppm -r 70 -png ...
"""
import re
import time
import unicodedata
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
VOLTA, PRAZO_M, SAIU, GUARDA, ABERTO = "volta à média", "prazo", "saiu da bolsa — valor real desconhecido", "dado suspeito", "em aberto"
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]
VOL_MIN = 500000.0      # regra 2 e 4: volume medio de 60 dias (R$) no dia do sinal
JANELA_FATO = 365       # regra 1: dias corridos de fatos olhados para tras (inclusive o dia do sinal)
# (nome, gatilho, volume minimo)
SUBS = {"Conservadora": (0.20, VOL_MIN), "Agressiva": (0.15, 0.0)}
CONS30 = ("Conservadora 30%", 0.30, VOL_MIN)
SIMS = list(SUBS.items()) + [(CONS30[0], CONS30[1:])]       # (nome, (gatilho, volume minimo))
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


# ---------------------------------------------------------------- regra 1: nao comprar fundo que vai sair da bolsa
def _unacc(t):
    return "".join(unicodedata.normalize("NFD", ch)[0] for ch in t)       # tira acento sem mudar o tamanho do texto


def _P(x):
    return x.replace(" ", r"\s+")


_ATV = r"(ativos|carteira|portfolio|patrimonio|acervo)"
# (nome, expressao). O texto e passado em minusculas e sem acento. "liquidacao financeira", "liquidez" e "liquidacao de CRI" NAO casam.
PADROES_SAIDA = [
    ("liquidação do fundo", _P(r"liquidacao (total |final |antecipada |e encerramento )?d[oea]s? (presente |referido |seu )?fundos?\b|liquidar (o )?fundo|liquidacao e encerramento do fundo")),
    ("dissolução do fundo", _P(r"dissolucao (e liquidacao )?d[oea]s? fundos?\b")),
    ("encerramento do fundo", _P(r"encerramento d[oea]s? (presente |referido |seu )?fundos?\b|encerrar (o )?fundo")),
    ("incorporação do fundo", _P(r"incorporacao d[oe] (presente |referido |seu )?fundo (ao|a|pel[oa]s?|por|em|no)\b|fundo (sera |seja |foi |sendo |esta sendo )?incorporado (ao|a|pel[oa]s?|por|em|no)\b|fundo (sera |seja |foi |sendo |esta sendo )incorporado\b")),
    ("fusão de fundos", _P(r"\bfusao d[oea]s? fundos?\b|\bfusao (do|entre os) fundos?\b|\bfusao entre fundos|\bfusao do (presente )?fundo")),
    ("cisão do fundo", _P(r"\bcisao total|\bcisao d[oe] (presente |referido |seu )?fundo\b")),
    ("venda da totalidade dos ativos", _P(r"(alienacao|aliena[- ]se|venda|aquisicao|transferencia|integralizacao|versao|incorporacao)\W+(\w+\W+){0,8}?(da totalidade|totalidade|100% \(cem por cento\)|100%) d(os|e seus|as|e suas|o|a) " + _ATV)),
    ("alienação dos ativos do fundo", _P(r"alienacao d(os|e todos os) ativos imobiliarios de titularidade do fundo|alienacao de todos os ativos")),
]
_NEG = re.compile(r"reprovad|rejeitad|nao aprovad|nao foi aprovad|desistenc|cancelad|nao sera liquidad|afastad|sem (a )?liquidacao")
_RX = [(n, re.compile(p_)) for n, p_ in PADROES_SAIDA]


def casa_saida(texto):
    """Devolve (expressao, inicio, fim, cancela) ou None.
    Achou expressao de saida da bolsa sem 'reprovada/cancelada/desistencia' por perto -> cancela=False (fato que bloqueia).
    So achou expressoes com esse tipo de negacao por perto -> cancela=True (fato de reprovacao: anula propostas anteriores)."""
    t = _unacc(str(texto).lower())
    neg = None
    for nome_, rx in _RX:
        for m in rx.finditer(t):
            if _NEG.search(t[max(0, m.start() - 140):m.end() + 60]):
                neg = neg or (nome_, m.start(), m.end(), True)
                continue
            return nome_, m.start(), m.end(), False
    return neg


def _carregar_fatos():
    ft = pd.read_csv(PL / "tecnico" / "fatos_textos.csv.gz", sep=";", encoding="utf-8-sig")
    ft = ft.rename(columns={"texto (primeiros 3.000 caracteres)": "texto"})
    an = pd.read_csv(PL / "anuncios.csv", sep=";", encoding="utf-8-sig")
    assert set(ft["id"]) == set(an["id"]), "fatos_textos e anuncios deveriam ter os mesmos ids"
    ft = ft.merge(an[["id", "inicio_do_texto"]], on="id", how="left")
    ft["dia"] = pd.to_datetime(ft["data_anuncio"].str[:10], format="%d/%m/%Y")
    return ft


FATOS = _carregar_fatos()
_hits, _so_anuncio = [], 0
for _r in FATOS.itertuples():
    h, txt = casa_saida(_r.texto), _r.texto
    if h is None:
        h = casa_saida(_r.inicio_do_texto)         # trecho curto de anuncios.csv (so conta se o texto longo nao pegou)
        txt = _r.inicio_do_texto
        if h is None:
            continue
        _so_anuncio += 1
    nome_, a_, b_, canc = h
    snip = re.sub(r"\s+", " ", txt[max(0, a_ - 90):b_ + 90]).strip()
    _hits.append(dict(id=int(_r.id), fundo=_r.fundo, dia=np.datetime64(_r.dia, "D"), padrao=nome_, trecho=snip, tipo=_r.tipo, cancela=canc))
FATOS_SAIDA = [h for h in _hits if not h["cancela"]]
FATOS_CANCELA = [h for h in _hits if h["cancela"]]
FS = {}                                              # fundo -> (dias ordenados, lista de fatos: os que bloqueiam e os que cancelam)
for _f, _g in pd.DataFrame(_hits).groupby("fundo"):
    _g = _g.sort_values(["dia", "id"])
    FS[_f] = (_g["dia"].to_numpy("datetime64[D]"), _g.to_dict("records"))


def bloqueio(fundo, dia_sinal):
    """Fatos de saida da bolsa do fundo com data em [dia_sinal - 365 dias, dia_sinal]. Lista vazia = nao bloqueia.
    Um fato de reprovacao/cancelamento (ex.: 'foi reprovada a dissolucao e liquidacao do Fundo') anula os fatos anteriores a ele."""
    if fundo not in FS:
        return []
    dias, regs = FS[fundo]
    d = np.datetime64(dia_sinal, "D")
    a = np.searchsorted(dias, d - np.timedelta64(JANELA_FATO, "D"), "left")
    b = np.searchsorted(dias, d, "right")
    jan = regs[a:b]
    assert all(r["dia"] <= d for r in jan), "fato do futuro entrou na regra"
    ult_canc = max([r["dia"] for r in jan if r["cancela"]], default=None)
    return [r for r in jan if not r["cancela"] and (ult_canc is None or r["dia"] > ult_canc)]


print(f"regra 1: {len(FATOS)} fatos lidos (fatos_textos.csv.gz + anuncios.csv, mesmos ids); {len(FATOS_SAIDA)} com expressao de saida da bolsa "
      f"e {len(FATOS_CANCELA)} de reprovacao/cancelamento ({_so_anuncio} achados so pelo trecho curto de anuncios.csv); "
      f"fundos com algum fato assim: {len(FS)}")

# candidatos por pregao de execucao; so sinais com data >= 02/01/2026 (carteira comeca vazia).
# Cada candidato leva: volume de 60 dias no dia do sinal e a lista de fatos que bloqueiam (vazia = livre).
CAND = {}
for X in GATILHOS:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if md >= J0 and md + 1 < NM:
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VOL"][s]), bloq=bloqueio(F["nome"], MD[md])))
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


def simular(nome, X, ordem, vol_min=0.0, bloquear=False):
    """vol_min / bloquear = regras 2 e 1 da versao 2. Com vol_min=0 e bloquear=False roda as regras da versao 1."""
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
            if bloquear and c["bloq"]:
                sinais_log.append(dict(base, resultado="bloqueado: pode sair da bolsa"))
                continue
            if vol_min > 0 and not (c["vol"] >= vol_min):
                sinais_log.append(dict(base, resultado="volume abaixo de R$ 500 mil"))
                continue
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
for nome, (X, vmin) in SIMS:
    for ordem in ORDENS:
        RES[(nome, ordem)] = simular(nome, X, ordem, vol_min=vmin, bloquear=True)
RES_V1 = {}                                          # versao 1 (regras antigas), so para comparar
for nome, (X, vmin) in SIMS:
    for ordem in ORDENS:
        RES_V1[(nome, ordem)] = simular(nome, X, ordem, vol_min=0.0, bloquear=False)
print(f"simulacoes rodadas: {len(RES)} da versao 2 + {len(RES_V1)} da versao 1 (comparacao); tempo: {time.time() - T0:.1f} s")


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


for R in list(RES.values()) + list(RES_V1.values()):
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
        res_ops=float(o["resultado"].sum()), n=len(o),
        n_bloq=int((sin["resultado"] == "bloqueado: pode sair da bolsa").sum()), n_vol=int((sin["resultado"] == "volume abaixo de R$ 500 mil").sum()),
        n_saiu=int((o["motivo"] == SAIU).sum()), v_saiu=float(o.loc[o["motivo"] == SAIU, "valor_compra"].sum()))


def metricas_ref(serie, cap, nome):
    q, dp, df_ = queda_max(serie, cap)
    return dict(nome=nome, cap=cap, pat=serie, p_ini=cap, p_fim=float(serie[-1]), ret=float(serie[-1] / cap - 1),
                p_liq=float(serie[-1]), ret_liq=float(serie[-1] / cap - 1), queda=q, d_pico=dp, d_fundo=df_)


BASE = {n: RES[(n, ORDEM_BASE)] for n in list(SUBS) + [CONS30[0]]}
BASE_V1 = {n: RES_V1[(n, ORDEM_BASE)] for n in BASE}
M = {n: metricas([BASE[n]], n) for n in BASE}
M["Total"] = metricas([BASE["Conservadora"], BASE["Agressiva"]], "Total")
M["CDI"] = metricas_ref(CDI20, 2 * CAP_SUB, "105% do CDI")
M["Mercado"] = metricas_ref(MERC20, 2 * CAP_SUB, "Mercado")
TOTAL_PAT = BASE["Conservadora"]["pat"] + BASE["Agressiva"]["pat"]
APLIC = {n: BASE[n]["pos_val"] / BASE[n]["pat"] for n in BASE}
APLIC["Total"] = (BASE["Conservadora"]["pos_val"] + BASE["Agressiva"]["pos_val"]) / TOTAL_PAT

M_V1 = {n: metricas([BASE_V1[n]], n) for n in BASE_V1}
M_V1["Total"] = metricas([BASE_V1["Conservadora"], BASE_V1["Agressiva"]], "Total")
assert all(m_["n_bloq"] == 0 and m_["n_vol"] == 0 for m_ in M_V1.values())
TOTAL_PAT_V1 = BASE_V1["Conservadora"]["pat"] + BASE_V1["Agressiva"]["pat"]
# a versao 1 recalculada aqui tem que dar os mesmos numeros que estavam no documento da versao 1
V1_DOC = {"Conservadora": (10170.81, 10170.81), "Agressiva": (10426.20, 10365.26), "Total": (20597.01, 20536.07)}
for k_, (pf_, pl_) in V1_DOC.items():
    assert abs(M_V1[k_]["p_fim"] - pf_) < 0.006 and abs(M_V1[k_]["p_liq"] - pl_) < 0.006, (k_, M_V1[k_]["p_fim"], M_V1[k_]["p_liq"])
assert abs(RES_V1[("Conservadora 30%", 1000.0)]["pat"][-1] - 10246.71) < 0.006

# ================================================================ REGRA 1: fundos bloqueados
# 1a) bloqueios dos sinais de 2026 (todos os gatilhos), um por (fundo, dia do sinal)
_bl = {}
for X in GATILHOS:
    for lst in CAND[X]:
        for c in lst:
            if c["bloq"]:
                k_ = (c["F"]["nome"], TS[c["md"]])
                d_ = _bl.setdefault(k_, dict(fundo=k_[0], sinal=k_[1], gatilhos=set(), vol=c["vol"], fatos=c["bloq"]))
                d_["gatilhos"].add(X)
comprou_v1 = {}
for n_, R in BASE_V1.items():
    for o in R["ops_raw"]:
        comprou_v1.setdefault((o["fundo"], o["sinal"]), []).append(f"{n_} (entrada {dt(o['entrada'])})")
SUBCART = {0.15: "Agressiva", 0.20: "Conservadora", 0.30: "Conservadora 30%"}
# leitura manual (feita depois de ver o trecho e os fatos seguintes): classe de cada bloqueio. O programa exige uma linha por bloqueio.
VERD, PR_AP, PR_RE, PR_PE = ("verdadeiro: saída aprovada ou concluída", "proposta na data, aprovada depois",
                             "proposta na data, reprovada depois", "proposta ainda pendente em 09/11/2026")
AVAL = {
    ("XPIN11", "23/06/2026"): (VERD, "Venda de todos os imóveis concluída em 14/04/2026; preços acabam em 13/07/2026."),
    ("XPIN11", "02/07/2026"): (VERD, "Fato de 30/06: liquidação final e encerramento do fundo."),
    ("ITIT11", "03/07/2026"): (PR_RE, "Fato de 26/06: proposta de consolidar o fundo no INHF, com liquidação, 'caso aprovada'. Reprovada em 07/08/2026; o fundo segue negociando."),
    ("ITIP11", "07/07/2026"): (PR_AP, "Fato de 26/06: mesma proposta de reorganização com liquidação; aprovada em 27/07/2026; preços acabam em 03/09/2026."),
    ("HCHG11", "14/07/2026"): (VERD, "Consulta formal aprovada em 11/2025: venda de 100% dos ativos ao VVCR e liquidação do fundo; fato de 09/07/2026 inicia a liquidação."),
    ("HCHG11", "15/07/2026"): (VERD, "Mesmo fato de 09/07/2026 (liquidação do fundo)."),
    ("ITIP11", "05/08/2026"): (VERD, "Fato de 27/07: aprovada a dissolução e liquidação do fundo."),
    ("ITIP11", "07/08/2026"): (VERD, "Idem (fatos de 27/07 e 07/08)."),
    ("OUJP11", "11/08/2026"): (PR_PE, "Fato de 01/06: a liquidação 'somente ocorrerá caso as aquisições sejam aprovadas'. Fatos de outubro tratam só de troca de administradora; o fundo negocia até 09/11."),
    ("OUJP11", "27/08/2026"): (PR_PE, "Idem."),
    ("OUJP11", "28/10/2026"): (PR_PE, "Idem."),
    ("OUJP11", "04/11/2026"): (PR_PE, "Idem."),
    ("RBRR11", "18/09/2026"): (PR_AP, "Fato de 21/08: reorganização com liquidação, 'caso aprovada'; aprovada em 28/10/2026."),
    ("RBRR11", "22/09/2026"): (PR_AP, "Idem."),
    ("RBRR11", "02/10/2026"): (PR_AP, "Idem."),
    ("RBRR11", "27/10/2026"): (PR_AP, "Idem (aprovada no dia seguinte)."),
    ("RBRR11", "03/11/2026"): (VERD, "Fato de 28/10: aquisição dos ativos pelo PCIP11 aprovada; cronograma de liquidação do fundo em dezembro."),
    ("RPRI11", "03/11/2026"): (VERD, "Fato de 21/08 (proposta com liquidação); aprovada em 28/10/2026, antes do sinal (a regra mostra o fato de 21/08, mas o de 28/10 já confirmava)."),
}
BL26 = []
for (f_, sd_), d_ in sorted(_bl.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    ft = d_["fatos"][-1]
    ch = AVAL.get((f_, dt(sd_)))
    assert ch is not None, ("bloqueio sem avaliacao manual", f_, dt(sd_))
    sub = []
    for X in sorted(d_["gatilhos"]):
        if X == 0.15:
            sub.append("Agressiva")
        else:
            sub.append(SUBCART[X] if d_["vol"] >= VOL_MIN else SUBCART[X] + " (já fora pelo volume)")
    BL26.append(dict(fundo=f_, sinal=sd_, gatilhos=", ".join(f"{int(100 * x)}%" for x in sorted(d_["gatilhos"])), sub=", ".join(sub),
                     vol=d_["vol"], n_fatos=len(d_["fatos"]), dia_fato=pd.Timestamp(ft["dia"]), id_fato=ft["id"], padrao=ft["padrao"],
                     trecho=ft["trecho"], classe=ch[0], nota=ch[1], v1="; ".join(comprou_v1.get((f_, sd_), [])) or "—"))
assert len(BL26) == len(AVAL), "ha avaliacao manual sobrando ou faltando"
BL26 = pd.DataFrame(BL26)
for r_ in BL26.itertuples():
    assert r_.dia_fato <= r_.sinal and (r_.sinal - r_.dia_fato).days <= JANELA_FATO
n_verd = int((BL26["classe"] == VERD).sum())
n_pap = int((BL26["classe"] == PR_AP).sum())
n_pre = int((BL26["classe"] == PR_RE).sum())
n_ppe = int((BL26["classe"] == PR_PE).sum())
n_err = 0                                              # trechos que NAO tratam de saida do proprio fundo: nenhum, pela leitura
print("\n" + "=" * 100)
print("REGRA 1: FUNDOS BLOQUEADOS EM 2026 (sinais de todos os gatilhos; fato <= dia do sinal, ate 365 dias antes)")
print("=" * 100)
for r_ in BL26.itertuples():
    print(f"{r_.fundo} | sinal {dt(r_.sinal)} (gatilho {r_.gatilhos}; vol60 R$ {br(r_.vol, 0)}; barra {r_.sub}) | fato de {dt(r_.dia_fato)} [{r_.padrao}] "
          f"(+{r_.n_fatos - 1} outros)\n    trecho: ...{r_.trecho}...\n    leitura: {r_.classe}. {r_.nota}   Versao 1 comprou? {r_.v1}")
print(f"\nBloqueios de 2026: {len(BL26)} (fundo x dia do sinal), {BL26['fundo'].nunique()} fundos: {', '.join(sorted(BL26['fundo'].unique()))}.")
print(f"Leitura de todos os {len(BL26)}: verdadeiros (saida aprovada/concluida) {n_verd}; propostas depois aprovadas {n_pap}; "
      f"propostas depois reprovadas {n_pre}; propostas ainda pendentes em 09/11 {n_ppe}; trechos que nao tratam de saida do proprio fundo (erro de leitura) {n_err}.")

# 1b) os 3 fundos que a versao 1 comprou e saiam da bolsa
print("\nCONFIRMACAO: HCHG11, XPIN11 e ITIP11 nas datas em que a versao 1 os comprou")
CONF3 = []
for f_ in ["HCHG11", "XPIN11", "ITIP11"]:
    ops1 = [o for R in BASE_V1.values() for o in R["ops_raw"] if o["fundo"] == f_]
    assert ops1, f_
    for o in ops1:
        bl = bloqueio(f_, MD[o["mi_d"]])
        assert bl, (f_, "NAO foi bloqueado")
        fut = [h for h in FATOS_SAIDA if h["fundo"] == f_ and h["dia"] > np.datetime64(o["sinal"], "D")]
        lista = "; ".join(f"{dt(pd.Timestamp(h['dia']))} (id {h['id']}, {h['padrao']})" for h in bl)
        print(f"  {f_}: {o['carteira']} comprou com sinal em {dt(o['sinal'])} (entrada {dt(o['entrada'])}) -> BLOQUEADO por {len(bl)} fato(s): {lista}")
        print(f"      trecho do mais recente: ...{bl[-1]['trecho']}...")
        if fut:
            print(f"      fatos de saida POSTERIORES ao sinal (ignorados pela regra): " + "; ".join(dt(pd.Timestamp(h['dia'])) for h in fut))
        CONF3.append(f"{f_}: a versão 1 comprou (sub-carteira {o['carteira']}, sinal {dt(o['sinal'])}, entrada {dt(o['entrada'])}); a regra bloqueia por "
                     f"{len(bl)} fato(s) de saída até o sinal ({lista}). Trecho do mais recente ({dt(pd.Timestamp(bl[-1]['dia']))}): “…{bl[-1]['trecho']}…”")
        if fut:
            CONF3[-1] += f" Fatos de saída posteriores ao sinal, ignorados: {', '.join(dt(pd.Timestamp(h['dia'])) for h in fut)}."
for f_ in ["HCHG11", "XPIN11", "ITIP11"]:
    assert not any(o["fundo"] == f_ for R in BASE.values() for o in R["ops_raw"]), f"{f_} ainda foi comprado na versao 2"
print("  confirmado: HCHG11, XPIN11 e ITIP11 foram bloqueados em todas as compras da versao 1 e nao aparecem em nenhuma compra da versao 2: PASSOU")

# 1c) a regra rodada no periodo todo, 2018 a 2026 (informativo): quantos sinais/fundos ela bloquearia
HIST = []
amostra_pool = []
for X in GATILHOS:
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if TS[md] < pd.Timestamp("2018-01-01") or md + 1 >= NM:
                continue
            bl = bloqueio(F["nome"], MD[md])
            last = F["n"] - 1
            saiu = (s + PRAZO > last) and (not F["aberto"])             # os precos acabam antes do prazo de 252 pregoes
            tem_hor = (s + PRAZO <= last) or (not F["aberto"])          # da pra saber o desfecho (fundo vivo com 252 pregoes pela frente, ou que parou)
            HIST.append(dict(X=X, fundo=F["nome"], ano=TS[md].year, sinal=TS[md], vol=float(F["VOL"][s]), bloq=bool(bl), saiu=saiu, tem_hor=tem_hor,
                             fato=bl[-1] if bl else None))
HIST = pd.DataFrame(HIST)
print("\nREGRA 1 NO PERIODO TODO, 2018 a 2026 (informativo; sinais com os mesmos filtros de universo)")
LIN_H = []
for X in GATILHOS:
    h = HIST[HIST["X"] == X]
    b = h[h["bloq"]]
    LIN_H.append([f"{int(100 * X)}%", len(h), h["fundo"].nunique(), len(b), pct(len(b) / len(h)), b["fundo"].nunique(),
                  f"{int(b['saiu'].sum())} de {int(b['tem_hor'].sum())}", f"{int(h[~h['bloq']]['saiu'].sum())} de {int(h[~h['bloq']]['tem_hor'].sum())}"])
    print("  ", LIN_H[-1])
LIN_HA = []
h = HIST[HIST["X"] == 0.20]
for ano in range(2018, 2027):
    ha = h[h["ano"] == ano]
    hb = ha[ha["bloq"]]
    LIN_HA.append([ano, len(ha), len(hb), hb["fundo"].nunique(), int((ha["vol"] >= VOL_MIN).sum()), int(((ha["vol"] >= VOL_MIN) & ha["bloq"]).sum())])
print("  gatilho 20% por ano:", LIN_HA)
# amostra de 20 bloqueios de 2018 a 2025 (todos os gatilhos), sorteados com semente fixa, para ler o trecho e contar os falsos
_pool = HIST[HIST["bloq"] & (HIST["ano"] <= 2025)].groupby(["fundo", "sinal"], as_index=False).agg(
    gat=("X", lambda v: ", ".join(f"{int(100 * x)}%" for x in sorted(set(v)))), saiu=("saiu", "max"), fato=("fato", "last"))
AMOSTRA = _pool.sample(min(20, len(_pool)), random_state=7).sort_values(["sinal", "fundo"]).reset_index(drop=True)
_txt_id = dict(zip(FATOS["id"], FATOS["texto"]))


def contexto_fato(h, w=230):
    t = _txt_id[h["id"]]
    m = casa_saida(t)
    return re.sub(r"\s+", " ", t[max(0, m[1] - w):m[2] + w]).strip()


H_OK, H_FALSO, H_OUTROS = ("acerto: os preços do fundo acabam depois", "falso: o fundo continuou negociando (preços até 09/11/2026)",
                           "trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo)")
AVAL_H = {
    ("SAAG11", "15/04/2020"): (H_OK, "Cotistas aprovam a incorporação do fundo pelo RBVA."),
    ("ABCP11", "26/11/2021"): (H_FALSO, "Cisão do fundo (parcial); o fundo segue negociando."),
    ("ABCP11", "01/12/2021"): (H_FALSO, "Idem."),
    ("BRCR11", "01/10/2024"): (H_FALSO, "Texto fala de saldo da 'liquidação do Fundo' por amortização de caixa e entrega de cotas do CENESP; mesmo assim o BRCR11 segue com preços até 09/11/2026 (operação parcial ou código reaproveitado: não dá para saber pela base)."),
    ("VRTM11", "01/10/2024"): (H_FALSO, "O VRTM seria o comprador da totalidade dos ativos (de outro fundo); o VRTM11 segue negociando."),
    ("RBED11", "04/11/2024"): (H_OK, "Venda de 100% dos ativos do fundo ao RBVA11."),
    ("RBED11", "11/11/2024"): (H_OK, "Idem."),
    ("BRCR11", "28/11/2024"): (H_FALSO, "Idem BRCR11 de 01/10/2024."),
    ("RVBI11", "04/12/2024"): (H_OUTROS, "Texto sobre leilão de frações e liquidação dos fundos BLMR, BLMC, MORC e MORE, não sobre o próprio RVBI11 (cujos preços acabam em 30/10/2025)."),
    ("BRCR11", "09/12/2024"): (H_FALSO, "Idem BRCR11 de 01/10/2024."),
    ("RVBI11", "16/12/2024"): (H_OUTROS, "Idem."),
    ("RVBI11", "08/01/2025"): (H_OUTROS, "Idem."),
    ("RVBI11", "10/01/2025"): (H_OUTROS, "Idem."),
    ("RVBI11", "17/01/2025"): (H_OUTROS, "Idem."),
    ("RVBI11", "07/02/2025"): (H_OUTROS, "Idem."),
    ("VRTM11", "17/03/2025"): (H_FALSO, "Idem VRTM11 de 01/10/2024."),
}
assert {(r_.fundo, dt(r_.sinal)) for r_ in AMOSTRA.itertuples()} == set(AVAL_H), "a amostra mudou: refazer a leitura manual de AVAL_H"
print(f"\n  (os bloqueios de 2018 a 2025, todos os gatilhos, sao {len(_pool)} pares fundo x dia do sinal; amostra de {len(AMOSTRA)}, semente 7)")
for r_ in AMOSTRA.itertuples():
    print(f"   {r_.fundo} sinal {dt(r_.sinal)} (gat {r_.gat}) | fato de {dt(pd.Timestamp(r_.fato['dia']))} [{r_.fato['padrao']}] | os precos acabam em ate 252 pregoes? "
          f"{'sim' if r_.saiu else 'nao'}\n        ...{contexto_fato(r_.fato)}...\n        leitura: {AVAL_H[(r_.fundo, dt(r_.sinal))][0]}. {AVAL_H[(r_.fundo, dt(r_.sinal))][1]}")
N_H = {c: sum(1 for v in AVAL_H.values() if v[0] == c) for c in (H_OK, H_FALSO, H_OUTROS)}
print(f"  leitura dos {len(AMOSTRA)}: acertos {N_H[H_OK]}; falsos (fundo continuou negociando) {N_H[H_FALSO]}; trecho sobre outros fundos {N_H[H_OUTROS]}")


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
    if c.empty:
        c = o[o["rend_recebido"] > 0]                      # sem fechadas: confere uma operacao em aberto (a preco de 09/11)
    if c.empty:
        c = o
    op = c.iloc[0] if escolha == "primeira" else c.iloc[-1]
    fechada = op["status"] == "Fechada"
    f = op["fundo"]
    g = PR[PR["fundo"] == f].reset_index(drop=True)
    e = int(g.index[g["data"] == op["entrada"]][0])
    k = int(g.index[g["data"] == op["saida"]][0]) if fechada else len(g) - 1
    ab = float(g.loc[e, C_AB])
    compra = op["cotas"] * ab
    taxa_c = B3 * compra
    if not fechada:
        ps = float(g.loc[k, C_FE])
        txt_s = f"ultimo fechamento ({dt(g.loc[k, 'data'])}) {ps:.2f}"
    elif op["motivo"] == VOLTA:
        media = float(g[C_FE].iloc[k - N:k].mean())
        ps = max(float(g.loc[k, C_AB]), media)
        txt_s = f"max(abertura {g.loc[k, C_AB]:.2f}; media dos 200 fechamentos anteriores {media:.4f}) = {ps:.4f}"
    else:
        ps = float(g.loc[k, C_FE])
        txt_s = f"fechamento {ps:.2f}"
    venda = op["cotas"] * ps
    taxa_v = B3 * venda if fechada else 0.0
    incl = op["motivo"] in (PRAZO_M, ABERTO)
    fim_ = op["saida"] if fechada else g.loc[k, "data"]
    msk = (PG["fundo"] == f) & (PG["data_base"] >= op["entrada"]) & ((PG["data_base"] <= fim_) if incl else (PG["data_base"] < fim_))
    av = PG[msk]
    rend = float(av["valor (R$/cota)"].sum()) * op["cotas"]
    res = venda - compra + rend - taxa_c - taxa_v
    sit = f"saida {dt(op['saida'])} ({op['motivo']})" if fechada else "em aberto em 09/11/2026 (a preco do ultimo fechamento)"
    print(f"\n  [{rotulo}] {f}: sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])} (depois do sinal), {sit}")
    print(f"    compra: {int(op['cotas'])} cotas x abertura {ab:.2f} = {compra:.2f}; taxa 0,03% = {taxa_c:.4f}")
    for _, a in av.iterrows():
        print(f"    rendimento: data-base {dt(a['data_base'])}, {a['valor (R$/cota)']:.4f}/cota x {int(op['cotas'])} = "
              f"{a['valor (R$/cota)'] * op['cotas']:.4f}; pago em {dt(a['data_pagamento'])}")
    print(f"    {'venda' if fechada else 'valor atual'}: {int(op['cotas'])} cotas x {txt_s} = {venda:.2f}; taxa 0,03% = {taxa_v:.4f}")
    print(f"    resultado = {venda:.2f} - {compra:.2f} + {rend:.4f} - {taxa_c:.4f} - {taxa_v:.4f} = {res:.4f}"
          f" ({100 * res / compra:.4f}% da compra)")
    print(f"    programa: compra {op['valor_compra']:.2f}, {'venda' if fechada else 'valor atual'} "
          f"{op['valor_venda'] if fechada else op['cotas'] * op['preco_saida']:.2f}, rendimentos {op['rend_direito']:.4f}, "
          f"taxas {op['taxas']:.4f}, resultado {op['resultado']:.4f} ({100 * op['resultado_pct']:.4f}%)")
    assert abs(compra - op["valor_compra"]) < 1e-6 and abs(venda - (op["valor_venda"] if fechada else op["cotas"] * op["preco_saida"])) < 1e-6
    assert abs(rend - op["rend_direito"]) < 1e-6 and abs(res - op["resultado"]) < 1e-6
    for _, a in av.iterrows():
        if pd.notna(a["data_pagamento"]) and np.datetime64(a["data_pagamento"], "D") <= MD[-1]:
            q = R["rend"][(R["rend"]["fundo"] == f) & (R["rend"]["data_base"] == a["data_base"])]
            assert len(q) >= 1, "pagamento nao entrou no caixa"
            dpay = q.iloc[0]["data"]
            esperado = TS[int(np.searchsorted(MD, np.datetime64(a["data_pagamento"], "D"), "left"))]
            assert dpay == esperado
            print(f"    rendimento caiu no caixa em {dt(dpay)} (pagamento {dt(a['data_pagamento'])}; "
                  f"se nao era pregao, vai ao pregao seguinte): PASSOU")
    print("    ASSERT PASSOU (compra, rendimento, valor, taxas e resultado batem com o programa)")
    return (f"{rotulo}, {f} (sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])}, {'saída ' + dt(op['saida']) if fechada else 'em aberto em 09/11/2026'}): compra {int(op['cotas'])} cotas × "
            f"R$ {br(ab)} = {brl(compra)}; rendimentos {brl(rend)}; {'venda' if fechada else 'valor atual'} {brl(venda)}; taxas {brl(taxa_c + taxa_v, 2)}; "
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
for nome, (X, vmin) in SIMS:
    for ordem in ORDENS:
        m = metricas([RES[(nome, ordem)]], nome)
        m1 = metricas([RES_V1[(nome, ordem)]], nome)
        VAR.append(dict(m, X=X, ordem=ordem, vmin=vmin, ret_liq_v1=m1["ret_liq"], p_liq_v1=m1["p_liq"], n_v1=m1["n"]))
        print(f"  {nome:18s} ordem {brl(ordem, 0):>10s}: final {brl(m['p_fim'])}; liquido {brl(m['p_liq'])}; retorno liq {pct(m['ret_liq'])}; "
              f"queda {pct(m['queda'])}; operacoes {m['n']}; giro {br(m['giro'], 2)}; sem dinheiro {m['sem_din']}")
print(f"  105% do CDI (R$ 10.000): {brl(CDI10[-1])} ({pct(CDI10[-1] / CAP_SUB - 1)})")

# ---------------------------------------------------------------- POSICOES ABERTAS em 09/11/2026
def posicoes_abertas():
    rows = []
    for nome_ in ("Conservadora", "Agressiva"):
        R = BASE[nome_]
        for nm_, P in R["pos"].items():
            op, F = P["op"], P["F"]
            rr = int(op["rr"])
            ult, d_ult = float(F["C"][rr]), pd.Timestamp(F["dates"][rr])
            val_atual = op["cotas"] * ult
            valoriz = val_atual - op["valor_compra"]
            res = valoriz + op["rend_recebido"] - op["taxa_compra"]
            rows.append(dict(carteira=nome_, fundo=nm_, entrada=op["entrada"], preco_entrada=op["preco_entrada"], cotas=int(op["cotas"]),
                             valor_entrada=op["valor_compra"], ult_preco=ult, data_ult=d_ult, valor_atual=val_atual,
                             rend_pago=op["rend_recebido"], rend_receber=op["rend_a_receber"], rend_sem_data=op["rend_sem_data"],
                             valoriz=valoriz, taxa=op["taxa_compra"], resultado=res, resultado_pct=res / op["valor_compra"],
                             sinal="positivo" if res > 0 else "negativo", rotulo=f"{nm_} {op['entrada']:%d/%m}"))
    d = pd.DataFrame(rows)
    d["ordc"] = d["carteira"].map({"Conservadora": 0, "Agressiva": 1})
    return d.sort_values(["ordc", "entrada", "fundo"]).drop(columns="ordc").reset_index(drop=True)


POS = posicoes_abertas()
for nome_ in ("Conservadora", "Agressiva"):
    g_ = POS[POS["carteira"] == nome_]
    assert abs(g_["valor_atual"].sum() - float(BASE[nome_]["dia"]["posicoes"].iloc[-1])) < 1e-6, "valor atual das abertas != posicoes do patrimonio"
    assert len(g_) == BASE[nome_]["o"]["status"].ne("Fechada").sum()
    assert (g_["data_ult"] <= TS[-1]).all()
TOT_POS = {}
for nome_ in ("Conservadora", "Agressiva"):
    g_ = POS[POS["carteira"] == nome_]
    TOT_POS[nome_] = dict(n=len(g_), valor_entrada=float(g_["valor_entrada"].sum()), valor_atual=float(g_["valor_atual"].sum()),
                          rend_pago=float(g_["rend_pago"].sum()), rend_receber=float(g_["rend_receber"].sum()), valoriz=float(g_["valoriz"].sum()),
                          taxa=float(g_["taxa"].sum()), resultado=float(g_["resultado"].sum()),
                          resultado_pct=float(g_["resultado"].sum() / g_["valor_entrada"].sum()),
                          n_neg=int((g_["resultado"] < 0).sum()), n_pos=int((g_["resultado"] > 0).sum()))
print("\n" + "=" * 100)
print("POSICOES ABERTAS EM 09/11/2026 (ordem R$ 1.000; resultado = valorizacao + rendimentos JA PAGOS - taxa de compra)")
print("=" * 100)
for nome_ in ("Conservadora", "Agressiva"):
    print(f"\n{nome_}:")
    print(f"  {'fundo':8s} {'entrada':10s} {'pr.entr.':>9s} {'cotas':>5s} {'valor entr.':>12s} {'ult.preco':>9s} {'data':10s} {'valor atual':>12s} {'rend.pago':>10s} "
          f"{'a receber':>10s} {'resultado':>11s} {'res.%':>7s}  sinal")
    for r_ in POS[POS["carteira"] == nome_].itertuples():
        print(f"  {r_.fundo:8s} {dt(r_.entrada):10s} {br(r_.preco_entrada):>9s} {r_.cotas:5d} {br(r_.valor_entrada):>12s} {br(r_.ult_preco):>9s} {dt(r_.data_ult):10s} "
              f"{br(r_.valor_atual):>12s} {br(r_.rend_pago):>10s} {br(r_.rend_receber):>10s} {br(r_.resultado):>11s} {pct(r_.resultado_pct):>7s}  {r_.sinal}")
    t_ = TOT_POS[nome_]
    print(f"  {'TOTAL':8s} {'':10s} {'':>9s} {'':>5s} {br(t_['valor_entrada']):>12s} {'':>9s} {'':10s} {br(t_['valor_atual']):>12s} {br(t_['rend_pago']):>10s} "
          f"{br(t_['rend_receber']):>10s} {br(t_['resultado']):>11s} {pct(t_['resultado_pct']):>7s}  {t_['n_pos']} positivas / {t_['n_neg']} negativas ({t_['n']} posicoes)")

# fundos comprados que depois sairam da bolsa (calculo mantido pelo ultimo preco; valor real desconhecido)
SAIU_DF = pd.concat([BASE[n]["o"] for n in ("Conservadora", "Agressiva")], ignore_index=True)
SAIU_DF = SAIU_DF[SAIU_DF["motivo"] == SAIU].sort_values(["carteira", "entrada"]).reset_index(drop=True)
print("\nFUNDOS COMPRADOS QUE SAIRAM DA BOLSA (valor real desconhecido; calculo pelo ultimo preco registrado):")
if SAIU_DF.empty:
    print("  nenhum")
for r_ in SAIU_DF.itertuples():
    print(f"  {r_.carteira}: {r_.fundo}, entrada {dt(r_.entrada)}, ultimo preco R$ {br(r_.preco_saida)} em {dt(r_.saida)}; comprado {brl(r_.valor_compra)}; "
          f"valor pelo ultimo preco {brl(r_.valor_venda)}; resultado simulado {brl(r_.resultado)} ({pct(r_.resultado_pct)}) -> SAIU DA BOLSA, VALOR REAL DESCONHECIDO")

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
ws["A1"] = "Carteira Kairi de R$ 20.000 em 2026: resumo (versão 2, de 17/11/2026)"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = (f"De {dt(TS[J0])} (1º pregão do ano) a {dt(TS[-1])} (último preço da base). Duas sub-carteiras de R$ 10.000, "
            f"ordem de R$ 1.000. Versão 2: Conservadora = cota 20% abaixo da média de 200 pregões E volume médio de 60 dias de R$ 500 mil ou mais; "
            f"Agressiva = 15% abaixo; nas duas, fundo com fato relevante de liquidação/incorporação/venda de todos os ativos nos 365 dias até o sinal NÃO é comprado. "
            f"As três últimas colunas mostram a versão 1 (regras antigas) para comparar. Um ano só não prova nada: leia a aba 'Legenda e avisos'.")
ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A2:I2")
ws.row_dimensions[2].height = 78
cab(ws, 4, ["Indicador", "Conservadora (20%, vol. ≥ R$ 500 mil) — v2", "Agressiva (15%) — v2", "Total (R$ 20 mil) — v2", "105% do CDI (R$ 20 mil)",
            "Mercado (R$ 20 mil)", "Conservadora (20%) — versão 1", "Agressiva (15%) — versão 1", "Total (R$ 20 mil) — versão 1"], [84, 24, 22, 22, 24, 22, 22, 22, 22])
ws.row_dimensions[4].height = 48
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
    ("Sinais bloqueados pela regra 1 (fundo que pode sair da bolsa)", lambda m: m.get("n_bloq", ND), '0'),
    ("Sinais barrados pelo volume (< R$ 500 mil), regra 2", lambda m: m.get("n_vol", ND), '0'),
    ("Compras que depois saíram da bolsa (valor real desconhecido)", lambda m: m.get("n_saiu", ND), '0'),
    ("Sinais que ficaram sem dinheiro", lambda m: m.get("sem_din", ND), '0'),
    ("Total comprado em fundos (R$)", lambda m: m.get("comprado", ND), F_BRL),
    ("Giro (total comprado ÷ patrimônio médio)", lambda m: m.get("giro", ND), '0.00'),
    ("Tempo médio por operação fechada (dias corridos)", lambda m: m.get("tempo", ND), '0.0'),
    ("Parte do dinheiro aplicada em fundos, em média (%)", lambda m: m.get("aplicado", ND), F_PCT),
]
for i, (nome_l, fn, fmt) in enumerate(LIN, 5):
    ws.cell(row=i, column=1, value=nome_l)
    for j, (k, MM_) in enumerate([(c_, M) for c_ in cols_m] + [(c_, M_V1) for c_ in ("Conservadora", "Agressiva", "Total")], 2):
        v = fn(MM_[k])
        if isinstance(v, (float, np.floating)) and np.isnan(v):
            v = ND
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
        c = ws.cell(row=i, column=j, value=v)
        c.number_format = fmt
        c.alignment = Alignment(horizontal="right")
        if j >= 7:
            c.fill = PatternFill("solid", fgColor="F4F4F4")
    ws.cell(row=i, column=1).border = BORDA
i_dif = 5 + len(LIN)
ws.cell(row=i_dif, column=1, value="Diferença no retorno líquido: versão 2 menos versão 1 (pontos percentuais)").font = Font(bold=True)
for j, k in zip((2, 3, 4), ("Conservadora", "Agressiva", "Total")):
    c = ws.cell(row=i_dif, column=j, value=100 * (M[k]["ret_liq"] - M_V1[k]["ret_liq"]))
    c.number_format = '0.0'
    c.font = Font(bold=True)
r_fim = 5 + len(LIN) + 2
ws.cell(row=r_fim, column=1, value=("Observação: 'Patrimônio final' soma o caixa (líquido de IR e IOF do 105% do CDI) com as cotas a preço de "
                                    "09/11/2026. O 'líquido' ainda desconta o imposto do FII que seria devido ao vender tudo. "
                                    "Em 105% do CDI o imposto já está descontado, como se fosse resgatado em 09/11.")).alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells(start_row=r_fim, start_column=1, end_row=r_fim, end_column=9)
ws.row_dimensions[r_fim].height = 48
ws.freeze_panes = "B5"

# ------------------------------------------------ Patrimonio dia a dia
wp = wb.create_sheet("Patrimônio dia a dia")
cab(wp, 1, ["Data", "Conservadora (R$)", "Agressiva (R$)", "Total (R$)", "105% do CDI, R$ 20 mil (R$)",
            "Mercado, R$ 20 mil (R$)", "105% do CDI, R$ 10 mil (R$)", "Total da versão 1, regras antigas (R$)"], [13, 18, 18, 18, 24, 22, 24, 24])
wp.row_dimensions[1].height = 45
for i in range(NDIA):
    r = i + 2
    wp.cell(row=r, column=1, value=DATAS[i].to_pydatetime()).number_format = F_DATA
    for j, v in enumerate([BASE["Conservadora"]["pat"][i], BASE["Agressiva"]["pat"][i], TOTAL_PAT[i], CDI20[i], MERC20[i], CDI10[i], TOTAL_PAT_V1[i]], 2):
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


ymin1 = arred_min(min(TOTAL_PAT.min(), CDI20.min(), MERC20.min(), TOTAL_PAT_V1.min()) * 0.99, 500)
ymax1 = float(np.ceil(max(TOTAL_PAT.max(), CDI20.max(), MERC20.max(), TOTAL_PAT_V1.max()) * 1.01 / 500) * 500)
grafico_linhas(wp, "Total de R$ 20 mil: carteira (v2 e v1), 105% do CDI e mercado", [4, 8, 5, 6], [COR["tot"], "B26BD6", COR["cdi"], COR["merc"]],
               ymin1, ymax1, "J2", dash=(1,))
allsub = np.r_[BASE["Conservadora"]["pat"], BASE["Agressiva"]["pat"], CDI10]
ymin2 = arred_min(allsub.min() * 0.99, 250)
ymax2 = float(np.ceil(allsub.max() * 1.01 / 250) * 250)
grafico_linhas(wp, "Cada sub-carteira (R$ 10 mil) contra 105% do CDI", [2, 3, 7], [COR["cons"], COR["agr"], COR["cdi"]],
               ymin2, ymax2, "J23")

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
        if r["motivo"] == SAIU:
            c.fill = PatternFill("solid", fgColor="FDE2E2")
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
      "Retorno líquido (versão 2)", "Maior queda (%)", "Operações", "Giro", "Sinais sem dinheiro", "Rótulo do gráfico",
      "Volume mínimo no sinal (R$)", "Retorno líquido da versão 1", "Diferença v2 − v1 (pontos)", "Operações na versão 1"]
cab(wv, 1, TV, [20, 9, 11, 20, 22, 14, 12, 11, 9, 13, 24, 16, 16, 16, 14])
wv.row_dimensions[1].height = 48
for i, v in enumerate(VAR, 2):
    vals = [v["nome"], v["X"], v["ordem"], v["p_fim"], v["p_liq"], v["ret_liq"], v["queda"], v["n"], v["giro"], v["sem_din"],
            f"{v['nome'].replace('Conservadora', 'Cons.').replace('Agressiva', 'Agr.')} R$ {int(v['ordem'])}", v["vmin"], v["ret_liq_v1"],
            100 * (v["ret_liq"] - v["ret_liq_v1"]), v["n_v1"]]
    fm = [None, '0%', F_BRL0, F_BRL, F_BRL, F_PCT, F_PCT, '0', '0.00', '0', None, F_BRL0, F_PCT, '0.0', '0']
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
wv.cell(row=rv, column=13, value=float(CDI10[-1] / CAP_SUB - 1)).number_format = F_PCT
wv.cell(row=rv, column=7, value=0.0).number_format = F_PCT
wv.cell(row=rv + 2, column=1, value=("Cada linha parte de R$ 10.000. 'Giro' = total comprado ÷ patrimônio médio. As ordens de R$ 500 e R$ 2.000 são "
                                    "testes de sensibilidade; a carteira principal usa R$ 1.000. Versão 2: a Conservadora e a Conservadora 30% só compram fundos com "
                                    "volume médio de 60 dias de R$ 500 mil ou mais no dia do sinal; as três linhas bloqueiam fundos com fato de saída da bolsa."))
ch = BarChart()
ch.type = "col"
ch.title = "Retorno líquido por variante (R$ 10 mil em cada): versão 2 e versão 1"
ch.height, ch.width = 9.5, 24
ch.add_data(Reference(wv, min_col=6, min_row=1, max_row=rv), titles_from_data=True)
ch.add_data(Reference(wv, min_col=13, min_row=1, max_row=rv), titles_from_data=True)
ch.set_categories(Reference(wv, min_col=11, min_row=2, max_row=rv))
eixos(ch, "Variante", "Retorno líquido no período (%)", '0%')
for s_, cor_ in zip(ch.series, [COR["tot"], "B26BD6"]):
    s_.graphicalProperties.solidFill = cor_
    s_.invertIfNegative = False
ch.gapWidth = 50
wv.add_chart(ch, f"A{rv + 5}")

# ------------------------------------------------ Posicoes abertas
wpo = wb.create_sheet("Posições abertas")
wpo["A1"] = f"Posições abertas em {dt(TS[-1])} (ordem de R$ 1.000), uma linha por operação"
wpo["A1"].font = Font(bold=True, size=13)
wpo["A2"] = ("Resultado = valorização (valor atual − valor de entrada) + rendimentos JÁ PAGOS (data de pagamento até 09/11/2026) − taxa de compra. "
             "Os rendimentos declarados e ainda a receber aparecem na coluna ao lado e NÃO entram no resultado desta aba. Antes do imposto do FII.")
wpo["A2"].alignment = Alignment(wrap_text=True, vertical="top")
wpo.merge_cells("A2:P2")
wpo.row_dimensions[2].height = 34
TP = ["Sub-carteira", "Fundo", "Data de entrada", "Preço de entrada (R$)", "Cotas", "Valor de entrada (R$)", "Último preço (R$)", "Data do último preço",
      "Valor atual (R$)", "Rendimentos já pagos (R$)", "Rendimentos a receber, declarados (R$)", "Resultado (R$)", "Resultado (%)", "Positivo / negativo",
      "Rótulo do gráfico", "Conservadora", "Agressiva"]
cab(wpo, 4, TP, [14, 10, 13, 12, 8, 14, 12, 13, 14, 14, 17, 14, 11, 12, 16, 14, 14])
wpo.row_dimensions[4].height = 62
fm_p = [None, None, F_DATA, '#,##0.00', '0', F_BRL, '#,##0.00', F_DATA, F_BRL, F_BRL, F_BRL, F_BRL, F_PCT, None, None, F_PCT, F_PCT]
VERM, VERD_ = PatternFill("solid", fgColor="FDE2E2"), PatternFill("solid", fgColor="E3F4E8")
for i, r in enumerate(POS.itertuples(), 5):
    vals = [r.carteira, r.fundo, r.entrada.to_pydatetime(), float(r.preco_entrada), int(r.cotas), float(r.valor_entrada), float(r.ult_preco),
            r.data_ult.to_pydatetime(), float(r.valor_atual), float(r.rend_pago), float(r.rend_receber), float(r.resultado), float(r.resultado_pct),
            r.sinal, r.rotulo, float(r.resultado_pct) if r.carteira == "Conservadora" else None,
            float(r.resultado_pct) if r.carteira == "Agressiva" else None]
    for j, (v, f) in enumerate(zip(vals, fm_p), 1):
        c = wpo.cell(row=i, column=j, value=v)
        if f:
            c.number_format = f
        if j == 14:
            c.fill = VERD_ if v == "positivo" else VERM
npo = len(POS) + 4
i0 = npo + 2
wpo.cell(row=i0, column=1, value="Totais por sub-carteira").font = Font(bold=True, size=12)
cab(wpo, i0 + 1, ["TOTAL da sub-carteira", "Posições", "", "", "", "Valor de entrada (R$)", "", "", "Valor atual (R$)", "Rendimentos já pagos (R$)",
                  "Rendimentos a receber (R$)", "Resultado (R$)", "Resultado (%)", "Positivas / negativas"])
wpo.row_dimensions[i0 + 1].height = 45
for i, nome_ in enumerate(("Conservadora", "Agressiva"), i0 + 2):
    t_ = TOT_POS[nome_]
    for j, (v, f) in enumerate(zip([nome_, t_["n"], None, None, None, t_["valor_entrada"], None, None, t_["valor_atual"], t_["rend_pago"],
                                    t_["rend_receber"], t_["resultado"], t_["resultado_pct"], f"{t_['n_pos']} positivas / {t_['n_neg']} negativas"],
                                   [None, '0', None, None, None, F_BRL, None, None, F_BRL, F_BRL, F_BRL, F_BRL, F_PCT, None]), 1):
        c = wpo.cell(row=i, column=j, value=v)
        c.font = Font(bold=True)
        if f:
            c.number_format = f
wpo.cell(row=i0 + 5, column=1, value=("Fundos cujo último preço é anterior a 09/11/2026 não negociaram nos dias seguintes; o valor atual usa esse último fechamento "
                                      "(veja a coluna 'Data do último preço')."))
wpo.freeze_panes = "C5"
ch = BarChart()
ch.type = "col"
ch.grouping = "clustered"
ch.overlap = 100
ch.title = "Resultado (%) de cada posição aberta em 09/11/2026"
ch.height, ch.width = 11, 28
for col in (16, 17):
    ch.add_data(Reference(wpo, min_col=col, min_row=4, max_row=npo), titles_from_data=True)
ch.set_categories(Reference(wpo, min_col=15, min_row=5, max_row=npo))
eixos(ch, "Fundo e data de entrada", "Resultado da posição (% do valor de entrada)", '0%')
for s_, cor in zip(ch.series, [COR["cons"], COR["agr"]]):
    s_.graphicalProperties.solidFill = cor
    s_.graphicalProperties.line.solidFill = cor
    s_.invertIfNegative = False
ch.gapWidth = 40
wpo.add_chart(ch, f"A{i0 + 8}")

# ------------------------------------------------ Fundos bloqueados (regra 1)
wb_ = wb.create_sheet("Fundos bloqueados")
wb_["A1"] = "Regra 1: fundos bloqueados no dia do sinal por fato de saída da bolsa (sinais de 2026, todos os gatilhos)"
wb_["A1"].font = Font(bold=True, size=13)
wb_["A2"] = (f"Bloqueia o fundo se, nos {JANELA_FATO} dias corridos até o dia do sinal (inclusive), houve fato relevante do mesmo fundo com expressão de liquidação/dissolução/"
             "encerramento do fundo, incorporação, fusão, cisão ou venda da totalidade dos ativos. Só fatos com data até o dia do sinal. "
             "A coluna 'Leitura' é minha leitura manual do trecho e do que aconteceu depois.")
wb_["A2"].alignment = Alignment(wrap_text=True, vertical="top")
wb_.merge_cells("A2:L2")
wb_.row_dimensions[2].height = 48
TB = ["Fundo", "Data do sinal", "Gatilho(s) do sinal", "Sub-carteira afetada", "Volume médio 60 dias (R$)", "Data do fato que bloqueou", "Id do fato",
      "Expressão que casou", "Trecho do fato", "Fatos na janela", "A versão 1 comprou? (entrada)", "Leitura", "Observação"]
cab(wb_, 4, TB, [10, 12, 11, 26, 15, 13, 10, 24, 90, 9, 34, 36, 70])
wb_.row_dimensions[4].height = 45
for i, r in enumerate(BL26.itertuples(), 5):
    vals = [r.fundo, r.sinal.to_pydatetime(), r.gatilhos, r.sub, float(r.vol), r.dia_fato.to_pydatetime(), int(r.id_fato), r.padrao,
            "…" + r.trecho + "…", int(r.n_fatos), r.v1, r.classe, r.nota]
    fm_b = [None, F_DATA, None, None, '#,##0', F_DATA, '0', None, None, '0', None, None, None]
    for j, (v, f) in enumerate(zip(vals, fm_b), 1):
        c = wb_.cell(row=i, column=j, value=v)
        if f:
            c.number_format = f
        if j in (9, 12, 13, 11, 4):
            c.alignment = Alignment(wrap_text=True, vertical="top")
    wb_.row_dimensions[i].height = 62
nb = len(BL26) + 4
r0_ = nb + 2
wb_.cell(row=r0_, column=1, value="A regra rodada no período todo, 2018 a 2026 (informativo; sinais dos mesmos filtros de universo)").font = Font(bold=True, size=12)
cab(wb_, r0_ + 1, ["Gatilho", "Sinais", "Fundos com sinal", "Sinais bloqueados", "% bloqueado", "Fundos bloqueados",
                   "Bloqueados cujos preços acabam em até 252 pregões", "Não bloqueados cujos preços acabam em até 252 pregões"])
wb_.row_dimensions[r0_ + 1].height = 62
for i, l_ in enumerate(LIN_H, r0_ + 2):
    for j, v in enumerate(l_, 1):
        wb_.cell(row=i, column=j, value=v)
r1_ = r0_ + 2 + len(LIN_H) + 1
wb_.cell(row=r1_, column=1, value="Gatilho 20% por ano").font = Font(bold=True, size=12)
cab(wb_, r1_ + 1, ["Ano", "Sinais", "Sinais bloqueados", "Fundos bloqueados", "Sinais com volume ≥ R$ 500 mil", "... dos quais bloqueados"])
wb_.row_dimensions[r1_ + 1].height = 45
for i, l_ in enumerate(LIN_HA, r1_ + 2):
    for j, v in enumerate(l_, 1):
        wb_.cell(row=i, column=j, value=v)
r2_ = r1_ + 2 + len(LIN_HA) + 1
wb_.cell(row=r2_, column=1, value=f"Leitura de todos os {len(AMOSTRA)} bloqueios de 2018 a 2025 (pares fundo x dia do sinal, todos os gatilhos)").font = Font(bold=True, size=12)
cab(wb_, r2_ + 1, ["Fundo", "Data do sinal", "Gatilho(s)", "", "", "Data do fato", "Id do fato", "Expressão que casou", "Trecho (230 caracteres de cada lado)", "", "", "Leitura", "Observação"])
for i, r in enumerate(AMOSTRA.itertuples(), r2_ + 2):
    cl_, ob_ = AVAL_H[(r.fundo, dt(r.sinal))]
    for j, (v, f) in enumerate(zip([r.fundo, r.sinal.to_pydatetime(), r.gat, None, None, pd.Timestamp(r.fato["dia"]).to_pydatetime(), int(r.fato["id"]), r.fato["padrao"],
                                    "…" + contexto_fato(r.fato) + "…", None, None, cl_, ob_],
                                   [None, F_DATA, None, None, None, F_DATA, '0', None, None, None, None, None, None]), 1):
        c = wb_.cell(row=i, column=j, value=v)
        if f:
            c.number_format = f
        if j in (9, 12, 13):
            c.alignment = Alignment(wrap_text=True, vertical="top")
    wb_.row_dimensions[i].height = 78
wb_.freeze_panes = "C5"

# ------------------------------------------------ Saiu da bolsa
wsb = wb.create_sheet("Saiu da bolsa")
wsb["A1"] = "Fundos comprados que depois saíram da bolsa: valor real desconhecido"
wsb["A1"].font = Font(bold=True, size=13)
wsb["A2"] = ("Os preços desses fundos acabam antes de 09/11/2026 (últimas linhas com 'negociou = 0'). A simulação mantém o cálculo pelo ÚLTIMO PREÇO registrado, mas não há "
             "dado do que realmente foi pago aos cotistas (liquidação, incorporação, suspensão). O valor real é desconhecido: pode ser pior ou melhor.")
wsb["A2"].alignment = Alignment(wrap_text=True, vertical="top")
wsb.merge_cells("A2:K2")
wsb.row_dimensions[2].height = 48
cab(wsb, 4, ["Sub-carteira", "Fundo", "Data de entrada", "Valor da compra (R$)", "Último preço (R$)", "Data do último preço", "Valor pelo último preço (R$)",
             "Resultado simulado (R$)", "Resultado simulado (%)", "Situação"], [14, 10, 13, 15, 13, 14, 16, 15, 13, 48])
wsb.row_dimensions[4].height = 45
for i, r in enumerate(SAIU_DF.itertuples(), 5):
    for j, (v, f) in enumerate(zip([r.carteira, r.fundo, r.entrada.to_pydatetime(), float(r.valor_compra), float(r.preco_saida), r.saida.to_pydatetime(),
                                    float(r.valor_venda), float(r.resultado), float(r.resultado_pct), SAIU],
                                   [None, None, F_DATA, F_BRL, '#,##0.00', F_DATA, F_BRL, F_BRL, F_PCT, None]), 1):
        c = wsb.cell(row=i, column=j, value=v)
        if f:
            c.number_format = f
        c.fill = PatternFill("solid", fgColor="FDE2E2")
if SAIU_DF.empty:
    wsb.cell(row=5, column=1, value="Nenhuma compra da versão 2 foi vendida por 'saiu da bolsa'.")

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
    ("Regras novas da versão 2 (17/11/2026)", ""),
    ("Regra 1: não comprar fundo que vai sair da bolsa", f"Vale para as duas sub-carteiras. No dia do sinal, o fundo é bloqueado se, nos {JANELA_FATO} dias corridos até o dia do sinal (inclusive), houve fato relevante do mesmo fundo (planilhas/tecnico/fatos_textos.csv.gz e planilhas/anuncios.csv) com expressão de liquidação/dissolução/encerramento do fundo, incorporação, fusão, cisão ou venda da totalidade dos ativos. 'Liquidação financeira', 'liquidez' e 'liquidação de CRI' não contam. Só fatos com data até o dia do sinal. Um fato de reprovação/cancelamento ('foi reprovada a dissolução…') anula os anteriores. A lista dos bloqueados de 2026, com o trecho, está na aba 'Fundos bloqueados'."),
    ("Regra 2: Conservadora com volume mínimo", "Gatilho de 20% como antes E só fundos com volume médio de 60 dias de R$ 500.000 ou mais no dia do sinal (só dados até o dia do sinal)."),
    ("Regra 3: Agressiva", "Igual à versão 1 (gatilho de 15%, sem filtro de volume), só com a regra 1."),
    ("Regra 4: variante 30%", "Conservadora com gatilho de 30%, também com volume de 60 dias de R$ 500 mil ou mais."),
    ("Saiu da bolsa — valor real desconhecido", "Se um fundo comprado mesmo assim parar de ter preço antes de 09/11/2026, o cálculo continua pelo último preço, mas a operação é marcada com esse texto (linha vermelha na aba Operações) e listada na aba 'Saiu da bolsa'."),
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
    ("Aba Patrimônio dia a dia", "Valor de cada carteira no fechamento de cada pregão (a última coluna é o total da versão 1, a linha tracejada roxa no primeiro gráfico). O caixa entra já descontado de IR e IOF (como se resgatasse naquele dia). 105% do CDI R$ 20 mil = tudo parado no CDI desde 02/01. Mercado = índice do fundo imobiliário do meio (planilhas/mercado.csv)."),
    ("Aba Quanto estava aplicado", "Valor das cotas dividido pelo patrimônio, dia a dia, em cada sub-carteira."),
    ("Aba Mês a mês", "Retorno de cada mês, do último fechamento do mês anterior ao último fechamento do mês. Janeiro parte de 02/01. Novembro vai até 09/11."),
    ("Colunas da versão 1 no Resumo", "As três últimas colunas da aba Resumo são a versão 1 (regras antigas, rodadas de novo pelo mesmo programa e conferidas com os números do documento antigo). A linha 'Diferença' mostra versão 2 menos versão 1 no retorno líquido, em pontos percentuais."),
    ("Aba Posições abertas", "Uma linha por operação ainda aberta em 09/11/2026, por sub-carteira. Valor de entrada = cotas × preço de entrada (sem a taxa). Valor atual = cotas × último preço (a data do último preço aparece ao lado: fundo que não negociou em 09/11 usa o último fechamento). Rendimentos já pagos = só os de data de pagamento até 09/11/2026. Rendimentos a receber = declarados, com pagamento depois (NÃO entram no resultado desta aba). Resultado = valorização + rendimentos já pagos − taxa de compra; % = resultado ÷ valor de entrada. Antes do imposto do FII."),
    ("Aba Fundos bloqueados", "Fundo, dia do sinal, data e trecho do fato que bloqueou, mais minha leitura manual de cada caso, a regra rodada de 2018 a 2026 (informativo) e a leitura dos bloqueios de 2018 a 2025."),
    ("Aba Operações", "Uma linha por compra. Sinal = dia em que a cota caiu abaixo do gatilho; Entrada = dia seguinte, preço de abertura. Valorização = venda − compra. Rendimentos = o que o fundo pagou por cota enquanto se tinha a cota (inclui os que ainda serão pagos). Resultado = valorização + rendimentos − taxas, antes do imposto do FII (que é cobrado por mês, não por operação). Resultado (%) = resultado ÷ valor da compra. As duas colunas finais servem ao gráfico."),
    ("Motivo da saída", "Volta à média = a cota subiu até a média dos últimos 200 pregões (vende por esse preço, ou pela abertura se for maior). Prazo = 252 pregões sem voltar. Saiu da bolsa — valor real desconhecido = os preços acabaram antes do fim da base; o cálculo usa o último preço (não é uma venda real). Em aberto = ainda comprado em 09/11."),
    ("Aba Variantes", "Mesmas regras da versão 2 com ordem de R$ 500, R$ 1.000 e R$ 2.000 e a conservadora com gatilho 30% (volume mínimo R$ 500 mil). Cada linha parte de R$ 10.000; as colunas da direita comparam com a versão 1."),
    ("Aba Saiu da bolsa", "Compras da versão 2 cujo fundo parou de ter preço antes de 09/11/2026; valor real desconhecido."),
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
    ("Um ano só não prova nada", f"São menos de 10 meses e poucas operações (a conservadora da versão 2 fez {M['Conservadora']['n']} compras com ordem de R$ 1.000, {M['Conservadora']['n_fe']} já fechadas). Uma ou duas operações mudam o resultado inteiro. Não tire conclusão sobre a estratégia a partir desta aba."),
    ("As regras novas foram escolhidas olhando 2026", "Os filtros da versão 2 (volume mínimo e bloqueio por fato) foram decididos depois de ver o resultado da versão 1 em 2026. Isso melhora o número de 2026 por construção; não é um teste fora da amostra."),
    ("A regra 1 é de palavras, não de leitura", f"A regra usa expressões no texto dos fatos e erra nos dois sentidos: bloqueia fundo que é o comprador dos ativos de outro, ou que fez cisão parcial, e pode deixar passar fundo cuja saída foi escrita com outras palavras. Nos bloqueios de 2026 não achei trecho que fugisse do assunto, mas {n_pre + n_ppe} de {len(BL26)} eram propostas que não se concretizaram até 09/11; de 2018 a 2025, dos {len(AMOSTRA)} bloqueios lidos só {N_H[H_OK]} foram saídas confirmadas (veja a aba Fundos bloqueados)."),
    ("Compra na abertura e venda pelo preço da média", "Compra-se no preço de abertura do dia seguinte ao sinal e vende-se pelo preço da média quando a máxima do dia a toca. Em fundo pouco negociado, ninguém garante esse preço. O resultado é otimista nesses casos. O dinheiro de uma venda também é usado já na abertura do mesmo dia."),
    ("Ordem de R$ 1.000 e cotas inteiras", "Com cotas inteiras, a ordem real fica um pouco abaixo do valor pretendido (veja 'Valor da compra' na aba Operações). O limite é 2% do negociado médio de 60 dias e o caixa disponível; abaixo de R$ 200 não compra."),
    ("Fundos que sumiram da base", "Alguns fundos deixam de ter preços no meio do período (parou de negociar, foi incorporado ou liquidado). A simulação mantém o cálculo pelo último preço, marcado 'saiu da bolsa — valor real desconhecido'; ninguém sabe se esse valor seria obtido (lacuna)."),
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

ORDEM_ABAS = ["Resumo", "Posições abertas", "Patrimônio dia a dia", "Quanto estava aplicado", "Mês a mês", "Operações", "Variantes",
              "Fundos bloqueados", "Saiu da bolsa", "Sinais sem dinheiro", "Legenda e avisos"]
assert sorted(ORDEM_ABAS) == sorted(wb.sheetnames), wb.sheetnames
wb._sheets = [wb[n_] for n_ in ORDEM_ABAS]
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
        out.append("| " + " | ".join(str(x).replace("|", "/") for x in l_) + " |")
    return "\n".join(out)


mc, ma, mt, mcdi, mmer = M["Conservadora"], M["Agressiva"], M["Total"], M["CDI"], M["Mercado"]
v1c, v1a, v1t = M_V1["Conservadora"], M_V1["Agressiva"], M_V1["Total"]
i_pico = int(np.argmax(TOTAL_PAT))
pico_tot, d_pico_tot = float(TOTAL_PAT[i_pico]), DATAS[i_pico]
ops_c, ops_a = BASE["Conservadora"]["o"], BASE["Agressiva"]["o"]
res_ab = float(pd.concat([ops_c, ops_a]).query("status != 'Fechada'")["resultado"].sum())
res_fe = float(pd.concat([ops_c, ops_a]).query("status == 'Fechada'")["resultado"].sum())
res_ab_pago = float(POS["resultado"].sum())
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
fundos_saiu = ", ".join(sorted(set(pd.concat([ops_c, ops_a]).query("motivo == @SAIU")["fundo"]))) or "nenhum"
# a versao 1, para o resumo: ordens que saiam da bolsa
_o1 = pd.concat([BASE_V1["Conservadora"]["o"], BASE_V1["Agressiva"]["o"]], ignore_index=True)
_s1 = _o1[_o1["motivo"] == SAIU]
assert len(_s1) == 5 and abs(_s1["valor_compra"].sum() - 4206.64) < 0.006 and abs(_s1["resultado"].sum() - (-783.48)) < 0.006, "versao 1 nao bate com o documento antigo"
cdi_r = mcdi["ret_liq"]


def f_pct1(x):
    return pct(x, 1)


def linha_resumo(k):
    return k


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
    ("Sinais bloqueados pela regra 1 (fundo que pode sair da bolsa)", [str(M[k]["n_bloq"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Sinais barrados pelo volume (< R$ 500 mil)", [str(M[k]["n_vol"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Compras que depois saíram da bolsa", [str(M[k]["n_saiu"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Sinais sem dinheiro", [str(M[k]["sem_din"]) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Giro", [br(M[k]["giro"], 2) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Tempo médio por operação fechada (dias)", [br(M[k]["tempo"], 1) if "n_ab" in M[k] else "—" for k in cols_m]),
    ("Dinheiro aplicado em fundos, em média", [pct(M[k]["aplicado"]) if "n_ab" in M[k] else "—" for k in cols_m]),
]
T_RES = md_tab(["Indicador", "Conservadora (20%, vol. ≥ R$ 500 mil)", "Agressiva (15%)", "Total (R$ 20 mil)", "105% do CDI (R$ 20 mil)", "Mercado (R$ 20 mil)"],
               [[a] + b for a, b in linhas_res])


def _cmp(fn):
    out = []
    for k, m1 in (("Conservadora", v1c), ("Agressiva", v1a), ("Total", v1t)):
        out += [fn(m1), fn(M[k])]
    return out


T_CMP = md_tab(["Indicador", "Conservadora v1", "Conservadora v2", "Agressiva v1", "Agressiva v2", "Total v1", "Total v2"], [
    ["Patrimônio final (cotas a preço de 09/11)"] + _cmp(lambda m: brl(m["p_fim"])),
    ["Retorno no período"] + _cmp(lambda m: pct(m["ret"])),
    ["Patrimônio final líquido do imposto"] + _cmp(lambda m: brl(m["p_liq"])),
    ["Retorno líquido"] + _cmp(lambda m: pct(m["ret_liq"])),
    ["Retorno líquido contra o CDI (pontos)"] + _cmp(lambda m: br(100 * (m["ret_liq"] - cdi_r), 1)),
    ["Maior queda no caminho"] + _cmp(lambda m: pct(m["queda"])),
    ["Operações abertas / fechadas"] + _cmp(lambda m: f"{m['n_ab']} / {m['n_fe']}"),
    ["Rendimentos recebidos"] + _cmp(lambda m: brl(m["rend"])),
    ["Imposto do FII pago"] + _cmp(lambda m: brl(m["imposto"])),
    ["Compras que saíram da bolsa"] + _cmp(lambda m: str(m["n_saiu"])),
    ["Sinais bloqueados (regra 1) / barrados por volume (regra 2)"] + _cmp(lambda m: f"{m['n_bloq']} / {m['n_vol']}"),
    ["Sinais sem dinheiro"] + _cmp(lambda m: str(m["sem_din"])),
])

T_MES = md_tab(["Mês", "Conservadora", "Agressiva", "Total", "105% do CDI", "Mercado"],
               [[f"{NOMES_MES[ym[1] - 1]}/{str(ym[0])[2:]}" + (" (até 09/11)" if ym == (TS[-1].year, TS[-1].month) else "")] +
                [pct(MM[(ym, k)]) for k in ["Conservadora", "Agressiva", "Total", "CDI", "Mercado"]] for ym in meses])

T_VAR = md_tab(["Sub-carteira", "Gatilho", "Volume mínimo", "Ordem", "Patrimônio final (preço de 09/11)", "Patrimônio final líquido", "Retorno líquido",
                "Retorno líquido da versão 1", "Maior queda", "Operações (v2 / v1)", "Giro", "Sinais sem dinheiro"],
               [[v["nome"], f"{int(v['X'] * 100)}%", brl(v["vmin"], 0) if v["vmin"] else "—", brl(v["ordem"], 0), brl(v["p_fim"]), brl(v["p_liq"]), pct(v["ret_liq"]),
                 pct(v["ret_liq_v1"]), pct(v["queda"]), f"{v['n']} / {v['n_v1']}", br(v["giro"], 2), v["sem_din"]] for v in VAR] +
               [["105% do CDI (R$ 10 mil)", "—", "—", "—", brl(CDI10[-1]), brl(CDI10[-1]), pct(CDI10[-1] / CAP_SUB - 1), pct(CDI10[-1] / CAP_SUB - 1), "0,0%", "—", "—", "—"]])

fech_all = pd.concat([ops_c, ops_a]).query("status == 'Fechada'").sort_values(["carteira", "saida"])
T_FEC = md_tab(["Sub-carteira", "Fundo", "Entrada", "Saída (ou último preço)", "Motivo", "Valor da compra", "Rendimentos", "Resultado", "Resultado (%)"],
               [[r.carteira, r.fundo, dt(r.entrada), dt(r.saida), r.motivo, brl(r.valor_compra), brl(r.rend_direito), brl(r.resultado),
                 pct(r.resultado_pct)] for r in fech_all.itertuples()])
ab_all = pd.concat([ops_c, ops_a]).query("status != 'Fechada'")
_pos_cols = ["Fundo", "Entrada", "Preço de entrada", "Cotas", "Valor de entrada", "Último preço", "Data do último preço", "Valor atual", "Rendimentos já pagos",
             "Rendimentos a receber", "Resultado (R$)", "Resultado (%)", "Positivo / negativo"]


def _t_pos(nome_):
    g_ = POS[POS["carteira"] == nome_]
    t_ = TOT_POS[nome_]
    linhas = [[r.fundo, dt(r.entrada), brl(r.preco_entrada), r.cotas, brl(r.valor_entrada), brl(r.ult_preco), dt(r.data_ult), brl(r.valor_atual), brl(r.rend_pago),
               brl(r.rend_receber), brl(r.resultado), pct(r.resultado_pct), r.sinal] for r in g_.itertuples()]
    linhas.append([f"**TOTAL {nome_} ({t_['n']})**", "", "", "", f"**{brl(t_['valor_entrada'])}**", "", "", f"**{brl(t_['valor_atual'])}**", f"**{brl(t_['rend_pago'])}**",
                   f"**{brl(t_['rend_receber'])}**", f"**{brl(t_['resultado'])}**", f"**{pct(t_['resultado_pct'])}**",
                   f"{t_['n_pos']} positivas / {t_['n_neg']} negativas"])
    return md_tab(_pos_cols, linhas)


T_POS_C, T_POS_A = _t_pos("Conservadora"), _t_pos("Agressiva")
T_SAIU = md_tab(["Sub-carteira", "Fundo", "Entrada", "Último preço (R$)", "Data do último preço", "Valor da compra", "Valor pelo último preço", "Resultado simulado", "Situação"],
                [[r.carteira, r.fundo, dt(r.entrada), br(r.preco_saida), dt(r.saida), brl(r.valor_compra), brl(r.valor_venda),
                  f"{brl(r.resultado)} ({pct(r.resultado_pct)})", "saiu da bolsa — valor real desconhecido"] for r in SAIU_DF.itertuples()]) if len(SAIU_DF) else "Nenhuma compra da versão 2 saiu da bolsa."
funil_md = funil.copy()
T_FUN = md_tab(["Sub-carteira (ordem R$ 1.000)"] + list(funil_md.columns) + ["Total de sinais"],
               [[c] + [int(v) for v in r] + [int(r.sum())] for c, r in funil_md.iterrows()])
T_CONF = "\n".join(f"- {t}" for t in CONF_TXT)
T_BL = md_tab(["Fundo", "Sinal", "Gatilho(s)", "Sub-carteira afetada", "Fato que bloqueou (data)", "Expressão", "Trecho do fato", "A v1 comprou?", "Leitura (manual)"],
              [[r.fundo, dt(r.sinal), r.gatilhos, r.sub, f"{dt(r.dia_fato)} (id {r.id_fato}; +{r.n_fatos - 1})", r.padrao, "…" + r.trecho + "…", r.v1, r.classe + ". " + r.nota]
               for r in BL26.itertuples()])
T_BL_RES = md_tab(["Leitura dos bloqueios de 2026", "Quantos", "Quais"], [
    [VERD, n_verd, ", ".join(sorted(set(f"{r.fundo} {dt(r.sinal)[:5]}" for r in BL26.itertuples() if r.classe == VERD)))],
    [PR_AP, n_pap, ", ".join(sorted(set(r.fundo for r in BL26.itertuples() if r.classe == PR_AP)))],
    [PR_RE, n_pre, ", ".join(sorted(set(r.fundo for r in BL26.itertuples() if r.classe == PR_RE)))],
    [PR_PE, n_ppe, ", ".join(sorted(set(r.fundo for r in BL26.itertuples() if r.classe == PR_PE)))],
    ["trecho que não trata de saída do próprio fundo (erro de leitura)", n_err, "nenhum"],
    ["Total de bloqueios (fundo × dia do sinal)", len(BL26), f"{BL26['fundo'].nunique()} fundos"],
])
T_CONF3 = "\n".join(f"- {t}" for t in CONF3)
T_HIST = md_tab(["Gatilho", "Sinais", "Fundos com sinal", "Sinais bloqueados", "% bloqueado", "Fundos bloqueados", "Bloqueados cujos preços acabam em até 252 pregões",
                 "Não bloqueados cujos preços acabam em até 252 pregões"], LIN_H)
T_HIST_ANO = md_tab(["Ano (gatilho 20%)", "Sinais", "Sinais bloqueados", "Fundos bloqueados", "Sinais com volume ≥ R$ 500 mil", "... dos quais bloqueados"], LIN_HA)
T_AMOSTRA = md_tab(["Fundo", "Sinal", "Gatilho(s)", "Fato (data)", "Expressão", "Leitura", "Observação"],
                   [[r.fundo, dt(r.sinal), r.gat, dt(pd.Timestamp(r.fato["dia"])), r.fato["padrao"], AVAL_H[(r.fundo, dt(r.sinal))][0], AVAL_H[(r.fundo, dt(r.sinal))][1]]
                    for r in AMOSTRA.itertuples()])
n_bloq_tot = int(BL26["fundo"].shape[0])

_lac = [
    [f"Fundos cujos preços acabam depois da compra ({fundos_saiu})",
     f"Em {LAC['saiu_n']} ordem(ns) da versão 2 o fundo parou de ter preço antes de 09/11 (as últimas linhas têm 'negociou = 0'). O cálculo mantém o último preço registrado, mas a operação está marcada 'saiu da bolsa — valor real desconhecido'. Não há dado do que realmente aconteceu (liquidação, incorporação, suspensão).",
     f"Comprado nessas ordens: {brl(LAC['saiu_valor'])}; resultado simulado: {brl(LAC['saiu_res'])}. O resultado real pode ser pior ou melhor."],
    ["Regra 1 (fatos de saída da bolsa)", f"Só os primeiros 3.000 caracteres de cada fato estão na base ({len(FATOS)} fatos); uma saída anunciada só mais adiante no texto, ou escrita com outras palavras, passa. Fato que fala de outro fundo (comprador dos ativos, fundo incorporador) também bloqueia por engano.", f"Medido: {N_H[H_FALSO]} falsos e {N_H[H_OUTROS]} de texto sobre outros fundos nos {len(AMOSTRA)} bloqueios de 2018 a 2025; nenhum erro de leitura nos {len(BL26)} de 2026. Saídas que passaram: não medido."],
    ["Amortizações (devolução de capital)", f"{LAC['amz_n']} eventos nas posições de 2026; não são creditadas no caixa se existirem.", f"Hoje: {brl(LAC['amz_valor'])}."],
    ["Rendimentos sem data de pagamento", f"{LAC['rend_sem_data_2026']} avisos de 2026 (todos os fundos) sem data de pagamento; nas posições simuladas, {brl(LAC['rend_sem_data_valor'])}. Não foi estimada data.", "Esse dinheiro não entra no caixa."],
    ["Rendimentos que vão ser pagos depois de 09/11", f"{brl(LAC['rend_a_receber'])} já declarados nas posições (conservadora + agressiva).", "Não entram no patrimônio de 09/11 (entrariam nos dias seguintes) nem no resultado da tabela de posições abertas."],
    ["Compra na abertura e venda pelo preço da média", "Ninguém garante esses preços em fundo pouco negociado; o limite de 2% do negociado médio reduz, mas não elimina, o problema.", "Resultado otimista, não medido."],
    ["Dinheiro da venda usado na mesma abertura", "O motor usa o dinheiro de uma venda do dia para comprar na abertura do mesmo dia.", "Pequeno ganho de tempo a favor da carteira; não medido."],
    ["Preço de 09/11 de fundos sem negociação no dia", f"{LAC['abertas_sem_negocio_hoje']} posições abertas (conservadora + agressiva) não tiveram negociação em 09/11; usa-se o último fechamento (veja a data do último preço na tabela de posições abertas).", "Valor das posições pode estar defasado."],
]
if max(LAC["pend"].values()) > 0.005:
    _lac.append(["DARF vencido sem caixa para pagar", "; ".join(f"{n_}: {brl(v_)} de imposto vencido ficou pendente (caixa todo aplicado), descontado do patrimônio" for n_, v_ in LAC["pend"].items() if v_ > 0.005) + ".", "Já considerado no patrimônio."])
_lac += [
    ["Outros custos", "Só a taxa de 0,03% por compra e por venda. Não há corretagem, custódia nem diferença entre preço de compra e de venda.", "Resultado real um pouco menor."],
    ["Prejuízo de anos anteriores", "A carteira nasce vazia em 02/01/2026; não há prejuízo acumulado de 2025 para abater.", "Nenhum."],
    ["Mercado (índice do fundo do meio)", "Índice sem custos nem imposto, calculado a partir do fechamento de 02/01/2026.", "Comparação apenas de referência."],
    ["Sinais de 20% e de 15% repetem", f"Um fundo que cai 20% abaixo da média antes passou pelos 15%, então os mesmos fundos podem aparecer nas duas sub-carteiras ({len(comuns)} fundos em comum: {', '.join(comuns) or 'nenhum'}); {sobrep} compras são idênticas (mesmo fundo e mesmo dia).", "As duas sub-carteiras não são apostas independentes; a mesma perda conta duas vezes no total."],
]
T_LAC = md_tab(["Dado ou regra", "Situação", "Efeito no resultado"], _lac)
T_V1 = md_tab(["Indicador (versão 1)", "Conservadora (20%)", "Agressiva (15%)", "Total (R$ 20 mil)"], [
    ["Patrimônio final (cotas a preço de 09/11)"] + [brl(m["p_fim"]) for m in (v1c, v1a, v1t)],
    ["Retorno no período"] + [pct(m["ret"]) for m in (v1c, v1a, v1t)],
    ["Patrimônio final líquido do imposto"] + [brl(m["p_liq"]) for m in (v1c, v1a, v1t)],
    ["Retorno líquido"] + [pct(m["ret_liq"]) for m in (v1c, v1a, v1t)],
    ["Retorno líquido contra o CDI (pontos)"] + [br(100 * (m["ret_liq"] - cdi_r), 1) for m in (v1c, v1a, v1t)],
    ["Maior queda no caminho"] + [pct(m["queda"]) for m in (v1c, v1a, v1t)],
    ["Operações abertas / fechadas"] + [f"{m['n_ab']} / {m['n_fe']}" for m in (v1c, v1a, v1t)],
    ["Fechadas com lucro"] + [pct(m["luc_fe"]) for m in (v1c, v1a, v1t)],
    ["Pior operação"] + [f"{pct(m['pior'])} {m['pior_f'].split(' ')[0]}" for m in (v1c, v1a, v1t)],
    ["Melhor operação"] + [f"{pct(m['melhor'])} {m['melhor_f'].split(' ')[0]}" for m in (v1c, v1a, v1t)],
    ["Rendimentos recebidos"] + [brl(m["rend"]) for m in (v1c, v1a, v1t)],
    ["Imposto do FII pago / devido e não pago"] + [f"{brl(m['imposto'])} / {brl(m['imp_devido'])}" for m in (v1c, v1a, v1t)],
    ["Sinais sem dinheiro"] + [str(m["sem_din"]) for m in (v1c, v1a, v1t)],
])
T_V1_VAR = md_tab(["Sub-carteira", "Gatilho", "Ordem", "Patrimônio final líquido", "Retorno líquido", "Maior queda", "Operações"],
                  [[n_, f"{int(X_ * 100)}%", brl(o_, 0), brl(m["p_liq"]), pct(m["ret_liq"]), pct(m["queda"]), m["n"]]
                   for n_, (X_, _vm) in SIMS for o_ in ORDENS for m in [metricas([RES_V1[(n_, o_)]], n_)]])
_cons_ret = [v["ret_liq"] for v in VAR]
todas_abaixo = all(v["ret_liq"] < cdi_r for v in VAR)
mono = all(V[(n_, 500.0)]["ret_liq"] > V[(n_, 1000.0)]["ret_liq"] > V[(n_, 2000.0)]["ret_liq"] for n_, _ in SIMS)
V30 = V[("Conservadora 30%", 1000.0)]

DOC_V2 = f"""## Versão 2 (2026-11-17): regras novas decididas pelo dono

### Resultado em uma frase

De {dt(TS[J0])} a {dt(TS[-1])}, a carteira total de R$ 20.000 foi para {brl(mt['p_fim'])} ({pct(mt['ret'])}; {pct(mt['ret_liq'])} descontando o imposto que seria devido ao vender tudo), contra {brl(mcdi['p_fim'])} ({pct(mcdi['ret'])}) de deixar tudo em 105% do CDI e {brl(mmer['p_fim'])} ({pct(mmer['ret'])}) do mercado de fundos. {"Perdeu do CDI nas duas sub-carteiras" if mc['ret_liq'] < cdi_r and ma['ret_liq'] < cdi_r else "Ganhou do CDI em pelo menos uma sub-carteira"}. Na versão 1 (regras antigas) o total tinha ficado em {brl(v1t['p_fim'])} ({pct(v1t['ret'])}; {pct(v1t['ret_liq'])} líquido).

### Regras novas

1. **Não comprar fundo que vai sair da bolsa (as duas sub-carteiras).** No dia do sinal, o fundo é bloqueado se, nos {JANELA_FATO} dias corridos até o dia do sinal (inclusive), houve fato relevante do mesmo fundo (`planilhas/tecnico/fatos_textos.csv.gz`, coluna de texto, e `planilhas/anuncios.csv`; os dois têm os mesmos {len(FATOS)} fatos) tratando de liquidação/dissolução/encerramento do fundo, incorporação, fusão, cisão ou venda da totalidade dos ativos. A busca é por expressões específicas no texto sem acento e em minúsculas, por exemplo: {"; ".join("“" + n_ + "”" for n_, _ in PADROES_SAIDA)}. "Liquidação financeira", "liquidez" e "liquidação de CRI" não casam com nenhuma delas. Só entram fatos com data até o dia do sinal (o programa confere com um assert). Ajustes feitos depois de testar: (a) o fato de XPIN11 de 16/04/2026 diz "alienação dos ativos imobiliários de titularidade do Fundo" e não usa a palavra "totalidade"; sem uma expressão própria para isso a regra deixaria XPIN11 passar, então ela foi acrescentada; (b) "cisão" só conta como "cisão total" ou "cisão do fundo" (a palavra solta casava com "decisão" e "rescisão" e com cisão de outras empresas); "fusão" só como fusão de fundos; (c) trechos com "reprovada", "cancelada", "desistência" por perto não bloqueiam, e um fato de reprovação anula os fatos anteriores (ITIT11: a dissolução proposta em 26/06 foi reprovada em 07/08/2026).
2. **Conservadora:** gatilho de 20% como antes **e** só fundos com volume médio de 60 dias (`volume_medio_60 (R$)`, valor do dia do sinal, só dados até esse dia) de R$ {br(VOL_MIN, 0)} ou mais.
3. **Agressiva:** igual à versão 1 (gatilho de 15%), só com a regra 1.
4. **Variante da conservadora com gatilho de 30%**, também com volume de R$ {br(VOL_MIN, 0)} ou mais.
5. **Fundo comprado que ainda assim sair da bolsa:** não é vendido em silêncio pelo último preço. A operação é marcada "saiu da bolsa — valor real desconhecido", o cálculo continua pelo último preço e ela aparece na tabela à parte "Fundos comprados que saíram da bolsa".

### O que foi simulado

- **Duas sub-carteiras independentes**, cada uma com caixa próprio de R$ 10.000 em {dt(TS[J0])} (primeiro pregão do ano). Começam vazias: só valem sinais com data a partir de 02/01/2026.
- **Conservadora:** compra quando a cota fecha 20% ou mais abaixo da média dos últimos 200 pregões (o "gatilho"), com rendimento do fundo mantido e volume de 60 dias de R$ 500 mil ou mais. **Agressiva:** gatilho de 15%. **Variante extra:** conservadora com gatilho de 30%.
- **Mesmas regras das ordens já estudadas** (`estudos/auditoria_bloco2.py`, cópia verificada de `kairi_ordens.py`): universo de fundos, filtros (patrimônio, negociado, rendimento, preço sobre valor patrimonial), guarda de dados com saltos e buracos, entrada na abertura do pregão seguinte ao sinal, saída quando a máxima do dia toca a média de 200 pregões (vende pelo preço da média, ou pela abertura se for maior) ou no prazo de 252 pregões.
- **Tamanho da ordem:** R$ 1.000 (testes com R$ 500 e R$ 2.000), cotas inteiras, no máximo 2% do negociado médio do fundo em 60 dias e no máximo o caixa disponível. Abaixo de R$ 200 não compra. O mesmo fundo não pode ser comprado de novo enquanto já está na sub-carteira. Se há mais sinais que dinheiro no mesmo dia, compra primeiro o fundo mais negociado.
- **Taxa:** 0,03% na compra e 0,03% na venda.
- **Rendimentos** (isentos) entram no caixa na **data de pagamento** (`rendimentos_pagamentos.csv`). Tem direito quem estava com a cota no fechamento da data de corte do aviso (a "data-base"), a mesma regra de `kairi_ordens.py`. Pagamento em dia sem pregão entra no pregão seguinte.
- **Caixa parado** rende 105% do CDI com liquidez diária (`cdi.csv`), em lotes: cada entrada de dinheiro é um lote; as compras resgatam do lote mais antigo, com IR regressivo (22,5% até 180 dias corridos; 20% de 181 a 360; 17,5% de 361 a 720; 15% acima) e IOF nos primeiros 29 dias, por lote. O caixa que aparece no patrimônio diário já é líquido de IR e IOF.
- **Imposto do FII:** 20% sobre o ganho líquido das vendas de cada mês (prejuízo abate os ganhos seguintes). O DARF sai do caixa no último dia útil do mês seguinte. Posições abertas no fim ficam a preço de 09/11/2026; mostramos também o valor líquido do imposto que seria devido se fossem vendidas.
- **Comparações:** R$ 20.000 todo em 105% do CDI (líquido de IR, como resgatado em 09/11/2026), o índice "mercado" (`mercado.csv`, fundo imobiliário do meio) e a versão 1.

### Tabela 1. Resumo (ordem de R$ 1.000)

{T_RES}

**Legenda.** *Patrimônio* = caixa (líquido de IR e IOF) + cotas ao último preço, em R$. *Retorno* = final ÷ inicial − 1, no período todo (não por ano). *Líquido* = patrimônio final menos o imposto do FII devido (de vendas já feitas e do que seria cobrado se as cotas abertas fossem vendidas em 09/11). *Contra o CDI* = retorno líquido menos o retorno líquido do 105% do CDI, em pontos percentuais. *Maior queda* = maior distância, em %, de um valor alto do patrimônio até o ponto mais baixo seguinte. *Operações abertas* = ainda com cotas em 09/11. *Com lucro* = resultado (valorização + rendimentos declarados − taxas) maior que zero. *Pior/melhor* = em % do valor comprado. *Imposto do FII pago* = DARF efetivamente pago até 09/11. *IR e IOF retidos do caixa* = imposto cobrado nos resgates do dinheiro parado (no 105% do CDI de R$ 20 mil, o IR do fim). *Sinais bloqueados* = sinais descartados pela regra 1. *Barrados pelo volume* = sinais descartados por volume médio de 60 dias abaixo de R$ 500 mil (só na conservadora). *Sinais sem dinheiro* = sinais em que a compra era possível pelo negociado, mas o caixa não tinha R$ 200 livres. *Giro* = total comprado em fundos ÷ patrimônio médio. *Dinheiro aplicado em fundos* = média diária de (valor das cotas ÷ patrimônio).

**Leitura prática.** A carteira ficou {br(-100 * (mt['ret_liq'] - mcdi['ret_liq']), 1)} pontos abaixo do CDI: ganhou {pct(mt['ret_liq'])} contra {pct(mcdi['ret_liq'])}. Até {dt(d_pico_tot)} o total chegou a {brl(pico_tot)}; de {dt(mt['d_pico'])} a {dt(mt['d_fundo'])} caiu {pct(-mt['queda'])}. As {mt['n_ab']} posições ainda abertas somam resultado de {brl(res_ab)} contando os rendimentos já declarados ({brl(res_ab_pago)} contando só os já pagos, como na tabela de posições abertas; as piores: {piores_ab}); as fechadas somam {brl(res_fe)}. Os rendimentos recebidos ({brl(mt['rend'])}) {"não cobriram" if mt['rend'] < -res_ab else "cobriram"} essas perdas.

### Tabela 1b. Versão 2 contra versão 1 (ordem de R$ 1.000)

{T_CMP}

**Legenda.** *v1* = regras antigas (gatilhos de 20% e 15%, sem filtro de volume e sem bloqueio por fato), rodadas de novo pelo mesmo programa; o programa confere que os valores finais batem com os do documento antigo (R$ 10.170,81; R$ 10.426,20; R$ 20.597,01). *v2* = regras novas. Demais colunas como na Tabela 1.

**Leitura prática.** O retorno líquido do total foi de {pct(v1t['ret_liq'])} na versão 1 para {pct(mt['ret_liq'])} na versão 2 ({br(100 * (mt['ret_liq'] - v1t['ret_liq']), 1)} pontos); a conservadora foi de {pct(v1c['ret_liq'])} para {pct(mc['ret_liq'])} e a agressiva de {pct(v1a['ret_liq'])} para {pct(ma['ret_liq'])}. A conservadora passou de {v1c['n']} para {mc['n']} compras (o volume mínimo tirou {mc['n_vol']} sinais e a regra 1 mais {mc['n_bloq']}). As duas continuam abaixo do CDI. Atenção: as regras novas foram decididas depois de ver 2026, então a melhora é, em parte, por construção.

### Tabela 2. Retorno mês a mês

{T_MES}

**Legenda.** Retorno de cada mês = patrimônio do último pregão do mês ÷ patrimônio do último pregão do mês anterior − 1. Janeiro parte do fechamento de 02/01/2026; novembro vai até 09/11. "Total" = as duas sub-carteiras somadas.

**Leitura prática.** O total ganhou do 105% do CDI em {meses_ganha} dos {len(meses)} meses. O pior mês foi {NOMES_MES[ret_tot_mes_pior[1] - 1]}/26 ({pct(MM[(ret_tot_mes_pior, 'Total')])}), junto com a queda do mercado. Os meses em que ficou abaixo do CDI foram: {", ".join(meses_abaixo)}.

### Tabela 3. Variantes (cada linha parte de R$ 10.000)

{T_VAR}

**Legenda.** *Gatilho* = queda abaixo da média de 200 pregões que dispara a compra. *Volume mínimo* = volume médio de 60 dias exigido no dia do sinal. *Ordem* = valor pretendido por compra. *Patrimônio final líquido* = descontado o imposto do FII devido e o que seria devido ao vender as posições abertas. *Retorno líquido* = patrimônio final líquido ÷ R$ 10.000 − 1; a coluna seguinte é o mesmo número na versão 1. *Operações (v2 / v1)* = número de compras nas duas versões. *Giro* = total comprado ÷ patrimônio médio. A última linha é R$ 10.000 em 105% do CDI.

**Leitura prática.** {"Todas as variantes ficaram abaixo do 105% do CDI" if todas_abaixo else "Nem todas as variantes ficaram abaixo do 105% do CDI"} ({pct(CDI10[-1] / CAP_SUB - 1)}). {"Quanto maior a ordem, pior o resultado neste ano" if mono else "A ordem de R$ 500 foi melhor que a de R$ 2.000 na maioria das linhas"}; ordens maiores esgotam o caixa mais cedo (deixam passar sinais) e fazem as perdas pesarem mais. Com apenas esta amostra, isso não é uma regra. A conservadora de 30% fez {V30['n']} compra(s) na versão 2 e {V30['n_v1']} na versão 1: o resto do dinheiro ficou parado no CDI.

### Tabela 4. Operações fechadas (ordem de R$ 1.000)

{T_FEC}

**Legenda.** *Motivo:* volta à média = a cota subiu até a média de 200 pregões; saiu da bolsa — valor real desconhecido = os preços acabaram antes de 09/11 e o cálculo usa o último preço (não é uma venda real). *Rendimentos* = o que o fundo pagou por cota enquanto se tinha a cota (inclui os ainda a receber). *Resultado* = valorização + rendimentos − taxas, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor da compra.

**Leitura prática.** Das {len(fech_all)} operações fechadas, as {len(_vo)} de volta à média tiveram resultado entre {pct(_vo['resultado_pct'].min())} e {pct(_vo['resultado_pct'].max())}; as {len(_sa)} marcada(s) 'saiu da bolsa' ficaram entre {pct(_sa['resultado_pct'].min()) if len(_sa) else 'nd'} e {pct(_sa['resultado_pct'].max()) if len(_sa) else 'nd'}. A conservadora não fechou nenhuma operação: as {mc['n_ab']} compras dela estão abertas.

### Tabela 5. Posições abertas em {dt(TS[-1])} (ordem de R$ 1.000)

**Conservadora**

{T_POS_C}

**Agressiva**

{T_POS_A}

**Legenda.** *Valor de entrada* = cotas × preço de entrada (sem a taxa). *Último preço* e sua data = último fechamento conhecido do fundo (se a data não é 09/11, o fundo não negociou nos dias seguintes). *Valor atual* = cotas × último preço. *Rendimentos já pagos* = só os de data de pagamento até 09/11/2026 (já estão no caixa). *Rendimentos a receber* = declarados, com pagamento depois de 09/11; **não entram** no resultado desta tabela. *Resultado (R$)* = valor atual − valor de entrada + rendimentos já pagos − taxa de compra, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor de entrada. *Positivo / negativo* = sinal do resultado. O gráfico de colunas do resultado (%) de cada posição está na aba "Posições abertas" da planilha.

**Leitura prática.** Na conservadora, {TOT_POS['Conservadora']['n_neg']} das {TOT_POS['Conservadora']['n']} posições abertas estão no prejuízo; na agressiva, {TOT_POS['Agressiva']['n_neg']} das {TOT_POS['Agressiva']['n']}. Juntas, as {len(POS)} posições custaram {brl(POS['valor_entrada'].sum())} e valem {brl(POS['valor_atual'].sum())}; já pagaram {brl(POS['rend_pago'].sum())} de rendimentos, e há {brl(POS['rend_receber'].sum())} a receber. O resultado só vira ganho ou perda de verdade quando as cotas forem vendidas.

### Tabela 6. Fundos comprados que saíram da bolsa — valor real desconhecido

{T_SAIU}

**Legenda.** *Último preço* = último fechamento registrado na base (os preços acabam nessa data). *Valor pelo último preço* = cotas × último preço, sem taxa de venda (a taxa de venda de 0,03% entra no resultado). *Resultado simulado* = valor pelo último preço − compra − taxas + rendimentos. O que o cotista realmente recebeu (liquidação, incorporação, leilão) não está na base.

**Leitura prática.** Só {len(SAIU_DF)} compra(s) da versão 2 virou/viraram fundo que saiu da bolsa (na versão 1 eram {len(_s1)}: {", ".join(sorted(set(_s1["fundo"])))}, com {brl(_s1['valor_compra'].sum())} comprados e {brl(_s1['resultado'].sum())} de resultado simulado). O número real do que sobrou pode ser melhor ou pior que o simulado.

### Tabela 7. Fundos bloqueados pela regra 1 em 2026 (todos os gatilhos)

{T_BL}

**Legenda.** *Sinal* = dia em que a cota cruzou o gatilho. *Gatilho(s)* = gatilhos de 15%, 20% ou 30% que deram sinal no mesmo dia. *Sub-carteira afetada* = onde o sinal seria comprado ("já fora pelo volume" = a conservadora também o descartaria pelo volume de 60 dias abaixo de R$ 500 mil). *Fato que bloqueou* = o mais recente dentro da janela, com data, número (id) do fato e quantos outros fatos também casaram (+N). *Expressão* = qual expressão da busca casou. *Trecho* = texto do fato em volta da expressão. *A v1 comprou?* = a versão 1 comprou esse fundo com sinal nesse dia (e em que sub-carteira, com a data de entrada). *Leitura (manual)* = minha leitura do trecho e dos fatos seguintes: "verdadeiro" = saída aprovada ou concluída; "proposta..." = a saída ainda era uma proposta na data.

{T_BL_RES}

**Legenda.** Contagem das leituras da tabela anterior (fundo × dia do sinal).

**Leitura prática.** Li os {len(BL26)} bloqueios de 2026 (todos). Nenhum trecho fugia do assunto (erro de leitura: {n_err}), mas {n_pre + n_ppe} de {len(BL26)} eram só propostas que não se concretizaram até 09/11 (ITIT11 foi reprovado em 07/08; OUJP11 ainda depende de aprovação). {n_pap} eram propostas depois aprovadas e {n_verd} eram saídas já aprovadas ou concluídas. Bloquear proposta é a leitura mais cautelosa: se a proposta passa, o fundo sai; se não passa, perdeu-se uma compra.

**Confirmação dos três fundos que a versão 1 comprou e saíram da bolsa** (confirmado por execução: o programa tem um assert para cada um):

{T_CONF3}

Nenhum dos três aparece em compra da versão 2.

### Tabela 8. A regra 1 no período todo, 2018 a 2026 (informativo)

{T_HIST}

{T_HIST_ANO}

**Legenda.** *Sinais* = dias de sinal com os mesmos filtros de universo (sem o filtro de volume, sem caixa limitado). *Sinais bloqueados* = os que a regra 1 descartaria. *Fundos bloqueados* = fundos distintos. *Preços acabam em até 252 pregões* = "X de Y": dos sinais cujo desfecho dá para saber (o fundo ainda tinha 252 pregões pela frente ou parou de ter preço), quantos viraram fundo sem preço depois. Esse desfecho só serve para avaliar a regra; ela mesma usa apenas fatos até o dia do sinal.

**Leitura prática.** A regra bloqueia pouco: {LIN_H[0][4]} dos sinais de 15% e {LIN_H[1][4]} dos de 20%. Entre os sinais bloqueados de 15%, {LIN_H[0][6]} acabaram sem preço em até 252 pregões, contra {LIN_H[0][7]} entre os não bloqueados: o bloqueio pega uma parte relevante das saídas, mas não todas.

**Leitura dos {len(AMOSTRA)} bloqueios de 2018 a 2025 (todos, pares fundo × dia do sinal):**

{T_AMOSTRA}

**Legenda.** *Leitura* = minha leitura do trecho (230 caracteres de cada lado, completo na aba "Fundos bloqueados") e do que aconteceu com os preços do fundo.

**Leitura prática.** De {len(AMOSTRA)} bloqueios, só {N_H[H_OK]} eram saídas reais confirmadas; {N_H[H_FALSO]} eram falsos (o fundo continuou negociando: cisão parcial, fundo que seria o comprador de outro, pagamento de saldo) e {N_H[H_OUTROS]} vinham de texto sobre outros fundos, embora o fundo tenha saído depois por outro motivo. Ou seja, a regra de palavras erra bastante nos anos antigos, mas também bloqueia poucos sinais.

### Tabela 9. O que aconteceu com cada sinal (ordem de R$ 1.000)

{T_FUN}

**Legenda.** *Comprado* = ordem executada com o valor pretendido. *Reduzido pelo caixa* = comprou menos que o pretendido, mas pelo menos R$ 200. *Fundo já em carteira* = o mesmo fundo já estava na sub-carteira. *Sem dinheiro* = faltou caixa. *Sem negociação na abertura* = o fundo não negociou no dia da entrada. *Bloqueado: pode sair da bolsa* = regra 1. *Volume abaixo de R$ 500 mil* = regra 2.

**Leitura prática.** A agressiva ficou sem dinheiro em {ma['sem_din']} sinais{', o primeiro em ' + d_sem_din if len(_sd) else ''}. A conservadora recebeu {int(funil.loc['Conservadora'].sum())} sinais: {mc['n_vol']} foram barrados pelo volume, {mc['n_bloq']} pela regra 1 e {mc['n']} viraram compra; não faltou dinheiro para nenhum.

### Conferências feitas pelo programa

Todas passaram (asserts dentro do programa; veja a saída impressa):

- O caixa nunca ficou negativo em nenhum dia, nas {len(RES)} simulações da versão 2 (menor caixa: {brl(min_cx)}).
- Nenhuma compra no dia do sinal ({sum(len(R['ops_raw']) for R in RES.values())} compras, todas depois) e nenhum sinal anterior a 02/01/2026.
- Nenhum fato posterior ao dia do sinal entra na regra 1 (assert dentro de `bloqueio`); todo bloqueio de 2026 tem fato entre 0 e {JANELA_FATO} dias antes do sinal.
- A versão 1 rodada de novo no mesmo programa bate com o documento antigo (R$ 10.170,81; R$ 10.426,20; R$ 20.597,01; variante de 30%: R$ 10.246,71; 5 ordens que saíram da bolsa, R$ 4.206,64 comprados e R$ -783,48 de resultado).
- O valor atual das posições abertas, somado, é igual ao valor das cotas no patrimônio de 09/11 de cada sub-carteira.
- O imposto do FII refeito por fora (mês a mês, com prejuízo abatendo) bate com o do programa; devido = pago + pendente + a vencer.
- R$ 20.000 em 105% do CDI refeitos à mão: {brl(CDI20[-1])} líquido (IR de 20%, {dias_cdi} dias).
{T_CONF}

### O que foi confirmado por execução e o que é interpretação

**Confirmado por execução (rodou e conferiu):** todos os números das tabelas; o caixa nunca negativo; entrada sempre depois do sinal; nenhum fato futuro na regra 1; HCHG11, XPIN11 e ITIP11 bloqueados nas datas em que a versão 1 os comprou; a versão 1 recalculada igual à do documento antigo; compra, rendimento, valor, taxa e resultado de uma operação de cada sub-carteira refeitos a partir dos arquivos de entrada; um resgate do caixa com IR (e outro com IOF + IR) refeitos com `cdi.csv`; imposto do FII refeito por fora; valor das posições abertas igual ao do patrimônio.

**Interpretação (decisão minha, onde o pedido não dizia):**
- "Um fundo por vez" foi lido como: o mesmo fundo não pode ser comprado duas vezes ao mesmo tempo na mesma sub-carteira (como em `kairi_carteira.py`). Cada sub-carteira pode ter vários fundos diferentes.
- Compras na abertura resgatam o caixa com o índice do CDI do pregão anterior (o dia de hoje ainda não rendeu); os dias corridos para IR/IOF contam até a data do resgate. A venda de um fundo vira um lote novo no mesmo dia.
- Direito ao rendimento: data-base entre a entrada e a saída (inclusive a data de saída só quando a saída é no fechamento, no prazo ou posição aberta), como em `kairi_ordens.py`.
- Pagamento em fim de semana ou feriado entra no pregão seguinte. Avisos sem data de pagamento não entram (nada foi estimado).
- Para o retorno e a comparação, usei o patrimônio líquido do imposto do FII que seria devido ao vender tudo (o CDI também está líquido). O patrimônio diário não desconta imposto ainda não vencido.
- Resultado de cada operação (Tabelas 1 e 4) = valorização + rendimentos declarados (inclusive os ainda a receber) − taxas, antes do imposto. Na Tabela 5 (posições abertas), por pedido, só contam os rendimentos já pagos.
- Regra 1: "dia do fato" é a data de divulgação (`data_anuncio`); um fato divulgado no próprio dia do sinal, mesmo à noite, conta (a entrada é na abertura do dia seguinte). A janela é de 365 dias corridos para trás, inclusive o dia do sinal. A regra olha o texto dos fatos do próprio fundo (coluna `fundo`), não os que citam o fundo.
- Regra 1: um fato de reprovação ou cancelamento anula os fatos de saída anteriores a ele (ajuste meu, feito ao ler o caso de ITIT11); sem isso, ITIT11 continuaria bloqueado em outubro e novembro mesmo depois de a saída ter sido reprovada.
- Regra 2: o volume é o `volume_medio_60 (R$)` da linha do dia do sinal (média até aquele dia, sem olhar o futuro). O mesmo número já limitava a ordem a 2% do volume.
- A leitura manual dos bloqueios (verdadeiro / proposta / falso) é minha, feita depois de ver o texto e os fatos posteriores; não é dado da base.

### Lacunas

{T_LAC}

### Avisos

- **2026 não é um teste novo.** O período de conferência (2023 a 2026) já foi visto em estudos anteriores; esta simulação usa dados que já entraram nas escolhas.
- **As regras novas foram escolhidas depois de ver 2026.** O volume mínimo e o bloqueio por fato melhoram o número de 2026 por construção; não é um teste fora da amostra.
- **Um ano só não prova nada.** São {NM - J0} pregões e {mt['n']} compras no total; a conservadora fez {mc['n']} e nenhuma fechou. Dois ou três fundos explicam quase toda a diferença para o CDI.
- **Compras na abertura e vendas pelo preço da média são otimistas** em fundo pouco negociado.
- **A regra 1 é uma busca por palavras**: pode bloquear fundo que não sai (cisão parcial, fundo comprador) e deixar passar saída escrita de outro jeito. Medimos isso acima, mas só com leitura manual.
"""

DOC_V1 = f"""## Versão 1 (regras antigas)

Resumo da simulação anterior, feita sem as regras novas e rodada de novo no mesmo programa (os números abaixo são os do documento antigo, conferidos por assert). Regras: conservadora com gatilho de 20% e agressiva de 15%, sem filtro de volume e sem bloqueio por fato relevante; variante de 30%; ordem de R$ 1.000 (testes com R$ 500 e R$ 2.000). Demais regras (caixa em 105% do CDI, imposto, taxas, prioridade por volume) iguais às da versão 2.

De 02/01/2026 a 09/11/2026, o total foi para {brl(v1t['p_fim'])} ({pct(v1t['ret'])}; {pct(v1t['ret_liq'])} líquido), contra {brl(mcdi['p_fim'])} ({pct(mcdi['ret'])}) do 105% do CDI. Perdeu do CDI nas duas sub-carteiras. A versão 1 comprou {len(_s1)} vezes fundos que saíram da bolsa antes de 09/11 ({", ".join(sorted(set(_s1["fundo"])))}; {brl(_s1['valor_compra'].sum())} comprados, resultado simulado de {brl(_s1['resultado'].sum())}), o que motivou a regra 1.

{T_V1}

**Legenda.** Mesmas definições da Tabela 1 da versão 2. Todos os valores são da ordem de R$ 1.000.

{T_V1_VAR}

**Legenda.** Variantes da versão 1: cada linha parte de R$ 10.000; *retorno líquido* = patrimônio final líquido do imposto ÷ R$ 10.000 − 1.

**Leitura prática.** Na versão 1 todas as variantes ficaram abaixo do 105% do CDI (10,0%), e quanto maior a ordem, pior o resultado. As perdas de fundos que saíram da bolsa, principalmente MCEM11, pesaram nas duas sub-carteiras.

"""

DOC = f"""# Simulação do Kairi em 2026: carteira de R$ 20.000

Programa: `estudos/kairi_carteira_2026.py` (rodada do zero em poucos segundos; comando: `cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/kairi_carteira_2026.py`). Planilha com gráficos: `planilhas/kairi_carteira_2026.xlsx` (abas Resumo, Posições abertas, Patrimônio dia a dia, Quanto estava aplicado, Mês a mês, Operações, Variantes, Fundos bloqueados, Saiu da bolsa, Sinais sem dinheiro, Legenda e avisos).
Gerado automaticamente; os números abaixo vêm da rodada do programa. Este documento tem a **Versão 2** (2026-11-17, regras novas), a **Versão 1** (regras antigas, resumida) e a conferência da queda geral de 26/10/2026.

{DOC_V2}
{DOC_V1}
"""
QUEDA_GERAL = """## Queda geral de 26/10/2026 (conferência feita depois da simulação)

Nas planilhas de preços, 153 dos 221 fundos que negociaram em 26/10/2026 caíram mais de 3% no dia. Só 1 subiu mais de 3%, e a variação do fundo do meio foi −5,0%. A queda continuou até 03/11/2026 (o fundo do meio caiu −2,4% nesse dia). Exemplos: HGLG11 foi de R$ 159,66 a R$ 144,62 e MXRF11 de R$ 9,44 a R$ 8,47.

| Data | Fundos que negociaram | Variação do fundo do meio | Caíram mais de 3% | Subiram mais de 3% |
|---|---|---|---|---|
| 23/10/2026 | 218 | +0,1% | 7 | 12 |
| 26/10/2026 | 221 | −5,0% | 153 | 1 |
| 28/10/2026 | 228 | −1,4% | 42 | 7 |
| 03/11/2026 | 220 | −2,4% | 92 | 10 |

Leitura prática: até 22/10/2026 a carteira total estava em R$ 22.771 (+13,9%), à frente do CDI. A queda geral do fim de outubro levou o resultado para baixo do CDI. **Não conferi essa queda em outra fonte.** Se for erro de dado, o resultado muda.
"""
DOC += QUEDA_GERAL.rstrip("\n") + f"""

Nota da versão 2: o valor de R$ 22.771 (+13,9%) acima é o pico da carteira total da versão 1. Na versão 2 o pico do total foi {brl(pico_tot)} em {dt(d_pico_tot)} e a queda de {dt(mt['d_pico'])} a {dt(mt['d_fundo'])} foi de {pct(mt['queda'])}.
"""
Path(RAIZ / "docs" / "SIMULACAO_KAIRI_2026.md").write_text(DOC, encoding="utf-8")
print(f"Texto salvo em {RAIZ / 'docs' / 'SIMULACAO_KAIRI_2026.md'}")
print(f"\nTempo total: {time.time() - T0:.1f} s")
