# Estudo: desconto com renda estável, dia a dia (2018 a 2026)

Feito em 2026-11-13 com `estudos/desconto.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/desconto.py`.

É a segunda estratégia do dono, diferente da do anúncio: comprar fundo com cota abaixo do valor patrimonial, rendimento estável e acima da Selic, sem notícia ruim interna; não vender por queda de preço; vender quando a cota sobe a ponto de o rendimento sobre o preço encostar na Selic, ou quando o fundo piora por dentro.

Uma primeira conta, feita com fechamento mensal, foi descartada: o dono apontou que a saída acontece num dia específico e só o diário enxerga. Esta versão usa abertura, máxima, mínima e fechamento de cada pregão.

## Regras

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Patrimônio mínimo | R$ 400 milhões | R$ 100 milhões | R$ 50 milhões |
| Liquidez mínima por dia | R$ 500 mil | R$ 200 mil | R$ 100 mil |
| Preço sobre valor patrimonial | 0,80 a 1,00 | 0,30 a 0,90 | 0,30 a 0,75 |
| Regularidade | 12 avisos seguidos variando até 10% | 6 avisos variando até 15% | 6 avisos variando até 15% |
| Entra com rendimento anual de | Selic + 1 ponto ou mais | Selic + 2 pontos ou mais | Selic + 4 pontos ou mais |
| Ordem de venda onde o rendimento fica em | Selic − 1 ponto | Selic | Selic |

Iguais nos três: sem amortização de 5% ou mais da cota nos últimos 12 meses; sem fato relevante de redução nos últimos 60 pregões; entrada na abertura do pregão seguinte; sem limite de perda pelo preço; saída também por corte de 15% ou mais no rendimento, por fato relevante de redução, ou depois de 2 anos.

Os patrimônios mínimos são a leitura que fiz das faixas do dono (50–100 milhões, até 400 milhões, acima de 400 milhões) como piso de cada perfil. As margens sobre a Selic e as faixas de preço sobre valor patrimonial são escolhas minhas, não otimizadas.

Só entra o que era conhecido no dia: rendimento pelo aviso do FNET, valor patrimonial com 75 dias de atraso, liquidez até a véspera.

## Resultado por operação

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Operações | 26 em 25 fundos | 168 em 116 fundos | 52 em 45 fundos |
| Tempo típico | 134 pregões | 98 pregões | 84 pregões |
| Resultado pessimista | −7,9% | −5,0% | +1,1% |
| Resultado típico | +0,6% | +1,8% | +12,5% |
| Resultado otimista | +9,1% | +8,8% | +19,5% |
| Pior 1 em 10 | −9,5% | −12,7% | −8,3% |
| Operações com ganho | 50% | 58% | 75% |
| Mercado no mesmo período (típico) | +1,7% | +0,9% | +5,8% |
| Renderam mais que o mercado | 35% | 51% | 67% |
| Menor preço no caminho (típico) | −13,1% | −13,8% | −12,3% |
| Menor preço no caminho (pior 1 em 10) | −29,6% | −30,5% | −25,3% |

Resultado = variação da cota mais rendimentos recebidos, sem custos nem imposto.

## Como as operações terminaram (moderado, 168 operações)

| Saída | Operações | Pregões | Resultado típico | Com ganho |
|---|---|---|---|---|
| Alvo: a cota subiu até o rendimento encostar na Selic | 40 | 70 | +10,9% | 100% |
| Rendimento ficou abaixo da Selic sem a cota subir | 51 | 133 | −2,5% | 35% |
| Rendimento cortado em 15% ou mais | 52 | 104 | +0,6% | 52% |
| Fundo declarou redução | 3 | 36 | −14,8% | 33% |
| Ainda aberta | 21 | 60 | −0,3% | 48% |
| Prazo de 2 anos | 1 | 504 | +3,1% | 100% |

No agressivo: 13 saídas pelo alvo com +18,9% típico em 66 pregões, todas com ganho; 26 saídas por corte de rendimento com +11,6% típico.

