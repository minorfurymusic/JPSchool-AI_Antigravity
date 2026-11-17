"""Kairi versao 3 nos anos anteriores (2018 a 2026), SEM baixar nada: so planilhas/ (precos, mercado, cdi, rendimentos, fatos_textos.csv.gz,
anuncios.csv e planilhas/tecnico/fnet_2026_documentos.csv.gz).

Mesmo motor de estudos/kairi_carteira_2026.py (versao 3), parametrizado por data de inicio e de fim. Quatro sub-carteiras de R$ 10.000, ordem de R$ 1.000:
    Agressiva 1: 15%, mediana de 60 pregoes do volume diario em [R$ 100 mil, R$ 200 mil)   Agressiva 2: 15%, [R$ 200 mil, R$ 500 mil)
    Conservadora 1: 20%, [R$ 500 mil, R$ 1 milhao)                                          Conservadora 2: 20%, R$ 1 milhao ou mais
Venda no fechamento do primeiro dia com fechamento >= media de 200 pregoes (media ate o dia anterior) ou prazo de 252 pregoes; rendimento mantido;
regra 1 (bloqueio por fatos relevantes e documentos do FNET), regra b (rendimento zero) e c (saida antecipada) COM OS DOCUMENTOS DO FNET SO QUANDO A DATA PERMITE
(a coleta so tem 01/05/2025 em diante e so 43 fundos; antes disso valem so os fatos relevantes); caixa em 105% do CDI com IR/IOF por lote; imposto do FII; taxa 0,03%.
A diferenca para a versao 3: as classificacoes dos documentos vem prontas do CSV (nao ha acesso a internet), e a simulacao aceita qualquer janela [inicio, fim].

Rodadas: 1) um ano por vez (2018 a 2025, e 2026 = versao 3), cada ano comeca com R$ 10 mil por sub-carteira no 1o pregao do ano e termina no ultimo pregao do ano
(posicoes abertas avaliadas pelo ultimo preco); 2) continua de 02/01/2018 a 09/11/2026.

Rodar com:
    cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/kairi_carteira_anos.py
Saidas: planilhas/kairi_carteira_anos.xlsx e docs/SIMULACAO_KAIRI_ANOS.md.
"""
import os
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
SAIDA_XLSX = PL / "kairi_carteira_anos.xlsx"

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
ORDEM = 1000.0
VOLTA, PRAZO_M, SAIU, GUARDA, ABERTO = "volta à média", "prazo", "saiu da bolsa — valor real desconhecido", "dado suspeito", "em aberto"
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]
JANELA_FATO = 365       # regra 1: dias corridos de fatos olhados para tras (inclusive o dia do sinal)
JAN_VOL = 60            # filtro de negociacao: mediana do volume diario dos 60 pregoes ate o dia do sinal (inclusive)
INF = float("inf")
# sub-carteiras: nome -> (gatilho, mediana minima inclusive, mediana maxima exclusiva); faixas [100k,200k), [200k,500k), [500k,1M), [1M, inf)
SUBS = {"Agressiva 1": (0.15, 100e3, 200e3), "Agressiva 2": (0.15, 200e3, 500e3),
        "Conservadora 1": (0.20, 500e3, 1e6), "Conservadora 2": (0.20, 1e6, INF)}
GATILHOS = [0.15, 0.20]
FNET_INI, FNET_FIM = pd.Timestamp("2025-05-01"), pd.Timestamp("2026-11-13")
CACHE_FNET = PL / "tecnico" / "fnet_2026_documentos.csv.gz"


# ---------------------------------------------------------------- formatacao
def isnan(x):
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


def br(x, d=2):
    if isnan(x):
        return "nd"
    if abs(x) < 0.5 * 10 ** (-d):
        x = 0.0                                   # evita "-0,00"
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
J0_2026 = int(np.searchsorted(MD, np.datetime64(INICIO_SIM, "D")))
assert TS[J0_2026] == INICIO_SIM, "02/01/2026 deveria ser pregao"
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
    VMED = pd.Series(g["volume_dia (R$)"].to_numpy(float)).rolling(JAN_VOL, min_periods=JAN_VOL).median().to_numpy()
    Cs = pd.Series(C)
    mN = Cs.rolling(N, min_periods=N).mean().to_numpy()
    mP = np.r_[np.nan, mN[:-1]]
    k200 = C / mP - 1
    sim = np.zeros(n, bool)
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= K_REND * R[:-LAG_REND]
    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome
    FD[nome] = dict(nome=nome, VMED=VMED, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, VOL=VOL, NEG=NEG,
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
# ================================================================ NOVOS PADROES (versao 3): tombamento / balcao / deslistagem
# Entram na regra 1 (fatos relevantes antigos e documentos do FNET) e na saida antecipada.
PADROES_SAIDA += [
    ("tombamento das cotas", r"\btombamento\W+(?:\w+\W+){0,3}?(?:totalidade\W+)?(?:das?\W+|do\W+)?(?:cotas|fundo)\b|\btombar\W+(?:\w+\W+){0,3}?cotas"),
    ("migração para o balcão", _P(r"(?:migracao|transferencia|tombamento|saida|retirada|mudanca)\w*\W+(?:\w+\W+){0,35}?para\W+(?:o\W+)?(?:mercado|segmento)\W+(?:\w+\W+){0,2}?balcao")),
    ("deslistagem das cotas", _P(r"\bdeslistag|cancelamento d[ao] (?:listagem|negociacao)\W+(?:\w+\W+){0,6}?(?:cotas|b3|bolsa)|cancelamento do registro de negociacao|(?:saida|retirada) d[ao]s? cotas d[ao]s? (?:b3|bolsa)|descredenciamento d[ao]s? cotas")),
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


# ================================================================ DOCUMENTOS DO FNET (so o CSV ja existente; nada e baixado)
# O CSV guarda, por documento, a classificacao feita na versao 3 sobre o texto completo (classe, padrao, trecho, sem_rend_*). Cancelados (situacao 'C')
# e PDFs sem texto ja saem sem classe. Documentos ficam nas datas de entrega de 01/05/2025 a 13/11/2026 e so de 43 fundos.
DOCS = pd.read_csv(CACHE_FNET, sep=";", encoding="utf-8-sig", compression="gzip")
DOCS["dia"] = pd.to_datetime(DOCS["data de entrega"].str[:10], format="%d/%m/%Y")
for _c in ["classe", "padrao", "trecho", "sem_rend_padrao", "sem_rend_trecho"]:
    DOCS[_c] = DOCS[_c].fillna("")
assert DOCS["dia"].between(FNET_INI, FNET_FIM).all(), "documento fora do periodo da coleta"
assert DOCS["id"].is_unique
FNET_FUNDOS = set(DOCS["fundo"])
print(f"FNET (so o CSV existente): {len(DOCS)} documentos de {len(FNET_FUNDOS)} fundos, entregues de {DOCS['dia'].min().date()} a {DOCS['dia'].max().date()}; "
      f"classes: {DOCS['classe'].replace('', 'nenhuma').value_counts().to_dict()}; com rendimento zero: {int((DOCS['sem_rend_padrao'] != '').sum())}")
EXD, CORTE = {}, {}
for r_ in DOCS.sort_values(["fundo", "dia", "id"]).itertuples():
    if r_.classe == "saída":
        EXD.setdefault(r_.fundo, []).append(dict(id=int(r_.id), dia=np.datetime64(r_.dia, "D"), tipo="saída da bolsa/liquidação etc.", padrao=r_.padrao,
                                                 trecho=r_.trecho, doc=f"{r_.categoria} / {r_.especie}"))
    if r_.sem_rend_padrao:
        EXD.setdefault(r_.fundo, []).append(dict(id=int(r_.id), dia=np.datetime64(r_.dia, "D"), tipo="rendimento zero", padrao=r_.sem_rend_padrao,
                                                 trecho=r_.sem_rend_trecho, doc=f"{r_.categoria} / {r_.especie}"))
        CORTE.setdefault(r_.fundo, []).append(EXD[r_.fundo][-1])
for _v in EXD.values():
    _v.sort(key=lambda x: (x["dia"], x["id"]))
for r_ in DOCS.itertuples():
    if r_.classe in ("saída", "reprovação"):
        _hits.append(dict(id=int(r_.id), fundo=r_.fundo, dia=np.datetime64(r_.dia, "D"), padrao=r_.padrao, trecho=r_.trecho,
                          tipo=f"FNET {r_.categoria}", cancela=(r_.classe == "reprovação")))
FS = {}
for _f, _g in pd.DataFrame(_hits).groupby("fundo"):
    _g = _g.sort_values(["dia", "id"])
    FS[_f] = (_g["dia"].to_numpy("datetime64[D]"), _g.to_dict("records"))


def corte_rendimento(fundo, dia_sinal, dia_ini):
    """Documentos de rendimento zero com data de entrega em [dia_ini, dia_sinal] (so documentos ate o dia do sinal)."""
    d1, d0 = np.datetime64(dia_sinal, "D"), np.datetime64(dia_ini, "D")
    lst = [x for x in CORTE.get(fundo, []) if d0 <= x["dia"] <= d1]
    assert all(x["dia"] <= d1 for x in lst), "documento do futuro entrou na regra de rendimento"
    return lst


# ================================================================ JANELAS: um ano por vez e a continua
def primeiro_pregao(ano):
    return int(np.searchsorted(MD, np.datetime64(f"{ano}-01-01", "D")))


def ultimo_pregao(ano):
    return int(np.searchsorted(MD, np.datetime64(f"{ano + 1}-01-01", "D"))) - 1 if ano < TS[-1].year else NM - 1


ANOS = list(range(2018, 2027))
JANELA = {a: (primeiro_pregao(a), ultimo_pregao(a)) for a in ANOS}
JA = JANELA[2018][0]
assert TS[JA] == pd.Timestamp("2018-01-02") and TS[JANELA[2026][0]] == INICIO_SIM and JANELA[2026][1] == NM - 1
assert J0_2026 == JANELA[2026][0]
for a_ in ANOS[:-1]:
    assert TS[JANELA[a_][1]].year == a_ and TS[JANELA[a_][1] + 1].year == a_ + 1


# ================================================================ CANDIDATOS (sinais desde 02/01/2018, qualquer faixa) E SAIDA
ASSERT_USO = []        # (o que, fundo, data do documento, data em que foi usado)
CAND = {}
for X in GATILHOS:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if md >= JA and md + 1 < NM:
                bl = bloqueio(F["nome"], MD[md])
                d_ini = F["dates"][s - LAG_REND]                                  # inicio dos 126 pregoes do fundo ate o sinal
                cut = corte_rendimento(F["nome"], MD[md], d_ini)
                for b_ in bl:
                    ASSERT_USO.append(("bloqueio", F["nome"], b_["dia"], MD[md], b_["tipo"]))
                for c_ in cut:
                    ASSERT_USO.append(("rendimento zero", F["nome"], c_["dia"], MD[md], "FNET"))
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VMED"][s]), vol_media=float(F["VOL"][s]), bloq=bl, cut=cut, d_ini=d_ini))
    CAND[X] = lst
print(f"sinais desde 02/01/2018 (antes do filtro de volume): " + ", ".join(f"{int(X * 100)}%: {sum(len(x) for x in CAND[X])}" for X in GATILHOS))


def regra_fim(F, e):
    last = F["n"] - 1
    if e + PRAZO <= last:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO])
    if F["aberto"]:
        return last, ABERTO, float(F["C"][last])
    return last, SAIU, float(F["C"][last])
