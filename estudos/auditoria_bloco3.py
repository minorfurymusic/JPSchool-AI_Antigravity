"""Auditoria, bloco 3: queda sem notícia contra queda com fato negativo (itens 6a, 6b, 6c, 6d).

Lê só planilhas/ (kairi_ordens.csv, anuncios.csv, cdi.csv, tecnico/fatos_textos.csv.gz).
Escreve planilhas/auditoria_bloco3_*.csv. Se receber um caminho como argumento, grava ali também
as tabelas em markdown (o que é impresso na tela).

AVISO que vale para todas as tabelas: a classificação dos fatos (tipo e sentido) foi feita por
palavras (fii/classificar.py) e erra. A medida do erro está na amostra lida à mão (seção 0).

Rodar:  cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/auditoria_bloco3.py [saida.md]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
PL = RAIZ / "planilhas"
SEMENTE_AMOSTRA = 2024
SEMENTE_BOOT = 7
N_BOOT = 10000
AVISO = ("Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; "
         "ver a medida do erro na seção 0.")

MD: list[str] = []


def emit(s: str = "") -> None:
    print(s)
    MD.append(s)


def f(x, d=1) -> str:
    """Número no formato brasileiro (vírgula decimal); vazio vira traço."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabela_md(df: pd.DataFrame, fmt: dict | None = None) -> str:
    fmt = fmt or {}
    cols = list(df.columns)
    linhas = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cel = []
        for c in cols:
            v = r[c]
            if c in fmt and not isinstance(v, str):
                cel.append(f(v, fmt[c]))
            elif isinstance(v, (float, np.floating)):
                cel.append(f(v, 1))
            else:
                cel.append(str(v))
        linhas.append("| " + " | ".join(cel) + " |")
    return "\n".join(linhas)


def salvar(df: pd.DataFrame, nome: str) -> None:
    df.to_csv(PL / f"auditoria_bloco3_{nome}.csv", sep=";", decimal=",", encoding="utf-8-sig", index=False)


# ---------------------------------------------------------------- dados
def carregar():
    o = pd.read_csv(PL / "kairi_ordens.csv", sep=";", decimal=",", encoding="utf-8-sig")
    a = pd.read_csv(PL / "anuncios.csv", sep=";", decimal=",", encoding="utf-8-sig")
    t = pd.read_csv(PL / "tecnico" / "fatos_textos.csv.gz", sep=";", encoding="utf-8-sig")
    t.columns = ["id", "fundo", "data", "tipo", "texto"]
    c = pd.read_csv(PL / "cdi.csv", sep=";", decimal=",", encoding="utf-8-sig")
    c["data"] = pd.to_datetime(c["data"], format="%d/%m/%Y")
    a["data"] = pd.to_datetime(a["data_anuncio"].str[:10], format="%d/%m/%Y")
    a["rep"] = a["repetido (1/0)"].astype(int)
    a["cont"] = a["continuacao (1/0)"].astype(int)
    a = a.merge(t[["id", "texto"]], on="id", how="left")
    for col in ["Data do sinal", "Data de entrada", "Data de saída (ou do último preço)"]:
        o[col] = pd.to_datetime(o[col], format="%d/%m/%Y")
    o = o.rename(columns={"Data do sinal": "sinal", "Data de entrada": "entrada",
                          "Data de saída (ou do último preço)": "saida", "Valor da ordem (R$)": "valor",
                          "Resultado (R$)": "res_rs", "Resultado (%)": "res_col",
                          "Motivo da saída": "motivo", "Fundos caídos no dia (%)": "caidos",
                          "Maior queda abaixo da entrada (%)": "maxqueda", "Dias corridos": "dias"})
    return o, a, c


# ---------------------------------------------------------------- régua CDI
IOF = [96, 93, 90, 86, 83, 80, 76, 73, 70, 66, 63, 60, 56, 53, 50, 46, 43, 40, 36, 33, 30, 26, 23, 20, 16, 13, 10, 6, 3]


def ir_aliquota(dias: int) -> float:
    return 0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15


class Regua:
    def __init__(self, c: pd.DataFrame):
        self.datas = c["data"].values
        self.ind = c["indice_105_do_cdi"].values

    def indice(self, d: pd.Timestamp) -> float:
        i = np.searchsorted(self.datas, np.datetime64(d), side="right") - 1  # último dia útil <= d
        return float(self.ind[i])

    def bruto(self, d0, d1) -> float:
        return self.indice(d1) / self.indice(d0) - 1

    def liquido(self, v, d0, d1) -> float:
        """Rendimento líquido (R$) de V aplicado em d0 e resgatado em d1: IOF (<30 dias) e depois IR regressivo."""
        rend = v * self.bruto(d0, d1)
        dias = (d1 - d0).days
        if rend > 0 and 1 <= dias <= 29:
            rend *= 1 - IOF[dias - 1] / 100
        if rend > 0:
            rend *= 1 - ir_aliquota(dias)
        return rend


