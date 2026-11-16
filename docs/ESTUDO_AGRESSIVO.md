# Estudo Agressivo

Data: 2026-11-16. Programa: `estudos/agressivo.py` (escrito e rodado por agente auxiliar). Planilha para leitura: `planilhas/estudo_agressivo.csv` (37 linhas, 33 colunas com nomes por extenso). Versão do programa: `planilhas/tecnico/estudo_agressivo_completo.csv`. Tipos dos fundos: `planilhas/fundos.csv`.

## Regras do estudo

- **Gatilho:** fato relevante de aumento de rendimento (venda com lucro, multa ou indenização, locação nova, ou o fundo declarando o aumento).
- **Entrada:** abertura do pregão seguinte ao anúncio.
- **Perfil agressivo:** cota entre 0,30 e 0,60 do valor patrimonial; patrimônio de R$ 50 milhões ou mais; fundo que aguenta ordem de R$ 200 ou mais (2% do negociado por dia). Sem régua de rendimento.
- **Saída:** abertura do pregão em que fica conhecido um rendimento 10% ou mais abaixo do maior desde a entrada; ou o fundo declara redução; ou o fundo sai da bolsa; ou 252 pregões.
- **Custos:** taxa de 0,03% na compra e na venda; imposto de 20% sobre a valorização; rendimento isento.
- **Fora do estudo:** XPPR11, por decisão do dono (fundo em encerramento; tinha 4 operações).
- **Período:** entradas de 2021 a 2026. São **37 operações: 35 fechadas e 2 em aberto**.
- As médias abaixo são das operações fechadas.

**Aviso:** 37 operações é pouco. Dividindo por faixa e por tipo, há caixas com 1 a 4 casos. O que está aqui é pista para orientar o próximo teste, não regra comprovada.

## Pergunta 1 — Por faixa e por tipo de fundo

**Por faixa de ordem que o fundo aguenta**

| Faixa de ordem | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R$ 200 a 500 | 6 | 6 | 0 | 116 | 33% | +2,9% | +1,7% | +1,9% | +3,6% | +4,4% | 33% |
| R$ 500 a 4.000 | 15 | 15 | 0 | 77 | 27% | −7,4% | −7,8% | +1,5% | −6,3% | +2,9% | 27% |
| R$ 4.000 ou mais | 16 | 14 | 2 | 131 | 57% | +1,3% | −0,3% | +6,6% | +6,3% | +5,4% | 71% |

**Por tipo de fundo**

| Tipo do fundo | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lajes corporativas | 15 | 15 | 0 | 105 | 40% | +2,1% | +0,6% | +1,8% | +2,4% | +4,0% | 53% |
| Logística | 1 | 1 | 0 | 19 | 0% | −4,9% | −4,9% | +0,0% | −4,9% | +0,7% | 0% |
| Outros | 21 | 19 | 2 | 110 | 42% | −5,4% | −6,1% | +5,3% | −0,8% | +4,5% | 42% |

**Por faixa de ordem e tipo**

| Faixa de ordem / tipo | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R$ 200 a 500 / Lajes corporativas | 4 | 4 | 0 | 124 | 50% | +5,5% | +3,6% | +1,1% | +4,7% | +4,6% | 50% |
| R$ 200 a 500 / Outros | 2 | 2 | 0 | 100 | 0% | −2,1% | −2,2% | +3,5% | +1,3% | +4,0% | 0% |
| R$ 4.000 ou mais / Lajes corporativas | 4 | 4 | 0 | 94 | 50% | +13,1% | +10,3% | +4,9% | +15,3% | +3,9% | 100% |
| R$ 4.000 ou mais / Outros | 12 | 10 | 2 | 146 | 60% | −3,4% | −4,6% | +7,3% | +2,7% | +6,1% | 60% |
| R$ 500 a 4.000 / Lajes corporativas | 7 | 7 | 0 | 101 | 29% | −6,1% | −6,7% | +0,4% | −6,3% | +3,7% | 29% |
| R$ 500 a 4.000 / Logística | 1 | 1 | 0 | 19 | 0% | −4,9% | −4,9% | +0,0% | −4,9% | +0,7% | 0% |
| R$ 500 a 4.000 / Outros | 7 | 7 | 0 | 61 | 29% | −9,1% | −9,3% | +2,8% | −6,5% | +2,4% | 29% |

