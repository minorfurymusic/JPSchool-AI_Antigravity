# Estudo por trimestre: todos os fundos, alto rendimento e venda de ativos

Feito em 2026-11-11 com `estudos/trimestral.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/trimestral.py`.

## Por que este estudo

298 dos 524 fundos ligados à CVM ficaram sem histórico mensal de rendimento. O informe trimestral da CVM tem o total de rendimentos declarados de todos eles, e também o ganho com venda de imóveis e de títulos. Com isso dá para incluir os fundos que pagam em poucos meses do ano e os que não preenchem o informe mensal direito.

## Quem ficou sem histórico mensal, e por quê

| Situação | Fundos | Ainda negociados | Negociados com liquidez |
|---|---|---|---|
| Rendimento mensal conferido (entra em tudo) | 237 | 169 | 116 |
| Informe mensal não bate com o valor anunciado na B3 | 67 | 62 | 45 |
| Sem valor da B3 para conferir e as contas da CVM não concordam | 220 | 54 | 20 |

Dos 220 do último grupo, 166 não são mais negociados (saíram da bolsa entre 2017 e 2026). Dos 54 ainda negociados: 19 têm menos de 12 meses de informe, 18 não informam rendimento (quase tudo zero), 7 pagam em poucos meses do ano, 9 preenchem as duas contas mas elas não concordam, 1 preenche só uma.

O grupo que importa é o do meio: na primeira medição eram 78 fundos, 51 com liquidez, e 55 rendiam 10% ao ano ou mais (mediana de 14,2%). São na maioria fundos de recebíveis. Depois de aceitar a conta "um mês adiante", 16 deles foram recuperados.

## Método

- Rendimento do trimestre por cota = rendimentos declarados ÷ cotas. O campo vem acumulado no semestre; o 2º e o 4º trimestres saem por diferença. Conferido contra a soma mensal em 4.342 trimestres: 73,5% dentro de 5%, 84,2% dentro de 15%, mediana da razão 1,00.
- Salto trimestral: rendimento do trimestre pelo menos 25% acima da média dos 4 trimestres anteriores (trimestre sem pagamento conta como zero).
- "Com ganho de venda de ativos": ganho com venda de imóveis ou títulos de pelo menos 0,5% do patrimônio no trimestre do salto ou no anterior.
- Retorno medido acima da mediana do mercado de FIIs, comprando no 1º pregão depois do fim do trimestre e, como alternativa, 2 meses depois.

## Resultado

330 saltos trimestrais em 216 fundos, de 12/2017 a 06/2026. 115 são de fundos sem histórico mensal; 152 de fundos que pagavam em poucos trimestres; 84 de fundos que já rendiam 10% ao ano ou mais.

| Grupo | Casos | Acima do mercado em 3 meses (mediana) | Confiança (t) | Casos acima do mercado | Cota 10% mais cara em 6 meses |
|---|---|---|---|---|---|
| Todos | 330 | +0,55% | 1,1 | 55% | 14% |
| Rendia 10% ao ano ou mais | 84 | +0,33% | 0,2 | 54% | 8% |
| Rendia menos de 10% ao ano | 246 | +0,69% | 1,1 | 55% | 16% |
| Com ganho de venda de ativos | 103 | +0,70% | 1,2 | 57% | 15% |
| Com ganho de venda de imóvel | 29 | +1,16% | 0,3 | 57% | 19% |
| 10% ou mais e com ganho de venda | 36 | +0,14% | 0,0 | 53% | 13% |
| Fundos sem histórico mensal | 115 | −0,92% | −1,0 | 44% | 12% |
| Fundos com histórico mensal | 215 | +1,34% | 2,3 | 60% | 15% |
| Pagava em poucos trimestres | 152 | +0,27% | 0,5 | 52% | 13% |

Nenhum grupo tem confiança suficiente (t acima de 3). Comprando 2 meses depois, nada sobra.

### A tese: salto com venda de imóvel, e depois?

40 casos (ganho de venda de imóvel ou venda informada).

