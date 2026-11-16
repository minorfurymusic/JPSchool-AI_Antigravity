# Estudo do índice de Kairi (quedas longas ou intensas)

Data: 2026-11-16. Ideia do dono. Programa: `estudos/kairi.py` (escrito e rodado por agente auxiliar; lê só das planilhas). Resultados completos: `planilhas/tecnico/kairi_configuracoes.csv` e `kairi_operacoes.csv`.

## Resultado em uma frase

**É o primeiro gatilho que ganhou da Selic líquida nos dois períodos**, o de escolha (2018 a 2022) e o de conferência (2023 a 2026): comprar o fundo quando a cota fica 15% a 20% abaixo da média de 200 pregões, com o rendimento mantido, e vender na volta à média. A ressalva é grande: o ganho vem de poucos episódios de queda geral do mercado.

## O que é

Índice de Kairi = quanto o preço está afastado da sua média móvel. Kairi de −20% na média de 200 pregões: a cota está 20% abaixo da média dos últimos 200 pregões.

## Regras testadas

- **Gatilho:** só o preço, sem anúncio. Sinal no dia em que a cota cruza para baixo o afastamento escolhido. **Entrada:** abertura do pregão seguinte.
- **Filtros fixos (regras do dono):** patrimônio de R$ 50 milhões ou mais; ordem de R$ 500 ou mais (2% do negociado por dia); fundo pagando rendimento; sem amortização relevante; cota entre 0,30 e 3,0 do valor patrimonial; XPPR11 e CARE11 fora.
- **O que variou (72 combinações):** média de 25, 75 ou 200 pregões; afastamento de 10%, 15%, 20% ou 30%; exigir ou não rendimento mantido (pelo menos 95% do de 126 pregões antes); três saídas.
- **Saídas:** (1) volta à média, com prazo máximo de 252 pregões; (2) prazo fixo de 120 pregões; (3) volta à média, saindo antes se o rendimento for cortado em 15% ou mais.
- **Conta completa:** valorização, rendimento, taxa de 0,03%, imposto de 20%, Selic líquida do mesmo período.
- **Guarda de dados:** operação que atravessa buraco ou salto absurdo de preço é descartada (88 de 19.866).
- **Períodos:** escolha = entradas até 2022; conferência = 2023 em diante.

"Acima da Selic" = resultado depois de custos e imposto, menos a Selic líquida do mesmo período.

## Média de 200 pregões (queda longa)

| Afastamento | Rendimento mantido | Saída | Escolha: operações | Escolha: acima da Selic | Conferência: operações | Conferência: acima da Selic | Conferência: ganharam da Selic | Conferência: pregões | Conferência: menor preço no caminho |
|---|---|---|---|---|---|---|---|---|---|
| 10% | sim | volta à média | 263 | +2,2% | 250 | +1,1% | 71% | 87 | −12,1% |
| 15% | não exigido | volta à média | 241 | +5,0% | 209 | +5,2% | 77% | 100 | −12,8% |
| 15% | sim | volta à média | 161 | +6,6% | 147 | +4,7% | 84% | 82 | −10,8% |
| 15% | sim | prazo de 120 | 165 | +4,7% | 136 | +4,4% | 76% | 116 | −11,1% |
| 15% | sim | volta à média ou corte | 168 | +6,9% | 157 | +3,9% | 77% | 67 | −9,5% |
| 20% | não exigido | volta à média | 139 | +10,4% | 106 | +8,2% | 78% | 110 | −14,4% |
| 20% | sim | volta à média | 94 | +12,1% | 66 | +6,2% | 85% | 93 | −12,0% |
| 20% | sim | prazo de 120 | 94 | +10,6% | 67 | +6,6% | 84% | 117 | −11,3% |
| 20% | sim | volta à média ou corte | 97 | +11,4% | 70 | +4,1% | 73% | 74 | −11,0% |
| 30% | não exigido | volta à média | 46 | +16,5% | 27 | −6,4% | 48% | 155 | −22,5% |
| 30% | não exigido | prazo de 120 | 48 | +16,8% | 30 | −6,2% | 50% | 111 | −20,1% |

A linha "20%, sim, volta à média ou corte" é a **aposta que defini antes de ver os dados**. Deu +11,4% na escolha e +4,1% na conferência.

Na conferência, com afastamento de 15% e rendimento mantido, saindo na volta à média: valorização média de +6,2%, rendimento de +3,7%, total depois de custos e imposto de +8,0%, contra Selic líquida de +3,2%, em 82 pregões.

## Comparação com compra ao acaso

3.000 compras sorteadas de fundos do mesmo universo, segurando 120 pregões:

| | Operações | Depois de custos e imposto | Selic líquida | Acima da Selic |
|---|---|---|---|---|
| Escolha | 1.350 | +0,7% | +2,7% | −2,0% |
| Conferência | 1.427 | +4,8% | +4,7% | +0,2% |

O Kairi de 200 pregões rende de 4 a 8 pontos a mais que comprar ao acaso, nos dois períodos.

## Médias curtas (25 e 75 pregões)

- **Queda rápida e funda não se sustentou.** Com média de 25 pregões e afastamento de 20% ou 30%, a escolha deu +10% a +27% e a conferência ficou perto de zero ou negativa.
- **Média de 75 pregões com 15%** foi positiva nos dois períodos (+3,9% e +3,9%), mais fraca que a de 200.
- **Afastamento de 30% falhou na conferência em todas as médias.** Queda grande demais costuma ser problema de verdade no fundo.

## O conjunto das 72 combinações

- Acima da Selic na escolha: 64 de 72. Na conferência: 46. **Nos dois: 38.**
- A relação entre o resultado na escolha e na conferência é positiva, mas fraca (0,21, numa escala de −1 a +1). Na busca por anúncios tinha sido negativa (−0,25).
- A combinação de maior resultado na escolha (média de 200, afastamento de 30%) **falhou** na conferência. Escolher o melhor número do passado continua sendo armadilha.

## Onde está o risco

**O ganho vem de poucos episódios.** Na aposta definida antes (afastamento de 20%, rendimento mantido), por ano de entrada:

