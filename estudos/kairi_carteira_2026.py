"""Simulacao do Kairi em 2026 (VERSAO 3, 2026-11-17): quatro sub-carteiras de R$ 10.000 cada, de 02/01/2026 (1o pregao do ano) a 09/11/2026,
ordem de R$ 1.000 (so essa), com regras novas decididas pelo dono.

Sub-carteiras (gatilho = cota fecha X abaixo da media de 200 pregoes, rendimento mantido; filtro de negociacao = MEDIANA do volume diario
(volume_dia (R$)) dos 60 pregoes ate o dia do sinal, inclusive; faixas [100k,200k), [200k,500k), [500k,1M), [1M,inf)):
    Agressiva 1: 15%, mediana de R$ 100 mil a R$ 200 mil.      Agressiva 2: 15%, mediana de R$ 200 mil a R$ 500 mil.
    Conservadora 1: 20%, mediana de R$ 500 mil a R$ 1 milhao.  Conservadora 2: 20%, mediana acima de R$ 1 milhao.
    (O dono escreveu "100 mil" para o capital da Agressiva 2; tratamos como R$ 10 mil, igual as outras.)
Mantidos: media de 200 pregoes, rendimento mantido, universo e guarda de dados, um fundo por vez por sub-carteira, prioridade por volume
(maior mediana primeiro), caixa parado em 105% do CDI em lotes (IR/IOF), imposto do FII, taxas de 0,03%, regra 1 de bloqueio de fundo que
vai sair da bolsa (versao 2, com as correcoes de propostas reprovadas).

Mudancas da versao 3:
  a) VENDA no FECHAMENTO do primeiro dia em que o fechamento fica >= media de 200 pregoes (media ate o dia anterior); prazo de 252 pregoes.
  b) RENDIMENTO ZERO: comunicado do FNET de que "nao havera distribuicao de rendimentos" nos 126 pregoes ate o sinal corta o rendimento (sem compra).
  c) SAIDA ANTECIPADA: com a posicao aberta, documento do FNET sobre liquidacao/incorporacao/fusao/cisao/venda de todos os ativos/tombamento
     para o balcao/deslistagem, ou comunicado de rendimento zero, vende na abertura do pregao seguinte a data de entrega. A regra 1 de bloqueio
     na entrada tambem usa esses documentos (alem dos fatos relevantes), com tombamento/balcao.
Documentos do FNET so dos fundos que deram sinal em 2026 (gatilho 15% ou 20%, antes do filtro de volume), de 01/05/2025 a 13/11/2026, nas
categorias Comunicado ao Mercado, Fato Relevante, Assembleia e Aviso aos Cotistas (estruturado/XML de rendimentos fora). A coleta esta em
estudos/kairi_fnet_2026.py; a lista e os textos (5.000 caracteres) ficam em planilhas/tecnico/fnet_2026_documentos.csv.gz.
Se o FNET falhar de vez, o programa roda sem b/c e diz isso (FNET_OK = False).

Rodar com:
    cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/kairi_carteira_2026.py
Saidas: planilhas/kairi_carteira_2026.xlsx, planilhas/tecnico/fnet_2026_documentos.csv.gz e docs/SIMULACAO_KAIRI_2026.md (gerados a cada rodada).
Imagens de conferencia (fora do repositorio): soffice --headless --convert-to pdf ... ; pdftoppm -r 70 -png ...
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



# Documentos do FNET (editais, cartas consulta, propostas, atas) trazem muito texto padrao do regulamento ("transformacao ou liquidacao do
# Fundo", "para processar a liquidacao do Fundo" na troca de administrador, "hipoteses de liquidacao"...). Esse texto nao e proposta: se a
# expressao de saida aparece colada a ele, e ignorada. As que sobram foram lidas uma a uma (ver conferencia impressa).
BOIL = re.compile(r"transformacao[\s,]+(?:\w+[\s,]+){0,3}?ou\s+liquidacao|transformacao,?\s+fusao|(?:fusao|incorporacao|cisao)[\s,]+(?:\w+[\s,]+){0,5}?liquidacao|"
                  r"processar a liquidacao|renuncia|destituicao|prestador(?:es)? de servicos? essenc|liquidacao extrajudicial|hipoteses? de liquidacao|"
                  r"despesas (?:com|de) liquidacao|eventos? de liquidacao|em caso de liquidacao|no caso de liquidacao|quando da liquidacao|permanecer no exercicio|"
                  r"liquidacao (?:financeira|e custodia)|liquidacao de (?:ordens|operacoes)|autorizada a liquidar|ainda que apos|se assim determinad|devendo tal liquidacao|"
                  r"(?:ate|apos) (?:a|o) (?:liquidacao|encerramento) d[oa]|termino do prazo de duracao|liquidacao antecipada do fundo|liquidar o fundo perante|"
                  r"liquidacao automatica|sem necessidade de aprovacao|cessar suas operacoes|alternativa realista|valores em caixa, detidos")


def casa_saida_doc(texto):
    t = _unacc(str(texto).lower())
    cands = sorted((m.start(), m.end(), nome_) for nome_, rx in _RX for m in rx.finditer(t))
    neg = None
    for a, b, nome_ in cands:
        if BOIL.search(t[max(0, a - 200):b + 200]):
            continue
        if _NEG.search(t[max(0, a - 140):b + 60]):
            neg = neg or (nome_, a, b, True)
            continue
        return nome_, a, b, False
    return neg

# ---------------------------------------------------------------- rendimento zero (versao 3): comunicado de que nao havera distribuicao
_W = r"\W+(?:\w+\W+){0,%d}?"
PADROES_SEM_REND = [
    ("não haverá distribuição de rendimentos", _P(r"nao haver[ai]\W+(?:\w+\W+){0,6}?distribuicao\W+(?:\w+\W+){0,4}?(rendimentos?|resultados?|proventos?)")),
    ("não serão distribuídos rendimentos", _P(r"nao (?:ha|havera|serao|sera)\W+(?:\w+\W+){0,3}?(?:distribuid[oa]s?|pagos?)\W+(?:\w+\W+){0,3}?(rendimentos?|resultados?|proventos?)|nao (?:serao|sera) (?:realizad[oa]s?|efetuad[oa]s?) (?:distribuicoes|distribuicao)")),
    ("fundo não distribuirá rendimentos", _P(r"(?:fundo )?nao (?:distribuira|pagara|efetuara|realizara)\W+(?:\w+\W+){0,6}?(rendimentos?|resultados?|proventos?|distribuicao)")),
    ("sem distribuição de rendimentos", _P(r"(?:sem|ausencia de|inexistencia de|suspensao d[ao]s?|suspendera a|suspender a) distribuicao\W+(?:\w+\W+){0,3}?(rendimentos?|resultados?|proventos?)|nao (?:ha|havera|houve) (?:rendimentos?|resultados?|proventos?) (?:a|para) (?:serem )?distribui|nao (?:ha|havera) (?:saldo|caixa|resultado) (?:a|para) (?:ser )?distribui")),
]
_RXS = [(n, re.compile(p_)) for n, p_ in PADROES_SEM_REND]
_FUT = re.compile(r"extraordinari|complementar|adicional|amortizac")        # "nao havera distribuicao extraordinaria/adicional" nao e corte


def casa_sem_rend(texto):
    t = _unacc(str(texto).lower())
    for nome_, rx in _RXS:
        for m in rx.finditer(t):
            ctx = t[max(0, m.start() - 80):m.end() + 80]
            if _FUT.search(t[max(0, m.start() - 20):m.end() + 40]):
                continue
            return nome_, m.start(), m.end()
    return None


# ================================================================ SINAIS DE 2026 (qualquer faixa) E FUNDOS QUE PRECISAM DE DOCUMENTOS DO FNET
SIG_FUNDOS = {}
for X in GATILHOS:
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if md >= J0 and md + 1 < NM:
                SIG_FUNDOS.setdefault(F["nome"], []).append((X, md, float(F["VMED"][s])))
print(f"sinais de 2026 (gatilhos 15% e 20%, antes do filtro de volume): {sum(len(v) for v in SIG_FUNDOS.values())} em {len(SIG_FUNDOS)} fundos")

# CNPJ de cada fundo com sinal: tirado do texto dos fatos (planilhas/tecnico/fatos_textos.csv.gz) e CONFERIDO no proprio FNET:
# a lista de documentos pedida por esse CNPJ tem de devolver o mesmo nome de pregao de planilhas/fundos.csv. CRFF11, FIIP11, INLG11 e
# TRBL11 nao tem fato nessa planilha: o CNPJ veio do nome do arquivo baixado do FNET (e conferido do mesmo jeito). APXM11: o FNET hoje
# chama o fundo de "FII VIML VIN" (nome mudou); o CNPJ e o do cabecalho dos fatos do APXM11.
CNPJS = {"ABCP11": "01201140000190", "APXM11": "43010485000107", "BCRI11": "22219335000138", "BRCR11": "08924783000101", "CRFF11": "31887401000139", "FIIP11": "08696175000197", "FVPQ11": "00332266000131", "GGRC11": "26614291000100", "HABT11": "30578417000105", "HCHG11": "34508959000154", "HSLG11": "32903621000171", "HSML11": "32892018000131", "INLG11": "34598181000111", "ITIP11": "36312772000106", "ITIT11": "36293425000183", "KIVO11": "42273325000198", "LIFE11": "39753295000102", "MAXR11": "11274415000170", "MCEM11": "46157247000117", "OUJP11": "26091656000150", "PATC11": "30048651000112", "RBHG11": "30647758000187", "RBHY11": "37899479000150", "RBRL11": "35705463000133", "RBRP11": "21408063000151", "RBRR11": "29467977000103", "RBRS11": "36517660000191", "RBRX11": "41088458000121", "RBVA11": "15576907000170", "RECM11": "56430935000162", "RECT11": "32274163000159", "RPRI11": "42502842000191", "TGAR11": "25032881000153", "TRBL11": "16671412000193", "TRXY11": "43985938000110", "VCJR11": "32400250000105", "VCRR11": "40041723000153", "VGHF11": "36771692000119", "VGRI11": "53656482000107", "VINO11": "12516185000170", "VRTA11": "11664201000100", "VVCR11": "23120027000113", "XPIN11": "28516325000140"}
assert set(SIG_FUNDOS) <= set(CNPJS), ("fundo com sinal sem CNPJ", set(SIG_FUNDOS) - set(CNPJS))
FNET_OK = True
FNET_ERRO = ""
t_fnet = time.time()
try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import kairi_fnet_2026 as KF
    DOCS_BRUTOS = KF.coletar({f: CNPJS[f] for f in sorted(SIG_FUNDOS)})
    assert not KF.LOG["erros"], KF.LOG["erros"][:3]
except Exception as e:  # noqa: BLE001  FNET falhou de vez: roda sem as regras b/c e diz isso
    FNET_OK, FNET_ERRO = False, f"{type(e).__name__}: {e}"
    DOCS_BRUTOS = []
    print("FNET FALHOU:", FNET_ERRO)
print(f"FNET: {len(DOCS_BRUTOS)} documentos (Comunicado ao Mercado, Fato Relevante, Assembleia, Aviso aos Cotistas) de {len(SIG_FUNDOS)} fundos, "
      f"{time.time() - t_fnet:.0f} s nesta rodada (textos ja baixados ficam em {os.environ.get('KAIRI_FNET_TXT', '/tmp/kairi_fnet_txt')})")

# Leitura manual: documentos que as expressoes pegaram mas que NAO tratam de saida do proprio fundo (lidos um a um; o trecho foi conferido).
LIDO_NAO_SAIDA = {
    1325373: "apresentação da administradora com casos de OUTROS fundos (o item 'Liquidação do Fundo' é de um caso passado)",
    895085: "texto padrão do regulamento (poderes dos cotistas / representante), não é proposta",
    922337: "texto padrão do regulamento (poderes dos cotistas / representante), não é proposta",
    1017602: "texto padrão (troca de administrador: 'ou deliberar pela liquidação do Fundo' é regra do regulamento)",
    1074439: "texto padrão (troca de administrador: 'ou deliberar pela liquidação do Fundo' é regra do regulamento)",
    1343531: "tabela de quóruns do regulamento, não é proposta",
    1126869: "lista de competências da assembleia (texto do regulamento), não é proposta",
    916966: "lista de competências da assembleia (texto do regulamento), não é proposta",
    929012: "lista de competências da assembleia (texto do regulamento), não é proposta",
    1221870: "texto do regulamento (administrador/liquidação), não é proposta",
    1343936: "reorganização com cisão PARCIAL do portfólio: o fundo continua negociando (os ativos de desinvestimento ficam no próprio fundo)",
}
DOCS = pd.DataFrame(DOCS_BRUTOS)
DOC_HITS, DOC_SEM_REND = [], []
if len(DOCS):
    DOCS["dia"] = pd.to_datetime(DOCS["entrega"].str[:10], format="%d/%m/%Y")
    assert DOCS["dia"].between(FNET_INI, FNET_FIM).all(), "documento fora do periodo pedido"
    DOCS["id"] = DOCS["id"].astype(int)
    DOCS = DOCS.drop_duplicates("id").sort_values(["fundo", "dia", "id"]).reset_index(drop=True)
    cls, pad, trc = [], [], []
    for r_ in DOCS.itertuples():
        c_, p_, tr_ = "", "", ""
        if r_.situacao_doc != "C" and r_.leitura == "ok":              # 'C' = documento cancelado no FNET: nao conta
            tx = r_.texto_completo
            h = casa_saida_doc(tx)
            if int(r_.id) in LIDO_NAO_SAIDA:
                h = None
            sr = casa_sem_rend(tx)
            if h is not None and not h[3]:
                c_, p_ = "saída", h[0]
                tr_ = re.sub(r"\s+", " ", tx[max(0, h[1] - 120):h[2] + 140]).strip()
            elif sr is not None:
                c_, p_ = "sem rendimento", sr[0]
                tr_ = re.sub(r"\s+", " ", tx[max(0, sr[1] - 120):sr[2] + 140]).strip()
            elif h is not None and h[3]:
                c_, p_ = "reprovação", h[0]
                tr_ = re.sub(r"\s+", " ", tx[max(0, h[1] - 120):h[2] + 140]).strip()
        cls.append(c_)
        pad.append(p_)
        trc.append(tr_)
    DOCS["classe"], DOCS["padrao"], DOCS["trecho"] = cls, pad, trc
    DOCS["leitura_manual"] = DOCS["id"].map(LIDO_NAO_SAIDA).fillna("")
    # um documento que casa saida E sem rendimento: guarda os dois (a saida manda; o corte de rendimento tambem e conferido)
    DOCS["sem_rend_trecho"] = ""
    DOCS["sem_rend_padrao"] = ""
    for i_, r_ in DOCS.iterrows():
        if r_["leitura"] == "ok" and r_["situacao_doc"] != "C":
            sr = casa_sem_rend(r_["texto_completo"])
            if sr is not None:
                DOCS.at[i_, "sem_rend_padrao"] = sr[0]
                DOCS.at[i_, "sem_rend_trecho"] = re.sub(r"\s+", " ", r_["texto_completo"][max(0, sr[1] - 120):sr[2] + 140]).strip()
    out = DOCS.assign(**{"data de entrega": DOCS["entrega"], "texto (primeiros 5.000 caracteres)": DOCS["texto_completo"].str[:5000]})
    out = out[["id", "fundo", "cnpj", "data de entrega", "categoria", "tipo", "especie", "situacao_doc", "versao", "formato", "leitura", "classe", "padrao",
               "trecho", "sem_rend_padrao", "sem_rend_trecho", "leitura_manual", "texto (primeiros 5.000 caracteres)"]]
    out.to_csv(CACHE_FNET, sep=";", index=False, encoding="utf-8-sig", compression="gzip")
    print(f"documentos e textos salvos em {CACHE_FNET} ({len(out)} linhas); leitura: {DOCS['leitura'].value_counts().to_dict()}; "
          f"cancelados no FNET (ignorados): {int((DOCS['situacao_doc'] == 'C').sum())}")
    print("classificacao dos documentos:", DOCS["classe"].replace("", "nenhuma").value_counts().to_dict(),
          "| com expressao de rendimento zero:", int((DOCS["sem_rend_padrao"] != "").sum()))

# listas por fundo
EXD = {}            # saida antecipada: documentos de saida ou de rendimento zero (nao cancelados), por fundo, em ordem de data
CORTE = {}          # fundo -> dias (datetime64) de documentos de rendimento zero
for r_ in DOCS.itertuples() if len(DOCS) else []:
    if r_.classe == "saída":
        EXD.setdefault(r_.fundo, []).append(dict(id=int(r_.id), dia=np.datetime64(r_.dia, "D"), tipo="saída da bolsa/liquidação etc.", padrao=r_.padrao,
                                                 trecho=r_.trecho, doc=f"{r_.categoria} / {r_.especie}"))
    if r_.sem_rend_padrao:
        EXD.setdefault(r_.fundo, []).append(dict(id=int(r_.id), dia=np.datetime64(r_.dia, "D"), tipo="rendimento zero", padrao=r_.sem_rend_padrao,
                                                 trecho=r_.sem_rend_trecho, doc=f"{r_.categoria} / {r_.especie}"))
        CORTE.setdefault(r_.fundo, []).append(EXD[r_.fundo][-1])
for _v in EXD.values():
    _v.sort(key=lambda x: (x["dia"], x["id"]))

# regra 1 tambem com os documentos do FNET: entram na mesma lista de fatos de saida (bloqueiam; reprovacao anula os anteriores)
for r_ in DOCS.itertuples() if len(DOCS) else []:
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


# ================================================================ CANDIDATOS (sinais de 2026) E SAIDA
ASSERT_USO = []        # (o que, fundo, data do documento, data em que foi usado)
# candidatos por pregao de execucao; so sinais com data >= 02/01/2026 (carteira comeca vazia).
CAND = {}
for X in GATILHOS:
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais(F, X)):
            md = int(F["mi"][s])
            if md >= J0 and md + 1 < NM:
                d_sin = pd.Timestamp(MD[md])
                bl = bloqueio(F["nome"], MD[md])
                d_ini = F["dates"][s - LAG_REND]                                  # inicio dos 126 pregoes do fundo ate o sinal
                cut = corte_rendimento(F["nome"], MD[md], d_ini) if FNET_OK else []
                for b_ in bl:
                    ASSERT_USO.append(("bloqueio", F["nome"], b_["dia"], MD[md]))
                for c_ in cut:
                    ASSERT_USO.append(("rendimento zero", F["nome"], c_["dia"], MD[md]))
                lst[md + 1].append(dict(F=F, s=int(s), md=md, vol=float(F["VMED"][s]), vol_media=float(F["VOL"][s]), bloq=bl, cut=cut, d_ini=d_ini))
    CAND[X] = lst


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


def saida_antecipada(F, nm, sinal_dia, mi_entrada, k_nat, mot_nat, dia_ult=None):
    """Documento do FNET publicado DEPOIS do dia do sinal (os de ate o dia do sinal ja foram usados na entrada) que manda vender na abertura do
    pregao seguinte: liquidacao/dissolucao/encerramento, incorporacao, fusao, cisao, venda da totalidade dos ativos, tombamento/balcao/deslistagem,
    ou comunicado de que nao havera distribuicao de rendimentos. Vale o primeiro que cair antes da saida normal (a venda e na abertura; a
    saida normal, no fechamento: no mesmo dia a antecipada vem antes). Devolve (k, doc) ou (None, alerta)."""
    alerta = None
    for d in EXD.get(nm, []):
        if d["dia"] <= np.datetime64(sinal_dia, "D"):
            continue
        mt = max(int(np.searchsorted(MD, d["dia"], "right")), mi_entrada + 1)     # 1o pregao depois da publicacao (e depois da compra)
        if mt >= NM:
            alerta = dict(d, motivo="publicado perto do fim: a venda seria depois de 09/11/2026 (fora da simulação)")
            continue
        rt = int(np.searchsorted(F["dates"], MD[mt], "left"))
        while rt < F["n"] and not (F["NEG"][rt] == 1 and np.isfinite(F["A"][rt]) and F["A"][rt] > 0):
            rt += 1
        if rt >= F["n"]:
            alerta = dict(d, motivo="o fundo não tem mais preço depois da publicação (não dá para vender)")
            continue
        if F["dates"][rt] <= F["dates"][k_nat]:
            assert d["dia"] < F["dates"][rt], "documento nao e anterior a venda"
            ASSERT_USO.append(("saida antecipada", nm, d["dia"], F["dates"][rt]))
            return rt, d
        return None, alerta
    return None, alerta


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


def serie_cdi(V, mi0):
    return np.array([lote_liq(mi0, V, mi, MD[mi])[0] for mi in range(mi0, NM)])


def imposto_mes(ganho_mes, pool):
    if ganho_mes >= 0:
        usa = min(pool, ganho_mes)
        base = ganho_mes - usa
        return IR_OP * base, pool - usa
    return 0.0, pool - ganho_mes


# ---------------------------------------------------------------- simulacao de uma sub-carteira
def simular(nome, X, lo, hi, ordem=ORDEM):
    """Sub-carteira de R$ 10.000: gatilho X, mediana de 60 pregoes do volume diario em [lo, hi)."""
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
        # 2. vendas na ABERTURA de hoje (saida antecipada por documento): o dinheiro vira um lote novo
        vender(mi, t, "abertura")
        # 3. entradas: sinais do pregao anterior, na abertura de hoje; maior mediana de volume primeiro
        for c in sorted([c for c in cands[mi] if lo <= c["vol"] < hi], key=lambda c: (-c["vol"], c["F"]["nome"])):
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
            if FNET_OK:
                kee, d_ee = saida_antecipada(F, nm, MD[c["md"]], mi, k, mot)
                if kee is not None:
                    k, mot, pxs, quando, doc = kee, "saída antecipada (aviso do FNET)", float(F["A"][kee]), "abertura", d_ee
                elif d_ee is not None:
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
                if mpay >= NM:
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
        rr = int(np.searchsorted(F["dates"], MD[NM - 1], "right") - 1)
        assert P["mot"] == ABERTO, (nome, nm, P["mot"])
        op.update(saida=pd.NaT, preco_saida=float(F["C"][rr]), status="Em aberto", rr=rr)
    gh = 0.0
    for nm, P in pos.items():
        op = P["op"]
        vv = P["cotas"] * op["preco_saida"]
        gh += (vv - B3 * vv) - (op["valor_compra"] + op["taxa_compra"])
    ym_f = (TS[-1].year, TS[-1].month)
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
    rend_cx = cx.rendimento_liquido(NM - 1, MD[NM - 1])
    return dict(nome=nome, X=X, lo=lo, hi=hi, ordem=ordem, dia=dia, ops=pd.DataFrame([{k: v for k, v in o.items() if k not in ("F", "doc")} for o in ops]),
                ops_raw=ops, sinais=pd.DataFrame(sinais_log), rend=pd.DataFrame(rend_log), darf=pd.DataFrame(darf_pagos),
                devidos=pd.DataFrame(devidos), caixa=cx, pos=pos, ganhos=ganhos, imp_hipotetico=tot_hip - tot_real,
                ganho_hipotetico=gh, darf_a_pagar=a_pagar, pend=pend, rend_cx=rend_cx, alertas=alertas)


print(f"base: {NM} pregoes ({TS[0].date()} a {TS[-1].date()}); carteira de 02/01/2026 a {TS[-1].date()} ({NM - J0} pregoes); fundos com precos: {len(FD)}")
for X in GATILHOS:
    print(f"  sinais (data >= 02/01/2026) com gatilho {int(X * 100)}%: {sum(len(x) for x in CAND[X])}")
RES = {nome: simular(nome, X, lo, hi) for nome, (X, lo, hi) in SUBS.items()}
print(f"simulacoes rodadas: {len(RES)} sub-carteiras; tempo: {time.time() - T0:.1f} s")


# ================================================================ PARTE 2: numeros, conferencias
NOMES = list(SUBS)
DATAS = TS[J0:]
NDIA = len(DATAS)
DIAS_CORR = (TS[-1] - TS[J0]).days
N_SUB = len(NOMES)
CAP_TOT = CAP_SUB * N_SUB
CDI10 = serie_cdi(CAP_SUB, J0)
CDI40 = N_SUB * CDI10
MERC40 = CAP_TOT * IDX[J0:] / IDX[J0]


def extremos(F, e, ultimo, px):
    """Menor e maior fechamento de e a ultimo (inclusive), como % do preco de entrada, com a data. Queda <= 0 e alta >= 0 (so conta o que passou do preco de entrada)."""
    c = F["C"][e:ultimo + 1]
    jm, jM = int(np.argmin(c)), int(np.argmax(c))
    q, a = float(c[jm] / px - 1), float(c[jM] / px - 1)
    return (min(q, 0.0), pd.Timestamp(F["dates"][e + jm]) if q < 0 else pd.NaT,
            max(a, 0.0), pd.Timestamp(F["dates"][e + jM]) if a > 0 else pd.NaT)


COLS_OPS = ["carteira", "gatilho", "ordem", "fundo", "tipo", "sinal", "entrada", "preco_entrada", "cotas", "valor_compra", "taxa_compra", "motivo", "status", "saida", "preco_saida",
            "taxa_venda", "valor_venda", "ganho_trib", "rend_direito", "rend_recebido", "rend_a_receber", "rend_sem_data", "e", "k", "mi_e", "mi_d", "mi_s", "vol", "pretendido", "quando",
            "valorizacao", "taxas", "rend", "resultado", "resultado_pct", "valor_saida", "dias", "queda_max", "queda_data", "alta_max", "alta_data", "rr"]


def prep_ops(R):
    o = R["ops"].copy()
    if o.empty:
        return pd.DataFrame({c: pd.Series(dtype="object" if c in ("carteira", "fundo", "tipo", "motivo", "status", "quando") else "float64") for c in COLS_OPS})
    raw = {(x["fundo"], x["entrada"]): x for x in R["ops_raw"]}
    fech = o["status"] == "Fechada"
    o["valorizacao"] = np.where(fech, o["valor_venda"] - o["valor_compra"], o["cotas"] * o["preco_saida"] - o["valor_compra"])
    o["taxas"] = o["taxa_compra"] + o["taxa_venda"].fillna(0.0)
    o["rend"] = o["rend_recebido"]
    o["resultado"] = o["valorizacao"] + o["rend"] - o["taxas"]
    o["resultado_pct"] = o["resultado"] / o["valor_compra"]
    o["valor_saida"] = np.where(fech, o["valor_venda"], o["cotas"] * o["preco_saida"])
    fim = pd.Series(TS[-1], index=o.index)
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


for R in RES.values():
    R["o"] = prep_ops(R)
    R["pat"] = R["dia"]["patrimonio"].to_numpy()
    R["pos_val"] = R["dia"]["posicoes"].to_numpy()
    R["cx_val"] = R["dia"]["caixa"].to_numpy()


def queda_max(p, base):
    b = np.r_[base, p]
    pico = np.maximum.accumulate(b)[1:]
    dd = p / pico - 1
    j = int(np.argmin(dd))
    ipk = np.flatnonzero(p[:j + 1] == pico[j])
    d_pico = DATAS[ipk[-1]] if ipk.size else TS[J0]
    return float(dd[j]), d_pico, DATAS[j]


def metricas(rs, nome):
    cap = CAP_SUB * len(rs)
    pat = sum(R["pat"] for R in rs)
    pos = sum(R["pos_val"] for R in rs)
    cxv = sum(R["cx_val"] for R in rs)
    o = pd.concat([R["o"] for R in rs], ignore_index=True)
    fech = o[o["status"] == "Fechada"]
    ab = o[o["status"] != "Fechada"]
    pf = float(pat[-1])
    a_pagar = sum(R["darf_a_pagar"] for R in rs)
    hip = sum(R["imp_hipotetico"] for R in rs)
    pliq = pf - a_pagar - hip
    q, dp, df_ = queda_max(pat, cap)
    imp_pago = float(sum(R["darf"]["pago"].sum() for R in rs if len(R["darf"])))
    imp_pend = float(sum(R["pend"] for R in rs))
    frac_parado = cxv / pat
    m = dict(nome=nome, cap=cap, pat=pat, p_ini=cap, p_fim=pf, ret=pf / cap - 1, p_liq=pliq, ret_liq=pliq / cap - 1,
             queda=q, d_pico=dp, d_fundo=df_, n_ab=len(ab), n_fe=len(fech),
             luc_fe=float((fech["resultado"] > 0).mean()) if len(fech) else np.nan, n_luc_fe=int((fech["resultado"] > 0).sum()),
             rend=float(o["rend"].sum()), rend_a_receber=float(o["rend_a_receber"].sum()), rend_sem_data=float(o["rend_sem_data"].sum()),
             imp_pago=imp_pago, imp_pend=imp_pend, imp_a_vencer=float(a_pagar), imp_hip=float(hip),
             ir_iof=float(sum(R["caixa"].ir + R["caixa"].iof for R in rs)), taxas=float(o["taxas"].sum()),
             parado_pct=float(frac_parado.mean()), parado_dias=float(frac_parado.mean() * DIAS_CORR), parado_rs=float(sum(R["rend_cx"] for R in rs)),
             res_fech=float((fech["valorizacao"] + fech["rend"]).sum()), res_ab=float((ab["valorizacao"] + ab["rend"]).sum()),
             comprado=float(o["valor_compra"].sum()), n=len(o), tempo=float(fech["dias"].mean()) if len(fech) else np.nan)
    m["ganho"] = pf - cap
    m["soma"] = m["res_fech"] + m["res_ab"] + m["parado_rs"] - m["imp_pago"] - m["imp_pend"] - m["taxas"]
    assert abs(m["soma"] - m["ganho"]) < 1e-6, ("a decomposicao nao fecha", nome, m["soma"], m["ganho"])
    return m


def metricas_ref(serie, cap, nome, parado=None):
    q, dp, df_ = queda_max(serie, cap)
    return dict(nome=nome, cap=cap, pat=serie, p_ini=cap, p_fim=float(serie[-1]), ret=float(serie[-1] / cap - 1), p_liq=float(serie[-1]),
                ret_liq=float(serie[-1] / cap - 1), queda=q, d_pico=dp, d_fundo=df_, ganho=float(serie[-1] - cap))


M = {n: metricas([RES[n]], n) for n in NOMES}
M["Total"] = metricas([RES[n] for n in NOMES], "Total")
M["CDI"] = metricas_ref(CDI40, CAP_TOT, "105% do CDI")
M["Mercado"] = metricas_ref(MERC40, CAP_TOT, "Mercado")
TOTAL_PAT = sum(RES[n]["pat"] for n in NOMES)
# a soma das sub-carteiras tem de ser a carteira total (tambem na decomposicao)
for k_ in ("res_fech", "res_ab", "parado_rs", "imp_pago", "imp_pend", "taxas", "ganho"):
    assert abs(sum(M[n][k_] for n in NOMES) - M["Total"][k_]) < 1e-6, k_
cdi_bruto_fim = CAP_TOT * (CIDX[NM - 1] / CIDX[J0] - 1)
cdi_ir_fim = cdi_bruto_fim - (CDI40[-1] - CAP_TOT)
M["CDI"].update(parado_pct=1.0, parado_dias=float(DIAS_CORR), parado_rs=float(CDI40[-1] - CAP_TOT))
OPS = pd.concat([RES[n]["o"] for n in NOMES], ignore_index=True)
SIN = pd.concat([RES[n]["sinais"] for n in NOMES], ignore_index=True)

# ---------------------------------------------------------------- conferencias (impressas)
print("\n" + "=" * 100)
print("CONFERENCIAS")
print("=" * 100)
min_cx = min(float(R["dia"]["caixa"].min()) for R in RES.values())
assert min_cx >= -1e-6
print(f"1) caixa liquido nunca negativo: menor caixa em qualquer dia das {len(RES)} sub-carteiras = {brl(min_cx)} (assert dentro do laco, a cada dia): PASSOU")
viol = sum(1 for R in RES.values() for o in R["ops_raw"] if not (o["entrada"] > o["sinal"] and o["mi_e"] > o["mi_d"]))
assert viol == 0
print(f"2) nenhuma compra no dia do sinal: {sum(len(R['ops_raw']) for R in RES.values())} compras, todas com entrada estritamente depois da data do sinal: PASSOU")
assert all(o["sinal"] >= INICIO_SIM for R in RES.values() for o in R["ops_raw"])
# faixa de volume respeitada
for n_, R in RES.items():
    for o in R["ops_raw"]:
        assert R["lo"] <= o["vol"] < R["hi"], (n_, o["fundo"], o["vol"])
print("   e cada compra tem a mediana de 60 pregoes dentro da faixa da sub-carteira (assert): PASSOU")
# nenhum documento com data posterior ao uso
n_uso = len(ASSERT_USO)
assert all(np.datetime64(d_, "D") <= np.datetime64(u_, "D") for _, _, d_, u_ in ASSERT_USO)
n_ee = sum(1 for x in ASSERT_USO if x[0] == "saida antecipada")
assert all(np.datetime64(d_, "D") < np.datetime64(u_, "D") for w_, _, d_, u_ in ASSERT_USO if w_ == "saida antecipada")
print(f"3) nenhum documento com data posterior ao uso: {n_uso} usos de documentos (bloqueio, rendimento zero e saida antecipada) conferidos; todos com data de entrega <= dia do sinal "
      f"(entrada) ou anterior ao dia da venda ({n_ee} saidas antecipadas): PASSOU")
# a mediana de 60 pregoes usa so dados ate o dia do sinal: refaz a mao para uma compra
_o = RES[NOMES[0]]["ops_raw"][0] if RES[NOMES[0]]["ops_raw"] else None
for n_ in NOMES:
    if RES[n_]["ops_raw"]:
        _o = RES[n_]["ops_raw"][0]
        F_ = _o["F"]
        s_ = int(np.searchsorted(F_["dates"], np.datetime64(_o["sinal"], "D")))
        g_ = PR[PR["fundo"] == _o["fundo"]].reset_index(drop=True)
        vv_ = g_["volume_dia (R$)"].to_numpy(float)[s_ - 59:s_ + 1]
        assert g_["data"].iloc[s_] == _o["sinal"] and len(vv_) == 60 and abs(np.median(vv_) - _o["vol"]) < 1e-6
        print(f"   mediana refeita a mao ({n_}, {_o['fundo']}, sinal {dt(_o['sinal'])}): mediana dos 60 volumes diarios de {dt(g_['data'].iloc[s_ - 59])} a {dt(g_['data'].iloc[s_])} = "
              f"{brl(np.median(vv_))}; o programa usou {brl(_o['vol'])}: PASSOU")
        break


def conferir_op(R, escolha, rotulo):
    o = R["o"]
    c = o[(o["status"] == "Fechada") & (o["rend_recebido"] > 0)]
    if c.empty:
        c = o[o["status"] == "Fechada"]
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
        ps = float(g.loc[k, C_FE])
        ant = g[C_FE].iloc[e + 1:k].to_numpy() < np.array([float(g[C_FE].iloc[j - N:j].mean()) for j in range(e + 1, k)])
        assert ps >= media and (len(ant) == 0 or ant.all()), "fechamento nao e o primeiro >= media"
        txt_s = (f"FECHAMENTO do dia {ps:.2f} (>= media dos 200 fechamentos anteriores {media:.4f}; todos os fechamentos dos {len(ant)} dias anteriores ficaram abaixo da media do dia)")
    elif op["motivo"] == PRAZO_M or op["motivo"] == GUARDA:
        ps = float(g.loc[k, C_FE])
        txt_s = f"fechamento {ps:.2f}"
    else:                                                  # saida antecipada: abertura
        ps = float(g.loc[k, C_AB])
        txt_s = f"ABERTURA do dia {ps:.2f}"
    venda = op["cotas"] * ps
    taxa_v = B3 * venda if fechada else 0.0
    incl = op["motivo"] in (PRAZO_M, ABERTO)
    fim_ = op["saida"] if fechada else g.loc[k, "data"]
    msk = (PG["fundo"] == f) & (PG["data_base"] >= op["entrada"]) & ((PG["data_base"] <= fim_) if incl else (PG["data_base"] < fim_))
    av = PG[msk]
    rend_decl = float(av["valor (R$/cota)"].sum()) * op["cotas"]
    rend_rec = sum(float(a["valor (R$/cota)"]) * op["cotas"] for _, a in av.iterrows() if pd.notna(a["data_pagamento"]) and np.datetime64(a["data_pagamento"], "D") <= MD[-1])
    res = venda - compra + rend_rec - taxa_c - taxa_v
    sit = f"saida {dt(op['saida'])} ({op['motivo']})" if fechada else "em aberto em 09/11/2026 (a preco do ultimo fechamento)"
    print(f"\n  [{rotulo}] {f}: sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])} (depois do sinal), {sit}")
    print(f"    compra: {int(op['cotas'])} cotas x abertura {ab:.2f} = {compra:.2f}; taxa 0,03% = {taxa_c:.4f}")
    for _, a in av.iterrows():
        print(f"    rendimento: data-base {dt(a['data_base'])}, {a['valor (R$/cota)']:.4f}/cota x {int(op['cotas'])} = {a['valor (R$/cota)'] * op['cotas']:.4f}; pago em {dt(a['data_pagamento'])}")
    print(f"    {'venda' if fechada else 'valor atual'}: {int(op['cotas'])} cotas x {txt_s} = {venda:.2f}; taxa 0,03% = {taxa_v:.4f}")
    print(f"    resultado = {venda:.2f} - {compra:.2f} + {rend_rec:.4f} - {taxa_c:.4f} - {taxa_v:.4f} = {res:.4f} ({100 * res / compra:.4f}% da compra)")
    print(f"    programa: compra {op['valor_compra']:.2f}, {'venda' if fechada else 'valor atual'} {op['valor_saida']:.2f}, rendimentos {op['rend']:.4f}, taxas {op['taxas']:.4f}, "
          f"resultado {op['resultado']:.4f} ({100 * op['resultado_pct']:.4f}%)")
    assert abs(compra - op["valor_compra"]) < 1e-6 and abs(venda - op["valor_saida"]) < 1e-6
    assert abs(rend_rec - op["rend"]) < 1e-6 and abs(res - op["resultado"]) < 1e-6
    print("    ASSERT PASSOU (compra, rendimento, valor de venda pelo fechamento, taxas e resultado batem com o programa)")
    return (f"{rotulo}, {f} (sinal {dt(op['sinal'])}, entrada {dt(op['entrada'])}, {'saída ' + dt(op['saida']) if fechada else 'em aberto em 09/11/2026'}): compra {int(op['cotas'])} cotas × "
            f"R$ {br(ab)} = {brl(compra)}; rendimentos {brl(rend_rec)}; {'venda' if fechada else 'valor atual'} {brl(venda)}; taxas {brl(taxa_c + taxa_v, 2)}; "
            f"resultado {brl(res)} ({pct(res / compra)}).")


print("\n4) Operacao fechada refeita a mao a partir dos arquivos de entrada (precos_*.csv e rendimentos_pagamentos.csv):")
CONF_TXT = []
for n_ in NOMES:
    if (RES[n_]["o"]["status"] == "Fechada").any():
        CONF_TXT.append(conferir_op(RES[n_], "primeira", n_))
        break
assert CONF_TXT, "nenhuma operacao fechada para conferir"
_ee = OPS[(OPS["status"] == "Fechada") & (OPS["motivo"].str.startswith("saída antecipada"))]
if len(_ee):
    print("\n   e uma saida antecipada (venda pela ABERTURA):")
    _n = _ee.iloc[0]["carteira"]
    _r = RES[_n]["o"]
    _i = _r.index[(_r["fundo"] == _ee.iloc[0]["fundo"]) & (_r["entrada"] == _ee.iloc[0]["entrada"])][0]
    _R2 = dict(RES[_n], o=_r.loc[[_i]])
    CONF_TXT.append(conferir_op(_R2, "primeira", _n + " (saída antecipada)"))

print("\n5) Resgate do caixa com IR e IOF (refeito a mao com cdi.csv):")


def conferir_resgate(R, cond, rotulo):
    lg = [x for x in R["caixa"].log if cond(x)]
    x = lg[0]
    i0 = float(CDI.loc[CDI["data"] == x["lote_data"], "indice_105_do_cdi"].iloc[0])
    i1 = float(CDI.loc[CDI["data"] == x["ref_data"], "indice_105_do_cdi"].iloc[0])
    dias = (x["data"] - x["lote_data"]).days
    p = x["principal"]
    bruto = p * (i1 / i0 - 1)
    iof = IOF[dias - 1] / 100 if 1 <= dias <= 29 else 0.0
    ir_aliq = aliq_rf(dias)
    liq = p + bruto * (1 - iof) * (1 - ir_aliq)
    print(f"  [{rotulo}] {x['motivo']} em {dt(x['data'])}: lote aplicado em {dt(x['lote_data'])} ({dias} dias corridos), principal resgatado {p:.4f}")
    print(f"    indice 105% CDI: {i0:.6f} -> {i1:.6f} ({dt(x['ref_data'])}); bruto = {p:.4f} x ({i1:.6f}/{i0:.6f} - 1) = {bruto:.4f}; IOF {100 * iof:.0f}% = {bruto * iof:.4f}; "
          f"IR {100 * ir_aliq:.1f}% sobre {bruto * (1 - iof):.4f} = {bruto * (1 - iof) * ir_aliq:.4f}; liquido = {liq:.4f}")
    print(f"    programa: bruto {x['bruto']:.4f}, IOF {x['iof']:.4f}, IR {x['ir']:.4f}, liquido {x['liquido']:.4f}")
    assert abs(liq - x["liquido"]) < 1e-6 and abs(bruto - x["bruto"]) < 1e-6
    print("    ASSERT PASSOU")


for n_ in NOMES:
    if any(x["dias"] >= 30 and x["bruto"] > 1 for x in RES[n_]["caixa"].log):
        conferir_resgate(RES[n_], lambda x: x["dias"] >= 30 and x["bruto"] > 1, n_ + ", so IR")
        break
for n_ in NOMES:
    if any(1 <= x["dias"] <= 29 and x["bruto"] > 0.01 for x in RES[n_]["caixa"].log):
        conferir_resgate(RES[n_], lambda x: 1 <= x["dias"] <= 29 and x["bruto"] > 0.01, n_ + ", IOF + IR")
        break

# 105% CDI direto
v_cdi = CAP_TOT * (CIDX[NM - 1] / CIDX[J0] - 1)
liq_cdi = CAP_TOT + v_cdi * (1 - aliq_rf(DIAS_CORR))
print(f"\n6) R$ {br(CAP_TOT, 0)} em 105% do CDI de {dt(TS[J0])} a {dt(TS[-1])} ({DIAS_CORR} dias corridos, IR {100 * aliq_rf(DIAS_CORR):.1f}%): bruto {v_cdi:.2f}; liquido {liq_cdi:.2f}; serie do programa {CDI40[-1]:.2f}")
assert abs(liq_cdi - CDI40[-1]) < 1e-6

print("\n7) Imposto do FII (20% sobre o ganho liquido do mes; prejuizo abate), refeito por fora:")
for nm_ in NOMES:
    R = RES[nm_]
    f_ = R["o"][R["o"]["status"] == "Fechada"].copy()
    if f_.empty:
        assert abs(float(R["devidos"]["devido"].sum())) < 1e-9 and R["pend"] == 0
        print(f"  {nm_}: sem vendas, sem imposto")
        continue
    f_["saida"] = pd.to_datetime(f_["saida"])
    f_["mes"] = f_["saida"].dt.to_period("M")
    pool, tot = 0.0, 0.0
    for mes, gg in f_.groupby("mes", sort=True):
        gm = float(gg["ganho_trib"].sum())
        if gm >= 0:
            base_ = max(gm - pool, 0.0)
            pool = max(pool - gm, 0.0)
        else:
            base_ = 0.0
            pool += -gm
        tot += IR_OP * base_
    devidos = float(R["devidos"]["devido"].sum())
    pago = float(R["darf"]["pago"].sum()) if len(R["darf"]) else 0.0
    print(f"  {nm_}: devido por fora {tot:.2f} = devido pelo programa {devidos:.2f}; pago ate 09/11 {pago:.2f}; vencido e pendente {R['pend']:.2f}; a vencer depois de 09/11 {R['darf_a_pagar']:.2f}")
    assert abs(tot - devidos) < 1e-6 and abs(devidos - (pago + R["pend"] + R["darf_a_pagar"])) < 1e-6
print("   ASSERT PASSOU (devido = pago + pendente + a vencer)")

print("\n8) De onde veio o resultado (R$), por sub-carteira: fechadas + abertas + dinheiro parado - imposto do FII - taxas = patrimonio final - R$ 10.000 (assert por sub-carteira e no total):")
for n_ in NOMES + ["Total"]:
    m = M[n_]
    print(f"  {n_:15s} {m['res_fech']:10.2f} + {m['res_ab']:10.2f} + {m['parado_rs']:8.2f} - {m['imp_pago'] + m['imp_pend']:7.2f} - {m['taxas']:6.2f} = {m['soma']:10.2f}  (patrimonio final {m['p_fim']:.2f} - {m['cap']:.0f} = {m['ganho']:.2f}): PASSOU")

# ---------------------------------------------------------------- tabelas impressas
print("\n" + "=" * 100)
print("RESUMO (ordem R$ 1.000)")
print("=" * 100)
cols = NOMES + ["Total", "CDI", "Mercado"]
linhas = [
    ("Patrimonio final (R$)", lambda m: brl(m["p_fim"])),
    ("Retorno liquido", lambda m: pct(m["ret_liq"])),
    ("Contra o CDI (pontos)", lambda m: br(100 * (m["ret_liq"] - M["CDI"]["ret_liq"]), 1)),
    ("Maior queda", lambda m: pct(m["queda"])),
]
print(" | ".join(["indicador"] + cols))
for nome_l, fn in linhas:
    print(" | ".join([nome_l] + [fn(M[c]) for c in cols]))
for c in NOMES + ["Total"]:
    m = M[c]
    print(f"\n{c}: operacoes {m['n']} (abertas {m['n_ab']}, fechadas {m['n_fe']}); fechadas com lucro {m['n_luc_fe']}; rendimentos recebidos {brl(m['rend'])}; "
          f"imposto FII pago {brl(m['imp_pago'])} + pendente {brl(m['imp_pend'])}; a vencer {brl(m['imp_a_vencer'])}; se vendesse tudo {brl(m['imp_hip'])}; "
          f"taxas {brl(m['taxas'])}; parado {pct(m['parado_pct'])} ({br(m['parado_dias'], 1)} dias) rendeu {brl(m['parado_rs'])}")
print(f"\n105% do CDI: R$ {br(CAP_TOT, 0)} -> {brl(CDI40[-1])} (bruto {brl(CAP_TOT + cdi_bruto_fim)}; IR {brl(cdi_ir_fim)}). Mercado: {brl(MERC40[-1])}.")

# sinais por resultado
print("\nSINAIS DE 2026 POR SUB-CARTEIRA (so os que caem na faixa de volume):")
print(SIN.groupby(["carteira", "resultado"]).size().unstack(fill_value=0).T.to_string())
out_faixa = []
for X in GATILHOS:
    for lst in CAND[X]:
        for c in lst:
            if not any(lo <= c["vol"] < hi and X == x_ for (x_, lo, hi) in SUBS.values()):
                out_faixa.append((X, c["F"]["nome"], TS[c["md"]], c["vol"]))
OUT_FAIXA = pd.DataFrame(out_faixa, columns=["X", "fundo", "sinal", "vol"])
print(f"\nsinais fora de todas as faixas (mediana < R$ 100 mil): {len(OUT_FAIXA)} em {OUT_FAIXA['fundo'].nunique()} fundos")

print("\nOPERACOES FECHADAS:")
for r_ in OPS[OPS["status"] == "Fechada"].sort_values(["carteira", "entrada"]).itertuples():
    print(f"  {r_.carteira:15s} {r_.fundo:7s} {dt(r_.entrada)} R$ {br(r_.preco_entrada)} -> {dt(r_.saida)} R$ {br(r_.preco_saida)} | {br(r_.valor_compra)} -> {br(r_.valor_saida)} | {r_.motivo} | {r_.dias} d | "
          f"queda {pct(r_.queda_max)} ({dt(r_.queda_data)}) alta {pct(r_.alta_max)} ({dt(r_.alta_data)}) | rend {br(r_.rend)} | res {br(r_.resultado)} ({pct(r_.resultado_pct)})")
print("\nPOSICOES ABERTAS EM 09/11/2026:")
for r_ in OPS[OPS["status"] != "Fechada"].sort_values(["carteira", "entrada"]).itertuples():
    print(f"  {r_.carteira:15s} {r_.fundo:7s} {dt(r_.entrada)} R$ {br(r_.preco_entrada)} x {int(r_.cotas)} | {br(r_.valor_compra)} -> {br(r_.valor_saida)} | rend pago {br(r_.rend)} a receber {br(r_.rend_a_receber)} | res {br(r_.resultado)} ({pct(r_.resultado_pct)}) | queda {pct(r_.queda_max)} alta {pct(r_.alta_max)}")
fech_pend = OPS[(OPS["status"] == "Fechada") & ((OPS["rend_a_receber"] > 0) | (OPS["rend_sem_data"] > 0))]
print(f"\nfechadas com rendimento declarado mas ainda nao pago/sem data de pagamento: {len(fech_pend)}")


# ================================================================ TABELAS DE SAIDAS ANTECIPADAS, BLOQUEIOS E LACUNAS
EE = OPS[(OPS["status"] == "Fechada") & (OPS["motivo"].str.startswith("saída antecipada"))].copy()
_doc_de = {(x["carteira"], x["fundo"], x["entrada"]): x["doc"] for R in RES.values() for x in R["ops_raw"] if x.get("doc") is not None}
EE["doc"] = [_doc_de[(r_.carteira, r_.fundo, r_.entrada)] for r_ in EE.itertuples()]
EE = EE.sort_values(["carteira", "entrada"]).reset_index(drop=True)
ALERTAS = pd.DataFrame([a for R in RES.values() for a in R["alertas"]])
BLQ_RAW = SIN[SIN["resultado"].isin(["bloqueado: pode sair da bolsa", "rendimento cortado (aviso do FNET)"])].copy()
if len(BLQ_RAW):
    BLQ_RAW["sinal_txt"] = BLQ_RAW["sinal"].map(dt)
    BLQ = (BLQ_RAW.groupby(["fundo", "resultado", "fonte", "doc_id", "doc_dia", "padrao", "trecho"], as_index=False)
           .agg(subs=("carteira", lambda v: ", ".join(sorted(set(v)))), sinais=("sinal_txt", lambda v: ", ".join(sorted(set(v), key=lambda s_: pd.to_datetime(s_, format="%d/%m/%Y")))),
                n=("sinal", "nunique"), primeiro=("sinal", "min")).sort_values(["primeiro", "fundo"]).reset_index(drop=True))
else:
    BLQ = pd.DataFrame(columns=["fundo", "resultado", "fonte", "doc_id", "doc_dia", "padrao", "trecho", "subs", "sinais", "n", "primeiro"])
BLQ_FNET = BLQ[BLQ["fonte"] == "FNET"] if len(BLQ) else BLQ

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


def graf_colunas(ws, titulo, col_val, col_cat, r0, r1, anchor, largura=26):
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "col", titulo, 10, largura
    ch.add_data(Reference(ws, min_col=col_val, min_row=r0 - 1, max_row=r1), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=col_cat, min_row=r0, max_row=r1))
    eixos(ch, "Operação (sub-carteira, fundo, entrada)", "Resultado (% do valor de entrada)", '0%')
    ch.legend = None
    s = ch.series[0]
    s.graphicalProperties.solidFill = "0072B2"
    s.invertIfNegative = False
    ch.gapWidth = 60
    ws.add_chart(ch, anchor)


# ---- linhas do resumo (usadas na planilha e no documento)
def _t(x, f):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f(x)


ND = "—"
LIN = [  # (rotulo, funcao -> valor bruto ou None, formato Excel, funcao de texto)
    ("Patrimônio inicial (R$)", lambda m: m["p_ini"], F_BRL, brl),
    ("Patrimônio final, cotas a preço de 09/11 (R$)", lambda m: m["p_fim"], F_BRL, brl),
    ("Retorno líquido (descontado o imposto do FII a vencer e o que seria devido se vendesse tudo)", lambda m: m["ret_liq"], F_PCT, pct),
    ("Contra o CDI (pontos percentuais do retorno líquido)", lambda m: 100 * (m["ret_liq"] - M["CDI"]["ret_liq"]), '0.0', lambda x: br(x, 1)),
    ("Maior queda do patrimônio no caminho", lambda m: m["queda"], F_PCT, pct),
    ("  ... do pico em", lambda m: m["d_pico"] if m["queda"] < 0 else None, F_DATA, dt),
    ("  ... até o ponto mais baixo em", lambda m: m["d_fundo"] if m["queda"] < 0 else None, F_DATA, dt),
    ("Operações abertas / fechadas", lambda m: f"{m['n_ab']} / {m['n_fe']}" if "n_ab" in m else None, "@", str),
    ("Fechadas com lucro", lambda m: (f"{m['n_luc_fe']} de {m['n_fe']} ({pct(m['luc_fe'], 0)})" if m.get("n_fe") else ("nenhuma fechada" if "n_fe" in m else None)), "@", str),
    ("Rendimentos recebidos no caixa (R$)", lambda m: m.get("rend"), F_BRL, brl),
    ("Imposto do FII pago + vencido e não pago (R$)", lambda m: m["imp_pago"] + m["imp_pend"] if "imp_pago" in m else None, F_BRL, brl),
    ("Dinheiro parado no CDI: % médio do patrimônio", lambda m: m.get("parado_pct"), F_PCT, pct),
    ("Dinheiro parado no CDI: dias-equivalentes parado (de 311 dias corridos)", lambda m: m.get("parado_dias"), '0.0', lambda x: br(x, 1)),
    ("Dinheiro parado no CDI: quanto rendeu, líquido de IR/IOF (R$)", lambda m: m.get("parado_rs"), F_BRL, brl),
    ("De onde veio: operações fechadas, valorização + rendimentos (R$)", lambda m: m.get("res_fech"), F_BRL, brl),
    ("De onde veio: operações abertas a preço de 09/11, valorização + rendimentos pagos (R$)", lambda m: m.get("res_ab"), F_BRL, brl),
    ("De onde veio: rendimento do dinheiro parado (R$)", lambda m: m.get("parado_rs"), F_BRL, brl),
    ("De onde veio: − imposto do FII (R$)", lambda m: -(m["imp_pago"] + m["imp_pend"]) if "imp_pago" in m else None, F_BRL, brl),
    ("De onde veio: − taxas de compra e venda (R$)", lambda m: -m["taxas"] if "taxas" in m else None, F_BRL, brl),
    ("= Ganho total (patrimônio final − capital) (R$)", lambda m: m["ganho"], F_BRL, brl),
]
COLS_R = NOMES + ["Total", "CDI", "Mercado"]
TIT_R = {"Agressiva 1": "Agressiva 1 (15%; mediana R$ 100–200 mil)", "Agressiva 2": "Agressiva 2 (15%; R$ 200–500 mil)", "Conservadora 1": "Conservadora 1 (20%; R$ 500 mil–1 mi)",
         "Conservadora 2": "Conservadora 2 (20%; > R$ 1 mi)", "Total": "Total (R$ 40 mil)", "CDI": "105% do CDI (R$ 40 mil)", "Mercado": "Mercado (R$ 40 mil)"}

# ------------------------------------------------ Resumo
ws = wb.active
ws.title = "Resumo"
ws["A1"] = "Kairi em 2026, versão 3: quatro sub-carteiras de R$ 10.000 (resumo, 17/11/2026)"
ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = (f"De {dt(TS[J0])} a {dt(TS[-1])}; ordem de R$ 1.000. Filtro de negociação: mediana do volume diário dos 60 pregões até o dia do sinal. "
            "Venda no fechamento do dia em que o fechamento fica igual ou acima da média de 200 pregões (ou prazo de 252 pregões). "
            "Avisos do FNET: rendimento zero bloqueia a compra; liquidação/incorporação/tombamento etc. publicados com a posição aberta vendem na abertura seguinte.")
ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("A2:H2")
ws.row_dimensions[2].height = 64
cab(ws, 4, ["Indicador"] + [TIT_R[c] for c in COLS_R], [86] + [24] * len(COLS_R))
for i, (rot, fn, fmt, _) in enumerate(LIN, 5):
    ws.cell(row=i, column=1, value=rot)
    for j, c in enumerate(COLS_R, 2):
        try:
            v = fn(M[c])
        except KeyError:
            v = None
        if c == "CDI" and rot.startswith("De onde veio") and "parado" not in rot and "Ganho" not in rot:
            v = None
        if v is None:
            ws.cell(row=i, column=j, value=ND).alignment = Alignment(horizontal="right")
            continue
        if isinstance(v, pd.Timestamp):
            v = v.to_pydatetime()
        elif isinstance(v, (np.floating, np.integer)):
            v = float(v)
        cell = ws.cell(row=i, column=j, value=v)
        cell.number_format = fmt
        cell.alignment = Alignment(horizontal="right")
ws.freeze_panes = "B5"

# ------------------------------------------------ Operacoes fechadas
wo = wb.create_sheet("Operações fechadas")
FE = OPS[OPS["status"] == "Fechada"].sort_values(["carteira", "entrada", "fundo"]).reset_index(drop=True)
TIT_FE = ["Sub-carteira", "Fundo", "Entrada (data)", "Entrada (preço R$)", "Saída (data)", "Saída (preço R$)", "Valor de entrada (R$)", "Valor de saída (R$)", "Motivo da saída", "Dias",
          "Maior queda (% do preço de entrada, menor fechamento)", "Data da maior queda", "Maior alta (% do preço de entrada, maior fechamento)", "Data da maior alta",
          "Rendimentos recebidos (R$)", "Resultado (R$)", "Resultado (%)", "Rótulo (gráfico)"]
cab(wo, 1, TIT_FE, [15, 9, 12, 10, 12, 10, 13, 13, 30, 7, 16, 12, 16, 12, 13, 13, 11, 28])
wo.row_dimensions[1].height = 62
for i, r_ in enumerate(FE.itertuples(), 2):
    vals = [r_.carteira, r_.fundo, r_.entrada.to_pydatetime(), r_.preco_entrada, r_.saida.to_pydatetime(), r_.preco_saida, r_.valor_compra, r_.valor_saida, r_.motivo, int(r_.dias),
            r_.queda_max, r_.queda_data.to_pydatetime() if pd.notna(r_.queda_data) else "—", r_.alta_max, r_.alta_data.to_pydatetime() if pd.notna(r_.alta_data) else "—",
            r_.rend, r_.resultado, r_.resultado_pct, f"{r_.carteira} {r_.fundo} {r_.entrada:%d/%m}"]
    fm = ["@", "@", F_DATA, '0.00', F_DATA, '0.00', F_BRL, F_BRL, "@", '0', F_PCT, F_DATA, F_PCT, F_DATA, F_BRL, F_BRL, F_PCT, "@"]
    for j, (v, f_) in enumerate(zip(vals, fm), 1):
        c = wo.cell(row=i, column=j, value=v)
        c.number_format = f_
wo.freeze_panes = "C2"
nfe = len(FE)
if nfe:
    graf_colunas(wo, "Resultado de cada operação fechada (% do valor de entrada)", 17, 18, 2, nfe + 1, f"A{nfe + 4}", largura=max(24, min(60, 1.3 * nfe + 14)))

# ------------------------------------------------ Posicoes abertas
wp = wb.create_sheet("Posições abertas")
AB = OPS[OPS["status"] != "Fechada"].sort_values(["carteira", "entrada", "fundo"]).reset_index(drop=True)
raw_ab = {(x["carteira"], x["fundo"], x["entrada"]): x for R in RES.values() for x in R["ops_raw"]}
TIT_AB = ["Sub-carteira", "Fundo", "Entrada (data)", "Entrada (preço R$)", "Cotas", "Valor de entrada (R$)", "Último preço (R$)", "Data do último preço", "Valor atual (R$)",
          "Rendimentos pagos (R$)", "A receber (R$)", "Resultado (R$)", "Resultado (%)", "Positivo / negativo", "Maior queda até agora (%)", "Maior alta até agora (%)", "Rótulo (gráfico)"]
cab(wp, 1, TIT_AB, [15, 9, 12, 10, 8, 13, 10, 12, 13, 13, 11, 13, 11, 12, 13, 13, 28])
wp.row_dimensions[1].height = 62
AB["ult_data"] = [pd.Timestamp(raw_ab[(r_.carteira, r_.fundo, r_.entrada)]["F"]["dates"][int(raw_ab[(r_.carteira, r_.fundo, r_.entrada)]["rr"])]) for r_ in AB.itertuples()]
for i, r_ in enumerate(AB.itertuples(), 2):
    vals = [r_.carteira, r_.fundo, r_.entrada.to_pydatetime(), r_.preco_entrada, int(r_.cotas), r_.valor_compra, r_.preco_saida, r_.ult_data.to_pydatetime(), r_.valor_saida,
            r_.rend, r_.rend_a_receber, r_.resultado, r_.resultado_pct, "positivo" if r_.resultado > 0 else "negativo", r_.queda_max, r_.alta_max,
            f"{r_.carteira} {r_.fundo} {r_.entrada:%d/%m}"]
    fm = ["@", "@", F_DATA, '0.00', '0', F_BRL, '0.00', F_DATA, F_BRL, F_BRL, F_BRL, F_BRL, F_PCT, "@", F_PCT, F_PCT, "@"]
    for j, (v, f_) in enumerate(zip(vals, fm), 1):
        wp.cell(row=i, column=j, value=v).number_format = f_
wp.freeze_panes = "C2"
nab = len(AB)
if nab:
    graf_colunas(wp, "Resultado de cada posição aberta em 09/11/2026 (% do valor de entrada)", 13, 17, 2, nab + 1, f"A{nab + 4}", largura=max(24, min(60, 1.3 * nab + 14)))

# ------------------------------------------------ Patrimonio dia a dia
wd = wb.create_sheet("Patrimônio dia a dia")
TIT_D = [f"{n} (R$)" for n in NOMES] + ["105% do CDI, R$ 10 mil (R$)", "Total das 4 (R$)", "105% do CDI, R$ 40 mil (R$)", "Mercado, R$ 40 mil (R$)"]
cab(wd, 1, ["Data"] + TIT_D, [13] + [20] * len(TIT_D))
for i in range(NDIA):
    wd.cell(row=i + 2, column=1, value=DATAS[i].to_pydatetime()).number_format = F_DATA
    for j, v in enumerate([RES[n]["pat"][i] for n in NOMES] + [CDI10[i], TOTAL_PAT[i], CDI40[i], MERC40[i]], 2):
        wd.cell(row=i + 2, column=j, value=float(v)).number_format = F_BRL
wd.freeze_panes = "B2"
nr = NDIA + 1
ch = LineChart()
ch.title = "Patrimônio de cada sub-carteira (R$ 10 mil) contra 105% do CDI"
ch.height, ch.width = 10.5, 26
for col in range(2, 7):
    ch.add_data(Reference(wd, min_col=col, min_row=1, max_row=nr), titles_from_data=True)
ch.x_axis = DateAxis(crossAx=100)
ch.y_axis.crossAx = 500
ch.x_axis.majorTimeUnit = "months"
ch.x_axis.majorUnit = 1
eixos(ch, "Data", "Patrimônio (R$)", '"R$" #,##0', "mmm/yy")
ch.set_categories(Reference(wd, min_col=1, min_row=2, max_row=nr))
for s, cor, dash in zip(ch.series, [COR[n] for n in NOMES] + [COR["cdi"]], [False] * 4 + [True]):
    estilo_linha(s, cor, dash)
_all = np.concatenate([RES[n]["pat"] for n in NOMES] + [CDI10])
ch.y_axis.scaling.min = float(np.floor(_all.min() * 0.99 / 250) * 250)
ch.y_axis.scaling.max = float(np.ceil(_all.max() * 1.01 / 250) * 250)
wd.add_chart(ch, "L2")

# ------------------------------------------------ Saidas antecipadas e bloqueios
wsb = wb.create_sheet("Saídas antecipadas e bloqueios")
wsb["A1"] = "Saídas antecipadas (posição aberta; venda na abertura do pregão seguinte à publicação)"
wsb["A1"].font = Font(bold=True, size=12)
cab(wsb, 2, ["Sub-carteira", "Fundo", "Documento (FNET)", "Id", "Publicado em", "Motivo / expressão", "Entrada (data)", "Saída (data)", "Saída (preço R$)", "Resultado (%)", "Trecho do documento"],
    [15, 9, 34, 10, 12, 30, 12, 12, 11, 11, 120])
r0 = 3
for r_ in EE.itertuples():
    for j, v in enumerate([r_.carteira, r_.fundo, r_.doc["doc"], r_.doc["id"], pd.Timestamp(r_.doc["dia"]).to_pydatetime(), f"{r_.doc['tipo']}: {r_.doc['padrao']}", r_.entrada.to_pydatetime(),
                           r_.saida.to_pydatetime(), r_.preco_saida, r_.resultado_pct, r_.doc["trecho"][:600]], 1):
        c = wsb.cell(row=r0, column=j, value=v)
        c.number_format = {5: F_DATA, 7: F_DATA, 8: F_DATA, 9: '0.00', 10: F_PCT}.get(j, "@")
    r0 += 1
if not len(EE):
    wsb.cell(row=r0, column=1, value="nenhuma saída antecipada")
    r0 += 1
r0 += 1
wsb.cell(row=r0, column=1, value="Sinais barrados por documento (regra 1 de bloqueio na entrada e rendimento cortado)").font = Font(bold=True, size=12)
r0 += 1
cab(wsb, r0, ["Sub-carteiras", "Fundo", "Barrado por", "Id", "Publicado em", "Expressão", "Fonte", "Sinais (datas)", "Nº de sinais", "", "Trecho do documento"])
r0 += 1
for r_ in BLQ.itertuples():
    for j, v in enumerate([r_.subs, r_.fundo, "rendimento zero (126 pregões)" if r_.resultado.startswith("rend") else "regra 1: pode sair da bolsa", int(r_.doc_id),
                           pd.Timestamp(r_.doc_dia).to_pydatetime(), r_.padrao, r_.fonte, r_.sinais, int(r_.n), "", r_.trecho[:600]], 1):
        c = wsb.cell(row=r0, column=j, value=v)
        c.number_format = F_DATA if j == 5 else "@"
    r0 += 1
if len(ALERTAS):
    r0 += 1
    wsb.cell(row=r0, column=1, value="Avisos do FNET que não puderam virar venda").font = Font(bold=True, size=12)
    r0 += 1
    for r_ in ALERTAS.itertuples():
        wsb.cell(row=r0, column=1, value=f"{r_.carteira} {r_.fundo}: doc {r_.id} de {dt(pd.Timestamp(r_.dia))} ({r_.padrao}): {r_.motivo}")
        r0 += 1


# ================================================================ CASOS: MCEM11 E VVCR11
print("\n" + "=" * 100)
print("CASO MCEM11 (comprado na versao 2 em 12/05/2026; -47,3%)")
print("=" * 100)
F_ = FD["MCEM11"]
s_ = int(np.searchsorted(F_["dates"], np.datetime64("2026-05-11")))
assert F_["dates"][s_] == np.datetime64("2026-05-11") and F_["dates"][s_ + 1] == np.datetime64("2026-05-12")
print("sinais de 2026 do MCEM11 (gatilho, dia do sinal, mediana dos 60 pregoes, media de 60 da planilha):")
for X_, md_, vm_ in SIG_FUNDOS["MCEM11"]:
    s2 = int(np.searchsorted(F_["dates"], MD[md_]))
    faixa = [n for n, (x_, lo, hi) in SUBS.items() if x_ == X_ and lo <= vm_ < hi]
    print(f"   {int(100 * X_)}% | {dt(TS[md_])} | mediana R$ {br(vm_, 0)} | media de 60 R$ {br(F_['VOL'][s2], 0)} | faixa: {faixa[0] if faixa else 'abaixo de R$ 100 mil: nenhuma sub-carteira'}")
assert not any(o["fundo"] == "MCEM11" for R in RES.values() for o in R["ops_raw"]), "MCEM11 foi comprado na versao 3"
print("   MCEM11 nao foi comprado em nenhuma das 4 sub-carteiras (assert): PASSOU. Mesmo sem o filtro de volume, as regras b/c agem assim:")
d0_ = F_["dates"][s_ - LAG_REND]
cut_ = corte_rendimento("MCEM11", MD[int(F_["mi"][s_])], d0_) if FNET_OK else []
bl_ = bloqueio("MCEM11", MD[int(F_["mi"][s_])])
print(f"   regra b (rendimento zero) no sinal de 11/05/2026, janela de 126 pregoes ({dt(d0_)} a 11/05/2026): {len(cut_)} documento(s)")
for c_ in cut_:
    print(f"      doc {c_['id']} de {dt(pd.Timestamp(c_['dia']))} [{c_['doc']}]: ...{c_['trecho']}...")
print(f"   regra 1 (saida da bolsa) no sinal de 11/05/2026: {len(bl_)} documento(s) ate o dia do sinal")
assert len(cut_) >= 1 and pd.Timestamp(cut_[-1]["dia"]) == pd.Timestamp("2026-04-30"), "o comunicado de 30/04/2026 deveria cortar o rendimento"
print("   => pela regra b, o sinal de 11/05 NAO vira compra em 12/05/2026 (assert: PASSOU)")
r_ = s_ + 1
k_nat, mot_nat, px_nat = saida_volta(F_, r_)
kee, dee = saida_antecipada(F_, "MCEM11", MD[int(F_["mi"][s_])], int(F_["mi"][r_]), k_nat, mot_nat)
assert kee is not None
print(f"   se fosse comprado mesmo assim (abertura de 12/05/2026 a R$ {br(F_['A'][r_])}): saida normal seria {dt(F_['dates'][k_nat])} ({mot_nat}); regra c: documento {dee['id']} de "
      f"{dt(pd.Timestamp(dee['dia']))} [{dee['doc']}; {dee['padrao']}] -> venda na abertura de {dt(F_['dates'][kee])} a R$ {br(F_['A'][kee])}")
print(f"      trecho: ...{dee['trecho']}...")
assert F_["dates"][kee] == np.datetime64("2026-05-25") and abs(F_["A"][kee] - 44.79) < 0.0051, (F_["dates"][kee], F_["A"][kee])
print("   => saida em 25/05/2026 a R$ 44,79, como esperado (assert: PASSOU)")
MC_DOCS = DOCS[DOCS["fundo"] == "MCEM11"][["id", "dia", "categoria", "especie", "situacao_doc", "classe", "padrao"]] if len(DOCS) else pd.DataFrame()
print("   documentos do MCEM11 lidos como sinal (classe != vazia):")
for r2 in MC_DOCS[MC_DOCS["classe"] != ""].itertuples():
    print(f"      {r2.id} {dt(r2.dia)} {r2.categoria} / {r2.especie} (situacao {r2.situacao_doc}): {r2.classe} [{r2.padrao}]")
MCEM_TXT = (f"MCEM11: gatilho em 11/05/2026 (mediana de volume R$ {br(F_['VMED'][s_], 0)}, abaixo de R$ 100 mil: nenhuma faixa compra). Mesmo sem o filtro de volume, o comunicado de 30/04/2026 "
            f"(doc {cut_[-1]['id']}: “não haverá distribuição de rendimentos”) está nos 126 pregões antes do sinal, então a regra b barra a compra de 12/05/2026. Se fosse comprado, o edital de 22/05/2026 "
            f"(doc {dee['id']}, tombamento das cotas para o balcão) mandaria vender na abertura de 25/05/2026 a R$ {br(F_['A'][kee])}.")

print("\n" + "=" * 100)
print("CASO VVCR11 (media de 60 inflada por negocios isolados)")
print("=" * 100)
F_ = FD["VVCR11"]
VV = []
for X_, md_, vm_ in SIG_FUNDOS["VVCR11"]:
    s2 = int(np.searchsorted(F_["dates"], MD[md_]))
    faixa = [n for n, (x_, lo, hi) in SUBS.items() if x_ == X_ and lo <= vm_ < hi]
    VV.append((X_, TS[md_], vm_, float(F_["VOL"][s2]), faixa[0] if faixa else "nenhuma (< R$ 100 mil)"))
    print(f"   {int(100 * X_)}% | sinal {dt(TS[md_])} | mediana de 60 pregoes R$ {br(vm_, 0)} | media de 60 R$ {br(F_['VOL'][s2], 0)} | faixa: {VV[-1][4]}")
assert not any(o["fundo"] == "VVCR11" for R in RES.values() for o in R["ops_raw"])
assert all(v[4].startswith("nenhuma") for v in VV)
print(f"   VVCR11 barrado pela mediana em todos os {len(VV)} sinais de 2026 (assert): PASSOU")
VV_TXT = (f"VVCR11: {len(VV)} sinais em 2026, mediana de volume entre R$ {br(min(v[2] for v in VV), 0)} e R$ {br(max(v[2] for v in VV), 0)} (a média de 60, inflada por negócios isolados, ia de "
          f"R$ {br(min(v[3] for v in VV), 0)} a R$ {br(max(v[3] for v in VV), 0)}); nenhuma faixa compra (mínimo R$ 100 mil). Barrado em todos.")

# ================================================================ LACUNAS (maximo 6 linhas)
n_sem_texto = int((DOCS["leitura"] != "ok").sum()) if len(DOCS) else 0
n_canc = int((DOCS["situacao_doc"] == "C").sum()) if len(DOCS) else 0
n_dup_pg = int(PG[PG["data_base"] >= INICIO_SIM]["data_pagamento"].isna().sum())
n_saiu = int((OPS["motivo"] == SAIU).sum())
LAC = []
LAC.append(["Documentos do FNET antes de 01/05/2025", "a coleta vai de 01/05/2025 a 13/11/2026; só os 43 fundos que deram sinal em 2026",
            "a regra 1 olha 365 dias para trás: para sinais antes de 01/05/2026 a janela só tem os fatos relevantes da planilha (fatos_textos.csv.gz); um aviso que só existisse como comunicado/assembleia antes de 05/2025 não seria visto"])
LAC.append(["Leitura dos documentos", f"{len(DOCS)} documentos lidos por expressões no texto completo (sem leitura humana de todos); {n_sem_texto} sem texto legível; {n_canc} cancelados no FNET foram ignorados",
            "pode haver aviso de liquidação/rendimento zero escrito de forma que as expressões não pegam (não barrado/vendido), e trecho que casa sem tratar do fundo. Todos os documentos que casaram foram lidos (trechos nas tabelas)"])
LAC.append(["Documentos publicados depois de 09/11/2026", "o FNET foi consultado até 13/11/2026, mas os preços acabam em 09/11/2026",
            (f"{len(ALERTAS)} aviso(s) de posição aberta ficaram sem venda por cair depois do fim dos preços" if len(ALERTAS) else "nenhum aviso de posição aberta cai depois do fim dos preços; posições abertas seguem a preço de 09/11/2026")])
LAC.append(["Rendimentos declarados e ainda não pagos", f"R$ {br(M['Total']['rend_a_receber'])} a receber e R$ {br(M['Total']['rend_sem_data'])} sem data de pagamento",
            "não entram no caixa nem no resultado; se pagos, o resultado das posições abertas sobe"])
LAC.append(["Imposto do FII ainda não vencido", f"R$ {br(M['Total']['imp_a_vencer'])} a vencer depois de 09/11 e R$ {br(M['Total']['imp_hip'])} se vendesse tudo",
            "entram só no retorno líquido, não no patrimônio final"])
LAC.append(["Compras de fundo que saiu da bolsa", f"{n_saiu} compra(s) com preços que acabam antes do prazo (valor real de saída desconhecido)",
            "se houver, o cálculo continua pelo último preço (pode estar errado para mais ou para menos)"])
assert len(LAC) <= 6

# ------------------------------------------------ Legenda (Excel)
wl = wb.create_sheet("Legenda")
wl.column_dimensions["A"].width = 38
wl.column_dimensions["B"].width = 150
LEG = [
    ("Regras", "Quatro sub-carteiras independentes de R$ 10.000 (02/01/2026 a 09/11/2026), ordem de R$ 1.000. Gatilho: cota fecha 15% (Agressivas) ou 20% (Conservadoras) abaixo da média de 200 pregões, com rendimento mantido, "
               "universo e guarda de dados de sempre. Compra na abertura do pregão seguinte ao sinal; um fundo por vez por sub-carteira; maior mediana de volume primeiro."),
    ("Faixas (mediana do volume diário dos 60 pregões até o dia do sinal, inclusive)", "Agressiva 1: [R$ 100 mil, R$ 200 mil). Agressiva 2: [R$ 200 mil, R$ 500 mil). Conservadora 1: [R$ 500 mil, R$ 1 milhão). Conservadora 2: R$ 1 milhão ou mais."),
    ("Nota sobre o capital da Agressiva 2", "Interpretação adotada: o dono escreveu \"100 mil\" para a Agressiva 2; tratamos como R$ 10 mil (R$ 10.000), igual às outras três sub-carteiras."),
    ("Venda", "No FECHAMENTO do primeiro dia em que o fechamento fica igual ou acima da média de 200 pregões (média até o dia anterior); prazo de 252 pregões; dado suspeito (salto ou buraco) sai no fechamento do dia anterior. "
              "Saída antecipada por aviso do FNET: venda na abertura do pregão seguinte à data de entrega do documento."),
    ("Rendimento zero (FNET)", "Se nos 126 pregões do fundo até o dia do sinal houve comunicado de que não haverá distribuição de rendimentos (data de entrega <= dia do sinal), o rendimento é tratado como cortado e o sinal não vira compra."),
    ("Regra 1 (bloqueio na entrada)", "Fato relevante da planilha ou documento do FNET (comunicado, fato relevante, edital, carta consulta, ata) com data <= dia do sinal, nos 365 dias anteriores, sobre liquidação/dissolução/encerramento, incorporação, fusão, cisão, venda da totalidade dos ativos ou tombamento/migração para o balcão/deslistagem. Um documento de reprovação anula os anteriores."),
    ("Dinheiro parado", "Caixa sem fundo rende 105% do CDI com liquidez diária, em lotes, com IR regressivo e IOF por lote. '% médio parado' = média diária de caixa ÷ patrimônio; 'dias-equivalentes' = esse % × 311 dias corridos; 'quanto rendeu' = rendimento líquido de IR e IOF de todo o dinheiro parado (já resgatado + ainda aplicado em 09/11)."),
    ("Imposto do FII", "20% sobre o ganho líquido do mês (prejuízo abate); DARF no último pregão do mês seguinte. 'Retorno líquido' desconta também o imposto que vence depois de 09/11 e o que seria devido se vendesse as posições abertas."),
    ("De onde veio o resultado", "operações fechadas (valorização + rendimentos recebidos) + operações abertas a preço de 09/11 (valorização + rendimentos pagos) + rendimento do dinheiro parado − imposto do FII (pago + vencido) − taxas (0,03% na compra e na venda) = patrimônio final − R$ 10.000 (conferido por assert no programa)."),
    ("Maior queda / maior alta durante a operação", "Menor e maior FECHAMENTO do dia da entrada até o último dia com a posição (na venda pela abertura, até o dia anterior), em % do preço de entrada. Queda nunca fica acima de 0% e alta nunca abaixo de 0% (se o fundo não passou do preço de entrada, 0% e sem data)."),
    ("Resultado da operação", "valor de saída − valor de entrada + rendimentos recebidos − taxas. Em aberto: valor de saída = cotas × último fechamento (09/11/2026); rendimentos = só os já pagos."),
    ("Confirmado por execução / dedução", "Tudo nas tabelas vem da execução do programa estudos/kairi_carteira_2026.py (com asserts). Interpretações: faixa da Agressiva 2; 'data de entrega' do FNET usada como data de publicação; documento cancelado (situação C) ignorado; Aviso aos Cotistas estruturado (XML de rendimentos) fora."),
]
for i, (a_, b_) in enumerate(LEG, 1):
    wl.cell(row=i, column=1, value=a_).font = Font(bold=True)
    c = wl.cell(row=i, column=2, value=b_)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    wl.cell(row=i, column=1).alignment = Alignment(wrap_text=True, vertical="top")
r0 = len(LEG) + 3
wl.cell(row=r0, column=1, value="Lacunas").font = Font(bold=True, size=12)
cab(wl, r0 + 1, ["Dado", "Situação e efeito"])
wl.column_dimensions["A"].width = 38
for i, (a_, b_, c_) in enumerate(LAC, r0 + 2):
    wl.cell(row=i, column=1, value=a_).alignment = Alignment(wrap_text=True, vertical="top")
    cc = wl.cell(row=i, column=2, value=f"{b_}. Efeito: {c_}.")
    cc.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(SAIDA_XLSX)
print(f"\nPlanilha salva em {SAIDA_XLSX}")


# ================================================================ DOCUMENTO EM MARKDOWN (simplificado)
def md_tab(cab_, linhas):
    out = ["| " + " | ".join(cab_) + " |", "|" + "|".join("---" for _ in cab_) + "|"]
    for l_ in linhas:
        out.append("| " + " | ".join(str(x).replace("|", "/") for x in l_) + " |")
    return "\n".join(out)


def cel(fn, tf, m):
    try:
        v = fn(m)
    except KeyError:
        return "—"
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return tf(v)


mt, mcdi, mmer = M["Total"], M["CDI"], M["Mercado"]
lin1 = []
for rot, fn, fmt, tf in LIN:
    cels = []
    for c in COLS_R:
        if c == "CDI" and rot.startswith("De onde veio") and "parado" not in rot:
            cels.append("—")
        else:
            cels.append(cel(fn, tf, M[c]))
    lin1.append([rot.replace("(descontado o imposto do FII a vencer e o que seria devido se vendesse tudo)", "(líquido do imposto)")] + cels)
T1 = md_tab(["Indicador"] + [TIT_R[c] for c in COLS_R], lin1)

# --- tabela 2: operacoes fechadas
rows2 = []
for r_ in FE.itertuples():
    rows2.append([r_.carteira, r_.fundo, f"{dt(r_.entrada)} a R$ {br(r_.preco_entrada)}", f"{dt(r_.saida)} a R$ {br(r_.preco_saida)}", brl(r_.valor_compra), brl(r_.valor_saida), r_.motivo,
                  int(r_.dias), f"{pct(r_.queda_max)}" + (f" ({dt(r_.queda_data)})" if pd.notna(r_.queda_data) else ""), f"{pct(r_.alta_max)}" + (f" ({dt(r_.alta_data)})" if pd.notna(r_.alta_data) else ""),
                  brl(r_.rend), f"{brl(r_.resultado)} ({pct(r_.resultado_pct)})"])
T2 = md_tab(["Sub-carteira", "Fundo", "Entrada", "Saída", "Valor de entrada", "Valor de saída", "Motivo", "Dias", "Maior queda (menor fechamento)", "Maior alta (maior fechamento)", "Rendimentos", "Resultado"], rows2) if rows2 else "Nenhuma operação fechada."

# --- tabela 3: posicoes abertas
rows3 = []
for r_ in AB.itertuples():
    rows3.append([r_.carteira, r_.fundo, f"{dt(r_.entrada)} a R$ {br(r_.preco_entrada)}", int(r_.cotas), brl(r_.valor_compra), f"R$ {br(r_.preco_saida)} ({dt(r_.ult_data)})", brl(r_.valor_saida),
                  brl(r_.rend), brl(r_.rend_a_receber), f"{brl(r_.resultado)} ({pct(r_.resultado_pct)})", "positivo" if r_.resultado > 0 else "negativo",
                  f"{pct(r_.queda_max)}" + (f" ({dt(r_.queda_data)})" if pd.notna(r_.queda_data) else ""), f"{pct(r_.alta_max)}" + (f" ({dt(r_.alta_data)})" if pd.notna(r_.alta_data) else "")])
T3 = md_tab(["Sub-carteira", "Fundo", "Entrada", "Cotas", "Valor de entrada", "Último preço", "Valor atual", "Rendimentos pagos", "A receber", "Resultado", "+/−", "Maior queda até agora", "Maior alta até agora"], rows3) if rows3 else "Nenhuma posição aberta."


def curto(t, n=150):
    t = re.sub(r"\s+", " ", str(t)).strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


rows4 = []
for r_ in EE.itertuples():
    rows4.append(["Saída antecipada", r_.carteira, r_.fundo, f"{dt(pd.Timestamp(r_.doc['dia']))} (id {r_.doc['id']}): {r_.doc['doc']}", f"{r_.doc['tipo']}: {r_.doc['padrao']}",
                  f"vendeu em {dt(r_.saida)} a R$ {br(r_.preco_saida)}; resultado {pct(r_.resultado_pct)}", "“…" + curto(r_.doc["trecho"]) + "…”"])
for r_ in BLQ_FNET.itertuples() if len(BLQ_FNET) else []:
    rows4.append(["Sinal barrado" + (" (rendimento zero)" if r_.resultado.startswith("rend") else " (regra 1)"), r_.subs, r_.fundo, f"{dt(pd.Timestamp(r_.doc_dia))} (id {r_.doc_id})", r_.padrao,
                  f"{int(r_.n)} sinal(is): {r_.sinais}", "“…" + curto(r_.trecho) + "…”"])
T4 = md_tab(["Tipo", "Sub-carteira(s)", "Fundo", "Documento do FNET (data de entrega)", "Expressão", "Efeito", "Trecho"], rows4) if rows4 else "Nenhuma saída antecipada nem bloqueio por documento do FNET."
T5 = md_tab(["Dado", "Situação", "Efeito"], LAC)

print("\n(DOC ainda nao escrito)")
print(f"\nTempo total: {time.time() - T0:.1f} s")