def saida_volta(F, e):
    """Versao 3: vende no FECHAMENTO do primeiro dia em que o fechamento fica >= media de 200 pregoes (media ate o dia anterior).
    Dado suspeito (guarda) antes disso: sai no fechamento do dia anterior ao dado suspeito. Prazo de 252 pregoes mantido."""
    last = F["n"] - 1
    jan = min(e + PRAZO, last)
    kg = kv = None
    if jan > e:
        w = np.flatnonzero(F["bad"][e + 1:jan + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        h = np.flatnonzero(F["C"][e + 1:jan + 1] >= F["mN"][e:jan])
        if h.size:
            kv = e + 1 + int(h[0])
    if kg is not None and (kv is None or kg <= kv):
        k = kg - 1
        return k, GUARDA, float(F["C"][k])
    if kv is not None:
        return kv, VOLTA, float(F["C"][kv])
    return regra_fim(F, e)




def saida_antecipada(F, nm, sinal_dia, mi_entrada, k_nat, jend):
    """Documento do FNET publicado DEPOIS do dia do sinal que manda vender na abertura do pregao seguinte: liquidacao/dissolucao/encerramento,
    incorporacao, fusao, cisao, venda da totalidade dos ativos, tombamento/balcao/deslistagem, ou comunicado de que nao havera distribuicao de
    rendimentos. Vale o primeiro que cair antes da saida normal. Venda depois do fim da janela (jend) nao conta (a posicao fica aberta)."""
    alerta = None
    for d in EXD.get(nm, []):
        if d["dia"] <= np.datetime64(sinal_dia, "D"):
            continue
        mt = max(int(np.searchsorted(MD, d["dia"], "right")), mi_entrada + 1)     # 1o pregao depois da publicacao (e depois da compra)
        if mt > jend:
            alerta = dict(d, motivo="publicado perto do fim da janela: a venda seria depois dela (posição segue aberta)")
            continue
        rt = int(np.searchsorted(F["dates"], MD[mt], "left"))
        while rt < F["n"] and not (F["NEG"][rt] == 1 and np.isfinite(F["A"][rt]) and F["A"][rt] > 0):
            rt += 1
        if rt >= F["n"]:
            alerta = dict(d, motivo="o fundo não tem mais preço depois da publicação (não dá para vender)")
            continue
        if int(F["mi"][rt]) > jend:
            alerta = dict(d, motivo="o fundo só volta a negociar depois do fim da janela")
            continue
        if F["dates"][rt] <= F["dates"][k_nat]:
            assert d["dia"] < F["dates"][rt], "documento nao e anterior a venda"
            ASSERT_USO.append(("saida antecipada", nm, d["dia"], F["dates"][rt], "FNET"))
            return rt, d
        return None, alerta
    return None, alerta


def truncar(F, k, mot, pxs, jend):
    """A saida natural (calculada com a historia inteira do fundo) so vale se cair ate o fim da janela; senao a posicao fica aberta, a preco do ultimo
    fechamento ate o fim da janela. Nada depois do fim da janela entra no resultado."""
    if int(F["mi"][k]) > jend:
        rr = int(np.searchsorted(F["dates"], MD[jend], "right") - 1)
        return rr, ABERTO, float(F["C"][rr])
    return k, mot, pxs


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
                                 principal=l[1] * f, bruto=bruto * f, iof=iofv * f, ir=irv * f, liquido=net * f, dias=dias))
            self.iof += iofv * f
            self.ir += irv * f
            rem -= net * f
            l[1] *= (1 - f)
            if l[1] < 1e-9:
                self.lots.remove(l)
        assert rem < 1e-6, ("caixa insuficiente", rem)

    def rendimento_liquido(self, ref_mi, data):
        """Rendimento liquido (de IR e IOF) de todo o dinheiro parado: o que ja foi resgatado + o que esta nos lotes agora."""
        ja = sum(x["liquido"] - x["principal"] for x in self.log)
        agora = sum(lote_liq(l[0], l[1], ref_mi, data)[0] - l[1] for l in self.lots)
        return ja + agora


def serie_cdi(V, mi0, jend):
    return np.array([lote_liq(mi0, V, mi, MD[mi])[0] for mi in range(mi0, jend + 1)])


def imposto_mes(ganho_mes, pool):
    if ganho_mes >= 0:
        usa = min(pool, ganho_mes)
        base = ganho_mes - usa
        return IR_OP * base, pool - usa
    return 0.0, pool - ganho_mes


def simular(nome, X, lo, hi, j0, jend, ordem=ORDEM):
    """Sub-carteira de R$ 10.000: gatilho X, mediana de 60 pregoes do volume diario em [lo, hi), do pregao j0 ao pregao jend (indices de MD)."""
    cands = CAND[X]
    cx = Caixa()
    pos, ops, sched = {}, [], {}
    ganhos, devidos, due, futuro = {}, [], {}, []
    pool = 0.0
    pend = 0.0
    darf_pagos, diario, sinais_log, rend_log, alertas = [], [], [], [], []

    def vender(mi, t, quando):
        for nm in sorted(p for p, P in pos.items() if P["mi_s"] == mi and P["quando"] == quando):
            P = pos.pop(nm)
            op = P["op"]
            vv = P["cotas"] * P["px_s"]
            tv = B3 * vv
            cx.add(mi, vv - tv)
            ganho = (vv - tv) - (op["valor_compra"] + op["taxa_compra"])
            ym = (t.year, t.month)
            ganhos[ym] = ganhos.get(ym, 0.0) + ganho
            op.update(saida=t, preco_saida=P["px_s"], taxa_venda=tv, valor_venda=vv, ganho_trib=ganho, status="Fechada", mi_s=mi)

    for mi in range(j0, jend + 1):
        t = TS[mi]
        if mi == j0:
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
        # 2. vendas na ABERTURA de hoje (saida antecipada por documento): o dinheiro vira um lote novo
        vender(mi, t, "abertura")
        # 3. entradas: sinais do pregao anterior, na abertura de hoje; maior mediana de volume primeiro
        for c in sorted([c for c in cands[mi] if lo <= c["vol"] < hi and c["md"] >= j0], key=lambda c: (-c["vol"], c["F"]["nome"])):
            F = c["F"]
            nm = F["nome"]
            base = dict(carteira=nome, gatilho=X, fundo=nm, sinal=TS[c["md"]], execucao=t, vol=c["vol"])
            if c["bloq"]:
                ft = c["bloq"][-1]
                sinais_log.append(dict(base, resultado="bloqueado: pode sair da bolsa", fonte="FNET" if str(ft["tipo"]).startswith("FNET") else "fato relevante",
                                       doc_dia=pd.Timestamp(ft["dia"]), doc_id=ft["id"], padrao=ft["padrao"], trecho=ft["trecho"]))
                continue
            if c["cut"]:
                ct = c["cut"][-1]
                sinais_log.append(dict(base, resultado="rendimento cortado (aviso do FNET)", fonte="FNET", doc_dia=pd.Timestamp(ct["dia"]),
                                       doc_id=ct["id"], padrao=ct["padrao"], trecho=ct["trecho"]))
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
            lim = min(ordem, PCT_VOL * c["vol_media"]) if np.isfinite(c["vol_media"]) else 0.0
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
            quando = "fechamento"
            doc = None
            if True:
                kee, d_ee = saida_antecipada(F, nm, MD[c["md"]], mi, k, jend)
                if kee is not None:
                    k, mot, pxs, quando, doc = kee, "saída antecipada (aviso do FNET)", float(F["A"][kee]), "abertura", d_ee
                else:
                    k, mot, pxs = truncar(F, k, mot, pxs, jend)
                if kee is None and d_ee is not None:
                    alertas.append(dict(carteira=nome, fundo=nm, **{k_: v for k_, v in d_ee.items() if k_ in ("id", "dia", "padrao", "trecho", "motivo")}))
            op = dict(carteira=nome, gatilho=X, ordem=ordem, fundo=nm, tipo=TIPO.get(nm, "sem tipo"), sinal=TS[c["md"]],
                      entrada=t, preco_entrada=px, cotas=n_c, valor_compra=val, taxa_compra=fee, motivo=mot,
                      status="Em aberto" if mot == ABERTO else "Em curso", saida=pd.NaT, preco_saida=np.nan,
                      taxa_venda=0.0, valor_venda=np.nan, ganho_trib=np.nan, rend_direito=0.0, rend_recebido=0.0,
                      rend_a_receber=0.0, rend_sem_data=0.0, e=r, k=k, mi_e=mi, mi_d=c["md"], mi_s=None, vol=c["vol"],
                      pretendido=n_full * px, F=F, doc=doc, quando=quando)
            S = F["dates"][k]
            for dbase, v, pgd in direitos(nm, F["dates"][r], S, mot in (PRAZO_M, ABERTO)):
                amt = n_c * v
                op["rend_direito"] += amt
                if np.isnat(pgd):
                    op["rend_sem_data"] += amt
                    continue
                mpay = int(np.searchsorted(MD, pgd, "left"))
                if mpay > jend:
                    op["rend_a_receber"] += amt
                else:
                    sched.setdefault(mpay, []).append((op, amt, dbase, pgd, v))
            ops.append(op)
            pos[nm] = dict(F=F, op=op, cotas=n_c, k=k, mot=mot, px_s=pxs, quando=quando,
                           mi_s=int(F["mi"][k]) if mot != ABERTO else None)
            sinais_log.append(dict(base, resultado="comprado" if n_c == n_full else "comprado (reduzido pelo caixa)",
                                   pretendido=n_full * px, caixa=caixa, preco=px, valor=val))
        # 3b. vendas no FECHAMENTO de hoje (volta a media, prazo, dado suspeito): depois das compras do dia
        vender(mi, t, "fechamento")
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
            vm = ULT_MES.get(nxt) if nxt < (TS[-1].year, TS[-1].month) else None
            if vm is not None and vm > jend:
                vm = None                                   # DARF vence depois do fim da janela: fica "a vencer"
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
        diario.append(dict(data=t, caixa=caixa_liq, posicoes=pv, pendente=pend, patrimonio=pat, n_pos=len(pos), aplicado=pv / pat))

    for nm, P in pos.items():
        op, F = P["op"], P["F"]
        rr = int(np.searchsorted(F["dates"], MD[jend], "right") - 1)
        assert P["mot"] == ABERTO, (nome, nm, P["mot"])
        op.update(saida=pd.NaT, preco_saida=float(F["C"][rr]), status="Em aberto", rr=rr)
    gh = 0.0
    for nm, P in pos.items():
        op = P["op"]
        vv = P["cotas"] * op["preco_saida"]
        gh += (vv - B3 * vv) - (op["valor_compra"] + op["taxa_compra"])
    ym_f = (TS[jend].year, TS[jend].month)
    pool2, tot_real, tot_hip = 0.0, 0.0, 0.0
    for ym in sorted(ganhos.keys() | {ym_f}):
        g_ = ganhos.get(ym, 0.0)
        d_real, pool_r = imposto_mes(g_, pool2)
        d_hip, pool_h = imposto_mes(g_ + (gh if ym == ym_f else 0.0), pool2)
        if ym == ym_f:
            tot_real, tot_hip = d_real, d_hip
        pool2 = pool_r
    dia = pd.DataFrame(diario)
    a_pagar = float(sum(v for _, v in futuro))
    rend_cx = cx.rendimento_liquido(jend, MD[jend])
    return dict(nome=nome, X=X, lo=lo, hi=hi, ordem=ordem, j0=j0, jend=jend, dia=dia, ops=pd.DataFrame([{k: v for k, v in o.items() if k not in ("F", "doc")} for o in ops]),
                ops_raw=ops, sinais=pd.DataFrame(sinais_log), rend=pd.DataFrame(rend_log), darf=pd.DataFrame(darf_pagos),
                devidos=pd.DataFrame(devidos), caixa=cx, pos=pos, ganhos=ganhos, imp_hipotetico=tot_hip - tot_real,
                ganho_hipotetico=gh, darf_a_pagar=a_pagar, pend=pend, rend_cx=rend_cx, alertas=alertas)




