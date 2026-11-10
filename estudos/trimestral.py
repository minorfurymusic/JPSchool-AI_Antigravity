"""Estudo por trimestre, com TODOS os fundos (inclusive os sem rendimento mensal
confiável e os que pagam em poucos meses do ano).

Pergunta: quando o rendimento do trimestre sobe pelo menos 25% sobre a média dos
4 trimestres anteriores, o que acontece com a cota depois? Muda se o fundo já
rendia mais de 10% ao ano? Muda se a alta veio junto com ganho na venda de ativos?

Fonte: informe trimestral da CVM (rendimentos declarados; receita de venda de
imóveis; resultado de venda de títulos) e cotações da B3.

Uso: PYTHONPATH=. .venv/bin/python estudos/trimestral.py
"""
import warnings

import duckdb
import numpy as np
import pandas as pd

from fii import aprendizado as ap
from fii import config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
SALTO = 1.25
GANHO_MINIMO = 0.005  # ganho com venda de ativos de pelo menos 0,5% do patrimônio no trimestre
H = [1, 3, 6, 12]


def tstat(s):
    s = s.dropna()
    return s.mean() / (s.std(ddof=1) / np.sqrt(len(s))) if len(s) > 5 and s.std() > 0 else np.nan


def montar_eventos(con):
    t = con.execute("select * from trimestral order by ticker, trimestre").df()
    m = con.execute("select * from mensal").df()
    vendas = con.execute("select ticker, data_venda, pct_pl from vendas").df()
    regra = m.groupby("ticker")["regra_rend"].first()
    tipo = m.dropna(subset=["vp_cota"]).sort_values("mes").groupby("ticker").tail(1).set_index("ticker").apply(ap.tipo_do_fundo, axis=1)
    vol = m.set_index(["ticker", "mes"])["vol_medio"]
    evs = []
    for tk, g in t.groupby("ticker", sort=False):
        g = g.reset_index(drop=True)
        r = g["rend_tri_aj"]
        vt = vendas[vendas["ticker"] == tk]
        ultimo = None
        for i in range(4, len(g)):
            ant = r[i - 4:i]
            if pd.isna(r[i]) or ant.notna().sum() < 3 or (g.at[i, "trimestre"] - g.at[i - 4, "trimestre"]).days > 380:
                continue
            base = ant.fillna(0).mean()
            preco_ant = g.at[i - 1, "preco"]
            if base <= 0 or pd.isna(preco_ant) or preco_ant <= 0:
                continue
            razao = r[i] / base
            if razao < SALTO or razao > 10 or r[i] / g.at[i, "preco"] > 0.3:
                continue
            q = g.at[i, "trimestre"]
            if ultimo is not None and (q - ultimo).days < 280:
                ultimo = q
                continue
            ultimo = q
            mes = q.to_period("M").to_timestamp()
            if not (vol.get((tk, mes), 0) >= ap.VOLUME_MINIMO):
                continue
            ganho = np.nanmax([g.at[i, "ganho_venda_pl"], g.at[i - 1, "ganho_venda_pl"]]) if not (pd.isna(g.at[i, "ganho_venda_pl"]) and pd.isna(g.at[i - 1, "ganho_venda_pl"])) else np.nan
            gi = (g.at[i, "ganho_imoveis"] + g.at[i - 1, "ganho_imoveis"]) / g.at[i, "pl"] if g.at[i, "pl"] else np.nan
            vendeu_imovel = bool(len(vt[(vt["data_venda"] > q - pd.DateOffset(months=9)) & (vt["data_venda"] <= q)]))
            depois = [r[i + k] / base if i + k < len(g) and pd.notna(r[i + k]) else np.nan for k in range(1, 7)]
            evs.append({"ticker": tk, "mes": mes, "trimestre": q, "evento": "salto trimestral", "razao": razao, "rend_antes": base / 3,
                        "dy_antes": ant.fillna(0).sum() / preco_ant, "zeros_antes": int((ant.fillna(0) == 0).sum()),
                        "cv_antes": ant.fillna(0).std() / base, "ganho_venda_pl": ganho, "ganho_imoveis_pl": gi, "vendeu_imovel": vendeu_imovel,
                        "tem_mensal": str(regra.get(tk, "")).startswith("CVM conta"), "tipo_fundo": tipo.get(tk, "misto"),
                        **{f"rz_q{k}": depois[k - 1] for k in range(1, 7)}})
    return pd.DataFrame(evs), m


