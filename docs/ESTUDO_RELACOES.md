# Estudo: quais relações separam os FIIs que rendem mais (2017 a 2026)

> **Correção de 2026-11-11.** A primeira versão deste estudo (commit `f08dafa`) tinha um erro na conta de retorno: fundos sem rendimento mensal confiável entravam com rendimento zero. Isso baixava o retorno do "mercado" e dos fundos sem dado, e inflava os resultados. Agora o rendimento desses fundos vem do total declarado no informe trimestral da CVM. O que mudou:
>
> | Resultado | Antes (errado) | Agora |
> |---|---|---|
> | Tendência de 12 meses | +0,98% no mês seguinte, t 3,7 | +0,38%, t 1,4: **não se sustenta, retirada** |
> | Rendimento acima do nível dos 6 meses anteriores | +1,48%, t 7,7 | +1,51%, t 8,0: mantida |
> | Rendimento do mês sobre o preço | +1,45%, t 5,6 | +1,37%, t 5,0: mantida |
> | Valor patrimonial crescendo (3 meses seguintes) | +1,64%, t 5,1 | +0,91% nos meses 2 e 3, t 3,5: mantida |
> | Os sinais combinados | +1,54%, t 5,6 | +1,52%, t 5,5: mantida |
> | Salto de rendimento, ganho mediano em 3 / 6 / 12 meses | +2,4% / +3,0% / +5,6% | +1,7% / +1,3% / +1,8% |
> | Salto, casos acima do mercado em 3 / 6 meses | 69% / 67% | 64% / 57% |
>
> As tabelas abaixo desta nota são da versão antiga e ficam como histórico. A saída literal no fim do arquivo é a nova.


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

## Saída literal (versão corrigida, 2026-11-11)

