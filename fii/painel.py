"""Gera o painel: uma página única, que abre em qualquer navegador, sem servidor."""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

import pandas as pd

from . import aprendizado as ap
from . import config

MOLDE = Path(__file__).with_name("painel_molde.html")


def _limpo(v, casas=4):
    if v is None:
        return None
    if isinstance(v, (pd.Timestamp, dt.date, dt.datetime)):
        return str(v)[:10]
    if isinstance(v, float):
        return None if math.isnan(v) or math.isinf(v) else round(v, casas)
    if hasattr(v, "item"):
        return _limpo(v.item(), casas)
    return v


def _registros(df: pd.DataFrame, casas=4) -> list[dict]:
    return [{k: _limpo(v, casas) for k, v in l.items()} for l in df.to_dict("records")]


def montar_dados(con, hoje: dt.date) -> dict:
    ult_pregao = con.execute("select max(data) from cotacoes").fetchone()[0]
    ult_cvm = con.execute("select max(mes) from mensal where vp_cota is not null").fetchone()[0]
    mensal = con.execute("select * from mensal").df()
    fundos = con.execute("select * from fundos").df().set_index("cnpj")
    ult = con.execute("""select c.ticker, c.data, c.fechamento, c.negocios, c.volume from cotacoes c
        join (select ticker, max(data) d from cotacoes group by 1) u on c.ticker=u.ticker and c.data=u.d""").df().set_index("ticker")
    quebras = con.execute("select * from quebras").df()
    suspeitos = set(quebras[(~quebras["confirmada"]) & (quebras["data"] >= pd.Timestamp(hoje) - pd.DateOffset(months=12))]["ticker"])

    lista = []
    for tk, g in mensal.groupby("ticker"):
        if tk not in ult.index or (pd.Timestamp(ult_pregao) - ult.at[tk, "data"]).days > 30:
            continue
        g = g.sort_values("mes")
        preco = float(ult.at[tk, "fechamento"])
        com_vp = g.dropna(subset=["vp_aj"])
        doze = g.tail(13).head(12) if pd.isna(g.iloc[-1]["rend_aj"]) else g.tail(12)
        rend12 = doze["rend_aj"].dropna()
        cad = fundos.loc[g["cnpj"].dropna().iloc[-1]] if g["cnpj"].notna().any() and g["cnpj"].dropna().iloc[-1] in fundos.index else None
        ult_rend = g.dropna(subset=["rend_aj"]).tail(1)
        serie = g.tail(72)
        lista.append({
            "t": tk, "nome": None if cad is None else cad["nome_cvm"], "seg": None if cad is None else cad["segmento"],
            "tipo": ap.tipo_do_fundo(com_vp.iloc[-1]) if len(com_vp) else None,
            "p": preco, "dp": str(ult.at[tk, "data"])[:10],
            "vp": _limpo(com_vp.iloc[-1]["vp_aj"]) if len(com_vp) else None,
            "dvp": str(com_vp.iloc[-1]["mes"])[:7] if len(com_vp) else None,
            "pvp": _limpo(preco / com_vp.iloc[-1]["vp_aj"]) if len(com_vp) and com_vp.iloc[-1]["vp_aj"] else None,
            "r": _limpo(ult_rend.iloc[0]["rend_aj"]) if len(ult_rend) else None,
            "dr": str(ult_rend.iloc[0]["mes"])[:7] if len(ult_rend) else None,
            "or": ult_rend.iloc[0]["origem_rend"] if len(ult_rend) else None,
            "dy12": _limpo(rend12.sum() / preco) if len(rend12) >= 10 and preco else None,
            "cot": _limpo(com_vp.iloc[-1]["cotistas"]) if len(com_vp) else None,
            "pl": _limpo(com_vp.iloc[-1]["pl"], 0) if len(com_vp) else None,
            "vol": _limpo(g.iloc[-1]["vol_medio"], 0),
            "regra": g.iloc[-1]["regra_rend"], "susp": tk in suspeitos,
            "s": [[str(m)[:7], _limpo(p, 2), _limpo(r, 4), _limpo(v, 2)]
                  for m, p, r, v in zip(serie["mes"], serie["preco_fim"], serie["rend_aj"], serie["vp_aj"])],
        })

    op = con.execute("select * from oportunidades").df()
    aprendido = con.execute("select * from aprendido").df()
    aprendido_d10 = con.execute("select * from aprendido_d10").df()
    eventos = con.execute("select * from eventos").df()
    por_ano = con.execute("""select year(mes) ano, count(*) n, median(exc_ini_3) exc3, median(exc_ini_6) exc6,
        avg(case when exc_ini_6 > 0 then 1.0 else 0 end) filter (where exc_ini_6 is not null) acerto6
        from eventos where evento='salto' group by 1 order by 1""").df()
    regras = con.execute("""select regexp_replace(regra_rend, ' \\(.*', '') regra, count(distinct ticker) n
        from mensal group by 1 order by 2 desc""").df()
    sem = con.execute("select ticker, nome, ultimo_pregao, motivo from sem_vinculo where ticker like '%11' "
                      "and ultimo_pregao >= ? order by ticker", [pd.Timestamp(ult_pregao) - pd.DateOffset(days=30)]).df()
    qs = quebras[(~quebras["confirmada"])].sort_values("data", ascending=False).head(40)
    sinais = con.execute("select count(*), min(visto_em), max(visto_em) from sinais").fetchone()

    def grupos(tab):
        t = tab[(tab["casos"] >= 15)]
        return _registros(t)

    return {
        "meta": {"gerado": str(hoje), "ultimo_pregao": str(ult_pregao)[:10], "ultimo_cvm": str(ult_cvm)[:7],
                 "fundos": len(lista), "eventos": int(len(eventos)),
                 "primeiro_ano": int(eventos["mes"].dt.year.min()) if len(eventos) else None,
                 "sinais": sinais[0], "sinais_desde": _limpo(sinais[1]),
                 "horizontes": ap.HORIZONTES, "salto": ap.SALTO, "queda": ap.QUEDA, "min_casos": ap.MIN_CASOS,
                 "volume_minimo": ap.VOLUME_MINIMO},
        "oportunidades": _registros(op),
        "aprendido": grupos(aprendido), "aprendido_d10": grupos(aprendido_d10),
        "por_ano": _registros(por_ano),
        "fundos": lista,
        "qualidade": {"regras": _registros(regras), "sem_vinculo": _registros(sem),
                      "quebras": _registros(qs[["ticker", "data", "ant", "fechamento"]], 2),
                      "sem_vinculo_total": int(len(sem)), "quebras_total": int((~quebras["confirmada"]).sum())},
    }


def gerar(con, hoje: dt.date, destino: Path | None = None) -> Path:
    destino = destino or config.PAINEL
    dados = montar_dados(con, hoje)
    carga = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = MOLDE.read_text(encoding="utf-8").replace("/*__DADOS__*/null", carga)
    destino.write_text(html, encoding="utf-8")
    return destino