| Ano | Operações | Depois de custos e imposto | Selic líquida | Acima da Selic | Ganharam da Selic |
|---|---|---|---|---|---|
| 2018 | 5 | +6,2% | +2,0% | +4,2% | 60% |
| 2019 | 2 | +10,9% | +1,1% | +9,8% | 50% |
| 2020 | 58 | +16,1% | +0,5% | +15,6% | 97% |
| 2021 | 25 | +6,5% | +2,8% | +3,7% | 64% |
| 2022 | 7 | +11,2% | +2,3% | +8,9% | 86% |
| 2023 | 5 | −11,0% | +4,0% | −15,0% | 0% |
| 2024 | 45 | +12,9% | +3,0% | +9,9% | 89% |
| 2025 | 15 | +3,9% | +2,9% | +1,0% | 67% |
| 2026 | 5 | −17,7% | +1,7% | −19,5% | 20% |

- **2020 (queda da pandemia) e 2024 (queda do fim do ano) concentram 103 das 167 operações.** São dois episódios, não 103 casos independentes.
- **Sem a queda de 2020, a escolha cai de +11,4% para +5,9%** (43 operações).
- **Quando o fundo cai sozinho, fora de uma queda geral, o resultado foi ruim:** 2023 e 2026 somam 10 operações, com −15% e −19%.
- **No caminho a cota ainda cai:** em média mais 11% a 12% abaixo da entrada antes de voltar.
- **Os sinais vêm todos juntos.** Em março de 2020 foram dezenas no mesmo mês. Com dinheiro limitado não dá para entrar em todos; falta simular isso.
- **Perdas grandes que a guarda de dados não pegou:** CACR11 (−66% em 2026), MGHT11 (−57% em 2024), MCEM11 (−47%). Falta conferir se são quedas reais ou erro de dados.

## Operações em aberto hoje (aposta definida antes)

| Fundo | Sinal | Entrada | Preço de entrada | Preço atual | Pregões | Valorização | Rendimento |
|---|---|---|---|---|---|---|---|
| MAXR11 | 10/07/2026 | 13/07/2026 | 48,02 | 55,56 | 82 | +15,7% | +2,5% |
| ITIT11 | 03/07/2026 | 06/07/2026 | 57,00 | 56,36 | 87 | −1,1% | +4,4% |
| RBHY11 | 17/08/2026 | 18/08/2026 | 61,29 | 55,05 | 56 | −10,2% | +4,6% |
| RBRR11 | 03/11/2026 | 04/11/2026 | 62,31 | 63,00 | 3 | +1,1% | 0,0% |
| RBRX11 | 03/11/2026 | 04/11/2026 | 6,26 | 6,40 | 3 | +2,2% | 0,0% |
| VINO11 | 03/11/2026 | 04/11/2026 | 3,85 | 4,03 | 3 | +4,7% | 0,0% |
| BCRI11 | 04/11/2026 | 05/11/2026 | 48,50 | 48,70 | 2 | +0,4% | 0,0% |
| OUJP11 | 04/11/2026 | 05/11/2026 | 62,43 | 63,33 | 2 | +1,4% | 0,0% |

Cinco sinais novos em dois dias de novembro de 2026: é o padrão de queda geral.

## Conclusão

- **Há um candidato a modelo:** média de 200 pregões, cota 15% a 20% abaixo dela, rendimento mantido, saída na volta à média. Bate com o que o estudo do conservador já tinha mostrado por outro caminho (fundo que cai com o rendimento mantido).
- **É um modelo de queda geral do mercado.** Rende quando tudo cai junto e volta; perde quando o fundo cai sozinho.
- **Ainda não está provado.** Os casos são muitos, mas os episódios são poucos.

## Conferência

- O agente refez 2 operações à mão (ALMI11 em 2018 e HCRI11 em 2021) e os números bateram com o programa.
- Pelo código, segundo o agente: o sinal usa só preços até o dia do sinal; a média da saída é calculada até a véspera; a escolha usa só o período de escolha.
- Eu não revisei o programa linha a linha. Listei as operações em aberto direto da planilha de operações.

## Próximos testes (a decidir pelo dono)

1. **Separar queda geral de queda isolada:** só entrar quando muitos fundos dão sinal ao mesmo tempo, ou quando o mercado inteiro está abaixo da sua média.
2. **Simular com dinheiro limitado** (R$ 10.000, ordens de R$ 500 a 2.000), já que os sinais vêm juntos.
3. **Conferir as perdas grandes** (CACR11, MGHT11, MCEM11): reais ou erro de dados.
4. **Juntar com os perfis:** agressivo e moderado pelo desconto sobre o valor patrimonial, dentro deste gatilho.

---

# Parte 2 — Regras expandidas (2026-11-16)

Programa: `estudos/kairi_expandido.py` (agente auxiliar). Planilhas: `planilhas/tecnico/kairi_exp_operacoes.csv` e `kairi_exp_grade.csv`. Saída completa: `dados/kairi_expandido.txt` (fora do repositório).

A base foi fixada antes de rodar: média de 200 pregões, rendimento mantido, saída na volta à média, com afastamento de 15% (B15) ou de 20% (B20). O programa reproduziu exatamente os números da Parte 1 antes de seguir.

Nas tabelas, cada célula é "operações / acima da Selic líquida". Escolha = entradas até 2022; conferência = 2023 em diante.

## Médias e afastamentos vizinhos (rendimento mantido, saída na volta à média)

| Média | 12% | 15% | 18% | 20% | 25% |
|---|---|---|---|---|---|
| 100 pregões, escolha | 193 / +4,6% | 140 / +7,5% | 95 / +12,7% | 79 / +14,4% | 55 / +20,1% |
| 100 pregões, conferência | 190 / +1,4% | 111 / +2,0% | 60 / +1,9% | 32 / +2,5% | 10 / −0,3% |
| 150 pregões, escolha | 212 / +3,9% | 156 / +8,1% | 113 / +12,4% | 90 / +14,6% | 53 / +18,6% |
| 150 pregões, conferência | 213 / +2,4% | 135 / +3,5% | 84 / +5,8% | 47 / +5,3% | 14 / +5,2% |
| 200 pregões, escolha | 217 / +3,5% | 161 / +6,6% | 123 / +10,1% | 94 / +12,1% | 51 / +17,1% |
| 200 pregões, conferência | 203 / +2,5% | 147 / +4,7% | 105 / +5,0% | 66 / +6,2% | 19 / +5,7% |
| 250 pregões, escolha | 202 / +1,8% | 164 / +3,9% | 122 / +6,6% | 104 / +8,6% | 49 / +12,2% |
| 250 pregões, conferência | 200 / +2,2% | 153 / +3,9% | 105 / +4,8% | 81 / +5,9% | 24 / +7,0% |