def linha(nome, g, ent="ini"):
    out = {"grupo": nome, "casos": len(g)}
    for h in H:
        e, p = g[f"exc_{ent}_{h}"].dropna(), g[f"pex_{ent}_{h}"].dropna()
        out[f"{h}m acima do mercado %"] = e.median() * 100 if len(e) else np.nan
        if h in (3, 6):
            out[f"{h}m média %"] = e.mean() * 100 if len(e) else np.nan
            out[f"{h}m t"] = tstat(e)
            out[f"{h}m acerto"] = (e > 0).mean() if len(e) else np.nan
            out[f"{h}m só cota %"] = p.median() * 100 if len(p) else np.nan
    p6 = g[f"pre_{ent}_6"].dropna()
    out["cota +10% em 6m"] = (p6 >= 0.10).mean() if len(p6) else np.nan
    out["rend. 2 tri depois ÷ antes"] = g["rz_q2"].median()
    out["rend. 4 tri depois ÷ antes"] = g["rz_q4"].median()
    out["rend. 5-6 tri depois ÷ antes"] = g[["rz_q5", "rz_q6"]].mean(axis=1).median()
    return out


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    ev, m = montar_eventos(con)
    q = con.execute("select * from quebras").df()
    med = ap.medir(ev, m, q)
    # entrada tardia: 2 meses depois do fim do trimestre, quando o informe da CVM já saiu
    tarde = ap.medir(ev.assign(mes=ev["mes"] + pd.DateOffset(months=2)), m, q)
    print(f"Saltos trimestrais (rendimento do trimestre >= {SALTO - 1:.0%} acima da média dos 4 anteriores): {len(med)} casos, "
          f"{med['ticker'].nunique()} fundos, {med['trimestre'].min():%m/%Y} a {med['trimestre'].max():%m/%Y}")
    print(f"  de fundos SEM rendimento mensal confiável: {(~med['tem_mensal']).sum()} | pagavam em poucos trimestres (algum zero nos 4 anteriores): {(med['zeros_antes'] > 0).sum()}")
    print(f"  rendiam >= 10% ao ano antes: {(med['dy_antes'] >= 0.10).sum()} | com ganho de venda de ativos >= {GANHO_MINIMO:.1%} do patrimônio: {(med['ganho_venda_pl'] >= GANHO_MINIMO).sum()} | com venda de imóvel informada: {med['vendeu_imovel'].sum()}")

    def tabela(d, titulo):
        alto, baixo = d["dy_antes"] >= 0.10, d["dy_antes"] < 0.10
        cg, sg = d["ganho_venda_pl"] >= GANHO_MINIMO, ~(d["ganho_venda_pl"] >= GANHO_MINIMO)
        gi = d["ganho_imoveis_pl"] >= GANHO_MINIMO
        linhas = [linha("todos", d), linha("rendia >= 10% ao ano", d[alto]), linha("rendia < 10% ao ano", d[baixo]),
                  linha("com ganho de venda de ativos", d[cg]), linha("sem ganho de venda de ativos", d[sg]),
                  linha("com ganho de venda de IMÓVEL", d[gi]), linha("com venda de imóvel informada", d[d["vendeu_imovel"]]),
                  linha(">= 10% E com ganho de venda", d[alto & cg]), linha(">= 10% E sem ganho de venda", d[alto & sg]),
                  linha("< 10% E com ganho de venda", d[baixo & cg]), linha("< 10% E sem ganho de venda", d[baixo & sg]),
                  linha("fundos sem rendimento mensal confiável", d[~d["tem_mensal"]]), linha("fundos com rendimento mensal", d[d["tem_mensal"]]),
                  linha("pagava em poucos trimestres", d[d["zeros_antes"] > 0]),
                  linha("tijolo", d[d["tipo_fundo"] == "tijolo"]), linha("papel", d[d["tipo_fundo"] == "papel"]),
                  linha("até 2021", d[d["mes"] < "2022-01-01"]), linha("2022 em diante", d[d["mes"] >= "2022-01-01"])]
        print(f"\n=== {titulo} ===")
        print(pd.DataFrame(linhas).round(2).to_string(index=False))

    tabela(med, "COMPRANDO NO 1º PREGÃO DEPOIS DO FIM DO TRIMESTRE")
    tabela(tarde, "COMPRANDO 2 MESES DEPOIS (quando o informe da CVM já está publicado)")

    print("\n=== A TESE: salto com venda de imóvel, e depois? ===")
    d = med[(med["ganho_imoveis_pl"] >= GANHO_MINIMO) | med["vendeu_imovel"]]
    print(f"{len(d)} casos. Rendimento em relação ao nível anterior (mediana), trimestre a trimestre depois do salto:")
    print("   no salto: %.2f | " % d["razao"].median() + " | ".join(f"{k} tri depois: {d[f'rz_q{k}'].median():.2f} (n {d[f'rz_q{k}'].notna().sum()})" for k in range(1, 7)))
    print("   % dos casos com rendimento ABAIXO do nível anterior:", " | ".join(f"{k} tri: {(d[f'rz_q{k}'].dropna() < 1).mean():.0%}" for k in (2, 4, 6)))
    for h in H:
        p = d[f"pre_ini_{h}"].dropna()
        print(f"   cota em {h:2d} meses: mediana {p.median()*100:+.1f}% | subiu 10% ou mais em {(p >= 0.10).mean():.0%} | caiu 10% ou mais em {(p <= -0.10).mean():.0%} (n {len(p)})")
    s = med[~((med["ganho_imoveis_pl"] >= GANHO_MINIMO) | med["vendeu_imovel"])]
    print("Comparação, saltos SEM venda de imóvel:", " | ".join(f"{k} tri depois: {s[f'rz_q{k}'].median():.2f}" for k in range(1, 7)))
    med.to_parquet(config.DADOS / "eventos_trimestrais.parquet")


if __name__ == "__main__":
    main()
