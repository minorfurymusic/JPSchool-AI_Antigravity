# Simulação: R$ 10.000 de 01/01/2026 a 31/10/2026, em três perfis

Feita em 2026-11-13 com `estudos/simulacao.py` e `estudos/simulacao_sorteio.py`.
Para refazer: `PYTHONPATH=. .venv/bin/python estudos/simulacao.py`.

É uma simulação com dados passados. Não é recomendação e não garante resultado.

## Os três perfis

Escritos antes de rodar 2026 e não ajustados depois de ver o resultado.

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Compra quando | o fundo declara aumento de rendimento em fato relevante; ou o aviso seguinte a um salto continua alto | os do conservador; mais fato relevante que informa valor por cota de 3% do preço ou mais; mais aviso de rendimento 25% acima dos anteriores | os do moderado; mais fato relevante bom só pelo assunto (venda com ganho, locação nova, recebimento) |
| Fundos aceitos | R$ 1 milhão negociado por dia ou mais | R$ 300 mil por dia ou mais | R$ 200 mil por dia ou mais |
| Quanto por operação | 10% do patrimônio | 20% | 33% |
| Operações ao mesmo tempo | até 5 | até 5 | até 3 |
| Ordem de venda (alvo) | +3% | +5% | +10% |
| Limite de perda | −3% | −5% | −8% |
| Prazo máximo | 15 pregões | 20 pregões | 30 pregões |

Regras iguais nos três:

- **Entrada**: na abertura do pregão seguinte ao anúncio (anúncio antes das 10h: mesmo dia).
- **Saída**: o que vier primeiro entre alvo, limite de perda, prazo, ou fato relevante em que o fundo declara redução de rendimento (vende na abertura seguinte).
- **Dinheiro parado**: rende a Selic do dia, descontados 22,5% de imposto.
- **Depois de vender um fundo**: 20 pregões sem recomprar o mesmo.

## Como a execução foi simulada

- Alvo executado se a máxima do dia tocar o preço; limite de perda, se a mínima tocar.
- Se os dois forem tocados no mesmo dia, vale a perda (não há a ordem dentro do dia).
- Abertura além do preço da ordem executa na abertura.
- Cotas inteiras.

## Custos

- Corretagem zero.
- Taxas da B3: 0,03% por operação.
- Imposto de 20% sobre o ganho líquido do mês em vendas, com prejuízo compensando ganhos seguintes.
- Rendimentos isentos, creditados na data de pagamento a quem tinha a cota no fechamento da data-base.

## Resultado de 2026

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Patrimônio final | R$ 10.566,23 | R$ 11.004,87 | R$ 12.296,93 |
| Resultado | +5,66% | +10,05% | +22,97% |
| Operações | 16 | 41 | 24 |
| Operações com ganho | 25% | 63% | 67% |
| Resultado médio por operação | −1,70% | +0,83% | +2,93% |
| Rendimentos recebidos | R$ 27,27 | R$ 445,54 | R$ 998,50 |
| Imposto pago | R$ 0,00 | R$ 98,34 | R$ 294,86 |
| Pior queda do patrimônio no caminho | −1,24% | −5,12% | −5,45% |
| Sinais ignorados por falta de dinheiro ou de vaga | 0 | 13 | 96 |

Comparações no mesmo período:

- Deixar tudo no caixa: R$ 10.900,83 (+9,01%).
- Comprar os 30 fundos mais negociados em janeiro e não mexer, com rendimentos: R$ 9.805,40 (−1,95%).

As operações, uma a uma, com datas e preços, estão em `docs/simulacao_2026_conservador.csv`, `docs/simulacao_2026_moderado.csv` e `docs/simulacao_2026_agressivo.csv`, e na saída literal abaixo.

## As mesmas regras de 2018 a 2025

R$ 10.000 em 1º de janeiro de cada ano, até 31 de dezembro.

| Ano | Caixa | 30 fundos mantidos | Conservador | Moderado | Agressivo |
|---|---|---|---|---|---|
| 2018 | +4,9% | +18,0% | +5,0% | +9,1% | +25,6% |
| 2019 | +4,6% | +42,8% | +6,4% | +29,7% | +49,3% |
| 2020 | +2,2% | −6,8% | +4,0% | +21,4% | +37,4% |
| 2021 | +3,4% | +6,7% | +3,5% | +8,1% | +25,2% |
| 2022 | +9,5% | +13,2% | +9,3% | +32,7% | +21,7% |
| 2023 | +10,0% | +21,3% | +8,4% | +43,5% | +68,9% |
| 2024 | +8,3% | +0,3% | +6,7% | +22,1% | +1,8% |
| 2025 | +10,9% | +20,8% | +10,9% | +22,2% | +17,6% |
| Média | +6,7% | +14,5% | +6,8% | +23,6% | +30,9% |

