"""Medição em DIAS (pregões) depois de um anúncio.

Regra de entrada do dono: comprar no pregão seguinte ao anúncio.
  * anúncio antes das 10h  -> o pregão seguinte é o do mesmo dia;
  * anúncio depois disso   -> o do dia útil seguinte.
Preço de entrada: ABERTURA desse pregão (dado oficial da B3).

Para cada caso, pregão a pregão:
  * onde a cota fechou em D0 (dia da entrada), D+1, D+2, ... ;
  * o MÁXIMO atingido até cada dia, usando a máxima do dia (não só o fechamento);
  * em que pregão o máximo aconteceu e quantos pregões levou para tocar +3%, +5%, +8%, +10%.
Sempre ao lado de um controle: outros fundos com liquidez, comprados na mesma abertura.

Uso: PYTHONPATH=. .venv/bin/python estudos/dias.py
"""
import warnings

import duckdb
import numpy as np
import pandas as pd

from fii import base, config

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
LIQ = 200_000
DIAS = [0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60]
ALVOS = [0.03, 0.05, 0.08, 0.10, 0.15]
HORIZONTE = 60


class Precos:
    def __init__(self, con):
        c = con.execute("select c.ticker, c.data, c.abertura, c.maxima, c.minima, c.fechamento, c.volume from cotacoes c "
                        "join (select distinct ticker from mensal) using(ticker)").df()
        q = con.execute("select * from quebras").df()
        conf, ruins = q[q["confirmada"]], q[~q["confirmada"]]
        partes = []
        for tk, g in c.groupby("ticker", sort=False):
            g = g.sort_values("data").copy()
            f = base.fator_de_ajuste(g["data"], conf[conf["ticker"] == tk])
            for col in ("abertura", "maxima", "minima", "fechamento"):
                g[col] = g[col] * f
            partes.append(g)
        c = pd.concat(partes)
        piv = lambda col: c.pivot(index="data", columns="ticker", values=col).sort_index()
        self.fech = piv("fechamento")
        self.datas, self.tickers = self.fech.index, list(self.fech.columns)
        self.col = {t: i for i, t in enumerate(self.tickers)}
        vol = piv("volume").fillna(0)
        self.liq = (vol.rolling(60, min_periods=20).mean() >= LIQ).to_numpy()
        self.negociou = (vol > 0).to_numpy()
        F = self.fech.ffill(limit=5).to_numpy().copy()
        self.F = F
        # dia sem negócio: abertura, máxima e mínima valem o último fechamento
        self.A = np.where(np.isnan(piv("abertura").to_numpy()), F, piv("abertura").to_numpy()).copy()
        self.H = np.where(np.isnan(piv("maxima").to_numpy()), F, piv("maxima").to_numpy()).copy()
        self.L = np.where(np.isnan(piv("minima").to_numpy()), F, piv("minima").to_numpy()).copy()
        for r in ruins.itertuples():  # salto de preço sem explicação: tira o entorno
            if r.ticker in self.col:
                i = self.datas.searchsorted(r.data)
                for M in (self.F, self.A, self.H, self.L):
                    M[max(0, i - 70):i + 70, self.col[r.ticker]] = np.nan

    def pregao_seguinte(self, quando) -> int:
        d = pd.Timestamp(quando)
        i = self.datas.searchsorted(d.normalize())
        if i < len(self.datas) and self.datas[i] == d.normalize() and d.hour < 10:
            return i
        return self.datas.searchsorted(d.normalize() + pd.Timedelta(days=1))

    def caminho(self, ticker, i0, h=HORIZONTE):
        """(fechamentos, máximas, mínimas) de D0 a D+h, como variação sobre a abertura de D0. None se faltar dado."""
        if ticker not in self.col or i0 + h >= len(self.datas):
            return None
        j = self.col[ticker]
        ent = self.A[i0, j]
        blocos = [M[i0:i0 + h + 1, j] for M in (self.F, self.H, self.L)]
        if not ent or np.isnan(ent) or any(np.isnan(b).any() for b in blocos) or not self.negociou[i0, j]:
            return None
        return [b / ent - 1 for b in blocos]

    def controle(self, i0, fora, rng, n=20):
        cand = [t for k, t in enumerate(self.tickers) if self.liq[i0, k] and t not in fora]
        return list(rng.choice(cand, size=min(n, len(cand)), replace=False)) if cand else []


def juntar(P, entradas):
    cam = [P.caminho(t, i) for t, i in entradas]
    cam = [c for c in cam if c is not None]
    if not cam:
        return None
    return [np.array([c[k] for c in cam]) for k in range(3)]


def tabela_por_dia(ev, ct):
    """Fechamento em cada dia e máximo acumulado até o dia, caso x controle."""
    lin = []
    for d in DIAS:
        fe, fc = ev[0][:, d], ct[0][:, d]
        me, mc = ev[1][:, :d + 1].max(axis=1), ct[1][:, :d + 1].max(axis=1)
        lin.append({"pregão": f"D+{d}" if d else "D0 (dia da compra)", "fechou em (mediana) %": np.median(fe) * 100, "controle %": np.median(fc) * 100,
                    "acima do controle %": (np.median(fe) - np.median(fc)) * 100, "casos no positivo": (fe > 0).mean(),
                    "máximo até o dia (mediana) %": np.median(me) * 100, "máx. controle %": np.median(mc) * 100,
                    "pior até o dia (mediana) %": np.median(ev[2][:, :d + 1].min(axis=1)) * 100})
    return pd.DataFrame(lin)


