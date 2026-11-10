# Estudo em dias: o que a cota faz, pregão a pregão, depois de um anúncio

Feito em 2026-11-12 com `estudos/dias.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/dias.py`.

## Regra medida (definida pelo dono)

Comprar no pregão seguinte ao anúncio, na abertura. Anúncio antes das 10h: o pregão seguinte é o do mesmo dia. Depois disso: o do dia útil seguinte.

O máximo usa a máxima de cada dia, não só o fechamento. Controle: outros fundos com liquidez comprados na mesma abertura.

## Parte 1: aviso de rendimento com aumento de 25% ou mais (393 casos, 2017 a 2026)

Este é o aviso formal, que sai depois do fechamento do último dia com direito. Não é o fato relevante.

| Pregão | Fechou em (mediana) | Controle | Máximo até o dia (mediana) | Máximo do controle |
|---|---|---|---|---|
| D0 (dia da compra) | −0,11% | −0,06% | +0,63% | +0,46% |
| D+1 | −0,07% | −0,10% | +0,86% | +0,70% |
| D+3 | −0,05% | −0,12% | +1,17% | +1,00% |
| D+5 | 0,00% | −0,15% | +1,45% | +1,23% |
| D+10 | +0,53% | −0,36% | +2,01% | +1,68% |
| D+15 | +0,66% | −0,51% | +2,58% | +2,01% |
| D+20 | +0,57% | −0,78% | +2,93% | +2,34% |
| D+30 | +0,06% | −1,08% | +3,51% | +2,78% |
| D+60 | +1,20% | −1,73% | +5,00% | +4,04% |

| Alvo | Tocou até D+60 | Em quantos pregões (mediana) | Depois voltou abaixo da compra | Controle: tocou |
|---|---|---|---|---|
| +3% | 66% | 9 | 54% | 59% |
| +5% | 50% | 18 | 31% | 43% |
| +8% | 32% | 27,5 | ver saída | 26% |

Leitura: comprando no aviso formal, a vantagem nos primeiros 5 pregões é quase nula e só aparece do 7º pregão em diante. O tamanho do aumento (25–50%, 50–100%, acima de 100%) não muda o máximo de forma relevante. Isso confirma que o gatilho tem que ser o fato relevante, não o aviso de rendimento.

## Parte 2: fato relevante (primeira amostra, 2.969 documentos)

Feito em 2026-11-12 com `estudos/fatos.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/fatos.py`.

### Amostra

2.969 fatos relevantes já baixados, de 02/01/2017 a 26/03/2021 (mais 12 de novembro de 2026). É o começo da fila, não um sorteio: faltam 7.794, de abril de 2021 em diante. Desses 2.969, 2.555 têm papel identificado e 1.252 tinham liquidez na data. O período inclui a queda de março de 2020.

85% dos fatos relevantes saem depois das 17h; 12% antes das 10h.

### Como o tipo foi decidido

Sem IA, por palavras (`fii/classificar.py`). Dois níveis:

1. **Tipo do assunto** (venda, locação, aumento de rendimento citado etc.). Conferência manual de 16 casos: 11 certos. Erra em oferta de cotas e em texto padrão.
2. **O fundo declara o efeito no rendimento** na própria frase ("a próxima distribuição será impactada positivamente em 13,91%"). Conferência manual de 8 casos: 8 certos. É o grupo confiável e o que corresponde ao pedido do dono.

### Resultado: o fundo declarou AUMENTO de rendimento (66 casos)

Cota comprada a R$ 10,00 na abertura do pregão seguinte.

| Dia | 1 em 10 fechou abaixo de | 1 em 4 abaixo de | Caso do meio | 1 em 4 acima de | 1 em 10 acima de | Fechou acima de R$ 10,00 | Acima de R$ 10,50 | Outros fundos, caso do meio |
|---|---|---|---|---|---|---|---|---|
| D+1 | 9,82 | 9,95 | 10,04 | 10,12 | 10,36 | 61% | 8% | 10,00 |
| D+2 | 9,73 | 9,89 | 10,03 | 10,16 | 10,54 | 56% | 12% | 10,00 |
| D+3 | 9,73 | 9,90 | 10,03 | 10,20 | 10,41 | 58% | 9% | 10,01 |
| D+5 | 9,73 | 9,93 | 10,06 | 10,25 | 10,54 | 65% | 12% | 10,02 |
| D+7 | 9,74 | 9,97 | 10,10 | 10,26 | 10,46 | 67% | 9% | 10,02 |
| D+10 | 9,72 | 9,95 | 10,08 | 10,28 | 10,57 | 61% | 14% | 10,04 |
| D+15 | 9,52 | 9,88 | 10,14 | 10,38 | 10,70 | 62% | 20% | 10,04 |
| D+20 | 9,31 | 9,88 | 10,12 | 10,54 | 10,97 | 62% | 29% | 10,06 |
| D+30 | 8,74 | 9,72 | 10,11 | 10,61 | 11,07 | 61% | 29% | 10,05 |
| D+45 | 8,97 | 9,63 | 10,17 | 10,65 | 11,23 | 61% | 32% | 10,06 |
| D+60 | 8,27 | 9,34 | 10,08 | 10,60 | 11,71 | 53% | 30% | 10,03 |

Máxima tocada (pela máxima do dia):

| Até | Caso do meio | Outros fundos | 1 em 4 passou de | 1 em 10 passou de | Dia da máxima |
|---|---|---|---|---|---|
| D+10 | R$ 10,32 | R$ 10,22 | R$ 10,46 | R$ 10,92 | 5º pregão |
| D+20 | R$ 10,42 | R$ 10,34 | R$ 10,74 | R$ 11,25 | 10º pregão |
| D+30 | R$ 10,47 | R$ 10,42 | R$ 10,89 | R$ 11,52 | 16º pregão |
| D+60 | R$ 10,70 | R$ 10,63 | R$ 11,29 | R$ 12,26 | 30º pregão |

### Resultado: o fundo declarou REDUÇÃO de rendimento (42 casos)

| Dia | Caso do meio | Fechou acima de R$ 10,00 | Outros fundos, caso do meio |
|---|---|---|---|
| D+1 | 9,98 | 43% | 10,00 |
| D+3 | 9,96 | 45% | 10,01 |
| D+10 | 9,95 | 45% | 10,04 |
| D+20 | 9,99 | 48% | 10,09 |
| D+30 | 10,05 | 52% | 10,10 |

### Por tamanho do aumento

Não dá para medir ainda: só 26 dos 66 casos dizem o percentual (2 de até 5%, 12 de 5% a 15%, 12 de 15% ou mais). Os outros 40 dizem o valor em reais por cota ou só a direção.

### Leitura

