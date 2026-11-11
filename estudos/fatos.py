"""Fatos relevantes: o que a cota faz, pregão a pregão, comprando na abertura do pregão seguinte.

Tudo em reais sobre uma cota comprada a R$ 10,00, para leitura direta.
Tipos pela classificação por palavras (fii/classificar.py), que erra: ver a conferência manual no relatório.

Uso: PYTHONPATH=. .venv/bin/python estudos/fatos.py
"""
import warnings
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from estudos import dias as D
from fii import classificar as cl
from fii import config, fnet

warnings.filterwarnings("ignore")
pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 40)
DIAS = [1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60]
BONS = ["rendimento_aumento", "venda_com_ganho", "recebimento", "locacao_nova"]
NOME = {"rendimento_aumento": "aumento de rendimento dito no texto", "venda_com_ganho": "venda de ativo com ganho",
        "recebimento": "recebimento extraordinário (multa, indenização)", "locacao_nova": "locação nova ou renovada",
        "venda": "venda de ativo, sem falar em ganho", "venda_com_perda": "venda de ativo com perda",
        "saida_inquilino": "saída de inquilino ou inadimplência", "rendimento_reducao": "redução de rendimento dita no texto",
        "aquisicao": "compra de ativo", "emissao": "emissão de cotas", "reorganizacao": "reorganização do fundo", "outro": "outros assuntos"}


def carregar(con_app, con_fnet):
    docs = con_fnet.execute("select id, cnpj, nome_pregao, entrega, arquivo from documentos where categoria='Fato Relevante' and estado='texto'").df()
    v = con_app.execute("select ticker, cnpj from vinculo").df()
    v["cnpj"] = v["cnpj"].str.replace(r"\D", "", regex=True)
    vol = con_app.execute("select ticker, sum(volume) v from cotacoes group by 1").df()
    v = v.merge(vol, on="ticker").sort_values("v").drop_duplicates("cnpj", keep="last")  # papel principal do fundo
    docs = docs.merge(v[["ticker", "cnpj"]], on="cnpj", how="left")
    lin = []
    for d in docs.itertuples():
        try:
            txt = Path(d.arquivo).with_suffix(".txt").read_text(encoding="utf-8")
        except OSError:
            continue
        r = cl.classificar(txt)
        imp = r.pop("impacto") or {}
        lin.append({"id": d.id, "ticker": d.ticker, "quando": d.entrega, **r, "imp_direcao": imp.get("direcao"), "imp_pct": imp.get("pct"),
                    "imp_valor": imp.get("valor_por_cota"), "imp_frase": imp.get("frase"), "inicio": " ".join(txt.split())[:260]})
    return pd.DataFrame(lin)


