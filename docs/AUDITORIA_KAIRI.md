# Auditoria do Estudo do Kairi — resultado

Data: 2026-11-17. Pedido em `docs/AUDITORIA_PEDIDO.md`. Régua: **105% do CDI em liquidez diária, com IR regressivo e IOF**.
Programas: `estudos/auditoria_bloco1.py`, `auditoria_bloco2.py`, `auditoria_bloco3.py` (escritos e rodados por agentes auxiliares; rodados de novo do zero por mim, saída sem erro). Planilhas: `planilhas/auditoria_bloco1_*.csv`, `auditoria_bloco2_*.csv`, `auditoria_bloco3_*.csv`.

## Resultado em uma frase

O Kairi ganhou do 105% do CDI em todas as contas, mas **a vantagem não está provada contra sorte**: as 341 ordens da carteira A são, na prática, 24 episódios (ondas de queda geral), 3 deles fazem 81% do ganho, e no período de conferência (2023 a 2026) o ganho da carteira inteira sobre o CDI foi de só 0,4 a 0,8 ponto ao ano, com intervalo de confiança que inclui zero.

## Tabela mestra

| Medida | A (15%) | B (20%) | C (15%, queda geral) | Bloco |
|---|---|---|---|---|
| Ordens (fechadas + em aberto) | 341 (311 + 30) | 175 (164 + 11) | 292 (267 + 25) | 1 |
| Episódios independentes (janela de 20 pregões) | 24 | 30 | 12 | 1 |
| Parte do ganho nos 3 maiores episódios | 81% | 92% | 86% | 1 |
| Resultado por ordem antes do imposto: média / mediana | 10,5% / 12,8% | 15,7% / 18,4% | 11,5% / 13,3% | 1 |
| Excesso por ordem sobre 105% CDI (antes do imposto dos dois lados): média / mediana | 6,9 / 9,8 pp | 12,1 / 14,7 pp | 8,0 / 10,1 pp | 1 |
| Excesso por ordem: quantil 5% (as 5% piores ficam abaixo) | −19,8 pp | −29,3 pp | −14,2 pp | 1 |
| Assimetria do excesso (negativa = cauda de perdas grandes) | −2,2 | −1,1 | −2,3 | 1 |
| Ganhos ÷ perdas em R$ (excesso) | 3,4 | 5,4 | 4,5 | 1 |
| Taxa interna de retorno do dinheiro enquanto está nas ordens / mesmo dinheiro em 105% CDI | 29,8% / 7,2% ao ano | 40,8% / 6,3% | 32,2% / 6,9% | 1 |
| Carteira com o dinheiro do pico (sobra em 105% CDI), 02/01/2018 a 09/11/2026: valor final | R$ 619.443 | R$ 386.241 | R$ 604.946 | 1 |
| Mesmo dinheiro todo em 105% CDI: valor final | R$ 545.854 | R$ 314.810 | R$ 530.099 | 1 |
| Retorno ao ano: carteira do pico / 105% CDI | 10,2% / 8,6% | 11,1% / 8,6% | 10,2% / 8,6% | 1 |
| Sharpe / Sortino / Calmar (carteira do pico) | 0,48 / 1,26 / 3,73 | 0,51 / 2,25 / 3,18 | 0,48 / 1,33 / 3,75 | 1 |
| Maior queda do patrimônio (março de 2020) | −2,7% | −3,5% | −2,7% | 1 |
| Excesso ao ano da carteira do pico, total: média e IC 95% (Newey-West, 6 defasagens) | 1,5 pp (−0,5 a 3,4); p = 0,13 | 2,4 pp (−1,2 a 6,0); p = 0,18 | 1,5 pp (−0,4 a 3,5); p = 0,13 | 1 |
| Idem, só conferência (2023–2026) | 0,4 pp (−1,2 a 2,1); p = 0,60 | 0,8 pp (−1,6 a 3,2); p = 0,51 | 0,7 pp (−1,0 a 2,3); p = 0,41 | 1 |
| Teste ingênuo por ordem (engana: trata ordens da mesma onda como independentes) | p < 0,001 | p < 0,001 | p < 0,001 | 1 |
| Ordens lucrativas perdidas ao subir o gatilho para o seguinte (15→20, 20→30) | 166 (R$ 60.798) contra 6 prejuízos evitados (R$ 677) | 125 (R$ 64.907) contra 6 (R$ 1.468) | — | 2 |
| Virada (esperar a cota parar de cair) contra entrada direta: excesso em R$ | R$ 48.166 contra R$ 68.487 (pior nos dois períodos) | R$ 37.666 contra R$ 60.666 (pior nos dois) | — | 2 |
| Entrada em duas partes contra direta, mesmos sinais | R$ 57.250 contra R$ 68.711 | R$ 48.353 contra R$ 60.787 | — | 2 |
| Ordens com fato negativo nos 60 dias antes do sinal | 12 a 19 por carteira, 45 de 764 no total (6%) | | | 3 |
| Diferença "sem notícia" menos "com fato negativo" (60 dias), IC 95% | −1,4 pp (−6,7 a +4,3); p = 0,34 | +0,9 pp (−9,0 a +11,6); p = 0,99 | −0,5 pp (−5,9 a +5,8); p = 0,53 | 3 |

Legenda:
- **pp** = pontos percentuais. **Excesso** = resultado do fundo menos o que o mesmo dinheiro, nas mesmas datas, renderia a 105% do CDI.
- **Episódio independente** = cadeia de ordens com entradas a no máximo 20 pregões uma da outra (com 10 e 40 pregões: A 46 e 12; B 39 e 19; C 23 e 7).
- **Taxa interna de retorno** = retorno ao ano dos fluxos reais (compra, rendimentos na data de pagamento, venda e imposto pago no mês seguinte). Mede o dinheiro **só enquanto está aplicado**; ignora o dinheiro parado esperando sinal.
- **Carteira do pico** = começa com o maior valor que chegou a estar aplicado ao mesmo tempo. O que não está em ordem fica em 105% do CDI, com IR e IOF por lote. **É a conta que mais se parece com a vida real.**
- **Sharpe** = ganho mensal acima do CDI ÷ oscilação, ao ano. **Sortino** = o mesmo, contando só a oscilação para baixo. **Calmar** = retorno ao ano ÷ maior queda.
- **p** = chance de ver um ganho desse tamanho só por sorte, se a regra não tivesse vantagem nenhuma. Abaixo de 0,05 costuma ser considerado prova. **IC 95%** = faixa em que o ganho verdadeiro provavelmente está; se inclui zero, não está provado.
- **Newey-West** = forma de calcular o p que leva em conta que meses seguidos se parecem.

Leitura prática:
- Na carteira real (dinheiro do pico), o Kairi rendeu 10,2% a 11,1% ao ano contra 8,6% do CDI: cerca de R$ 71 a 75 mil a mais em quase 9 anos, com queda máxima de 3,5%.
- Esse ganho veio de poucas ondas (principalmente 2020 e 2024). Na conferência, ele quase desaparece e não dá para separar de sorte.
- Subir o gatilho, esperar a virada ou entrar em duas partes **pioram** o resultado. Ter ou não fato negativo antes da queda não mostrou diferença.

## Avisos de comparação entre blocos

| Ponto | Situação |
|---|---|
| Base do "excesso" no bloco 2 | O bloco 2 compara o fundo **antes** do imposto com o CDI **líquido** de IR. Os blocos 1 e 3 comparam os dois **antes** do imposto. Por isso, os R$ de excesso do bloco 2 ficam maiores que os do bloco 1 para a mesma carteira. As conclusões do bloco 2 (gatilho, virada, duas partes) comparam regras entre si na mesma base e não mudam. A conta com imposto dos dois lados é a da carteira do pico (bloco 1). |
| Carteira C | Todas as 292 ordens têm 15% ou mais de fundos caídos no dia. Por isso, o item 6d do bloco 3 repete o 6a/6b. |
| Ordens em aberto (66) | Entram pelo preço de 09/11/2026, sem imposto. As estatísticas por ordem usam só as fechadas. |

## Lacunas (todas as do pedido e as achadas pelos três blocos)

| Dado | Situação | Efeito |
|---|---|---|
| Classificação dos fatos relevantes | Por palavras. Numa amostra lida, errou 10 de 20 negativos e 7 de 20 positivos | Os cruzamentos do bloco 3 são aproximados |
| Texto dos fatos | Só os primeiros 3.000 caracteres (3.466 de 7.962 cortados). Fatos em imagem não têm texto. Comunicados ao mercado não foram baixados | Fatos podem faltar ou estar mal lidos |
| Fundos sem nenhum fato | 15 fundos, 44 ordens, fora das comparações do bloco 3 | "Sem dado" não é "sem notícia" |
| Cobertura dos fatos nos primeiros anos | 278 em 2017, 402 em 2018, 538 em 2019, contra cerca de 1.000 depois | Os primeiros anos têm menos fatos |
| Amortizações | Não entram como dinheiro recebido nas ordens | Fundos que devolveram patrimônio aparecem com perda maior que a real |
| Saltos de preço | 334 variações de mais de 25% num dia, em 128 fundos, sem ajuste. 13 das 341 ordens da A têm um salto | Afeta essas ordens; não foram removidas |
| Data de pagamento dos rendimentos | 3 avisos (R$ 82,08) sem data; usada a data-base + 11 dias. 20 avisos (R$ 690,98) pagos depois de 09/11/2026 | Pequeno |
| Imposto por ordem | O imposto do fundo é mensal com abatimento e não se divide por ordem | Comparações por ordem são antes do imposto |
| Ordens em aberto | Sem imposto na venda hipotética | Taxa interna de retorno e valor final levemente favorecidos |
| Índice da bolsa de ações | Não está na base; "mercado" é o fundo imobiliário do meio | Sem comparação com ações |
| Dias úteis depois de 13/11/2026 | Sem feriados | No máximo 1 dia de diferença num imposto |

---

## Bloco 1 da auditoria — indicadores, taxa interna de retorno e significância

Programa: `estudos/auditoria_bloco1.py` (lê só `planilhas/`; roda em cerca de 12 segundos). Planilhas geradas: `planilhas/auditoria_bloco1_*.csv` (indicadores, correlacao_grupos, episodios, tir, pico, risco, patrimonio_mensal, significancia, ordens, lacunas). Ordens: as 341 (A), 175 (B) e 292 (C) de `planilhas/kairi_ordens.csv`. Régua: 105% do CDI em aplicação de liquidez diária, com IR regressivo e IOF. Escolha = entradas de 2018 a 2022; conferência = entradas de 2023 a 2026; total = todas.

### O que foi confirmado por execução e o que é interpretação

**Confirmado por execução** (o programa imprime a conferência):

- A soma dos rendimentos de cada ordem, refeita pela regra de direito (aviso com data-base a partir do dia da entrada e antes da saída; até a saída incluída nas saídas por prazo e nas ordens em aberto) usando `rendimentos_pagamentos.csv`, bate com a coluna "Rendimentos recebidos (R$)" em todas as 808 ordens (maior diferença: R$ 0,005, arredondamento do centavo). Totais: A R$ 32.278,69 contra 32.278,68; B R$ 17.968,13 contra 17.968,13; C R$ 27.509,43 contra 27.509,42.
- Cotas × preço de abertura do dia da entrada (lido de `precos_*.csv`) bate com "Valor da ordem" (diferença máxima R$ 0,005). As taxas de 0,03% por lado batem com a planilha (diferença máxima R$ 0,005). O resultado antes do imposto bate com `kairi_ordens_saidas.csv` nas carteiras A e B (diferença máxima R$ 0,0097); a carteira C não está nesse arquivo.
- O imposto mensal com abatimento de prejuízo, calculado aqui para a carteira A inteira (ordens fechadas), dá R$ 13.033,09, igual aos R$ 13.033 que a Parte 4 do `ESTUDO_KAIRI.md` registra. B: R$ 11.795,95 (a Parte 4 diz R$ 11.796). C: R$ 12.720,35.
- Duas contas refeitas à mão com código independente: a ordem BBVJ11 da carteira A (entrada 28/05/2018, saída 21/12/2018) e uma aplicação de R$ 10.000 em 105% do CDI (com IR de 20%; e outra com IOF de 50% no 15º dia). Todas bateram até o centavo (ver "Conferência" no fim).
- Testes do motor de lotes: sem ordens, o saldo final é igual ao do espelho (diferença 0,000000); um saque líquido de R$ 55.000 em três lotes reduz o saldo líquido exatamente R$ 55.000,00. A carteira do pico nunca ficou sem caixa (0 eventos).

**Interpretação ou dedução minha** (o pedido admitia mais de uma leitura):

1. *Excesso por ordem* = resultado antes do imposto da ordem (valorização + rendimentos − taxas, dividido pelo valor da ordem) menos o rendimento bruto de 105% do CDI do dia da entrada ao dia da saída. Os dois lados são antes do imposto porque o imposto do FII é mensal, com abatimento de prejuízo, e não se divide por ordem.
2. *Estatísticas por ordem usam só as ordens fechadas* (311, 164 e 267), como o estudo anterior. As 66 ordens em aberto entram só na contagem de episódios, nos fluxos da TIR e na carteira do pico.
3. *Episódio:* ordens ordenadas pela data de entrada, dentro da carteira; uma ordem pertence ao mesmo episódio da anterior se a entrada está a no máximo W pregões da entrada anterior (cadeia). Pregões = calendário de `mercado.csv`. Os episódios são montados separadamente dentro de cada período, então a soma dos episódios de escolha e conferência pode passar um pouco do total.
4. *Grupos de sinais:* (a) mesma data de sinal; (b) janela de 5 pregões a partir do primeiro sinal do grupo (janela fixa, sem encadear). Correlação do par = correlação de Pearson dos retornos diários de fechamento nos pregões em que as duas ordens estavam abertas ao mesmo tempo (do dia seguinte à última entrada até a primeira saída), com no mínimo 20 dias. Retornos acima de +60% ou abaixo de −45% num dia foram descartados (mesma guarda de dado suspeito do estudo). Pares sorteados: para cada par real, 5 pares de fundos sorteados (semente fixa) entre os que estavam no universo do estudo (patrimônio de R$ 50 milhões ou mais, negociado médio de R$ 25 mil ou mais) em pelo menos 90% dos dias do mesmo intervalo, fora os fundos do grupo.
5. *Fluxos da TIR das ordens:* compra e taxa na data da entrada; rendimentos na data de pagamento; venda menos taxa na data da saída; imposto do FII do mês no último dia útil do mês seguinte. O imposto é calculado sobre as ordens fechadas do subconjunto (carteira e período), mês a mês, com prejuízo abatendo os meses seguintes. Ordens em aberto: venda a preço de 09/11/2026, sem imposto, com a taxa de venda.
6. *Espelho em 105% do CDI (item 2b):* cada ordem vira uma aplicação do mesmo valor (compra + taxa) na data da entrada, resgatada na data da saída com IR regressivo e IOF. Os rendimentos intermediários não aparecem no espelho (o dinheiro fica aplicado). Ordens em aberto no espelho são resgatadas em 09/11/2026 já com IR.
7. *Carteira do pico (item 2c):* dinheiro do pico em 02/01/2018; compras tiram do saldo líquido (lote mais antigo primeiro); rendimentos (na data de pagamento) e vendas voltam; o DARF sai do saldo na data de pagamento. **Data final: 09/11/2026** (último preço da base; o `cdi.csv` vai até 13/11/2026 mas não foi usado). O valor final = ordens em aberto a mercado (cotas × último fechamento, menos a taxa de 0,03% da venda) + saldo líquido de IR/IOF + rendimentos declarados e ainda não pagos − DARF devido. O comparativo é o mesmo dinheiro todo em 105% do CDI desde 02/01/2018, resgatado com IR de 15%.
8. *Retornos mensais do patrimônio (itens 2d e 3):* patrimônio líquido diário = saldo líquido de IR e IOF se resgatado no dia + ordens abertas a mercado + rendimentos declarados a receber − DARF devido. Retorno do mês = patrimônio do último dia útil do mês sobre o do mês anterior (o primeiro mês parte de 02/01/2018 e o último termina em 09/11/2026). A taxa livre de risco do mês é o retorno do mesmo mês do "espelho": todo o dinheiro em 105% do CDI desde 02/01/2018, líquido de IR e IOF como se fosse resgatado no fim do mês. Como o espelho é a própria taxa livre de risco, o excesso dele é zero por construção e Sharpe e Sortino dele não existem.
9. *Períodos nos itens 2d e 3(ii)(iii):* a carteira do pico é uma só (2018 a 2026); "escolha" e "conferência" são fatias de meses (2018-01 a 2022-12 e 2023-01 a 2026-11) do mesmo patrimônio, não carteiras separadas.
10. *Testes:* valor p de duas caudas pela distribuição t com n−1 graus de liberdade. Newey-West com pesos de Bartlett e erro-padrão da média; excesso médio anualizado = média mensal × 12. Bootstrap: blocos consecutivos de 6 meses sorteados com reposição, 10.000 repetições, semente 20261117, intervalo pelos percentis 2,5% e 97,5% da média anualizada. Quantis por interpolação linear; semidesvio = raiz da média de min(x, 0)² sobre todas as ordens.

**Valor p, em uma frase:** se a estratégia na verdade não tivesse vantagem nenhuma, o valor p é a chance de, só por sorte, aparecer um excesso tão grande quanto o que foi medido; quanto menor, mais difícil de ser sorte (costuma-se desconfiar de sorte abaixo de 0,05).

---

### 1. Indicadores usados e omitidos

#### 1.1 O que o estudo anterior já usava e o que omitia

Fonte: leitura do `docs/ESTUDO_KAIRI.md` (Partes 1, 2 e 4) e busca por palavras no texto.

| Indicador | O estudo anterior usava? | Onde / observação |
|---|---|---|
| Média do resultado (%) | Sim | Parte 4: "Resultado (%)" por ano e total; tabelas por carteira |
| Mediana do resultado por ordem | Não | "mediana" só aparece para prazos em pregões (volta ao preço de entrada, saída pela escada) |
| Quantis (5% a 95%) | Não | Só a "média das 10% piores quedas" (−41,6% na A), que é queda dentro da ordem, não resultado da ordem |
| Assimetria e curtose | Não | Não aparecem no texto |
| Desvio padrão | Não | Não aparece no texto |
| Desvio só das perdas (semidesvio) | Não | Há "valorização média dos que saíram com perda" (−22,5% na A), que não é o mesmo |
| Ganhos ÷ perdas em R$ | Não | Havia média dos ganhos e média das perdas em %, não a razão das somas em reais |
| % de ordens positivas | Sim | "Com resultado positivo" (88% na A, 88% na B) |
| Excesso sobre a régua, por ordem | Parcial | "Diferença para a Selic" (média e % que ganharam); agora a régua é 105% do CDI |
| Correlação entre fundos que dão sinal juntos | Não | A única correlação citada (0,21) é entre o resultado de escolha e o de conferência das 72 combinações |
| Episódios independentes | Só em texto | "Dois episódios, não 103 casos independentes" (Parte 1); nunca contados nem testados |
| TIR, Sharpe, Sortino, Calmar, valor p | Não | Não aparecem |

**Leitura prática:** o estudo anterior mostrou a média e a porcentagem de ordens que deram certo, que são os dois números mais animadores. Ficaram de fora justamente os que mostram o lado ruim: a cauda de perdas, a dispersão, a razão entre o que se ganha e o que se perde, e quantas apostas realmente independentes existem.

#### 1.2 Indicadores por ordem, antes do imposto (ordens fechadas)

Cada ordem é medida de duas formas: o resultado antes do imposto e o excesso sobre 105% do CDI (mesmo valor, mesmas datas), ambos antes do imposto.

##### Carteira A — resultado antes do imposto

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 165 | 146 | 311 |
| média (%) | 11,14 | 9,73 | 10,48 |
| mediana (%) | 12,61 | 13,17 | 12,77 |
| quantil 5% (%) | -13,89 | -17,05 | -15,61 |
| quantil 10% (%) | -3,26 | 0,79 | -3,12 |
| quantil 25% (%) | 4,35 | 8,20 | 6,65 |
| quantil 75% (%) | 18,88 | 16,76 | 17,35 |
| quantil 90% (%) | 26,91 | 19,36 | 23,53 |
| quantil 95% (%) | 32,00 | 20,32 | 27,20 |
| assimetria | -1,39 | -3,31 | -2,29 |
| curtose (excesso) | 5,83 | 14,14 | 9,78 |
| desvio padrão (pp) | 14,79 | 14,95 | 14,86 |
| semidesvio das perdas (pp) | 7,91 | 10,95 | 9,46 |
| ganhos ÷ perdas (R$) | 7,28 | 5,86 | 6,56 |
| ordens positivas (%) | 84,85 | 91,10 | 87,78 |

##### Carteira A — excesso sobre 105% do CDI

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 165 | 146 | 311 |
| média (%) | 8,20 | 5,33 | 6,85 |
| mediana (%) | 10,17 | 9,32 | 9,76 |
| quantil 5% (%) | -17,65 | -26,66 | -19,81 |
| quantil 10% (%) | -10,10 | -5,59 | -8,61 |
| quantil 25% (%) | 0,02 | 3,01 | 1,55 |
| quantil 75% (%) | 17,60 | 12,50 | 15,62 |
| quantil 90% (%) | 25,90 | 17,00 | 21,76 |
| quantil 95% (%) | 31,40 | 18,64 | 26,42 |
| assimetria | -1,44 | -3,15 | -2,19 |
| curtose (excesso) | 5,59 | 13,25 | 9,10 |
| desvio padrão (pp) | 16,90 | 16,75 | 16,87 |
| semidesvio das perdas (pp) | 10,31 | 13,45 | 11,89 |
| ganhos ÷ perdas (R$) | 3,78 | 2,91 | 3,37 |
| ordens positivas (%) | 75,15 | 82,19 | 78,46 |

##### Carteira B — resultado antes do imposto

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 97 | 67 | 164 |
| média (%) | 17,12 | 13,53 | 15,65 |
| mediana (%) | 19,88 | 18,06 | 18,44 |
| quantil 5% (%) | -12,89 | -23,45 | -18,62 |
| quantil 10% (%) | -2,89 | -8,44 | -4,59 |
| quantil 25% (%) | 8,00 | 13,12 | 11,20 |
| quantil 75% (%) | 27,00 | 20,74 | 23,57 |
| quantil 90% (%) | 34,56 | 22,97 | 30,31 |
| quantil 95% (%) | 41,31 | 24,96 | 37,51 |
| assimetria | -0,85 | -1,94 | -1,20 |
| curtose (excesso) | 1,42 | 4,75 | 2,62 |
| desvio padrão (pp) | 16,48 | 15,66 | 16,20 |
| semidesvio das perdas (pp) | 6,54 | 9,20 | 7,74 |
| ganhos ÷ perdas (R$) | 11,74 | 6,81 | 9,27 |
| ordens positivas (%) | 88,66 | 86,57 | 87,80 |

