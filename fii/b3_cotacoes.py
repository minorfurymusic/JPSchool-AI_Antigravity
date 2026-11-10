"""Leitura do arquivo histórico de cotações da B3 (COTAHIST).

Arquivo de texto de largura fixa, sem cabeçalho de colunas. As linhas NÃO vêm
em ordem de data: quem usa tem que ordenar. Posições conferidas contra o
arquivo real de 2026 (ver PLANO.md, seção 1A).
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

BDI_FII = b"12"
TAMANHO_LINHA = 245


class FormatoInesperado(Exception):
    pass


def ler_linha(bruta: bytes) -> dict | None:
    """Devolve a cotação de uma linha de FII, ou None se a linha não interessa."""
    if bruta[0:2] != b"01" or bruta[10:12] != BDI_FII:
        return None
    if len(bruta.rstrip(b"\r\n")) != TAMANHO_LINHA:
        raise FormatoInesperado(f"linha com {len(bruta.rstrip())} posições, esperado {TAMANHO_LINHA}")
    l = bruta.decode("latin-1")
    return {
        "data": f"{l[2:6]}-{l[6:8]}-{l[8:10]}",
        "ticker": l[12:24].strip(),
        "nome": l[27:39].strip(),
        "especie": l[39:49].strip(),
        "abertura": int(l[56:69]) / 100,
        "maxima": int(l[69:82]) / 100,
        "minima": int(l[82:95]) / 100,
        "media": int(l[95:108]) / 100,
        "fechamento": int(l[108:121]) / 100,
        "negocios": int(l[147:152]),
        "quantidade": int(l[152:170]),
        "volume": int(l[170:188]) / 100,
        "isin": l[230:242].strip(),
    }


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    linhas = []
    with zipfile.ZipFile(caminho) as z:
        nomes = z.namelist()
        if len(nomes) != 1:
            raise FormatoInesperado(f"{caminho.name}: esperado 1 arquivo, veio {nomes}")
        with z.open(nomes[0]) as f:
            primeira = f.readline()
            if not primeira.startswith(b"00COTAHIST"):
                raise FormatoInesperado(f"{caminho.name}: cabeçalho inesperado {primeira[:30]!r}")
            for bruta in f:
                reg = ler_linha(bruta)
                if reg:
                    linhas.append(reg)
    df = pd.DataFrame(linhas)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def nome_anual(ano: int) -> str:
    return f"COTAHIST_A{ano}.ZIP"


def nome_diario(dia) -> str:
    return f"COTAHIST_D{dia:%d%m%Y}.ZIP"
