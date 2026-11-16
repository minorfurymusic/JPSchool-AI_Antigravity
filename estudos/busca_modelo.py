"""Busca disciplinada de regras de entrada e saida em FIIs.

Le SO as planilhas de planilhas/. Escolhe regras com dados de TREINO
(entradas ate 31/12/2022) e mede em TESTE (entradas a partir de 01/01/2023).

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/busca_modelo.py 2>&1 | tee dados/busca_modelo.txt
"""
import itertools
import time
from pathlib import Path

import numpy as np
import pandas as pd

np.seterr(all="ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_colwidth", 60)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
TEC = PL / "tecnico"
TEC.mkdir(parents=True, exist_ok=True)
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")

CORTE = pd.Timestamp("2022-12-31")
B3 = 0.0006
ALVOS = [None, 0.05, 0.07, 0.10, 0.15]
LIMITES = [None, -0.07, -0.10, -0.15]
PRAZOS = [60, 120, 252]
SAIRS = [False, True]
ABERTO = "em aberto"
SAIU = "fundo saiu da bolsa"

GRUPOS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "BONS"]
GRUPO_NOME = {
    "G1": "fundo declarou aumento", "G2": "venda de imovel", "G3": "recebimento extraordinario",
    "G4": "locacao nova", "G5": "aumento citado no texto", "G6": "noticia ruim",
    "G7": "outros assuntos", "BONS": "BONS (G1 a G5)",
}
BONS_SET = ["G1", "G2", "G3", "G4", "G5"]
FAIXAS = ["0,30–0,60", "0,60–0,75", "0,75–0,90", "acima de 0,90"]
ACIMAS = ["sim", "não", "tanto faz"]
REGIMES = ["subiu", "caiu", "parada", "tanto faz"]


def pc(x):
    return "nd" if x is None or pd.isna(x) else f"{x * 100:.2f}%".replace(".", ",")


def nu(x, d=2):
    return "nd" if x is None or pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def show(df, pcts=(), nums=()):
    d = df.copy()
    for c in pcts:
        d[c] = d[c].map(pc)
    for c in nums:
        d[c] = d[c].map(nu)
    print(d.to_string(index=False))


# ---------------------------------------------------------------- carga
def carregar(nome):
    df = pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    for c in ["data", "data_conhecido", "data_base", "data_entrada"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], format="%d/%m/%Y")
    return df


PR = pd.concat([carregar(a.stem) for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
MK = carregar("mercado").sort_values("data").reset_index(drop=True)
RD = carregar("rendimentos")
AN = carregar("anuncios")
FU = carregar("fundos")

print("== COLUNAS (df.columns) ==")
for nome, df in [("precos_AAAA (todos os anos juntos)", PR), ("mercado", MK),
                 ("rendimentos", RD), ("anuncios", AN), ("fundos", FU)]:
    print(f"{nome}: {df.shape}")
    print("  ", list(df.columns))

C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_REND, C_PVP, C_PAT = "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL60, C_AMO, C_NEG = "volume_medio_60 (R$)", "amortizacao_12m (1/0)", "negociou (1/0)"
for c in [C_AB, C_MX, C_MN, C_FE, C_REND, C_PVP, C_PAT, C_VOL60, C_AMO]:
    assert c in PR.columns, c

dups = PR.duplicated(["fundo", "data"]).sum()
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"])
print(f"\nlinhas duplicadas (fundo, data) em precos removidas: {dups}")
print(f"selic NaN em mercado: {int(MK['selic_ano (%)'].isna().sum())}")
print(f"linhas duplicadas em rendimentos (mantidas, como manda o pedido): "
      f"{int(RD.duplicated(['fundo', 'data_base', 'valor (R$/cota)']).sum())}")

MD = MK["data"].to_numpy("datetime64[D]")
NM = len(MD)
SEL = MK["selic_ano (%)"].to_numpy(float)
CUM = np.concatenate([[0.0], np.cumsum(np.log1p(np.nan_to_num(SEL) / 100) / 252)])
TIPO_FUNDO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))


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


def regime_de(d):
    if d is None or not np.isfinite(d):
        return "sem dado"
    if d >= 0.5:
        return "subiu"
    if d <= -0.5:
        return "caiu"
    return "parada"


def grupo_de(decl, tipo):
    if decl == "aumento":
        return "G1"
    if tipo in ("venda_com_ganho", "venda"):
        return "G2"
    if tipo == "recebimento":
        return "G3"
    if tipo == "locacao_nova":
        return "G4"
    if tipo == "rendimento_aumento":
        return "G5"
    if decl == "reducao" or tipo in ("saida_inquilino", "rendimento_reducao", "venda_com_perda"):
        return "G6"
    return "G7"


