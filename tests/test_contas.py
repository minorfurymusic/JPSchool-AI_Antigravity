"""Testes das contas: escolha da série de rendimento, vínculo, eventos."""
import numpy as np
import pandas as pd
import pytest

from fii import aprendizado as ap
from fii import base


def meses(n, inicio="2024-01-01"):
    return pd.date_range(inicio, periods=n, freq="MS")


def quadro(a, b, b3, emissao=None):
    n = len(a)
    return pd.DataFrame({"rend_a": a, "rend_b": b, "rend_b3": b3, "emissao": emissao or [False] * n})


def test_serie_usa_conta_que_bate_com_a_b3():
    a = [1.0] * 12
    b = [0.5] * 12
    b3 = [np.nan] * 6 + [1.0] * 6
    final, origem, regra = base.escolher_serie(quadro(a, b, b3))
    assert list(final) == [1.0] * 12 and "conta A" in regra
    assert list(origem) == ["CVM"] * 6 + ["B3"] * 6
    final, _, regra = base.escolher_serie(quadro(b, a, b3))
    assert list(final) == [1.0] * 12 and "conta B" in regra


def test_serie_descarta_historico_que_nao_bate():
    a = [0.002] * 12  # caso real: fundo que não preenche "rendimentos a distribuir"
    b = [0.3] * 12
    b3 = [np.nan] * 6 + [1.0] * 6
    final, origem, regra = base.escolher_serie(quadro(a, b, b3))
    assert final[:6].isna().all() and list(final[6:]) == [1.0] * 6 and "não bate" in regra


def test_serie_sem_b3_exige_que_as_duas_contas_concordem():
    final, _, regra = base.escolher_serie(quadro([1.0] * 8, [1.02] * 8, [np.nan] * 8))
    assert final.notna().all() and "concordam" in regra
    final, _, regra = base.escolher_serie(quadro([1.0] * 8, [0.4] * 8, [np.nan] * 8))
    assert final.isna().all() and "sem histórico" in regra


@pytest.mark.parametrize("r,esperado", [
    ({"referencia": "OUTUBRO/2026", "data_com": "2026-10-30"}, "2026-10-01"),
    ({"referencia": "Setembro-2026/2026", "data_com": "2026-10-15"}, "2026-10-01"),   # formato real da B3
    ({"referencia": "4º QUADRIMESTRE 2025/2026", "data_com": "2026-01-30"}, "2026-01-01"),
    ({"referencia": "", "data_com": None}, None),
])
def test_mes_do_rendimento_e_o_da_data_limite(r, esperado):
    m = base.mes_da_data_com(r)
    assert (None if m is None else str(m.date())) == esperado


def test_papel_com_dois_cnpjs_nos_mesmos_meses_e_ambiguo():
    ms = meses(10)
    troca = pd.DataFrame({"ticker": "AAAA11", "cnpj": ["1"] * 5 + ["2"] * 5, "mes": ms, "pl": 100.0})   # trocou de CNPJ: ok
    duplo = pd.DataFrame({"ticker": "BBBB11", "cnpj": ["3"] * 10 + ["4"] * 10, "mes": list(ms) * 2, "pl": [1.0] * 10 + [2.0] * 10})
    boas, amb = base.resolver_conflitos(pd.concat([troca, duplo]))
    assert amb == {"BBBB11"} and set(boas["ticker"]) == {"AAAA11"} and len(boas) == 10


def test_ajuste_de_desdobramento():
    datas = pd.Series(pd.to_datetime(["2018-04-16", "2018-04-17", "2018-04-18"]))
    quebra = pd.DataFrame({"data": [pd.Timestamp("2018-04-18")], "razao": [0.1]})  # 1 cota virou 10
    assert list(base.fator_de_ajuste(datas, quebra)) == pytest.approx([0.1, 0.1, 1.0])


def mensal_de(rend, emissao=None, ticker="XXXX11", preco=100.0):
    n = len(rend)
    return pd.DataFrame({"ticker": ticker, "mes": meses(n), "rend_aj": rend, "emissao": emissao or [False] * n,
                         "vol_medio": 1e6, "preco_fim": preco, "preco_ini": preco, "preco_d10": preco, "pvp": 1.0,
                         "pct_imoveis": 0.9, "pct_papel": 0.0, "pct_fundos": 0.0, "origem_rend": "CVM", "anuncio_b3": None})


