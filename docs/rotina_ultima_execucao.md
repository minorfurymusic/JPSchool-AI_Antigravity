# Rotina diária — rodada de 23/11/2026 07:50 (horário de Brasília)

Etapas com erro: 0. Saída literal de cada etapa abaixo.

## 1 preços dos FIIs (B3) — OK (1s)

```
tabela ia até 19/11/2026; arquivos da B3 baixados: 0; sem arquivo (feriado ou ainda não publicado): 20/11 (404), 23/11 (404)
```

## 2 mercado de fundos e CDI — OK (0s)

```
nada novo: mercado.csv já vai até 19/11/2026 (preços até 19/11/2026)
```

## 3 documentos dos FIIs (FNET) — OK (198s)

```
período 16/11/2026 a 23/11/2026: 589 documentos listados, 589 novos; resultado: {'lido': 63, 'texto': 170}
fnet_documentos_2026-11.csv: 589 -> 589 linhas
fnet_rendimentos_2026.csv: 71 -> 71 linhas
textos de PDF guardados: 170 documentos
```

## 4 dólar, IFIX e Ibovespa — OK (2s)

```
indicadores_diarios.csv: 2480 -> 2480 linhas (dólar desde 09/11/2026; IFIX: só o pregão de hoje, pela B3; Ibovespa pelo Yahoo Finance)
últimos dias:
      data  dolar_ptax_venda (R$)  ifix (pontos)  ibovespa (pontos)
17/11/2026                 5.7851            NaN           169817.0
18/11/2026                 5.8102            NaN           167538.0
19/11/2026                 5.8889        3485.06           166376.0
```

## 5 IPCA e IGP-M — OK (2s)

```
indicadores_mensais.csv: 118 meses, último 10/2026
    mes  ipca_mes (%)  igpm_mes (%)  ipca_12_meses (%)  igpm_12_meses (%)
09/2026          0.82          1.57               4.58               3.35
10/2026          0.14          1.47               4.63               5.25
```

## 6 Boletim Focus — OK (14s)

```
focus.csv: 0 -> 14719 linhas (desde 01/01/2017)
      data indicador  ano_referencia  mediana
13/11/2026    Câmbio            2026   5.4000
13/11/2026    Câmbio            2027   5.4500
13/11/2026      IPCA            2026   5.1082
13/11/2026      IPCA            2027   5.0000
13/11/2026     Selic            2026  13.7500
13/11/2026     Selic            2027  12.7500
```

## 7 juros futuros da B3 — OK (481s)

```
19/11 DI x pré: sem resposta da B3 (ReadTimeout: HTTPSConnectionPool(host='www2.bmf.com.br', port=443): Read timed out. (read timeout=120))
19/11 DI x IPCA: sem resposta da B3 (ReadTimeout: HTTPSConnectionPool(host='www2.bmf.com.br', port=443): Read timed out. (read timeout=120))
```