# ---------------------------------------------------------------- arrays por fundo (so passado ate o dia)
FD = {}
for f, g in PR.groupby("fundo", sort=False):
    dates = g["data"].to_numpy("datetime64[D]")
    A = g[C_AB].to_numpy(float)
    H = g[C_MX].to_numpy(float)
    Lo = g[C_MN].to_numpy(float)
    C = g[C_FE].to_numpy(float)
    R = g[C_REND].to_numpy(float)
    PVP = g[C_PVP].to_numpy(float)
    PAT = g[C_PAT].to_numpy(float)
    VOL = g[C_VOL60].to_numpy(float)
    AMO = g[C_AMO].to_numpy(float)
    n = len(dates)
    Cp = np.r_[np.nan, C[:-1]]                       # fechamento da vespera
    mm = pd.Series(C).rolling(200).mean().to_numpy()
    mmp = np.r_[np.nan, mm[:-1]]                      # media dos 200 anteriores (sem o dia)
    rm = pd.Series(C).rolling(252).max().to_numpy()
    rmp = np.r_[np.nan, rm[:-1]]                      # maior fechamento dos 252 anteriores
    acima = np.where(np.isnan(mmp), "sem dado", np.where(Cp > mmp, "sim", "não")).astype(object)
    last_idx = np.searchsorted(MD, dates[-1], "left")
    FD[f] = dict(dates=dates, n=n, A=A, H=H, L=Lo, C=C, R=R, PVP=PVP, PAT=PAT, VOL=VOL, AMO=AMO,
                 Cp=Cp, mmp=mmp, rmp=rmp, acima=acima,
                 pvp_p=np.r_[np.nan, PVP[:-1]], pat_p=np.r_[np.nan, PAT[:-1]],
                 vol_p=np.r_[np.nan, VOL[:-1]],
                 aberto=bool(last_idx >= NM - 21))  # ultimo dado nos ultimos 20 pregoes da base

RDF = {}
for f, g in RD.sort_values("data_base").groupby("fundo"):
    bd = g["data_base"].to_numpy("datetime64[D]")
    cs = np.concatenate([[0.0], np.cumsum(g["valor (R$/cota)"].to_numpy(float))])
    RDF[f] = (bd, cs)


def rend_soma(f, D, S, incl):
    if f not in RDF:
        return 0.0
    bd, cs = RDF[f]
    a = np.searchsorted(bd, D, "left")
    b = np.searchsorted(bd, S, "right" if incl else "left")
    return float(cs[b] - cs[a]) if b > a else 0.0


# ---------------------------------------------------------------- simulador
def prep(f, i0, ent, cid=-1):
    F = FD[f]
    n = F["n"]
    L = min(253, n - i0)
    sl = slice(i0, i0 + L)
    R = F["R"][sl]
    return dict(f=f, cid=cid, i0=i0, L=L, fim=(i0 + L == n), aberto=F["aberto"], ent=float(ent),
                D=F["dates"][i0], datas=F["dates"][sl], A=F["A"][sl], H=F["H"][sl], Lo=F["L"][sl],
                C=F["C"][sl], R=R, cm=np.maximum.accumulate(np.where(np.isnan(R), -np.inf, R)),
                cache={})


def memo(p, chave, fn):
    c = p["cache"]
    if chave not in c:
        c[chave] = fn()
    return c[chave]


def primeiro(cond):
    if cond.size == 0:
        return None
    k = int(np.argmax(cond))
    return k if cond[k] else None


def simular1(p, alvo, limite, prazo, sair):
    """Acha o dia de saida. Prioridade no mesmo dia: 1 rendimento, 2 limite, 3 alvo, 4 prazo, 5 fim dos dados."""
    ent = p["ent"]
    ev = []
    if sair:
        k = memo(p, "cut", lambda: primeiro((p["R"] <= 0.9 * p["cm"]) & (np.arange(p["L"]) > 0)))
        if k is not None:
            ev.append((k, 0, "rendimento caiu"))
    if limite is not None:
        k = memo(p, ("lim", limite), lambda: primeiro(p["Lo"] <= ent * (1 + limite)))
        if k is not None:
            ev.append((k, 1, "limite de perda"))
    if alvo is not None:
        k = memo(p, ("alv", alvo), lambda: primeiro(p["H"] >= ent * (1 + alvo)))
        if k is not None:
            ev.append((k, 2, "alvo"))
    if prazo <= p["L"] - 1:
        ev.append((prazo, 3, "prazo"))
    if p["fim"]:
        ev.append((p["L"] - 1, 4, ABERTO if p["aberto"] else SAIU))
    k, prio, mot = min(ev, key=lambda e: (e[0], e[1]))
    O = p["A"][k]
    if prio == 0:
        px = O
    elif prio == 1:
        px = min(O, ent * (1 + limite))
    elif prio == 2:
        px = max(O, ent * (1 + alvo))
    else:
        px = p["C"][k]
    return k, mot, px