**Por tamanho do desconto**

| Cota sobre valor patrimonial | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0,30 a 0,45 | 8 | 7 | 1 | 109 | 29% | −7,5% | −8,3% | +3,0% | −5,3% | +4,5% | 29% |
| 0,45 a 0,60 | 29 | 28 | 1 | 104 | 43% | −0,8% | −1,9% | +3,8% | +1,9% | +4,1% | 50% |

**Por tipo do anúncio**

| Tipo do anúncio | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1A multa | 1 | 1 | 0 | 75 | 100% | +6,4% | +5,1% | +2,3% | +7,4% | +3,0% | 100% |
| 1A venda | 9 | 8 | 1 | 107 | 38% | −7,8% | −8,4% | +5,8% | −2,6% | +4,0% | 38% |
| 1B | 14 | 13 | 1 | 116 | 31% | −4,7% | −5,4% | +2,9% | −2,5% | +4,6% | 38% |
| 1C | 13 | 13 | 0 | 96 | 46% | +3,2% | +1,7% | +3,1% | +4,8% | +3,9% | 54% |

**Por motivo da saída**

| Motivo da saída | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| em aberto | 2 | 0 | 2 | — | — | — | — | — | — | — | — |
| fundo declarou redução | 2 | 2 | 0 | 88 | 50% | −6,1% | −6,8% | +3,2% | −3,5% | +3,1% | 50% |
| fundo saiu da bolsa | 1 | 1 | 0 | 61 | 100% | +4,7% | +3,7% | +2,2% | +5,9% | +2,7% | 100% |
| prazo de 252 pregões | 6 | 6 | 0 | 252 | 50% | +3,1% | +1,0% | +6,0% | +7,0% | +10,8% | 50% |
| rendimento caiu | 26 | 26 | 0 | 74 | 35% | −3,3% | −4,1% | +3,2% | −1,0% | +2,8% | 42% |

O que aparece:
- **Lajes corporativas foram melhores que o resto.** O melhor grupo é laje corporativa em fundo bem negociado (ordem de R$ 4.000 ou mais), mas são só 4 casos.
- **A faixa de R$ 500 a 4.000 perdeu nos dois tipos.** Não é efeito de um tipo de fundo; é da faixa.
- **O desconto maior foi pior.** Cota de 0,30 a 0,45 do valor patrimonial perdeu; de 0,45 a 0,60 ficou perto de zero.
- **O anúncio em que o fundo declara o aumento (1C) foi o único tipo de anúncio que ganhou da Selic líquida.**
- **Limite do cadastro:** a CVM classifica 21 das 37 operações em "Outros" (multicategoria, residencial, hospital, hotel, varejo). Só 1 é de logística e nenhuma é de shopping. Não dá para comparar laje, logística e shopping com estes dados.

## Pergunta 2 — A queda é do fundo, do mercado ou da Selic?

"Mercado" aqui é o fundo imobiliário do meio (mediana), nas mesmas datas de entrada e saída de cada operação, só pelo preço da cota. O índice da bolsa de ações não está na base.

**Por faixa de ordem**

| Faixa de ordem | Fechadas | Valorização do fundo | Valorização do mercado | Valorização dos fundos do mesmo tipo | Fundo menos mercado | Total depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|---|
| R$ 200 a 500 | 6 | +2,2% | +1,0% | +1,5% | +1,2% | +3,6% | +4,4% |
| R$ 500 a 4.000 | 15 | −7,3% | −2,0% | −3,9% | −5,3% | −6,3% | +2,9% |
| R$ 4.000 ou mais | 14 | +1,1% | −1,1% | −2,4% | +2,2% | +6,3% | +5,4% |

