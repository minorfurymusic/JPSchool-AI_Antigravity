"""Rotina completa: baixa o que falta, monta a base, aprende e gera o painel.

Uso:  python -m fii.atualizar            (com coleta)
      python -m fii.atualizar --sem-rede (só refaz as contas com o que já foi baixado)
"""
from __future__ import annotations

import datetime as dt
import json
import sys

import pandas as pd

from . import aprendizado as ap
from . import base, coleta, config, oportunidades


def ultimo_fechamento(con) -> pd.DataFrame:
    """Último fechamento oficial de cada papel, escolhido pela MAIOR DATA, na base de cotas de hoje."""
    return con.execute("""
        select c.ticker, c.data, c.fechamento, c.fechamento as fechamento_aj, c.abertura, c.maxima, c.minima,
               c.negocios, c.volume
        from cotacoes c join (select ticker, max(data) d from cotacoes group by 1) u
          on c.ticker = u.ticker and c.data = u.d""").df()


def rodar(sem_rede: bool = False, hoje: dt.date | None = None) -> dict:
    hoje = hoje or dt.date.today()
    resumo = {"hoje": str(hoje)}
    con = base.conectar()
    if not sem_rede:
        tem = con.execute("select count(*) from information_schema.tables where table_name='cotacoes'").fetchone()[0]
        ult = con.execute("select max(data) from cotacoes").fetchone()[0].date() if tem else None
        resumo["cvm_baixados"] = len(coleta.coletar_cvm(hoje))
        resumo["b3_baixados"] = coleta.coletar_cotacoes(hoje, ultimo_pregao=ult)
        if tem:
            cods = [r[0] for r in con.execute("""select distinct substr(ticker,1,4) from cotacoes
                    where data >= (select max(data) from cotacoes) - interval 120 day
                      and length(ticker) between 6 and 7 order by 1""").fetchall()]
            resumo["b3_fundos"] = coleta.coletar_fundos_b3(cods)
    resumo["base"] = base.montar(con)
    mensal = con.execute("select * from mensal").df()
    vendas = con.execute("select * from vendas").df()
    quebras = con.execute("select * from quebras").df()
    eventos = ap.detectar(mensal, vendas)
    medidos = ap.medir(eventos, mensal, quebras)
    aprendido = ap.aprender(medidos, "ini")
    aprendido_d10 = ap.aprender(medidos, "d10")
    base.gravar(con, "eventos", medidos)
    base.gravar(con, "aprendido", aprendido)
    base.gravar(con, "aprendido_d10", aprendido_d10)
    ult = ultimo_fechamento(con)
    ab = oportunidades.abertas(medidos, aprendido, mensal, ult, pd.Timestamp(hoje))
    base.gravar(con, "oportunidades", ab)
    resumo["sinais_novos"] = oportunidades.registrar(con, ab, pd.Timestamp(hoje)) if len(ab) else 0
    resumo["eventos"] = {f"{k[0]} {'com' if k[1] else 'sem'} venda": int(v)
                         for k, v in medidos.groupby(["evento", "com_venda"]).size().items()}
    resumo["oportunidades"] = ab["situacao"].value_counts().to_dict() if len(ab) else {}
    try:
        from . import painel
        resumo["painel"] = str(painel.gerar(con, hoje))
    except ImportError:
        pass
    con.close()
    return resumo


if __name__ == "__main__":
    print(json.dumps(rodar(sem_rede="--sem-rede" in sys.argv), ensure_ascii=False, indent=1, default=str))