def operar(p, alvo, limite, prazo, sair):
    k, mot, px = simular1(p, alvo, limite, prazo, sair)
    ent, D, S = p["ent"], p["D"], p["datas"][k]
    val = px / ent - 1
    rend = rend_soma(p["f"], D, S, mot in ("prazo", ABERTO)) / ent
    liq = val - B3 - 0.20 * max(val - B3, 0) + rend
    ie = np.searchsorted(MD, D, "left")
    isx = np.searchsorted(MD, S, "left")
    selic_b = np.exp(CUM[isx] - CUM[ie]) - 1
    dias = int((S - D) / np.timedelta64(1, "D"))
    imp = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
    selic = selic_b * (1 - imp)
    return dict(cid=p["cid"], fundo=p["f"], entrada=pd.Timestamp(D), saida=pd.Timestamp(S), pregoes=int(k),
                motivo=mot, ent=ent, preco_saida=float(px), valorizacao=val, rendimento=rend,
                liquido=liq, selic=selic, excesso=liq - selic, dias=dias, ik=p["i0"] + int(k))


# ---------------------------------------------------------------- Passo 1: candidatos
print("\n== PASSO 1: candidatos a entrada ==")
AN["cid"] = np.arange(len(AN))
print(f"anuncios lidos: {len(AN)}")
X = AN.copy()
FILTROS = [
    ("repetido == 0", lambda d: d["repetido (1/0)"] == 0),
    ("preco_entrada preenchido e negociou_na_entrada == 1",
     lambda d: d["preco_entrada"].notna() & (d["negociou_na_entrada (1/0)"] == 1)),
    ("patrimonio >= 50 milhoes", lambda d: d["patrimonio (R$)"] >= 50e6),
    ("ordem_maxima >= 500", lambda d: d["ordem_maxima (R$)"] >= 500),
    ("rendimento mensal na entrada > 0", lambda d: d["rendimento_mensal_na_entrada (R$/cota)"] > 0),
    ("P/VP entre 0,30 e 3,0", lambda d: d["preco_sobre_valor_patrimonial"].between(0.30, 3.0)),
    ("data_entrada >= 01/01/2018", lambda d: d["data_entrada"] >= pd.Timestamp("2018-01-01")),
    ("fundo diferente de XPPR11", lambda d: d["fundo"] != "XPPR11"),
]
for nome, fn in FILTROS:
    antes = len(X)
    X = X[fn(X)]
    print(f"  {nome}: saem {antes - len(X)}, restam {len(X)}")

PREP = {}
linhas = []
saem_fundo = saem_linha = saem_amort = 0
for _, r in X.iterrows():
    f = r["fundo"]
    F = FD.get(f)
    if F is None:
        saem_fundo += 1
        continue
    D = np.datetime64(r["data_entrada"].date(), "D")
    i0 = int(np.searchsorted(F["dates"], D, "left"))
    if i0 >= F["n"] or F["dates"][i0] != D:
        saem_linha += 1
        continue
    if F["AMO"][i0] == 1:
        saem_amort += 1
        continue
    ent = float(r["preco_entrada"])
    pvp = float(r["preco_sobre_valor_patrimonial"])
    mi = int(np.searchsorted(MD, D, "left"))
    if mi >= 126 and MD[mi] == D and np.isfinite(SEL[mi]) and np.isfinite(SEL[mi - 126]):
        reg = regime_de(SEL[mi] - SEL[mi - 126])
    else:
        reg = "sem dado"
    dm = F["Cp"][i0] / F["rmp"][i0] - 1 if np.isfinite(F["rmp"][i0]) else np.nan
    grp = grupo_de(r["declarou_efeito"], r["tipo"])
    cid = int(r["cid"])
    feat = dict(cid=cid, fundo=f, entrada=r["data_entrada"], ent=ent, grupo=grp,
                faixa=faixa_de(pvp), acima=F["acima"][i0], regime=reg, dist_max=dm,
                passa_regua=bool(r["rendimento_ano_sobre_preco (%)"] >= r["selic_ano (%)"] * 0.825 + 3),
                tipo_fundo=TIPO_FUNDO.get(f, "sem tipo"), ordem=float(r["ordem_maxima (R$)"]),
                ano=int(r["data_entrada"].year), pvp=pvp)
    linhas.append(feat)
    p = prep(f, i0, ent, cid)
    p.update(grupo=grp, faixa=feat["faixa"], acima=feat["acima"], regime=reg)
    PREP[cid] = p

print(f"  sem linha de preco na entrada: saem {saem_linha}")
print(f"  amortizacao_12m == 1 na entrada: saem {saem_amort}")
print(f"  fundo sem historico em precos: saem {saem_fundo}")
CAND = pd.DataFrame(linhas)
print(f"CANDIDATOS FINAIS: {len(CAND)}")
print("  por grupo:", CAND["grupo"].value_counts().sort_index().to_dict())
print("  acima_mm200:", CAND["acima"].value_counts().to_dict())
print("  selic_regime:", CAND["regime"].value_counts().to_dict())
print("  faixa_pvp:", CAND["faixa"].value_counts().to_dict())
print("  dist_max sem dado:", int(CAND["dist_max"].isna().sum()))

