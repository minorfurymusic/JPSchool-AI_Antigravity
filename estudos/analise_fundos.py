"""Análise de uma lista de fundos num dia, com os critérios das Skills (pedido do dono, 18/11/2026).

    PYTHONPATH=. python3 estudos/analise_fundos.py FUNDO11 FUNDO11 ... [--cotahist ARQUIVO_ANUAL.ZIP]

Para cada fundo, no último pregão da base: classe pela carteira (CVM); preço; variação em 1, 6 e 12 meses; distância da
média de 200 pregões e negociação típica (zonas do Kairi Padrão: C1 = −25% com R$ 500 mil–1 mi/dia; C2 = −20% com
R$ 1 mi+/dia); preço ÷ patrimônio (corrigido); rendimento ao ano sobre o preço; constância do rendimento em 12 meses;
patrimônio por cota em 12 meses; cobertura do rendimento (CVM); avaliação de saúde; se está entre os candidatos do
Papel Padrão (corte essencial) e a posição na classe.
Fundo fora da base (código que nunca entrou): preço e médias pelo COTAHIST da B3 (--cotahist), valor patrimonial pelo
informe mensal da CVM (vale 75 dias depois do mês de referência); rendimento não disponível.
Saída: planilhas/analise_fundos_AAAA-MM-DD.csv.
"""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import estudos.descontado_saudavel as DS
from estudos.classificacao_carteira import classe
from estudos.cobertura_rendimento import cobertura
from estudos.saude_fundo import saude

RD = DS.RD
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")


def var(s, d, meses):
    a = s.loc[:d - pd.DateOffset(months=meses)]
    return float(s.loc[:d].iloc[-1] / a.iloc[-1] - 1) if len(a) else np.nan


def vp_cvm(prefixo, d):
    m = pd.read_csv("planilhas/classificacao_carteira_mensal.csv", dtype=str, sep=";", encoding="utf-8-sig")
    cn = m[m["fundo"].fillna("").str[:4] == prefixo]["cnpj"].dropna().unique()
    L = []
    for a in (2025, 2026):
        with zipfile.ZipFile(f"/tmp/claude-0/cvm_men/inf_mensal_fii_{a}.zip") as z:
            c = pd.read_csv(z.open(f"inf_mensal_fii_complemento_{a}.csv"), sep=";", encoding="latin-1", dtype=str)
        L.append(c[c["CNPJ_Fundo_Classe"].isin(cn)])
    c = pd.concat(L)
    if c.empty:
        return np.nan, "", None
    c["vale"] = pd.to_datetime(c["Data_Referencia"]) + pd.Timedelta(days=75)
    c = c[c["vale"] <= d].sort_values(["Data_Referencia", "Versao"])
    if c.empty:
        return np.nan, "", None
    # o mesmo começo de ISIN pode estar em mais de um CNPJ (ex.: TRXF, XPML): fica o de maior patrimônio no último mês
    u = c[c["Data_Referencia"] == c["Data_Referencia"].max()].copy()
    u["pl"] = pd.to_numeric(u["Patrimonio_Liquido"], errors="coerce")
    cnpj = u.sort_values("pl")["CNPJ_Fundo_Classe"].iloc[-1]
    c = c[c["CNPJ_Fundo_Classe"] == cnpj]
    return float(c["Valor_Patrimonial_Cotas"].iloc[-1]), c["Data_Referencia"].iloc[-1][:7], cnpj


