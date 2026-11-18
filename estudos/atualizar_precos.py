"""Acrescenta pregões novos em planilhas/precos_AAAA.csv a partir do arquivo oficial da B3 (COTAHIST) — 18/11/2026.

Uso:
  PYTHONPATH=. python3 estudos/atualizar_precos.py CAMINHO_DO_COTAHIST.ZIP [mais arquivos...]
  (diário: https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_DddmmAAAA.ZIP; anual: COTAHIST_AAAA.ZIP;
   baixar com curl --http1.1, o servidor falha em HTTP/2)

Regras (iguais às da tabela existente, conferidas em 18/11/2026):
  - só os fundos que já estão na tabela no último dia; pregões depois do último dia da tabela;
  - fundo sem negócio no dia: linha com o último fechamento em abertura/máxima/mínima/fechamento, negociou 0, volume 0;
  - volume_medio_60 = média do volume_dia dos 60 pregões anteriores (linhas da tabela, inclusive sem negócio);
  - rendimento_mensal = o último já anunciado (rendimentos.csv, data_conhecido <= dia; senão, o da linha anterior);
  - valor_patrimonial_cota e patrimonio = informe mensal da CVM a partir de (1º dia do mês de referência + 75 dias);
    antes disso, o da linha anterior. CNPJ -> código pela tabela planilhas/classificacao_carteira_mensal.csv;
  - rendimento_ano_sobre_preco = rendimento_mensal × 12 ÷ fechamento × 100; preço ÷ valor patrimonial;
  - amortizacao_12m = a da linha anterior.
Avisos impressos: código novo na B3 que não está na tabela; variação de mais de 25% no fechamento.
"""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from fii.b3_cotacoes import ler_arquivo

RAIZ = Path(__file__).resolve().parents[1]
OP = dict(sep=";", decimal=",", encoding="utf-8-sig")
CVM = Path("/tmp/claude-0/cvm_men")


def vp_cvm():
    """(prefixo de 4 letras, data em que vale) -> (valor patrimonial, patrimônio), do informe mensal da CVM."""
    L = []
    for a in (2025, 2026):
        with zipfile.ZipFile(CVM / f"inf_mensal_fii_{a}.zip") as z:
            c = pd.read_csv(z.open(f"inf_mensal_fii_complemento_{a}.csv"), sep=";", encoding="latin-1", dtype=str)
        L.append(c.rename(columns={"CNPJ_Fundo": "CNPJ_Fundo_Classe"}))
    c = pd.concat(L)
    c["Versao"] = pd.to_numeric(c["Versao"], errors="coerce")
    c = c.sort_values("Versao").drop_duplicates(["CNPJ_Fundo_Classe", "Data_Referencia"], keep="last")
    m = pd.read_csv(RAIZ / "planilhas/classificacao_carteira_mensal.csv", dtype=str, **{k: v for k, v in OP.items() if k != "decimal"})
    m = m.dropna(subset=["fundo"]).drop_duplicates("cnpj", keep="last").set_index("cnpj")["fundo"].str[:4]
    c["prefixo"] = c["CNPJ_Fundo_Classe"].map(m)
    c["vale_de"] = pd.to_datetime(c["Data_Referencia"]) + pd.Timedelta(days=75)
    c["vp"] = pd.to_numeric(c["Valor_Patrimonial_Cotas"], errors="coerce")
    c["pl"] = pd.to_numeric(c["Patrimonio_Liquido"], errors="coerce")
    return c.dropna(subset=["prefixo", "vp"])[["prefixo", "vale_de", "vp", "pl"]]


