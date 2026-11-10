"""Testes do coletor do FNET, sem rede: respostas copiadas do formato real."""
import datetime as dt
import json

import pytest

from fii import fnet

# aviso real (FNET id 1373300, 09/11/2026), com um bloco de amortização vazio acrescentado
XML_RENDIMENTO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DadosEconomicoFinanceiros><DadosGerais><NomeFundo>SHOPP CIDADE JD FII</NomeFundo><CNPJFundo>15447110000173</CNPJFundo>
<DataInformacao>2026-11-09</DataInformacao><Ano>2026</Ano></DadosGerais>
<InformeRendimentos><Provento><CodISIN>BRALVSCTF003</CodISIN><CodNegociacao>2457320UN1</CodNegociacao>
<Rendimento><AtoSocietarioAprovacao/><DataBase>2026-11-09</DataBase><ValorProvento>0.020453567</ValorProvento>
<DataPagamento>2026-11-16</DataPagamento><PeriodoReferencia>Setembro-2026</PeriodoReferencia><RendimentoIsentoIR>Sim</RendimentoIsentoIR></Rendimento>
<Amortizacao><DataBase/><ValorProvento/><DataPagamento/></Amortizacao>
</Provento></InformeRendimentos></DadosEconomicoFinanceiros>""".encode()

LINHA = {"id": 1373549, "descricaoFundo": "PÁTRIA LOG - FII", "nomePregao": "FII HGLG PAX", "categoriaDocumento": "Fato Relevante",
         "tipoDocumento": "", "especieDocumento": "", "dataReferencia": "09/11/2026", "dataEntrega": "09/11/2026 21:34", "versao": 1,
         "situacaoDocumento": "A"}


def linha(i, categoria="Aviso aos Cotistas - Estruturado", entrega="09/11/2026 19:40"):
    return {**LINHA, "id": i, "categoriaDocumento": categoria, "dataEntrega": entrega}


def falso_fnet(linhas, arquivos, falhar=()):
    """Imita o FNET: lista paginada e download por id."""
    pedidos = []

    def buscar(url):
        pedidos.append(url)
        if "pesquisarGerenciadorDocumentosDados" in url:
            inicio = int(url.split("&s=")[1].split("&")[0])
            return json.dumps({"data": linhas[inicio:inicio + fnet.PAGINA], "recordsTotal": len(linhas)}).encode(), {}
        i = int(url.rsplit("=", 1)[1])
        if i in falhar:
            raise fnet.RespostaInesperada("o FNET respondeu 403")
        conteudo, nome = arquivos[i]
        return conteudo, {"Content-Disposition": f'attachment; filename="{nome}"'}

    buscar.pedidos = pedidos
    return buscar


def test_le_aviso_de_rendimento_real():
    r = fnet.ler_aviso_rendimento(XML_RENDIMENTO)
    assert r == [{"cnpj": "15447110000173", "isin": "BRALVSCTF003", "cod_negociacao": "2457320UN1", "tipo": "Rendimento",
                  "data_base": dt.date(2026, 11, 9), "valor": 0.020453567, "data_pagamento": dt.date(2026, 11, 16),
                  "periodo": "Setembro-2026", "isento": "Sim"}]


@pytest.mark.parametrize("ruim", [b"<html>erro</html>", b"isto nao e xml", b"<Outro/>"])
def test_xml_estranho_vira_erro_claro(ruim):
    with pytest.raises(fnet.RespostaInesperada):
        fnet.ler_aviso_rendimento(ruim)


def test_hora_de_entrega_e_guardada_como_veio():
    assert fnet._entrega("09/11/2026 21:34") == dt.datetime(2026, 11, 9, 21, 34)
    assert fnet._entrega("") is None and fnet._entrega(None) is None


def test_lista_percorre_todas_as_paginas():
    linhas = [linha(i) for i in range(1, 451)]
    b = falso_fnet(linhas, {})
    vistos = list(fnet.listar(dt.date(2026, 11, 1), dt.date(2026, 11, 10), buscar=b, pausa=0))
    assert len(vistos) == 450 and len(b.pedidos) == 3
    assert "dataInicial=01%2F11%2F2026" in b.pedidos[0] and "l=200" in b.pedidos[0]


def test_lista_em_formato_estranho_para_com_erro():
    with pytest.raises(fnet.RespostaInesperada):
        list(fnet.listar(dt.date(2026, 11, 1), dt.date(2026, 11, 2), buscar=lambda u: (b"<html>manutencao</html>", {}), pausa=0))


def test_fluxo_completo_erro_vira_pendencia_e_reprocessa(tmp_path):
    con = fnet.conectar(tmp_path / "f.duckdb")
    linhas = [linha(1), linha(2), linha(3, "Assembleia"), linha(4, "Fato Relevante")]
    arquivos = {1: (XML_RENDIMENTO, "15447110000173-ACE09112026V02-000000001.xml"), 2: (XML_RENDIMENTO, "15447110000173-ACE-2.xml"),
                4: (b"conteudo desconhecido", "11728688000147-FRV09112026V01-000000004.doc")}
    r = fnet.coletar(con, dt.date(2026, 11, 10), dt.date(2026, 11, 9), buscar=falso_fnet(linhas, arquivos, falhar={2}), pasta=tmp_path, paralelo=1)
    assert r["listados"] == 4 and r["novos"] == 4
    assert r["pendencias"] == {"baixado": 1, "erro": 1, "ignorado": 1, "lido": 1}
    assert con.execute("select cnpj, formato from documentos where id=4").fetchone() == ("11728688000147", "doc")
    assert (tmp_path / "2026" / "1.xml").read_bytes() == XML_RENDIMENTO  # original guardado
    assert con.execute("select count(*), max(valor) from rendimentos_fnet").fetchone() == (1, 0.020453567)
    p = fnet.pendencias(con)
    assert p["erros"][0]["id"] == 2 and "403" in p["erros"][0]["erro"] and p["motivos"] == {"RespostaInesperada: o FNET respondeu 403": 1}

    # rodar de novo não duplica nada nem baixa de novo o que já está lido
    b2 = falso_fnet(linhas, arquivos, falhar={2})
    r2 = fnet.coletar(con, dt.date(2026, 11, 10), dt.date(2026, 11, 9), buscar=b2, pasta=tmp_path, paralelo=1)
    assert r2["novos"] == 0 and not [u for u in b2.pedidos if "downloadDocumento" in u]
    assert con.execute("select count(*) from rendimentos_fnet").fetchone()[0] == 1

    # reprocessar a pendência, agora com o FNET respondendo
    rep = fnet.reprocessar(con, buscar=falso_fnet(linhas, arquivos), pasta=tmp_path, paralelo=1)
    assert rep["pedidos"] == 1 and rep["resultado"] == {"lido": 1}
    assert rep["detalhe"] == [{"id": 2, "antes": "erro", "agora": "lido", "motivo": None}]
    assert con.execute("select count(*) from rendimentos_fnet").fetchone()[0] == 2
    assert fnet.pendencias(con)["por_estado"] == {"baixado": 1, "ignorado": 1, "lido": 2}


def test_reprocessar_um_id_que_continua_falhando(tmp_path):
    con = fnet.conectar(tmp_path / "f.duckdb")
    fnet.registrar(con, [linha(7)])
    b = falso_fnet([], {}, falhar={7})
    for _ in range(2):
        rep = fnet.reprocessar(con, [7, 999], buscar=b, pasta=tmp_path, paralelo=1)
    assert rep["nao_encontrados"] == [999] and rep["detalhe"][0]["agora"] == "erro"
    assert con.execute("select tentativas from documentos where id=7").fetchone()[0] == 2


def test_documento_ja_registrado_nao_e_sobrescrito(tmp_path):
    con = fnet.conectar(tmp_path / "f.duckdb")
    assert fnet.registrar(con, [linha(5)]) == 1
    assert fnet.registrar(con, [{**linha(5), "descricaoFundo": "OUTRO NOME"}]) == 0
    assert con.execute("select fundo from documentos where id=5").fetchone()[0] == "PÁTRIA LOG - FII"


def test_arquivo_vazio_vira_pendencia(tmp_path):
    con = fnet.conectar(tmp_path / "f.duckdb")
    fnet.registrar(con, [linha(8)])
    fnet.processar(con, buscar=falso_fnet([], {8: (b"  ", "x.xml")}), pasta=tmp_path, paralelo=1)
    assert con.execute("select estado, erro from documentos where id=8").fetchone() == ("erro", "RespostaInesperada: o FNET devolveu arquivo vazio")


# formato antigo, real (FNET, 2017 e 2021)
XML_ANTIGO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DadosEconomicoFinanceiros xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><DadosGerais><NomeFundo>FII RIO NEGRO</NomeFundo>
<CNPJFundo>15006286000190</CNPJFundo><CodISINCota>BRRNGOCTF003</CodISINCota><CodNegociacaoCota>RNGO11</CodNegociacaoCota></DadosGerais>
<InformeRendimentos><Rendimento><DataAprovacao>2017-06-30</DataAprovacao><DataBase>2017-06-30</DataBase><DataPagamento>2017-07-14</DataPagamento>
<ValorProventoCota>0.54</ValorProventoCota><PeriodoReferencia>JUNHO/2017</PeriodoReferencia><Ano>2017</Ano><RendimentoIsentoIR>true</RendimentoIsentoIR></Rendimento>
<Amortizacao tipo=""/></InformeRendimentos></DadosEconomicoFinanceiros>""".encode()