##### Carteira B — excesso sobre 105% do CDI

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 97 | 67 | 164 |
| média (%) | 14,52 | 8,70 | 12,14 |
| mediana (%) | 19,00 | 13,30 | 14,68 |
| quantil 5% (%) | -15,55 | -35,00 | -29,32 |
| quantil 10% (%) | -8,79 | -16,22 | -9,83 |
| quantil 25% (%) | 4,72 | 8,38 | 6,99 |
| quantil 75% (%) | 25,72 | 17,41 | 21,85 |
| quantil 90% (%) | 33,59 | 19,50 | 29,92 |
| quantil 95% (%) | 40,68 | 21,51 | 35,96 |
| assimetria | -0,87 | -1,77 | -1,12 |
| curtose (excesso) | 1,30 | 3,67 | 2,14 |
| desvio padrão (pp) | 18,15 | 17,20 | 17,94 |
| semidesvio das perdas (pp) | 8,35 | 11,91 | 9,96 |
| ganhos ÷ perdas (R$) | 7,07 | 3,66 | 5,41 |
| ordens positivas (%) | 79,38 | 86,57 | 82,32 |

##### Carteira C — resultado antes do imposto

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 150 | 117 | 267 |
| média (%) | 11,28 | 11,84 | 11,53 |
| mediana (%) | 12,72 | 14,08 | 13,28 |
| quantil 5% (%) | -14,80 | 1,85 | -11,51 |
| quantil 10% (%) | -3,41 | 5,77 | 0,32 |
| quantil 25% (%) | 5,17 | 10,02 | 7,50 |
| quantil 75% (%) | 18,93 | 16,63 | 17,31 |
| quantil 90% (%) | 26,81 | 19,10 | 23,51 |
| quantil 95% (%) | 32,89 | 19,80 | 27,25 |
| assimetria | -1,45 | -5,22 | -2,40 |
| curtose (excesso) | 5,95 | 37,53 | 12,55 |
| desvio padrão (pp) | 15,10 | 10,99 | 13,44 |
| semidesvio das perdas (pp) | 8,25 | 7,84 | 8,07 |
| ganhos ÷ perdas (R$) | 6,96 | 15,24 | 9,10 |
| ordens positivas (%) | 86,00 | 96,58 | 90,64 |

##### Carteira C — excesso sobre 105% do CDI

| Indicador | Escolha (entradas 2018-2022) | Conferência (entradas 2023-2026) | Total |
|---|---|---|---|
| n | 150 | 117 | 267 |
| média (%) | 8,34 | 7,61 | 8,02 |
| mediana (%) | 10,20 | 9,98 | 10,07 |
| quantil 5% (%) | -18,97 | -6,15 | -14,16 |
| quantil 10% (%) | -8,92 | -1,03 | -6,32 |
| quantil 25% (%) | 0,40 | 5,55 | 3,41 |
| quantil 75% (%) | 18,01 | 12,63 | 15,62 |
| quantil 90% (%) | 25,95 | 16,80 | 22,07 |
| quantil 95% (%) | 32,07 | 17,88 | 26,43 |
| assimetria | -1,51 | -4,76 | -2,33 |
| curtose (excesso) | 5,79 | 32,43 | 11,73 |
| desvio padrão (pp) | 17,22 | 12,81 | 15,42 |
| semidesvio das perdas (pp) | 10,65 | 9,87 | 10,32 |
| ganhos ÷ perdas (R$) | 3,76 | 6,48 | 4,49 |
| ordens positivas (%) | 76,67 | 88,89 | 82,02 |

**Legenda (vale para as seis tabelas):**

- *n*: ordens fechadas do período (unidades).
- *média, mediana, quantil k%*: em % da ordem (resultado) ou em pontos percentuais (excesso). Quantil k% = valor abaixo do qual ficam k% das ordens (interpolação linear). Mediana = quantil 50%.
- *assimetria*: terceiro momento padronizado (sem unidade); negativa = cauda longa de perdas.
- *curtose (excesso)*: quarto momento padronizado menos 3 (sem unidade); positiva = caudas mais pesadas que a normal.
- *desvio padrão*: raiz da variância amostral (n−1), em pontos percentuais.
- *semidesvio das perdas*: raiz da média de min(x; 0)² sobre todas as ordens, em pontos percentuais.
- *ganhos ÷ perdas (R$)*: soma dos reais das ordens positivas dividida pela soma, em módulo, dos reais das ordens negativas (sem unidade). Para o excesso, os reais são resultado − valor × rendimento do CDI.
- *ordens positivas*: % de ordens com resultado (ou excesso) maior que zero.

**Leitura prática:** nas três carteiras a mediana é maior que a média e a assimetria é negativa: a maioria das ordens ganha bem, mas existe uma cauda de perdas grandes que puxa a média para baixo. No total, a A tem média de 10,5% e mediana de 12,8% por ordem (excesso: 6,9 e 9,8 pontos); a B, 15,7% e 18,4% (excesso 12,1 e 14,7); a C, 11,5% e 13,3% (excesso 8,0 e 10,1). A pior vigésima parte das ordens da A perde 15,6% ou mais do dinheiro (19,8 pontos abaixo do CDI). Entre escolha e conferência a média cai na A e na B (excesso de 8,2 para 5,3 pontos na A; de 14,5 para 8,7 na B) e fica parecida na C.

#### 1.3 Correlação entre fundos que dão sinal juntos

| Carteira | Período | Agrupamento | Grupos | Grupos com 2+ fundos | Grupos com correlação calculada | Mediana (com sinal) | q5% | q25% | q75% | q95% | Mediana (pares sorteados) | q25% sorteio | q75% sorteio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | mesma data de sinal | 95 | 19 | 18 | 0,19 | -0,16 | 0,00 | 0,33 | 0,52 | 0,10 | 0,03 | 0,19 |
| A | Escolha (entradas 2018-2022) | sinais em até 5 pregões | 47 | 23 | 21 | 0,07 | -0,05 | 0,03 | 0,13 | 0,24 | 0,10 | 0,05 | 0,12 |
| A | Conferência (entradas 2023-2026) | mesma data de sinal | 109 | 21 | 18 | 0,22 | -0,03 | 0,10 | 0,31 | 0,40 | 0,14 | 0,10 | 0,16 |
| A | Conferência (entradas 2023-2026) | sinais em até 5 pregões | 57 | 27 | 22 | 0,18 | -0,09 | 0,06 | 0,25 | 0,30 | 0,14 | 0,11 | 0,17 |
| A | Total | mesma data de sinal | 204 | 40 | 36 | 0,21 | -0,16 | 0,06 | 0,33 | 0,51 | 0,16 | 0,10 | 0,18 |
| A | Total | sinais em até 5 pregões | 104 | 50 | 43 | 0,11 | -0,09 | 0,04 | 0,23 | 0,30 | 0,12 | 0,08 | 0,17 |
| B | Escolha (entradas 2018-2022) | mesma data de sinal | 44 | 8 | 8 | 0,24 | -0,04 | 0,12 | 0,27 | 0,33 | 0,11 | 0,04 | 0,25 |
| B | Escolha (entradas 2018-2022) | sinais em até 5 pregões | 27 | 9 | 9 | 0,11 | -0,14 | 0,09 | 0,26 | 0,34 | 0,14 | 0,12 | 0,23 |
| B | Conferência (entradas 2023-2026) | mesma data de sinal | 50 | 13 | 11 | 0,19 | 0,04 | 0,12 | 0,27 | 0,34 | 0,16 | 0,15 | 0,19 |
| B | Conferência (entradas 2023-2026) | sinais em até 5 pregões | 30 | 13 | 12 | 0,15 | -0,18 | -0,02 | 0,22 | 0,27 | 0,16 | 0,11 | 0,20 |
| B | Total | mesma data de sinal | 94 | 21 | 19 | 0,21 | -0,00 | 0,12 | 0,28 | 0,36 | 0,16 | 0,13 | 0,22 |
| B | Total | sinais em até 5 pregões | 57 | 22 | 21 | 0,12 | -0,22 | -0,01 | 0,22 | 0,32 | 0,11 | 0,08 | 0,23 |
| C | Escolha (entradas 2018-2022) | mesma data de sinal | 80 | 19 | 18 | 0,19 | -0,10 | 0,02 | 0,33 | 0,52 | 0,13 | 0,05 | 0,23 |
| C | Escolha (entradas 2018-2022) | sinais em até 5 pregões | 33 | 22 | 20 | 0,07 | -0,05 | 0,02 | 0,12 | 0,25 | 0,12 | 0,10 | 0,12 |
| C | Conferência (entradas 2023-2026) | mesma data de sinal | 72 | 22 | 20 | 0,23 | -0,01 | 0,11 | 0,29 | 0,36 | 0,14 | 0,10 | 0,17 |
| C | Conferência (entradas 2023-2026) | sinais em até 5 pregões | 30 | 21 | 17 | 0,22 | -0,06 | 0,09 | 0,28 | 0,32 | 0,15 | 0,10 | 0,18 |
| C | Total | mesma data de sinal | 152 | 41 | 38 | 0,22 | -0,09 | 0,07 | 0,31 | 0,51 | 0,15 | 0,11 | 0,19 |
| C | Total | sinais em até 5 pregões | 63 | 43 | 37 | 0,11 | -0,06 | 0,05 | 0,22 | 0,30 | 0,12 | 0,09 | 0,14 |

**Legenda:**

- *Grupos*: grupos de ordens da carteira e do período com a mesma data de sinal (ou sinais em até 5 pregões a partir do primeiro do grupo); *Grupos com 2+ fundos*: os que têm pelo menos dois fundos diferentes; *Grupos com correlação calculada*: os que tiveram ao menos um par com 20 ou mais pregões abertos juntos (unidades).
- *Mediana (com sinal), q5%, q25%, q75%, q95%*: distribuição, entre os grupos, da correlação média par a par dos retornos diários de fechamento enquanto as ordens estavam abertas juntas (de −1 a +1).
- *Mediana (pares sorteados), q25%, q75% sorteio*: o mesmo, mas com pares de fundos sorteados no mesmo intervalo, sem sinal (média por grupo de 5 pares sorteados para cada par real).

**Leitura prática:** os fundos que dão sinal no mesmo dia andam um pouco mais juntos que fundos sorteados (mediana de 0,21 a 0,22 contra 0,15 a 0,16 no total); quando se agrupa por janela de 5 pregões, a diferença desaparece (0,11 a 0,12 contra 0,11 a 0,12). A correlação em si é baixa; o que torna as ordens dependentes é o fato de entrarem na mesma época (a queda do mercado inteiro), e isso aparece melhor na contagem de episódios abaixo. Só 40 das 204 datas de sinal da A tiveram dois fundos ou mais; mas as ordens se empilham em poucas semanas.

#### 1.4 Episódios independentes

| Janela W (pregões) | Carteira | Período | Ordens | Episódios | Ordens por episódio (média) | Maior episódio (ordens) | Episódios com ordem fechada | Soma do resultado antes do imposto (R$) | % médio por episódio (média) | % médio por episódio (mediana) | Episódios com soma > 0 | Excesso médio por episódio (pp) | Parte da soma nos 3 maiores episódios |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | A | Escolha (entradas 2018-2022) | 165 | 23 | 7,2 | 63 | 23 | 53.509,19 | 8,2% | 12,3% | 83% | 5,0 pp | 91% |
| 10 | A | Conferência (entradas 2023-2026) | 176 | 24 | 7,3 | 92 | 23 | 42.430,76 | 6,3% | 8,7% | 83% | 2,3 pp | 86% |
| 10 | A | Total | 341 | 46 | 7,4 | 92 | 45 | 95.939,95 | 7,5% | 9,3% | 82% | 4,0 pp | 79% |
| 10 | B | Escolha (entradas 2018-2022) | 97 | 20 | 4,8 | 53 | 20 | 48.849,24 | 8,3% | 10,1% | 80% | 4,9 pp | 92% |
| 10 | B | Conferência (entradas 2023-2026) | 78 | 19 | 4,1 | 46 | 14 | 26.505,52 | 4,6% | 8,5% | 71% | -0,3 pp | 98% |
| 10 | B | Total | 175 | 39 | 4,5 | 53 | 34 | 75.354,76 | 6,8% | 10,1% | 76% | 2,7 pp | 91% |
| 10 | C | Escolha (entradas 2018-2022) | 150 | 15 | 10,0 | 63 | 15 | 49.321,55 | 3,8% | 9,2% | 73% | -0,2 pp | 98% |
| 10 | C | Conferência (entradas 2023-2026) | 142 | 8 | 17,8 | 93 | 7 | 40.921,89 | 13,6% | 14,2% | 100% | 10,5 pp | 93% |
| 10 | C | Total | 292 | 23 | 12,7 | 93 | 22 | 90.243,44 | 6,9% | 11,6% | 82% | 3,2 pp | 84% |
| 20 | A | Escolha (entradas 2018-2022) | 165 | 14 | 11,8 | 65 | 14 | 53.509,19 | 10,7% | 11,3% | 86% | 7,6 pp | 95% |
| 20 | A | Conferência (entradas 2023-2026) | 176 | 11 | 16,0 | 95 | 11 | 42.430,76 | 9,1% | 9,3% | 82% | 4,9 pp | 94% |
| 20 | A | Total | 341 | 24 | 14,2 | 95 | 24 | 95.939,95 | 10,6% | 9,2% | 88% | 7,2 pp | 81% |
| 20 | B | Escolha (entradas 2018-2022) | 97 | 16 | 6,1 | 53 | 16 | 48.849,24 | 8,4% | 11,6% | 81% | 4,9 pp | 94% |
| 20 | B | Conferência (entradas 2023-2026) | 78 | 14 | 5,6 | 54 | 11 | 26.505,52 | 4,7% | 10,5% | 64% | 0,0 pp | 102% |
| 20 | B | Total | 175 | 30 | 5,8 | 54 | 27 | 75.354,76 | 6,9% | 10,5% | 74% | 2,9 pp | 92% |
| 20 | C | Escolha (entradas 2018-2022) | 150 | 10 | 15,0 | 63 | 10 | 49.321,55 | 5,8% | 7,5% | 70% | 2,0 pp | 102% |
| 20 | C | Conferência (entradas 2023-2026) | 142 | 3 | 47,3 | 95 | 3 | 40.921,89 | 14,5% | 16,1% | 100% | 11,4 pp | 100% |
| 20 | C | Total | 292 | 12 | 24,3 | 95 | 12 | 90.243,44 | 9,3% | 10,1% | 83% | 6,0 pp | 86% |
| 40 | A | Escolha (entradas 2018-2022) | 165 | 7 | 23,6 | 74 | 7 | 53.509,19 | 8,5% | 9,4% | 86% | 5,1 pp | 100% |
| 40 | A | Conferência (entradas 2023-2026) | 176 | 6 | 29,3 | 103 | 6 | 42.430,76 | 12,3% | 9,3% | 100% | 8,5 pp | 91% |
| 40 | A | Total | 341 | 12 | 28,4 | 103 | 12 | 95.939,95 | 11,6% | 9,2% | 100% | 8,3 pp | 82% |
| 40 | B | Escolha (entradas 2018-2022) | 97 | 11 | 8,8 | 54 | 11 | 48.849,24 | 11,0% | 13,1% | 91% | 7,6 pp | 92% |
| 40 | B | Conferência (entradas 2023-2026) | 78 | 8 | 9,8 | 55 | 8 | 26.505,52 | 7,9% | 12,5% | 62% | 4,5 pp | 104% |
| 40 | B | Total | 175 | 19 | 9,2 | 55 | 19 | 75.354,76 | 9,7% | 13,1% | 79% | 6,3 pp | 92% |
| 40 | C | Escolha (entradas 2018-2022) | 150 | 5 | 30,0 | 67 | 5 | 49.321,55 | 3,9% | 7,1% | 80% | 0,3 pp | 104% |
| 40 | C | Conferência (entradas 2023-2026) | 142 | 3 | 47,3 | 95 | 3 | 40.921,89 | 14,5% | 16,1% | 100% | 11,4 pp | 100% |
| 40 | C | Total | 292 | 7 | 41,7 | 95 | 7 | 90.243,44 | 10,5% | 10,8% | 100% | 7,7 pp | 86% |

**Legenda:**

- *Janela W*: número máximo de pregões entre uma entrada e a anterior para continuarem no mesmo episódio (pregões).
- *Ordens*: total de ordens da carteira no período, incluindo as em aberto (unidades). *Episódios*: cadeias de ordens (unidades). *Ordens por episódio*: Ordens ÷ Episódios. *Maior episódio*: maior número de ordens num episódio.
- *Episódios com ordem fechada*: os que entram nas colunas de resultado.
- *Soma do resultado antes do imposto*: soma, em R$, do resultado das ordens fechadas de todos os episódios (valorização + rendimentos − taxas).
- *% médio por episódio*: para cada episódio, a média simples do resultado % das suas ordens fechadas; depois média e mediana entre episódios.
- *Episódios com soma > 0*: % de episódios em que a soma em R$ das ordens é positiva.
- *Excesso médio por episódio*: média entre episódios do excesso médio sobre 105% do CDI, em pontos percentuais.
- *Parte da soma nos 3 maiores episódios*: soma em R$ dos três maiores episódios ÷ soma total (pode passar de 100% quando outros episódios têm perda).

**Leitura prática:** as 341 ordens da A viram 46, 24 ou 12 episódios independentes, conforme a janela seja de 10, 20 ou 40 pregões; as 175 da B viram 39, 30 ou 19; as 292 da C, 23, 12 ou 7. Os três maiores episódios respondem por cerca de 80% a 90% do dinheiro ganho (com a janela de 20 pregões: A 81%, B 92%, C 86%). Há muito mais ordens que apostas realmente separadas.

---

### 2. Taxa interna de retorno

#### 2.1 Fluxos das ordens contra o espelho em 105% do CDI (itens 2a e 2b)

| Carteira | Período | Base | Ordens | Investido (compras + taxa) | Rendimentos (na data de pagamento) | Vendas líquidas de taxa | Imposto do FII (mensal, com abatimento) | Imposto + IOF do espelho | TIR das ordens | TIR do espelho 105% CDI | Diferença |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | todas as ordens (em aberto a mercado, sem imposto) | 165 | R$ 464.715 | R$ 14.889 | R$ 503.336 | R$ 8.738 | R$ 2.786 | 30,2% | 5,4% | 24,8 pp |
| A | Escolha (entradas 2018-2022) | só ordens fechadas | 165 | R$ 464.715 | R$ 14.889 | R$ 503.336 | R$ 8.738 | R$ 2.786 | 30,2% | 5,4% | 24,8 pp |
| A | Conferência (entradas 2023-2026) | todas as ordens (em aberto a mercado, sem imposto) | 176 | R$ 498.433 | R$ 17.390 | R$ 522.067 | R$ 5.309 | R$ 4.307 | 27,7% | 10,4% | 17,3 pp |
| A | Conferência (entradas 2023-2026) | só ordens fechadas | 146 | R$ 411.267 | R$ 15.886 | R$ 437.812 | R$ 5.309 | R$ 3.891 | 30,2% | 10,4% | 19,8 pp |
| A | Total | todas as ordens (em aberto a mercado, sem imposto) | 341 | R$ 963.148 | R$ 32.279 | R$ 1.025.403 | R$ 13.033 | R$ 7.093 | 29,8% | 7,2% | 22,7 pp |
| A | Total | só ordens fechadas | 311 | R$ 875.982 | R$ 30.774 | R$ 941.148 | R$ 13.033 | R$ 6.677 | 30,4% | 7,1% | 23,3 pp |
| B | Escolha (entradas 2018-2022) | todas as ordens (em aberto a mercado, sem imposto) | 97 | R$ 277.231 | R$ 8.669 | R$ 317.412 | R$ 8.269 | R$ 1.451 | 42,1% | 4,5% | 37,6 pp |
| B | Escolha (entradas 2018-2022) | só ordens fechadas | 97 | R$ 277.231 | R$ 8.669 | R$ 317.412 | R$ 8.269 | R$ 1.451 | 42,1% | 4,5% | 37,6 pp |
| B | Conferência (entradas 2023-2026) | todas as ordens (em aberto a mercado, sem imposto) | 78 | R$ 220.492 | R$ 9.300 | R$ 236.296 | R$ 3.760 | R$ 2.115 | 32,7% | 10,5% | 22,1 pp |
| B | Conferência (entradas 2023-2026) | só ordens fechadas | 67 | R$ 189.078 | R$ 8.724 | R$ 206.860 | R$ 3.760 | R$ 1.953 | 35,5% | 10,5% | 25,0 pp |
| B | Total | todas as ordens (em aberto a mercado, sem imposto) | 175 | R$ 497.723 | R$ 17.968 | R$ 553.708 | R$ 11.796 | R$ 3.566 | 40,8% | 6,3% | 34,5 pp |
| B | Total | só ordens fechadas | 164 | R$ 466.309 | R$ 17.392 | R$ 524.272 | R$ 11.796 | R$ 3.405 | 41,3% | 6,3% | 35,0 pp |
| C | Escolha (entradas 2018-2022) | todas as ordens (em aberto a mercado, sem imposto) | 150 | R$ 426.956 | R$ 13.555 | R$ 462.722 | R$ 8.259 | R$ 2.573 | 30,4% | 5,3% | 25,1 pp |
| C | Escolha (entradas 2018-2022) | só ordens fechadas | 150 | R$ 426.956 | R$ 13.555 | R$ 462.722 | R$ 8.259 | R$ 2.573 | 30,4% | 5,3% | 25,1 pp |
| C | Conferência (entradas 2023-2026) | todas as ordens (em aberto a mercado, sem imposto) | 142 | R$ 407.461 | R$ 13.954 | R$ 435.035 | R$ 5.567 | R$ 3.286 | 38,6% | 10,4% | 28,2 pp |
| C | Conferência (entradas 2023-2026) | só ordens fechadas | 117 | R$ 334.143 | R$ 13.087 | R$ 361.978 | R$ 5.567 | R$ 3.054 | 39,7% | 10,5% | 29,2 pp |
| C | Total | todas as ordens (em aberto a mercado, sem imposto) | 292 | R$ 834.417 | R$ 27.509 | R$ 897.757 | R$ 12.720 | R$ 5.859 | 32,2% | 6,9% | 25,2 pp |
| C | Total | só ordens fechadas | 267 | R$ 761.099 | R$ 26.642 | R$ 824.701 | R$ 12.720 | R$ 5.628 | 32,3% | 6,9% | 25,4 pp |

**Legenda:**

- *Ordens*: ordens do subconjunto (unidades). *Base*: "todas" inclui as ordens em aberto vendidas a 09/11/2026 sem imposto; "só fechadas" as exclui.
- *Investido*: soma de valor da ordem + taxa de compra (R$). *Rendimentos*: soma dos rendimentos pelas datas de pagamento (R$). *Vendas líquidas*: venda − taxa de venda (R$).
- *Imposto do FII*: 20% do ganho mensal líquido, com abatimento de prejuízo (R$). *Imposto + IOF do espelho*: IR regressivo e IOF pagos no espelho (R$).
- *TIR*: taxa anual (base 365 dias, datas reais) que zera o valor presente dos fluxos: −compra na entrada, +rendimentos na data de pagamento, +venda na saída, −imposto do FII no último dia útil do mês seguinte à venda. *TIR do espelho*: a mesma conta com os mesmos valores aplicados em 105% do CDI entre a entrada e a saída de cada ordem. *Diferença*: TIR das ordens − TIR do espelho, em pontos percentuais.

**Leitura prática:** enquanto o dinheiro está dentro das ordens (cerca de 140 dias em média), ele rende bem mais que 105% do CDI: no total, 29,8% ao ano contra 7,2% na A, 40,8% contra 6,3% na B e 32,2% contra 6,9% na C. É um retorno do dinheiro enquanto aplicado, não da carteira inteira: o dinheiro fica parado entre uma ordem e outra (item 2c). A TIR das ordens da conferência é menor que a da escolha na A (27,7% contra 30,2%) e na B (32,7% contra 42,1%), e maior na C (38,6% contra 30,4%).

