# Rotina diária — rodada de 25/11/2026 10:14 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 documentos dos FIIs (FNET) — OK (125s)

```
período 21/11/2026 a 25/11/2026: 238 documentos listados, 238 novos; resultado: {'texto': 122, 'lido': 17}
fnet_documentos_2026-11.csv: 820 -> 827 linhas
fnet_rendimentos_2026.csv: 93 -> 93 linhas
textos de PDF guardados: 122 documentos
```

## 2 rendimentos novos na base de preços — OK (0s)

```
nada novo: os 58 avisos do FNET já estão em planilhas/rendimentos.csv
```

## 3 preços dos FIIs (B3) — OK (8s)

```
tabela ia até 24/11/2026; arquivos da B3 baixados: 4; sem arquivo (feriado ou ainda não publicado): 20/11 (404), 25/11 (404)
planilhas/tecnico/b3_cotahist_fii_diario.csv: 0 -> 1127 linhas; ia até 17/11/2026; pregões acrescentados: 18/11, 19/11, 23/11, 24/11; 309 códigos
nada novo: a tabela já vai até 24/11/2026
```

## 4 mercado de fundos e CDI — OK (0s)

```
nada novo: mercado.csv já vai até 24/11/2026 (preços até 24/11/2026)
```

## 5 dólar, IFIX e Ibovespa — OK (6s)

```
indicadores_diarios.csv: 2482 -> 2482 linhas (dólar: Banco Central; IFIX e Ibovespa: B3, desde 2017); dias sem valor: {'dolar_ptax_venda (R$)': 0, 'ifix (pontos)': 25, 'ibovespa (pontos)': 25}
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
arquivos da ANBIMA lidos: 0; sem arquivo: 25/11 (404)
```