Das 40 combinações (contando também as sem exigência de rendimento mantido), 40 ficaram acima da Selic na escolha e 34 na conferência. **A regra não depende de um número exato.** Mas a ordem entre as combinações não se repete de um período para o outro (relação de 0,06): não dá para dizer qual é "a melhor".

## O que separa as operações boas das ruins (B15)

| Corte | Grupo | Escolha | Conferência |
|---|---|---|---|
| Mercado inteiro contra a sua média de 200 | 5% ou mais abaixo | 66 / +14,0% | 74 / +7,1% |
| | até 5% abaixo | 62 / +1,4% | 31 / +4,9% |
| | acima da média | 33 / +1,4% | 42 / +0,4% |
| Quantos fundos estão caídos no dia | queda geral (15% dos fundos ou mais) | 141 / +6,8% | 114 / +6,9% |
| | intermediária | 17 / +4,7% | 27 / −4,9% |
| | queda isolada (menos de 5%) | 3 / +6,2% | 6 / +7,8% |
| Queda do fundo além da do mercado | 15 pontos ou mais | 10 / +9,6% | 18 / −0,5% |
| | 8 a 15 pontos | 59 / −1,6% | 44 / +3,5% |
| | menos de 8 pontos | 92 / +11,5% | 85 / +6,5% |
| Cota sobre valor patrimonial | 0,30 a 0,60 | 16 / −0,3% | 36 / +0,1% |
| | 0,60 a 0,75 | 33 / +1,3% | 40 / +7,3% |
| | 0,75 a 0,90 | 72 / +9,4% | 64 / +7,4% |
| | acima de 0,90 | 40 / +8,6% | 7 / −10,5% |
| Ordem que o fundo aguenta | R$ 500 a 2.000 | 35 / +2,6% | 27 / −2,6% |
| | R$ 2.000 a 4.000 | 25 / +5,5% | 22 / +1,2% |
| | R$ 4.000 ou mais | 101 / +8,2% | 98 / +7,5% |
| Tipo de fundo | Lajes corporativas | 29 / +6,6% | 15 / +3,4% |
| | Logística | 19 / +10,7% | 16 / +5,9% |
| | Shoppings | 16 / +4,5% | 7 / +7,7% |
| | Outros | 91 / +6,0% | 108 / +4,5% |
| Selic nos 6 meses anteriores | subiu | 73 / 0,0% | 91 / +6,2% |
| | caiu | 81 / +12,0% | 30 / +0,1% |

- **Funciona quando o mercado caiu junto e o fundo caiu parecido com os outros.**
- **Fundo que caiu muito mais que o mercado, fundo pouco negociado e cota acima de 0,90 do valor patrimonial foram ruins na conferência.**
- **O perfil agressivo (cota de 0,30 a 0,60) empatou com a Selic nos dois períodos.** A faixa de 0,75 a 0,90 foi a melhor nos dois.
- **Tipo de fundo e direção da Selic não separam de forma consistente.**

## Saídas e entradas alternativas (B15)

| Regra | Escolha | Conferência |
|---|---|---|
| Saída na volta à média (base) | 161 / +6,6% | 147 / +4,7% |
| Volta à média, prazo máximo de 120 | 173 / +6,5% | 151 / +5,0% |
| Prazo fixo de 120 | 165 / +4,7% | 136 / +4,4% |
| Volta à média ou corte do rendimento | 168 / +6,9% | 157 / +3,9% |
| Meio caminho até a média | 196 / +4,4% | 173 / +3,3% |
| Alvo fixo de +10% | 188 / +3,6% | 170 / +3,4% |
| Volta à média com limite de perda de −20% | 180 / +2,7% | 154 / +4,7% |
| Volta à média com limite de perda de −30% | 164 / +4,2% | 152 / +4,7% |
| Entrada: esperar a cota parar de cair | 157 / +4,5% | 141 / +4,1% |
| Entrada: só se cair mais 5% | 76 / +9,0% | 63 / +3,5% |

**Nenhuma alternativa foi melhor que a regra simples.** Limite de perda não ajudou; esperar a cota virar também não.

## As perdas grandes

As 5 piores do B15: BRIM11 (−88,5%), TORD11 (−81,2%), MGHT11 (−79,2%), MCEM11 (−48,7%), CBOP11 (−45,7%).

- **MGHT11 e TORD11:** quedas com volume alto nos dias de queda. Parecem reais: fundos que afundaram de vez.
- **BRIM11:** saltos diários de 30% a 40% com volume de R$ 12 mil a R$ 80 mil. Série suspeita; conferir em outra fonte.
- **MCEM11:** sem negócio nos dias seguintes à queda; o preço de saída não tem compra e venda que o confirme.
- **A regra não tem proteção contra o fundo que quebra.** A única defesa testada que funciona é não concentrar: muitas posições pequenas.

---

# Parte 3 — Carteira com dinheiro limitado (2026-11-16)

Programa: `estudos/kairi_carteira.py` (agente auxiliar). Planilhas: `planilhas/tecnico/kairi_carteira_resumo.csv`, `kairi_carteira_operacoes.csv`, `kairi_carteira_patrimonio.csv`.

## Regras

- R$ 10.000 em 02/01/2018, até 09/11/2026 (2.201 pregões), um caixa só.
- **Carteira A:** afastamento de 15%. **Carteira B:** 20%. **Carteira C:** 15%, só em dia de queda geral. Todas com média de 200 pregões, rendimento mantido e saída na volta à média (prazo máximo de 252 pregões).
- **Ordem** de R$ 1.000, R$ 2.000 ou R$ 3.300, limitada a 2% do negociado por dia e ao caixa. Um fundo por vez. Com mais sinais que dinheiro, compra primeiro o fundo mais negociado.
- **Custos:** taxa de 0,03% por operação; imposto de 20% sobre o ganho do mês, com prejuízo abatendo depois; rendimento isento; caixa parado rende a Selic menos 22,5%.
- **Comparações:** tudo na Selic (mesma conta do caixa) e o mercado de fundos.

