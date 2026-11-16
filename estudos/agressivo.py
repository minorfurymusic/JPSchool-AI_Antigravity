"""Estudo agressivo: operações do anúncio de saída (PL >= 50 mi, P/VP 0,30 a 0,60).

Acrescenta tipo do fundo, mercado (preço contra preço), Selic, gráfico e dividendos
às operações, e imprime os resumos R1 a R14 e as conferências.

Saídas: planilhas/fundos.csv, planilhas/estudo_agressivo.csv e a impressão no terminal.
Rodar com: PYTHONPATH=. .venv/bin/python estudos/agressivo.py 2>&1 | tee dados/agressivo_resumo.txt
"""
import warnings
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from estudos.planilhas import carregar, carregar_precos
from fii import config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)

RAIZ = Path(__file__).resolve().parents[1]
PLAN = RAIZ / "planilhas"
DOCS = RAIZ / "docs"
VAL = "valor (R$/cota)"
OPCOES = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")
NAN = np.nan

# Segmento como vem da CVM (tabela fundos.segmento) -> tipo simplificado
MAPA_SEG = {
    "Lajes Corporativas": "Lajes corporativas",
    "Escritórios": "Lajes corporativas",
    "Logística": "Logística",
    "Shoppings": "Shoppings",
    "Títulos e Val. Mob.": "Papel (títulos)",
    "Híbrido": "Híbrido",
    "Multicategoria": "Outros",
    "Outros": "Outros",
    "Residencial": "Outros",
    "Hospital": "Outros",
    "Hotel": "Outros",
    "Varejo": "Outros",
    "Educacional": "Outros",
}


# ---------- formatação ----------
def P(x, c=1):
    return "-" if x is None or pd.isna(x) else f"{x * 100:.{c}f}%".replace(".", ",")


def N(x, c=1):
    return "-" if x is None or pd.isna(x) else f"{x:.{c}f}".replace(".", ",")


def D(x):
    return "-" if x is None or pd.isna(x) else pd.Timestamp(x).strftime("%d/%m/%Y")


def PP(x):
    return "-" if x is None or pd.isna(x) else f"{x:+.2f}".replace(".", ",") + " p.p."


# ---------- passo 0: tipo do fundo ----------
def tipo_de(seg):
    if pd.isna(seg):
        return "Sem informação"
    if seg not in MAPA_SEG:
        print(f"  ATENÇÃO: segmento não mapeado: {seg} (vira Outros)")
        return "Outros"
    return MAPA_SEG[seg]


def passo0(con):
    print("== describe fundos")
    print(con.sql("describe fundos").df().to_string())
    print("== show tables:", ", ".join(con.sql("show tables").df()["name"]))

    vin = con.sql(
        "select v.ticker, v.nome, f.segmento, f.mandato "
        "from vinculo v left join fundos f on f.cnpj = v.cnpj"
    ).df()
    vin["_ok"] = vin.segmento.notna()
    vin = vin.sort_values(["ticker", "_ok"], ascending=[True, False]).drop_duplicates("ticker")
    vin = vin.drop(columns="_ok").reset_index(drop=True)
    vin["tipo"] = vin.segmento.map(tipo_de)

    print("\n== mapeamento segmento (valor original) -> tipo  [tickers]")
    mp = vin.assign(seg=vin.segmento.fillna("(vazio)")).groupby(["seg", "tipo"]).size()
    for (seg, tp), n in mp.items():
        print(f"  {seg} -> {tp}  [{n}]")

    PLAN.mkdir(exist_ok=True)
    out = pd.DataFrame({
        "fundo": vin.ticker,
        "nome": vin.nome.fillna(""),
        "segmento": vin.segmento.fillna(""),
        "mandato": vin.mandato.fillna(""),
        "tipo": vin.tipo,
    })
    out.to_csv(PLAN / "fundos.csv", **OPCOES)
    print(f"\nfundos.csv: {len(out)} tickers")
    return dict(zip(vin.ticker, vin.tipo))


