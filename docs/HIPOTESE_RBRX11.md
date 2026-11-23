# Hipóteses do dono sobre o corte do RBRX11 (23/11/2026)

Pergunta do dono: (H1) o mercado já esperava o corte e derrubou a cota antes? (H2) o fundo paga mais do que ganha porque
a receita vem concentrada em certas épocas (ex.: 30% do ano de uma vez)?

Programa: `estudos/hipotese_corte_antecipado.py`. Saída literal da execução:

```
===== A. RBRX11: resultado × distribuído, trimestre a trimestre
trimestre  resultado por cota (R$)  distribuído por cota (R$)  resultado ÷ distribuído  parte do resultado que veio de venda de ativos  cotas (milhões)
  12/2022                    0.411                      0.449                     0.91                                            0.14             18.8
  03/2023                    0.408                      0.360                     1.13                                            0.10             18.8
  06/2023                    0.275                      0.350                     0.78                                            0.20             18.8
  09/2023                    0.352                      0.337                     1.05                                            0.37             18.8
  12/2023                    0.267                      0.305                     0.88                                            0.24             18.8
  03/2024                    0.252                      0.280                     0.90                                            0.45             18.8
  06/2024                    0.358                      0.320                     1.12                                            0.47             29.5
  09/2024                    0.229                      0.280                     0.82                                            0.05             29.5
  12/2024                    0.279                      0.240                     1.16                                           -0.22             29.5
  03/2025                    0.210                      0.240                     0.87                                            0.05             29.5
  06/2025                    0.280                      0.260                     1.08                                            0.13             29.5
  09/2025                    0.257                      0.276                     0.93                                            0.07             29.5
  12/2025                    0.216                      0.270                     0.80                                            0.07            133.4
  03/2026                    0.347                      0.270                     1.28                                            0.54            146.4
  06/2026                    0.223                      0.270                     0.82                                            0.42            146.4
  09/2026                    0.266                      0.270                     0.98                                            0.15            146.4

média de resultado ÷ distribuído por trimestre do ano (2022 em diante):
     mean   min   max  count
tri                         
03   1.04  0.87  1.28      4
06   0.95  0.78  1.12      4
09   0.94  0.82  1.05      4
12   0.94  0.80  1.16      4

===== B. RBRX11: cota antes do aviso de corte (16/11/2026; base = fechamento de 13/11/2026, R$ 6.72)
  126 pregões antes (15/05/2026): R$ 8.42 -> variação até a véspera -20.2%; mercado -5.4%; contra o mercado -14.8%
   60 pregões antes (18/08/2026): R$ 7.08 -> variação até a véspera -5.1%; mercado -1.8%; contra o mercado -3.2%
   20 pregões antes (15/10/2026): R$ 7.73 -> variação até a véspera -13.1%; mercado -7.7%; contra o mercado -5.4%
    5 pregões antes (06/11/2026): R$ 6.52 -> variação até a véspera +3.1%; mercado +0.1%; contra o mercado +3.0%
  depois do aviso: 16/11 R$ 6.47, 17/11 R$ 6.39, 18/11 R$ 6.22, 19/11 R$ 6.08

===== C. Todos os fundos: 184 cortes de rendimento em 78 fundos (2017–2026)
Variação da cota CONTRA O MERCADO antes do aviso (mediana; entre parênteses, 1 em 4 pior / 1 em 4 melhor):
   20 pregões antes: cortes +0.1% (-2.0% / +1.9%), n=184 | qualquer janela dos mesmos fundos -0.8% (-2.5% / +0.9%), n=4461 | cortes que já tinham caído 5%+ contra o mercado: 5% contra 8%
   60 pregões antes: cortes -1.3% (-4.6% / +1.3%), n=184 | qualquer janela dos mesmos fundos -2.2% (-5.1% / +0.7%), n=4461 | cortes que já tinham caído 5%+ contra o mercado: 23% contra 26%
  126 pregões antes: cortes -3.7% (-7.6% / -0.0%), n=179 | qualquer janela dos mesmos fundos -4.4% (-8.8% / -0.1%), n=4461 | cortes que já tinham caído 5%+ contra o mercado: 41% contra 46%
Depois do aviso (mesmo estudo): mediana contra o mercado em 20 pregões -1.2%; em 126 pregões -7.0%
```

## Leitura

- H1, regra geral (184 cortes em 78 fundos, 2017–2026): NÃO se confirma. Antes do aviso, a cota dos fundos que cortaram
  andou igual à de qualquer período dos mesmos fundos (60 pregões antes: −1,3% contra −2,2% contra o mercado). A queda
  vem DEPOIS do aviso (−7,0% contra o mercado em 126 pregões, mediana).
- H1, RBRX11: caiu 14,8% contra o mercado nos 6 meses antes do aviso, mas subiu 3% na semana anterior e caiu 9,5% nos
  4 pregões seguintes (R$ 6,72 → R$ 6,08). Parte da queda anterior pode ter outros motivos (incorporação, cotas de
  29,5 para 146 milhões; relatório de setembro mostrando a reserva caindo) — não testado.
- H2, RBRX11: NÃO há trimestre do ano que pague sistematicamente o resto (média de resultado ÷ distribuído 0,94 a 1,04
  por trimestre do ano). Em 16 trimestres, 10 ficaram abaixo de 1,00; somando tudo, ganhou R$ 4,63 e distribuiu
  R$ 4,78 por cota (97%). O que vem "concentrado" é ganho com VENDA de ativos (até 54% do resultado num trimestre),
  que não é receita que se repete.
- Limites: cotas estimadas por patrimônio ÷ valor patrimonial por cota; trimestres com incorporação (12/2025, 03/2026)
  distorcem o "por cota"; resultado do informe trimestral da CVM é contábil (competência), não caixa.
