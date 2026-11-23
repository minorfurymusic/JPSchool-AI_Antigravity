"""Todos os documentos de UM fundo no FNET num período, com o texto (23/11/2026).

O FNET só responde ao GitHub (não a este computador nem ao ambiente do Claude), então o pedido vai num arquivo:
  docs/pedido_fnet.txt  — linha 1: trecho do nome do fundo como o FNET escreve (ex.: PATRIA PLUS)
                          linha 2: data inicial dd/mm/aaaa
O GitHub roda este programa quando o arquivo muda (.github/workflows/fnet-fundo.yml) e grava:
  planilhas/tecnico/fnet_fundo_<NOME>.csv.gz — id, categoria, tipo, data de referência, entrega, link e texto
  docs/fnet_fundo_ultimo.md                  — lista e começo de cada texto

    PYTHONPATH=. python3 estudos/fnet_fundo.py "PATRIA PLUS" 01/09/2026
"""
import datetime as dt
import re
import sys
from pathlib import Path

import pandas as pd

from fii import fnet

nome, ini = sys.argv[1].upper(), dt.datetime.strptime(sys.argv[2], "%d/%m/%Y").date()
hoje = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).date()
linhas = [l for l in fnet.listar(ini, hoje) if nome in (l.get("descricaoFundo") or "").upper()]
L = []
for l in sorted(linhas, key=lambda x: x["id"]):
    txt, formato, erro = "", "", ""
    try:
        conteudo, formato, _ = fnet.baixar(l["id"])
        if formato == "pdf":
            txt = fnet.texto_do_pdf(conteudo)
        elif formato in ("xml", "html", "htm", "txt"):
            txt = re.sub(r"<[^>]+>", " ", conteudo.decode("utf-8", "ignore"))
        else:
            txt = conteudo[:20000].decode("latin-1", "ignore")
    except Exception as e:  # noqa: BLE001
        erro = f"{type(e).__name__}: {e}"[:200]
    L.append({"id": l["id"], "categoria": (l.get("categoriaDocumento") or "").strip(), "tipo": (l.get("tipoDocumento") or "").strip(),
              "especie": (l.get("especieDocumento") or "").strip(), "data_referencia": l.get("dataReferencia"),
              "entrega": l.get("dataEntrega"), "formato": formato, "erro": erro,
              "link": f"https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={l['id']}",
              "caracteres": len(txt), "texto": re.sub(r"\s+", " ", txt).strip()})
D = pd.DataFrame(L)
slug = re.sub(r"[^A-Z0-9]+", "_", nome).strip("_")
Path("planilhas/tecnico").mkdir(parents=True, exist_ok=True)
D.to_csv(f"planilhas/tecnico/fnet_fundo_{slug}.csv.gz", sep=";", index=False, encoding="utf-8", compression={"method": "gzip", "mtime": 0})
md = [f"# FNET — {nome} desde {ini:%d/%m/%Y} (rodado em {hoje:%d/%m/%Y})", "", f"{len(D)} documentos.", ""]
for _, x in D.iterrows():
    md += [f"## {x['id']} — {x['categoria']} / {x['tipo']} — ref. {x['data_referencia']} — entregue {x['entrega']}",
           f"{x['link']} — {x['formato']}, {x['caracteres']} caracteres {x['erro']}", "", x["texto"][:1500], ""]
Path("docs/fnet_fundo_ultimo.md").write_text("\n".join(md), encoding="utf-8")
print(D.drop(columns="texto").to_string(index=False))