- **Rendimento depois do salto**, em relação ao nível anterior: 1,43 no salto; 1,08 um trimestre depois; 1,26; 1,15; 1,21; 1,14; 1,13 no sexto trimestre. Sem venda de imóvel o rendimento fica mais alto por mais tempo: 1,31 a 1,40.
- **Rendimento abaixo do nível anterior**: 26% dos casos dois trimestres depois, 14% quatro trimestres depois, 28% seis trimestres depois.
- **Cota**: mediana de +2,1% em 3 meses, +0,7% em 6 e −1,9% em 12. Subiu 10% ou mais em 18% dos casos em 3 meses; caiu 10% ou mais em 13%.

## Leitura

- No trimestre, a relação quase desaparece. No estudo mensal ela é forte. A diferença é o tempo: quando o trimestre fecha, o salto já tem até três meses e o mercado já reagiu.
- Fundos que rendem mais de 10% ao ano não mostram efeito nenhum. Neles o rendimento alto já é a regra, e uma alta a mais não surpreende.
- Venda de ativos não melhora o resultado de forma confiável. O número é positivo mas com poucos casos e muita dispersão.
- O padrão "sobe 30% e depois cai abaixo do nível antigo" não é o caso típico: acontece em cerca de 1 a cada 4. No caso típico, o rendimento volta para 10% a 20% acima do nível anterior.
- A alta de 10% ou mais na cota acontece em cerca de 1 caso a cada 6, e a queda de 10% ou mais é quase tão frequente.

## Limites

- O app não sabe o motivo do salto no momento do anúncio. A classificação "com venda" usa o informe trimestral, que sai até 45 dias depois do fim do trimestre.
- "Ganho de venda de títulos" inclui giro normal de carteira em fundos de recebíveis, não só eventos extraordinários.
- O campo de receita de venda de imóveis não vem preenchido de modo uniforme (KNRI11 repete o mesmo valor em vários trimestres).
- Sem custos nem imposto de 20% sobre ganho na cota.

## Saída literal

