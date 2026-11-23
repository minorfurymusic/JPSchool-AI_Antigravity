"""Testa, de onde roda, o acesso às fontes da rotina diária (23/11/2026). Grava o resultado em docs/teste_rede.txt.

    python3 estudos/teste_rede.py
"""
import base64
import datetime as dt
import json
import time
from pathlib import Path

import requests

b64 = lambda d: base64.b64encode(json.dumps(d).encode()).decode()
FONTES = {
    "FNET lista (19/11/2026)": "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=5"
        "&tipoFundo=1&idCategoriaDocumento=0&idTipoDocumento=0&idEspecieDocumento=0&dataInicial=19/11/2026&dataFinal=19/11/2026",
    "B3 COTAHIST diário 19/11/2026": "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D19112026.ZIP",
    "Banco Central dólar (série 1)": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/3?formato=json",
    "Banco Central IPCA (série 433)": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/3?formato=json",
    "Banco Central IGP-M (série 189)": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados/ultimos/3?formato=json",
    "Banco Central Focus": "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais?$top=3&$format=json&$orderby=Data%20desc&$filter=Indicador%20eq%20'Selic'",
    "Tesouro Direto taxas": "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv",
    "B3 IFIX histórico do ano": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetYearlyHistory/"
        + b64({"language": "pt-br", "index": "IFIX", "year": "2026"}),
    "B3 Ibovespa histórico do ano": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetYearlyHistory/"
        + b64({"language": "pt-br", "index": "IBOV", "year": "2026"}),
    "CVM informe mensal FII": "https://dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/",
}

linhas = [f"Rodado em {dt.datetime.utcnow():%d/%m/%Y %H:%M} UTC"]
for nome, url in FONTES.items():
    t = time.time()
    try:
        r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
        corpo = r.raw.read(400, decode_content=True)
        linhas.append(f"{r.status_code} | {time.time()-t:5.1f}s | {nome} | {r.headers.get('content-type','')} | "
                      f"{r.headers.get('content-length','?')} bytes | início: {corpo[:160]!r}")
    except Exception as e:  # noqa: BLE001
        linhas.append(f"ERRO | {time.time()-t:5.1f}s | {nome} | {type(e).__name__}: {str(e)[:160]}")
Path("docs").mkdir(exist_ok=True)
Path("docs/teste_rede.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
