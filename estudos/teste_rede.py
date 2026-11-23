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
FONTES = {  # rodada 3: juro longo (o Tesouro Transparente recusou a conexão do GitHub nas rodadas 1 e 2)
    "Tesouro Transparente (página inicial)": "https://www.tesourotransparente.gov.br/",
    "B3 taxas referenciais DI x IPCA (19/11/2026)": "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data=19/11/2026&Data1=20261119&slcTaxa=DIC",
    "B3 taxas referenciais DI x pré (19/11/2026)": "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data=19/11/2026&Data1=20261119&slcTaxa=PRE",
    "Yahoo dólar (BRL=X)": "https://query1.finance.yahoo.com/v8/finance/chart/BRL%3DX?range=5d&interval=1d",
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
