# Perfil conservador como base da carteira

Data: 2026-11-13. Programa: `estudos/conservador.py`. Saída completa: `dados/conservador.txt` (fora do repositório).

## Pergunta do dono

O conservador olha o fundo em si. Se a cota cai 10–15% e o rendimento continua igual, ele não venderia.
Talvez o conservador seja a base da carteira e fique fora da dinâmica de gatilhos; moderado e agressivo ficam com os gatilhos.

## Como foi medido (confirmado por execução real)

Dia a dia, 2018 a 2026, só com o que era conhecido em cada data.

- **Fundo de base:** patrimônio de R$ 400 milhões ou mais, liquidez de R$ 500 mil por dia ou mais, 12 avisos de rendimento seguidos variando até 10%, sem amortização relevante.
- **Queda com rendimento mantido:** primeiro pregão em que o fechamento fica 10%, 15% ou 20% abaixo do maior fechamento dos 252 pregões anteriores, com o rendimento atual em pelo menos 95% do de 126 pregões antes. Um caso por fundo por ano.
- **Compra** na abertura do pregão seguinte.
- **Selic líquida:** Selic do dia acumulada, menos o imposto da renda fixa conforme o prazo.
- Resultado = cota + rendimentos recebidos, sem custos nem imposto sobre ganho.

## Resultado 1 — fundo de base que cai com o rendimento mantido

| | Queda de 10% | Queda de 15% | Queda de 20% |
|---|---|---|---|
| Casos | 104 | 83 | 53 |
| Rendimento foi cortado 15% ou mais nos 252 pregões seguintes | 17% | 16% | 15% |
| **Segurar 252 pregões** — pessimista | −1,7% | +0,4% | +4,5% |
| típico | +8,0% | +11,3% | +18,0% |
| otimista | +21,0% | +23,8% | +26,2% |
| pior 1 em 10 | −10,2% | −8,3% | −6,2% |
| Terminou com ganho | 70% | 75% | 78% |
| Selic líquida no mesmo período (típico) | +11,0% | +11,0% | +10,9% |
| Ganhou da Selic líquida | 45% | 55% | 59% |
| Menor preço no caminho (típico) | −12,6% | −10,9% | −10,8% |
| Só a cota, 252 pregões (típico) | −2,7% | +1,8% | +8,5% |
| Voltou ao preço do pico em até 504 pregões | 36% | 31% | 25% |

Separando pelo que aconteceu depois com o rendimento (queda de 15%, 252 pregões):

| | Casos | Pessimista | Típico | Otimista |
|---|---|---|---|---|
| Rendimento não foi cortado | 46 | +2,5% | +12,9% | +24,9% |
| Rendimento foi cortado | 9 | −11,6% | +3,4% | +16,2% |

## Resultado 2 — vender só quando o rendimento é cortado

Mesmos casos, janela de 504 pregões. "Até o corte" = vende na abertura seguinte a um aviso 15% ou mais abaixo e deixa o dinheiro na Selic líquida.

| Queda de 15% (33 casos) | Pessimista | Típico | Otimista | Pior 1 em 10 |
|---|---|---|---|---|
| Segurar sempre | −0,1% | +9,4% | +14,6% | −7,2% |
| Segurar até o corte | +5,2% | +12,1% | +20,5% | −3,0% |

Em 504 pregões a Selic líquida rendeu +21,8% (típico); só 18% dos casos ganharam dela.

## Resultado 3 — comprar o fundo de base no primeiro pregão do ano e segurar 252 pregões

| Ano | Fundos | Total típico | Só rendimentos | Selic líquida | Ganhou da Selic | Menor preço |
|---|---|---|---|---|---|---|
| 2018 | 1 | +9,7% | 8,9% | 5,4% | 100% | −14,3% |
| 2020 | 1 | −7,1% | 5,4% | 2,4% | 0% | −47,8% |
| 2021 | 3 | −9,6% | 6,7% | 3,8% | 0% | −28,2% |
| 2022 | 5 | −2,8% | 8,9% | 10,4% | 0% | −20,8% |
| 2023 | 10 | +15,1% | 10,1% | 11,0% | 50% | −12,7% |
| 2024 | 11 | −12,0% | 9,0% | 9,0% | 0% | −28,1% |
| 2025 | 17 | +24,4% | 13,0% | 11,9% | 82% | −6,8% |

Todos os anos (48 casos): pessimista −7,4%, típico +2,0%, otimista +23,0%. Ganhou da Selic líquida em 42%. Rendimento cortado no ano em 19%.

## O que os números dizem