## Resultado

| Carteira | Ordem | Patrimônio final | Retorno total | Ao ano | Maior queda no caminho | Operações | Com ganho | Sinais sem dinheiro | 2018 a 2022 | 2023 a 2026 |
|---|---|---|---|---|---|---|---|---|---|---|
| A (15%) | R$ 1.000 | R$ 23.402 | +134,0% | 10,2% | −19,2% | 154 | 80% | 336 | +53,2% | +52,8% |
| A (15%) | R$ 2.000 | R$ 19.358 | +93,6% | 7,9% | −24,8% | 114 | 76% | 484 | +41,5% | +36,8% |
| A (15%) | R$ 3.300 | R$ 17.857 | +78,6% | 6,9% | −23,1% | 95 | 79% | 538 | +49,0% | +19,8% |
| B (20%) | R$ 1.000 | R$ 25.963 | +159,6% | 11,5% | −8,4% | 88 | 83% | 111 | +68,5% | +54,1% |
| B (20%) | R$ 2.000 | R$ 23.244 | +132,4% | 10,1% | −17,3% | 62 | 76% | 163 | +60,4% | +44,9% |
| B (20%) | R$ 3.300 | R$ 21.200 | +112,0% | 9,0% | −26,8% | 54 | 74% | 180 | +60,1% | +32,4% |
| C (15%, queda geral) | R$ 1.000 | R$ 23.216 | +132,2% | 10,1% | −18,9% | 107 | 84% | 328 | +44,8% | +60,4% |
| C (15%, queda geral) | R$ 2.000 | R$ 19.557 | +95,6% | 8,0% | −24,6% | 71 | 80% | 443 | +36,2% | +43,6% |
| C (15%, queda geral) | R$ 3.300 | R$ 16.574 | +65,7% | 6,0% | −24,5% | 55 | 78% | 497 | +38,3% | +19,9% |
| **Tudo na Selic** | — | R$ 18.332 | +83,3% | 7,2% | — | — | — | — | +27,0% | +44,4% |
| **Mercado de fundos** | — | R$ 14.899 | +49,0% | 4,7% | — | — | — | — | +21,1% | +23,0% |

## Retorno por ano

| Ano | A, R$ 1.000 | A, R$ 2.000 | B, R$ 1.000 | B, R$ 2.000 | C, R$ 1.000 | Tudo na Selic | Mercado |
|---|---|---|---|---|---|---|---|
| 2018 | +12,7% | +5,2% | +8,6% | +9,4% | +13,8% | +4,9% | +3,7% |
| 2019 | +7,0% | +10,0% | +7,3% | +11,2% | +5,2% | +4,6% | +24,9% |
| 2020 | +14,2% | +9,9% | +26,3% | +22,1% | +10,5% | +2,2% | −9,9% |
| 2021 | +2,8% | −4,9% | +5,4% | −0,7% | +0,6% | +3,4% | −0,5% |
| 2022 | +8,2% | +17,0% | +8,6% | +8,7% | +8,8% | +9,5% | +4,3% |
| 2023 | +12,6% | +1,8% | +7,2% | +4,8% | +13,1% | +10,0% | +17,1% |
| 2024 | +0,6% | −5,1% | +10,9% | +7,1% | +4,5% | +8,3% | −5,5% |
| 2025 | +20,2% | +28,4% | +22,0% | +25,0% | +17,4% | +10,9% | +15,1% |
| 2026 (até 09/11) | +12,2% | +10,3% | +6,2% | +3,2% | +15,6% | +9,2% | −3,5% |

## O que diz

- **Seis das nove carteiras ganharam da Selic no período todo.** A faixa vai de 6,0% a 11,5% ao ano, contra 7,2% da Selic líquida e 4,7% do mercado de fundos.
- **O tamanho da ordem pesa mais que a regra.** Com ordem de R$ 1.000 (dez posições), as três carteiras ganharam da Selic nos dois períodos. Com R$ 3.300 (três posições), duas das três perderam.
- **De 2023 em diante, só quatro das nove ganharam da Selic** (as três de R$ 1.000 e a B de R$ 2.000). Com a Selic alta, a folga é pequena.
- **Nenhuma carteira ganha todo ano.** A de afastamento de 15% com R$ 1.000 perdeu da Selic em 2021, 2022 e 2024. A de 20% com R$ 1.000 perdeu em 2022, 2023 e 2026.
- **O patrimônio chegou a cair de 8% a 27% no caminho**, sempre em março de 2020.
- **Faltou dinheiro para a maioria dos sinais:** de 111 a 538 ficaram de fora, porque chegam todos juntos.
- **Posições abertas hoje (carteira A, ordem de R$ 2.000): 13**, entre −29,7% (APXM11) e +14,0% (MAXR11).

## Limites

- **A melhor linha da tabela (afastamento de 20%, ordem de R$ 1.000) foi a melhor entre nove.** Não é o resultado esperado; é o teto do que foi visto.
- A diferença entre ordens (10,2% ao ano com R$ 1.000 e 6,9% com R$ 3.300, na mesma regra) mostra que o resultado depende muito de quais sinais o dinheiro alcançou. Parte disso é sorte.
- A compra é pela abertura e a venda pelo preço da média; em fundo pouco negociado isso é otimista.
- Os programas dos agentes não foram revisados linha a linha. Os agentes refizeram operações à mão (as contas bateram) e o da carteira confirmou, com testes automáticos dentro do programa, que o caixa nunca ficou negativo e que nenhum sinal virou compra no mesmo dia. Eu recalculei os retornos por ano a partir da planilha de patrimônio.
- Três avisos de rendimento estão duplicados na base e podem inflar um pouco os rendimentos.
- O período de conferência já foi visto mais de uma vez. A prova de verdade é daqui para a frente.

## Conclusão das três partes

