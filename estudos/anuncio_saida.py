"""Estudo: o que acontece depois de um fato relevante de anúncio, com saída por rendimento, notícia ou prazo.

Entrada: pregão seguinte ao fato relevante (i0), a abertura. Saídas, na ordem, no primeiro pregão em que valer:
  0. fundo saiu da bolsa: preço (F) NaN do pregão k até k+20 (ou até o fim dos dados); vende no último preço anterior;
  1. rendimento caiu: rendimento conhecido no pregão k 10% ou mais abaixo do maior desde a entrada;
  2. fundo declarou redução de rendimento (fato relevante interno);
  3. prazo de 252 pregões (fechamento; sem preço no dia, usa o último anterior).
Só com o que era conhecido no dia (rendimento via P.div, fatos classificados).
Perfil pelo patrimônio líquido no pregão de entrada: AGRESSIVO 50-100 mi, MODERADO 100-400 mi, fora os demais.
Sem piso fixo de liquidez: a ordem pode ser até 2% do valor negociado por dia (P.vol60); ordem máxima abaixo de R$ 200 fica de fora.
Tabelas (grupo TODOS, pl >= 50 mi e pvp entre 0,30 e 0,90) saem no terminal e em dados/secao_1_1e.md.

Uso: PYTHONPATH=. .venv/bin/python estudos/anuncio_saida.py
"""
import warnings

import duckdb
import numpy as np
import pandas as pd

from estudos import desconto as E
from estudos import fatos
from estudos.conservador import rendimentos, selic_liquida
from fii import config, fnet

warnings.filterwarnings("ignore")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

INICIO = pd.Timestamp("2018-01-01")
PRAZO = 252
SEM_PRECO = 21  # pregões seguidos sem preço (k até k+20) para considerar que o fundo saiu da bolsa
QUEDA = 0.90
SUBIDA = 1.05
CUSTO = 0.0006  # 0,03% na compra + 0,03% na venda
IMPOSTO = 0.20
ORDEM_PCT = 0.02  # ordem máxima = 2% do valor negociado por dia (média de 60 pregões até a véspera)
ORDEM_MIN = 200  # entrada descartada se a ordem máxima ficar abaixo de R$ 200
REGUA_FATOR = 0.825  # Selic líquida = Selic x 0,825 (imposto de 17,5%)
REGUA_MARGEM = 3.0  # pontos percentuais ao ano acima da Selic líquida
PL_MIN = 50e6
PVP_MIN, PVP_MAX = 0.30, 0.90
ORIGEM = ["1A venda", "1A multa", "1B", "1C"]
MOTIVOS_ATE_K = ("prazo de 252 pregões", "em aberto")
SAIU = "fundo saiu da bolsa"
CACHE = config.DADOS / "fatos_sem_piso.parquet"
PERFIS_PVP = ["Agressivo 0,30 a 0,60", "Faixa a decidir 0,60 a 0,75", "Moderado 0,75 a 0,90"]
FAIXAS = [(200, 400, "200 a 400"), (400, 600, "400 a 600"), (600, 800, "600 a 800"), (800, 1000, "800 a 1.000"),
          (1000, 1200, "1.000 a 1.200"), (1200, 1400, "1.200 a 1.400"), (1400, 1600, "1.400 a 1.600"),
          (1600, 1800, "1.600 a 1.800"), (1800, 2000, "1.800 a 2.000"), (2000, 4000, "2.000 a 4.000"),
          (4000, np.inf, "4.000 ou mais")]
LIQ = [("ordem de 200 a 500", 200, 500), ("ordem de 500 a 4.000", 500, 4000), ("ordem de 4.000 ou mais", 4000, np.inf)]
COLUNAS = ["origem", "ticker", "entrada", "saida", "preco_entrada", "preco_saida", "div0", "maior", "motivo", "pregoes",
           "valorizacao", "rendimento", "total", "liquido", "selic", "subiu", "aumento_max", "aberta", "perfil", "pl", "pvp",
           "vol60", "ordem_max", "dy", "regua", "passa_regua"]
