"""Classificação de cada fundo, mês a mês, pelo que ele tem na carteira (informe mensal da CVM, tabela ativo_passivo).

Motivo (18/11/2026): em planilhas/fundos.csv, 338 de 524 fundos estão como "Outros" (o fundo se declara "Multicategoria"),
e a regra "rendimento acima do próprio tipo" comparava quase tudo com o mercado inteiro.

Regra (fixada antes de rodar qualquer carteira). Parte de cada grupo sobre a soma dos grupos:
  papel           CRI, CRI_CRA, LCI, LCI_LCA, LIG, Letras_Hipotecarias, Debentures, Cedulas_Debentures, Notas_Promissorias,
                  FDIC (FIDC), Certificados_Deposito_Valores_Mobiliarios
  imoveis         Terrenos, Imoveis_Renda_Acabados, Imoveis_Renda_Construcao, Imoveis_Venda_Acabados, Imoveis_Venda_Construcao,
                  Outros_Direitos_Reais, Acoes_Sociedades_Atividades_FII, Cotas_Sociedades_Atividades_FII
  fii             FII (cotas de outros fundos imobiliários)
  outros          Acoes, Fundo_Acoes, FIP, Outras_Cotas_FI, CEPAC, Bonus_Subscricao, Outros_Valores_Mobliarios
  Classe: Papel se papel >= 2/3; Fundo de fundos se fii >= 2/3; Tijolo se imoveis >= 2/3 (Desenvolvimento se metade ou
  mais dos imóveis for "para venda"); senão Híbrido. Sem nada investido: "Sem carteira".
  Vale a partir da data de entrega do informe (Data_Entrega da tabela geral); na consulta, o último informe entregue com
  referência de até 24 meses antes; sem informe, o tipo do cadastro (planilhas/fundos.csv) quando for específico.
Código de negociação: 4 letras do ISIN + "11" (BRLIFECTF... -> LIFE11), ligado pelo CNPJ (ISIN de qualquer mês do
mesmo CNPJ). Na consulta, vale o prefixo de 4 letras (BBFI11B usa BBFI).

Saída: planilhas/classificacao_carteira_mensal.csv (uma linha por fundo e mês).

    PYTHONPATH=. python3 estudos/classificacao_carteira.py
"""
import os
import subprocess
import zipfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "planilhas" / "classificacao_carteira_mensal.csv"
PASTA = Path(os.environ.get("CVM_MENSAL", "/tmp/claude-0/cvm_men"))
URL = "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/inf_mensal_fii_{a}.zip"
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
GRUPOS = {
    "papel": ["CRI", "CRI_CRA", "LCI", "LCI_LCA", "LIG", "Letras_Hipotecarias", "Debentures", "Cedulas_Debentures",
              "Notas_Promissorias", "FDIC", "Certificados_Deposito_Valores_Mobiliarios"],
    "imoveis": ["Terrenos", "Imoveis_Renda_Acabados", "Imoveis_Renda_Construcao", "Imoveis_Venda_Acabados",
                "Imoveis_Venda_Construcao", "Outros_Direitos_Reais", "Acoes_Sociedades_Atividades_FII",
                "Cotas_Sociedades_Atividades_FII"],
    "fii": ["FII"],
    "outros": ["Acoes", "Fundo_Acoes", "FIP", "Outras_Cotas_FI", "CEPAC", "Bonus_Subscricao", "Outros_Valores_Mobliarios"],
}
VENDA = ["Imoveis_Venda_Acabados", "Imoveis_Venda_Construcao"]


def _ler(z, nome):
    df = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str)
    return df.rename(columns={"CNPJ_Fundo": "CNPJ_Fundo_Classe", "Nome_Fundo": "Nome_Fundo_Classe"})