# ---------- passo 1: operações ----------
def passo1(TIPO):
    ops = pd.read_csv(DOCS / "anuncio_saida_operacoes.csv", parse_dates=["entrada", "saida"])
    total = len(ops)
    ops = ops[(ops.pl >= 50e6) & (ops.pvp >= 0.30) & (ops.pvp < 0.60) & (ops.ticker != "XPPR11")]
    ops = ops.reset_index(drop=True)
    ops["aberta"] = ops["aberta"].astype(bool)
    print(f"\nOperações no arquivo: {total}; após filtro: {len(ops)}; "
          f"fechadas: {(~ops.aberta).sum()}; em aberto: {ops.aberta.sum()}")
    if len(ops) != 37:
        raise SystemExit(f"PAROU: deu {len(ops)} operações, esperado 37.")

    ops["tipo"] = ops.ticker.map(TIPO)
    ov = ops.ordem_max
    ops["faixa_ordem"] = np.select(
        [ov.isna(), ov < 200, ov < 500, ov < 4000, ov >= 4000],
        ["sem dado", "abaixo de R$ 200", "R$ 200 a 500", "R$ 500 a 4.000", "R$ 4.000 ou mais"],
        default="?",
    )
    ops["faixa_desconto"] = np.where(ops.pvp < 0.45, "0,30 a 0,45", "0,45 a 0,60")
    v = ops.valorizacao
    ops["val_liquida"] = v - 0.0006 - 0.20 * np.maximum(v - 0.0006, 0)
    ops["dif_selic"] = ops.liquido - ops.selic
    return ops


def precos_op(F, V60, A, TIPO_F, e, s, t, tipo):
    """Mercado (preço contra preço) e preço do próprio fundo, entrada -> saída."""
    out = dict(fundo_preco=NAN, mercado_preco=NAN, tipo_preco=NAN)
    if e not in F.index or s not in F.index:
        return out
    fe, fs = F.loc[e], F.loc[s]
    base = (V60.loc[e] >= 10000) & fe.notna() & fs.notna() & (fe > 0)
    ret = fs[base] / fe[base] - 1
    if len(ret):
        out["mercado_preco"] = ret.median()
    if isinstance(tipo, str):
        mt = ret[TIPO_F.reindex(ret.index) == tipo]
        if len(mt) >= 5:
            out["tipo_preco"] = mt.median()
    if t in F.columns and pd.notna(fe[t]) and pd.notna(fs[t]) and fe[t] > 0:
        out["fundo_preco"] = fs[t] / fe[t] - 1
    return out


def grafico(F, e, t):
    """Indicadores com fechamentos ATÉ a véspera da entrada."""
    out = dict(mm200=NAN, mm50=NAN, acima_mm200=NAN, acima_mm50=NAN,
               ret60=NAN, dist_max252=NAN)
    if t not in F.columns:
        return out
    v = F[t].dropna()
    v = v[v.index < e]
    if not len(v):
        return out
    last = v.iloc[-1]
    if len(v) >= 200:
        out["mm200"] = v.iloc[-200:].mean()
        out["acima_mm200"] = bool(last > out["mm200"])
    if len(v) >= 50:
        out["mm50"] = v.iloc[-50:].mean()
        out["acima_mm50"] = bool(last > out["mm50"])
    if len(v) >= 61:
        out["ret60"] = last / v.iloc[-61] - 1
    if len(v) >= 253:  # 252 pregões anteriores à véspera
        out["dist_max252"] = last / v.iloc[-253:-1].max() - 1
    return out


def div_entrada(r, anu, rend, DI):
    out = dict(data_anuncio=pd.NaT, perdeu_dividendo=NAN,
               dividendo_perdido_pct=NAN, pregoes_ate_data_base=NAN)
    a = anu[(anu.fundo == r.ticker) & (anu.data_entrada == r.entrada)].sort_values("data_anuncio")
    if a.empty:
        return out, True
    dA = a.data_anuncio.iloc[0].normalize()
    out["data_anuncio"] = dA
    av = rend[rend.fundo == r.ticker]
    perd = av[(av.data_base >= dA) & (av.data_base < r.entrada)]
    out["perdeu_dividendo"] = int(len(perd) > 0)
    out["dividendo_perdido_pct"] = perd[VAL].sum() / r.preco_entrada
    fut = av.loc[av.data_base >= r.entrada, "data_base"]
    if len(fut):
        out["pregoes_ate_data_base"] = DI.searchsorted(fut.min()) - DI.searchsorted(r.entrada)
    return out, False