- **O candidato a modelo ficou mais firme:** média de 200 pregões, cota 15% a 20% abaixo, rendimento mantido, saída na volta à média, em **ordens pequenas (perto de 10% do dinheiro cada)** e fundos bem negociados.
- **O que evitar:** fundo que caiu muito mais que o mercado, fundo pouco negociado, cota acima de 0,90 do valor patrimonial.
- **O ganho esperado é modesto:** alguns pontos por ano acima da Selic líquida, com anos em que perde e quedas de até um quarto do patrimônio no caminho.
- **Próximo passo natural:** colocar o sinal no app e acompanhar daqui para a frente, sem dinheiro de verdade, para ver se o resultado se repete em dados que ninguém viu.


---

# Parte 4 — Carteira infinita, saídas de Fibonacci, imposto com abatimento e cortes de rendimento (2026-11-16)

Pedido do dono. Programas: `estudos/kairi_ordens.py` e `estudos/kairi_saidas.py` (agentes auxiliares). Planilhas para leitura: `planilhas/kairi_ordens.csv` (uma linha por ordem), `planilhas/kairi_ordens_saidas.csv` (cada ordem em 7 regras de saída) e `planilhas/kairi_cortes.csv` (uma linha por corte de rendimento). Saída completa: `dados/kairi_saidas.txt` (fora do repositório).

## Regras

- **Carteira infinita:** todo sinal vira ordem; 40 sinais no mesmo dia são 40 ordens. Um fundo por vez.
- **Tamanho da ordem:** o menor entre R$ 3.000 e 5% do negociado por dia; abaixo de R$ 1.000 não entra (3 sinais ficaram de fora).
- **Sinal:** média de 200 pregões, rendimento mantido. Carteira A: cota 15% abaixo da média. B: 20%. C: 15%, só em queda geral.
- **Conta de cada ordem:** valorização e rendimentos em reais; taxa de 0,03% na compra e na venda; Selic líquida do mesmo dinheiro, do dia da entrada ao da saída.
- **Imposto:** 20% sobre o ganho do mês da venda, com prejuízo abatendo os ganhos seguintes.
- **Período:** entradas de 02/01/2018 a 09/11/2026. Escolha = entradas até 2022; conferência = 2023 em diante.

## Balanço ano a ano, carteira A (15%), saída na volta à média com prazo de 252

Pelo ano da entrada. Resultado antes do imposto, já com taxas.

| Ano | Ordens | Aplicado | Dias por ordem | Valorização | Rendimentos | Resultado | Resultado (%) | Selic líquida | Diferença (pontos) | Com resultado positivo | Queda média | Pior queda | Voltou ao preço de entrada | Pregões do fundo até voltar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 14 | R$ 38.113 | 166 | R$ 2.844 | R$ 1.413 | R$ 4.234 | 11,1% | R$ 848 | +8,9 | 86% | −9,8% | −29,0% ALMI11 | 86% | 13 |
| 2019 | 1 | R$ 2.944 | 139 | R$ 644 | R$ 153 | R$ 795 | 27,0% | R$ 50 | +25,3 | 100% | −22,2% | −22,2% XPCM11 | 100% | 84 |
| 2020 | 70 | R$ 201.019 | 139 | R$ 31.103 | R$ 4.290 | R$ 35.263 | 17,5% | R$ 1.619 | +16,7 | 90% | −16,8% | −42,7% HTMX11 | 93% | 4 |
| 2021 | 62 | R$ 176.607 | 163 | R$ 6.325 | R$ 7.017 | R$ 13.234 | 7,5% | R$ 5.483 | +4,4 | 81% | −11,4% | −46,5% HCRI11 | 77% | 8 |
| 2022 | 18 | R$ 45.893 | 177 | −R$ 2.006 | R$ 2.016 | −R$ 17 | 0,0% | R$ 2.232 | −4,9 | 78% | −15,7% | −71,7% TORD11 | 67% | 10 |
| 2023 | 21 | R$ 57.998 | 129 | R$ 4.506 | R$ 1.866 | R$ 6.335 | 10,9% | R$ 1.879 | +7,7 | 86% | −8,7% | −40,2% CBOP11 | 86% | 14 |
| 2024 | 85 | R$ 241.080 | 142 | R$ 12.667 | R$ 11.003 | R$ 23.522 | 9,8% | R$ 8.776 | +6,1 | 93% | −11,7% | −72,7% MGHT11 | 89% | 11 |
| 2025 | 25 | R$ 70.077 | 109 | R$ 5.896 | R$ 2.294 | R$ 8.147 | 11,6% | R$ 2.138 | +8,6 | 92% | −11,9% | −78,9% BRIM11 | 92% | 9 |
| 2026 | 45 (30 em aberto) | R$ 129.127 | 45 | — | — | R$ 3.021 | 2,3% | R$ 1.777 | +1,0 | 87% | −6,8% | −55,1% MCEM11 | 79% | 4 |
| **Total** | 341 | R$ 962.859 | 140 | R$ 65.711 | R$ 30.774 | R$ 94.534 | 9,8% | R$ 24.801 | +7,2 | 88% | −12,5% | −78,9% BRIM11 | 86% | 9 |

Valorização e rendimentos de 2018 a 2025 são das ordens fechadas; a linha de 2026 e o total do resultado incluem as 30 em aberto pelo preço de hoje. Imposto com abatimento, no total: R$ 13.033. **Resultado líquido: R$ 81.501, contra R$ 24.801 da Selic.**

Média das 10% piores quedas: −41,6%. Quando a ordem sai com ganho (273), a cota valorizou 11,2% em média; quando sai com perda (38), caiu 22,5%.

## Carteira B (20%), mesmo formato, resumido

| Ano | Ordens | Aplicado | Resultado antes do imposto | Resultado (%) | Selic líquida | Diferença (pontos) | Com resultado positivo |
|---|---|---|---|---|---|---|---|
| 2018 | 5 | R$ 11.640 | R$ 1.773 | 15,2% | R$ 284 | +12,8 | 80% |
| 2019 | 2 | R$ 5.842 | R$ 840 | 14,4% | R$ 159 | +11,7 | 100% |
| 2020 | 58 | R$ 168.278 | R$ 36.942 | 22,0% | R$ 1.517 | +21,1 | 91% |
| 2021 | 25 | R$ 72.184 | R$ 7.041 | 9,8% | R$ 2.652 | +6,1 | 80% |
| 2022 | 7 | R$ 19.205 | R$ 2.253 | 11,7% | R$ 835 | +7,4 | 100% |
| 2023 | 6 | R$ 14.886 | −R$ 318 | −2,1% | R$ 941 | −8,5 | 50% |
| 2024 | 44 | R$ 127.508 | R$ 20.655 | 16,2% | R$ 4.413 | +12,7 | 91% |
| 2025 | 15 | R$ 42.990 | R$ 6.423 | 14,9% | R$ 1.324 | +11,9 | 93% |
| 2026 | 13 (11 em aberto) | R$ 35.041 | −R$ 1.656 | −4,7% | R$ 517 | −6,2 | 50% |
| **Total** | 175 | R$ 497.574 | R$ 73.953 | 14,9% | R$ 12.642 | +12,3 | 88% |