def resumo_do_pico(M, nome, ate=(10, 20, 30, 60)):
    """Tamanho do máximo e em que pregão ele aconteceu, por horizonte."""
    lin = []
    for h in ate:
        h_ = M[1][:, :h + 1]
        pico, dia = h_.max(axis=1), h_.argmax(axis=1)
        lin.append({"grupo": nome, "até o pregão": f"D+{h}", "casos": len(pico), "máximo: mediana %": np.median(pico) * 100,
                    "1 em 4 passou de %": np.quantile(pico, .75) * 100, "1 em 10 passou de %": np.quantile(pico, .9) * 100,
                    "dia do máximo: mediana": np.median(dia), "metade dos casos entre os dias": f"{np.quantile(dia, .25):.0f} e {np.quantile(dia, .75):.0f}",
                    "fechou D+%d acima da compra" % h: (M[0][:, h] > 0).mean()})
    return pd.DataFrame(lin)


def alvos(M, nome, h=HORIZONTE):
    lin = {"grupo": nome, "casos": M[1].shape[0]}
    for a in ALVOS:
        bate = (M[1][:, :h + 1] >= a)
        tocou = bate.any(axis=1)
        dias = bate.argmax(axis=1)[tocou]
        # depois de tocar o alvo, a cota fechou abaixo do preço de compra em algum dia até D+h?
        devolveu = np.array([(M[0][k, d:h + 1] < 0).any() for k, d in zip(np.where(tocou)[0], dias)]) if tocou.any() else np.array([])
        lin[f"+{a:.0%}: tocou"] = tocou.mean()
        lin[f"+{a:.0%}: em quantos pregões (mediana)"] = np.median(dias) if len(dias) else np.nan
        lin[f"+{a:.0%}: depois voltou abaixo da compra"] = devolveu.mean() if len(devolveu) else np.nan
    return lin


def estudar(P, ev, titulo, grupos, rng, fora=None):
    """ev: DataFrame com ticker, quando (data e hora do anúncio). grupos: {nome: máscara}."""
    ev = ev.copy()
    ev["i0"] = [P.pregao_seguinte(q) for q in ev["quando"]]
    ev = ev[(ev["i0"] < len(P.datas) - 1)]
    ev = ev[[t in P.col and bool(P.liq[i, P.col[t]]) for t, i in zip(ev["ticker"], ev["i0"])]].reset_index(drop=True)
    fora = fora if fora is not None else set(ev["ticker"])
    ent = list(zip(ev["ticker"], ev["i0"]))
    E = juntar(P, ent)
    C = juntar(P, [(t, i) for i in sorted(set(ev["i0"])) for t in P.controle(i, fora, rng)])
    print(f"\n{'=' * 110}\n{titulo}\n{'=' * 110}")
    print(f"{len(ev)} anúncios com liquidez; {E[0].shape[0]} com os {HORIZONTE} pregões seguintes completos. Controle: {C[0].shape[0]} compras de outros fundos na mesma abertura.")
    print("\n--- dia a dia depois da compra (variação sobre o preço de abertura da compra) ---")
    print(tabela_por_dia(E, C).round(2).to_string(index=False))
    print("\n--- tamanho do máximo e dia em que ele aconteceu ---")
    print(pd.concat([resumo_do_pico(E, "anúncio"), resumo_do_pico(C, "controle")]).round(2).to_string(index=False))
    print(f"\n--- alvos: quantos tocaram, em quantos pregões, e se depois a cota voltou abaixo da compra (até D+{HORIZONTE}) ---")
    lin = [alvos(E, "anúncio"), alvos(C, "controle")]
    picos = []
    for nome, mask in grupos(ev).items():
        sub = juntar(P, [e for e, m in zip(ent, mask) if m])
        if sub is None or sub[0].shape[0] < 10:
            continue
        lin.append(alvos(sub, nome))
        picos.append(resumo_do_pico(sub, nome, ate=(10, 20, 30, 60)))
    print(pd.DataFrame(lin).round(2).to_string(index=False))
    if picos:
        print("\n--- por tipo: tamanho do máximo e dia em que aconteceu ---")
        print(pd.concat(picos).round(2).to_string(index=False))
    return ev


def main():
    con = duckdb.connect(str(config.BANCO), read_only=True)
    P = Precos(con)
    rng = np.random.default_rng(3)
    s = pd.read_parquet(config.DADOS / "saltos_anunciados.parquet").rename(columns={"entrega": "quando"})

    def grupos(ev):
        return {"aumento de 25 a 50%": (ev["razao"] < 1.5).to_numpy(), "aumento de 50 a 100%": ((ev["razao"] >= 1.5) & (ev["razao"] < 2)).to_numpy(),
                "aumento acima de 100%": (ev["razao"] >= 2).to_numpy(),
                "depois se viu: isolado": ev["classe"].str.startswith("isolado").to_numpy(),
                "depois se viu: temporário": ev["classe"].str.startswith("temporário").to_numpy(),
                "depois se viu: longo": ev["classe"].str.startswith("longo").to_numpy(),
                "até 2021": (ev["quando"] < "2022-01-01").to_numpy(), "2022 em diante": (ev["quando"] >= "2022-01-01").to_numpy()}

    estudar(P, s, "AVISO DE RENDIMENTO COM AUMENTO DE 25% OU MAIS: compra na abertura do pregão seguinte", grupos, rng)


if __name__ == "__main__":
    main()
