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

## Parte 2: fato relevante (primeira amostra, 2.969 documentos; substituída pela parte 3)

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

## Parte 3: fato relevante, todos os documentos (10.696), formato novo

Feito em 2026-11-11, depois de concluído o download. Substitui a parte 2, que era só o começo da fila (2017 a março de 2021) e mostrava um efeito maior do que o conjunto completo confirma.

### Download

- 10.696 fatos relevantes com texto, de 02/01/2017 a 10/11/2026.
- 111 sem texto (PDF só de imagem) e 6 com erro (4 arquivos vazios no FNET, 2 recusas do FNET). Ficam como pendência.
- 7.980 com papel identificado; 4.034 com liquidez na data; 692 repetições do mesmo fundo e tipo em até 10 pregões foram descartadas.
- Os 14.929 comunicados ao mercado estão só listados, não baixados.

### Nomes das colunas

Pessimista: 1 em cada 4 casos foi pior. Típico: o caso do meio. Otimista: 1 em cada 4 foi melhor. Cota comprada a R$ 10,00 na abertura do pregão seguinte.

### O fundo declarou AUMENTO de rendimento (147 casos)

| Dia | Mínima do dia | Fechamento | Máxima do dia | Fechamento pessimista | Fechamento otimista | Maior preço até o dia: típico | Maior preço: otimista | Menor preço até o dia: típico | Menor preço: pessimista |
|---|---|---|---|---|---|---|---|---|---|
| D0 | 9,94 | 10,01 | 10,07 | 9,95 | 10,09 | 10,07 | 10,15 | 9,94 | 9,86 |
| D+1 | 9,94 | 10,02 | 10,08 | 9,94 | 10,12 | 10,10 | 10,19 | 9,91 | 9,81 |
| D+3 | 9,96 | 10,03 | 10,10 | 9,91 | 10,17 | 10,15 | 10,29 | 9,89 | 9,76 |
| D+5 | 9,95 | 10,02 | 10,10 | 9,92 | 10,20 | 10,18 | 10,34 | 9,87 | 9,72 |
| D+7 | 9,96 | 10,04 | 10,09 | 9,91 | 10,21 | 10,20 | 10,39 | 9,85 | 9,70 |
| D+10 | 9,94 | 10,01 | 10,08 | 9,89 | 10,24 | 10,24 | 10,44 | 9,82 | 9,68 |
| D+15 | 9,96 | 10,01 | 10,10 | 9,81 | 10,30 | 10,30 | 10,54 | 9,75 | 9,59 |
| D+20 | 9,96 | 10,03 | 10,10 | 9,80 | 10,38 | 10,35 | 10,65 | 9,73 | 9,55 |
| D+30 | 9,92 | 10,02 | 10,09 | 9,69 | 10,36 | 10,41 | 10,79 | 9,69 | 9,38 |
| D+60 | 9,85 | 9,91 | 9,97 | 9,41 | 10,48 | 10,59 | 10,97 | 9,49 | 9,00 |

Maior preço: no 4º pregão (até D+10), no 10º (até D+20), no 13º (até D+30).
Ordem de venda a R$ 10,30: executada em 29% até D+5, 43% até D+10, 54% até D+20, 61% até D+30.
Outros fundos na mesma abertura (fechamento típico): 10,00 em D+1, D+5 e D+10; 9,96 em D+20.

### O fundo declarou REDUÇÃO de rendimento (101 casos)

Fechamento típico: 9,97 em D0, 9,95 em D+1, 9,93 em D+3, 9,94 em D+10, 9,96 em D+20, 9,90 em D+30. Fechou acima da compra em 36% a 44% dos casos nos primeiros 20 pregões. Outros fundos: 9,99 a 10,00.

### Por assunto do texto

- Venda de ativo com ganho (229 casos): fechamento típico de 10,00 a 10,01 até D+5 e 9,99 em D+10 e D+20. Praticamente igual aos outros fundos.
- Valor por cota informado de 3% do preço ou mais (73 casos): típico de 10,04 em D+5 e D+7, 10,05 em D+15; ordem a R$ 10,50 executada em 37% até D+20.
- Valor por cota entre 1% e 3% (71 casos): sem diferença para os outros fundos.

### Leitura

- No conjunto completo, o caso típico quase não sai do lugar: a cota fecha entre R$ 10,01 e R$ 10,04 nos primeiros 30 pregões depois de um aumento declarado.
- A vantagem sobre os outros fundos existe, mas é de 2 a 7 centavos por cota de R$ 10.
- O que há de aproveitável é a parte de cima: o cenário otimista chega a R$ 10,38 no D+20, e o maior preço tocado até lá passa de R$ 10,65 em 1 caso a cada 4.
- A redução declarada tem efeito mais nítido que o aumento: 6 em cada 10 fecham abaixo da compra nos primeiros 20 pregões.
- A parte 2, com 66 casos, mostrava R$ 10,14 no D+15. Com 147 casos é R$ 10,01. Amostra pequena engana.

### Limites

- Leitura por palavras: acha 147 aumentos declarados em 10.696 fatos relevantes. Há mais, escritos de outro jeito.
- Só 35 aumentos dizem o percentual; não dá para separar por tamanho.
- Sem rendimento recebido, custos ou imposto.

## Saída literal (parte 3, todos os documentos)

