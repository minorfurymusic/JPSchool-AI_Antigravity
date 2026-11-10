"""Leitura dos informes de FII do portal de dados abertos da CVM.

A CVM já trocou nomes de colunas (CNPJ_Fundo -> CNPJ_Fundo_Classe). A leitura
confere as colunas que o app usa e para com aviso claro se alguma sumir.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

NOMES_ANTIGOS = {"CNPJ_Fundo": "CNPJ_Fundo_Classe", "Nome_Fundo": "Nome_Fundo_Classe"}
CHAVE = ["CNPJ_Fundo_Classe", "Data_Referencia", "Versao"]

# tabela -> colunas que o app usa (obrigatórias)
USADAS = {
    "inf_mensal_fii_geral": CHAVE + ["Nome_Fundo_Classe", "Codigo_ISIN", "Segmento_Atuacao", "Mandato",
                                     "Tipo_Gestao", "Mercado_Negociacao_Bolsa", "Nome_Administrador", "Data_Entrega"],
    "inf_mensal_fii_complemento": CHAVE + ["Total_Numero_Cotistas", "Patrimonio_Liquido", "Cotas_Emitidas",
                                           "Valor_Patrimonial_Cotas", "Percentual_Dividend_Yield_Mes",
                                           "Percentual_Amortizacao_Cotas_Mes"],
    "inf_mensal_fii_ativo_passivo": CHAVE + ["Rendimentos_Distribuir", "Total_Investido", "Direitos_Bens_Imoveis",
                                             "CRI", "FII", "Total_Passivo", "Contas_Receber_Venda_Imoveis"],
    "inf_trimestral_fii_alienacao_imovel": CHAVE + ["Nome_Imovel", "Data_Alienacao", "Percentual_Imovel_PL"],
    "inf_trimestral_fii_aquisicao_imovel": CHAVE + ["Nome_Imovel", "Percentual_Imovel_Total_Investido"],
    "inf_trimestral_fii_imovel": CHAVE + ["Nome_Imovel", "Percentual_Vacancia", "Percentual_Inadimplencia",
                                          "Percentual_Receitas_FII"],
    "inf_trimestral_fii_resultado_contabil_financeiro": CHAVE + [
        "Receita_Venda_Investimento_Financeiro", "Receita_Aluguel_Investimento_Financeiro"],
}


class CabecalhoMudou(Exception):
    pass


def ler_csv(arquivo, tabela: str, origem: str = "") -> pd.DataFrame:
    df = pd.read_csv(arquivo, sep=";", encoding="latin-1", dtype=str, quoting=3, on_bad_lines="warn")
    df = df.rename(columns=NOMES_ANTIGOS)
    faltam = [c for c in USADAS[tabela] if c not in df.columns]
    # colunas criadas pela CVM em anos recentes podem faltar só nos arquivos antigos
    toleradas = {"Contas_Receber_Venda_Imoveis"}
    graves = [c for c in faltam if c not in toleradas]
    if graves:
        raise CabecalhoMudou(f"{origem or tabela}: a CVM mudou o arquivo. Colunas que sumiram: {graves}. "
                             f"Colunas presentes: {list(df.columns)}")
    for c in faltam:
        df[c] = None
    return df[USADAS[tabela]].copy()


def ler_tabela(pasta: Path, tabela: str) -> pd.DataFrame:
    """Junta todos os anos de uma tabela e fica só com a versão mais alta de cada informe."""
    grupo = "inf_mensal_fii" if tabela.startswith("inf_mensal") else "inf_trimestral_fii"
    partes = []
    for zp in sorted(pasta.glob(f"{grupo}_*.zip")):
        ano = zp.stem.rsplit("_", 1)[1]
        with zipfile.ZipFile(zp) as z:
            nome = f"{tabela}_{ano}.csv"
            if nome not in z.namelist():
                continue
            with z.open(nome) as f:
                partes.append(ler_csv(f, tabela, origem=f"{zp.name}/{nome}"))
    if not partes:
        raise FileNotFoundError(f"nenhum arquivo de {tabela} em {pasta}")
    df = pd.concat(partes, ignore_index=True)
    df["Versao"] = pd.to_numeric(df["Versao"], errors="coerce").fillna(0).astype(int)
    df["Data_Referencia"] = pd.to_datetime(df["Data_Referencia"], errors="coerce")
    df = df.dropna(subset=["Data_Referencia", "CNPJ_Fundo_Classe"])
    ultima = df.groupby(["CNPJ_Fundo_Classe", "Data_Referencia"])["Versao"].transform("max")
    return df[df["Versao"] == ultima].reset_index(drop=True)


def numero(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie, errors="coerce")
