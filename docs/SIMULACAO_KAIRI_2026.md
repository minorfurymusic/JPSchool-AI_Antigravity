# Simulação do Kairi em 2026: carteira de R$ 20.000

Programa: `estudos/kairi_carteira_2026.py` (rodada do zero em poucos segundos). Planilha com gráficos: `planilhas/kairi_carteira_2026.xlsx`.
Gerado automaticamente; os números abaixo vêm da rodada do programa.

## Resultado em uma frase

De 02/01/2026 a 09/11/2026, a carteira total de R$ 20.000 foi para R$ 20.597,01 (3,0%; 2,7% descontando o imposto que seria devido ao vender tudo), contra R$ 22.007,15 (10,0%) de deixar tudo em 105% do CDI e R$ 19.396,19 (-3,0%) do mercado de fundos. Perdeu do CDI nas duas sub-carteiras.

## O que foi simulado

- **Duas sub-carteiras independentes**, cada uma com caixa próprio de R$ 10.000 em 02/01/2026 (primeiro pregão do ano). Começam vazias: só valem sinais com data a partir de 02/01/2026.
- **Conservadora:** compra quando a cota fecha 20% ou mais abaixo da média dos últimos 200 pregões (o "gatilho"), com rendimento do fundo mantido. **Agressiva:** gatilho de 15%. **Variante extra:** conservadora com gatilho de 30%.
- **Mesmas regras das ordens já estudadas** (`estudos/auditoria_bloco2.py`, cópia verificada de `kairi_ordens.py`): universo de fundos, filtros (patrimônio, negociado, rendimento, preço sobre valor patrimonial), guarda de dados com saltos e buracos, entrada na abertura do pregão seguinte ao sinal, saída quando a máxima do dia toca a média de 200 pregões (vende pelo preço da média, ou pela abertura se for maior) ou no prazo de 252 pregões.
- **Tamanho da ordem:** R$ 1.000 (testes com R$ 500 e R$ 2.000), cotas inteiras, no máximo 2% do negociado médio do fundo em 60 dias e no máximo o caixa disponível. Abaixo de R$ 200 não compra. O mesmo fundo não pode ser comprado de novo enquanto já está na sub-carteira. Se há mais sinais que dinheiro no mesmo dia, compra primeiro o fundo mais negociado.
- **Taxa:** 0,03% na compra e 0,03% na venda.
- **Rendimentos** (isentos) entram no caixa na **data de pagamento** (`rendimentos_pagamentos.csv`). Tem direito quem estava com a cota no fechamento da data de corte do aviso (a "data-base"), a mesma regra de `kairi_ordens.py`. Pagamento em dia sem pregão entra no pregão seguinte.
- **Caixa parado** rende 105% do CDI com liquidez diária (`cdi.csv`), em lotes: cada entrada de dinheiro é um lote; as compras resgatam do lote mais antigo, com IR regressivo (22,5% até 180 dias corridos; 20% de 181 a 360; 17,5% de 361 a 720; 15% acima) e IOF nos primeiros 29 dias, por lote. O caixa que aparece no patrimônio diário já é líquido de IR e IOF.
- **Imposto do FII:** 20% sobre o ganho líquido das vendas de cada mês (prejuízo abate os ganhos seguintes). O DARF sai do caixa no último dia útil do mês seguinte. Posições abertas no fim ficam a preço de 09/11/2026; mostramos também o valor líquido do imposto que seria devido se fossem vendidas.
- **Comparações:** R$ 20.000 todo em 105% do CDI (líquido de IR, como resgatado em 09/11/2026) e o índice "mercado" (`mercado.csv`, fundo imobiliário do meio).

## Tabela 1. Resumo (ordem de R$ 1.000)

