"""Transforma eventos recentes em uma lista para o dono olhar, com o que o
histórico de casos parecidos mostrou. Não é ordem de compra."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import aprendizado as ap


def janela_sugerida(grupo: dict) -> int | None:
    """Horizonte em que a valorização mediana acima do mercado foi maior."""
    melhores = [(grupo.get(f"pex_med_{h}"), h) for h in ap.HORIZONTES
                if grupo.get(f"pex_med_{h}") is not None and (grupo.get(f"n_{h}") or 0) >= ap.MIN_CASOS]
    return max(melhores)[1] if melhores else None


def abertas(medidos: pd.DataFrame, aprendido: pd.DataFrame, mensal: pd.DataFrame, ultimo: pd.DataFrame,
            hoje: pd.Timestamp, meses_max: int = 12) -> pd.DataFrame:
    """Saltos de rendimento dos últimos meses em que o rendimento ainda não voltou ao nível anterior."""
    if medidos.empty:
        return pd.DataFrame()
    corte = (hoje.to_period("M") - meses_max).to_timestamp()
    ev = medidos[(medidos["mes"] >= corte)].copy()
    preco = ultimo.set_index("ticker")
    ult_mensal = mensal.sort_values("mes").groupby("ticker").tail(1).set_index("ticker")
    entrada = mensal.set_index(["ticker", "mes"])["preco_ini"]
    vp_atual = mensal.dropna(subset=["vp_aj"]).sort_values("mes").groupby("ticker")["vp_aj"].last().to_dict()
    linhas = []
    for e in ev.itertuples(index=False):
        if e.ticker not in preco.index:
            continue
        atr = {"venda": "com venda de imóvel" if e.com_venda else "sem venda de imóvel",
               "tipo_fundo": e.tipo_fundo, "f_salto": ap.faixa_salto(e.razao)}
        g = ap.melhor_grupo(aprendido, e.evento, atr)
        meses = (hoje.to_period("M") - e.mes.to_period("M")).n
        p_ent = entrada.get((e.ticker, e.mes + pd.DateOffset(months=1)))
        p_ref = p_ent if pd.notna(p_ent) else e.preco_mes
        p_hoje = float(preco.at[e.ticker, "fechamento_aj"])
        janela = janela_sugerida(g) if e.evento != "queda" else None
        if e.evento == "venda":
            situacao = "venda de imóvel informada" if meses <= 12 else "venda antiga"
        elif e.evento in ("salto", "salto mantido"):
            if not e.censurado:
                situacao = "rendimento já voltou ao nível anterior"
            elif meses <= 1:
                situacao = "novo"
            elif janela and meses >= janela:
                situacao = "passou da janela: rever"
            else:
                situacao = "em andamento"
        else:
            situacao = "queda recente" if meses <= 2 else "queda"
        linhas.append({
            "ticker": e.ticker, "evento": e.evento, "mes": e.mes, "anuncio": e.anuncio, "origem": e.origem,
            "rend_antes": e.rend_antes, "rend_novo": e.rend_novo, "variacao": e.razao - 1,
            "com_venda": bool(e.com_venda), "imoveis_vendidos": e.imoveis_vendidos, "pct_venda": e.pct_venda,
            "tipo_fundo": e.tipo_fundo, "pvp": p_hoje / vp_atual.get(e.ticker) if vp_atual.get(e.ticker) else np.nan,
            "preco_referencia": p_ref,
            "preco_hoje": p_hoje, "data_preco": preco.at[e.ticker, "data"],
            "desde": p_hoje / p_ref - 1 if p_ref else np.nan, "meses": meses, "situacao": situacao,
            "aberto": bool(e.censurado), "grupo": g.get("grupo"), "grupo_casos": g.get("casos"),
            "janela": janela,
            **{f"hist_{k}": g.get(k) for k in ("exc_med_3", "exc_med_6", "pre_med_3", "pre_med_6", "pex_med_3",
                                                "pex_med_6", "acerto_6", "subiu10_6", "duracao_med",
                                                "rend_12a18_med", "pct_voltou_12m", "n_6")},
            "rend_atual": ult_mensal.at[e.ticker, "rend_aj"] if e.ticker in ult_mensal.index else np.nan,
        })
    df = pd.DataFrame(linhas)
    if df.empty:
        return df
    ordem = {"venda de imóvel informada": 1, "novo": 0, "em andamento": 1, "passou da janela: rever": 2, "queda recente": 3,
             "rendimento já voltou ao nível anterior": 4, "queda": 5}
    df["_o"] = df["situacao"].map(ordem)
    return df.sort_values(["_o", "mes", "variacao"], ascending=[True, False, False]).drop(columns="_o").reset_index(drop=True)


def registrar(con, abertas_df: pd.DataFrame, hoje: pd.Timestamp) -> int:
    """Guarda cada sinal na primeira vez em que aparece. Nunca apaga nem reescreve:
    é o histórico para conferir depois se o app acertou."""
    con.execute("""create table if not exists sinais (ticker varchar, evento varchar, mes date, visto_em date,
                   preco_quando_visto double, variacao double, com_venda boolean, situacao_inicial varchar)""")
    novos = 0
    for l in abertas_df.itertuples(index=False):
        existe = con.execute("select 1 from sinais where ticker=? and evento=? and mes=?",
                             [l.ticker, l.evento, l.mes.date()]).fetchone()
        if not existe:
            con.execute("insert into sinais values (?,?,?,?,?,?,?,?)",
                        [l.ticker, l.evento, l.mes.date(), hoje.date(), float(l.preco_hoje), float(l.variacao),
                         bool(l.com_venda), l.situacao])
            novos += 1
    return novos