# ---------------------------------------------------------------- amostra lida à mão (veredito do analista)
# Sorteio: RandomState(2024).choice(n, 20, replace=False) sobre os fatos (sem repetidos/continuações) com o
# sentido pedido, ordenados por id. Veredito dado por leitura do texto (só os 3.000 primeiros caracteres existem).
VEREDITOS = {
    "queda": {
        105619: ("ok", "fundo recebeu notificações de rescisão de módulos de galpão"),
        740634: ("mal classificado", "é a aprovação de nova emissão de cotas; nada sobre redução de rendimento"),
        84199: ("ok", "recuperação judicial do grupo que é inquilino (Leader)"),
        709629: ("mal classificado", "aprovação da 10ª emissão de cotas"),
        433490: ("mal classificado", "venda de parte de um portfólio de imóveis; o texto lido não fala em redução de rendimento"),
        611047: ("ok", "inadimplência do aluguel de um galpão"),
        13748: ("duvidoso", "fundo esclarece sua relação com grupo em recuperação judicial (comprou unidades); efeito no rendimento não aparece"),
        705148: ("mal classificado", "escritura de venda de um módulo (preço R$ 6,6 mi); não é redução de rendimento"),
        36595: ("ok", "inadimplemento do aluguel por um inquilino"),
        690753: ("mal classificado", "oferta de novas cotas (a palavra 'diminuída' é da regra da distribuição parcial)"),
        332456: ("ok", "inquilino pediu rescisão do contrato"),
        161443: ("mal classificado", "oferta de novas cotas (mesma palavra 'diminuída' da distribuição parcial)"),
        250032: ("mal classificado", "aprovação da 2ª emissão de cotas"),
        549130: ("mal classificado", "aprovação da 10ª emissão de cotas"),
        55240: ("ok", "rescisão antecipada de locação (com multa a favor do fundo, mas o inquilino sai)"),
        113269: ("ok", "notificação de rescisão antecipada do contrato de locação"),
        92276: ("ok", "devolução de andares reduz a área locada; fundo diz que impacta rendimentos em cerca de 15%"),
        353068: ("duvidoso", "troca de cartas sobre rescisão/devolução parcial de área; não fica claro se o inquilino sairá"),
        124446: ("mal classificado", "aprovação da 2ª emissão de cotas"),
        467813: ("mal classificado", "aprovação da 2ª emissão de cotas"),
    },
    "alta": {
        783410: ("mal classificado", "negócio entre sócios da gestora (compra de participação); não muda o fundo"),
        84073: ("duvidoso", "fundo 'ainda está recebendo a multa'; texto lido é só um trecho, efeito incerto"),
        383342: ("ok", "novo contrato de locação"),
        34946: ("mal classificado", "troca de escriturador; o texto diz que não há acréscimo de custos"),
        14339: ("ok", "distribuição extraordinária de rendimentos"),
        501362: ("mal classificado", "tabela da carteira de CRI do fundo ('alienação fiduciária' é garantia, não venda)"),
        373778: ("ok", "novo contrato de locação com petroleira"),
        1221531: ("duvidoso", "venda de participação em parcelas; não diz se há ganho nem efeito no rendimento"),
        80009: ("mal classificado", "aprovação da 2ª emissão de cotas"),
        226179: ("ok", "venda de dois imóveis, uma delas 45,9% acima do valor patrimonial"),
        1035450: ("mal classificado", "aquisição de fazenda (compra, não venda nem aumento de rendimento)"),
        332807: ("ok", "novo contrato de locação de vários módulos"),
        322042: ("duvidoso", "venda de módulos; o texto lido não mostra o ganho"),
        32747: ("duvidoso", "só recebeu proposta vinculante de compra de imóvel; negócio ainda não fechado"),
        355168: ("mal classificado", "escritura de compra (aquisição de 50% de condomínio), não venda"),
        791138: ("ok", "venda concluída e preço recebido; gestão fala em geração de valor ao investidor"),
        47068: ("mal classificado", "aprovação da 4ª emissão de cotas"),
        741826: ("duvidoso", "venda de 75% de uma empresa que tem parte de um edifício; efeito no rendimento incerto"),
        188347: ("duvidoso", "venda de conjuntos por R$ 22 mi; texto lido não mostra ganho nem efeito no rendimento"),
        1363359: ("ok", "venda com ganho estimado de R$ 23,5 mi (R$ 0,35 por cota)"),
    },
}


def amostra_leitura(a: pd.DataFrame) -> pd.DataFrame:
    v = a[(a.rep == 0) & (a.cont == 0)]
    linhas = []
    for sent in ["queda", "alta"]:
        g = v[v.sentido == sent].sort_values("id").reset_index(drop=True)
        rs = np.random.RandomState(SEMENTE_AMOSTRA)
        idx = rs.choice(len(g), 20, replace=False)
        ids = [int(g.loc[i, "id"]) for i in idx]
        assert set(ids) == set(VEREDITOS[sent]), f"amostra {sent} mudou: o veredito lido à mão não vale mais"
        for i in idx:
            r = g.loc[i]
            ver, motivo = VEREDITOS[sent][int(r["id"])]
            linhas.append({"sentido sorteado": sent, "id": int(r["id"]), "fundo": r["fundo"],
                           "data": r["data"].strftime("%d/%m/%Y"), "tipo (palavras)": r["tipo"],
                           "veredito da leitura": ver, "motivo": motivo})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- medidas por grupo
def medidas(d: pd.DataFrame) -> dict:
    n = len(d)
    if n == 0:
        return {"ordens": 0}
    return {
        "ordens": n,
        "média (%)": d["res_pct"].mean(),
        "mediana (%)": d["res_pct"].median(),
        "% positivas": 100 * (d["res_rs"] > 0).mean(),
        "excesso médio s/ 105% CDI bruto (p.p.)": d["exc_pp"].mean(),
        "excesso médio s/ 105% CDI líquido (p.p.)": d["exc_liq_pp"].mean(),
        "pior ordem (%)": d["res_pct"].min(),
        "maior queda média abaixo da entrada (%)": d["maxqueda"].mean(),
        "dias corridos médios": d["dias"].mean(),
        "% saiu por prazo": 100 * (d["motivo"] == "prazo").mean(),
        "% em aberto": 100 * (d["motivo"] == "em aberto").mean(),
    }