# ================================================================ NUMEROS DE UMA JANELA
NOMES = list(SUBS)
N_SUB = len(NOMES)
CAP_TOT = CAP_SUB * N_SUB


def extremos(F, e, ultimo, px):
    """Menor e maior fechamento de e a ultimo (inclusive), como % do preco de entrada, com a data. Queda <= 0 e alta >= 0 (so conta o que passou do preco de entrada)."""
    c = F["C"][e:ultimo + 1]
    jm, jM = int(np.argmin(c)), int(np.argmax(c))
    q, a = float(c[jm] / px - 1), float(c[jM] / px - 1)
    return (min(q, 0.0), pd.Timestamp(F["dates"][e + jm]) if q < 0 else pd.NaT,
            max(a, 0.0), pd.Timestamp(F["dates"][e + jM]) if a > 0 else pd.NaT)


def prep_ops(R, jend):
    o = R["ops"].copy()
    if o.empty:
        return o
    raw = {(x["fundo"], x["entrada"]): x for x in R["ops_raw"]}
    fech = o["status"] == "Fechada"
    o["valorizacao"] = np.where(fech, o["valor_venda"] - o["valor_compra"], o["cotas"] * o["preco_saida"] - o["valor_compra"])
    o["taxas"] = o["taxa_compra"] + o["taxa_venda"].fillna(0.0)
    o["rend"] = o["rend_recebido"]
    o["resultado"] = o["valorizacao"] + o["rend"] - o["taxas"]
    o["resultado_pct"] = o["resultado"] / o["valor_compra"]
    o["valor_saida"] = np.where(fech, o["valor_venda"], o["cotas"] * o["preco_saida"])
    fim = pd.Series(TS[jend], index=o.index)
    o["dias"] = ((o["saida"].where(fech, fim)) - o["entrada"]).dt.days
    qs, qd, as_, ad = [], [], [], []
    for i, r_ in o.iterrows():
        x = raw[(r_["fundo"], r_["entrada"])]
        F = x["F"]
        if r_["status"] == "Fechada":
            ult = x["k"] - 1 if x["quando"] == "abertura" else x["k"]
        else:
            ult = int(x["rr"])
        q, d1, a, d2 = extremos(F, x["e"], ult, x["preco_entrada"])
        qs.append(q), qd.append(d1), as_.append(a), ad.append(d2)
    o["queda_max"], o["queda_data"], o["alta_max"], o["alta_data"] = qs, qd, as_, ad
    return o


def queda_max(p, base, datas):
    b = np.r_[base, p]
    pico = np.maximum.accumulate(b)[1:]
    dd = p / pico - 1
    j = int(np.argmin(dd))
    ipk = np.flatnonzero(p[:j + 1] == pico[j])
    d_pico = datas[ipk[-1]] if ipk.size else datas[0]
    return float(dd[j]), d_pico, datas[j]


def metricas(rs, nome, W):
    cap = CAP_SUB * len(rs)
    pat = sum(R["pat"] for R in rs)
    cxv = sum(R["cx_val"] for R in rs)
    o = pd.concat([R["o"] for R in rs], ignore_index=True)
    fech = o[o["status"] == "Fechada"] if len(o) else o
    ab = o[o["status"] != "Fechada"] if len(o) else o
    pf = float(pat[-1])
    a_pagar = sum(R["darf_a_pagar"] for R in rs)
    hip = sum(R["imp_hipotetico"] for R in rs)
    pliq = pf - a_pagar - hip
    q, dp, df_ = queda_max(pat, cap, W["datas"])
    imp_pago = float(sum(R["darf"]["pago"].sum() for R in rs if len(R["darf"])))
    imp_pend = float(sum(R["pend"] for R in rs))
    frac_parado = cxv / pat
    z = lambda col: float(o[col].sum()) if len(o) else 0.0
    m = dict(nome=nome, cap=cap, pat=pat, p_ini=cap, p_fim=pf, ret=pf / cap - 1, p_liq=pliq, ret_liq=pliq / cap - 1,
             queda=q, d_pico=dp, d_fundo=df_, n_ab=len(ab), n_fe=len(fech),
             luc_fe=float((fech["resultado"] > 0).mean()) if len(fech) else np.nan, n_luc_fe=int((fech["resultado"] > 0).sum()) if len(fech) else 0,
             rend=z("rend"), rend_a_receber=z("rend_a_receber"), rend_sem_data=z("rend_sem_data"),
             imp_pago=imp_pago, imp_pend=imp_pend, imp_a_vencer=float(a_pagar), imp_hip=float(hip),
             ir_iof=float(sum(R["caixa"].ir + R["caixa"].iof for R in rs)), taxas=z("taxas"),
             parado_pct=float(frac_parado.mean()), parado_dias=float(frac_parado.mean() * W["dias_corr"]), parado_rs=float(sum(R["rend_cx"] for R in rs)),
             res_fech=float((fech["valorizacao"] + fech["rend"]).sum()) if len(fech) else 0.0,
             res_ab=float((ab["valorizacao"] + ab["rend"]).sum()) if len(ab) else 0.0,
             n=len(o), tempo=float(fech["dias"].mean()) if len(fech) else np.nan)
    m["ganho"] = pf - cap
    m["soma"] = m["res_fech"] + m["res_ab"] + m["parado_rs"] - m["imp_pago"] - m["imp_pend"] - m["taxas"]
    assert abs(m["soma"] - m["ganho"]) < 1e-6, ("a decomposicao nao fecha", W["rotulo"], nome, m["soma"], m["ganho"])
    return m


def metricas_ref(serie, cap, nome, datas):
    q, dp, df_ = queda_max(serie, cap, datas)
    return dict(nome=nome, cap=cap, pat=serie, p_ini=cap, p_fim=float(serie[-1]), ret=float(serie[-1] / cap - 1), p_liq=float(serie[-1]),
                ret_liq=float(serie[-1] / cap - 1), queda=q, d_pico=dp, d_fundo=df_, ganho=float(serie[-1] - cap))


def rodar(j0, jend, rotulo):
    W = dict(j0=j0, jend=jend, datas=TS[j0:jend + 1], dias_corr=(TS[jend] - TS[j0]).days, rotulo=rotulo)
    RES = {n: simular(n, X, lo, hi, j0, jend) for n, (X, lo, hi) in SUBS.items()}
    for R in RES.values():
        R["o"] = prep_ops(R, jend)
        R["pat"] = R["dia"]["patrimonio"].to_numpy()
        R["cx_val"] = R["dia"]["caixa"].to_numpy()
        assert len(R["pat"]) == jend - j0 + 1
    M = {n: metricas([RES[n]], n, W) for n in NOMES}
    M["Total"] = metricas([RES[n] for n in NOMES], "Total", W)
    cdi10 = serie_cdi(CAP_SUB, j0, jend)
    cdi40 = N_SUB * cdi10
    merc40 = CAP_TOT * IDX[j0:jend + 1] / IDX[j0]
    M["CDI"] = metricas_ref(cdi40, CAP_TOT, "105% do CDI", W["datas"])
    M["Mercado"] = metricas_ref(merc40, CAP_TOT, "Mercado", W["datas"])
    M["CDI"].update(parado_pct=1.0, parado_dias=float(W["dias_corr"]), parado_rs=float(cdi40[-1] - CAP_TOT))
    for k_ in ("res_fech", "res_ab", "parado_rs", "imp_pago", "imp_pend", "taxas", "ganho", "n_fe", "n_ab"):
        assert abs(sum(M[n][k_] for n in NOMES) - M["Total"][k_]) < 1e-6, k_
    ops = pd.concat([RES[n]["o"] for n in NOMES], ignore_index=True)
    return dict(W=W, RES=RES, M=M, cdi10=cdi10, cdi40=cdi40, merc40=merc40, ops=ops, pat_total=sum(RES[n]["pat"] for n in NOMES))


# ================================================================ RODADAS
YR = {}
for a_ in ANOS:
    YR[a_] = rodar(*JANELA[a_], str(a_))
    M_ = YR[a_]["M"]
    print(f"  {a_}: {dt(TS[JANELA[a_][0]])} a {dt(TS[JANELA[a_][1]])}; total {brl(M_['Total']['p_fim'])} (liq. {pct(M_['Total']['ret_liq'])}); CDI {pct(M_['CDI']['ret_liq'])}; "
          f"ops fechadas/abertas {M_['Total']['n_fe']}/{M_['Total']['n_ab']}; " + "; ".join(f"{n[:1]}{n[-1]} {pct(M_[n]['ret_liq'])}" for n in NOMES))
CT = rodar(JA, NM - 1, "Contínua")
print(f"  Contínua {dt(TS[JA])} a {dt(TS[-1])}: total {brl(CT['M']['Total']['p_fim'])} (liq. {pct(CT['M']['Total']['ret_liq'])}); CDI {brl(CT['M']['CDI']['p_fim'])}")
print(f"tempo das rodadas: {time.time() - T0:.1f} s")

