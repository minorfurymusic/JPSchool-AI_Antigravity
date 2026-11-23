# Rotina diária — rodada de 23/11/2026 08:23 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 preços dos FIIs (B3) — OK (1s)

```
tabela ia até 19/11/2026; arquivos da B3 baixados: 0; sem arquivo (feriado ou ainda não publicado): 20/11 (404), 23/11 (404)
```

## 2 mercado de fundos e CDI — OK (0s)

```
nada novo: mercado.csv já vai até 19/11/2026 (preços até 19/11/2026)
```

## 3 documentos dos FIIs (FNET) — OK (186s)

```
período 16/11/2026 a 23/11/2026: 590 documentos listados, 590 novos; resultado: {'lido': 63, 'texto': 171}
fnet_documentos_2026-11.csv: 589 -> 590 linhas
fnet_rendimentos_2026.csv: 71 -> 71 linhas
textos de PDF guardados: 171 documentos
```

## 4 dólar, IFIX e Ibovespa — OK (6s)

```
indicadores_diarios.csv: 2480 -> 2480 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
17/11/2026                 5.7851        3542.29          169816.64
18/11/2026                 5.8102        3513.11          167537.95
19/11/2026                 5.8889        3485.06          166376.43
```

## 5 IPCA e IGP-M — OK (1s)

```
indicadores_mensais.csv: 118 meses, último 10/2026
    mes  ipca_mes (%)  igpm_mes (%)  ipca_12_meses (%)  igpm_12_meses (%)
09/2026          0.82          1.57               4.58               3.35
10/2026          0.14          1.47               4.63               5.25
```

## 6 Boletim Focus — OK (1s)

```
focus.csv: 14719 -> 14719 linhas (desde 03/11/2026)
      data indicador  ano_referencia  mediana
13/11/2026    Câmbio            2026   5.4000
13/11/2026    Câmbio            2027   5.4500
13/11/2026      IPCA            2026   5.1082
13/11/2026      IPCA            2027   5.0000
13/11/2026     Selic            2026  13.7500
13/11/2026     Selic            2027  12.7500
```

## 7 juros dos títulos públicos (ANBIMA) — OK (1s)

```
titulos_publicos_anbima.csv: 0 -> 250 linhas
arquivos da ANBIMA lidos: 5; sem arquivo: 03/11 (404), 04/11 (404), 05/11 (404), 06/11 (404), 09/11 (404), 10/11 (404), 11/11 (404), 12/11 (404), 20/11 (404), 23/11 (404)
NTN-B (juro real, IPCA+) em 19/11/2026:
      data titulo vencimento  taxa_indicativa (% ao ano)     pu (R$)
19/11/2026  NTN-B 15/05/2027                      3.7200 4832.122914
19/11/2026  NTN-B 15/08/2028                      7.4300 4746.866731
19/11/2026  NTN-B 15/05/2029                      7.5643 4627.521448
19/11/2026  NTN-B 15/08/2030                      7.7740 4597.740047
19/11/2026  NTN-B 15/05/2031                      7.8001 4482.282201
19/11/2026  NTN-B 15/08/2032                      7.9112 4457.223989
19/11/2026  NTN-B 15/05/2033                      7.9315 4343.996405
19/11/2026  NTN-B 15/05/2035                      7.9660 4239.718523
19/11/2026  NTN-B 15/05/2037                      7.8470 4190.542917
19/11/2026  NTN-B 15/08/2040                      7.6800 4209.153905
19/11/2026  NTN-B 15/05/2045                      7.6571 4042.056180
19/11/2026  NTN-B 15/08/2050                      7.6526 4031.253498
19/11/2026  NTN-B 15/05/2055                      7.6316 3920.466307
19/11/2026  NTN-B 15/08/2060                      7.6336 3949.368974
```
