"""Coletor de documentos do FNET (sistema oficial onde todo FII publica).

Fluxo de cada documento:
    listado  -> baixado -> lido            (aviso de rendimento em XML: lido direto)
                        -> texto           (PDF: texto extraído, aguardando leitura por IA)
             -> erro                       (fica como pendência; pode ser reprocessado)
    ignorado                               (categoria que o app não baixa, só registra)

Nada é apagado: o registro do documento e o arquivo original ficam guardados.

O FNET fica sem resposta com HTTP/2 e responde com HTTP/1.1 (ver PLANO.md,
seção 9). A biblioteca `requests` usa HTTP/1.1.

Uso:
    python -m fii.fnet coletar                 novos documentos desde a última rodada
    python -m fii.fnet coletar --desde 01/11/2026
    python -m fii.fnet rendimentos --desde 01/01/2017   só avisos de rendimento (carga do histórico)
    python -m fii.fnet reler                   relê os avisos já baixados (depois de corrigir o leitor)
    python -m fii.fnet pendencias              mostra o que está com erro ou por fazer
    python -m fii.fnet reprocessar --todos     tenta de novo tudo o que está com erro
    python -m fii.fnet reprocessar --id 1373549
"""
from __future__ import annotations

import datetime as dt
import io
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode

import duckdb
import requests

from . import config

BASE = "https://fnet.bmfbovespa.com.br/fnet/publico/"
BANCO = config.DADOS / "fnet.duckdb"
PASTA = config.DADOS / "bruto" / "fnet"
PAGINA = 200  # o FNET recusa páginas de 1000
CATEGORIA_RENDIMENTO = 14  # "Aviso aos Cotistas - Estruturado"
# categorias cujo arquivo o app baixa; as demais só ficam registradas
BAIXAR = {"Aviso aos Cotistas - Estruturado", "Fato Relevante", "Comunicado ao Mercado", "Aviso aos Cotistas", "Relatórios"}
MAX_TENTATIVAS = 5
ESPERA_RECUSA = 30  # segundos; multiplicado a cada nova tentativa


class RespostaInesperada(Exception):
    pass


# ------------------------------------------------------------------ rede (substituível nos testes)
def buscar(url: str, limite_s: int = 60, tentativas: int = 3) -> tuple[bytes, dict]:
    """Devolve (conteúdo, cabeçalhos). Falha de rede é tentada de novo; resposta de erro do site, não."""
    ultimo = None
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=limite_s)
        except requests.RequestException as e:
            ultimo = f"falha de rede: {type(e).__name__}"
            time.sleep(2 * (i + 1))
            continue
        if r.status_code == 200:
            return r.content, dict(r.headers)
        ultimo = f"o FNET respondeu {r.status_code}"
        # 403 e 429: o FNET recusa por um tempo quando recebe pedidos demais (visto em 11/11/2026,
        # logo depois de uma rajada de consultas; minutos depois voltou a aceitar). Espera e tenta de novo.
        if r.status_code in (403, 429):
            time.sleep(ESPERA_RECUSA * (i + 1))
        elif r.status_code >= 500:
            time.sleep(5 * (i + 1))
        else:
            break
    raise RespostaInesperada(ultimo)


# ------------------------------------------------------------------ banco
def conectar(caminho: Path | None = None):
    caminho = caminho or BANCO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(caminho))
    con.execute("""create table if not exists documentos (
        id bigint primary key, fundo varchar, nome_pregao varchar, categoria varchar, tipo varchar, especie varchar,
        data_referencia varchar, entrega_texto varchar, entrega timestamp, versao integer, situacao varchar,
        cnpj varchar, arquivo varchar, formato varchar, estado varchar, erro varchar, tentativas integer default 0,
        visto_em timestamp, atualizado_em timestamp)""")
    con.execute("""create table if not exists rendimentos_fnet (
        doc_id bigint, cnpj varchar, isin varchar, cod_negociacao varchar, tipo varchar, data_base date, valor double,
        data_pagamento date, periodo varchar, isento varchar, entrega timestamp, versao integer)""")
    return con