| Indicador | Conservadora (20%) | Agressiva (15%) | Total (R$ 20 mil) | 105% do CDI (R$ 20 mil) | Mercado (R$ 20 mil) |
|---|---|---|---|---|---|
| Patrimônio inicial | R$ 10.000,00 | R$ 10.000,00 | R$ 20.000,00 | R$ 20.000,00 | R$ 20.000,00 |
| Patrimônio final (cotas a preço de 09/11) | R$ 10.170,81 | R$ 10.426,20 | R$ 20.597,01 | R$ 22.007,15 | R$ 19.396,19 |
| Retorno no período | 1,7% | 4,3% | 3,0% | 10,0% | -3,0% |
| Patrimônio final líquido do imposto que seria devido | R$ 10.170,81 | R$ 10.365,26 | R$ 20.536,07 | R$ 22.007,15 | R$ 19.396,19 |
| Retorno líquido | 1,7% | 3,7% | 2,7% | 10,0% | -3,0% |
| Retorno líquido contra o CDI (pontos) | -8,3 | -6,4 | -7,4 | 0,0 | -13,1 |
| Maior queda no caminho | -10,1% | -12,7% | -11,2% | 0,0% | -10,5% |
| ... do pico em / até | 22/10/2026 / 03/11/2026 | 09/10/2026 / 04/11/2026 | 22/10/2026 / 03/11/2026 | — | 23/10/2026 / 03/11/2026 |
| Operações abertas / fechadas | 11 / 2 | 12 / 12 | 23 / 14 | — | — |
| Fechadas com lucro | 50,0% | 83,3% | 78,6% | — | — |
| Todas com lucro (abertas a preço de 09/11) | 61,5% | 58,3% | 59,5% | — | — |
| Pior operação | -47,3% MCEM11 | -47,3% MCEM11 | -47,3% MCEM11 | — | — |
| Melhor operação | 51,3% RBRS11 | 21,0% RBRP11 | 51,3% RBRS11 | — | — |
| Rendimentos recebidos | R$ 157,36 | R$ 421,01 | R$ 578,37 | — | — |
| Imposto do FII pago | R$ 60,93 | R$ 22,55 | R$ 83,48 | — | — |
| Imposto do FII devido e não pago | R$ 0,00 | R$ 102,67 | R$ 102,67 | — | — |
| Imposto se vendesse as abertas em 09/11 | R$ 0,00 | R$ 0,00 | R$ 0,00 | — | — |
| IR e IOF retidos do caixa | R$ 203,84 | R$ 158,47 | R$ 362,31 | R$ 501,79 | — |
| Taxas de compra e venda | R$ 3,99 | R$ 10,23 | R$ 14,22 | — | — |
| Sinais sem dinheiro | 0 | 29 | 29 | — | — |
| Giro | 1,14 | 2,17 | 1,65 | — | — |
| Tempo médio por operação fechada (dias) | 33,0 | 42,1 | 40,8 | — | — |
| Dinheiro aplicado em fundos, em média | 19,5% | 45,1% | 32,2% | — | — |

**Legenda.** *Patrimônio* = caixa (líquido de IR e IOF) + cotas ao último preço, em R$. *Retorno* = final ÷ inicial − 1, no período todo (não por ano). *Líquido* = patrimônio final menos o imposto do FII devido (de vendas já feitas e do que seria cobrado se as cotas abertas fossem vendidas em 09/11). *Contra o CDI* = retorno líquido menos o retorno líquido do 105% do CDI, em pontos percentuais. *Maior queda* = maior distância, em %, de um valor alto do patrimônio até o ponto mais baixo seguinte. *Operações abertas* = ainda com cotas em 09/11. *Com lucro* = resultado (valorização + rendimentos − taxas) maior que zero. *Pior/melhor* = em % do valor comprado. *Imposto do FII pago* = DARF efetivamente pago até 09/11. *IR e IOF retidos do caixa* = imposto cobrado nos resgates do dinheiro parado (no 105% do CDI de R$ 20 mil, o IR do fim). *Sinais sem dinheiro* = sinais em que a compra era possível pelo negociado, mas o caixa não tinha R$ 200 livres. *Giro* = total comprado em fundos ÷ patrimônio médio. *Dinheiro aplicado em fundos* = média diária de (valor das cotas ÷ patrimônio).