**Por tipo de fundo**

| Tipo do fundo | Fechadas | Valorização do fundo | Valorização do mercado | Valorização dos fundos do mesmo tipo | Fundo menos mercado | Total depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|---|
| Lajes corporativas | 15 | +1,7% | −1,7% | −3,8% | +3,5% | +2,4% | +4,0% |
| Logística | 1 | −5,1% | −0,8% | −2,3% | −4,3% | −4,9% | +0,7% |
| Outros | 19 | −5,3% | −0,6% | −1,3% | −4,7% | −0,8% | +4,5% |

**Pelo que a Selic fez entre a entrada e a saída**

| Selic durante a operação | Fechadas | Valorização do fundo | Valorização do mercado | Valorização dos fundos do mesmo tipo | Fundo menos mercado | Total depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|---|
| subindo | 14 | −5,5% | −4,8% | −5,5% | −0,7% | −1,9% | +4,7% |
| estável | 11 | −2,3% | −1,0% | −1,3% | −1,4% | −0,4% | +2,3% |
| caindo | 10 | +2,2% | +3,8% | +0,7% | −1,6% | +4,7% | +5,5% |

**Por ano de entrada**

| Ano de entrada | Entradas | Fechadas | Em aberto | Pregões | Cota subiu | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 2 | 2 | 0 | 184 | 0% | −14,5% | −14,6% | +1,0% | −13,6% | +5,0% | 0% |
| 2022 | 5 | 5 | 0 | 82 | 60% | −0,1% | −1,0% | +1,0% | +0,0% | +3,5% | 60% |
| 2023 | 8 | 8 | 0 | 134 | 50% | +6,4% | +4,1% | +3,7% | +7,8% | +5,5% | 50% |
| 2024 | 12 | 12 | 0 | 85 | 8% | −12,0% | −12,2% | +3,7% | −8,5% | +3,1% | 25% |
| 2025 | 7 | 7 | 0 | 115 | 86% | +6,7% | +5,3% | +6,6% | +11,9% | +5,3% | 86% |
| 2026 | 3 | 1 | 2 | 5 | 0% | −0,4% | −0,5% | +0,0% | −0,4% | +0,2% | 0% |

Das 18 operações fechadas em que a cota caiu:
- em 14, o mercado também caiu no mesmo período;
- em 9, o mercado caiu mais de 3%;
- em 11, o fundo caiu pelo menos 5 pontos a mais que o mercado (queda própria do fundo);
- 8 aconteceram com a Selic subindo.

Resposta:
- **As duas coisas.** A cota do fundo anda junto com o mercado (correlação de 0,61, numa escala em que 0 é nenhuma relação e 1 é relação total).
- **Com a Selic subindo, a queda foi do mercado inteiro.** O fundo caiu praticamente o mesmo que o mercado. O anúncio de aumento não protegeu.
- **2024 concentra o prejuízo:** 12 entradas, a cota subiu em 1 só. Foi o ano em que a Selic voltou a subir.
- **Na faixa de R$ 500 a 4.000 a queda é do próprio fundo:** caiu cerca de 5 pontos a mais que o mercado.
- **Nos fundos bem negociados e nas lajes, o fundo foi melhor que o mercado.**

## Pergunta 3 — A análise gráfica explica alguma coisa?

Medido com os preços até a véspera da entrada.

| Situação da cota na entrada | Fechadas | Valorização | Fundo menos mercado | Total depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|
| Abaixo da média de 200 pregões | 26 | −4,4% | −3,6% | −2,0% | +4,2% | 38% |
| Acima da média de 200 pregões | 9 | +4,4% | +5,8% | +7,4% | +4,1% | 67% |
| Até 20% abaixo | 14 | −6,0% | −1,7% | −3,1% | +4,0% | 36% |
| Mais de 20% abaixo do maior preço em 252 pregões | 21 | +0,4% | −0,8% | +2,9% | +4,3% | 52% |

