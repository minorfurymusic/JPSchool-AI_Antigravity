# Estratégias do Radar de FIIs

Atualizado em 2026-11-13 (versão refeita a pedido do dono; a anterior está no histórico do repositório).
Tudo aqui foi medido **dia a dia** (pregão a pregão). Nada é mensal.

## Como ler

| Termo | Significado |
|---|---|
| Entrada | Compra da cota. Sempre na abertura do pregão seguinte ao sinal. |
| Saída | Venda da cota. |
| Em aberto | Entrou e ainda não saiu até 09/11/2026 (último pregão da base). |
| Pregões | Dias de bolsa entre a entrada e a saída. |
| Valorização | Quanto o **preço da cota** subiu ou caiu entre a entrada e a saída. |
| Rendimento | O dinheiro pago pelo fundo por cota durante a operação. |
| Total | Valorização + rendimento. |
| Queda | Sempre do preço da cota. |
| Corte | Sempre do rendimento. |
| Típico | A operação do meio. "Típico +10,9%" = metade das operações ganhou mais que 10,9% e metade ganhou menos. **Não** quer dizer que 10,9% dos fundos subiram. |
| Pessimista / Otimista | 1 em cada 4 operações foi pior que isso / 1 em cada 4 foi melhor. |
| D+5, D+20 | 5º e 20º pregão depois da entrada. |

## Quadro que todo estudo deve trazer (pedido do dono)

1. Quantidade de entradas, de saídas e em aberto.
2. Pregões entre a entrada e a saída.
3. Lucro ou prejuízo em duas contas: valorização e rendimento.
4. Selic no mesmo período.
5. Tudo já descontado de custos e imposto.

Situação hoje: **nenhum estudo cumpre os 5 itens.** Cada seção diz o que tem e o que falta.

---

## Estratégia 1 — Anúncio de aumento de rendimento

**Ideia:** o fundo publica um fato relevante que faz o rendimento subir. Entrada no pregão seguinte, saída depois que a cota valoriza.

- **1A, por tempo determinado:** venda de imóvel com lucro, multa, indenização. O rendimento sobe e depois volta.
- **1B, por mudança no lucro:** área vaga que foi alugada, contrato novo. O rendimento sobe e fica.
- **1C, o fundo declara o aumento:** o texto diz que o rendimento vai subir; o programa não sabe se é 1A ou 1B.

### Estudo 1.1 — Da entrada até a saída (2018 a 2026)

Programa: `estudos/anuncio_saida.py`, escrito e rodado por agente auxiliar; operações uma a uma em `docs/anuncio_saida_operacoes.csv`.

**Regras rodadas**
- **Entrada:** abertura do pregão seguinte ao fato relevante.
- **Saída 1, rendimento caiu:** abertura do pregão em que fica conhecido um rendimento 10% ou mais abaixo do maior desde a entrada.
- **Saída 2:** o fundo declara redução de rendimento.
- **Saída 3:** 252 pregões sem nada acontecer.
- Não há saída por preço. Não há perfil (conservador, moderado, agressivo): entram todos os fundos com R$ 200 mil ou mais negociados por dia.
- **Custos:** taxa de 0,03% na compra e na venda; imposto de 20% sobre a valorização; rendimento isento.
- **Selic:** líquida de imposto, nos mesmos pregões de cada operação.
- Os 10%, os 252 pregões e a saída na abertura são escolha minha. Não há preço de dentro do dia.

**Operações fechadas**

| | 1A venda com lucro | 1A multa ou indenização | 1B locação nova | 1C aumento declarado | Todas |
|---|---|---|---|---|---|
| Entradas | 150 | 38 | 96 | 99 | 287 |
| Fechadas | 116 | 35 | 87 | 93 | 244 |
| Pregões entre entrada e saída (média) | 128 | 144 | 118 | 118 | 119 |
| Fechadas em que a cota subiu | 47% | 40% | 44% | 51% | 49% |
| … valorização média dessas | +6,3% | +7,2% | +7,2% | +7,7% | +7,8% |
| Fechadas em que a cota caiu | 53% | 57% | 56% | 49% | 51% |
| … queda média dessas | −9,0% | −10,8% | −10,3% | −10,5% | −9,8% |
| Valorização média (todas as fechadas) | −1,7% | −3,3% | −2,7% | −1,3% | −1,2% |
| Rendimento médio recebido | +5,5% | +5,6% | +4,4% | +4,2% | +4,7% |
| Valorização + rendimento | +3,7% | +2,3% | +1,7% | +2,9% | +3,5% |
| Depois de custos e imposto | +3,1% | +1,7% | +1,0% | +2,1% | +2,7% |
| Selic líquida no mesmo período | +4,5% | +4,9% | +3,8% | +3,4% | +3,9% |
| Operações que ganharam da Selic líquida | 50% | 34% | 46% | 54% | 52% |
| O rendimento subiu de fato 5% ou mais depois da entrada | 61% | 60% | 46% | 67% | 58% |

