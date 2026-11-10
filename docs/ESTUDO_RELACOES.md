# Estudo: quais relações separam os FIIs que rendem mais (2017 a 2026)

Feito em 2026-11-10 com `estudos/relacoes.py`, sobre a base oficial (B3 e CVM). Para refazer: `PYTHONPATH=. .venv/bin/python estudos/relacoes.py`.

## Método

- Em cada fim de mês, os fundos são ordenados por um sinal e divididos em 5 grupos.
- Mede-se o retorno do mês seguinte (cota mais rendimento, comprando no 1º pregão), sempre acima da mediana do mercado de FIIs.
- Um sinal só conta se funcionar nas duas metades do período (até 2021 e de 2022 em diante).
- Valor patrimonial e cotistas entram com 2 meses de atraso, que é quando a CVM já publicou.
- Só fundos com pelo menos R$ 200 mil negociados por dia.
- "t" é a estatística de confiança: acima de 2 é sinal razoável, acima de 3 é forte.

## O que funcionou

| Relação | Diferença entre o grupo melhor e o pior | Confiança (t) | Meses a favor | Funciona nas duas metades |
|---|---|---|---|---|
| Rendimento do mês acima do nível dos 6 meses anteriores | +1,48% no mês seguinte | 7,7 | 76% | sim (6,9 e 5,0) |
| Rendimento do mês alto em relação ao preço | +1,45% no mês seguinte | 5,6 | 76% | sim (5,6 e 3,2) |
| Tendência: fundo que subiu nos últimos 12 meses | +0,98% no mês seguinte | 3,7 | 69% | sim (2,1 e 3,1) |
| Valor patrimonial crescendo em 6 meses | +1,64% em 3 meses | 5,1 | 68% | sim (2,1 e 5,3) |
| Os quatro combinados | +1,54% no mês seguinte | 5,6 | 71% | sim (4,7 e 3,6) |

- Os quatro sinais quase não se repetem entre si (correlação entre 0 e 0,23), então somam.
- Entrando só no 10º pregão do mês seguinte, o sinal de rendimento cai pela metade (+0,70%), mas continua forte. Rapidez vale dinheiro.
- A tendência de 12 meses não depende de rapidez: funciona igual entrando tarde.
- **O efeito está diminuindo.** A diferença do sinal combinado foi de cerca de 2,2% ao mês em 2020–21, 1,3% a 1,7% em 2022–24 e 0,5% a 0,8% em 2025–26.

## O que não funcionou

- Preço abaixo do valor patrimonial: não separou nada (t −0,5).
- Rendimento acumulado de 12 meses sobre o preço: funcionou só até 2021.
- Fundo que caiu no mês não se recupera no mês seguinte.
- Tamanho, liquidez, número de cotistas, volume fora do normal: nada consistente.
- Fundos que oscilam muito renderam menos em 3 meses (t −2,6), sinal fraco.

## A cota em volta da data limite do rendimento

2.608 pagamentos de 276 fundos, de junho de 2025 em diante. Rendimento médio de 1,04% da cota.

- Nos 10 pregões até a data limite, a cota sobe 0,73% acima do mercado (t 10).
- No 1º pregão sem direito, a cota cai 0,79%. Quem ficou recebe 1,04% e perde 0,79%: saldo de +0,24%.
- Comprar na data limite e vender 10 pregões depois: +0,43% acima do mercado (t 5,7), em 60% dos casos.

É pequeno por operação e ainda falta descontar imposto de 20% sobre o ganho na cota e a diferença entre compra e venda.

## O preço se mexe antes do salto?

Em 259 saltos, o fundo rendeu +2,16% acima do mercado no próprio mês do salto (t 7,8) e +0,6% em cada um dos dois meses anteriores (t 2,3 e 1,8). Volume praticamente normal. Ou seja: a maior parte da reação acontece no mês do anúncio, e há um pequeno movimento antes.

## Juros, bolsa, dólar, eleição

- **Selic:** o mercado de FIIs rendeu mais nos meses de Selic parada (+1,0% ao mês) do que com Selic subindo ou caindo (perto de zero). Os saltos de rendimento funcionaram nas três fases.
- **Bolsa:** na mesma semana explica 34% da oscilação do mercado de FIIs. De um dia para o outro, quase nada (correlação 0,08). De 2022 em diante, depois de a bolsa cair mais de 2%, os FIIs caíram mais 0,13% no dia seguinte (50 dias, t −2,4); até 2021 isso não aparecia.
- **Dólar:** some quando a bolsa entra na conta.
- **Eleição:** três casos. O que move é o resultado contra a expectativa, e não há dado de expectativa na base. Não dá para aprender com três.
- **Juro longo:** não testado (sem fonte liberada).

## Limites