```
Painel: 01/2017 a 10/2026, 396 fundos, 12140 fundo-meses com liquidez >= R$ 200,000/dia

=== 1. SINAIS E O RETORNO DO MÊS SEGUINTE (acima do mercado) ===
                                            sinal  meses  fundos/mês  grupo baixo %  grupo alto %  alto-baixo %     t  meses a favor  1ª metade %    t1  2ª metade %    t2                    monotônico
   queda_no_mes (retorno do mês acima do mercado)    101         123           0.01          0.01         -0.00 -0.01           0.46        -0.27 -0.51         0.19  0.89 +0.01 +0.01 +0.23 +0.27 +0.01
tendencia_12m (retorno de 12 meses, sem o último)     95         115          -0.20          0.18          0.38  1.36           0.60         0.52  1.16         0.29  0.81 -0.20 +0.20 +0.17 +0.23 +0.18
    tendencia_3m (retorno dos 3 meses anteriores)     98         119           0.13         -0.03         -0.17 -0.62           0.46        -0.34 -0.71        -0.05 -0.16 +0.13 +0.26 +0.23 +0.10 -0.03
           preco_sobre_vp (com 2 meses de atraso)    100         121           0.03         -0.14         -0.17 -0.58           0.44        -0.46 -1.12         0.04  0.10 +0.03 +0.31 +0.25 +0.16 -0.14
                       rendimento_12m_sobre_preco     84          80          -0.04          0.39          0.42  1.38           0.62         0.97  1.66         0.18  0.50 -0.04 +0.14 +0.26 +0.55 +0.39
                    rendimento_do_mes_sobre_preco     89          86          -0.28          1.09          1.37  4.99           0.76         2.19  4.51         0.94  2.91 -0.28 -0.07 +0.12 +0.58 +1.09
                rendimento_vs_6m (salto ou queda)     86          84          -0.52          0.98          1.51  8.03           0.80         2.33  7.49         1.11  5.11 -0.52 +0.15 +0.33 +0.55 +0.98
         volume_fora_do_normal (mês ÷ média de 6)     98         120          -0.11          0.24          0.36  1.83           0.63         0.51  1.68         0.25  0.97 -0.11 -0.01 +0.15 +0.44 +0.24
         cotistas_crescendo (3 meses, com atraso)     98         119           0.06          0.14          0.08  0.39           0.57        -0.14 -0.36         0.23  1.04 +0.06 +0.20 +0.10 +0.27 +0.14
                 tamanho (patrimônio, com atraso)    100         121           0.25          0.11         -0.15 -0.82           0.52        -0.36 -1.17         0.01  0.03 +0.25 +0.15 +0.05 +0.06 +0.11
         oscilacao_12m (desvio do retorno mensal)     97         116           0.15         -0.21         -0.36 -1.26           0.57        -0.49 -1.01        -0.28 -0.77 +0.15 +0.19 +0.41 +0.14 -0.21
                   liquidez (volume diário médio)    102         124           0.21          0.11         -0.11 -0.64           0.53         0.10  0.33        -0.27 -1.37 +0.21 -0.06 +0.05 +0.18 +0.11
               vp_crescendo (6 meses, com atraso)     97         117          -0.12          0.25          0.37  2.49           0.63         0.17  0.60         0.51  3.23 -0.12 +0.02 +0.27 +0.26 +0.25

=== 2. MESMOS SINAIS, RETORNO DOS 3 MESES SEGUINTES ===
                                            sinal  meses  alto-baixo %     t  meses a favor  1ª metade %    t1  2ª metade %    t2                    monotônico
   queda_no_mes (retorno do mês acima do mercado)     97         -0.43 -1.06           0.53        -1.08 -1.59         0.05  0.10 -0.26 +0.19 +0.45 +0.19 -0.69
tendencia_12m (retorno de 12 meses, sem o último)     93          0.84  1.69           0.59         0.68  0.89         0.95  1.43 -0.83 +0.20 +0.45 +0.14 +0.01
    tendencia_3m (retorno dos 3 meses anteriores)     96         -0.45 -1.03           0.56        -0.23 -0.34        -0.61 -1.04 -0.12 +0.60 +0.28 -0.12 -0.57
           preco_sobre_vp (com 2 meses de atraso)     97         -0.04 -0.07           0.47        -0.94 -1.42         0.62  0.78 -0.46 +0.52 +0.52 -0.18 -0.50
                       rendimento_12m_sobre_preco     81          0.05  0.09           0.58         2.08  3.02        -0.86 -1.20 -0.17 -0.13 -0.10 +0.58 -0.12
                    rendimento_do_mes_sobre_preco     87          1.65  3.46           0.66         3.44  5.44         0.66  1.06 -0.35 -0.41 -0.15 +0.67 +1.29
                rendimento_vs_6m (salto ou queda)     84          2.21  5.88           0.69         3.69  5.54         1.47  3.46 -1.14 -0.10 +0.29 +0.61 +1.07
         volume_fora_do_normal (mês ÷ média de 6)     96          0.38  1.08           0.55         0.18  0.37         0.52  1.07 -0.31 -0.19 +0.26 +0.26 +0.07
         cotistas_crescendo (3 meses, com atraso)     96         -0.07 -0.22           0.45        -0.30 -0.57         0.09  0.21 +0.18 -0.23 +0.11 -0.08 +0.11
                 tamanho (patrimônio, com atraso)     97          0.18  0.57           0.51        -0.16 -0.33         0.43  1.06 -0.11 +0.22 -0.25 -0.02 +0.07
         oscilacao_12m (desvio do retorno mensal)     95         -1.39 -2.63           0.67        -1.33 -1.53        -1.43 -2.15 +0.27 +0.26 +0.67 -0.08 -1.12
                   liquidez (volume diário médio)     98          0.30  0.88           0.55         0.55  0.86         0.12  0.32 +0.03 -0.27 -0.32 +0.08 +0.33
               vp_crescendo (6 meses, com atraso)     95          1.62  4.90           0.71         1.18  1.93         1.93  5.30 -1.03 +0.04 +0.15 +0.27 +0.59

=== 2b. OS SINAIS FORTES RESISTEM A ENTRAR MAIS TARDE? ===
entrando no 10º pregão do mês seguinte (retorno do resto do mês)
                                            sinal  meses  alto-baixo %    t  meses a favor  1ª metade %    t1  2ª metade %   t2                    monotônico
tendencia_12m (retorno de 12 meses, sem o último)     95          0.29 1.53           0.58         0.62  2.14         0.08 0.33 +0.00 +0.12 +0.18 +0.16 +0.29
                    rendimento_do_mes_sobre_preco     89          1.35 8.54           0.88         1.82  6.37         1.09 6.04 -0.28 +0.10 +0.19 +0.45 +1.07
                rendimento_vs_6m (salto ou queda)     86          0.73 5.73           0.72         1.16  4.55         0.53 3.82 -0.05 +0.22 +0.31 +0.37 +0.68
               vp_crescendo (6 meses, com atraso)     97          0.09 0.71           0.54        -0.10 -0.42         0.21 1.52 +0.02 +0.15 +0.20 +0.28 +0.11
pulando o mês seguinte inteiro (retorno dos meses 2 e 3)
                                            sinal  meses  alto-baixo %    t  meses a favor  1ª metade %   t1  2ª metade %    t2                    monotônico
tendencia_12m (retorno de 12 meses, sem o último)     93          0.79 1.98           0.63         0.56 0.83         0.93  1.91 -0.81 +0.08 +0.30 -0.04 -0.03
                    rendimento_do_mes_sobre_preco     87          0.27 0.71           0.56         1.22 1.98        -0.25 -0.53 -0.10 -0.31 -0.13 +0.10 +0.17
                rendimento_vs_6m (salto ou queda)     84          0.63 2.27           0.58         1.27 2.69         0.31  0.91 -0.56 -0.25 +0.12 -0.00 +0.07
               vp_crescendo (6 meses, com atraso)     95          0.91 3.52           0.61         0.71 1.50         1.05  3.62 -0.68 +0.04 -0.13 -0.02 +0.23
Correlação entre os sinais fortes (posição no ranking):
                               tendencia_12m  rendimento_do_mes_sobre_preco  rendimento_vs_6m  vp_crescendo
tendencia_12m                           1.00                           0.00             -0.00          0.23
rendimento_do_mes_sobre_preco           0.00                           1.00              0.19         -0.16
rendimento_vs_6m                       -0.00                           0.19              1.00          0.04
vp_crescendo                            0.23                          -0.16              0.04          1.00
Sinal combinado (média da posição nos 4 sinais):
 meses  fundos/mês  grupo baixo %  grupo alto %  alto-baixo %    t  meses a favor  1ª metade %   t1  2ª metade %   t2                    monotônico
    84          82          -0.63           0.9          1.52 5.47           0.75         2.63 4.67         1.03 3.47 -0.63 +0.08 +0.40 +0.51 +0.90
Sinal combinado, ano a ano (grupo alto acima do mercado, % ao mês | alto menos baixo):
ano      2019   2020   2021   2022   2023   2024   2025   2026
meses    2.00  12.00  12.00  12.00  12.00  12.00  12.00  10.00
alto     2.95   1.68   1.29   0.62   0.65   0.50   0.93   0.13
dif      6.33   2.33   2.31   1.42   1.46   1.18   0.31   0.73
a_favor  1.00   0.83   0.92   0.83   0.75   0.83   0.50   0.50

=== 3. O PREÇO JÁ SE MEXE ANTES DO SALTO DE RENDIMENTO? ===
salto: 268 casos | retorno acima do mercado (média %, estatística t) e volume relativo (mediana):
   3 mês(es) antes  retorno -0.79% (t -2.8, 31% positivos) | volume 0.97x
   2 mês(es) antes  retorno +0.43% (t +1.3, 41% positivos) | volume 0.99x
   1 mês(es) antes  retorno +0.31% (t +1.2, 40% positivos) | volume 1.00x
   mês do evento    retorno +1.96% (t +7.3, 56% positivos) | volume 1.08x
queda: 189 casos | retorno acima do mercado (média %, estatística t) e volume relativo (mediana):
   3 mês(es) antes  retorno +0.12% (t +0.3, 42% positivos) | volume 1.02x
   2 mês(es) antes  retorno -0.70% (t -1.4, 42% positivos) | volume 1.08x
   1 mês(es) antes  retorno -0.51% (t -1.0, 32% positivos) | volume 1.05x
   mês do evento    retorno -2.33% (t -3.5, 29% positivos) | volume 1.01x

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
Selic caindo      49            0.30                  0.23       0.65
Selic parada      37            1.20                  1.14       0.78
Selic subindo     32            0.25                  0.33       0.50
Saltos de rendimento por fase dos juros (retorno acima do mercado, mediana %):
               casos  em_3m  em_6m  acerto_3m
fase                                         
Selic caindo     122   1.44   1.25       0.61
Selic parada      77   2.54   1.57       0.70
Selic subindo     69   1.78   1.03       0.62

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
