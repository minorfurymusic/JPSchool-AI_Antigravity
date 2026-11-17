"""Auditoria do estudo do Kairi - BLOCO 1: indicadores, taxa interna de retorno e significancia.

Le SO as planilhas de planilhas/ (kairi_ordens.csv, kairi_ordens_saidas.csv, cdi.csv, mercado.csv,
rendimentos_pagamentos.csv, rendimentos.csv, precos_*.csv). Nao altera nada existente.

Regua: 105% do CDI em aplicacao de liquidez diaria, com IR regressivo e IOF (decisao do dono).
Carteiras A, B e C (ordens ja prontas em kairi_ordens.csv). Periodos: escolha (entradas 2018-2022),
conferencia (entradas 2023-2026) e total.

Itens:
  1) indicadores por ordem (resultado antes do imposto e excesso sobre 105% do CDI, antes do imposto),
     correlacao entre fundos que dao sinal juntos, episodios independentes (janelas de 10, 20 e 40 pregoes);
  2) TIR (XIRR): (a) fluxos reais das ordens, (b) espelho em 105% do CDI, (c) carteira do pico com saldo
     parado em 105% do CDI (lotes, FIFO, IR e IOF por lote), (d) Sharpe, Sortino e Calmar;
  3) significancia do excesso: por ordem (ingenuo), por episodio, Newey-West no excesso mensal da carteira
     do pico (defasagens 3, 6 e 12) e bootstrap em blocos de 6 meses.

Rodar com:
    cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/auditoria_bloco1.py [caminho_tabelas.md]
O argumento opcional e o arquivo onde gravar as tabelas em markdown (alem de imprimir).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq

np.seterr(all="ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 80)

T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
PL = RAIZ / "planilhas"
OPC = dict(sep=";", decimal=",", encoding="utf-8-sig", index=False, date_format="%d/%m/%Y")
MD_SAIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else None

B3 = 0.0003
CORTE_ESC = 2022          # escolha: entradas ate 2022; conferencia: 2023 em diante
FIM = pd.Timestamp("2026-11-09")        # ultimo preco da base: avaliacao das ordens em aberto e do fim das carteiras
INI = pd.Timestamp("2018-01-02")
PICO = {"A": 262698.0, "B": 151506.0, "C": 255116.0}
CARTS = ["A", "B", "C"]
PERIODOS = ["escolha", "conferência", "total"]
PER_ROT = {"escolha": "Escolha (entradas 2018-2022)", "conferência": "Conferência (entradas 2023-2026)",
           "total": "Total"}
SEMENTE = 20261117
IOF_TAB = np.array([100, 96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26,
                    23, 20, 16, 13, 10, 6, 3, 0], float) / 100.0   # indice = dias corridos (0 nao usado: sem rendimento)
IOF_TAB[0] = 0.0
MD_BUF = []


# ---------------------------------------------------------------- formatacao
def isnan(x):
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


def br(x, d=2):
    if isnan(x):
        return "n/d"
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(x, d=0):
    return "n/d" if isnan(x) else "R$ " + br(x, d)


def pc(x, d=1):
    """x em fracao -> texto em %."""
    return "n/d" if isnan(x) else br(100 * x, d) + "%"


def emit(txt=""):
    print(txt)
    MD_BUF.append(txt)


def md_tabela(cols, linhas):
    emit("| " + " | ".join(cols) + " |")
    emit("|" + "|".join(["---"] * len(cols)) + "|")
    for l in linhas:
        emit("| " + " | ".join(str(c) for c in l) + " |")
    emit()


def secao(t):
    emit(f"\n### {t}\n")


# ---------------------------------------------------------------- carga
def le(nome):
    return pd.read_csv(PL / f"{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig")


def dt(s):
    return pd.to_datetime(s, format="%d/%m/%Y")


ORD = le("kairi_ordens")
SAI = le("kairi_ordens_saidas")
ORD = ORD.rename(columns={
    "Carteira": "cart", "Fundo": "fundo", "Data do sinal": "sinal", "Data de entrada": "entrada",
    "Preço de entrada (R$)": "px_e", "Cotas": "cotas", "Valor da ordem (R$)": "valor", "Situação": "situacao",
    "Data de saída (ou do último preço)": "saida", "Preço de saída (ou atual) (R$)": "px_s",
    "Motivo da saída": "motivo", "Valorização (R$)": "valoriz", "Rendimentos recebidos (R$)": "rend_csv",
    "Taxas (R$)": "taxas_csv", "Imposto (R$)": "imposto_csv", "Resultado (R$)": "res_csv"})
for c in ["sinal", "entrada", "saida"]:
    ORD[c] = dt(ORD[c])
ORD["fechada"] = ORD["situacao"] == "Fechada"
ORD["periodo"] = np.where(ORD["entrada"].dt.year <= CORTE_ESC, "escolha", "conferência")
ORD["incl"] = ORD["motivo"].isin(["prazo", "em aberto"])       # regra de direito: avisos com data_base <= saida
ORD = ORD.sort_values(["cart", "entrada", "fundo"]).reset_index(drop=True)
ORD["id"] = np.arange(len(ORD))
assert ORD.groupby("cart").size().to_dict() == {"A": 341, "B": 175, "C": 292}
assert (ORD.loc[~ORD["fechada"], "saida"] <= FIM).all()
N_ABERTA_ANTES = int((ORD.loc[~ORD["fechada"], "saida"] < FIM).sum())   # fundo cujo ultimo preco e anterior a 09/11/2026

SAI = SAI[SAI["Regra de saída"] == "Volta à média (prazo de 252 pregões)"].copy()
SAI["entrada"] = dt(SAI["Data de entrada"])
SAI = SAI.rename(columns={"Carteira": "cart", "Fundo": "fundo", "Resultado antes do imposto (R$)": "res_pre_saidas"})

CD = le("cdi")
CD["data"] = dt(CD["data"])
CD = CD.sort_values("data").reset_index(drop=True)
CDD = CD["data"].to_numpy("datetime64[D]")
I105 = CD["indice_105_do_cdi"].to_numpy(float)
assert (np.diff(CDD).astype(int) > 0).all()

MK = le("mercado")
MK["data"] = dt(MK["data"])
MKD = MK["data"].to_numpy("datetime64[D]")

PG = le("rendimentos_pagamentos")
for c in ["data_conhecido", "data_base", "data_pagamento"]:
    PG[c] = dt(PG[c])
PG = PG.dropna(subset=["data_base"]).sort_values(["fundo", "data_base"]).reset_index(drop=True)
MEDIANA_DIAS = int(np.median((PG["data_pagamento"] - PG["data_base"]).dt.days.dropna()))
PG["sem_pag"] = PG["data_pagamento"].isna()
PG["pag"] = PG["data_pagamento"].fillna(PG["data_base"] + pd.Timedelta(days=MEDIANA_DIAS))
PGF = {f: g.reset_index(drop=True) for f, g in PG.groupby("fundo")}

PR = pd.concat([pd.read_csv(a, sep=";", decimal=",", encoding="utf-8-sig",
                            usecols=["data", "fundo", "abertura", "fechamento", "volume_medio_60 (R$)",
                                     "patrimonio (R$)"])
                for a in sorted(PL.glob("precos_*.csv"))], ignore_index=True)
PR["data"] = dt(PR["data"])
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
PRF = {f: (g["data"].to_numpy("datetime64[D]"), g["fechamento"].to_numpy(float), g["abertura"].to_numpy(float))
       for f, g in PR.groupby("fundo")}

print(f"ordens: {len(ORD)}; fechadas {int(ORD.fechada.sum())}; em aberto {int((~ORD.fechada).sum())}")
print(f"cdi.csv: {CDD[0]} a {CDD[-1]} ({len(CDD)} dias); mercado.csv: {MKD[0]} a {MKD[-1]} ({len(MKD)} pregoes)")
print(f"data final usada nas carteiras e nas ordens em aberto: {FIM:%d/%m/%Y} (ultimo preco da base; o cdi.csv vai ate "
      f"{pd.Timestamp(CDD[-1]):%d/%m/%Y}, mas nao usado)")
print(f"mediana de dias entre data-base e pagamento (rendimentos com data): {MEDIANA_DIAS}")


# ---------------------------------------------------------------- CDI, IR e IOF
def ix_cdi(d):
    """Indice do ultimo dia do cdi.csv <= d (fim de semana usa o dia util anterior)."""
    return int(np.searchsorted(CDD, np.datetime64(pd.Timestamp(d), "D"), "right")) - 1


def ix_cdi_prox(d):
    """Primeiro dia do cdi.csv >= d."""
    return int(np.searchsorted(CDD, np.datetime64(pd.Timestamp(d), "D"), "left"))


def ind(d):
    return I105[ix_cdi(d)]


def aliq_ir(dias):
    dias = np.asarray(dias)
    return np.where(dias <= 180, 0.225, np.where(dias <= 360, 0.20, np.where(dias <= 720, 0.175, 0.15)))


def iof_taxa(dias):
    dias = np.asarray(dias)
    return np.where(dias >= 30, 0.0, IOF_TAB[np.clip(dias, 0, 30)])


def fator_liquido(y, dias):
    """Fracao do valor bruto que sobra depois de IOF e IR, dado y = parte do valor que e rendimento."""
    iof = iof_taxa(dias)
    return 1 - y * (iof + aliq_ir(dias) * (1 - iof))


def cdi_liquido(V, d0, d1):
    """Aplicacao de V em d0 resgatada em d1 a 105% do CDI: devolve (liquido, imposto total, bruto)."""
    d0, d1 = pd.Timestamp(d0), pd.Timestamp(d1)
    g = V * (ind(d1) / ind(d0) - 1)
    dias = (d1 - d0).days
    iof = float(iof_taxa(dias))
    ir = float(aliq_ir(dias)) * g * (1 - iof)
    return V + g - g * iof - ir, g * iof + ir, g


def xirr(cfs):
    """cfs: lista de (data, valor). Taxa anual (base 365) que zera o valor presente."""
    if not cfs:
        return np.nan
    t0 = min(d for d, _ in cfs)
    t = np.array([(d - t0).days / 365.0 for d, _ in cfs])
    a = np.array([v for _, v in cfs], float)
    f = lambda r: float(np.sum(a * (1 + r) ** (-t)))
    lo, hi = -0.9999, 1e4
    try:
        return brentq(f, lo, hi, xtol=1e-12, maxiter=500)
    except ValueError:
        return np.nan


def ultimo_dia_util_mes(ano, mes):
    """Ultimo dia util do mes: do cdi.csv se o mes esta completo na base; senao ultimo dia de semana."""
    ini = pd.Timestamp(ano, mes, 1)
    fim = ini + pd.offsets.MonthEnd(0)
    if fim <= pd.Timestamp(CDD[-1]):
        j = ix_cdi(fim)
        return pd.Timestamp(CDD[j])
    d = fim
    while d.dayofweek >= 5:
        d -= pd.Timedelta(days=1)
    return d


# ---------------------------------------------------------------- por ordem: direitos de rendimento, fluxos, excesso
def direitos(f, D, S, incl):
    """Mesma regra de rend_val (kairi_ordens.py): data_base >= entrada e < saida (<= saida se prazo/aberto)."""
    if f not in PGF:
        return PG.iloc[0:0]
    g = PGF[f]
    m = (g["data_base"] >= D) & ((g["data_base"] <= S) if incl else (g["data_base"] < S))
    return g[m]


rows = []
for r in ORD.itertuples():
    d = direitos(r.fundo, r.entrada, r.saida, r.incl)
    val_cota = float(d["valor (R$/cota)"].sum())
    rend = val_cota * r.cotas
    taxa_c = B3 * r.valor
    venda = r.valor + r.valoriz
    taxa_v = B3 * venda
    taxas = taxa_c + taxa_v
    res_pre = r.valoriz + rend - taxas
    g = ind(r.saida) / ind(r.entrada) - 1
    rows.append(dict(id=r.id, rend=rend, n_dir=len(d), taxa_c=taxa_c, venda=venda, taxa_v=taxa_v, taxas=taxas,
                     res_pre=res_pre, res_pre_pct=res_pre / r.valor, cdi_bruto_pct=g,
                     exc_pct=res_pre / r.valor - g, exc_rs=res_pre - r.valor * g))
O = ORD.merge(pd.DataFrame(rows), on="id")
DIR = []   # direitos por ordem (para os fluxos)
for r in O.itertuples():
    d = direitos(r.fundo, r.entrada, r.saida, r.incl)
    for base, pag, sp, v in zip(d["data_base"], d["pag"], d["sem_pag"], d["valor (R$/cota)"]):
        DIR.append(dict(id=r.id, cart=r.cart, fundo=r.fundo, base=base, pag=pag, sem_pag=bool(sp), valor=v * r.cotas))
DIR = pd.DataFrame(DIR)
assert abs(DIR.groupby("id")["valor"].sum().reindex(O["id"]).fillna(0).to_numpy() - O["rend"].to_numpy()).max() < 1e-6

# conferencia da soma dos rendimentos com a planilha
O["dif_rend"] = O["rend"] - O["rend_csv"]
O["dif_res_saidas"] = np.nan
mm = O.merge(SAI[["cart", "fundo", "entrada", "res_pre_saidas"]], on=["cart", "fundo", "entrada"], how="left")
O["res_pre_saidas"] = mm["res_pre_saidas"].to_numpy()
O["dif_res_saidas"] = O["res_pre"] - O["res_pre_saidas"]
O["ano_e"] = O["entrada"].dt.year


def sub(carteira, periodo, so_fechadas=False):
    d = O[O["cart"] == carteira]
    if periodo != "total":
        d = d[d["periodo"] == periodo]
    if so_fechadas:
        d = d[d["fechada"]]
    return d


# ================================================================= CONFERENCIAS DE ENTRADA
print("\n==== CONFERENCIAS DOS DADOS DE ENTRADA ====")
print(f"direitos de rendimento reproduzidos pela regra de rend_val: {len(DIR)} avisos em {DIR['id'].nunique()} ordens")
print(f"soma dos rendimentos por ordem (pagamentos) menos a coluna 'Rendimentos recebidos (R$)': "
      f"maior diferenca absoluta {O['dif_rend'].abs().max():.4f}; ordens com diferenca > R$ 0,01: "
      f"{int((O['dif_rend'].abs() > 0.011).sum())}")
print("soma dos rendimentos (R$): " + "; ".join(
    f"{c}: calculado {br(O[O.cart == c]['rend'].sum())} / planilha {br(O[O.cart == c]['rend_csv'].sum())}"
    for c in CARTS))
print(f"resultado antes do imposto (valorizacao + rendimentos - taxas) contra 'kairi_ordens_saidas.csv' (regra 252): "
      f"maior diferenca absoluta {O['dif_res_saidas'].abs().max():.4f}; ordens A e B sem par: {int(O[O.cart != 'C']['res_pre_saidas'].isna().sum())} (a carteira C nao esta em kairi_ordens_saidas.csv)")
chk_taxas = (O["taxas"] - O["taxas_csv"]).abs().max()
print(f"taxas recalculadas (0,03% na compra e na venda) contra a planilha: maior diferenca {chk_taxas:.4f}")
# entrada: preco de abertura no dia da entrada x planilha
dx = []
for r in O.itertuples():
    dts, cl, ab = PRF[r.fundo]
    k = np.searchsorted(dts, np.datetime64(r.entrada, "D"))
    dx.append(r.cotas * ab[k] - r.valor)
dx = np.array(dx)
print(f"cotas x abertura do dia da entrada (precos_*.csv) menos 'Valor da ordem': maior diferenca absoluta "
      f"{np.abs(dx).max():.4f}")
sp = DIR[DIR["sem_pag"]]
pos_fim = DIR[DIR["pag"] > FIM]
print(f"direitos sem data de pagamento (usada data-base + {MEDIANA_DIAS} dias): {len(sp)} avisos, "
      f"R$ {br(sp['valor'].sum())}")
print(f"direitos com pagamento depois de {FIM:%d/%m/%Y}: {len(pos_fim)} avisos, R$ {br(pos_fim['valor'].sum())}")
print(f"direitos pagos em fim de semana (mantida a data do pagamento): {int((DIR['pag'].dt.dayofweek >= 5).sum())}")


# ================================================================= ITEM 1: INDICADORES POR ORDEM
def indicadores(x, rs):
    """x: medida por ordem em % (array); rs: mesma medida em R$ (array)."""
    x = np.asarray(x, float)
    rs = np.asarray(rs, float)
    n = len(x)
    out = {"n": n}
    if n == 0:
        return out
    out["média (%)"] = x.mean()
    out["mediana (%)"] = np.median(x)
    for q in [5, 10, 25, 75, 90, 95]:
        out[f"quantil {q}% (%)"] = np.percentile(x, q)
    out["assimetria"] = stats.skew(x, bias=False) if n > 2 else np.nan
    out["curtose (excesso)"] = stats.kurtosis(x, fisher=True, bias=False) if n > 3 else np.nan
    out["desvio padrão (pp)"] = x.std(ddof=1) if n > 1 else np.nan
    out["semidesvio das perdas (pp)"] = np.sqrt(np.mean(np.minimum(x, 0.0) ** 2))
    perd = -rs[rs < 0].sum()
    out["ganhos ÷ perdas (R$)"] = rs[rs > 0].sum() / perd if perd > 0 else np.nan
    out["ordens positivas (%)"] = 100 * np.mean(x > 0)
    return out


IND_ORDEM = ["n", "média (%)", "mediana (%)", "quantil 5% (%)", "quantil 10% (%)", "quantil 25% (%)",
             "quantil 75% (%)", "quantil 90% (%)", "quantil 95% (%)", "assimetria", "curtose (excesso)",
             "desvio padrão (pp)", "semidesvio das perdas (pp)", "ganhos ÷ perdas (R$)", "ordens positivas (%)"]
MEDIDAS = {"res": ("Resultado antes do imposto", "res_pre_pct", "res_pre"),
           "exc": ("Excesso sobre 105% do CDI (antes do imposto)", "exc_pct", "exc_rs")}
LINHAS_IND = []
IND_RES = {}
for c in CARTS:
    for med, (rot, col, colr) in MEDIDAS.items():
        for p in PERIODOS:
            d = sub(c, p, True)
            o = indicadores(100 * d[col].to_numpy(), d[colr].to_numpy())
            IND_RES[(c, med, p)] = o
            for k_, v in o.items():
                LINHAS_IND.append(dict(carteira=c, medida=rot, periodo=PER_ROT[p], indicador=k_, valor=v))
pd.DataFrame(LINHAS_IND).to_csv(PL / "auditoria_bloco1_indicadores.csv", **OPC, float_format="%.6f")

emit("## Item 1 - Indicadores")
for c in CARTS:
    for med, (rot, col, colr) in MEDIDAS.items():
        secao(f"Carteira {c} - {rot} (ordens fechadas)")
        linhas = []
        for k_ in IND_ORDEM:
            lin = [k_]
            for p in PERIODOS:
                v = IND_RES[(c, med, p)].get(k_, np.nan)
                lin.append(str(int(v)) if k_ == "n" else br(v, 2))
            linhas.append(lin)
        md_tabela(["Indicador"] + [PER_ROT[p] for p in PERIODOS], linhas)

# ---- correlacao entre fundos que dao sinal juntos
print("\n== correlacao entre fundos com sinal juntos ==")
PRP = PR[PR["data"] >= pd.Timestamp("2017-01-02")]
CL = PRP.pivot(index="data", columns="fundo", values="fechamento").reindex(MK["data"])
VOLW = PRP.pivot(index="data", columns="fundo", values="volume_medio_60 (R$)").reindex(MK["data"])
PATW = PRP.pivot(index="data", columns="fundo", values="patrimonio (R$)").reindex(MK["data"])
RET = (CL / CL.shift(1) - 1).to_numpy().copy()
RET[(RET > 0.60) | (RET < -0.45)] = np.nan          # mesma guarda de dado suspeito do estudo
FUNDOS = list(CL.columns)
FCOL = {f: i for i, f in enumerate(FUNDOS)}
VALID = np.isfinite(RET)
UNIV = np.isfinite(RET) & (VOLW.to_numpy() >= 25000) & (PATW.to_numpy() >= 50e6)
CS_UNIV = np.vstack([np.zeros((1, UNIV.shape[1])), np.cumsum(UNIV, axis=0)])
RNG = np.random.default_rng(SEMENTE)
MIN_OBS = 20


def pos_pregao(d):
    return int(np.searchsorted(MKD, np.datetime64(pd.Timestamp(d), "D"), "left"))


def corr_par(i, j, a, b):
    x, y = RET[a:b + 1, i], RET[a:b + 1, j]
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < MIN_OBS:
        return np.nan
    x, y = x[m], y[m]
    if x.std() == 0 or y.std() == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def grupos_de(d, modo):
    """Devolve lista de listas de indices de linhas de d. modo 0: mesma data de sinal; 5: janela de 5 pregoes
    a partir do primeiro sinal do grupo (janela ancorada, sem encadear)."""
    d = d.sort_values(["sinal", "fundo"])
    if modo == 0:
        return [g.index.tolist() for _, g in d.groupby("sinal")]
    pos = d["sinal"].map(pos_pregao)
    out, atual, ini = [], [], None
    for idx, p in zip(d.index, pos):
        if ini is None or p - ini > 5:
            if atual:
                out.append(atual)
            atual, ini = [idx], p
        else:
            atual.append(idx)
    if atual:
        out.append(atual)
    return out


GR_ROWS = []
N_BASE = 5          # pares sorteados por par real


def correlacao_grupo(d, idxs):
    g = d.loc[idxs].drop_duplicates("fundo")
    if len(g) < 2:
        return None
    ents = [pos_pregao(x) for x in g["entrada"]]
    sais = [pos_pregao(x) for x in g["saida"]]
    cols = [FCOL.get(f, None) for f in g["fundo"]]
    reais, base = [], []
    excl = set(c_ for c_ in cols if c_ is not None)
    npar = 0
    for a_ in range(len(g)):
        for b_ in range(a_ + 1, len(g)):
            if cols[a_] is None or cols[b_] is None:
                continue
            ini = max(ents[a_], ents[b_]) + 1
            fim = min(sais[a_], sais[b_])
            if fim - ini + 1 < MIN_OBS:
                continue
            cr = corr_par(cols[a_], cols[b_], ini, fim)
            if np.isnan(cr):
                continue
            reais.append(cr)
            L = fim - ini + 1
            elig = np.flatnonzero((CS_UNIV[fim + 1] - CS_UNIV[ini]) >= 0.9 * L)
            elig = np.array([e for e in elig if e not in excl])
            vals = []
            if len(elig) >= 2:
                for _ in range(N_BASE):
                    i, j = RNG.choice(elig, 2, replace=False)
                    cr2 = corr_par(int(i), int(j), ini, fim)
                    if not np.isnan(cr2):
                        vals.append(cr2)
            if vals:
                base.append(np.mean(vals))
    if not reais:
        return None
    return dict(n_ordens=len(g), n_pares=len(reais), corr_media=float(np.mean(reais)),
                corr_sorteio=float(np.mean(base)) if base else np.nan,
                inicio=g["entrada"].min(), sinal=g["sinal"].min())


CORR_RES = {}
for c in CARTS:
    for p in PERIODOS:
        d = sub(c, p)
        for modo in [0, 5]:
            lst = []
            gs = grupos_de(d, modo)
            n_g2 = 0
            for idxs in gs:
                if d.loc[idxs, "fundo"].nunique() >= 2:
                    n_g2 += 1
                    r_ = correlacao_grupo(d, idxs)
                    if r_:
                        r_.update(carteira=c, periodo=PER_ROT[p], agrupamento="mesma data de sinal" if modo == 0
                                  else "sinais em até 5 pregões")
                        lst.append(r_)
                        GR_ROWS.append(r_)
            CORR_RES[(c, p, modo)] = (len(gs), n_g2, pd.DataFrame(lst))
GRP = pd.DataFrame(GR_ROWS)
GRP.rename(columns={"n_ordens": "fundos no grupo", "n_pares": "pares com 20+ dias juntos",
                    "corr_media": "correlação média dos pares", "corr_sorteio": "correlação média de pares sorteados",
                    "inicio": "primeira entrada", "sinal": "primeiro sinal"}).to_csv(
    PL / "auditoria_bloco1_correlacao_grupos.csv", **OPC, float_format="%.6f")

secao("Correlação entre fundos que dão sinal juntos")
linhas = []
for c in CARTS:
    for p in PERIODOS:
        for modo, rot in [(0, "mesma data de sinal"), (5, "sinais em até 5 pregões")]:
            ng, ng2, df = CORR_RES[(c, p, modo)]
            if len(df) == 0:
                linhas.append([c, PER_ROT[p], rot, ng, ng2, 0] + ["n/d"] * 8)
                continue
            q = lambda s, v: br(np.percentile(s.dropna(), v), 2)
            linhas.append([c, PER_ROT[p], rot, ng, ng2, len(df),
                           br(df["corr_media"].median(), 2), q(df["corr_media"], 5), q(df["corr_media"], 25),
                           q(df["corr_media"], 75), q(df["corr_media"], 95),
                           br(df["corr_sorteio"].median(), 2), q(df["corr_sorteio"], 25), q(df["corr_sorteio"], 75)])
md_tabela(["Carteira", "Período", "Agrupamento", "Grupos", "Grupos com 2+ fundos", "Grupos com correlação calculada",
           "Mediana (com sinal)", "q5%", "q25%", "q75%", "q95%", "Mediana (pares sorteados)", "q25% sorteio",
           "q75% sorteio"], linhas)


# ---- episodios independentes
def episodios(d, W):
    """Ordens ordenadas pela entrada; novo episodio quando a entrada esta a mais de W pregoes da entrada anterior."""
    d = d.sort_values(["entrada", "fundo"])
    pos = d["entrada"].map(pos_pregao).to_numpy()
    ep = np.zeros(len(d), int)
    for k in range(1, len(d)):
        ep[k] = ep[k - 1] + (1 if pos[k] - pos[k - 1] > W else 0)
    d = d.assign(episodio=ep + 1)
    return d


EP_ROWS, EP_RES = [], {}
for W in [10, 20, 40]:
    for c in CARTS:
        for p in PERIODOS:
            d = episodios(sub(c, p), W)
            for e, g in d.groupby("episodio"):
                gf = g[g["fechada"]]
                EP_ROWS.append(dict(janela_pregoes=W, carteira=c, periodo=PER_ROT[p], episodio=e,
                                    primeira_entrada=g["entrada"].min(), ultima_entrada=g["entrada"].max(),
                                    ordens=len(g), ordens_fechadas=len(gf),
                                    soma_res_antes_imposto_rs=gf["res_pre"].sum() if len(gf) else np.nan,
                                    res_pct_medio=100 * gf["res_pre_pct"].mean() if len(gf) else np.nan,
                                    excesso_pct_medio=100 * gf["exc_pct"].mean() if len(gf) else np.nan,
                                    excesso_rs=gf["exc_rs"].sum() if len(gf) else np.nan))
EPD = pd.DataFrame(EP_ROWS)
EPD.to_csv(PL / "auditoria_bloco1_episodios.csv", **OPC, float_format="%.6f")

secao("Episódios independentes (ordens encadeadas a no máximo W pregões da entrada anterior, dentro da carteira)")
linhas = []
for W in [10, 20, 40]:
    for c in CARTS:
        for p in PERIODOS:
            e = EPD[(EPD.janela_pregoes == W) & (EPD.carteira == c) & (EPD.periodo == PER_ROT[p])]
            n_ord = int(e["ordens"].sum())
            ef = e.dropna(subset=["res_pct_medio"])
            soma = ef["soma_res_antes_imposto_rs"].sum()
            top3 = ef["soma_res_antes_imposto_rs"].sort_values(ascending=False).head(3).sum() / soma if soma > 0 else np.nan
            linhas.append([f"{W}", c, PER_ROT[p], n_ord, len(e), br(n_ord / len(e), 1), int(e["ordens"].max()),
                           len(ef), br(soma), br(ef["res_pct_medio"].mean(), 1) + "%",
                           br(ef["res_pct_medio"].median(), 1) + "%", br(100 * (ef["soma_res_antes_imposto_rs"] > 0).mean(), 0) + "%",
                           br(ef["excesso_pct_medio"].mean(), 1) + " pp", pc(top3, 0)])
md_tabela(["Janela W (pregões)", "Carteira", "Período", "Ordens", "Episódios", "Ordens por episódio (média)",
           "Maior episódio (ordens)", "Episódios com ordem fechada", "Soma do resultado antes do imposto (R$)",
           "% médio por episódio (média)", "% médio por episódio (mediana)", "Episódios com soma > 0",
           "Excesso médio por episódio (pp)", "Parte da soma nos 3 maiores episódios"], linhas)

# ================================================================= ITEM 2: TIR
print("\n==== ITEM 2: TIR ====")


def imposto_mensal(d):
    """d: ordens fechadas. Ganho da venda = valorizacao - taxas; soma por mes da venda; prejuizo abate os meses seguintes;
    20% do ganho liquido positivo; pago no ultimo dia util do mes seguinte. Devolve lista (mes, ganho, imposto, data_pag)."""
    d = d.assign(mes=d["saida"].dt.to_period("M"), ganho=d["valoriz"] - d["taxas"])
    mm = d.groupby("mes")["ganho"].sum().sort_index()
    carry, out = 0.0, []
    for mes, gsum in mm.items():
        tot = gsum + carry
        if tot > 0:
            imp, carry = 0.2 * tot, 0.0
        else:
            imp, carry = 0.0, tot
        prox = mes + 1
        out.append(dict(mes=mes, ganho=float(gsum), imposto=imp, pag=ultimo_dia_util_mes(prox.year, prox.month)))
    return out


def fluxos_ordens(d, com_imposto=True, so_fechadas=False):
    cfs = []
    dd = d[d["fechada"]] if so_fechadas else d
    for r in dd.itertuples():
        cfs.append((r.entrada, -(r.valor + r.taxa_c)))
        cfs.append((r.saida, r.venda - r.taxa_v))
    ids = set(dd["id"])
    rr = DIR[DIR["id"].isin(ids)]
    for pag, v in zip(rr["pag"], rr["valor"]):
        cfs.append((pag, v))
    imp = imposto_mensal(dd[dd["fechada"]])
    if com_imposto:
        for t in imp:
            if t["imposto"] > 0:
                cfs.append((t["pag"], -t["imposto"]))
    return cfs, imp


def fluxos_espelho(d, so_fechadas=False):
    cfs, imp_tot = [], 0.0
    dd = d[d["fechada"]] if so_fechadas else d
    for r in dd.itertuples():
        V = r.valor + r.taxa_c
        liq, imp, _ = cdi_liquido(V, r.entrada, r.saida)
        cfs.append((r.entrada, -V))
        cfs.append((r.saida, liq))
        imp_tot += imp
    return cfs, imp_tot


TIR_ROWS = []
for c in CARTS:
    for p in PERIODOS:
        d = sub(c, p)
        for rot, sf in [("todas as ordens (em aberto a mercado, sem imposto)", False), ("só ordens fechadas", True)]:
            cfs, imp = fluxos_ordens(d, True, sf)
            cfm, imp_m = fluxos_espelho(d, sf)
            tir, tir_m = xirr(cfs), xirr(cfm)
            dd = d[d["fechada"]] if sf else d
            TIR_ROWS.append(dict(carteira=c, periodo=PER_ROT[p], base=rot, ordens=len(dd),
                                 investido_rs=float((dd["valor"] + dd["taxa_c"]).sum()),
                                 rendimentos_rs=float(DIR[DIR["id"].isin(set(dd["id"]))]["valor"].sum()),
                                 vendas_liq_rs=float((dd["venda"] - dd["taxa_v"]).sum()),
                                 imposto_fii_rs=float(sum(t["imposto"] for t in imp)),
                                 imposto_espelho_rs=imp_m,
                                 tir_ordens=tir, tir_espelho_105=tir_m, diferenca_pp=100 * (tir - tir_m)))
TIRD = pd.DataFrame(TIR_ROWS)
TIRD.to_csv(PL / "auditoria_bloco1_tir.csv", **OPC, float_format="%.6f")

secao("Taxa interna de retorno (a.a., XIRR com datas reais) - fluxos das ordens contra o espelho em 105% do CDI")
linhas = []
for r in TIRD.itertuples():
    linhas.append([r.carteira, r.periodo, r.base, r.ordens, brl(r.investido_rs), brl(r.rendimentos_rs),
                   brl(r.vendas_liq_rs), brl(r.imposto_fii_rs), brl(r.imposto_espelho_rs), pc(r.tir_ordens),
                   pc(r.tir_espelho_105), br(r.diferenca_pp, 1) + " pp"])
md_tabela(["Carteira", "Período", "Base", "Ordens", "Investido (compras + taxa)", "Rendimentos (na data de pagamento)",
           "Vendas líquidas de taxa", "Imposto do FII (mensal, com abatimento)", "Imposto + IOF do espelho",
           "TIR das ordens", "TIR do espelho 105% CDI", "Diferença"], linhas)

# imposto mensal vs documento (conferencia): A total
imp_A = imposto_mensal(sub("A", "total", True))
print(f"imposto mensal com abatimento, A total (fechadas): R$ {br(sum(t['imposto'] for t in imp_A))} "
      f"(o ESTUDO_KAIRI.md, Parte 4, diz R$ 13.033 com abatimento: bate)")
for c in ["B", "C"]:
    print(f"imposto mensal com abatimento, {c} total (fechadas): R$ "
          f"{br(sum(t['imposto'] for t in imposto_mensal(sub(c, 'total', True))))}")


# ---------------------------------------------------------------- 2c: carteira do pico
class Conta:
    """Saldo parado em 105% do CDI de liquidez diaria, em lotes. Cada deposito e um lote (unidades do indice);
    resgates saem do lote mais antigo (FIFO); IR (por dias corridos do lote) e IOF na hora do resgate."""

    def __init__(self, n_max):
        self.j = np.zeros(n_max, int)
        self.dta = np.zeros(n_max, "datetime64[D]")
        self.q = np.zeros(n_max)
        self.n = 0
        self.ini = 0
        self.divida_q = 0.0
        self.eventos_falta = []

    def deposita(self, jdia, valor):
        if valor <= 0:
            return
        if self.divida_q > 0:                       # quita a divida antes
            q = valor / I105[jdia]
            pago = min(q, self.divida_q)
            self.divida_q -= pago
            valor = (q - pago) * I105[jdia]
            if valor <= 1e-9:
                return
        self.j[self.n], self.dta[self.n] = jdia, CDD[jdia]
        self.q[self.n] = valor / I105[jdia]
        self.n += 1

    def fatores(self, jdia):
        sl = slice(self.ini, self.n)
        j0 = self.j[sl]
        y = 1 - I105[j0] / I105[jdia]
        dias = (CDD[jdia] - self.dta[sl]).astype(int)
        return y, dias, fator_liquido(y, dias)

    def saldo_liquido(self, jdia):
        if self.n == self.ini:
            return 0.0
        _, _, f = self.fatores(jdia)
        return float(np.sum(self.q[self.ini:self.n] * I105[jdia] * f))

    def saca_liquido(self, jdia, N):
        """Retira N liquido, do lote mais antigo ao mais novo. Devolve o que faltou (divida)."""
        while N > 1e-9 and self.ini < self.n:
            k = self.ini
            valor = self.q[k] * I105[jdia]
            y = 1 - I105[self.j[k]] / I105[jdia]
            dias = int((CDD[jdia] - self.dta[k]) / np.timedelta64(1, "D"))
            f = float(fator_liquido(y, dias))
            liq = valor * f
            if N >= liq - 1e-12:
                N -= liq
                self.q[k] = 0.0
                self.ini += 1
            else:
                G = N / f
                self.q[k] -= G / I105[jdia]
                N = 0.0
        if N > 1e-9:
            self.divida_q += N / I105[jdia]
            self.eventos_falta.append((pd.Timestamp(CDD[jdia]), N))
        return N


def simula_pico(c, d, pico):
    """Carteira do pico: deposito unico em 02/01/2018; ordens, rendimentos, vendas e imposto movimentam o saldo."""
    j0, jf = ix_cdi(INI), ix_cdi(FIM)
    nd = jf - j0 + 1
    ev = []        # (j, tipo 0=deposito 1=saque, valor)
    mkt = np.zeros(nd)
    rec = np.zeros(nd)
    pas = np.zeros(nd)
    fechadas = d[d["fechada"]]
    for r in d.itertuples():
        je = ix_cdi_prox(r.entrada)
        ev.append((je, 1, r.valor + r.taxa_c))
        js = ix_cdi_prox(r.saida) if r.fechada else jf
        if r.fechada:
            ev.append((js, 0, r.venda - r.taxa_v))
        dts, cl, _ = PRF[r.fundo]
        dias = CDD[je:(js if r.fechada else jf + 1)]
        pos = np.searchsorted(dts, dias, "right") - 1
        mkt[je - j0:(js if r.fechada else jf + 1) - j0] += r.cotas * cl[pos] * (1 - B3)
    rr = DIR[DIR["id"].isin(set(d["id"]))]
    for base, pag, v in zip(rr["base"], rr["pag"], rr["valor"]):
        jp = ix_cdi_prox(pag)
        a = ix_cdi_prox(base + pd.Timedelta(days=1))
        if pag <= FIM:
            ev.append((jp, 0, v))
            rec[max(a, j0) - j0:jp - j0] += v
        else:
            rec[max(a, j0) - j0:] += v
    imp = imposto_mensal(fechadas)
    pend_darf = 0.0
    for t in imp:
        if t["imposto"] <= 0:
            continue
        fim_mes = t["mes"].to_timestamp(how="end").normalize()
        a = min(ix_cdi(fim_mes), jf)
        if t["pag"] <= FIM:
            jp = ix_cdi_prox(t["pag"])
            ev.append((jp, 1, t["imposto"]))
            pas[a - j0:jp - j0] += t["imposto"]
        else:
            pas[a - j0:] += t["imposto"]
            pend_darf += t["imposto"]
    ev = sorted([e for e in ev if j0 <= e[0] <= jf], key=lambda e: (e[0], e[1]))
    conta = Conta(len(ev) + 5)
    conta.deposita(j0, pico)
    eq = np.zeros(nd)
    saldo = np.zeros(nd)
    k = 0
    for j in range(j0, jf + 1):
        while k < len(ev) and ev[k][0] == j:
            _, tipo, v = ev[k]
            if tipo == 0:
                conta.deposita(j, v)
            else:
                conta.saca_liquido(j, v)
            k += 1
        saldo[j - j0] = conta.saldo_liquido(j) - conta.divida_q * I105[j]
        eq[j - j0] = saldo[j - j0] + mkt[j - j0] + rec[j - j0] - pas[j - j0]
    comp = dict(saldo_liquido=saldo[-1], ordens_mercado=mkt[-1], a_receber=rec[-1], darf_pendente=pas[-1],
                dívida=conta.divida_q * I105[jf], faltas=len(conta.eventos_falta),
                falta_max=max([v for _, v in conta.eventos_falta], default=0.0), final=eq[-1])
    return eq, comp, conta


def espelho_pico(pico, jdias):
    """Todo o dinheiro em 105% do CDI desde 02/01/2018: patrimonio liquido (se resgatado no dia)."""
    j0 = jdias[0]
    y = 1 - I105[j0] / I105[jdias]
    dias = (CDD[jdias] - CDD[j0]).astype(int)
    return pico * I105[jdias] / I105[j0] * fator_liquido(y, dias)


JDIAS = np.arange(ix_cdi(INI), ix_cdi(FIM) + 1)
DIAS_TOT = (FIM - pd.Timestamp(CDD[JDIAS[0]])).days
MESES = {}
for pos_, j in enumerate(JDIAS):
    MESES.setdefault((CDD[j].astype("datetime64[M]")), []).append(pos_)
FIM_MES = {m: v[-1] for m, v in MESES.items()}          # posicao do ultimo dia de cada mes
MES_LISTA = sorted(FIM_MES)


def serie_mensal(eq):
    pts = [0] + [FIM_MES[m] for m in MES_LISTA]
    v = eq[pts]
    return v[1:] / v[:-1] - 1


def queda_maxima(eq):
    pk = np.maximum.accumulate(eq)
    dd = eq / pk - 1
    k = int(np.argmin(dd))
    k0 = int(np.argmax(eq[:k + 1]))
    return float(dd[k]), JDIAS[k0], JDIAS[k]


PICO_RES, SERIES = {}, {}
for c in CARTS:
    d = sub(c, "total")
    eq, comp, conta = simula_pico(c, d, PICO[c])
    eqb = espelho_pico(PICO[c], JDIAS)
    PICO_RES[c] = (eq, comp, eqb)
    SERIES[c] = dict(carteira=serie_mensal(eq), espelho=serie_mensal(eqb))
    print(f"carteira {c}: componentes finais {dict((k_, round(v_, 2)) for k_, v_ in comp.items())}")

# teste de consistencia do motor de lotes: sem ordens, o saldo final tem que ser igual ao do espelho
_c0 = Conta(10)
_c0.deposita(JDIAS[0], 100000.0)
dum = _c0.saldo_liquido(JDIAS[-1])
ref = float(espelho_pico(100000.0, JDIAS)[-1])
print(f"teste do motor de lotes (sem ordens): saldo {br(dum)} contra espelho {br(ref)}; diferenca {dum - ref:.6f}")
assert abs(dum - ref) < 1e-6
# teste de saque: depositar 3 lotes, sacar liquido, e conferir que o patrimonio total cai exatamente o liquido sacado
_c1 = Conta(10)
for jj, vv in [(JDIAS[0], 50000.0), (ix_cdi(pd.Timestamp("2019-03-04")), 20000.0), (ix_cdi(pd.Timestamp("2019-06-03")), 10000.0)]:
    _c1.deposita(jj, vv)
jt = ix_cdi(pd.Timestamp("2019-06-20"))
antes = _c1.saldo_liquido(jt)
_c1.saca_liquido(jt, 55000.0)
depois = _c1.saldo_liquido(jt)
print(f"teste de saque FIFO: saldo liquido antes {br(antes)}, sacou 55.000,00, depois {br(depois)}; "
      f"antes - depois = {br(antes - depois)}")
assert abs((antes - depois) - 55000.0) < 1e-6

secao(f"Carteira do pico (saldo parado em 105% do CDI) contra todo o dinheiro em 105% do CDI - valores em {FIM:%d/%m/%Y}")
linhas, PICO_ROWS = [], []
for c in CARTS:
    eq, comp, eqb = PICO_RES[c]
    P0, F, Fb = PICO[c], comp["final"], eqb[-1]
    anos = DIAS_TOT / 365.0
    ra, rb = (F / P0) ** (1 / anos) - 1, (Fb / P0) ** (1 / anos) - 1
    PICO_ROWS.append(dict(carteira=c, dinheiro_inicial=P0, ordens_em_aberto_a_mercado=comp["ordens_mercado"],
                          saldo_liquido_de_IR=comp["saldo_liquido"], rendimentos_a_receber=comp["a_receber"],
                          DARF_a_pagar=comp["darf_pendente"], valor_final_carteira=F, valor_final_espelho=Fb,
                          retorno_aa_carteira=ra, retorno_aa_espelho=rb, diferenca_pp=100 * (ra - rb),
                          diferenca_rs=F - Fb, faltas_de_caixa=comp["faltas"]))
    linhas.append([c, brl(P0), brl(comp["ordens_mercado"]), brl(comp["saldo_liquido"]), brl(comp["a_receber"]),
                   brl(-comp["darf_pendente"]), brl(F), brl(Fb), pc(ra), pc(rb), br(100 * (ra - rb), 1) + " pp",
                   brl(F - Fb), comp["faltas"]])
pd.DataFrame(PICO_ROWS).to_csv(PL / "auditoria_bloco1_pico.csv", **OPC, float_format="%.6f")
md_tabela(["Carteira", "Dinheiro no início (pico)", "Ordens em aberto a mercado", "Saldo líquido de IR e IOF",
           "Rendimentos declarados a receber", "DARF a pagar", "Valor final da carteira",
           "Valor final, tudo em 105% CDI", "Retorno ao ano da carteira (TIR)", "Retorno ao ano, tudo em 105% CDI",
           "Diferença", "Diferença (R$)", "Eventos de falta de caixa"], linhas)

# ---------------------------------------------------------------- 2d: Sharpe, Sortino, Calmar
secao("Sharpe, Sortino e Calmar da carteira do pico (retornos mensais do patrimônio líquido)")
RISCO_ROWS = []
linhas = []
for c in CARTS:
    eq, comp, eqb = PICO_RES[c]
    rm, rf = SERIES[c]["carteira"], SERIES[c]["espelho"]
    ex = rm - rf
    anos = DIAS_TOT / 365.0
    cagr = (eq[-1] / PICO[c]) ** (1 / anos) - 1
    dd, dpk, dfd = queda_maxima(eq)
    sharpe = ex.mean() / ex.std(ddof=1) * np.sqrt(12)
    semi = np.sqrt(np.mean(np.minimum(ex, 0.0) ** 2))
    sortino = ex.mean() / semi * np.sqrt(12)
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    ddb, _, _ = queda_maxima(eqb)
    cagrb = (eqb[-1] / PICO[c]) ** (1 / anos) - 1
    RISCO_ROWS += [dict(carteira=c, serie="carteira do pico", retorno_aa=cagr, vol_mensal=rm.std(ddof=1),
                        excesso_mensal_medio=ex.mean(), sharpe=sharpe, sortino=sortino, calmar=calmar,
                        maior_queda=dd, inicio_queda=pd.Timestamp(CDD[dpk]), fundo_queda=pd.Timestamp(CDD[dfd])),
                   dict(carteira=c, serie="espelho 105% CDI", retorno_aa=cagrb, vol_mensal=rf.std(ddof=1),
                        excesso_mensal_medio=0.0, sharpe=np.nan, sortino=np.nan, calmar=np.nan, maior_queda=ddb,
                        inicio_queda=pd.NaT, fundo_queda=pd.NaT)]
    linhas.append([c, "Carteira do pico", pc(cagr), pc(rm.std(ddof=1), 2), br(100 * ex.mean(), 3) + " pp",
                   br(sharpe, 2), br(sortino, 2), br(calmar, 2), pc(dd),
                   f"{pd.Timestamp(CDD[dpk]):%d/%m/%Y} a {pd.Timestamp(CDD[dfd]):%d/%m/%Y}"])
    linhas.append([c, "Espelho: tudo em 105% CDI", pc(cagrb), pc(rf.std(ddof=1), 2), "0 por construção", "n/d", "n/d",
                   "n/d (sem queda)", pc(ddb), "-"])
pd.DataFrame(RISCO_ROWS).to_csv(PL / "auditoria_bloco1_risco.csv", **OPC, float_format="%.6f")
md_tabela(["Carteira", "Série", "Retorno ao ano", "Desvio dos retornos mensais", "Excesso mensal médio",
           "Sharpe", "Sortino", "Calmar", "Maior queda do patrimônio", "Período da maior queda (do pico ao fundo)"],
          linhas)

# patrimonio mensal (csv)
mrows = []
for c in CARTS:
    eq, comp, eqb = PICO_RES[c]
    pts = [FIM_MES[m] for m in MES_LISTA]
    rm, rf = SERIES[c]["carteira"], SERIES[c]["espelho"]
    for k_, m in enumerate(MES_LISTA):
        mrows.append(dict(carteira=c, mes=str(m), data_fim=pd.Timestamp(CDD[JDIAS[pts[k_]]]), patrimonio_carteira=eq[pts[k_]],
                          patrimonio_espelho=eqb[pts[k_]], retorno_carteira=rm[k_], retorno_espelho=rf[k_],
                          excesso=rm[k_] - rf[k_]))
MES_DF = pd.DataFrame(mrows)
MES_DF.to_csv(PL / "auditoria_bloco1_patrimonio_mensal.csv", **OPC, float_format="%.6f")

# ================================================================= ITEM 3: SIGNIFICANCIA
print("\n==== ITEM 3: SIGNIFICANCIA ====")


def t_teste(x):
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return dict(n=n, media=x.mean() if n else np.nan, t=np.nan, p=np.nan, lo=np.nan, hi=np.nan)
    m, se = x.mean(), x.std(ddof=1) / np.sqrt(n)
    t = m / se
    p = 2 * (1 - stats.t.cdf(abs(t), n - 1))
    h = stats.t.ppf(0.975, n - 1) * se
    return dict(n=n, media=m, t=t, p=p, lo=m - h, hi=m + h)


def newey_west(x, L):
    x = np.asarray(x, float)
    n = len(x)
    m = x.mean()
    e = x - m
    s = np.sum(e * e) / n
    for l in range(1, L + 1):
        s += 2 * (1 - l / (L + 1)) * np.sum(e[l:] * e[:-l]) / n
    se = np.sqrt(s / n)
    t = m / se
    p = 2 * (1 - stats.t.cdf(abs(t), n - 1))
    h = stats.t.ppf(0.975, n - 1) * se
    return dict(n=n, media=m, se=se, t=t, p=p, lo=m - h, hi=m + h)


def boot_blocos(x, L=6, B=10000, seed=SEMENTE):
    x = np.asarray(x, float)
    n = len(x)
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / L))
    st = rng.integers(0, n - L + 1, size=(B, nb))
    idx = (st[:, :, None] + np.arange(L)[None, None, :]).reshape(B, -1)[:, :n]
    mm = x[idx].mean(axis=1)
    return np.percentile(mm, 2.5), np.percentile(mm, 97.5), float(np.mean(mm <= 0)), float(mm.std(ddof=1))


SIG = []
# (i) por ordem, ingenuo; (ii) por episodio
for c in CARTS:
    for p in PERIODOS:
        d = sub(c, p, True)
        t = t_teste(100 * d["exc_pct"].to_numpy())
        SIG.append(dict(carteira=c, periodo=PER_ROT[p], metodo="por ordem, ingênuo", n=t["n"], media=t["media"],
                        t=t["t"], p=t["p"], ic_lo=t["lo"], ic_hi=t["hi"], unidade="pp por ordem"))
        for W in [10, 20, 40]:
            e = EPD[(EPD.janela_pregoes == W) & (EPD.carteira == c) & (EPD.periodo == PER_ROT[p])].dropna(subset=["excesso_pct_medio"])
            t = t_teste(e["excesso_pct_medio"].to_numpy())
            SIG.append(dict(carteira=c, periodo=PER_ROT[p], metodo=f"por episódio (W={W})", n=t["n"], media=t["media"],
                            t=t["t"], p=t["p"], ic_lo=t["lo"], ic_hi=t["hi"], unidade="pp por episódio"))

# (ii) Newey-West e (iii) bootstrap no excesso mensal da carteira do pico
def fatia_meses(p):
    out = []
    for k_, m in enumerate(MES_LISTA):
        ano = int(str(m)[:4])
        if p == "total" or (p == "escolha" and ano <= CORTE_ESC) or (p == "conferência" and ano > CORTE_ESC):
            out.append(k_)
    return np.array(out)


for c in CARTS:
    ex_all = SERIES[c]["carteira"] - SERIES[c]["espelho"]
    for p in PERIODOS:
        x = ex_all[fatia_meses(p)]
        for L in [3, 6, 12]:
            r_ = newey_west(x, L)
            SIG.append(dict(carteira=c, periodo=PER_ROT[p], metodo=f"mensal do pico, Newey-West (defasagens={L})",
                            n=r_["n"], media=12 * 100 * r_["media"], t=r_["t"], p=r_["p"], ic_lo=12 * 100 * r_["lo"],
                            ic_hi=12 * 100 * r_["hi"], unidade="pp ao ano (média mensal x 12)"))
        lo, hi, pnl, sd = boot_blocos(x)
        SIG.append(dict(carteira=c, periodo=PER_ROT[p], metodo="mensal do pico, bootstrap em blocos de 6 meses",
                        n=len(x), media=12 * 100 * x.mean(), t=np.nan, p=np.nan, ic_lo=12 * 100 * lo, ic_hi=12 * 100 * hi,
                        unidade="pp ao ano (média mensal x 12)", rep_nao_positivas=100 * pnl))
SIGD = pd.DataFrame(SIG)
SIGD.to_csv(PL / "auditoria_bloco1_significancia.csv", **OPC, float_format="%.6f")


def linha_sig(r):
    return [r.carteira, r.periodo, r.n, br(r.media, 2), br(r.t, 2), br(r.p, 4) if not isnan(r.p) else "n/d",
            f"{br(r.ic_lo, 2)} a {br(r.ic_hi, 2)}"]


secao("Significância - por ordem (ingênuo, trata cada ordem como independente) e por episódio independente")
cols = ["Carteira", "Período", "n", "Média do excesso (pp)", "t", "Valor p", "IC 95% (pp)"]
for metodo in ["por ordem, ingênuo", "por episódio (W=20)", "por episódio (W=10)", "por episódio (W=40)"]:
    emit(f"**{metodo}**\n")
    md_tabela(cols, [linha_sig(r) for r in SIGD[SIGD.metodo == metodo].itertuples()])

secao("Significância - excesso mensal da carteira do pico (Newey-West, em pontos percentuais ao ano) e bootstrap em blocos")
for L in [6, 3, 12]:
    emit(f"**Newey-West, defasagens = {L}**\n")
    md_tabela(["Carteira", "Período", "Meses", "Excesso médio (pp/ano)", "t", "Valor p", "IC 95% (pp/ano)"],
              [linha_sig(r) for r in SIGD[SIGD.metodo == f"mensal do pico, Newey-West (defasagens={L})"].itertuples()])
emit("**Bootstrap em blocos de 6 meses (10.000 repetições)**\n")
md_tabela(["Carteira", "Período", "Meses", "Excesso médio (pp/ano)", "IC 95% (pp/ano)", "% das repetições com média <= 0"],
          [[r.carteira, r.periodo, r.n, br(r.media, 2), f"{br(r.ic_lo, 2)} a {br(r.ic_hi, 2)}",
            br(r.rep_nao_positivas, 2) + "%"]
           for r in SIGD[SIGD.metodo == "mensal do pico, bootstrap em blocos de 6 meses"].itertuples()])

# ================================================================= CONFERENCIA A MAO
print("\n==== CONFERENCIA A MAO (refeita com codigo independente, lendo as planilhas brutas) ====")
cand = O[(O.cart == "A") & O.fechada & (O.rend > 0) & (O.res_pre > 0)].iloc[0]
print(f"Ordem: carteira A, {cand.fundo}, entrada {cand.entrada:%d/%m/%Y}, saida {cand.saida:%d/%m/%Y} ({cand.motivo})")
raw_p = pd.read_csv(PL / f"precos_{cand.entrada.year}.csv", sep=";", decimal=",", encoding="utf-8-sig")
lin = raw_p[(raw_p["fundo"] == cand.fundo) & (raw_p["data"] == cand.entrada.strftime("%d/%m/%Y"))].iloc[0]
px_e = float(lin["abertura"])
print(f"  abertura em {cand.entrada:%d/%m/%Y} (precos_{cand.entrada.year}.csv) = {px_e:.4f}; cotas = {cand.cotas}; "
      f"cotas x preco = {cand.cotas * px_e:.2f}; planilha da ordem diz {cand.valor:.2f}")
rend_m, lst = 0.0, []
for _, rw in pd.read_csv(PL / "rendimentos_pagamentos.csv", sep=";", decimal=",", encoding="utf-8-sig").iterrows():
    if rw["fundo"] != cand.fundo:
        continue
    db = pd.to_datetime(rw["data_base"], format="%d/%m/%Y")
    ok = (db >= cand.entrada) and ((db <= cand.saida) if cand.incl else (db < cand.saida))
    if ok:
        v = float(rw["valor (R$/cota)"]) * cand.cotas
        rend_m += v
        lst.append((rw["data_base"], rw["data_pagamento"], float(rw["valor (R$/cota)"]), v))
for l in lst:
    print(f"  aviso data-base {l[0]}, pago em {l[1]}: R$ {l[2]:.4f}/cota x {cand.cotas} = R$ {l[3]:.2f}")
print(f"  soma dos rendimentos = R$ {rend_m:.2f}; planilha 'Rendimentos recebidos' = R$ {cand.rend_csv:.2f}")
venda = cand.valor + cand.valoriz
taxa_c, taxa_v = 0.0003 * cand.valor, 0.0003 * venda
print(f"  compra = {cand.valor:.2f} + taxa {taxa_c:.4f} = {cand.valor + taxa_c:.4f}; venda = valor + valorizacao = "
      f"{cand.valor:.2f} + ({cand.valoriz:.2f}) = {venda:.2f}; taxa de venda {taxa_v:.4f}")
res_m = cand.valoriz + rend_m - taxa_c - taxa_v
print(f"  resultado antes do imposto = {cand.valoriz:.2f} + {rend_m:.2f} - {taxa_c:.4f} - {taxa_v:.4f} = {res_m:.4f} "
      f"({100 * res_m / cand.valor:.3f}% da ordem); pipeline: {cand.res_pre:.4f} ({100 * cand.res_pre_pct:.3f}%)")
cdi_raw = pd.read_csv(PL / "cdi.csv", sep=";", decimal=",", encoding="utf-8-sig").set_index("data")
i0, i1 = float(cdi_raw.loc[cand.entrada.strftime("%d/%m/%Y"), "indice_105_do_cdi"]), float(
    cdi_raw.loc[cand.saida.strftime("%d/%m/%Y"), "indice_105_do_cdi"])
g_m = i1 / i0 - 1
print(f"  105% do CDI no mesmo prazo: {i1:.8f} / {i0:.8f} - 1 = {100 * g_m:.4f}%; excesso = {100 * res_m / cand.valor:.3f}% - "
      f"{100 * g_m:.3f}% = {100 * (res_m / cand.valor - g_m):.3f} pp; pipeline: {100 * cand.exc_pct:.3f} pp")
assert abs(res_m - cand.res_pre) < 0.02 and abs((res_m / cand.valor - g_m) - cand.exc_pct) < 5e-4

print("\n  Aplicacao no CDI (mao): R$ 10.000,00 de 09/05/2018 a 19/03/2019")
a0, a1 = float(cdi_raw.loc["09/05/2018", "indice_105_do_cdi"]), float(cdi_raw.loc["19/03/2019", "indice_105_do_cdi"])
dias = (pd.Timestamp("2019-03-19") - pd.Timestamp("2018-05-09")).days
bruto = 10000 * (a1 / a0 - 1)
aliq = 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15
liq_m = 10000 + bruto - aliq * bruto
liq_f, imp_f, br_f = cdi_liquido(10000, "2018-05-09", "2019-03-19")
print(f"  indices {a1:.8f}/{a0:.8f}; bruto = {bruto:.4f}; dias corridos = {dias} -> aliquota {100 * aliq:.1f}%; liquido = "
      f"{liq_m:.4f}; funcao: {liq_f:.4f}")
assert abs(liq_m - liq_f) < 1e-6
print("\n  Aplicacao no CDI com IOF (mao): R$ 10.000,00 de 03/02/2020 a 18/02/2020 (15 dias)")
a0, a1 = float(cdi_raw.loc["03/02/2020", "indice_105_do_cdi"]), float(cdi_raw.loc["18/02/2020", "indice_105_do_cdi"])
bruto = 10000 * (a1 / a0 - 1)
iof = 0.50          # 15o dia da tabela (96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50): 50%
liq_m = 10000 + bruto - bruto * iof - 0.225 * (bruto * (1 - iof))
liq_f, imp_f, br_f = cdi_liquido(10000, "2020-02-03", "2020-02-18")
print(f"  bruto = {bruto:.4f}; IOF 50% = {bruto * iof:.4f}; IR 22,5% sobre {bruto * (1 - iof):.4f} = "
      f"{0.225 * bruto * (1 - iof):.4f}; liquido = {liq_m:.4f}; funcao: {liq_f:.4f}")
assert abs(liq_m - liq_f) < 1e-6
# TIR de uma ordem so (conferencia): NPV a taxa encontrada tem que ser ~ 0
one = O[O["id"] == cand["id"]]
cf1, _ = fluxos_ordens(one, False, True)
r1 = xirr(cf1)
t0_ = min(d_ for d_, _ in cf1)
npv = sum(v * (1 + r1) ** (-(d_ - t0_).days / 365) for d_, v in cf1)
print(f"\n  TIR da ordem sozinha (sem imposto): {100 * r1:.3f}% ao ano; valor presente dos fluxos nessa taxa = {npv:.8f}")
print("  fluxos: " + "; ".join(f"{d_:%d/%m/%Y} {v:+.2f}" for d_, v in sorted(cf1)))
assert abs(npv) < 1e-4

# ================================================================= LACUNAS
lac = [
    ("Data de pagamento dos rendimentos", f"{len(sp)} avisos (R$ {br(sp['valor'].sum())}) nas ordens sem data de pagamento; "
     f"usada data-base + {MEDIANA_DIAS} dias", "pequeno: desloca poucos dias o recebimento na TIR e no saldo"),
    ("Rendimentos pagos depois de 09/11/2026", f"{len(pos_fim)} avisos (R$ {br(pos_fim['valor'].sum())}) de ordens da base; entram na "
     "TIR na data de pagamento e na carteira do pico como 'a receber' (valor declarado)", "valor final inclui dinheiro ainda não recebido"),
    ("Ordens em aberto", f"{int((~O.fechada).sum())} ordens avaliadas ao preço de 09/11/2026, sem imposto e com taxa de venda",
     "TIR das ordens um pouco favorecida (sem imposto); versão só com fechadas mostrada"),
    ("Imposto por ordem", "o imposto do FII é mensal com abatimento: não se divide por ordem", "comparações por ordem são antes do imposto dos dois lados"),
    ("Dias úteis depois de 13/11/2026", "o cdi.csv termina em 13/11/2026; DARF de vendas de novembro/2026 usa o último dia de semana de dezembro (sem feriados)",
     "no máximo 1 dia de diferença em um imposto"),
    ("Amortizações", "não entram como dinheiro recebido nas ordens (lacuna herdada do estudo anterior)",
     "ordens de fundos que devolveram patrimônio aparecem com perda maior que a real"),
    ("Saltos de preço sem ajuste", "334 variações de mais de 25% em um dia, em 128 fundos (README das planilhas); 13 das 341 ordens da A têm um salto",
     "afeta o resultado dessas ordens; não removidas"),
    ("Preços da planilha de ordens", "valor e valorização arredondados ao centavo em kairi_ordens.csv", "erro de até 1 centavo por ordem"),
    ("Índice da bolsa de ações", "não existe na base; 'mercado' do estudo é o FII do meio", "sem comparação com ações"),
    ("Fundo com último preço antes de 09/11/2026", f"{N_ABERTA_ANTES} ordem(ns) em aberto cujo último preço é anterior a 09/11/2026 (avaliada nesse preço)",
     "efeito desprezível"),
    ("Ordens em aberto fora das estatísticas por ordem", f"as {int((~O.fechada).sum())} ordens em aberto não entram nos indicadores, no teste ingênuo nem no resultado por episódio (só nos fluxos de TIR, no saldo do pico e na contagem de episódios)",
     "estatísticas por ordem usam só ordens fechadas, como o estudo anterior"),
    ("kairi_ordens_saidas.csv sem a carteira C", "a conferência cruzada do resultado antes do imposto com esse arquivo só vale para A e B; para C a conferência é a dos rendimentos e das taxas",
     "nenhum efeito nos números"),
    ("Imposto a pagar no patrimônio mensal", "o imposto do mês só entra como dívida no último dia do mês da venda; antes disso o patrimônio não o desconta",
     "pequena oscilação no patrimônio dentro do mês; afeta pouco Sharpe, Sortino e Calmar"),
    ("Falta de caixa na carteira do pico", "o programa prevê dívida a 105% do CDI se o saldo acabar; não ocorreu nenhuma vez (ver coluna da tabela)",
     "sem efeito"),
    ("Estimativa do imposto das ordens em aberto", "não calculado (venda hipotética)", "TIR das ordens e valor final do pico levemente favorecidos"),
]
O.drop(columns=["incl"]).assign(
    entrada=O["entrada"], saida=O["saida"]).rename(columns={
        "cart": "carteira", "px_e": "preco_entrada", "px_s": "preco_saida", "valoriz": "valorizacao_rs",
        "rend": "rendimentos_calculados_rs", "rend_csv": "rendimentos_planilha_rs", "res_pre": "resultado_antes_imposto_rs",
        "res_pre_pct": "resultado_antes_imposto_frac", "cdi_bruto_pct": "cdi105_bruto_frac", "exc_pct": "excesso_frac",
        "exc_rs": "excesso_rs", "taxa_c": "taxa_compra_rs", "taxa_v": "taxa_venda_rs", "dif_rend": "dif_rendimentos_rs",
        "dif_res_saidas": "dif_resultado_vs_saidas_rs"})[
    ["carteira", "fundo", "sinal", "entrada", "saida", "motivo", "situacao", "periodo", "cotas", "valor",
     "valorizacao_rs", "rendimentos_calculados_rs", "rendimentos_planilha_rs", "dif_rendimentos_rs", "taxa_compra_rs",
     "taxa_venda_rs", "resultado_antes_imposto_rs", "resultado_antes_imposto_frac", "cdi105_bruto_frac", "excesso_frac",
     "excesso_rs", "dif_resultado_vs_saidas_rs"]].to_csv(PL / "auditoria_bloco1_ordens.csv", **OPC, float_format="%.6f")
pd.DataFrame(lac, columns=["dado", "situacao", "efeito"]).to_csv(PL / "auditoria_bloco1_lacunas.csv", **OPC)

print(f"\nTempo total: {time.time() - T0:.1f} s")
if MD_SAIDA:
    MD_SAIDA.write_text("\n".join(MD_BUF), encoding="utf-8")
print("Roda sem erro.")