Imposto com abatimento: R$ 11.796. **Resultado líquido: R$ 62.157, contra R$ 12.642 da Selic.**

## Dinheiro necessário

| | A (15%) | B (20%) | C (15%, queda geral) |
|---|---|---|---|
| Maior valor aplicado ao mesmo tempo | R$ 262.698 (10/02/2025) | R$ 151.506 (24/03/2020) | R$ 255.116 (10/02/2025) |
| Ordens abertas nesse dia | 92 | 52 | 89 |
| Valor médio aplicado por dia | R$ 38.936 | R$ 22.282 | R$ 33.216 |

Para aceitar todos os sinais é preciso ter o valor do pico disponível. Na maior parte do tempo, a maior parte dele fica parada.

## Qual saída rende mais

As saídas têm durações diferentes, então a comparação justa é o **retorno ao ano do dinheiro enquanto ele está aplicado**: resultado líquido dividido por (reais x dias aplicados / 365). A Selic está na mesma conta. Todas as ordens entram, as em aberto pelo preço de hoje.

Carteira A (341 ordens):

| Saída | Em aberto | Resultado líquido | Selic do mesmo dinheiro | Diferença | Retorno ao ano | Selic ao ano | Com resultado positivo | Pico de dinheiro |
|---|---|---|---|---|---|---|---|---|
| Volta à média, prazo de 252 (atual) | 30 | R$ 81.501 | R$ 24.801 | +R$ 56.699 | 23,5% | 7,1% | 88% | R$ 262.698 |
| Volta à média, sem prazo | 31 | R$ 80.545 | R$ 27.412 | +R$ 53.133 | 21,5% | 7,3% | 88% | R$ 267.572 |
| Volta à média, nunca abaixo da entrada, sem prazo | 44 | R$ 86.116 | R$ 50.229 | +R$ 35.887 | 15,9% | 9,3% | 96% | R$ 295.006 |
| Média do dia do sinal (congelada), sem prazo | 130 | R$ 146.090 | R$ 190.566 | −R$ 44.476 | 9,0% | 11,7% | 93% | R$ 459.260 |
| Fibonacci 38,2% da queda, sem prazo | 81 | R$ 104.263 | R$ 121.193 | −R$ 16.930 | 9,9% | 11,5% | 95% | R$ 352.794 |
| Fibonacci 50%, sem prazo | 116 | R$ 119.891 | R$ 180.299 | −R$ 60.408 | 7,8% | 11,7% | 93% | R$ 445.806 |
| Fibonacci 61,8%, sem prazo | 146 | R$ 144.623 | R$ 228.642 | −R$ 84.019 | 7,5% | 11,9% | 92% | R$ 517.424 |
| Fibonacci 100% (volta ao pico), sem prazo | 211 | R$ 182.962 | R$ 310.091 | −R$ 127.129 | 7,1% | 12,0% | 85% | R$ 620.942 |
| 127,2% da distância até a média, sem prazo | 164 | R$ 163.030 | R$ 240.784 | −R$ 77.754 | 8,0% | 11,8% | 90% | R$ 527.993 |
| 161,8% da distância até a média, sem prazo | 201 | R$ 171.822 | R$ 289.297 | −R$ 117.475 | 7,1% | 12,0% | 87% | R$ 592.618 |
| Fibonacci 50%, prazo de 252 | 31 | R$ 84.907 | R$ 47.105 | +R$ 37.802 | 14,7% | 8,1% | 79% | R$ 261.594 |
| 127,2% da distância, prazo de 252 | 37 | R$ 105.891 | R$ 59.447 | +R$ 46.444 | 14,8% | 8,3% | 79% | R$ 279.484 |

Nas três carteiras, e nos dois períodos, a ordem é a mesma. Retorno ao ano da saída atual: A 22,9% na escolha e 24,3% na conferência; B 32,5% e 29,1%; C 22,4% e 32,6%.

- **A volta à média foi a melhor saída em todas as carteiras e nos dois períodos.**
- **Os alvos de Fibonacci e as projeções acima da média dão mais reais no total, mas perdem da Selic.** O dinheiro fica preso muito mais tempo: de 81 a 211 das 341 ordens nunca chegam ao alvo e seguem abertas.
- **Tirar o prazo quase não muda nada** (21,5% contra 23,5% ao ano). O prazo de 252 pregões só atua em 15 das 341 ordens.
- **A média congelada foi ruim:** 95 ordens abertas há mais de 252 pregões, com a cota 27% abaixo da entrada em média.
- **"Nunca vender abaixo da entrada" aumenta os acertos (96%) e reduz o retorno** (15,9% ao ano), porque a espera custa tempo.

**Atenção:** o retorno ao ano acima vale para o dinheiro enquanto está aplicado. Não é o retorno de uma carteira, porque o dinheiro fica parado a maior parte do tempo. Para a carteira com dinheiro limitado, ver a Parte 3.

## A média cai abaixo do preço de entrada? (pergunta do dono)

| | A | B | C |
|---|---|---|---|
| Saídas pela volta à média | 284 | 146 | 247 |
| Com preço de saída abaixo da entrada | 37 | 13 | 26 |
| Dessas, a cota chegou a ficar acima da entrada antes | 31 | 9 | 22 |
| Maior alta média delas | +4,2% | +5,5% | +4,4% |
| Resultado médio delas | −3,0% | −5,9% | −3,5% |

**Sim, acontece em 1 de cada 8 saídas**, e em quase todas a cota tinha passado da entrada antes. Mas esperar para não vender abaixo da entrada rendeu menos no conjunto (tabela anterior).

## Preço sobre valor patrimonial na entrada e na saída

