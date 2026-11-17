# Simulação do Kairi nos anos anteriores, versão 3 (17/11/2026)

Programa: `estudos/kairi_carteira_anos.py` (mesmo motor da versão 3, com datas de início e fim); planilha: `planilhas/kairi_carteira_anos.xlsx`. Nada foi baixado: só `planilhas/`.

**Regras (as da versão 3).**
1. Quatro sub-carteiras de R$ 10.000, ordem de R$ 1.000, um fundo por vez em cada uma; gatilho: a cota fecha 15% (Agressivas) ou 20% (Conservadoras) abaixo da média de 200 pregões, rendimento mantido.
2. Faixa pela mediana do volume diário dos 60 pregões até o sinal: Agressiva 1 R$ 100–200 mil; Agressiva 2 R$ 200–500 mil; Conservadora 1 R$ 500 mil–1 milhão; Conservadora 2 acima de R$ 1 milhão (valores nominais).
3. Compra na abertura do dia seguinte ao sinal; venda no fechamento do primeiro dia acima da média de 200 pregões, ou em 252 pregões; maior mediana primeiro.
4. Regra 1 (não comprar fundo que vai sair da bolsa) pelos fatos relevantes; regras b (rendimento zero) e c (saída antecipada) e parte da regra 1 pelos documentos do FNET **só de 01/05/2025 em diante e só de 43 fundos**; antes disso, só fatos relevantes.
5. Caixa parado em 105% do CDI (IR/IOF por lote); imposto do FII (20%, DARF no mês seguinte); taxa de 0,03%. Ano a ano: cada ano começa com R$ 10 mil por sub-carteira no 1º pregão e termina no último; posições abertas valem o último preço. Contínua: 02/01/2018 a 09/11/2026 sem zerar.

### Tabela A. Ano a ano (retorno líquido de cada ano)

| Ano | Agressiva 1 | Agressiva 2 | Conservadora 1 | Conservadora 2 | Total (R$ 40 mil) | 105% do CDI | Mercado | Total contra o CDI (pontos) | Operações fechadas / abertas (total) | Dinheiro parado, % médio (total) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 10,0% | 7,4% | 5,7% | 5,4% | 7,1% | 5,4% | 3,7% | 1,8 | 6 / 2 | 93,0% |
| 2019 | 5,1% | 5,1% | 7,1% | 5,1% | 5,6% | 5,1% | 24,9% | 0,5 | 1 / 0 | 99,0% |
| 2020 | 14,5% | 13,0% | 23,5% | 31,4% | 20,6% | 2,4% | -10,0% | 18,2 | 37 / 9 | 58,5% |
| 2021 | 5,2% | 9,8% | 6,4% | 12,2% | 8,4% | 3,7% | -0,2% | 4,7 | 4 / 30 | 81,8% |
| 2022 | 10,9% | 12,9% | 10,4% | 9,9% | 11,0% | 10,4% | 5,4% | 0,7 | 5 / 3 | 94,4% |
| 2023 | 10,9% | 12,3% | 10,9% | 9,4% | 10,9% | 10,9% | 17,7% | 0,0 | 6 / 5 | 93,1% |
| 2024 | 7,5% | 6,7% | 13,7% | 16,1% | 11,0% | 9,4% | -5,2% | 1,6 | 1 / 41 | 92,0% |
| 2025 | 16,0% | 23,3% | 17,2% | 19,9% | 19,1% | 12,4% | 15,6% | 6,7 | 29 / 1 | 79,1% |
| 2026 (versão 3, até 09/11) | 11,1% | 9,7% | 10,0% | 3,8% | 8,7% | 10,0% | -3,0% | -1,4 | 2 / 14 | 93,8% |

**Legenda.** Cada linha é uma rodada independente (R$ 10 mil por sub-carteira, R$ 40 mil no total). *Retorno líquido* = (patrimônio no último pregão − imposto do FII a vencer − imposto se vendesse tudo) ÷ capital − 1, em %. *CDI* = 105% do CDI líquido de IR/IOF no mesmo período. *Mercado* = índice de mercado.csv no período. *Contra o CDI* = retorno do total − retorno do CDI, em pontos percentuais. *Operações* = compras fechadas / abertas no fim do ano. *Parado* = caixa ÷ patrimônio, média diária.

