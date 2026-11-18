---
name: descontado-saudavel
description: Tipo 1 — filtro de fundos imobiliários (FII) descontados, saudáveis e com rendimento constante, para o momento de queda moderada do mercado (sem a crise de desespero do Kairi). Use quando o dono pedir fundos descontados que pagam bem, a lista de hoje do Tipo 1, ou a simulação dessa carteira.
---

# Descontado saudável (Tipo 1) — SITUAÇÃO: TRADE EM PAPEL PROMISSOR; RESTO NÃO VALIDADO

Leia primeiro `docs/TIPO1_TRADE.md` (registro de tudo o que foi descoberto, 18/11/2026).

Responder em português simples, sem jargão. Nunca dizer "funciona" sem mostrar a saída real do programa.

## Para que serve

Achar fundo que caiu de 10% a 25% em 6 meses (queda maior é terreno do Kairi Padrão), negociado com desconto sobre o
patrimônio, saudável, pagando bem e sempre o mesmo rendimento. Expectativa do dono (18/11/2026): juros caindo em 2027.

## Regras (fixadas em 18/11/2026, antes de rodar)

As 10 regras de entrada e as 3 de saída estão no começo de `estudos/descontado_saudavel.py` e em
`docs/FILTRO_DESCONTADOS.md`. Resumo: patrimônio ≥ R$ 100 mi; negociação típica ≥ R$ 250 mil/dia; sem amortização e
sem bloqueio do Kairi; queda de 10% a 25% em 6 meses; preço 0,60–0,90 do patrimônio; patrimônio por cota ≥ −5% em 12
meses; rendimento 2 pontos acima da mediana da própria classe e acima da Selic esperada pelo Focus (líquida de IR);
rendimento constante (11 de 12 meses, oscilação ≤ 0,03, no máximo 1 queda de 2%, sem tendência de queda); cobertura do
rendimento ≥ 1,0; avaliação de saúde diferente de NÃO COMPRAR. Saída: doença confirmada em 2 meses, corte de mais de 5%
ou preço a 0,95 do patrimônio.

## Como rodar

```bash
PYTHONPATH=. python3 estudos/descontado_saudavel.py
```

Saída em `planilhas/descontado_saudavel.xlsx`: resumo (2018–2022, 2023–2026, completo), operações, patrimônio dia a dia,
funil por revisão e a aba "Hoje - onde cada fundo parou" (valor de cada medida e a primeira regra em que o fundo para).
Antes de qualquer compra: Skill `avaliar-fundo`, passo 4 (ler o relatório gerencial).

## Tabelas que usa

| Tabela | Programa |
|---|---|
| `planilhas/precos_AAAA.csv`, `rendimentos_pagamentos.csv`, `cdi.csv`, `mercado.csv` | base |
| `planilhas/classificacao_carteira_mensal.csv` (classe pela carteira: Papel, Tijolo, Desenvolvimento, Fundo de fundos, Híbrido) | `estudos/classificacao_carteira.py` |
| `planilhas/tecnico/valor_patrimonial_correcoes.csv` (correções do valor patrimonial) | `estudos/vp_correcoes.py` |
| `planilhas/tecnico/cobertura_trimestral.csv` (cobertura do rendimento) | `estudos/cobertura_rendimento.py` |
| `planilhas/focus_selic_fim_de_ano.csv` (Selic esperada) | `estudos/focus.py` |

## Resultado de referência (18/11/2026, R$ 10 mil, 2018 a 09/11/2026, com classe e valor patrimonial corrigidos)

| | 2018–2022 | 2023–11/2026 | Completo |
|---|---|---|---|
| Operações | 0 | 3 (KORE11 −1,3%, GGRC11 −4,7%, HABT11 −2,2% em aberto) | 3 |
| Carteira ao ano | 5,5% | 10,0% | 7,4% |
| 105% do CDI líquido ao ano | 5,8% | 12,0% | 8,6% |

Valor final R$ 18.860 contra R$ 20.779 do CDI. O filtro quase não dispara: em média 0,2 fundo por mês passa na
constância e nenhum chega ao fim. Hoje (09/11/2026) nenhum fundo passa; LIFE11 e HABT11 param só na constância.

## Versão 2 (18/11/2026): corte só no essencial, o resto vira nota