| Carteira | Regra de saída | Cota sobre valor patrimonial na entrada (média) | Na saída (média) |
|---|---|---|---|
| A | Extensão 127,2% da média do sinal (sem prazo) | 0,77 | 0,94 |
| A | Fibonacci 50% do pico (sem prazo) | 0,77 | 0,92 |
| A | Fibonacci 61,8% do pico (sem prazo) | 0,78 | 0,94 |
| A | Média dos 200 pregões do sinal (sem prazo) | 0,77 | 0,91 |
| A | Volta à média (prazo de 252 pregões) | 0,77 | 0,84 |
| A | Volta à média (sem prazo) | 0,77 | 0,85 |
| A | Volta à média, nunca abaixo da entrada (sem prazo) | 0,77 | 0,87 |
| B | Extensão 127,2% da média do sinal (sem prazo) | 0,72 | 0,88 |
| B | Fibonacci 50% do pico (sem prazo) | 0,73 | 0,87 |
| B | Fibonacci 61,8% do pico (sem prazo) | 0,73 | 0,90 |
| B | Média dos 200 pregões do sinal (sem prazo) | 0,72 | 0,87 |
| B | Volta à média (prazo de 252 pregões) | 0,73 | 0,83 |
| B | Volta à média (sem prazo) | 0,73 | 0,83 |
| B | Volta à média, nunca abaixo da entrada (sem prazo) | 0,73 | 0,85 |

Cada ordem tem os dois valores em `planilhas/kairi_ordens_saidas.csv`.

## Cortes de rendimento

Não é regra de saída; é análise. Corte = primeiro aviso, depois da entrada, 15% ou mais abaixo do rendimento da entrada. Medido na saída pela volta à média sem prazo.

| | A (15%) | B (20%) |
|---|---|---|
| Ordens | 341 | 175 |
| Tiveram corte enquanto abertas | 80 | 60 |
| Dessas, entradas de 2020 | 32 | 30 |
| O rendimento voltou (95% do da entrada em até 6 avisos) | 24 (30%) | 20 (33%) |
| Voltou: resultado de quem segurou / de quem sairia no corte | +9,7% / 0,0% | +16,2% / +5,2% |
| Não voltou: resultado de quem segurou / de quem sairia no corte | +2,5% / +3,2% | +7,3% / +7,2% |
| Cortes sem fato relevante do fundo por perto | 56 de 80 | 39 de 60 |

- **Sair no corte não ajuda.** Quando o rendimento volta, quem sai perde quase 10 pontos; quando não volta, tanto faz.
- **O corte foi passageiro em 1 de cada 3 casos**, não na maioria.
- **Sete em cada dez cortes não têm fato relevante do fundo por perto**; os que têm são, na maioria, saída de inquilino.
- A lista para ler caso a caso está em `planilhas/kairi_cortes.csv` (140 linhas), com o rendimento antes, o do corte, os seis avisos seguintes e o fato relevante mais próximo. Há 6 cortes de 90% ou mais (BBVJ11, CNES11, FVPQ11, RBGS11 em março de 2020) que podem ser erro de dados.

## Dados suspeitos

Ordens que têm, entre 200 pregões antes do sinal e a saída, alguma variação de mais de 25% num dia: 13 de 341 na carteira A, 4 de 175 na B, 7 de 292 na C. Sem elas, o retorno ao ano muda pouco: A de 23,5% para 24,8%; B de 31,2% para 30,5%; C de 26,3% para 27,1%.

Nas planilhas de preços há 334 variações de mais de 25% num dia, em 128 fundos. A maioria não entra nas ordens, mas a base precisa dessa limpeza.

## Conferência

- O programa novo reproduziu as 808 ordens do anterior, uma a uma (data, motivo, preço, cotas e resultado).
- Os agentes refizeram ordens à mão (BBVJ11, FIGS11) e as contas bateram; o abatimento do imposto foi mostrado mês a mês.
- Testes dentro do programa confirmaram que os alvos usam só informação até o dia do sinal.
- Eu calculei a tabela de preço sobre valor patrimonial direto da planilha de ordens. Não revisei os programas linha a linha.
- TORD11 aparece com último preço de R$ 0,97 (−97,5%); a conferir.

## Conclusão da Parte 4

- **Não achei saída melhor que a volta à média.** A ideia de alvo por Fibonacci aumenta o lucro por ordem e o acerto, mas prende o dinheiro e perde da Selic no conjunto.
- **Sair por corte de rendimento não vale a pena.**
- **Com carteira infinita, todas as ordens somadas ganharam da Selic em 8 dos 9 anos (carteira A) e em 7 dos 9 (carteira B).**

---

# Parte 5 — Saída em escada (2026-11-16)

Ideia do dono: mirar o alvo de Fibonacci mais alto e, se a cota não chegar nele e recuar, sair no alvo de baixo ou na média. Programa: `estudos/kairi_escada.py` (agente auxiliar). Planilhas: `planilhas/kairi_escada.csv` (cada ordem das carteiras A e B em 4 regras) e `planilhas/tecnico/kairi_escada_comparacao.csv`. Saída completa: `dados/kairi_escada.txt` (fora do repositório).

Mesmas ordens da Parte 4 (carteira infinita; A = afastamento de 15%, B = 20%, C = 15% em queda geral). O programa reproduziu os números da saída atual antes de seguir.

## As ordens que não chegaram ao alvo de Fibonacci tocaram a média?

Sim, a maioria. Carteira A:

| Alvo (sem prazo) | Ordens que nunca chegaram ao alvo | Dessas, tocaram a média | Maior alta média sobre a entrada |
|---|---|---|---|
| Fibonacci 38,2% | 81 | 52 | +8,5% |
| Fibonacci 50% | 116 | 86 | +12,4% |
| Fibonacci 61,8% | 146 | 115 | +14,0% |
| Fibonacci 100% | 211 | 180 | +18,7% |

No ponto mais alto, essas ordens percorreram em média metade do caminho entre a entrada e o alvo.

E o inverso: das 284 ordens da carteira A que tocaram a média, quantas depois chegaram a cada nível.

| Nível | Chegaram depois | Pregões depois do toque na média (mediana) |
|---|---|---|
| Fibonacci 38,2% | 215 (76%) | 2 |
| Fibonacci 50% | 185 (65%) | 21 |
| Fibonacci 61,8% | 150 (53%) | 56 |
| Fibonacci 100% | 65 (23%) | 186 |