#### 2.2 Carteira com o dinheiro do pico (item 2c)

| Carteira | Dinheiro no início (pico) | Ordens em aberto a mercado | Saldo líquido de IR e IOF | Rendimentos declarados a receber | DARF a pagar | Valor final da carteira | Valor final, tudo em 105% CDI | Retorno ao ano da carteira (TIR) | Retorno ao ano, tudo em 105% CDI | Diferença | Diferença (R$) | Eventos de falta de caixa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | R$ 262.698 | R$ 84.255 | R$ 535.286 | R$ 334 | R$ -432 | R$ 619.443 | R$ 545.854 | 10,2% | 8,6% | 1,6 pp | R$ 73.590 | 0 |
| B | R$ 151.506 | R$ 29.436 | R$ 356.693 | R$ 111 | R$ -0 | R$ 386.241 | R$ 314.810 | 11,1% | 8,6% | 2,5 pp | R$ 71.430 | 0 |
| C | R$ 255.116 | R$ 73.057 | R$ 531.807 | R$ 245 | R$ -162 | R$ 604.946 | R$ 530.099 | 10,2% | 8,6% | 1,6 pp | R$ 74.847 | 0 |

**Legenda:**

- *Dinheiro no início*: maior valor aplicado ao mesmo tempo nas ordens, depositado em 02/01/2018 (R$).
- *Ordens em aberto a mercado*: cotas × último fechamento − taxa de venda de 0,03% (R$). *Saldo líquido*: saldo em 105% do CDI depois de IR regressivo e IOF por lote, como se resgatado em 09/11/2026 (R$). *Rendimentos a receber*: avisos declarados, com pagamento depois de 09/11/2026 (R$). *DARF a pagar*: imposto do FII já devido e ainda não pago (R$, negativo).
- *Valor final da carteira* = soma das quatro colunas anteriores (R$). *Valor final, tudo em 105% CDI* = dinheiro inicial × (índice final ÷ índice inicial), com IR de 15% (R$).
- *Retorno ao ano*: (valor final ÷ dinheiro inicial)^(365 ÷ 3.233 dias) − 1; como há um único depósito e um único valor final, é igual à TIR. *Diferença*: pontos percentuais e R$.
- *Eventos de falta de caixa*: vezes em que o saldo não cobriu uma compra (unidades).

**Leitura prática:** com o dinheiro do pico parado no CDI entre uma ordem e outra, a carteira A termina com R$ 619.443 contra R$ 545.854 de quem deixou tudo no CDI (R$ 73.590 a mais; 10,2% contra 8,6% ao ano). B: R$ 386.241 contra R$ 314.810 (R$ 71.430 a mais; 11,1% contra 8,6%). C: R$ 604.946 contra R$ 530.099 (R$ 74.847 a mais; 10,2% contra 8,6%). O ganho sobre o CDI é de 1,6 a 2,5 pontos ao ano, bem menor que os 22 a 35 pontos da TIR das ordens, porque o dinheiro passa a maior parte do tempo parado.

#### 2.3 Sharpe, Sortino e Calmar (item 2d)

| Carteira | Série | Retorno ao ano | Desvio dos retornos mensais | Excesso mensal médio | Sharpe | Sortino | Calmar | Maior queda do patrimônio | Período da maior queda (do pico ao fundo) |
|---|---|---|---|---|---|---|---|---|---|
| A | Carteira do pico | 10,2% | 0,92% | 0,123 pp | 0,48 | 1,26 | 3,73 | -2,7% | 13/03/2020 a 23/03/2020 |
| A | Espelho: tudo em 105% CDI | 8,6% | 0,33% | 0 por construção | n/d | n/d | n/d (sem queda) | 0,0% | - |
| B | Carteira do pico | 11,1% | 1,36% | 0,201 pp | 0,51 | 2,25 | 3,18 | -3,5% | 20/03/2020 a 23/03/2020 |
| B | Espelho: tudo em 105% CDI | 8,6% | 0,33% | 0 por construção | n/d | n/d | n/d (sem queda) | 0,0% | - |
| C | Carteira do pico | 10,2% | 0,95% | 0,128 pp | 0,48 | 1,33 | 3,75 | -2,7% | 20/03/2020 a 23/03/2020 |
| C | Espelho: tudo em 105% CDI | 8,6% | 0,33% | 0 por construção | n/d | n/d | n/d (sem queda) | 0,0% | - |

**Legenda:**

- *Retorno ao ano*: do patrimônio líquido, de 02/01/2018 a 09/11/2026. *Desvio dos retornos mensais*: desvio padrão (n−1) dos retornos do patrimônio de cada mês.
- *Excesso mensal médio*: média de (retorno do mês − retorno do mês do espelho 105% CDI líquido), em pontos percentuais.
- *Sharpe* = média do excesso mensal ÷ desvio do excesso × √12. *Sortino* = média do excesso ÷ semidesvio negativo do excesso × √12 (semidesvio = raiz da média de min(excesso; 0)² sobre todos os meses). *Calmar* = retorno ao ano ÷ módulo da maior queda.
- *Maior queda*: maior baixa do patrimônio líquido diário, do pico ao fundo (%); datas do pico e do fundo.
- Para o espelho, o excesso é zero por construção; Sharpe, Sortino e Calmar não existem (divisão por zero), e o espelho nunca cai (queda zero).

**Leitura prática:** a carteira do pico quase não oscila, porque a maior parte do patrimônio fica no CDI: a pior queda foi de 2,7% (A e C) e 3,5% (B), todas em março de 2020. Em retorno por risco, o Sharpe fica perto de 0,5 nas três e o Sortino (que só penaliza os meses ruins) entre 1,3 e 2,3, com Calmar entre 3,2 e 3,8. Esses números são bons porque o patrimônio é quase todo renda fixa; não dizem que cada ordem é segura.

---

### 3. Significância do excesso sobre 105% do CDI

Duas medidas diferentes, não comparáveis entre si: o excesso por ordem (em pontos percentuais da ordem, antes do imposto) e o excesso mensal da carteira do pico (em pontos ao ano sobre todo o patrimônio, líquido de imposto).

#### 3.1 Por ordem (ingênuo) e por episódio independente

**Por ordem, ingênuo (trata as ordens como independentes)**

| Carteira | Período | n | Média do excesso (pp) | t | Valor p | IC 95% (pp) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 165 | 8,20 | 6,23 | 0,0000 | 5,60 a 10,80 |
| A | Conferência (entradas 2023-2026) | 146 | 5,33 | 3,84 | 0,0002 | 2,59 a 8,07 |
| A | Total | 311 | 6,85 | 7,16 | 0,0000 | 4,97 a 8,73 |
| B | Escolha (entradas 2018-2022) | 97 | 14,52 | 7,88 | 0,0000 | 10,86 a 18,17 |
| B | Conferência (entradas 2023-2026) | 67 | 8,70 | 4,14 | 0,0001 | 4,51 a 12,90 |
| B | Total | 164 | 12,14 | 8,66 | 0,0000 | 9,37 a 14,91 |
| C | Escolha (entradas 2018-2022) | 150 | 8,34 | 5,94 | 0,0000 | 5,57 a 11,12 |
| C | Conferência (entradas 2023-2026) | 117 | 7,61 | 6,42 | 0,0000 | 5,26 a 9,95 |
| C | Total | 267 | 8,02 | 8,50 | 0,0000 | 6,16 a 9,88 |

**Por episódio independente, janela de 20 pregões**

| Carteira | Período | n | Média do excesso (pp) | t | Valor p | IC 95% (pp) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 14 | 7,62 | 2,04 | 0,0625 | -0,46 a 15,70 |
| A | Conferência (entradas 2023-2026) | 11 | 4,86 | 1,31 | 0,2180 | -3,37 a 13,09 |
| A | Total | 24 | 7,19 | 2,90 | 0,0081 | 2,06 a 12,32 |
| B | Escolha (entradas 2018-2022) | 16 | 4,95 | 1,13 | 0,2771 | -4,40 a 14,30 |
| B | Conferência (entradas 2023-2026) | 11 | 0,03 | 0,00 | 0,9972 | -19,55 a 19,62 |
| B | Total | 27 | 2,95 | 0,68 | 0,5042 | -5,99 a 11,89 |
| C | Escolha (entradas 2018-2022) | 10 | 1,96 | 0,41 | 0,6922 | -8,87 a 12,78 |
| C | Conferência (entradas 2023-2026) | 3 | 11,42 | 4,27 | 0,0506 | -0,08 a 22,93 |
| C | Total | 12 | 5,97 | 1,98 | 0,0727 | -0,65 a 12,59 |

**Sensibilidade: janela de 10 pregões**

| Carteira | Período | n | Média do excesso (pp) | t | Valor p | IC 95% (pp) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 23 | 4,99 | 1,43 | 0,1669 | -2,25 a 12,24 |
| A | Conferência (entradas 2023-2026) | 23 | 2,29 | 0,61 | 0,5512 | -5,56 a 10,14 |
| A | Total | 45 | 3,96 | 1,54 | 0,1309 | -1,22 a 9,14 |
| B | Escolha (entradas 2018-2022) | 20 | 4,89 | 1,13 | 0,2744 | -4,21 a 13,99 |
| B | Conferência (entradas 2023-2026) | 14 | -0,33 | -0,04 | 0,9657 | -16,55 a 15,89 |
| B | Total | 34 | 2,74 | 0,69 | 0,4942 | -5,33 a 10,82 |
| C | Escolha (entradas 2018-2022) | 15 | -0,20 | -0,04 | 0,9652 | -9,95 a 9,55 |
| C | Conferência (entradas 2023-2026) | 7 | 10,48 | 7,20 | 0,0004 | 6,92 a 14,04 |
| C | Total | 22 | 3,20 | 0,97 | 0,3410 | -3,63 a 10,02 |

**Sensibilidade: janela de 40 pregões**

| Carteira | Período | n | Média do excesso (pp) | t | Valor p | IC 95% (pp) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 7 | 5,09 | 0,95 | 0,3782 | -8,00 a 18,19 |
| A | Conferência (entradas 2023-2026) | 6 | 8,54 | 1,76 | 0,1390 | -3,94 a 21,03 |
| A | Total | 12 | 8,28 | 2,72 | 0,0200 | 1,57 a 14,99 |
| B | Escolha (entradas 2018-2022) | 11 | 7,59 | 1,61 | 0,1381 | -2,90 a 18,07 |
| B | Conferência (entradas 2023-2026) | 8 | 4,52 | 0,44 | 0,6765 | -20,04 a 29,08 |
| B | Total | 19 | 6,29 | 1,26 | 0,2234 | -4,19 a 16,78 |
| C | Escolha (entradas 2018-2022) | 5 | 0,32 | 0,04 | 0,9686 | -20,76 a 21,40 |
| C | Conferência (entradas 2023-2026) | 3 | 11,42 | 4,27 | 0,0506 | -0,08 a 22,93 |
| C | Total | 7 | 7,66 | 3,05 | 0,0224 | 1,52 a 13,80 |

**Legenda (as quatro tabelas):**

- *n*: ordens fechadas (ingênuo) ou episódios com ordem fechada (por episódio).
- *Média do excesso*: em pontos percentuais da ordem; no teste por episódio, média entre episódios do excesso médio de cada um.
- *t* = média ÷ (desvio ÷ √n). *Valor p*: duas caudas, distribuição t com n−1 graus de liberdade (0,0000 = menor que 0,00005). *IC 95%*: média ± t crítico × erro-padrão (pontos percentuais).

**Leitura prática:** contando cada ordem como uma aposta independente, todos os testes parecem decisivos (t de 6 a 9, valor p praticamente zero). Contando episódios, o quadro muda: na A, com janela de 20 pregões, o excesso médio por episódio é de 7,2 pontos e continua significativo (p = 0,008; intervalo de 2,1 a 12,3), mas com janela de 10 pregões deixa de ser (p = 0,13) e com 40 volta a ser (p = 0,02); na B nenhum recorte por episódio é significativo (p entre 0,22 e 0,50); na C, p = 0,34, 0,07 e 0,02 para as janelas de 10, 20 e 40 pregões. Na conferência (2023 a 2026) quase nada é significativo por episódio (a exceção é a C, com só 3 a 7 episódios). O resultado depende de como se define "episódio", o que já indica fragilidade.

#### 3.2 Excesso mensal da carteira do pico: Newey-West e bootstrap

**Newey-West, 6 defasagens (principal)**

| Carteira | Período | Meses | Excesso médio (pp/ano) | t | Valor p | IC 95% (pp/ano) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 60 | 2,29 | 1,47 | 0,1482 | -0,84 a 5,41 |
| A | Conferência (entradas 2023-2026) | 47 | 0,43 | 0,53 | 0,6003 | -1,21 a 2,08 |
| A | Total | 107 | 1,47 | 1,51 | 0,1340 | -0,46 a 3,40 |
| B | Escolha (entradas 2018-2022) | 60 | 3,68 | 1,22 | 0,2254 | -2,33 a 9,69 |
| B | Conferência (entradas 2023-2026) | 47 | 0,79 | 0,67 | 0,5081 | -1,59 a 3,17 |
| B | Total | 107 | 2,41 | 1,34 | 0,1841 | -1,16 a 5,98 |
| C | Escolha (entradas 2018-2022) | 60 | 2,21 | 1,37 | 0,1774 | -1,03 a 5,45 |
| C | Conferência (entradas 2023-2026) | 47 | 0,68 | 0,84 | 0,4078 | -0,96 a 2,31 |
| C | Total | 107 | 1,54 | 1,55 | 0,1253 | -0,44 a 3,51 |

**Newey-West, 3 defasagens**

| Carteira | Período | Meses | Excesso médio (pp/ano) | t | Valor p | IC 95% (pp/ano) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 60 | 2,29 | 1,45 | 0,1532 | -0,88 a 5,45 |
| A | Conferência (entradas 2023-2026) | 47 | 0,43 | 0,49 | 0,6290 | -1,35 a 2,22 |
| A | Total | 107 | 1,47 | 1,49 | 0,1379 | -0,48 a 3,42 |
| B | Escolha (entradas 2018-2022) | 60 | 3,68 | 1,25 | 0,2178 | -2,23 a 9,59 |
| B | Conferência (entradas 2023-2026) | 47 | 0,79 | 0,70 | 0,4873 | -1,48 a 3,05 |
| B | Total | 107 | 2,41 | 1,38 | 0,1718 | -1,06 a 5,88 |
| C | Escolha (entradas 2018-2022) | 60 | 2,21 | 1,34 | 0,1845 | -1,08 a 5,51 |
| C | Conferência (entradas 2023-2026) | 47 | 0,68 | 0,78 | 0,4416 | -1,08 a 2,44 |
| C | Total | 107 | 1,54 | 1,52 | 0,1313 | -0,47 a 3,54 |

**Newey-West, 12 defasagens**

| Carteira | Período | Meses | Excesso médio (pp/ano) | t | Valor p | IC 95% (pp/ano) |
|---|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 60 | 2,29 | 1,59 | 0,1163 | -0,58 a 5,16 |
| A | Conferência (entradas 2023-2026) | 47 | 0,43 | 0,62 | 0,5354 | -0,96 a 1,82 |
| A | Total | 107 | 1,47 | 1,60 | 0,1134 | -0,36 a 3,30 |
| B | Escolha (entradas 2018-2022) | 60 | 3,68 | 1,31 | 0,1940 | -1,92 a 9,28 |
| B | Conferência (entradas 2023-2026) | 47 | 0,79 | 0,69 | 0,4943 | -1,51 a 3,09 |
| B | Total | 107 | 2,41 | 1,39 | 0,1669 | -1,02 a 5,84 |
| C | Escolha (entradas 2018-2022) | 60 | 2,21 | 1,52 | 0,1339 | -0,70 a 5,12 |
| C | Conferência (entradas 2023-2026) | 47 | 0,68 | 0,99 | 0,3264 | -0,70 a 2,06 |
| C | Total | 107 | 1,54 | 1,68 | 0,0958 | -0,28 a 3,35 |

**Bootstrap em blocos de 6 meses, 10.000 repetições**

| Carteira | Período | Meses | Excesso médio (pp/ano) | IC 95% (pp/ano) | % das repetições com média <= 0 |
|---|---|---|---|---|---|
| A | Escolha (entradas 2018-2022) | 60 | 2,29 | -0,15 a 6,05 | 3,73% |
| A | Conferência (entradas 2023-2026) | 47 | 0,43 | -0,82 a 2,50 | 30,24% |
| A | Total | 107 | 1,47 | -0,13 a 3,80 | 4,10% |
| B | Escolha (entradas 2018-2022) | 60 | 3,68 | -0,42 a 11,02 | 6,27% |
| B | Conferência (entradas 2023-2026) | 47 | 0,79 | -0,88 a 3,71 | 23,94% |
| B | Total | 107 | 2,41 | -0,18 a 6,79 | 4,35% |
| C | Escolha (entradas 2018-2022) | 60 | 2,21 | -0,35 a 6,14 | 5,72% |
| C | Conferência (entradas 2023-2026) | 47 | 0,68 | -0,63 a 2,67 | 22,50% |
| C | Total | 107 | 1,54 | -0,13 a 3,88 | 3,96% |

**Legenda:**

- *Meses*: meses da fatia (unidades). *Excesso médio*: média mensal do (retorno do patrimônio − retorno do espelho 105% CDI líquido) × 12, em pontos percentuais ao ano.
- *t*: excesso médio ÷ erro-padrão de Newey-West (que corrige a correlação entre meses vizinhos com pesos de Bartlett). *Valor p*: duas caudas, t com n−1 graus de liberdade. *IC 95% (pp/ano)*: média ± t crítico × erro-padrão, anualizado.
- *Bootstrap*: IC pelos percentis 2,5% e 97,5% das médias de 10.000 séries reamostradas em blocos de 6 meses. *% das repetições com média ≤ 0*: fração das séries reamostradas em que o excesso médio não foi positivo.

**Leitura prática:** olhando o patrimônio todo, mês a mês, o excesso sobre 105% do CDI é de 1,5 ponto ao ano na A, 2,4 na B e 1,5 na C no período total, e **o intervalo de 95% inclui zero nas três carteiras, com qualquer número de defasagens (3, 6 ou 12) e também no bootstrap** (por exemplo, A: de −0,5 a 3,4 pontos pelo Newey-West e de −0,1 a 3,8 pelo bootstrap). Na conferência (2023 a 2026) o excesso é de 0,4 a 0,8 ponto ao ano e está longe de qualquer significância (p entre 0,33 e 0,63). Ou seja: o que parecia certeza por ordem vira, na carteira inteira, uma vantagem pequena e que os dados ainda não separam de sorte.

---

### Conferência (refeita à mão no próprio programa)

Saída impressa do programa (trecho):

- Ordem BBVJ11, carteira A, entrada 28/05/2018, saída 21/12/2018 (volta à média). Abertura de 28/05/2018 em `precos_2018.csv` = 50,0500; 59 cotas × 50,05 = 2.952,95, igual à planilha. Rendimentos: seis avisos (data-base 29/06, 31/07, 31/08, 28/09, 31/10 e 30/11/2018, pagos em 10/07, 08/08, 11/09, 08/10, 09/11 e 10/12) somam R$ 9,62, igual à coluna da planilha. Compra = 2.952,95 + taxa 0,8859 = 2.953,8359; venda = 2.952,95 + 6,21 = 2.959,16, taxa de venda 0,8877. Resultado antes do imposto = 6,21 + 9,62 − 0,8859 − 0,8877 = 14,0534, ou 0,476% da ordem; o pipeline dá o mesmo valor. 105% do CDI no mesmo prazo: 1,17752902 ÷ 1,13454462 − 1 = 3,7887%; excesso = 0,476% − 3,789% = −3,313 pontos (pipeline: −3,313).
- Aplicação de R$ 10.000 em 105% do CDI de 09/05/2018 a 19/03/2019: índices 1,19531510 ÷ 1,13074444, rendimento bruto R$ 571,0456; 314 dias corridos, alíquota de 20%; líquido R$ 10.456,8365 (função do programa: igual).
- Aplicação de R$ 10.000 de 03/02/2020 a 18/02/2020 (15 dias): bruto R$ 18,8543; IOF de 50% (15º dia da tabela) = R$ 9,4271; IR de 22,5% sobre R$ 9,4271 = R$ 2,1211; líquido R$ 10.007,3060 (função: igual).
- TIR da ordem BBVJ11 sozinha, sem imposto: 0,841% ao ano; o valor presente dos fluxos nessa taxa é 0,00000000. Fluxos: 28/05/2018 −2.953,84; seis rendimentos de R$ 0,77 a R$ 1,77; 21/12/2018 +2.958,27.

---

### Tabela de lacunas

| Dado | Situação | Efeito |
|---|---|---|
| Data de pagamento dos rendimentos | 3 avisos (R$ 82,08) nas ordens sem data de pagamento; usada data-base + 11 dias | pequeno: desloca poucos dias o recebimento na TIR e no saldo |
| Rendimentos pagos depois de 09/11/2026 | 20 avisos (R$ 690,98) de ordens da base; entram na TIR na data de pagamento e na carteira do pico como 'a receber' (valor declarado) | valor final inclui dinheiro ainda não recebido |
| Ordens em aberto | 66 ordens avaliadas ao preço de 09/11/2026, sem imposto e com taxa de venda | TIR das ordens um pouco favorecida (sem imposto); versão só com fechadas mostrada |
| Imposto por ordem | o imposto do FII é mensal com abatimento: não se divide por ordem | comparações por ordem são antes do imposto dos dois lados |
| Dias úteis depois de 13/11/2026 | o cdi.csv termina em 13/11/2026; DARF de vendas de novembro/2026 usa o último dia de semana de dezembro (sem feriados) | no máximo 1 dia de diferença em um imposto |
| Amortizações | não entram como dinheiro recebido nas ordens (lacuna herdada do estudo anterior) | ordens de fundos que devolveram patrimônio aparecem com perda maior que a real |
| Saltos de preço sem ajuste | 334 variações de mais de 25% em um dia, em 128 fundos (README das planilhas); 13 das 341 ordens da A têm um salto | afeta o resultado dessas ordens; não removidas |
| Preços da planilha de ordens | valor e valorização arredondados ao centavo em kairi_ordens.csv | erro de até 1 centavo por ordem |
| Índice da bolsa de ações | não existe na base; 'mercado' do estudo é o FII do meio | sem comparação com ações |
| Fundo com último preço antes de 09/11/2026 | 1 ordem(ns) em aberto cujo último preço é anterior a 09/11/2026 (avaliada nesse preço) | efeito desprezível |
| Ordens em aberto fora das estatísticas por ordem | as 66 ordens em aberto não entram nos indicadores, no teste ingênuo nem no resultado por episódio (só nos fluxos de TIR, no saldo do pico e na contagem de episódios) | estatísticas por ordem usam só ordens fechadas, como o estudo anterior |
| kairi_ordens_saidas.csv sem a carteira C | a conferência cruzada do resultado antes do imposto com esse arquivo só vale para A e B; para C a conferência é a dos rendimentos e das taxas | nenhum efeito nos números |
| Imposto a pagar no patrimônio mensal | o imposto do mês só entra como dívida no último dia do mês da venda; antes disso o patrimônio não o desconta | pequena oscilação no patrimônio dentro do mês; afeta pouco Sharpe, Sortino e Calmar |
| Falta de caixa na carteira do pico | o programa prevê dívida a 105% do CDI se o saldo acabar; não ocorreu nenhuma vez (ver coluna da tabela) | sem efeito |
| Estimativa do imposto das ordens em aberto | não calculado (venda hipotética) | TIR das ordens e valor final do pico levemente favorecidos |

