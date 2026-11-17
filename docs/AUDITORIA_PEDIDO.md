# Auditoria do Estudo do Kairi — pedido e preparação

Data: 2026-11-17. Pedido do dono, a partir de um roteiro montado com outra IA. **A auditoria ainda não foi rodada.** Este arquivo guarda o que foi decidido e o que já está pronto, para ela poder ser feita em qualquer conversa.

## Decisões do dono

- **Régua de comparação: 105% do CDI, em aplicação de liquidez diária, com os impostos.** Substitui a Selic líquida usada até aqui.
- Imposto da renda fixa a aplicar: tabela regressiva pelo prazo de cada aplicação (22,5% até 180 dias, 20% até 360, 17,5% até 720, 15% acima) e IOF regressivo nos resgates com menos de 30 dias.
- Todo resultado em tabela, com legenda (coluna, unidade, fórmula) e uma leitura prática logo abaixo.
- Nada de número estimado: o que faltar vai numa tabela de lacunas.

## O que a auditoria deve entregar

1. **Indicadores usados e omitidos** nas carteiras A (15%), B (20%) e C (15% em queda geral): média contra mediana; quantis de 5% a 95%; assimetria e curtose; desvio padrão; desvio só das perdas; ganhos divididos por perdas; correlação entre os fundos que dão sinal juntos; número de episódios independentes contra o total de ordens (341, 175 e 292).
2. **Taxa interna de retorno** dos fluxos reais (compra, rendimentos na data de pagamento, venda, imposto) contra 105% do CDI líquido nos mesmos valores e dias; a mesma conta para a carteira com o dinheiro do pico (R$ 262.698 na A, R$ 151.506 na B) e saldo parado a 105% do CDI; índices de Sharpe, Sortino e Calmar.
3. **Significância:** estatística t, valor p e intervalo de 95% do excesso sobre 105% do CDI, corrigidos pela sobreposição das ordens, em escolha (2018 a 2022), conferência (2023 a 2026) e total.
4. **Funil das quedas:** dos fundos que bateram 10% e 15% abaixo da média, quantos foram a 20% e a 30%; resultado por faixa; quantas ordens lucrativas se perdem subindo o gatilho.
5. **Regra de "virada"** (esperar a cota parar de cair) contra a entrada direta, com as medidas de risco; e se vale testar entrada em duas partes.
6. **Fatos relevantes:** queda sem notícia contra queda com 1 ou 2 fatos negativos nos 30 a 60 dias antes do sinal; subida com e sem fato positivo; resultado por tema do fato; e o mesmo em dias de queda geral.
7. **Tabela mestra** das três carteiras e **tabela de lacunas**.

## O que já está pronto no repositório

| Dado | Arquivo | Situação |
|---|---|---|
| CDI de cada dia, de 02/01/2017 a 13/11/2026, com os índices de 100% e de 105% | `planilhas/cdi.csv` | baixado do Banco Central (série 12) |
| Data de pagamento de cada rendimento | `planilhas/rendimentos_pagamentos.csv` | 23.742 de 23.800 com data (99,8%); mediana de 11 dias depois da data-base |
| Amortizações (devolução de patrimônio) | `planilhas/amortizacoes.csv` | 2.147, em 300 fundos; valores sem ajuste por desdobramento |
| Texto dos fatos relevantes (primeiros 3.000 caracteres) | `planilhas/tecnico/fatos_textos.csv.gz` | os 7.962 da planilha de anúncios |
| Ordens das três carteiras | `planilhas/kairi_ordens.csv`, `kairi_ordens_saidas.csv` | Parte 4 do estudo |
| Preços diários, mercado, tipo dos fundos | `planilhas/precos_*.csv`, `mercado.csv`, `fundos.csv` | — |
| Programas | `estudos/kairi*.py` | a regra de "virada" está em `kairi_expandido.py` |

## Lacunas já conhecidas

| Dado | Situação | Efeito |
|---|---|---|
| Classificação dos fatos relevantes | por palavras, e erra | os cruzamentos com fatos negativos e positivos são aproximados |
| Amortizações | não entram como dinheiro recebido nas ordens | ordens de fundos que devolveram patrimônio aparecem com perda maior que a real |
| Preços | 334 variações de mais de 25% num dia, em 128 fundos, sem ajuste | 13 das 341 ordens da carteira A têm um salto desses |
| Índice da bolsa de ações | não está na base | "mercado" é o fundo imobiliário do meio |

## Como rodar

Em conversa nova, em três blocos, cada um com um agente auxiliar: (1) indicadores, taxa de retorno e significância; (2) funil das quedas e virada; (3) fatos relevantes. Depois, a tabela mestra.