RES = ["Entradas", "Fechadas", "Em aberto", "Pregões (média, fechadas)", "Cota subiu (% das fechadas)",
       "Valorização média (fechadas)", "Rendimento médio (fechadas)", "Valorização + rendimento (fechadas)",
       "Depois de custos e imposto (fechadas)", "Selic líquida no período (fechadas)",
       "Ganharam da Selic líquida (% das fechadas, líquido > selic)",
       "Em aberto: valorização + rendimento (média)", "Em aberto: Selic líquida (média)"]


def grupos(f):
    m_venda = ((f["tipo"] == "venda_com_ganho") & (f["sentido"] == "alta")).to_numpy()
    m_multa = ((f["tipo"] == "recebimento") & (f["sentido"] == "alta")).to_numpy()
    m_loc = ((f["tipo"] == "locacao_nova") & (f["sentido"] == "alta")).to_numpy()
    m_aum = (f["imp_direcao"] == 1).to_numpy()
    todos = m_venda | m_multa | m_loc | m_aum
    g = f.assign(origem=np.select([m_venda, m_multa, m_loc, m_aum], ORIGEM, default=""))
    return {
        "1A venda com lucro": g[m_venda],
        "1A multa ou indenização": g[m_multa],
        "1B locação nova": g[m_loc],
        "1C aumento declarado": g[m_aum],
        "TODOS": g[todos],
    }


def perfil_de(pl):
    if np.isnan(pl):
        return "sem patrimônio conhecido (fora)"
    if pl < PL_MIN:
        return "pequeno demais (fora)"
    if pl < 100e6:
        return "AGRESSIVO"
    if pl < 400e6:
        return "MODERADO"
    return "conservador (fora)"


def perfil_pvp(x):
    if x < 0.60:
        return PERFIS_PVP[0]
    if x < 0.75:
        return PERFIS_PVP[1]
    return PERFIS_PVP[2]


def anuncios_sem_piso(P, con, cf):
    """Fatos relevantes de papel na bolsa, sem filtro de liquidez. Cache em dados/fatos_sem_piso.parquet."""
    if CACHE.exists():
        print(f"Lendo cache: {CACHE}")
        return pd.read_parquet(CACHE)
    f = fatos.carregar(con, cf).dropna(subset=["ticker"]).copy()
    f["i0"] = [P.pregao_seguinte(q) for q in f["quando"]]
    f = f[f["i0"].notna()]
    f = f[f["i0"] < len(P.datas) - 1]
    f = f[f["ticker"].isin(list(P.col))].reset_index(drop=True)
    f["i0"] = f["i0"].astype(int)
    f = f.sort_values("quando").reset_index(drop=True)
    # mesmo fundo, mesmo tipo, em menos de 10 pregões: é a mesma notícia repetida; vale a primeira
    rep = f.groupby(["ticker", "tipo"])["i0"].diff()
    f["repetido"] = (rep.notna() & (rep <= 10)).to_numpy()
    f.to_parquet(CACHE)
    print(f"Lista sem piso gravada em {CACHE}")
    return f


def ultimo_preco(F, k):
    """Índice do último preço (F) não NaN anterior a k, ou None."""
    v = np.flatnonzero(~np.isnan(F[:k]))
    return int(v[-1]) if len(v) else None


def saida(P, j, i, ruins):
    """Primeiro pregão k > i em que uma das saídas vale. Devolve (k, motivo, preço, maior rendimento visto)."""
    N = len(P.datas)
    F = P.F[:, j]
    div0 = P.div[i, j]
    maior = div0
    for k in range(i + 1, N):
        d = P.div[k, j]
        if d > maior:  # NaN não entra
            maior = d
        if np.isnan(F[k]) and np.isnan(F[k:min(k + SEM_PRECO, N)]).all():  # sem preço por 21 pregões: saiu da bolsa
            m = ultimo_preco(F, k)
            return m, SAIU, F[m], maior
        a = P.A[k, j]
        if not np.isnan(a):
            if d <= QUEDA * maior:  # NaN não dispara
                return k, "rendimento caiu", a, maior
            if k in ruins:
                return k, "fundo declarou redução", a, maior
        if k - i >= PRAZO:
            sai = F[k] if not np.isnan(F[k]) else F[ultimo_preco(F, k)]
            return k, "prazo de 252 pregões", sai, maior
    ult = F[~np.isnan(F)]
    return N - 1, "em aberto", ult[-1], maior