---

### Resumo dos achados

- O estudo anterior mostrava média e % de ordens positivas; ficaram de fora mediana, quantis, assimetria, curtose, desvio, semidesvio, razão ganhos ÷ perdas, correlação e contagem de episódios. Com eles: mediana acima da média, assimetria negativa (−2,3 na A) e cauda de perdas.
- As 341, 175 e 292 ordens equivalem a 24, 30 e 12 episódios independentes (janela de 20 pregões); 12, 19 e 7 com 40 pregões; 46, 39 e 23 com 10.
- TIR do dinheiro enquanto está nas ordens: 29,8% (A), 40,8% (B), 32,2% (C) ao ano, contra 7,2%, 6,3% e 6,9% do espelho em 105% do CDI.
- Com o dinheiro do pico parado em 105% do CDI: 10,2%, 11,1% e 10,2% ao ano contra 8,6% de ficar tudo no CDI (R$ 73,6 mil, R$ 71,4 mil e R$ 74,8 mil a mais em 09/11/2026).
- Sharpe 0,48 / 0,51 / 0,48; Sortino 1,26 / 2,25 / 1,33; Calmar 3,73 / 3,18 / 3,75; maior queda de 2,7% / 3,5% / 2,7% (março de 2020).
- Teste por ordem: tudo "significativo" (p ≈ 0). Corrigido pela sobreposição: A com 20 pregões p = 0,008 mas p = 0,13 com 10; B e C geralmente não significativos.
- Excesso mensal da carteira do pico: 1,5 / 2,4 / 1,5 ponto ao ano no total, com intervalo de 95% incluindo zero em todos os métodos; na conferência, 0,4 a 0,8 ponto.
- Conclusão estatística: a vantagem sobre 105% do CDI existe nos números, mas não está provada contra sorte quando se respeita que as ordens vêm em ondas.

---

## Bloco 2 da auditoria do Kairi: funil das quedas (item 4) e regra de "virada" (item 5)

Programa: `estudos/auditoria_bloco2.py` (lê só `planilhas/`). Rodar: `cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/auditoria_bloco2.py`. Planilhas: `planilhas/auditoria_bloco2_*.csv`.

### 0. O que é confirmado por execução e o que é dedução

- **Confirmado por execução:** minha cópia das regras reproduziu as 341 ordens da carteira A (15%) e as 175 da B (20%) de `planilhas/kairi_ordens.csv`: mesmos fundos, datas de entrada e saída, motivos, cotas, preços (diferença máxima 0,00) e resultado por ordem (diferença máxima 0,00 em R$, com o imposto por ordem daquele arquivo). Dinheiro do pico bateu: A R$ 262.698 e B R$ 151.506. Também conferi à mão uma ordem (SDIL11) e sua aplicação no 105% do CDI, e uma entrada em duas partes (FIGS11); os números bateram (impresso no programa).
- **Dedução/interpretação:** as frases de "Leitura prática", as divisões entre números de tabelas diferentes e as definições abaixo.

#### Interpretações que precisei fazer

1. **Resultado de cada ordem "antes do imposto"** = valorização + rendimentos recebidos − taxas de 0,03% (compra e venda). É o mesmo critério das tabelas da Parte 4 ("antes do imposto, já com taxas"). O imposto do FII (20% mensal, prejuízo abatendo) aparece à parte, só por carteira, nas colunas finais do CSV `gatilhos` e `virada_resumo`.
2. **Régua:** 105% do CDI líquido de IOF (menos de 30 dias) e IR regressivo, sobre o mesmo valor (custo de compra da ordem), da data de entrada à data de saída (dia sem linha no `cdi.csv` usa o último dia útil anterior). **Excesso = resultado antes do imposto do FII − CDI líquido** (um número líquido de IR da renda fixa contra um bruto de imposto de FII, como pedido; ver Lacunas).
3. **Ordens em aberto** (preço de 09/11/2026) entram em todas as contas, avaliadas pelo último preço, e vão contadas à parte nas tabelas. Para elas o CDI vai até 09/11/2026.
4. **"Chegou a X% abaixo da média" (funil):** em algum fechamento do episódio (do dia do sinal até o dia da saída da ordem: volta à média, prazo de 252 pregões, dado suspeito ou fim da base) o afastamento do fechamento em relação à média dos 200 fechamentos anteriores foi ≤ −X. É a mesma medida do sinal. A **profundidade máxima** é o menor afastamento desse episódio.
5. **Funil por ordens, não por sinais brutos.** Cada gatilho tem muito mais sinais do que ordens, porque a carteira só tem um lote por fundo por vez: 10%: 1.735 sinais, 582 ordens; 15%: 809 sinais, 341 ordens; 20%: 332 sinais, 175 ordens; 30%: 46 sinais, 37 ordens. Os demais ficaram bloqueados (fundo já em carteira), sem negociação na abertura seguinte ou com ordem menor que R$ 1.000. Usei as ordens porque só elas têm saída e resultado.
6. **"Lucrativa" = resultado antes do imposto > 0**; "perdida" = ordem do gatilho menor que nunca chegou ao nível do gatilho maior, logo a carteira maior não teria aquela entrada (conferi: nenhuma dessas 247, 172 e 131 teve ordem real da carteira maior no episódio).
7. **Virada (E2).** Código em `estudos/kairi_expandido.py`, função `gatilho`, Parte 4: depois do sinal (cruzamento do afastamento para baixo de −X, no dia d), olha os pregões j = d+1 até d+60. O **primeiro** j em que (a) o fechamento de j é maior que a média dos 10 fechamentos anteriores a j e (b) o afastamento de j, calculado com a média de 200 que **inclui** o próprio j, é ≤ −5% dispara a virada. Compra na abertura de j+1, se o fundo negociou nesse dia; se não negociou, o sinal fica sem ordem. Não há nova checagem de universo/rendimento em j. Se nenhum j serve em 60 pregões, não há ordem. A saída é a mesma da carteira direta (volta à média com prazo de 252 pregões contados da entrada), um fundo por vez, mesmo tamanho (menor entre R$ 3.000 e 5% do negociado no dia do sinal, mínimo R$ 1.000). O sinal em si usa a definição de `kairi_ordens.py` (média até a véspera), não a do `kairi_expandido.py` (média até o dia); por isso os sinais são os das carteiras A e B.
8. **Período no item 5:** em todos os métodos o período é o da data da entrada **direta** do sinal (dia seguinte ao sinal), para que direta, virada e duas partes sejam comparáveis sinal a sinal. Uma virada de um sinal de dezembro de 2022 comprada em janeiro de 2023 fica na escolha.
9. **Duas partes:** a ordem direta de sempre é dividida ao meio (valor da ordem direta / 2 em cada metade, cotas inteiras). A 1ª metade entra na entrada direta. A 2ª entra na abertura de j+1 da virada **somente se isso ocorrer antes do dia da saída da 1ª metade**; as duas saem juntas, no mesmo dia e preço. Se a 2ª metade não é comprada, esse dinheiro fica no CDI: mostro o resultado do comprado e, à parte, o resultado somado ao rendimento líquido desse CDI sobre a base (comprado + parado). Como o CDI parado rende igual à régua, ele não altera o excesso em R$. Uma ordem direta de 15% (valor de uma cota só, metade de zero cotas) ficou de fora das duas partes. Compara-se com a "direta nos mesmos sinais".
10. **Medidas de risco** (todas sobre o resultado % de cada ordem antes do imposto): desvio padrão; "desvio das perdas" = raiz da média de min(resultado, 0)² sobre todas as ordens; média dos 10% piores (as ⌈10%·n⌉ piores); queda abaixo da entrada = menor mínima do dia desde a entrada até a saída sobre o preço de entrada (nas duas partes, o valor da posição inteira, cada metade a partir do seu dia de entrada, sobre o custo já pago); quantis 5% e 95% do resultado %.

### 1. Item 4: funil das quedas

#### 1.1 Cada gatilho como carteira (ordens da carteira infinita, saída na volta à média, prazo de 252)

| Gatilho | Período | Ordens (em aberto) | Aplicado | Resultado R$ | Resultado % | 105% CDI líq. R$ | Excesso R$ | Excesso (pp do aplicado) | % positivas | Pior ordem | Dias médios | Dinheiro do pico |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10% | Escolha 2018–2022 | 265 (0) | R$ 748.719 | R$ 41.725 | 5,6% | R$ 18.896 | R$ 22.829 | 3,0 | 80,0% | -37,3% | 155 | nd |
| 10% | Conferência 2023–2026 | 317 (65) | R$ 905.326 | R$ 35.962 | 4,0% | R$ 28.022 | R$ 7.941 | 0,9 | 77,3% | -78,2% | 113 | nd |
| 10% | Total | 582 (65) | R$ 1.654.045 | R$ 77.688 | 4,7% | R$ 46.918 | R$ 30.770 | 1,9 | 78,5% | -78,2% | 132 | R$ 346.710 |
| 15% | Escolha 2018–2022 | 165 (0) | R$ 464.576 | R$ 53.509 | 11,5% | R$ 10.723 | R$ 42.787 | 9,2 | 84,8% | -70,1% | 154 | nd |
| 15% | Conferência 2023–2026 | 176 (30) | R$ 498.283 | R$ 41.024 | 8,2% | R$ 15.325 | R$ 25.700 | 5,2 | 86,4% | -76,6% | 112 | nd |
| 15% | Total | 341 (30) | R$ 962.859 | R$ 94.534 | 9,8% | R$ 26.047 | R$ 68.487 | 7,1 | 85,6% | -76,6% | 132 | R$ 262.698 |
| 20% | Escolha 2018–2022 | 97 (0) | R$ 277.148 | R$ 48.849 | 17,6% | R$ 5.681 | R$ 43.168 | 15,6 | 88,7% | -37,7% | 165 | nd |
| 20% | Conferência 2023–2026 | 78 (11) | R$ 220.426 | R$ 25.104 | 11,4% | R$ 7.606 | R$ 17.497 | 7,9 | 83,3% | -47,3% | 124 | nd |
| 20% | Total | 175 (11) | R$ 497.574 | R$ 73.953 | 14,9% | R$ 13.287 | R$ 60.666 | 12,2 | 86,3% | -47,3% | 147 | R$ 151.506 |
| 30% | Escolha 2018–2022 | 28 (0) | R$ 82.460 | R$ 24.505 | 29,7% | R$ 1.426 | R$ 23.079 | 28,0 | 100,0% | 5,7% | 177 | nd |
| 30% | Conferência 2023–2026 | 9 (1) | R$ 24.557 | R$ 2.873 | 11,7% | R$ 902 | R$ 1.971 | 8,0 | 66,7% | -46,1% | 132 | nd |
| 30% | Total | 37 (1) | R$ 107.017 | R$ 27.378 | 25,6% | R$ 2.329 | R$ 25.050 | 23,4 | 91,9% | -46,1% | 166 | R$ 65.275 |

**Legenda.** *Gatilho*: cota X% abaixo da média de 200 pregões (10, 15 = carteira A, 20 = carteira B, 30%), com rendimento mantido. *Período*: pelo ano da data de entrada (escolha 2018–2022, conferência 2023–2026). *Ordens (em aberto)*: número de ordens (quantas ainda abertas em 09/11/2026). *Aplicado*: soma do custo de compra das ordens (R$). *Resultado R$*: valorização + rendimentos − taxas, antes do imposto do FII. *Resultado %*: Resultado R$ ÷ Aplicado. *105% CDI líq. R$*: o mesmo dinheiro nas mesmas datas a 105% do CDI, líquido de IR e IOF. *Excesso R$*: Resultado R$ − CDI. *Excesso (pp do aplicado)*: Excesso R$ ÷ Aplicado, em pontos percentuais. *% positivas*: ordens com resultado > 0. *Pior ordem*: menor resultado % de uma ordem. *Dias médios*: dias corridos médios da entrada à saída. *Dinheiro do pico*: maior soma de custos de ordens abertas ao mesmo tempo (só no total).

**Leitura prática.** Subir o gatilho reduz muito o dinheiro necessário (pico de R$ 347 mil no de 10%, R$ 263 mil no de 15%, R$ 152 mil no de 20% e R$ 65 mil no de 30%) e aumenta o ganho por real aplicado. O excesso total em R$ é maior nos gatilhos de 15% (R$ 68.487) e 20% (R$ 60.666), cai no de 10% (R$ 30.770) e no de 30% (R$ 25.050, só 37 ordens). Em todos os gatilhos o excesso por real aplicado é menor na conferência que na escolha; no de 30% a conferência tem só 9 ordens e 5 delas ganharam do CDI.

(Dedução, divisão de números da tabela: excesso total ÷ dinheiro do pico = 8,9% no gatilho de 10%, 26,1% no de 15%, 40,0% no de 20% e 38,4% no de 30%. O imposto do FII por carteira, com abatimento de prejuízo e sem a defasagem do DARF, está em `auditoria_bloco2_gatilhos.csv`: 10%: R$ 6.371; 15%: R$ 13.033, igual ao da Parte 4; 20%: R$ 11.796; 30%: R$ 5.030.)

#### 1.2 O funil: quantas ordens chegaram mais fundo

| Gatilho | Período | Ordens (sinais) | Chegaram a 15% | Chegaram a 20% | Chegaram a 30% |
|---|---|---|---|---|---|
| 10% | Escolha 2018–2022 | 265 | 165 (62%) | 94 (35%) | 29 (11%) |
| 10% | Conferência 2023–2026 | 317 | 170 (54%) | 81 (26%) | 19 (6%) |
| 10% | Total | 582 | 335 (58%) | 175 (30%) | 48 (8%) |
| 15% | Escolha 2018–2022 | 165 | - | 93 (56%) | 29 (18%) |
| 15% | Conferência 2023–2026 | 176 | - | 76 (43%) | 16 (9%) |
| 15% | Total | 341 | - | 169 (50%) | 45 (13%) |

**Legenda.** *Ordens (sinais)*: ordens do gatilho da primeira coluna (cada uma de um sinal). *Chegaram a 15/20/30%*: quantas tiveram, em algum fechamento do episódio, afastamento ≤ −15%, −20% ou −30% (e o % entre parênteses é essa contagem ÷ ordens). "-" quando o nível é o próprio gatilho. Episódio: do sinal até a saída da ordem.

**Leitura prática.** De cada 10 ordens de 10%, 6 chegaram a 15%, 3 a 20% e menos de 1 a 30% (582 → 335 → 175 → 48). Das de 15%, metade chegou a 20% e uma em oito a 30% (341 → 169 → 45). Na conferência a fração que chega fundo é parecida com a da escolha.

#### 1.3 Resultado conforme a profundidade máxima atingida

| Entrada em | Período | Profundidade máxima | Ordens | Resultado médio | Mediana | % positivas | Excesso sobre 105% CDI (pp, média) | Excesso R$ | Resultado R$ |
|---|---|---|---|---|---|---|---|---|---|
| 10% | Escolha 2018–2022 | 10–15% | 100 | 9,0% | 9,3% | 99,0% | 6,9 | R$ 19.123 | R$ 24.721 |
| 10% | Escolha 2018–2022 | 15–20% | 71 | 5,9% | 5,7% | 87,3% | 2,7 | R$ 5.543 | R$ 11.710 |
| 10% | Escolha 2018–2022 | 20–30% | 65 | 4,7% | 2,4% | 56,9% | 2,0 | R$ 3.847 | R$ 9.070 |
| 10% | Escolha 2018–2022 | mais de 30% | 29 | -5,1% | -0,4% | 48,3% | -6,9 | R$ -5.684 | R$ -3.776 |
| 10% | Conferência 2023–2026 | 10–15% | 147 | 8,1% | 9,2% | 96,6% | 6,4 | R$ 27.038 | R$ 34.347 |
| 10% | Conferência 2023–2026 | 15–20% | 89 | 5,3% | 6,1% | 75,3% | 1,9 | R$ 4.959 | R$ 13.529 |
| 10% | Conferência 2023–2026 | 20–30% | 62 | 0,3% | 1,4% | 54,8% | -4,9 | R$ -8.620 | R$ 424 |
| 10% | Conferência 2023–2026 | mais de 30% | 19 | -27,8% | -29,7% | 10,5% | -31,2 | R$ -15.437 | R$ -12.338 |
| 10% | Total | 10–15% | 247 | 8,4% | 9,3% | 97,6% | 6,6 | R$ 46.161 | R$ 59.069 |
| 10% | Total | 15–20% | 160 | 5,5% | 6,0% | 80,6% | 2,3 | R$ 10.502 | R$ 25.239 |
| 10% | Total | 20–30% | 127 | 2,5% | 1,6% | 55,9% | -1,3 | R$ -4.773 | R$ 9.494 |
| 10% | Total | mais de 30% | 48 | -14,1% | -15,3% | 33,3% | -16,0 | R$ -21.121 | R$ -16.114 |
| 15% | Escolha 2018–2022 | 15–20% | 72 | 13,2% | 13,0% | 95,8% | 11,3 | R$ 22.542 | R$ 26.544 |
| 15% | Escolha 2018–2022 | 20–30% | 64 | 10,9% | 12,1% | 79,7% | 9,0 | R$ 16.516 | R$ 21.052 |
| 15% | Escolha 2018–2022 | mais de 30% | 29 | 6,3% | 8,4% | 69,0% | 4,5 | R$ 3.729 | R$ 5.914 |
| 15% | Conferência 2023–2026 | 15–20% | 100 | 11,9% | 13,3% | 97,0% | 9,4 | R$ 26.745 | R$ 33.578 |
| 15% | Conferência 2023–2026 | 20–30% | 60 | 9,4% | 10,6% | 86,7% | 5,9 | R$ 10.149 | R$ 16.266 |
| 15% | Conferência 2023–2026 | mais de 30% | 16 | -23,8% | -27,1% | 18,8% | -27,2 | R$ -11.194 | R$ -8.820 |
| 15% | Total | 15–20% | 172 | 12,4% | 13,3% | 96,5% | 10,2 | R$ 49.287 | R$ 60.122 |
| 15% | Total | 20–30% | 124 | 10,2% | 11,2% | 83,1% | 7,5 | R$ 26.665 | R$ 37.318 |
| 15% | Total | mais de 30% | 45 | -4,4% | 2,3% | 51,1% | -6,0 | R$ -7.466 | R$ -2.906 |

**Legenda.** *Entrada em*: gatilho da ordem. *Profundidade máxima*: faixa do menor afastamento do episódio (10–15% = parou entre −10% e −15%, e assim por diante; "mais de 30%" = foi além de −30%). *Ordens*: quantas. *Resultado médio* e *Mediana*: resultado % por ordem (antes do imposto). *% positivas*: ordens com resultado > 0. *Excesso (pp, média)*: média de (resultado − CDI) ÷ custo da ordem. *Excesso R$* e *Resultado R$*: somas.

**Leitura prática.** Quanto mais fundo a cota vai depois da entrada, pior o resultado: a ordem de 10% que parou entre 10 e 15% ganhou 8,4% em média e 98% foram positivas; as que passaram de 30% perderam 14,1% em média e só 1 em 3 ficou no positivo (na conferência, −27,8% e 2 de 19). A faixa mais funda da conferência é onde o dinheiro se perde: R$ −15.437 de excesso nas 19 ordens de 10% e R$ −11.194 nas 16 de 15%.

#### 1.4 Ordens lucrativas perdidas ao subir o gatilho (e prejuízos evitados)

| Subir de → para | Período | Ordens do gatilho menor | Nunca chegaram ao maior | Lucrativas perdidas (n) | Lucrativas perdidas (R$) | Prejuízos evitados (n) | Prejuízos evitados (R$) | Saldo do que a carteira maior não tem (R$) | Excesso s/ CDI do que não tem (R$) |
|---|---|---|---|---|---|---|---|---|---|
| 10% → 15% | Escolha 2018–2022 | 265 | 100 | 99 | R$ 24.839 | 1 | R$ -118 | R$ 24.721 | R$ 19.123 |
| 10% → 15% | Conferência 2023–2026 | 317 | 147 | 142 | R$ 34.617 | 5 | R$ -269 | R$ 34.347 | R$ 27.038 |
| 10% → 15% | Total | 582 | 247 | 241 | R$ 59.456 | 6 | R$ -387 | R$ 59.069 | R$ 46.161 |
| 15% → 20% | Escolha 2018–2022 | 165 | 72 | 69 | R$ 26.958 | 3 | R$ -414 | R$ 26.544 | R$ 22.542 |
| 15% → 20% | Conferência 2023–2026 | 176 | 100 | 97 | R$ 33.840 | 3 | R$ -263 | R$ 33.578 | R$ 26.745 |
| 15% → 20% | Total | 341 | 172 | 166 | R$ 60.798 | 6 | R$ -677 | R$ 60.122 | R$ 49.287 |
| 20% → 30% | Escolha 2018–2022 | 97 | 68 | 63 | R$ 34.699 | 5 | R$ -1.301 | R$ 33.398 | R$ 29.191 |
| 20% → 30% | Conferência 2023–2026 | 78 | 63 | 62 | R$ 30.208 | 1 | R$ -167 | R$ 30.041 | R$ 24.539 |
| 20% → 30% | Total | 175 | 131 | 125 | R$ 64.907 | 6 | R$ -1.468 | R$ 63.439 | R$ 53.730 |

**Legenda.** *Subir de → para*: comparação entre o gatilho menor e o maior. *Ordens do gatilho menor*: as do gatilho de partida. *Nunca chegaram ao maior*: ordens cujo afastamento nunca passou do gatilho maior (a carteira maior não teria essa entrada). *Lucrativas perdidas*: dessas, as com resultado > 0 (número e soma do resultado em R$). *Prejuízos evitados*: dessas, as com resultado ≤ 0. *Saldo*: resultado R$ de todas as que nunca chegaram. *Excesso s/ CDI*: o mesmo saldo menos o CDI líquido. Atenção: é o que a carteira maior **não** tem, não a diferença entre as duas carteiras (a maior também compra mais barato nas ordens que chegaram lá).

**Leitura prática.** Subir o gatilho joga fora quase só lucro: de 10% para 15% saem 241 ordens lucrativas (R$ 59.456) para evitar 6 prejuízos (R$ 387); de 15% para 20%, 166 lucrativas (R$ 60.798) contra 6 prejuízos (R$ 677); de 20% para 30%, 125 lucrativas (R$ 64.907) contra 6 prejuízos (R$ 1.468). As perdas grandes estão entre as ordens que **chegaram** fundo (por exemplo, 20% → 30% na conferência: as 15 ordens que chegaram a 30% somaram R$ −4.937), por isso o gatilho maior não as evita, só as torna proporcionalmente mais pesadas. Nos dois períodos o padrão se repete.

### 2. Item 5: virada contra entrada direta

#### 2.1 Gatilho de 15%