def em_reais(M, C, titulo):
    """Cota comprada a R$ 10,00. Três tabelas: o dia típico; fechamento em três cenários; até onde chegou.
    Pessimista = 1 em cada 4 casos foi pior que isso. Típico = o caso do meio. Otimista = 1 em cada 4 foi melhor."""
    if M is None or M[0].shape[0] < 15:
        print(f"\n--- {titulo}: poucos casos ({0 if M is None else M[0].shape[0]}) ---")
        return
    q = lambda x, p: float(10 * (1 + np.quantile(x, p)))
    print(f"\n--- {titulo}: {M[0].shape[0]} casos | cota comprada a R$ 10,00 ---")
    t1, t2, t3 = [], [], []
    for d in [0] + DIAS:
        F, H, L = M[0][:, d], M[1][:, d], M[2][:, d]
        Hc, Lc = M[1][:, :d + 1].max(axis=1), M[2][:, :d + 1].min(axis=1)
        dia = f"D+{d}" if d else "D0 (compra)"
        t1.append({"dia": dia, "mínima do dia": q(L, .5), "fechamento": q(F, .5), "máxima do dia": q(H, .5)})
        t2.append({"dia": dia, "pessimista": q(F, .25), "típico": q(F, .5), "otimista": q(F, .75), "fechou acima da compra": (F > 0).mean(),
                   "acima de 10,30": (F >= .03).mean(), "acima de 10,50": (F >= .05).mean()})
        t3.append({"até o dia": dia, "maior preço: típico": q(Hc, .5), "maior preço: otimista": q(Hc, .75), "menor preço: típico": q(Lc, .5),
                   "menor preço: pessimista": q(Lc, .25)})
    print("Tabela 1. O dia típico:")
    print(pd.DataFrame(t1).round(2).to_string(index=False))
    print("Tabela 2. Fechamento nos três cenários:")
    print(pd.DataFrame(t2).round(2).to_string(index=False))
    print("Tabela 3. Até onde a cota chegou desde a compra:")
    print(pd.DataFrame(t3).round(2).to_string(index=False))
    print("Dia em que a cota fez o maior preço: " + " | ".join(
        f"até D+{h}: {np.median(M[1][:, :h + 1].argmax(axis=1)):.0f}º pregão" for h in (10, 20, 30, 60)))
    print("Ordem de venda executada (a máxima do dia tocou o preço): " + " | ".join(
        f"R$ {10 * (1 + a):.2f}: " + ", ".join(f"{(M[1][:, :h + 1].max(axis=1) >= a).mean():.0%} até D+{h}" for h in (5, 10, 20, 30)) for a in (.03, .05, .10)))
    print("Comparação com outros fundos comprados na mesma abertura (fechamento típico): " + " | ".join(
        f"D+{d}: {q(M[0][:, d], .5):.2f} x {q(C[0][:, d], .5):.2f}" for d in (1, 5, 10, 20, 30)))


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    cf = duckdb.connect(str(fnet.BANCO), read_only=True)
    f = carregar(con, cf)
    print(f"Fatos relevantes lidos: {len(f)}, de {f['quando'].min():%d/%m/%Y} a {f['quando'].max():%d/%m/%Y} | com papel na bolsa identificado: {f['ticker'].notna().sum()}")
    h = pd.to_datetime(f["quando"]).dt.hour
    print(f"Hora de entrega: antes das 10h {(h < 10).mean():.0%} | 10h às 17h {((h >= 10) & (h < 17)).mean():.0%} | 17h em diante {(h >= 17).mean():.0%}")
    t = f.groupby("tipo").agg(documentos=("id", "size"), com_valor_por_cota=("valor_por_cota", lambda s: s.notna().sum()),
                              continuacao=("continuacao", "sum")).sort_values("documentos", ascending=False)
    t.index = [NOME.get(i, i) for i in t.index]
    print("\nTipo principal de cada fato relevante (classificação por palavras):")
    print(t.to_string())

    P = D.Precos(con)
    rng = np.random.default_rng(5)
    f = f.dropna(subset=["ticker"]).copy()
    f["i0"] = [P.pregao_seguinte(q) for q in f["quando"]]
    f = f[f["i0"] < len(P.datas) - 1]
    f = f[[tk in P.col and bool(P.liq[i, P.col[tk]]) for tk, i in zip(f["ticker"], f["i0"])]].reset_index(drop=True)
    f["preco"] = [P.A[i, P.col[tk]] for tk, i in zip(f["ticker"], f["i0"])]
    f["pct_cota"] = f["valor_por_cota"] / f["preco"]
    # mesmo fundo, mesmo tipo, em menos de 10 pregões: é a mesma notícia repetida; vale a primeira
    f = f.sort_values("quando")
    rep = f.groupby(["ticker", "tipo"])["i0"].diff()
    f["repetido"] = (rep.notna() & (rep <= 10)).to_numpy()
    print(f"\nCom liquidez e preço: {len(f)} | repetições do mesmo fundo e tipo em até 10 pregões: {f['repetido'].sum()}")
    f.to_parquet(config.DADOS / "fatos_classificados.parquet")

    # controle: outros fundos, mesma abertura, sem fato relevante "bom" nos 20 pregões em volta
    bons_por_ticker = f[f["tipo"].isin(BONS)].groupby("ticker")["i0"].apply(list).to_dict()

    def controle(posicoes):
        ent = []
        for i0 in sorted(set(posicoes)):
            cand = [tk for k, tk in enumerate(P.tickers) if P.liq[i0, k] and not any(abs(i0 - j) <= 20 for j in bons_por_ticker.get(tk, ()))]
            ent += [(tk, i0) for tk in (rng.choice(cand, size=min(15, len(cand)), replace=False) if cand else [])]
        return D.juntar(P, ent)

    def rodar(sel, titulo):
        em_reais(D.juntar(P, list(zip(sel["ticker"], sel["i0"]))), controle(sel["i0"]), titulo)

    u = f[~f["repetido"]]
    print("\n" + "=" * 120 + "\nCOMPRA NA ABERTURA DO PREGÃO SEGUINTE AO FATO RELEVANTE\n" + "=" * 120)
    rodar(u[u["tipo"].isin(BONS) & (u["sentido"] == "alta")], "TODOS os que se encaixam: aumento ou possível aumento de rendimento, sem sinal contrário no texto")
    for tp in BONS:
        rodar(u[(u["tipo"] == tp) & (u["sentido"] == "alta")], NOME[tp])
    b = u[u["tipo"].isin(BONS) & (u["sentido"] == "alta") & u["pct_cota"].notna()]
    rodar(b[b["pct_cota"] < 0.01], "valor informado por cota abaixo de 1% do preço")
    rodar(b[(b["pct_cota"] >= 0.01) & (b["pct_cota"] < 0.03)], "valor informado por cota entre 1% e 3% do preço")
    rodar(b[b["pct_cota"] >= 0.03], "valor informado por cota de 3% do preço ou mais")
    rodar(u[u["tipo"].isin(BONS) & (u["sentido"] == "alta") & ~u["continuacao"]], "primeira notícia (texto não diz que é continuação de fato anterior)")
    rodar(u[u["tipo"].isin(BONS) & (u["sentido"] == "alta") & u["continuacao"]], "continuação de fato relevante anterior")
    print("\n" + "=" * 120 + "\nO FUNDO INFORMOU O TAMANHO DO EFEITO NO RENDIMENTO (texto do próprio fato relevante)\n" + "=" * 120)
    im = u[u["imp_direcao"].notna()].copy()
    # tamanho do efeito: o percentual dito; se só disser reais por cota, compara com o preço (valor mensal x 12 / preço não é assumido)
    im["tam"] = im["imp_pct"]
    sobe, desce = im[im["imp_direcao"] > 0], im[im["imp_direcao"] < 0]
    print(f"{len(im)} fatos relevantes em que o fundo declara efeito no rendimento | aumento: {len(sobe)} (com percentual: {sobe['tam'].notna().sum()}, mediana {sobe['tam'].median():.1%}) | "
          f"redução: {len(desce)} (com percentual: {desce['tam'].notna().sum()}, mediana {desce['tam'].median():.1%})")
    rodar(sobe, "O FUNDO DECLAROU AUMENTO de rendimento (qualquer tamanho)")
    rodar(sobe[sobe["tam"] < 0.05], "aumento declarado de até 5%")
    rodar(sobe[(sobe["tam"] >= 0.05) & (sobe["tam"] < 0.15)], "aumento declarado de 5% a 15%")
    rodar(sobe[sobe["tam"] >= 0.15], "aumento declarado de 15% ou mais")
    rodar(sobe[sobe["tam"].isna()], "aumento declarado sem dizer o percentual")
    rodar(desce, "O FUNDO DECLAROU REDUÇÃO de rendimento (qualquer tamanho)")
    rodar(desce[desce["tam"] >= 0.10], "redução declarada de 10% ou mais")
    rodar(u[u["tipo"].isin(["saida_inquilino", "rendimento_reducao", "venda_com_perda"]) & (u["sentido"] == "queda")], "COMPARAÇÃO: notícia ruim (saída de inquilino, redução de rendimento, venda com perda)")
    rodar(u[u["tipo"].isin(["outro", "reorganizacao", "emissao", "aquisicao"])], "COMPARAÇÃO: fatos relevantes sobre outros assuntos")


if __name__ == "__main__":
    main()