**Por motivo da saída (todas, 244 fechadas)**

| Motivo | Quantas | Pregões | Valorização | Rendimento | Depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|
| Rendimento caiu 10% ou mais | 167 | 85 | −1,0% | +3,7% | +1,9% | +2,7% |
| Fundo declarou redução | 25 | 65 | −3,4% | +2,1% | −1,9% | +1,7% |
| 252 pregões | 52 | 252 | −0,6% | +9,3% | +7,5% | +8,9% |

**O rendimento subiu mesmo? (todas, 244 fechadas)**

| | Quantas | Pregões | Valorização | Rendimento | Depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|
| Subiu 5% ou mais depois da entrada | 141 | 141 | +0,1% | +5,7% | +4,7% | +4,6% |
| Não subiu | 103 | 89 | −2,9% | +3,4% | 0,0% | +2,9% |

**Operações em aberto**

| | Quantas | Pregões | Valorização | Rendimento | Valorização + rendimento | Selic líquida |
|---|---|---|---|---|---|---|
| Em aberto de verdade (menos de 252 pregões) | 28 | 96 | −8,0% | +4,0% | −4,1% | +4,2% |
| Fundos que pararam de negociar (não são operações reais em aberto) | 15 | — | — | — | — | — |

O programa marcou 43 como em aberto; 15 delas são fundos que saíram da bolsa (incorporados ou encerrados) e ficaram sem preço de saída. É um defeito a corrigir: falta tratar a saída desses fundos.

**O que diz**
- Na média, a Estratégia 1 com estas regras **perdeu da Selic líquida**: +2,7% contra +3,9%, em cerca de 119 pregões.
- A cota, na média, não valorizou (−1,2%). O ganho veio do rendimento.
- Metade das operações teve a cota em alta (+7,8% em média) e metade em queda (−9,8% em média).
- Em 4 de cada 10 anúncios o rendimento não subiu depois. Nessas, o resultado foi zero.
- Quando o rendimento subiu de fato, a operação empatou com a Selic líquida (+4,7% contra +4,6%).
- O melhor tipo foi o 1A venda com lucro (+3,1%); o pior, o 1B locação nova (+1,0%).

**Limites**
- Todos os fundos entram juntos. Falta filtrar por qualidade e por desconto (o exemplo do dono é de um fundo com cota a 50% do valor patrimonial).
- O tipo do anúncio é lido por palavras e erra.
- Conferência: os totais fecham e uma operação foi refeita à mão; o programa não foi revisado linha a linha.

O estudo antigo, que olhava o preço em D+5, D+10, D+20, D+30 e D+60, saiu deste documento por decisão do dono. Continua em `docs/ESTUDO_DIAS.md`.

### Estudo 1.1b — Separado por perfil (moderado e agressivo)

Mesmo programa e mesmas regras do Estudo 1.1, com duas mudanças: o perfil é dado pelo patrimônio do fundo no dia da entrada, e fundo que saiu da bolsa passa a fechar a operação no último preço (antes ficava "em aberto"). Os números do Estudo 1.1 são da versão anterior a essa correção.

**Onde caíram as 287 entradas**

| Perfil | Patrimônio | Entradas |
|---|---|---|
| Agressivo | R$ 50 a 100 milhões | 4 |
| Moderado | R$ 100 a 400 milhões | 80 |
| Conservador (fora desta estratégia) | R$ 400 milhões ou mais | 199 |
| Sem patrimônio conhecido | — | 4 |

**Moderado**

