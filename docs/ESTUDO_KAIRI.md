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