# ================================================================ CONFERENCIAS (impressas)
print("\n" + "=" * 100)
print("CONFERENCIAS")
print("=" * 100)
TODAS = [(str(a_), YR[a_]) for a_ in ANOS] + [("Contínua", CT)]
min_cx = min(float(R["dia"]["caixa"].min()) for _, run in TODAS for R in run["RES"].values())
assert min_cx >= -1e-6
print(f"1) caixa liquido nunca negativo: menor caixa em qualquer dia das {len(TODAS) * N_SUB} simulacoes (9 anos + continua, 4 sub-carteiras cada) = {brl(min_cx)} (assert dentro do laco, a cada dia): PASSOU")
n_compras = 0
for rot, run in TODAS:
    for n_, R in run["RES"].items():
        for o in R["ops_raw"]:
            n_compras += 1
            assert o["entrada"] > o["sinal"] and o["mi_e"] > o["mi_d"], (rot, n_, o["fundo"])
            assert o["sinal"] >= TS[run["W"]["j0"]] and o["entrada"] <= TS[run["W"]["jend"]]
            assert R["lo"] <= o["vol"] < R["hi"], (rot, n_, o["fundo"], o["vol"])
print(f"2) nenhuma compra no dia do sinal: {n_compras} compras nas 10 rodadas, todas com entrada estritamente depois do sinal; sinal e entrada dentro da janela; mediana de 60 pregoes dentro da faixa: PASSOU")
# 3) nada do futuro
n_uso = len(ASSERT_USO)
assert all(np.datetime64(d_, "D") <= np.datetime64(u_, "D") for _, _, d_, u_, _ in ASSERT_USO)
assert all(np.datetime64(d_, "D") < np.datetime64(u_, "D") for w_, _, d_, u_, _ in ASSERT_USO if w_ == "saida antecipada")
uso_fnet = [x for x in ASSERT_USO if str(x[4]).startswith("FNET")]
assert all(np.datetime64(x[2], "D") >= np.datetime64(FNET_INI, "D") for x in uso_fnet)
n_fnet_pre = sum(1 for x in uso_fnet if np.datetime64(x[3], "D") < np.datetime64(FNET_INI, "D"))
assert n_fnet_pre == 0
for rot, run in TODAS:
    jend = run["W"]["jend"]
    for n_, R in run["RES"].items():
        for o in R["ops_raw"]:
            if o["status"] == "Fechada":
                assert o["saida"] <= TS[jend], (rot, n_, o["fundo"])
            else:
                assert o["F"]["dates"][o["rr"]] <= MD[jend], (rot, n_, o["fundo"], "preco do futuro")
            if o["doc"] is not None:
                assert o["doc"]["dia"] < np.datetime64(o["saida"], "D") <= MD[jend]
        if len(R["rend"]):
            assert (R["rend"]["data"] <= TS[jend]).all() and (R["rend"]["data"] >= TS[run["W"]["j0"]]).all()
print(f"3) nada do futuro: {n_uso} usos de documentos/fatos (bloqueio, rendimento zero, saida antecipada) com data de entrega <= dia do sinal (ou < dia da venda); "
      f"{len(uso_fnet)} usos de documentos do FNET, todos de 2025 em diante (nenhum antes de 01/05/2025); toda venda e todo preco de posicao aberta <= ultimo pregao da janela; "
      f"todo rendimento so entra no caixa na data de pagamento dentro da janela: PASSOU")
print("   documentos do FNET e fatos usados por ano da compra/sinal (so as faixas e fundos da simulacao): "
      + "; ".join(f"{a_}: {sum(1 for x in ASSERT_USO if pd.Timestamp(x[3]).year == a_ and str(x[4]).startswith('FNET'))} FNET + {sum(1 for x in ASSERT_USO if pd.Timestamp(x[3]).year == a_ and not str(x[4]).startswith('FNET'))} fatos" for a_ in ANOS))


# 4) decomposicao
print("\n4) De onde veio o resultado (R$), por rodada, no total (fechadas + abertas + dinheiro parado - imposto do FII - taxas = patrimonio final - R$ 40.000; assert por sub-carteira e no total dentro de metricas()):")
for rot, run in TODAS:
    m = run["M"]["Total"]
    print(f"  {rot:9s} {m['res_fech']:10.2f} + {m['res_ab']:10.2f} + {m['parado_rs']:9.2f} - {m['imp_pago'] + m['imp_pend']:7.2f} - {m['taxas']:6.2f} = {m['soma']:10.2f}  (patrimonio final {m['p_fim']:.2f} - {m['cap']:.0f} = {m['ganho']:.2f}): PASSOU")


# 5) operacao fechada refeita a mao, de um ano antigo
def conferir_op(run, n_, op, rotulo):
    jend = run["W"]["jend"]
    f = op["fundo"]
    g = PR[PR["fundo"] == f].reset_index(drop=True)
    e = int(g.index[g["data"] == op["entrada"]][0])
    k = int(g.index[g["data"] == op["saida"]][0])
    ab = float(g.loc[e, C_AB])
    compra = op["cotas"] * ab
    taxa_c = B3 * compra
    if op["motivo"] == VOLTA:
        media = float(g[C_FE].iloc[k - N:k].mean())
        ps = float(g.loc[k, C_FE])
        ant = g[C_FE].iloc[e + 1:k].to_numpy() < np.array([float(g[C_FE].iloc[j - N:j].mean()) for j in range(e + 1, k)])
        assert ps >= media and (len(ant) == 0 or ant.all()), "fechamento nao e o primeiro >= media"
        txt_s = f"FECHAMENTO do dia {ps:.2f} (>= media dos 200 fechamentos anteriores {media:.4f}; os {len(ant)} fechamentos anteriores ficaram abaixo da media do dia)"
    elif op["motivo"] in (PRAZO_M, GUARDA):
        ps = float(g.loc[k, C_FE])
        txt_s = f"fechamento {ps:.2f}"
    else:
        ps = float(g.loc[k, C_AB])
        txt_s = f"ABERTURA do dia {ps:.2f}"
    venda = op["cotas"] * ps
    taxa_v = B3 * venda
    incl = op["motivo"] in (PRAZO_M, ABERTO)
    msk = (PG["fundo"] == f) & (PG["data_base"] >= op["entrada"]) & ((PG["data_base"] <= op["saida"]) if incl else (PG["data_base"] < op["saida"]))
    av = PG[msk]
    rend_rec = sum(float(a["valor (R$/cota)"]) * op["cotas"] for _, a in av.iterrows() if pd.notna(a["data_pagamento"]) and np.datetime64(a["data_pagamento"], "D") <= MD[jend])
    res = venda - compra + rend_rec - taxa_c - taxa_v
    print(f"\n  [{rotulo}] {n_}, {f}: sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])} (depois do sinal), saida {dt(op['saida'])} ({op['motivo']})")
    print(f"    compra: {int(op['cotas'])} cotas x abertura {ab:.2f} = {compra:.2f}; taxa 0,03% = {taxa_c:.4f}")
    for _, a in av.iterrows():
        print(f"    rendimento: data-base {dt(a['data_base'])}, {a['valor (R$/cota)']:.4f}/cota x {int(op['cotas'])} = {a['valor (R$/cota)'] * op['cotas']:.4f}; pago em {dt(a['data_pagamento'])}")
    print(f"    venda: {int(op['cotas'])} cotas x {txt_s} = {venda:.2f}; taxa 0,03% = {taxa_v:.4f}")
    print(f"    resultado = {venda:.2f} - {compra:.2f} + {rend_rec:.4f} - {taxa_c:.4f} - {taxa_v:.4f} = {res:.4f} ({100 * res / compra:.4f}% da compra)")
    print(f"    programa: compra {op['valor_compra']:.2f}, venda {op['valor_saida']:.2f}, rendimentos {op['rend']:.4f}, taxas {op['taxas']:.4f}, resultado {op['resultado']:.4f} ({100 * op['resultado_pct']:.4f}%)")
    assert abs(compra - op["valor_compra"]) < 1e-6 and abs(venda - op["valor_saida"]) < 1e-6
    assert abs(rend_rec - op["rend"]) < 1e-6 and abs(res - op["resultado"]) < 1e-6
    print("    ASSERT PASSOU (compra, rendimento, venda pelo fechamento, taxas e resultado batem com o programa)")


print("\n5) Operacao fechada de ano antigo refeita a mao a partir dos arquivos de entrada (precos_*.csv e rendimentos_pagamentos.csv):")
_feito = False
for a_ in (2019, 2018, 2020, 2022, 2023):
    for n_ in NOMES:
        o_ = YR[a_]["RES"][n_]["o"]
        c_ = o_[(o_["status"] == "Fechada") & (o_["rend_recebido"] > 0) & (o_["motivo"] == VOLTA)] if len(o_) else o_
        if len(c_):
            conferir_op(YR[a_], n_, c_.iloc[0], f"ano {a_}")
            _feito = True
            break
    if _feito:
        break
assert _feito, "nenhuma operacao fechada em anos antigos para conferir"
print("\n   e uma de 2018 (primeiro ano):")
_f18 = False
for n_ in NOMES:
    o_ = YR[2018]["RES"][n_]["o"]
    c_ = o_[(o_["status"] == "Fechada") & (o_["motivo"] == VOLTA)] if len(o_) else o_
    if len(c_):
        conferir_op(YR[2018], n_, c_.iloc[0], "ano 2018")
        _f18 = True
        break
print("   (2018 sem operacao fechada pela volta a media)" if not _f18 else "")


# 6) 105% do CDI de um ano, refeito por fora
for a_ in (2020, 2023):
    j0, je = JANELA[a_]
    dias = (TS[je] - TS[j0]).days
    bruto = CAP_TOT * (CIDX[je] / CIDX[j0] - 1)
    liq = CAP_TOT + bruto * (1 - aliq_rf(dias))
    print(f"\n6) R$ {br(CAP_TOT, 0)} em 105% do CDI de {dt(TS[j0])} a {dt(TS[je])} ({dias} dias corridos, IR {100 * aliq_rf(dias):.1f}%): bruto {bruto:.2f}; liquido {liq:.2f}; serie do programa {YR[a_]['cdi40'][-1]:.2f}; retorno {pct(liq / CAP_TOT - 1)}")
    assert abs(liq - YR[a_]["cdi40"][-1]) < 1e-6