def montar():
    PASTA.mkdir(parents=True, exist_ok=True)
    A, G = [], []
    for a in range(2017, 2027):
        zp = PASTA / f"inf_mensal_fii_{a}.zip"
        if not zp.exists():
            subprocess.run(["curl", "-sS", "-f", "-o", str(zp), URL.format(a=a)], check=True)
        with zipfile.ZipFile(zp) as z:
            A.append(_ler(z, f"inf_mensal_fii_ativo_passivo_{a}.csv"))
            G.append(_ler(z, f"inf_mensal_fii_geral_{a}.csv")[["CNPJ_Fundo_Classe", "Data_Referencia", "Versao", "Data_Entrega",
                                                               "Codigo_ISIN", "Nome_Fundo_Classe"]])
    k = ["CNPJ_Fundo_Classe", "Data_Referencia"]
    A, G = pd.concat(A), pd.concat(G)
    for X in (A, G):
        X["Versao"] = pd.to_numeric(X["Versao"], errors="coerce").fillna(0)
    A = A.sort_values("Versao").drop_duplicates(k, keep="last")
    G = G.sort_values("Versao").drop_duplicates(k, keep="last")
    cols = sorted({c for v in GRUPOS.values() for c in v})
    faltam = [c for c in cols if c not in A.columns]
    assert not faltam, f"colunas que sumiram da CVM: {faltam}"
    for c in cols:
        A[c] = pd.to_numeric(A[c], errors="coerce").fillna(0).clip(lower=0)
    T = A[k].copy()
    for g, cs in GRUPOS.items():
        T[g] = A[cs].sum(axis=1)
    T["imoveis_venda"] = A[VENDA].sum(axis=1)
    soma = T[list(GRUPOS)].sum(axis=1)
    for g in GRUPOS:
        T[f"parte_{g}"] = np.where(soma > 0, T[g] / soma, np.nan)
    T["parte_venda_nos_imoveis"] = np.where(T["imoveis"] > 0, T["imoveis_venda"] / T["imoveis"], np.nan)
    cl = np.select([soma <= 0, T["parte_papel"] >= 2 / 3, T["parte_fii"] >= 2 / 3,
                    (T["parte_imoveis"] >= 2 / 3) & (T["parte_venda_nos_imoveis"] >= 0.5), T["parte_imoveis"] >= 2 / 3],
                   ["Sem carteira", "Papel", "Fundo de fundos", "Desenvolvimento", "Tijolo"], "Híbrido")
    T["classe"] = cl
    T["total_classificado (R$)"] = soma
    T = T.merge(G.drop(columns="Versao"), on=k, how="left")
    # código pelo CNPJ: o ISIN falta em alguns meses; vale o ISIN informado pelo mesmo CNPJ em qualquer mês (o mais recente)
    isin = T["Codigo_ISIN"].fillna("").str.upper()
    T["prefixo"] = np.where(isin.str.match(r"^BR[A-Z]{4}CTF"), isin.str[2:6], None)
    m = T.dropna(subset=["prefixo"]).sort_values("Data_Referencia").groupby("CNPJ_Fundo_Classe")["prefixo"].last()
    T["prefixo"] = T["prefixo"].fillna(T["CNPJ_Fundo_Classe"].map(m))
    # reserva: CNPJ -> código pelo informe trimestral (planilhas/tecnico/cobertura_trimestral.csv)
    tri = pd.read_csv(RAIZ / "planilhas/tecnico/cobertura_trimestral.csv", dtype=str, **{k: v for k, v in OP.items() if k != "decimal"})
    m2 = tri.dropna(subset=["fundo"]).groupby("cnpj")["fundo"].last().str[:4]
    T["prefixo"] = T["prefixo"].fillna(T["CNPJ_Fundo_Classe"].map(m2))
    T["fundo"] = np.where(T["prefixo"].notna(), T["prefixo"] + "11", None)
    T["mes_referencia"] = pd.to_datetime(T["Data_Referencia"]).dt.strftime("%m/%Y")
    T["entrega"] = pd.to_datetime(T["Data_Entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
    out = T.rename(columns={"CNPJ_Fundo_Classe": "cnpj", "Nome_Fundo_Classe": "nome"})[
        ["fundo", "cnpj", "nome", "mes_referencia", "entrega", "classe", "parte_papel", "parte_imoveis", "parte_fii", "parte_outros",
         "parte_venda_nos_imoveis", "total_classificado (R$)"]]
    out.to_csv(SAIDA, index=False, float_format="%.4f", **OP)
    return out


@lru_cache(maxsize=1)
def _tab():
    T = pd.read_csv(SAIDA, **OP)
    T = T.dropna(subset=["fundo"])
    T["fundo"] = T["fundo"].str[:4]
    T["entrega"] = pd.to_datetime(T["entrega"], dayfirst=True)
    T["ref"] = pd.to_datetime("01/" + T["mes_referencia"], dayfirst=True)
    return {f: x.sort_values(["ref", "entrega"]) for f, x in T.groupby("fundo")}


CADASTRO = {"Logística": "Tijolo", "Shoppings": "Tijolo", "Lajes corporativas": "Tijolo", "Papel (títulos)": "Papel",
            "Híbrido": "Híbrido"}


@lru_cache(maxsize=1)
def _cad():
    f = pd.read_csv(RAIZ / "planilhas/fundos.csv", sep=";", encoding="utf-8-sig")
    return f.set_index("fundo")["tipo"].map(CADASTRO).dropna().to_dict()


def classe_e_fonte(fundo, dia):
    """(classe, fonte). Fonte: 'informe' (último informe mensal entregue até o dia, referência de até 24 meses antes),
    'cadastro' (tipo específico de planilhas/fundos.csv) ou 'nenhuma'."""
    d = pd.Timestamp(dia)
    x = _tab().get(str(fundo)[:4])
    if x is not None:
        x = x[(x["entrega"] <= d) & (x["ref"] >= d - pd.DateOffset(months=24))]
        if len(x) and x["classe"].iloc[-1] != "Sem carteira":
            return x["classe"].iloc[-1], "informe"
    c = _cad().get(fundo)
    return (c, "cadastro") if c else ("Sem informe", "nenhuma")


def classe(fundo, dia):
    return classe_e_fonte(fundo, dia)[0]


if __name__ == "__main__":
    T = montar()
    print(f"gravado: {SAIDA.relative_to(RAIZ)} ({len(T)} linhas, {T['fundo'].nunique()} fundos com código, "
          f"{T['fundo'].isna().sum()} linhas sem código de negociação)")
    print("sem data de entrega:", T["entrega"].isna().sum())
    ult = T.dropna(subset=["fundo"]).sort_values("mes_referencia").groupby("fundo").tail(1)
    print("classe no último informe de cada fundo:", ult["classe"].value_counts().to_dict())
    P = pd.read_csv(RAIZ / "planilhas/precos_2026.csv", **OP, usecols=["data", "fundo", "volume_medio_60 (R$)"])
    neg = P[P["data"] == P["data"].iloc[-1]]
    neg = neg[neg["volume_medio_60 (R$)"] >= 250e3]["fundo"]
    hoje = pd.to_datetime(P["data"].iloc[-1], dayfirst=True)
    c = pd.Series({f: classe(f, hoje) for f in neg})
    print(f"fundos negociados com R$ 250 mil/dia em {hoje:%d/%m/%Y}: {len(c)}; por classe: {c.value_counts().to_dict()}")
    for f in ["HGLG11", "KNCR11", "XPML11", "LIFE11", "HABT11", "RBRX11", "HFOF11", "JSAF11", "RCRB11", "MXRF11"]:
        print(f, classe(f, hoje))