## Leitura

- **A regra de saída do dono funciona quando é a cota que sobe**: +10,9% em cerca de 70 pregões no moderado, +18,9% no agressivo, sempre com ganho.
- **Isso acontece em 1 de cada 4 operações.** No moderado, 6 em cada 10 terminam de outro jeito: a Selic sobe ou o rendimento cai e o fundo deixa de pagar mais que a Selic, ou o rendimento é cortado.
- **O perfil agressivo é o único que bate o mercado com folga**: 67% das operações, 6,2 pontos de diferença típica. É o desconto fundo com rendimento bem acima da Selic.
- **O conservador perde para o mercado.** Fundo grande, regular, com pouco desconto e pagando acima da Selic é raro (26 casos em 9 anos), e quando aparece costuma ser porque o mercado espera corte.
- **Sem limite de perda, o caminho é duro.** O preço chega a ficar 13% abaixo da entrada na operação típica e 25% a 30% abaixo em 1 de cada 10.
- **Depois da saída pelo alvo, a cota ainda sobe cerca de 4% nos 60 pregões seguintes** (maior preço típico). A regra sai um pouco cedo.
- **2026 foi ruim nos três perfis**: resultado típico de −2,7% a −7,1% nas operações abertas no ano, a maioria ainda aberta.

## Pontos em aberto

- **Selic bruta ou líquida.** O rendimento de FII é isento; a Selic paga imposto de 15% a 22,5%. Comparar com a Selic bruta exige do fundo mais do que o necessário e esvazia o perfil conservador quando a Selic está alta. A decisão é do dono.
- **A regra de saída pela Selic vende no prejuízo quando a Selic sobe.** É coerente com a regra, mas vale decidir se nesse caso o dono prefere segurar.

## Limites

- Cada operação é independente; não é uma carteira com dinheiro limitado.
- As entradas se concentram em poucos períodos (2020, 2021, 2024, 2026), então as operações não são independentes entre si.
- Poucas operações no conservador e no agressivo.
- Valor patrimonial vem do informe da CVM e tem erros de preenchimento; preço sobre valor patrimonial abaixo de 0,30 foi tratado como dado suspeito.
- "Sem notícia ruim" usa só a leitura por palavras dos fatos relevantes.
- Sem custos nem imposto de 20% sobre o ganho na cota.
- O mercado de comparação é a mediana dos fundos com liquidez, com o rendimento mediano do dia.

As operações, uma a uma, estão em `docs/desconto_conservador.csv`, `docs/desconto_moderado.csv` e `docs/desconto_agressivo.csv`.

## Saída literal