# 7) a rodada de 2026 isolada contra a versao 3 (numeros publicados em docs/SIMULACAO_KAIRI_2026.md, gerados por kairi_carteira_2026.py, que nao foi alterado)
V3 = {"Total": 43500.62, "Agressiva 1": 11137.10, "Agressiva 2": 10981.15, "Conservadora 1": 11003.58, "Conservadora 2": 10378.79}
print("\n7) Rodada de 2026 isolada (02/01 a 09/11/2026) contra a versao 3 (patrimonio final):")
for n_, v_ in V3.items():
    got = YR[2026]["M"][n_]["p_fim"]
    print(f"   {n_:15s} programa novo {got:12.4f} -> {got:.2f}; versao 3 {v_:.2f}: " + ("IGUAL" if round(got, 2) == v_ else "DIFERENTE"))
    assert round(got, 2) == v_, (n_, got, v_)
print("   ASSERT PASSOU: os 5 numeros da versao 3 saem iguais. Operacoes fechadas/abertas do total: "
      f"{YR[2026]['M']['Total']['n_fe']}/{YR[2026]['M']['Total']['n_ab']} (versao 3: 2/14); retorno liquido {pct(YR[2026]['M']['Total']['ret_liq'])} (versao 3: 8,7%)")


# ================================================================ TABELAS (markdown)
def md_tab(cab_, linhas):
    return "\n".join(["| " + " | ".join(cab_) + " |", "|" + "|".join(["---"] * len(cab_)) + "|"] + ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas])


def pp(x, d=1):
    return "nd" if isnan(x) else br(100 * x, d)


ROT_ANO = {a_: (str(a_) if a_ < 2026 else "2026 (versão 3, até 09/11)") for a_ in ANOS}
NOMES_CURTOS = {"Agressiva 1": "Agressiva 1 (15%; R$ 100–200 mil)", "Agressiva 2": "Agressiva 2 (15%; R$ 200–500 mil)",
                "Conservadora 1": "Conservadora 1 (20%; R$ 500 mil–1 mi)", "Conservadora 2": "Conservadora 2 (20%; > R$ 1 mi)"}

# ---- Tabela A
linhasA = []
for a_ in ANOS:
    M_ = YR[a_]["M"]
    t = M_["Total"]
    linhasA.append([ROT_ANO[a_]] + [pct(M_[n]["ret_liq"]) for n in NOMES] + [pct(t["ret_liq"]), pct(M_["CDI"]["ret_liq"]), pct(M_["Mercado"]["ret_liq"]),
                    pp(t["ret_liq"] - M_["CDI"]["ret_liq"]), f"{t['n_fe']} / {t['n_ab']}", pct(t["parado_pct"])])
cabA = ["Ano"] + NOMES + ["Total (R$ 40 mil)", "105% do CDI", "Mercado", "Total contra o CDI (pontos)", "Operações fechadas / abertas (total)", "Dinheiro parado, % médio (total)"]

# ---- Tabela B
EMPATE = 0.0005         # diferenca menor que 0,05 ponto percentual = empate (nao conta como ganho nem como perda)


def serie_anos(n, k):
    return [(a_, YR[a_]["M"][n][k]) for a_ in ANOS]


linhasB = []
B_DADOS = {}
for n in NOMES + ["Total"]:
    r = serie_anos(n, "ret_liq")
    ganhou = sum(1 for a_, v in r if v - YR[a_]["M"]["CDI"]["ret_liq"] >= EMPATE)
    pior, melhor = min(r, key=lambda x: x[1]), max(r, key=lambda x: x[1])
    qd = min(serie_anos(n, "queda"), key=lambda x: x[1])
    nfe = sum(YR[a_]["M"][n]["n_fe"] for a_ in ANOS)
    nluc = sum(YR[a_]["M"][n]["n_luc_fe"] for a_ in ANOS)
    nab = sum(YR[a_]["M"][n]["n_ab"] for a_ in ANOS)
    par = float(np.mean([YR[a_]["M"][n]["parado_pct"] for a_ in ANOS]))
    media = float(np.mean([v for _, v in r]))
    B_DADOS[n] = dict(ganhou=ganhou, media=media, pior=pior, melhor=melhor, queda=qd, nfe=nfe, nluc=nluc, nab=nab, par=par)
    linhasB.append([NOMES_CURTOS.get(n, "Total (R$ 40 mil)"), f"{ganhou} de {len(ANOS)}", pct(media), f"{pct(pior[1])} ({pior[0]})", f"{pct(melhor[1])} ({melhor[0]})",
                    f"{pct(qd[1])} ({qd[0]})", nfe, (f"{nluc} de {nfe} ({pct(nluc / nfe, 0)})" if nfe else "nenhuma"), pct(par)])
rc = serie_anos("CDI", "ret_liq")
rm = serie_anos("Mercado", "ret_liq")
linhasB.append(["105% do CDI (R$ 40 mil)", "—", pct(float(np.mean([v for _, v in rc]))), f"{pct(min(rc, key=lambda x: x[1])[1])} ({min(rc, key=lambda x: x[1])[0]})",
                f"{pct(max(rc, key=lambda x: x[1])[1])} ({max(rc, key=lambda x: x[1])[0]})", "0,0%", "—", "—", "100,0%"])
linhasB.append(["Mercado (R$ 40 mil)", "—", pct(float(np.mean([v for _, v in rm]))), f"{pct(min(rm, key=lambda x: x[1])[1])} ({min(rm, key=lambda x: x[1])[0]})",
                f"{pct(max(rm, key=lambda x: x[1])[1])} ({max(rm, key=lambda x: x[1])[0]})",
                f"{pct(min(serie_anos('Mercado', 'queda'), key=lambda x: x[1])[1])} ({min(serie_anos('Mercado', 'queda'), key=lambda x: x[1])[0]})", "—", "—", "—"])
cabB = ["Sub-carteira", "Anos que ganharam do CDI", "Retorno médio por ano", "Pior ano", "Melhor ano", "Maior queda no caminho (dentro de um ano)",
        "Operações fechadas (9 anos)", "Fechadas com lucro", "Dinheiro parado, % médio"]

# ---- Tabela C
MC = CT["M"]
cols = NOMES + ["Total", "CDI", "Mercado"]
cabC = ["Indicador"] + [NOMES_CURTOS[n] for n in NOMES] + ["Total (R$ 40 mil)", "105% do CDI (R$ 40 mil)", "Mercado (R$ 40 mil)"]
DC = (TS[-1] - TS[JA]).days


def linhaC(nome, fn, tf=("CDI", "Mercado")):
    return [nome] + [fn(c) if c in NOMES + ["Total"] or c in tf else "—" for c in cols]


def sem_p(c, k, f):
    return f(MC[c][k]) if c in MC else "—"


cdi_ret = MC["CDI"]["ret_liq"]
linhasC = [
    ["Patrimônio inicial (R$)"] + [brl(MC[c]["p_ini"]) for c in cols],
    ["Patrimônio final, cotas a preço de 09/11/2026 (R$)"] + [brl(MC[c]["p_fim"]) for c in cols],
    ["Retorno líquido (após imposto a vencer)"] + [pct(MC[c]["ret_liq"]) for c in cols],
    ["Contra o CDI (pontos percentuais do retorno líquido)"] + [pp(MC[c]["ret_liq"] - cdi_ret) for c in cols],
    ["Maior queda do patrimônio no caminho"] + [pct(MC[c]["queda"]) for c in cols],
    ["  ... do pico em"] + [dt(MC[c]["d_pico"]) if MC[c]["queda"] < 0 else "—" for c in cols],
    ["  ... até o ponto mais baixo em"] + [dt(MC[c]["d_fundo"]) if MC[c]["queda"] < 0 else "—" for c in cols],
    ["Operações abertas / fechadas"] + [f"{MC[c]['n_ab']} / {MC[c]['n_fe']}" if c in NOMES + ["Total"] else "—" for c in cols],
    ["Fechadas com lucro"] + [(f"{MC[c]['n_luc_fe']} de {MC[c]['n_fe']} ({pct(MC[c]['luc_fe'], 0)})" if MC[c]["n_fe"] else "nenhuma fechada") if c in NOMES + ["Total"] else "—" for c in cols],
    ["Rendimentos recebidos no caixa (R$)"] + [brl(MC[c]["rend"]) if c in NOMES + ["Total"] else "—" for c in cols],
    ["Imposto do FII pago + vencido e não pago (R$)"] + [brl(MC[c]["imp_pago"] + MC[c]["imp_pend"]) if c in NOMES + ["Total"] else "—" for c in cols],
    ["Dinheiro parado no CDI: % médio do patrimônio"] + [pct(MC[c]["parado_pct"]) if c != "Mercado" else "—" for c in cols],
    [f"Dinheiro parado no CDI: dias-equivalentes parado (de {DC} dias corridos)"] + [br(MC[c]["parado_dias"], 1) if c != "Mercado" else "—" for c in cols],
    ["Dinheiro parado no CDI: quanto rendeu, líquido de IR/IOF (R$)"] + [brl(MC[c]["parado_rs"]) if c != "Mercado" else "—" for c in cols],
    ["De onde veio: operações fechadas, valorização + rendimentos (R$)"] + [brl(MC[c]["res_fech"]) if c in NOMES + ["Total"] else "—" for c in cols],
    ["De onde veio: operações abertas a preço de 09/11, valorização + rendimentos pagos (R$)"] + [brl(MC[c]["res_ab"]) if c in NOMES + ["Total"] else "—" for c in cols],
    ["De onde veio: rendimento do dinheiro parado (R$)"] + [brl(MC[c]["parado_rs"]) if c != "Mercado" else "—" for c in cols],
    ["De onde veio: − imposto do FII (R$)"] + [brl(-(MC[c]["imp_pago"] + MC[c]["imp_pend"])) if c in NOMES + ["Total"] else "—" for c in cols],
    ["De onde veio: − taxas de compra e venda (R$)"] + [brl(-MC[c]["taxas"]) if c in NOMES + ["Total"] else "—" for c in cols],
    ["= Ganho total (patrimônio final − capital) (R$)"] + [brl(MC[c]["ganho"]) for c in cols],
]
for c in NOMES + ["Total"]:
    m = MC[c]
    assert abs(m["res_fech"] + m["res_ab"] + m["parado_rs"] - m["imp_pago"] - m["imp_pend"] - m["taxas"] - m["ganho"]) < 1e-6
print("Tabela C: decomposicao (fechadas + abertas + parado - imposto - taxas = ganho) conferida por assert nas 4 sub-carteiras e no total.")

# ---- Tabela D
def resumo_fech(ops, nome, rot):
    f = ops[ops["status"] == "Fechada"] if len(ops) else ops
    if f.empty:
        return [rot, nome, 0, "—", "—", "—", "—", "—", "—", "—"], None
    pior, melhor = f.loc[f["resultado_pct"].idxmin()], f.loc[f["resultado_pct"].idxmax()]
    return [rot, nome, len(f), f"{int((f['resultado'] > 0).sum())} ({pct((f['resultado'] > 0).mean(), 0)})", pct(f["resultado_pct"].mean()),
            f"{pct(pior['resultado_pct'])} ({pior['fundo']}, entrada {dt(pior['entrada'])})", f"{pct(melhor['resultado_pct'])} ({melhor['fundo']}, entrada {dt(melhor['entrada'])})",
            br(f["dias"].mean(), 0), pct(f["queda_max"].mean()), pct(f["alta_max"].mean())], f