**Leitura prática.** A carteira ficou 7,4 pontos abaixo do CDI: ganhou 2,7% contra 10,0%. Até 22/10/2026 o total chegou a R$ 22.771,41; de 22/10/2026 a 03/11/2026 caiu 11,2%. As 23 posições ainda abertas somam resultado de R$ -1.209,09 (as piores: TGAR11 (-35,1%), APXM11 (-29,7%), VGHF11 (-28,9%)); as fechadas somam R$ 700,34. Os rendimentos recebidos (R$ 578,37) não cobriram essas perdas.

## Tabela 2. Retorno mês a mês

| Mês | Conservadora | Agressiva | Total | 105% do CDI | Mercado |
|---|---|---|---|---|---|
| jan/26 | 0,8% | 0,8% | 0,8% | 0,8% | 2,5% |
| fev/26 | 2,3% | 0,9% | 1,6% | 0,9% | 1,1% |
| mar/26 | 2,6% | 1,7% | 2,1% | 1,0% | -0,6% |
| abr/26 | 0,3% | 1,2% | 0,8% | 0,9% | 1,2% |
| mai/26 | -1,0% | -2,3% | -1,7% | 0,9% | -1,3% |
| jun/26 | -0,5% | -0,4% | -0,5% | 0,9% | -0,5% |
| jul/26 | 2,4% | 4,1% | 3,3% | 1,2% | -0,1% |
| ago/26 | 0,1% | -1,9% | -0,9% | 0,9% | -0,9% |
| set/26 | -0,4% | 3,4% | 1,4% | 0,9% | 0,5% |
| out/26 | -3,9% | -1,8% | -2,8% | 0,9% | -3,4% |
| nov/26 (até 09/11) | -0,8% | -1,3% | -1,1% | 0,2% | -1,4% |

**Legenda.** Retorno de cada mês = patrimônio do último pregão do mês ÷ patrimônio do último pregão do mês anterior − 1. Janeiro parte do fechamento de 02/01/2026; novembro vai até 09/11. "Total" = as duas sub-carteiras somadas.

**Leitura prática.** O total ganhou do 105% do CDI em 4 dos 11 meses. O pior mês foi out/26 (-2,8%), junto com a queda do mercado. Os meses em que ficou abaixo do CDI foram: abr/26, mai/26, jun/26, ago/26, out/26, nov/26.

## Tabela 3. Variantes (cada linha parte de R$ 10.000)

| Sub-carteira | Gatilho | Ordem | Patrimônio final (preço de 09/11) | Patrimônio final líquido | Retorno líquido | Maior queda | Operações | Giro | Sinais sem dinheiro |
|---|---|---|---|---|---|---|---|---|---|
| Conservadora | 20% | R$ 500 | R$ 10.643,44 | R$ 10.643,44 | 6,4% | -4,8% | 13 | 0,59 | 0 |
| Conservadora | 20% | R$ 1.000 | R$ 10.170,81 | R$ 10.170,81 | 1,7% | -10,1% | 13 | 1,14 | 0 |
| Conservadora | 20% | R$ 2.000 | R$ 9.327,87 | R$ 9.327,87 | -6,7% | -19,7% | 9 | 1,16 | 4 |
| Agressiva | 15% | R$ 500 | R$ 10.900,41 | R$ 10.818,64 | 8,2% | -8,5% | 39 | 1,77 | 6 |
| Agressiva | 15% | R$ 1.000 | R$ 10.426,20 | R$ 10.365,26 | 3,7% | -12,7% | 24 | 2,17 | 29 |
| Agressiva | 15% | R$ 2.000 | R$ 9.788,57 | R$ 9.775,70 | -2,2% | -13,9% | 14 | 2,07 | 48 |
| Conservadora 30% | 30% | R$ 500 | R$ 10.625,14 | R$ 10.625,14 | 6,3% | -1,6% | 2 | 0,09 | 0 |
| Conservadora 30% | 30% | R$ 1.000 | R$ 10.246,71 | R$ 10.246,71 | 2,5% | -3,8% | 2 | 0,19 | 0 |
| Conservadora 30% | 30% | R$ 2.000 | R$ 9.948,80 | R$ 9.948,80 | -0,5% | -4,8% | 2 | 0,30 | 0 |
| 105% do CDI (R$ 10 mil) | — | — | R$ 11.003,58 | R$ 11.003,58 | 10,0% | 0,0% | — | — | — |

