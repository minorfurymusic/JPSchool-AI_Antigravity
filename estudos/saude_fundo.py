"""Saúde de um fundo imobiliário num dia (só com dados publicados até esse dia). Usado pela Skill "avaliar-fundo"
(.claude/skills/avaliar-fundo/SKILL.md), pela ficha (estudos/ficha_fundo.py) e pelas simulações.

Medidas:
  queda_fundo_6m / queda_mercado_6m / individual_6m  queda do fundo, do mercado de fundos e a diferença (6 meses)
  tendencia_rend   média dos 3 últimos meses de rendimento ÷ média dos 3 primeiros dos últimos 12 meses − 1
  cortes_rend      meses em que o rendimento caiu mais de 5% contra o mês anterior (12 meses)
  oscilacao_rend   desvio padrão ÷ média do rendimento mensal (12 meses)
  vp_12m           variação do valor patrimonial por cota em 12 meses (dado com 75 dias de atraso)
  pvp              preço ÷ valor patrimonial
  docs_negativos   fatos relevantes e comunicados (12 meses) com calote, inadimplemento, remarcação ou reavaliação
                   negativa, ofício da B3/CVM sobre oscilação, recuperação judicial, rescisão ou despejo
Veredito automático (aproximação da leitura humana da Skill):
  NÃO COMPRAR  queda só do fundo (10 pontos ou mais pior que o mercado em 6 meses) E algum problema:
               rendimento caindo mais de 10%, 3 ou mais cortes, valor patrimonial caindo mais de 5%, ou documento negativo
  ATENÇÃO      queda só do fundo de 20 pontos ou mais, sem problema visível nos dados (compra; motivo desconhecido)
  SAUDÁVEL     o resto
"""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

PL = Path(__file__).resolve().parents[1] / "planilhas"
_OPC = dict(sep=";", decimal=",", encoding="utf-8-sig")


