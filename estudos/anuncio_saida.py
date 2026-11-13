"""Estudo: o que acontece depois de um fato relevante de anúncio, com saída por rendimento, notícia ou prazo.

Entrada: pregão seguinte ao fato relevante (i0), a abertura. Saídas, na ordem, no primeiro pregão em que valer:
  0. fundo saiu da bolsa: preço (F) NaN do pregão k até k+20 (ou até o fim dos dados); vende no último preço anterior;
  1. rendimento caiu: rendimento conhecido no pregão k 10% ou mais abaixo do maior desde a entrada;
  2. fundo declarou redução de rendimento (fato relevante interno);
  3. prazo de 252 pregões (fechamento; sem preço no dia, usa o último anterior).
Só com o que era conhecido no dia (rendimento via P.div, fatos classificados).
Perfil pelo patrimônio líquido no pregão de entrada: AGRESSIVO 50-100 mi, MODERADO 100-400 mi, fora os demais.

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
SEM_PRECO = 21  # pregões seguidos sem preço (k até k+20) para considerar que o fundo saiu da bolsa
QUEDA = 0.90
SUBIDA = 1.05
DESCONTO = 0.90  # pvp na entrada
CUSTO = 0.0006  # 0,03% na compra + 0,03% na venda
IMPOSTO = 0.20
ORIGEM = ["1A venda", "1A multa", "1B", "1C"]
MOTIVOS_ATE_K = ("prazo de 252 pregões", "em aberto")
PERFIS = ["AGRESSIVO", "MODERADO", "conservador (fora)", "pequeno demais (fora)", "sem patrimônio conhecido (fora)"]
SAIU = "fundo saiu da bolsa"
COLUNAS = ["origem", "ticker", "entrada", "saida", "preco_entrada", "preco_saida", "div0", "maior", "motivo", "pregoes",
           "valorizacao", "rendimento", "total", "liquido", "selic", "subiu", "aumento_max", "aberta", "perfil", "pl", "pvp"]
ROTULOS = ["Entradas", "Fechadas", "Em aberto",
           "FECHADAS: pregões entre entrada e saída (média)",
           "FECHADAS em que a cota subiu (% das fechadas)",
           "… valorização média dessas",
           "FECHADAS em que a cota caiu (% das fechadas)",
           "… queda média dessas",
           "FECHADAS: valorização média (todas)",
           "FECHADAS: rendimento médio recebido",
           "FECHADAS: valorização + rendimento (média)",
           "FECHADAS: depois de custos e imposto (média)",
           "FECHADAS: Selic líquida no mesmo período (média)",
           "FECHADAS que ganharam da Selic líquida (%)",
           "FECHADAS em que o rendimento subiu 5% ou mais depois da entrada (%)",
           "EM ABERTO: pregões desde a entrada (média)",
           "EM ABERTO: valorização média",
           "EM ABERTO: rendimento médio recebido",
           "EM ABERTO: valorização + rendimento (média)",
           "EM ABERTO: depois de custos e imposto, se vendesse hoje (média)",
           "EM ABERTO: Selic líquida no mesmo período (média)"]


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


def perfil_de(pl):
    if np.isnan(pl):
        return "sem patrimônio conhecido (fora)"
    if pl < 50e6:
        return "pequeno demais (fora)"
    if pl < 100e6:
        return "AGRESSIVO"
    if pl < 400e6:
        return "MODERADO"
    return "conservador (fora)"


def ultimo_preco(F, k):
    """Índice do último preço (F) não NaN anterior a k, ou None."""
    v = np.flatnonzero(~np.isnan(F[:k]))
    return int(v[-1]) if len(v) else None


def saida(P, j, i, ruins):
    """Primeiro pregão k > i em que uma das saídas vale. Devolve (k, motivo, preço, maior rendimento visto)."""
    N = len(P.datas)
    F = P.F[:, j]
    div0 = P.div[i, j]
    maior = div0
    for k in range(i + 1, N):
        d = P.div[k, j]
        if d > maior:  # NaN não entra
            maior = d
        if np.isnan(F[k]) and np.isnan(F[k:min(k + SEM_PRECO, N)]).all():  # sem preço por 21 pregões: saiu da bolsa
            m = ultimo_preco(F, k)
            return m, SAIU, F[m], maior
        a = P.A[k, j]
        if not np.isnan(a):
            if d <= QUEDA * maior:  # NaN não dispara
                return k, "rendimento caiu", a, maior
            if k in ruins:
                return k, "fundo declarou redução", a, maior
        if k - i >= PRAZO:
            sai = F[k] if not np.isnan(F[k]) else F[ultimo_preco(F, k)]
            return k, "prazo de 252 pregões", sai, maior
    ult = F[~np.isnan(F)]
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
        pl = P.pl[i, j]
        ops.append({"origem": r.origem, "ticker": tk, "entrada": P.datas[i], "saida": P.datas[k],
                    "preco_entrada": ent, "preco_saida": sai, "div0": div0, "maior": maior, "motivo": motivo,
                    "pregoes": k - i, "valorizacao": valorizacao, "rendimento": rend, "total": total, "liquido": liquido,
                    "selic": selic_liquida(P, i, k), "subiu": maior >= SUBIDA * div0, "aumento_max": maior / div0 - 1,
                    "aberta": motivo == "em aberto", "perfil": perfil_de(pl), "pl": pl, "pvp": ent / P.vp[i, j]})
    df = pd.DataFrame(ops, columns=COLUNAS)
    return df.astype({"aberta": bool, "subiu": bool, "pl": float, "pvp": float, "valorizacao": float,
                      "rendimento": float, "total": float, "liquido": float, "selic": float})


def fmt_pct(v):
    return "—" if pd.isna(v) else f"{v * 100:+.1f}%"


def fmt_share(n, den):
    return "—" if den == 0 else f"{n / den * 100:.1f}%"


def fmt_num(v):
    return "—" if pd.isna(v) else f"{v:.1f}"


def coluna(d):
    """Valores das linhas de ROTULOS para um conjunto de operações."""
    fe, ab = d[~d["aberta"]], d[d["aberta"]]
    alta, baixa = fe[fe["valorizacao"] > 0], fe[fe["valorizacao"] < 0]

    def mm(x, col):
        return fmt_pct(x[col].mean())

    return [
        str(len(d)), str(len(fe)), str(len(ab)),
        fmt_num(fe["pregoes"].mean()),
        fmt_share(len(alta), len(fe)), mm(alta, "valorizacao"),
        fmt_share(len(baixa), len(fe)), mm(baixa, "valorizacao"),
        mm(fe, "valorizacao"), mm(fe, "rendimento"), mm(fe, "total"), mm(fe, "liquido"), mm(fe, "selic"),
        fmt_share(int((fe["liquido"] > fe["selic"]).sum()), len(fe)),
        fmt_share(int(fe["subiu"].sum()), len(fe)),
        fmt_num(ab["pregoes"].mean()),
        mm(ab, "valorizacao"), mm(ab, "rendimento"), mm(ab, "total"), mm(ab, "liquido"), mm(ab, "selic"),
    ]


def tabela(perfil, res):
    t = res["TODOS"][res["TODOS"]["perfil"] == perfil]
    cols = {nome: res[nome][res[nome]["perfil"] == perfil] for nome in ["1A venda com lucro", "1A multa ou indenização",
                                                                      "1B locação nova", "1C aumento declarado"]}
    cols["Todas"] = t
    cols["Todas com desconto (pvp <= 0.90)"] = t[t["pvp"] <= DESCONTO]
    cols["Todas sem desconto (pvp > 0.90 ou NaN)"] = t[~(t["pvp"] <= DESCONTO)]
    return pd.DataFrame({nome: coluna(d) for nome, d in cols.items()}, index=ROTULOS)


def linha_motivo(g):
    return (f"{len(g)} | {fmt_num(g['pregoes'].mean())} | {fmt_pct(g['valorizacao'].mean())} | "
            f"{fmt_pct(g['rendimento'].mean())} | {fmt_pct(g['liquido'].mean())} | {fmt_pct(g['selic'].mean())}")


def imprimir_listas(perfil, t):
    fe, ab = t[~t["aberta"]], t[t["aberta"]]
    print(f"Por motivo da saída (coluna Todas, {perfil}, fechadas):")
    print("  quantas | pregões médios | valorização média | rendimento médio | líquido médio | Selic líquida média")
    if fe.empty:
        print("  (nenhuma)")
    for motivo, g in fe.groupby("motivo"):
        print(f"  {motivo}: {linha_motivo(g)}")
    print(f"Em aberto ({perfil}): {len(ab)} operações")
    print("  ticker | data de entrada | preço de entrada | preço atual | pregões | valorização | rendimento | pvp na entrada")
    if ab.empty:
        print("  (nenhuma)")
    for r in ab.sort_values("entrada").itertuples(index=False):
        print(f"  {r.ticker} | {r.entrada:%d/%m/%Y} | {r.preco_entrada:.4f} | {r.preco_saida:.4f} | {r.pregoes} | "
              f"{fmt_pct(r.valorizacao)} | {fmt_pct(r.rendimento)} | {r.pvp:.2f}")


def main():
    P = E.preparar()
    f = pd.read_parquet(config.DADOS / "fatos_classificados.parquet")
    validos = [t for t in P.col if t in P.avisos]
    f = f[~f["repetido"] & f["ticker"].isin(validos)]
    res = {}
    for nome, linhas in grupos(f).items():
        res[nome] = simular(P, linhas)

    todos = res["TODOS"]
    cont = todos["perfil"].value_counts().reindex(PERFIS).fillna(0).astype(int)
    print("Operações do grupo TODOS por perfil: " + " | ".join(f"{k}: {v}" for k, v in cont.items()))

    tabelas = {}
    for perfil in ["MODERADO", "AGRESSIVO"]:
        tabelas[perfil] = tabela(perfil, res)
        print(f"\n=== {perfil} ===")
        print(tabelas[perfil].to_string())
        imprimir_listas(perfil, todos[todos["perfil"] == perfil])

    print("\n=== CONFERÊNCIAS ===")
    em_aberto_252 = sum(int((o.loc[o["aberta"], "pregoes"] >= PRAZO).sum()) for o in res.values())
    print(f"1. Roda sem erro: sim")
    print(f"2. Em aberto com {PRAZO} pregões ou mais: {em_aberto_252} (tem que ser 0)")
    for perfil, T in tabelas.items():
        e, fe, ab = (int(T.loc[x, "Todas"]) for x in ["Entradas", "Fechadas", "Em aberto"])
        d, s, ent = (int(T.loc["Entradas", c]) for c in ["Todas com desconto (pvp <= 0.90)",
                                                          "Todas sem desconto (pvp > 0.90 ou NaN)", "Todas"])
        ok = (fe + ab == e) and (d + s == ent)
        print(f"3. {perfil}: Fechadas {fe} + Em aberto {ab} = Entradas {e}: {fe + ab == e} | "
              f"com desconto {d} + sem desconto {s} = Todas {ent}: {d + s == ent} | {'OK' if ok else 'FALHOU'}")
    saiu = int((todos["motivo"] == SAIU).sum())
    print(f"4. Operações do grupo TODOS que fecharam por \"{SAIU}\": {saiu} (todos os perfis); "
          f"em todos os grupos: {sum(int((o['motivo'] == SAIU).sum()) for o in res.values())}")

    res["TODOS"].round(4).to_csv(config.RAIZ / "docs" / "anuncio_saida_operacoes.csv", index=False)
    print(f"\nOperações do grupo TODOS salvas em docs/anuncio_saida_operacoes.csv ({len(todos)} linhas)")


if __name__ == "__main__":
    main()