# ---------------------------------------------------------------- Passo 3 ETAPA A: saida neutra
print("\n== PASSO 3 - ETAPA A: entradas (saida neutra: prazo 120, sem alvo, sem limite, sem corte) ==")
res_a = [operar(PREP[c], None, None, 120, False) for c in CAND["cid"]]
RA = pd.DataFrame(res_a)
CAND["ex_A"] = RA["excesso"].to_numpy()
CAND["fec_A"] = (RA["motivo"] != ABERTO).to_numpy()
CAND["motivo_A"] = RA["motivo"].to_numpy()
CAND["treino"] = CAND["entrada"] <= CORTE
EX = CAND["ex_A"].to_numpy(float)
FEC = CAND["fec_A"].to_numpy(bool)
TR = CAND["treino"].to_numpy(bool)
print(f"operacoes fechadas: {int(FEC.sum())}; em aberto: {int((~FEC).sum())}; "
      f"treino (fechadas): {int((FEC & TR).sum())}; teste (fechadas): {int((FEC & ~TR).sum())}")


def estat(ex):
    ex = np.asarray(ex, float)
    if ex.size == 0:
        return dict(n=0, media=np.nan, mediana=np.nan, pos=np.nan)
    return dict(n=int(ex.size), media=float(ex.mean()), mediana=float(np.median(ex)), pos=float((ex > 0).mean()))


def mascara(g, fx, ac, rg):
    m = np.ones(len(CAND), bool)
    m &= CAND["grupo"].isin(BONS_SET).to_numpy() if g == "BONS" else (CAND["grupo"] == g).to_numpy()
    if fx != "todas":
        m &= (CAND["faixa"] == fx).to_numpy()
    if ac != "tanto faz":
        m &= (CAND["acima"] == ac).to_numpy()
    if rg != "tanto faz":
        m &= (CAND["regime"] == rg).to_numpy()
    return m


def stats_mask(m):
    tr = estat(EX[m & FEC & TR])
    te = estat(EX[m & FEC & ~TR])
    return tr, te


rows_cel = []
CELULAS = {}
for g, fx, ac, rg in itertools.product(GRUPOS, FAIXAS + ["todas"], ACIMAS, REGIMES):
    m = mascara(g, fx, ac, rg)
    tr, te = stats_mask(m)
    lab = f"{GRUPO_NOME[g]} | pvp {fx} | acima mm200 {ac} | selic {rg}"
    CELULAS[(g, fx, ac, rg)] = dict(mask=m, lab=lab, tr=tr, te=te)
    rows_cel.append(dict(grupo=g, faixa_pvp=fx, acima_mm200=ac, selic_regime=rg,
                         n_treino=tr["n"], excesso_medio_treino=tr["media"], excesso_mediano_treino=tr["mediana"],
                         pct_positivo_treino=tr["pos"], n_teste=te["n"], excesso_medio_teste=te["media"],
                         excesso_mediano_teste=te["mediana"], pct_positivo_teste=te["pos"]))
TAB_CEL = pd.DataFrame(rows_cel)
TAB_CEL.to_csv(TEC / "busca_celulas.csv", **OPC)
print(f"celulas definidas: {len(TAB_CEL)}; com n_treino > 0: {int((TAB_CEL.n_treino > 0).sum())}; "
      f"com n_treino >= 20: {int((TAB_CEL.n_treino >= 20).sum())}")

BIG = TAB_CEL[TAB_CEL.n_treino >= 20].copy()
BIG["lab"] = [CELULAS[(r.grupo, r.faixa_pvp, r.acima_mm200, r.selic_regime)]["lab"] for r in BIG.itertuples()]
cols_show = ["lab", "n_treino", "excesso_medio_treino", "excesso_mediano_treino", "pct_positivo_treino",
             "n_teste", "excesso_medio_teste", "excesso_mediano_teste", "pct_positivo_teste"]
cols_pct = ["excesso_medio_treino", "excesso_mediano_treino", "pct_positivo_treino",
            "excesso_medio_teste", "excesso_mediano_teste", "pct_positivo_teste"]
print("\nTABELA A1 - 20 celulas de MAIOR excesso medio no treino (n_treino >= 20)")
show(BIG.sort_values("excesso_medio_treino", ascending=False).head(20)[cols_show], pcts=cols_pct, nums=[])
print("\nTABELA A2 - 10 celulas de MENOR excesso medio no treino (n_treino >= 20)")
show(BIG.sort_values("excesso_medio_treino").head(10)[cols_show], pcts=cols_pct, nums=[])
ok_corr = TAB_CEL[(TAB_CEL.n_treino >= 20) & (TAB_CEL.n_teste >= 15)]
rho = ok_corr["excesso_medio_treino"].rank().corr(ok_corr["excesso_medio_teste"].rank())  # Spearman = Pearson dos postos (sem scipy)
print(f"\nCorrelacao de Spearman (treino x teste, celulas n_tr>=20 e n_te>=15; {len(ok_corr)} celulas): {nu(rho, 3)}")