| Método | Período | Ordens | Sinais sem ordem | Entrada vs fech. do sinal | Resultado R$ | Resultado % | 105% CDI R$ | Excesso R$ | % positivas |
|---|---|---|---|---|---|---|---|---|---|
| Entrada direta | Escolha 2018–2022 | 165 | 0 | 0,0% | R$ 53.509 | 11,5% | R$ 10.723 | R$ 42.787 | 84,8% |
| Virada (E2, até 60 pregões) | Escolha 2018–2022 | 162 | 7 | 2,3% | R$ 37.124 | 8,1% | R$ 10.073 | R$ 27.052 | 82,7% |
| Duas partes (½ direta + ½ virada) | Escolha 2018–2022 | 164 | 8 | 1,0% | R$ 44.351 | 10,1% | R$ 9.880 | R$ 34.471 | 86,6% |
| Direta nos mesmos sinais das duas partes | Escolha 2018–2022 | 164 | 0 | 0,0% | R$ 53.681 | 11,6% | R$ 10.670 | R$ 43.011 | 85,4% |
| Entrada direta | Conferência 2023–2026 | 176 | 0 | 0,4% | R$ 41.024 | 8,2% | R$ 15.325 | R$ 25.700 | 86,4% |
| Virada (E2, até 60 pregões) | Conferência 2023–2026 | 156 | 21 | 1,5% | R$ 34.918 | 7,9% | R$ 13.803 | R$ 21.115 | 83,3% |
| Duas partes (½ direta + ½ virada) | Conferência 2023–2026 | 176 | 23 | 0,7% | R$ 37.142 | 8,1% | R$ 14.363 | R$ 22.779 | 83,5% |
| Direta nos mesmos sinais das duas partes | Conferência 2023–2026 | 176 | 0 | 0,4% | R$ 41.024 | 8,2% | R$ 15.325 | R$ 25.700 | 86,4% |
| Entrada direta | Total | 341 | 0 | 0,2% | R$ 94.534 | 9,8% | R$ 26.047 | R$ 68.487 | 85,6% |
| Virada (E2, até 60 pregões) | Total | 318 | 28 | 1,9% | R$ 72.042 | 8,0% | R$ 23.876 | R$ 48.166 | 83,0% |
| Duas partes (½ direta + ½ virada) | Total | 340 | 31 | 0,8% | R$ 81.493 | 9,1% | R$ 24.243 | R$ 57.250 | 85,0% |
| Direta nos mesmos sinais das duas partes | Total | 340 | 0 | 0,2% | R$ 94.706 | 9,9% | R$ 25.995 | R$ 68.711 | 85,9% |

| Método | Período | Desvio padrão | Desvio das perdas | Pior ordem | Média dos 10% piores | Queda abaixo da entrada (média) | Queda (pior) | Quantil 5% | Quantil 95% | Dias médios |
|---|---|---|---|---|---|---|---|---|---|---|
| Entrada direta | Escolha 2018–2022 | 14,8% | 7,9% | -70,1% | -19,5% | -14,1% | -71,7% | -13,9% | 32,0% | 154 |
| Virada (E2, até 60 pregões) | Escolha 2018–2022 | 12,6% | 8,0% | -68,3% | -20,4% | -9,9% | -72,6% | -12,7% | 22,8% | 148 |
| Duas partes (½ direta + ½ virada) | Escolha 2018–2022 | 13,2% | 7,9% | -70,6% | -18,9% | -14,2% | -72,2% | -12,5% | 26,6% | 154 |
| Direta nos mesmos sinais das duas partes | Escolha 2018–2022 | 14,7% | 7,9% | -70,1% | -19,1% | -14,0% | -71,7% | -14,0% | 32,1% | 154 |
| Entrada direta | Conferência 2023–2026 | 14,8% | 10,6% | -76,6% | -26,4% | -10,4% | -78,9% | -21,7% | 20,1% | 112 |
| Virada (E2, até 60 pregões) | Conferência 2023–2026 | 14,0% | 10,2% | -70,6% | -24,7% | -10,7% | -74,7% | -20,2% | 20,5% | 113 |
| Duas partes (½ direta + ½ virada) | Conferência 2023–2026 | 14,3% | 10,5% | -76,5% | -25,8% | -10,7% | -78,7% | -21,8% | 18,6% | 112 |
| Direta nos mesmos sinais das duas partes | Conferência 2023–2026 | 14,8% | 10,6% | -76,6% | -26,4% | -10,4% | -78,9% | -21,7% | 20,1% | 112 |
| Entrada direta | Total | 14,9% | 9,4% | -76,6% | -23,2% | -12,2% | -78,9% | -16,5% | 27,1% | 132 |
| Virada (E2, até 60 pregões) | Total | 13,3% | 9,1% | -70,6% | -22,6% | -10,3% | -74,7% | -17,1% | 20,9% | 131 |
| Duas partes (½ direta + ½ virada) | Total | 13,8% | 9,3% | -76,5% | -22,6% | -12,4% | -78,7% | -14,9% | 22,6% | 132 |
| Direta nos mesmos sinais das duas partes | Total | 14,9% | 9,4% | -76,6% | -23,0% | -12,1% | -78,9% | -16,6% | 27,1% | 132 |

#### 2.2 Gatilho de 20%

| Método | Período | Ordens | Sinais sem ordem | Entrada vs fech. do sinal | Resultado R$ | Resultado % | 105% CDI R$ | Excesso R$ | % positivas |
|---|---|---|---|---|---|---|---|---|---|
| Entrada direta | Escolha 2018–2022 | 97 | 0 | 0,2% | R$ 48.849 | 17,6% | R$ 5.681 | R$ 43.168 | 88,7% |
| Virada (E2, até 60 pregões) | Escolha 2018–2022 | 96 | 2 | 6,6% | R$ 28.189 | 10,3% | R$ 5.323 | R$ 22.866 | 82,3% |
| Duas partes (½ direta + ½ virada) | Escolha 2018–2022 | 96 | 4 | 2,8% | R$ 37.676 | 14,4% | R$ 5.240 | R$ 32.436 | 90,6% |
| Direta nos mesmos sinais das duas partes | Escolha 2018–2022 | 96 | 0 | 0,2% | R$ 48.922 | 17,7% | R$ 5.632 | R$ 43.289 | 89,6% |
| Entrada direta | Conferência 2023–2026 | 78 | 0 | 0,4% | R$ 25.104 | 11,4% | R$ 7.606 | R$ 17.497 | 83,3% |
| Virada (E2, até 60 pregões) | Conferência 2023–2026 | 72 | 8 | 2,3% | R$ 21.776 | 10,7% | R$ 6.976 | R$ 14.799 | 84,7% |
| Duas partes (½ direta + ½ virada) | Conferência 2023–2026 | 78 | 8 | 0,9% | R$ 23.096 | 11,2% | R$ 7.179 | R$ 15.917 | 84,6% |
| Direta nos mesmos sinais das duas partes | Conferência 2023–2026 | 78 | 0 | 0,4% | R$ 25.104 | 11,4% | R$ 7.606 | R$ 17.497 | 83,3% |
| Entrada direta | Total | 175 | 0 | 0,3% | R$ 73.953 | 14,9% | R$ 13.287 | R$ 60.666 | 86,3% |
| Virada (E2, até 60 pregões) | Total | 168 | 10 | 4,8% | R$ 49.964 | 10,5% | R$ 12.299 | R$ 37.666 | 83,3% |
| Duas partes (½ direta + ½ virada) | Total | 174 | 12 | 2,0% | R$ 60.772 | 13,0% | R$ 12.419 | R$ 48.353 | 87,9% |
| Direta nos mesmos sinais das duas partes | Total | 174 | 0 | 0,3% | R$ 74.025 | 14,9% | R$ 13.239 | R$ 60.787 | 86,8% |

| Método | Período | Desvio padrão | Desvio das perdas | Pior ordem | Média dos 10% piores | Queda abaixo da entrada (média) | Queda (pior) | Quantil 5% | Quantil 95% | Dias médios |
|---|---|---|---|---|---|---|---|---|---|---|
| Entrada direta | Escolha 2018–2022 | 16,5% | 6,5% | -37,7% | -16,9% | -14,0% | -44,8% | -12,9% | 41,3% | 165 |
| Virada (E2, até 60 pregões) | Escolha 2018–2022 | 14,1% | 7,1% | -37,3% | -19,1% | -9,4% | -43,9% | -13,3% | 29,6% | 158 |
| Duas partes (½ direta + ½ virada) | Escolha 2018–2022 | 14,2% | 6,7% | -38,3% | -16,4% | -14,2% | -44,8% | -10,6% | 33,1% | 165 |
| Direta nos mesmos sinais das duas partes | Escolha 2018–2022 | 16,4% | 6,6% | -37,7% | -16,6% | -13,9% | -44,8% | -12,9% | 41,4% | 165 |
| Entrada direta | Conferência 2023–2026 | 16,7% | 10,0% | -47,3% | -29,0% | -10,9% | -55,1% | -25,0% | 24,1% | 124 |
| Virada (E2, até 60 pregões) | Conferência 2023–2026 | 14,8% | 8,7% | -33,7% | -26,5% | -10,7% | -42,2% | -25,5% | 25,4% | 122 |
| Duas partes (½ direta + ½ virada) | Conferência 2023–2026 | 16,0% | 9,8% | -47,3% | -28,5% | -11,4% | -55,1% | -26,0% | 22,7% | 124 |
| Direta nos mesmos sinais das duas partes | Conferência 2023–2026 | 16,7% | 10,0% | -47,3% | -29,0% | -10,9% | -55,1% | -25,0% | 24,1% | 124 |
| Entrada direta | Total | 16,8% | 8,3% | -47,3% | -23,4% | -12,7% | -55,1% | -22,7% | 36,8% | 147 |
| Virada (E2, até 60 pregões) | Total | 14,4% | 7,8% | -37,3% | -22,6% | -9,9% | -43,9% | -22,1% | 28,2% | 142 |
| Duas partes (½ direta + ½ virada) | Total | 15,1% | 8,3% | -47,3% | -23,9% | -12,9% | -55,1% | -20,8% | 28,8% | 146 |
| Direta nos mesmos sinais das duas partes | Total | 16,8% | 8,3% | -47,3% | -24,3% | -12,6% | -55,1% | -22,8% | 36,9% | 146 |

**Legenda das duas tabelas de cada gatilho.** *Método*: entrada direta (abertura do dia seguinte ao sinal), virada (regra E2 do item 7 acima) ou duas partes (metade direta + metade na virada); a última linha de cada período é a direta restrita aos sinais que entraram nas duas partes. *Sinais sem ordem*: sinais da carteira direta que não viraram ordem (na linha das duas partes: 2ª metade não comprada). *Entrada vs fech. do sinal*: média de (preço médio de entrada ÷ fechamento do dia do sinal − 1). *Resultado R$/%*, *105% CDI R$*, *Excesso R$*, *% positivas*: como no item 1.1 (% é resultado ÷ aplicado; na tabela de duas partes o aplicado é só o efetivamente comprado). *Desvio padrão*: desvio padrão do resultado % das ordens. *Desvio das perdas*: raiz da média de min(resultado %, 0)². *Pior ordem*: menor resultado %. *Média dos 10% piores*: média dos 10% menores resultados %. *Queda abaixo da entrada*: menor mínima desde a entrada até a saída ÷ preço de entrada − 1 (média e pior). *Quantil 5% / 95%*: resultados % abaixo dos quais ficam 5% / 95% das ordens. *Dias médios*: dias corridos da entrada à saída.

#### 2.3 O que a virada evitou e o que perdeu

| Gatilho | Período | Ordens diretas | Sem ordem na virada | (não virou / sem negoc. / bloqueado / <R$ 1.000) | Perda evitada (n) | Perda evitada (R$) | Ganho perdido (n) | Ganho perdido (R$) | Saldo (R$) | Excesso s/ CDI dessas (R$) |
|---|---|---|---|---|---|---|---|---|---|---|
| 15% | Escolha 2018–2022 | 165 | 7 | 1 / 1 / 5 / 0 | 3 | R$ -1.159 | 4 | R$ 1.808 | R$ 649 | R$ 323 |
| 15% | Conferência 2023–2026 | 176 | 21 | 18 / 1 / 2 / 0 | 5 | R$ -2.705 | 16 | R$ 2.476 | R$ -229 | R$ -546 |
| 15% | Total | 341 | 28 | 19 / 2 / 7 / 0 | 8 | R$ -3.865 | 20 | R$ 4.284 | R$ 420 | R$ -223 |
| 20% | Escolha 2018–2022 | 97 | 2 | 1 / 1 / 0 / 0 | 0 | R$ 0 | 2 | R$ 1.021 | R$ 1.021 | R$ 999 |
| 20% | Conferência 2023–2026 | 78 | 8 | 6 / 1 / 1 / 0 | 1 | R$ -1.017 | 7 | R$ 962 | R$ -55 | R$ -214 |
| 20% | Total | 175 | 10 | 7 / 2 / 1 / 0 | 1 | R$ -1.017 | 9 | R$ 1.984 | R$ 966 | R$ 785 |

**Legenda.** *Ordens diretas*: ordens da carteira direta. *Sem ordem na virada*: as que a virada não comprou, e entre parênteses o motivo (não virou em 60 pregões / virou mas o fundo não negociou na abertura seguinte / bloqueado por já ter o fundo em carteira / ordem menor que R$ 1.000). *Perda evitada*: dessas, as direta com resultado < 0 (número e soma R$: o que a virada deixou de perder). *Ganho perdido*: dessas, as com resultado > 0 (número e soma R$: o que a virada deixou de ganhar). *Saldo*: soma do resultado de todas. *Excesso s/ CDI*: o mesmo menos o CDI líquido.

| Gatilho | Período | Sinais com as duas ordens | Direta nesses (R$) | Virada nesses (R$) | Excesso direta (R$) | Excesso virada (R$) | Entrada da virada vs direta (média) | Pregões até virar (média) | Ordens da virada sem ordem direta |
|---|---|---|---|---|---|---|---|---|---|
| 15% | Escolha 2018–2022 | 158 | R$ 52.860 | R$ 38.722 | R$ 42.464 | R$ 29.010 | 2,7% | 8,2 | 4 |
| 15% | Conferência 2023–2026 | 155 | R$ 41.254 | R$ 34.843 | R$ 26.246 | R$ 21.040 | 1,1% | 7,8 | 1 |
| 15% | Total | 313 | R$ 94.114 | R$ 73.565 | R$ 68.709 | R$ 50.049 | 1,9% | 8,0 | 5 |
| 20% | Escolha 2018–2022 | 95 | R$ 47.828 | R$ 28.203 | R$ 42.170 | R$ 22.898 | 6,7% | 6,9 | 1 |
| 20% | Conferência 2023–2026 | 70 | R$ 25.159 | R$ 21.211 | R$ 17.711 | R$ 14.327 | 1,6% | 7,1 | 2 |
| 20% | Total | 165 | R$ 72.987 | R$ 49.414 | R$ 59.880 | R$ 37.225 | 4,5% | 7,0 | 3 |

**Legenda.** *Sinais com as duas ordens*: sinais em que houve ordem direta e ordem na virada. *Direta nesses / Virada nesses*: resultado R$ das duas, nos mesmos sinais. *Excesso*: o mesmo contra o CDI. *Entrada da virada vs direta*: média de (preço da virada ÷ preço da direta − 1). *Pregões até virar*: média de dias de pregão entre a entrada direta e a da virada. *Ordens da virada sem direta*: a virada comprou, a direta não (fundo bloqueado ou sem negociação no dia seguinte).

#### 2.4 Entrada em duas partes: o dinheiro que ficou no CDI

| Gatilho | Período | Ordens | 2ª metade comprada | 2ª metade não comprada | Dinheiro que ficou no CDI | Rendimento líq. desse CDI | Resultado só do comprado | Resultado + CDI parado | Base (comprado + parado) | Resultado % da base | Excesso R$ (só comprado) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15% | Escolha 2018–2022 | 164 | 156 | 8 | R$ 10.788 | R$ 36 | R$ 44.351 | R$ 44.387 | R$ 449.037 | 9,9% | R$ 34.471 |
| 15% | Conferência 2023–2026 | 176 | 153 | 23 | R$ 31.271 | R$ 36 | R$ 37.142 | R$ 37.178 | R$ 491.803 | 7,6% | R$ 22.779 |
| 15% | Total | 340 | 309 | 31 | R$ 42.058 | R$ 72 | R$ 81.493 | R$ 81.565 | R$ 940.840 | 8,7% | R$ 57.250 |
| 20% | Escolha 2018–2022 | 96 | 92 | 4 | R$ 5.639 | R$ 30 | R$ 37.676 | R$ 37.706 | R$ 267.209 | 14,1% | R$ 32.436 |
| 20% | Conferência 2023–2026 | 78 | 70 | 8 | R$ 10.666 | R$ 28 | R$ 23.096 | R$ 23.124 | R$ 217.772 | 10,6% | R$ 15.917 |
| 20% | Total | 174 | 162 | 12 | R$ 16.305 | R$ 58 | R$ 60.772 | R$ 60.830 | R$ 484.981 | 12,5% | R$ 48.353 |

**Legenda.** *2ª metade comprada / não comprada*: a virada ocorreu (ou não) antes da saída da 1ª metade. *Dinheiro que ficou no CDI*: soma das metades não compradas (R$). *Rendimento líq. desse CDI*: 105% do CDI líquido sobre essas metades da entrada à saída. *Resultado só do comprado*: antes do imposto. *Resultado + CDI parado* ÷ *Base*: resultado do comprado mais o CDI da metade parada, sobre o que foi comprado mais o que ficou parado = *Resultado % da base*. *Excesso R$ (só comprado)*: contra o CDI do dinheiro realmente investido; a metade parada tem excesso zero por construção.

#### Leitura prática e se vale a pena (item 5)

- **A virada não vale a pena.** O excesso em R$ foi menor que o da entrada direta nos dois gatilhos e nos dois períodos. 15%: R$ 27.052 contra R$ 42.787 na escolha e R$ 21.115 contra R$ 25.700 na conferência; 20%: R$ 22.866 contra R$ 43.168 e R$ 14.799 contra R$ 17.497. O excesso por real aplicado também ficou abaixo (15%: 5,9 contra 9,2 pontos na escolha, 4,8 contra 5,2 na conferência; 20%: 8,4 contra 15,6 e 7,3 contra 7,9). Na conferência a diferença é pequena, na escolha é grande.
- **O motivo não é ter perdido ordens ruins nem boas, é o preço de entrada.** As ordens diretas sem ordem na virada somam quase zero (15%: 8 perdas evitadas de R$ −3.865 contra 20 ganhos perdidos de R$ +4.284, saldo +R$ 420; 20%: 1 perda de R$ −1.017 contra 9 ganhos de R$ +1.984). Já nos sinais em que as duas entraram (313 no gatilho de 15%, 165 no de 20%) a direta fez R$ 94.114 e a virada R$ 73.565 (15%) e R$ 72.987 contra R$ 49.414 (20%): a virada entra em média 1,9% (15%) e 4,5% (20%) acima do preço direto, porque espera a cota subir um pouco antes de comprar, e perde esse pedaço da alta até a média.
- **O que a virada melhora é só um pouco do risco:** desvio padrão menor (15%: 13,3% contra 14,9%; 20%: 14,4% contra 16,8%), pior ordem menos ruim (15%: −70,6% contra −76,6%; 20%: −37,3% contra −47,3%) e queda média abaixo da entrada menor (−10,3% contra −12,2% e −9,9% contra −12,7%). Mas a média dos 10% piores quase não mudou (15%: −22,6% contra −23,2%; 20%: −22,6% contra −23,4%), o quantil 5% do 15% ficou pior (−17,1% contra −16,5%) e o desvio das perdas é praticamente o mesmo (9,1% contra 9,4% e 7,8% contra 8,3%). A "pior ordem" melhor vem de poucos casos.
- **Duas partes fica no meio caminho, também perdendo da direta:** excesso total de R$ 57.250 contra R$ 68.711 (15%) e R$ 48.353 contra R$ 60.787 (20%), com a queda média abaixo da entrada igual à da direta (−12,4% e −12,9%). Nos dois períodos o excesso da direta nos mesmos sinais é maior (15%: R$ 34.471 contra 43.011 na escolha, 22.779 contra 25.700 na conferência; 20%: 32.436 contra 43.289 e 15.917 contra 17.497). Reduz o desvio padrão (13,8% contra 14,9% e 15,1% contra 16,8%), sem ganho no pior caso (pior ordem −76,5% e −47,3%, igual à direta). Não paga o que custa.
- **Conclusão pelos números:** a entrada direta fica. A virada só se justificaria para quem aceita abrir mão de cerca de R$ 20 mil de excesso (15%) ou R$ 23 mil (20%) no período todo, em troca de um desvio padrão 1,6 a 2,4 pontos menor.
- **Efeito do imposto do FII (dedução):** em todas as linhas o imposto do FII por carteira (CSV `virada_resumo`) é proporcional ao ganho e não muda a ordem entre os métodos (direta R$ 55.453 de excesso após imposto contra R$ 38.987 da virada no gatilho de 15%).

### 3. Conferências feitas

| Conferência | Resultado |
|---|---|
| Cópia das regras reproduz A e B de `kairi_ordens.csv` (nº de ordens, datas, preços, cotas, motivo, resultado por ordem) | 341 e 175 ordens iguais; diferença máxima de preço e de resultado 0,00 (a soma difere em R$ 0,04, por arredondamento a 2 casas das colunas do CSV) |
| Dinheiro do pico | A R$ 262.698, B R$ 151.506 (iguais ao esperado) |
| Ordem SDIL11 refeita a mão lendo planilhas cruas | resultado antes do imposto 530,46 e CDI 105% líquido 42,91 (103 dias, IR 22,5%), excesso 487,55; iguais ao programa |
| Entrada em duas partes FIGS11, regra E2 conferida à mão | fechamento 75,01 > média dos 10 anteriores 74,71 e afastamento −15,8% ≤ −5% em 01/06/2018; 2ª compra em 04/06/2018 a 75,03 |
| Imposto FII do gatilho 15% | R$ 13.033, igual ao da Parte 4 do estudo |
| Consistência do funil | nenhuma ordem "nunca chegou ao maior" teve ordem real da carteira maior no episódio |

### 4. Lacunas

| Dado | Situação | Efeito |
|---|---|---|
| Dados brutos (`dados/`) | Não existem neste ambiente; usei só `planilhas/` | Nenhum: as ordens A e B reproduziram o CSV |
| Pagamento do DARF no último dia útil do mês seguinte | O imposto do FII é calculado por mês de venda, sem a defasagem do pagamento, e só por carteira (ordens em aberto não pagam) | O excesso "após imposto do FII" do CSV é um pouco otimista para o fim do período; os números das tabelas deste relatório são antes do imposto do FII |
| Comparação "antes do imposto" contra CDI líquido | O resultado das ordens está antes do imposto do FII e o CDI está líquido de IR/IOF, como pedido | O excesso fica pequeno para menos em relação a uma comparação totalmente líquida; a ordem entre métodos não muda no que testei (item 5) |
| Ordens em aberto | 65 ordens de 10%, 30 de 15%, 11 de 20% e 1 de 30% avaliadas pelo preço de 09/11/2026 | A conferência inclui resultado ainda não realizado; no funil, a profundidade delas pode aumentar |
| Funil de sinais que não viraram ordem | Só ordens têm saída e resultado; sinais bloqueados, sem negociação ou menores que R$ 1.000 ficaram de fora | Os números de "sinais" do funil são ordens (contagem dos sinais brutos no item 0) |
| Sobra de dinheiro por cotas inteiras | Cada metade usa cotas inteiras; a diferença entre metade e custo das cotas não foi levada ao CDI | Efeito de poucos reais por ordem |
| Rendimento na virada | A virada só recebe os avisos de rendimento a partir da sua própria compra; a direta recebe também os do intervalo entre as duas entradas (média de 7 a 8 pregões) | Parte da vantagem da direta em R$ vem desse rendimento; está dentro do resultado e não foi isolado |
| 1 ordem das duas partes | Uma ordem direta de 15% (uma cota, metade vira zero) ficou fora das duas partes e está na comparação "direta nos mesmos sinais" | Mínimo (340 contra 341 ordens) |
| Preço de entrada da virada usa a abertura do dia seguinte à virada | Execução ao preço de abertura, sem folga de execução além da taxa de 0,03% | O mesmo vale para a direta |

