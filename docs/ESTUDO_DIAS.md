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

## Parte 2: fato relevante

Pendente. 10.813 fatos relevantes e 14.938 comunicados listados desde 2017; download em andamento.

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