def tabela_dim(base, col, titulo):
    print(f"\n{titulo}")
    rows = []
    vals = CAND.loc[base, col].astype(str)
    for v in sorted(vals.unique()):
        m = base & (CAND[col].astype(str).to_numpy() == v)
        tr, te = stats_mask(m)
        rows.append({col: v, "n_treino": tr["n"], "exc_medio_treino": tr["media"], "pct_pos_treino": tr["pos"],
                     "n_teste": te["n"], "exc_medio_teste": te["media"], "pct_pos_teste": te["pos"]})
    show(pd.DataFrame(rows), pcts=["exc_medio_treino", "pct_pos_treino", "exc_medio_teste", "pct_pos_teste"])


def bucket_dist(x):
    if x is None or not np.isfinite(x):
        return "sem dado"
    if x < -0.30:
        return "< -30%"
    if x <= -0.15:
        return "-30% a -15%"
    return "> -15%"


def bucket_ordem(x):
    if x < 2000:
        return "500–2.000"
    if x < 4000:
        return "2.000–4.000"
    return "4.000+"


CAND["dist_faixa"] = CAND["dist_max"].map(bucket_dist)
CAND["ordem_faixa"] = CAND["ordem"].map(bucket_ordem)
CAND["passa_txt"] = np.where(CAND["passa_regua"], "sim", "não")
base_bons = mascara("BONS", "todas", "tanto faz", "tanto faz")
print(f"\nTabelas de uma dimensao - grupo BONS, outros filtros 'tanto faz' (n BONS = {int(base_bons.sum())})")
tabela_dim(base_bons, "tipo_fundo", "por tipo_fundo")
tabela_dim(base_bons, "passa_txt", "por passa_regua")
tabela_dim(base_bons, "dist_faixa", "por dist_max")
tabela_dim(base_bons, "ordem_faixa", "por faixa de ordem_maxima")
tabela_dim(base_bons, "ano", "por ano de entrada")
TAB_CEL.to_csv(TEC / "busca_celulas.csv", **OPC)

# ---------------------------------------------------------------- Passo 4 ETAPA B
print("\n== PASSO 4 - ETAPA B: melhor saida para as 3 melhores entradas ==")
elegiveis = TAB_CEL[(TAB_CEL.n_treino >= 20) & (TAB_CEL.n_teste >= 15)].sort_values(
    "excesso_medio_treino", ascending=False)
print(f"celulas elegiveis (n_tr>=20 e n_te>=15): {len(elegiveis)}")
escolhidas = []
for r in elegiveis.itertuples():
    key = (r.grupo, r.faixa_pvp, r.acima_mm200, r.selic_regime)
    A_ids = set(CAND.loc[CELULAS[key]["mask"], "cid"])
    sobrep = False
    for k2 in escolhidas:
        B_ids = set(CAND.loc[CELULAS[k2]["mask"], "cid"])
        inter = len(A_ids & B_ids)
        if inter / min(len(A_ids), len(B_ids)) > 0.8:
            print(f"  pulando {CELULAS[key]['lab']}: quase igual a {CELULAS[k2]['lab']}")
            sobrep = True
            break
    if not sobrep:
        escolhidas.append(key)
    if len(escolhidas) == 3:
        break
for i, k in enumerate(escolhidas, 1):
    print(f"ESCOLHIDA {i}: {CELULAS[k]['lab']}  (n_tr={CELULAS[k]['tr']['n']}, "
          f"exc_tr={pc(CELULAS[k]['tr']['media'])}, n_te={CELULAS[k]['te']['n']})")


def rodar_um_fundo(cids, params):
    busy = {}
    out = []
    for cid in cids:
        p = PREP[cid]
        if p["f"] in busy and p["D"] < busy[p["f"]]:
            continue
        res = operar(p, *params)
        busy[p["f"]] = pd.Timestamp(res["saida"]).to_datetime64()
        out.append(res)
    return out


def met(df, tr):
    if df.empty:
        return dict(n=0, media=np.nan, mediana=np.nan, pos=np.nan, pregoes=np.nan, abertas=0)
    per = df["entrada"] <= CORTE if tr else df["entrada"] > CORTE
    fech = df[per & (df["motivo"] != ABERTO)]
    ab = int((per & (df["motivo"] == ABERTO)).sum())
    e = estat(fech["excesso"].to_numpy(float))
    e["pregoes"] = float(fech["pregoes"].mean()) if len(fech) else np.nan
    e["abertas"] = ab
    return e