def simular(P, linhas):
    ruins = {tk: set(v) for tk, v in P.ruim.items()}
    lin = linhas.assign(i=linhas["i0"].astype(int)).sort_values(["i", "ticker"], kind="stable")
    ocupado_ate = {}
    ops = []
    for r in lin.itertuples(index=False):
        tk, i = r.ticker, r.i
        j = P.col[tk]
        if P.datas[i] < INICIO or i < ocupado_ate.get(tk, -1):  # ainda com operação aberta nesse fundo
            continue
        ent, div0 = P.A[i, j], P.div[i, j]
        if np.isnan(ent) or not P.negociou[i, j] or np.isnan(div0) or div0 <= 0:
            continue
        vol60 = P.vol60[i, j]
        ordem = ORDEM_PCT * vol60
        if np.isnan(vol60) or ordem < ORDEM_MIN:  # sem volume conhecido ou ordem pequena demais: não entra
            continue
        k, motivo, sai, maior = saida(P, j, i, ruins.get(tk, set()))
        ocupado_ate[tk] = k
        fim = k if motivo in MOTIVOS_ATE_K else k - 1
        valorizacao = sai / ent - 1
        rend = rendimentos(P, tk, i, fim) / ent
        total = valorizacao + rend
        liquido = total - CUSTO - IMPOSTO * max(valorizacao - CUSTO, 0)
        pl = P.pl[i, j]
        dy = div0 * 12 / ent * 100
        regua = P.selic[i] * REGUA_FATOR + REGUA_MARGEM
        ops.append({"origem": r.origem, "ticker": tk, "entrada": P.datas[i], "saida": P.datas[k],
                    "preco_entrada": ent, "preco_saida": sai, "div0": div0, "maior": maior, "motivo": motivo,
                    "pregoes": k - i, "valorizacao": valorizacao, "rendimento": rend, "total": total, "liquido": liquido,
                    "selic": selic_liquida(P, i, k), "subiu": maior >= SUBIDA * div0, "aumento_max": maior / div0 - 1,
                    "aberta": motivo == "em aberto", "perfil": perfil_de(pl), "pl": pl, "pvp": ent / P.vp[i, j],
                    "vol60": vol60, "ordem_max": ordem, "dy": dy, "regua": regua, "passa_regua": bool(dy >= regua)})
    df = pd.DataFrame(ops, columns=COLUNAS)
    return df.astype({"aberta": bool, "subiu": bool, "pl": float, "pvp": float, "valorizacao": float,
                      "rendimento": float, "total": float, "liquido": float, "selic": float, "vol60": float,
                      "ordem_max": float, "dy": float, "regua": float, "passa_regua": bool})


# ---------- formatação ----------

def pct(v, sinal=True):
    if pd.isna(v):
        return "—"
    s = f"{v * 100:+.1f}" if sinal else f"{v * 100:.1f}"
    return s.replace("-", "−").replace(".", ",") + "%"


def num(v, casas=1):
    return "—" if pd.isna(v) else f"{v:.{casas}f}".replace(".", ",")


def inteiro(v):
    return "—" if pd.isna(v) else f"{v:,.0f}".replace(",", ".")


# ---------- tabelas ----------

def media(x, col):
    return float(x[col].mean()) if len(x) else np.nan


def metricas(d):
    fe, ab = d[~d["aberta"]], d[d["aberta"]]
    n = len(fe)
    return {
        "entradas": len(d), "fechadas": n, "abertas": len(ab),
        "pregoes": media(fe, "pregoes"),
        "subiu": (fe["valorizacao"] > 0).sum() / n if n else np.nan,
        "valorizacao": media(fe, "valorizacao"), "rendimento": media(fe, "rendimento"),
        "total": media(fe, "total"), "liquido": media(fe, "liquido"), "selic": media(fe, "selic"),
        "ganhou": (fe["liquido"] > fe["selic"]).sum() / n if n else np.nan,
        "ab_total": media(ab, "total"), "ab_selic": media(ab, "selic"),
    }