**Legenda.** *Gatilho* = queda abaixo da média de 200 pregões que dispara a compra. *Ordem* = valor pretendido por compra. *Patrimônio final líquido* = descontado o imposto do FII devido e o que seria devido ao vender as posições abertas. *Retorno líquido* = patrimônio final líquido ÷ R$ 10.000 − 1. *Giro* = total comprado ÷ patrimônio médio. A última linha é R$ 10.000 em 105% do CDI.

**Leitura prática.** Todas as variantes ficaram abaixo do 105% do CDI (10,0%). Quanto maior a ordem, pior o resultado neste ano; ordens maiores esgotam o caixa mais cedo (deixam passar sinais) e fazem as perdas de fundos como MCEM11 pesarem mais. Com apenas esta amostra, isso não é uma regra. A conservadora de 30% quase não operou (2 compras): a queda foi pequena, mas o dinheiro ficou parado no CDI.

## Tabela 4. Operações fechadas (ordem de R$ 1.000)

| Sub-carteira | Fundo | Entrada | Saída | Motivo | Valor da compra | Rendimentos | Resultado | Resultado (%) |
|---|---|---|---|---|---|---|---|---|
| Agressiva | MCEM11 | 09/03/2026 | 17/03/2026 | volta à média | R$ 841,82 | R$ 0,00 | R$ 65,90 | 7,8% |
| Agressiva | MCEM11 | 12/05/2026 | 25/06/2026 | fundo saiu da bolsa | R$ 818,72 | R$ 0,00 | R$ -387,58 | -47,3% |
| Agressiva | VVCR11 | 02/07/2026 | 07/07/2026 | volta à média | R$ 995,52 | R$ 0,00 | R$ 167,05 | 16,8% |
| Agressiva | XPIN11 | 24/06/2026 | 13/07/2026 | fundo saiu da bolsa | R$ 984,00 | R$ 0,00 | R$ 8,05 | 0,8% |
| Agressiva | VVCR11 | 15/07/2026 | 22/07/2026 | volta à média | R$ 997,53 | R$ 15,99 | R$ 180,31 | 18,1% |
| Agressiva | HCHG11 | 15/07/2026 | 22/07/2026 | fundo saiu da bolsa | R$ 640,00 | R$ 0,00 | R$ -20,58 | -3,2% |
| Agressiva | ITIP11 | 08/07/2026 | 03/09/2026 | fundo saiu da bolsa | R$ 945,20 | R$ 28,56 | R$ 4,20 | 0,4% |
| Agressiva | VVCR11 | 04/09/2026 | 22/09/2026 | volta à média | R$ 994,14 | R$ 12,60 | R$ 172,71 | 17,4% |
| Agressiva | RBRP11 | 05/08/2026 | 30/09/2026 | volta à média | R$ 975,20 | R$ 16,10 | R$ 204,61 | 21,0% |
| Agressiva | VVCR11 | 01/10/2026 | 02/10/2026 | volta à média | R$ 993,28 | R$ 0,00 | R$ 174,23 | 17,5% |
| Agressiva | FIIP11 | 16/03/2026 | 07/10/2026 | volta à média | R$ 930,16 | R$ 69,30 | R$ 99,35 | 10,7% |
| Agressiva | VCRR11 | 05/08/2026 | 22/10/2026 | volta à média | R$ 855,68 | R$ 14,08 | R$ 114,47 | 13,4% |
| Conservadora | RBRS11 | 10/02/2026 | 04/03/2026 | volta à média | R$ 594,90 | R$ 0,54 | R$ 305,19 | 51,3% |
| Conservadora | MCEM11 | 12/05/2026 | 25/06/2026 | fundo saiu da bolsa | R$ 818,72 | R$ 0,00 | R$ -387,58 | -47,3% |