| | 1A venda com lucro | 1A multa ou indenização | 1B locação nova | 1C aumento declarado | Todas | Com desconto (cota até 90% do valor patrimonial) | Sem desconto |
|---|---|---|---|---|---|---|---|
| Entradas | 23 | 9 | 32 | 39 | 80 | 42 | 38 |
| Fechadas | 20 | 9 | 32 | 39 | 77 | 39 | 38 |
| Em aberto | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| Fechadas: pregões entre entrada e saída (média) | 99 | 107 | 100 | 106 | 104 | 115 | 92 |
| Fechadas em que a cota subiu | 35% | 33% | 47% | 46% | 40% | 36% | 45% |
| … valorização média dessas | +5,6% | +7,8% | +9,1% | +6,8% | +8,4% | +10,2% | +6,9% |
| Fechadas em que a cota caiu | 65% | 67% | 53% | 54% | 60% | 64% | 55% |
| … queda média dessas | −7,1% | −13,0% | −11,2% | −12,4% | −10,0% | −9,3% | −10,7% |
| Fechadas: valorização média | −2,7% | −6,1% | −1,7% | −3,6% | −2,6% | −2,3% | −2,9% |
| Fechadas: rendimento médio recebido | +6,1% | +5,0% | +4,0% | +3,7% | +4,5% | +5,4% | +3,6% |
| Fechadas: valorização + rendimento | +3,4% | −1,0% | +2,3% | +0,2% | +1,9% | +3,1% | +0,7% |
| Fechadas: depois de custos e imposto | +3,0% | −1,6% | +1,4% | −0,5% | +1,2% | +2,3% | 0,0% |
| Fechadas: Selic líquida no mesmo período | +3,7% | +4,1% | +2,8% | +2,6% | +3,1% | +4,3% | +1,9% |
| Fechadas que ganharam da Selic líquida | 35% | 33% | 50% | 51% | 44% | 36% | 53% |
| Em aberto: pregões desde a entrada (média) | 88 | — | — | — | 88 | 88 | — |
| Em aberto: valorização média | −2,2% | — | — | — | −2,2% | −2,2% | — |
| Em aberto: rendimento médio recebido | +4,7% | — | — | — | +4,7% | +4,7% | — |
| Em aberto: valorização + rendimento | +2,5% | — | — | — | +2,5% | +2,5% | — |
| Em aberto: Selic líquida no mesmo período | +3,9% | — | — | — | +3,9% | +3,9% | — |

Em aberto em 09/11/2026: NEWL11 (entrada 22/12/2025 a R$ 110,90, hoje R$ 105,00, 217 pregões, cota −5,3%, rendimento +10,0%); CXAG11 (08/09/2026 a R$ 70,82, hoje R$ 74,50, 42 pregões, +5,2%, +2,9%); RPRI11 (29/10/2026 a R$ 72,75, hoje R$ 68,00, 6 pregões, −6,5%, +1,2%).

| Motivo da saída (moderado, 77 fechadas) | Quantas | Pregões | Valorização | Rendimento | Depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|
| Rendimento caiu 10% ou mais | 49 | 72 | −4,2% | +3,3% | −1,3% | +2,2% |
| 252 pregões | 15 | 252 | −0,6% | +9,1% | +6,9% | +7,8% |
| Fundo saiu da bolsa | 8 | 42 | −1,1% | +3,9% | +2,5% | +1,2% |
| Fundo declarou redução | 5 | 69 | +5,0% | +2,8% | +6,6% | +1,8% |

**Agressivo**

Só 4 entradas em 9 anos, todas fechadas, nenhuma em aberto. Não dá para tirar conclusão. Uma delas subiu 46%; as outras três, de 0,5% a 2,2%.

**O que diz**
- O moderado perdeu da Selic líquida: +1,2% contra +3,1%.
- Com desconto foi melhor que sem (+2,3% contra 0,0%), mas ainda abaixo da Selic líquida do período (+4,3%).
- Sair quando o rendimento cai deu prejuízo (−1,3%): a cota já tinha caído 4,2% antes.
- 7 de cada 10 anúncios são de fundos de R$ 400 milhões ou mais. Com as faixas de patrimônio atuais, o agressivo fica quase vazio nesta estratégia.

**Limites**
- A saída "fundo saiu da bolsa" (8 no moderado) pode incluir fundos que só tiveram um trecho de preço descartado da base. Não conferido.
- A base de anúncios só tem fundos com R$ 200 mil ou mais negociados por dia; o agressivo aceitaria a partir de R$ 100 mil.

### Estudo 1.1c — Agressivo definido pelo desconto (decisão do dono em 2026-11-13)

