# Estudo do caminho diário da cota depois de um salto de rendimento

Feito em 2026-11-11 com `estudos/caminho_diario.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/caminho_diario.py`.

## Por que este estudo

Os estudos anteriores comparavam o preço na entrada com o preço 1, 3, 6 ou 12 meses depois. Isso esconde o caminho: a cota pode ter ido a +12% e voltado. Aqui cada salto é seguido pregão a pregão.

## Método

- 268 saltos de rendimento (2017 a 2026). Compra no fechamento do 1º pregão do mês seguinte ao do salto.
- Para cada caso: maior alta (pico), maior queda (fundo), dia do pico, e quem veio primeiro.
- **Controle**: como toda cota oscila, o pico de qualquer fundo é sempre positivo. Cada salto é comparado com até 25 outros fundos com liquidez, comprados no mesmo dia, sem salto nos 6 meses em volta (6.694 compras).
- Preço ajustado por desdobramento. Períodos com salto de preço sem explicação ficam fora.
- Seções 1 e 2 são só preço. A seção 3 soma o rendimento recebido, estimado pela mediana (1,15% ao mês depois de salto; 0,87% no controle).

## Resultado

### Até onde a cota foi

| Janela | | Pico (mediana) | Fundo (mediana) | Fim da janela | Dia do pico | Tocou +5% | Tocou +10% | Tocou −5% | Tocou −10% |
|---|---|---|---|---|---|---|---|---|---|
| 1 mês | depois de salto | +2,1% | −1,4% | +0,5% | 12º | 21% | 3% | 16% | 5% |
| 1 mês | controle | +1,6% | −1,9% | −0,4% | 9º | 16% | 4% | 22% | 6% |
| 3 meses | depois de salto | +4,3% | −3,1% | 0,0% | 28º | 42% | 15% | 37% | 18% |
| 3 meses | controle | +3,1% | −4,5% | −1,1% | 21º | 35% | 15% | 46% | 21% |
| 6 meses | depois de salto | +6,0% | −5,6% | −0,9% | 46º | 56% | 27% | 54% | 34% |
| 6 meses | controle | +4,4% | −7,7% | −2,6% | 39º | 46% | 24% | 65% | 39% |

### Vender num alvo (com rendimento recebido, até 6 meses)

| Regra | Depois de salto: média por operação | Ganhou | Dias (mediana) | Controle: média | Controle: ganhou | Vantagem por operação |
|---|---|---|---|---|---|---|
| Vender em +5% ou em −5% | +2,8% | 62% | 32 | +1,1% | 47% | +1,8% |
| Vender em +8% ou em −8% | +3,7% | 63% | 68 | +1,7% | 54% | +2,1% |
| Vender em +10% ou em −10% | +4,2% | 66% | 101 | +2,0% | 57% | +2,1% |
| Vender em +5%, sem limite de perda | +3,2% | 80% | 97 | +1,4% | 69% | +1,8% |
| Segurar 6 meses | +5,3% | 72% | 126 | +2,1% | 61% | +3,2% |

### A partir da entrada: sobe nos primeiros 30 dias e devolve nos 30 seguintes?

Acrescentado em 2026-11-11. O dono esclareceu que "mês seguinte" são os 30 dias depois dos primeiros 30 dias da posição, não o mês do calendário. Conta feita com 21 pregões para cada período de 30 dias.

| Pico nos primeiros 30 dias | | Casos | No 21º pregão | No 42º pregão | Devolveu metade ou mais do pico | Voltou ao preço de entrada ou abaixo | Queda a partir do pico nos 30 dias seguintes |
|---|---|---|---|---|---|---|---|
| 3% a 6% | depois de salto | 53 (22%) | +2,4% | +1,0% | 60% | 42% | −4,7% |
| 3% a 6% | controle | 1.129 (18%) | +2,0% | +1,5% | 56% | 37% | −4,3% |
| 6% a 10% | depois de salto | 29 (12%) | +5,2% | +5,1% | 34% | 17% | −4,5% |
| 6% a 10% | controle | 457 (7%) | +5,4% | +4,0% | 47% | 23% | −5,4% |
| 10% ou mais | depois de salto | 8 (3%) | +11,1% | +9,2% | 38% | 0% | −10,9% |
| 10% ou mais | controle | 260 (4%) | +10,4% | +9,6% | 36% | 15% | −6,7% |