GRADE = {}
for i, key in enumerate(escolhidas, 1):
    sub = CAND.loc[CELULAS[key]["mask"]].sort_values(["entrada", "cid"])["cid"].tolist()
    lista = []
    for params in itertools.product(ALVOS, LIMITES, PRAZOS, SAIRS):
        ops = rodar_um_fundo(sub, params)
        df = pd.DataFrame(ops)
        mt, mte = met(df, True), met(df, False)
        lista.append(dict(params=params, df=df, tr=mt, te=mte))
    GRADE[key] = lista

    rows = []
    for L_ in lista:
        a, l, pz, sa = L_["params"]
        rows.append(dict(celula=CELULAS[key]["lab"], alvo=a, limite=l, prazo=pz, sair_no_corte=sa,
                         n_treino=L_["tr"]["n"], exc_medio_treino=L_["tr"]["media"],
                         exc_mediano_treino=L_["tr"]["mediana"], pct_pos_treino=L_["tr"]["pos"],
                         pregoes_treino=L_["tr"]["pregoes"], em_aberto_treino=L_["tr"]["abertas"],
                         n_teste=L_["te"]["n"], exc_medio_teste=L_["te"]["media"],
                         exc_mediano_teste=L_["te"]["mediana"], pct_pos_teste=L_["te"]["pos"],
                         pregoes_teste=L_["te"]["pregoes"], em_aberto_teste=L_["te"]["abertas"]))
    G = pd.DataFrame(rows)
    G.to_csv(TEC / "busca_saidas.csv" if i == 1 else TEC / f"busca_saidas_{i}.csv", **OPC)
    print(f"\n--- Celula {i}: {CELULAS[key]['lab']}")
    print(f"combinacoes com excesso medio > 0: treino {int((G.exc_medio_treino > 0).sum())} de 120; "
          f"teste {int((G.exc_medio_teste > 0).sum())} de 120")
    top = G.sort_values("exc_medio_treino", ascending=False).head(5)
    show(top[["alvo", "limite", "prazo", "sair_no_corte", "n_treino", "exc_medio_treino", "pct_pos_treino",
              "n_teste", "exc_medio_teste", "pct_pos_teste"]],
         pcts=["alvo", "limite", "exc_medio_treino", "pct_pos_treino", "exc_medio_teste", "pct_pos_teste"])

# arquivo unico pedido: planilhas/tecnico/busca_saidas.csv (todas as celulas empilhadas)
PILHA = []
for i, key in enumerate(escolhidas, 1):
    PILHA.append(pd.read_csv(TEC / ("busca_saidas.csv" if i == 1 else f"busca_saidas_{i}.csv"),
                             sep=";", decimal=",", encoding="utf-8-sig"))
pd.concat(PILHA, ignore_index=True).to_csv(TEC / "busca_saidas.csv", **OPC)
for i in range(2, len(escolhidas) + 1):
    (TEC / f"busca_saidas_{i}.csv").unlink(missing_ok=True)

# ---------------------------------------------------------------- Passo 5: modelo final
print("\n== PASSO 5 - MODELO FINAL DE CADA CELULA ==")
MODELOS = {}
for i, key in enumerate(escolhidas, 1):
    cand_L = [L_ for L_ in GRADE[key] if np.isfinite(L_["tr"]["media"])]
    best = max(cand_L, key=lambda L_: L_["tr"]["media"])
    MODELOS[i] = dict(key=key, params=best["params"], df=best["df"], tr=best["tr"], te=best["te"])
    a, l, pz, sa = best["params"]
    print(f"\n### MODELO {i}: {CELULAS[key]['lab']}")
    print(f"definicao: alvo={a}, limite={l}, prazo={pz}, sair_no_corte={sa}")
    for tr_flag, nome in [(True, "TREINO"), (False, "TESTE")]:
        df = best["df"]
        if df.empty:
            print(nome, "sem operacoes")
            continue
        per = df["entrada"] <= CORTE if tr_flag else df["entrada"] > CORTE
        d = df[per]
        f_ = d[d["motivo"] != ABERTO]
        ent_n = len(d)
        q = f_
        if len(q) == 0:
            print(nome, "sem operacoes fechadas")
            continue
        print(f"[{nome}] entradas={ent_n} | fechadas={len(q)} | em aberto={ent_n - len(q)} | "
              f"pregoes medios={nu(q.pregoes.mean(), 1)} | % cota em alta={pc((q.valorizacao > 0).mean())} | "
              f"valorizacao media={pc(q.valorizacao.mean())} | rendimento medio={pc(q.rendimento.mean())} | "
              f"liquido medio={pc(q.liquido.mean())} | selic media={pc(q.selic.mean())} | "
              f"excesso medio={pc(q.excesso.mean())} | % ganharam da selic={pc((q.excesso > 0).mean())}")
        anos = q.assign(ano=q.entrada.dt.year).groupby("ano").agg(n=("liquido", "size"),
                                                                 liq=("liquido", "mean"), selic=("selic", "mean"))
        print(f"  por ano de entrada [{nome}]:")
        show(anos.reset_index(), pcts=["liq", "selic"])
        mot = q.groupby("motivo").agg(n=("liquido", "size"), liq=("liquido", "mean")).reset_index()
        print(f"  por motivo de saida [{nome}]:")
        show(mot, pcts=["liq"])
    fechadas = df[df["motivo"] != ABERTO]
    print("5 piores operacoes (todas, fechadas):")
    show(fechadas.nsmallest(5, "liquido")[["fundo", "entrada", "saida", "motivo", "liquido"]].assign(
        entrada=lambda x: x.entrada.dt.strftime("%d/%m/%Y"), saida=lambda x: x.saida.dt.strftime("%d/%m/%Y")),
        pcts=["liquido"])
    print("5 melhores operacoes (todas, fechadas):")
    show(fechadas.nlargest(5, "liquido")[["fundo", "entrada", "saida", "motivo", "liquido"]].assign(
        entrada=lambda x: x.entrada.dt.strftime("%d/%m/%Y"), saida=lambda x: x.saida.dt.strftime("%d/%m/%Y")),
        pcts=["liquido"])
    abertas = df[df["motivo"] == ABERTO]
    print(f"em aberto ({len(abertas)}):")
    if len(abertas):
        show(abertas[["fundo", "entrada", "saida", "pregoes", "valorizacao", "liquido"]].assign(
            entrada=lambda x: x.entrada.dt.strftime("%d/%m/%Y"), saida=lambda x: x.saida.dt.strftime("%d/%m/%Y")),
            pcts=["valorizacao", "liquido"])