@lru_cache(maxsize=1)
def _dados():
    P = pd.concat([pd.read_csv(PL / f"precos_{a}.csv", **_OPC,
                               usecols=["data", "fundo", "fechamento", "valor_patrimonial_cota", "preco_sobre_valor_patrimonial",
                                        "rendimento_ano_sobre_preco (%)", "patrimonio (R$)", "volume_medio_60 (R$)"])
                   for a in range(2017, 2027)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    PF = {f: x.set_index("data").sort_index() for f, x in P.groupby("fundo")}
    M = pd.read_csv(PL / "mercado.csv", **_OPC)
    M["data"] = pd.to_datetime(M["data"], dayfirst=True)
    M = M.set_index("data")["indice_mercado"]
    R = pd.read_csv(PL / "rendimentos_pagamentos.csv", **_OPC)
    R["data_base"] = pd.to_datetime(R["data_base"], dayfirst=True)
    R = R.drop_duplicates(["fundo", "data_base", "valor (R$/cota)"])
    RF = {f: x.sort_values("data_base") for f, x in R.groupby("fundo")}
    T = pd.read_csv(PL / "tecnico" / "fatos_textos.csv.gz", sep=";", encoding="utf-8-sig")
    T["dia"] = pd.to_datetime(T["data_anuncio"].str[:10], dayfirst=True)
    T = T.rename(columns={T.columns[4]: "texto"})[["fundo", "dia", "texto"]].assign(fonte="fato relevante")
    try:
        F = pd.read_csv(PL / "tecnico" / "fnet_2026_documentos.csv.gz", sep=";", encoding="utf-8-sig")
        F["dia"] = pd.to_datetime(F["data de entrega"].astype(str).str[:10], dayfirst=True, errors="coerce")
        F = F.rename(columns={"texto (primeiros 5.000 caracteres)": "texto"})
        F = F.assign(fonte="FNET: " + F["categoria"].astype(str))[["fundo", "dia", "texto", "fonte"]]
        T = pd.concat([T, F], ignore_index=True)
    except FileNotFoundError:
        pass
    DOC = {f: x.sort_values("dia") for f, x in T.groupby("fundo")}
    return PF, M, RF, DOC


def _sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFD", str(t).lower()) if unicodedata.category(c) != "Mn")


NEGATIVOS = [
    ("calote / inadimplemento", r"inadimplemento|nao foram honrad|nao honrou|deixou de (pagar|honrar)|calote|default\b|vencimento antecipado"),
    ("recuperação judicial", r"recuperacao judicial|recuperacao extrajudicial|falencia"),
    ("remarcação negativa", r"(remarcacao|reavaliacao|marcacao a mercado)\W+(\w+\W+){0,25}?(variacao negativa|negativ|reducao|desvaloriza)|variacao negativa de"),
    ("ofício da B3/CVM sobre oscilação", r"oficio\W+(\w+\W+){0,30}?oscilac|esclarecimentos de consulta|ultimas oscilacoes registradas"),
    ("rescisão / despejo / saída de inquilino", r"rescisao (antecipada )?do contrato|acao de despejo|desocupacao|devolucao do imovel|aviso previo de rescisao"),
]


def saude(fundo, dia):
    PF, M, RF, DOC = _dados()
    d = pd.Timestamp(dia)
    out = dict(fundo=fundo, dia=d)
    p = PF.get(fundo)
    if p is None or p.loc[:d].empty:
        return dict(out, veredito="SEM DADOS")
    pd_ = p.loc[:d]

    def var(s, meses):
        a = s.loc[:d - pd.DateOffset(months=meses)]
        return float(s.loc[:d].iloc[-1] / a.iloc[-1] - 1) if len(a) else np.nan

    out["queda_fundo_6m"] = var(p["fechamento"], 6)
    out["queda_mercado_6m"] = var(M, 6)
    out["individual_6m"] = out["queda_fundo_6m"] - out["queda_mercado_6m"]
    out["queda_fundo_12m"], out["queda_mercado_12m"] = var(p["fechamento"], 12), var(M, 12)
    out["pvp"] = float(pd_["preco_sobre_valor_patrimonial"].iloc[-1])
    out["rend_ano_sobre_preco"] = float(pd_["rendimento_ano_sobre_preco (%)"].iloc[-1]) / 100
    out["patrimonio_mi"] = float(pd_["patrimonio (R$)"].iloc[-1]) / 1e6
    vp = pd_["valor_patrimonial_cota"].dropna()
    vp12 = vp.loc[:d - pd.DateOffset(months=12)]
    out["vp_12m"] = float(vp.iloc[-1] / vp12.iloc[-1] - 1) if len(vp) and len(vp12) else np.nan
    r = RF.get(fundo)
    v = np.array([])
    if r is not None:
        r = r[(r["data_base"] <= d) & (r["data_base"] > d - pd.Timedelta(days=365))]
        v = r.groupby(r["data_base"].dt.to_period("M"))["valor (R$/cota)"].sum().to_numpy(float)
    out["meses_rend"] = len(v)
    if len(v) >= 6:
        var_m = v[1:] / v[:-1] - 1
        out["tendencia_rend"] = float(v[-3:].mean() / v[:3].mean() - 1)
        out["cortes_rend"] = int((var_m < -0.05).sum())
        out["oscilacao_rend"] = float(v.std() / v.mean())
    else:
        out["tendencia_rend"] = out["cortes_rend"] = out["oscilacao_rend"] = np.nan
    achados = []
    docs = DOC.get(fundo)
    if docs is not None:
        docs = docs[(docs["dia"] <= d) & (docs["dia"] > d - pd.DateOffset(months=12))]
        for x in docs.itertuples():
            t = _sem_acento(x.texto)
            for nome, pad in NEGATIVOS:
                m = re.search(pad, t)
                if m:
                    achados.append(f"{x.dia:%d/%m/%Y} {x.fonte}: {nome} («{t[max(0, m.start() - 60):m.end() + 60]}»)")
                    break
    out["docs_negativos"] = achados
    problemas = []
    if out["tendencia_rend"] < -0.10:
        problemas.append(f"rendimento caindo {out['tendencia_rend']:.0%} em 12 meses")
    if out["cortes_rend"] >= 3:
        problemas.append(f"{out['cortes_rend']} cortes de rendimento em 12 meses")
    if out["vp_12m"] < -0.05:
        problemas.append(f"valor patrimonial por cota {out['vp_12m']:.0%} em 12 meses")
    if achados:
        problemas.append(f"{len(achados)} documento(s) negativo(s)")
    out["problemas"] = problemas
    so_fundo = out["individual_6m"] <= -0.10
    if so_fundo and problemas:
        out["veredito"] = "NÃO COMPRAR"
    elif out["individual_6m"] <= -0.20:
        out["veredito"] = "ATENÇÃO"
    else:
        out["veredito"] = "SAUDÁVEL"
    return out