- Depois de um salto, 12% dos casos tiveram pico de 6% a 10% nos primeiros 30 dias (7% no controle).
- Desses, 34% devolveram metade ou mais até o 42º pregão e 17% voltaram ao preço de entrada. No controle, 47% e 23%.
- A partir do pico, a cota recua cerca de 4,5% nos 30 dias seguintes, com ou sem salto.
- São 29 casos na faixa de 6% a 10% e 8 acima de 10%: pouco para conclusão firme.

### Por mês do calendário (primeira versão, mantida como histórico)

A conta abaixo usa meses do calendário, não a data de entrada. Não responde à pergunta do dono.


- Em 11.717 fundo-meses, a cota subiu 6% ou mais em 7,8% e caiu 6% ou mais em 9,0%.
- Depois de subir 6% ou mais, o mês seguinte foi em média +0,3%. Devolveu metade ou mais da alta em 16% dos casos.
- Dentro de um mesmo mês, a distância entre o menor e o maior fechamento tem mediana de 4,7%; passa de 6% em 36% dos meses e de 10% em 15%.

## Leitura

- O caminho importa. Em 3 meses a cota termina em 0% na mediana, mas no meio passou por +4,3% e −3,1%.
- O salto de rendimento melhora as altas pequenas e protege a queda: toca +5% mais vezes (42% contra 35%) e toca −5% menos vezes (37% contra 46%).
- O salto não aumenta as altas grandes. Tocar +10% ou +15% acontece com a mesma frequência de qualquer outro fundo.
- O pico costuma vir entre o 28º e o 46º pregão.
- Em 6 meses, 27% dos casos passaram de +6% e terminaram abaixo da metade do pico (21% no controle). É o padrão "sobe e devolve", em cerca de 1 caso a cada 4.
- A alta de 6% num mês seguida de devolução no mês seguinte não é o caso típico (16%).

## Limites

- A data de entrada é o 1º pregão do mês seguinte, não o dia do anúncio. Com a data real o pico pode ser maior e vir antes.
- Preço de fechamento: máximas e mínimas dentro do dia não entram, então alvos e limites seriam tocados um pouco mais vezes na prática.
- O rendimento da seção 3 é uma estimativa pela mediana, não o valor de cada fundo. Parte da vantagem dessa seção (cerca de 0,3% ao mês) vem dessa diferença de rendimento.
- Sem custos nem imposto de 20% sobre ganho na cota.
- O controle é sorteado (semente fixa); outro sorteio muda os números do controle na segunda casa.

## Saída literal