if __name__ == "__main__":
    novos = pd.concat([ler_arquivo(Path(a)) for a in sys.argv[1:]]).drop_duplicates(["data", "ticker"])
    novos["data"] = pd.to_datetime(novos["data"])
    ano = int(novos["data"].dt.year.max())
    arq = RAIZ / f"planilhas/precos_{ano}.csv"
    T = pd.concat([pd.read_csv(RAIZ / f"planilhas/precos_{a}.csv", **OP) for a in (ano - 1, ano)])
    T["data"] = pd.to_datetime(T["data"], dayfirst=True)
    ult = T["data"].max()
    dias = sorted(d for d in novos["data"].unique() if d > ult)
    if not dias:
        sys.exit(f"nada novo: a tabela já vai até {ult:%d/%m/%Y}")
    fundos = sorted(T.loc[T["data"] == ult, "fundo"])
    fora = sorted(set(novos.loc[novos["data"].isin(dias), "ticker"]) - set(T["fundo"]))
    R = pd.read_csv(RAIZ / "planilhas/rendimentos.csv", **OP)
    R["data_conhecido"] = pd.to_datetime(R["data_conhecido"], dayfirst=True)
    V = vp_cvm()
    hist = {f: x.sort_values("data") for f, x in T[T["fundo"].isin(fundos)].groupby("fundo")}
    linhas, saltos = [], []
    for d in dias:
        b = novos[novos["data"] == d].set_index("ticker")
        for f in fundos:
            h = hist[f]
            a = h.iloc[-1]
            if f in b.index:
                q = b.loc[f]
                ab, mx, mn, fe, neg, vol = q["abertura"], q["maxima"], q["minima"], q["fechamento"], 1, round(float(q["volume"]))
                if abs(fe / a["fechamento"] - 1) > 0.25:
                    saltos.append((f, d.date(), a["fechamento"], fe))
            else:
                ab = mx = mn = fe = a["fechamento"]
                neg, vol = 0, 0
            vm = float(h["volume_dia (R$)"].iloc[-60:].mean())
            r = R[(R["fundo"] == f) & (R["data_conhecido"] <= d)]
            rend = float(r.sort_values("data_conhecido")["valor (R$/cota)"].iloc[-1]) if len(r) else a["rendimento_mensal (R$/cota)"]
            if len(r) and r["data_conhecido"].max() <= ult:
                rend = a["rendimento_mensal (R$/cota)"]           # nada novo anunciado: mantém o da linha anterior
            v = V[(V["prefixo"] == f[:4]) & (V["vale_de"] <= d)].sort_values("vale_de")
            if len(v) and v["vale_de"].iloc[-1] > ult:
                vp, pl = float(v["vp"].iloc[-1]), float(v["pl"].iloc[-1])
            else:
                vp, pl = a["valor_patrimonial_cota"], a["patrimonio (R$)"]
            nova = {"data": d, "fundo": f, "abertura": ab, "maxima": mx, "minima": mn, "fechamento": fe, "negociou (1/0)": neg,
                    "volume_dia (R$)": vol, "volume_medio_60 (R$)": round(vm), "rendimento_mensal (R$/cota)": rend,
                    "rendimento_ano_sobre_preco (%)": round(rend * 12 / fe * 100, 2) if pd.notna(rend) and fe else np.nan,
                    "valor_patrimonial_cota": round(vp, 4) if pd.notna(vp) else np.nan,
                    "preco_sobre_valor_patrimonial": round(fe / vp, 4) if pd.notna(vp) and vp else np.nan,
                    "patrimonio (R$)": round(pl) if pd.notna(pl) else np.nan, "amortizacao_12m (1/0)": a["amortizacao_12m (1/0)"]}
            linhas.append(nova)
            hist[f] = pd.concat([h, pd.DataFrame([nova])], ignore_index=True)
    N = pd.DataFrame(linhas)
    for c in ("volume_dia (R$)", "volume_medio_60 (R$)", "patrimonio (R$)", "negociou (1/0)", "amortizacao_12m (1/0)"):
        N[c] = N[c].astype("Int64")
    N["data"] = N["data"].dt.strftime("%d/%m/%Y")
    N.to_csv(arq, mode="a", header=False, index=False, sep=";", decimal=",", encoding="utf-8")
    print(f"acrescentados em {arq.relative_to(RAIZ)}: {len(N)} linhas, {len(dias)} pregões "
          f"({', '.join(f'{x:%d/%m}' for x in dias)}), {len(fundos)} fundos; com negócio: {int(N['negociou (1/0)'].sum())}")
    print(f"valor patrimonial novo da CVM aplicado: {int((N['valor_patrimonial_cota'] != N.groupby('fundo')['valor_patrimonial_cota'].transform('first')).sum())} linhas")
    print("códigos negociados que não estão na tabela (não acrescentados):", fora)
    print("variação de mais de 25% no fechamento (conferir):", saltos)
