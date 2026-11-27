# Rotina diária — rodada de 27/11/2026 07:26 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (205s)

```
período 23/11/2026 a 27/11/2026: 439 documentos listados, 439 novos; resultado: {'texto': 201, 'lido': 24}
fnet_documentos_2026-11.csv: 934 -> 1028 linhas
fnet_rendimentos_2026.csv: 98 -> 101 linhas
textos de PDF guardados: 201 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
planilhas/rendimentos.csv: +1 avisos novos do FNET (data conhecida = dia da entrega; depois das 18h, pregão seguinte)
```

## 3 preços dos FIIs (B3) — OK (3s)

```
tabela ia até 25/11/2026; arquivos da B3 baixados: 1; sem arquivo (feriado ou ainda não publicado): 27/11 (404)
planilhas/tecnico/b3_cotahist_fii_diario.csv: 1397 -> 1678 linhas; ia até 25/11/2026; pregões acrescentados: 26/11; 281 códigos
acrescentados em planilhas/precos_2026.csv: 253 linhas, 1 pregões (26/11), 253 fundos; com negócio: 224
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'CXTL11', 'DAMT11', 'DAYM11', 'DVLT11', 'EDGA11', 'FAMB11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'IBCR11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LMAI11', 'MAGM11', 'MCLO11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PMRL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RRES11', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPG215', 'SPTW11', 'TRPL11', 'TRUE11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): []
```

## 4 mercado de fundos e CDI — OK (3s)

```
mercado.csv: +1 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
26/11/2026          13.75                11.3438          1.6243                224                                 0.7901
cdi.csv: +1 dias       data  cdi_ao_dia (%)  cdi_ao_ano (%)  indice_100_do_cdi  indice_105_do_cdi
25/11/2026        0.050788           13.65           2.411938           2.520462
```

## 5 dólar, IFIX e Ibovespa — OK (11s)

```
indicadores_diarios.csv: 2483 -> 2484 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
24/11/2026                 5.8573        3467.64          164089.81
25/11/2026                 5.8825        3541.11          166684.61
26/11/2026                 5.7446        3578.98          176799.84
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
titulos_publicos_anbima.csv: 400 -> 450 linhas
arquivos da ANBIMA lidos: 1; sem arquivo: 27/11 (404)
juro_real_10_anos.csv: 2462 -> 2463 linhas
NTN-B (juro real, IPCA+) em 26/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
26/11/2026  NTN-B 15/05/2027                      3.3542 4846.471596
26/11/2026  NTN-B 15/08/2028                      7.1857 4773.505325
26/11/2026  NTN-B 15/05/2029                      7.3400 4658.715000
26/11/2026  NTN-B 15/08/2030                      7.5198 4642.718530
26/11/2026  NTN-B 15/05/2031                      7.5700 4528.893634
26/11/2026  NTN-B 15/08/2032                      7.6500 4518.077974
26/11/2026  NTN-B 15/05/2033                      7.6600 4411.809223
26/11/2026  NTN-B 15/05/2035                      7.6617 4328.075086
26/11/2026  NTN-B 15/05/2037                      7.5700 4282.714317
26/11/2026  NTN-B 15/08/2040                      7.4699 4292.378154
26/11/2026  NTN-B 15/05/2045                      7.4600 4130.592523
26/11/2026  NTN-B 15/08/2050                      7.4642 4123.041157
26/11/2026  NTN-B 15/05/2055                      7.4454 4015.171324
26/11/2026  NTN-B 15/08/2060                      7.4451 4047.885946
```