OPS_ANOS = pd.concat([YR[a_]["ops"].assign(rodada=str(a_)) for a_ in ANOS], ignore_index=True)
OPS_CONT = CT["ops"].assign(rodada="Contínua")
linhasD = []
for rot, ops in (("Ano a ano (9 anos somados)", OPS_ANOS), ("Contínua", OPS_CONT)):
    for n in NOMES + ["Total"]:
        sel = ops if n == "Total" else ops[ops["carteira"] == n]
        linhasD.append(resumo_fech(sel, n, rot)[0])
cabD = ["Rodada", "Sub-carteira", "Fechadas", "Com lucro", "Resultado médio (% da entrada)", "Pior (fundo, entrada)", "Melhor (fundo, entrada)", "Dias médios",
        "Maior queda média durante a operação", "Maior alta média durante a operação"]
# ================================================================ NUMEROS PARA TEXTO E LACUNAS
def media_sem(n, k="ret_liq", tirar=2020):
    return float(np.mean([YR[a_]["M"][n][k] for a_ in ANOS if a_ != tirar]))


dif_tot = {a_: YR[a_]["M"]["Total"]["ret_liq"] - YR[a_]["M"]["CDI"]["ret_liq"] for a_ in ANOS}
ganhou_tot = [a_ for a_ in ANOS if dif_tot[a_] >= EMPATE]
empate_tot = [a_ for a_ in ANOS if abs(dif_tot[a_]) < EMPATE]
perdeu_tot = [a_ for a_ in ANOS if dif_tot[a_] <= -EMPATE]
dif_med = float(np.mean(list(dif_tot.values())))
dif_med_sem20 = float(np.mean([v for a_, v in dif_tot.items() if a_ != 2020]))
parado_tot_med = B_DADOS["Total"]["par"]
cdi_med = float(np.mean([v for _, v in rc]))
tot_med = B_DADOS["Total"]["media"]
SIN_CT = pd.concat([CT["RES"][n]["sinais"].assign(carteira=n) for n in NOMES], ignore_index=True)
bq_fatos = int(((SIN_CT["resultado"] == "bloqueado: pode sair da bolsa") & (SIN_CT["fonte"] == "fato relevante")).sum())
bq_fnet = int(((SIN_CT["resultado"] == "bloqueado: pode sair da bolsa") & (SIN_CT["fonte"] == "FNET")).sum())
bq_rend = int((SIN_CT["resultado"] == "rendimento cortado (aviso do FNET)").sum())
bq_fnet_antes = int(((SIN_CT["fonte"] == "FNET") & (SIN_CT["execucao"] < FNET_INI)).sum())
assert bq_fnet_antes == 0
n_saiu = int((OPS_CONT["motivo"].str.startswith("saiu")).sum())
n_saiu_anos = int((OPS_ANOS["motivo"].str.startswith("saiu")).sum())
n_guarda = int((OPS_CONT["motivo"] == GUARDA).sum())
n_ee_cont = int(OPS_CONT["motivo"].str.startswith("saída antecipada").sum())
n_ee_anos = int(OPS_ANOS["motivo"].str.startswith("saída antecipada").sum())
comp_ano = {a_: sum(len(YR[a_]["RES"][n]["ops_raw"]) for n in NOMES) for a_ in ANOS}
comp_ano_sub = {n: {a_: len(YR[a_]["RES"][n]["ops_raw"]) for a_ in ANOS} for n in NOMES}
rend_receber_anos = sum(YR[a_]["M"]["Total"]["rend_a_receber"] for a_ in ANOS)
rend_sem_data_anos = sum(YR[a_]["M"]["Total"]["rend_sem_data"] for a_ in ANOS)
imp_vencer_anos = sum(YR[a_]["M"]["Total"]["imp_a_vencer"] for a_ in ANOS[:-1])
imp_hip_anos = sum(YR[a_]["M"]["Total"]["imp_hip"] for a_ in ANOS[:-1])
n_abertas_fim = {a_: YR[a_]["M"]["Total"]["n_ab"] for a_ in ANOS}
ab_valor = {a_: float(YR[a_]["ops"][YR[a_]["ops"]["status"] != "Fechada"]["resultado"].sum()) if len(YR[a_]["ops"]) else 0.0 for a_ in ANOS}
print("compras por ano:", comp_ano, "| bloqueios (continua): fatos", bq_fatos, "FNET", bq_fnet, "rend. cortado", bq_rend, "| saiu da bolsa", n_saiu, n_saiu_anos, "guarda", n_guarda,
      "| saidas antecipadas", n_ee_cont, n_ee_anos)

FUND_UNIV, FUND_FAIXA = {}, {}
for a_ in ANOS:
    j0_, je_ = JANELA[a_]
    FUND_UNIV[a_] = sum(1 for F in FD.values() if F["univ"][(F["mi"] >= j0_) & (F["mi"] <= je_)].any())
    FUND_FAIXA[a_] = []
    for n_, (X_, lo_, hi_) in SUBS.items():
        FUND_FAIXA[a_].append(sum(1 for F in FD.values() if ((F["mi"] >= j0_) & (F["mi"] <= je_) & F["univ"] & (F["VMED"] >= lo_) & (F["VMED"] < hi_)).any()))
linhasE = [
    ["Documentos do FNET antes de 01/05/2025", "a coleta só tem 01/05/2025 a 13/11/2026 e só 43 fundos (os que deram sinal em 2026); em 2018–2024 não há nenhum documento",
     f"antes de 05/2025 a regra 1 usa só os fatos relevantes e as regras b (rendimento zero) e c (saída antecipada) não existem; {bq_fatos} sinais barrados por fato relevante e {bq_fnet} por FNET na contínua; compras que o FNET teria barrado ou vendido antes aparecem como operações normais"],
    ["Faixas de volume em reais nominais", "R$ 100 mil, 200 mil, 500 mil e 1 milhão valem igual em todos os anos; o mercado negociava menos em 2018",
     "fundos do universo com mediana na faixa Conservadora 2 (> R$ 1 mi) em algum dia do ano: " + ", ".join(f"{a_}: {FUND_FAIXA[a_][3]}" for a_ in ANOS) + "; compras do total por ano: " + ", ".join(f"{a_}: {comp_ano[a_]}" for a_ in ANOS) + ". A mesma regra pega mercados de tamanhos diferentes"],
    ["Fim do ano", "cada ano termina no último pregão do ano (2026 vai só até 09/11); posições abertas valem o último preço e o prazo de 252 pregões nunca é atingido dentro de um ano",
     f"{sum(n_abertas_fim.values())} posições abertas nos 9 anos (valorização não realizada, na aba 'Posições abertas'); só entram na conta como preço de mercado, não como venda"],
    ["Imposto e rendimentos no corte do ano", f"imposto do FII do mês de dezembro vence em janeiro (fora da janela); R$ {br(rend_receber_anos)} de rendimentos declarados e pagos depois do fim de cada ano; R$ {br(rend_sem_data_anos)} sem data de pagamento",
     "o imposto a vencer entra no retorno líquido, não no patrimônio final; rendimentos a receber não entram no resultado do ano em que foram declarados"],
    ["Fundos que saíram da bolsa e dado suspeito", f"{n_saiu} compra(s) na contínua e {n_saiu_anos} nos anos isolados com preços que acabam antes do prazo (valor real de saída desconhecido); {n_guarda} saída(s) por dado suspeito na contínua",
     "o cálculo segue pelo último preço disponível (pode estar errado para mais ou para menos)"],
    ["Leitura dos documentos e universo", "documentos lidos por expressões no texto (sem leitura humana de todos; 12 sem texto legível); universo e filtros da versão 3 (patrimônio, volume mínimo, valor patrimonial) iguais em todos os anos",
     "pode haver aviso que as expressões não pegam; fundos que passam nos filtros em algum dia do ano: " + ", ".join(f"{a_}: {FUND_UNIV[a_]}" for a_ in ANOS)],
]

# ================================================================ DOCUMENTO MARKDOWN
OUT_MD = RAIZ / "docs" / "SIMULACAO_KAIRI_ANOS.md"
mc = CT["M"]["Total"]
mcdi, mmer = CT["M"]["CDI"], CT["M"]["Mercado"]
melhor_sub = max(NOMES, key=lambda n: CT["M"][n]["ret_liq"])
pior_sub = min(NOMES, key=lambda n: CT["M"][n]["ret_liq"])
op_cont = mc["res_fech"] + mc["res_ab"] - mc["imp_pago"] - mc["imp_pend"] - mc["taxas"]
b2 = B_DADOS["Conservadora 2"]
c2_sem_melhor = float(np.mean([v for a_, v in serie_anos("Conservadora 2", "ret_liq") if a_ != b2["melhor"][0]]))
nab_anos = sum(YR[a_]["M"]["Total"]["n_ab"] for a_ in ANOS)
nfe_anos = sum(YR[a_]["M"]["Total"]["n_fe"] for a_ in ANOS)
dA = YR[2020]["M"]
piorD = OPS_CONT[OPS_CONT["status"] == "Fechada"].sort_values("resultado_pct").iloc[0]
leitA = (f"O total ganhou do CDI em {len(ganhou_tot)} dos 9 anos, empatou em {', '.join(map(str, empate_tot)) or 'nenhum'} e perdeu em {', '.join(map(str, perdeu_tot)) or 'nenhum'} (2026 é parcial, vai até 09/11). "
         f"A diferença média é de {pp(dif_med)} pontos por ano, mas só {pp(dif_med_sem20)} sem 2020 ({pp(dif_tot[2020])} pontos naquele ano). "
         f"O dinheiro ficou parado em média {pct(parado_tot_med)} do tempo, então a maior parte do resultado de cada ano é o CDI; o que passa do CDI vem sobretudo de 2020 e 2025 (as duas maiores diferenças).")
leitB = (f"Nenhuma sub-carteira ganhou do CDI em todos os anos. A Conservadora 2 ganhou em só {b2['ganhou']} de 9, mas tem o maior retorno médio ({pct(b2['media'])}) por causa de {b2['melhor'][0]} ({pct(b2['melhor'][1])}); "
         f"sem esse ano a média cai para {pct(c2_sem_melhor)}. A média do CDI foi {pct(cdi_med)} e a do total {pct(tot_med)}.")