Corte de vez: tamanho, negociação, amortização/bloqueio, saúde, preço 0,50–1,00 do patrimônio, rendimento acima do
Focus líquido. Nota (média das posições) em desconto, rendimento acima da classe, constância, cobertura, patrimônio por
cota e queda de 10% a 25%. Os 5 de maior nota. Saídas iguais às da versão 1.

| | v1 completo | v2 2018–2022 | v2 2023–11/2026 | v2 completo |
|---|---|---|---|---|
| Operações | 3 | 123 | 29 | 152 |
| Com lucro | 0% | 59% | 55% | 58% |
| Carteira ao ano | 7,4% | 2,2% | 5,4% | 3,6% |
| Maior queda | −4,3% | −37,2% | −19,9% | −37,2% |

v2: R$ 13.642 contra R$ 20.779 do CDI. Afrouxar fez comprar muito e perder: 46 saídas por corte de rendimento e 39 por
rendimento caindo, com resultado perto de zero; só as 43 saídas por preço a 0,95 do patrimônio deram lucro (+5,8%).

## Como trade (correção do dono, 18/11/2026) — É ASSIM QUE A ESTRATÉGIA DEVE SER LIDA

Comprar, receber o rendimento e vender quando cota + rendimentos chegam a +10% ou +15%. Não é carteira parada.
`PYTHONPATH=. python3 estudos/descontado_trade.py` -> `planilhas/descontado_trade.xlsx`. Entradas: os 5 de maior nota
da v2 em cada fim de mês; prazo de 1 ano; sem stop.

| | Alvo +10% | Alvo +15% |
|---|---|---|
| Operações encerradas | 149 | 139 |
| Chegaram ao alvo | 61% | 53% |
| Chegaram em até ~3 meses / ~6 meses | 28% / 46% | 12% / 30% |
| Pregões até o alvo (mediana) | 76 | 114 |
| Não chegaram: resultado em 1 ano (média) | −8,3% | −7,3% |
| Pior momento (mediana / 1 em 10) | −6,3% / −22% | −6,9% / −23% |

## Formas de comprar e vender (18/11/2026, `estudos/descontado_saidas.py`, `planilhas/descontado_saidas.xlsx`)

Compra na abertura seguinte ao sinal (A); prazo de 1 ano. Ganho por mês aplicado = soma dos resultados ÷ soma dos
pregões × 21 (CDI no mesmo dinheiro e tempo: 0,66% a 0,69%).

| Venda | Operações | Com lucro | Resultado médio | Ganho por mês aplicado | Perdas de mais de 10% |
|---|---|---|---|---|---|
| Média 21 cruza abaixo da 70 | 203 | 56% | +3,8% | **0,79%** | 6% |
| Média 21 cruza abaixo da 90 | 200 | 54% | +3,5% | 0,67% | 7% |
| Alvo +15% | 139 | 65% | +4,9% | 0,57% | 16% |
| Alvo +10% | 149 | 70% | +3,4% | 0,47% | 13% |
| Fibonacci 61,8% / 50% / 38,2% | 159–177 | 69%–72% | +1,8% a +3,2% | 0,31% a 0,44% | 13%–14% |
| Banda superior de Bollinger | 300 | 65% | −0,3% | −0,17% | 10% |

Comprar só quando o fechamento toca a banda inferior de Bollinger (B) piorou todas as vendas (melhor: cruzamento
21×70, 0,73% por mês).

## Por classe de fundo (18/11/2026, contas corrigidas: rendimento pela data-com e 20% de IR sobre ganho na cota)

`PYTHONPATH=. python3 estudos/descontado_classes.py` -> `planilhas/descontado_classes.xlsx`.
Só **Papel** ganhou do CDI do mesmo período (em 7 das 8 vendas). Papel com alvo +10%: 93% com lucro, +7,4% líquido
por operação, +0,37 ponto por mês acima do CDI. Tijolo perdeu em todas as vendas.

## Limites

- Com 3 operações não há o que concluir; a carteira ficou quase toda no CDI.
- A avaliação de saúde (`estudos/saude_fundo.py`) ainda lê o valor patrimonial sem correção.
- Classe sem informe mensal em 0% a 4% dos fundos negociados por ano (lista em `estudos/classificacao_carteira.py`).
- Afrouxar regras depois de ver este resultado é ajuste ao passado: se o dono quiser, registrar como versão nova e
  mostrar as duas lado a lado.