- Quando o fundo declara aumento, a cota abre vantagem já no D+1 (R$ 10,04 contra R$ 10,00) e chega a R$ 10,14 no D+15. Os outros fundos ficam em R$ 10,04.
- A vantagem do caso do meio é pequena: 8 a 10 centavos por cota de R$ 10.
- A diferença maior está nos casos bons: no D+20, 29% estavam acima de R$ 10,50, contra 19% dos outros fundos; 1 em 10 passou de R$ 10,97.
- O risco também existe: no D+30, 1 em 10 estava abaixo de R$ 8,74.
- Declaração de redução: a cota fica abaixo dos outros fundos por 20 pregões e depois se iguala.
- Pelo tipo do assunto, sem a declaração do fundo (212 casos), a vantagem quase some: R$ 10,01 no D+10. A classificação por assunto é fraca demais para servir de gatilho.

### Limites

- 66 casos é pouco, e de um período só (2017 a início de 2021).
- A leitura por palavras perde declarações escritas de outro jeito. A leitura por IA deve achar mais.
- Só preço da cota: sem rendimento recebido, custos ou imposto.
- Fuso da hora de entrega presumido.

## Limites

- Sem rendimento recebido, custos ou imposto.
- Fuso da hora de entrega do FNET presumido (Brasília).
- Controle sorteado com semente fixa.

## Saída literal (parte 1)

```

==============================================================================================================
AVISO DE RENDIMENTO COM AUMENTO DE 25% OU MAIS: compra na abertura do pregão seguinte
==============================================================================================================
393 anúncios com liquidez; 361 com os 60 pregões seguintes completos. Controle: 3110 compras de outros fundos na mesma abertura.

--- dia a dia depois da compra (variação sobre o preço de abertura da compra) ---
            pregão  fechou em (mediana) %  controle %  acima do controle %  casos no positivo  máximo até o dia (mediana) %  máx. controle %  pior até o dia (mediana) %
D0 (dia da compra)                  -0.11       -0.06                -0.05               0.40                          0.63             0.46                       -0.87
               D+1                  -0.07       -0.10                 0.02               0.42                          0.86             0.70                       -1.09
               D+2                  -0.13       -0.12                -0.01               0.43                          1.01             0.87                       -1.32
               D+3                  -0.05       -0.12                 0.07               0.47                          1.17             1.00                       -1.45
               D+5                   0.00       -0.15                 0.15               0.50                          1.45             1.23                       -1.66
               D+7                   0.16       -0.25                 0.41               0.53                          1.79             1.41                       -1.76
              D+10                   0.53       -0.36                 0.88               0.57                          2.01             1.68                       -1.90
              D+15                   0.66       -0.51                 1.16               0.60                          2.58             2.01                       -2.05
              D+20                   0.57       -0.78                 1.35               0.58                          2.93             2.34                       -2.32
              D+30                   0.06       -1.08                 1.14               0.52                          3.51             2.78                       -2.91
              D+45                  -0.01       -1.57                 1.57               0.50                          4.26             3.41                       -3.51
              D+60                   1.20       -1.73                 2.94               0.57                          5.00             4.04                       -4.25

--- tamanho do máximo e dia em que ele aconteceu ---
   grupo até o pregão  casos  máximo: mediana %  1 em 4 passou de %  1 em 10 passou de %  dia do máximo: mediana metade dos casos entre os dias  fechou D+10 acima da compra  fechou D+20 acima da compra  fechou D+30 acima da compra  fechou D+60 acima da compra
 anúncio         D+10    361               2.01                3.67                 6.17                     4.0                          0 e 9                         0.57                          NaN                          NaN                          NaN
 anúncio         D+20    361               2.93                5.46                 8.59                    10.0                         2 e 17                          NaN                         0.58                          NaN                          NaN
 anúncio         D+30    361               3.51                6.12                10.69                    14.0                         3 e 21                          NaN                          NaN                         0.52                          NaN
 anúncio         D+60    361               5.00                9.21                15.09                    22.0                         9 e 48                          NaN                          NaN                          NaN                         0.57
controle         D+10   3110               1.68                3.51                 6.28                     3.0                          0 e 7                         0.43                          NaN                          NaN                          NaN
controle         D+20   3110               2.34                4.87                 8.69                     6.0                         1 e 14                          NaN                         0.39                          NaN                          NaN
controle         D+30   3110               2.78                5.94                10.60                     8.5                         1 e 20                          NaN                          NaN                         0.39                          NaN
controle         D+60   3110               4.04                8.42                14.57                    16.0                         3 e 42                          NaN                          NaN                          NaN                         0.39

--- alvos: quantos tocaram, em quantos pregões, e se depois a cota voltou abaixo da compra (até D+60) ---
                    grupo  casos  +3%: tocou  +3%: em quantos pregões (mediana)  +3%: depois voltou abaixo da compra  +5%: tocou  +5%: em quantos pregões (mediana)  +5%: depois voltou abaixo da compra  +8%: tocou  +8%: em quantos pregões (mediana)  +8%: depois voltou abaixo da compra  +10%: tocou  +10%: em quantos pregões (mediana)  +10%: depois voltou abaixo da compra  +15%: tocou  +15%: em quantos pregões (mediana)  +15%: depois voltou abaixo da compra
                  anúncio    361        0.66                                9.0                                 0.54        0.50                               18.0                                 0.31        0.32                               27.5                                 0.18         0.22                                26.0                                  0.12         0.11                                32.0                                  0.08
                 controle   3110        0.59                               10.0                                 0.62        0.43                               17.0                                 0.46        0.26                               24.0                                 0.30         0.20                                26.0                                  0.26         0.09                                32.0                                  0.23
      aumento de 25 a 50%    194        0.67                                8.0                                 0.50        0.47                               18.0                                 0.25        0.31                               24.0                                 0.21         0.22                                26.0                                  0.14         0.10                                30.0                                  0.10
     aumento de 50 a 100%     96        0.64                                7.0                                 0.62        0.52                               17.0                                 0.40        0.31                               24.5                                 0.17         0.21                                23.0                                  0.10         0.11                                34.0                                  0.00
    aumento acima de 100%     71        0.69                               11.0                                 0.55        0.54                               19.5                                 0.34        0.32                               29.0                                 0.13         0.24                                29.0                                  0.12         0.10                                30.0                                  0.14
   depois se viu: isolado    151        0.62                                8.0                                 0.59        0.44                               17.0                                 0.33        0.31                               27.0                                 0.19         0.19                                28.0                                  0.10         0.07                                28.5                                  0.10
depois se viu: temporário    132        0.69                               11.0                                 0.57        0.50                               18.5                                 0.33        0.30                               26.0                                 0.15         0.23                                24.5                                  0.13         0.14                                35.0                                  0.05
     depois se viu: longo     72        0.72                                8.5                                 0.40        0.60                               19.0                                 0.23        0.38                               35.0                                 0.22         0.28                                40.0                                  0.15         0.11                                25.5                                  0.12
                 até 2021    172        0.69                                9.0                                 0.51        0.52                               18.0                                 0.30        0.33                               24.0                                 0.16         0.23                                26.0                                  0.10         0.10                                27.0                                  0.12
           2022 em diante    189        0.65                                9.0                                 0.57        0.48                               18.0                                 0.32        0.30                               29.0                                 0.21         0.22                                26.0                                  0.15         0.11                                35.0                                  0.05

--- por tipo: tamanho do máximo e dia em que aconteceu ---
                    grupo até o pregão  casos  máximo: mediana %  1 em 4 passou de %  1 em 10 passou de %  dia do máximo: mediana metade dos casos entre os dias  fechou D+10 acima da compra  fechou D+20 acima da compra  fechou D+30 acima da compra  fechou D+60 acima da compra
      aumento de 25 a 50%         D+10    194               1.95                3.82                 5.92                     5.0                          0 e 9                         0.59                          NaN                          NaN                          NaN
      aumento de 25 a 50%         D+20    194               2.67                5.14                 9.02                    10.5                         1 e 17                          NaN                         0.64                          NaN                          NaN
      aumento de 25 a 50%         D+30    194               3.50                5.96                10.93                    14.5                         3 e 22                          NaN                          NaN                         0.53                          NaN
      aumento de 25 a 50%         D+60    194               4.65                9.21                14.95                    24.5                         9 e 48                          NaN                          NaN                          NaN                         0.59
     aumento de 50 a 100%         D+10     96               2.36                3.66                 5.91                     3.0                          0 e 8                         0.56                          NaN                          NaN                          NaN
     aumento de 50 a 100%         D+20     96               3.12                5.61                 8.00                    11.0                         2 e 17                          NaN                         0.56                          NaN                          NaN
     aumento de 50 a 100%         D+30     96               3.52                6.12                10.63                    13.0                         2 e 19                          NaN                          NaN                         0.50                          NaN
     aumento de 50 a 100%         D+60     96               5.24                8.78                16.68                    18.5                         6 e 52                          NaN                          NaN                          NaN                         0.55
    aumento acima de 100%         D+10     71               1.89                3.20                 7.25                     4.0                          0 e 9                         0.55                          NaN                          NaN                          NaN
    aumento acima de 100%         D+20     71               2.82                5.70                 9.60                    10.0                         2 e 18                          NaN                         0.44                          NaN                          NaN
    aumento acima de 100%         D+30     71               3.62                6.69                10.30                    18.0                         6 e 22                          NaN                          NaN                         0.51                          NaN
    aumento acima de 100%         D+60     71               5.63                9.11                12.99                    22.0                        10 e 44                          NaN                          NaN                          NaN                         0.51
   depois se viu: isolado         D+10    151               2.22                3.61                 5.79                     4.0                          0 e 9                         0.60                          NaN                          NaN                          NaN
   depois se viu: isolado         D+20    151               3.01                5.20                 8.43                    11.0                         2 e 17                          NaN                         0.54                          NaN                          NaN
   depois se viu: isolado         D+30    151               3.45                5.97                10.30                    12.0                         3 e 19                          NaN                          NaN                         0.44                          NaN
   depois se viu: isolado         D+60    151               4.29                8.87                11.63                    18.0                         8 e 40                          NaN                          NaN                          NaN                         0.47
depois se viu: temporário         D+10    132               1.88                3.42                 5.71                     5.0                          0 e 8                         0.58                          NaN                          NaN                          NaN
depois se viu: temporário         D+20    132               2.81                5.49                 8.39                    10.0                         1 e 17                          NaN                         0.60                          NaN                          NaN
depois se viu: temporário         D+30    132               3.32                6.29                11.63                    15.0                         4 e 22                          NaN                          NaN                         0.56                          NaN
depois se viu: temporário         D+60    132               5.02                9.10                17.35                    25.0                         9 e 50                          NaN                          NaN                          NaN                         0.56
     depois se viu: longo         D+10     72               2.28                4.14                 6.32                     3.5                          0 e 7                         0.50                          NaN                          NaN                          NaN
     depois se viu: longo         D+20     72               3.08                5.71                10.28                     9.0                         1 e 17                          NaN                         0.60                          NaN                          NaN
     depois se viu: longo         D+30     72               4.00                6.04                11.02                    16.0                         4 e 23                          NaN                          NaN                         0.58                          NaN
     depois se viu: longo         D+60     72               6.26               10.29                14.91                    37.0                        15 e 57                          NaN                          NaN                          NaN                         0.76
                 até 2021         D+10    172               2.05                3.92                 6.03                     4.0                          0 e 9                         0.55                          NaN                          NaN                          NaN
                 até 2021         D+20    172               2.86                5.40                 9.53                    10.0                         1 e 17                          NaN                         0.56                          NaN                          NaN
                 até 2021         D+30    172               3.68                5.84                10.78                    14.5                         3 e 21                          NaN                          NaN                         0.51                          NaN
                 até 2021         D+60    172               5.20                9.45                14.63                    22.0                         6 e 54                          NaN                          NaN                          NaN                         0.56
           2022 em diante         D+10    189               1.92                3.56                 7.26                     4.0                          0 e 9                         0.60                          NaN                          NaN                          NaN
           2022 em diante         D+20    189               3.04                5.60                 8.42                    10.0                         2 e 17                          NaN                         0.60                          NaN                          NaN
           2022 em diante         D+30    189               3.45                6.43                10.37                    14.0                         4 e 21                          NaN                          NaN                         0.52                          NaN
           2022 em diante         D+60    189               4.56                8.70                15.89                    22.0                         9 e 45                          NaN                          NaN                          NaN                         0.57
```