## A regra da escada

- A ordem mira o **teto**. Quando a cota toca o **piso**, ela não vende: fica armada.
- Armada, vende no teto se a cota chegar lá, ou no piso se a cota recuar até ele.
- Se piso e teto são tocados no mesmo dia, vale o piso. Se a cota abre abaixo do piso, vende na abertura.
- Se nunca arma, vale a reserva da regra atual: prazo de 252 pregões.

| Escada | Piso | Teto |
|---|---|---|
| 1 | média de 200 pregões | Fibonacci 61,8% |
| 2 | média | Fibonacci 50% |
| 3 | média | Fibonacci 100% |
| 4 | média | 127,2% da distância até a média |
| 5 | Fibonacci 38,2% | Fibonacci 61,8% |
| 6 | Fibonacci 38,2% | Fibonacci 100% |
| 7 | Fibonacci 50% | Fibonacci 100% |
| 8 | vários degraus: a cada nível tocado, o piso sobe para o anterior | Fibonacci 100% |
| 9 e 10 | arma na média; vende se o fechamento cair 5% ou 8% do maior desde então | sem teto |

## Resultado

Retorno ao ano do dinheiro enquanto aplicado, com imposto abatido e ordens em aberto pelo preço de hoje. Escolha = entradas até 2022; conferência = 2023 em diante.

| Regra | A: total | A: escolha | A: conferência | B: total | B: escolha | B: conferência | C: total | C: escolha | C: conferência |
|---|---|---|---|---|---|---|---|---|---|
| **Volta à média (atual)** | **23,5%** | **22,9%** | **24,3%** | **31,2%** | **32,5%** | **29,1%** | **26,3%** | **22,4%** | **32,6%** |
| Escada 1 | 21,5% | 20,5% | 22,9% | 29,5% | 30,5% | 27,7% | 24,3% | 20,2% | 31,2% |
| Escada 2 | 22,1% | 20,9% | 23,5% | 30,1% | 31,2% | 28,3% | 24,9% | 20,6% | 32,0% |
| Escada 3 | 20,6% | 19,6% | 21,9% | 28,2% | 29,1% | 26,7% | 23,3% | 19,3% | 30,1% |
| Escada 4 | 21,3% | 20,5% | 22,4% | 29,2% | 30,2% | 27,4% | 24,0% | 20,2% | 30,3% |
| Escada 5 | 16,7% | 14,5% | 19,6% | 27,6% | 29,4% | 25,6% | 20,1% | 15,4% | 27,4% |
| Escada 6 | 16,2% | 14,0% | 19,0% | 26,6% | 28,2% | 24,8% | 19,5% | 14,8% | 26,8% |
| Escada 7 | 13,6% | 10,5% | 17,9% | 20,1% | 19,2% | 21,4% | 17,6% | 12,6% | 25,9% |
| Escada 8 | 20,4% | 18,4% | 23,1% | 33,1% | 36,4% | 28,5% | 23,3% | 18,3% | 31,8% |
| Escada 9 (recuo de 5%) | 17,6% | 17,4% | 17,9% | 24,0% | 25,4% | 21,8% | 20,1% | 17,6% | 23,6% |
| Escada 10 (recuo de 8%) | 16,0% | 14,9% | 17,1% | 21,1% | 22,0% | 20,1% | 17,9% | 15,2% | 20,8% |

**Nenhuma das dez escadas ficou acima da volta à média nos dois períodos, em nenhuma das três carteiras.** A que chegou mais perto foi a escada 8 na carteira B: 36,4% contra 32,5% na escolha, mas 28,5% contra 29,1% na conferência.

Em reais, carteira A: a volta à média deu R$ 81.501 líquidos; a escada 1, R$ 76.448; a escada 8, R$ 65.831. A escada 10 deu mais reais (R$ 104.334), mas ficou com o dinheiro aplicado quase o dobro do tempo (265 dias contra 140) e a diferença para a Selic foi menor (R$ 50.621 contra R$ 56.699).

## Por que a escada não ajudou

Escada 1 na carteira A, pelo motivo da saída:

| Como saiu | Ordens | Dias | Resultado médio |
|---|---|---|---|
| Chegou ao teto | 10 | 75 | +28,8% |
| Saída simples (o teto estava abaixo da média; vendeu na média) | 89 | 134 | +16,4% |
| Recuou ao piso | 185 | 137 | +9,4% |
| Prazo | 15 | 371 | −25,0% |
| Fundo saiu da bolsa | 10 | 92 | −12,4% |

- **Depois de tocar a média, a cota recua muito mais vezes do que segue até o teto:** 185 recuos contra 10 chegadas.
- **O recuo custa.** A venda no recuo saiu em média 1,65% abaixo do piso, porque a cota abre abaixo dele, e 42 das 185 venderam abaixo do preço de entrada.
- **Ordem a ordem, contra a regra atual:** a escada 1 rendeu mais em 32 ordens (+2,8 pontos em média), menos em 162 (−2,2 pontos) e igual em 147.

## Conclusão

- **A volta à média continua sendo a melhor saída testada**, agora contra 22 alternativas (12 da Parte 4 e 10 escadas), nos dois períodos e nas três carteiras.
- **Vender logo ao tocar a média e liberar o dinheiro rende mais do que esperar o alvo de cima.** O ganho extra de quem chega ao teto não paga os recuos.
- **A escada de vários degraus (8) é a única que merece ser lembrada:** gira o dinheiro mais rápido (130 dias) e empata com a regra atual na carteira de 20%. Não há base para trocar.

## Conferência

- O programa reproduziu a saída atual: carteira A com R$ 81.501 e 23,5% ao ano; B com R$ 62.157 e 31,2%.
- O agente refez duas ordens à mão (GRLV11, que chegou ao teto, e ALMI11, que recuou ao piso) e os números bateram.
- Testes dentro do programa confirmaram, segundo o agente, que a ordem só arma com informação do próprio dia, que o piso usa a média até a véspera, e que no empate vale o piso.
- A soma por motivo de saída é igual ao número de ordens em todas as escadas.
- Eu não revisei o programa linha a linha.