Também medi a média de 50 pregões e a tendência dos 60 pregões anteriores: nenhuma das duas separou operações boas de ruins.

Resposta:
- **A tendência longa separou bem.** Quando a cota estava acima da média de 200 pregões na entrada, a operação ganhou da Selic líquida com folga; abaixo, perdeu. São 9 casos acima, então é pista forte, não prova.
- **Cota muito caída em relação ao maior preço do ano foi melhor que cota pouco caída.** Combina com a ideia do dono de comprar o que já caiu bastante, desde que tenha parado de cair.
- **Sinais curtos não ajudaram.**

## Pergunta 4 — Segurar para receber o dividendo faz diferença?

- **Na entrada:** em 1 das 37 operações (OULG11, 16/11/2023) a data-base do pagamento ficou entre o anúncio e a entrada, e o rendimento perdido foi de 1,2% do preço.
- **Na saída:** em 1 das 26 saídas por queda de rendimento a data-base ainda não tinha passado. Esperar um pregão a mais deu resultado 1,9 ponto pior, porque a cota caiu mais que o rendimento recebido.
- **Por que quase nunca se aplica:** o aviso de rendimento costuma sair no próprio dia da data-base. Quando o rendimento menor fica conhecido, o pagamento a que ele se refere já está garantido para quem tinha a cota, e o estudo já conta esse valor.

Resposta: **nestes dados não é relevante.** Não incluí regra de espera.

## Pontos suspeitos

- **Três operações ficaram 252 pregões sem receber nada:** ALMI11 (duas, 2021 e 2022) e TRNT11 (2024). Fundo que não paga não deveria ter passado como anúncio de aumento. É erro da leitura dos anúncios por palavras.
- **Em 5 das 35 fechadas, a valorização medida pelo fechamento e a medida pelo preço de entrada e saída têm sinais diferentes.** Não foi investigado.
- O programa do agente não foi revisado linha a linha. Conferido: 37 operações, 35 fechadas e 2 em aberto; nenhuma sem tipo.

## O que testar a seguir (propostas, a decidir pelo dono)

1. Excluir fundos em encerramento como regra fixa, não só o XPPR11.
2. Entrar só com a cota acima da média de 200 pregões.
3. Tirar a faixa de 0,30 a 0,45 do valor patrimonial, ou tratá-la com regra própria.
4. Não entrar em fundo que não pagou rendimento nos últimos meses.
5. Testar um freio de Selic: não entrar quando a Selic subiu nos últimos meses (só com informação conhecida no dia).
6. Ler os anúncios com IA para tirar os falsos "aumentos".

Cada um desses filtros reduz ainda mais os casos. O teste tem de ser feito no conjunto maior (cota de 0,30 a 0,90, 210 operações) e conferido por período.

## Planilha das operações

Uma linha por operação, ordenada por faixa de ordem, tipo e data de entrada. A mesma lista, com mais colunas, está em `planilhas/estudo_agressivo.csv`.