def div_saida(r, rend, A):
    out = dict(esperar_aplica=0, data_base_saida=pd.NaT, valor_aviso_saida=NAN,
               saida_alt=pd.NaT, preco_saida_alt=NAN, total_alt=NAN, ganho_esperar=NAN)
    if "rendimento caiu" not in str(r.motivo):
        return out
    av = rend[(rend.fundo == r.ticker) & (rend.data_conhecido == r.saida)]
    if av.empty:
        return out
    aviso = av.sort_values("data_base").iloc[-1]
    out["data_base_saida"] = aviso.data_base
    out["valor_aviso_saida"] = aviso[VAL]
    if pd.isna(aviso.data_base) or aviso.data_base < r.saida:
        return out
    out["esperar_aplica"] = 1
    if r.ticker not in A.columns:
        return out
    Ai = A[r.ticker].dropna()
    dep = Ai[Ai.index > aviso.data_base]
    if dep.empty:
        return out
    out["saida_alt"] = dep.index[0]
    out["preco_saida_alt"] = dep.iloc[0]
    out["total_alt"] = dep.iloc[0] / r.preco_entrada - 1 + r.rendimento + aviso[VAL] / r.preco_entrada
    out["ganho_esperar"] = out["total_alt"] - r.total
    return out


def montar_colunas(ops, F, V60, A, TIPO, SELIC, DI, anu, rend):
    TIPO_F = pd.Series(TIPO).reindex(F.columns)
    linhas, sem_anuncio, sem_precos = [], 0, 0
    for _, r in ops.iterrows():
        d = {}
        d.update(precos_op(F, V60, A, TIPO_F, r.entrada, r.saida, r.ticker, r.tipo))
        if r.entrada not in F.index or r.saida not in F.index:
            sem_precos += 1
        d.update(grafico(F, r.entrada, r.ticker))
        de, falta = div_entrada(r, anu, rend, DI)
        sem_anuncio += falta
        d.update(de)
        d.update(div_saida(r, rend, A))
        d["selic_entrada"] = SELIC.get(r.entrada, NAN)
        d["selic_saida"] = SELIC.get(r.saida, NAN)
        linhas.append(d)
    novas = pd.DataFrame(linhas)
    novas["var_selic"] = novas.selic_saida - novas.selic_entrada
    novas["regime_selic"] = np.select(
        [novas.var_selic >= 0.5, novas.var_selic <= -0.5], ["subindo", "caindo"], default="estável")
    novas["excesso_mercado"] = novas.fundo_preco - novas.mercado_preco
    novas["excesso_tipo"] = novas.fundo_preco - novas.tipo_preco
    print(f"\nDiagnósticos: operações sem anúncio casado: {sem_anuncio}; "
          f"entrada ou saída fora da grade de preços: {sem_precos}; "
          f"ordem_max abaixo de R$ 200: {(ops.ordem_max < 200).sum()}")
    return pd.concat([ops.reset_index(drop=True), novas], axis=1)


# ---------- passo 2: resumos ----------
def met(g):
    ab = g.aberta.astype(bool)
    f = g[~ab]
    return dict(
        n=len(g), fech=len(f), ab=int(ab.sum()),
        preg=f.pregoes.mean(),
        alta=(f.valorizacao > 0).mean() if len(f) else NAN,
        val=g.valorizacao.mean(), vliq=g.val_liquida.mean(),
        rend=g.rendimento.mean(), liq=g.liquido.mean(), selic=g.selic.mean(),
        ganhou=(g.liquido > g.selic).mean(),
    )


def linha(rot, g):
    m = met(g)
    return (f"{rot}: n={m['n']} | fechadas={m['fech']} | em aberto={m['ab']} | "
            f"pregões médios={N(m['preg'])} | cota em alta={P(m['alta'])} | "
            f"valorização média={P(m['val'])} | val. líquida média={P(m['vliq'])} | "
            f"rendimento médio={P(m['rend'])} | líquido médio={P(m['liq'])} | "
            f"selic média={P(m['selic'])} | ganharam da Selic={P(m['ganhou'])}")


def bloco(titulo, df, chave):
    print(f"\n{titulo}")
    for k, g in df.groupby(chave, sort=True):
        rot = " x ".join(map(str, k)) if isinstance(k, tuple) else str(k)
        print("  " + linha(rot, g))


def linha_merc(rot, g):
    ex = g.excesso_mercado.dropna()
    return (f"  {rot}: n={len(g)} | fundo_preco={P(g.fundo_preco.mean())} | "
            f"mercado_preco={P(g.mercado_preco.mean())} | tipo_preco={P(g.tipo_preco.mean())} | "
            f"excesso_mercado={P(g.excesso_mercado.mean())} | excesso_tipo={P(g.excesso_tipo.mean())} | "
            f"excesso_mercado>0={P((ex > 0).mean())}")


def linha_selic(rot, g):
    return (f"  {rot}: n={len(g)} | var_selic={PP(g.var_selic.mean())} | "
            f"fundo_preco={P(g.fundo_preco.mean())} | mercado_preco={P(g.mercado_preco.mean())} | "
            f"excesso_mercado={P(g.excesso_mercado.mean())} | liquido={P(g.liquido.mean())} | "
            f"selic={P(g.selic.mean())}")