# ---------------------------------------------------------------- PLACEBO
print("\n== PLACEBO (sorteio de fundo com mesma faixa_pvp e mesmo acima_mm200 na vespera) ==")
POOL = {}
for f, F in FD.items():
    ok = (F["pvp_p"] >= 0.30) & (F["pvp_p"] <= 3.0) & (F["pat_p"] >= 50e6) & (F["vol_p"] >= 25000) & \
         np.isfinite(F["A"]) & (F["A"] > 0)
    ok[0] = False
    for i in np.flatnonzero(ok):
        key = (int(F["dates"][i].astype("int64")), faixa_de(F["pvp_p"][i]), F["acima"][i])
        POOL.setdefault(key, []).append((f, int(i)))
PREP_PL = {}


def prep_placebo(f, i):
    k = (f, i)
    if k not in PREP_PL:
        PREP_PL[k] = prep(f, i, FD[f]["A"][i], -1)
    return PREP_PL[k]


def placebo(modelo, seed):
    rng = np.random.default_rng(seed)
    df = modelo["df"]
    alvo, limite, prazo, sair = modelo["params"]
    reais = df[df["motivo"] != ABERTO]
    out = []
    sem = 0
    for o in reais.itertuples():
        p_real = PREP[o.cid]
        key = (int(np.datetime64(o.entrada.date(), "D").astype("int64")), p_real["faixa"], p_real["acima"])
        pool = [x for x in POOL.get(key, []) if x[0] != o.fundo]
        if not pool:
            sem += 1
            continue
        f, i = pool[int(rng.integers(len(pool)))]
        res = operar(prep_placebo(f, i), alvo, limite, prazo, sair)
        out.append(dict(entrada=o.entrada, excesso=res["excesso"]))
    d = pd.DataFrame(out)
    tr = d[d["entrada"] <= CORTE]["excesso"].mean() if len(d) else np.nan
    te = d[d["entrada"] > CORTE]["excesso"].mean() if len(d) else np.nan
    return tr, te, sem


PLACEBO_RES = {}
for i, mdl in MODELOS.items():
    trs, tes, sems = [], [], []
    for seed in range(1, 21):
        tr, te, sem = placebo(mdl, seed)
        trs.append(tr)
        tes.append(te)
        sems.append(sem)
    rt = mdl["tr"]["media"]
    rte = mdl["te"]["media"]
    PLACEBO_RES[i] = dict(tr=float(np.nanmean(trs)), te=float(np.nanmean(tes)))
    print(f"MODELO {i}: excesso medio REAL treino={pc(rt)} teste={pc(rte)} | "
          f"PLACEBO (media de 20 sorteios) treino={pc(np.nanmean(trs))} teste={pc(np.nanmean(tes))} | "
          f"sem sorteio possivel por seed (media)={nu(np.mean(sems), 1)}")

# operacoes dos 3 modelos
OPS_OUT = []
for i, mdl in MODELOS.items():
    d = mdl["df"].copy()
    d["modelo"] = i
    d["periodo"] = np.where(d["entrada"] <= CORTE, "treino", "teste")
    d["grupo"] = [PREP[c]["grupo"] for c in d["cid"]]
    d["faixa"] = [PREP[c]["faixa"] for c in d["cid"]]
    d["acima"] = [PREP[c]["acima"] for c in d["cid"]]
    d["regime"] = [PREP[c]["regime"] for c in d["cid"]]
    OPS_OUT.append(d)
OPS_DF = pd.concat(OPS_OUT, ignore_index=True)
OPS_DF.to_csv(TEC / "busca_operacoes.csv", **OPC)
print(f"\noperacoes gravadas em planilhas/tecnico/busca_operacoes.csv: {len(OPS_DF)}")