Pior queda do patrimônio dentro de um ano: moderado −16,8% e agressivo −22,6%, os dois em 2020.

## Teste de sorteio: o ganho vem dos sinais ou das regras?

Mesmos dias de compra e mesmas regras de saída, mas com o fundo sorteado entre os que tinham liquidez. 30 sorteios por ano e perfil.

| Perfil | Média com os sinais | Média do sorteio típico | Anos em que os sinais ganharam do sorteio típico | Sorteios que renderam mais que os sinais |
|---|---|---|---|---|
| Conservador | +6,7% | +7,3% | 1 de 9 | 183 de 270 |
| Moderado | +22,1% | +11,4% | 8 de 9 | 51 de 270 |
| Agressivo | +30,0% | +13,4% | 8 de 9 | 53 de 270 |

Em 2026: moderado +10,0% com os sinais contra +2,5% no sorteio típico (2 de 30 sorteios foram melhores); agressivo +23,0% contra −4,3% (nenhum dos 30 foi melhor).

## Leitura

- **Cerca de metade do resultado não vem dos sinais.** Comprar fundos sorteados nas mesmas datas, com as mesmas regras de saída, rendeu 11% a 13% ao ano. É o mercado de FIIs mais a disciplina de alvo e limite.
- **Os sinais acrescentam a outra metade** nos perfis moderado e agressivo: em 8 de 9 anos ficaram acima do sorteio típico.
- **O perfil conservador não funciona.** Rendeu menos que o caixa em 2026 e menos que o sorteio em 8 de 9 anos. O alvo de 3% com limite de 3% é apertado demais: 9 das 16 operações de 2026 saíram pelo limite de perda, 3 delas no próprio dia da compra.
- **O gatilho "aviso seguinte continuou alto" foi o pior de 2026**: perdeu em 8 de 10 operações no conservador e em 4 de 5 no moderado.
- **O aviso de salto foi o que mais contribuiu em 2026**: 26 operações no moderado, 69% com ganho, +1,6% por operação.
- **O agressivo deixou 96 sinais sem comprar** por estar sempre cheio. O resultado dele depende de quais sinais chegaram primeiro.
- **O resultado por operação é pequeno** (+0,8% no moderado). O resultado do ano vem de repetir isso 40 a 60 vezes com 20% do patrimônio.

## Limites

- **A execução é otimista.** Supõe que a ordem é executada sempre que o preço é tocado e que há cotas na abertura pelo preço de abertura. Em fundo com pouco negócio isso nem sempre acontece.
- **Os perfis não foram otimizados nem conferidos fora da amostra de forma separada**: foram escritos de uma vez e rodados em todos os anos. O teste de sorteio é a defesa contra autoengano, não uma prova.
- **A leitura dos fatos relevantes é por palavras**, com os erros já descritos em `docs/ESTUDO_DIAS.md`.
- **O imposto sobre o caixa é uma aproximação** (22,5% sobre o rendimento diário).
- **Amortização entra como dinheiro recebido**, sem tratamento fiscal próprio.
- **A hora de entrega do FNET é presumida** como horário de Brasília.
- **Resultado passado não garante o próximo.** Nos estudos anteriores o efeito dos sinais vinha diminuindo ano a ano.

## Saída literal da simulação

