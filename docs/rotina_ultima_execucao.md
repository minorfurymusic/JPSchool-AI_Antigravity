# Rotina diária — rodada de 28/11/2026 06:41 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (247s)

```
período 23/11/2026 a 28/11/2026: 519 documentos listados, 519 novos; resultado: {'texto': 227, 'lido': 29}
fnet_documentos_2026-11.csv: 1028 -> 1108 linhas
fnet_rendimentos_2026.csv: 101 -> 107 linhas
textos de PDF guardados: 227 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
planilhas/rendimentos.csv: +1 avisos novos do FNET (data conhecida = dia da entrega; depois das 18h, pregão seguinte)
```

## 3 preços dos FIIs (B3) — OK (5s)

```
tabela ia até 26/11/2026; arquivos da B3 baixados: 1; sem arquivo (feriado ou ainda não publicado): nenhum
planilhas/tecnico/b3_cotahist_fii_diario.csv: 1678 -> 1956 linhas; ia até 26/11/2026; pregões acrescentados: 27/11; 278 códigos
acrescentados em planilhas/precos_2026.csv: 253 linhas, 1 pregões (27/11), 253 fundos; com negócio: 218
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BFCC11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'DAMT11', 'DAYM11', 'EDGA11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'HUSC11', 'IBCR11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LASC11', 'LMAI11', 'LRDI11', 'MAGM11', 'MCLO11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RSRV11', 'RTEL16', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPG215', 'SPTW11', 'TRUE11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): [('KNRE11', datetime.date(2026, 11, 27), np.float64(0.27), np.float64(0.19))]
```

## 4 mercado de fundos e CDI — OK (2s)

```
mercado.csv: +1 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
27/11/2026          13.75                11.3438          1.6568                218                                 0.7962
cdi.csv: +1 dias       data  cdi_ao_dia (%)  cdi_ao_ano (%)  indice_100_do_cdi  indice_105_do_cdi
26/11/2026        0.050788           13.65           2.413163           2.521806
```

## 5 dólar, IFIX e Ibovespa — OK (8s)

```
indicadores_diarios.csv: 2484 -> 2485 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
25/11/2026                 5.8825        3541.11          166684.61
26/11/2026                 5.7446        3578.98          176799.84
27/11/2026                 5.5430        3664.06          176573.35
```

## 6 IPCA e IGP-M — OK (2s)

```
indicadores_mensais.csv: 119 meses, último 11/2026
    mes  ipca_mes (%)  igpm_mes (%)  ipca_12_meses (%)  igpm_12_meses (%)
10/2026          0.14          1.47               4.63               5.25
11/2026           NaN          1.24                NaN               6.26
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
titulos_publicos_anbima.csv: 450 -> 500 linhas
arquivos da ANBIMA lidos: 1; sem arquivo: nenhum
juro_real_10_anos.csv: 2463 -> 2464 linhas
NTN-B (juro real, IPCA+) em 27/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
27/11/2026  NTN-B 15/05/2027                      3.3631 4847.062521
27/11/2026  NTN-B 15/08/2028                      7.0598 4784.068842
27/11/2026  NTN-B 15/05/2029                      7.2154 4672.615913
27/11/2026  NTN-B 15/08/2030                      7.3422 4669.571377
27/11/2026  NTN-B 15/05/2031                      7.3790 4562.071086
27/11/2026  NTN-B 15/08/2032                      7.4600 4557.908150
27/11/2026  NTN-B 15/05/2033                      7.4683 4455.689196
27/11/2026  NTN-B 15/05/2035                      7.4704 4380.751571
27/11/2026  NTN-B 15/05/2037                      7.3971 4337.616673
27/11/2026  NTN-B 15/08/2040                      7.2994 4356.041607
27/11/2026  NTN-B 15/05/2045                      7.2797 4207.820060
27/11/2026  NTN-B 15/08/2050                      7.2849 4206.883280
27/11/2026  NTN-B 15/05/2055                      7.2704 4101.275667
27/11/2026  NTN-B 15/08/2060                      7.2784 4132.643461
```