## Saída literal (parte 2)

```
Fatos relevantes lidos: 2969, de 02/01/2017 a 10/11/2026 | com papel na bolsa identificado: 2555
Hora de entrega: antes das 10h 12% | 10h às 17h 3% | 17h em diante 85%

Tipo principal de cada fato relevante (classificação por palavras):
                                                 documentos  com_valor_por_cota  continuacao
outros assuntos                                         696                  45           53
aumento de rendimento dito no texto                     375                 129           63
emissão de cotas                                        354                  29           13
venda de ativo, sem falar em ganho                      325                  98           33
saída de inquilino ou inadimplência                     251                  86           25
reorganização do fundo                                  217                   9           12
redução de rendimento dita no texto                     195                  38           11
compra de ativo                                         190                  41           33
locação nova ou renovada                                174                  45           10
recebimento extraordinário (multa, indenização)         105                  25           20
venda de ativo com ganho                                 86                  38           17
venda de ativo com perda                                  1                   0            0

Com liquidez e preço: 1252 | repetições do mesmo fundo e tipo em até 10 pregões: 239

========================================================================================================================
COMPRA NA ABERTURA DO PREGÃO SEGUINTE AO FATO RELEVANTE
========================================================================================================================

--- TODOS os que se encaixam: aumento ou possível aumento de rendimento, sem sinal contrário no texto: 212 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.81              9.92                     10.01            10.09             10.23            0.06                   0.52            0.06            0.03                           10.08                            9.92                     10.00                    0.01
 D+2               9.74              9.90                     10.01            10.10             10.25            0.10                   0.52            0.07            0.02                           10.10                            9.91                     10.00                    0.02
 D+3               9.74              9.90                     10.02            10.11             10.30            0.16                   0.54            0.10            0.02                           10.12                            9.90                     10.00                    0.03
 D+5               9.66              9.89                     10.03            10.19             10.34            0.28                   0.58            0.13            0.06                           10.17                            9.87                     10.00                    0.05
 D+7               9.55              9.84                     10.03            10.19             10.45            0.31                   0.57            0.17            0.07                           10.22                            9.85                     10.00                    0.07
D+10               9.54              9.81                     10.01            10.24             10.53            0.13                   0.52            0.23            0.12                           10.24                            9.82                     10.00                    0.09
D+15               9.46              9.78                     10.01            10.28             10.60            0.06                   0.51            0.24            0.13                           10.31                            9.76                     10.00                    0.11
D+20               9.41              9.73                     10.02            10.32             10.71            0.21                   0.51            0.26            0.20                           10.38                            9.73                     10.01                    0.15
D+30               9.13              9.67                     10.03            10.43             10.77            0.27                   0.53            0.32            0.22                           10.48                            9.63                     10.01                    0.18
D+45               8.86              9.55                     10.03            10.63             11.01            0.27                   0.52            0.36            0.29                           10.59                            9.56                     10.01                    0.21
D+60               8.48              9.31                     10.05            10.58             11.27            0.53                   0.51            0.35            0.27                           10.66                            9.49                      9.99                    0.24
   máxima até D+10: caso do meio R$ 10.24 (outros fundos R$ 10.19) | 1 em 4 passou de R$ 10.51 | 1 em 10 passou de R$ 10.73 | dia da máxima: 4º pregão (metade entre o 1º e o 8º)
   máxima até D+20: caso do meio R$ 10.38 (outros fundos R$ 10.29) | 1 em 4 passou de R$ 10.70 | 1 em 10 passou de R$ 11.05 | dia da máxima: 7º pregão (metade entre o 2º e o 16º)
   máxima até D+30: caso do meio R$ 10.48 (outros fundos R$ 10.35) | 1 em 4 passou de R$ 10.81 | 1 em 10 passou de R$ 11.14 | dia da máxima: 12º pregão (metade entre o 3º e o 22º)
   máxima até D+60: caso do meio R$ 10.66 (outros fundos R$ 10.52) | 1 em 4 passou de R$ 11.07 | 1 em 10 passou de R$ 11.61 | dia da máxima: 23º pregão (metade entre o 5º e o 48º)

--- aumento de rendimento dito no texto: 121 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.81              9.91                     10.01            10.11             10.23            0.07                   0.55            0.07            0.02                           10.08                            9.91                     10.00                    0.01
 D+2               9.73              9.85                     10.00            10.11             10.23            0.00                   0.50            0.07            0.02                           10.09                            9.90                     10.00                    0.02
 D+3               9.73              9.87                     10.01            10.12             10.31            0.12                   0.53            0.11            0.02                           10.11                            9.90                     10.00                    0.02
 D+5               9.66              9.87                     10.03            10.19             10.33            0.29                   0.58            0.12            0.05                           10.18                            9.88                     10.00                    0.04
 D+7               9.55              9.84                     10.03            10.18             10.43            0.28                   0.57            0.17            0.07                           10.25                            9.85                     10.00                    0.05
D+10               9.54              9.81                     10.01            10.26             10.52            0.07                   0.53            0.23            0.11                           10.28                            9.83                     10.00                    0.08
D+15               9.55              9.76                     10.06            10.29             10.59            0.61                   0.57            0.25            0.12                           10.33                            9.77                     10.00                    0.12
D+20               9.44              9.80                     10.05            10.37             10.71            0.47                   0.58            0.30            0.22                           10.42                            9.75                     10.00                    0.15
D+30               9.27              9.75                     10.12            10.53             10.77            1.20                   0.61            0.38            0.26                           10.54                            9.66                     10.01                    0.20
D+45               8.98              9.73                     10.10            10.69             11.05            1.00                   0.62            0.41            0.31                           10.66                            9.64                     10.02                    0.22
D+60               8.78              9.59                     10.10            10.58             11.32            1.02                   0.55            0.38            0.27                           10.68                            9.57                      9.99                    0.25
   máxima até D+10: caso do meio R$ 10.28 (outros fundos R$ 10.18) | 1 em 4 passou de R$ 10.54 | 1 em 10 passou de R$ 10.70 | dia da máxima: 5º pregão (metade entre o 1º e o 8º)
   máxima até D+20: caso do meio R$ 10.42 (outros fundos R$ 10.28) | 1 em 4 passou de R$ 10.70 | 1 em 10 passou de R$ 11.05 | dia da máxima: 9º pregão (metade entre o 2º e o 17º)
   máxima até D+30: caso do meio R$ 10.54 (outros fundos R$ 10.37) | 1 em 4 passou de R$ 10.80 | 1 em 10 passou de R$ 11.14 | dia da máxima: 15º pregão (metade entre o 3º e o 24º)
   máxima até D+60: caso do meio R$ 10.68 (outros fundos R$ 10.52) | 1 em 4 passou de R$ 11.18 | 1 em 10 passou de R$ 11.73 | dia da máxima: 29º pregão (metade entre o 6º e o 50º)

--- venda de ativo com ganho: 36 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.84              9.96                     10.00            10.06             10.16            0.04                   0.53            0.06            0.03                           10.07                            9.94                     10.00                    0.01
 D+2               9.86              9.94                     10.03            10.07             10.32            0.25                   0.61            0.11            0.03                           10.11                            9.93                     10.00                    0.04
 D+3               9.81              9.96                     10.03            10.11             10.40            0.26                   0.58            0.14            0.06                           10.14                            9.93                     10.00                    0.05
 D+5               9.66              9.94                     10.05            10.20             10.52            0.50                   0.64            0.17            0.11                           10.17                            9.88                     10.00                    0.08
 D+7               9.55              9.79                     10.00            10.30             10.51            0.01                   0.50            0.25            0.11                           10.19                            9.86                     10.00                    0.09
D+10               9.65              9.82                     10.01            10.31             10.62            0.10                   0.50            0.28            0.17                           10.21                            9.83                     10.02                    0.13
D+15               9.64              9.89                     10.02            10.43             10.59            0.22                   0.56            0.31            0.17                           10.26                            9.77                     10.02                    0.14
D+20               9.56              9.82                     10.09            10.27             10.75            0.89                   0.58            0.25            0.17                           10.35                            9.77                     10.02                    0.16
D+30               9.47              9.68                      9.93            10.31             10.75           -0.67                   0.47            0.25            0.17                           10.41                            9.66                     10.01                    0.18
D+45               8.98              9.45                      9.99            10.63             10.95           -0.11                   0.50            0.36            0.31                           10.59                            9.55                     10.00                    0.21
D+60               7.62              9.09                     10.14            10.61             10.90            1.39                   0.56            0.42            0.36                           10.73                            9.55                      9.97                    0.23
   máxima até D+10: caso do meio R$ 10.21 (outros fundos R$ 10.20) | 1 em 4 passou de R$ 10.52 | 1 em 10 passou de R$ 10.87 | dia da máxima: 4º pregão (metade entre o 1º e o 6º)
   máxima até D+20: caso do meio R$ 10.35 (outros fundos R$ 10.30) | 1 em 4 passou de R$ 10.80 | 1 em 10 passou de R$ 11.04 | dia da máxima: 6º pregão (metade entre o 2º e o 17º)
   máxima até D+30: caso do meio R$ 10.41 (outros fundos R$ 10.39) | 1 em 4 passou de R$ 10.85 | 1 em 10 passou de R$ 11.20 | dia da máxima: 14º pregão (metade entre o 5º e o 25º)
   máxima até D+60: caso do meio R$ 10.73 (outros fundos R$ 10.57) | 1 em 4 passou de R$ 11.02 | 1 em 10 passou de R$ 11.59 | dia da máxima: 22º pregão (metade entre o 5º e o 51º)

--- recebimento extraordinário (multa, indenização): poucos casos (14) ---

--- locação nova ou renovada: 41 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.87              9.92                      9.99            10.08             10.20           -0.08                   0.46            0.02            0.02                           10.08                            9.90                     10.00                    0.01
 D+2               9.87              9.91                     10.00            10.06             10.26           -0.02                   0.49            0.05            0.02                           10.10                            9.90                     10.00                    0.02
 D+3               9.80              9.91                     10.00            10.07             10.21            0.02                   0.54            0.07            0.00                           10.10                            9.89                     10.00                    0.02
 D+5               9.76              9.88                     10.03            10.16             10.26            0.28                   0.61            0.10            0.05                           10.18                            9.85                     10.00                    0.04
 D+7               9.82              9.95                     10.07            10.19             10.44            0.67                   0.68            0.12            0.07                           10.19                            9.85                     10.01                    0.05
D+10               9.70              9.91                     10.06            10.14             10.50            0.55                   0.59            0.20            0.12                           10.21                            9.78                     10.01                    0.07
D+15               9.71              9.82                      9.96            10.08             10.65           -0.35                   0.41            0.17            0.15                           10.25                            9.76                     10.02                    0.13
D+20               9.53              9.73                      9.94            10.16             10.70           -0.60                   0.34            0.22            0.20                           10.35                            9.70                     10.01                    0.14
D+30               9.19              9.67                      9.91            10.34             10.71           -0.88                   0.46            0.27            0.17                           10.38                            9.57                     10.02                    0.18
D+45               9.25              9.47                      9.70            10.54             10.78           -3.00                   0.39            0.27            0.27                           10.38                            9.44                      9.98                    0.22
D+60               8.49              9.22                      9.73            10.24             10.82           -2.71                   0.41            0.24            0.22                           10.39                            9.31                      9.94                    0.23
   máxima até D+10: caso do meio R$ 10.21 (outros fundos R$ 10.19) | 1 em 4 passou de R$ 10.39 | 1 em 10 passou de R$ 10.68 | dia da máxima: 4º pregão (metade entre o 1º e o 8º)
   máxima até D+20: caso do meio R$ 10.35 (outros fundos R$ 10.29) | 1 em 4 passou de R$ 10.67 | 1 em 10 passou de R$ 11.11 | dia da máxima: 7º pregão (metade entre o 2º e o 13º)
   máxima até D+30: caso do meio R$ 10.38 (outros fundos R$ 10.39) | 1 em 4 passou de R$ 10.81 | 1 em 10 passou de R$ 11.11 | dia da máxima: 10º pregão (metade entre o 2º e o 20º)
   máxima até D+60: caso do meio R$ 10.39 (outros fundos R$ 10.55) | 1 em 4 passou de R$ 10.95 | 1 em 10 passou de R$ 11.33 | dia da máxima: 14º pregão (metade entre o 4º e o 38º)

--- valor informado por cota abaixo de 1% do preço: 57 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.82              9.93                     10.02            10.12             10.25            0.19                   0.60            0.05            0.05                           10.10                            9.96                     10.00                    0.02
 D+2               9.75              9.90                     10.03            10.11             10.29            0.32                   0.60            0.11            0.05                           10.12                            9.95                     10.00                    0.03
 D+3               9.80              9.93                     10.05            10.17             10.34            0.47                   0.63            0.14            0.05                           10.14                            9.93                     10.00                    0.04
 D+5               9.75              9.94                     10.03            10.25             10.55            0.29                   0.63            0.21            0.14                           10.20                            9.91                     10.00                    0.07
 D+7               9.55              9.91                     10.07            10.25             10.45            0.75                   0.63            0.23            0.07                           10.23                            9.86                     10.00                    0.07
D+10               9.55              9.87                     10.00            10.26             10.56           -0.02                   0.49            0.25            0.12                           10.30                            9.83                     10.00                    0.08
D+15               9.54              9.75                      9.99            10.29             10.53           -0.07                   0.49            0.25            0.11                           10.33                            9.76                      9.98                    0.10
D+20               9.40              9.63                      9.94            10.19             10.55           -0.60                   0.40            0.21            0.12                           10.37                            9.72                      9.97                    0.11
D+30               9.00              9.59                      9.85            10.13             10.67           -1.49                   0.37            0.19            0.16                           10.39                            9.57                      9.96                    0.15
D+45               8.99              9.43                      9.79            10.15             10.64           -2.12                   0.35            0.19            0.12                           10.45                            9.50                      9.94                    0.18
D+60               8.01              8.98                      9.87            10.15             10.74           -1.32                   0.40            0.21            0.16                           10.56                            9.38                      9.86                    0.19
   máxima até D+10: caso do meio R$ 10.30 (outros fundos R$ 10.18) | 1 em 4 passou de R$ 10.53 | 1 em 10 passou de R$ 10.69 | dia da máxima: 5º pregão (metade entre o 1º e o 7º)
   máxima até D+20: caso do meio R$ 10.37 (outros fundos R$ 10.27) | 1 em 4 passou de R$ 10.66 | 1 em 10 passou de R$ 10.92 | dia da máxima: 5º pregão (metade entre o 2º e o 12º)
   máxima até D+30: caso do meio R$ 10.39 (outros fundos R$ 10.36) | 1 em 4 passou de R$ 10.68 | 1 em 10 passou de R$ 11.24 | dia da máxima: 7º pregão (metade entre o 2º e o 17º)
   máxima até D+60: caso do meio R$ 10.56 (outros fundos R$ 10.48) | 1 em 4 passou de R$ 10.83 | 1 em 10 passou de R$ 11.38 | dia da máxima: 14º pregão (metade entre o 4º e o 47º)

--- valor informado por cota entre 1% e 3% do preço: poucos casos (10) ---

--- valor informado por cota de 3% do preço ou mais: poucos casos (14) ---

--- primeira notícia (texto não diz que é continuação de fato anterior): 176 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.82              9.92                     10.01            10.10             10.23            0.06                   0.53            0.05            0.02                           10.08                            9.92                     10.00                    0.01
 D+2               9.77              9.91                     10.02            10.10             10.22            0.18                   0.54            0.06            0.01                           10.10                            9.91                     10.00                    0.02
 D+3               9.75              9.92                     10.02            10.11             10.29            0.20                   0.56            0.10            0.02                           10.12                            9.90                     10.00                    0.03
 D+5               9.69              9.91                     10.03            10.18             10.34            0.32                   0.60            0.14            0.06                           10.17                            9.88                     10.00                    0.05
 D+7               9.65              9.85                     10.04            10.18             10.43            0.35                   0.59            0.16            0.06                           10.22                            9.85                     10.00                    0.07
D+10               9.56              9.83                     10.02            10.23             10.53            0.20                   0.53            0.22            0.12                           10.24                            9.83                     10.00                    0.09
D+15               9.54              9.79                     10.01            10.28             10.56            0.11                   0.52            0.24            0.12                           10.32                            9.76                     10.00                    0.13
D+20               9.47              9.78                     10.02            10.30             10.62            0.21                   0.52            0.26            0.19                           10.38                            9.74                     10.01                    0.15
D+30               9.28              9.69                     10.03            10.41             10.76            0.31                   0.54            0.31            0.20                           10.48                            9.63                     10.02                    0.19
D+45               8.89              9.58                     10.04            10.58             11.00            0.36                   0.54            0.35            0.27                           10.59                            9.56                     10.02                    0.22
D+60               8.41              9.31                     10.05            10.59             11.31            0.53                   0.51            0.35            0.28                           10.67                            9.48                     10.00                    0.24
   máxima até D+10: caso do meio R$ 10.24 (outros fundos R$ 10.20) | 1 em 4 passou de R$ 10.48 | 1 em 10 passou de R$ 10.72 | dia da máxima: 4º pregão (metade entre o 1º e o 8º)
   máxima até D+20: caso do meio R$ 10.38 (outros fundos R$ 10.29) | 1 em 4 passou de R$ 10.69 | 1 em 10 passou de R$ 11.03 | dia da máxima: 8º pregão (metade entre o 2º e o 16º)
   máxima até D+30: caso do meio R$ 10.48 (outros fundos R$ 10.36) | 1 em 4 passou de R$ 10.80 | 1 em 10 passou de R$ 11.13 | dia da máxima: 12º pregão (metade entre o 3º e o 21º)
   máxima até D+60: caso do meio R$ 10.67 (outros fundos R$ 10.51) | 1 em 4 passou de R$ 11.08 | 1 em 10 passou de R$ 11.61 | dia da máxima: 22º pregão (metade entre o 5º e o 48º)

--- continuação de fato relevante anterior: 36 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.77              9.88                     10.00            10.09             10.30           -0.02                   0.47            0.11            0.06                           10.09                            9.94                     10.00                    0.01
 D+2               9.71              9.82                     10.00            10.09             10.35           -0.04                   0.44            0.11            0.08                           10.09                            9.92                     10.01                    0.02
 D+3               9.74              9.82                     10.00            10.08             10.33           -0.01                   0.47            0.14            0.06                           10.11                            9.90                     10.00                    0.02
 D+5               9.50              9.74                      9.99            10.20             10.27           -0.08                   0.50            0.08            0.06                           10.18                            9.79                     10.00                    0.04
 D+7               9.08              9.70                     10.01            10.24             10.49            0.11                   0.50            0.22            0.11                           10.22                            9.78                      9.99                    0.05
D+10               8.69              9.63                     10.00            10.30             10.50           -0.01                   0.47            0.28            0.11                           10.27                            9.76                     10.00                    0.08
D+15               8.23              9.65                     10.00            10.31             10.66            0.00                   0.47            0.25            0.19                           10.27                            9.74                     10.00                    0.10
D+20               8.41              9.49                     10.00            10.42             10.78            0.05                   0.50            0.31            0.25                           10.38                            9.66                     10.00                    0.14
D+30               8.51              9.49                     10.01            10.67             10.89            0.06                   0.50            0.39            0.31                           10.47                            9.58                     10.02                    0.21
D+45               8.65              9.32                      9.97            10.74             11.00           -0.33                   0.44            0.39            0.39                           10.54                            9.54                     10.01                    0.20
D+60               8.56              9.29                     10.04            10.47             10.84            0.41                   0.50            0.33            0.25                           10.55                            9.54                     10.00                    0.20
   máxima até D+10: caso do meio R$ 10.27 (outros fundos R$ 10.22) | 1 em 4 passou de R$ 10.55 | 1 em 10 passou de R$ 10.77 | dia da máxima: 4º pregão (metade entre o 2º e o 7º)
   máxima até D+20: caso do meio R$ 10.38 (outros fundos R$ 10.31) | 1 em 4 passou de R$ 10.73 | 1 em 10 passou de R$ 11.12 | dia da máxima: 5º pregão (metade entre o 2º e o 15º)
   máxima até D+30: caso do meio R$ 10.47 (outros fundos R$ 10.41) | 1 em 4 passou de R$ 10.83 | 1 em 10 passou de R$ 11.15 | dia da máxima: 8º pregão (metade entre o 2º e o 25º)
   máxima até D+60: caso do meio R$ 10.55 (outros fundos R$ 10.54) | 1 em 4 passou de R$ 11.01 | 1 em 10 passou de R$ 11.66 | dia da máxima: 24º pregão (metade entre o 3º e o 49º)

========================================================================================================================
O FUNDO INFORMOU O TAMANHO DO EFEITO NO RENDIMENTO (texto do próprio fato relevante)
========================================================================================================================
111 fatos relevantes em que o fundo declara efeito no rendimento | aumento: 67 (com percentual: 26, mediana 13.4%) | redução: 44 (com percentual: 23, mediana 11.6%)

--- O FUNDO DECLAROU AUMENTO de rendimento (qualquer tamanho): 66 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.82              9.95                     10.04            10.12             10.36            0.39                   0.61            0.12            0.08                           10.10                            9.92                     10.00                    0.03
 D+2               9.73              9.89                     10.03            10.16             10.54            0.29                   0.56            0.17            0.12                           10.16                            9.90                     10.00                    0.05
 D+3               9.73              9.90                     10.03            10.20             10.41            0.29                   0.58            0.18            0.09                           10.18                            9.89                     10.01                    0.06
 D+5               9.73              9.93                     10.06            10.25             10.54            0.63                   0.65            0.21            0.12                           10.20                            9.88                     10.02                    0.07
 D+7               9.74              9.97                     10.10            10.26             10.46            1.00                   0.67            0.21            0.09                           10.25                            9.87                     10.02                    0.08
D+10               9.72              9.95                     10.08            10.28             10.57            0.82                   0.61            0.24            0.14                           10.32                            9.86                     10.04                    0.11
D+15               9.52              9.88                     10.14            10.38             10.70            1.40                   0.62            0.33            0.20                           10.39                            9.82                     10.04                    0.14
D+20               9.31              9.88                     10.12            10.54             10.97            1.15                   0.62            0.38            0.29                           10.42                            9.78                     10.06                    0.19
D+30               8.74              9.72                     10.11            10.61             11.07            1.08                   0.61            0.36            0.29                           10.47                            9.75                     10.05                    0.23
D+45               8.97              9.63                     10.17            10.65             11.23            1.72                   0.61            0.41            0.32                           10.62                            9.69                     10.06                    0.26
D+60               8.27              9.34                     10.08            10.60             11.71            0.80                   0.53            0.38            0.30                           10.70                            9.62                     10.03                    0.29
   máxima até D+10: caso do meio R$ 10.32 (outros fundos R$ 10.22) | 1 em 4 passou de R$ 10.46 | 1 em 10 passou de R$ 10.92 | dia da máxima: 5º pregão (metade entre o 0º e o 8º)
   máxima até D+20: caso do meio R$ 10.42 (outros fundos R$ 10.34) | 1 em 4 passou de R$ 10.74 | 1 em 10 passou de R$ 11.25 | dia da máxima: 10º pregão (metade entre o 3º e o 17º)
   máxima até D+30: caso do meio R$ 10.47 (outros fundos R$ 10.42) | 1 em 4 passou de R$ 10.89 | 1 em 10 passou de R$ 11.52 | dia da máxima: 16º pregão (metade entre o 6º e o 25º)
   máxima até D+60: caso do meio R$ 10.70 (outros fundos R$ 10.63) | 1 em 4 passou de R$ 11.29 | 1 em 10 passou de R$ 12.26 | dia da máxima: 30º pregão (metade entre o 10º e o 50º)

--- aumento declarado de até 5%: poucos casos (2) ---

--- aumento declarado de 5% a 15%: poucos casos (12) ---

--- aumento declarado de 15% ou mais: poucos casos (12) ---

--- aumento declarado sem dizer o percentual: 40 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.84              9.95                     10.04            10.14             10.57            0.39                   0.62            0.18            0.12                           10.09                            9.90                     10.00                    0.05
 D+2               9.70              9.89                     10.03            10.18             10.64            0.29                   0.55            0.22            0.20                           10.15                            9.89                     10.00                    0.08
 D+3               9.63              9.89                     10.03            10.28             10.69            0.28                   0.57            0.25            0.15                           10.19                            9.87                     10.00                    0.10
 D+5               9.60              9.92                     10.04            10.29             10.84            0.43                   0.68            0.25            0.20                           10.21                            9.86                     10.00                    0.11
 D+7               9.54              9.95                     10.09            10.35             11.04            0.93                   0.62            0.28            0.12                           10.27                            9.84                     10.01                    0.12
D+10               9.62              9.93                     10.10            10.32             11.05            1.04                   0.57            0.28            0.18                           10.34                            9.83                     10.02                    0.15
D+15               9.20              9.77                     10.14            10.50             10.97            1.41                   0.60            0.35            0.25                           10.40                            9.82                     10.04                    0.17
D+20               8.10              9.73                     10.09            10.48             11.21            0.91                   0.55            0.32            0.25                           10.42                            9.74                     10.04                    0.21
D+30               7.94              9.59                     10.02            10.52             11.37            0.23                   0.52            0.32            0.25                           10.45                            9.74                     10.02                    0.23
D+45               8.16              9.29                     10.04            10.60             11.35            0.36                   0.52            0.40            0.28                           10.61                            9.65                      9.94                    0.23
D+60               7.70              9.18                      9.93            10.64             11.98           -0.66                   0.45            0.30            0.25                           10.66                            9.56                      9.92                    0.25
   máxima até D+10: caso do meio R$ 10.34 (outros fundos R$ 10.19) | 1 em 4 passou de R$ 10.66 | 1 em 10 passou de R$ 11.48 | dia da máxima: 5º pregão (metade entre o 0º e o 8º)
   máxima até D+20: caso do meio R$ 10.42 (outros fundos R$ 10.35) | 1 em 4 passou de R$ 10.76 | 1 em 10 passou de R$ 11.94 | dia da máxima: 8º pregão (metade entre o 3º e o 15º)
   máxima até D+30: caso do meio R$ 10.45 (outros fundos R$ 10.41) | 1 em 4 passou de R$ 11.24 | 1 em 10 passou de R$ 12.10 | dia da máxima: 12º pregão (metade entre o 5º e o 21º)
   máxima até D+60: caso do meio R$ 10.66 (outros fundos R$ 10.56) | 1 em 4 passou de R$ 11.55 | 1 em 10 passou de R$ 12.68 | dia da máxima: 20º pregão (metade entre o 6º e o 47º)

--- O FUNDO DECLAROU REDUÇÃO de rendimento (qualquer tamanho): 42 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.58              9.86                      9.98            10.11             10.20           -0.18                   0.43            0.05            0.00                           10.08                            9.86                     10.00                    0.02
 D+2               9.55              9.85                      9.99            10.08             10.29           -0.14                   0.45            0.10            0.00                           10.09                            9.84                     10.00                    0.04
 D+3               9.57              9.86                      9.96            10.09             10.22           -0.43                   0.45            0.10            0.02                           10.12                            9.84                     10.01                    0.05
 D+5               9.55              9.86                      9.99            10.10             10.34           -0.11                   0.45            0.12            0.07                           10.14                            9.82                     10.03                    0.08
 D+7               9.60              9.75                      9.98            10.16             10.35           -0.18                   0.48            0.12            0.10                           10.14                            9.76                     10.02                    0.11
D+10               9.62              9.72                      9.95            10.13             10.51           -0.49                   0.45            0.14            0.12                           10.20                            9.70                     10.03                    0.15
D+15               9.53              9.76                      9.98            10.16             10.70           -0.17                   0.45            0.19            0.14                           10.22                            9.68                     10.06                    0.20
D+20               9.55              9.86                      9.99            10.14             10.63           -0.11                   0.48            0.17            0.17                           10.23                            9.66                     10.08                    0.22
D+30               9.38              9.74                     10.05            10.50             10.78            0.49                   0.52            0.36            0.26                           10.28                            9.62                     10.11                    0.26
D+45               9.56              9.79                     10.10            10.61             11.04            0.99                   0.55            0.36            0.31                           10.48                            9.55                     10.15                    0.30
D+60               9.39              9.73                     10.07            10.64             10.94            0.66                   0.55            0.43            0.33                           10.61                            9.45                     10.18                    0.34
   máxima até D+10: caso do meio R$ 10.20 (outros fundos R$ 10.21) | 1 em 4 passou de R$ 10.41 | 1 em 10 passou de R$ 10.78 | dia da máxima: 1º pregão (metade entre o 0º e o 5º)
   máxima até D+20: caso do meio R$ 10.23 (outros fundos R$ 10.34) | 1 em 4 passou de R$ 10.43 | 1 em 10 passou de R$ 10.95 | dia da máxima: 4º pregão (metade entre o 0º e o 12º)
   máxima até D+30: caso do meio R$ 10.28 (outros fundos R$ 10.43) | 1 em 4 passou de R$ 10.76 | 1 em 10 passou de R$ 11.58 | dia da máxima: 13º pregão (metade entre o 1º e o 25º)
   máxima até D+60: caso do meio R$ 10.61 (outros fundos R$ 10.70) | 1 em 4 passou de R$ 11.54 | 1 em 10 passou de R$ 11.72 | dia da máxima: 37º pregão (metade entre o 14º e o 54º)

--- redução declarada de 10% ou mais: poucos casos (13) ---

--- COMPARAÇÃO: notícia ruim (saída de inquilino, redução de rendimento, venda com perda): 112 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.67              9.87                      9.99            10.09             10.28           -0.14                   0.46            0.07            0.03                           10.09                            9.84                     10.00                    0.03
 D+2               9.49              9.83                      9.96            10.09             10.29           -0.38                   0.44            0.09            0.05                           10.12                            9.84                     10.00                    0.04
 D+3               9.48              9.83                      9.94            10.09             10.23           -0.56                   0.40            0.09            0.05                           10.13                            9.80                     10.00                    0.04
 D+5               9.34              9.73                      9.95            10.10             10.24           -0.52                   0.41            0.08            0.04                           10.18                            9.77                     10.00                    0.06
 D+7               9.35              9.78                      9.94            10.12             10.38           -0.58                   0.44            0.12            0.06                           10.21                            9.76                      9.99                    0.07
D+10               9.38              9.76                      9.93            10.09             10.33           -0.73                   0.40            0.13            0.09                           10.24                            9.72                     10.00                    0.10
D+15               9.36              9.78                      9.94            10.20             10.78           -0.57                   0.43            0.19            0.14                           10.28                            9.66                     10.00                    0.14
D+20               9.26              9.72                      9.98            10.22             10.80           -0.19                   0.46            0.21            0.15                           10.31                            9.62                     10.00                    0.17
D+30               9.12              9.72                     10.01            10.44             11.01            0.07                   0.50            0.31            0.24                           10.40                            9.57                      9.99                    0.20
D+45               8.62              9.63                      9.99            10.69             11.44           -0.05                   0.49            0.38            0.30                           10.55                            9.48                     10.00                    0.23
D+60               8.61              9.41                      9.96            10.62             11.42           -0.39                   0.48            0.41            0.30                           10.65                            9.44                     10.00                    0.25
   máxima até D+10: caso do meio R$ 10.24 (outros fundos R$ 10.20) | 1 em 4 passou de R$ 10.41 | 1 em 10 passou de R$ 10.82 | dia da máxima: 2º pregão (metade entre o 0º e o 6º)
   máxima até D+20: caso do meio R$ 10.31 (outros fundos R$ 10.30) | 1 em 4 passou de R$ 10.60 | 1 em 10 passou de R$ 11.34 | dia da máxima: 6º pregão (metade entre o 0º e o 14º)
   máxima até D+30: caso do meio R$ 10.40 (outros fundos R$ 10.37) | 1 em 4 passou de R$ 10.86 | 1 em 10 passou de R$ 11.67 | dia da máxima: 11º pregão (metade entre o 0º e o 22º)
   máxima até D+60: caso do meio R$ 10.65 (outros fundos R$ 10.53) | 1 em 4 passou de R$ 11.55 | 1 em 10 passou de R$ 12.24 | dia da máxima: 32º pregão (metade entre o 6º e o 49º)

--- COMPARAÇÃO: fatos relevantes sobre outros assuntos: 449 casos | cota comprada a R$ 10,00 ---
 dia  1 em 10 abaixo de  1 em 4 abaixo de  FECHOU EM (caso do meio)  1 em 4 acima de  1 em 10 acima de  ganho % (meio)  fechou acima de 10,00  acima de 10,30  acima de 10,50  máxima tocada até o dia (meio)  mínima tocada até o dia (meio)  outros fundos: fechou em  outros: acima de 10,50
 D+1               9.78              9.90                     10.00            10.10             10.22            0.00                   0.48            0.06            0.02                           10.08                            9.89                     10.00                    0.02
 D+2               9.71              9.90                     10.00            10.11             10.26            0.00                   0.49            0.08            0.04                           10.10                            9.87                     10.00                    0.02
 D+3               9.69              9.87                     10.00            10.12             10.30           -0.02                   0.49            0.10            0.05                           10.12                            9.85                     10.00                    0.04
 D+5               9.61              9.84                     10.00            10.16             10.44            0.01                   0.50            0.16            0.08                           10.16                            9.82                     10.00                    0.05
 D+7               9.56              9.81                      9.99            10.21             10.51           -0.08                   0.49            0.19            0.11                           10.18                            9.80                     10.00                    0.06
D+10               9.54              9.78                     10.00            10.23             10.67            0.00                   0.49            0.20            0.14                           10.21                            9.77                     10.01                    0.09
D+15               9.46              9.78                     10.00            10.29             10.82            0.04                   0.51            0.24            0.17                           10.26                            9.73                     10.02                    0.13
D+20               9.36              9.74                     10.02            10.38             10.80            0.24                   0.53            0.28            0.20                           10.30                            9.69                     10.03                    0.16
D+30               9.21              9.71                     10.04            10.48             10.89            0.42                   0.53            0.33            0.24                           10.40                            9.65                     10.04                    0.20
D+45               9.00              9.60                     10.05            10.52             11.11            0.45                   0.54            0.35            0.26                           10.51                            9.57                     10.04                    0.24
D+60               8.82              9.41                     10.00            10.62             11.25            0.00                   0.50            0.37            0.29                           10.63                            9.48                     10.03                    0.26
   máxima até D+10: caso do meio R$ 10.21 (outros fundos R$ 10.20) | 1 em 4 passou de R$ 10.47 | 1 em 10 passou de R$ 10.97 | dia da máxima: 3º pregão (metade entre o 0º e o 8º)
   máxima até D+20: caso do meio R$ 10.30 (outros fundos R$ 10.30) | 1 em 4 passou de R$ 10.66 | 1 em 10 passou de R$ 11.20 | dia da máxima: 8º pregão (metade entre o 1º e o 16º)
   máxima até D+30: caso do meio R$ 10.40 (outros fundos R$ 10.38) | 1 em 4 passou de R$ 10.87 | 1 em 10 passou de R$ 11.43 | dia da máxima: 13º pregão (metade entre o 2º e o 24º)
   máxima até D+60: caso do meio R$ 10.63 (outros fundos R$ 10.56) | 1 em 4 passou de R$ 11.18 | 1 em 10 passou de R$ 11.88 | dia da máxima: 26º pregão (metade entre o 6º e o 46º)
```
