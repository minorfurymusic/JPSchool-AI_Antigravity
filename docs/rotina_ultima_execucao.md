# Rotina diária — rodada de 25/11/2026 07:46 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (117s)

```
período 21/11/2026 a 25/11/2026: 231 documentos listados, 231 novos; resultado: {'texto': 121, 'lido': 17}
fnet_documentos_2026-11.csv: 718 -> 820 linhas
fnet_rendimentos_2026.csv: 87 -> 93 linhas
textos de PDF guardados: 121 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
nada novo: os 58 avisos do FNET já estão em planilhas/rendimentos.csv
```

## 3 preços dos FIIs (B3) — OK (3s)

```
tabela ia até 23/11/2026; arquivos da B3 baixados: 1; sem arquivo (feriado ou ainda não publicado): 25/11 (404)
acrescentados em planilhas/precos_2026.csv: 253 linhas, 1 pregões (24/11), 253 fundos; com negócio: 215
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'CXTL11', 'DAMT11', 'DAYM11', 'EDGA11', 'FAMB11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'HUSC11', 'IBCR11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LASC11', 'MAGM11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PMRL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RRES11', 'RTEL16', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPTW11', 'TRUE11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'VVMR11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): [('CARE11', datetime.date(2026, 11, 24), np.float64(3.09), np.float64(4.0)), ('KNRE11', datetime.date(2026, 11, 24), np.float64(0.17), np.float64(0.22)), ('VVRI11', datetime.date(2026, 11, 24), np.float64(6.6), np.float64(8.88))]
```

## 4 mercado de fundos e CDI — OK (2s)

```
mercado.csv: +1 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
24/11/2026          13.75                11.3438          1.5935                215                                 0.7697
cdi.csv: +1 dias       data  cdi_ao_dia (%)  cdi_ao_ano (%)  indice_100_do_cdi  indice_105_do_cdi
23/11/2026        0.050788           13.65            2.40949           2.517776
```

## 5 dólar, IFIX e Ibovespa — OK (6s)

```
indicadores_diarios.csv: 2481 -> 2482 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
19/11/2026                 5.8889        3485.06          166376.43
23/11/2026                 5.9708        3440.08          164796.05
24/11/2026                 5.8573        3467.64          164089.81
```

## 6 IPCA e IGP-M — OK (1s)

```
indicadores_mensais.csv: 118 meses, último 10/2026
    mes  ipca_mes (%)  igpm_mes (%)  ipca_12_meses (%)  igpm_12_meses (%)
09/2026          0.82          1.57               4.58               3.35
10/2026          0.14          1.47               4.63               5.25
```

## 7 Boletim Focus — OK (1s)

```
focus.csv: 14743 -> 14743 linhas (desde 09/11/2026)
      data indicador  ano_referencia  mediana
19/11/2026    Câmbio            2026   5.5500
19/11/2026    Câmbio            2027   5.5000
19/11/2026      IPCA            2026   5.1505
19/11/2026      IPCA            2027   5.1214
19/11/2026     Selic            2026  13.7500
19/11/2026     Selic            2027  13.0000
```

## 8 juros dos títulos públicos (ANBIMA) — OK (0s)

```
titulos_publicos_anbima.csv: 300 -> 350 linhas
arquivos da ANBIMA lidos: 1; sem arquivo: 25/11 (404)
juro_real_10_anos.csv: 2460 -> 2461 linhas
NTN-B (juro real, IPCA+) em 24/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
24/11/2026  NTN-B 15/05/2027                      3.4862 4840.472543
24/11/2026  NTN-B 15/08/2028                      7.2900 4761.495140
24/11/2026  NTN-B 15/05/2029                      7.4492 4643.418404
24/11/2026  NTN-B 15/08/2030                      7.6891 4614.222898
24/11/2026  NTN-B 15/05/2031                      7.7481 4495.181100
24/11/2026  NTN-B 15/08/2032                      7.8400 4475.736540
24/11/2026  NTN-B 15/05/2033                      7.8634 4363.048861
24/11/2026  NTN-B 15/05/2035                      7.8863 4264.669895
24/11/2026  NTN-B 15/05/2037                      7.7854 4213.129866
24/11/2026  NTN-B 15/08/2040                      7.6600 4220.291388
24/11/2026  NTN-B 15/05/2045                      7.6462 4050.359305
24/11/2026  NTN-B 15/08/2050                      7.6628 4030.675868
24/11/2026  NTN-B 15/05/2055                      7.6372 3921.671668
24/11/2026  NTN-B 15/08/2060                      7.6425 3948.970493
```
