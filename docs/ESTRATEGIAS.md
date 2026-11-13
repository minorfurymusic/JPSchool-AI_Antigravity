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