XML_ANTIGO_AMORTIZACAO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<DadosEconomicoFinanceiros><DadosGerais><CNPJFundo>18369510000104</CNPJFundo><CodISINCota>BRFINFCTF002</CodISINCota><CodNegociacaoCota>FINF11</CodNegociacaoCota></DadosGerais>
<InformeRendimentos><Rendimento>
</Rendimento><Amortizacao tipo="Parcial"><DataBase>2021-02-05</DataBase><DataPagamento>2021-02-12</DataPagamento>
<ValorProventoCota>0.4877</ValorProventoCota><PeriodoReferencia>Fevereiro</PeriodoReferencia></Amortizacao></InformeRendimentos></DadosEconomicoFinanceiros>""".encode()


def test_le_aviso_no_formato_antigo():
    r = fnet.ler_aviso_rendimento(XML_ANTIGO)
    assert r == [{"cnpj": "15006286000190", "isin": "BRRNGOCTF003", "cod_negociacao": "RNGO11", "tipo": "Rendimento",
                  "data_base": dt.date(2017, 6, 30), "valor": 0.54, "data_pagamento": dt.date(2017, 7, 14),
                  "periodo": "JUNHO/2017", "isento": "Sim"}]
    a = fnet.ler_aviso_rendimento(XML_ANTIGO_AMORTIZACAO)
    assert len(a) == 1 and a[0]["tipo"] == "Amortizacao" and a[0]["valor"] == 0.4877 and a[0]["isin"] == "BRFINFCTF002"


def test_valor_em_lugar_desconhecido_nao_passa_em_silencio():
    estranho = b"<DadosEconomicoFinanceiros><Novo><ValorProventoNovo>1.5</ValorProventoNovo></Novo></DadosEconomicoFinanceiros>"
    with pytest.raises(fnet.RespostaInesperada, match="não conhece"):
        fnet.ler_aviso_rendimento(estranho)


def test_reler_do_disco_sem_baixar(tmp_path):
    con = fnet.conectar(tmp_path / "f.duckdb")
    fnet.registrar(con, [linha(1, entrega="30/06/2017 18:00")])
    fnet.processar(con, buscar=falso_fnet([], {1: (XML_ANTIGO, "15006286000190-ACE-1.xml")}), pasta=tmp_path, paralelo=1)
    con.execute("delete from rendimentos_fnet")  # simula o leitor antigo, que não extraía nada
    r = fnet.reler(con)
    assert r == {"relidos": 1, "com_erro": 0, "rendimentos_extraidos": 1}
    assert con.execute("select isin, valor, entrega from rendimentos_fnet").fetchone() == ("BRRNGOCTF003", 0.54, dt.datetime(2017, 6, 30, 18, 0))
    assert con.execute("select estado, tentativas from documentos where id=1").fetchone() == ("lido", 1)