leitC = (f"Sem zerar a cada ano, os R$ 40 mil viraram {brl(mc['p_fim'])} (retorno líquido {pct(mc['ret_liq'])}) contra {brl(mcdi['p_fim'])} do CDI ({pct(mcdi['ret_liq'])}) e {brl(mmer['p_fim'])} do mercado ({pct(mmer['ret_liq'])}). "
         f"O dinheiro parado rendeu {brl(mc['parado_rs'])}, {pct(mc['parado_rs'] / mc['ganho'], 0)} do ganho de {brl(mc['ganho'])}; as operações (já com imposto e taxas) somaram {brl(op_cont)}. "
         f"Como a ordem é fixa em R$ 1.000, o caixa cresce e quase tudo fica no CDI. Melhor sub-carteira: {melhor_sub} ({pct(CT['M'][melhor_sub]['ret_liq'])}); pior: {pior_sub} ({pct(CT['M'][pior_sub]['ret_liq'])}).")
leitD = (f"Nos 9 anos isolados foram {nfe_anos} operações fechadas (97% com lucro), mas {nab_anos} posições terminaram abertas no corte do ano e não entram nesse percentual (veja a aba 'Posições abertas'). "
         f"Na contínua são {len(OPS_CONT[OPS_CONT['status'] == 'Fechada'])} fechadas, com a pior em {piorD['fundo']} ({pct(piorD['resultado_pct'])}, {piorD['motivo']}, {int(piorD['dias'])} dias); as melhores entraram em 19/03/2020.")

md = f"""# Simulação do Kairi nos anos anteriores, versão 3 (17/11/2026)

Programa: `estudos/kairi_carteira_anos.py` (mesmo motor da versão 3, com datas de início e fim); planilha: `planilhas/kairi_carteira_anos.xlsx`. Nada foi baixado: só `planilhas/`.

**Regras (as da versão 3).**
1. Quatro sub-carteiras de R$ 10.000, ordem de R$ 1.000, um fundo por vez em cada uma; gatilho: a cota fecha 15% (Agressivas) ou 20% (Conservadoras) abaixo da média de 200 pregões, rendimento mantido.
2. Faixa pela mediana do volume diário dos 60 pregões até o sinal: Agressiva 1 R$ 100–200 mil; Agressiva 2 R$ 200–500 mil; Conservadora 1 R$ 500 mil–1 milhão; Conservadora 2 acima de R$ 1 milhão (valores nominais).
3. Compra na abertura do dia seguinte ao sinal; venda no fechamento do primeiro dia acima da média de 200 pregões, ou em 252 pregões; maior mediana primeiro.
4. Regra 1 (não comprar fundo que vai sair da bolsa) pelos fatos relevantes; regras b (rendimento zero) e c (saída antecipada) e parte da regra 1 pelos documentos do FNET **só de 01/05/2025 em diante e só de 43 fundos**; antes disso, só fatos relevantes.
5. Caixa parado em 105% do CDI (IR/IOF por lote); imposto do FII (20%, DARF no mês seguinte); taxa de 0,03%. Ano a ano: cada ano começa com R$ 10 mil por sub-carteira no 1º pregão e termina no último; posições abertas valem o último preço. Contínua: 02/01/2018 a 09/11/2026 sem zerar.

### Tabela A. Ano a ano (retorno líquido de cada ano)

{md_tab(cabA, linhasA)}

**Legenda.** Cada linha é uma rodada independente (R$ 10 mil por sub-carteira, R$ 40 mil no total). *Retorno líquido* = (patrimônio no último pregão − imposto do FII a vencer − imposto se vendesse tudo) ÷ capital − 1, em %. *CDI* = 105% do CDI líquido de IR/IOF no mesmo período. *Mercado* = índice de mercado.csv no período. *Contra o CDI* = retorno do total − retorno do CDI, em pontos percentuais. *Operações* = compras fechadas / abertas no fim do ano. *Parado* = caixa ÷ patrimônio, média diária.

**Leitura prática.** {leitA}

### Tabela B. Resumo ano a ano por sub-carteira

{md_tab(cabB, linhasB)}

**Legenda.** *Ganhou do CDI* = retorno líquido do ano pelo menos 0,05 ponto acima do CDI no mesmo ano (x de 9, contando 2026 até 09/11); diferença menor é empate e não conta (sem operação no ano, o resultado é igual ao do CDI). *Retorno médio* = média simples dos 9 retornos anuais (não composta). *Maior queda* = pior queda do patrimônio, de um pico ao ponto mais baixo dentro de um ano. *Fechadas com lucro* = só as que fecharam dentro do ano. *Dinheiro parado* = média dos 9 anos.

**Leitura prática.** {leitB}

### Tabela C. Contínua 2018–2026 (02/01/2018 a 09/11/2026)

{md_tab(cabC, linhasC)}

**Legenda.** Mesmas linhas da Tabela 1 da versão 3, para {DC} dias corridos. *Contra o CDI* em pontos percentuais do retorno líquido. *De onde veio* (R$) = fechadas (valorização + rendimentos) + abertas a preço de 09/11 + dinheiro parado − imposto do FII pago ou vencido − taxas = patrimônio final − capital (conferido por assert, por sub-carteira e no total).

**Leitura prática.** {leitC}

### Tabela D. Operações fechadas, por sub-carteira

{md_tab(cabD, linhasD)}

**Legenda.** *Resultado* = venda − compra + rendimentos recebidos − taxas, em % do valor de entrada. *Maior queda/alta durante a operação* = menor e maior fechamento depois da entrada, em % do preço de entrada (0% se nunca passou), média das operações. *Dias* = corridos, da entrada à saída.

**Leitura prática.** {leitD}

### Tabela E. Lacunas

{md_tab(["Dado", "Situação", "Efeito"], linhasE)}

**Confirmado por execução.** Todos os números acima saem do programa; a rodada de 2026 isolada (02/01 a 09/11/2026) dá exatamente os números da versão 3 (total R$ 43.500,62; Agressiva 1 R$ 11.137,10; Agressiva 2 R$ 10.981,15; Conservadora 1 R$ 11.003,58; Conservadora 2 R$ 10.378,79), com `kairi_carteira_2026.py` intocado. Asserts: caixa nunca negativo; nenhuma compra no dia do sinal; nenhum dado ou documento do futuro ({len(uso_fnet)} usos de documentos do FNET, todos de 2025 em diante); decomposição fecha em todas as rodadas; operações de 2018 e 2019 refeitas à mão.
**Interpretação.** "Um ano de cada vez" = carteira vazia no 1º pregão, sinais só a partir desse dia (sinal de dezembro do ano anterior não vale); a saída que cairia depois do último pregão do ano vira posição aberta a preço de fechamento; "ganhou do CDI" = retorno líquido do ano pelo menos 0,05 ponto acima do CDI; média dos anos simples; "mercado" = índice de mercado.csv. Que a regra repita o desempenho em outro ano é dedução, não está provado.
"""
OUT_MD.write_text(md, encoding="utf-8")
print(f"\nescrito {OUT_MD}")


# ================================================================ PLANILHA EXCEL
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.axis import DateAxis
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

COR = {"Agressiva 1": "D55E00", "Agressiva 2": "E69F00", "Conservadora 1": "0072B2", "Conservadora 2": "56B4E9", "tot": "222222", "cdi": "009E73", "merc": "9A9A9A"}
F_BRL, F_PCT, F_DATA = '"R$" #,##0.00', '0.0%', 'dd/mm/yyyy'
HDR_FILL, HDR_FONT, THIN = PatternFill("solid", fgColor="E8EEF4"), Font(bold=True, color="1B2733"), Side(style="thin", color="C9D1D9")
BORDA = Border(bottom=THIN)
wb = Workbook()


def cab(ws, row, titulos, larg=None):
    for j, t in enumerate(titulos, 1):
        c = ws.cell(row=row, column=j, value=t)
        c.font, c.fill, c.border = HDR_FONT, HDR_FILL, BORDA
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if larg:
        for j, w in enumerate(larg, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[row].height = 46


def eixos(ch, xt, yt, yfmt, xfmt=None):
    ch.x_axis.title, ch.y_axis.title = xt, yt
    ch.y_axis.number_format = yfmt
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.tickLblPos = "low"                 # rotulos do eixo no pe do grafico (nao no meio das barras negativas)
    ch.legend.position = "b"
    if xfmt:
        ch.x_axis.number_format = xfmt


def estilo_linha(s, cor, tracejada=False):
    s.smooth = False
    s.marker.symbol = "none"
    s.graphicalProperties.line.solidFill = cor
    s.graphicalProperties.line.width = 22000
    if tracejada:
        s.graphicalProperties.line.dashStyle = "dash"


def ajusta_pagina(ws):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# ------------------------------------------------ Ano a ano
ws = wb.active
ws.title = "Ano a ano"
ws["A1"] = "Kairi versão 3, um ano de cada vez: retorno líquido (R$ 10 mil por sub-carteira no 1º pregão do ano; posições abertas a preço do último pregão)"
ws["A1"].font = Font(bold=True, size=12)
cab(ws, 3, ["Ano", *NOMES, "Total (R$ 40 mil)", "105% do CDI", "Mercado", "Total contra o CDI (pontos)", "Operações fechadas (total)", "Operações abertas no fim (total)", "Dinheiro parado, % médio (total)",
            "Patrimônio final do total (R$)", "Patrimônio final do CDI (R$)"], [26, 14, 14, 15, 15, 14, 13, 12, 14, 13, 13, 14, 15, 15])
for i, a_ in enumerate(ANOS):
    M_ = YR[a_]["M"]
    r = 4 + i
    vals = [ROT_ANO[a_] if a_ < 2026 else "2026 (até 09/11)"] + [M_[n]["ret_liq"] for n in NOMES] + [M_["Total"]["ret_liq"], M_["CDI"]["ret_liq"], M_["Mercado"]["ret_liq"],
            100 * (M_["Total"]["ret_liq"] - M_["CDI"]["ret_liq"]), M_["Total"]["n_fe"], M_["Total"]["n_ab"], M_["Total"]["parado_pct"], M_["Total"]["p_fim"], M_["CDI"]["p_fim"]]
    for j, v in enumerate(vals, 1):
        c = ws.cell(row=r, column=j, value=v)
        c.number_format = F_PCT if 2 <= j <= 8 or j == 12 else '0.0' if j == 9 else F_BRL if j >= 13 else "0"
R0, R1 = 4, 3 + len(ANOS)


def graf_barras(ws, titulo, cols, cores, anchor, ytit="Retorno líquido no ano"):
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "col", titulo, 10, 26
    for c_ in cols:
        ch.add_data(Reference(ws, min_col=c_, min_row=3, max_row=R1), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=R0, max_row=R1))
    eixos(ch, "Ano", ytit, '0%')
    for s_, cor in zip(ch.series, cores):
        s_.graphicalProperties.solidFill = cor
        s_.invertIfNegative = False
    ch.gapWidth = 60
    ws.add_chart(ch, anchor)


