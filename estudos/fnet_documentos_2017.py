"""FNET de 2017 a 2026 para uma lista de fundos: fatos relevantes e comunicados ao mercado (texto completo numa pasta de
trabalho fora do repositório; os primeiros 5.000 caracteres vão para planilhas/tecnico/fnet_2017_documentos.csv.gz).

Usa as funções de estudos/kairi_fnet_2026.py (pausa de 0,3 s, nova tentativa quando o FNET recusa). CNPJ de cada fundo vem
do informe trimestral da CVM (planilhas/tecnico/cobertura_trimestral.csv, pelo ISIN).

    PYTHONPATH=. python3 estudos/fnet_documentos_2017.py FUNDO11 FUNDO11 ...
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("KAIRI_FNET_TXT", "/tmp/claude-0/fnet_2017_txt")
import pandas as pd  # noqa: E402

from estudos import kairi_fnet_2026 as KF  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "planilhas" / "tecnico" / "fnet_2017_documentos.csv.gz"
CATEG = {"Fato Relevante", "Comunicado ao Mercado"}
OP = dict(sep=";", encoding="utf-8-sig")


def cnpjs(fundos):
    T = pd.read_csv(RAIZ / "planilhas/tecnico/cobertura_trimestral.csv", dtype=str, **OP)
    m = T.drop_duplicates("fundo", keep="last").set_index("fundo")["cnpj"].str.replace(r"\D", "", regex=True)
    return {f: m[f] for f in fundos if f in m.index}


def coletar(mapa, log=print):
    out = []
    for k, (fundo, cnpj) in enumerate(sorted(mapa.items()), 1):
        arq = KF.PASTA / f"lista17_{cnpj}.json"
        KF.PASTA.mkdir(parents=True, exist_ok=True)
        if arq.exists():
            rows = json.loads(arq.read_text(encoding="utf-8"))
        else:
            rows, tot = KF.listar_fundo(cnpj, ini="01/01/2017", fim="17/11/2026")
            assert len(rows) == tot, (fundo, len(rows), tot)
            rows = [r for r in rows if (r.get("categoriaDocumento") or "").strip() in CATEG]
            arq.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        for r in rows:
            f, s, t = KF.baixar_texto(r["id"])
            out.append({"id": int(r["id"]), "fundo": fundo, "cnpj": cnpj, "data de entrega": r["dataEntrega"],
                        "categoria": r["categoriaDocumento"].strip(), "tipo": (r.get("tipoDocumento") or "").strip(),
                        "formato": f, "leitura": s, "texto (primeiros 5.000 caracteres)": t[:5000]})
        log(f"  {k}/{len(mapa)} {fundo}: {len(rows)} documentos (pedidos: {KF.LOG['pedidos']}, recusas: {KF.LOG['recusas']})", flush=True)
    return pd.DataFrame(out)


if __name__ == "__main__":
    fundos = sys.argv[1:]
    mapa = cnpjs(fundos)
    print("sem CNPJ:", sorted(set(fundos) - set(mapa)))
    D = coletar(mapa)
    if SAIDA.exists():
        D = pd.concat([pd.read_csv(SAIDA, **OP), D]).drop_duplicates(["id", "fundo"], keep="last")
    D.to_csv(SAIDA, index=False, **OP)
    print(f"gravado: {SAIDA.relative_to(RAIZ)} ({len(D)} documentos; leitura: {D['leitura'].value_counts().to_dict()}; "
          f"erros: {len(KF.LOG['erros'])})")