```
PERFIS (definidos antes de rodar):
  conservador: só o sinal mais forte, fundos grandes, 10% por operação, sai cedo | compra em: FR_AUMENTO, AVISO_CONFIRMADO | liquidez mínima R$ 1,000,000/dia | 10% do patrimônio por operação, até 5 ao mesmo tempo | ordem de venda em +3% | limite de perda -3% | prazo 15 pregões
  moderado: sinais fortes e aviso de salto, 20% por operação | compra em: FR_AUMENTO, FR_VALOR, AVISO_CONFIRMADO, AVISO_SALTO | liquidez mínima R$ 300,000/dia | 20% do patrimônio por operação, até 5 ao mesmo tempo | ordem de venda em +5% | limite de perda -5% | prazo 20 pregões
  agressivo: qualquer sinal, 33% por operação, alvo alto e prazo longo | compra em: FR_AUMENTO, FR_VALOR, AVISO_SALTO, AVISO_CONFIRMADO, FR_ASSUNTO | liquidez mínima R$ 200,000/dia | 33% do patrimônio por operação, até 3 ao mesmo tempo | ordem de venda em +10% | limite de perda -8% | prazo 30 pregões

Sinais em 2026 (2026-01-01 a 2026-10-31): {'FR_ASSUNTO': 60, 'AVISO_SALTO': 38, 'AVISO_CONFIRMADO': 21, 'FR_AUMENTO': 8, 'FR_VALOR': 7, 'FR_REDUCAO': 1}

==============================================================================================================
R$ 10,000 DE 2026-01-01 A 2026-10-31
==============================================================================================================
     perfil  final R$  resultado %  operações  com ganho  resultado médio por operação %  pregões por operação  rendimentos recebidos R$  imposto pago R$  pior queda do patrimônio %  sinais sem dinheiro ou vaga
conservador  10566.23         5.66         16       0.25                           -1.70                   7.0                     27.27             0.00                       -1.24                            0
   moderado  11004.87        10.05         41       0.63                            0.83                  20.0                    445.54            98.34                       -5.12                           13
  agressivo  12296.93        22.97         24       0.67                            2.93                  30.0                    998.50           294.86                       -5.45                           96
Comparações: tudo no caixa R$ 10,900.83 (+9.01%) | 30 fundos mais negociados, comprados em 2026 e mantidos, com rendimentos: R$ 9,805.40 (-1.95%)

--- CONSERVADOR: operações ---
 fundo          gatilho          anuncio    entrada  cotas  preco_entrada  aplicado      saida  preco_saida  pregoes                          motivo  ganho_na_cota  rendimento_recebido  resultado  resultado_pct
HGBS11       FR_AUMENTO 2026-03-03 19:30 2026-03-04     49          20.56   1007.74 2026-03-25        20.20       15                  prazo esgotado         -18.24                 0.00     -18.24          -1.81
HPDP11 AVISO_CONFIRMADO 2026-03-31 17:01 2026-04-01     10         100.00   1000.30 2026-04-01        97.00        0                 limite de perda         -30.59                 0.00     -30.59          -3.06
TRBL11 AVISO_CONFIRMADO 2026-04-30 17:01 2026-05-04     13          74.25    965.54 2026-05-04        72.02        0                 limite de perda         -29.53                 0.00     -29.53          -3.06
RBVA11       FR_AUMENTO 2026-05-04 09:25 2026-05-04    104           9.85   1024.71 2026-05-11         9.55        5                 limite de perda         -31.34                 0.00     -31.34          -3.06
TEPP11 AVISO_CONFIRMADO 2026-04-30 17:03 2026-05-04    115           8.91   1024.96 2026-05-12         8.64        6 abriu abaixo do limite de perda         -31.66                 0.00     -31.66          -3.09
RECR11 AVISO_CONFIRMADO 2026-05-08 10:02 2026-05-11     12          82.49    990.18 2026-05-13        80.02        2                 limite de perda         -30.28                 0.00     -30.28          -3.06
RCRB11       FR_AUMENTO 2026-04-29 09:09 2026-04-29      7         140.49    983.73 2026-05-21       139.32       15                  prazo esgotado          -8.78                 7.49      -1.29          -0.13
KNIP11 AVISO_CONFIRMADO 2026-04-30 17:19 2026-05-04     11          93.50   1028.81 2026-05-25        92.55       15                  prazo esgotado         -11.06                 0.00     -11.06          -1.08
HGBS11       FR_AUMENTO 2026-05-19 18:54 2026-05-20     52          19.49   1013.78 2026-05-29        20.07        7                   alvo atingido          29.79                 0.00      29.79           2.94
VGIP11 AVISO_CONFIRMADO 2026-06-11 17:08 2026-06-12     13          78.59   1021.98 2026-06-30        80.95       12                   alvo atingido          30.03                 0.00      30.03           2.94
RBVA11       FR_AUMENTO 2026-06-29 09:40 2026-06-29    114           9.04   1030.87 2026-07-20         9.05       15                  prazo esgotado           0.52                10.26      10.78           1.05
KNHY11 AVISO_CONFIRMADO 2026-06-30 17:56 2026-07-01     10          99.24    992.70 2026-07-22        99.88       15                  prazo esgotado           5.80                 0.00       5.80           0.58
VCJR11 AVISO_CONFIRMADO 2026-07-31 17:22 2026-08-03     14          71.00    994.30 2026-08-03        68.87        0                 limite de perda         -30.41                 0.00     -30.41          -3.06
PATC11 AVISO_CONFIRMADO 2026-08-31 17:00 2026-09-01     26          39.05   1015.60 2026-09-11        37.37        7 abriu abaixo do limite de perda         -44.28                 0.00     -44.28          -4.36
HGBS11       FR_AUMENTO 2026-09-10 20:25 2026-09-11     56          18.68   1046.39 2026-10-01        18.12       14                 limite de perda         -32.00                 9.52     -22.48          -2.15
CPOF11 AVISO_CONFIRMADO 2026-10-16 17:14 2026-10-19      8         118.00    944.28 2026-10-21       110.00        2 abriu abaixo do limite de perda         -64.55                 0.00     -64.55          -6.84
Por gatilho:
                  operações  com_ganho  resultado_R  médio_pct
gatilho                                                       
AVISO_CONFIRMADO         10       0.20      -236.53      -2.41
FR_AUMENTO                6       0.33       -32.78      -0.53
Por motivo de saída:
                                 operações  resultado_R  médio_pct
motivo                                                            
abriu abaixo do limite de perda          3      -140.49      -4.76
alvo atingido                            2        59.82       2.94
limite de perda                          6      -174.63      -2.91
prazo esgotado                           5       -14.01      -0.28
Patrimônio no fim de cada mês: 01/26 10,091 | 02/26 10,169 | 03/26 10,240 | 04/26 10,304 | 05/26 10,255 | 06/26 10,377 | 07/26 10,472 | 08/26 10,531 | 09/26 10,560 | 10/26 10,566

--- MODERADO: operações ---
 fundo          gatilho          anuncio    entrada  cotas  preco_entrada  aplicado      saida  preco_saida  pregoes                          motivo  ganho_na_cota  rendimento_recebido  resultado  resultado_pct
CXCO11      AVISO_SALTO 2025-12-30 18:17 2026-01-02     29          67.05   1945.03 2026-01-14        70.40        8                   alvo atingido          96.03                 0.00      96.03           4.94
BCIA11      AVISO_SALTO 2025-12-30 15:10 2026-01-02     22          87.94   1935.26 2026-01-26        92.34       16                   alvo atingido          95.54                 0.00      95.54           4.94
ITRI11      AVISO_SALTO 2025-12-30 18:04 2026-01-02     23          84.30   1939.48 2026-01-27        88.52       17                   alvo atingido          95.75                 0.00      95.75           4.94
CYCR11      AVISO_SALTO 2025-12-30 18:02 2026-01-02    227           8.79   1995.93 2026-01-30         9.23       20                   alvo atingido          98.54                 0.00      98.54           4.94
CJCT11      AVISO_SALTO 2025-12-30 18:01 2026-01-02     31          63.20   1959.79 2026-01-30        64.93       20                  prazo esgotado          52.44                 7.44      59.88           3.06
RINV11      AVISO_SALTO 2026-01-14 18:02 2026-01-15     18         108.40   1951.79 2026-02-12       111.00       20                  prazo esgotado          45.62                19.80      65.42           3.35
AIEC11         FR_VALOR 2026-02-12 18:32 2026-02-13     38          54.40   2067.82 2026-02-13        57.12        0                   alvo atingido         102.09                 0.00     102.09           4.94
APXM11 AVISO_CONFIRMADO 2026-02-20 18:08 2026-02-23     26          79.00   2054.62 2026-02-23        75.05        0                 limite de perda        -103.90                 0.00    -103.90          -5.06
HPDP11      AVISO_SALTO 2026-02-27 18:23 2026-03-02     22          95.20   2095.03 2026-03-09        90.44        5                 limite de perda        -105.95                 0.00    -105.95          -5.06
HGBS11       FR_AUMENTO 2026-03-03 19:30 2026-03-04    102          20.56   2097.75 2026-04-01        20.45       20                  prazo esgotado         -12.47                17.34       4.87           0.23
KCRE11      AVISO_SALTO 2026-03-31 17:06 2026-04-01    235           8.90   2092.13 2026-04-22         9.35       13                   alvo atingido         103.29                 0.00     103.29           4.94
BBFO11      AVISO_SALTO 2026-03-31 17:02 2026-04-01     28          72.87   2040.97 2026-05-04        71.82       20                  prazo esgotado         -30.62                26.32      -4.30          -0.21
KNIP11      AVISO_SALTO 2026-03-31 17:06 2026-04-01     23          90.61   2084.66 2026-05-04        92.94       20                  prazo esgotado          52.32                25.30      77.62           3.72
TEPP11      AVISO_SALTO 2026-03-31 17:14 2026-04-01    232           9.00   2088.63 2026-05-04         8.74       20                  prazo esgotado         -61.55                30.39     -31.16          -1.49
RECR11      AVISO_SALTO 2026-04-08 10:35 2026-04-09     25          80.78   2020.11 2026-05-11        80.85       20                  prazo esgotado           0.54                26.31      26.85           1.33
RCRB11       FR_AUMENTO 2026-04-29 09:09 2026-04-29     15         140.49   2107.98 2026-05-28       140.70       20                  prazo esgotado           1.88                16.05      17.93           0.85
HGLG11         FR_VALOR 2026-05-04 20:41 2026-05-05     13         156.00   2028.61 2026-06-02       154.12       20                  prazo esgotado         -25.65                14.30     -11.35          -0.56
EMET11      AVISO_SALTO 2026-06-08 10:32 2026-06-09    254           8.44   2144.40 2026-06-09         8.86        0                   alvo atingido         105.87                 0.00     105.87           4.94
VGIP11      AVISO_SALTO 2026-05-13 17:06 2026-05-14     26          79.43   2065.80 2026-06-12        79.16       20                  prazo esgotado          -8.26                27.30      19.04           0.92
RZAT11 AVISO_CONFIRMADO 2026-05-15 17:05 2026-05-18     22          96.95   2133.54 2026-06-16        95.55       20                  prazo esgotado         -32.07                37.40       5.33           0.25
HGBS11       FR_AUMENTO 2026-05-19 18:54 2026-05-20    109          19.49   2125.05 2026-06-18        19.54       20                  prazo esgotado           4.17                18.53      22.70           1.07
KNHY11      AVISO_SALTO 2026-05-29 17:28 2026-06-01     21          99.25   2084.88 2026-06-30       100.17       20                  prazo esgotado          18.06                25.20      43.26           2.08
TRXB11      AVISO_SALTO 2026-06-30 16:49 2026-07-01     12         170.03   2040.97 2026-07-02       179.70        1             abriu acima do alvo         114.78                 0.00     114.78           5.62
OUJP11 AVISO_CONFIRMADO 2026-06-30 18:00 2026-07-01     28          75.62   2118.00 2026-07-07        71.84        4                 limite de perda        -107.11                 0.00    -107.11          -5.06
EMET11 AVISO_CONFIRMADO 2026-07-07 17:22 2026-07-08    229           9.48   2171.57 2026-07-08         9.01        0                 limite de perda        -109.82                 0.00    -109.82          -5.06
HGRE11      AVISO_SALTO 2026-06-30 17:47 2026-07-01     17         125.33   2131.25 2026-07-24       119.06       17                 limite de perda        -107.78                 0.00    -107.78          -5.06
RBVA11       FR_AUMENTO 2026-06-29 09:40 2026-06-29    241           9.04   2179.29 2026-07-27         8.95       20                  prazo esgotado         -22.99                21.69      -1.30          -0.06
HTMX11      AVISO_SALTO 2026-06-30 17:26 2026-07-01     15         137.05   2056.37 2026-07-29       138.94       20                  prazo esgotado          27.11                 0.00      27.11           1.32
CLIN11      AVISO_SALTO 2026-07-08 17:14 2026-07-09     23          89.70   2063.72 2026-08-06        88.83       20                  prazo esgotado         -21.24                 0.00     -21.24          -1.03
IRIM11      AVISO_SALTO 2026-07-09 17:08 2026-07-10     32          65.93   2110.39 2026-08-07        64.54       20                  prazo esgotado         -45.73                 0.00     -45.73          -2.17
VCJR11 AVISO_CONFIRMADO 2026-07-31 17:22 2026-08-03     30          71.00   2130.64 2026-08-10        67.45        5                 limite de perda        -107.75                 0.00    -107.75          -5.06
PATC11      AVISO_SALTO 2026-07-31 16:57 2026-08-03     53          40.00   2120.64 2026-08-20        37.42       13 abriu abaixo do limite de perda        -137.97                 0.00    -137.97          -6.51
TRXB11         FR_VALOR 2026-08-21 18:55 2026-08-24     11         186.85   2055.97 2026-08-24       177.51        0                 limite de perda        -103.97                 0.00    -103.97          -5.06
RBRP11         FR_VALOR 2026-09-10 19:16 2026-09-11     44          46.99   2068.18 2026-09-16        49.34        3                   alvo atingido         102.11                 0.00     102.11           4.94
HGRE11         FR_VALOR 2026-08-28 19:29 2026-08-31     17         116.41   1979.56 2026-09-29       116.07       20                  prazo esgotado          -6.97                14.45       7.48           0.38
RPRI11      AVISO_SALTO 2026-08-31 17:25 2026-09-01     29          72.00   2088.63 2026-09-30        72.00       20                  prazo esgotado          -1.25                18.85      17.60           0.84
RBRL11      AVISO_SALTO 2026-09-30 11:52 2026-10-01     27          76.00   2052.62 2026-10-06        79.80        3                   alvo atingido         101.34                 0.00     101.34           4.94
HGBS11       FR_AUMENTO 2026-09-10 20:25 2026-09-11    111          18.68   2074.10 2026-10-09        19.61       20                   alvo atingido         102.40                18.87     121.27           5.85
CPOF11      AVISO_SALTO 2026-09-16 17:16 2026-09-17     18         115.00   2070.62 2026-10-16       118.00       20                  prazo esgotado          52.74                36.00      88.74           4.29
VVRI11      AVISO_SALTO 2026-10-19 16:33 2026-10-20    295           7.35   2168.90 2026-10-20         7.72        0                   alvo atingido         107.08                 0.00     107.08           4.94
AFHI11      AVISO_SALTO 2026-10-14 16:32 2026-10-15     22          97.45   2144.54 2026-10-26        92.58        7                 limite de perda        -108.45                44.00     -64.45          -3.01
Por gatilho:
                  operações  com_ganho  resultado_R  médio_pct
gatilho                                                       
AVISO_CONFIRMADO          5       0.20      -423.25      -4.00
AVISO_SALTO              26       0.69       825.16       1.60
FR_AUMENTO                5       0.80       165.47       1.59
FR_VALOR                  5       0.60        96.36       0.93
Por motivo de saída:
                                 operações  resultado_R  médio_pct
motivo                                                            
abriu abaixo do limite de perda          1      -137.97      -6.51
abriu acima do alvo                      1       114.78       5.62
alvo atingido                           11      1128.91       5.02
limite de perda                          8      -810.73      -4.80
prazo esgotado                          20       368.75       0.91
Patrimônio no fim de cada mês: 01/26 10,425 | 02/26 10,500 | 03/26 10,458 | 04/26 10,790 | 05/26 10,799 | 06/26 10,924 | 07/26 10,712 | 08/26 10,456 | 09/26 10,606 | 10/26 11,005

--- AGRESSIVO: operações ---
 fundo          gatilho          anuncio    entrada  cotas  preco_entrada  aplicado      saida  preco_saida  pregoes          motivo  ganho_na_cota  rendimento_recebido  resultado  resultado_pct
BCIA11      AVISO_SALTO 2025-12-30 15:10 2026-01-02     37          87.94   3254.76 2026-01-30        96.73       20   alvo atingido         323.33                 0.00     323.33           9.93
CJCT11      AVISO_SALTO 2025-12-30 18:01 2026-01-02     52          63.20   3287.39 2026-02-13        64.20       30  prazo esgotado          50.01                12.48      62.49           1.90
CYCR11      AVISO_SALTO 2025-12-30 18:02 2026-01-02    375           8.79   3297.24 2026-02-13         9.08       30  prazo esgotado         106.74                39.75     146.49           4.44
KIVO11      AVISO_SALTO 2026-01-30 16:02 2026-02-02     51          68.10   3474.14 2026-03-18        63.57       30  prazo esgotado        -233.04                43.86    -189.18          -5.45
BRCO11       FR_ASSUNTO 2026-02-19 18:31 2026-02-20     28         118.70   3324.60 2026-04-06       114.79       30  prazo esgotado        -111.44                51.52     -59.92          -1.80
RBVA11       FR_ASSUNTO 2026-02-20 09:02 2026-02-20    345           9.92   3423.43 2026-04-06         9.70       30  prazo esgotado         -77.93                62.10     -15.83          -0.46
HOFC11       FR_ASSUNTO 2026-03-27 19:08 2026-03-30    104          32.14   3343.56 2026-05-14        33.50       30  prazo esgotado         139.39                 0.00     139.39           4.17
RECR11      AVISO_SALTO 2026-04-08 10:35 2026-04-09     41          80.78   3312.97 2026-05-25        81.28       30  prazo esgotado          18.51                43.15      61.66           1.86
CPLG11       FR_ASSUNTO 2026-05-27 19:06 2026-05-28    311          11.19   3481.13 2026-06-01        12.31        2   alvo atingido         345.82                 0.00     345.82           9.93
RZAT11      AVISO_SALTO 2026-04-15 17:32 2026-04-16     36          93.76   3376.37 2026-06-01        97.50       30  prazo esgotado         132.57                61.20     193.77           5.74
EMET11      AVISO_SALTO 2026-06-08 10:32 2026-06-09    427           8.44   3604.96 2026-06-09         9.28        0   alvo atingido         358.12                 0.00     358.12           9.93
HGRU11       FR_ASSUNTO 2026-05-14 19:48 2026-05-15     26         129.82   3376.33 2026-06-29       130.67       30  prazo esgotado          20.07                24.70      44.77           1.33
KNHY11      AVISO_SALTO 2026-05-29 17:28 2026-06-01     36          99.25   3574.07 2026-07-14       100.26       30  prazo esgotado          34.21                43.20      77.41           2.17
VGIP11 AVISO_CONFIRMADO 2026-06-11 17:08 2026-06-12     47          78.59   3694.84 2026-07-24        79.04       30  prazo esgotado          18.93                54.52      73.45           1.99
GGRC11       FR_ASSUNTO 2026-06-29 18:30 2026-06-30    385           9.84   3789.54 2026-08-11         9.59       30  prazo esgotado         -98.49                77.00     -21.49          -0.57
SNFF11      AVISO_SALTO 2026-07-15 09:13 2026-07-15     50          73.70   3686.11 2026-08-17        67.80       23 limite de perda        -296.92                91.00    -205.92          -5.59
HGLG11       FR_ASSUNTO 2026-07-30 18:28 2026-07-31     25         147.48   3688.11 2026-09-14       147.87       30  prazo esgotado           7.53                58.50      66.03           1.79
RBRX11       FR_ASSUNTO 2026-08-11 19:24 2026-08-12    506           7.39   3740.46 2026-09-24         7.15       30  prazo esgotado        -123.65                91.08     -32.57          -0.87
XPLG11       FR_ASSUNTO 2026-08-17 19:33 2026-08-18     41          88.55   3631.64 2026-09-30        92.51       30  prazo esgotado         160.13                67.24     227.37           6.26
RBRL11      AVISO_SALTO 2026-09-30 11:52 2026-10-01     50          76.00   3801.14 2026-10-08        83.60        5   alvo atingido         377.61                 0.00     377.61           9.93
LVBI11       FR_ASSUNTO 2026-09-29 20:39 2026-09-30     39          97.00   3784.13 2026-10-22       106.70       15   alvo atingido         375.92                31.20     407.12          10.76
CPOF11      AVISO_SALTO 2026-09-16 17:16 2026-09-17     32         115.00   3681.10 2026-10-30       120.00       30  prazo esgotado         157.74                64.00     221.74           6.02
AFHI11      AVISO_SALTO 2026-10-14 16:32 2026-10-15     41          97.45   3996.65 2026-10-30        93.00       11  fim do período        -184.79                82.00    -102.79          -2.57
ADSH11       FR_ASSUNTO 2026-10-23 17:58 2026-10-26    393          10.46   4112.01 2026-10-30        10.40        4  fim do período         -26.04                 0.00     -26.04          -0.63
Por gatilho:
                  operações  com_ganho  resultado_R  médio_pct
gatilho                                                       
AVISO_CONFIRMADO          1       1.00        73.45       1.99
AVISO_SALTO              12       0.75      1324.73       3.19
FR_ASSUNTO               11       0.55      1074.65       2.72
Por motivo de saída:
                 operações  resultado_R  médio_pct
motivo                                            
alvo atingido            5      1812.00      10.10
fim do período           2      -128.83      -1.60
limite de perda          1      -205.92      -5.59
prazo esgotado          16       995.58       1.78
Patrimônio no fim de cada mês: 01/26 10,540 | 02/26 10,598 | 03/26 10,274 | 04/26 10,650 | 05/26 10,709 | 06/26 11,443 | 07/26 11,552 | 08/26 11,395 | 09/26 11,570 | 10/26 12,297

==============================================================================================================
MESMAS REGRAS, ANO A ANO (R$ 10.000 em 1º de janeiro, até 31 de dezembro)
==============================================================================================================
 ano  caixa %  30 fundos mantidos %  conservador %  conservador ops  conservador pior queda %  moderado %  moderado ops  moderado pior queda %  agressivo %  agressivo ops  agressivo pior queda %
2018      4.9                  18.0            5.0                2                      -0.1         9.1            17                   -2.1         25.6             27                    -6.9
2019      4.6                  42.8            6.4               13                      -0.2        29.7            40                   -1.5         49.3             27                    -3.5
2020      2.2                  -6.8            4.0               29                      -1.7        21.4            63                  -16.8         37.4             29                   -22.6
2021      3.4                   6.7            3.5               31                      -1.0         8.1            57                   -7.6         25.2             28                    -7.9
2022      9.5                  13.2            9.3               10                      -0.3        32.7            47                   -2.4         21.7             27                    -5.6
2023     10.0                  21.3            8.4               17                      -0.6        43.5            47                   -2.9         68.9             25                    -4.6
2024      8.3                   0.3            6.7               20                      -0.9        22.1            49                   -2.9          1.8             21                   -12.7
2025     10.9                  20.8           10.9               10                      -0.3        22.2            48                   -4.9         17.6             20                    -7.6
Média dos 8 anos: caixa %: +6.7 | 30 fundos mantidos %: +14.5 | conservador %: +6.8 | moderado %: +23.6 | agressivo %: +30.9
Anos em que o perfil rendeu mais que o caixa: conservador: 4 de 8 | moderado: 8 de 8 | agressivo: 7 de 8
Anos em que o perfil rendeu mais que os 30 fundos mantidos: conservador: 2 de 8 | moderado: 6 de 8 | agressivo: 7 de 8
```