**Legenda.** *Motivo:* volta à média = a cota subiu até a média de 200 pregões; fundo saiu da bolsa = os preços acabaram antes de 09/11 (vendido ao último preço). *Rendimentos* = o que o fundo pagou por cota enquanto se tinha a cota (inclui os ainda a receber). *Resultado* = valorização + rendimentos − taxas, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor da compra.

| Sub-carteira | Posições abertas | Valor comprado | Resultado hoje (com rendimentos) | Em prejuízo | Pior |
|---|---|---|---|---|---|
| Conservadora | 11 | R$ 10.569,88 | R$ -455,15 | 4 | TGAR11 -35,1% |
| Agressiva | 12 | R$ 11.519,64 | R$ -753,94 | 8 | APXM11 -29,7% |

**Legenda.** *Resultado hoje* = valorização a preço de 09/11 + rendimentos − taxa de compra. *Em prejuízo* = posições abertas com resultado negativo.

**Leitura prática.** Das 14 operações fechadas, as 9 de volta à média tiveram resultado entre 7,8% e 51,3%; as 5 que fecharam por 'fundo saiu da bolsa' ficaram entre -47,3% e 0,8%. Entre as abertas, 12 de 23 estão no prejuízo, e a conta final depende de elas voltarem à média ou não.

## Tabela 5. O que aconteceu com cada sinal (ordem de R$ 1.000)

| Sub-carteira (ordem R$ 1.000) | comprado | comprado (reduzido pelo caixa) | fundo já em carteira | sem dinheiro | sem negociação na abertura | Total de sinais |
|---|---|---|---|---|---|---|
| Agressiva | 21 | 3 | 26 | 29 | 0 | 79 |
| Conservadora | 13 | 0 | 5 | 0 | 1 | 19 |
| Conservadora 30% | 2 | 0 | 1 | 0 | 0 | 3 |

**Legenda.** *Comprado* = ordem executada com o valor pretendido. *Reduzido pelo caixa* = comprou menos que o pretendido, mas pelo menos R$ 200. *Fundo já em carteira* = o mesmo fundo já estava na sub-carteira. *Sem dinheiro* = faltou caixa. *Sem negociação na abertura* = o fundo não negociou no dia da entrada.

**Leitura prática.** A agressiva ficou sem dinheiro em 29 sinais, o primeiro em 06/08/2026 (caixa todo aplicado). A conservadora teve poucos sinais e não faltou dinheiro para nenhum.

## Conferências feitas pelo programa

Todas passaram (asserts dentro do programa; veja a saída impressa):