**Leitura prática.** O total ganhou do CDI em 7 dos 9 anos, empatou em 2023 e perdeu em 2026 (2026 é parcial, vai até 09/11). A diferença média é de 3,6 pontos por ano, mas só 1,8 sem 2020 (18,2 pontos naquele ano). O dinheiro ficou parado em média 87,2% do tempo, então a maior parte do resultado de cada ano é o CDI; o que passa do CDI vem sobretudo de 2020 e 2025 (as duas maiores diferenças).

### Tabela B. Resumo ano a ano por sub-carteira

| Sub-carteira | Anos que ganharam do CDI | Retorno médio por ano | Pior ano | Melhor ano | Maior queda no caminho (dentro de um ano) | Operações fechadas (9 anos) | Fechadas com lucro | Dinheiro parado, % médio |
|---|---|---|---|---|---|---|---|---|
| Agressiva 1 (15%; R$ 100–200 mil) | 6 de 9 | 10,1% | 5,1% (2019) | 16,0% (2025) | -7,0% (2021) | 26 | 25 de 26 (96%) | 84,7% |
| Agressiva 2 (15%; R$ 200–500 mil) | 6 de 9 | 11,1% | 5,1% (2019) | 23,3% (2025) | -10,7% (2020) | 34 | 32 de 34 (94%) | 82,9% |
| Conservadora 1 (20%; R$ 500 mil–1 mi) | 6 de 9 | 11,7% | 5,7% (2018) | 23,5% (2020) | -5,2% (2024) | 14 | 14 de 14 (100%) | 91,3% |
| Conservadora 2 (20%; > R$ 1 mi) | 4 de 9 | 12,6% | 3,8% (2026) | 31,4% (2020) | -5,8% (2020) | 17 | 17 de 17 (100%) | 89,9% |
| Total (R$ 40 mil) | 7 de 9 | 11,4% | 5,6% (2019) | 20,6% (2020) | -5,4% (2024) | 91 | 88 de 91 (97%) | 87,2% |
| 105% do CDI (R$ 40 mil) | — | 7,7% | 2,4% (2020) | 12,4% (2025) | 0,0% | — | — | 100,0% |
| Mercado (R$ 40 mil) | — | 5,4% | -10,0% (2020) | 24,9% (2019) | -29,1% (2020) | — | — | — |

**Legenda.** *Ganhou do CDI* = retorno líquido do ano pelo menos 0,05 ponto acima do CDI no mesmo ano (x de 9, contando 2026 até 09/11); diferença menor é empate e não conta (sem operação no ano, o resultado é igual ao do CDI). *Retorno médio* = média simples dos 9 retornos anuais (não composta). *Maior queda* = pior queda do patrimônio, de um pico ao ponto mais baixo dentro de um ano. *Fechadas com lucro* = só as que fecharam dentro do ano. *Dinheiro parado* = média dos 9 anos.

**Leitura prática.** Nenhuma sub-carteira ganhou do CDI em todos os anos. A Conservadora 2 ganhou em só 4 de 9, mas tem o maior retorno médio (12,6%) por causa de 2020 (31,4%); sem esse ano a média cai para 10,2%. A média do CDI foi 7,7% e a do total 11,4%.

### Tabela C. Contínua 2018–2026 (02/01/2018 a 09/11/2026)