def linha_grafico(rot, g):
    return (f"  {rot}: n={len(g)} | valorização={P(g.valorizacao.mean())} | "
            f"excesso_mercado={P(g.excesso_mercado.mean())} | liquido={P(g.liquido.mean())} | "
            f"selic={P(g.selic.mean())} | ganharam da Selic={P((g.liquido > g.selic).mean())}")


def resumos(ops):
    o = ops.copy()
    for c in ["faixa_ordem", "tipo", "faixa_desconto", "motivo", "origem"]:
        o[c] = o[c].fillna("sem tipo" if c == "tipo" else "sem dado")
    o["ano"] = o.entrada.dt.year
    fech = o[~o.aberta].copy()

    bloco("R1. Por faixa de ordem", o, "faixa_ordem")
    bloco("R2. Por tipo", o, "tipo")
    bloco("R3. Por faixa de ordem x tipo", o, ["faixa_ordem", "tipo"])
    bloco("R4. Por faixa de desconto (P/VP)", o, "faixa_desconto")
    bloco("R5. Por ano de entrada", o, "ano")
    bloco("R6. Por motivo de saída", o, "motivo")
    bloco("R7. Por origem (tipo do anúncio)", o, "origem")

    print("\nR8. Mercado e Selic (só fechadas), por faixa de ordem e por tipo")
    for k, g in fech.groupby("faixa_ordem"):
        print(linha_merc(f"faixa {k}", g))
    for k, g in fech.groupby("tipo"):
        print(linha_merc(f"tipo {k}", g))

    print("\nR9. Por regime da Selic (só fechadas)")
    for k, g in fech.groupby("regime_selic"):
        print(linha_selic(k, g))

    print("\nR10. Fechadas com fundo_preco < 0")
    neg = fech[fech.fundo_preco < 0]
    print(f"  total: {len(neg)}")
    print(f"  mercado_preco < 0: {(neg.mercado_preco < 0).sum()} de {neg.mercado_preco.notna().sum()} com dado")
    print(f"  mercado_preco < -3%: {(neg.mercado_preco < -0.03).sum()}")
    print(f"  excesso_mercado < -5% (queda própria do fundo): {(neg.excesso_mercado < -0.05).sum()}")
    print(f"  ocorridas com regime_selic 'subindo': {(neg.regime_selic == 'subindo').sum()}")
    c1 = fech[["fundo_preco", "mercado_preco"]].dropna()
    c2 = fech[["fundo_preco", "var_selic"]].dropna()
    print(f"  Pearson (todas as fechadas): fundo_preco x mercado_preco = "
          f"{N(c1.corr().iloc[0, 1], 2)} (n={len(c1)}); "
          f"fundo_preco x var_selic = {N(c2.corr().iloc[0, 1], 2)} (n={len(c2)})")

    print("\nR11. Gráfico (só fechadas; indicadores até a véspera da entrada)")
    fech["b_mm200"] = fech.acima_mm200.map(lambda x: "sem dado" if pd.isna(x) else str(bool(x)))
    fech["b_mm50"] = fech.acima_mm50.map(lambda x: "sem dado" if pd.isna(x) else str(bool(x)))
    fech["b_ret60"] = np.where(fech.ret60.isna(), "sem dado",
                               np.where(fech.ret60 >= 0, ">= 0", "< 0"))
    fech["b_dist"] = np.where(fech.dist_max252.isna(), "sem dado",
                              np.where(fech.dist_max252 < -0.20, "< -20%", ">= -20%"))
    for col, titulo in [("b_mm200", "acima da mm200"), ("b_mm50", "acima da mm50"),
                        ("b_ret60", "ret60"), ("b_dist", "dist. do máximo 252")]:
        print(f"  [{titulo}]")
        for k, g in fech.groupby(col):
            print(linha_grafico(f"    {k}", g))

    print("\nR12. Dividendo perdido na entrada (todas as operações)")
    perd = o[o.perdeu_dividendo == 1]
    print(f"  operações com dividendo perdido: {len(perd)} de {len(o)}")
    print(f"  média de dividendo_perdido_pct entre elas: {P(perd.dividendo_perdido_pct.mean())}")
    print(f"  mediana de pregoes_ate_data_base entre elas: {N(perd.pregoes_ate_data_base.median(), 0)}")
    for _, r in perd.iterrows():
        print(f"  {r.ticker} | anúncio {D(r.data_anuncio)} | entrada {D(r.entrada)} | "
              f"perdido {P(r.dividendo_perdido_pct)}")

    print("\nR13. Saída: esperar a próxima data-base (motivo 'rendimento caiu')")
    esp = o[o.esperar_aplica == 1]
    ge = esp.ganho_esperar.dropna()
    print(f"  operações com esperar_aplica = 1: {len(esp)}")
    print(f"  ganho_esperar média: {P(ge.mean(), 2)} | mediana: {P(ge.median(), 2)} | "
          f"% com ganho > 0: {P((ge > 0).mean())} (de {len(ge)} com valor)")
    for _, r in esp.iterrows():
        print(f"  {r.ticker} | saída {D(r.saida)} | saida_alt {D(r.saida_alt)} | "
              f"preco_saida {N(r.preco_saida, 2)} | preco_saida_alt {N(r.preco_saida_alt, 2)} | "
              f"valor aviso {N(r.valor_aviso_saida, 4)} | ganho_esperar {P(r.ganho_esperar, 2)}")

    print("\nR14. Suspeitas: rendimento == 0 e pregoes >= 100")
    sus = o[(o.rendimento == 0) & (o.pregoes >= 100)]
    print(f"  total: {len(sus)}")
    for _, r in sus.iterrows():
        print(f"  {r.ticker} | entrada {D(r.entrada)} | saida {D(r.saida)} | "
              f"motivo {r.motivo} | div0 {N(r.div0, 4)}")