def _entrega(txt: str | None):
    """Hora de entrega como o FNET publica ("09/11/2026 21:34"). O FNET não informa o fuso;
    o valor é guardado como veio, sem conversão."""
    try:
        return dt.datetime.strptime(txt, "%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ listar
def url_lista(ini: dt.date, fim: dt.date, inicio: int, categoria: int = 0) -> str:
    q = {"d": 1, "s": inicio, "l": PAGINA, "o[0][dataEntrega]": "asc", "tipoFundo": 1, "idCategoriaDocumento": categoria,
         "idTipoDocumento": 0, "idEspecieDocumento": 0, "dataInicial": f"{ini:%d/%m/%Y}", "dataFinal": f"{fim:%d/%m/%Y}"}
    return BASE + "pesquisarGerenciadorDocumentosDados?" + urlencode(q)


def listar(ini: dt.date, fim: dt.date, categoria: int = 0, buscar=buscar, pausa: float = 0.2):
    """Todas as linhas do período, página a página."""
    inicio, total = 0, None
    while total is None or inicio < total:
        bruto, _ = buscar(url_lista(ini, fim, inicio, categoria))
        try:
            d = json.loads(bruto)
            linhas, total = d["data"], int(d["recordsTotal"])
        except (ValueError, KeyError, TypeError) as e:
            raise RespostaInesperada(f"lista do FNET em formato inesperado: {bruto[:120]!r}") from e
        if not linhas:
            break
        yield from linhas
        inicio += len(linhas)
        time.sleep(pausa)


def registrar(con, linhas, agora: dt.datetime | None = None) -> int:
    """Guarda documentos ainda não vistos. Documento já registrado nunca é sobrescrito."""
    agora = agora or dt.datetime.now()
    novos = 0
    for l in linhas:
        if con.execute("select 1 from documentos where id = ?", [l["id"]]).fetchone():
            continue
        categoria = (l.get("categoriaDocumento") or "").strip()
        estado = "listado" if categoria in BAIXAR else "ignorado"
        con.execute("insert into documentos (id, fundo, nome_pregao, categoria, tipo, especie, data_referencia, entrega_texto, entrega,"
                    " versao, situacao, estado, tentativas, visto_em, atualizado_em) values (?,?,?,?,?,?,?,?,?,?,?,?,0,?,?)",
                    [l["id"], l.get("descricaoFundo"), (l.get("nomePregao") or "").strip() or None, categoria,
                     (l.get("tipoDocumento") or "").strip(), (l.get("especieDocumento") or "").strip(), l.get("dataReferencia"),
                     l.get("dataEntrega"), _entrega(l.get("dataEntrega")), l.get("versao"), l.get("situacaoDocumento"),
                     estado, agora, agora])
        novos += 1
    return novos


# ------------------------------------------------------------------ baixar e ler
def baixar(doc_id: int, buscar=buscar) -> tuple[bytes, str, str | None]:
    """Devolve (conteúdo, formato, cnpj). O CNPJ vem no nome do arquivo que o FNET informa."""
    conteudo, cab = buscar(BASE + f"downloadDocumento?id={doc_id}")
    cab = {k.lower(): v for k, v in cab.items()}
    nome = re.search(r'filename="?([^";]+)', cab.get("content-disposition", ""))
    nome = nome.group(1) if nome else ""
    cnpj = re.match(r"(\d{14})-", nome)
    if not conteudo.strip():
        raise RespostaInesperada("o FNET devolveu arquivo vazio")
    if conteudo[:5] == b"%PDF-":
        formato = "pdf"
    elif conteudo.lstrip()[:5] == b"<?xml" or nome.lower().endswith(".xml"):
        formato = "xml"
    else:
        formato = (nome.rsplit(".", 1)[-1].lower() if "." in nome else "bin")[:8]
    return conteudo, formato, cnpj.group(1) if cnpj else None


def _txt(no, nome):
    x = no.find(nome)
    return x.text.strip() if x is not None and x.text and x.text.strip() else None


def _data(txt):
    try:
        return dt.date.fromisoformat(txt[:10])
    except (TypeError, ValueError):
        return None


def ler_aviso_rendimento(xml: bytes) -> list[dict]:
    """Lê o aviso estruturado. O FNET tem dois formatos:

    novo (de set/2022 em diante): <Provento> com <CodISIN> e, dentro, <Rendimento>/<Amortizacao> com <ValorProvento>;
    antigo: ISIN em <DadosGerais><CodISINCota> e <Rendimento>/<Amortizacao> direto, com <ValorProventoCota>.

    Bloco presente mas vazio é normal (aviso só de rendimento traz <Amortizacao/> vazio).
    Se o arquivo tem valor em algum lugar e nada foi lido, é formato desconhecido: erro, nunca "lido" em silêncio.
    """
    try:
        raiz = ET.fromstring(xml)
    except ET.ParseError as e:
        raise RespostaInesperada(f"XML ilegível: {e}") from e
    if raiz.tag != "DadosEconomicoFinanceiros":
        raise RespostaInesperada(f"XML de tipo inesperado: {raiz.tag}")
    gerais = raiz.find("DadosGerais")
    gerais = gerais if gerais is not None else raiz
    cnpj = _txt(gerais, "CNPJFundo")
    isin_geral, cod_geral = _txt(gerais, "CodISINCota"), _txt(gerais, "CodNegociacaoCota")
    saida = []

    def bloco(no, tipo, isin, cod):
        valor = _txt(no, "ValorProvento") or _txt(no, "ValorProventoCota")
        if valor is None:
            return
        try:
            valor = float(valor.replace(",", "."))
        except ValueError as e:
            raise RespostaInesperada(f"valor ilegível: {valor!r}") from e
        isento = _txt(no, "RendimentoIsentoIR")
        saida.append({"cnpj": cnpj, "isin": isin, "cod_negociacao": cod, "tipo": tipo,
                      "data_base": _data(_txt(no, "DataBase")), "valor": valor,
                      "data_pagamento": _data(_txt(no, "DataPagamento")), "periodo": _txt(no, "PeriodoReferencia"),
                      "isento": {"true": "Sim", "false": "Não"}.get((isento or "").lower(), isento)})

    proventos = list(raiz.iter("Provento"))
    for prov in proventos:
        for tipo in ("Rendimento", "Amortizacao"):
            for no in prov.findall(tipo):
                bloco(no, tipo, _txt(prov, "CodISIN"), _txt(prov, "CodNegociacao"))
    if not proventos:
        informe = raiz.find("InformeRendimentos")
        for tipo in ("Rendimento", "Amortizacao"):
            for no in (informe.findall(tipo) if informe is not None else []):
                bloco(no, tipo, isin_geral, cod_geral)
    if not saida and any((e.text or "").strip() for e in raiz.iter() if e.tag.startswith("ValorProvento")):
        raise RespostaInesperada("aviso com valor em formato que o app não conhece")
    return saida


def texto_do_pdf(pdf: bytes) -> str:
    from pypdf import PdfReader
    leitor = PdfReader(io.BytesIO(pdf))
    return "\n".join((p.extract_text() or "") for p in leitor.pages).strip()


def _caminho(doc_id: int, entrega: dt.datetime | None, formato: str, pasta: Path) -> Path:
    ano = str(entrega.year) if entrega else "sem_data"
    return pasta / ano / f"{doc_id}.{formato}"


def tratar(doc_id: int, entrega, buscar=buscar, pasta: Path | None = None) -> dict:
    """Baixa, guarda o original e lê. Roda fora do banco (pode ir em paralelo). Nunca levanta exceção:
    o erro volta descrito para virar pendência."""
    pasta = pasta or PASTA
    try:
        conteudo, formato, cnpj = baixar(doc_id, buscar)
        arq = _caminho(doc_id, entrega, formato, pasta)
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_bytes(conteudo)
        res = {"id": doc_id, "cnpj": cnpj, "arquivo": str(arq), "formato": formato, "rendimentos": None}
        if formato == "xml":
            res["rendimentos"] = ler_aviso_rendimento(conteudo)
            res["estado"] = "lido"
        elif formato == "pdf":
            txt = texto_do_pdf(conteudo)
            arq.with_suffix(".txt").write_text(txt, encoding="utf-8")
            # PDF só de imagem não tem texto: fica marcado, para leitura por IA com a imagem
            res["estado"] = "texto" if len(txt) >= 80 else "sem_texto"
        else:
            res["estado"] = "baixado"
        return res
    except Exception as e:  # qualquer falha vira pendência com o motivo
        return {"id": doc_id, "estado": "erro", "erro": f"{type(e).__name__}: {e}"[:300]}


def gravar_resultado(con, res: dict, entrega, versao, agora: dt.datetime | None = None) -> None:
    agora = agora or dt.datetime.now()
    if res["estado"] == "erro":
        con.execute("update documentos set estado='erro', erro=?, tentativas=tentativas+1, atualizado_em=? where id=?",
                    [res["erro"], agora, res["id"]])
        return
    con.execute("update documentos set estado=?, erro=null, tentativas=tentativas+1, cnpj=?, arquivo=?, formato=?, atualizado_em=? where id=?",
                [res["estado"], res.get("cnpj"), res.get("arquivo"), res.get("formato"), agora, res["id"]])
    if res.get("rendimentos") is not None:
        con.execute("delete from rendimentos_fnet where doc_id=?", [res["id"]])  # releitura do MESMO documento
        for r in res["rendimentos"]:
            con.execute("insert into rendimentos_fnet values (?,?,?,?,?,?,?,?,?,?,?,?)",
                        [res["id"], r["cnpj"] or res.get("cnpj"), r["isin"], r["cod_negociacao"], r["tipo"], r["data_base"],
                         r["valor"], r["data_pagamento"], r["periodo"], r["isento"], entrega, versao])


def processar(con, estados=("listado",), ids: list[int] | None = None, limite: int | None = None, paralelo: int = 4,
              buscar=buscar, pasta: Path | None = None, avisar=None) -> dict:
    """Trata os documentos nos estados pedidos (ou os ids dados). Devolve a contagem por resultado."""
    if ids is not None:
        linhas = con.execute(f"select id, entrega, versao from documentos where id in ({','.join('?' * len(ids))})", ids).fetchall() if ids else []
    else:
        marcas = ",".join("?" * len(estados))
        linhas = con.execute(f"select id, entrega, versao from documentos where estado in ({marcas}) and tentativas < ? order by entrega"
                             + (f" limit {int(limite)}" if limite else ""), [*estados, MAX_TENTATIVAS]).fetchall()
    contagem: dict[str, int] = {}
    info = {i: (e, v) for i, e, v in linhas}
    with ThreadPoolExecutor(max_workers=max(1, paralelo)) as fila:
        for n, res in enumerate(fila.map(lambda l: tratar(l[0], l[1], buscar, pasta), linhas), start=1):
            gravar_resultado(con, res, *info[res["id"]])
            contagem[res["estado"]] = contagem.get(res["estado"], 0) + 1
            if avisar and n % 500 == 0:
                avisar(n, len(linhas), contagem)
    return contagem


# ------------------------------------------------------------------ rotinas
def coletar(con, hoje: dt.date, desde: dt.date | None = None, categoria: int = 0, buscar=buscar, pasta=None,
            paralelo: int = 4, baixar_arquivos: bool = True) -> dict:
    """Lista o que foi entregue desde a última rodada (com 3 dias de folga) e trata o que falta.
    Se o computador ficou desligado, a próxima rodada cobre o buraco sozinha."""
    if desde is None:
        ultima = con.execute("select max(entrega) from documentos").fetchone()[0]
        desde = (ultima.date() - dt.timedelta(days=3)) if ultima else hoje - dt.timedelta(days=7)
    novos = vistos = 0
    dia = desde
    while dia <= hoje:  # um mês por vez: resposta menor e retomada mais fácil
        fim = min(hoje, (dia.replace(day=1) + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1))
        lote = list(listar(dia, fim, categoria, buscar))
        vistos += len(lote)
        novos += registrar(con, lote)
        dia = fim + dt.timedelta(days=1)
    resultado = processar(con, buscar=buscar, pasta=pasta, paralelo=paralelo) if baixar_arquivos else {}
    return {"periodo": f"{desde:%d/%m/%Y} a {hoje:%d/%m/%Y}", "listados": vistos, "novos": novos, "tratados": resultado,
            "pendencias": pendencias(con)["por_estado"]}


def reler(con, pasta: Path | None = None) -> dict:
    """Lê de novo os avisos de rendimento a partir dos ORIGINAIS guardados, sem baixar nada.
    Serve quando o leitor é corrigido. Só troca as linhas do próprio documento relido."""
    docs = con.execute("select id, arquivo, entrega, versao, cnpj from documentos where formato='xml' and arquivo is not null").fetchall()
    ok = falhas = linhas = 0
    for i, arq, entrega, versao, cnpj in docs:
        try:
            rend = ler_aviso_rendimento(Path(arq).read_bytes())
        except (OSError, RespostaInesperada) as e:
            con.execute("update documentos set estado='erro', erro=?, atualizado_em=? where id=?",
                        [f"{type(e).__name__}: {e}"[:300], dt.datetime.now(), i])
            falhas += 1
            continue
        gravar_resultado(con, {"id": i, "estado": "lido", "cnpj": cnpj, "arquivo": arq, "formato": "xml", "rendimentos": rend}, entrega, versao)
        con.execute("update documentos set tentativas=tentativas-1 where id=?", [i])  # reler do disco não é tentativa de download
        ok += 1
        linhas += len(rend)
    return {"relidos": ok, "com_erro": falhas, "rendimentos_extraidos": linhas}


def pendencias(con) -> dict:
    por_estado = dict(con.execute("select estado, count(*) from documentos group by 1 order by 1").fetchall())
    erros = con.execute("""select id, fundo, categoria, tipo, entrega_texto, tentativas, erro from documentos
                           where estado = 'erro' order by entrega desc limit 200""").fetchall()
    motivos = dict(con.execute("select erro, count(*) from documentos where estado='erro' group by 1 order by 2 desc limit 20").fetchall())
    return {"por_estado": por_estado, "motivos": motivos,
            "erros": [dict(zip(("id", "fundo", "categoria", "tipo", "entrega", "tentativas", "erro"), e)) for e in erros]}


def reprocessar(con, ids: list[int] | None = None, buscar=buscar, pasta=None, paralelo: int = 4) -> dict:
    """Tenta de novo: um documento, uma lista, ou todos os que estão com erro. Devolve o resultado de cada um."""
    if ids is None:
        ids = [r[0] for r in con.execute("select id from documentos where estado='erro'").fetchall()]
    antes = dict(con.execute(f"select id, estado from documentos where id in ({','.join('?' * len(ids))})", ids).fetchall()) if ids else {}
    contagem = processar(con, ids=ids, buscar=buscar, pasta=pasta, paralelo=paralelo)
    depois = con.execute(f"select id, estado, erro from documentos where id in ({','.join('?' * len(ids))})", ids).fetchall() if ids else []
    return {"pedidos": len(ids), "nao_encontrados": [i for i in ids if i not in antes], "resultado": contagem,
            "detalhe": [{"id": i, "antes": antes.get(i), "agora": e, "motivo": m} for i, e, m in depois]}


def _data_arg(args, nome):
    if nome in args:
        return dt.datetime.strptime(args[args.index(nome) + 1], "%d/%m/%Y").date()
    return None


def main(args: list[str]) -> None:
    con = conectar()
    hoje = dt.date.today()
    cmd = args[0] if args else "pendencias"
    if cmd == "coletar":
        saida = coletar(con, hoje, _data_arg(args, "--desde"))
    elif cmd == "rendimentos":
        def avisar(n, total, c):
            print(f"  {n}/{total} {c}", flush=True)
        desde = _data_arg(args, "--desde") or dt.date(2017, 1, 1)
        saida = coletar(con, hoje, desde, CATEGORIA_RENDIMENTO, baixar_arquivos=False)
        print(json.dumps(saida, ensure_ascii=False, default=str), flush=True)
        ids = [r[0] for r in con.execute("select id from documentos where estado='listado' and categoria='Aviso aos Cotistas - Estruturado' order by entrega").fetchall()]
        saida = {"tratados": processar(con, ids=ids, paralelo=4, avisar=avisar), "pendencias": pendencias(con)["por_estado"]}
    elif cmd == "reler":
        saida = reler(con)
    elif cmd == "reprocessar":
        ids = [int(args[args.index("--id") + 1])] if "--id" in args else None
        saida = reprocessar(con, ids)
    else:
        saida = pendencias(con)
    print(json.dumps(saida, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
