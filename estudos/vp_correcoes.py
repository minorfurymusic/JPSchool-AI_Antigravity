"""Correções do valor patrimonial por cota (vem do informe mensal da CVM, preenchido pelo administrador do fundo).

NÃO altera planilhas/precos_AAAA.csv (usadas pelo Kairi e pelos outros estudos): gera a tabela de correções
planilhas/tecnico/valor_patrimonial_correcoes.csv e a função `aplicar(P)`, que devolve uma cópia com
valor_patrimonial_cota, preco_sobre_valor_patrimonial e patrimonio corrigidos. Aplicar à base inteira depende do dono.

Regra (fixada antes de rodar a carteira). Para cada fundo, a sequência dos valores informados (cada troca de valor):
  r1 = valor ÷ valor anterior. Salto = r1 > 1,5 ou r1 < 0,65.
  A  Erro que volta: depois do salto, o valor seguinte volta para 0,8 a 1,25 do valor de antes do salto
     -> o valor do salto é descartado (fica valendo o anterior até o seguinte).
  B  Desdobramento/grupamento não ajustado: salto que não volta; preço ÷ valor patrimonial (mediana de 60 pregões)
     fora de 0,3–3,0 ANTES e dentro DEPOIS -> todos os valores anteriores multiplicados por r1.
  C  Valor novo absurdo: salto que não volta; preço ÷ valor patrimonial dentro de 0,3–3,0 ANTES e fora DEPOIS
     -> valores a partir do salto descartados (sem valor patrimonial).
  B e C só valem com as duas medianas conhecidas (corrigido em 18/11/2026: sem preço antes, a regra B piorava CARE11,
     DMAC11, HGPO11, PNDL11 e VIFI11).
  D  O resto: salto mantido (provável evento real: venda de imóvel, amortização, reavaliação), marcado para conferência.

    PYTHONPATH=. python3 estudos/vp_correcoes.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "planilhas" / "tecnico" / "valor_patrimonial_correcoes.csv"
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")


def _pvp_med(x, ini, fim):
    s = (x["fechamento"] / x["vp"]).loc[ini:fim].dropna()
    return float(s.median()) if len(s) else np.nan


def detectar(P):
    """P: data, fundo, fechamento, valor_patrimonial_cota. Devolve a tabela de correções."""
    L = []
    for f, x in P.sort_values("data").groupby("fundo"):
        x = x.set_index("data").rename(columns={"valor_patrimonial_cota": "vp"})
        v = x["vp"].dropna()
        mud = v[v.diff() != 0]
        if len(mud) < 2:
            continue
        datas, vals = mud.index, mud.to_numpy(float)
        i = 1
        while i < len(vals):
            r1 = vals[i] / vals[i - 1]
            if 0.65 <= r1 <= 1.5:
                i += 1
                continue
            nxt = vals[i + 1] / vals[i - 1] if i + 1 < len(vals) else np.nan
            base = dict(fundo=f, data_salto=datas[i], valor_antes=vals[i - 1], valor_salto=vals[i], razao=r1)
            if 0.8 <= nxt <= 1.25:
                L.append(dict(base, tipo="A erro que volta", acao="descartar valor do salto",
                              ate=datas[i + 1], fator=np.nan))
                i += 2
                continue
            antes = _pvp_med(x, datas[i] - pd.Timedelta(days=90), datas[i] - pd.Timedelta(days=1))
            depois = _pvp_med(x, datas[i], datas[i] + pd.Timedelta(days=90))
            ok_a, ok_d = 0.3 <= antes <= 3.0, 0.3 <= depois <= 3.0
            conhecido = not (np.isnan(antes) or np.isnan(depois))   # sem as duas medidas, não decide (vira D)
            if conhecido and not ok_a and ok_d:
                L.append(dict(base, tipo="B desdobramento não ajustado", acao="multiplicar valores anteriores", ate=datas[i], fator=r1,
                              pvp_antes=antes, pvp_depois=depois))
            elif conhecido and ok_a and not ok_d:
                L.append(dict(base, tipo="C valor novo absurdo", acao="descartar a partir do salto", ate=pd.NaT, fator=np.nan,
                              pvp_antes=antes, pvp_depois=depois))
            else:
                L.append(dict(base, tipo="D salto mantido (conferir)", acao="nenhuma", ate=pd.NaT, fator=np.nan,
                              pvp_antes=antes, pvp_depois=depois))
            i += 1
    return pd.DataFrame(L)


def aplicar(P, C=None):
    """Cópia de P com valor patrimonial (e P/VP e patrimônio) corrigidos pela tabela C."""
    if C is None:
        C = pd.read_csv(SAIDA, **OP)
        for c in ("data_salto", "ate"):
            C[c] = pd.to_datetime(C[c], dayfirst=True)
    P = P.copy()
    vp = P["valor_patrimonial_cota"].copy()
    pat = P["patrimonio (R$)"].copy() if "patrimonio (R$)" in P else None
    for r in C.itertuples():
        m = P["fundo"] == r.fundo
        if r.tipo.startswith("A"):
            k = m & (P["data"] >= r.data_salto) & (P["data"] < r.ate)
            vp[k] = r.valor_antes
        elif r.tipo.startswith("B"):
            k = m & (P["data"] < r.data_salto)
            vp[k] = vp[k] * r.fator
        elif r.tipo.startswith("C"):
            k = m & (P["data"] >= r.data_salto)
            vp[k] = np.nan
            if pat is not None:
                pat[k] = np.nan
    P["valor_patrimonial_cota"] = vp
    P["preco_sobre_valor_patrimonial"] = P["fechamento"] / vp
    if pat is not None:
        P["patrimonio (R$)"] = pat
    return P


if __name__ == "__main__":
    P = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{a}.csv", **OP,
                               usecols=["data", "fundo", "fechamento", "valor_patrimonial_cota", "patrimonio (R$)", "volume_medio_60 (R$)"])
                   for a in range(2017, 2027)])
    P["data"] = pd.to_datetime(P["data"], dayfirst=True)
    C = detectar(P)
    C.to_csv(SAIDA, index=False, date_format="%d/%m/%Y", **OP)
    print(f"gravado: {SAIDA.relative_to(RAIZ)} ({len(C)} saltos em {C['fundo'].nunique()} fundos)")
    print(C["tipo"].value_counts().to_string())
    Q = aplicar(P, C)
    liq = Q["volume_medio_60 (R$)"] >= 250e3
    for nome, X in (("antes", P.assign(pvp=P["fechamento"] / P["valor_patrimonial_cota"])), ("depois", Q.assign(pvp=Q["preco_sobre_valor_patrimonial"]))):
        b = X[liq & ((X["pvp"] < 0.3) | (X["pvp"] > 3))]
        print(f"{nome}: linhas com preço/patrimônio fora de 0,3–3,0 em fundos com R$ 250 mil/dia: {len(b)} "
              f"({', '.join(sorted(b['fundo'].unique()))})")
    print(C[C["fundo"].isin(["HSAF11", "STRX11", "ALZR11", "TEPP11", "SNLG11"])].to_string(index=False))