PERIODOS = [("escolha 2018-2022", lambda d: d["ano"] <= 2022), ("conferência 2023-2026", lambda d: d["ano"] >= 2023),
            ("total", lambda d: d["ano"] >= 0)]
GRUPOS = [("0", lambda s: s == 0), ("1", lambda s: s == 1), ("2 ou mais", lambda s: s >= 2)]


def tabela_grupos(d: pd.DataFrame, col: str, rotulo: dict) -> pd.DataFrame:
    linhas = []
    for cart in ["A", "B", "C"]:
        dc = d[d["Carteira"] == cart]
        for pn, pf in PERIODOS:
            dp = dc[pf(dc)]
            for gn, gf in GRUPOS:
                m = medidas(dp[gf(dp[col])])
                linhas.append({**rotulo, "carteira": cart, "período": pn, "grupo": gn, **m})
    return pd.DataFrame(linhas)


def boot_dif(a: np.ndarray, b: np.ndarray, seed: int = SEMENTE_BOOT):
    rng = np.random.default_rng(seed)
    ma = rng.choice(a, (N_BOOT, len(a))).mean(axis=1)
    mb = rng.choice(b, (N_BOOT, len(b))).mean(axis=1)
    dif = ma - mb
    return np.percentile(dif, 2.5), np.percentile(dif, 97.5)


def teste_sem_com(d: pd.DataFrame, col: str, rotulo: dict) -> pd.DataFrame:
    """Sem notícia (0) contra com fato (1 ou mais): Mann-Whitney e diferença de médias com IC95 por bootstrap."""
    linhas = []
    for cart in ["A", "B", "C"]:
        dc = d[d["Carteira"] == cart]
        for pn, pf in PERIODOS:
            dp = dc[pf(dc)]
            sem, com = dp[dp[col] == 0], dp[dp[col] >= 1]
            for medida, nome in [("res_pct", "resultado (%)"), ("exc_pp", "excesso s/ 105% CDI bruto (p.p.)")]:
                r = {**rotulo, "carteira": cart, "período": pn, "medida": nome, "ordens sem": len(sem), "ordens com": len(com),
                     "média sem": np.nan, "média com": np.nan, "diferença (sem − com)": np.nan, "IC95 inferior": np.nan,
                     "IC95 superior": np.nan, "p Mann-Whitney": np.nan}
                if len(sem) >= 5 and len(com) >= 5:
                    x, y = sem[medida].values, com[medida].values
                    lo, hi = boot_dif(x, y)
                    r.update({"média sem": x.mean(), "média com": y.mean(), "diferença (sem − com)": x.mean() - y.mean(),
                              "IC95 inferior": lo, "IC95 superior": hi,
                              "p Mann-Whitney": stats.mannwhitneyu(x, y, alternative="two-sided").pvalue})
                linhas.append(r)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- principal
