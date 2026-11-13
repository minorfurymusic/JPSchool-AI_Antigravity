"""Estudo: o que acontece depois de um fato relevante de anúncio, com saída por rendimento, notícia ou prazo.

Entrada: pregão seguinte ao fato relevante (i0), a abertura. Saídas, na ordem, no primeiro pregão em que valer:
  1. rendimento caiu: rendimento conhecido no pregão k 10% ou mais abaixo do maior desde a entrada;
  2. fundo declarou redução de rendimento (fato relevante interno);
  3. prazo de 252 pregões (fechamento).
Só com o que era conhecido no dia (rendimento via P.div, fatos classificados).

Uso: PYTHONPATH=. .venv/bin/python estudos/anuncio_saida.py
"""
import warnings

import numpy as np
import pandas as pd

from estudos import desconto as E
from estudos.conservador import rendimentos, selic_liquida
from fii import config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

INICIO = pd.Timestamp("2018-01-01")
PRAZO = 252
QUEDA = 0.90
SUBIDA = 1.05
CUSTO = 0.0006  # 0,03% na compra + 0,03% na venda
IMPOSTO = 0.20
ORIGEM = ["1A venda", "1A multa", "1B", "1C"]
MOTIVOS_ATE_K = ("prazo de 252 pregões", "em aberto")
COLUNAS = ["origem", "ticker", "entrada", "saida", "preco_entrada", "preco_saida", "div0", "maior", "motivo", "pregoes",
           "valorizacao", "rendimento", "total", "liquido", "selic", "subiu", "aumento_max", "aberta"]


def grupos(f):
    m_venda = ((f["tipo"] == "venda_com_ganho") & (f["sentido"] == "alta")).to_numpy()
    m_multa = ((f["tipo"] == "recebimento") & (f["sentido"] == "alta")).to_numpy()
    m_loc = ((f["tipo"] == "locacao_nova") & (f["sentido"] == "alta")).to_numpy()
    m_aum = (f["imp_direcao"] == 1).to_numpy()
    todos = m_venda | m_multa | m_loc | m_aum
    g = f.assign(origem=np.select([m_venda, m_multa, m_loc, m_aum], ORIGEM, default=""))
    return {
        "1A venda com lucro": g[m_venda],
        "1A multa ou indenização": g[m_multa],
        "1B locação nova": g[m_loc],
        "1C aumento declarado": g[m_aum],
        "TODOS": g[todos],
    }


def saida(P, j, i, ruins):
    """Primeiro pregão k > i em que uma das três saídas vale. Devolve (k, motivo, preço, maior rendimento visto)."""
    N = len(P.datas)
    div0 = P.div[i, j]
    maior = div0
    for k in range(i + 1, N):
        d = P.div[k, j]
        if d > maior:  # NaN não entra
            maior = d
        a = P.A[k, j]
        if not np.isnan(a):
            if d <= QUEDA * maior:  # NaN não dispara
                return k, "rendimento caiu", a, maior
            if k in ruins:
                return k, "fundo declarou redução", a, maior
        fk = P.F[k, j]
        if k - i >= PRAZO and not np.isnan(fk):
            return k, "prazo de 252 pregões", fk, maior
    ult = P.F[:, j][~np.isnan(P.F[:, j])]
    return N - 1, "em aberto", ult[-1], maior


def simular(P, linhas):
    ruins = {tk: set(v) for tk, v in P.ruim.items()}
    lin = linhas.assign(i=linhas["i0"].astype(int)).sort_values(["i", "ticker"], kind="stable")
    ocupado_ate = {}
    ops = []
    for r in lin.itertuples(index=False):
        tk, i = r.ticker, r.i
        j = P.col[tk]
        if P.datas[i] < INICIO or i < ocupado_ate.get(tk, -1):  # ainda com operação aberta nesse fundo
            continue
        ent, div0 = P.A[i, j], P.div[i, j]
        if np.isnan(ent) or not P.negociou[i, j] or np.isnan(div0) or div0 <= 0:
            continue
        k, motivo, sai, maior = saida(P, j, i, ruins.get(tk, set()))
        ocupado_ate[tk] = k
        fim = k if motivo in MOTIVOS_ATE_K else k - 1
        valorizacao = sai / ent - 1
        rend = rendimentos(P, tk, i, fim) / ent
        total = valorizacao + rend
        liquido = total - CUSTO - IMPOSTO * max(valorizacao - CUSTO, 0)
        ops.append({"origem": r.origem, "ticker": tk, "entrada": P.datas[i], "saida": P.datas[k],
                    "preco_entrada": ent, "preco_saida": sai, "div0": div0, "maior": maior, "motivo": motivo,
                    "pregoes": k - i, "valorizacao": valorizacao, "rendimento": rend, "total": total, "liquido": liquido,
                    "selic": selic_liquida(P, i, k), "subiu": maior >= SUBIDA * div0, "aumento_max": maior / div0 - 1,
                    "aberta": motivo == "em aberto"})
    return pd.DataFrame(ops, columns=COLUNAS)


def p(x):
    return "n/d" if pd.isna(x) else f"{x * 100:+.1f}%"


def media(df, col):
    return p(df[col].mean()) if len(df) else "n/d"


