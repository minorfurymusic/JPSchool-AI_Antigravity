"""Papel Padrão — trade em fundos de Papel descontados (Skill `papel-padrao`, 18/11/2026).

Regras (conferidas em docs/TIPO1_TRADE.md):
  Sinal: no último pregão de cada mês, fundos que passam no corte essencial da versão 2
    (descontado_saudavel.candidatos_v2: patrimônio >= R$ 100 mi; negociação típica >= R$ 250 mil/dia; sem amortização
    nem saída da bolsa; avaliação de saúde != NÃO COMPRAR; preço 0,50–1,00 do patrimônio; rendimento >= Selic esperada
    pelo Focus × 0,825), SÓ da classe Papel (classe pela carteira, informe mensal da CVM), ordenados pela nota.
    Os 5 primeiros são o sinal.
  Antes de comprar: ler o relatório gerencial (Skill avaliar-fundo).
  Compra: abertura do pregão seguinte ao sinal.
  Venda: no fechamento do dia em que (preço + rendimentos com data-com desde a compra) chega a +10% sobre o custo;
    prazo de 1 ano (252 pregões).

Uso:
  PYTHONPATH=. python3 estudos/papel_padrao.py sinais [dd/mm/aaaa]   sinal do último fim de mês até a data (padrão: hoje)
  PYTHONPATH=. python3 estudos/papel_padrao.py posicoes              acompanha planilhas/papel_padrao_posicoes.csv
Saída: planilhas/papel_padrao.xlsx (abas Sinais, Cenário do país, Posições, Regras).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import estudos.descontado_saudavel as DS
from estudos.cobertura_rendimento import cobertura
from estudos.saude_fundo import saude

RD = DS.RD
RAIZ = Path(__file__).resolve().parents[1]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
POS = RAIZ / "planilhas" / "papel_padrao_posicoes.csv"
SAIDA = RAIZ / "planilhas" / "papel_padrao.xlsx"
ALVO, PRAZO, B3, IR = 0.10, 252, 0.0003, 0.20


def historico():
    """Operações passadas de Papel com alvo +10% (planilhas/descontado_classes.xlsx, contas corrigidas)."""
    O = pd.read_excel(RAIZ / "planilhas/descontado_classes.xlsx", sheet_name="Operações")
    return O[(O["classe"] == "Papel") & (O["venda"] == "Alvo +10%")]


def cenario(d):
    """Quadro do país do mês anterior ao dia d e resultado passado de Papel (alvo +10%) no mesmo cenário."""
    M = pd.read_csv(RAIZ / "planilhas/macro_mensal.csv", **OP)
    M["mes"] = pd.PeriodIndex(pd.to_datetime("01/" + M["mes"], dayfirst=True), freq="M")
    M = M.set_index("mes")
    m = M.loc[: d.to_period("M") - 1].ffill().iloc[-1]
    esp = m["mercado espera (focus - selic, pontos)"]
    g_esp = "espera queda forte da Selic" if esp <= -1 else ("espera alta da Selic" if esp >= 1 else "espera Selic estável")
    div = m["divida bruta: variação em 12 meses (pontos)"]
    g_div = "dívida subiu mais de 2 pontos em 12 meses" if div > 2 else "dívida estável ou caindo"
    G = pd.read_excel(RAIZ / "planilhas/descontado_periodos.xlsx", sheet_name="1 por cenário").set_index("grupo")
    linhas = [("Selic (% ao ano)", m["selic (% ano)"]), ("Focus: Selic no fim do ano seguinte (%)", m["focus selic fim do ano seguinte (%)"]),
              ("Mercado espera (Focus − Selic, pontos)", esp), ("IPCA 12 meses (%)", m["ipca 12 meses (%)"]),
              ("Dívida bruta (% do PIB)", m["divida bruta (% PIB)"]), ("Dívida: variação em 12 meses (pontos)", div),
              ("Dólar médio (R$)", m["dolar medio (R$)"])]
    T = pd.DataFrame(linhas, columns=["Medida", "Valor"])
    H = G.loc[[g_esp, g_div], ["Operações", "Com lucro", "Bateram o CDI", "Resultado médio", "Ganho − CDI por mês (pontos)"]]
    return T, H.reset_index().rename(columns={"grupo": "Cenário de hoje (resultado passado de Papel, alvo +10%)"})


def mes_completo(x):
    """O último pregão de um mês só é fim de mês se a base tiver dado do mês seguinte ou chegar perto do fim do mês."""
    return x < RD.DIAS[-1] or x >= (x + pd.offsets.MonthEnd(0)) - pd.Timedelta(days=3)


def sinais(d, previa=False):
    dias = [x for x in RD.FIM_MES if x <= d and (previa or mes_completo(x))]
    fm = dias[-1] if not previa else RD.DIAS[RD.DIAS.index(max(x for x in RD.DIAS if x <= d))]
    C = DS.candidatos_v2(fm)
    C = C[C["tipo"] == "Papel"].reset_index(drop=True)
    H = historico()
    L = []
    for i, r in C.iterrows():
        h = H[H["fundo"] == r["fundo"]]
        sv = saude(r["fundo"], fm)
        cb = cobertura(r["fundo"], fm)
        L.append({"posição": i + 1, "sinal (top 5)": "SIM" if i < 5 else "", "fundo": r["fundo"], "preço": r["preco"],
                  "preço ÷ patrimônio": r["pvp"], "rendimento ao ano": r["dy"], "acima da mediana de Papel": r["acima_tipo"],
                  "queda em 6 meses": r["queda_6m"], "patrimônio por cota em 12 meses": r["vp_12m"], "oscilação do rendimento": r["oscilacao"],
                  "quedas de rendimento > 2% (12 meses)": r["quedas_2pct"],
                  "cobertura do rendimento (CVM)": cb["cobertura"] if cb else np.nan, "janela da cobertura": cb["janela"] if cb else "",
                  "saúde": sv["veredito"], "documentos negativos (12 meses)": len(sv.get("docs_negativos", [])), "nota": r["nota"],
                  "histórico: operações": len(h), "histórico: com lucro": (h["resultado_liquido"] > 0).mean() if len(h) else np.nan,
                  "histórico: resultado médio": h["resultado_liquido"].mean() if len(h) else np.nan,
                  "histórico: pregões médios": h["pregoes"].mean() if len(h) else np.nan})
    return fm, pd.DataFrame(L)


def ret_ate(f, ent, preco, dia=None):
    """(ret bruto com rendimentos pela data-com, resultado líquido se vendesse no fechamento, pregões, último dia)."""
    s = RD.PF[f]
    y = s.loc[ent:]
    y = y[y["negociou (1/0)"] == 1]
    if dia is not None:
        y = y.loc[:dia]
    custo = preco * (1 + B3)
    r = RD.RF.get(f)
    rend = float(r[(r["data_base"] >= ent) & (r["data_base"] <= y.index[-1])]["valor (R$/cota)"].sum()) if r is not None else 0.0
    venda = float(y["fechamento"].iloc[-1]) * (1 - B3)
    bruto = (venda + rend) / custo - 1
    imp = IR * max(venda - custo, 0)
    return bruto, (venda - imp + rend) / custo - 1, len(y), y.index[-1], rend


def posicoes():
    if not POS.exists():
        pd.DataFrame(columns=["fundo", "data_compra", "preco_compra", "cotas"]).to_csv(POS, index=False, **OP)
    P = pd.read_csv(POS, **OP)
    L = []
    for r in P.itertuples():
        ent = pd.to_datetime(r.data_compra, dayfirst=True)
        bruto, liq, n, ult, rend = ret_ate(r.fundo, ent, float(r.preco_compra))
        aviso = []
        if bruto >= ALVO:
            aviso.append("ALVO ATINGIDO: vender")
        if n >= PRAZO:
            aviso.append("prazo de 1 ano vencido: vender")
        if n >= 20 and bruto < -0.05:
            aviso.append("abaixo de −5% com 20+ pregões: no passado, 64% a 91% dessas terminaram no prejuízo")
        L.append({"fundo": r.fundo, "compra": ent.date(), "preço de compra": r.preco_compra, "cotas": r.cotas, "último dia com dado": ult.date(),
                  "pregões": n, "rendimentos recebidos (R$/cota)": rend, "resultado bruto": bruto, "resultado líquido se vender hoje": liq,
                  "falta para +10%": ALVO - bruto, "aviso": "; ".join(aviso)})
    return pd.DataFrame(L)


REGRAS = pd.DataFrame({"Regra": [
    "Sinal: último pregão do mês; corte essencial da versão 2; só classe Papel; os 5 de maior nota",
    "Antes de comprar: ler o relatório gerencial (Skill avaliar-fundo): cobertura, reserva, atraso de título",
    "Compra: abertura do pregão seguinte ao sinal",
    "Venda: fechamento do dia em que preço + rendimentos (data-com) chega a +10% sobre o custo",
    "Prazo: 1 ano (252 pregões)",
    "Passado (2018–11/2026): 117 operações, 93% com lucro, 79% bateram o CDI do mesmo período, +7,4% líquido, ~137 pregões",
    "Cenário de queda forte da Selic esperada ou dívida subindo: ainda positivo, mas só +0,14 a +0,18 ponto por mês acima do CDI"]})


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    modo = sys.argv[1] if len(sys.argv) > 1 else "sinais"
    ult_dado = RD.DIAS[-1]
    hoje = pd.Timestamp.today().normalize()
    print(f"Dados de preço até {ult_dado:%d/%m/%Y}" + (f"  ATENÇÃO: {(hoje - ult_dado).days} dias de atraso; atualizar a base antes de comprar"
                                                      if (hoje - ult_dado).days > 3 else ""))
    abas = {"Regras": REGRAS}
    if modo == "sinais":
        d = pd.to_datetime(sys.argv[2], dayfirst=True) if len(sys.argv) > 2 else ult_dado
        fm, S = sinais(d)
        T, H = cenario(fm)
        print(f"\nSINAL DE {fm:%d/%m/%Y} (compra na abertura do pregão seguinte, depois de ler o relatório):")
        print(S.head(10).to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
        print("\nCENÁRIO DO PAÍS (mês anterior ao sinal)")
        print(T.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
        print(H.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
        abas.update({"Sinais": S, "Cenário do país": T, "Cenário - resultado passado": H})
        if not mes_completo(RD.FIM_MES[-1]):
            dp, SP = sinais(ult_dado, previa=True)
            print(f"\nPRÉVIA com os dados de {dp:%d/%m/%Y} (mês ainda não fechou; NÃO é sinal):")
            print(SP.head(5)[["posição", "fundo", "preço", "preço ÷ patrimônio", "rendimento ao ano", "cobertura do rendimento (CVM)",
                              "saúde", "histórico: operações", "histórico: com lucro"]].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
            abas["Prévia do mês"] = SP
    Pz = posicoes()
    print("\nPOSIÇÕES (planilhas/papel_padrao_posicoes.csv)")
    print(Pz.to_string(index=False, float_format=lambda v: f"{v:,.3f}") if len(Pz) else "nenhuma posição cadastrada")
    abas["Posições"] = Pz
    with pd.ExcelWriter(SAIDA) as w:
        for n, t in abas.items():
            t.to_excel(w, sheet_name=n, index=False)
    print(f"gravado: {SAIDA.relative_to(RAIZ)}")
