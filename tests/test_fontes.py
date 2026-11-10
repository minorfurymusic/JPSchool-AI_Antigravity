"""Testes contra o formato real das fontes (linhas e respostas copiadas dos arquivos oficiais)."""
import datetime as dt
import io
import json
import zipfile

import pandas as pd
import pytest

from fii import b3_cotacoes, b3_fundos, coleta, cvm

# linha real do COTAHIST de 10/2026 (ação, código 02): não é FII
LINHA_ACAO = (b"012026100102HAGA4       010HAGA S/A    PN           R$  000000000017300000000001750000000000170000000000017400000000001750000000000170"
              b"000000000017400015000000000000021500000000000003753900000000000000009999123100000010000000000000BRHAGAACNPR4103\r\n")


def linha_fii(data="20261109", ticker="HGLG11", fech=14510, isin="BRHGLGCTF004", neg=18184):
    """Monta uma linha no layout real (245 posições), código 12 = fundo imobiliário."""
    l = ("01" + data + "12" + ticker.ljust(12) + "010" + "FII HGLG PAX".ljust(12) + "CI".ljust(10) + "   " + "R$  "
         + f"{14686:013d}{14711:013d}{14427:013d}{14525:013d}{fech:013d}{14510:013d}{14512:013d}"
         + f"{neg:05d}{117600:018d}{1707588734:018d}" + f"{0:013d}" + "0" + "99991231" + f"{1:07d}" + f"{0:013d}" + isin + "118")
    assert len(l) == 245, len(l)
    return (l + "\r\n").encode("latin-1")


def test_linha_real_de_acao_tem_245_posicoes_e_e_ignorada():
    assert len(LINHA_ACAO.rstrip(b"\r\n")) == 245
    assert b3_cotacoes.ler_linha(LINHA_ACAO) is None


def test_linha_de_fii():
    r = b3_cotacoes.ler_linha(linha_fii())
    assert r["ticker"] == "HGLG11" and r["data"] == "2026-11-09" and r["isin"] == "BRHGLGCTF004"
    assert r["fechamento"] == 145.10 and r["abertura"] == 146.86 and r["negocios"] == 18184
    assert r["volume"] == 17075887.34


def test_linha_com_tamanho_errado_para_com_erro():
    with pytest.raises(b3_cotacoes.FormatoInesperado):
        b3_cotacoes.ler_linha(linha_fii()[:200] + b"\r\n")


def test_arquivo_fora_de_ordem_de_data(tmp_path):
    """O arquivo real não vem em ordem de data. O último preço tem que sair pela maior data."""
    corpo = (b"00COTAHIST.2026BOVESPA 20261109\r\n" + linha_fii("20261109", fech=14510) + linha_fii("20261019", fech=15612)
             + linha_fii("20261030", fech=14950) + LINHA_ACAO + b"99COTAHIST.2026BOVESPA 2026110900000000005\r\n")
    zp = tmp_path / "COTAHIST_M112026.ZIP"
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("COTAHIST_M112026.TXT", corpo)
    df = b3_cotacoes.ler_arquivo(zp)
    assert len(df) == 3
    ultimo = df.sort_values("data").groupby("ticker").tail(1).iloc[0]
    assert str(ultimo["data"].date()) == "2026-11-09" and ultimo["fechamento"] == 145.10


def test_arquivo_sem_cabecalho_esperado(tmp_path):
    zp = tmp_path / "x.ZIP"
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("x.TXT", b"qualquer coisa\r\n")
    with pytest.raises(b3_cotacoes.FormatoInesperado):
        b3_cotacoes.ler_arquivo(zp)


CAB_NOVO = "CNPJ_Fundo_Classe;Data_Referencia;Versao;Total_Numero_Cotistas;Patrimonio_Liquido;Cotas_Emitidas;Valor_Patrimonial_Cotas;Percentual_Dividend_Yield_Mes;Percentual_Amortizacao_Cotas_Mes"
CAB_ANTIGO = CAB_NOVO.replace("CNPJ_Fundo_Classe", "CNPJ_Fundo")
LINHA_CVM = "00.332.266/0001-31;2026-01-01;2;3639;258202136.67;2800149;92.2101419138767;0.004342;0"


@pytest.mark.parametrize("cab", [CAB_NOVO, CAB_ANTIGO])
def test_cvm_aceita_cabecalho_novo_e_antigo(cab):
    df = cvm.ler_csv(io.BytesIO((cab + "\n" + LINHA_CVM + "\n").encode("latin-1")), "inf_mensal_fii_complemento")
    assert df.loc[0, "CNPJ_Fundo_Classe"] == "00.332.266/0001-31"
    assert float(df.loc[0, "Valor_Patrimonial_Cotas"]) == pytest.approx(92.2101419)