def linha_fechada(df):
    """quantas | valorização média | rendimento médio | líquido médio | Selic líquida média | pregões médios"""
    if df.empty:
        return "0 | n/d | n/d | n/d | n/d | n/d"
    return (f"{len(df)} | {media(df, 'valorizacao')} | {media(df, 'rendimento')} | {media(df, 'liquido')} | "
            f"{media(df, 'selic')} | {df['pregoes'].mean():.1f}")


def linha_motivo(df):
    """quantas | pregões médios | valorização média | rendimento médio | líquido médio | Selic líquida média"""
    return (f"{len(df)} | {df['pregoes'].mean():.1f} | {media(df, 'valorizacao')} | {media(df, 'rendimento')} | "
            f"{media(df, 'liquido')} | {media(df, 'selic')}")


def linha_aberta(df):
    """quantas | valorização média | rendimento médio | valorização + rendimento | líquido se vendesse hoje | Selic líquida média | pregões médios"""
    if df.empty:
        return "0 | n/d | n/d | n/d | n/d | n/d | n/d"
    return (f"{len(df)} | {media(df, 'valorizacao')} | {media(df, 'rendimento')} | {media(df, 'total')} | "
            f"{media(df, 'liquido')} | {media(df, 'selic')} | {df['pregoes'].mean():.1f}")


def imprimir(nome, ops):
    print(f"\n=== {nome} ===")
    if ops.empty:
        print("Entradas: 0 | Fechadas: 0 | Em aberto: 0")
        return
    ab, fe = ops[ops["aberta"]], ops[~ops["aberta"]]
    print(f"Entradas: {len(ops)} | Fechadas: {len(fe)} | Em aberto: {len(ab)}")
    print("FECHADAS")
    if fe.empty:
        print("  (nenhuma)")
    else:
        pos, neg = fe[fe["valorizacao"] > 0], fe[fe["valorizacao"] < 0]
        print(f"  Com valorização da cota: {len(pos) / len(fe) * 100:.1f}% das fechadas, valorização média {media(pos, 'valorizacao')}")
        print(f"  Com queda da cota: {len(neg) / len(fe) * 100:.1f}% das fechadas, queda média {media(neg, 'valorizacao')}")
        print(f"  Valorização média (todas as fechadas): {media(fe, 'valorizacao')}")
        print(f"  Rendimento médio recebido: {media(fe, 'rendimento')}")
        print(f"  Valorização + rendimento (média): {media(fe, 'total')}")
        print(f"  Depois de custos e imposto (média): {media(fe, 'liquido')}")
        print(f"  Selic líquida no mesmo período (média): {media(fe, 'selic')}")
        print(f"  Operações que ganharam da Selic líquida: {(fe['liquido'] > fe['selic']).mean() * 100:.1f}%")
        print(f"  Pregões entre entrada e saída: média {fe['pregoes'].mean():.1f}, mediana {fe['pregoes'].median():.0f}")
        print(f"  O rendimento subiu 5% ou mais depois da entrada: {fe['subiu'].mean() * 100:.1f}% | "
              f"aumento máximo médio: {media(fe, 'aumento_max')}")
        print("  Por motivo da saída: quantas | pregões médios | valorização média | rendimento médio | líquido médio | Selic líquida média")
        for motivo, g in fe.groupby("motivo"):
            print(f"    {motivo}: {linha_motivo(g)}")
        print("  Só as em que o rendimento subiu 5% ou mais: quantas | valorização média | rendimento médio | líquido médio | Selic líquida média | pregões médios")
        print(f"    {linha_fechada(fe[fe['subiu']])}")
        print("  Só as em que NÃO subiu: quantas | valorização média | rendimento médio | líquido médio | Selic líquida média | pregões médios")
        print(f"    {linha_fechada(fe[~fe['subiu']])}")
    print("EM ABERTO")
    print("  Quantas | valorização média | rendimento médio | valorização + rendimento | líquido se vendesse hoje | Selic líquida média | pregões médios")
    print(f"  {linha_aberta(ab)}")


def conferencia(ops):
    print("\n=== CONFERÊNCIA: 5 operações fechadas do grupo 1C aumento declarado ===")
    fe = ops[~ops["aberta"]].sort_values("entrada").head(5)
    if fe.empty:
        print("(nenhuma operação fechada)")
        return
    cols = ["ticker", "entrada", "saida", "preco_entrada", "preco_saida", "div0", "maior", "motivo", "valorizacao", "rendimento", "total"]
    print(fe[cols].to_string(index=False))
    r = fe.iloc[0]
    print(f"Conta à mão na 1ª ({r['ticker']}): saída/entrada - 1 = {r['preco_saida']:.4f}/{r['preco_entrada']:.4f} - 1 = "
          f"{r['preco_saida'] / r['preco_entrada'] - 1:.6f} | valorização gravada = {r['valorizacao']:.6f}")


def main():
    P = E.preparar()
    f = pd.read_parquet(config.DADOS / "fatos_classificados.parquet")
    validos = [t for t in P.col if t in P.avisos]
    f = f[~f["repetido"] & f["ticker"].isin(validos)]
    res = {}
    for nome, linhas in grupos(f).items():
        res[nome] = simular(P, linhas)
        imprimir(nome, res[nome])
    conferencia(res["1C aumento declarado"])
    res["TODOS"].round(4).to_csv(config.RAIZ / "docs" / "anuncio_saida_operacoes.csv", index=False)
    print(f"\nOperações do grupo TODOS salvas em docs/anuncio_saida_operacoes.csv ({len(res['TODOS'])} linhas)")


if __name__ == "__main__":
    main()