| Indicador | Agressiva 1 (15%; R$ 100–200 mil) | Agressiva 2 (15%; R$ 200–500 mil) | Conservadora 1 (20%; R$ 500 mil–1 mi) | Conservadora 2 (20%; > R$ 1 mi) | Total (R$ 40 mil) | 105% do CDI (R$ 40 mil) | Mercado (R$ 40 mil) |
|---|---|---|---|---|---|---|---|
| Patrimônio inicial (R$) | R$ 10.000,00 | R$ 10.000,00 | R$ 10.000,00 | R$ 10.000,00 | R$ 40.000,00 | R$ 40.000,00 | R$ 40.000,00 |
| Patrimônio final, cotas a preço de 09/11/2026 (R$) | R$ 23.134,81 | R$ 25.015,16 | R$ 26.350,97 | R$ 28.443,14 | R$ 102.944,08 | R$ 83.114,99 | R$ 59.579,47 |
| Retorno líquido (após imposto a vencer) | 131,2% | 150,1% | 163,5% | 184,4% | 157,3% | 107,8% | 48,9% |
| Contra o CDI (pontos percentuais do retorno líquido) | 23,4 | 42,3 | 55,7 | 76,6 | 49,5 | 0,0 | -58,8 |
| Maior queda do patrimônio no caminho | -6,0% | -9,6% | -4,0% | -5,4% | -3,9% | 0,0% | -29,1% |
|   ... do pico em | 03/07/2020 | 13/03/2020 | 03/07/2020 | 20/03/2020 | 20/03/2020 | — | 03/01/2020 |
|   ... até o ponto mais baixo em | 23/11/2021 | 23/03/2020 | 07/08/2020 | 23/03/2020 | 23/03/2020 | — | 23/03/2020 |
| Operações abertas / fechadas | 4 / 41 | 7 / 61 | 0 / 30 | 3 / 37 | 14 / 169 | — | — |
| Fechadas com lucro | 35 de 41 (85%) | 53 de 61 (87%) | 29 de 30 (97%) | 35 de 37 (95%) | 152 de 169 (90%) | — | — |
| Rendimentos recebidos no caixa (R$) | R$ 1.721,09 | R$ 2.408,01 | R$ 1.478,33 | R$ 1.720,91 | R$ 7.328,35 | — | — |
| Imposto do FII pago + vencido e não pago (R$) | R$ 377,99 | R$ 691,18 | R$ 843,12 | R$ 1.278,67 | R$ 3.190,96 | — | — |
| Dinheiro parado no CDI: % médio do patrimônio | 83,9% | 81,8% | 89,7% | 88,7% | 86,2% | 100,0% | — |
| Dinheiro parado no CDI: dias-equivalentes parado (de 3233 dias corridos) | 2.713,8 | 2.645,1 | 2.898,6 | 2.869,0 | 2.786,3 | 3.233,0 | — |
| Dinheiro parado no CDI: quanto rendeu, líquido de IR/IOF (R$) | R$ 9.842,68 | R$ 9.856,02 | R$ 11.616,23 | R$ 12.232,48 | R$ 43.547,42 | R$ 43.114,99 | — |
| De onde veio: operações fechadas, valorização + rendimentos (R$) | R$ 3.637,05 | R$ 5.911,11 | R$ 5.596,42 | R$ 8.073,40 | R$ 23.217,98 | — | — |
| De onde veio: operações abertas a preço de 09/11, valorização + rendimentos pagos (R$) | R$ 58,30 | R$ -22,60 | R$ 0,00 | R$ -560,02 | R$ -524,32 | — | — |
| De onde veio: rendimento do dinheiro parado (R$) | R$ 9.842,68 | R$ 9.856,02 | R$ 11.616,23 | R$ 12.232,48 | R$ 43.547,42 | R$ 43.114,99 | — |
| De onde veio: − imposto do FII (R$) | R$ -377,99 | R$ -691,18 | R$ -843,12 | R$ -1.278,67 | R$ -3.190,96 | — | — |
| De onde veio: − taxas de compra e venda (R$) | R$ -25,23 | R$ -38,19 | R$ -18,55 | R$ -24,06 | R$ -106,04 | — | — |
| = Ganho total (patrimônio final − capital) (R$) | R$ 13.134,81 | R$ 15.015,16 | R$ 16.350,97 | R$ 18.443,14 | R$ 62.944,08 | R$ 43.114,99 | R$ 19.579,47 |

**Legenda.** Mesmas linhas da Tabela 1 da versão 3, para 3233 dias corridos. *Contra o CDI* em pontos percentuais do retorno líquido. *De onde veio* (R$) = fechadas (valorização + rendimentos) + abertas a preço de 09/11 + dinheiro parado − imposto do FII pago ou vencido − taxas = patrimônio final − capital (conferido por assert, por sub-carteira e no total).