def conferencias(ops):
    print("\n== CONFERÊNCIAS")
    print(f"1. operações: {len(ops)} | fechadas: {(~ops.aberta).sum()} | em aberto: {ops.aberta.sum()}")
    fech = ops[~ops.aberta]
    print("2. fundo_preco (fechamento entrada->saída) x valorizacao (preco_entrada->preco_saida), 3 operações:")
    for _, r in fech[fech.fundo_preco.notna()].head(3).iterrows():
        print(f"   {r.ticker} | entrada {D(r.entrada)} saída {D(r.saida)} | "
              f"preco_entrada {N(r.preco_entrada, 4)} preco_saida {N(r.preco_saida, 4)} | "
              f"valorizacao {P(r.valorizacao, 2)} | fundo_preco {P(r.fundo_preco, 2)} | "
              f"mesmo sinal: {np.sign(r.valorizacao) == np.sign(r.fundo_preco)}")
    ok = fech[fech.fundo_preco.notna() & (fech.valorizacao != 0)]
    print(f"   mesmo sinal em {(np.sign(ok.valorizacao) == np.sign(ok.fundo_preco)).sum()} de {len(ok)} "
          f"fechadas com dado (a diferença de base explica os casos divergentes)")
    sem_tipo = ops.tipo.isna()
    sem_mm = ops.mm200.isna()
    print(f"3. sem tipo: {sem_tipo.sum()} ({', '.join(ops.ticker[sem_tipo]) or '-'}) | "
          f"sem mm200: {sem_mm.sum()} | sem tipo e sem mm200: {(sem_tipo & sem_mm).sum()}")


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    TIPO = passo0(con)
    con.close()

    ops = passo1(TIPO)

    print("\nCarregando preços e mercado...")
    pre = carregar_precos()
    F = pre.pivot_table(index="data", columns="fundo", values="fechamento", aggfunc="last").sort_index()
    A = pre.pivot_table(index="data", columns="fundo", values="abertura", aggfunc="last")
    V60 = pre.pivot_table(index="data", columns="fundo", values="volume_medio_60 (R$)", aggfunc="last")
    A = A.reindex(index=F.index, columns=F.columns)
    V60 = V60.reindex(index=F.index, columns=F.columns)

    mer = carregar("mercado").sort_values("data").reset_index(drop=True)
    SELIC = mer.set_index("data")["selic_ano (%)"]
    DI = pd.DatetimeIndex(mer["data"])
    anu = carregar("anuncios")
    rend = carregar("rendimentos")

    ops = montar_colunas(ops, F, V60, A, TIPO, SELIC, DI, anu, rend)

    out = ops.copy()
    for c in out.select_dtypes("float").columns:
        out[c] = out[c].round(4)
    out.to_csv(PLAN / "estudo_agressivo.csv", **OPCOES)
    print(f"\nestudo_agressivo.csv: {len(out)} linhas, {out.shape[1]} colunas")

    resumos(ops)
    conferencias(ops)


if __name__ == "__main__":
    main()