---

## Bloco 3 da auditoria do estudo do Kairi: queda sem notícia contra queda com fato negativo

Programa: `estudos/auditoria_bloco3.py` (lê só `planilhas/`). Planilhas geradas: `planilhas/auditoria_bloco3_*.csv`. Comando: `cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/auditoria_bloco3.py`.

**Aviso para todas as tabelas:** o tipo e o sentido de cada fato foram classificados por palavras (`fii/classificar.py`) e erram. A seção 0 mede o erro lendo 40 textos à mão: de 20 fatos "de queda", 10 estavam mal classificados (e 2 duvidosos); de 20 "de alta", 7 mal classificados (e 6 duvidosos). Nenhuma conclusão abaixo é mais confiável que essa classificação.

### Resumo em linguagem simples

1. Quase toda ordem é "queda sem notícia": com a classificação por palavras, só 45 das 764 ordens com dados (6%) tiveram fato negativo do mesmo fundo nos 60 dias antes do sinal (12 a 19 por carteira).
2. Resultado médio, carteira A total, 60 dias: sem fato 7,8%, com fato 9,3%. B: 11,8% e 10,9%. C: 8,9% e 9,3%. A diferença "sem menos com" tem intervalo de 95% que inclui zero em todos os casos (ex.: A, −1,4 ponto, de −6,7 a +4,3; p = 0,34). Não há prova de que a notícia ruim piore (ou melhore) o resultado, mas também há poucas ordens para ver.
3. Fato positivo nos 60 dias antes do sinal: resultados um pouco maiores (A 8,9% contra 7,8%; B 16,3% contra 11,3%; C 9,6% contra 8,8%), todos dentro do ruído.
4. Fato positivo durante a posição (6b-ii) não pode ser regra de compra (é informação do futuro) e mistura-se com duração da ordem: ordens com 2 ou mais fatos duraram ~220 dias contra ~122.
5. Por tema (6c), o que mais aparece é "emissão de cotas" (melhores médias, 16,9% a 19,7%) e "reorganização" (piores, ~0%); mas a classificação erra e as ordens se sobrepõem.
6. Em dias de queda geral (6d) o quadro é o mesmo. Como extra, ordens da A com menos de 15% de fundos caídos (queda só do fundo) renderam menos (2,4% nas 51 sem fato), só 57 ordens.
7. Contra 105% do CDI antes do imposto, o grupo "sem notícia" ganha em média 4,4 (A), 8,6 (B) e 5,6 (C) pontos percentuais por ordem no total (60 dias).
8. As duas contas de conferência batem (ordem 1 e ordem 14 do arquivo).

### O que foi confirmado por execução e o que é interpretação

Confirmado por execução (o programa calculou e conferiu): contagem de fatos por ordem e janela; resultado e excesso sobre a régua; tabelas de grupos; testes (Mann-Whitney e bootstrap com semente 7, 10.000 sorteios); amostra de 40 textos sorteada com semente 2024 (o programa confere que os ids sorteados são os que foram lidos).

Dedução ou interpretação minha (registradas aqui):
- "30 (ou 60) dias corridos antes do sinal, inclusive o dia do sinal" = fatos com data de sinal−30 (ou −60) até a data do sinal, só a data (a hora do anúncio não foi usada).
- "Diferença contra 105% do CDI antes do imposto": usei o rendimento bruto (sem IR e sem IOF) de aplicar o valor da ordem na data de entrada e resgatar na data de saída; o resultado da ordem já vem com taxas e o imposto de 20% sobre o ganho da própria ordem (sem compensação de prejuízo e sem atraso do DARF, como no arquivo de ordens). Como acréscimo, a planilha traz também o excesso sobre o CDI líquido (IR regressivo e IOF), no CSV. Resultado (%) = Resultado (R$) ÷ valor da ordem (o programa confere com a coluna do arquivo, tolerância de 0,06).
- "Excesso médio" = média das diferenças ordem a ordem, em pontos percentuais.
- 6b-(ii): fato positivo com data entre a data de entrada e a de saída, inclusive.
- 6c: a ordem entra em todas as linhas dos tipos que tem nos 60 dias; o tipo é a coluna `tipo` (primeiro tipo achado por palavras).
- 6d: carteira C (todas as ordens têm 15,4% ou mais de fundos caídos no dia, então é idêntica à 6a/6b) e ordens da A com "Fundos caídos no dia (%)" ≥ 15; a A com menos de 15 entrou como extra.
- Ordens de 15 fundos que não têm nenhum fato em `anuncios.csv` (44 ordens) saíram das comparações, porque lá "zero fatos" seria "sem dado" e não "sem notícia".
- "Fato negativo": definição 1 (principal) = sentido "queda"; definição 2 = tipo rendimento_reducao, saida_inquilino ou venda_com_perda; definição 3 = só saida_inquilino (escolhida por ter sido a mais confiável na leitura à mão; a escolha vem de uma amostra pequena).
- Os vereditos "ok / duvidoso / mal classificado" são julgamento de um leitor só, sobre os primeiros 3.000 caracteres de cada texto; não são um gabarito.


## Tabelas (saída do programa, geradas por estudos/auditoria_bloco3.py)

Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

### 0. Fatos usados e erro da classificação

| grupo de fatos | fatos |
|---|---|
| todos os fatos da planilha anuncios.csv | 7.962 |
| ignorados por serem repetidos (repetido = 1) | 1.265 |
| ignorados por serem continuação (continuacao = 1) | 933 |
| ignorados que são os dois ao mesmo tempo | 188 |
| total ignorado (repetido ou continuação) | 2.010 |
| fatos contados | 5.952 |
|   dos contados: sentido queda | 763 |
|   dos contados: sentido alta | 1.805 |
|   dos contados: tipo rendimento_reducao, saida_inquilino ou venda_com_perda | 875 |
|   dos contados: tipo saida_inquilino | 367 |

**Leitura prática:** Dos 7.962 fatos, 2.010 são repetidos ou continuação e ficaram de fora; contamos 5.952 (763 de sentido queda, 1.805 de alta).

Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

Amostra lida à mão (20 fatos sentido queda + 20 sentido alta, sorteados com semente 2024 entre os fatos contados):

| sentido sorteado | ok | duvidoso | mal classificado | total |
|---|---|---|---|---|
| alta | 7 | 6 | 7 | 20 |
| queda | 8 | 2 | 10 | 20 |

- sentido queda, mal classificados: 740634, 709629, 433490, 705148, 690753, 161443, 250032, 549130, 124446, 467813
- sentido queda, duvidosos: 13748, 353068
- sentido alta, mal classificados: 783410, 34946, 501362, 80009, 1035450, 355168, 47068
- sentido alta, duvidosos: 84073, 1221531, 322042, 32747, 741826, 188347


Dentro da amostra de queda, por tipo atribuído pelas palavras:

| tipo (palavras) | duvidoso | mal classificado | ok |

|---|---|---|---|
| rendimento_reducao | 0 | 10 | 1 |
| saida_inquilino | 2 | 0 | 7 |

**Leitura prática:** De 20 fatos "de queda" sorteados, só 8 eram mesmo notícia ruim para o fundo e 10 estavam errados (quase todos são anúncios de emissão de novas cotas ou de venda de imóvel, pegos por uma palavra como "diminuída"). Os "de alta" erraram 7 em 20 e deixaram 6 duvidosos. A parte "saída de inquilino" foi a mais confiável (nenhum erro em 9); a parte "redução de rendimento" errou 10 em 11. São só 40 textos lidos por uma pessoa (eu) em textos cortados em 3.000 caracteres, então a taxa de erro real é incerta.

### Cobertura dos fatos

| carteira | ordens | ordens de fundo sem nenhum fato na planilha |
|---|---|---|
| A | 341 | 19 |
| B | 175 | 9 |
| C | 292 | 16 |
| total | 808 | 44 |

**Leitura prática:** 44 das 808 ordens são de 15 fundos que não têm nenhum fato na planilha; para eles "sem notícia" seria falso (é "sem dado"), por isso foram tiradas das comparações (ficam 764 ordens).

Fundos das ordens que não aparecem em anuncios.csv: AEFI11, AGCX11, ASMT11, BBVJ11, CRFF11, CXCI11, FIIP11, IFIE11, INLG11, MGLG11, OUCY11, RBCO11, RBOP11, TRBL11, UBSR11. Para eles 'zero fatos' não quer dizer 'sem notícia', quer dizer 'sem dado'. Interpretação adotada: essas ordens saem das comparações (grupo 0, 1, 2 ou mais) e ficam só na planilha de ordens.

Ordens usadas nas comparações: 764 (de 808).

Chaves das contagens (janela = dias corridos antes do sinal, incluindo o dia do sinal, isto é, de sinal−30 (ou −60) até o dia do sinal):
- fato negativo, definição 1 (principal) = sentido 'queda'; definição 2 = tipo rendimento_reducao, saida_inquilino ou venda_com_perda; definição 3 = só tipo saida_inquilino (a que a leitura à mão mostrou mais confiável).
- fato positivo = sentido 'alta'. 6b(ii) usa fatos com data de anúncio entre a data de entrada e a de saída (inclusive).

### 6a. Queda sem notícia contra queda com fato negativo

Janela de 30 dias, fato negativo = definição 1 (sentido queda). Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 0 | 147 | 9,1 | 10,9 | 86 | 6,2 | -70,1 | -13,6 | 150 | 7 |
| A | escolha 2018-2022 | 1 | 8 | 6,3 | 5,7 | 75 | 1,5 | -20,0 | -20,4 | 208 | 0 |
| A | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A | conferência 2023-2026 | 0 | 162 | 7,0 | 10,7 | 90 | 3,2 | -76,6 | -9,7 | 107 | 2 |
| A | conferência 2023-2026 | 1 | 5 | 5,4 | 9,1 | 60 | 1,2 | -11,1 | -10,4 | 127 | 0 |
| A | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A | total | 0 | 309 | 8,0 | 10,8 | 88 | 4,6 | -76,6 | -11,6 | 128 | 5 |
| A | total | 1 | 13 | 5,9 | 9,1 | 69 | 1,4 | -20,0 | -16,6 | 177 | 0 |
| A | total | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | escolha 2018-2022 | 0 | 86 | 13,7 | 16,2 | 88 | 11,1 | -37,7 | -13,2 | 166 | 12 |
| B | escolha 2018-2022 | 1 | 5 | 15,1 | 14,6 | 100 | 11,1 | 2,2 | -25,0 | 196 | 0 |
| B | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | conferência 2023-2026 | 0 | 71 | 9,3 | 14,6 | 87 | 5,2 | -47,3 | -9,7 | 115 | 3 |
| B | conferência 2023-2026 | 1 | 4 | 8,2 | 5,4 | 50 | 1,8 | -19,1 | -20,2 | 182 | 0 |
| B | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | total | 0 | 157 | 11,7 | 15,0 | 88 | 8,5 | -47,3 | -11,6 | 143 | 8 |
| B | total | 1 | 9 | 12,0 | 13,3 | 78 | 7,0 | -19,1 | -22,9 | 190 | 0 |
| B | total | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | escolha 2018-2022 | 0 | 135 | 9,2 | 10,9 | 87 | 6,3 | -70,1 | -13,8 | 153 | 8 |
| C | escolha 2018-2022 | 1 | 5 | 4,3 | 2,2 | 80 | -0,5 | -20,0 | -20,7 | 234 | 0 |
| C | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | conferência 2023-2026 | 0 | 132 | 8,8 | 11,1 | 94 | 5,2 | -76,6 | -8,2 | 101 | 2 |
| C | conferência 2023-2026 | 1 | 4 | 7,9 | 9,7 | 75 | 4,9 | -4,1 | -6,7 | 83 | 0 |
| C | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | total | 0 | 267 | 9,0 | 11,0 | 90 | 5,7 | -76,6 | -11,0 | 127 | 5 |
| C | total | 1 | 9 | 5,9 | 9,1 | 78 | 1,9 | -20,0 | -14,5 | 167 | 0 |
| C | total | 2 ou mais | 0 | - | - | - | - | - | - | - | - |

Janela de 60 dias, fato negativo = definição 1 (sentido queda). Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 0 | 143 | 8,9 | 10,8 | 85 | 5,9 | -70,1 | -13,9 | 153 | 8 |
| A | escolha 2018-2022 | 1 | 12 | 9,8 | 14,5 | 83 | 6,3 | -20,0 | -15,1 | 160 | 0 |
| A | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A | conferência 2023-2026 | 0 | 160 | 6,9 | 10,6 | 89 | 3,1 | -76,6 | -9,7 | 107 | 2 |
| A | conferência 2023-2026 | 1 | 5 | 6,2 | 9,1 | 60 | 1,4 | -11,1 | -12,9 | 134 | 0 |
| A | conferência 2023-2026 | 2 ou mais | 2 | 13,9 | 13,9 | 100 | 10,6 | 10,8 | -3,8 | 104 | 0 |
| A | total | 0 | 303 | 7,8 | 10,8 | 87 | 4,4 | -76,6 | -11,7 | 129 | 5 |
| A | total | 1 | 17 | 8,7 | 13,3 | 76 | 4,8 | -20,0 | -14,4 | 153 | 0 |
| A | total | 2 ou mais | 2 | 13,9 | 13,9 | 100 | 10,6 | 10,8 | -3,8 | 104 | 0 |
| B | escolha 2018-2022 | 0 | 85 | 13,6 | 16,1 | 88 | 11,0 | -37,7 | -13,4 | 167 | 12 |
| B | escolha 2018-2022 | 1 | 6 | 15,9 | 17,4 | 100 | 12,6 | 2,2 | -21,4 | 174 | 0 |
| B | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | conferência 2023-2026 | 0 | 69 | 9,6 | 14,6 | 88 | 5,6 | -47,3 | -9,3 | 111 | 1 |
| B | conferência 2023-2026 | 1 | 5 | 10,8 | 11,3 | 60 | 4,2 | -22,2 | -18,4 | 184 | 20 |
| B | conferência 2023-2026 | 2 ou mais | 1 | -19,1 | -19,1 | 0 | -30,4 | -19,1 | -38,7 | 321 | 0 |
| B | total | 0 | 154 | 11,8 | 14,9 | 88 | 8,6 | -47,3 | -11,5 | 142 | 7 |
| B | total | 1 | 11 | 13,6 | 14,6 | 82 | 8,7 | -22,2 | -20,1 | 178 | 9 |
| B | total | 2 ou mais | 1 | -19,1 | -19,1 | 0 | -30,4 | -19,1 | -38,7 | 321 | 0 |
| C | escolha 2018-2022 | 0 | 131 | 9,0 | 10,8 | 86 | 6,0 | -70,1 | -14,1 | 156 | 8 |
| C | escolha 2018-2022 | 1 | 9 | 9,8 | 15,6 | 89 | 6,7 | -20,0 | -13,4 | 158 | 0 |
| C | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | conferência 2023-2026 | 0 | 131 | 8,7 | 11,2 | 94 | 5,1 | -76,6 | -8,2 | 101 | 2 |
| C | conferência 2023-2026 | 1 | 4 | 7,9 | 9,7 | 75 | 4,9 | -4,1 | -6,7 | 83 | 0 |
| C | conferência 2023-2026 | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |
| C | total | 0 | 262 | 8,9 | 10,9 | 90 | 5,6 | -76,6 | -11,1 | 128 | 5 |
| C | total | 1 | 13 | 9,2 | 13,3 | 85 | 6,2 | -20,0 | -11,4 | 135 | 0 |
| C | total | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |

Legenda: carteira = A (15% abaixo da média), B (20%), C (15% só em queda geral); período = ano da entrada; grupo = número de fatos negativos do mesmo fundo na janela; ordens = quantidade de ordens; média e mediana (%) = Resultado (%) da ordem (resultado em R$ ÷ valor da ordem, já com taxas e imposto da ordem); % positivas = ordens com resultado maior que zero; excesso (p.p.) = média de (Resultado % − rendimento de 105% do CDI antes do imposto, com o mesmo valor, da data de entrada à de saída); pior ordem = menor Resultado (%); maior queda média = média da coluna 'Maior queda abaixo da entrada (%)'; dias = média de dias corridos; % saiu por prazo = ordens com motivo 'prazo' (não voltaram à média em 252 pregões). Ordens 'em aberto' valem pelo preço de 09/11/2026 e entram nas médias.

**Leitura prática:** Entre as ordens com dados, só 45 de 764 (6%) tiveram algum fato negativo (pelo critério de palavras) do mesmo fundo nos 60 dias antes do sinal; quase todas as ordens são "queda sem notícia". O resultado médio dos dois grupos é parecido (por exemplo, carteira C total, 60 dias: 8,9% sem fato contra 9,3% com fato), e o grupo "com fato" é pequeno demais para dizer que a notícia muda algo. As poucas ordens de 2 ou mais fatos (4 no total) não permitem leitura.

Teste simples, sem notícia (0) contra com fato negativo (1 ou mais). Diferença de médias = média do grupo 0 menos média do grupo 'com'; IC 95% por bootstrap (10000 sorteios, semente 7); p = Mann-Whitney bilateral. Atenção: as ordens se sobrepõem no tempo (muitas entram nos mesmos dias de queda geral e o mesmo fato entra na contagem de várias ordens), então o p é otimista (parece mais convincente do que é). Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

Janela de 30 dias, definição 1, medida: Resultado (%).

| carteira | período | janela (dias) | medida | ordens sem | ordens com | média sem | média com | diferença (sem − com) | IC95 inferior | IC95 superior | p Mann-Whitney |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 30 | resultado (%) | 147 | 8 | 9,1 | 6,3 | 2,8 | -6,3 | 12,8 | 0,559 |
| A | conferência 2023-2026 | 30 | resultado (%) | 162 | 5 | 7,0 | 5,4 | 1,6 | -8,0 | 12,2 | 0,924 |
| A | total | 30 | resultado (%) | 309 | 13 | 8,0 | 5,9 | 2,0 | -4,9 | 9,3 | 0,576 |
| B | escolha 2018-2022 | 30 | resultado (%) | 86 | 5 | 13,7 | 15,1 | -1,4 | -8,4 | 6,1 | 0,980 |
| B | conferência 2023-2026 | 30 | resultado (%) | 71 | 4 | - | - | - | - | - | - |
| B | total | 30 | resultado (%) | 157 | 9 | 11,7 | 12,0 | -0,3 | -10,9 | 10,4 | 0,765 |
| C | escolha 2018-2022 | 30 | resultado (%) | 135 | 5 | 9,2 | 4,3 | 4,9 | -7,6 | 18,1 | 0,519 |
| C | conferência 2023-2026 | 30 | resultado (%) | 132 | 4 | - | - | - | - | - | - |
| C | total | 30 | resultado (%) | 267 | 9 | 9,0 | 5,9 | 3,1 | -4,4 | 11,5 | 0,460 |

Janela de 60 dias, definição 1, medida: Resultado (%).

| carteira | período | janela (dias) | medida | ordens sem | ordens com | média sem | média com | diferença (sem − com) | IC95 inferior | IC95 superior | p Mann-Whitney |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 60 | resultado (%) | 143 | 12 | 8,9 | 9,8 | -0,9 | -7,5 | 6,9 | 0,527 |
| A | conferência 2023-2026 | 60 | resultado (%) | 160 | 7 | 6,9 | 8,4 | -1,5 | -9,3 | 7,4 | 0,576 |
| A | total | 60 | resultado (%) | 303 | 19 | 7,8 | 9,3 | -1,4 | -6,7 | 4,3 | 0,343 |
| B | escolha 2018-2022 | 60 | resultado (%) | 85 | 6 | 13,6 | 15,9 | -2,3 | -8,4 | 4,4 | 0,785 |
| B | conferência 2023-2026 | 60 | resultado (%) | 69 | 6 | 9,6 | 5,8 | 3,7 | -14,3 | 21,5 | 0,535 |
| B | total | 60 | resultado (%) | 154 | 12 | 11,8 | 10,9 | 0,9 | -9,0 | 11,6 | 0,993 |
| C | escolha 2018-2022 | 60 | resultado (%) | 131 | 9 | 9,0 | 9,8 | -0,8 | -8,7 | 8,8 | 0,439 |
| C | conferência 2023-2026 | 60 | resultado (%) | 131 | 5 | 8,7 | 8,5 | 0,3 | -5,2 | 6,9 | 0,753 |
| C | total | 60 | resultado (%) | 262 | 14 | 8,9 | 9,3 | -0,5 | -5,9 | 5,8 | 0,533 |

Legenda: ordens sem/com = ordens sem fato / com 1 ou mais fatos negativos; média = média do Resultado (%) (p.p. de rentabilidade); diferença (sem − com) = média sem − média com, em pontos percentuais; IC95 = intervalo de 95% da diferença; p = probabilidade, se não houvesse diferença, de ver algo tão distante (otimista, ver aviso). Valor '-' = menos de 5 ordens em algum dos grupos. Os mesmos testes para o excesso sobre 105% CDI e para as definições 2 e 3 estão em planilhas/auditoria_bloco3_6a_testes.csv.

**Leitura prática:** Nenhum teste mostra diferença que se possa afirmar: todos os intervalos de 95% passam por zero (carteira A total, 60 dias: sem fato 7,8% contra com fato 9,3%, diferença −1,4 ponto, intervalo de −6,7 a +4,3, p = 0,34). Mesmo com esse p otimista, não há sinal; e "não há sinal" aqui é por falta de ordens com fato (12 a 19), não prova de que a notícia não importa.

Sensibilidade à definição de fato negativo (total dos períodos, janela de 60 dias; só excesso médio e número de ordens):

| definição | carteira | ordens grupo 0 | média (%) grupo 0 | excesso (p.p.) grupo 0 | ordens grupo 1 | média (%) grupo 1 | excesso (p.p.) grupo 1 | ordens grupo 2 ou mais | média (%) grupo 2 ou mais | excesso (p.p.) grupo 2 ou mais |
|---|---|---|---|---|---|---|---|---|---|---|
| 1: sentido queda | A | 303 | 7,8 | 4,4 | 17 | 8,7 | 4,8 | 2 | 13,9 | 10,6 |
| 1: sentido queda | B | 154 | 11,8 | 8,6 | 11 | 13,6 | 8,7 | 1 | -19,1 | -30,4 |
| 1: sentido queda | C | 262 | 8,9 | 5,6 | 13 | 9,2 | 6,2 | 1 | 10,8 | 7,4 |
| 2: reducao+saida_inquilino+venda_com_perda | A | 302 | 7,7 | 4,3 | 18 | 10,2 | 6,5 | 2 | 13,9 | 10,6 |
| 2: reducao+saida_inquilino+venda_com_perda | B | 152 | 11,6 | 8,5 | 13 | 15,2 | 10,6 | 1 | -19,1 | -30,4 |
| 2: reducao+saida_inquilino+venda_com_perda | C | 261 | 8,8 | 5,5 | 14 | 11,1 | 8,2 | 1 | 10,8 | 7,4 |
| 3: só saida_inquilino | A | 310 | 7,9 | 4,5 | 10 | 7,3 | 3,9 | 2 | 13,9 | 10,6 |
| 3: só saida_inquilino | B | 160 | 11,7 | 8,4 | 5 | 19,8 | 16,6 | 1 | -19,1 | -30,4 |
| 3: só saida_inquilino | C | 267 | 8,9 | 5,6 | 8 | 7,9 | 4,7 | 1 | 10,8 | 7,4 |

