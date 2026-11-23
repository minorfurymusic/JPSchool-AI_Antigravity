# Rotina diária — rodada de 23/11/2026 07:44 (horário de Brasília)

Etapas com erro: 1. Saída literal de cada etapa abaixo.

## 1 preços dos FIIs (B3) — OK (11s)

```
tabela ia até 17/11/2026; arquivos da B3 baixados: 2; sem arquivo (feriado ou ainda não publicado): 20/11 (404), 23/11 (404)
acrescentados em planilhas/precos_2026.csv: 506 linhas, 2 pregões (18/11, 19/11), 253 fundos; com negócio: 449
valor patrimonial novo da CVM aplicado: 0 linhas
códigos negociados que não estão na tabela (não acrescentados): ['AFHF11', 'APTO11', 'ARXD11', 'BGRB11', 'BSLT11', 'BTCI11', 'BTHF11', 'BTHI11', 'CPSH11', 'CXTL11', 'DAMT11', 'DAYM11', 'EDGA11', 'FAMB11', 'FYTO11', 'GSRF11', 'GZIT11', 'HCTR11', 'HUSC11', 'IBCR11', 'IMMB11', 'INHF11', 'JCCJ11', 'KNUQ11', 'LASC11', 'LMAI11', 'LRDI11', 'MAGM11', 'MCLO11', 'MCRE11', 'ONDA11', 'PCIP11', 'PLAG11', 'PMLL11', 'PMRL11', 'PQDP11', 'PSEC11', 'RBIC11', 'RBRY11', 'RECD11', 'RSRV11', 'RTEL16', 'RZLC11', 'RZZR11', 'SEQR11', 'SMRE11', 'SNEL11', 'SPG215', 'SPTW11', 'TRPL11', 'TRUE11', 'TRXF11', 'TVRI11', 'VIML11', 'VTOT11', 'VVCO11', 'VVMR11', 'XLPR11', 'XPML11', 'ZAGH11']
variação de mais de 25% no fechamento (conferir): [('KNRE11', datetime.date(2026, 11, 19), np.float64(0.25), np.float64(0.17)), ('SJAU11', datetime.date(2026, 11, 19), np.float64(0.7), np.float64(0.89))]
```

## 2 mercado de fundos e CDI — OK (2s)

```
mercado.csv: +2 dias       data  selic_ano (%)  selic_liquida_ano (%)  indice_mercado  fundos_negociados  mediana_preco_sobre_valor_patrimonial
18/11/2026          13.75                11.3438          1.6032                224                                 0.7786
19/11/2026          13.75                11.3438          1.5991                225                                 0.7806
cdi.csv: +2 dias       data  cdi_ao_dia (%)  cdi_ao_ano (%)  indice_100_do_cdi  indice_105_do_cdi
18/11/2026        0.050788           13.65           2.407044           2.515093
19/11/2026        0.050788           13.65           2.408267           2.516434
```

## 3 documentos dos FIIs (FNET) — OK (191s)

```
período 16/11/2026 a 23/11/2026: 589 documentos listados, 589 novos; resultado: {'lido': 63, 'texto': 170}
fnet_documentos_2026-11.csv: 0 -> 589 linhas
fnet_rendimentos_2026.csv: 0 -> 71 linhas
textos de PDF guardados: 170 documentos
```

## 4 dólar, IFIX e Ibovespa — OK (6s)

```
indicadores_diarios.csv: 0 -> 2480 linhas (desde 01/01/2017; IFIX e Ibovespa pelo Yahoo Finance)
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

## 6 Boletim Focus — ERRO (1s)

```
Traceback (most recent call last):
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 321, in main
    saida, status = f(), "OK"
                    ^^^
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 244, in etapa_focus
    r = get(base, params={"$filter": filtro, "$select": "Indicador,Data,DataReferencia,Mediana", "$format": "json",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/JPSchool-AI_Antigravity/JPSchool-AI_Antigravity/estudos/rotina_diaria.py", line 52, in get
    r.raise_for_status()
  File "/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/site-packages/requests/models.py", line 1167, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais?%24filter=%28Indicador+eq+%27Selic%27+or+Indicador+eq+%27IPCA%27+or+Indicador+eq+%27C%C3%A2mbio%27%29+and+Data+ge+%272017-01-01%27+and+baseCalculo+eq+0&%24select=Indicador%2CData%2CDataReferencia%2CMediana&%24format=json&%24top=5000&%24skip=0&%24orderby=Data

```

## 7 juros futuros da B3 — OK (61s)

```
19/11 DI x pré: sem resposta (ReadTimeout)
19/11 DI x IPCA: sem resposta (ImportError)
```