| Faixa de ordem | Tipo do fundo | Fundo | Entrada | Preço de entrada | Saída | Preço de saída | Pregões | Motivo da saída | Cota sobre valor patrimonial | Valorização | Valorização depois de imposto | Rendimento | Total depois de custos e imposto | Selic líquida | Diferença para a Selic | Valorização do mercado | Selic na entrada e na saída |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R$ 200 a 500 | Lajes corporativas | TRNT11 | 26/08/2021 | 114,51 | 14/02/2022 | 105,01 | 116 | rendimento caiu | 0,55 | −8,3% | −8,4% | +1,9% | −6,4% | +2,7% | −9,1% | −4,7% | 5,25% → 10,75% |
| R$ 200 a 500 | Lajes corporativas | TRNT11 | 15/03/2022 | 104,35 | 13/06/2022 | 116,99 | 62 | rendimento caiu | 0,52 | +12,1% | +9,6% | +1,2% | +10,8% | +2,2% | +8,6% | −0,2% | 10,75% → 12,75% |
| R$ 200 a 500 | Lajes corporativas | TRNT11 | 15/05/2023 | 100,86 | 14/08/2023 | 125,00 | 64 | rendimento caiu | 0,51 | +23,9% | +19,1% | +1,3% | +20,4% | +2,6% | +17,8% | +7,4% | 13,75% → 13,25% |
| R$ 200 a 500 | Lajes corporativas | TRNT11 | 06/09/2024 | 101,50 | 11/09/2025 | 95,60 | 252 | prazo de 252 pregões | 0,51 | −5,8% | −5,9% | +0,0% | −5,9% | +10,9% | −16,8% | −7,6% | 10,50% → 15,00% |
| R$ 200 a 500 | Outros | RBRS11 | 24/04/2023 | 52,02 | 26/01/2024 | 50,40 | 190 | rendimento caiu | 0,55 | −3,1% | −3,2% | +6,2% | +3,0% | +7,7% | −4,7% | +9,9% | 13,75% → 11,75% |
| R$ 200 a 500 | Outros | HGIC11 | 24/02/2025 | 64,79 | 11/03/2025 | 64,02 | 9 | rendimento caiu | 0,60 | −1,2% | −1,2% | +0,9% | −0,3% | +0,4% | −0,7% | +1,2% | 13,25% → 13,25% |
| R$ 500 a 4.000 | Lajes corporativas | ALMI11 | 02/07/2021 | 1130,11 | 07/07/2022 | 895,00 | 252 | prazo de 252 pregões | 0,55 | −20,8% | −20,9% | +0,0% | −20,9% | +7,3% | −28,2% | −10,7% | 4,25% → 13,25% |
| R$ 500 a 4.000 | Lajes corporativas | TRNT11 | 03/08/2022 | 115,01 | 15/08/2022 | 111,00 | 8 | rendimento caiu | 0,57 | −3,5% | −3,5% | +0,3% | −3,3% | +0,3% | −3,6% | +1,8% | 13,25% → 13,75% |
| R$ 500 a 4.000 | Lajes corporativas | ALMI11 | 11/10/2022 | 910,00 | 16/10/2023 | 740,00 | 252 | prazo de 252 pregões | 0,40 | −18,7% | −18,7% | +0,0% | −18,7% | +11,2% | −30,0% | −2,2% | 13,75% → 12,75% |
| R$ 500 a 4.000 | Lajes corporativas | TRNT11 | 11/10/2022 | 114,01 | 16/01/2023 | 124,67 | 65 | rendimento caiu | 0,56 | +9,3% | +7,4% | +1,3% | +8,7% | +2,6% | +6,1% | −6,3% | 13,75% → 13,75% |
| R$ 500 a 4.000 | Lajes corporativas | HOFC11 | 18/03/2024 | 30,00 | 01/07/2024 | 32,48 | 72 | rendimento caiu | 0,43 | +8,3% | +6,6% | +0,7% | +7,3% | +2,3% | +5,0% | −4,0% | 11,25% → 10,50% |
| R$ 500 a 4.000 | Lajes corporativas | FPAB11 | 12/04/2024 | 198,85 | 09/05/2024 | 190,00 | 18 | rendimento caiu | 0,58 | −4,5% | −4,5% | +0,3% | −4,2% | +0,6% | −4,8% | −1,7% | 10,75% → 10,50% |
| R$ 500 a 4.000 | Lajes corporativas | ALMI11 | 01/08/2024 | 656,66 | 01/10/2024 | 570,00 | 43 | rendimento caiu | 0,30 | −13,2% | −13,3% | +0,5% | −12,8% | +1,3% | −14,1% | −3,5% | 10,50% → 10,75% |
| R$ 500 a 4.000 | Logística | OULG11 | 17/11/2023 | 34,00 | 14/12/2023 | 32,35 | 19 | rendimento caiu | 0,50 | −4,9% | −4,9% | +0,0% | −4,9% | +0,7% | −5,6% | −0,8% | 12,25% → 11,75% |
| R$ 500 a 4.000 | Outros | RBRD11 | 28/06/2022 | 38,20 | 01/08/2022 | 38,37 | 24 | rendimento caiu | 0,54 | +0,4% | +0,3% | +2,4% | +2,7% | +0,9% | +1,7% | −0,9% | 13,25% → 13,25% |
| R$ 500 a 4.000 | Outros | RELG11 | 21/03/2023 | 65,01 | 08/02/2024 | 48,31 | 221 | rendimento caiu | 0,53 | −25,7% | −25,8% | +0,3% | −25,5% | +9,0% | −34,5% | +9,6% | 13,75% → 11,25% |
| R$ 500 a 4.000 | Outros | RELG11 | 27/02/2024 | 48,85 | 08/03/2024 | 48,00 | 8 | rendimento caiu | 0,39 | −1,7% | −1,8% | +0,2% | −1,6% | +0,3% | −1,9% | +0,0% | 11,25% → 11,25% |
| R$ 500 a 4.000 | Outros | MGHT11 | 20/05/2024 | 38,15 | 11/07/2024 | 28,35 | 37 | rendimento caiu | 0,44 | −25,7% | −25,8% | +1,5% | −24,2% | +1,1% | −25,4% | −2,4% | 10,50% → 10,50% |
| R$ 500 a 4.000 | Outros | MAXR11 | 26/09/2024 | 74,05 | 09/01/2025 | 62,78 | 69 | rendimento caiu | 0,57 | −15,2% | −15,3% | +13,1% | −2,1% | +2,3% | −4,4% | −10,0% | 10,75% → 12,25% |
| R$ 500 a 4.000 | Outros | BTRA11 | 04/09/2025 | 54,68 | 01/12/2025 | 57,23 | 61 | fundo saiu da bolsa | 0,49 | +4,7% | +3,7% | +2,2% | +5,9% | +2,7% | +3,2% | +1,2% | 15,00% → 15,00% |
| R$ 500 a 4.000 | Outros | RBRS11 | 25/03/2026 | 46,16 | 01/04/2026 | 45,97 | 5 | rendimento caiu | 0,48 | −0,4% | −0,5% | +0,0% | −0,4% | +0,2% | −0,7% | −0,1% | 14,75% → 14,75% |
| R$ 4.000 ou mais | Lajes corporativas | RCRB11 | 10/02/2023 | 111,49 | 20/02/2024 | 163,10 | 252 | prazo de 252 pregões | 0,53 | +46,3% | +37,0% | +8,5% | +45,5% | +10,8% | +34,7% | +8,1% | 13,75% → 11,25% |
| R$ 4.000 ou mais | Lajes corporativas | AIEC11 | 02/01/2024 | 56,25 | 01/02/2024 | 55,21 | 22 | rendimento caiu | 0,59 | −1,8% | −1,9% | +5,0% | +3,1% | +0,8% | +2,4% | +0,0% | 11,75% → 11,25% |
| R$ 4.000 ou mais | Lajes corporativas | AIEC11 | 28/11/2024 | 45,84 | 03/02/2025 | 45,82 | 43 | rendimento caiu | 0,54 | −0,0% | −0,1% | +4,4% | +4,3% | +1,5% | +2,8% | −8,0% | 11,25% → 13,25% |
| R$ 4.000 ou mais | Lajes corporativas | RCRB11 | 12/03/2025 | 117,63 | 06/06/2025 | 126,99 | 59 | rendimento caiu | 0,58 | +8,0% | +6,3% | +1,9% | +8,2% | +2,5% | +5,7% | +5,3% | 13,25% → 14,75% |
| R$ 4.000 ou mais | Outros | RBRP11 | 20/01/2023 | 46,64 | 12/05/2023 | 49,63 | 75 | fundo declarou redução | 0,57 | +6,4% | +5,1% | +2,3% | +7,4% | +3,0% | +4,4% | −1,1% | 13,75% → 13,75% |
| R$ 4.000 ou mais | Outros | BRCR11 | 06/03/2023 | 55,06 | 11/09/2023 | 62,46 | 130 | rendimento caiu | 0,55 | +13,4% | +10,7% | +5,7% | +16,4% | +5,5% | +10,9% | +8,7% | 13,75% → 13,25% |
| R$ 4.000 ou mais | Outros | RECT11 | 10/10/2023 | 44,14 | 08/04/2024 | 41,80 | 120 | rendimento caiu | 0,48 | −5,3% | −5,4% | +5,3% | −0,0% | +4,3% | −4,4% | +1,5% | 12,75% → 10,75% |
| R$ 4.000 ou mais | Outros | BRCR11 | 18/03/2024 | 59,49 | 12/03/2025 | 39,51 | 246 | rendimento caiu | 0,60 | −33,6% | −33,7% | +10,0% | −23,7% | +8,7% | −32,4% | −16,5% | 11,25% → 13,25% |
| R$ 4.000 ou mais | Outros | RECT11 | 11/07/2024 | 34,70 | 03/12/2024 | 28,25 | 101 | fundo declarou redução | 0,38 | −18,6% | −18,6% | +4,2% | −14,5% | +3,2% | −17,7% | −11,3% | 10,50% → 11,25% |
| R$ 4.000 ou mais | Outros | BLMG11 | 27/08/2024 | 40,43 | 10/02/2025 | 27,52 | 113 | rendimento caiu | 0,56 | −31,9% | −32,0% | +4,6% | −27,4% | +3,8% | −31,3% | −17,3% | 10,50% → 13,25% |
| R$ 4.000 ou mais | Outros | BPML11 | 28/01/2025 | 72,47 | 18/06/2025 | 79,52 | 96 | rendimento caiu | 0,57 | +9,7% | +7,7% | +8,6% | +16,4% | +4,0% | +12,4% | +8,7% | 12,25% → 14,75% |
| R$ 4.000 ou mais | Outros | RECT11 | 01/04/2025 | 33,94 | 06/04/2026 | 39,70 | 252 | prazo de 252 pregões | 0,37 | +17,0% | +13,5% | +14,1% | +27,7% | +12,3% | +15,4% | +4,9% | 14,25% → 14,75% |
| R$ 4.000 ou mais | Outros | BLMG11 | 29/04/2025 | 33,10 | 04/05/2026 | 33,40 | 252 | prazo de 252 pregões | 0,47 | +0,9% | +0,7% | +13,6% | +14,3% | +12,3% | +2,0% | +3,2% | 14,25% → 14,50% |
| R$ 4.000 ou mais | Outros | BROF11 | 29/04/2025 | 49,60 | 19/08/2025 | 53,59 | 78 | rendimento caiu | 0,45 | +8,0% | +6,4% | +4,5% | +10,9% | +3,4% | +7,5% | −1,3% | 14,25% → 15,00% |
| R$ 4.000 ou mais | Outros | RBRP11 | 11/09/2026 | 46,99 | em aberto | 42,70 | 39 | em aberto | 0,59 | −9,1% | −9,2% | +2,2% | −7,0% | +1,6% | −8,5% | −3,7% | 14,00% → 13,75% |
| R$ 4.000 ou mais | Outros | RECT11 | 28/10/2026 | 33,00 | em aberto | 32,32 | 7 | em aberto | 0,37 | −2,1% | −2,1% | +1,4% | −0,8% | +0,3% | −1,0% | −1,1% | 13,75% → 13,75% |
