"""Detecta eventos de rendimento e mede o que aconteceu depois de cada um.

"Aprender" aqui é isto: toda vez que roda, o app refaz a conta com todo o
histórico disponível. Cada mês novo de dados vira mais casos, e as estimativas
mudam sozinhas. Não há previsão mágica: é estatística de casos parecidos.

Aproximações assumidas (ver LIMITAÇÕES no PLANO.md):
  * no histórico, a data do evento é o fim do mês de referência do informe da
    CVM; a entrada é o fechamento do 1º pregão do mês seguinte;
  * o rendimento do mês de referência k é somado ao retorno do mês k.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

HORIZONTES = [1, 2, 3, 4, 6, 9, 12]
JANELA_BASE = 6
MIN_BASE = 4
SALTO = 1.25
QUEDA = 0.75
VOLUME_MINIMO = 100_000  # R$ por dia, média do mês
VOLTOU = 1.10            # rendimento voltou a até 10% acima do nível anterior
MIN_CASOS = 25
RAZAO_MAXIMA = 10        # rendimento mais de 10x o nível anterior
PAGAMENTO_MAXIMO = 0.15  # ou mais de 15% do preço da cota em um mês


# ------------------------------------------------------------------ eventos
VENDA_MINIMA = 0.03  # venda de pelo menos 3% do patrimônio


def montar_evento(tk, g, i, tipo, razao, base, novo, v) -> dict:
    mes = g.at[i, "mes"]
    pct_venda, imoveis = 0.0, []
    if v is not None:
        perto = v[(v["data_venda"] >= mes - pd.DateOffset(months=9)) & (v["data_venda"] <= mes + pd.DateOffset(months=2))]
        perto = perto.drop_duplicates(subset=["imovel", "data_venda"])
        pct_venda = float(perto["pct_pl"].fillna(0).sum())
        imoveis = sorted(set(perto["imovel"].dropna().astype(str)))[:5]
    return {
        "ticker": tk, "mes": mes, "evento": tipo, "razao": float(razao), "rend_antes": base,
        "rend_novo": float(novo), "preco_mes": g.at[i, "preco_fim"], "pvp": g.at[i, "pvp"],
        "dy_antes": base / g.at[i, "preco_fim"] if g.at[i, "preco_fim"] else np.nan,
        "tipo_fundo": tipo_do_fundo(g.loc[i]), "com_venda": len(imoveis) > 0, "pct_venda": pct_venda,
        "imoveis_vendidos": "; ".join(imoveis), "origem": g.at[i, "origem_rend"],
        "anuncio": g.at[i, "anuncio_b3"] if "anuncio_b3" in g else None,
    }

def tipo_do_fundo(l) -> str:
    if pd.notna(l.get("pct_imoveis")) and l["pct_imoveis"] >= 0.5:
        return "tijolo"
    if pd.notna(l.get("pct_papel")) and l["pct_papel"] >= 0.5:
        return "papel"
    if pd.notna(l.get("pct_fundos")) and l["pct_fundos"] >= 0.5:
        return "fundo de fundos"
    return "misto"


def detectar(mensal: pd.DataFrame, vendas: pd.DataFrame) -> pd.DataFrame:
    """Um evento é o primeiro mês em que o rendimento por cota foge do nível
    dos 6 meses anteriores. Mês com emissão de cotas não conta (distorce a conta)."""
    vendas_por = {tk: g for tk, g in vendas.groupby("ticker")} if len(vendas) else {}
    eventos = []
    for tk, g in mensal.groupby("ticker", sort=False):
        g = g.sort_values("mes").reset_index(drop=True)
        r = g["rend_aj"].where((g["rend_aj"] > 0) & ~g["emissao"])
        ultimo = {"salto": None, "queda": None}
        pendente = None
        for i in range(len(g)):
            if pd.isna(r[i]):
                continue
            if pendente is not None:
                # mês seguinte a um salto: se o rendimento continua alto, o salto "se manteve"
                i0, base0 = pendente
                pendente = None
                if i - i0 <= 2 and r[i] / base0 >= SALTO and g.at[i, "vol_medio"] >= VOLUME_MINIMO:
                    eventos.append(montar_evento(tk, g, i, "salto mantido", r[i] / base0, base0, r[i], vendas_por.get(tk)))
            ant = r[max(0, i - 12):i].dropna().tail(JANELA_BASE)
            if len(ant) < MIN_BASE:
                continue
            base = float(ant.median())
            razao = r[i] / base
            tipo = "salto" if razao >= SALTO else "queda" if razao <= QUEDA else None
            if not tipo:
                continue
            if razao > RAZAO_MAXIMA or r[i] / g.at[i, "preco_fim"] > PAGAMENTO_MAXIMO:
                continue  # valor fora do comum (erro de preenchimento ou devolução de capital): não é sinal
            mes = g.at[i, "mes"]
            if ultimo[tipo] is not None and (mes.to_period("M") - ultimo[tipo].to_period("M")).n <= 6:
                ultimo[tipo] = mes
                continue  # continuação do mesmo movimento
            ultimo[tipo] = mes
            if not (g.at[i, "vol_medio"] >= VOLUME_MINIMO):
                continue
            if tipo == "salto":
                pendente = (i, base)
            eventos.append(montar_evento(tk, g, i, tipo, razao, base, r[i], vendas_por.get(tk)))
        # venda de imóvel relevante informada à CVM (data real da venda)
        v = vendas_por.get(tk)
        if v is not None:
            vm = v.drop_duplicates(subset=["imovel", "data_venda"]).assign(mes=lambda d: d["data_venda"].dt.to_period("M").dt.to_timestamp())
            por_mes = vm.groupby("mes")["pct_pl"].sum()
            pos = {m: k for k, m in enumerate(g["mes"])}
            ultima = None
            for mes, pct in por_mes.items():
                if pct < VENDA_MINIMA or mes not in pos:
                    continue
                if ultima is not None and (mes.to_period("M") - ultima.to_period("M")).n <= 6:
                    continue
                i = pos[mes]
                ant = r[max(0, i - 12):i].dropna().tail(JANELA_BASE)
                if len(ant) < MIN_BASE or not (g.at[i, "vol_medio"] >= VOLUME_MINIMO):
                    continue
                ultima = mes
                base = float(ant.median())
                atual = r[i] if pd.notna(r[i]) else base
                eventos.append(montar_evento(tk, g, i, "venda", atual / base, base, atual, v))
    return pd.DataFrame(eventos)


# ------------------------------------------------------------------ retornos
def retornos_mensais(mensal: pd.DataFrame) -> pd.DataFrame:
    m = mensal.sort_values(["ticker", "mes"]).copy()
    ant = m.groupby("ticker")["preco_fim"].shift()
    mes_ant = m.groupby("ticker")["mes"].shift()
    rend = m["rend_aj"].fillna(0)
    m["tr"] = (m["preco_fim"] + rend) / ant - 1            # mês cheio, com rendimento
    m["tr_ini"] = (m["preco_fim"] + rend) / m["preco_ini"] - 1   # entrando no 1º pregão do mês
    m["tr_d10"] = (m["preco_fim"] + rend) / m["preco_d10"] - 1   # entrando no 10º pregão
    m["pr"] = m["preco_fim"] / ant - 1                     # só preço
    m["pr_ini"] = m["preco_fim"] / m["preco_ini"] - 1
    m["pr_d10"] = m["preco_fim"] / m["preco_d10"] - 1
    # buraco de meses sem negócio: retorno do mês não é confiável
    furo = (m["mes"].dt.year * 12 + m["mes"].dt.month) - (mes_ant.dt.year * 12 + mes_ant.dt.month) != 1
    m.loc[furo, ["tr", "pr"]] = np.nan
    return m


def mercado(ret: pd.DataFrame) -> pd.DataFrame:
    """Retorno do "mercado de FIIs" em cada mês: mediana dos fundos com liquidez."""
    liq = ret[(ret["vol_medio"] >= VOLUME_MINIMO)]
    cols = ["tr", "tr_ini", "tr_d10", "pr", "pr_ini", "pr_d10"]
    limpo = liq[cols].where(liq[cols].abs() < 0.6)
    return limpo.groupby(liq["mes"]).median().add_prefix("mkt_")


def medir(eventos: pd.DataFrame, mensal: pd.DataFrame, quebras: pd.DataFrame) -> pd.DataFrame:
    """Para cada evento: retorno do fundo e do mercado em cada horizonte,
    e por quantos meses o rendimento ficou fora do nível anterior."""
    ret = retornos_mensais(mensal)
    mkt = mercado(ret)
    ret = ret.merge(mkt, left_on="mes", right_index=True, how="left")
    por_ticker = {tk: g.set_index("mes") for tk, g in ret.groupby("ticker")}
    ruins = {}
    if len(quebras):
        for tk, g in quebras[~quebras["confirmada"]].groupby("ticker"):
            ruins[tk] = list(g["data"])
    linhas = []
    for ev in eventos.itertuples(index=False):
        g = por_ticker[ev.ticker]
        meses = [ev.mes + pd.DateOffset(months=k) for k in range(1, max(HORIZONTES) + 7)]
        lin = ev._asdict()
        for entrada in ("ini", "d10"):
            ac_f = ac_m = ac_pf = ac_pm = 1.0
            ok = True
            for k, mes in enumerate(meses[:max(HORIZONTES)], start=1):
                if mes not in g.index:
                    ok = False
                if ok:
                    l = g.loc[mes]
                    suf = f"_{entrada}" if k == 1 else ""
                    vals = [l["tr" + suf], l["mkt_tr" + suf], l["pr" + suf], l["mkt_pr" + suf]]
                    if any(pd.isna(v) for v in vals) or any(mes <= d <= mes + pd.offsets.MonthEnd(0) for d in ruins.get(ev.ticker, [])):
                        ok = False
                    else:
                        ac_f *= 1 + vals[0]; ac_m *= 1 + vals[1]; ac_pf *= 1 + vals[2]; ac_pm *= 1 + vals[3]
                if k in HORIZONTES:
                    lin[f"tot_{entrada}_{k}"] = ac_f - 1 if ok else np.nan       # retorno total do fundo
                    lin[f"exc_{entrada}_{k}"] = ac_f - ac_m if ok else np.nan    # acima do mercado
                    lin[f"pre_{entrada}_{k}"] = ac_pf - 1 if ok else np.nan      # só valorização da cota
                    lin[f"pex_{entrada}_{k}"] = ac_pf - ac_pm if ok else np.nan  # valorização acima do mercado
        # caminho do rendimento depois do evento
        razoes = []
        for mes in meses:
            if mes in g.index and pd.notna(g.at[mes, "rend_aj"]) and g.at[mes, "rend_aj"] > 0 and not g.at[mes, "emissao"]:
                razoes.append(g.at[mes, "rend_aj"] / ev.rend_antes)
            else:
                razoes.append(np.nan)  # mês sem rendimento informado não conta como "voltou"
        # "voltou" = dois meses observados seguidos de volta ao nível anterior (um mês isolado pode ser ruído)
        obs = [(k, rz) for k, rz in enumerate(razoes, start=1) if pd.notna(rz)]
        fora = (lambda rz: rz > 1 / VOLTOU) if ev.evento == "queda" else (lambda rz: rz < VOLTOU)
        lin["duracao"] = np.nan
        for j in range(len(obs) - 1):
            if fora(obs[j][1]) and fora(obs[j + 1][1]):
                lin["duracao"] = obs[j][0] - 1  # meses em que ficou alterado depois do mês do evento
                break
        lin["meses_observados"] = len(obs)
        lin["censurado"] = bool(pd.isna(lin["duracao"]))  # ainda não voltou dentro do que dá para ver
        doze = [x for x in razoes[:12] if pd.notna(x)]
        lin["pico_12"] = float(max(doze)) if doze else np.nan
        lin["meses_altos_12"] = int(sum(x >= SALTO for x in doze)) if doze else np.nan
        depois = [x for x in razoes[11:18] if pd.notna(x)]
        lin["razao_12a18"] = float(np.median(depois)) if depois else np.nan
        linhas.append(lin)
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ o que o histórico ensina
def faixa_salto(rz: float) -> str:
    x = abs(rz - 1) if rz >= 1 else abs(1 / rz - 1)
    return "25 a 50%" if x < 0.5 else "50 a 100%" if x < 1 else "mais de 100%"


def faixa_pvp(p) -> str:
    if pd.isna(p):
        return "sem dado"
    return "abaixo de 0,90" if p < 0.9 else "0,90 a 1,05" if p <= 1.05 else "acima de 1,05"


def resumir(g: pd.DataFrame, entrada: str = "ini") -> dict:
    out = {"casos": int(len(g))}
    for h in HORIZONTES:
        e = g[f"exc_{entrada}_{h}"].dropna()
        p = g[f"pre_{entrada}_{h}"].dropna()
        px = g[f"pex_{entrada}_{h}"].dropna()
        out[f"n_{h}"] = int(len(e))
        out[f"exc_med_{h}"] = float(e.median()) if len(e) else None
        out[f"exc_media_{h}"] = float(e.mean()) if len(e) else None
        out[f"acerto_{h}"] = float((e > 0).mean()) if len(e) else None
        out[f"pre_med_{h}"] = float(p.median()) if len(p) else None
        out[f"pex_med_{h}"] = float(px.median()) if len(px) else None
        out[f"subiu10_{h}"] = float((p >= 0.10).mean()) if len(p) else None
    # duração: quem não voltou em 12 meses conta como 12; quem ainda não deu tempo de ver fica de fora
    conhecidos = g[(~g["censurado"]) | (g["meses_observados"] >= 12)]
    d = conhecidos["duracao"].fillna(12).clip(upper=12)
    out["duracao_med"] = float(d.median()) if len(d) else None
    out["pct_voltou_3m"] = float((d <= 3).mean()) if len(d) else None
    out["pct_voltou_12m"] = float((d < 12).mean()) if len(d) else None
    completos = g[g["meses_observados"] >= 9]
    out["pct_teve_salto_12m"] = float((completos["pico_12"] >= SALTO).mean()) if len(completos) else None
    out["meses_altos_med"] = float(completos["meses_altos_12"].median()) if len(completos) else None
    r = g["razao_12a18"].dropna()
    out["rend_12a18_med"] = float(r.median()) if len(r) else None
    return out


def aprender(medidos: pd.DataFrame, entrada: str = "ini") -> pd.DataFrame:
    """Tabela de grupos de casos parecidos, do mais geral ao mais específico."""
    m = medidos.copy()
    m["venda"] = np.where(m["com_venda"], "com venda de imóvel", "sem venda de imóvel")
    m["f_salto"] = m["razao"].map(faixa_salto)
    m["f_pvp"] = m["pvp"].map(faixa_pvp)
    grupos = [[], ["venda"], ["tipo_fundo"], ["f_salto"], ["f_pvp"], ["venda", "tipo_fundo"],
              ["venda", "f_salto"], ["venda", "f_pvp"], ["tipo_fundo", "f_salto"]]
    linhas = []
    for ev, ge in m.groupby("evento"):
        for cols in grupos:
            partes = [((), ge)] if not cols else ge.groupby(cols)
            for chave, g in partes:
                chave = chave if isinstance(chave, tuple) else (chave,)
                linhas.append({"evento": ev, "criterio": " + ".join(cols) or "todos",
                               "grupo": " | ".join(map(str, chave)) or "todos os casos", **resumir(g, entrada)})
    return pd.DataFrame(linhas)


def melhor_grupo(aprendido: pd.DataFrame, evento: str, atributos: dict) -> dict:
    """Grupo mais específico com casos suficientes para o evento novo."""
    ordem = [("venda + tipo_fundo", f"{atributos['venda']} | {atributos['tipo_fundo']}"),
             ("venda + f_salto", f"{atributos['venda']} | {atributos['f_salto']}"),
             ("venda", atributos["venda"]), ("todos", "todos os casos")]
    a = aprendido[aprendido["evento"] == evento]
    for criterio, grupo in ordem:
        l = a[(a["criterio"] == criterio) & (a["grupo"] == grupo)]
        if len(l) and l.iloc[0]["n_6"] >= MIN_CASOS:
            return l.iloc[0].to_dict()
    l = a[a["criterio"] == "todos"]
    return l.iloc[0].to_dict() if len(l) else {}
