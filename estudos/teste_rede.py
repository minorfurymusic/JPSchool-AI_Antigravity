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
FONTES = {  # rodada 4 (23/11/2026): juro real longo (NTN-B / IPCA+) e histórico do IFIX
    "ANBIMA títulos públicos 19/11/2026 (ms261119)": "https://www.anbima.com.br/informacoes/merc-sec/arqs/ms261119.txt",
    "ANBIMA títulos públicos 19/11/2021 (ms211119)": "https://www.anbima.com.br/informacoes/merc-sec/arqs/ms211119.txt",
    "ANBIMA títulos públicos 02/01/2017 (ms170102)": "https://www.anbima.com.br/informacoes/merc-sec/arqs/ms170102.txt",
    "ANBIMA IMA (índices de títulos)": "https://www.anbima.com.br/informacoes/ima/arqs/ima_completo.txt",
    "B3 arquivo de taxas de swap 19/11/2026": "https://www.b3.com.br/pesquisapregao/download?filelist=TS261119.ex_",
    "Tesouro Transparente API": "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto",
    "Tesouro Transparente por http": "http://www.tesourotransparente.gov.br/",
    "B3 IFIX histórico (indexCall minúsculo)": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/indexCall/GetYearlyHistory/"
        + b64({"index": "IFIX", "language": "pt-br", "year": "2025"}),
    "B3 IFIX evolução diária": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetDailyHistory/"
        + b64({"index": "IFIX", "language": "pt-br", "year": "2025"}),
    "B3 IFIX estatística (página)": "https://sistemaswebb3-listados.b3.com.br/indexStatisticsPage/day/IFIX?language=pt-br",
    "Yahoo ^IFIX máximo": "https://query1.finance.yahoo.com/v8/finance/chart/%5EIFIX?range=max&interval=1d",
    "Yahoo IFIX.SA máximo": "https://query1.finance.yahoo.com/v8/finance/chart/IFIX.SA?range=max&interval=1d",
    "brapi IFIX": "https://brapi.dev/api/quote/%5EIFIX?range=1y&interval=1d",
    "Investing IFIX": "https://br.investing.com/indices/bm-fbovespa-real-estate-ifix-historical-data",
    "stooq IFIX": "https://stooq.com/q/d/l/?s=ifix.br&i=d",
}

linhas = [f"Rodado em {dt.datetime.utcnow():%d/%m/%Y %H:%M} UTC"]
for nome, url in FONTES.items():
    t = time.time()
    try:
        r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
        corpo = r.raw.read(700, decode_content=True)
        linhas.append(f"{r.status_code} | {time.time()-t:5.1f}s | {nome} | {r.headers.get('content-type','')} | "
                      f"{r.headers.get('content-length','?')} bytes | início: {corpo[:600]!r}")
    except Exception as e:  # noqa: BLE001
        linhas.append(f"ERRO | {time.time()-t:5.1f}s | {nome} | {type(e).__name__}: {str(e)[:160]}")
Path("docs").mkdir(exist_ok=True)
Path("docs/teste_rede.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
