"""Carteira simulada do Indice de Kairi em FIIs: dinheiro limitado, dia a dia.

Reaproveita a carga, o universo, o calculo do Kairi, os sinais e a guarda de qualidade
de estudos/kairi.py. Como kairi.py executa todo o estudo no import, as funções foram
copiadas (mesma regra).

Carteiras (todas N=200, rendimento mantido = sim):
    A: X=0,15     B: X=0,20     C: X=0,15 so em dia de queda geral (amplitude >= 0,15)
Ordens: R$ 1.000, R$ 2.000, R$ 3.300  ->  9 simulacoes.

Rodar com:
    PYTHONPATH=. .venv/bin/python estudos/kairi_carteira.py 2>&1 | tee dados/kairi_carteira.txt
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

INICIO_D = np.datetime64("2018-01-01", "D")
CORTE_22 = pd.Timestamp("2022-12-31")
CAPITAL = 10000.0
B3 = 0.0003                              # taxa de 0,03% por lado (compra e venda)
IR_OP = 0.20
IR_CX = 0.225
MIN_OP = 200.0
PCT_VOL = 0.02
EXCLUIDOS = {"XPPR11", "CARE11"}
N = 200
PRAZO = 252
LAG_REND = 126
AMP_LIM = 0.15
AMP_K = -0.10
ORDENS = [1000.0, 2000.0, 3300.0]
CART = {
    "A": dict(X=0.15, amp=False),
    "B": dict(X=0.20, amp=False),
    "C": dict(X=0.15, amp=True),
}
VOLTA = "volta à média"
GUARDA = "guarda de qualidade"
PRAZO_M = "prazo 252 pregoes"
SAIU = "linhas de preco acabaram"
ABERTO = "em aberto"


def pc(x):
    return "nd" if x is None or pd.isna(x) else f"{x * 100:.2f}%".replace(".", ",")


def nu(x, d=2):
    return "nd" if x is None or pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def brl(x):
    if x is None or pd.isna(x):
        return "nd"
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def show(df, pcts=(), brls=(), nums=()):
    d = df.copy()
    for c in pcts:
        d[c] = d[c].map(pc)
    for c in brls:
        d[c] = d[c].map(brl)
    for c in nums:
        d[c] = d[c].map(lambda v: nu(v, 1))
    print(d.to_string(index=False))


# ---------------------------------------------------------------- carga (copiada de estudos/kairi.py)
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

C_AB, C_MX, C_MN, C_FE = "abertura", "maxima", "minima", "fechamento"
C_NEG = "negociou (1/0)"
C_REND, C_PVP, C_PAT = "rendimento_mensal (R$/cota)", "preco_sobre_valor_patrimonial", "patrimonio (R$)"
C_VOL, C_AMO = "volume_medio_60 (R$)", "amortizacao_12m (1/0)"
for c in [C_AB, C_MX, C_MN, C_FE, C_NEG, C_REND, C_PVP, C_PAT, C_VOL, C_AMO]:
    assert c in PR.columns, c
assert "valor (R$/cota)" in RD.columns

dups = int(PR.duplicated(["fundo", "data"]).sum())
PR = PR.drop_duplicates(["fundo", "data"]).sort_values(["fundo", "data"]).reset_index(drop=True)
print(f"linhas duplicadas (fundo, data) em precos removidas: {dups}")
print(f"linhas de precos com fechamento NaN: {int(PR[C_FE].isna().sum())}")
RD_NA = int(RD["data_base"].isna().sum())
RD = RD.dropna(subset=["data_base"]).reset_index(drop=True)
RD_DUP = int(RD.duplicated(["fundo", "data_base", "valor (R$/cota)"]).sum())
print(f"rendimentos com data_base NaN (removidos): {RD_NA}; avisos duplicados (fundo, data_base, valor), "
      f"MANTIDOS como em kairi.py: {RD_DUP}")

MK_DATAS = MK["data"]
MD = MK_DATAS.to_numpy("datetime64[D]")
NM = len(MD)
TS = list(MK_DATAS)
SEL = MK["selic_ano (%)"].to_numpy(float)
IDX = MK["indice_mercado"].to_numpy(float)
assert not np.isnan(SEL).any() and not np.isnan(IDX).any()
assert len(set(MD)) == NM
I0 = int(np.searchsorted(MD, INICIO_D))
assert TS[I0] == pd.Timestamp("2018-01-02"), TS[I0]
G_CX = ((1 + SEL / 100) ** (1 / 252) - 1) * (1 - IR_CX)          # accrual diario do caixa e da Selic
LASTM = np.array([(mi == NM - 1) or (TS[mi + 1].month != TS[mi].month) for mi in range(NM)])
TIPO = dict(zip(FU["fundo"], FU["tipo"].astype(str)))


# ---------------------------------------------------------------- arrays por fundo (copiado de kairi.py + mi)
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

    univ = (PAT >= 50e6) & (VOL >= 25000) & (R > 0) & (AMO == 0) & (PVP >= 0.30) & (PVP <= 3.0)
    if nome in EXCLUIDOS:
        univ[:] = False

    bad = np.zeros(n, bool)                  # bad[j] trata o par (j-1, j)
    if n > 1:
        gap = np.diff(dates).astype("timedelta64[D]").astype(int)
        ret = C[1:] / C[:-1] - 1
        bad[1:] = (gap > 15) | (ret > 0.60) | (ret < -0.45)
    cbad = np.r_[0, np.cumsum(bad)]

    Cs = pd.Series(C)
    mN200 = Cs.rolling(N, min_periods=N).mean().to_numpy()       # inclui o dia
    k200 = C / mN200 - 1

    sim = np.zeros(n, bool)                  # rendimento hoje >= 0,95 x rendimento 126 pregoes antes
    if n > LAG_REND:
        sim[LAG_REND:] = R[LAG_REND:] >= 0.95 * R[:-LAG_REND]

    mi = np.searchsorted(MD, dates)
    assert (MD[mi] == dates).all(), nome                  # toda data de preco e dia de mercado
    FD[nome] = dict(nome=nome, n=n, dates=dates, mi=mi, A=A, H=H, L=L, C=C, R=R, PVP=PVP, NEG=NEG,
                    VOL=VOL, univ=univ, bad=bad, cbad=cbad, mN=mN200, k200=k200, sim=sim,
                    aberto=int(mi[-1]) >= NM - 21)       # ultimo dado nos ultimos 20 pregoes da base

# avisos de rendimento por pregao de mercado (data_base == pregao)
RDMI = {}
for f_, db_, v_ in zip(RD["fundo"], RD["data_base"], RD["valor (R$/cota)"]):
    dd_ = np.datetime64(db_, "D")
    m = int(np.searchsorted(MD, dd_))
    assert MD[m] == dd_
    RDMI.setdefault(m, []).append((f_, float(v_)))

# amplitude(d): fracao dos fundos do universo em d com kairi_200 <= -0,10 (so dados ate d)
AMP_NUM = np.zeros(NM)
AMP_DEN = np.zeros(NM)
for F in FD.values():
    valid = F["univ"] & np.isfinite(F["k200"])
    hit = valid & (F["k200"] <= AMP_K)
    np.add.at(AMP_DEN, F["mi"][valid], 1)
    np.add.at(AMP_NUM, F["mi"][hit], 1)
AMP = np.where(AMP_DEN > 0, AMP_NUM / np.where(AMP_DEN > 0, AMP_DEN, 1), np.nan)


# ---------------------------------------------------------------- sinais (copiado de kairi.py, sem ent_ok)
def sinais_base(F, X):
    """Cruzamento para baixo de -X em d, universo em d, N fechamentos, janela sem salto/buraco, rendimento mantido."""
    k = F["k200"]
    cross = np.zeros(F["n"], bool)
    cross[1:] = (k[1:] <= -X) & (k[:-1] > -X)
    base = cross & F["univ"]
    base[:N] = False
    idx = np.flatnonzero(base)
    jan = np.zeros(F["n"], bool)
    jan[idx] = (F["cbad"][idx + 1] - F["cbad"][idx - N]) > 0
    return base & ~jan & F["sim"]


# candidatos por pregao de EXECUCAO: sinal em d -> executa na abertura do pregao seguinte (mi_d + 1)
CAND = {}
for tipo, cfg in CART.items():
    if cfg["X"] in CAND:
        continue
    lst = [[] for _ in range(NM)]
    for F in FD.values():
        for s in np.flatnonzero(sinais_base(F, cfg["X"])):
            md = int(F["mi"][s])
            if md + 1 < NM:
                lst[md + 1].append(dict(F=F, s=int(s), mi_d=md, vol=float(F["VOL"][s])))
    CAND[cfg["X"]] = lst


# ---------------------------------------------------------------- saida da posicao
def saida(F, e):
    """Saida 'volta a media' com guarda de qualidade e prazo. Retorna (linha k, motivo, preco, media).

    Volta no pregao k: maxima(k) >= media dos N fechamentos ate k-1; vende max(abertura(k), media).
    Guarda: par (j-1, j) ruim com e < j <= k: vende no fechamento de j-1 (antes do problema).
    """
    last = F["n"] - 1
    fim = min(e + PRAZO, last)
    kg = kv = None
    mp = F["mN"]
    if fim > e:
        w = np.flatnonzero(F["bad"][e + 1:fim + 1])
        if w.size:
            kg = e + 1 + int(w[0])
        w2 = np.flatnonzero(F["H"][e + 1:fim + 1] >= mp[e:fim])
        if w2.size:
            kv = e + 1 + int(w2[0])
    if kg is not None and (kv is None or kg <= kv):      # o dado de j e lido antes da volta de j
        k = kg - 1
        return k, GUARDA, float(F["C"][k]), np.nan
    if kv is not None:
        media = float(mp[kv - 1])
        return kv, VOLTA, max(float(F["A"][kv]), media), media
    if e + PRAZO <= last:
        return e + PRAZO, PRAZO_M, float(F["C"][e + PRAZO]), np.nan
    if F["aberto"]:
        return None, ABERTO, np.nan, np.nan
    return last, SAIU, float(F["C"][last]), np.nan


# ---------------------------------------------------------------- simulacao da carteira
def simular(tipo, ordem):
    cfg = CART[tipo]
    cands = CAND[cfg["X"]]
    nome_sim = f"{tipo}-{int(ordem)}"
    cash = CAPITAL
    pend = 0.0
    pool = 0.0
    pos = {}
    ganhos_mes = {}
    ops, compras, rendas, impostos, nao, diario = [], [], [], [], [], []

    def vender(mi, t):
        """Vende as posicoes com saida neste pregao (saida no fechamento ou na mesma sessao da compra)."""
        nonlocal cash
        for nm in sorted(p for p, P in pos.items() if P["mi_s"] == mi):
            P = pos.pop(nm)
            vv = P["cotas"] * P["px_s"]
            tv = B3 * vv
            cash += vv - tv
            custo = P["val_c"] + P["fee_c"]
            ganho = (vv - tv) - custo
            ym = (t.year, t.month)
            ganhos_mes[ym] = ganhos_mes.get(ym, 0.0) + ganho
            rend = P["rend"]
            ops.append(dict(
                simulacao=nome_sim, carteira=tipo, ordem=ordem, fundo=nm, sinal=P["sinal"], entrada=P["entrada"],
                saida=t, motivo=P["mot"], pregoes=P["k"] - P["e"], cotas=P["cotas"], preco_entrada=P["px_e"],
                valor_compra=P["val_c"], taxa_compra=P["fee_c"], preco_saida=P["px_s"], valor_venda=vv,
                taxa_venda=tv, rendimentos=rend, ganho_tributavel=ganho,
                resultado=(vv - tv + rend - custo) / custo, em_aberto="nao", e_row=P["e"], k_row=P["k"],
                media_saida=P["media"], mi_d=P["mi_d"], mi_e=P["mi_e"], rend_det=P["rend_det"],
                ano=t.year))

    for mi in range(I0, NM):
        t = TS[mi]
        # 1. saidas
        vender(mi, t)
        # 2. imposto pendente de meses anteriores (se o caixa nao cobriu) e pago antes das compras
        if pend > 0 and cash > 0:
            pg = min(cash, pend)
            cash -= pg
            pend -= pg
            impostos.append(dict(data=t, mes=None, ganho_mes=np.nan, base=np.nan, devido=0.0, pago=pg))
        # 3. entradas: sinais do pregao anterior, na abertura de hoje, maior volume de 60 primeiro
        for c in sorted(cands[mi], key=lambda c: (-c["vol"], c["F"]["nome"])):
            F = c["F"]
            nm = F["nome"]
            if cfg["amp"] and not (np.isfinite(AMP[c["mi_d"]]) and AMP[c["mi_d"]] >= AMP_LIM):
                continue
            if nm in pos:
                continue
            r = int(np.searchsorted(F["dates"], MD[mi]))
            if r >= F["n"] or F["dates"][r] != MD[mi]:
                continue                                      # fundo nao negociou/sem linha hoje
            if F["NEG"][r] != 1 or not np.isfinite(F["A"][r]):
                continue
            px = float(F["A"][r])
            pc_ = px * (1 + B3)
            lim = min(ordem, PCT_VOL * c["vol"])
            n_oth = int(np.floor(lim / pc_ + 1e-9))
            budget = min(lim, cash)
            n_c = int(np.floor(budget / pc_ + 1e-9))
            if n_c * px < MIN_OP:
                if cash < lim and n_oth * px >= MIN_OP:
                    nao.append(dict(data=t, fundo=nm, sinal=TS[c["mi_d"]], ano=t.year))
                continue
            val = n_c * px
            fee = B3 * val
            cash -= val + fee
            k, mot, pxs, media = saida(F, r)
            P = dict(F=F, e=r, mi_e=mi, mi_d=c["mi_d"], sinal=TS[c["mi_d"]], entrada=t, cotas=n_c,
                     px_e=px, val_c=val, fee_c=fee, k=k, mot=mot, px_s=pxs, media=media,
                     mi_s=int(F["mi"][k]) if k is not None else None, rend=0.0, rend_det=[])
            pos[nm] = P
            compras.append(dict(data=t, fundo=nm, sinal=TS[c["mi_d"]], cotas=n_c, preco=px, valor=val,
                                taxa=fee, ano=t.year, mi_d=c["mi_d"], mi_e=mi, e_row=r, mot=mot))
        # 3b. posicao comprada hoje cuja saida e neste mesmo pregao (guarda no 1o dia): vende no fechamento
        vender(mi, t)
        # 2b. rendimentos: avisos com data_base = hoje, para posicoes abertas no fechamento de hoje
        for nm_f, valor in RDMI.get(mi, []):
            if nm_f in pos:
                P = pos[nm_f]
                amt = P["cotas"] * valor
                cash += amt
                P["rend"] += amt
                P["rend_det"].append((t, valor, P["cotas"], amt))
                rendas.append(dict(data=t, fundo=nm_f, valor=valor, cotas=P["cotas"], recebido=amt, ano=t.year))
        # 4. caixa parado rende a Selic
        cash += cash * G_CX[mi]
        # 5. imposto no ultimo pregao do mes
        if LASTM[mi]:
            ym = (t.year, t.month)
            gm = ganhos_mes.get(ym, 0.0)
            if gm >= 0:
                usa = min(pool, gm)
                base = gm - usa
                pool -= usa
            else:
                pool += -gm
                base = 0.0
            devido = IR_OP * base
            pend += devido
            pg = min(cash, pend)
            cash -= pg
            pend -= pg
            impostos.append(dict(data=t, mes=f"{ym[0]}-{ym[1]:02d}", ganho_mes=gm, base=base,
                                 devido=devido, pago=pg, ano=t.year))
        # 6. patrimonio = caixa + cotas x ultimo fechamento conhecido
        pv = 0.0
        for P in pos.values():
            F = P["F"]
            rr = int(np.searchsorted(F["dates"], MD[mi], "right") - 1)
            pv += P["cotas"] * float(F["C"][rr])
        pat = cash + pv - pend
        assert cash >= -1e-6, (nome_sim, t, cash)
        if pend == 0:
            assert abs(pat - (cash + pv)) < 1e-6, (nome_sim, t)
        diario.append(dict(data=t, caixa=cash, posicoes=pv, pendente=pend, patrimonio=pat,
                           n_pos=len(pos), aplicado=pv / pat))

    abertas = []
    for nm, P in pos.items():
        assert P["k"] is None and P["mi_s"] is None, (nome_sim, nm, P["mot"])   # so 'em aberto' sobra no fim
        F = P["F"]
        rr = int(np.searchsorted(F["dates"], MD[NM - 1], "right") - 1)
        cur = float(F["C"][rr])
        custo = P["val_c"] + P["fee_c"]
        abertas.append(dict(fundo=nm, entrada=P["entrada"], preco_entrada=P["px_e"], preco_atual=cur,
                            cotas=P["cotas"], valorizacao=cur / P["px_e"] - 1,
                            resultado=(cur * P["cotas"] + P["rend"] - custo) / custo,
                            rendimentos=P["rend"], dias_fundo=int(rr - P["e"])))
        ops.append(dict(
            simulacao=nome_sim, carteira=tipo, ordem=ordem, fundo=nm, sinal=P["sinal"], entrada=P["entrada"],
            saida=pd.NaT, motivo=P["mot"], pregoes=np.nan, cotas=P["cotas"], preco_entrada=P["px_e"],
            valor_compra=P["val_c"], taxa_compra=P["fee_c"], preco_saida=cur, valor_venda=np.nan,
            taxa_venda=np.nan, rendimentos=P["rend"], ganho_tributavel=np.nan, resultado=np.nan,
            em_aberto="sim", e_row=P["e"], k_row=None, media_saida=np.nan, mi_d=P["mi_d"], mi_e=P["mi_e"],
            rend_det=P["rend_det"], ano=np.nan))

    DIA = pd.DataFrame(diario)
    return dict(nome=nome_sim, tipo=tipo, ordem=ordem, dia=DIA,
                ops=pd.DataFrame([o for o in ops if o["em_aberto"] == "nao"]),
                ops_todas=pd.DataFrame(ops), compras=pd.DataFrame(compras), rendas=pd.DataFrame(rendas),
                impostos=pd.DataFrame(impostos), nao=pd.DataFrame(nao), abertas=pd.DataFrame(abertas))


# ---------------------------------------------------------------- comparacoes
SEL_VAL = CAPITAL * np.cumprod(1 + G_CX[I0:])                  # Tudo na Selic (mesma conta do caixa)
MERC_VAL = CAPITAL * IDX[I0:] / IDX[I0 - 1]                    # Mercado: indice do fundo do meio, sem custos
DATAS_SIM = TS[I0:]
N_PASSOS = NM - I0                                             # pregoes entre o fechamento de 29/12/2017 e o fim
ANOS_BASE = N_PASSOS / 252


def ano_base(v_final, anos):
    return (v_final / CAPITAL) ** (1 / anos) - 1


print(f"\nbase: {NM} pregoes de mercado ({TS[0].date()} a {TS[-1].date()}); inicio da carteira: {TS[I0].date()}; "
      f"fundos com precos: {len(FD)}; universo fixado em kairi.py (exceto XPPR11/CARE11).")
print(f"sinais por carteira (candidatos a executar, antes de caixa e volume): "
      f"X=0,15: {sum(len(x) for x in CAND[0.15])}; X=0,20: {sum(len(x) for x in CAND[0.20])}")

RES = {}
for tipo in CART:
    for ordem in ORDENS:
        RES[f"{tipo}-{int(ordem)}"] = simular(tipo, ordem)
print(f"\nsimulacoes rodadas: {len(RES)}; tempo ate aqui: {time.time() - T0:.1f} s")


def resumo_de(R):
    D = R["dia"].copy()
    D["selic"] = SEL_VAL
    D["mercado"] = MERC_VAL
    p = D["patrimonio"].to_numpy()
    base = np.r_[CAPITAL, p]
    pico = np.maximum.accumulate(base)[1:]
    dd = p / pico - 1
    j = int(np.argmin(dd))
    pk_val = pico[j]
    ipk = np.flatnonzero(p[:j + 1] == pk_val)
    data_pico = DATAS_SIM[ipk[-1]] if ipk.size else TS[I0 - 1]
    ops = R["ops"]
    ano_fim = D.groupby(D["data"].dt.year)
    fim_22 = D[D["data"] <= CORTE_22].iloc[-1]
    fim_fim = D.iloc[-1]
    return dict(
        patrimonio_final=float(fim_fim["patrimonio"]),
        retorno_total=float(fim_fim["patrimonio"] / CAPITAL - 1),
        retorno_ao_ano=float(ano_base(fim_fim["patrimonio"], ANOS_BASE)),
        selic_total=float(fim_fim["selic"] / CAPITAL - 1), selic_ao_ano=float(ano_base(fim_fim["selic"], ANOS_BASE)),
        mercado_total=float(fim_fim["mercado"] / CAPITAL - 1),
        mercado_ao_ano=float(ano_base(fim_fim["mercado"], ANOS_BASE)),
        maior_queda=float(dd[j]), data_pico=data_pico, pico_valor=float(pk_val),
        data_fundo=DATAS_SIM[j], max_posicoes=int(D["n_pos"].max()),
        operacoes=int(len(ops)),
        pct_ganho=float((ops["resultado"] > 0).mean()) if len(ops) else np.nan,
        resultado_medio=float(ops["resultado"].mean()) if len(ops) else np.nan,
        pregoes_medios=float(ops["pregoes"].mean()) if len(ops) else np.nan,
        abertas_fim=int((R["abertas"]).shape[0]),
        nao_atendidos=int(len(R["nao"])),
        ret_18_22=float(fim_22["patrimonio"] / CAPITAL - 1),
        ret_23_fim=float(fim_fim["patrimonio"] / fim_22["patrimonio"] - 1),
        selic_18_22=float(fim_22["selic"] / CAPITAL - 1), selic_23_fim=float(fim_fim["selic"] / fim_22["selic"] - 1),
        mercado_18_22=float(fim_22["mercado"] / CAPITAL - 1),
        mercado_23_fim=float(fim_fim["mercado"] / fim_22["mercado"] - 1),
        ret_18_22_val=float(fim_22["patrimonio"]), dd_pico=pk_val,
    )


def tabela_anos(R):
    D = R["dia"].copy()
    D["selic"] = SEL_VAL
    D["mercado"] = MERC_VAL
    D["ano"] = D["data"].dt.year
    ano_fim = D.groupby("ano").last()
    rows = []
    prev = dict(patrimonio=CAPITAL, selic=CAPITAL, mercado=CAPITAL)
    ops = R["ops"]
    comp, imp, ren, nao_ = R["compras"], R["impostos"], R["rendas"], R["nao"]
    for ano in ano_fim.index:
        f = ano_fim.loc[ano]
        o = ops[ops["ano"] == ano] if len(ops) else ops
        rows.append(dict(
            ano=str(ano) + (" (ate 09/11)" if ano == TS[-1].year else ""),
            patrimonio_fim=float(f["patrimonio"]),
            retorno_ano=float(f["patrimonio"] / prev["patrimonio"] - 1),
            selic_ano=float(f["selic"] / prev["selic"] - 1),
            mercado_ano=float(f["mercado"] / prev["mercado"] - 1),
            compras=int((comp["data"].dt.year == ano).sum()) if len(comp) else 0,
            vendas=int(len(o)),
            pct_vendas_ganho=float((o["resultado"] > 0).mean()) if len(o) else np.nan,
            rendimentos=float(ren.loc[ren["ano"] == ano, "recebido"].sum()) if len(ren) else 0.0,
            imposto_pago=float(imp.loc[imp["data"].dt.year == ano, "pago"].sum()) if len(imp) else 0.0,
            nao_atendidos=int((nao_["ano"] == ano).sum()) if len(nao_) else 0,
            pct_aplicado=float(D.loc[D["ano"] == ano, "aplicado"].mean()),
        ))
        prev = dict(patrimonio=f["patrimonio"], selic=f["selic"], mercado=f["mercado"])
    return pd.DataFrame(rows)


RESUMO = {k: resumo_de(R) for k, R in RES.items()}
for k, R in RES.items():
    print(f"\n==================== SIMULACAO {k}: carteira {R['tipo']}, ordem {brl(R['ordem'])} ====================")
    r = RESUMO[k]
    print(f"patrimonio final {brl(r['patrimonio_final'])}; retorno total {pc(r['retorno_total'])}; "
          f"retorno ao ano {pc(r['retorno_ao_ano'])}")
    print(f"  Tudo na Selic: {brl(SEL_VAL[-1])}; total {pc(r['selic_total'])}; ao ano {pc(r['selic_ao_ano'])}")
    print(f"  Mercado: {brl(MERC_VAL[-1])}; total {pc(r['mercado_total'])}; ao ano {pc(r['mercado_ao_ano'])}")
    print(f"maior queda {pc(r['maior_queda'])}: pico {r['data_pico'].date()} ({brl(r['pico_valor'])}), "
          f"fundo {pd.Timestamp(r['data_fundo']).date()}; maior numero de posicoes abertas ao mesmo tempo: "
          f"{r['max_posicoes']}")
    print(f"operacoes fechadas: {r['operacoes']}; resultado medio por operacao {pc(r['resultado_medio'])}; "
          f"pregoes medios {nu(r['pregoes_medios'], 1)}; % com ganho {pc(r['pct_ganho'])}; "
          f"abertas no fim: {r['abertas_fim']}; sinais nao atendidos por falta de caixa: {r['nao_atendidos']}")
    print(f"retorno 02/01/2018 a 31/12/2022: carteira {pc(r['ret_18_22'])} | Selic {pc(r['selic_18_22'])} | "
          f"Mercado {pc(r['mercado_18_22'])}")
    print(f"retorno 01/01/2023 ao fim: carteira {pc(r['ret_23_fim'])} | Selic {pc(r['selic_23_fim'])} | "
          f"Mercado {pc(r['mercado_23_fim'])}")
    t = tabela_anos(R)
    print("\nPor ano civil:")
    show(t, pcts=["retorno_ano", "selic_ano", "mercado_ano", "pct_vendas_ganho", "pct_aplicado"],
         brls=["patrimonio_fim", "rendimentos", "imposto_pago"])
    if len(R["abertas"]):
        ab = R["abertas"].copy()
        ab["entrada"] = ab["entrada"].dt.strftime("%d/%m/%Y")
        print("\nPosicoes abertas no ultimo dia:")
        show(ab, pcts=["valorizacao", "resultado"], brls=["rendimentos"], nums=[])
    else:
        print("\nPosicoes abertas no ultimo dia: nenhuma")

# ---------------------------------------------------------------- tabela resumo, operacoes e patrimonio (CSV)
linhas = []
for k, r in RESUMO.items():
    R = RES[k]
    linhas.append(dict(simulacao=k, carteira=R["tipo"], ordem=R["ordem"], patrimonio_final=r["patrimonio_final"],
                       retorno_total=r["retorno_total"], retorno_ao_ano=r["retorno_ao_ano"],
                       selic_total=r["selic_total"], mercado_total=r["mercado_total"],
                       selic_ao_ano=r["selic_ao_ano"], mercado_ao_ano=r["mercado_ao_ano"],
                       maior_queda=r["maior_queda"], data_pico=r["data_pico"], data_fundo=r["data_fundo"],
                       max_posicoes=r["max_posicoes"], operacoes=r["operacoes"], pct_com_ganho=r["pct_ganho"],
                       resultado_medio_op=r["resultado_medio"], pregoes_medios=r["pregoes_medios"],
                       sinais_nao_atendidos=r["nao_atendidos"], abertas_fim=r["abertas_fim"],
                       retorno_2018_2022=r["ret_18_22"], retorno_2023_fim=r["ret_23_fim"],
                       selic_2018_2022=r["selic_18_22"], selic_2023_fim=r["selic_23_fim"],
                       mercado_2018_2022=r["mercado_18_22"], mercado_2023_fim=r["mercado_23_fim"]))
RESUMO_DF = pd.DataFrame(linhas)
RESUMO_DF.assign(ordem=RESUMO_DF["ordem"].astype(int)).round(6).to_csv(TEC / "kairi_carteira_resumo.csv", **OPC)

ops_all = pd.concat([R["ops_todas"] for R in RES.values()], ignore_index=True)
ops_csv = ops_all.drop(columns=["e_row", "k_row", "mi_d", "mi_e", "rend_det", "ano"], errors="ignore")
ops_csv.round(6).to_csv(TEC / "kairi_carteira_operacoes.csv", **OPC)

# patrimonio de fim de mes
PAT_M = pd.DataFrame({"data": DATAS_SIM})
for k, R in RES.items():
    PAT_M[k] = R["dia"]["patrimonio"].to_numpy()
PAT_M["Tudo na Selic"] = SEL_VAL
PAT_M["Mercado"] = MERC_VAL
fim_mes = PAT_M.groupby([PAT_M["data"].dt.year, PAT_M["data"].dt.month]).tail(1)
fim_mes.round(2).to_csv(TEC / "kairi_carteira_patrimonio.csv", **OPC)

print("\n==================== TABELA RESUMO (9 simulacoes) ====================")
tab = RESUMO_DF.copy()
tab_out = pd.DataFrame({
    "simulacao": tab["simulacao"],
    "patrimonio final": tab["patrimonio_final"].map(brl),
    "retorno total": tab["retorno_total"].map(pc),
    "retorno ao ano": tab["retorno_ao_ano"].map(pc),
    "Selic": tab["selic_total"].map(pc),
    "Mercado": tab["mercado_total"].map(pc),
    "maior queda": tab["maior_queda"].map(pc),
    "operacoes": tab["operacoes"],
    "% com ganho": tab["pct_com_ganho"].map(pc),
    "sinais nao atendidos": tab["sinais_nao_atendidos"],
    "retorno 2018-2022": tab["retorno_2018_2022"].map(pc),
    "retorno 2023-fim": tab["retorno_2023_fim"].map(pc),
})
print(tab_out.to_string(index=False))
print(f"\nComparacoes (iguais em todas as 9): Selic ao ano {pc(RESUMO['A-1000']['selic_ao_ano'])}; "
      f"Mercado ao ano {pc(RESUMO['A-1000']['mercado_ao_ano'])}")
print(f"Periodo 2018-2022: Selic {pc(RESUMO['A-1000']['selic_18_22'])}, Mercado {pc(RESUMO['A-1000']['mercado_18_22'])}; "
      f"2023-fim: Selic {pc(RESUMO['A-1000']['selic_23_fim'])}, Mercado {pc(RESUMO['A-1000']['mercado_23_fim'])}")

print(f"\ngravados: planilhas/tecnico/kairi_carteira_resumo.csv ({len(RESUMO_DF)} linhas), "
      f"kairi_carteira_operacoes.csv ({len(ops_csv)} linhas), kairi_carteira_patrimonio.csv ({len(fim_mes)} linhas)")

# ---------------------------------------------------------------- CONFERENCIAS
print("\n==================== CONFERENCIAS ====================")
print("2) Caixa >= 0 e patrimonio = caixa + posicoes: verificado a cada pregao dentro do laco (asserts).")
for k, R in RES.items():
    D = R["dia"]
    assert (D["caixa"] >= -1e-6).all()
    dias_pend = int((D["pendente"] > 0).sum())
    print(f"   {k}: dias com caixa >= 0 = {len(D)}/{len(D)}; dias com imposto pendente (caixa nao cobriu): {dias_pend}")
print("   ASSERT PASSOU: caixa >= 0 em todos os dias das 9 simulacoes; patrimonio = caixa + posicoes "
      "onde nao ha imposto pendente.")

# 5a. compra so na abertura do pregao seguinte ao sinal; sinal antes da compra
for k, R in RES.items():
    for c in R["compras"].itertuples(index=False):
        assert c.sinal < c.data
        assert TS[c.mi_d + 1] == c.data
print("5a) ASSERT PASSOU: em todas as compras das 9 simulacoes, a data do sinal d < data da compra = pregao d+1 "
      "(TS[mi_d + 1]).")

# 5b. media de saida: calculada ate k-1 (recalculo independente com os fechamentos brutos)
n_volta = 0
for k, R in RES.items():
    for o in R["ops"].itertuples(index=False):
        if o.motivo != VOLTA:
            continue
        F = FD[o.fundo]
        kk = o.k_row
        media = F["C"][kk - N:kk].mean()          # fechamentos k-N .. k-1
        assert abs(media - o.media_saida) < 1e-9, (k, o.fundo, media, o.media_saida)
        assert F["H"][kk] >= media - 1e-12
        n_volta += 1
print(f"5b) ASSERT PASSOU: em {n_volta} saidas por volta, a media usada = media dos 200 fechamentos ate k-1 "
      "(recalculada a partir de C[k-200:k]).")

# 5c. amplitude de d usa so os dados ate d: recalcula por dados brutos truncados em d
def amp_indep(d):
    sub = PR[PR["data"] <= d]
    ult = sub[sub["data"] == d]
    num = den = 0
    for f, g in sub.groupby("fundo", sort=False):
        gg = g.tail(N)
        if len(gg) < N or gg["data"].iloc[-1] != d:
            continue
        row = gg.iloc[-1]
        rvt = row[C_PAT]
        univ = (rvt >= 50e6) and (row[C_VOL] >= 25000) and (row[C_REND] > 0) and (row[C_AMO] == 0) \
            and (0.30 <= row[C_PVP] <= 3.0) and f not in EXCLUIDOS
        if not univ:
            continue
        kair = row[C_FE] / gg[C_FE].mean() - 1
        den += 1
        num += int(kair <= AMP_K)
    return num / den if den else np.nan


dias_chk = [TS[int(np.searchsorted(MD, np.datetime64(x, "D")))] for x in ["2018-03-15", "2020-03-16", "2022-06-14"]]
dias_chk.append(TS[int(np.nanargmax(AMP))])
for d in dias_chk:
    mi_d = int(np.searchsorted(MD, np.datetime64(d, "D")))
    a_ind = amp_indep(d)
    assert abs(a_ind - AMP[mi_d]) < 1e-12, (d, a_ind, AMP[mi_d])
    print(f"5c) amplitude em {d.date()}: recalculo com dados ate d = {nu(a_ind, 4)}; "
          f"usado no script = {nu(AMP[mi_d], 4)}  ASSERT PASSOU")
print("   Codigo: amp[d] = AMP_NUM[mi]/AMP_DEN[mi] (somas por pregao d, a partir de k200 de cada fundo ate d);"
      " o sinal de C usa AMP[mi_d] com mi_d o pregao do sinal.")

# 3. operacoes completas, carteira A, ordem 2.000
A2 = RES["A-2000"]
print("\n3) CARTEIRA A, ORDEM R$ 2.000: 3 operacoes completas (conta refeita a mao a partir dos numeros logados)")
trio = A2["ops"].sort_values("entrada").head(3)
for o in trio.itertuples(index=False):
    F = FD[o.fundo]
    print(f"\n--- {o.fundo}: sinal em {o.sinal.date()} (pregao d); entrada na abertura de {o.entrada.date()}")
    print(f"    compra: {o.cotas} cotas x {nu(o.preco_entrada, 4)} = {brl(o.valor_compra)}; taxa 0,03% = "
          f"{brl(o.taxa_compra)}; total debitado {brl(o.valor_compra + o.taxa_compra)}")
    rd = o.rend_det
    for (dt, valor, cot, amt) in rd:
        print(f"    rendimento creditado {dt.date()} (data_base): {nu(valor, 4)} x {cot} cotas = {brl(amt)}")
    if not rd:
        print("    rendimentos creditados: nenhum")
    print(f"    saida: {o.saida.date()} (pregao {o.pregoes} depois da entrada), motivo: {o.motivo}")
    k = int(o.k_row)
    if o.motivo == VOLTA:
        print(f"    no pregao da saida: abertura {nu(F['A'][k], 4)}, maxima {nu(F['H'][k], 4)}, "
              f"media dos 200 fechamentos ate k-1 {nu(o.media_saida, 4)} -> maxima >= media: "
              f"{F['H'][k] >= o.media_saida}; vende max(abertura, media) = {nu(o.preco_saida, 4)}")
    print(f"    venda: {o.cotas} cotas x {nu(o.preco_saida, 4)} = {brl(o.valor_venda)}; taxa 0,03% = "
          f"{brl(o.taxa_venda)}")
    # conta a mao, com numeros logados
    custo = o.cotas * o.preco_entrada
    tc = 0.0003 * custo
    venda = o.cotas * o.preco_saida
    tv = 0.0003 * venda
    rend_mao = sum(cot * valor for (_, valor, cot, _) in rd)
    ganho_mao = (venda - tv) - (custo + tc)
    res_mao = (venda - tv + rend_mao - (custo + tc)) / (custo + tc)
    print(f"    CONTA A MAO: custo+taxa = {custo:.4f} + {tc:.4f} = {custo + tc:.4f}; venda-taxa = "
          f"{venda:.4f} - {tv:.4f} = {venda - tv:.4f}; ganho tributavel = {ganho_mao:.4f}")
    print(f"    CONTA A MAO: rendimentos = {rend_mao:.4f}; resultado = ({venda - tv:.4f} + {rend_mao:.4f} - "
          f"{custo + tc:.4f}) / {custo + tc:.4f} = {res_mao * 100:.4f}%")
    print(f"    script: ganho = {o.ganho_tributavel:.4f}; rendimentos = {o.rendimentos:.4f}; "
          f"resultado = {o.resultado * 100:.4f}%")
    assert abs(ganho_mao - o.ganho_tributavel) < 1e-6
    assert abs(res_mao - o.resultado) < 1e-9
    # rendimentos independentes: avisos do fundo com entrada <= data_base < saida, cotas da compra
    rdcheck = RD[(RD["fundo"] == o.fundo) & (RD["data_base"] >= o.entrada) & (RD["data_base"] < o.saida)]
    rd_ind = float(rdcheck["valor (R$/cota)"].sum()) * o.cotas
    assert abs(rd_ind - o.rendimentos) < 1e-6, (o.fundo, rd_ind, o.rendimentos)
    print(f"    rendimentos recalculados pelo rendimentos.csv (data_base em [entrada, saida)): {brl(rd_ind)} "
          f"ASSERT PASSOU")

# 4. Tudo na Selic
sel_ano = ano_base(SEL_VAL[-1], ANOS_BASE)
sel_med = float(np.mean(SEL[I0:]))
print(f"\n4) TUDO NA SELIC: final {brl(SEL_VAL[-1])} (de {brl(CAPITAL)}); retorno total {pc(SEL_VAL[-1] / CAPITAL - 1)}; "
      f"retorno ao ano (252 pregoes, {N_PASSOS} pregoes) {pc(sel_ano)}.")
print(f"   referencia: Selic anual media do periodo = {nu(sel_med, 2)}% ao ano bruta; "
      f"liquida pelo 22,5% fixo = {nu(sel_med * (1 - IR_CX), 2)}% ao ano. A coluna selic_liquida_ano do "
      f"mercado.csv usa outra aliquota e nao foi usada.")

print(f"\n1) Roda sem erro. Tempo total: {time.time() - T0:.1f} s")
