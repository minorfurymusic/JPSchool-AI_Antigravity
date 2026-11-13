"""Hipótese do dono para o perfil conservador: fundo bom que cai 10-15% com o rendimento mantido não se vende.

Medido DIA A DIA (2018-2026), só com o que era conhecido no dia.

Fundo "de base": patrimônio >= R$ 400 mi, liquidez >= R$ 500 mil/dia, 12 avisos seguidos com variação até 10%,
sem amortização relevante.

Parte 1 - a queda: primeiro pregão em que o fechamento fica X% abaixo do maior fechamento dos 252 pregões
anteriores, com o rendimento atual >= 95% do rendimento de 126 pregões antes (rendimento mantido).
A partir da abertura seguinte, compara:
  * SEGURAR 252 e 504 pregões (cota + rendimentos);
  * SEGURAR ATÉ O CORTE: vende só se o rendimento cair 15% ou mais (abertura seguinte), senão segura;
  * Selic líquida de imposto no mesmo período e o mercado de fundos.
Parte 2 - a base: comprar o fundo de base no primeiro pregão de cada ano e segurar 252 pregões.

Uso: PYTHONPATH=. .venv/bin/python estudos/conservador.py
"""
import numpy as np
import pandas as pd

from estudos import desconto as E

PL, LIQ, VAR = 400e6, 500_000, 1.10
CORTE = 0.85


def selic_liquida(P, i, k):
    """Selic acumulada entre os pregões i e k, menos o imposto da renda fixa pelo prazo."""
    bruto = np.prod((1 + P.selic[i:k] / 100) ** (1 / 252)) - 1
    dias = (P.datas[k] - P.datas[i]).days
    imposto = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
    return bruto * (1 - imposto)


def rendimentos(P, tk, i, k):
    return sum(v for _, base, v in P.avisos[tk] if i <= base <= k)


def de_base(P, j):
    return (P.pl[:, j] >= PL) & (P.vol60[:, j] >= LIQ) & (P.var12[:, j] <= VAR) & ~P.amort[:, j]


def quedas(P, queda):
    N = len(P.datas)
    i_ini = P.datas.searchsorted(pd.Timestamp(E.INICIO))
    lin = []
    for tk, j in P.col.items():
        if tk not in P.avisos:
            continue
        f = pd.Series(P.F[:, j])
        pico = f.rolling(252, min_periods=126).max().shift(1).to_numpy()
        base = de_base(P, j)
        i = max(i_ini, 127)
        while i < N - 1:
            d0, d6 = P.div[i, j], P.div[i - 126, j]
            if not (base[i] and f[i] <= pico[i] * (1 - queda) and d0 >= 0.95 * d6 and not np.isnan(P.A[i + 1, j]) and P.negociou[i + 1, j]):
                i += 1
                continue
            e = i + 1
            ent = P.A[e, j]
            r = {"fundo": tk, "entrada": P.datas[e], "queda_desde_o_pico": f[i] / pico[i] - 1, "rend_anual": d0 * 12 / ent}
            for h in (252, 504):
                k = e + h
                if k < N and not np.isnan(P.F[k, j]):
                    r[f"segurar_{h}"] = P.F[k, j] / ent - 1 + rendimentos(P, tk, e, k) / ent
                    r[f"cota_{h}"] = P.F[k, j] / ent - 1
                    r[f"selic_{h}"] = selic_liquida(P, e, k)
                    r[f"mercado_{h}"] = P.mercado[k] / P.mercado[e] - 1
                    r[f"menor_{h}"] = np.nanmin(P.L[e:k + 1, j]) / ent - 1
            # o rendimento foi cortado 15% ou mais nos 252 pregões seguintes?
            fim = min(N - 1, e + 252)
            corte = np.where(P.div[e:fim + 1, j] <= CORTE * d0)[0]
            r["cortou_em_252"] = len(corte) > 0 if e + 252 < N else np.nan
            # segurar até o corte (máximo 504 pregões)
            k2 = e + 504
            if k2 < N:
                c2 = np.where(P.div[e:k2 + 1, j] <= CORTE * d0)[0]
                if len(c2) and not np.isnan(P.A[e + c2[0], j]):
                    ks, sai = e + c2[0], P.A[e + c2[0], j]
                    r["ate_o_corte"] = sai / ent - 1 + rendimentos(P, tk, e, ks - 1) / ent + selic_liquida(P, ks, k2)
                elif not np.isnan(P.F[k2, j]):
                    r["ate_o_corte"] = P.F[k2, j] / ent - 1 + rendimentos(P, tk, e, k2) / ent
            # em quantos pregões a cota voltou ao preço do pico
            volta = np.where(P.H[e:, j] >= pico[i])[0]
            r["pregoes_ate_voltar_ao_pico"] = volta[0] if len(volta) else np.nan
            r["observado"] = N - 1 - e
            lin.append(r)
            i += 252  # um caso por fundo por ano
    return pd.DataFrame(lin)


def faixa(s):
    s = s.dropna() * 100
    return f"pessimista {s.quantile(.25):+.1f}% | típico {s.median():+.1f}% | otimista {s.quantile(.75):+.1f}% | pior 1 em 10 {s.quantile(.1):+.1f}%  ({len(s)} casos)"


