"""Coletor do FNET para a simulacao do Kairi de 2026 (versao 3): lista e texto dos documentos de cada fundo que deu sinal.

Para cada fundo (por CNPJ) pede a lista de documentos de 01/05/2025 a 13/11/2026 (pesquisarGerenciadorDocumentosDados com
cnpjFundo), fica com as categorias Comunicado ao Mercado, Fato Relevante, Assembleia e Aviso aos Cotistas (o "Aviso aos
Cotistas - Estruturado" e o XML de rendimentos, que ja esta em planilhas/rendimentos_pagamentos.csv, e nao entra) e baixa cada
documento (downloadDocumento?id=). PDF vira texto com `pdftotext -layout`. Pausa de 0,3 s entre pedidos; 403/429 (FNET recusando)
espera e tenta de novo. Nada e inventado: documento que nao pode ser lido fica registrado com a situacao (erro / sem texto).

Os textos completos ficam numa pasta de trabalho FORA do repositorio (variavel KAIRI_FNET_TXT; padrao /tmp/kairi_fnet_txt), um
arquivo por documento; se ja existe, nao baixa de novo. O programa principal le essa pasta.
"""
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import requests

BASE = "https://fnet.bmfbovespa.com.br/fnet/publico/"
CATEGORIAS = {"Comunicado ao Mercado", "Fato Relevante", "Assembleia", "Aviso aos Cotistas"}
PAUSA = 0.3
ESPERA_RECUSA = 30
PASTA = Path(os.environ.get("KAIRI_FNET_TXT", "/tmp/kairi_fnet_txt"))
SESSAO = requests.Session()
LOG = {"pedidos": 0, "recusas": 0, "erros": []}


def pedir(url, params=None, tentativas=6):
    """GET com pausa de 0,3 s e nova tentativa se o FNET recusar (403/429) ou der erro de rede/5xx."""
    ultimo = None
    for i in range(tentativas):
        time.sleep(PAUSA)
        LOG["pedidos"] += 1
        try:
            r = SESSAO.get(url, params=params, timeout=90)
        except requests.RequestException as e:
            ultimo = f"rede: {type(e).__name__}"
            time.sleep(5 * (i + 1))
            continue
        if r.status_code == 200:
            return r
        ultimo = f"HTTP {r.status_code}"
        if r.status_code in (403, 429):
            LOG["recusas"] += 1
            time.sleep(ESPERA_RECUSA * (i + 1))
        elif r.status_code >= 500:
            time.sleep(5 * (i + 1))
        else:
            break
    raise RuntimeError(f"FNET: {url} {ultimo}")


def listar_fundo(cnpj, ini="01/05/2025", fim="13/11/2026"):
    """Todas as linhas (todas as categorias) do fundo no periodo, em paginas de 100."""
    rows, s = [], 0
    while True:
        p = dict(d=1, s=s, l=100, tipoFundo=1, cnpjFundo=cnpj, idCategoriaDocumento=0, idTipoDocumento=0,
                 idEspecieDocumento=0, dataInicial=ini, dataFinal=fim)
        d = pedir(BASE + "pesquisarGerenciadorDocumentosDados", p).json()
        rows += d["data"]
        s += len(d["data"])
        if not d["data"] or s >= int(d["recordsTotal"]):
            return rows, int(d["recordsTotal"])


def texto_de(conteudo, cabecalho):
    """(formato, texto, situacao). PDF -> pdftotext -layout; XML/HTML/texto -> decodificado; outro -> nao lido."""
    if conteudo[:5] == b"%PDF-":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(conteudo)
            nome = f.name
        try:
            out = subprocess.run(["pdftotext", "-layout", nome, "-"], capture_output=True, timeout=120)
            t = out.stdout.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            return "pdf", "", f"erro no pdftotext: {type(e).__name__}"
        finally:
            os.unlink(nome)
        t = re.sub(r"\s+", " ", t).strip()
        return "pdf", t, ("ok" if len(t) >= 40 else "sem texto (PDF sem camada de texto)")
    ini = conteudo.lstrip()[:200].lower()
    if ini.startswith(b"<?xml") or ini.startswith(b"<!doctype html") or ini.startswith(b"<html"):
        t = conteudo.decode("utf-8", "replace")
        t = re.sub(r"<[^>]+>", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return "xml/html", t, ("ok" if len(t) >= 40 else "sem texto")
    return "outro", "", "formato nao lido (nao e PDF nem XML/HTML)"


def baixar_texto(doc_id):
    """Garante PASTA/<id>.txt (cabecalho na 1a linha: formato|situacao; resto = texto). Devolve (formato, situacao, texto)."""
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / f"{doc_id}.txt"
    if arq.exists():
        l1, _, resto = arq.read_text(encoding="utf-8").partition("\n")
        f, s = l1.split("|", 1)
        return f, s, resto
    try:
        r = pedir(BASE + f"downloadDocumento?id={doc_id}")
        f, t, s = texto_de(r.content, r.headers)
    except Exception as e:  # noqa: BLE001
        LOG["erros"].append((doc_id, str(e)))
        return "erro", f"erro: {e}", ""          # nao grava: sera tentado de novo na proxima rodada
    arq.write_text(f"{f}|{s}\n{t}", encoding="utf-8")
    return f, s, t


def coletar(cnpjs, log=print):
    """cnpjs: {fundo: cnpj de 14 digitos}. Devolve lista de dicts (um por documento das categorias pedidas) com o texto completo."""
    out = []
    PASTA.mkdir(parents=True, exist_ok=True)
    for k, (fundo, cnpj) in enumerate(sorted(cnpjs.items()), 1):
        arq_l = PASTA / f"lista_{cnpj}.json"
        if arq_l.exists():
            rows = json.loads(arq_l.read_text(encoding="utf-8"))
        else:
            rows, tot = listar_fundo(cnpj)
            assert len(rows) == tot, (fundo, len(rows), tot)
            rows = [r for r in rows if (r.get("categoriaDocumento") or "").strip() in CATEGORIAS]
            arq_l.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        for r in rows:
            f, s, t = baixar_texto(r["id"])
            out.append(dict(id=int(r["id"]), fundo=fundo, cnpj=cnpj, entrega=r["dataEntrega"], categoria=r["categoriaDocumento"].strip(),
                            tipo=(r.get("tipoDocumento") or "").strip(), especie=(r.get("especieDocumento") or "").strip(),
                            situacao_doc=r.get("situacaoDocumento"), versao=r.get("versao"), formato=f, leitura=s, texto_completo=t))
        log(f"  FNET {k}/{len(cnpjs)} {fundo}: {len(rows)} documentos das categorias pedidas (pedidos ate agora: {LOG['pedidos']}, recusas: {LOG['recusas']})")
    return out