## Saída literal do teste de sorteio

```
 ano      perfil  com os sinais %  sorteio: típico %  sorteio: pior %  sorteio: melhor %  sorteios que renderam mais que os sinais
2018 conservador              5.0                6.4              4.7               11.5                                        28
2018    moderado              9.1               10.8              5.4               22.0                                        24
2018   agressivo             25.6               19.8             -1.1               62.4                                         6
2019 conservador              6.4                8.1              5.3               11.0                                        26
2019    moderado             29.7               25.3             14.2               47.4                                        10
2019   agressivo             49.3               33.7             14.6               64.3                                         5
2020 conservador              4.0                2.0             -1.0                6.0                                         5
2020    moderado             21.4                4.9             -7.7               35.8                                         2
2020   agressivo             37.4                3.4            -15.9               50.0                                         1
2021 conservador              3.5                4.0             -0.7                7.3                                        18
2021    moderado              8.1                1.5             -9.4               15.6                                         6
2021   agressivo             25.2                5.5            -16.5               27.1                                         1
2022 conservador              9.3               10.4              6.4               17.4                                        19
2022    moderado             32.7               15.0             -4.7               41.4                                         2
2022   agressivo             21.7               17.3             -6.1               70.6                                        11
2023 conservador              8.4                9.4              7.1               13.3                                        21
2023    moderado             43.5               23.4              8.4               35.2                                         0
2023   agressivo             68.9               26.9              0.7               47.6                                         0
2024 conservador              6.7                7.5              5.2               10.5                                        21
2024    moderado             22.1                1.1             -2.7               12.4                                         0
2024   agressivo              1.8               -0.2            -12.8               19.0                                        12
2025 conservador             10.9               11.5              8.8               14.1                                        21
2025    moderado             22.2               18.1              7.9               32.7                                         5
2025   agressivo             17.6               18.3              5.3               44.6                                        17
2026 conservador              5.7                6.7              5.2               11.0                                        24
2026    moderado             10.0                2.5             -5.4               12.1                                         2
2026   agressivo             23.0               -4.3            -15.7               19.2                                         0
conservador: média com os sinais +6.7% | média do sorteio típico +7.3% | anos em que os sinais ficaram acima do sorteio típico: 1 de 9 | sorteios que bateram os sinais: 183 de 270
moderado: média com os sinais +22.1% | média do sorteio típico +11.4% | anos em que os sinais ficaram acima do sorteio típico: 8 de 9 | sorteios que bateram os sinais: 51 de 270
agressivo: média com os sinais +30.0% | média do sorteio típico +13.4% | anos em que os sinais ficaram acima do sorteio típico: 8 de 9 | sorteios que bateram os sinais: 53 de 270
```
