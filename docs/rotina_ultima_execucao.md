# Rotina diária — rodada de 24/11/2026 08:55 (horário de Brasília)

Etapas com erro: 1. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (61s)

```
período 20/11/2026 a 24/11/2026: 129 documentos listados, 129 novos; resultado: {'texto': 62, 'lido': 12}
fnet_documentos_2026-11.csv: 590 -> 718 linhas
fnet_rendimentos_2026.csv: 71 -> 87 linhas
textos de PDF guardados: 62 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
planilhas/rendimentos.csv: +4 avisos novos do FNET (data conhecida = dia da entrega; depois das 18h, pregão seguinte)
```

## 3 preços dos FIIs (B3) — OK (5s)

```
tabela ia até 19/11/2026; arquivos da B3 baixados: 1; sem arquivo (feriado ou ainda não publicado): 20/11 (404), 24/11 (404)
acrescentados em planilhas/precos_2026.csv: 253 linhas, 1 pregões (23/11), 253 fundos; com negócio: 224
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'DAMT11', 'DAYM11', 'EDGA11', 'FAMB11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'HUSC11', 'IBCR11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LASC11', 'LMAI11', 'LRDI11', 'MAGM11', 'MCLO11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RTEL16', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPTW11', 'TRPL11', 'TRUE11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'VVMR11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): []
```

## 4 mercado de fundos e CDI — ERRO (3s)

```
Traceback (most recent call last):
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 424, in main
    saida, status = f(), "OK"
                    ^^^
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 199, in etapa_mercado
    return rodar(["estudos/atualizar_mercado_cdi.py"])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 82, in rodar
    raise RuntimeError(f"saiu com código {r.returncode}:\n{saida[-3000:]}")
RuntimeError: saiu com código 1:
mercado.csv: +1 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
23/11/2026          13.75                11.3438          1.5839                224                                 0.7657
Traceback (most recent call last):
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/atualizar_mercado_cdi.py", line 61, in <module>
    cdi = sgs(12, C["data"].max() + pd.Timedelta(days=1))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/atualizar_mercado_cdi.py", line 24, in sgs
    r.raise_for_status()
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/site-packages/requests/models.py", line 1167, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=20/11/2026

```

## 5 dólar, IFIX e Ibovespa — OK (8s)

```
indicadores_diarios.csv: 2480 -> 2481 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
18/11/2026                 5.8102        3513.11          167537.95
19/11/2026                 5.8889        3485.06          166376.43
23/11/2026                 5.9708        3440.08          164796.05
```

## 6 IPCA e IGP-M — OK (2s)

```
indicadores_mensais.csv: 118 meses, último 10/2026
    mes  ipca_mes (%)  igpm_mes (%)  ipca_12_meses (%)  igpm_12_meses (%)
09/2026          0.82          1.57               4.58               3.35
10/2026          0.14          1.47               4.63               5.25
```

## 7 Boletim Focus — OK (1s)

```
focus.csv: 14719 -> 14743 linhas (desde 03/11/2026)
      data indicador  ano_referencia  mediana
19/11/2026    Câmbio            2026   5.5500
19/11/2026    Câmbio            2027   5.5000
19/11/2026      IPCA            2026   5.1505
19/11/2026      IPCA            2027   5.1214
19/11/2026     Selic            2026  13.7500
19/11/2026     Selic            2027  13.0000
```

## 8 juros dos títulos públicos (ANBIMA) — OK (1s)

```
titulos_publicos_anbima.csv: 250 -> 300 linhas
arquivos da ANBIMA lidos: 1; sem arquivo: 20/11 (404), 24/11 (404)
juro_real_10_anos.csv: 2459 -> 2460 linhas
NTN-B (juro real, IPCA+) em 23/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
23/11/2026  NTN-B 15/05/2027                      3.5502 4837.481628
23/11/2026  NTN-B 15/08/2028                      7.3100 4757.812259
23/11/2026  NTN-B 15/05/2029                      7.4546 4640.675026
23/11/2026  NTN-B 15/08/2030                      7.6905 4611.790760
23/11/2026  NTN-B 15/05/2031                      7.7388 4494.529334
23/11/2026  NTN-B 15/08/2032                      7.8695 4467.684688
23/11/2026  NTN-B 15/05/2033                      7.8810 4357.086657
23/11/2026  NTN-B 15/05/2035                      7.9063 4257.355454
23/11/2026  NTN-B 15/05/2037                      7.8007 4206.474819
23/11/2026  NTN-B 15/08/2040                      7.6600 4218.253982
23/11/2026  NTN-B 15/05/2045                      7.6340 4053.340921
23/11/2026  NTN-B 15/08/2050                      7.6371 4040.004577
23/11/2026  NTN-B 15/05/2055                      7.6187 3928.288816
23/11/2026  NTN-B 15/08/2060                      7.6169 3959.174489
```