def mostrar_quedas(q, queda):
    print(f"\n=== QUEDA DE {queda:.0%} OU MAIS DESDE O PICO, COM RENDIMENTO MANTIDO: {len(q)} casos em {q['fundo'].nunique()} fundos ===")
    if q.empty:
        return
    print(f"Na entrada (típico): queda {q['queda_desde_o_pico'].median():.1%}, rendimento {q['rend_anual'].median():.1%} ao ano")
    print("Por ano:", q.assign(ano=q["entrada"].dt.year).groupby("ano").size().to_dict())
    c = q["cortou_em_252"].dropna()
    print(f"O rendimento foi cortado 15% ou mais nos 252 pregões seguintes: {c.mean():.0%} dos {len(c)} casos")
    for h in (252, 504):
        if f"segurar_{h}" not in q:
            continue
        s = q.dropna(subset=[f"segurar_{h}"])
        print(f"SEGURAR {h} pregões: {faixa(s[f'segurar_{h}'])}")
        print(f"   só a cota: {faixa(s[f'cota_{h}'])}")
        print(f"   Selic líquida no período: típico {s[f'selic_{h}'].median()*100:+.1f}% | ganhou da Selic líquida: {(s[f'segurar_{h}'] > s[f'selic_{h}']).mean():.0%} | "
              f"ganhou do mercado de fundos: {(s[f'segurar_{h}'] > s[f'mercado_{h}']).mean():.0%} | terminou com ganho: {(s[f'segurar_{h}'] > 0).mean():.0%}")
        print(f"   menor preço no caminho: típico {s[f'menor_{h}'].median()*100:+.1f}% | pior 1 em 10 {s[f'menor_{h}'].quantile(.1)*100:+.1f}%")
        if h == 252:
            for nome, m in (("rendimento NÃO cortado", s["cortou_em_252"] == False), ("rendimento cortado", s["cortou_em_252"] == True)):  # noqa: E712
                if m.sum() >= 5:
                    print(f"   {nome}: {faixa(s.loc[m, 'segurar_252'])}")
    if "ate_o_corte" in q:
        s = q.dropna(subset=["ate_o_corte", "segurar_504"])
        print(f"SEGURAR ATÉ O CORTE (vende no corte e deixa na Selic; máximo 504 pregões): {faixa(s['ate_o_corte'])}")
        print(f"   nos mesmos casos, segurar os 504 pregões sem vender: {faixa(s['segurar_504'])}")
    v = q[q["observado"] >= 504]
    if len(v):
        voltou = v["pregoes_ate_voltar_ao_pico"]
        print(f"Voltou ao preço do pico (casos com 504 pregões observados): {(voltou <= 252).mean():.0%} em até 252 pregões | {(voltou <= 504).mean():.0%} em até 504 | "
              f"tempo típico de quem voltou: {voltou.dropna().median():.0f} pregões")


def base_anual(P):
    N = len(P.datas)
    lin = []
    for ano in range(2018, 2026):
        e = P.datas.searchsorted(pd.Timestamp(f"{ano}-01-01"))
        k = e + 252
        if k >= N:
            continue
        for tk, j in P.col.items():
            if tk not in P.avisos or not de_base(P, j)[e] or np.isnan(P.A[e, j]) or np.isnan(P.F[k, j]):
                continue
            ent = P.A[e, j]
            lin.append({"ano": ano, "fundo": tk, "total": P.F[k, j] / ent - 1 + rendimentos(P, tk, e, k) / ent, "rend": rendimentos(P, tk, e, k) / ent,
                        "selic": selic_liquida(P, e, k), "mercado": P.mercado[k] / P.mercado[e] - 1, "menor": np.nanmin(P.L[e:k + 1, j]) / ent - 1,
                        "cortou": bool((P.div[e:k + 1, j] <= CORTE * P.div[e, j]).any())})
    b = pd.DataFrame(lin)
    print(f"\n=== A BASE: comprar o fundo de base no primeiro pregão do ano e segurar 252 pregões: {len(b)} casos ===")
    t = b.groupby("ano").agg(fundos=("total", "size"), total_típico=("total", lambda s: s.median() * 100), só_rendimentos=("rend", lambda s: s.median() * 100),
                             selic_líquida=("selic", lambda s: s.median() * 100), mercado=("mercado", lambda s: s.median() * 100),
                             ganhou_da_selic=("total", lambda s: (s > b.loc[s.index, "selic"]).mean()), menor_preço=("menor", lambda s: s.median() * 100),
                             cortou_rendimento=("cortou", "mean")).round(2)
    print(t.to_string())
    print(f"Todos os anos: total {faixa(b['total'])}")
    print(f"   só rendimentos (típico): {b['rend'].median()*100:.1f}% | Selic líquida (típico): {b['selic'].median()*100:.1f}% | ganhou da Selic líquida: {(b['total'] > b['selic']).mean():.0%} | "
          f"rendimento cortado 15%+ no ano: {b['cortou'].mean():.0%}")
    print(f"   sem corte: {faixa(b.loc[~b['cortou'], 'total'])}")
    print(f"   com corte: {faixa(b.loc[b['cortou'], 'total'])}")


def main():
    P = E.preparar()
    for queda in (0.10, 0.15, 0.20):
        mostrar_quedas(quedas(P, queda), queda)
    base_anual(P)


if __name__ == "__main__":
    main()