- O caixa nunca ficou negativo em nenhum dia, nas 9 simulações (menor caixa: R$ 0,00).
- Nenhuma compra no dia do sinal (118 compras, todas depois) e nenhum sinal anterior a 02/01/2026.
- O imposto do FII refeito por fora (mês a mês, com prejuízo abatendo) bate com o do programa; devido = pago + pendente + a vencer.
- R$ 20.000 em 105% do CDI refeitos à mão: R$ 22.007,15 líquido (IR de 20%, 311 dias).
- Conservadora, RBRS11 (sinal 09/02/2026, entrada 10/02/2026, saída 04/03/2026): compra 18 cotas × R$ 33,05 = R$ 594,90; rendimentos R$ 0,54; venda R$ 900,00; taxas R$ 0,45; resultado R$ 305,19 (51,3%). O programa deu o mesmo valor.
- Agressiva, FIIP11 (sinal 13/03/2026, entrada 16/03/2026, saída 07/10/2026): compra 7 cotas × R$ 132,88 = R$ 930,16; rendimentos R$ 69,30; venda R$ 960,77; taxas R$ 0,57; resultado R$ 99,35 (10,7%). O programa deu o mesmo valor.
- Resgate do caixa (Agressiva), só IR: compra em 09/03/2026; lote de 02/01/2026 (66 dias corridos); parte resgatada R$ 825,94; rendimento bruto R$ 20,81; IOF R$ 0,00; IR de 22,5% = R$ 4,68; líquido R$ 842,07. O programa deu o mesmo valor.
- Resgate do caixa (Agressiva), IOF + IR: compra em 10/07/2026; lote de 15/06/2026 (25 dias corridos); parte resgatada R$ 9,94; rendimento bruto R$ 0,10; IOF R$ 0,02; IR de 22,5% = R$ 0,02; líquido R$ 10,00. O programa deu o mesmo valor.

## O que foi confirmado por execução e o que é interpretação

**Confirmado por execução (rodou e conferiu):** todos os números das tabelas; o caixa nunca negativo; entrada sempre depois do sinal; compra, rendimento, venda, taxa e resultado de uma operação de cada sub-carteira refeitos a partir dos arquivos de entrada; um resgate do caixa com IR (e outro com IOF + IR) refeitos com `cdi.csv`; imposto do FII refeito por fora.

**Interpretação (decisão minha, onde o pedido não dizia):**
- "Um fundo por vez" foi lido como: o mesmo fundo não pode ser comprado duas vezes ao mesmo tempo na mesma sub-carteira (como em `kairi_carteira.py`). Cada sub-carteira pode ter vários fundos diferentes.
- Compras na abertura resgatam o caixa com o índice do CDI do pregão anterior (o dia de hoje ainda não rendeu); os dias corridos para IR/IOF contam até a data do resgate. A venda de um fundo vira um lote novo no mesmo dia.
- Direito ao rendimento: data-base entre a entrada e a saída (inclusive a data de saída só quando a saída é no fechamento, no prazo ou posição aberta), como em `kairi_ordens.py`.
- Pagamento em fim de semana ou feriado entra no pregão seguinte. Avisos sem data de pagamento não entram (nada foi estimado).
- Para o retorno e a comparação, usei o patrimônio líquido do imposto do FII que seria devido ao vender tudo (o CDI também está líquido). O patrimônio diário não desconta imposto ainda não vencido.
- Resultado de cada operação = valorização + rendimentos (inclusive os ainda a receber) − taxas, antes do imposto, que é cobrado por mês.
- Total = soma simples das duas sub-carteiras (R$ 10.000 + R$ 10.000); elas compram, em parte, os mesmos fundos.

## Lacunas

