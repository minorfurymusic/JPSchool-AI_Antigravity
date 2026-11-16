"""Caminho da cota, dia a dia, depois da entrada (pergunta do dono em 2026-11-16).

Para cada operação: quando a cota fechou acima da entrada pela primeira vez, até onde subiu e caiu,
em que pregão, e a ORDEM: subiu 5% primeiro ou caiu 5% primeiro, e o que veio depois.
Janela fixa de 120 pregões a partir da entrada, sem olhar a regra de saída. Lê só das planilhas.

Uso: PYTHONPATH=. .venv/bin/python estudos/caminho_agressivo.py
"""
import numpy as np
import pandas as pd

from estudos import planilhas as PL

JANELA, LIMIAR = 120, 0.05


def caminho(g, ent):
    """g: linhas de preço do fundo a partir da entrada (D0...). Devolve as medidas da operação."""
    c, h, l = (g[k].to_numpy()[:JANELA + 1] / ent - 1 for k in ("fechamento", "maxima", "minima"))
    n = len(c) - 1
    r = {"pregoes_observados": n, "completa": n >= JANELA}
    pos = np.where(c > 0)[0]
    r["primeiro_fechamento_acima"] = pos[0] if len(pos) else np.nan
    r["dias_fechando_acima"] = (c > 0).mean()
    r["maior_alta"], r["dia_maior_alta"] = h.max(), int(h.argmax())
    r["maior_queda"], r["dia_maior_queda"] = l.min(), int(l.argmin())
    sobe, cai = np.where(h >= LIMIAR)[0], np.where(l <= -LIMIAR)[0]
    ds, dc = (sobe[0] if len(sobe) else 10**6), (cai[0] if len(cai) else 10**6)
    if ds == dc == 10**6:
        r["padrao"] = "ficou entre -5% e +5%"
    elif dc <= ds:  # no mesmo dia, vale a queda (não há a ordem dentro do dia)
        r["padrao"], r["dia_primeiro_toque"] = "caiu 5% primeiro", dc
        k = int(l.argmin())
        r["fundo"], r["dia_fundo"] = l.min(), k
        volta = np.where(h[k:] >= 0)[0]
        r["voltou_ao_preco_de_entrada"] = len(volta) > 0
        r["dia_da_volta"] = k + volta[0] if len(volta) else np.nan
        r["maior_alta_depois_do_fundo"] = h[k:].max()
        r["tocou_mais5_depois"] = bool((h[k:] >= LIMIAR).any())
    else:
        r["padrao"], r["dia_primeiro_toque"] = "subiu 5% primeiro", ds
        k = int(h.argmax())
        r["pico"], r["dia_pico"] = h.max(), k
        volta = np.where(l[k:] <= 0)[0]
        r["voltou_ao_preco_de_entrada"] = len(volta) > 0
        r["dia_da_volta"] = k + volta[0] if len(volta) else np.nan
        r["maior_queda_depois_do_pico"] = l[k:].min()
        r["tocou_menos5_depois"] = bool((l[k:] <= -LIMIAR).any())
    for d in (20, 60, 120):
        r[f"fechamento_d{d}"] = c[d] if n >= d else np.nan
    return r


def medir(ops, precos):
    lin = []
    for o in ops.itertuples():
        g = precos[(precos["fundo"] == o.ticker) & (precos["data"] >= o.entrada)].sort_values("data")
        if len(g) < 2:
            continue
        lin.append({"fundo": o.ticker, "entrada": o.entrada, "preco_entrada": o.preco_entrada, "pvp": o.pvp, "origem": o.origem,
                    **caminho(g, o.preco_entrada)})
    return pd.DataFrame(lin)