Legenda: igual à tabela anterior, mas somando todos os períodos; grupo 0/1/2 ou mais = número de fatos negativos em 60 dias. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

**Leitura prática:** Trocar a definição de "fato negativo" (3 versões) não muda o quadro: nenhum grupo com fato é claramente melhor ou pior que o sem fato, e os grupos "2 ou mais" têm 1 a 2 ordens. Isso vale com a classificação que erra; com uma leitura correta, os números poderiam ser outros.

### 6b. Subida com e sem fato positivo

Interpretação registrada: (i) fato positivo (sentido 'alta') do mesmo fundo nos 30 ou 60 dias antes do sinal, incluindo o dia do sinal; (ii) fato positivo com data entre a data de entrada e a data de saída da ordem (inclusive). Em (ii) o grupo é definido com informação que só existe depois da entrada, então NÃO dá para usar como regra de compra; e ordens mais longas têm mais chance de ter algum fato, o que mistura 'fato positivo' com 'ordem demorada'.

(i) 30 dias antes do sinal. Grupo = número de fatos positivos. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 0 | 146 | 8,8 | 10,8 | 85 | 5,8 | -70,1 | -13,7 | 152 | 8 |
| A | escolha 2018-2022 | 1 | 8 | 11,4 | 12,2 | 88 | 8,6 | -2,7 | -19,5 | 180 | 0 |
| A | escolha 2018-2022 | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,3 | 10,8 | -6,9 | 131 | 0 |
| A | conferência 2023-2026 | 0 | 152 | 7,2 | 10,9 | 90 | 3,3 | -76,6 | -9,9 | 110 | 3 |
| A | conferência 2023-2026 | 1 | 15 | 4,2 | 4,7 | 73 | 1,3 | -16,5 | -7,9 | 84 | 0 |
| A | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A | total | 0 | 298 | 8,0 | 10,9 | 88 | 4,5 | -76,6 | -11,8 | 131 | 5 |
| A | total | 1 | 23 | 6,7 | 10,1 | 78 | 3,8 | -16,5 | -11,9 | 117 | 0 |
| A | total | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,3 | 10,8 | -6,9 | 131 | 0 |
| B | escolha 2018-2022 | 0 | 84 | 13,1 | 14,6 | 88 | 10,4 | -37,7 | -14,0 | 167 | 12 |
| B | escolha 2018-2022 | 1 | 7 | 22,0 | 19,5 | 100 | 19,8 | 12,5 | -12,5 | 173 | 0 |
| B | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | conferência 2023-2026 | 0 | 72 | 9,6 | 14,7 | 86 | 5,4 | -47,3 | -10,2 | 118 | 3 |
| B | conferência 2023-2026 | 1 | 3 | 1,6 | 3,2 | 67 | -2,6 | -12,4 | -10,9 | 119 | 0 |
| B | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | total | 0 | 156 | 11,5 | 14,6 | 87 | 8,1 | -47,3 | -12,3 | 144 | 8 |
| B | total | 1 | 10 | 15,9 | 16,8 | 90 | 13,1 | -12,4 | -12,0 | 157 | 0 |
| B | total | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | escolha 2018-2022 | 0 | 132 | 8,9 | 10,8 | 86 | 5,9 | -70,1 | -13,7 | 154 | 8 |
| C | escolha 2018-2022 | 1 | 7 | 11,4 | 12,6 | 86 | 8,5 | -2,7 | -21,4 | 196 | 0 |
| C | escolha 2018-2022 | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,3 | 10,8 | -6,9 | 131 | 0 |
| C | conferência 2023-2026 | 0 | 125 | 9,1 | 11,2 | 95 | 5,4 | -76,6 | -8,2 | 103 | 2 |
| C | conferência 2023-2026 | 1 | 11 | 4,9 | 8,7 | 73 | 2,5 | -16,5 | -7,2 | 66 | 0 |
| C | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C | total | 0 | 257 | 9,0 | 11,0 | 91 | 5,7 | -76,6 | -11,0 | 129 | 5 |
| C | total | 1 | 18 | 7,4 | 10,5 | 78 | 4,9 | -16,5 | -12,7 | 117 | 0 |
| C | total | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,3 | 10,8 | -6,9 | 131 | 0 |

(i) 60 dias antes do sinal. Grupo = número de fatos positivos. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 0 | 140 | 8,6 | 10,5 | 84 | 5,5 | -70,1 | -14,0 | 156 | 8 |
| A | escolha 2018-2022 | 1 | 12 | 12,5 | 12,7 | 92 | 10,3 | -2,7 | -13,0 | 134 | 0 |
| A | escolha 2018-2022 | 2 ou mais | 3 | 11,8 | 10,8 | 100 | 9,3 | 10,8 | -14,0 | 117 | 0 |
| A | conferência 2023-2026 | 0 | 145 | 7,0 | 10,8 | 90 | 3,1 | -76,6 | -10,2 | 110 | 3 |
| A | conferência 2023-2026 | 1 | 18 | 6,3 | 10,4 | 78 | 3,3 | -16,5 | -7,3 | 86 | 0 |
| A | conferência 2023-2026 | 2 ou mais | 4 | 7,5 | 7,4 | 100 | 3,9 | 2,5 | -3,4 | 106 | 0 |
| A | total | 0 | 285 | 7,8 | 10,7 | 87 | 4,3 | -76,6 | -12,1 | 133 | 5 |
| A | total | 1 | 30 | 8,8 | 11,9 | 83 | 6,1 | -16,5 | -9,6 | 105 | 0 |
| A | total | 2 ou mais | 7 | 9,4 | 10,8 | 100 | 6,2 | 2,5 | -7,9 | 111 | 0 |
| B | escolha 2018-2022 | 0 | 83 | 13,0 | 14,6 | 88 | 10,3 | -37,7 | -14,1 | 168 | 12 |
| B | escolha 2018-2022 | 1 | 5 | 21,8 | 20,1 | 100 | 20,4 | 17,5 | -15,3 | 175 | 0 |
| B | escolha 2018-2022 | 2 ou mais | 3 | 21,9 | 16,2 | 100 | 18,7 | 12,5 | -6,2 | 136 | 0 |
| B | conferência 2023-2026 | 0 | 68 | 9,2 | 14,4 | 85 | 4,9 | -47,3 | -10,6 | 119 | 3 |
| B | conferência 2023-2026 | 1 | 7 | 10,1 | 14,1 | 86 | 6,1 | -12,4 | -7,3 | 116 | 0 |
| B | conferência 2023-2026 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| B | total | 0 | 151 | 11,3 | 14,6 | 87 | 7,9 | -47,3 | -12,5 | 146 | 8 |
| B | total | 1 | 12 | 15,0 | 16,9 | 92 | 12,0 | -12,4 | -10,6 | 141 | 0 |
| B | total | 2 ou mais | 3 | 21,9 | 16,2 | 100 | 18,7 | 12,5 | -6,2 | 136 | 0 |
| C | escolha 2018-2022 | 0 | 126 | 8,7 | 10,7 | 86 | 5,6 | -70,1 | -14,0 | 158 | 9 |
| C | escolha 2018-2022 | 1 | 11 | 12,6 | 12,9 | 91 | 10,4 | -2,7 | -13,6 | 140 | 0 |
| C | escolha 2018-2022 | 2 ou mais | 3 | 11,8 | 10,8 | 100 | 9,3 | 10,8 | -14,0 | 117 | 0 |
| C | conferência 2023-2026 | 0 | 117 | 8,9 | 11,0 | 95 | 5,2 | -76,6 | -8,5 | 105 | 2 |
| C | conferência 2023-2026 | 1 | 16 | 7,2 | 11,5 | 81 | 4,7 | -16,5 | -6,4 | 70 | 0 |
| C | conferência 2023-2026 | 2 ou mais | 3 | 9,2 | 10,1 | 100 | 6,4 | 4,7 | -1,2 | 79 | 0 |
| C | total | 0 | 243 | 8,8 | 10,8 | 90 | 5,4 | -76,6 | -11,4 | 133 | 5 |
| C | total | 1 | 27 | 9,4 | 12,2 | 85 | 7,0 | -16,5 | -9,4 | 99 | 0 |
| C | total | 2 ou mais | 6 | 10,5 | 10,8 | 100 | 7,9 | 4,7 | -7,6 | 98 | 0 |

(ii) entre a entrada e a saída. Grupo = número de fatos positivos. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | 0 | 126 | 9,7 | 11,2 | 87 | 6,8 | -70,1 | -13,1 | 146 | 6 |
| A | escolha 2018-2022 | 1 | 19 | 8,5 | 10,4 | 95 | 6,0 | -37,1 | -14,9 | 157 | 11 |
| A | escolha 2018-2022 | 2 ou mais | 10 | 0,2 | 2,2 | 50 | -4,9 | -33,5 | -23,3 | 236 | 10 |
| A | conferência 2023-2026 | 0 | 150 | 7,1 | 10,9 | 89 | 3,5 | -76,6 | -9,7 | 104 | 2 |
| A | conferência 2023-2026 | 1 | 12 | 5,0 | 10,2 | 83 | 0,5 | -34,7 | -8,9 | 126 | 8 |
| A | conferência 2023-2026 | 2 ou mais | 5 | 5,7 | 5,9 | 100 | -0,1 | 0,8 | -12,4 | 178 | 0 |
| A | total | 0 | 276 | 8,3 | 11,0 | 88 | 5,0 | -76,6 | -11,2 | 123 | 4 |
| A | total | 1 | 31 | 7,2 | 10,4 | 90 | 3,8 | -37,1 | -12,6 | 145 | 10 |
| A | total | 2 ou mais | 15 | 2,1 | 5,9 | 67 | -3,3 | -33,5 | -19,7 | 217 | 7 |
| B | escolha 2018-2022 | 0 | 71 | 14,2 | 16,1 | 90 | 11,9 | -30,2 | -13,6 | 159 | 10 |
| B | escolha 2018-2022 | 1 | 11 | 13,1 | 16,3 | 91 | 9,6 | -37,7 | -15,9 | 197 | 18 |
| B | escolha 2018-2022 | 2 ou mais | 9 | 11,0 | 11,8 | 78 | 7,1 | -31,6 | -13,7 | 195 | 11 |
| B | conferência 2023-2026 | 0 | 69 | 9,9 | 14,8 | 87 | 5,8 | -47,3 | -9,7 | 113 | 1 |
| B | conferência 2023-2026 | 1 | 4 | -2,0 | -0,5 | 50 | -8,5 | -29,5 | -18,4 | 184 | 25 |
| B | conferência 2023-2026 | 2 ou mais | 2 | 10,8 | 10,8 | 100 | 5,2 | 8,9 | -14,1 | 166 | 0 |
| B | total | 0 | 140 | 12,1 | 15,2 | 89 | 8,9 | -47,3 | -11,7 | 137 | 6 |
| B | total | 1 | 15 | 9,1 | 12,5 | 80 | 4,8 | -37,7 | -16,5 | 193 | 20 |
| B | total | 2 ou mais | 11 | 11,0 | 11,8 | 82 | 6,8 | -31,6 | -13,8 | 190 | 9 |
| C | escolha 2018-2022 | 0 | 114 | 9,7 | 11,2 | 88 | 6,9 | -70,1 | -13,0 | 148 | 7 |
| C | escolha 2018-2022 | 1 | 17 | 8,4 | 10,4 | 94 | 5,7 | -37,1 | -16,2 | 167 | 12 |
| C | escolha 2018-2022 | 2 ou mais | 9 | 1,4 | 7,0 | 56 | -3,8 | -33,5 | -22,7 | 238 | 11 |
| C | conferência 2023-2026 | 0 | 123 | 8,8 | 11,2 | 93 | 5,3 | -76,6 | -8,2 | 99 | 2 |
| C | conferência 2023-2026 | 1 | 10 | 8,1 | 10,3 | 90 | 4,5 | -16,5 | -7,1 | 100 | 0 |
| C | conferência 2023-2026 | 2 ou mais | 3 | 8,5 | 6,8 | 100 | 2,8 | 5,9 | -8,8 | 168 | 0 |
| C | total | 0 | 237 | 9,2 | 11,2 | 91 | 6,1 | -76,6 | -10,5 | 122 | 4 |
| C | total | 1 | 27 | 8,3 | 10,4 | 93 | 5,3 | -37,1 | -12,8 | 142 | 7 |
| C | total | 2 ou mais | 12 | 3,2 | 6,9 | 67 | -2,1 | -33,5 | -19,2 | 220 | 8 |

Legenda: igual à 6a, mas o grupo é o número de fatos positivos (sentido 'alta') do mesmo fundo.

**Leitura prática:** Com fato positivo nos 60 dias antes do sinal, as ordens renderam um pouco mais (A: 8,9% contra 7,8%; B: 16,3% contra 11,3%; C: 9,6% contra 8,8%, tabela de testes abaixo), mas a diferença é pequena diante do ruído. O grupo (ii), fato positivo durante a posição, mostra "2 ou mais" com resultado pior (A 2,1%, C 3,2%), mas essas ordens duraram bem mais (217 a 220 dias contra 122 a 123): quanto mais tempo a ordem fica aberta, mais fatos aparecem, então isso mede duração, não efeito do fato.

Teste simples (sem fato positivo contra com fato positivo), Resultado (%), mesmos cuidados da 6a (p otimista):

(i) 60 dias antes do sinal

| carteira | período | medida | ordens sem | ordens com | média sem | média com | diferença (sem − com) | IC95 inferior | IC95 superior | p Mann-Whitney |
|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | resultado (%) | 140 | 15 | 8,6 | 12,4 | -3,8 | -7,4 | 0,0 | 0,186 |
| A | conferência 2023-2026 | resultado (%) | 145 | 22 | 7,0 | 6,5 | 0,5 | -3,7 | 5,0 | 0,378 |
| A | total | resultado (%) | 285 | 37 | 7,8 | 8,9 | -1,1 | -4,2 | 2,1 | 0,774 |
| B | escolha 2018-2022 | resultado (%) | 83 | 8 | 13,0 | 21,8 | -8,8 | -15,3 | -3,1 | 0,106 |
| B | conferência 2023-2026 | resultado (%) | 68 | 7 | 9,2 | 10,1 | -0,9 | -8,7 | 8,5 | 0,838 |
| B | total | resultado (%) | 151 | 15 | 11,3 | 16,3 | -5,1 | -10,8 | 1,1 | 0,203 |
| C | escolha 2018-2022 | resultado (%) | 126 | 14 | 8,7 | 12,4 | -3,7 | -7,7 | 0,3 | 0,234 |
| C | conferência 2023-2026 | resultado (%) | 117 | 19 | 8,9 | 7,5 | 1,4 | -2,8 | 6,0 | 0,730 |
| C | total | resultado (%) | 243 | 33 | 8,8 | 9,6 | -0,8 | -3,9 | 2,5 | 0,506 |

(ii) entre a entrada e a saída

| carteira | período | medida | ordens sem | ordens com | média sem | média com | diferença (sem − com) | IC95 inferior | IC95 superior | p Mann-Whitney |
|---|---|---|---|---|---|---|---|---|---|---|
| A | escolha 2018-2022 | resultado (%) | 126 | 29 | 9,7 | 5,7 | 4,0 | -1,8 | 10,3 | 0,106 |
| A | conferência 2023-2026 | resultado (%) | 150 | 17 | 7,1 | 5,2 | 2,0 | -3,8 | 8,9 | 0,402 |
| A | total | resultado (%) | 276 | 46 | 8,3 | 5,5 | 2,8 | -1,5 | 7,4 | 0,088 |
| B | escolha 2018-2022 | resultado (%) | 71 | 20 | 14,2 | 12,2 | 2,0 | -6,4 | 11,5 | 0,770 |
| B | conferência 2023-2026 | resultado (%) | 69 | 6 | 9,9 | 2,2 | 7,6 | -5,7 | 22,9 | 0,193 |
| B | total | resultado (%) | 140 | 26 | 12,1 | 9,9 | 2,2 | -5,2 | 10,3 | 0,571 |
| C | escolha 2018-2022 | resultado (%) | 114 | 26 | 9,7 | 6,0 | 3,8 | -2,4 | 10,6 | 0,152 |
| C | conferência 2023-2026 | resultado (%) | 123 | 13 | 8,8 | 8,2 | 0,6 | -3,7 | 5,9 | 0,684 |
| C | total | resultado (%) | 237 | 39 | 9,2 | 6,7 | 2,5 | -1,8 | 7,4 | 0,168 |

Legenda: como a dos testes da 6a, com 'sem' = sem fato positivo e 'com' = 1 ou mais fatos positivos.

**Leitura prática:** Todos os intervalos de 95% incluem zero e o menor p entre as tabelas mostradas é 0,088 (carteira A, grupo (ii), total, que tem o problema de duração descrito acima). Nada firme a concluir.

### 6c. Resultado por tema do fato (coluna tipo)

Interpretação: para cada ordem com pelo menos um fato do mesmo fundo nos 60 dias antes do sinal (fatos repetidos e continuações fora), a ordem entra em uma linha para cada tipo de fato que ela tem nessa janela; uma ordem com fatos de 2 tipos aparece nas 2 linhas, então as linhas não somam o total. O tipo é o da classificação por palavras (erra, ver seção 0). Linhas com menos de 10 ordens ficam marcadas 'não concluir'.

Total e períodos por tipo. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| carteira | tipo | ordens tot | média (%) tot | mediana (%) tot | % positivas tot | excesso s/ 105% CDI (p.p.) tot | ordens esc | média (%) esc | ordens conf | média (%) conf | pode concluir? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | aquisicao | 3 | 3,2 | 3,3 | 67 | -2,8 | 1 | -2,7 | 2 | 6,2 | não concluir (menos de 10 ordens) |
| A | emissao | 19 | 16,9 | 14,2 | 95 | 15,7 | 16 | 19,4 | 3 | 3,3 | sim |
| A | locacao_nova | 18 | 9,8 | 11,3 | 89 | 6,9 | 10 | 9,2 | 8 | 10,5 | sim |
| A | outro | 24 | 6,2 | 10,9 | 92 | 3,2 | 11 | 6,2 | 13 | 6,1 | sim |
| A | recebimento | 2 | 15,1 | 15,1 | 100 | 12,8 | 2 | 15,1 | 0 | - | não concluir (menos de 10 ordens) |
| A | rendimento_aumento | 12 | 11,5 | 11,5 | 100 | 9,2 | 5 | 11,9 | 7 | 11,2 | sim |
| A | rendimento_reducao | 8 | 13,8 | 16,2 | 88 | 9,8 | 6 | 12,3 | 2 | 18,5 | não concluir (menos de 10 ordens) |
| A | reorganizacao | 11 | -0,1 | 3,6 | 64 | -4,4 | 8 | -4,2 | 3 | 10,8 | sim |
| A | saida_inquilino | 12 | 8,4 | 12,1 | 75 | 5,0 | 7 | 11,4 | 5 | 4,3 | sim |
| A | venda | 12 | 9,9 | 10,5 | 100 | 6,5 | 4 | 14,3 | 8 | 7,7 | sim |
| A | venda_com_ganho | 5 | 2,9 | -6,5 | 40 | 0,6 | 2 | 22,8 | 3 | -10,4 | não concluir (menos de 10 ordens) |
| A | (nenhum fato nos 60 dias) | 220 | 7,4 | 10,4 | 88 | 3,7 | 97 | 7,7 | 123 | 7,1 | sim |
| B | aquisicao | 1 | 6,8 | 6,8 | 100 | -1,9 | 1 | 6,8 | 0 | - | não concluir (menos de 10 ordens) |
| B | emissao | 13 | 19,7 | 21,3 | 92 | 17,5 | 11 | 24,6 | 2 | -6,9 | sim |
| B | locacao_nova | 2 | 16,2 | 16,2 | 100 | 13,2 | 1 | 16,2 | 1 | 16,3 | não concluir (menos de 10 ordens) |
| B | outro | 15 | 12,3 | 16,3 | 93 | 9,0 | 6 | 16,7 | 9 | 9,4 | sim |
| B | recebimento | 1 | 19,5 | 19,5 | 100 | 17,8 | 1 | 19,5 | 0 | - | não concluir (menos de 10 ordens) |
| B | rendimento_aumento | 4 | 24,6 | 23,6 | 100 | 21,9 | 2 | 34,3 | 2 | 14,9 | não concluir (menos de 10 ordens) |
| B | rendimento_reducao | 8 | 12,4 | 13,6 | 88 | 6,9 | 5 | 17,1 | 3 | 4,5 | não concluir (menos de 10 ordens) |
| B | reorganizacao | 7 | -2,1 | 7,9 | 57 | -6,3 | 5 | -10,0 | 2 | 17,9 | não concluir (menos de 10 ordens) |
| B | saida_inquilino | 6 | 13,4 | 17,9 | 67 | 8,7 | 3 | 19,5 | 3 | 7,2 | não concluir (menos de 10 ordens) |
| B | venda | 7 | 12,8 | 12,5 | 86 | 8,3 | 3 | 17,6 | 4 | 9,1 | não concluir (menos de 10 ordens) |
| B | venda_com_ganho | 4 | 14,0 | 16,8 | 75 | 12,3 | 3 | 22,8 | 1 | -12,4 | não concluir (menos de 10 ordens) |
| B | (nenhum fato nos 60 dias) | 108 | 10,9 | 13,7 | 88 | 7,7 | 56 | 12,4 | 52 | 9,3 | sim |
| C | aquisicao | 3 | 3,2 | 3,3 | 67 | -2,8 | 1 | -2,7 | 2 | 6,2 | não concluir (menos de 10 ordens) |
| C | emissao | 16 | 19,4 | 17,8 | 100 | 18,3 | 16 | 19,4 | 0 | - | sim |
| C | locacao_nova | 16 | 10,6 | 12,0 | 94 | 8,0 | 9 | 8,9 | 7 | 12,8 | sim |
| C | outro | 19 | 7,2 | 11,0 | 95 | 4,8 | 9 | 3,5 | 10 | 10,5 | sim |
| C | recebimento | 2 | 15,1 | 15,1 | 100 | 12,8 | 2 | 15,1 | 0 | - | não concluir (menos de 10 ordens) |
| C | rendimento_aumento | 12 | 11,5 | 11,5 | 100 | 9,2 | 5 | 11,9 | 7 | 11,2 | sim |
| C | rendimento_reducao | 6 | 15,5 | 16,2 | 100 | 13,0 | 5 | 15,3 | 1 | 16,3 | não concluir (menos de 10 ordens) |
| C | reorganizacao | 10 | -0,5 | 7,0 | 60 | -4,7 | 8 | -4,2 | 2 | 14,4 | sim |
| C | saida_inquilino | 9 | 8,2 | 10,8 | 78 | 5,0 | 5 | 9,5 | 4 | 6,5 | não concluir (menos de 10 ordens) |
| C | venda | 10 | 11,3 | 11,2 | 100 | 8,5 | 4 | 14,3 | 6 | 9,2 | sim |
| C | venda_com_ganho | 5 | 2,9 | -6,5 | 40 | 0,6 | 2 | 22,8 | 3 | -10,4 | não concluir (menos de 10 ordens) |
| C | (nenhum fato nos 60 dias) | 188 | 8,3 | 10,6 | 90 | 4,7 | 86 | 7,8 | 102 | 8,7 | sim |