**Leitura prática.** Sem zerar a cada ano, os R$ 40 mil viraram R$ 102.944,08 (retorno líquido 157,3%) contra R$ 83.114,99 do CDI (107,8%) e R$ 59.579,47 do mercado (48,9%). O dinheiro parado rendeu R$ 43.547,42, 69% do ganho de R$ 62.944,08; as operações (já com imposto e taxas) somaram R$ 19.396,66. Como a ordem é fixa em R$ 1.000, o caixa cresce e quase tudo fica no CDI. Melhor sub-carteira: Conservadora 2 (184,4%); pior: Agressiva 1 (131,2%).

### Tabela D. Operações fechadas, por sub-carteira

| Rodada | Sub-carteira | Fechadas | Com lucro | Resultado médio (% da entrada) | Pior (fundo, entrada) | Melhor (fundo, entrada) | Dias médios | Maior queda média durante a operação | Maior alta média durante a operação |
|---|---|---|---|---|---|---|---|---|---|
| Ano a ano (9 anos somados) | Agressiva 1 | 26 | 25 (96%) | 13,9% | -1,5% (BBRC11, entrada 25/03/2021) | 29,8% (OUCY11, entrada 19/03/2020) | 131 | -7,0% | 12,0% |
| Ano a ano (9 anos somados) | Agressiva 2 | 34 | 32 (94%) | 16,1% | -5,7% (HTMX11, entrada 13/03/2020) | 36,9% (CEOC11, entrada 19/03/2020) | 94 | -4,9% | 14,8% |
| Ano a ano (9 anos somados) | Conservadora 1 | 14 | 14 (100%) | 25,6% | 12,8% (CCME11, entrada 16/01/2025) | 46,4% (OUJP11, entrada 19/03/2020) | 134 | -6,2% | 23,2% |
| Ano a ano (9 anos somados) | Conservadora 2 | 17 | 17 (100%) | 28,8% | 13,4% (BBIG11, entrada 26/02/2025) | 47,0% (GGRC11, entrada 19/03/2020) | 130 | -2,3% | 27,4% |
| Ano a ano (9 anos somados) | Total | 91 | 88 (97%) | 19,3% | -5,7% (HTMX11, entrada 13/03/2020) | 47,0% (GGRC11, entrada 19/03/2020) | 117 | -5,2% | 17,6% |
| Contínua | Agressiva 1 | 41 | 35 (85%) | 9,2% | -17,7% (OULG11, entrada 19/10/2021) | 29,8% (OUCY11, entrada 19/03/2020) | 183 | -9,9% | 9,9% |
| Contínua | Agressiva 2 | 61 | 53 (87%) | 10,0% | -70,1% (TORD11, entrada 15/12/2022) | 36,9% (CEOC11, entrada 19/03/2020) | 158 | -9,7% | 11,7% |
| Contínua | Conservadora 1 | 30 | 29 (97%) | 19,4% | -4,1% (TRBL11, entrada 28/10/2024) | 46,4% (OUJP11, entrada 19/03/2020) | 169 | -7,8% | 19,0% |
| Contínua | Conservadora 2 | 37 | 35 (95%) | 23,0% | -18,5% (DEVA11, entrada 18/05/2023) | 47,2% (RBRR11, entrada 19/03/2020) | 158 | -5,1% | 22,8% |
| Contínua | Total | 169 | 152 (90%) | 14,3% | -70,1% (TORD11, entrada 15/12/2022) | 47,2% (RBRR11, entrada 19/03/2020) | 166 | -8,4% | 15,0% |

**Legenda.** *Resultado* = venda − compra + rendimentos recebidos − taxas, em % do valor de entrada. *Maior queda/alta durante a operação* = menor e maior fechamento depois da entrada, em % do preço de entrada (0% se nunca passou), média das operações. *Dias* = corridos, da entrada à saída.