```
PERFIS:
  conservador: fundo grande, rendimento muito regular, desconto moderado | patrimônio >= R$ 400 mi | liquidez >= R$ 500,000/dia | preço sobre valor patrimonial de 0.80 a 1.00 | últimos 12 avisos com variação até 10% | entra com rendimento >= Selic +1 pt | ordem de venda onde o rendimento = Selic -1 pt
  moderado: fundo médio, rendimento regular, desconto de 10% ou mais | patrimônio >= R$ 100 mi | liquidez >= R$ 200,000/dia | preço sobre valor patrimonial de 0.30 a 0.90 | últimos 6 avisos com variação até 15% | entra com rendimento >= Selic +2 pt | ordem de venda onde o rendimento = Selic +0 pt
  agressivo: fundo menor, desconto de 25% ou mais, rendimento bem acima da Selic | patrimônio >= R$ 50 mi | liquidez >= R$ 100,000/dia | preço sobre valor patrimonial de 0.30 a 0.75 | últimos 6 avisos com variação até 15% | entra com rendimento >= Selic +4 pt | ordem de venda onde o rendimento = Selic +0 pt

--- CONSERVADOR: 26 operações em 25 fundos ---
Na entrada (típico): rendimento 13.3% ao ano, Selic 11.00%, preço sobre valor patrimonial 0.93
Tempo na operação: típico 134 pregões (pessimista 186, otimista 45)
Resultado total (cota + rendimentos): pessimista -7.9% | típico +0.6% | otimista +9.1% | pior 1 em 10 -9.5% | com ganho 50%
   só a cota: típico -4.5% | só rendimentos: típico +3.9% | ao ano (típico): +0.0%
   mercado no mesmo período: típico +1.7% | operações que renderam mais que o mercado: 35% | diferença típica -0.8 pontos
No caminho: maior preço típico +3.6% no 16º pregão | menor preço típico -13.1% | pior 1 em 10 chegou a -29.6%
                                                     operações  pregões  total_típico  cota_típica  com_ganho  acima_do_mercado  subiu_mais_depois
motivo                                                                                                                                            
ainda aberta                                                 6    156.5         -3.46        -7.22       0.33              0.17                NaN
alvo: cota subiu até o rendimento encostar na Selic          6     56.0         10.56         6.86       1.00              0.83               6.43
fundo declarou redução de rendimento                         1    106.0         -6.41       -11.11       0.00              0.00               0.00
prazo de 2 anos                                              1    504.0          8.18       -20.91       1.00              0.00               5.15
rendimento cortado 15% ou mais                               6     88.5          0.58        -1.59       0.50              0.33               5.30
rendimento ficou abaixo da Selic sem a cota subir            6    153.0         -8.53       -11.82       0.17              0.17               3.39
Por ano de entrada:
ano            2018   2020   2021  2022   2024  2025  2026
operações       1.0    4.0    4.0   2.0    7.0   4.0   4.0
total_típico    9.7   24.0   -8.5   1.2    3.3   6.8  -6.8
mercado         6.3   20.6   -2.8   1.1    1.7   4.2  -3.3
com_ganho       1.0    0.8    0.0   0.5    0.7   0.8   0.0
pregões       197.0  281.5  153.0  41.5  164.0  45.5  69.5
Operações com entrada em 2026:
 fundo    entrada  preco_entrada  rend_anual_entrada  pvp_entrada      saida  preco_saida  pregoes       motivo   cota  rendimentos  total  maior_preco  menor_preco
CPTS11 2026-10-28           7.14               0.151        0.842 2026-11-09         6.99        7 ainda aberta -0.021        0.000 -0.021        0.000       -0.045
LIFE11 2026-02-18           8.90               0.162        0.883 2026-11-09         6.76      181 ainda aberta -0.240        0.119 -0.121        0.011       -0.274
RZAK11 2026-04-30          85.22               0.155        0.967 2026-11-09        71.32      132 ainda aberta -0.163        0.075 -0.089        0.010       -0.169
VRTA11 2026-10-30          68.50               0.149        0.819 2026-11-09        64.35        5 ainda aberta -0.061        0.012 -0.048        0.007       -0.094

--- MODERADO: 168 operações em 116 fundos ---
Na entrada (típico): rendimento 13.0% ao ano, Selic 10.50%, preço sobre valor patrimonial 0.84
Tempo na operação: típico 98 pregões (pessimista 199, otimista 47)
Resultado total (cota + rendimentos): pessimista -5.0% | típico +1.8% | otimista +8.8% | pior 1 em 10 -12.7% | com ganho 58%
   só a cota: típico -2.5% | só rendimentos: típico +4.7% | ao ano (típico): +5.0%
   mercado no mesmo período: típico +0.9% | operações que renderam mais que o mercado: 51% | diferença típica +0.3 pontos
No caminho: maior preço típico +5.6% no 18º pregão | menor preço típico -13.8% | pior 1 em 10 chegou a -30.5%
                                                     operações  pregões  total_típico  cota_típica  com_ganho  acima_do_mercado  subiu_mais_depois
motivo                                                                                                                                            
ainda aberta                                                21     60.0         -0.29        -2.39       0.48              0.48                NaN
alvo: cota subiu até o rendimento encostar na Selic         40     69.5         10.92         7.07       1.00              0.92               4.39
fundo declarou redução de rendimento                         3     36.0        -14.75       -15.72       0.33              0.33              16.30
prazo de 2 anos                                              1    504.0          3.07       -24.33       1.00              0.00               0.83
rendimento cortado 15% ou mais                              52    104.0          0.57        -6.68       0.52              0.40               4.26
rendimento ficou abaixo da Selic sem a cota subir           51    133.0         -2.47        -9.27       0.35              0.33               5.06
Por ano de entrada:
ano            2018   2019   2020   2021  2022   2023  2024  2025  2026
operações       7.0    1.0   28.0   37.0   2.0    8.0  50.0  14.0  21.0
total_típico   25.0    3.6    9.9   -2.3   2.9    5.3   1.9   8.0  -2.7
mercado        12.2    3.1    8.2    0.8   0.6    4.4  -0.4   4.0  -3.6
com_ganho       0.9    1.0    0.7    0.4   0.5    0.6   0.6   0.9   0.4
pregões       286.0  387.0  213.0  105.0  38.0  114.5  98.0  52.5  59.0
Operações com entrada em 2026:
 fundo    entrada  preco_entrada  rend_anual_entrada  pvp_entrada      saida  preco_saida  pregoes                         motivo   cota  rendimentos  total  maior_preco  menor_preco
ALZC11 2026-07-10           7.43               0.162        0.792 2026-11-09         6.83       83                   ainda aberta -0.081        0.054 -0.027        0.011       -0.109
BBFO11 2026-07-02          67.79               0.168        0.888 2026-11-03        60.85       85 rendimento cortado 15% ou mais -0.102        0.054 -0.049        0.056       -0.121
BCRI11 2026-09-02          56.16               0.160        0.662 2026-11-09        48.70       45                   ainda aberta -0.133        0.026 -0.107        0.051       -0.152
BLMG11 2026-11-03          29.09               0.161        0.638 2026-11-09        29.00        4                   ainda aberta -0.003        0.013  0.010        0.038       -0.008
CYCR11 2026-11-04           7.96               0.160        0.837 2026-11-09         8.08        3                   ainda aberta  0.015        0.000  0.015        0.077       -0.001
HABT11 2026-06-10          68.97               0.165        0.721 2026-11-09        61.85      105                   ainda aberta -0.103        0.068 -0.035        0.080       -0.118
KIVO11 2026-08-03          56.80               0.184        0.673 2026-11-09        49.51       67                   ainda aberta -0.128        0.048 -0.080        0.033       -0.131
LIFE11 2026-10-28           7.09               0.195        0.724 2026-11-09         6.76        7                   ainda aberta -0.047        0.016 -0.030        0.006       -0.089
MANA11 2026-11-05           8.12               0.163        0.878 2026-11-09         8.58        2                   ainda aberta  0.057        0.000  0.057        0.069       -0.025
RBHG11 2026-08-04          58.52               0.164        0.676 2026-11-09        57.59       66                   ainda aberta -0.016        0.039  0.024        0.102       -0.107
RBHY11 2026-04-30          79.55               0.166        0.856 2026-11-03        57.00      128 rendimento cortado 15% ou mais -0.283        0.086 -0.197        0.006       -0.341
RBRX11 2026-10-29           6.68               0.162        0.723 2026-11-09         6.40        6                   ainda aberta -0.042        0.000 -0.042        0.010       -0.073
RECT11 2026-08-12          33.08               0.163        0.369 2026-11-09        32.32       60                   ainda aberta -0.023        0.041  0.018        0.088       -0.078
RZAK11 2026-08-07          78.50               0.161        0.889 2026-11-09        71.32       63                   ainda aberta -0.091        0.040 -0.051        0.035       -0.098
SPXS11 2026-08-13           7.45               0.159        0.791 2026-11-09         7.26       59                   ainda aberta -0.026        0.041  0.015        0.074       -0.072
TGAR11 2026-07-02          53.10               0.163        0.484 2026-11-03        34.01       85 rendimento cortado 15% ou mais -0.360        0.049 -0.311        0.026       -0.411
TOPP11 2026-07-03          61.00               0.165        0.576 2026-09-15        61.73       51 rendimento cortado 15% ou mais  0.012        0.037  0.049        0.186       -0.023
VCRI11 2026-10-30           6.85               0.158        0.717 2026-11-09         6.74        5                   ainda aberta -0.016        0.013 -0.003        0.000       -0.079
VGRI11 2026-09-01           5.42               0.166        0.628 2026-11-09         5.52       46                   ainda aberta  0.018        0.028  0.046        0.161       -0.048
VRTA11 2026-11-04          63.70               0.160        0.762 2026-11-09        64.35        3                   ainda aberta  0.010        0.000  0.010        0.048       -0.025
VRTM11 2026-08-06           6.62               0.163        0.699 2026-11-09         6.02       64                   ainda aberta -0.091        0.041 -0.050        0.060       -0.091

--- AGRESSIVO: 52 operações em 45 fundos ---
Na entrada (típico): rendimento 15.7% ao ano, Selic 10.75%, preço sobre valor patrimonial 0.72
Tempo na operação: típico 84 pregões (pessimista 165, otimista 56)
Resultado total (cota + rendimentos): pessimista +1.1% | típico +12.5% | otimista +19.5% | pior 1 em 10 -8.3% | com ganho 75%
   só a cota: típico +4.3% | só rendimentos: típico +5.0% | ao ano (típico): +23.7%
   mercado no mesmo período: típico +5.8% | operações que renderam mais que o mercado: 67% | diferença típica +6.2 pontos
No caminho: maior preço típico +14.1% no 39º pregão | menor preço típico -12.3% | pior 1 em 10 chegou a -25.3%
                                                     operações  pregões  total_típico  cota_típica  com_ganho  acima_do_mercado  subiu_mais_depois
motivo                                                                                                                                            
ainda aberta                                                 6     73.0          2.90        -7.01       0.67              0.50                NaN
alvo: cota subiu até o rendimento encostar na Selic         13     66.0         18.91        14.29       1.00              1.00               3.86
fundo declarou redução de rendimento                         3     29.0         13.45        12.16       0.67              1.00              16.30
rendimento cortado 15% ou mais                              26    108.0         11.63        -1.31       0.62              0.50               3.61
rendimento ficou abaixo da Selic sem a cota subir            4    164.5          2.94        -2.70       1.00              0.75               2.32
Por ano de entrada:
ano            2018   2019  2020   2021  2023  2024  2025  2026
operações       2.0    1.0  11.0    7.0   1.0  18.0   7.0   5.0
total_típico   53.6   20.6  23.0    2.7   5.0  10.9  14.6  -7.1
mercado        17.2    3.0  16.6    0.7   3.8   3.0   5.8  -4.3
com_ganho       1.0    1.0   1.0    0.6   1.0   0.7   0.7   0.4
pregões       256.5  386.0  98.0  145.0  58.0  81.5  87.0  64.0
Operações com entrada em 2026:
 fundo    entrada  preco_entrada  rend_anual_entrada  pvp_entrada      saida  preco_saida  pregoes                         motivo   cota  rendimentos  total  maior_preco  menor_preco
HABT11 2026-11-04          60.90               0.181        0.656 2026-11-09        61.85        3                   ainda aberta  0.016        0.000  0.016        0.029        0.000
KIVO11 2026-08-04          56.25               0.186        0.667 2026-11-09        49.51       66                   ainda aberta -0.120        0.049 -0.071        0.043       -0.122
LIFE11 2026-07-15           6.90               0.209        0.715 2026-11-09         6.76       80                   ainda aberta -0.020        0.067  0.046        0.101       -0.064
RBHY11 2026-08-06          63.15               0.190        0.680 2026-11-09        55.05       64                   ainda aberta -0.128        0.044 -0.084        0.038       -0.189
TGAR11 2026-08-10          47.67               0.181        0.438 2026-11-03        34.01       58 rendimento cortado 15% ou mais -0.287        0.039 -0.248        0.143       -0.343
```
