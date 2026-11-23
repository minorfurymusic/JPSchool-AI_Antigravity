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
FONTES = {  # rodada 2: alternativas para o que falhou na rodada 1 (Tesouro e índices da B3)
    "Tesouro Transparente (página do conjunto)": "https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto",
    "Tesouro Direto taxas do dia (JSON)": "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json",
    "B3 cotação IFIX": "https://cotacao.b3.com.br/mds/api/v1/instrumentQuotation/IFIX",
    "B3 cotação IBOV": "https://cotacao.b3.com.br/mds/api/v1/instrumentQuotation/IBOV",
    "B3 variação do dia IFIX": "https://cotacao.b3.com.br/mds/api/v1/DailyFluctuationHistory/IFIX",
    "B3 IFIX carteira do dia": "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"
        + b64({"language": "pt-br", "pageNumber": 1, "pageSize": 5, "index": "IFIX", "segment": "1"}),
    "B3 IFIX estatística (GetYearlyHistory, ordem 2)": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetYearlyHistory/"
        + b64({"index": "IFIX", "language": "pt-br", "year": "2026"}),
    "Yahoo Ibovespa": "https://query1.finance.yahoo.com/v8/finance/chart/%5EBVSP?range=5d&interval=1d",
    "Yahoo IFIX": "https://query1.finance.yahoo.com/v8/finance/chart/IFIX.SA?range=5d&interval=1d",
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