def main() -> None:
    o, a, c = carregar()
    reg = Regua(c)

    emit("# Bloco 3 (saída do programa): queda sem notícia contra queda com fato negativo")
    emit()
    emit(AVISO)
    emit()

    # ---------- 0. fatos usados e amostra lida
    n_tot = len(a)
    n_rep, n_cont = int((a.rep == 1).sum()), int((a.cont == 1).sum())
    n_ambos = int(((a.rep == 1) & (a.cont == 1)).sum())
    fatos = a[(a.rep == 0) & (a.cont == 0)].copy()
    emit("## 0. Fatos usados e erro da classificação")
    emit()
    ign = pd.DataFrame([
        {"grupo de fatos": "todos os fatos da planilha anuncios.csv", "fatos": n_tot},
        {"grupo de fatos": "ignorados por serem repetidos (repetido = 1)", "fatos": n_rep},
        {"grupo de fatos": "ignorados por serem continuação (continuacao = 1)", "fatos": n_cont},
        {"grupo de fatos": "ignorados que são os dois ao mesmo tempo", "fatos": n_ambos},
        {"grupo de fatos": "total ignorado (repetido ou continuação)", "fatos": n_tot - len(fatos)},
        {"grupo de fatos": "fatos contados", "fatos": len(fatos)},
        {"grupo de fatos": "  dos contados: sentido queda", "fatos": int((fatos.sentido == "queda").sum())},
        {"grupo de fatos": "  dos contados: sentido alta", "fatos": int((fatos.sentido == "alta").sum())},
        {"grupo de fatos": "  dos contados: tipo rendimento_reducao, saida_inquilino ou venda_com_perda",
         "fatos": int(fatos.tipo.isin(["rendimento_reducao", "saida_inquilino", "venda_com_perda"]).sum())},
        {"grupo de fatos": "  dos contados: tipo saida_inquilino", "fatos": int((fatos.tipo == "saida_inquilino").sum())},
    ])
    salvar(ign, "fatos_ignorados")
    emit(tabela_md(ign, {"fatos": 0}))
    emit()
    emit(AVISO)
    emit()

    am = amostra_leitura(a)
    salvar(am, "amostra_leitura")
    resumo = (am.groupby(["sentido sorteado", "veredito da leitura"]).size().unstack(fill_value=0)
              .reindex(columns=["ok", "duvidoso", "mal classificado"], fill_value=0).reset_index())
    resumo["total"] = resumo[["ok", "duvidoso", "mal classificado"]].sum(axis=1)
    emit("Amostra lida à mão (20 fatos sentido queda + 20 sentido alta, sorteados com semente 2024 entre os fatos contados):")
    emit()
    emit(tabela_md(resumo, {"ok": 0, "duvidoso": 0, "mal classificado": 0, "total": 0}))
    emit()
    for sent in ["queda", "alta"]:
        s = am[am["sentido sorteado"] == sent]
        emit(f"- sentido {sent}, mal classificados: " + ", ".join(str(i) for i in s[s["veredito da leitura"] == "mal classificado"]["id"]))
        emit(f"- sentido {sent}, duvidosos: " + ", ".join(str(i) for i in s[s["veredito da leitura"] == "duvidoso"]["id"]))
    # por tipo, dentro dos negativos sorteados
    am_q = am[am["sentido sorteado"] == "queda"].groupby(["tipo (palavras)", "veredito da leitura"]).size().unstack(fill_value=0).reset_index()
    emit()
    emit("Dentro da amostra de queda, por tipo atribuído pelas palavras:")
    emit()
    emit(tabela_md(am_q, {k: 0 for k in am_q.columns[1:]}))
    emit()

    # ---------- ordens: resultado, régua CDI
    o["ano"] = o["entrada"].dt.year
    o["res_pct"] = 100 * o["res_rs"] / o["valor"]
    assert (o["res_pct"] - o["res_col"]).abs().max() < 0.06, "Resultado (%) recalculado não bate com a coluna"
    o["cdi_bruto_rs"] = [v * reg.bruto(e, s) for v, e, s in zip(o["valor"], o["entrada"], o["saida"])]
    o["cdi_liq_rs"] = [reg.liquido(v, e, s) for v, e, s in zip(o["valor"], o["entrada"], o["saida"])]
    o["cdi_bruto_pct"] = 100 * o["cdi_bruto_rs"] / o["valor"]
    o["cdi_liq_pct"] = 100 * o["cdi_liq_rs"] / o["valor"]
    o["exc_pp"] = o["res_pct"] - o["cdi_bruto_pct"]
    o["exc_liq_pp"] = o["res_pct"] - o["cdi_liq_pct"]
    o["exc_rs"] = o["res_rs"] - o["cdi_bruto_rs"]

    # ---------- fatos por ordem
    por_fundo = {k: g for k, g in fatos.groupby("fundo")}
    fundos_com_fato = set(a["fundo"])  # qualquer fato da planilha, inclusive repetidos
    tipos_neg2 = ["rendimento_reducao", "saida_inquilino", "venda_com_perda"]
    cont = []
    tipos60: list[dict] = []
    for _, r in o.iterrows():
        g = por_fundo.get(r["Fundo"])
        linha = {"sem_cobertura": int(r["Fundo"] not in fundos_com_fato)}
        tp = {}
        for sufixo, dias in [("30", 30), ("60", 60)]:
            for nome in ["neg1", "neg2", "neg3", "pos"]:
                linha[f"{nome}_{sufixo}"] = 0
        linha["pos_entre"] = 0
        linha["fatos_60_qualquer"] = 0
        if g is not None:
            d = g["data"]
            for sufixo, dias in [("30", 30), ("60", 60)]:
                j = g[(d >= r["sinal"] - timedelta(days=dias)) & (d <= r["sinal"])]
                linha[f"neg1_{sufixo}"] = int((j.sentido == "queda").sum())
                linha[f"neg2_{sufixo}"] = int(j.tipo.isin(tipos_neg2).sum())
                linha[f"neg3_{sufixo}"] = int((j.tipo == "saida_inquilino").sum())
                linha[f"pos_{sufixo}"] = int((j.sentido == "alta").sum())
                if dias == 60:
                    linha["fatos_60_qualquer"] = len(j)
                    tp = {t: 1 for t in j.tipo.unique()}
            e = g[(d >= r["entrada"]) & (d <= r["saida"])]
            linha["pos_entre"] = int((e.sentido == "alta").sum())
        cont.append(linha)
        tipos60.append(tp)
    cont = pd.DataFrame(cont)
    o = pd.concat([o.reset_index(drop=True), cont], axis=1)

    n_sc = int(o["sem_cobertura"].sum())
    emit("## Cobertura dos fatos")
    emit()
    cob = o.groupby("Carteira").agg(ordens=("Fundo", "size"), sem_cobertura=("sem_cobertura", "sum")).reset_index()
    cob.columns = ["carteira", "ordens", "ordens de fundo sem nenhum fato na planilha"]
    cob.loc[len(cob)] = ["total", cob["ordens"].sum(), cob["ordens de fundo sem nenhum fato na planilha"].sum()]
    salvar(cob, "cobertura")
    emit(tabela_md(cob, {"ordens": 0, "ordens de fundo sem nenhum fato na planilha": 0}))
    emit()
    emit("Fundos das ordens que não aparecem em anuncios.csv: " + ", ".join(sorted(set(o[o.sem_cobertura == 1]["Fundo"]))) +
         ". Para eles 'zero fatos' não quer dizer 'sem notícia', quer dizer 'sem dado'. "
         "Interpretação adotada: essas ordens saem das comparações (grupo 0, 1, 2 ou mais) e ficam só na planilha de ordens.")
    emit()
    salvar(o.drop(columns=[]).assign(**{c_: o[c_].dt.strftime("%d/%m/%Y") for c_ in ["sinal", "entrada", "saida"]}), "ordens_com_fatos")

    base = o[o["sem_cobertura"] == 0].copy()
    emit(f"Ordens usadas nas comparações: {len(base)} (de {len(o)}).")
    emit()
    emit("Chaves das contagens (janela = dias corridos antes do sinal, incluindo o dia do sinal, isto é, de sinal−30 (ou −60) até o dia do sinal):")
    emit("- fato negativo, definição 1 (principal) = sentido 'queda'; definição 2 = tipo rendimento_reducao, saida_inquilino ou venda_com_perda; "
         "definição 3 = só tipo saida_inquilino (a que a leitura à mão mostrou mais confiável).")
    emit("- fato positivo = sentido 'alta'. 6b(ii) usa fatos com data de anúncio entre a data de entrada e a de saída (inclusive).")
    emit()

    # ---------- 6a
    def bloco_6a(d: pd.DataFrame, titulo_rot: str, rot_extra: dict, defs=(1, 2, 3), md_janelas=("30", "60"), md_defs=(1,)):
        todos, tt = [], []
        for dn in defs:
            for jan in ["30", "60"]:
                col = f"neg{dn}_{jan}"
                rot = {**rot_extra, "definição de fato negativo": dn, "janela (dias)": jan}
                todos.append(tabela_grupos(d, col, rot))
                tt.append(teste_sem_com(d, col, rot))
        return pd.concat(todos), pd.concat(tt)

    emit("## 6a. Queda sem notícia contra queda com fato negativo")
    emit()
    t6a, test6a = bloco_6a(base, "6a", {})
    salvar(t6a, "6a_grupos")
    salvar(test6a, "6a_testes")
    colunas_md = ["carteira", "período", "grupo", "ordens", "média (%)", "mediana (%)", "% positivas",
                  "excesso médio s/ 105% CDI bruto (p.p.)", "pior ordem (%)", "maior queda média abaixo da entrada (%)",
                  "dias corridos médios", "% saiu por prazo"]
    fm = {"ordens": 0, "dias corridos médios": 0, "% positivas": 0, "% saiu por prazo": 0}
    for jan in ["30", "60"]:
        x = t6a[(t6a["definição de fato negativo"] == 1) & (t6a["janela (dias)"] == jan)][colunas_md]
        emit(f"Janela de {jan} dias, fato negativo = definição 1 (sentido queda). {AVISO}")
        emit()
        emit(tabela_md(x, fm))
        emit()

    def legenda_grupos():
        emit("Legenda: carteira = A (15% abaixo da média), B (20%), C (15% só em queda geral); período = ano da entrada; "
             "grupo = número de fatos negativos do mesmo fundo na janela; ordens = quantidade de ordens; média e mediana (%) = "
             "Resultado (%) da ordem (resultado em R$ ÷ valor da ordem, já com taxas e imposto da ordem); % positivas = ordens com resultado "
             "maior que zero; excesso (p.p.) = média de (Resultado % − rendimento de 105% do CDI antes do imposto, com o mesmo valor, "
             "da data de entrada à de saída); pior ordem = menor Resultado (%); maior queda média = média da coluna 'Maior queda abaixo da entrada (%)'; "
             "dias = média de dias corridos; % saiu por prazo = ordens com motivo 'prazo' (não voltaram à média em 252 pregões). "
             "Ordens 'em aberto' valem pelo preço de 09/11/2026 e entram nas médias.")
        emit()

    legenda_grupos()

    emit("Teste simples, sem notícia (0) contra com fato negativo (1 ou mais). Diferença de médias = média do grupo 0 menos média do grupo 'com'; "
         f"IC 95% por bootstrap ({N_BOOT} sorteios, semente {SEMENTE_BOOT}); p = Mann-Whitney bilateral. "
         "Atenção: as ordens se sobrepõem no tempo (muitas entram nos mesmos dias de queda geral e o mesmo fato entra na contagem de várias ordens), "
         "então o p é otimista (parece mais convincente do que é). " + AVISO)
    emit()
    tc = ["carteira", "período", "janela (dias)", "medida", "ordens sem", "ordens com", "média sem", "média com",
          "diferença (sem − com)", "IC95 inferior", "IC95 superior", "p Mann-Whitney"]
    for jan in ["30", "60"]:
        x = test6a[(test6a["definição de fato negativo"] == 1) & (test6a["janela (dias)"] == jan) & (test6a["medida"] == "resultado (%)")][tc]
        emit(f"Janela de {jan} dias, definição 1, medida: Resultado (%).")
        emit()
        emit(tabela_md(x, {"ordens sem": 0, "ordens com": 0, "média sem": 1, "média com": 1, "diferença (sem − com)": 1,
                           "IC95 inferior": 1, "IC95 superior": 1, "p Mann-Whitney": 3}))
        emit()
    emit("Legenda: ordens sem/com = ordens sem fato / com 1 ou mais fatos negativos; média = média do Resultado (%) (p.p. de rentabilidade); "
         "diferença (sem − com) = média sem − média com, em pontos percentuais; IC95 = intervalo de 95% da diferença; p = probabilidade, "
         "se não houvesse diferença, de ver algo tão distante (otimista, ver aviso). Valor '-' = menos de 5 ordens em algum dos grupos. "
         "Os mesmos testes para o excesso sobre 105% CDI e para as definições 2 e 3 estão em planilhas/auditoria_bloco3_6a_testes.csv.")
    emit()

    # sensibilidade: total, defs 2 e 3, 60 dias
    emit("Sensibilidade à definição de fato negativo (total dos períodos, janela de 60 dias; só excesso médio e número de ordens):")
    emit()
    sens = []
    for dn, nome in [(1, "1: sentido queda"), (2, "2: reducao+saida_inquilino+venda_com_perda"), (3, "3: só saida_inquilino")]:
        for cart in ["A", "B", "C"]:
            dc = base[base["Carteira"] == cart]
            r = {"definição": nome, "carteira": cart}
            for gn, gf in GRUPOS:
                s = dc[gf(dc[f"neg{dn}_60"])]
                r[f"ordens grupo {gn}"] = len(s)
                r[f"média (%) grupo {gn}"] = s["res_pct"].mean() if len(s) else np.nan
                r[f"excesso (p.p.) grupo {gn}"] = s["exc_pp"].mean() if len(s) else np.nan
            sens.append(r)
    sens = pd.DataFrame(sens)
    salvar(sens, "6a_sensibilidade_definicao")
    emit(tabela_md(sens, {k: 0 for k in sens.columns if k.startswith("ordens")}))
    emit()
    emit("Legenda: igual à tabela anterior, mas somando todos os períodos; grupo 0/1/2 ou mais = número de fatos negativos em 60 dias. " + AVISO)
    emit()

    # ---------- 6b
    emit("## 6b. Subida com e sem fato positivo")
    emit()
    emit("Interpretação registrada: (i) fato positivo (sentido 'alta') do mesmo fundo nos 30 ou 60 dias antes do sinal, incluindo o dia do sinal; "
         "(ii) fato positivo com data entre a data de entrada e a data de saída da ordem (inclusive). Em (ii) o grupo é definido com informação que só "
         "existe depois da entrada, então NÃO dá para usar como regra de compra; e ordens mais longas têm mais chance de ter algum fato, "
         "o que mistura 'fato positivo' com 'ordem demorada'.")
    emit()
    t6b, test6b = [], []
    for nome, col in [("(i) 30 dias antes do sinal", "pos_30"), ("(i) 60 dias antes do sinal", "pos_60"), ("(ii) entre a entrada e a saída", "pos_entre")]:
        rot = {"janela": nome}
        t6b.append(tabela_grupos(base, col, rot))
        test6b.append(teste_sem_com(base, col, rot))
    t6b, test6b = pd.concat(t6b), pd.concat(test6b)
    salvar(t6b, "6b_grupos")
    salvar(test6b, "6b_testes")
    for nome in ["(i) 30 dias antes do sinal", "(i) 60 dias antes do sinal", "(ii) entre a entrada e a saída"]:
        x = t6b[t6b["janela"] == nome][colunas_md]
        emit(f"{nome}. Grupo = número de fatos positivos. {AVISO}")
        emit()
        emit(tabela_md(x, fm))
        emit()
    emit("Legenda: igual à 6a, mas o grupo é o número de fatos positivos (sentido 'alta') do mesmo fundo.")
    emit()
    emit("Teste simples (sem fato positivo contra com fato positivo), Resultado (%), mesmos cuidados da 6a (p otimista):")
    emit()
    for nome in ["(i) 60 dias antes do sinal", "(ii) entre a entrada e a saída"]:
        x = test6b[(test6b["janela"] == nome) & (test6b["medida"] == "resultado (%)")][tc[:2] + tc[3:]]
        emit(nome)
        emit()
        emit(tabela_md(x, {"ordens sem": 0, "ordens com": 0, "média sem": 1, "média com": 1, "diferença (sem − com)": 1,
                           "IC95 inferior": 1, "IC95 superior": 1, "p Mann-Whitney": 3}))
        emit()
    emit("Legenda: como a dos testes da 6a, com 'sem' = sem fato positivo e 'com' = 1 ou mais fatos positivos.")
    emit()

    # ---------- 6c
    emit("## 6c. Resultado por tema do fato (coluna tipo)")
    emit()
    emit("Interpretação: para cada ordem com pelo menos um fato do mesmo fundo nos 60 dias antes do sinal (fatos repetidos e continuações fora), "
         "a ordem entra em uma linha para cada tipo de fato que ela tem nessa janela; uma ordem com fatos de 2 tipos aparece nas 2 linhas, "
         "então as linhas não somam o total. O tipo é o da classificação por palavras (erra, ver seção 0). "
         "Linhas com menos de 10 ordens ficam marcadas 'não concluir'.")
    emit()
    tipos_todos = sorted(set(t for d in tipos60 for t in d))
    base_idx = base.index
    linhas = []
    for cart in ["A", "B", "C"]:
        for tp in tipos_todos + ["(nenhum fato nos 60 dias)"]:
            if tp.startswith("("):
                m = (o["Carteira"] == cart) & (o["sem_cobertura"] == 0) & (o["fatos_60_qualquer"] == 0)
            else:
                m = (o["Carteira"] == cart) & pd.Series([tp in d for d in tipos60], index=o.index)
            d = o[m]
            r = {"carteira": cart, "tipo": tp}
            for pn, pf in PERIODOS:
                dp = d[pf(d)]
                m_ = medidas(dp)
                suf = {"escolha 2018-2022": "esc", "conferência 2023-2026": "conf", "total": "tot"}[pn]
                r[f"ordens {suf}"] = len(dp)
                r[f"média (%) {suf}"] = m_.get("média (%)", np.nan)
                if suf == "tot":
                    r["mediana (%) tot"] = m_.get("mediana (%)", np.nan)
                    r["% positivas tot"] = m_.get("% positivas", np.nan)
                    r["excesso s/ 105% CDI (p.p.) tot"] = m_.get("excesso médio s/ 105% CDI bruto (p.p.)", np.nan)
            r["pode concluir?"] = "sim" if r["ordens tot"] >= 10 else "não concluir (menos de 10 ordens)"
            linhas.append(r)
    t6c = pd.DataFrame(linhas)
    salvar(t6c, "6c_por_tipo")
    fm6c = {"ordens esc": 0, "ordens conf": 0, "ordens tot": 0, "% positivas tot": 0}
    emit(f"Total e períodos por tipo. {AVISO}")
    emit()
    emit(tabela_md(t6c[["carteira", "tipo", "ordens tot", "média (%) tot", "mediana (%) tot", "% positivas tot",
                        "excesso s/ 105% CDI (p.p.) tot", "ordens esc", "média (%) esc", "ordens conf", "média (%) conf",
                        "pode concluir?"]], fm6c))
    emit()
    emit("Legenda: ordens = ordens com pelo menos um fato desse tipo nos 60 dias antes do sinal (uma ordem pode estar em várias linhas); "
         "média e mediana (%) = Resultado (%) das ordens; % positivas = ordens com resultado maior que zero; excesso = média de "
         "(Resultado % − 105% do CDI bruto no mesmo período e valor), em p.p.; esc/conf/tot = entradas 2018-2022 / 2023-2026 / todas. "
         "'nenhum fato nos 60 dias' = ordens (de fundos com cobertura) sem fato algum, de qualquer tipo, na janela.")
    emit()

    # ---------- 6d
    emit("## 6d. Só nos dias de queda geral")
    emit()
    emit("Interpretação: carteira C (que já é só de queda geral; todas as 292 ordens têm 'Fundos caídos no dia' de 15,4% ou mais, então C é idêntica à 6a/6b) "
         "e ordens da carteira A com 'Fundos caídos no dia (%)' ≥ 15. Como comparação extra, ordens da A com menos de 15 (queda só do fundo).")
    emit()
    subs = [("C (todas: queda geral)", base[base["Carteira"] == "C"]),
            ("A com fundos caídos no dia ≥ 15%", base[(base["Carteira"] == "A") & (base["caidos"] >= 15)]),
            ("A com fundos caídos no dia < 15% (extra)", base[(base["Carteira"] == "A") & (base["caidos"] < 15)])]
    emit(f"Ordens por subconjunto (de fundos com cobertura): " + "; ".join(f"{n}: {len(d)}" for n, d in subs) + ".")
    emit()
    l6d, t6d = [], []

    def grupos_sub(d, col, rot, nome_sub):
        linhas = []
        for pn, pf in PERIODOS:
            dp = d[pf(d)]
            for gn, gf in GRUPOS:
                linhas.append({"subconjunto": nome_sub, **rot, "período": pn, "grupo": gn, **medidas(dp[gf(dp[col])])})
        return pd.DataFrame(linhas)

    def teste_sub(d, col, rot, nome_sub):
        out = []
        for pn, pf in PERIODOS:
            dp = d[pf(d)]
            sem, com = dp[dp[col] == 0], dp[dp[col] >= 1]
            r = {"subconjunto": nome_sub, **rot, "período": pn, "ordens sem": len(sem), "ordens com": len(com),
                 "média sem": np.nan, "média com": np.nan, "diferença (sem − com)": np.nan, "IC95 inferior": np.nan,
                 "IC95 superior": np.nan, "p Mann-Whitney": np.nan}
            if len(sem) >= 5 and len(com) >= 5:
                x, y = sem["res_pct"].values, com["res_pct"].values
                lo, hi = boot_dif(x, y)
                r.update({"média sem": x.mean(), "média com": y.mean(), "diferença (sem − com)": x.mean() - y.mean(),
                          "IC95 inferior": lo, "IC95 superior": hi, "p Mann-Whitney": stats.mannwhitneyu(x, y, alternative="two-sided").pvalue})
            out.append(r)
        return pd.DataFrame(out)

    visoes = [("6a negativo def.1, 30 dias", "neg1_30"), ("6a negativo def.1, 60 dias", "neg1_60"),
              ("6b positivo (i), 30 dias", "pos_30"), ("6b positivo (i), 60 dias", "pos_60"),
              ("6b positivo (ii), entre entrada e saída", "pos_entre")]
    for ns, d in subs:
        for vn, col in visoes:
            l6d.append(grupos_sub(d, col, {"visão": vn}, ns))
            t6d.append(teste_sub(d, col, {"visão": vn}, ns))
    l6d, t6d = pd.concat(l6d), pd.concat(t6d)
    salvar(l6d, "6d_grupos")
    salvar(t6d, "6d_testes")
    cm6d = ["subconjunto", "período", "grupo", "ordens", "média (%)", "mediana (%)", "% positivas",
            "excesso médio s/ 105% CDI bruto (p.p.)", "pior ordem (%)", "maior queda média abaixo da entrada (%)",
            "dias corridos médios", "% saiu por prazo"]
    for vn in ["6a negativo def.1, 60 dias", "6b positivo (i), 60 dias", "6b positivo (ii), entre entrada e saída"]:
        x = l6d[l6d["visão"] == vn][cm6d]
        emit(f"{vn}. {AVISO}")
        emit()
        emit(tabela_md(x, fm))
        emit()
    emit("Legenda: igual à 6a; subconjunto = quais ordens entram. As visões de 30 dias e os testes estão em "
         "planilhas/auditoria_bloco3_6d_grupos.csv e planilhas/auditoria_bloco3_6d_testes.csv.")
    emit()
    emit("Teste simples dentro dos dias de queda geral (Resultado %, sem contra com; p otimista, ordens se sobrepõem):")
    emit()
    x = t6d[t6d["visão"].isin(["6a negativo def.1, 60 dias"])][["subconjunto", "período", "ordens sem", "ordens com", "média sem",
                                                                "média com", "diferença (sem − com)", "IC95 inferior", "IC95 superior", "p Mann-Whitney"]]
    emit(tabela_md(x, {"ordens sem": 0, "ordens com": 0, "média sem": 1, "média com": 1, "diferença (sem − com)": 1,
                       "IC95 inferior": 1, "IC95 superior": 1, "p Mann-Whitney": 3}))
    emit()
    emit("Legenda: como a dos testes da 6a (definição 1, janela de 60 dias).")
    emit()

    # ---------- lacunas medidas
    L = a["texto"].fillna("")
    alfa = L.map(lambda s: (sum(ch.isalpha() for ch in s) / max(1, len(s.replace(" ", "")))) if s else 0)
    emit("## Números para a tabela de lacunas")
    emit()
    lac = pd.DataFrame([
        {"medida": "fatos com texto menor que 600 caracteres", "valor": int((L.str.len() < 600).sum())},
        {"medida": "fatos com menos de 60% de letras nos primeiros 3.000 caracteres (provável imagem/slide mal lido)", "valor": int((alfa < 0.6).sum())},
        {"medida": "fatos cujo texto guardado tem exatamente 3.000 caracteres (cortados)", "valor": int((L.str.len() == 3000).sum())},
        {"medida": "fatos cujos primeiros 3.000 caracteres não trazem a expressão 'FATO RELEVANTE'", "valor": int((~L.str.contains("FATO RELEVANTE", case=False)).sum())},
        {"medida": "ordens de fundos sem nenhum fato na planilha", "valor": n_sc},
        {"medida": "fundos das ordens sem nenhum fato na planilha", "valor": len(set(o[o.sem_cobertura == 1]["Fundo"]))},
    ])
    salvar(lac, "lacunas_medidas")
    emit(tabela_md(lac, {"valor": 0}))
    emit()

    # ---------- conferência à mão
    emit("## Conferência à mão (contas refeitas por outro caminho no próprio programa)")
    emit()
    idx = [0]
    com_fato = base[(base["neg1_60"] >= 1)].index
    idx.append(int(com_fato[0]))
    for k in idx:
        r = o.loc[k]
        emit(f"Ordem {k + 1} do arquivo: carteira {r['Carteira']}, {r['Fundo']}, sinal {r['sinal']:%d/%m/%Y}, entrada {r['entrada']:%d/%m/%Y}, saída {r['saida']:%d/%m/%Y}")
        # resultado a partir das parcelas
        bruto = pd.read_csv(PL / "kairi_ordens.csv", sep=";", decimal=",", encoding="utf-8-sig").loc[k]
        soma = bruto["Valorização (R$)"] + bruto["Rendimentos recebidos (R$)"] - bruto["Taxas (R$)"] - bruto["Imposto (R$)"]
        emit(f"  resultado = valorização {bruto['Valorização (R$)']:.2f} + rendimentos {bruto['Rendimentos recebidos (R$)']:.2f} − taxas {bruto['Taxas (R$)']:.2f} − imposto {bruto['Imposto (R$)']:.2f} = {soma:.2f}; coluna Resultado (R$) = {bruto['Resultado (R$)']:.2f}; "
             f"bate: {abs(soma - bruto['Resultado (R$)']) < 0.02}")
        emit(f"  resultado % = {r['res_rs']:.2f} ÷ {r['valor']:.2f} = {100 * r['res_rs'] / r['valor']:.3f}%  (coluna: {r['res_col']}%)")
        # CDI à mão
        cc = c.set_index("data")["indice_105_do_cdi"]
        d0 = cc.index[cc.index <= r["entrada"]][-1]
        d1 = cc.index[cc.index <= r["saida"]][-1]
        i0, i1 = cc[d0], cc[d1]
        rend = r["valor"] * (i1 / i0 - 1)
        dias = (r["saida"] - r["entrada"]).days
        emit(f"  105% CDI: índice em {d0:%d/%m/%Y} = {i0:.6f}; em {d1:%d/%m/%Y} = {i1:.6f}; bruto = {r['valor']:.2f} × ({i1:.6f} ÷ {i0:.6f} − 1) = {rend:.2f} R$ ({100 * rend / r['valor']:.3f}%); "
             f"programa: {r['cdi_bruto_rs']:.2f}; bate: {abs(rend - r['cdi_bruto_rs']) < 0.005}")
        liq = rend
        if 1 <= dias <= 29:
            liq *= 1 - IOF[dias - 1] / 100
        liq *= 1 - (0.225 if dias <= 180 else 0.20 if dias <= 360 else 0.175 if dias <= 720 else 0.15)
        emit(f"  líquido ({dias} dias corridos, IR {ir_aliquota(dias) * 100:.1f}%): {liq:.2f} R$; programa: {r['cdi_liq_rs']:.2f}; bate: {abs(liq - r['cdi_liq_rs']) < 0.005}")
        emit(f"  excesso sobre 105% CDI bruto = {r['res_pct']:.3f} − {r['cdi_bruto_pct']:.3f} = {r['res_pct'] - r['cdi_bruto_pct']:.3f} p.p.; programa: {r['exc_pp']:.3f}")
        # contagem de fatos à mão (laço simples, sem pandas)
        lista = []
        for _, fa in a.iterrows():
            if fa["fundo"] != r["Fundo"] or fa["rep"] == 1 or fa["cont"] == 1 or fa["sentido"] != "queda":
                continue
            dt = datetime.strptime(fa["data_anuncio"][:10], "%d/%m/%Y")
            dias_antes = (r["sinal"].to_pydatetime() - dt).days
            if 0 <= dias_antes <= 60:
                lista.append((int(fa["id"]), fa["data_anuncio"][:10], dias_antes))
        n30 = sum(1 for _, _, x in lista if x <= 30)
        emit(f"  fatos negativos (sentido queda, sem repetidos/continuações) de {r['Fundo']} de 60 a 0 dias antes do sinal, contados em laço: {lista}; "
             f"30 dias: {n30}, 60 dias: {len(lista)}; programa: {int(r['neg1_30'])} e {int(r['neg1_60'])}; bate: {n30 == r['neg1_30'] and len(lista) == r['neg1_60']}")
        emit()
        assert abs(soma - bruto["Resultado (R$)"]) < 0.02 and abs(rend - r["cdi_bruto_rs"]) < 0.005 and abs(liq - r["cdi_liq_rs"]) < 0.005
        assert n30 == r["neg1_30"] and len(lista) == r["neg1_60"]

    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text("\n".join(MD) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