**Regras:** as mesmas do Estudo 1.1 (entrada na abertura do pregão seguinte ao anúncio; saída quando o rendimento cai 10% ou mais, quando o fundo declara redução, em 252 pregões ou quando o fundo sai da bolsa; custos e imposto descontados). **Filtro do agressivo:** patrimônio de R$ 50 milhões ou mais, sem teto, e cota entre 30% e 75% do valor patrimonial no dia da entrada. Usa sempre o preço sobre valor patrimonial do próprio fundo, sem ajuste pela média do mercado.

Cada operação aparece em uma coluna só; quando o anúncio cabe em dois tipos, vale o primeiro da esquerda.

| | 1A venda com lucro | 1A multa ou indenização | 1B locação nova | 1C aumento declarado | Todas |
|---|---|---|---|---|---|
| Entradas | 23 | 3 | 20 | 13 | 59 |
| Fechadas | 17 | 3 | 19 | 13 | 52 |
| Em aberto | 6 | 0 | 1 | 0 | 7 |
| Fechadas: pregões entre entrada e saída (média) | 107 | 132 | 121 | 129 | 119 |
| Fechadas em que a cota subiu | 53% | 33% | 47% | 62% | 52% |
| … valorização média dessas | +9,3% | +6,4% | +14,2% | +14,7% | +12,4% |
| Fechadas em que a cota caiu | 47% | 67% | 53% | 38% | 48% |
| … queda média dessas | −13,5% | −7,0% | −16,7% | −10,4% | −13,6% |
| Fechadas: valorização média | −1,4% | −2,5% | −2,1% | +5,0% | −0,1% |
| Fechadas: rendimento médio recebido | +4,9% | +4,9% | +4,8% | +5,6% | +5,0% |
| Fechadas: valorização + rendimento | +3,4% | +2,4% | +2,8% | +10,7% | +4,9% |
| Fechadas: depois de custos e imposto | +2,4% | +1,9% | +1,4% | +8,8% | +3,6% |
| Fechadas: Selic líquida no mesmo período | +4,3% | +5,3% | +5,0% | +5,2% | +4,9% |
| Fechadas que ganharam da Selic líquida | 53% | 33% | 53% | 69% | 56% |
| Fechadas em que o rendimento subiu 5% ou mais depois da entrada | 41% | 67% | 26% | 69% | 44% |
| Em aberto: pregões desde a entrada (média) | 55 | — | 7 | — | 48 |
| Em aberto: valorização média | −3,2% | — | −2,1% | — | −3,0% |
| Em aberto: rendimento médio recebido | +2,9% | — | +1,4% | — | +2,7% |
| Em aberto: valorização + rendimento | −0,3% | — | −0,7% | — | −0,3% |
| Em aberto: Selic líquida no mesmo período | +2,4% | — | +0,3% | — | +2,1% |

Patrimônio dos fundos que entraram: 0 de R$ 50 a 100 milhões, 15 de R$ 100 a 400 milhões, 44 de R$ 400 milhões ou mais. Fundos diferentes: 28.

**Por motivo da saída (fechadas)**

| Motivo da saída | Quantas | Pregões | Valorização | Rendimento | Depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|
| Rendimento caiu | 29 | 92 | −0,7% | +4,2% | +2,3% | +3,5% |
| Prazo de 252 pregões | 11 | 252 | +8,0% | +10,7% | +15,9% | +11,1% |
| Fundo declarou redução | 8 | 47 | −3,7% | +1,4% | −2,5% | +1,7% |
| Fundo saiu da bolsa | 4 | 94 | −11,0% | +2,8% | −8,9% | +3,7% |

**Por tamanho do desconto (fechadas)**

| Faixa de preço sobre valor patrimonial na entrada | Fechadas | Valorização | Rendimento | Depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|---|---|
| 0,30 a 0,50 | 8 | −10,6% | +6,4% | −4,9% | +6,8% | 38% |
| 0,50 a 0,60 | 10 | +2,9% | +5,2% | +6,1% | +4,1% | 80% |
| 0,60 a 0,75 | 34 | +1,5% | +4,7% | +4,9% | +4,6% | 53% |

**Por ano da entrada**

| Ano da entrada | Entradas | Depois de custos e imposto (fechadas) | Selic líquida |
|---|---|---|---|
| 2018 | 1 | +3,8% | +0,3% |
| 2020 | 1 | +12,0% | +0,6% |
| 2021 | 2 | −14,0% | +4,7% |
| 2022 | 9 | +1,6% | +5,9% |
| 2023 | 8 | +8,4% | +4,9% |
| 2024 | 18 | −3,1% | +4,1% |
| 2025 | 14 | +13,4% | +5,8% |
| 2026 | 6 | — | — |