# ---------------------------------------------------------------- CONFERENCIAS
print("\n== CONFERENCIAS ==")
print("2) Recalculo a mao de 3 operacoes do modelo 1 (caminho independente, lendo as planilhas por fundo):")
MK_IDX = MK.set_index("data")
m1 = MODELOS[1]
alvo1, lim1, pz1, sa1 = m1["params"]
fech1 = m1["df"][m1["df"]["motivo"] != ABERTO].reset_index(drop=True)
amostra = [0, len(fech1) // 2, len(fech1) - 1]
for idx in amostra:
    o = fech1.iloc[idx]
    g = PR[PR["fundo"] == o.fundo].reset_index(drop=True)
    i0 = int(g.index[g["data"] == o.entrada][0])
    ent = float(o.ent)
    cm = -np.inf
    mot = px = saida = None
    lin_saida = None
    for d in range(0, 253):
        j = i0 + d
        if j >= len(g):
            break
        row = g.loc[j]
        rend = row[C_REND]
        if np.isfinite(rend):
            cm = max(cm, rend)
        if sa1 and d > 0 and rend <= 0.9 * cm:
            mot, px, saida = "rendimento caiu", row[C_AB], j
            break
        if lim1 is not None and row[C_MN] <= ent * (1 + lim1):
            mot, px, saida = "limite de perda", min(row[C_AB], ent * (1 + lim1)), j
            break
        if alvo1 is not None and row[C_MX] >= ent * (1 + alvo1):
            mot, px, saida = "alvo", max(row[C_AB], ent * (1 + alvo1)), j
            break
        if d == pz1:
            mot, px, saida = "prazo", row[C_FE], j
            break
        if j == len(g) - 1:
            ult = np.searchsorted(MD, np.datetime64(g.loc[j, "data"].date(), "D"), "left")
            mot, px, saida = (ABERTO if ult >= NM - 21 else SAIU), row[C_FE], j
            break
    S_ = g.loc[saida, "data"]
    print(f"\nOperacao {idx}: {o.fundo} entrada {o.entrada.date()} (preco_entrada={ent:.4f}) | "
          f"saida {S_.date()} motivo={mot}")
    print(f"  linha da saida: abertura={g.loc[saida, C_AB]:.4f} maxima={g.loc[saida, C_MX]:.4f} "
          f"minima={g.loc[saida, C_MN]:.4f} fechamento={g.loc[saida, C_FE]:.4f} -> preco usado={px:.4f}")
    val = px / ent - 1
    incl = mot in ("prazo", ABERTO)
    mask_r = RD[(RD["fundo"] == o.fundo) & (RD["data_base"] >= o.entrada) &
                (RD["data_base"] <= S_ if incl else RD["data_base"] < S_)]
    print(f"  avisos de rendimento somados (data_base {'<=' if incl else '<'} saida):")
    for _, rr in mask_r.iterrows():
        print(f"    data_base={rr['data_base'].date()} valor={rr['valor (R$/cota)']:.4f}")
    rend_m = mask_r["valor (R$/cota)"].sum() / ent
    liq_m = val - B3 - 0.20 * max(val - B3, 0) + rend_m
    mk = MK[(MK["data"] >= o.entrada) & (MK["data"] < S_)]
    prod = 1.0
    for s in mk["selic_ano (%)"]:
        prod *= (1 + s / 100) ** (1 / 252)
    dias = (S_ - o.entrada).days
    imp = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
    selic_m = (prod - 1) * (1 - imp)
    print(f"  valorizacao={val:.6f} (saida/entrada-1 = {px:.4f}/{ent:.4f}-1)")
    print(f"  rendimento={rend_m:.6f} | liquido={liq_m:.6f}")
    print(f"  selic: {len(mk)} pregoes, produto={prod:.6f}, dias corridos={dias}, imposto={imp}, selic liquida={selic_m:.6f}")
    print(f"  excesso manual={liq_m - selic_m:.6f} | excesso do script={o.excesso:.6f} | "
          f"diferenca={abs((liq_m - selic_m) - o.excesso):.2e}")

print("\n4) Celulas com n_treino >= 20 e |excesso medio| > 15% (ETAPA A) - 5 operacoes mais extremas:")
flag = TAB_CEL[(TAB_CEL.n_treino >= 20) & (TAB_CEL.excesso_medio_treino.abs() > 0.15)]
if flag.empty:
    print("  nenhuma")
for r in flag.itertuples():
    m = CELULAS[(r.grupo, r.faixa_pvp, r.acima_mm200, r.selic_regime)]["mask"] & FEC
    sub = CAND.loc[m, ["fundo", "entrada", "motivo_A"]].assign(ex=EX[m])
    print(f"\n  {CELULAS[(r.grupo, r.faixa_pvp, r.acima_mm200, r.selic_regime)]['lab']} "
          f"(n_tr={r.n_treino}, media treino={pc(r.excesso_medio_treino)})")
    ext = pd.concat([sub.nlargest(5, "ex"), sub.nsmallest(5, "ex")])
    show(ext.assign(entrada=ext.entrada.dt.strftime("%d/%m/%Y")), pcts=["ex"])

print(f"\n1) Roda sem erro. Tempo total: {time.time() - T0:.1f} s")
