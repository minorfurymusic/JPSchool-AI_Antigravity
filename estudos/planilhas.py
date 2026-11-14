"""Gera as planilhas (CSV para o Excel) com os dados dos fundos, ano a ano.

Saída: pasta planilhas/ na raiz do repositório.
Rodar com: PYTHONPATH=. .venv/bin/python estudos/planilhas.py
"""
import warnings
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from estudos import desconto as E
from fii import config

warnings.filterwarnings("ignore")

SAIDA = Path(__file__).resolve().parents[1] / "planilhas"
ANOS = list(range(2017, 2027))
OPCOES = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")
DATAS = ["data", "data_conhecido", "data_base", "data_entrada", "data_anuncio"]
FATOR_LIQUIDA = 0.825  # multiplicador da Selic usado no estudo


def arred(x, casas):
    """Arredonda; valores infinitos viram vazio."""
    x = np.asarray(x, dtype=float)
    return np.round(np.where(np.isfinite(x), x, np.nan), casas)


def inteiro(x):
    """Inteiro que aceita vazio (coluna Int64)."""
    return pd.Series(arred(x, 0)).astype("Int64")


def limpa(s):
    """Tira ponto e vírgula, quebra de linha e tabulação de texto livre."""
    return s.fillna("").astype(str).str.replace(r"[;\r\n\t]", " ", regex=True)


def volume_matriz(con, P):
    """Dinheiro negociado bruto por dia e fundo, na mesma grade de P."""
    v = con.execute("select c.ticker, c.data, c.volume from cotacoes c "
                    "join (select distinct ticker from mensal) using(ticker)").df()
    v = v.pivot(index="data", columns="ticker", values="volume").reindex(index=P.datas, columns=P.tickers).fillna(0)
    return v.to_numpy(float)


def tabela_precos(P, V):
    ii, jj = np.nonzero(~np.isnan(P.F))
    F = P.F[ii, jj]
    vp = P.vp[ii, jj]
    with np.errstate(divide="ignore", invalid="ignore"):
        rend_ano = np.where(F > 0, P.div[ii, jj] * 12 / F * 100, np.nan)
        pvp = np.where(vp > 0, F / vp, np.nan)
    return pd.DataFrame({
        "data": P.datas[ii],
        "fundo": np.asarray(P.tickers, dtype=object)[jj],
        "abertura": arred(P.A[ii, jj], 4),
        "maxima": arred(P.H[ii, jj], 4),
        "minima": arred(P.L[ii, jj], 4),
        "fechamento": arred(F, 4),
        "negociou (1/0)": P.negociou[ii, jj].astype(int),
        "volume_dia (R$)": inteiro(V[ii, jj]),
        "volume_medio_60 (R$)": inteiro(P.vol60[ii, jj]),
        "rendimento_mensal (R$/cota)": arred(P.div[ii, jj], 4),
        "rendimento_ano_sobre_preco (%)": arred(rend_ano, 2),
        "valor_patrimonial_cota": arred(vp, 4),
        "preco_sobre_valor_patrimonial": arred(pvp, 4),
        "patrimonio (R$)": inteiro(P.pl[ii, jj]),
        "amortizacao_12m (1/0)": P.amort[ii, jj].astype(int),
    })


def tabela_mercado(P):
    ratio = P.F / P.vp
    ok = (P.vol60 >= 10000) & (ratio >= 0.2) & (ratio <= 3)
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(np.where(ok, ratio, np.nan), axis=1)
    return pd.DataFrame({
        "data": P.datas,
        "selic_ano (%)": arred(P.selic, 4),
        "selic_liquida_ano (%)": arred(P.selic * FATOR_LIQUIDA, 4),
        "indice_mercado": arred(P.mercado, 4),
        "fundos_negociados": P.negociou.sum(axis=1).astype(int),
        "mediana_preco_sobre_valor_patrimonial": arred(med, 4),
    })