**Leitura prática.** Nos 9 anos isolados foram 91 operações fechadas (97% com lucro), mas 105 posições terminaram abertas no corte do ano e não entram nesse percentual (veja a aba 'Posições abertas'). Na contínua são 169 fechadas, com a pior em TORD11 (-70,1%, prazo, 369 dias); as melhores entraram em 19/03/2020.

### Tabela E. Lacunas

| Dado | Situação | Efeito |
|---|---|---|
| Documentos do FNET antes de 01/05/2025 | a coleta só tem 01/05/2025 a 13/11/2026 e só 43 fundos (os que deram sinal em 2026); em 2018–2024 não há nenhum documento | antes de 05/2025 a regra 1 usa só os fatos relevantes e as regras b (rendimento zero) e c (saída antecipada) não existem; 4 sinais barrados por fato relevante e 4 por FNET na contínua; compras que o FNET teria barrado ou vendido antes aparecem como operações normais |
| Faixas de volume em reais nominais | R$ 100 mil, 200 mil, 500 mil e 1 milhão valem igual em todos os anos; o mercado negociava menos em 2018 | fundos do universo com mediana na faixa Conservadora 2 (> R$ 1 mi) em algum dia do ano: 2018: 12, 2019: 35, 2020: 61, 2021: 67, 2022: 59, 2023: 57, 2024: 73, 2025: 64, 2026: 61; compras do total por ano: 2018: 8, 2019: 1, 2020: 46, 2021: 34, 2022: 8, 2023: 11, 2024: 42, 2025: 30, 2026: 16. A mesma regra pega mercados de tamanhos diferentes |
| Fim do ano | cada ano termina no último pregão do ano (2026 vai só até 09/11); posições abertas valem o último preço e o prazo de 252 pregões nunca é atingido dentro de um ano | 105 posições abertas nos 9 anos (valorização não realizada, na aba 'Posições abertas'); só entram na conta como preço de mercado, não como venda |
| Imposto e rendimentos no corte do ano | imposto do FII do mês de dezembro vence em janeiro (fora da janela); R$ 608,27 de rendimentos declarados e pagos depois do fim de cada ano; R$ 9,12 sem data de pagamento | o imposto a vencer entra no retorno líquido, não no patrimônio final; rendimentos a receber não entram no resultado do ano em que foram declarados |
| Fundos que saíram da bolsa e dado suspeito | 2 compra(s) na contínua e 2 nos anos isolados com preços que acabam antes do prazo (valor real de saída desconhecido); 2 saída(s) por dado suspeito na contínua | o cálculo segue pelo último preço disponível (pode estar errado para mais ou para menos) |
| Leitura dos documentos e universo | documentos lidos por expressões no texto (sem leitura humana de todos; 12 sem texto legível); universo e filtros da versão 3 (patrimônio, volume mínimo, valor patrimonial) iguais em todos os anos | pode haver aviso que as expressões não pegam; fundos que passam nos filtros em algum dia do ano: 2018: 89, 2019: 116, 2020: 165, 2021: 198, 2022: 218, 2023: 225, 2024: 251, 2025: 235, 2026: 220 |

**Confirmado por execução.** Todos os números acima saem do programa; a rodada de 2026 isolada (02/01 a 09/11/2026) dá exatamente os números da versão 3 (total R$ 43.500,62; Agressiva 1 R$ 11.137,10; Agressiva 2 R$ 10.981,15; Conservadora 1 R$ 11.003,58; Conservadora 2 R$ 10.378,79), com `kairi_carteira_2026.py` intocado. Asserts: caixa nunca negativo; nenhuma compra no dia do sinal; nenhum dado ou documento do futuro (131 usos de documentos do FNET, todos de 2025 em diante); decomposição fecha em todas as rodadas; operações de 2018 e 2019 refeitas à mão.
**Interpretação.** "Um ano de cada vez" = carteira vazia no 1º pregão, sinais só a partir desse dia (sinal de dezembro do ano anterior não vale); a saída que cairia depois do último pregão do ano vira posição aberta a preço de fechamento; "ganhou do CDI" = retorno líquido do ano pelo menos 0,05 ponto acima do CDI; média dos anos simples; "mercado" = índice de mercado.csv. Que a regra repita o desempenho em outro ano é dedução, não está provado.