**Em aberto em 09/11/2026**

| Fundo | Entrada | Preço de entrada | Preço atual | Pregões | Valorização | Rendimento | Preço sobre valor patrimonial na entrada |
|---|---|---|---|---|---|---|---|
| RCRB11 | 2025-12-01 | 128.47 | 128.82 | 232 | +0,3% | +9,8% | 0.65 |
| CXAG11 | 2026-09-08 | 70.82 | 74.50 | 42 | +5,2% | +2,9% | 0.68 |
| RBRP11 | 2026-09-11 | 46.99 | 42.70 | 39 | −9,1% | +2,2% | 0.59 |
| RECT11 | 2026-10-28 | 33.00 | 32.32 | 7 | −2,1% | +1,4% | 0.37 |
| RBRR11 | 2026-10-29 | 65.70 | 63.00 | 6 | −4,1% | +0,0% | 0.71 |
| RPRI11 | 2026-10-29 | 72.75 | 68.00 | 6 | −6,5% | +1,2% | 0.73 |
| VCJR11 | 2026-10-29 | 66.15 | 63.00 | 6 | −4,8% | +1,2% | 0.72 |

Números tirados de `docs/anuncio_saida_operacoes.csv` (filtro aplicado sobre as 287 operações do Estudo 1.1b; nenhum estudo novo foi rodado).

### Estudo 1.1d — Régua de rendimento igual para os dois perfis; o desconto separa moderado de agressivo (decisão do dono em 2026-11-14)

**Regras**
- **Gatilho:** fato relevante de aumento de rendimento (1A, 1B, 1C). Entrada na abertura do pregão seguinte.
- **Checagem na entrada, igual para os dois perfis:** rendimento do último aviso x 12 sobre o preço de entrada maior ou igual à Selic líquida + 3 pontos. Selic líquida = Selic do dia menos 17,5% de imposto. Patrimônio de R$ 50 milhões ou mais.
- **O que separa os perfis:** só o preço sobre valor patrimonial. O dono definiu agressivo de 0,30 a 0,75 e moderado a partir de 0,60; a faixa de 0,60 a 0,75 ficou nos dois e aparece separada para o dono decidir.
- **Saída, custos e imposto:** os mesmos do Estudo 1.1. Declaração de redução vale só como saída.

Das 147 operações entre 0,30 e 0,90, 39 passam na régua de rendimento e 108 não passam.

**Com a régua de rendimento (39 operações)**

| | Agressivo: 0,30 a 0,60 | Faixa em aberto: 0,60 a 0,75 | Moderado: 0,75 a 0,90 | Todas: 0,30 a 0,90 |
|---|---|---|---|---|
| Entradas | 6 | 9 | 24 | 39 |
| Fechadas | 5 | 9 | 24 | 38 |
| Em aberto | 1 | 0 | 0 | 1 |
| Fechadas: pregões entre entrada e saída (média) | 75 | 107 | 77 | 84 |
| Fechadas em que a cota subiu | 20% | 67% | 42% | 45% |
| … valorização média dessas | +9,7% | +9,7% | +4,3% | +6,6% |
| Fechadas em que a cota caiu | 80% | 33% | 58% | 55% |
| … queda média dessas | −13,1% | −14,8% | −8,7% | −10,4% |
| Fechadas: valorização média | −8,5% | +1,6% | −3,3% | −2,8% |
| Fechadas: rendimento médio recebido | +5,4% | +5,1% | +3,7% | +4,2% |
| Fechadas: valorização + rendimento | −3,2% | +6,7% | +0,4% | +1,4% |
| Fechadas: depois de custos e imposto | −3,6% | +5,3% | −0,0% | +0,8% |
| Fechadas: Selic líquida no mesmo período | +2,7% | +4,1% | +2,0% | +2,6% |
| Fechadas que ganharam da Selic líquida | 60% | 67% | 46% | 53% |
| Em aberto: pregões desde a entrada (média) | 7 | — | — | 7 |
| Em aberto: valorização média | −2,1% | — | — | −2,1% |
| Em aberto: rendimento médio recebido | +1,4% | — | — | +1,4% |
| Em aberto: valorização + rendimento | −0,7% | — | — | −0,7% |
| Em aberto: Selic líquida no mesmo período | +0,3% | — | — | +0,3% |