def tabela_rendimentos(P):
    n = len(P.datas)
    linhas = []
    for tk, avisos in P.avisos.items():
        for conhecido, base, valor in avisos:
            if 0 <= conhecido < n and 0 <= base < n:
                linhas.append((tk, P.datas[conhecido], P.datas[base], float(valor)))
    df = pd.DataFrame(linhas, columns=["fundo", "data_conhecido", "data_base", "valor (R$/cota)"])
    df["valor (R$/cota)"] = arred(df["valor (R$/cota)"], 4)
    return df.sort_values(["data_conhecido", "fundo"]).reset_index(drop=True)


def tabela_anuncios(P):
    n = len(P.datas)
    f = pd.read_parquet(config.DADOS / "fatos_sem_piso.parquet")
    f = f[f["ticker"].isin(list(P.col))]
    f = f[(f["i0"] >= 0) & (f["i0"] < n)].sort_values("quando").reset_index(drop=True)
    i0 = f["i0"].to_numpy(int)
    jj = f["ticker"].map(P.col).to_numpy(int)
    preco = P.A[i0, jj]
    vp = P.vp[i0, jj]
    div = P.div[i0, jj]
    vol60 = P.vol60[i0, jj]
    selic = P.selic[i0]
    with np.errstate(divide="ignore", invalid="ignore"):
        pvp = np.where(vp > 0, preco / vp, np.nan)
        rend_ano = np.where(preco > 0, div * 12 / preco * 100, np.nan)
    imp = f["imp_direcao"].to_numpy(float)
    return pd.DataFrame({
        "id": f["id"].astype(int).to_numpy(),
        "fundo": f["ticker"].to_numpy(),
        "data_anuncio": f["quando"].dt.strftime("%d/%m/%Y %H:%M").to_numpy(),
        "data_entrada": P.datas[i0],
        "tipo": limpa(f["tipo"]).to_numpy(),
        "sentido": limpa(f["sentido"]).to_numpy(),
        "repetido (1/0)": f["repetido"].astype(int).to_numpy(),
        "continuacao (1/0)": f["continuacao"].astype(int).to_numpy(),
        "declarou_efeito": np.select([imp == 1, imp == -1], ["aumento", "reducao"], default="vazio"),
        "efeito_percentual": arred(f["imp_pct"], 4),
        "valor_por_cota_citado": arred(f["valor_por_cota"], 4),
        "preco_entrada": arred(preco, 4),
        "negociou_na_entrada (1/0)": P.negociou[i0, jj].astype(int),
        "volume_medio_60 (R$)": inteiro(vol60),
        "ordem_maxima (R$)": inteiro(0.02 * vol60),
        "rendimento_mensal_na_entrada (R$/cota)": arred(div, 4),
        "rendimento_ano_sobre_preco (%)": arred(rend_ano, 2),
        "selic_ano (%)": arred(selic, 4),
        "regua_selic_liquida_mais_3 (%)": arred(selic * FATOR_LIQUIDA + 3, 4),
        "valor_patrimonial_cota": arred(vp, 4),
        "preco_sobre_valor_patrimonial": arred(pvp, 4),
        "patrimonio (R$)": inteiro(P.pl[i0, jj]),
        "frase_do_efeito": limpa(f["imp_frase"]).to_numpy(),
        "inicio_do_texto": limpa(f["inicio"]).to_numpy(),
    })