def test_cvm_para_quando_coluna_some():
    cab = CAB_NOVO.replace("Valor_Patrimonial_Cotas", "VP_Cota")
    with pytest.raises(cvm.CabecalhoMudou) as e:
        cvm.ler_csv(io.BytesIO((cab + "\n" + LINHA_CVM + "\n").encode("latin-1")), "inf_mensal_fii_complemento")
    assert "Valor_Patrimonial_Cotas" in str(e.value)


# resposta real da B3 para HGLG (09/11/2026), reduzida
RESPOSTA_B3 = json.dumps({"quotedPer": "25/06/2010", "fund": "FII HGLG PAX", "quantity": "45.601.745", "code": "HGLG",
    "cashDividends": [{"assetIssued": "BRHGLGCTF004", "paymentDate": "16/11/2026", "rate": "1,17000000000", "relatedTo": "OUTUBRO/2026",
                       "approvedOn": "30/10/2026", "isinCode": "BRHGLGCTF004", "label": "RENDIMENTO", "lastDatePrior": "30/10/2026", "remarks": ""}],
    "stockDividends": [{"assetIssued": "BRHGLGCTF004", "factor": "900,00000000000", "approvedOn": "17/04/2018", "isinCode": "BRHGLGCTF004",
                        "label": "DESDOBRAMENTO", "lastDatePrior": "17/04/2018", "remarks": ""}],
    "subscriptions": [{"assetIssued": "BRHGLGCTF004", "percentage": "19,76415376209", "priceUnit": "166,50000000000",
                       "approvedOn": "14/08/2026", "isinCode": "BRHGLGCTF004", "label": "SUBSCRICAO", "lastDatePrior": "20/08/2026"}]}).encode()


def test_b3_fundo_resposta_real():
    d = b3_fundos.interpretar(RESPOSTA_B3)
    r = d["rendimentos"][0]
    assert r == {"isin": "BRHGLGCTF004", "tipo": "RENDIMENTO", "valor": 1.17, "referencia": "OUTUBRO/2026",
                 "anuncio": "2026-10-30", "data_com": "2026-10-30", "pagamento": "2026-11-16"}
    assert d["desdobramentos"][0]["fator"] == 900.0 and d["subscricoes"][0]["preco"] == 166.5


@pytest.mark.parametrize("bruto", [b"", b"  ", b"{}", b'{"code": null}', b"[]"])
def test_b3_fundo_resposta_vazia(bruto):
    assert b3_fundos.interpretar(bruto) is None


def test_b3_data_invalida_vira_vazio():
    d = b3_fundos.interpretar(json.dumps({"code": "X", "cashDividends": [{"rate": "abc", "lastDatePrior": "31/12/9999 a 25/02/2026"}]}).encode())
    assert d["rendimentos"][0]["valor"] is None and d["rendimentos"][0]["data_com"] is None


def test_acumular_nunca_perde_o_antigo():
    antigo = {"codigo": "HGLG", "rendimentos": [{"data_com": "2025-01-31", "valor": 1.1}], "desdobramentos": [], "subscricoes": []}
    novo = {"codigo": "HGLG", "rendimentos": [{"data_com": "2026-10-30", "valor": 1.17}, {"data_com": "2025-01-31", "valor": 1.1}],
            "desdobramentos": [], "subscricoes": []}
    junto = coleta.acumular(antigo, novo)
    assert len(junto["rendimentos"]) == 2
    assert coleta.acumular(antigo, None) == antigo and coleta.acumular(None, novo) == novo
    so_novo = {"codigo": "HGLG", "rendimentos": [{"data_com": "2026-11-30", "valor": 1.2}], "desdobramentos": [], "subscricoes": []}
    assert len(coleta.acumular(junto, so_novo)["rendimentos"]) == 3


def test_coleta_diaria_sem_rede(tmp_path):
    """Busca um arquivo por dia útil depois do último pregão; feriado (não encontrado) não derruba."""
    pedidos = []

    def buscar(url):
        pedidos.append(url.rsplit("/", 1)[1])
        if "D06112026" in url:
            raise FileNotFoundError(url)
        return b"conteudo"

    for ano in range(2017, 2027):
        (tmp_path / b3_cotacoes.nome_anual(ano)).write_bytes(b"x")
    feitos = coleta.coletar_cotacoes(dt.date(2026, 11, 10), buscar=buscar, pasta=tmp_path, ultimo_pregao=dt.date(2026, 11, 5))
    assert pedidos == ["COTAHIST_D06112026.ZIP", "COTAHIST_D09112026.ZIP", "COTAHIST_D10112026.ZIP"]  # 7 e 8 são fim de semana
    assert feitos == ["COTAHIST_D09112026.ZIP", "COTAHIST_D10112026.ZIP"]
    assert not list(tmp_path.glob("*.part"))