if __name__ == "__main__":
    args = sys.argv[1:]
    cot = None
    if "--cotahist" in args:
        i = args.index("--cotahist")
        cot = args[i + 1]
        args = args[:i] + args[i + 2:]
    d = RD.DIAS[-1]
    C = DS.candidatos_v2(d)
    C["pos_classe"] = C.groupby("tipo").cumcount() + 1
    L = []
    for f in [a.upper() for a in args]:
        cl = classe(f, d)
        lin = {"fundo": f, "classe pela carteira": cl}
        if f in RD.PF:
            x = RD.PF[f].loc[:d]
            x = x[x["negociou (1/0)"] == 1]
            c = x["fechamento"]
            con = DS.constancia(f, d) or {}
            cb = cobertura(f, d)
            sv = saude(f, d)
            linha = C[C["fundo"] == f]
            lin.update({"fonte": "base", "preço": float(c.iloc[-1]), "variação 1 mês": var(c, d, 1), "variação 6 meses": var(c, d, 6),
                        "variação 12 meses": var(c, d, 12), "distância da média de 200": float(c.iloc[-1] / c.iloc[-200:].mean() - 1),
                        "negociação típica (R$/dia)": float(x["volume_dia (R$)"].iloc[-60:].median()),
                        "preço ÷ patrimônio": float(x["preco_sobre_valor_patrimonial"].iloc[-1]),
                        "rendimento ao ano": float(x["rendimento_ano_sobre_preco (%)"].iloc[-1]) / 100,
                        "oscilação do rendimento": con.get("osc"), "quedas de rendimento > 2%": con.get("quedas2"),
                        "tendência do rendimento": con.get("tend"), "patrimônio por cota 12 meses": float(x["vp12"].iloc[-1]),
                        "cobertura (CVM)": cb["cobertura"] if cb else np.nan, "saúde": sv["veredito"],
                        "problemas": "; ".join(sv.get("problemas", [])),
                        "Papel Padrão: candidato (corte essencial)": "sim" if len(linha) else "não",
                        "posição na classe": int(linha["pos_classe"].iloc[0]) if len(linha) else np.nan})
        elif cot:
            from fii.b3_cotacoes import ler_arquivo
            b = ler_arquivo(Path(cot))
            b = b[b["ticker"] == f].sort_values("data").set_index("data")
            c = b["fechamento"]
            vp, ref, cnpj = vp_cvm(f[:4], d)
            if cnpj:                                   # classe pelo CNPJ escolhido (não pelo prefixo, que pode repetir)
                m = pd.read_csv("planilhas/classificacao_carteira_mensal.csv", dtype=str, sep=";", encoding="utf-8-sig")
                m = m[m["cnpj"] == cnpj].copy()
                m["ref"] = pd.to_datetime("01/" + m["mes_referencia"], dayfirst=True)
                m = m[pd.to_datetime(m["entrega"], dayfirst=True) <= d].sort_values("ref")
                if len(m):
                    lin["classe pela carteira"] = m["classe"].iloc[-1]
            lin.update({"fonte": "fora da base: B3 2026 + CVM", "preço": float(c.iloc[-1]), "variação 1 mês": var(c, d, 1),
                        "variação 6 meses": var(c, d, 6), "distância da média de 200": float(c.iloc[-1] / c.iloc[-200:].mean() - 1),
                        "negociação típica (R$/dia)": float(b["volume"].iloc[-60:].median()),
                        "preço ÷ patrimônio": float(c.iloc[-1] / vp) if vp == vp else np.nan,
                        "problemas": f"sem rendimento, cobertura e saúde (fundo fora da base); patrimônio da CVM ref. {ref}, CNPJ {cnpj}"})
        k, v = lin.get("distância da média de 200", np.nan), lin.get("negociação típica (R$/dia)", 0)
        lin["Kairi Padrão hoje"] = ("SINAL C2" if k <= -0.20 and v >= 1e6 else "SINAL C1" if k <= -0.25 and 5e5 <= v < 1e6 else
                                    "perto (−15% ou menos)" if k <= -0.15 else "não")
        L.append(lin)
    T = pd.DataFrame(L)
    arq = f"planilhas/analise_fundos_{pd.Timestamp.today():%Y-%m-%d}.csv"
    T.to_csv(arq, index=False, float_format="%.4f", **OP)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(f"dia dos dados: {d:%d/%m/%Y}")
    print(T.drop(columns=["problemas"]).to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print("\nPROBLEMAS (avaliação de saúde)")
    print(T[["fundo", "problemas"]].to_string(index=False))
    print(f"gravado: {arq}")