```
Saltos trimestrais (rendimento do trimestre >= 25% acima da média dos 4 anteriores): 330 casos, 216 fundos, 12/2017 a 06/2026
  de fundos SEM rendimento mensal confiável: 115 | pagavam em poucos trimestres (algum zero nos 4 anteriores): 152
  rendiam >= 10% ao ano antes: 84 | com ganho de venda de ativos >= 0.5% do patrimônio: 103 | com venda de imóvel informada: 30

=== COMPRANDO NO 1º PREGÃO DEPOIS DO FIM DO TRIMESTRE ===
                                 grupo  casos  1m acima do mercado %  3m acima do mercado %  3m média %  3m t  3m acerto  3m só cota %  6m acima do mercado %  6m média %  6m t  6m acerto  6m só cota %  12m acima do mercado %  cota +10% em 6m  rend. 2 tri depois ÷ antes  rend. 4 tri depois ÷ antes  rend. 5-6 tri depois ÷ antes
                                 todos    330                   0.08                   0.55        0.48  1.08       0.55          0.49                   1.10        0.90  1.38       0.54          0.11                    1.34             0.14                        1.32                        1.38                          1.34
                  rendia >= 10% ao ano     84                  -0.03                   0.33        0.15  0.19       0.54         -0.25                   0.22       -0.18 -0.14       0.50         -1.04                    0.73             0.08                        1.04                        1.07                          0.96
                   rendia < 10% ao ano    246                   0.11                   0.69        0.59  1.11       0.55          0.62                   1.35        1.24  1.63       0.56          0.88                    1.46             0.16                        1.40                        1.43                          1.43
          com ganho de venda de ativos    103                   0.33                   0.70        0.99  1.18       0.57          0.51                   1.21        1.72  1.30       0.53         -0.36                   -0.17             0.15                        1.31                        1.36                          1.25
          sem ganho de venda de ativos    227                  -0.03                   0.44        0.24  0.46       0.53          0.45                   1.04        0.52  0.71       0.55          0.34                    1.41             0.14                        1.32                        1.38                          1.37
          com ganho de venda de IMÓVEL     29                   0.96                   1.16        0.77  0.30       0.57          1.06                   1.80        1.50  0.36       0.52          1.49                   -2.69             0.19                        1.29                        1.15                          1.07
         com venda de imóvel informada     30                   0.75                   1.21        0.70  0.33       0.62          1.12                   2.23        2.14  0.55       0.54          1.50                    1.30             0.14                        1.21                        1.20                          1.09
           >= 10% E com ganho de venda     36                   0.32                   0.14        0.02  0.02       0.53         -0.68                  -0.78        0.27  0.14       0.48         -1.06                   -1.19             0.13                        1.06                        1.05                          0.98
           >= 10% E sem ganho de venda     48                  -0.22                   0.47        0.24  0.22       0.54         -0.02                   0.85       -0.52 -0.29       0.51         -1.02                    0.97             0.05                        1.03                        1.07                          0.96
            < 10% E com ganho de venda     67                   0.34                   1.41        1.49  1.31       0.60          0.85                   2.33        2.41  1.38       0.55          0.93                    0.11             0.17                        1.50                        1.50                          1.28
            < 10% E sem ganho de venda    179                  -0.02                   0.43        0.23  0.40       0.53          0.61                   1.10        0.78  0.96       0.56          0.55                    1.51             0.16                        1.37                        1.41                          1.45
fundos sem rendimento mensal confiável    115                  -0.38                  -0.92       -0.80 -0.97       0.44         -1.09                   0.00        0.63  0.49       0.50         -0.36                    1.36             0.12                        1.36                        1.41                          1.38
          fundos com rendimento mensal    215                   0.60                   1.34        1.17  2.31       0.60          1.00                   1.31        1.04  1.41       0.57          0.46                    1.29             0.15                        1.31                        1.34                          1.34
           pagava em poucos trimestres    152                  -0.19                   0.27        0.30  0.46       0.52         -0.23                   1.10        0.58  0.59       0.52         -0.45                    1.51             0.13                        1.40                        1.41                          1.43
                                tijolo    149                  -0.03                   0.49        0.57  0.74       0.53          0.77                   1.49        0.13  0.10       0.57          1.09                   -0.53             0.16                        1.31                        1.30                          1.31
                                 papel      8                  -0.73                   3.89        2.64  1.41       0.62          3.90                   5.08        3.37  1.46       0.67          4.36                    0.53             0.17                        1.72                        1.65                          1.60
                              até 2021    151                   0.14                   1.12        1.10  1.76       0.56          0.81                   1.17        1.12  1.24       0.56          0.46                    1.41             0.16                        1.42                        1.52                          1.45
                        2022 em diante    179                   0.07                   0.21       -0.08 -0.12       0.53         -0.10                   0.97        0.70  0.74       0.53         -0.40                    0.75             0.13                        1.26                        1.21                          1.23

=== COMPRANDO 2 MESES DEPOIS (quando o informe da CVM já está publicado) ===
                                 grupo  casos  1m acima do mercado %  3m acima do mercado %  3m média %  3m t  3m acerto  3m só cota %  6m acima do mercado %  6m média %  6m t  6m acerto  6m só cota %  12m acima do mercado %  cota +10% em 6m  rend. 2 tri depois ÷ antes  rend. 4 tri depois ÷ antes  rend. 5-6 tri depois ÷ antes
                                 todos    330                   0.12                   0.77        0.30  0.75       0.53          0.17                   0.57        0.19  0.34       0.54          0.06                    1.29             0.13                        1.32                        1.38                          1.34
                  rendia >= 10% ao ano     84                   0.51                   0.43        0.01  0.02       0.51         -0.28                   0.60        0.27  0.25       0.56         -0.14                   -1.41             0.08                        1.04                        1.07                          0.96
                   rendia < 10% ao ano    246                  -0.18                   0.81        0.39  0.85       0.54          0.36                   0.53        0.17  0.25       0.54          0.09                    1.96             0.14                        1.40                        1.43                          1.43
          com ganho de venda de ativos    103                   0.23                   1.03        0.69  0.97       0.56          0.69                   0.75       -0.19 -0.19       0.53          0.21                   -1.91             0.12                        1.31                        1.36                          1.25
          sem ganho de venda de ativos    227                   0.01                   0.26        0.12  0.24       0.51         -0.04                   0.43        0.37  0.53       0.55         -0.04                    1.67             0.13                        1.32                        1.38                          1.37
          com ganho de venda de IMÓVEL     29                   0.70                  -0.48       -0.15 -0.08       0.46         -0.16                   0.01       -0.84 -0.39       0.52          0.01                   -3.22             0.19                        1.29                        1.15                          1.07
         com venda de imóvel informada     30                   0.38                  -0.32        0.28  0.17       0.45          0.03                  -1.23       -0.52 -0.31       0.43         -0.68                   -0.58             0.14                        1.21                        1.20                          1.09
           >= 10% E com ganho de venda     36                  -0.28                  -0.25       -0.24 -0.24       0.47         -0.32                  -0.81       -0.62 -0.36       0.48         -1.05                   -3.71             0.10                        1.06                        1.05                          0.98
           >= 10% E sem ganho de venda     48                   0.79                   0.79        0.21  0.18       0.55         -0.18                   0.69        0.95  0.74       0.62         -0.01                   -0.03             0.08                        1.03                        1.07                          0.96
            < 10% E com ganho de venda     67                   0.61                   1.28        1.17  1.24       0.61          0.98                   1.56        0.02  0.02       0.55          0.42                    0.88             0.14                        1.50                        1.50                          1.28
            < 10% E sem ganho de venda    179                  -0.47                   0.15        0.09  0.18       0.51         -0.02                   0.40        0.23  0.28       0.53         -0.04                    1.96             0.15                        1.37                        1.41                          1.45
fundos sem rendimento mensal confiável    115                  -0.48                   0.83        0.48  0.70       0.54          0.76                   1.67        0.97  0.93       0.60          1.12                    3.90             0.14                        1.36                        1.41                          1.38
          fundos com rendimento mensal    215                   0.40                   0.65        0.20  0.41       0.53          0.03                   0.32       -0.21 -0.31       0.51         -0.35                    0.57             0.13                        1.31                        1.34                          1.34
           pagava em poucos trimestres    152                  -0.20                   0.28       -0.09 -0.14       0.52         -0.18                  -0.52       -0.80 -0.93       0.49         -1.65                    1.29             0.09                        1.40                        1.41                          1.43
                                tijolo    149                   0.19                   0.38        0.03  0.04       0.53          0.27                   0.19       -0.46 -0.54       0.51         -0.32                   -1.41             0.17                        1.31                        1.30                          1.31
                                 papel      8                  -0.72                   0.62       -0.05 -0.03       0.50          0.05                   3.15       -0.84 -0.23       0.67          1.91                    1.77             0.00                        1.72                        1.65                          1.60
                              até 2021    138                   0.13                   1.18        0.53  0.84       0.58          0.86                   0.88        0.70  0.85       0.55          0.23                    2.61             0.16                        1.40                        1.51                          1.45
                        2022 em diante    192                  -0.15                  -0.09        0.13  0.24       0.49         -0.28                   0.43       -0.22 -0.28       0.54         -0.26                   -0.39             0.11                        1.27                        1.24                          1.25

=== A TESE: salto com venda de imóvel, e depois? ===
40 casos. Rendimento em relação ao nível anterior (mediana), trimestre a trimestre depois do salto:
   no salto: 1.43 | 1 tri depois: 1.08 (n 36) | 2 tri depois: 1.26 (n 34) | 3 tri depois: 1.15 (n 32) | 4 tri depois: 1.21 (n 29) | 5 tri depois: 1.14 (n 25) | 6 tri depois: 1.13 (n 25)
   % dos casos com rendimento ABAIXO do nível anterior: 2 tri: 26% | 4 tri: 14% | 6 tri: 28%
   cota em  1 meses: mediana +1.3% | subiu 10% ou mais em 5% | caiu 10% ou mais em 2% (n 40)
   cota em  3 meses: mediana +2.1% | subiu 10% ou mais em 18% | caiu 10% ou mais em 13% (n 39)
   cota em  6 meses: mediana +0.7% | subiu 10% ou mais em 16% | caiu 10% ou mais em 21% (n 38)
   cota em 12 meses: mediana -1.9% | subiu 10% ou mais em 22% | caiu 10% ou mais em 28% (n 32)
Comparação, saltos SEM venda de imóvel: 1 tri depois: 1.31 | 2 tri depois: 1.32 | 3 tri depois: 1.34 | 4 tri depois: 1.40 | 5 tri depois: 1.39 | 6 tri depois: 1.30
```