graf_barras(ws, "Retorno líquido por ano: total (R$ 40 mil) e 105% do CDI", [6, 7], [COR["tot"], COR["cdi"]], "A15")
graf_barras(ws, "Retorno líquido por ano: as 4 sub-carteiras", [2, 3, 4, 5], [COR[n] for n in NOMES], "A37")
ws.freeze_panes = "B4"
ajusta_pagina(ws)
ws.page_setup.fitToHeight = 1

# ------------------------------------------------ Contínua
wd = wb.create_sheet("Contínua")
wd["A1"] = "Kairi versão 3, contínua de 02/01/2018 a 09/11/2026 (R$ 10 mil por sub-carteira, sem zerar a cada ano): patrimônio no fechamento de cada dia"
wd["A1"].font = Font(bold=True, size=12)
HR = 27
cab(wd, HR, ["Data", *NOMES, "105% do CDI (R$ 10 mil)", "Total (R$ 40 mil)", "105% do CDI (R$ 40 mil)", "Mercado (R$ 40 mil)"], [12, 15, 15, 15, 15, 17, 16, 17, 16])
NDIA = NM - JA
for i in range(NDIA):
    wd.cell(row=HR + 1 + i, column=1, value=TS[JA + i].to_pydatetime()).number_format = F_DATA
    for j, v in enumerate([CT["RES"][n]["pat"][i] for n in NOMES] + [CT["cdi10"][i], CT["pat_total"][i], CT["cdi40"][i], CT["merc40"][i]], 2):
        wd.cell(row=HR + 1 + i, column=j, value=float(v)).number_format = F_BRL
wd.freeze_panes = f"B{HR + 1}"
nr = HR + NDIA
ch = LineChart()
ch.title = "Patrimônio de cada sub-carteira (R$ 10 mil, contínua 2018–2026) contra 105% do CDI"
ch.height, ch.width = 11.5, 28
for col in range(2, 7):
    ch.add_data(Reference(wd, min_col=col, min_row=HR, max_row=nr), titles_from_data=True)
ch.x_axis = DateAxis(crossAx=100)
ch.y_axis.crossAx = 500
ch.x_axis.majorTimeUnit = "years"
ch.x_axis.majorUnit = 1
eixos(ch, "Data", "Patrimônio (R$)", '"R$" #,##0', "mmm/yy")
ch.set_categories(Reference(wd, min_col=1, min_row=HR + 1, max_row=nr))
for s_, cor, dash in zip(ch.series, [COR[n] for n in NOMES] + [COR["cdi"]], [False] * 4 + [True]):
    estilo_linha(s_, cor, dash)
wd.add_chart(ch, "A3")
ajusta_pagina(wd)

# ------------------------------------------------ Operacoes fechadas (todas)
wo = wb.create_sheet("Operações fechadas")
wo["A1"] = "Operações fechadas: as 9 rodadas de um ano e a contínua (coluna Rodada). Resultado = venda − compra + rendimentos recebidos − taxas."
wo["A1"].font = Font(bold=True, size=12)
T_OPS = ["Rodada", "Sub-carteira", "Fundo", "Tipo", "Sinal", "Entrada", "Preço de entrada (R$)", "Cotas", "Valor de entrada (R$)", "Saída", "Preço de saída (R$)", "Valor de saída (R$)", "Motivo da saída",
         "Dias", "Maior queda (% da entrada)", "Data da maior queda", "Maior alta (% da entrada)", "Data da maior alta", "Rendimentos recebidos (R$)", "Taxas (R$)", "Resultado (R$)", "Resultado (%)"]
cab(wo, 3, T_OPS, [11, 15, 9, 14, 11, 11, 11, 7, 12, 11, 11, 12, 28, 7, 11, 12, 11, 12, 12, 9, 12, 10])
fech_all = pd.concat([OPS_ANOS, OPS_CONT], ignore_index=True)
fech_all = fech_all[fech_all["status"] == "Fechada"].reset_index(drop=True)
FORM_OPS = [None, None, None, None, F_DATA, F_DATA, F_BRL, "0", F_BRL, F_DATA, F_BRL, F_BRL, None, "0", F_PCT, F_DATA, F_PCT, F_DATA, F_BRL, F_BRL, F_BRL, F_PCT]


def nat(x):
    return None if (x is None or (not isinstance(x, (list, tuple)) and pd.isna(x))) else (x.to_pydatetime() if isinstance(x, pd.Timestamp) else (float(x) if isinstance(x, (np.floating,)) else (int(x) if isinstance(x, np.integer) else x)))


for i, r_ in fech_all.iterrows():
    vals = [r_["rodada"], r_["carteira"], r_["fundo"], r_["tipo"], r_["sinal"], r_["entrada"], r_["preco_entrada"], r_["cotas"], r_["valor_compra"], r_["saida"], r_["preco_saida"],
            r_["valor_saida"], r_["motivo"], r_["dias"], r_["queda_max"], r_["queda_data"], r_["alta_max"], r_["alta_data"], r_["rend"], r_["taxas"], r_["resultado"], r_["resultado_pct"]]
    for j, v in enumerate(vals, 1):
        c = wo.cell(row=4 + i, column=j, value=nat(v))
        if FORM_OPS[j - 1]:
            c.number_format = FORM_OPS[j - 1]
wo.freeze_panes = "D4"
wo.auto_filter.ref = f"A3:{get_column_letter(len(T_OPS))}{3 + len(fech_all)}"

# ------------------------------------------------ Posicoes abertas no fim de cada ano
wp = wb.create_sheet("Posições abertas no fim do ano")
wp["A1"] = "Posições abertas no último pregão de cada rodada (valor a preço do último fechamento; não é venda). Contínua = 09/11/2026."
wp["A1"].font = Font(bold=True, size=12)
T_AB = ["Rodada", "Sub-carteira", "Fundo", "Sinal", "Entrada", "Preço de entrada (R$)", "Cotas", "Valor de entrada (R$)", "Último preço (R$)", "Data do último preço", "Valor atual (R$)",
        "Rendimentos pagos (R$)", "Rendimentos a receber (R$)", "Resultado (R$)", "Resultado (%)", "Maior queda até o fim (%)", "Data", "Maior alta até o fim (%)", "Data"]
cab(wp, 3, T_AB, [11, 15, 9, 11, 11, 11, 7, 12, 11, 12, 12, 12, 12, 12, 10, 12, 11, 12, 11])
linhas_ab = []
for rot, run in [(str(a_), YR[a_]) for a_ in ANOS] + [("Contínua", CT)]:
    for n in NOMES:
        o = run["RES"][n]["o"]
        if not len(o):
            continue
        raw = {(x["fundo"], x["entrada"]): x for x in run["RES"][n]["ops_raw"]}
        for _, r_ in o[o["status"] != "Fechada"].iterrows():
            x = raw[(r_["fundo"], r_["entrada"])]
            linhas_ab.append([rot, n, r_["fundo"], r_["sinal"], r_["entrada"], r_["preco_entrada"], r_["cotas"], r_["valor_compra"], r_["preco_saida"], pd.Timestamp(x["F"]["dates"][x["rr"]]),
                              r_["valor_saida"], r_["rend"], r_["rend_a_receber"], r_["resultado"], r_["resultado_pct"], r_["queda_max"], r_["queda_data"], r_["alta_max"], r_["alta_data"]])
FORM_AB = [None, None, None, F_DATA, F_DATA, F_BRL, "0", F_BRL, F_BRL, F_DATA, F_BRL, F_BRL, F_BRL, F_BRL, F_PCT, F_PCT, F_DATA, F_PCT, F_DATA]
for i, l in enumerate(linhas_ab):
    for j, v in enumerate(l, 1):
        c = wp.cell(row=4 + i, column=j, value=nat(v))
        if FORM_AB[j - 1]:
            c.number_format = FORM_AB[j - 1]
wp.freeze_panes = "D4"
wp.auto_filter.ref = f"A3:{get_column_letter(len(T_AB))}{3 + len(linhas_ab)}"
assert len(linhas_ab) == nab_anos + CT["M"]["Total"]["n_ab"]

# ------------------------------------------------ Legenda
wl = wb.create_sheet("Legenda")
wl.column_dimensions["A"].width = 34
wl.column_dimensions["B"].width = 140
LEG = [("Regras", "Versão 3 do Kairi: 4 sub-carteiras de R$ 10.000, ordem de R$ 1.000; gatilho 15% (Agressivas) ou 20% (Conservadoras) abaixo da média de 200 pregões, rendimento mantido; faixa pela mediana do volume diário de 60 pregões (R$ 100–200 mil, 200–500 mil, 500 mil–1 mi, acima de 1 mi, valores nominais); venda no fechamento acima da média de 200 pregões ou em 252 pregões; caixa em 105% do CDI com IR/IOF por lote; imposto do FII; taxa 0,03%."),
       ("FNET", "Documentos do FNET (regras b, c e parte da regra 1) só de 01/05/2025 em diante e só de 43 fundos; antes disso só fatos relevantes."),
       ("Ano a ano", "Cada ano começa com R$ 10 mil por sub-carteira no 1º pregão e termina no último pregão do ano; posições abertas valem o último preço (aba Posições abertas). 2026 = versão 3, até 09/11/2026."),
       ("Contínua", "02/01/2018 a 09/11/2026 sem zerar. Patrimônio dia a dia = caixa líquido de IR/IOF + cotas × fechamento − DARF vencido e não pago."),
       ("Retorno líquido", "(patrimônio final − imposto do FII a vencer − imposto se vendesse tudo) ÷ capital − 1."),
       ("Contra o CDI", "retorno do total − retorno de 105% do CDI líquido de IR/IOF no mesmo período, em pontos percentuais."),
       ("Mercado", "índice de mercado.csv (planilhas/mercado.csv) no período, aplicado a R$ 40 mil."),
       ("Resultado da operação", "venda − compra + rendimentos recebidos − taxas (0,03% na compra e na venda); % = resultado ÷ valor de entrada."),
       ("Maior queda / maior alta", "menor e maior fechamento depois da entrada em % do preço de entrada (0% se nunca passou do preço de entrada)."),
       ("Gráficos", "Os rótulos dos eixos ficam na base (tickLblPos = low).")]
for i, (a_, b_) in enumerate(LEG, 1):
    wl.cell(row=i, column=1, value=a_).font = Font(bold=True)
    wl.cell(row=i, column=2, value=b_).alignment = Alignment(wrap_text=True, vertical="top")
wb.save(SAIDA_XLSX)
print(f"escrito {SAIDA_XLSX}; fechadas na aba: {len(fech_all)}; abertas: {len(linhas_ab)}")
print(f"tempo total: {time.time() - T0:.1f} s")