SEM_VENDAS = pd.DataFrame(columns=["ticker", "cnpj", "trimestre", "imovel", "data_venda", "pct_pl"])


def test_salto_e_detectado_uma_vez_e_o_mes_seguinte_vira_salto_mantido():
    ev = ap.detectar(mensal_de([1.0] * 8 + [1.3, 1.3, 1.3, 1.3]), SEM_VENDAS)
    assert list(ev["evento"]) == ["salto", "salto mantido"]
    assert str(ev.iloc[0]["mes"].date()) == "2024-09-01" and ev.iloc[0]["razao"] == pytest.approx(1.3)
    assert ev.iloc[0]["tipo_fundo"] == "tijolo" and not ev.iloc[0]["com_venda"]


def test_variacao_pequena_nao_e_evento():
    assert ap.detectar(mensal_de([1.0] * 8 + [1.2, 0.8, 1.0]), SEM_VENDAS).empty


def test_mes_com_emissao_de_cotas_nao_gera_queda_falsa():
    # caso real HGLG11 11/2025: rendimento por cota "cai" porque entraram cotas novas no meio do mês
    rend = [1.1] * 8 + [0.6] + [1.1] * 3
    assert len(ap.detectar(mensal_de(rend), SEM_VENDAS)) == 1
    assert ap.detectar(mensal_de(rend, emissao=[False] * 8 + [True] + [False] * 3), SEM_VENDAS).empty


def test_valor_absurdo_nao_vira_sinal():
    # caso real HGPO11 05/2026: de R$ 0,04 para R$ 107 por cota
    assert ap.detectar(mensal_de([0.04] * 8 + [107.6, 0.04]), SEM_VENDAS).empty


def test_salto_com_venda_de_imovel_no_periodo():
    vendas = pd.DataFrame({"ticker": ["XXXX11"], "cnpj": ["1"], "trimestre": [pd.Timestamp("2024-09-30")],
                           "imovel": ["Galpão A"], "data_venda": [pd.Timestamp("2024-07-15")], "pct_pl": [0.08]})
    ev = ap.detectar(mensal_de([1.0] * 8 + [1.5, 1.0]), vendas)
    salto = ev[ev["evento"] == "salto"].iloc[0]
    assert salto["com_venda"] and salto["imoveis_vendidos"] == "Galpão A" and salto["pct_venda"] == pytest.approx(0.08)
    assert (ev["evento"] == "venda").sum() == 1


def test_retorno_acima_do_mercado_e_duracao():
    # fundo com salto que dura 3 meses e sobe 2% ao mês; outros 5 fundos parados (são o "mercado")
    alvo = mensal_de([1.0] * 8 + [1.5, 1.5, 1.5, 1.5] + [1.0] * 12)
    alvo["preco_fim"] = [100.0] * 9 + [100 * 1.02 ** k for k in range(1, 16)]
    alvo = alvo.assign(preco_ini=alvo["preco_fim"].shift().fillna(100.0), preco_d10=alvo["preco_fim"])
    outros = [mensal_de([1.0] * 24, ticker=f"OUT{k}11") for k in range(5)]
    m = pd.concat([alvo] + outros, ignore_index=True)
    ev = ap.detectar(m, SEM_VENDAS)
    med = ap.medir(ev[ev["evento"] == "salto"], m, pd.DataFrame(columns=["ticker", "data", "confirmada"]))
    l = med.iloc[0]
    # 3 meses: cota 1,02^3 e rendimento de 1,5 por mês sobre ~100; mercado: 1% ao mês de rendimento, cota parada
    assert l["pre_ini_3"] == pytest.approx(1.02 ** 3 - 1, abs=1e-6)
    assert l["exc_ini_3"] > 0.06 and l["pex_ini_3"] == pytest.approx(1.02 ** 3 - 1, abs=1e-6)
    assert l["duracao"] == 3 and not l["censurado"]