LEIAME = """# Planilhas dos fundos imobiliários (FIIs)

## O que são estes arquivos

Aqui estão os dados dos fundos imobiliários negociados na bolsa, organizados em planilhas para você analisar ano a ano no Excel.

- **Período dos dados:** de {ini} até {fim}.
- **Como abrir:** dê dois cliques no arquivo, ou use Excel > Arquivo > Abrir. Os arquivos já estão no formato do Brasil (as colunas são separadas por ponto e vírgula, e os números usam vírgula). Se tudo aparecer em uma coluna só, use Dados > Texto para Colunas e escolha ponto e vírgula como separador.
- **Cada arquivo tem menos de 1 milhão de linhas**, então abre inteiro no Excel.

## Observações importantes

- **Preços ajustados por desdobramento.** Quando um fundo divide suas cotas em partes (por exemplo, uma cota vira duas), o preço antigo é ajustado para continuar comparável com o preço de hoje.
- **Valor patrimonial e patrimônio só aparecem 75 dias depois do mês a que se referem.** Esse é o prazo em que o fundo costuma divulgar essas informações. Antes disso, a célula fica vazia.
- **Dinheiro (R$)** aparece sem centavos, para facilitar a leitura.

## Arquivos

### precos_AAAA.csv (um arquivo por ano, de 2017 a 2026)

Uma linha por fundo e por dia. Se o fundo ficou alguns dias sem negociar, ainda aparece a última cotação recente, com "negociou" igual a 0.

| Coluna | O que significa |
|---|---|
| data | Dia de negociação |
| fundo | Código do fundo na bolsa |
| abertura | Preço da primeira negociação do dia (R$ por cota) |
| maxima | Preço mais alto do dia (R$ por cota) |
| minima | Preço mais baixo do dia (R$ por cota) |
| fechamento | Preço do último negócio do dia (R$ por cota) |
| negociou (1/0) | 1 se o fundo negociou naquele dia; 0 se não negociou |
| volume_dia (R$) | Dinheiro negociado no dia |
| volume_medio_60 (R$) | Média diária do dinheiro negociado nos 60 dias anteriores |
| rendimento_mensal (R$/cota) | Rendimento por cota que o fundo já tinha anunciado naquele dia |
| rendimento_ano_sobre_preco (%) | Quanto o rendimento mensal daria em 12 meses, em relação ao preço de fechamento |
| valor_patrimonial_cota | Patrimônio do fundo dividido pelo número de cotas (R$ por cota). Aparece 75 dias depois do mês de referência |
| preco_sobre_valor_patrimonial | Preço de fechamento dividido pelo valor patrimonial por cota. Abaixo de 1 significa cota vendida com desconto |
| patrimonio (R$) | Patrimônio líquido do fundo. Aparece 75 dias depois do mês de referência |
| amortizacao_12m (1/0) | 1 se, nos últimos 12 meses, o fundo devolveu aos cotistas uma parte relevante do patrimônio; 0 se não |

### mercado.csv

Uma linha por dia de negociação, com o resumo de todos os fundos.

| Coluna | O que significa |
|---|---|
| data | Dia de negociação |
| selic_ano (%) | Taxa Selic anual naquele dia |
| selic_liquida_ano (%) | Selic multiplicada por 0,825 (é o cálculo usado no estudo) |
| indice_mercado | Índice acumulado que mostra o desempenho médio dos fundos. Começa em 1 no primeiro dia |
| fundos_negociados | Quantos fundos negociaram naquele dia |
| mediana_preco_sobre_valor_patrimonial | Número do meio: metade dos fundos está acima e metade abaixo. Considera só fundos com pelo menos R$ 10 mil negociados por dia, em média, e deixa de fora valores muito fora do normal (abaixo de 0,2 ou acima de 3) |

### rendimentos.csv

Uma linha por aviso de rendimento que os fundos publicaram.

| Coluna | O que significa |
|---|---|
| fundo | Código do fundo na bolsa |
| data_conhecido | Dia em que o aviso passou a ser conhecido pelo mercado |
| data_base | Data de referência do rendimento. Quem tinha a cota nessa data tem direito ao valor |
| valor (R$/cota) | Valor do rendimento por cota |

### anuncios.csv

Uma linha por fato relevante (comunicado importante) publicado por um fundo, com o que aconteceu no preço logo depois do anúncio.

| Coluna | O que significa |
|---|---|
| id | Número de identificação do comunicado |
| fundo | Código do fundo na bolsa |
| data_anuncio | Dia e hora em que o comunicado foi publicado |
| data_entrada | Primeiro dia de negociação em que o mercado pôde reagir ao comunicado |
| tipo | Tipo de comunicado, classificado automaticamente (venda, locação, emissão, rendimento etc.) |
| sentido | Se o comunicado parece positivo (alta), negativo (queda), misto ou neutro |
| repetido (1/0) | 1 se o mesmo assunto já tinha sido comunicado antes |
| continuacao (1/0) | 1 se o comunicado é continuação de outro |
| declarou_efeito | Se o fundo disse que o rendimento vai aumentar, diminuir, ou se não disse nada sobre isso |
| efeito_percentual | Percentual de efeito declarado no comunicado, quando existe |
| valor_por_cota_citado | Valor por cota citado no comunicado (R$) |
| preco_entrada | Preço de abertura no dia de entrada (R$ por cota) |
| negociou_na_entrada (1/0) | 1 se o fundo negociou no dia de entrada |
| volume_medio_60 (R$) | Média diária do dinheiro negociado nos 60 dias anteriores |
| ordem_maxima (R$) | 2% do volume_medio_60: um valor de referência para o tamanho de uma ordem sem mexer muito no preço |
| rendimento_mensal_na_entrada (R$/cota) | Rendimento mensal por cota já conhecido no dia de entrada |
| rendimento_ano_sobre_preco (%) | Quanto o rendimento mensal daria em 12 meses, em relação ao preço de abertura da entrada |
| selic_ano (%) | Taxa Selic anual no dia de entrada |
| regua_selic_liquida_mais_3 (%) | Selic líquida (Selic x 0,825) mais 3 pontos percentuais: uma referência de rendimento |
| valor_patrimonial_cota | Valor patrimonial por cota no dia de entrada (R$) |
| preco_sobre_valor_patrimonial | Preço de abertura da entrada dividido pelo valor patrimonial por cota |
| patrimonio (R$) | Patrimônio líquido do fundo no dia de entrada |
| frase_do_efeito | Trecho do comunicado que diz qual é o efeito |
| inicio_do_texto | Começo do texto do comunicado |
"""