**Sem passar na régua, para comparação (108 operações)**

| | Agressivo: 0,30 a 0,60 | Faixa em aberto: 0,60 a 0,75 | Moderado: 0,75 a 0,90 | Todas: 0,30 a 0,90 |
|---|---|---|---|---|
| Entradas | 14 | 29 | 65 | 108 |
| Fechadas | 13 | 24 | 53 | 90 |
| Em aberto | 1 | 5 | 12 | 18 |
| Fechadas: pregões entre entrada e saída (média) | 152 | 117 | 122 | 125 |
| Fechadas em que a cota subiu | 62% | 46% | 51% | 51% |
| … valorização média dessas | +14,1% | +13,5% | +7,6% | +10,2% |
| Fechadas em que a cota caiu | 38% | 54% | 49% | 49% |
| … queda média dessas | −25,1% | −9,1% | −7,5% | −10,0% |
| Fechadas: valorização média | −1,0% | +1,2% | +0,2% | +0,3% |
| Fechadas: rendimento médio recebido | +5,8% | +4,6% | +5,1% | +5,1% |
| Fechadas: valorização + rendimento | +4,8% | +5,8% | +5,3% | +5,4% |
| Fechadas: depois de custos e imposto | +3,0% | +4,6% | +4,5% | +4,3% |
| Fechadas: Selic líquida no mesmo período | +6,3% | +4,9% | +4,6% | +4,9% |
| Fechadas que ganharam da Selic líquida | 62% | 46% | 51% | 51% |
| Em aberto: pregões desde a entrada (média) | 39 | 58 | 86 | 76 |
| Em aberto: valorização média | −9,1% | −2,0% | −8,1% | −6,5% |
| Em aberto: rendimento médio recebido | +2,2% | +3,0% | +4,4% | +3,9% |
| Em aberto: valorização + rendimento | −6,9% | +1,0% | −3,7% | −2,6% |
| Em aberto: Selic líquida no mesmo período | +1,6% | +2,6% | +3,7% | +3,3% |

**Com a régua, por tipo do anúncio (fechadas)**

| Tipo do anúncio | Fechadas | Depois de custos e imposto | Selic líquida | Ganharam da Selic |
|---|---|---|---|---|
| 1A multa | 4 | +2,4% | +3,2% | 75% |
| 1A venda | 17 | +1,2% | +3,1% | 41% |
| 1B | 10 | −2,6% | +2,0% | 50% |
| 1C | 7 | +3,8% | +1,7% | 71% |

**Com a régua, por motivo da saída (fechadas)**

| Motivo da saída | Quantas | Pregões | Valorização | Rendimento | Depois de custos e imposto | Selic líquida |
|---|---|---|---|---|---|---|
| Rendimento caiu | 27 | 72 | −2,6% | +3,7% | +0,4% | +1,8% |
| Fundo saiu da bolsa | 5 | 22 | +0,4% | +1,1% | +1,4% | +0,8% |
| Prazo de 252 pregões | 4 | 252 | −5,1% | +12,6% | +6,5% | +10,3% |
| Fundo declarou redução | 2 | 57 | −9,0% | +2,1% | −7,0% | +1,8% |

**Com a régua, em aberto em 09/11/2026**

| Fundo | Entrada | Preço de entrada | Preço atual | Pregões | Valorização | Rendimento | Preço sobre valor patrimonial | Rendimento ao ano na entrada | Régua na entrada |
|---|---|---|---|---|---|---|---|---|---|
| RECT11 | 28/10/2026 | 33,00 | 32,32 | 7 | −2,1% | +1,4% | 0,37 | 16,4% | 14,3% |

Números tirados de `docs/anuncio_saida_operacoes.csv` e da Selic oficial (`dados/bruto/sgs_432.json`); o filtro foi aplicado sobre as 287 operações já calculadas.

### Estudo 1.2 — Carteira de R$ 10.000 em 2026 (com saída, custos e imposto)

