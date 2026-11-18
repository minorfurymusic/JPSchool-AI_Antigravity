"""Regra 1 do Kairi (não comprar fundo que vai sair da bolsa), COPIADA SEM MUDANÇA de estudos/kairi_carteira_anos.py
(trecho da "regra 1" e trecho "DOCUMENTOS DO FNET", que acrescenta os documentos do FNET 2025–2026 à regra; 18/11/2026), para os estudos novos não precisarem carregar o programa inteiro do Kairi (que tem
conferências presas aos dados até 09/11/2026). Se a regra mudar lá, copiar de novo.
"""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

PL = Path(__file__).resolve().parents[1] / "planilhas"
FNET_INI, FNET_FIM = pd.Timestamp("2025-05-01"), pd.Timestamp("2026-11-13")
CACHE_FNET = PL / "tecnico" / "fnet_2026_documentos.csv.gz"
JANELA_FATO = 365       # regra 1: dias corridos de fatos olhados para tras (inclusive o dia do sinal)

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