```
268 saltos de rendimento (2017-2026), comprando no fechamento do 1º pregão do mês seguinte. Controle: 6694 compras de outros fundos nos mesmos dias.

=== 1. ATÉ ONDE A COTA FOI, DIA A DIA (só preço, sem rendimento) ===
--- janela de 1 mês (21 pregões) ---
                                               depois de salto  controle (outros fundos, mesmo dia)
casos                                                  252.000                             6309.000
pico (mediana) %                                         2.076                                1.562
fundo (mediana) %                                       -1.354                               -1.931
fim da janela (mediana) %                                0.546                               -0.422
dia do pico (mediano)                                   12.000                                9.000
tocou +5%                                                0.210                                0.157
tocou +10%                                               0.032                                0.043
tocou +15%                                               0.012                                0.014
tocou -5%                                                0.155                                0.216
tocou -10%                                               0.048                                0.059
+10% antes de -10%                                       0.032                                0.043
+5% antes de -5%                                         0.210                                0.154
devolveu (pico >= 6% e fim <= metade do pico)            0.028                                0.033
--- janela de 3 meses (63 pregões) ---
                                               depois de salto  controle (outros fundos, mesmo dia)
casos                                                  245.000                             6116.000
pico (mediana) %                                         4.301                                3.073
fundo (mediana) %                                       -3.122                               -4.504
fim da janela (mediana) %                                0.000                               -1.144
dia do pico (mediano)                                   28.000                               21.000
tocou +5%                                                0.424                                0.349
tocou +10%                                               0.147                                0.147
tocou +15%                                               0.057                                0.069
tocou -5%                                                0.367                                0.463
tocou -10%                                               0.176                                0.207
+10% antes de -10%                                       0.143                                0.145
+5% antes de -5%                                         0.392                                0.305
devolveu (pico >= 6% e fim <= metade do pico)            0.110                                0.115
--- janela de 6 meses (126 pregões) ---
                                               depois de salto  controle (outros fundos, mesmo dia)
casos                                                  226.000                             5584.000
pico (mediana) %                                         5.980                                4.405
fundo (mediana) %                                       -5.582                               -7.692
fim da janela (mediana) %                               -0.875                               -2.633
dia do pico (mediano)                                   46.500                               39.000
tocou +5%                                                0.558                                0.463
tocou +10%                                               0.270                                0.244
tocou +15%                                               0.133                                0.128
tocou -5%                                                0.540                                0.649
tocou -10%                                               0.336                                0.387
+10% antes de -10%                                       0.265                                0.233
+5% antes de -5%                                         0.478                                0.369
devolveu (pico >= 6% e fim <= metade do pico)            0.274                                0.212

=== 2. POR GRUPO, JANELA DE 3 MESES (salto x controle do mesmo grupo de datas) ===
               grupo  casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +10%  tocou -10%  +10% antes de -10%
               papel     46             4.315             -2.223                      1.027                   42.5       0.087       0.109               0.087
              tijolo    119             4.738             -3.356                      0.781                   26.0       0.168       0.176               0.168
 com venda de imóvel     29             2.928             -4.608                      0.781                   21.0       0.138       0.276               0.138
   salto de 25 a 50%    138             3.863             -3.069                     -0.141                   32.5       0.145       0.167               0.138
  salto acima de 50%    107             4.738             -3.356                      0.014                   24.0       0.150       0.187               0.150
rendia >= 10% ao ano     98             2.977             -3.666                     -1.108                   20.5       0.112       0.194               0.102
 rendia < 10% ao ano    147             4.794             -2.802                      0.975                   32.0       0.170       0.163               0.170
            até 2021    111             5.000             -2.392                      0.990                   38.0       0.162       0.162               0.162
      2022 em diante    134             3.206             -3.905                     -0.604                   23.0       0.134       0.187               0.127

=== 3. VENDER NUM ALVO: resultado por operação, com rendimento recebido (janela máxima de 6 meses) ===
(rendimento considerado por mês: 1.15% da cota depois de salto; 0.87% no controle)
                    regra  salto: média %  salto: mediana %  salto: ganhou  salto: resultado >= alvo  salto: dias (mediana)  controle: média %  controle: ganhou  controle: resultado >= alvo  vantagem (média) %  vantagem ao ano %
            vender em +5%            3.17              5.71           0.80                      0.66                   97.0               1.36              0.69                         0.54                1.81               6.30
            vender em +8%            3.85              7.56           0.75                      0.47                  126.0               1.95              0.65                         0.37                1.90               5.14
           vender em +10%            4.44              6.96           0.74                      0.36                  126.0               2.20              0.64                         0.30                2.24               5.30
           vender em +15%            5.13              6.79           0.74                      0.22                  126.0               2.44              0.63                         0.16                2.69               5.71
  vender em +5% ou em -5%            2.84              5.38           0.62                      0.56                   32.0               1.05              0.47                         0.42                1.80               9.75
  vender em +8% ou em -8%            3.74              6.38           0.63                      0.43                   68.0               1.65              0.54                         0.34                2.09               7.13
vender em +10% ou em -10%            4.15              6.02           0.66                      0.34                  101.0               2.01              0.57                         0.28                2.14               5.98
 vender em +10% ou em -5%            4.09              1.43           0.57                      0.30                   66.0               1.75              0.40                         0.23                2.34               7.71
          segurar 6 meses            5.32              6.02           0.72                       NaN                  126.0               2.13              0.61                          NaN                3.19               6.38

=== 4. "SOBE 6-10% NUM MÊS E DEVOLVE NO SEGUINTE": com que frequência, em qualquer fundo? ===
11717 fundo-meses. Subiu 6% ou mais no mês: 7.8% | caiu 6% ou mais: 9.0%
   depois de subir 6% ou mais       916 casos | mês seguinte: média +0.32%, mediana +0.19% | devolveu metade ou mais: 16%
   depois de subir 3 a 6%          1202 casos | mês seguinte: média +0.30%, mediana +0.12% | devolveu metade ou mais: 27%
   mês comum (entre -3 e +3%)      6985 casos | mês seguinte: média -0.38%, mediana -0.32% | devolveu metade ou mais: 39%
   depois de cair 3 a 6%           1561 casos | mês seguinte: média -1.29%, mediana -1.03% | devolveu metade ou mais: 20%
   depois de cair 6% ou mais       1053 casos | mês seguinte: média -0.21%, mediana -0.31% | devolveu metade ou mais: 20%
Dentro de um mês, distância entre o menor e o maior fechamento: mediana 4.7% | 6% ou mais em 36% dos meses | 10% ou mais em 15%

=== 5. A PARTIR DA ENTRADA: sobe nos primeiros 30 dias e devolve nos 30 seguintes? (21 pregões = ~30 dias) ===
depois de salto: 245 casos
   pico de 3% a 6% nos primeiros 30 dias: 53 casos (22%) | dia do pico 14º | no 21º pregão estava em +2.4% | no 42º em +1.0% | devolveu metade ou mais do pico até o 42º: 60% | devolveu tudo (voltou ao preço de entrada ou abaixo): 42% | queda a partir do pico nos 30 dias seguintes (mediana): -4.7%
   pico de 6% a 10% nos primeiros 30 dias: 29 casos (12%) | dia do pico 18º | no 21º pregão estava em +5.2% | no 42º em +5.1% | devolveu metade ou mais do pico até o 42º: 34% | devolveu tudo (voltou ao preço de entrada ou abaixo): 17% | queda a partir do pico nos 30 dias seguintes (mediana): -4.5%
   pico de 10% ou mais nos primeiros 30 dias: 8 casos (3%) | dia do pico 20º | no 21º pregão estava em +11.1% | no 42º em +9.2% | devolveu metade ou mais do pico até o 42º: 38% | devolveu tudo (voltou ao preço de entrada ou abaixo): 0% | queda a partir do pico nos 30 dias seguintes (mediana): -10.9%
controle: 6116 casos
   pico de 3% a 6% nos primeiros 30 dias: 1129 casos (18%) | dia do pico 16º | no 21º pregão estava em +2.0% | no 42º em +1.5% | devolveu metade ou mais do pico até o 42º: 56% | devolveu tudo (voltou ao preço de entrada ou abaixo): 37% | queda a partir do pico nos 30 dias seguintes (mediana): -4.3%
   pico de 6% a 10% nos primeiros 30 dias: 457 casos (7%) | dia do pico 17º | no 21º pregão estava em +5.4% | no 42º em +4.0% | devolveu metade ou mais do pico até o 42º: 47% | devolveu tudo (voltou ao preço de entrada ou abaixo): 23% | queda a partir do pico nos 30 dias seguintes (mediana): -5.4%
   pico de 10% ou mais nos primeiros 30 dias: 260 casos (4%) | dia do pico 19º | no 21º pregão estava em +10.4% | no 42º em +9.6% | devolveu metade ou mais do pico até o 42º: 36% | devolveu tudo (voltou ao preço de entrada ou abaixo): 15% | queda a partir do pico nos 30 dias seguintes (mediana): -6.7%
```