def linha(d):
    x = metricas(d)
    return [str(x["entradas"]), str(x["fechadas"]), str(x["abertas"]), num(x["pregoes"]),
            pct(x["subiu"], False), pct(x["valorizacao"]), pct(x["rendimento"]), pct(x["total"]),
            pct(x["liquido"]), pct(x["selic"]), pct(x["ganhou"], False), pct(x["ab_total"]), pct(x["ab_selic"])]


def cortes_a(m):
    out = [((rot,), m[(m["ordem_max"] >= lo) & (m["ordem_max"] < hi)]) for lo, hi, rot in FAIXAS]
    out.append((("Ordem de 500 ou mais",), m[m["ordem_max"] >= 500]))
    out.append((("Todas",), m))
    return out


def cortes_bc(m):
    out = []
    for perfil in PERFIS_PVP:
        mp = m[m["perfil_pvp"] == perfil]
        for rot, lo, hi in LIQ:
            out.append(((perfil, rot), mp[(mp["ordem_max"] >= lo) & (mp["ordem_max"] < hi)]))
        out.append(((perfil, "Total"), mp))
    return out


def tabela_resultados(cortes, rotulos):
    return rotulos + RES, [list(rot) + linha(d) for rot, d in cortes]


def tabela_abertas(m):
    ab = m[m["aberta"]].sort_values("entrada")
    header = ["Ticker", "Entrada", "Preço de entrada", "Preço atual", "Pregões", "Valorização", "Rendimento",
              "PVP na entrada", "Ordem máx. (R$)", "Perfil"]
    rows = [[r.ticker, f"{r.entrada:%d/%m/%Y}", num(r.preco_entrada, 4), num(r.preco_saida, 4), str(r.pregoes),
             pct(r.valorizacao), pct(r.rendimento), num(r.pvp, 2), inteiro(r.ordem_max), r.perfil_pvp]
            for r in ab.itertuples(index=False)]
    return header, rows