- Foram testados 13 sinais. Com tantos testes, um ou outro passaria por sorte; por isso só valem os que passam nas duas metades e com t bem acima de 3.
- Retornos sem custos e sem imposto de 20% sobre ganho na cota.
- O grupo melhor tem cerca de 16 fundos por mês e muda todo mês: seguir à risca exige muita troca.
- 220 fundos estão fora por falta de histórico de rendimento confiável.
- No histórico, "rendimento do mês" pode ter sido anunciado alguns dias depois do fim do mês. O teste entrando no 10º pregão cobre esse risco.
- Resultado passado não garante o próximo, e o efeito vem caindo.

## Saída literal

```
Painel: 01/2017 a 10/2026, 396 fundos, 12140 fundo-meses com liquidez >= R$ 200,000/dia

=== 1. SINAIS E O RETORNO DO MÊS SEGUINTE (acima do mercado) ===
                                            sinal  meses  fundos/mês  grupo baixo %  grupo alto %  alto-baixo %     t  meses a favor  1ª metade %    t1  2ª metade %    t2                    monotônico
   queda_no_mes (retorno do mês acima do mercado)    101         123          -0.06          0.10          0.17  0.66           0.53        -0.10 -0.19         0.37  1.55 -0.06 +0.01 +0.19 +0.26 +0.10
tendencia_12m (retorno de 12 meses, sem o último)     95         115          -0.48          0.50          0.98  3.74           0.69         0.88  2.07         1.04  3.12 -0.48 +0.01 +0.12 +0.39 +0.50
    tendencia_3m (retorno dos 3 meses anteriores)     98         119          -0.04          0.10          0.13  0.52           0.58        -0.11 -0.23         0.30  1.00 -0.04 +0.12 +0.14 +0.33 +0.10
           preco_sobre_vp (com 2 meses de atraso)    100         121           0.00         -0.15         -0.15 -0.51           0.46        -0.42 -1.03         0.05  0.12 +0.00 +0.33 +0.25 +0.13 -0.15
                       rendimento_12m_sobre_preco     81          79           0.27          0.71          0.43  1.47           0.60         0.95  2.01         0.23  0.62 +0.27 +0.41 +0.47 +0.80 +0.71
                    rendimento_do_mes_sobre_preco     89          84          -0.08          1.37          1.45  5.57           0.76         2.24  5.56         1.03  3.16 -0.08 +0.22 +0.36 +0.77 +1.37
                rendimento_vs_6m (salto ou queda)     85          82          -0.26          1.22          1.48  7.66           0.76         2.29  6.90         1.10  4.96 -0.26 +0.28 +0.60 +0.84 +1.22
         volume_fora_do_normal (mês ÷ média de 6)     98         120          -0.13          0.18          0.31  1.62           0.61         0.44  1.48         0.22  0.87 -0.13 -0.01 +0.19 +0.44 +0.18
         cotistas_crescendo (3 meses, com atraso)     98         119           0.01          0.11          0.10  0.48           0.57        -0.12 -0.31         0.25  1.11 +0.01 +0.20 +0.11 +0.30 +0.11
                 tamanho (patrimônio, com atraso)    100         121           0.17          0.19          0.01  0.08           0.52        -0.18 -0.61         0.16  0.73 +0.17 +0.13 +0.03 +0.05 +0.19
         oscilacao_12m (desvio do retorno mensal)     97         116           0.14         -0.22         -0.36 -1.24           0.58        -0.59 -1.27        -0.20 -0.55 +0.14 +0.19 +0.37 +0.17 -0.22
                   liquidez (volume diário médio)    102         124           0.19          0.12         -0.07 -0.41           0.53         0.19  0.63        -0.27 -1.38 +0.19 -0.09 +0.04 +0.22 +0.12
               vp_crescendo (6 meses, com atraso)     97         117          -0.12          0.26          0.38  2.54           0.63         0.20  0.71         0.49  3.14 -0.12 +0.01 +0.26 +0.22 +0.26

=== 2. MESMOS SINAIS, RETORNO DOS 3 MESES SEGUINTES ===
                                            sinal  meses  alto-baixo %     t  meses a favor  1ª metade %    t1  2ª metade %    t2                    monotônico
   queda_no_mes (retorno do mês acima do mercado)     97         -0.14 -0.35           0.52        -0.95 -1.41         0.45  0.93 -0.39 +0.12 +0.33 +0.29 -0.53
tendencia_12m (retorno de 12 meses, sem o último)     93          1.99  4.30           0.71         1.53  2.30         2.29  3.63 -1.37 -0.18 +0.26 +0.65 +0.62
    tendencia_3m (retorno dos 3 meses anteriores)     96          0.17  0.39           0.51         0.05  0.08         0.26  0.43 -0.49 +0.34 +0.29 +0.20 -0.32
           preco_sobre_vp (com 2 meses de atraso)     97          0.02  0.04           0.57        -0.86 -1.30         0.66  0.82 -0.51 +0.60 +0.51 -0.25 -0.49
                       rendimento_12m_sobre_preco     79         -0.06 -0.10           0.43         1.74  2.33        -0.80 -1.10 +0.73 +0.72 +0.64 +1.23 +0.67
                    rendimento_do_mes_sobre_preco     87          1.66  3.43           0.64         3.26  4.98         0.77  1.22 +0.36 +0.32 +0.70 +1.34 +2.01
                rendimento_vs_6m (salto ou queda)     82          2.11  5.55           0.70         3.60  5.50         1.41  3.22 -0.34 +0.34 +0.95 +1.32 +1.76
         volume_fora_do_normal (mês ÷ média de 6)     96          0.25  0.72           0.56        -0.06 -0.12         0.47  0.97 -0.34 -0.16 +0.36 +0.27 -0.09
         cotistas_crescendo (3 meses, com atraso)     96          0.01  0.04           0.55        -0.21 -0.40         0.17  0.38 +0.01 -0.22 +0.16 +0.05 +0.03
                 tamanho (patrimônio, com atraso)     97          0.67  2.14           0.58         0.36  0.72         0.90  2.24 -0.34 +0.19 -0.29 -0.04 +0.34
         oscilacao_12m (desvio do retorno mensal)     95         -1.39 -2.61           0.67        -1.59 -1.89        -1.25 -1.80 +0.27 +0.21 +0.64 -0.01 -1.12
                   liquidez (volume diário médio)     98          0.43  1.22           0.54         0.83  1.29         0.12  0.33 -0.05 -0.36 -0.37 +0.20 +0.38
               vp_crescendo (6 meses, com atraso)     95          1.64  5.06           0.68         1.30  2.13         1.88  5.33 -1.00 +0.03 +0.14 +0.18 +0.64

=== 2b. OS SINAIS FORTES RESISTEM A ENTRAR MAIS TARDE? ===
entrando no 10º pregão do mês seguinte (retorno do resto do mês)
                                            sinal  meses  alto-baixo %    t  meses a favor  1ª metade %    t1  2ª metade %   t2                    monotônico
tendencia_12m (retorno de 12 meses, sem o último)     95          0.77 4.38           0.71         0.71  2.60         0.80 3.50 -0.24 -0.04 +0.17 +0.30 +0.53
                    rendimento_do_mes_sobre_preco     89          1.39 9.09           0.85         1.87  6.79         1.13 6.46 -0.08 +0.34 +0.41 +0.66 +1.31
                rendimento_vs_6m (salto ou queda)     85          0.70 5.09           0.72         1.16  4.19         0.48 3.27 +0.19 +0.38 +0.52 +0.63 +0.88
               vp_crescendo (6 meses, com atraso)     97          0.09 0.76           0.52        -0.06 -0.28         0.20 1.47 +0.02 +0.14 +0.19 +0.25 +0.11
pulando o mês seguinte inteiro (retorno dos meses 2 e 3)
                                            sinal  meses  alto-baixo %    t  meses a favor  1ª metade %   t1  2ª metade %    t2                    monotônico
tendencia_12m (retorno de 12 meses, sem o último)     93          1.22 3.37           0.67         0.89 1.52         1.45  3.10 -0.99 -0.10 +0.15 +0.32 +0.23
                    rendimento_do_mes_sobre_preco     87          0.20 0.52           0.56         0.98 1.57        -0.24 -0.50 +0.43 +0.11 +0.49 +0.52 +0.63
                rendimento_vs_6m (salto ou queda)     82          0.58 2.04           0.59         1.28 2.68         0.25  0.72 -0.06 +0.12 +0.51 +0.45 +0.52
               vp_crescendo (6 meses, com atraso)     95          0.87 3.44           0.60         0.66 1.43         1.01  3.58 -0.60 +0.04 -0.13 -0.09 +0.27
Correlação entre os sinais fortes (posição no ranking):
                               tendencia_12m  rendimento_do_mes_sobre_preco  rendimento_vs_6m  vp_crescendo
tendencia_12m                           1.00                          -0.00              0.00          0.23
rendimento_do_mes_sobre_preco          -0.00                           1.00              0.18         -0.16
rendimento_vs_6m                        0.00                           0.18              1.00          0.04
vp_crescendo                            0.23                          -0.16              0.04          1.00
Sinal combinado (média da posição nos 4 sinais):
 meses  fundos/mês  grupo baixo %  grupo alto %  alto-baixo %    t  meses a favor  1ª metade %   t1  2ª metade %   t2                    monotônico
    83          80          -0.38          1.16          1.54 5.57           0.71         2.45 4.72         1.15 3.64 -0.38 +0.29 +0.58 +0.81 +1.16
Sinal combinado, ano a ano (grupo alto acima do mercado, % ao mês | alto menos baixo):
ano      2019   2020   2021   2022   2023   2024   2025   2026
meses    1.00  12.00  12.00  12.00  12.00  12.00  12.00  10.00
alto     1.93   2.03   1.54   1.00   1.09   0.78   1.25   0.21
dif      8.01   2.26   2.18   1.35   1.70   1.30   0.52   0.83
a_favor  1.00   0.75   0.92   0.75   0.75   0.75   0.50   0.50

=== 3. O PREÇO JÁ SE MEXE ANTES DO SALTO DE RENDIMENTO? ===
salto: 259 casos | retorno acima do mercado (média %, estatística t) e volume relativo (mediana):
   3 mês(es) antes  retorno -0.50% (t -1.7, 35% positivos) | volume 0.95x
   2 mês(es) antes  retorno +0.58% (t +1.8, 42% positivos) | volume 1.00x
   1 mês(es) antes  retorno +0.60% (t +2.3, 44% positivos) | volume 1.00x
   mês do evento    retorno +2.16% (t +7.8, 57% positivos) | volume 1.08x
queda: 181 casos | retorno acima do mercado (média %, estatística t) e volume relativo (mediana):
   3 mês(es) antes  retorno +0.25% (t +0.6, 44% positivos) | volume 1.02x
   2 mês(es) antes  retorno -0.36% (t -0.7, 51% positivos) | volume 1.09x
   1 mês(es) antes  retorno -0.19% (t -0.4, 35% positivos) | volume 1.05x
   mês do evento    retorno -2.25% (t -3.3, 31% positivos) | volume 1.02x

=== 4. DATA LIMITE DO RENDIMENTO ("data com"): o que a cota faz em volta ===
2608 pagamentos de 276 fundos (jun/2025 em diante). Rendimento médio: 1.04% da cota.
   10 pregões até a data limite (só cota)                                 +0.73% acima do mercado (t +10.0, 63% positivos)
   3 pregões até a data limite (só cota)                                  +0.26% acima do mercado (t +5.9, 58% positivos)
   1º pregão sem direito (só cota)                                        -0.79% acima do mercado (t -19.5, 24% positivos)
   1º pregão sem direito (cota + rendimento)                              +0.24% acima do mercado (t +6.0, 60% positivos)
   comprar na data limite, vender 5 pregões depois (cota + rendimento)    +0.26% acima do mercado (t +4.3, 59% positivos)
   comprar na data limite, vender 10 pregões depois (cota + rendimento)   +0.43% acima do mercado (t +5.7, 60% positivos)

=== 5. JUROS (SELIC) E O MERCADO DE FIIs ===
               meses  retorno_no_mes  retorno_mes_seguinte  positivos
fase                                                                 
Selic caindo      49            0.12                  0.05       0.63
Selic parada      37            1.00                  0.93       0.70
Selic subindo     32           -0.06                  0.03       0.47
Saltos de rendimento por fase dos juros (retorno acima do mercado, mediana %):
               casos  em_3m  em_6m  acerto_3m
fase                                         
Selic caindo     119   1.73   2.55       0.64
Selic parada      74   3.37   3.30       0.79
Selic subindo     66   2.96   3.64       0.68

=== 6. A BOLSA DE HOJE AVISA O FII DE AMANHÃ? (diário) ===
2443 pregões. Correlação do FII de hoje com: bolsa de hoje +0.44 | bolsa de ontem +0.08 | bolsa de anteontem +0.15 | FII de ontem +0.08 | dólar de ontem -0.04
   bolsa caiu mais de 2% ontem    2017-21:   84 dias | FII hoje -0.099% (t -0.9, 49% positivos) | dia comum -0.007%
   bolsa caiu mais de 2% ontem    2022-26:   50 dias | FII hoje -0.128% (t -2.4, 34% positivos) | dia comum -0.026%
   bolsa subiu mais de 2% ontem   2017-21:   88 dias | FII hoje +0.021% (t +0.1, 65% positivos) | dia comum -0.007%
   bolsa subiu mais de 2% ontem   2022-26:   52 dias | FII hoje +0.109% (t +1.8, 52% positivos) | dia comum -0.026%
   FII caiu mais de 0,5% ontem    2017-21:   55 dias | FII hoje -0.247% (t -0.9, 51% positivos) | dia comum -0.007%
   FII caiu mais de 0,5% ontem    2022-26:   92 dias | FII hoje -0.118% (t -2.6, 38% positivos) | dia comum -0.026%
   FII subiu mais de 0,5% ontem   2017-21:   43 dias | FII hoje +0.223% (t +1.0, 74% positivos) | dia comum -0.007%
   FII subiu mais de 0,5% ontem   2022-26:   40 dias | FII hoje +0.083% (t +0.6, 60% positivos) | dia comum -0.026%
```