- **A hipótese do dono se confirma no ponto principal:** queda de preço com rendimento mantido não previu corte. Só 1 em cada 6 fundos cortou depois.
- **A regra "não vende pelo preço, vende pelo corte" foi melhor que segurar sempre**, no típico e no pior caso.
- **A cota não volta rápido.** Só 1 em cada 3 voltou ao pico em dois anos. Quem segura fica pela renda, não pela valorização.
- **Com juro alto, a renda sozinha não ganha da Selic líquida.** Em dois anos, perdeu em 4 de cada 5 casos.
- **Quanto maior a queda, melhor a entrada.** Queda de 20% com rendimento mantido deu +18,0% típico em 252 pregões, contra +8,0% na queda de 10%.
- **Comprar em data fixa foi pior que comprar na queda:** +2,0% típico contra +11,3%.

## Limites

- Poucos casos: 33 a 66 com janela completa; a tabela por ano tem 1 a 17 fundos.
- Os casos se concentram em 2024–2026, período de juro alto.
- O filtro de 12 avisos variando até 10% é rígido e deixa poucos fundos (17 em 2025).
- Casos do mesmo período andam juntos; não são independentes.
- "Rendimento mantido" não separa rendimento recorrente de não recorrente.
- Não há dado de inquilino, vacância ou dívida neste estudo.

## Pesquisa na internet (três agentes, modelo Haiku)

Qualidade baixa: os agentes leram só resumos de busca, de corretoras e blogs. Vale como pista, não como prova.

**Como os investidores fazem**
- Não achou regra numérica do tipo "vende se cair 10–15%". O critério citado é "os motivos da compra deixaram de existir" (Suno, FundsExplorer, Clube FII no site da B3).
- Vender só porque a cota subiu é citado como erro comum (Suno).
- Imposto: 20% sobre o ganho líquido na venda; prejuízo só abate ganho de outro fundo imobiliário, Fiagro ou FI-Infra; rendimento mensal isento (Toro, Renova).
- Armadilhas: rendimento inflado por venda de imóvel, multa de rescisão, renda mínima garantida que acaba, amortização (Capital Aberto, InfoMoney).

**Análise fundamentalista**
- Patrimônio mínimo citado: R$ 300 milhões (Renova). Liquidez: sem consenso.
- Preço sobre valor patrimonial: abaixo de 1,0 desconto; 1,0 a 1,2 justo; acima de 1,5 caro (fonte não identificada).
- Vacância física abaixo de 10% (fonte não identificada). Vacância financeira é a que afeta o rendimento.
- Fundos de papel: relação dívida/garantia abaixo de 60% é conservador (Renova); mais de 10% do patrimônio num devedor é alerta.
- Sinais antes do corte: vacância financeira subindo, contrato grande vencendo, adiamento de aluguel, dívida subindo junto com vacância.

**Notícias de 2026**
- Selic: 15% até março, cortes até 13,75%. Conferido nos nossos dados oficiais do Banco Central: 13,75% desde 17/09/2026, vigente em 09/11/2026.
- Imposto: a medida provisória 1.303/2025 (5% sobre rendimentos) perdeu validade em 08/10/2025 (COAD). Nada aprovado em 2026 foi encontrado.
- Eleição: primeiro turno em 04/10/2026; resultado do segundo turno **não confirmado** pelo agente. Dólar a R$ 5,44 em 30/10 (Brapi).
- Recuperação judicial da Casas Bahia, com queda de cerca de 10% num fundo de logística que a tem como inquilina (Investidor10; data não confirmada).
- Índice dos fundos em 2026: perto de zero até agosto (Meus Dividendos); máxima em outubro sem fonte verificada.

## Proposta de mudança na estratégia (a decidir pelo dono)

1. **Conservador vira a base**, sem gatilho de anúncio. Regras: não vende por preço; vende por corte de 15% ou mais, declaração de redução ou amortização relevante.
2. **Entrada da base pela queda**, não por data: fundo de base 15–20% abaixo do pico com rendimento mantido.
3. **Moderado e agressivo** ficam com os gatilhos (anúncio de aumento e desconto com renda estável).
4. **Régua: Selic líquida de imposto.**
5. **Separar fundo de papel de fundo de imóveis**; o rendimento do papel acompanha o juro.
6. **Nota de qualidade** com o que a CVM já entrega por trimestre: vacância, inquilinos, dívida, origem do rendimento.
7. **Aviso de troca com prejuízo:** quando há prejuízo acumulado e um fundo parecido disponível, mostrar o crédito de imposto.
