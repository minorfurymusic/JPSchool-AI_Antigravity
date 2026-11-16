"""Estudo do Indice de Kairi em FIIs: comprar apos queda forte do preço em relacao a media movel.

kairi_N(d) = fechamento(d) / media dos N fechamentos ate d (inclusive) - 1.
Sinal: kairi cruza para baixo de -X no dia d. Entrada na abertura do pregao seguinte.

Le SO as planilhas de planilhas/ (e fundos.csv). Escolhe a configuracao com dados da
ESCOLHA (entradas ate 31/12/2022) e mede na CONFERENCIA (entradas a partir de 01/01/2023).

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi.py 2>&1 | tee dados/kairi.txt
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

np.seterr(all="ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_colwidth", 60)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
TEC = PL / "tecnico"
TEC.mkdir(parents=True, exist_ok=True)
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

CORTE = pd.Timestamp("2022-12-31")
INICIO = pd.Timestamp("2018-01-01")
INICIO_D = np.datetime64("2018-01-01", "D")
CONF_INI = pd.Timestamp("2023-01-01")
B3 = 0.0006
EXCLUIDOS = {"XPPR11", "CARE11"}
NS = [25, 75, 200]
XS = [0.10, 0.15, 0.20, 0.30]
MANTIDOS = ["qualquer", "sim"]
SAIDAS = ["S1", "S2", "S3"]
PRAZO_S1 = 252
PRAZO_S2 = 120
LAG_REND = 126
CORTE_REND = 0.85
ABERTO = "em aberto"
SAIU = "fundo saiu da bolsa"
VOLTA = "voltou à média"
CORTADO = "rendimento cortado"
PRAZO = "prazo"
FAIXAS = ["0,30–0,60", "0,60–0,75", "0,75–0,90", "acima de 0,90"]


def pc(x):
    return "nd" if x is None or pd.isna(x) else f"{x * 100:.2f}%".replace(".", ",")


def nu(x, d=2):
    return "nd" if x is None or pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def show(df, pcts=(), nums=()):
    d = df.copy()
    for c in pcts:
        d[c] = d[c].map(pc)
    for c in nums:
        d[c] = d[c].map(lambda v: nu(v, 1))
    print(d.to_string(index=False))


# ---------------------------------------------------------------- carga (copiada de busca_modelo.py)
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base", "data_entrada"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
RD = carregar("rendimentos")
FU = carregar("fundos")

print("== COLUNAS (df.columns) ==")
for nome, df in [("precos_AAAA (todos os anos juntos)", PR), ("mercado", MK),
                 ("rendimentos", RD), ("fundos", FU)]:
    print(f"{nome}: {df.shape}")
    print("  ", list(df.columns))

C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG = "negociou (1/0)"
C_REND, C_PVP, C_PAT = "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL, C_AMO = "volume_medio_60 (R$)", "amortizacao_12m (1/0)"
for c in [C_AB, C_MX, C_MN, C_FE, C_NEG, C_REND, C_PVP, C_PAT, C_VOL, C_AMO]:
    assert c in PR.columns, c
assert "valor (R$/cota)" in RD.columns

dups = int(PR.duplicated(["fundo", "data"]).sum())
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
print(f"\nlinhas duplicadas (fundo, data) em precos removidas: {dups}")
nan_fe = int(PR[C_FE].isna().sum())
print(f"linhas de precos com fechamento NaN: {nan_fe}")
RD_NA = int(RD["data_base"].isna().sum())
RD = RD.dropna(subset=["data_base"])
print(f"rendimentos com data_base NaN (removidos): {RD_NA}; "
      f"linhas duplicadas em rendimentos (mantidas, como em busca_modelo.py): "
      f"{int(RD.duplicated(['fundo', 'data_base', 'valor (R$/cota)']).sum())}")

MD = MK["data"].to_numpy("datetime64[D]")
NM = len(MD)
SEL = MK["selic_ano (%)"].to_numpy(float)
print(f"selic NaN em mercado: {int(np.isnan(SEL).sum())} (tratada como 0 no acumulado, como em busca_modelo.py)")
CUM = np.concatenate([[0.0], np.cumsum(np.log1p(np.nan_to_num(SEL) / 100) / 252)])
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))


def faixa_de(v):
    if v is None or not np.isfinite(v) or v < 0.30 or v > 3.0:
        return None
    if v < 0.60:
        return FAIXAS[0]
    if v < 0.75:
        return FAIXAS[1]
    if v < 0.90:
        return FAIXAS[2]
    return FAIXAS[3]


def imposto(dias):
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


# ---------------------------------------------------------------- arrays por fundo (vetorizado)
FD = {}
for nome, g in PR.groupby("fundo", sort=False):
    dates = g["data"].to_numpy("datetime64[D]")
    n = len(dates)
    A = g[C_AB].to_numpy(float)
    H = g[C_MX].to_numpy(float)
    L = g[C_MN].to_numpy(float)
    C = g[C_FE].to_numpy(float)
    R = g[C_REND].to_numpy(float)
    PVP = g[C_PVP].to_numpy(float)
    PAT = g[C_PAT].to_numpy(float)
    VOL = g[C_VOL].to_numpy(float)
    AMO = g[C_AMO].to_numpy(float)
    NEG = g[C_NEG].to_numpy(float)

    # universo medido no dia d (so dados ate d)
    univ = (PAT >= 50e6) & (VOL >= 25000) & (R > 0) & (AMO == 0) & (PVP >= 0.30) & (PVP <= 3.0)
    if nome in EXCLUIDOS:
        univ[:] = False

    # pares de linhas ruins: bad[j] trata o par (j-1, j)
    bad = np.zeros(n, bool)
    if n > 1:
        gap = np.diff(dates).astype("timedelta64[D]").astype(int)
        ret = C[1:] / C[:-1] - 1
        bad[1:] = (gap > 15) | (ret > 0.60) | (ret < -0.45)
    cbad = np.r_[0, np.cumsum(bad)]          # soma de bad[0..m-1]

    Cs = pd.Series(C)
    mN = {N: Cs.rolling(N, min_periods=N).mean().to_numpy() for N in NS}   # inclui o dia
    kair = {N: C / mN[N] - 1 for N in NS}

    sim = np.zeros(n, bool)                  # rendimento hoje >= 0,95 x rendimento 126 pregoes antes
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= 0.95 * R[:-LAG_REND]

    last_pos = int(np.searchsorted(MD, dates[-1], "left"))
    FD[nome] = dict(nome=nome, n=n, dates=dates, A=A, H=H, L=L, C=C, R=R, PVP=PVP, NEG=NEG,
                    univ=univ, cbad=cbad, mN=mN, kair=kair, sim=sim,
                    aberto=last_pos >= NM - 21)      # ultimo dado nos ultimos 20 pregoes da base

RDF = {}
for f, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f] = (bd, cs)


def rend_soma(f, D, S, incl):
    """Soma de avisos com data_base >= D e < S (ou <= S se incl). Mesma regra de busca_modelo.py."""
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


# ---------------------------------------------------------------- simulador de saida
def primeiro(cond):
    if cond.size == 0 or not cond.any():
        return None
    return int(np.argmax(cond))


def fim_motivo(F):
    return ABERTO if F["aberto"] else SAIU


def simular(F, e, saida, N):
    """Saida para entrada no indice e (abertura de e). Usa a media ate k-1 para sair em k.

    Retorna (indice da saida k, motivo, preco de saida).
    """
    last = F["n"] - 1
    if saida == "S2":
        k = e + PRAZO_S2
        if k <= last:
            return k, PRAZO, F["C"][k]
        return last, fim_motivo(F), F["C"][last]

    fim = min(e + PRAZO_S1, last)
    if fim > e:
        H = F["H"][e + 1:fim + 1]
        mp = F["mN"][N][e:fim]              # mp[i] = media dos N fechamentos ate k-1, com k = e+1+i
        kv = primeiro(H >= mp)
        kc = None
        if saida == "S3" and np.isfinite(F["R"][e]):
            kc = primeiro(F["R"][e + 1:fim + 1] <= CORTE_REND * F["R"][e])
        if kc is not None and (kv is None or kc <= kv):      # corte testado antes da volta
            k = e + 1 + kc
            return k, CORTADO, F["A"][k]
        if kv is not None:
            k = e + 1 + kv
            return k, VOLTA, max(F["A"][k], mp[kv])
    if e + PRAZO_S1 <= last:
        k = e + PRAZO_S1
        return k, PRAZO, F["C"][k]
    return last, fim_motivo(F), F["C"][last]


def operar(F, s, e, saida, N):
    k, mot, px = simular(F, e, saida, N)
    ent = float(F["A"][e])
    D = F["dates"][e]
    S = F["dates"][k]
    val = px / ent - 1
    incl = mot in (PRAZO, ABERTO)
    rend = rend_soma(F["nome"], D, S, incl) / ent
    liq = val - B3 - 0.20 * max(val - B3, 0) + rend
    ie = np.searchsorted(MD, D, "left")
    isx = np.searchsorted(MD, S, "left")
    dias = int((S - D) / np.timedelta64(1, "D"))
    selic = (np.exp(CUM[isx] - CUM[ie]) - 1) * (1 - imposto(dias))
    menor = float(F["L"][e:k + 1].min() / ent - 1)
    desc = bool(F["cbad"][k + 1] - F["cbad"][e + 1] > 0)
    return dict(sinal=pd.Timestamp(F["dates"][s]), entrada=pd.Timestamp(D), saida_data=pd.Timestamp(S),
                motivo=mot, pregoes=int(k - e), preco_entrada=ent, preco_saida=float(px),
                valorizacao=val, rendimento=rend, liquido=liq, selic=selic, excesso=liq - selic,
                menor_preco=menor, descartada=desc, dias=dias, k_idx=int(k))


# ---------------------------------------------------------------- sinais
def sinais(F, N, X):
    """Sinais validos em F: cruzamento para baixo de -X, universo em d, N fechamentos,
    entrada negociada no pregao seguinte e janela da media sem salto/buraco."""
    n = F["n"]
    k = F["kair"][N]
    cross = np.zeros(n, bool)
    cross[1:] = (k[1:] <= -X) & (k[:-1] > -X)
    base = cross & F["univ"]
    base[:N] = False                          # exige N fechamentos de historico (kairi de d e de d-1)
    idx = np.flatnonzero(base)
    ent_ok = np.zeros(n, bool)
    ent_ok[:-1] = (F["NEG"][1:] == 1) & np.isfinite(F["A"][1:])
    jan = np.zeros(n, bool)
    jan[idx] = (F["cbad"][idx + 1] - F["cbad"][idx - N]) > 0    # pares j em [s-N, s]
    ok = base & ent_ok & ~jan
    cont = dict(cruz=int(base.sum()), sem_entrada=int((base & ~ent_ok).sum()),
                janela=int((base & ent_ok & jan).sum()))
    return ok, cont


SIG = {}
CONT = []
for N in NS:
    for X in XS:
        lst = []
        tot = dict(N=N, X=X, cruz=0, sem_entrada=0, janela=0)
        for F in FD.values():
            ok, c = sinais(F, N, X)
            for kk in ("cruz", "sem_entrada", "janela"):
                tot[kk] += c[kk]
            for s in np.flatnonzero(ok):
                lst.append((F, int(s)))
        SIG[(N, X)] = lst
        tot["sinais"] = len(lst)
        tot["sinais_sim"] = int(sum(F["sim"][s] for F, s in lst))
        CONT.append(tot)
print("\n== SINAIS POR CONFIGURACAO (antes do filtro de 2018 e da regra de 'um fundo por vez') ==")
show(pd.DataFrame(CONT))

# ---------------------------------------------------------------- operacoes (simula, depois aplica 'um fundo por vez')
TRADES = {}


def trade(F, N, s, saida):
    key = (N, F["nome"], s, saida)
    if key not in TRADES:
        e = s + 1
        TRADES[key] = operar(F, s, e, saida, N) if F["dates"][e] >= INICIO_D else None
    return TRADES[key]


OPS_L = []
for N in NS:
    for X in XS:
        lst = SIG[(N, X)]
        for mant in MANTIDOS:
            for saida in SAIDAS:
                busy = {}
                for F, s in lst:
                    if mant == "sim" and not F["sim"][s]:
                        continue
                    t = trade(F, N, s, saida)
                    if t is None:
                        continue
                    if busy.get(F["nome"], -1) > s:          # fundo ainda com operacao aberta nesta config
                        continue
                    busy[F["nome"]] = t["k_idx"]
                    rec = {k: v for k, v in t.items() if k != "k_idx"}
                    OPS_L.append(dict(N=N, X=X, mantido=mant, saida=saida, fundo=F["nome"],
                                      kairi_sinal=float(F["kair"][N][s]), pvp_sinal=float(F["PVP"][s]),
                                      **rec))

OPS = pd.DataFrame(OPS_L)
OPS["fechada"] = (OPS["motivo"] != ABERTO) & (~OPS["descartada"])
OPS["periodo"] = np.where(OPS["entrada"] <= CORTE, "ESCOLHA", "CONFERENCIA")
OPS["ano"] = OPS["entrada"].dt.year
OPS["tipo_fundo"] = OPS["fundo"].map(TIPO).fillna("sem tipo")
OPS["faixa_pvp"] = pd.cut(OPS["pvp_sinal"], bins=[0.30, 0.60, 0.75, 0.90, 10.0], labels=FAIXAS,
                          right=False).astype(str)
print(f"\noperacoes geradas (todas as configs): {len(OPS)}; descartadas pela guarda de qualidade: "
      f"{int(OPS['descartada'].sum())}; em aberto: {int((OPS['motivo'] == ABERTO).sum())}")


# ---------------------------------------------------------------- estatisticas
def stats_df(d):
    if len(d) == 0:
        return dict(n=0, preg=np.nan, alta=np.nan, val=np.nan, rend=np.nan, liq=np.nan, selic=np.nan,
                    exc=np.nan, exc_med=np.nan, pos=np.nan, menor=np.nan)
    return dict(n=int(len(d)), preg=float(d.pregoes.mean()), alta=float((d.valorizacao > 0).mean()),
                val=float(d.valorizacao.mean()), rend=float(d.rendimento.mean()),
                liq=float(d.liquido.mean()), selic=float(d.selic.mean()), exc=float(d.excesso.mean()),
                exc_med=float(d.excesso.median()), pos=float((d.excesso > 0).mean()),
                menor=float(d.menor_preco.mean()))


def curto(d):
    if len(d) == 0:
        return dict(n=0, liq=np.nan, selic=np.nan, exc=np.nan, pos=np.nan)
    return dict(n=int(len(d)), liq=float(d.liquido.mean()), selic=float(d.selic.mean()),
                exc=float(d.excesso.mean()), pos=float((d.excesso > 0).mean()))


# ---------------------------------------------------------------- T1
print("\n== T1 - 72 CONFIGURACOES (ESCOLHA x CONFERENCIA) ==")
PCT_COLS = ["alta", "val", "rend", "liq", "selic", "exc", "exc_med", "pos", "menor"]
linhas = []
for N in NS:
    for X in XS:
        for mant in MANTIDOS:
            for saida in SAIDAS:
                sub = OPS[(OPS.N == N) & (OPS.X == X) & (OPS.mantido == mant) & (OPS.saida == saida)]
                row = dict(N=N, X=X, mantido=mant, saida=saida)
                for pref, mask in [("E_", sub.periodo == "ESCOLHA"), ("C_", sub.periodo == "CONFERENCIA")]:
                    d = sub[mask & sub.fechada]
                    row.update({pref + k: v for k, v in stats_df(d).items()})
                    row[pref + "abertas"] = int((mask & (sub.motivo == ABERTO)).sum())
                    row[pref + "descart"] = int((mask & sub.descartada).sum())
                linhas.append(row)
T1 = pd.DataFrame(linhas)
T1.to_csv(TEC / "kairi_configuracoes.csv", **OPC)

cols_t1 = ["N", "X", "mantido", "saida"]
for pref in ["E_", "C_"]:
    cols_t1 += [pref + c for c in ["n", "preg", "alta", "val", "rend", "liq", "selic", "exc", "exc_med", "pos", "menor"]]
disp = T1[cols_t1].copy()
disp["X"] = disp["X"].map(lambda v: nu(v, 2))
disp.columns = [c.replace("E_", "E.").replace("C_", "C.").replace("exc_med", "excmed").replace("alta", "%alta")
                .replace("pos", "%ganh") for c in disp.columns]
show(disp, pcts=[c for c in disp.columns if c.split(".")[-1] in
                 ("%alta", "val", "rend", "liq", "selic", "exc", "excmed", "%ganh", "menor")],
     nums=["E.preg", "C.preg"])

# ---------------------------------------------------------------- T2
print("\n== T2 - CORRELACAO E QUANTAS CONFIGURACOES DAO EXCESSO POSITIVO ==")
ok2 = (T1.E_n >= 30) & (T1.C_n >= 30)
rho = T1.loc[ok2, "E_exc"].rank().corr(T1.loc[ok2, "C_exc"].rank())
print(f"configs com n >= 30 nos dois periodos: {int(ok2.sum())}")
print(f"Spearman (excesso medio ESCOLHA x CONFERENCIA): {nu(rho, 3)}")
pos_e = int((T1.E_exc > 0).sum())
pos_c = int((T1.C_exc > 0).sum())
pos_ambos = int(((T1.E_exc > 0) & (T1.C_exc > 0)).sum())
print(f"das 72: excesso medio > 0 na ESCOLHA = {pos_e}; na CONFERENCIA = {pos_c}; nos DOIS = {pos_ambos}")

# ---------------------------------------------------------------- T3 base de comparacao
print("\n== T3 - BASE DE COMPARACAO: 3.000 pares (fundo, dia) do universo, sem Kairi, entrada seguinte, S2 (120) ==")
POOL = []
for F in FD.values():
    n = F["n"]
    if n < 2:
        continue
    ok = np.zeros(n, bool)
    ok[:-1] = F["univ"][:-1] & (F["NEG"][1:] == 1) & np.isfinite(F["A"][1:]) & (F["dates"][1:] >= INICIO_D)
    for s in np.flatnonzero(ok):
        POOL.append((F, int(s)))
rng = np.random.default_rng(42)
amostra = rng.choice(len(POOL), size=min(3000, len(POOL)), replace=False)
base_l = []
for i in amostra:
    F, s = POOL[i]
    t = operar(F, s, s + 1, "S2", 0)
    base_l.append(t)
BASE = pd.DataFrame(base_l)
BASE = BASE[~BASE["descartada"]]
BASE["periodo"] = np.where(BASE["entrada"] <= CORTE, "ESCOLHA", "CONFERENCIA")
print(f"pares no universo (pool): {len(POOL)}; amostra: {len(amostra)}; descartadas pela guarda: "
      f"{int(len(base_l) - len(BASE))}; em aberto: {int((BASE.motivo == ABERTO).sum())}")
rows3 = []
for per in ["ESCOLHA", "CONFERENCIA"]:
    d = BASE[(BASE.periodo == per) & (BASE.motivo != ABERTO)]
    rows3.append(dict(periodo=per, **curto(d), preg=float(d.pregoes.mean()) if len(d) else np.nan))
d = BASE[BASE.motivo != ABERTO]
rows3.append(dict(periodo="TOTAL", **curto(d), preg=float(d.pregoes.mean()) if len(d) else np.nan))
show(pd.DataFrame(rows3), pcts=["liq", "selic", "exc", "pos"], nums=["preg"])


# ---------------------------------------------------------------- T4 / T5
def tabela_ano(d, titulo):
    print(f"\n{titulo}")
    rows = []
    for ano, g in d.groupby(d["entrada"].dt.year):
        rows.append(dict(linha=str(ano), **curto(g)))
    rows.append(dict(linha="TOTAL ESCOLHA", **curto(d[d.entrada <= CORTE])))
    rows.append(dict(linha="TOTAL CONFERENCIA", **curto(d[d.entrada > CORTE])))
    rows.append(dict(linha="TOTAL", **curto(d)))
    show(pd.DataFrame(rows), pcts=["liq", "selic", "exc", "pos"])


def tabela_grupo(d, col, titulo, fn=None):
    print(f"\n{titulo}")
    rows = []
    for v, g in d.groupby(col, observed=True):
        r = dict(grupo=str(v), **curto(g))
        r["preg"] = float(g.pregoes.mean())
        rows.append(r)
    show(pd.DataFrame(rows), pcts=["liq", "selic", "exc", "pos"], nums=["preg"])


def analisa(cfg, titulo, completo):
    N, X, mant, saida = cfg
    sub = OPS[(OPS.N == N) & (OPS.X == X) & (OPS.mantido == mant) & (OPS.saida == saida)]
    fe = sub[sub.fechada]
    print(f"\n==================== {titulo}: N={N}, X={X:.2f}, mantido={mant}, saida={saida} ====================")
    print(f"operacoes fechadas: {len(fe)}; em aberto: {int((sub.motivo == ABERTO).sum())}; "
          f"descartadas: {int(sub.descartada.sum())}")
    tabela_ano(fe, f"{titulo} - POR ANO DE ENTRADA (fechadas)")
    if not completo:
        return sub
    tabela_grupo(fe, "motivo", f"{titulo} - POR MOTIVO DE SAIDA (fechadas)")
    print(f"{titulo} - por motivo (n, pregoes, liquido, excesso) acima")
    tabela_grupo(fe, "tipo_fundo", f"{titulo} - POR TIPO DE FUNDO (fundos.csv)")
    tabela_grupo(fe, "faixa_pvp", f"{titulo} - POR FAIXA DE PRECO SOBRE VALOR PATRIMONIAL NO SINAL")
    cols = ["fundo", "entrada", "saida_data", "motivo", "pregoes", "liquido", "excesso"]
    fm = fe.copy()
    fm["entrada"] = fm.entrada.dt.strftime("%d/%m/%Y")
    fm["saida_data"] = fm.saida_data.dt.strftime("%d/%m/%Y")
    print(f"\n{titulo} - 5 PIORES operacoes (por excesso):")
    show(fm.nsmallest(5, "excesso")[cols], pcts=["liquido", "excesso"])
    print(f"\n{titulo} - 5 MELHORES operacoes (por excesso):")
    show(fm.nlargest(5, "excesso")[cols], pcts=["liquido", "excesso"])
    ab = sub[sub.motivo == ABERTO].copy()
    print(f"\n{titulo} - EM ABERTO: {len(ab)} (fora das medias)")
    if len(ab):
        ab["entrada"] = ab.entrada.dt.strftime("%d/%m/%Y")
        show(ab[["fundo", "entrada", "preco_entrada", "preco_saida", "pregoes", "valorizacao", "rendimento"]]
             .rename(columns={"preco_saida": "preco_atual"}),
             pcts=["valorizacao", "rendimento"], nums=[])
    return sub


ELEG = T1[(T1.E_n >= 30) & (T1.C_n >= 30)]
print("\n== T4 - CONFIGURACAO ESCOLHIDA PELA ESCOLHA (maior excesso medio na ESCOLHA, n >= 30 nos dois) ==")
if ELEG.empty:
    print("nenhuma configuracao com n >= 30 nos dois periodos")
    sub4 = OPS.iloc[0:0]
else:
    best = ELEG.loc[ELEG.E_exc.idxmax()]
    cfg4 = (int(best.N), float(best.X), best.mantido, best.saida)
    print(f"escolhida: N={cfg4[0]}, X={cfg4[1]:.2f}, mantido={cfg4[2]}, saida={cfg4[3]} "
          f"(excesso medio ESCOLHA {pc(best.E_exc)}, n ESCOLHA {int(best.E_n)}; n CONFERENCIA {int(best.C_n)}; "
          f"a CONFERENCIA nao entrou na escolha)")
    sub4 = analisa(cfg4, "T4", completo=True)

cfg5 = (200, 0.20, "sim", "S3")
print("\n== T5 - APOSTA DEFINIDA ANTES (N=200, X=0.20, mantido=sim, S3) ==")
sub5 = analisa(cfg5, "T5", completo=False)
ex5 = T1[(T1.N == 200) & (T1.X == 0.20) & (T1.mantido == "sim") & (T1.saida == "S3")]
print(f"T5 total: ESCOLHA n={int(ex5.E_n.iloc[0])} exc={pc(ex5.E_exc.iloc[0])} | "
      f"CONFERENCIA n={int(ex5.C_n.iloc[0])} exc={pc(ex5.C_exc.iloc[0])}")

# operacoes gravadas
OPS_CSV = pd.concat([sub4.assign(escolha="T4"), sub5.assign(escolha="T5")], ignore_index=True)
OPS_CSV = OPS_CSV.drop(columns=["k_idx"], errors="ignore")
OPS_CSV.to_csv(TEC / "kairi_operacoes.csv", **OPC)
print(f"\ngravados: planilhas/tecnico/kairi_configuracoes.csv ({len(T1)} linhas), "
      f"planilhas/tecnico/kairi_operacoes.csv ({len(OPS_CSV)} linhas)")


# ---------------------------------------------------------------- CONFERENCIAS
print("\n== CONFERENCIAS ==")
print(f"1) Roda sem erro. Operacoes descartadas pela guarda: total {int(OPS.descartada.sum())} "
      f"de {len(OPS)} geradas (ESCOLHA {int((OPS.descartada & (OPS.periodo == 'ESCOLHA')).sum())}, "
      f"CONFERENCIA {int((OPS.descartada & (OPS.periodo == 'CONFERENCIA')).sum())}); "
      f"base T3: {int(len(base_l) - len(BASE))} descartadas.")


def recalcular(op, N, saida):
    """Refaz uma operacao com laco simples, lendo as planilhas de novo (sem usar FD nem simular)."""
    f = op["fundo"]
    ds = pd.Timestamp(op["sinal"])
    g = PR[PR["fundo"] == f].reset_index(drop=True)
    s = int(g.index[g["data"] == ds][0])
    N_ = N
    C = g[C_FE].to_numpy(float)
    A = g[C_AB].to_numpy(float)
    H = g[C_MX].to_numpy(float)
    R = g[C_REND].to_numpy(float)
    NEG = g[C_NEG].to_numpy(float)
    last = len(g) - 1
    print(f"\n--- {f}: sinal em {ds.date()} (linha {s} de {last}, valor de D: {g.loc[s, 'data'].date()})")
    jan = C[s - N_ + 1:s + 1]
    jan_v = C[s - N_:s]
    print(f"  janela de {N_} fechamentos ate d: primeiro {g.loc[s - N_ + 1, 'data'].date()} = {jan[0]:.4f}; "
          f"ultimo {g.loc[s, 'data'].date()} = {jan[-1]:.4f}; media = {jan.mean():.4f}")
    k_d = C[s] / jan.mean() - 1
    k_v = C[s - 1] / jan_v.mean() - 1
    print(f"  kairi(d) = {k_d:.6f} (<= -0,20: {k_d <= -0.20}) | kairi(d-1) = {k_v:.6f} (> -0,20: {k_v > -0.20})")
    e = s + 1
    ent = A[e]
    print(f"  entrada {g.loc[e, 'data'].date()}: abertura = {ent:.4f}, negociou = {NEG[e]:.0f}; "
          f"preco_entrada no script = {op['preco_entrada']:.4f}")
    kk = None
    mot = None
    px = None
    media_saida = None
    for k in range(e + 1, min(e + PRAZO_S1, last) + 1):
        if saida == "S3" and np.isfinite(R[e]) and R[k] <= CORTE_REND * R[e]:
            kk, mot, px = k, CORTADO, A[k]
            break
        m_prev = C[k - N_:k].mean()
        if H[k] >= m_prev:
            kk, mot, px, media_saida = k, VOLTA, max(A[k], m_prev), m_prev
            break
    if kk is None:
        if e + PRAZO_S1 <= last:
            kk, mot, px = e + PRAZO_S1, PRAZO, C[e + PRAZO_S1]
        else:
            kk, mot, px = last, (ABERTO if g.loc[last, 'data'] >= MK['data'].iloc[NM - 21] else SAIU), C[last]
    d_e = g.loc[e, "data"]
    d_s = g.loc[kk, "data"]
    print(f"  saida {d_s.date()} (pregao {kk - e} depois da entrada): motivo = {mot}; preco usado = {px:.4f}; "
          f"maxima do dia = {H[kk]:.4f}; abertura do dia = {A[kk]:.4f}"
          + (f"; media dos {N_} fechamentos ate k-1 = {media_saida:.4f}" if media_saida is not None else ""))
    val = px / ent - 1
    incl = mot in (PRAZO, ABERTO)
    av = RD[(RD["fundo"] == f) & (RD["data_base"] >= d_e) &
            ((RD["data_base"] <= d_s) if incl else (RD["data_base"] < d_s))]
    print(f"  avisos de rendimento ({'data_base <= saida' if incl else 'data_base < saida'}):")
    for _, rr in av.iterrows():
        print(f"    data_base {rr['data_base'].date()} valor {rr['valor (R$/cota)']:.4f}")
    rend = av["valor (R$/cota)"].sum() / ent
    liq = val - B3 - 0.20 * max(val - B3, 0) + rend
    mk = MK[(MK["data"] >= d_e) & (MK["data"] < d_s)]
    prod = 1.0
    for sv in mk["selic_ano (%)"].fillna(0):
        prod *= (1 + sv / 100) ** (1 / 252)
    dias = (d_s - d_e).days
    selic = (prod - 1) * (1 - imposto(dias))
    print(f"  valorizacao = {val:.6f} | rendimento = {rend:.6f} | liquido = {liq:.6f}")
    print(f"  selic: {len(mk)} pregoes, dias corridos = {dias}, imposto = {imposto(dias)}, selic liquida = {selic:.6f}")
    print(f"  excesso = {liq - selic:.6f}")
    print(f"  script: pregoes = {op['pregoes']}, motivo = {op['motivo']}, valorizacao = {op['valorizacao']:.6f}, "
          f"rendimento = {op['rendimento']:.6f}, liquido = {op['liquido']:.6f}, selic = {op['selic']:.6f}, "
          f"excesso = {op['excesso']:.6f}")
    print(f"  diferenca |excesso manual - script| = {abs((liq - selic) - op['excesso']):.2e}")


fech5 = sub5[sub5.fechada].sort_values("entrada").reset_index(drop=True)
if len(fech5):
    for idx in sorted({0, len(fech5) // 2}):
        recalcular(fech5.iloc[idx], 200, "S3")
else:
    print("sem operacoes fechadas na T5 para refazer")

print("\n4) Configs com n >= 30 e |excesso medio| > 15% (ESCOLHA ou CONFERENCIA): 5 mais extremas (fechadas)")
flag = T1[((T1.E_n >= 30) & (T1.E_exc.abs() > 0.15)) | ((T1.C_n >= 30) & (T1.C_exc.abs() > 0.15))]
if flag.empty:
    print("  nenhuma")
for r in flag.itertuples():
    sub = OPS[(OPS.N == r.N) & (OPS.X == r.X) & (OPS.mantido == r.mantido) & (OPS.saida == r.saida) & OPS.fechada]
    print(f"\n  N={r.N}, X={r.X:.2f}, mantido={r.mantido}, saida={r.saida}: "
          f"ESCOLHA n={r.E_n} exc={pc(r.E_exc)} | CONFERENCIA n={r.C_n} exc={pc(r.C_exc)}")
    ext = pd.concat([sub.nlargest(5, "excesso"), sub.nsmallest(5, "excesso")])
    ext = ext.assign(entrada=ext.entrada.dt.strftime("%d/%m/%Y"), saida_data=ext.saida_data.dt.strftime("%d/%m/%Y"))
    show(ext[["fundo", "entrada", "saida_data", "motivo", "pregoes", "liquido", "excesso", "periodo"]],
         pcts=["liquido", "excesso"])

print(f"\nTempo total: {time.time() - T0:.1f} s")
