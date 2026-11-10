"""Caminhos e endereços. Tudo em um lugar para facilitar troca e teste."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
BRUTO_B3 = DADOS / "bruto" / "b3"
BRUTO_CVM = DADOS / "bruto" / "cvm"
BRUTO_FUNDOS = DADOS / "bruto" / "b3_fundos"
BANCO = DADOS / "fii.duckdb"
PAINEL = DADOS / "painel.html"

URL_COTAHIST = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/{nome}"
URL_CVM = "https://dados.cvm.gov.br/dados/FII/DOC/{pasta}/DADOS/{nome}"
URL_B3_FUNDO = "https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedSupplementFunds/{param}"
URL_B3_COTACAO = "https://cotacao.b3.com.br/mds/api/v1/instrumentQuotation/{ticker}"

PRIMEIRO_ANO_PRECO = 2017
PRIMEIRO_ANO_CVM = 2016