**Regras rodadas** (01/01/2026 a 31/10/2026)

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Entra quando | fundo declara aumento (1C), ou aviso seguinte a um salto continua alto | os do conservador + valor por cota de 3% do preço ou mais + aviso 25% acima dos anteriores | os do moderado + 1A e 1B só pelo assunto |
| Fundo aceito (negociado por dia) | R$ 1 milhão | R$ 300 mil | R$ 200 mil |
| Quanto por operação | 10% | 20% | 33% |
| Sai com ganho de | +3% | +5% | +10% |
| Sai com perda de | −3% | −5% | −8% |
| Prazo máximo | 15 pregões | 20 pregões | 30 pregões |

Custos: corretagem zero, taxa da B3 de 0,03%, imposto de 20% sobre o ganho do mês, rendimento isento. Dinheiro parado rende a Selic menos 22,5%.

| Resultado | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Entradas | 16 | 41 | 24 |
| Entradas com ganho | 25% | 63% | 67% |
| Resultado médio por entrada | −1,70% | +0,83% | +2,93% |
| Rendimento recebido | R$ 27 | R$ 446 | R$ 999 |
| Imposto pago | R$ 0 | R$ 98 | R$ 295 |
| Dinheiro no fim | R$ 10.566 | R$ 11.005 | R$ 12.297 |
| Resultado no período | +5,7% | +10,1% | +23,0% |
| Mesmo dinheiro na Selic, com imposto | R$ 10.901 (+9,0%) | igual | igual |

**O que diz:** só moderado e agressivo ganharam da Selic. No teste com fundos sorteados, cerca de metade do ganho veio do mercado e das regras de saída, não do anúncio.

### O que falta na Estratégia 1

- Filtrar as entradas por qualidade do fundo e por desconto sobre o valor patrimonial, e medir de novo.
- Corrigir a saída dos fundos que pararam de negociar.
- Ler quanto tempo dura e de quanto é o aumento. A separação 1A/1B é por palavras e erra.

---

## Estratégia 2 — Desconto com renda estável

**Ideia:** a cota caiu, o rendimento em reais não mudou, então o fundo rende muito sobre o preço. Entra, não sai por queda, e sai quando a cota sobe a ponto de o rendimento sobre o preço chegar na Selic (exemplo do dono: rendia 20% ao ano, a cota subiu, passou a render 13%).

**Regras rodadas** (2018 a 2026)

| | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Patrimônio mínimo | R$ 400 milhões | R$ 100 milhões | R$ 50 milhões |
| Negociado por dia | R$ 500 mil | R$ 200 mil | R$ 100 mil |
| Preço sobre valor patrimonial | 0,80 a 1,00 | 0,30 a 0,90 | 0,30 a 0,75 |
| Rendimento regular | 12 avisos variando até 10% | 6 avisos até 15% | 6 avisos até 15% |
| Entra com rendimento de | Selic + 1 ponto | Selic + 2 pontos | Selic + 4 pontos |
| Sai quando o rendimento chega a | Selic − 1 ponto | Selic | Selic |

Nos três: sai também por corte de 15% ou mais, ou se o fundo declarar redução, ou em 2 anos. Não sai por queda. Fundo com amortização relevante não entra. Selic usada: **bruta**.

| Resultado | Conservador | Moderado | Agressivo |
|---|---|---|---|
| Entradas | 26 | 168 | 52 |
| Saídas | 20 | 147 | 46 |
| Em aberto | 6 | 21 | 6 |
| Pregões entre entrada e saída (típico) | 134 | 98 | 84 |
| Valorização (típico) | −4,5% | −2,5% | +4,3% |
| Rendimento (típico) | +3,9% | +4,7% | +5,0% |
| Total (pessimista) | −7,9% | −5,0% | +1,1% |
| Total (típico) | +0,6% | +1,8% | +12,5% |
| Total (otimista) | +9,1% | +8,8% | +19,5% |
| Entradas com ganho | 50% | 58% | 75% |
| Menor preço no caminho (típico) | −13,1% | −13,8% | −12,3% |
| Selic no mesmo período | não medido | não medido | não medido |
| Custos e imposto | não descontados | não descontados | não descontados |

O típico de cada linha é calculado separado, por isso valorização + rendimento não fecha exato com o total.

| Motivo da saída (moderado) | Quantas | Pregões | Total típico |
|---|---|---|---|
| Cota subiu até o rendimento chegar na Selic | 40 | 70 | +10,9% |
| Rendimento ficou abaixo da Selic sem a cota subir | 51 | 133 | −2,5% |
| Corte de 15% ou mais | 52 | 104 | +0,6% |
| Fundo declarou redução | 3 | 36 | −14,8% |
| Em aberto | 21 | 60 | −0,3% |