def escrever_leiame(P):
    ini = pd.Timestamp(P.datas[0]).strftime("%d/%m/%Y")
    fim = pd.Timestamp(P.datas[-1]).strftime("%d/%m/%Y")
    (SAIDA / "LEIA-ME.md").write_text(LEIAME.format(ini=ini, fim=fim), encoding="utf-8")


def carregar(nome):
    """Lê de volta uma planilha de planilhas/ (nome sem .csv) no formato certo."""
    df = pd.read_csv(SAIDA / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in DATAS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], dayfirst=True)
    return df


def carregar_precos():
    """Junta todos os precos_AAAA.csv em uma tabela só."""
    arquivos = sorted(SAIDA.glob("precos_*.csv"))
    return pd.concat([carregar(a.stem) for a in arquivos], ignore_index=True)


def main():
    SAIDA.mkdir(exist_ok=True)
    print("Preparando os dados (pode demorar)...")
    P = E.preparar()
    con = duckdb.connect(str(config.BANCO), read_only=True)
    V = volume_matriz(con, P)
    con.close()

    precos = tabela_precos(P, V)
    for ano in ANOS:
        precos[precos["data"].dt.year == ano].to_csv(SAIDA / f"precos_{ano}.csv", **OPCOES)
        print(f"precos_{ano}.csv")
    tabela_mercado(P).to_csv(SAIDA / "mercado.csv", **OPCOES)
    tabela_rendimentos(P).to_csv(SAIDA / "rendimentos.csv", **OPCOES)
    tabela_anuncios(P).to_csv(SAIDA / "anuncios.csv", **OPCOES)
    escrever_leiame(P)
    print("Pronto:", SAIDA)


if __name__ == "__main__":
    main()