| Dado ou regra | Situação | Efeito no resultado |
|---|---|---|
| Fundos cujos preços acabam no meio do período (HCHG11, ITIP11, MCEM11, XPIN11) | Em 5 ordens (conservadora + agressiva) o fundo parou de ter preço antes de 09/11 (as últimas linhas têm 'negociou = 0'). Vendido ao último preço registrado. Não há dado do que realmente aconteceu (liquidação, incorporação, suspensão). | Comprado nessas ordens: R$ 4.206,64; resultado simulado: R$ -783,48 (a maior parte é MCEM11, que caiu de 62 para 26,97). O resultado real pode ser pior ou melhor. |
| Amortizações (devolução de capital) | 0 eventos nas posições de 2026; não são creditadas no caixa se existirem. | Hoje: R$ 0,00. |
| Rendimentos sem data de pagamento | 5 avisos de 2026 (todos os fundos) sem data de pagamento; nas posições simuladas, R$ 0,00. Não foi estimada data. | Esse dinheiro não entra no caixa. |
| Rendimentos que vão ser pagos depois de 09/11 | R$ 98,40 já declarados nas posições (conservadora + agressiva). | Não entram no patrimônio de 09/11 (entrariam nos dias seguintes). |
| Compra na abertura e venda pelo preço da média | Ninguém garante esses preços em fundo pouco negociado; o limite de 2% do negociado médio reduz, mas não elimina, o problema. | Resultado otimista, não medido. |
| Dinheiro da venda usado na mesma abertura | O motor usa o dinheiro de uma venda do dia para comprar na abertura do mesmo dia. | Pequeno ganho de tempo a favor da carteira; não medido. |
| Preço de 09/11 de fundos sem negociação no dia | 3 posições abertas (conservadora + agressiva) não tiveram negociação em 09/11; usa-se o último fechamento. | Valor das posições pode estar defasado. |
| DARF vencido sem caixa para pagar | Agressiva: R$ 41,74 de imposto vencido em 30/10 ficou pendente (caixa todo aplicado). Foi descontado do patrimônio. | Já considerado no patrimônio. |
| Outros custos | Só a taxa de 0,03% por compra e por venda. Não há corretagem, custódia nem diferença entre preço de compra e de venda. | Resultado real um pouco menor. |
| Prejuízo de anos anteriores | A carteira nasce vazia em 02/01/2026; não há prejuízo acumulado de 2025 para abater. | Nenhum. |
| Mercado (índice do fundo do meio) | Índice sem custos nem imposto, calculado a partir do fechamento de 02/01/2026. | Comparação apenas de referência. |
| Sinais de 20% e de 15% repetem | Um fundo que cai 20% abaixo da média antes passou pelos 15%, então os mesmos fundos aparecem nas duas sub-carteiras (8 fundos em comum: BCRI11, ITIT11, MAXR11, MCEM11, OUJP11, RBRR11, RBRX11, VGHF11); 2 compras são idênticas (mesmo fundo e mesmo dia). | As duas sub-carteiras não são apostas independentes; a mesma perda (ex.: MCEM11 em 12/05) conta duas vezes no total. |

## Avisos

- **2026 não é um teste novo.** O período de conferência (2023 a 2026) já foi visto em estudos anteriores; esta simulação usa dados que já entraram nas escolhas.
- **Um ano só não prova nada.** São 213 pregões e 37 compras no total; a conservadora fez 13 e só 2 já fecharam. Dois ou três fundos explicam quase toda a diferença para o CDI.
- **Compras na abertura e vendas pelo preço da média são otimistas** em fundo pouco negociado.

## Queda geral de 26/10/2026 (conferência feita depois da simulação)

Nas planilhas de preços, 153 dos 221 fundos que negociaram em 26/10/2026 caíram mais de 3% no dia. Só 1 subiu mais de 3%, e a variação do fundo do meio foi −5,0%. A queda continuou até 03/11/2026 (o fundo do meio caiu −2,4% nesse dia). Exemplos: HGLG11 foi de R$ 159,66 a R$ 144,62 e MXRF11 de R$ 9,44 a R$ 8,47.

| Data | Fundos que negociaram | Variação do fundo do meio | Caíram mais de 3% | Subiram mais de 3% |
|---|---|---|---|---|
| 23/10/2026 | 218 | +0,1% | 7 | 12 |
| 26/10/2026 | 221 | −5,0% | 153 | 1 |
| 28/10/2026 | 228 | −1,4% | 42 | 7 |
| 03/11/2026 | 220 | −2,4% | 92 | 10 |

Leitura prática: até 22/10/2026 a carteira total estava em R$ 22.771 (+13,9%), à frente do CDI. A queda geral do fim de outubro levou o resultado para baixo do CDI. **Não conferi essa queda em outra fonte.** Se for erro de dado, o resultado muda.