**O que diz:** só o agressivo foi bem. Quando a saída é pela cota ter subido, o ganho é bom (+10,9%), mas isso foi 1 em cada 4 entradas.

### O que falta na Estratégia 2

- Refazer com a Selic líquida de imposto (decisão do dono).
- Comparar com a Selic no mesmo período e descontar custos e imposto.
- Decidir se sai ou segura quando a Selic sobe e o fundo passa a render menos que ela sem a cota ter subido.
- Pendência do dono: saída também em anúncios muito sérios. Levantar mais dados antes de definir.

---

## Estratégia 3 — Inquilino com problema que se recupera (caso SPTW11)

**Ideia do dono:** fundo cai muito por problema com o inquilino e depois o problema se resolve.

**Nenhum estudo feito.** Há 223 fatos relevantes de saída de inquilino ou inadimplência na base. Falta o dono definir o sinal de entrada e o de saída.

---

## Conservador — a base da carteira (para o dono rever)

Não é estratégia de gatilho. É a parte da carteira que fica.

**Proposta**
1. **Fundo aceito:** patrimônio de R$ 400 milhões ou mais, R$ 500 mil negociados por dia ou mais, 12 avisos seguidos de rendimento variando até 10%, sem amortização relevante.
2. **Entrada:** quando o preço da cota está 15% a 20% abaixo do maior preço dos últimos 252 pregões e o rendimento em reais continua o mesmo.
3. **Não sai** por queda do preço.
4. **Saída:** corte do rendimento de 15% ou mais, fundo declarar redução, ou amortização relevante.

Exemplo do dono: a cota valia R$ 100 e pagava R$ 1. Hoje vale R$ 80 e paga R$ 1. Não vende; pela proposta, é hora de entrar ou comprar mais.

**Regras rodadas** (2018 a 2026): entrada na abertura do pregão seguinte ao dia em que a cota ficou 15% abaixo do maior preço, com rendimento mantido. Sem regra de saída: conta feita 252 pregões depois.

| Resultado | Queda de 15% |
|---|---|
| Entradas | 83 |
| Com 252 pregões completos | 55 |
| Em aberto (menos de 252 pregões) | 28 |
| Pregões | 252 (fixo) |
| Valorização (típico) | +1,8% |
| Rendimento (típico) | cerca de +9,5% |
| Total (pessimista) | +0,4% |
| Total (típico) | +11,3% |
| Total (otimista) | +23,8% |
| Entradas com ganho | 75% |
| Selic líquida no mesmo período | +11,0% |
| Fundo cortou o rendimento nesses 252 pregões | 16% |
| Menor preço no caminho (típico) | −10,9% |
| Custos e imposto | não descontados |

Outras quedas, total típico em 252 pregões: queda de 10%, +8,0% (104 entradas); queda de 20%, +18,0% (53 entradas).

Teste da regra de saída (504 pregões, 33 entradas):

| | Pessimista | Típico | Otimista |
|---|---|---|---|
| Nunca sair | −0,1% | +9,4% | +14,6% |
| Sair só no corte do rendimento | +5,2% | +12,1% | +20,5% |

**O que diz**
- Queda do preço com rendimento mantido não avisou corte: só 1 em cada 6 fundos cortou depois.
- Sair só no corte foi melhor que nunca sair.
- O ganho veio quase todo do rendimento; a cota pouco se mexeu.
- Empatou com a Selic líquida em 252 pregões (+11,3% contra +11,0%).

**Para o dono rever**
- Os critérios de fundo aceito são rígidos: 17 fundos em 2025.
- A queda que dá a entrada: 10%, 15% ou 20%.
- O corte que dá a saída: 15% foi escolha minha.
- Vender com prejuízo gera crédito que só abate ganho de outro fundo imobiliário ou Fiagro (20%). Não está no estudo.
- Faltam: inquilinos, vacância, dívida e se o rendimento é recorrente.

---

## Próximo passo sugerido

Rodar as Estratégias 1 e 2 e o conservador de novo, uma vez, já no quadro padrão: entradas, saídas, em aberto, pregões, valorização, rendimento, Selic líquida, custos e imposto descontados.

Estudos de origem: `docs/ESTUDO_DIAS.md`, `docs/SIMULACAO_2026.md`, `docs/ESTUDO_DESCONTO.md`, `docs/ESTUDO_CONSERVADOR.md`.