Legenda: ordens = ordens com pelo menos um fato desse tipo nos 60 dias antes do sinal (uma ordem pode estar em várias linhas); média e mediana (%) = Resultado (%) das ordens; % positivas = ordens com resultado maior que zero; excesso = média de (Resultado % − 105% do CDI bruto no mesmo período e valor), em p.p.; esc/conf/tot = entradas 2018-2022 / 2023-2026 / todas. 'nenhum fato nos 60 dias' = ordens (de fundos com cobertura) sem fato algum, de qualquer tipo, na janela.

**Leitura prática:** Ordens com fato de emissão de cotas nos 60 dias antes do sinal foram as de melhor resultado (A 16,9% com 19 ordens; B 19,7% com 13; C 19,4% com 16), e "reorganização" as piores (A −0,1% com 11; C −0,5% com 10), mas esse tema é "neutro" para a classificação e ela erra, as ordens se sobrepõem e as médias vêm de poucas ordens. Linhas com menos de 10 ordens estão marcadas e não devem ser lidas.

### 6d. Só nos dias de queda geral

Interpretação: carteira C (que já é só de queda geral; todas as 292 ordens têm 'Fundos caídos no dia' de 15,4% ou mais, então C é idêntica à 6a/6b) e ordens da carteira A com 'Fundos caídos no dia (%)' ≥ 15. Como comparação extra, ordens da A com menos de 15 (queda só do fundo).

Ordens por subconjunto (de fundos com cobertura): C (todas: queda geral): 276; A com fundos caídos no dia ≥ 15%: 265; A com fundos caídos no dia < 15% (extra): 57.

6a negativo def.1, 60 dias. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| subconjunto | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C (todas: queda geral) | escolha 2018-2022 | 0 | 131 | 9,0 | 10,8 | 86 | 6,0 | -70,1 | -14,1 | 156 | 8 |
| C (todas: queda geral) | escolha 2018-2022 | 1 | 9 | 9,8 | 15,6 | 89 | 6,7 | -20,0 | -13,4 | 158 | 0 |
| C (todas: queda geral) | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| C (todas: queda geral) | conferência 2023-2026 | 0 | 131 | 8,7 | 11,2 | 94 | 5,1 | -76,6 | -8,2 | 101 | 2 |
| C (todas: queda geral) | conferência 2023-2026 | 1 | 4 | 7,9 | 9,7 | 75 | 4,9 | -4,1 | -6,7 | 83 | 0 |
| C (todas: queda geral) | conferência 2023-2026 | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |
| C (todas: queda geral) | total | 0 | 262 | 8,9 | 10,9 | 90 | 5,6 | -76,6 | -11,1 | 128 | 5 |
| C (todas: queda geral) | total | 1 | 13 | 9,2 | 13,3 | 85 | 6,2 | -20,0 | -11,4 | 135 | 0 |
| C (todas: queda geral) | total | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 0 | 127 | 8,9 | 10,8 | 86 | 6,0 | -70,1 | -14,3 | 158 | 9 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 1 | 9 | 9,8 | 15,6 | 89 | 6,7 | -20,0 | -13,4 | 158 | 0 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 0 | 125 | 8,9 | 11,2 | 94 | 5,3 | -76,6 | -8,3 | 102 | 2 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 1 | 3 | 7,1 | 9,1 | 67 | 3,9 | -4,1 | -5,3 | 88 | 0 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |
| A com fundos caídos no dia ≥ 15% | total | 0 | 252 | 8,9 | 11,0 | 90 | 5,6 | -76,6 | -11,3 | 130 | 5 |
| A com fundos caídos no dia ≥ 15% | total | 1 | 12 | 9,1 | 14,5 | 83 | 6,0 | -20,0 | -11,4 | 141 | 0 |
| A com fundos caídos no dia ≥ 15% | total | 2 ou mais | 1 | 10,8 | 10,8 | 100 | 7,4 | 10,8 | -3,8 | 103 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 0 | 16 | 8,4 | 9,7 | 81 | 5,9 | -10,6 | -10,2 | 113 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 1 | 3 | 9,6 | 9,3 | 67 | 4,9 | -3,2 | -20,0 | 166 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 0 | 35 | -0,4 | 5,9 | 74 | -4,7 | -69,6 | -14,7 | 125 | 6 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 1 | 2 | 4,8 | 4,8 | 50 | -2,4 | -11,1 | -24,2 | 202 | 0 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 2 ou mais | 1 | 16,9 | 16,9 | 100 | 13,9 | 16,9 | -3,7 | 104 | 0 |
| A com fundos caídos no dia < 15% (extra) | total | 0 | 51 | 2,4 | 6,3 | 76 | -1,4 | -69,6 | -13,3 | 121 | 4 |
| A com fundos caídos no dia < 15% (extra) | total | 1 | 5 | 7,7 | 9,3 | 60 | 2,0 | -11,1 | -21,7 | 181 | 0 |
| A com fundos caídos no dia < 15% (extra) | total | 2 ou mais | 1 | 16,9 | 16,9 | 100 | 13,9 | 16,9 | -3,7 | 104 | 0 |

6b positivo (i), 60 dias. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| subconjunto | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C (todas: queda geral) | escolha 2018-2022 | 0 | 126 | 8,7 | 10,7 | 86 | 5,6 | -70,1 | -14,0 | 158 | 9 |
| C (todas: queda geral) | escolha 2018-2022 | 1 | 11 | 12,6 | 12,9 | 91 | 10,4 | -2,7 | -13,6 | 140 | 0 |
| C (todas: queda geral) | escolha 2018-2022 | 2 ou mais | 3 | 11,8 | 10,8 | 100 | 9,3 | 10,8 | -14,0 | 117 | 0 |
| C (todas: queda geral) | conferência 2023-2026 | 0 | 117 | 8,9 | 11,0 | 95 | 5,2 | -76,6 | -8,5 | 105 | 2 |
| C (todas: queda geral) | conferência 2023-2026 | 1 | 16 | 7,2 | 11,5 | 81 | 4,7 | -16,5 | -6,4 | 70 | 0 |
| C (todas: queda geral) | conferência 2023-2026 | 2 ou mais | 3 | 9,2 | 10,1 | 100 | 6,4 | 4,7 | -1,2 | 79 | 0 |
| C (todas: queda geral) | total | 0 | 243 | 8,8 | 10,8 | 90 | 5,4 | -76,6 | -11,4 | 133 | 5 |
| C (todas: queda geral) | total | 1 | 27 | 9,4 | 12,2 | 85 | 7,0 | -16,5 | -9,4 | 99 | 0 |
| C (todas: queda geral) | total | 2 ou mais | 6 | 10,5 | 10,8 | 100 | 7,9 | 4,7 | -7,6 | 98 | 0 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 0 | 122 | 8,6 | 10,7 | 85 | 5,5 | -70,1 | -14,3 | 160 | 9 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 1 | 11 | 12,6 | 12,9 | 91 | 10,4 | -2,7 | -13,6 | 140 | 0 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 2 ou mais | 3 | 11,8 | 10,8 | 100 | 9,3 | 10,8 | -14,0 | 117 | 0 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 0 | 112 | 9,1 | 11,2 | 95 | 5,3 | -76,6 | -8,6 | 106 | 2 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 1 | 14 | 7,4 | 11,8 | 79 | 4,8 | -16,5 | -6,5 | 73 | 0 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 2 ou mais | 3 | 9,2 | 10,1 | 100 | 6,4 | 4,7 | -1,2 | 79 | 0 |
| A com fundos caídos no dia ≥ 15% | total | 0 | 234 | 8,8 | 10,9 | 90 | 5,4 | -76,6 | -11,6 | 134 | 6 |
| A com fundos caídos no dia ≥ 15% | total | 1 | 25 | 9,7 | 12,6 | 84 | 7,3 | -16,5 | -9,7 | 103 | 0 |
| A com fundos caídos no dia ≥ 15% | total | 2 ou mais | 6 | 10,5 | 10,8 | 100 | 7,9 | 4,7 | -7,6 | 98 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 0 | 18 | 8,4 | 8,9 | 78 | 5,5 | -10,6 | -12,0 | 125 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 1 | 1 | 11,7 | 11,7 | 100 | 9,2 | 11,7 | -6,1 | 65 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 2 ou mais | 0 | - | - | - | - | - | - | - | - |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 0 | 33 | 0,0 | 6,3 | 73 | -4,3 | -69,6 | -15,7 | 126 | 6 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 1 | 4 | 2,4 | 1,8 | 75 | -2,2 | -4,8 | -9,8 | 132 | 0 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 2 ou mais | 1 | 2,5 | 2,5 | 100 | -3,6 | 2,5 | -9,9 | 189 | 0 |
| A com fundos caídos no dia < 15% (extra) | total | 0 | 51 | 3,0 | 7,3 | 75 | -0,9 | -69,6 | -14,4 | 125 | 4 |
| A com fundos caídos no dia < 15% (extra) | total | 1 | 5 | 4,2 | 3,2 | 80 | 0,1 | -4,8 | -9,1 | 119 | 0 |
| A com fundos caídos no dia < 15% (extra) | total | 2 ou mais | 1 | 2,5 | 2,5 | 100 | -3,6 | 2,5 | -9,9 | 189 | 0 |

6b positivo (ii), entre entrada e saída. Aviso: tipo e sentido dos fatos foram classificados por palavras (fii/classificar.py) e erram; ver a medida do erro na seção 0.

| subconjunto | período | grupo | ordens | média (%) | mediana (%) | % positivas | excesso médio s/ 105% CDI bruto (p.p.) | pior ordem (%) | maior queda média abaixo da entrada (%) | dias corridos médios | % saiu por prazo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C (todas: queda geral) | escolha 2018-2022 | 0 | 114 | 9,7 | 11,2 | 88 | 6,9 | -70,1 | -13,0 | 148 | 7 |
| C (todas: queda geral) | escolha 2018-2022 | 1 | 17 | 8,4 | 10,4 | 94 | 5,7 | -37,1 | -16,2 | 167 | 12 |
| C (todas: queda geral) | escolha 2018-2022 | 2 ou mais | 9 | 1,4 | 7,0 | 56 | -3,8 | -33,5 | -22,7 | 238 | 11 |
| C (todas: queda geral) | conferência 2023-2026 | 0 | 123 | 8,8 | 11,2 | 93 | 5,3 | -76,6 | -8,2 | 99 | 2 |
| C (todas: queda geral) | conferência 2023-2026 | 1 | 10 | 8,1 | 10,3 | 90 | 4,5 | -16,5 | -7,1 | 100 | 0 |
| C (todas: queda geral) | conferência 2023-2026 | 2 ou mais | 3 | 8,5 | 6,8 | 100 | 2,8 | 5,9 | -8,8 | 168 | 0 |
| C (todas: queda geral) | total | 0 | 237 | 9,2 | 11,2 | 91 | 6,1 | -76,6 | -10,5 | 122 | 4 |
| C (todas: queda geral) | total | 1 | 27 | 8,3 | 10,4 | 93 | 5,3 | -37,1 | -12,8 | 142 | 7 |
| C (todas: queda geral) | total | 2 ou mais | 12 | 3,2 | 6,9 | 67 | -2,1 | -33,5 | -19,2 | 220 | 8 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 0 | 110 | 9,7 | 11,2 | 87 | 6,9 | -70,1 | -13,3 | 150 | 7 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 1 | 17 | 8,4 | 10,4 | 94 | 5,7 | -37,1 | -16,2 | 167 | 12 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 2 ou mais | 9 | 1,4 | 7,0 | 56 | -3,8 | -33,5 | -22,7 | 238 | 11 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 0 | 119 | 8,9 | 11,2 | 93 | 5,3 | -76,6 | -8,3 | 100 | 2 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 1 | 8 | 8,9 | 11,0 | 88 | 4,8 | -16,5 | -6,8 | 113 | 0 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 2 ou mais | 2 | 9,3 | 9,3 | 100 | 3,4 | 5,9 | -8,6 | 169 | 0 |
| A com fundos caídos no dia ≥ 15% | total | 0 | 229 | 9,3 | 11,2 | 90 | 6,1 | -76,6 | -10,7 | 124 | 4 |
| A com fundos caídos no dia ≥ 15% | total | 1 | 25 | 8,5 | 10,4 | 92 | 5,4 | -37,1 | -13,2 | 150 | 8 |
| A com fundos caídos no dia ≥ 15% | total | 2 ou mais | 11 | 2,9 | 7,0 | 64 | -2,5 | -33,5 | -20,1 | 225 | 9 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 0 | 16 | 9,6 | 9,9 | 81 | 6,7 | -3,2 | -11,6 | 121 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 1 | 2 | 10,1 | 10,1 | 100 | 8,3 | 9,3 | -4,5 | 74 | 0 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 2 ou mais | 1 | -10,6 | -10,6 | 0 | -14,7 | -10,6 | -29,0 | 225 | 0 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 0 | 31 | 0,5 | 6,3 | 71 | -3,7 | -69,6 | -15,2 | 120 | 3 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 1 | 4 | -2,9 | 3,2 | 75 | -8,2 | -34,7 | -13,2 | 150 | 25 |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 2 ou mais | 3 | 3,3 | 2,5 | 100 | -2,5 | 0,8 | -14,9 | 184 | 0 |
| A com fundos caídos no dia < 15% (extra) | total | 0 | 47 | 3,6 | 8,4 | 74 | -0,2 | -69,6 | -13,9 | 120 | 2 |
| A com fundos caídos no dia < 15% (extra) | total | 1 | 6 | 1,4 | 7,6 | 83 | -2,7 | -34,7 | -10,3 | 125 | 17 |
| A com fundos caídos no dia < 15% (extra) | total | 2 ou mais | 4 | -0,1 | 1,6 | 75 | -5,6 | -10,6 | -18,4 | 194 | 0 |

Legenda: igual à 6a; subconjunto = quais ordens entram. As visões de 30 dias e os testes estão em planilhas/auditoria_bloco3_6d_grupos.csv e planilhas/auditoria_bloco3_6d_testes.csv.

**Leitura prática:** Em dias de queda geral (carteira C, que é idêntica à da 6a/6b, e carteira A com 15% ou mais de fundos caídos, quase o mesmo conjunto) o quadro é igual ao anterior: sem fato 8,9%, com fato (1 ou mais) 9,3%, e as contas por grupo têm pouquíssimas ordens com fato. O extra "A com menos de 15% de fundos caídos" (queda só do fundo) teve resultado menor (2,4% nas 51 ordens sem fato; excesso −1,4 ponto sobre 105% do CDI), mas são só 57 ordens, uma delas com −69,6%, então vale como pista, não como conclusão.

Teste simples dentro dos dias de queda geral (Resultado %, sem contra com; p otimista, ordens se sobrepõem):

| subconjunto | período | ordens sem | ordens com | média sem | média com | diferença (sem − com) | IC95 inferior | IC95 superior | p Mann-Whitney |
|---|---|---|---|---|---|---|---|---|---|
| C (todas: queda geral) | escolha 2018-2022 | 131 | 9 | 9,0 | 9,8 | -0,8 | -8,7 | 8,8 | 0,439 |
| C (todas: queda geral) | conferência 2023-2026 | 131 | 5 | 8,7 | 8,5 | 0,3 | -5,2 | 6,9 | 0,753 |
| C (todas: queda geral) | total | 262 | 14 | 8,9 | 9,3 | -0,5 | -5,9 | 5,8 | 0,533 |
| A com fundos caídos no dia ≥ 15% | escolha 2018-2022 | 127 | 9 | 8,9 | 9,8 | -0,9 | -8,7 | 8,5 | 0,452 |
| A com fundos caídos no dia ≥ 15% | conferência 2023-2026 | 125 | 4 | - | - | - | - | - | - |
| A com fundos caídos no dia ≥ 15% | total | 252 | 13 | 8,9 | 9,3 | -0,3 | -6,3 | 6,5 | 0,515 |
| A com fundos caídos no dia < 15% (extra) | escolha 2018-2022 | 16 | 3 | - | - | - | - | - | - |
| A com fundos caídos no dia < 15% (extra) | conferência 2023-2026 | 35 | 3 | - | - | - | - | - | - |
| A com fundos caídos no dia < 15% (extra) | total | 51 | 6 | 2,4 | 9,2 | -6,8 | -17,7 | 4,6 | 0,365 |

Legenda: como a dos testes da 6a (definição 1, janela de 60 dias).

**Leitura prática:** Dentro dos dias de queda geral, a diferença entre sem fato e com fato negativo é de −0,5 ponto (C total; intervalo −5,9 a +5,8, p = 0,53): não dá para distinguir de zero. Onde há "-" não há 5 ordens em um dos grupos.

### Números para a tabela de lacunas

| medida | valor |
|---|---|
| fatos com texto menor que 600 caracteres | 8 |
| fatos com menos de 60% de letras nos primeiros 3.000 caracteres (provável imagem/slide mal lido) | 3 |
| fatos cujo texto guardado tem exatamente 3.000 caracteres (cortados) | 3.466 |
| fatos cujos primeiros 3.000 caracteres não trazem a expressão 'FATO RELEVANTE' | 158 |
| ordens de fundos sem nenhum fato na planilha | 44 |
| fundos das ordens sem nenhum fato na planilha | 15 |

**Leitura prática:** Só 8 textos têm menos de 600 caracteres e 3 parecem ser quase só símbolos, mas isso não mede imagens: anúncio que é só imagem ou PDF escaneado não deixa texto para contar. E 3.466 dos 7.962 textos foram cortados em 3.000 caracteres.

### Conferência à mão (contas refeitas por outro caminho no próprio programa)

Ordem 1 do arquivo: carteira A, FIGS11, sinal 08/05/2018, entrada 09/05/2018, saída 19/03/2019
  resultado = valorização -339.87 + rendimentos 324.99 − taxas 1.66 − imposto 0.00 = -16.54; coluna Resultado (R$) = -16.55; bate: True
  resultado % = -16.55 ÷ 2944.50 = -0.562%  (coluna: -0.6%)
  105% CDI: índice em 09/05/2018 = 1.130744; em 19/03/2019 = 1.195315; bruto = 2944.50 × (1.195315 ÷ 1.130744 − 1) = 168.14 R$ (5.710%); programa: 168.14; bate: True
  líquido (314 dias corridos, IR 20.0%): 134.52 R$; programa: 134.52; bate: True
  excesso sobre 105% CDI bruto = -0.562 − 5.710 = -6.273 p.p.; programa: -6.273
  fatos negativos (sentido queda, sem repetidos/continuações) de FIGS11 de 60 a 0 dias antes do sinal, contados em laço: []; 30 dias: 0, 60 dias: 0; programa: 0 e 0; bate: True

Ordem 14 do arquivo: carteira A, GRLV11, sinal 25/09/2018, entrada 26/09/2018, saída 16/04/2019
  resultado = valorização 651.31 + rendimentos 139.19 − taxas 1.94 − imposto 129.87 = 658.69; coluna Resultado (R$) = 658.68; bate: True
  resultado % = 658.68 ÷ 2913.69 = 22.606%  (coluna: 22.6%)
  105% CDI: índice em 26/09/2018 = 1.159709; em 16/04/2019 = 1.201510; bruto = 2913.69 × (1.201510 ÷ 1.159709 − 1) = 105.02 R$ (3.604%); programa: 105.02; bate: True
  líquido (202 dias corridos, IR 20.0%): 84.02 R$; programa: 84.02; bate: True
  excesso sobre 105% CDI bruto = 22.606 − 3.604 = 19.002 p.p.; programa: 19.002
  fatos negativos (sentido queda, sem repetidos/continuações) de GRLV11 de 60 a 0 dias antes do sinal, contados em laço: [(32806, '24/09/2018', 1)]; 30 dias: 1, 60 dias: 1; programa: 1 e 1; bate: True

**Leitura prática:** As duas contas (uma ordem sem fato e uma com fato) batem: o resultado refeito pelas parcelas, a régua de 105% do CDI refeita pelos índices e a contagem de fatos refeita em laço dão o mesmo que o programa.



### Tabela de lacunas

| Dado | Situação | Efeito |
|---|---|---|
| Classificação dos fatos (tipo e sentido) | Feita por palavras (`fii/classificar.py`); a leitura de 40 textos achou 10 de 20 "queda" e 7 de 20 "alta" mal classificados (quase todos anúncios de emissão ou venda, e aquisição lida como venda) | Todos os grupos "com fato negativo/positivo" estão contaminados; os números mostram o que a regra de palavras separa, não o que o fundo realmente anunciou. Falta uma leitura correta (por pessoa ou por modelo) de todos os fatos |
| Texto dos fatos | `fatos_textos.csv.gz` guarda só os 3.000 primeiros caracteres; 3.466 dos 7.962 textos estão cortados. O classificador usou o texto inteiro | Em vários casos a frase que decidiu o tipo estava fora do que pude ler; marquei "duvidoso" ou "mal classificado" só com o que se lê. Erro real da classificação pode ser maior ou menor que o medido |
| Fatos que são imagem sem texto | Só 8 textos têm menos de 600 caracteres e 3 parecem quase só símbolos; anúncios só em imagem/PDF escaneado não deixam texto e não dá para contá-los na base | Esses fatos aparecem como "outro/neutro" ou nem aparecem; podem estar em ordens contadas como "sem notícia" |
| Comunicados ao mercado e outros documentos (relatórios gerenciais, atas) | Não foram baixados; a base tem só os 7.962 fatos relevantes (alguns se intitulam "comunicado ao mercado") | "Sem notícia" quer dizer "sem fato relevante na base", não "sem nenhuma informação pública" |
| 15 fundos sem nenhum fato na base (44 ordens) | Fundos: AEFI11, AGCX11, ASMT11, BBVJ11, CRFF11, CXCI11, FIIP11, IFIE11, INLG11, MGLG11, OUCY11, RBCO11, RBOP11, TRBL11, UBSR11 | Ordens fora das comparações (764 de 808 usadas) |
| Cobertura por ano | Fatos por ano de anúncio: 2017 278, 2018 402, 2019 538, 2020 1.029, 2021 1.103, 2022 903, 2023 924, 2024 1.123, 2025 882, 2026 780 | Nos primeiros anos pode haver menos fatos coletados, o que inflaria "sem notícia" (só 34 ordens entram em 2018-2019) |
| Hora do anúncio | Só a data foi usada; fato publicado depois do pregão do dia do sinal entra na contagem | Pode contar como "conhecido" um fato que saiu depois da compra do sinal |
| Imposto das ordens | Vem do arquivo de ordens: 20% por ordem, sem compensar prejuízos entre ordens e sem atraso do DARF | Resultado (%) de cada ordem pode diferir do imposto real da carteira |
| Poucas ordens com fato | 45 ordens com fato negativo (60 dias) em 764; muitas linhas com menos de 10 ordens | Testes sem força; ausência de diferença não é prova de ausência de efeito |
| Ordens sobrepostas no tempo | Várias ordens entram nos mesmos dias de queda geral e o mesmo fato conta para várias | O p do Mann-Whitney é otimista; os intervalos de bootstrap também ficam estreitos demais |
| Ordens em aberto | 66 ordens valem pelo preço de 09/11/2026 | Resultado delas pode mudar |

---