def md_tabela(titulo, header, rows):
    linhas = [f"**{titulo}**", "", "| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    linhas += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(linhas)


def checar_extremos(nome, cortes):
    """Células com médias absurdas: mostra as 5 operações mais extremas. Devolve quantas células alertaram."""
    alertas = 0
    for rot, d in cortes:
        x = metricas(d)
        if x["fechadas"] == 0:
            continue
        fe = d[~d["aberta"]]
        cols = ["ticker", "entrada", "pregoes", "preco_entrada", "preco_saida", "valorizacao", "rendimento", "ordem_max"]
        if x["valorizacao"] > 1.0 or x["valorizacao"] < -0.6:
            alertas += 1
            sel = fe.nlargest(5, "valorizacao") if x["valorizacao"] > 1.0 else fe.nsmallest(5, "valorizacao")
            print(f"  ALERTA {nome} | {' / '.join(rot)}: valorização média {pct(x['valorizacao'])}; 5 mais extremas:")
            print(sel[cols].to_string(index=False))
        if x["rendimento"] > 0.5:
            alertas += 1
            print(f"  ALERTA {nome} | {' / '.join(rot)}: rendimento médio {pct(x['rendimento'])}; 5 mais extremas:")
            print(fe.nlargest(5, "rendimento")[cols].to_string(index=False))
    return alertas


def main():
    P = E.preparar()
    con = duckdb.connect(str(config.BANCO), read_only=True)
    cf = duckdb.connect(str(fnet.BANCO), read_only=True)
    f = anuncios_sem_piso(P, con, cf)
    validos = [t for t in P.col if t in P.avisos]
    f = f[~f["repetido"] & f["ticker"].isin(validos)]
    res = {}
    for nome, linhas in grupos(f).items():
        res[nome] = simular(P, linhas)
    todos = res["TODOS"]
    print("Operações por grupo (depois da ordem mínima de R$ 200): " + " | ".join(f"{k}: {len(v)}" for k, v in res.items()))

    # filtro do grupo TODOS: pl e pvp
    total = len(todos)
    pl_ok = todos["pl"].notna() & (todos["pl"] >= PL_MIN)
    pvp_ok = todos["pvp"].between(PVP_MIN, PVP_MAX)
    fora_pl = int((~pl_ok).sum())
    fora_pvp = int((pl_ok & ~pvp_ok).sum())
    m = todos[pl_ok & pvp_ok].assign(perfil_pvp=lambda d: d["pvp"].map(perfil_pvp))
    m_reg = m[m["passa_regua"]]
    print(f"\nGrupo TODOS: {total} operações | fora por pl (NaN ou < 50 mi): {fora_pl} | "
          f"fora por pvp (NaN ou fora de 0,30 a 0,90, com pl ok): {fora_pvp} | restam: {len(m)}")

    cortes = {"A": cortes_a(m), "B": cortes_bc(m), "C": cortes_bc(m_reg)}
    tab = {
        "A": ("Tabela A — por faixa de ordem", tabela_resultados(cortes["A"], ["Faixa de ordem"])),
        "B": ("Tabela B — por perfil (pvp) e grupo de liquidez", tabela_resultados(cortes["B"], ["Perfil", "Grupo de liquidez"])),
        "C": ("Tabela C — por perfil (pvp) e grupo de liquidez, só operações que passam na régua",
              tabela_resultados(cortes["C"], ["Perfil", "Grupo de liquidez"])),
        "D": ("Tabela D — operações em aberto", tabela_abertas(m)),
    }
    for chave, (titulo, (header, rows)) in tab.items():
        print(f"\n=== {titulo} ===")
        print(pd.DataFrame(rows, columns=header).to_string(index=False))
    md = "\n\n".join(md_tabela(titulo, header, rows) for titulo, (header, rows) in tab.values())
    (config.RAIZ / "dados" / "secao_1_1e.md").write_text(md + "\n", encoding="utf-8")

    print("\n=== CONFERÊNCIAS ===")
    print("1. Roda sem erro: sim")
    lidas = len(pd.read_parquet(CACHE))
    print(f"2. Linhas em dados/fatos_sem_piso.parquet: {lidas} | operações do grupo TODOS agora: {total} (antes eram 287)")
    cels_a = cortes["A"]
    soma_faixas = sum(len(d) for _, d in cels_a[:len(FAIXAS)])
    ok_a = soma_faixas == len(m)
    todas_linhas_ok = all(metricas(d)["fechadas"] + metricas(d)["abertas"] == metricas(d)["entradas"]
                          for k in ("A", "B", "C") for _, d in cortes[k])
    print(f"3. Tabela A: soma das Entradas das 11 faixas = {soma_faixas}, linha Todas = {len(m)}: {'OK' if ok_a else 'FALHOU'} | "
          f"Fechadas + Em aberto = Entradas em todas as linhas das tabelas A, B e C: {'OK' if todas_linhas_ok else 'FALHOU'}")
    abertas_252 = int((todos["aberta"] & (todos["pregoes"] >= PRAZO)).sum())
    print(f"4. Operações em aberto com {PRAZO} pregões ou mais (grupo TODOS, sem filtro): {abertas_252} (tem que ser 0)")
    ge4000 = int((todos["ordem_max"] >= 4000).sum())
    print(f"5. Operações do grupo TODOS com ordem_max >= 4.000: {ge4000} (comparar com as 287 antigas, que usavam piso de R$ 200 mil, "
          f"o que dá ordem >= 4.000 por construção)")
    print("6. Células com médias absurdas (valorização média > +100% ou < −60%; rendimento médio > 50%):")
    alertas = checar_extremos("A", cortes["A"]) + checar_extremos("B", cortes["B"]) + checar_extremos("C", cortes["C"])
    if alertas == 0:
        print("  nenhuma")

    todos.round(4).to_csv(config.RAIZ / "docs" / "anuncio_saida_operacoes.csv", index=False)
    print(f"\nOperações do grupo TODOS salvas em docs/anuncio_saida_operacoes.csv ({len(todos)} linhas)")
    print("Tabelas salvas em dados/secao_1_1e.md")


if __name__ == "__main__":
    main()