def resumo(m, titulo):
    f = m[m["completa"]]
    p = lambda x: f"{x * 100:+.1f}%"
    print(f"\n=== {titulo}: {len(m)} operações, {len(f)} com os {JANELA} pregões completos ===")
    tem = f["primeiro_fechamento_acima"].notna()
    print(f"Fechou acima da entrada em algum dia: {tem.mean():.0%} | primeiro dia: média {f.loc[tem, 'primeiro_fechamento_acima'].mean():.0f}, mediana {f.loc[tem, 'primeiro_fechamento_acima'].median():.0f} | "
          f"já no dia da entrada ou no seguinte: {(f['primeiro_fechamento_acima'] <= 1).mean():.0%} | nunca: {(~tem).mean():.0%}")
    print(f"Dias fechando acima da entrada (média): {f['dias_fechando_acima'].mean():.0%}")
    print(f"Maior alta sobre a entrada: média {p(f['maior_alta'].mean())}, mediana {p(f['maior_alta'].median())}, no pregão {f['dia_maior_alta'].mean():.0f} (mediana {f['dia_maior_alta'].median():.0f})")
    print(f"Maior queda sob a entrada: média {p(f['maior_queda'].mean())}, mediana {p(f['maior_queda'].median())}, no pregão {f['dia_maior_queda'].mean():.0f} (mediana {f['dia_maior_queda'].median():.0f})")
    print(f"O ponto mais baixo veio ANTES do mais alto: {(f['dia_maior_queda'] < f['dia_maior_alta']).mean():.0%}")
    for a in (0.03, 0.05, 0.10):
        print(f"   tocou +{a:.0%}: {(f['maior_alta'] >= a).mean():.0%} | tocou -{a:.0%}: {(f['maior_queda'] <= -a).mean():.0%}")
    print("Fechamento médio: " + " | ".join(f"D+{d}: {p(f[f'fechamento_d{d}'].mean())} (acima da entrada: {(f[f'fechamento_d{d}'] > 0).mean():.0%})" for d in (20, 60, 120)))
    for nome, g in f.groupby("padrao"):
        print(f"--- {nome}: {len(g)} ({len(g) / len(f):.0%}) ---")
        if nome.startswith("caiu"):
            print(f"   tocou -5% no pregão {g['dia_primeiro_toque'].mean():.0f} (mediana {g['dia_primeiro_toque'].median():.0f}) | fundo: {p(g['fundo'].mean())} (mediana {p(g['fundo'].median())}) no pregão {g['dia_fundo'].mean():.0f} (mediana {g['dia_fundo'].median():.0f})")
            v = g["voltou_ao_preco_de_entrada"]
            print(f"   depois do fundo voltou ao preço de entrada: {v.mean():.0%}, em {(g.loc[v, 'dia_da_volta'] - g.loc[v, 'dia_fundo']).mean():.0f} pregões depois do fundo (pregão {g.loc[v, 'dia_da_volta'].mean():.0f} desde a entrada) | "
                  f"chegou a +5%: {g['tocou_mais5_depois'].mean():.0%} | maior alta depois do fundo: {p(g['maior_alta_depois_do_fundo'].mean())}")
        elif nome.startswith("subiu"):
            print(f"   tocou +5% no pregão {g['dia_primeiro_toque'].mean():.0f} (mediana {g['dia_primeiro_toque'].median():.0f}) | pico: {p(g['pico'].mean())} (mediana {p(g['pico'].median())}) no pregão {g['dia_pico'].mean():.0f} (mediana {g['dia_pico'].median():.0f})")
            v = g["voltou_ao_preco_de_entrada"]
            print(f"   depois do pico voltou ao preço de entrada: {v.mean():.0%}, em {(g.loc[v, 'dia_da_volta'] - g.loc[v, 'dia_pico']).mean():.0f} pregões depois do pico (pregão {g.loc[v, 'dia_da_volta'].mean():.0f} desde a entrada) | "
                  f"chegou a -5%: {g['tocou_menos5_depois'].mean():.0%} | maior queda depois do pico: {p(g['maior_queda_depois_do_pico'].mean())}")
        print("   fechamento médio: " + " | ".join(f"D+{d}: {p(g[f'fechamento_d{d}'].mean())}" for d in (20, 60, 120)) + f" | maior alta {p(g['maior_alta'].mean())} | maior queda {p(g['maior_queda'].mean())}")


def main():
    precos = PL.carregar_precos()
    precos["data"] = pd.to_datetime(precos["data"], dayfirst=True)
    o = pd.read_csv("docs/anuncio_saida_operacoes.csv", parse_dates=["entrada"])
    o = o[(o["pl"] >= 50e6) & (o["ticker"] != "XPPR11")]
    agr = medir(o[(o["pvp"] >= 0.30) & (o["pvp"] < 0.60)], precos)
    resumo(agr, "AGRESSIVO (cota de 0,30 a 0,60 do valor patrimonial)")
    for nome, g in agr[agr["completa"]].groupby("origem"):
        print(f"   {nome}: {len(g)} | " + " | ".join(f"{k}: {v}" for k, v in g["padrao"].value_counts().items()))
    resumo(medir(o[(o["pvp"] >= 0.30) & (o["pvp"] <= 0.90)], precos), "COMPARAÇÃO: todas de 0,30 a 0,90")
    agr.round(4).to_csv("planilhas/tecnico/caminho_agressivo.csv", sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")


if __name__ == "__main__":
    main()
