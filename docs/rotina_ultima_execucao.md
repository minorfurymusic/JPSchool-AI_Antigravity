# Rotina diária — rodada de 26/11/2026 07:20 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (158s)

```
período 22/11/2026 a 26/11/2026: 345 documentos listados, 345 novos; resultado: {'texto': 161, 'lido': 21}
fnet_documentos_2026-11.csv: 827 -> 934 linhas
fnet_rendimentos_2026.csv: 93 -> 98 linhas
textos de PDF guardados: 161 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
planilhas/rendimentos.csv: +2 avisos novos do FNET (data conhecida = dia da entrega; depois das 18h, pregão seguinte)
```

## 3 preços dos FIIs (B3) — OK (3s)

```
tabela ia até 24/11/2026; arquivos da B3 baixados: 1; sem arquivo (feriado ou ainda não publicado): 26/11 (404)
planilhas/tecnico/b3_cotahist_fii_diario.csv: 1127 -> 1397 linhas; ia até 24/11/2026; pregões acrescentados: 25/11; 270 códigos
acrescentados em planilhas/precos_2026.csv: 253 linhas, 1 pregões (25/11), 253 fundos; com negócio: 211
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'DAMT11', 'DAYM11', 'EDGA11', 'FAMB11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'HUSC11', 'IBCR11', 'IMMB11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LASC11', 'MAGM11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PMRL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RJDA15', 'RSRV11', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPTW11', 'TRPL11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'VVMR11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): []
```

## 4 mercado de fundos e CDI — OK (1s)

```
mercado.csv: +1 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
25/11/2026          13.75                11.3438           1.609                211                                 0.7843
cdi.csv: +1 dias       data  cdi_ao_dia (%)  cdi_ao_ano (%)  indice_100_do_cdi  indice_105_do_cdi
24/11/2026        0.050788           13.65           2.410713           2.519119
```

## 5 dólar, IFIX e Ibovespa — OK (6s)

```
indicadores_diarios.csv: 2482 -> 2483 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
23/11/2026                 5.9708        3440.08          164796.05
24/11/2026                 5.8573        3467.64          164089.81
25/11/2026                 5.8825        3541.11          166684.61
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
titulos_publicos_anbima.csv: 350 -> 400 linhas
arquivos da ANBIMA lidos: 1; sem arquivo: 26/11 (404)
juro_real_10_anos.csv: 2461 -> 2462 linhas
NTN-B (juro real, IPCA+) em 25/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
25/11/2026  NTN-B 15/05/2027                      3.3955 4844.018719
25/11/2026  NTN-B 15/08/2028                      7.2601 4765.896013
25/11/2026  NTN-B 15/05/2029                      7.4183 4648.704786
25/11/2026  NTN-B 15/08/2030                      7.6656 4619.780893
25/11/2026  NTN-B 15/05/2031                      7.7395 4498.776471
25/11/2026  NTN-B 15/08/2032                      7.8266 4480.589731
25/11/2026  NTN-B 15/05/2033                      7.8400 4370.274678
25/11/2026  NTN-B 15/05/2035                      7.8479 4276.813182
25/11/2026  NTN-B 15/05/2037                      7.7469 4226.787700
25/11/2026  NTN-B 15/08/2040                      7.6151 4238.251176
25/11/2026  NTN-B 15/05/2045                      7.5917 4074.431937
25/11/2026  NTN-B 15/08/2050                      7.5953 4062.347264
25/11/2026  NTN-B 15/05/2055                      7.5726 3953.403624
25/11/2026  NTN-B 15/08/2060                      7.5755 3982.705014
```