```
Fatos relevantes lidos: 10696, de 02/01/2017 a 10/11/2026 | com papel na bolsa identificado: 7980
Hora de entrega: antes das 10h 13% | 10h às 17h 3% | 17h em diante 84%

Tipo principal de cada fato relevante (classificação por palavras):
                                                 documentos  com_valor_por_cota  continuacao
outros assuntos                                        3001                 253          319
venda de ativo, sem falar em ganho                     1480                 272          222
aumento de rendimento dito no texto                     925                 386          158
emissão de cotas                                        904                  57           33
redução de rendimento dita no texto                     815                  92           25
reorganização do fundo                                  805                  42           75
saída de inquilino ou inadimplência                     659                 213           71
locação nova ou renovada                                651                 272           41
compra de ativo                                         588                  96           86
venda de ativo com ganho                                572                 325          112
recebimento extraordinário (multa, indenização)         292                 112           47
venda de ativo com perda                                  4                   0            0

Com liquidez e preço: 4034 | repetições do mesmo fundo e tipo em até 10 pregões: 692

========================================================================================================================
COMPRA NA ABERTURA DO PREGÃO SEGUINTE AO FATO RELEVANTE
========================================================================================================================

--- TODOS os que se encaixam: aumento ou possível aumento de rendimento, sem sinal contrário no texto: 708 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.00          10.06
        D+1           9.95       10.00          10.06
        D+2           9.95       10.00          10.06
        D+3           9.94       10.00          10.06
        D+5           9.94       10.00          10.06
        D+7           9.93        9.99          10.05
       D+10           9.92        9.99          10.04
       D+15           9.93        9.98          10.04
       D+20           9.93        9.98          10.05
       D+30           9.90        9.95          10.01
       D+45           9.86        9.94          10.00
       D+60           9.85        9.90           9.97
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.00     10.06                    0.49            0.03            0.01
        D+1        9.93   10.00     10.08                    0.49            0.05            0.02
        D+2        9.92   10.00     10.09                    0.51            0.07            0.02
        D+3        9.91   10.00     10.10                    0.51            0.07            0.02
        D+5        9.89   10.00     10.13                    0.50            0.10            0.04
        D+7        9.87    9.99     10.14                    0.48            0.12            0.05
       D+10        9.83    9.99     10.16                    0.47            0.15            0.07
       D+15        9.79    9.98     10.19                    0.46            0.17            0.09
       D+20        9.77    9.98     10.19                    0.47            0.19            0.12
       D+30        9.69    9.95     10.26                    0.45            0.23            0.14
       D+45        9.58    9.94     10.35                    0.45            0.27            0.19
       D+60        9.41    9.90     10.38                    0.44            0.28            0.20
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.06                  10.12                 9.95                     9.88
        D+1                10.08                  10.17                 9.92                     9.84
        D+2                10.10                  10.20                 9.90                     9.81
        D+3                10.11                  10.24                 9.89                     9.78
        D+5                10.14                  10.29                 9.87                     9.73
        D+7                10.16                  10.34                 9.84                     9.70
       D+10                10.18                  10.39                 9.81                     9.65
       D+15                10.23                  10.46                 9.76                     9.58
       D+20                10.25                  10.54                 9.73                     9.48
       D+30                10.31                  10.64                 9.67                     9.38
       D+45                10.39                  10.79                 9.57                     9.20
       D+60                10.44                  10.88                 9.49                     9.04
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 7º pregão | até D+30: 11º pregão | até D+60: 21º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 24% até D+5, 35% até D+10, 46% até D+20, 52% até D+30 | R$ 10.50: 10% até D+5, 17% até D+10, 28% até D+20, 34% até D+30 | R$ 11.00: 2% até D+5, 4% até D+10, 8% até D+20, 10% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 9.99 | D+5: 10.00 x 9.99 | D+10: 9.99 x 9.98 | D+20: 9.98 x 9.96 | D+30: 9.95 x 9.95

--- aumento de rendimento dito no texto: 264 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.93       10.00          10.04
        D+1           9.93        9.99          10.04
        D+2           9.92        9.98          10.05
        D+3           9.92        9.99          10.04
        D+5           9.92        9.98          10.03
        D+7           9.91        9.99          10.04
       D+10           9.93        9.99          10.03
       D+15           9.96       10.01          10.05
       D+20           9.93        9.99          10.05
       D+30           9.94       10.00          10.04
       D+45           9.93       10.00          10.04
       D+60           9.89        9.94          10.01
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.94   10.00     10.06                    0.44            0.04            0.01
        D+1        9.91    9.99     10.09                    0.46            0.05            0.02
        D+2        9.89    9.98     10.09                    0.44            0.06            0.02
        D+3        9.89    9.99     10.10                    0.47            0.08            0.02
        D+5        9.87    9.98     10.12                    0.46            0.09            0.04
        D+7        9.85    9.99     10.12                    0.48            0.11            0.05
       D+10        9.83    9.99     10.16                    0.47            0.16            0.08
       D+15        9.79   10.01     10.22                    0.50            0.17            0.09
       D+20        9.78    9.99     10.21                    0.49            0.19            0.13
       D+30        9.69   10.00     10.30                    0.50            0.25            0.16
       D+45        9.61   10.00     10.40                    0.50            0.30            0.20
       D+60        9.46    9.94     10.41                    0.45            0.30            0.19
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.04                  10.11                 9.93                     9.87
        D+1                10.07                  10.15                 9.91                     9.82
        D+2                10.09                  10.19                 9.89                     9.77
        D+3                10.10                  10.23                 9.88                     9.75
        D+5                10.12                  10.26                 9.86                     9.69
        D+7                10.15                  10.32                 9.84                     9.67
       D+10                10.18                  10.40                 9.81                     9.64
       D+15                10.23                  10.50                 9.76                     9.56
       D+20                10.25                  10.58                 9.74                     9.47
       D+30                10.30                  10.67                 9.66                     9.37
       D+45                10.40                  10.83                 9.60                     9.20
       D+60                10.46                  10.88                 9.56                     9.08
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 8º pregão | até D+30: 12º pregão | até D+60: 24º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 20% até D+5, 34% até D+10, 44% até D+20, 51% até D+30 | R$ 10.50: 11% até D+5, 19% até D+10, 30% até D+20, 37% até D+30 | R$ 11.00: 2% até D+5, 5% até D+10, 8% até D+20, 9% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 9.99 x 10.00 | D+5: 9.98 x 9.99 | D+10: 9.99 x 9.98 | D+20: 9.99 x 9.97 | D+30: 10.00 x 9.95

--- venda de ativo com ganho: 229 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.00          10.06
        D+1           9.96       10.00          10.06
        D+2           9.96       10.01          10.07
        D+3           9.96       10.01          10.07
        D+5           9.95       10.01          10.06
        D+7           9.94        9.99          10.05
       D+10           9.94        9.99          10.04
       D+15           9.94        9.98          10.04
       D+20           9.95        9.99          10.08
       D+30           9.89        9.95          10.01
       D+45           9.88        9.95          10.00
       D+60           9.90        9.96          10.03
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.97   10.00     10.05                    0.51            0.02            0.01
        D+1        9.95   10.00     10.06                    0.49            0.03            0.02
        D+2        9.94   10.01     10.07                    0.55            0.09            0.01
        D+3        9.93   10.01     10.09                    0.53            0.08            0.02
        D+5        9.91   10.01     10.14                    0.52            0.11            0.05
        D+7        9.89    9.99     10.15                    0.49            0.13            0.06
       D+10        9.83    9.99     10.19                    0.49            0.16            0.07
       D+15        9.82    9.98     10.16                    0.47            0.16            0.07
       D+20        9.80    9.99     10.16                    0.49            0.17            0.08
       D+30        9.73    9.95     10.26                    0.45            0.22            0.12
       D+45        9.62    9.95     10.37                    0.46            0.28            0.20
       D+60        9.56    9.96     10.42                    0.47            0.30            0.22
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.06                  10.12                 9.95                     9.90
        D+1                10.08                  10.17                 9.93                     9.87
        D+2                10.10                  10.18                 9.92                     9.84
        D+3                10.11                  10.21                 9.90                     9.82
        D+5                10.14                  10.27                 9.87                     9.78
        D+7                10.16                  10.31                 9.86                     9.73
       D+10                10.17                  10.37                 9.84                     9.68
       D+15                10.20                  10.44                 9.80                     9.59
       D+20                10.24                  10.49                 9.77                     9.55
       D+30                10.31                  10.57                 9.70                     9.44
       D+45                10.39                  10.75                 9.58                     9.29
       D+60                10.43                  10.84                 9.53                     9.11
Dia em que a cota fez o maior preço: até D+10: 4º pregão | até D+20: 7º pregão | até D+30: 12º pregão | até D+60: 24º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 24% até D+5, 33% até D+10, 45% até D+20, 51% até D+30 | R$ 10.50: 8% até D+5, 15% até D+10, 24% até D+20, 31% até D+30 | R$ 11.00: 2% até D+5, 3% até D+10, 7% até D+20, 9% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 9.99 | D+5: 10.01 x 9.98 | D+10: 9.99 x 9.97 | D+20: 9.99 x 9.96 | D+30: 9.95 x 9.93

--- recebimento extraordinário (multa, indenização): 50 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.94       10.00          10.07
        D+1           9.96        9.99          10.06
        D+2           9.94       10.00          10.06
        D+3           9.95        9.99          10.06
        D+5           9.94       10.00          10.04
        D+7           9.93        9.97          10.04
       D+10           9.93        9.96          10.03
       D+15           9.95        9.98          10.00
       D+20           9.95       10.00          10.05
       D+30           9.82        9.87           9.93
       D+45           9.83        9.93           9.98
       D+60           9.69        9.73           9.84
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.91   10.00     10.05                    0.48            0.02            0.00
        D+1        9.92    9.99     10.06                    0.46            0.06            0.02
        D+2        9.92   10.00     10.06                    0.50            0.06            0.00
        D+3        9.93    9.99     10.09                    0.46            0.04            0.02
        D+5        9.93   10.00     10.09                    0.48            0.08            0.02
        D+7        9.89    9.97     10.06                    0.44            0.14            0.00
       D+10        9.77    9.96     10.16                    0.40            0.16            0.06
       D+15        9.82    9.98     10.16                    0.46            0.18            0.14
       D+20        9.70   10.00     10.20                    0.54            0.22            0.12
       D+30        9.66    9.87     10.08                    0.30            0.12            0.12
       D+45        9.60    9.93     10.05                    0.28            0.12            0.12
       D+60        9.52    9.73     10.19                    0.36            0.22            0.12
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.11                 9.94                     9.86
        D+1                10.09                  10.14                 9.94                     9.82
        D+2                10.10                  10.15                 9.93                     9.78
        D+3                10.12                  10.18                 9.90                     9.76
        D+5                10.13                  10.29                 9.88                     9.74
        D+7                10.15                  10.44                 9.83                     9.72
       D+10                10.16                  10.48                 9.79                     9.59
       D+15                10.17                  10.57                 9.76                     9.51
       D+20                10.23                  10.59                 9.72                     9.49
       D+30                10.28                  10.67                 9.64                     9.40
       D+45                10.30                  10.71                 9.58                     9.28
       D+60                10.43                  10.74                 9.51                     9.14
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 8º pregão | até D+30: 10º pregão | até D+60: 15º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 26% até D+5, 38% até D+10, 46% até D+20, 50% até D+30 | R$ 10.50: 14% até D+5, 20% até D+10, 30% até D+20, 32% até D+30 | R$ 11.00: 0% até D+5, 0% até D+10, 8% até D+20, 10% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 9.99 x 9.99 | D+5: 10.00 x 10.00 | D+10: 9.96 x 10.00 | D+20: 10.00 x 9.99 | D+30: 9.87 x 9.96

--- locação nova ou renovada: 165 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.01          10.08
        D+1           9.96       10.01          10.08
        D+2           9.95       10.02          10.08
        D+3           9.95       10.02          10.08
        D+5           9.95       10.02          10.08
        D+7           9.94       10.00          10.08
       D+10           9.89        9.98          10.05
       D+15           9.88        9.94          10.02
       D+20           9.89        9.95          10.01
       D+30           9.85        9.93          10.00
       D+45           9.78        9.86           9.92
       D+60           9.69        9.76           9.83
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.01     10.07                    0.56            0.02            0.01
        D+1        9.94   10.01     10.12                    0.53            0.05            0.02
        D+2        9.93   10.02     10.12                    0.56            0.07            0.02
        D+3        9.91   10.02     10.12                    0.55            0.07            0.02
        D+5        9.90   10.02     10.14                    0.56            0.10            0.04
        D+7        9.89   10.00     10.15                    0.50            0.11            0.07
       D+10        9.84    9.98     10.14                    0.47            0.13            0.08
       D+15        9.73    9.94     10.17                    0.40            0.17            0.12
       D+20        9.71    9.95     10.19                    0.41            0.20            0.13
       D+30        9.66    9.93     10.26                    0.44            0.22            0.13
       D+45        9.43    9.86     10.29                    0.39            0.25            0.19
       D+60        9.22    9.76     10.28                    0.38            0.25            0.21
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.08                  10.15                 9.95                     9.86
        D+1                10.10                  10.19                 9.92                     9.84
        D+2                10.13                  10.26                 9.90                     9.82
        D+3                10.14                  10.28                 9.89                     9.79
        D+5                10.17                  10.34                 9.86                     9.74
        D+7                10.18                  10.37                 9.84                     9.72
       D+10                10.20                  10.40                 9.79                     9.67
       D+15                10.27                  10.45                 9.74                     9.56
       D+20                10.29                  10.53                 9.70                     9.43
       D+30                10.35                  10.70                 9.59                     9.29
       D+45                10.38                  10.86                 9.45                     9.08
       D+60                10.45                  10.97                 9.31                     8.83
Dia em que a cota fez o maior preço: até D+10: 4º pregão | até D+20: 6º pregão | até D+30: 8º pregão | até D+60: 17º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 29% até D+5, 38% até D+10, 49% até D+20, 55% até D+30 | R$ 10.50: 10% até D+5, 14% até D+10, 27% até D+20, 36% até D+30 | R$ 11.00: 2% até D+5, 5% até D+10, 11% até D+20, 13% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.01 x 10.00 | D+5: 10.02 x 9.99 | D+10: 9.98 x 9.98 | D+20: 9.95 x 9.96 | D+30: 9.93 x 9.92

--- valor informado por cota abaixo de 1% do preço: 254 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.00          10.06
        D+1           9.96       10.00          10.06
        D+2           9.96       10.00          10.06
        D+3           9.95       10.01          10.06
        D+5           9.94       10.00          10.06
        D+7           9.93        9.99          10.04
       D+10           9.91        9.97          10.03
       D+15           9.90        9.96          10.01
       D+20           9.90        9.96          10.01
       D+30           9.85        9.91           9.98
       D+45           9.78        9.85           9.94
       D+60           9.77        9.84           9.90
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.00     10.06                    0.51            0.03            0.01
        D+1        9.93   10.00     10.08                    0.50            0.03            0.02
        D+2        9.91   10.00     10.10                    0.51            0.07            0.02
        D+3        9.90   10.01     10.10                    0.52            0.06            0.02
        D+5        9.90   10.00     10.14                    0.50            0.10            0.06
        D+7        9.86    9.99     10.15                    0.46            0.13            0.04
       D+10        9.81    9.97     10.15                    0.45            0.15            0.07
       D+15        9.75    9.96     10.17                    0.43            0.16            0.09
       D+20        9.74    9.96     10.17                    0.44            0.19            0.11
       D+30        9.63    9.91     10.15                    0.42            0.18            0.10
       D+45        9.46    9.85     10.24                    0.41            0.22            0.14
       D+60        9.28    9.84     10.26                    0.41            0.24            0.17
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.06                  10.12                 9.95                     9.89
        D+1                10.08                  10.16                 9.94                     9.86
        D+2                10.10                  10.18                 9.91                     9.83
        D+3                10.11                  10.23                 9.90                     9.79
        D+5                10.14                  10.29                 9.87                     9.74
        D+7                10.15                  10.32                 9.84                     9.69
       D+10                10.17                  10.37                 9.82                     9.66
       D+15                10.19                  10.44                 9.76                     9.56
       D+20                10.23                  10.47                 9.72                     9.47
       D+30                10.28                  10.59                 9.60                     9.32
       D+45                10.33                  10.72                 9.52                     9.14
       D+60                10.37                  10.81                 9.40                     8.95
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 6º pregão | até D+30: 10º pregão | até D+60: 20º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 23% até D+5, 35% até D+10, 43% até D+20, 47% até D+30 | R$ 10.50: 9% até D+5, 16% até D+10, 24% até D+20, 30% até D+30 | R$ 11.00: 2% até D+5, 4% até D+10, 7% até D+20, 9% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 9.99 | D+5: 10.00 x 9.99 | D+10: 9.97 x 9.97 | D+20: 9.96 x 9.94 | D+30: 9.91 x 9.91

--- valor informado por cota entre 1% e 3% do preço: 71 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.93       10.00          10.06
        D+1           9.96       10.00          10.05
        D+2           9.95        9.99          10.04
        D+3           9.95        9.99          10.04
        D+5           9.92        9.96          10.03
        D+7           9.91        9.99          10.02
       D+10           9.91        9.98          10.04
       D+15           9.91       10.00          10.04
       D+20           9.88        9.99          10.04
       D+30           9.90       10.00          10.04
       D+45           9.82        9.92           9.97
       D+60           9.89        9.96           9.99
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.97   10.00     10.04                    0.46            0.01            0.00
        D+1        9.96   10.00     10.07                    0.49            0.07            0.03
        D+2        9.94    9.99     10.07                    0.48            0.11            0.03
        D+3        9.92    9.99     10.07                    0.48            0.06            0.01
        D+5        9.87    9.96     10.08                    0.44            0.08            0.03
        D+7        9.88    9.99     10.12                    0.46            0.11            0.08
       D+10        9.81    9.98     10.19                    0.48            0.14            0.07
       D+15        9.74   10.00     10.16                    0.49            0.14            0.04
       D+20        9.66    9.99     10.14                    0.46            0.14            0.08
       D+30        9.70   10.00     10.22                    0.49            0.21            0.13
       D+45        9.66    9.92     10.33                    0.44            0.27            0.18
       D+60        9.57    9.96     10.42                    0.44            0.37            0.21
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.06                  10.11                 9.93                     9.88
        D+1                10.08                  10.15                 9.91                     9.86
        D+2                10.09                  10.17                 9.90                     9.82
        D+3                10.10                  10.18                 9.88                     9.80
        D+5                10.12                  10.24                 9.86                     9.74
        D+7                10.14                  10.30                 9.84                     9.71
       D+10                10.16                  10.40                 9.81                     9.66
       D+15                10.20                  10.45                 9.78                     9.53
       D+20                10.24                  10.48                 9.73                     9.48
       D+30                10.32                  10.53                 9.71                     9.40
       D+45                10.43                  10.65                 9.58                     9.23
       D+60                10.46                  10.81                 9.50                     9.05
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 8º pregão | até D+30: 9º pregão | até D+60: 24º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 20% até D+5, 32% até D+10, 46% até D+20, 51% até D+30 | R$ 10.50: 10% até D+5, 17% até D+10, 24% até D+20, 30% até D+30 | R$ 11.00: 4% até D+5, 6% até D+10, 8% até D+20, 10% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 10.00 | D+5: 9.96 x 9.98 | D+10: 9.98 x 9.98 | D+20: 9.99 x 9.95 | D+30: 10.00 x 9.97

--- valor informado por cota de 3% do preço ou mais: 73 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.01          10.07
        D+1           9.95       10.01          10.07
        D+2           9.96       10.03          10.07
        D+3           9.98       10.02          10.09
        D+5           9.97       10.04          10.09
        D+7           9.95       10.04          10.09
       D+10           9.96       10.03          10.07
       D+15           9.97       10.05          10.09
       D+20           9.96       10.01          10.11
       D+30           9.93        9.98          10.06
       D+45           9.95       10.03          10.07
       D+60           9.95       10.01          10.10
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.94   10.01     10.11                    0.52            0.07            0.05
        D+1        9.94   10.01     10.14                    0.51            0.11            0.07
        D+2        9.96   10.03     10.08                    0.59            0.16            0.05
        D+3        9.95   10.02     10.13                    0.56            0.11            0.07
        D+5        9.92   10.04     10.18                    0.56            0.15            0.10
        D+7        9.91   10.04     10.18                    0.58            0.16            0.10
       D+10        9.88   10.03     10.26                    0.55            0.19            0.10
       D+15        9.86   10.05     10.23                    0.59            0.21            0.12
       D+20        9.87   10.01     10.22                    0.55            0.23            0.14
       D+30        9.79    9.98     10.30                    0.48            0.25            0.15
       D+45        9.64   10.03     10.38                    0.52            0.32            0.18
       D+60        9.57   10.01     10.45                    0.51            0.30            0.23
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.17                 9.95                     9.87
        D+1                10.10                  10.26                 9.94                     9.84
        D+2                10.11                  10.30                 9.92                     9.83
        D+3                10.15                  10.30                 9.91                     9.81
        D+5                10.18                  10.35                 9.88                     9.77
        D+7                10.18                  10.44                 9.87                     9.75
       D+10                10.20                  10.55                 9.86                     9.74
       D+15                10.28                  10.66                 9.83                     9.66
       D+20                10.33                  10.73                 9.79                     9.64
       D+30                10.38                  10.74                 9.72                     9.57
       D+45                10.47                  10.78                 9.71                     9.43
       D+60                10.47                  10.84                 9.65                     9.29
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 7º pregão | até D+30: 13º pregão | até D+60: 18º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 33% até D+5, 42% até D+10, 55% até D+20, 59% até D+30 | R$ 10.50: 16% até D+5, 26% até D+10, 37% até D+20, 45% até D+30 | R$ 11.00: 3% até D+5, 7% até D+10, 11% até D+20, 12% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.01 x 10.00 | D+5: 10.04 x 10.01 | D+10: 10.03 x 10.01 | D+20: 10.01 x 10.00 | D+30: 9.98 x 9.98

--- primeira notícia (texto não diz que é continuação de fato anterior): 595 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.94       10.00          10.06
        D+1           9.95       10.00          10.06
        D+2           9.95       10.01          10.06
        D+3           9.94       10.01          10.06
        D+5           9.94       10.00          10.06
        D+7           9.93        9.99          10.05
       D+10           9.91        9.98          10.04
       D+15           9.92        9.97          10.03
       D+20           9.92        9.97          10.04
       D+30           9.88        9.95          10.00
       D+45           9.85        9.92           9.99
       D+60           9.81        9.89           9.97
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.00     10.06                    0.50            0.03            0.01
        D+1        9.93   10.00     10.08                    0.50            0.05            0.02
        D+2        9.92   10.01     10.10                    0.52            0.08            0.01
        D+3        9.91   10.01     10.11                    0.51            0.08            0.02
        D+5        9.89   10.00     10.13                    0.51            0.10            0.04
        D+7        9.87    9.99     10.14                    0.48            0.12            0.05
       D+10        9.83    9.98     10.15                    0.46            0.15            0.07
       D+15        9.78    9.97     10.18                    0.45            0.16            0.09
       D+20        9.75    9.97     10.18                    0.46            0.18            0.11
       D+30        9.69    9.95     10.26                    0.44            0.22            0.13
       D+45        9.57    9.92     10.34                    0.44            0.26            0.18
       D+60        9.34    9.89     10.39                    0.43            0.29            0.20
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.06                  10.12                 9.94                     9.87
        D+1                10.09                  10.17                 9.92                     9.84
        D+2                10.10                  10.20                 9.90                     9.82
        D+3                10.11                  10.24                 9.89                     9.79
        D+5                10.14                  10.30                 9.87                     9.73
        D+7                10.16                  10.35                 9.84                     9.71
       D+10                10.18                  10.40                 9.81                     9.65
       D+15                10.23                  10.46                 9.76                     9.57
       D+20                10.26                  10.53                 9.73                     9.46
       D+30                10.32                  10.64                 9.65                     9.37
       D+45                10.38                  10.79                 9.56                     9.20
       D+60                10.45                  10.90                 9.45                     9.01
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 7º pregão | até D+30: 10º pregão | até D+60: 20º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 25% até D+5, 35% até D+10, 46% até D+20, 52% até D+30 | R$ 10.50: 10% até D+5, 16% até D+10, 27% até D+20, 34% até D+30 | R$ 11.00: 2% até D+5, 4% até D+10, 8% até D+20, 10% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 10.00 | D+5: 10.00 x 9.99 | D+10: 9.98 x 9.98 | D+20: 9.97 x 9.96 | D+30: 9.95 x 9.94

--- continuação de fato relevante anterior: 113 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.96       10.00          10.05
        D+1           9.96        9.99          10.04
        D+2           9.96       10.00          10.05
        D+3           9.95       10.00          10.06
        D+5           9.93       10.00          10.05
        D+7           9.94       10.00          10.07
       D+10           9.98       10.02          10.08
       D+15           9.99       10.03          10.06
       D+20           9.97       10.02          10.07
       D+30           9.95       10.01          10.05
       D+45           9.95        9.99          10.02
       D+60           9.91        9.99          10.02
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.97   10.00     10.05                    0.46            0.05            0.01
        D+1        9.92    9.99     10.07                    0.43            0.04            0.03
        D+2        9.90   10.00     10.07                    0.47            0.05            0.04
        D+3        9.89   10.00     10.08                    0.48            0.06            0.03
        D+5        9.88   10.00     10.12                    0.49            0.06            0.04
        D+7        9.91   10.00     10.11                    0.50            0.12            0.07
       D+10        9.87   10.02     10.20                    0.54            0.17            0.10
       D+15        9.88   10.03     10.24                    0.53            0.19            0.13
       D+20        9.88   10.02     10.21                    0.56            0.20            0.13
       D+30        9.70   10.01     10.25                    0.52            0.24            0.17
       D+45        9.62    9.99     10.42                    0.48            0.29            0.22
       D+60        9.61    9.99     10.32                    0.48            0.26            0.18
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.05                  10.12                 9.96                     9.90
        D+1                10.07                  10.15                 9.94                     9.82
        D+2                10.09                  10.17                 9.92                     9.79
        D+3                10.10                  10.22                 9.90                     9.75
        D+5                10.13                  10.27                 9.89                     9.73
        D+7                10.15                  10.30                 9.86                     9.69
       D+10                10.19                  10.38                 9.83                     9.66
       D+15                10.23                  10.51                 9.82                     9.59
       D+20                10.24                  10.54                 9.77                     9.55
       D+30                10.30                  10.68                 9.70                     9.42
       D+45                10.41                  10.81                 9.64                     9.29
       D+60                10.43                  10.82                 9.59                     9.18
Dia em que a cota fez o maior preço: até D+10: 4º pregão | até D+20: 9º pregão | até D+30: 15º pregão | até D+60: 27º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 20% até D+5, 31% até D+10, 43% até D+20, 51% até D+30 | R$ 10.50: 11% até D+5, 20% até D+10, 30% até D+20, 37% até D+30 | R$ 11.00: 1% até D+5, 4% até D+10, 9% até D+20, 11% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 9.99 x 9.99 | D+5: 10.00 x 9.99 | D+10: 10.02 x 9.98 | D+20: 10.02 x 9.98 | D+30: 10.01 x 9.95

========================================================================================================================
O FUNDO INFORMOU O TAMANHO DO EFEITO NO RENDIMENTO (texto do próprio fato relevante)
========================================================================================================================
264 fatos relevantes em que o fundo declara efeito no rendimento | aumento: 156 (com percentual: 35, mediana 12.7%) | redução: 108 (com percentual: 26, mediana 11.5%)

--- O FUNDO DECLAROU AUMENTO de rendimento (qualquer tamanho): 147 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.94       10.01          10.07
        D+1           9.94       10.02          10.08
        D+2           9.95       10.02          10.08
        D+3           9.96       10.03          10.10
        D+5           9.95       10.02          10.10
        D+7           9.96       10.04          10.09
       D+10           9.94       10.01          10.08
       D+15           9.96       10.01          10.10
       D+20           9.96       10.03          10.10
       D+30           9.92       10.02          10.09
       D+45           9.89        9.99          10.09
       D+60           9.85        9.91           9.97
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.01     10.09                    0.54            0.06            0.03
        D+1        9.94   10.02     10.12                    0.58            0.07            0.05
        D+2        9.92   10.02     10.14                    0.56            0.12            0.07
        D+3        9.91   10.03     10.17                    0.57            0.11            0.05
        D+5        9.92   10.02     10.20                    0.56            0.14            0.07
        D+7        9.91   10.04     10.21                    0.56            0.16            0.07
       D+10        9.89   10.01     10.24                    0.53            0.18            0.10
       D+15        9.81   10.01     10.30                    0.53            0.25            0.12
       D+20        9.80   10.03     10.38                    0.56            0.29            0.20
       D+30        9.69   10.02     10.36                    0.51            0.27            0.18
       D+45        9.63    9.99     10.39                    0.50            0.31            0.21
       D+60        9.41    9.91     10.48                    0.46            0.30            0.24
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.15                 9.94                     9.86
        D+1                10.10                  10.19                 9.91                     9.81
        D+2                10.13                  10.24                 9.90                     9.78
        D+3                10.15                  10.29                 9.89                     9.76
        D+5                10.18                  10.34                 9.87                     9.72
        D+7                10.20                  10.39                 9.85                     9.70
       D+10                10.24                  10.44                 9.82                     9.68
       D+15                10.30                  10.54                 9.75                     9.59
       D+20                10.35                  10.65                 9.73                     9.55
       D+30                10.41                  10.79                 9.69                     9.38
       D+45                10.49                  10.88                 9.58                     9.29
       D+60                10.59                  10.97                 9.49                     9.00
Dia em que a cota fez o maior preço: até D+10: 4º pregão | até D+20: 10º pregão | até D+30: 13º pregão | até D+60: 23º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 29% até D+5, 43% até D+10, 54% até D+20, 61% até D+30 | R$ 10.50: 13% até D+5, 20% até D+10, 35% até D+20, 39% até D+30 | R$ 11.00: 5% até D+5, 7% até D+10, 12% até D+20, 14% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.02 x 10.00 | D+5: 10.02 x 10.00 | D+10: 10.01 x 10.00 | D+20: 10.03 x 9.96 | D+30: 10.02 x 9.95

--- aumento declarado de até 5%: poucos casos (3) ---

--- aumento declarado de 5% a 15%: 15 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.95       10.07          10.07
        D+1           9.95       10.01          10.08
        D+2           9.97       10.06          10.08
        D+3           9.99       10.02          10.09
        D+5          10.00       10.07          10.10
        D+7          10.02       10.11          10.13
       D+10          10.00       10.05          10.11
       D+15          10.05       10.16          10.22
       D+20          10.07       10.22          10.23
       D+30          10.36       10.60          10.68
       D+45          10.59       10.60          10.66
       D+60          10.48       10.54          10.60
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.99   10.07     10.11                    0.53            0.00            0.00
        D+1        9.96   10.01     10.10                    0.53            0.00            0.00
        D+2        9.97   10.06     10.13                    0.60            0.07            0.00
        D+3        9.96   10.02     10.15                    0.53            0.07            0.00
        D+5        9.97   10.07     10.14                    0.60            0.13            0.00
        D+7        9.99   10.11     10.19                    0.67            0.13            0.07
       D+10       10.00   10.05     10.22                    0.60            0.13            0.07
       D+15        9.95   10.16     10.31                    0.67            0.27            0.20
       D+20       10.08   10.22     10.55                    0.80            0.47            0.40
       D+30       10.23   10.60     10.76                    0.87            0.67            0.53
       D+45       10.24   10.60     10.87                    0.87            0.60            0.53
       D+60       10.06   10.54     11.16                    0.73            0.67            0.60
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.13                 9.95                     9.91
        D+1                10.08                  10.15                 9.94                     9.82
        D+2                10.08                  10.18                 9.94                     9.81
        D+3                10.09                  10.29                 9.94                     9.81
        D+5                10.10                  10.30                 9.94                     9.80
        D+7                10.20                  10.40                 9.89                     9.73
       D+10                10.20                  10.41                 9.89                     9.71
       D+15                10.35                  10.55                 9.77                     9.40
       D+20                10.42                  10.74                 9.77                     9.34
       D+30                10.74                  10.91                 9.77                     9.34
       D+45                10.88                  11.11                 9.75                     9.34
       D+60                10.94                  11.34                 9.75                     9.13
Dia em que a cota fez o maior preço: até D+10: 6º pregão | até D+20: 13º pregão | até D+30: 26º pregão | até D+60: 49º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 27% até D+5, 40% até D+10, 67% até D+20, 87% até D+30 | R$ 10.50: 0% até D+5, 13% até D+10, 47% até D+20, 67% até D+30 | R$ 11.00: 0% até D+5, 0% até D+10, 7% até D+20, 13% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.01 x 10.00 | D+5: 10.07 x 10.01 | D+10: 10.05 x 10.02 | D+20: 10.22 x 10.08 | D+30: 10.60 x 10.08

--- aumento declarado de 15% ou mais: poucos casos (13) ---

--- aumento declarado sem dizer o percentual: 116 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.93       10.01          10.07
        D+1           9.94       10.02          10.09
        D+2           9.95       10.02          10.07
        D+3           9.95       10.03          10.08
        D+5           9.94       10.02          10.09
        D+7           9.95       10.01          10.08
       D+10           9.94       10.00          10.07
       D+15           9.95       10.01          10.07
       D+20           9.95       10.01          10.09
       D+30           9.87        9.94          10.06
       D+45           9.82        9.89          10.01
       D+60           9.78        9.88           9.92
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.95   10.01     10.09                    0.54            0.07            0.03
        D+1        9.94   10.02     10.12                    0.59            0.09            0.06
        D+2        9.93   10.02     10.14                    0.54            0.13            0.09
        D+3        9.91   10.03     10.17                    0.57            0.12            0.07
        D+5        9.90   10.02     10.16                    0.57            0.14            0.09
        D+7        9.89   10.01     10.20                    0.53            0.17            0.09
       D+10        9.86   10.00     10.23                    0.51            0.17            0.11
       D+15        9.79   10.01     10.29                    0.51            0.24            0.13
       D+20        9.76   10.01     10.30                    0.53            0.25            0.17
       D+30        9.62    9.94     10.23                    0.47            0.23            0.14
       D+45        9.58    9.89     10.32                    0.44            0.28            0.18
       D+60        9.36    9.88     10.29                    0.41            0.25            0.21
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.15                 9.93                     9.84
        D+1                10.11                  10.19                 9.91                     9.82
        D+2                10.13                  10.22                 9.89                     9.77
        D+3                10.15                  10.25                 9.87                     9.76
        D+5                10.17                  10.32                 9.86                     9.72
        D+7                10.20                  10.39                 9.82                     9.69
       D+10                10.24                  10.46                 9.80                     9.66
       D+15                10.30                  10.55                 9.74                     9.58
       D+20                10.34                  10.63                 9.72                     9.55
       D+30                10.38                  10.73                 9.68                     9.39
       D+45                10.47                  10.86                 9.57                     9.19
       D+60                10.54                  10.96                 9.45                     8.97
Dia em que a cota fez o maior preço: até D+10: 4º pregão | até D+20: 9º pregão | até D+30: 12º pregão | até D+60: 20º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 27% até D+5, 42% até D+10, 53% até D+20, 57% até D+30 | R$ 10.50: 15% até D+5, 22% até D+10, 35% até D+20, 38% até D+30 | R$ 11.00: 7% até D+5, 9% até D+10, 14% até D+20, 16% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.02 x 10.00 | D+5: 10.02 x 10.00 | D+10: 10.00 x 10.00 | D+20: 10.01 x 9.95 | D+30: 9.94 x 9.91

--- O FUNDO DECLAROU REDUÇÃO de rendimento (qualquer tamanho): 101 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.86        9.97          10.07
        D+1           9.85        9.95          10.02
        D+2           9.89        9.95          10.00
        D+3           9.86        9.93          10.00
        D+5           9.88        9.95          10.02
        D+7           9.86        9.93          10.00
       D+10           9.86        9.94          10.00
       D+15           9.86        9.96          10.01
       D+20           9.86        9.96          10.01
       D+30           9.82        9.90           9.96
       D+45           9.84        9.91           9.96
       D+60           9.93        9.97          10.07
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.84    9.97     10.04                    0.36            0.02            0.00
        D+1        9.81    9.95     10.06                    0.37            0.03            0.00
        D+2        9.77    9.95     10.06                    0.37            0.06            0.02
        D+3        9.75    9.93     10.06                    0.38            0.07            0.03
        D+5        9.75    9.95     10.10                    0.41            0.12            0.06
        D+7        9.69    9.93     10.11                    0.36            0.13            0.07
       D+10        9.66    9.94     10.19                    0.43            0.17            0.11
       D+15        9.61    9.96     10.16                    0.44            0.18            0.13
       D+20        9.58    9.96     10.12                    0.41            0.15            0.15
       D+30        9.52    9.90     10.25                    0.42            0.24            0.18
       D+45        9.37    9.91     10.47                    0.43            0.28            0.23
       D+60        9.28    9.97     10.69                    0.49            0.39            0.31
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.07                  10.15                 9.86                     9.73
        D+1                10.09                  10.21                 9.83                     9.64
        D+2                10.10                  10.22                 9.80                     9.60
        D+3                10.13                  10.26                 9.78                     9.57
        D+5                10.15                  10.36                 9.76                     9.52
        D+7                10.16                  10.41                 9.71                     9.46
       D+10                10.21                  10.43                 9.67                     9.40
       D+15                10.21                  10.46                 9.63                     9.32
       D+20                10.24                  10.49                 9.61                     9.25
       D+30                10.30                  10.68                 9.52                     9.08
       D+45                10.45                  11.06                 9.39                     8.79
       D+60                10.54                  11.36                 9.36                     8.58
Dia em que a cota fez o maior preço: até D+10: 1º pregão | até D+20: 4º pregão | até D+30: 10º pregão | até D+60: 25º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 30% até D+5, 38% até D+10, 41% até D+20, 50% até D+30 | R$ 10.50: 14% até D+5, 20% até D+10, 25% até D+20, 32% até D+30 | R$ 11.00: 3% até D+5, 5% até D+10, 11% até D+20, 17% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 9.95 x 9.99 | D+5: 9.95 x 9.99 | D+10: 9.94 x 9.99 | D+20: 9.96 x 10.00 | D+30: 9.90 x 9.98

--- redução declarada de 10% ou mais: poucos casos (14) ---

--- COMPARAÇÃO: notícia ruim (saída de inquilino, redução de rendimento, venda com perda): 398 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.92        9.99          10.05
        D+1           9.92       10.00          10.04
        D+2           9.91        9.99          10.04
        D+3           9.90        9.97          10.04
        D+5           9.89        9.96          10.02
        D+7           9.90        9.96          10.01
       D+10           9.88        9.94          10.01
       D+15           9.87        9.95          10.01
       D+20           9.86        9.94           9.99
       D+30           9.87        9.95          10.00
       D+45           9.87        9.94           9.99
       D+60           9.79        9.85           9.91
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.92    9.99     10.04                    0.41            0.03            0.01
        D+1        9.90   10.00     10.06                    0.46            0.04            0.02
        D+2        9.86    9.99     10.07                    0.45            0.05            0.03
        D+3        9.85    9.97     10.06                    0.42            0.07            0.02
        D+5        9.82    9.96     10.08                    0.40            0.08            0.03
        D+7        9.79    9.96     10.09                    0.40            0.10            0.04
       D+10        9.78    9.94     10.08                    0.39            0.12            0.07
       D+15        9.76    9.95     10.13                    0.41            0.15            0.09
       D+20        9.71    9.94     10.13                    0.40            0.15            0.09
       D+30        9.67    9.95     10.20                    0.42            0.20            0.12
       D+45        9.52    9.94     10.25                    0.41            0.22            0.16
       D+60        9.30    9.85     10.29                    0.39            0.25            0.19
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.05                  10.12                 9.92                     9.83
        D+1                10.07                  10.17                 9.88                     9.77
        D+2                10.08                  10.20                 9.86                     9.75
        D+3                10.10                  10.22                 9.84                     9.71
        D+5                10.14                  10.29                 9.81                     9.65
        D+7                10.16                  10.32                 9.79                     9.61
       D+10                10.18                  10.36                 9.77                     9.56
       D+15                10.21                  10.41                 9.73                     9.48
       D+20                10.24                  10.44                 9.68                     9.42
       D+30                10.27                  10.54                 9.63                     9.31
       D+45                10.33                  10.68                 9.53                     9.16
       D+60                10.40                  10.79                 9.43                     8.95
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 5º pregão | até D+30: 9º pregão | até D+60: 22º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 24% até D+5, 33% até D+10, 40% até D+20, 46% até D+30 | R$ 10.50: 9% até D+5, 14% até D+10, 20% até D+20, 28% até D+30 | R$ 11.00: 3% até D+5, 5% até D+10, 9% até D+20, 12% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 10.00 x 9.99 | D+5: 9.96 x 9.98 | D+10: 9.94 x 9.97 | D+20: 9.94 x 9.95 | D+30: 9.95 x 9.92

--- COMPARAÇÃO: fatos relevantes sobre outros assuntos: 1214 casos | cota comprada a R$ 10,00 ---
Tabela 1. O dia típico:
        dia  mínima do dia  fechamento  máxima do dia
D0 (compra)           9.93        9.99          10.05
        D+1           9.93        9.99          10.05
        D+2           9.93        9.99          10.04
        D+3           9.92        9.98          10.04
        D+5           9.92        9.98          10.04
        D+7           9.91        9.97          10.03
       D+10           9.91        9.97          10.03
       D+15           9.90        9.96          10.02
       D+20           9.90        9.96          10.02
       D+30           9.88        9.95          10.00
       D+45           9.86        9.91           9.98
       D+60           9.82        9.90           9.95
Tabela 2. Fechamento nos três cenários:
        dia  pessimista  típico  otimista  fechou acima da compra  acima de 10,30  acima de 10,50
D0 (compra)        9.93    9.99     10.04                    0.42            0.02            0.01
        D+1        9.91    9.99     10.06                    0.44            0.04            0.01
        D+2        9.89    9.99     10.07                    0.44            0.06            0.03
        D+3        9.87    9.98     10.08                    0.44            0.07            0.03
        D+5        9.84    9.98     10.11                    0.44            0.11            0.05
        D+7        9.82    9.97     10.14                    0.44            0.14            0.06
       D+10        9.78    9.97     10.16                    0.45            0.15            0.09
       D+15        9.77    9.96     10.19                    0.45            0.18            0.11
       D+20        9.72    9.96     10.21                    0.44            0.19            0.12
       D+30        9.65    9.95     10.26                    0.44            0.23            0.15
       D+45        9.54    9.91     10.34                    0.44            0.26            0.18
       D+60        9.44    9.90     10.37                    0.43            0.28            0.21
Tabela 3. Até onde a cota chegou desde a compra:
  até o dia  maior preço: típico  maior preço: otimista  menor preço: típico  menor preço: pessimista
D0 (compra)                10.05                  10.12                 9.93                     9.86
        D+1                10.07                  10.16                 9.90                     9.81
        D+2                10.09                  10.19                 9.88                     9.77
        D+3                10.11                  10.22                 9.86                     9.73
        D+5                10.13                  10.27                 9.83                     9.68
        D+7                10.15                  10.32                 9.81                     9.64
       D+10                10.17                  10.37                 9.78                     9.58
       D+15                10.20                  10.44                 9.74                     9.52
       D+20                10.23                  10.48                 9.69                     9.46
       D+30                10.29                  10.63                 9.62                     9.32
       D+45                10.36                  10.79                 9.53                     9.17
       D+60                10.42                  10.91                 9.45                     9.00
Dia em que a cota fez o maior preço: até D+10: 3º pregão | até D+20: 7º pregão | até D+30: 10º pregão | até D+60: 20º pregão
Ordem de venda executada (a máxima do dia tocou o preço): R$ 10.30: 22% até D+5, 32% até D+10, 41% até D+20, 48% até D+30 | R$ 10.50: 10% até D+5, 16% até D+10, 24% até D+20, 31% até D+30 | R$ 11.00: 2% até D+5, 5% até D+10, 10% até D+20, 13% até D+30
Comparação com outros fundos comprados na mesma abertura (fechamento típico): D+1: 9.99 x 10.00 | D+5: 9.98 x 9.99 | D+10: 9.97 x 9.99 | D+20: 9.96 x 9.97 | D+30: 9.95 x 9.96
```
