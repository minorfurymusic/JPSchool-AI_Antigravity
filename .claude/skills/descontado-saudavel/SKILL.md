---
name: descontado-saudavel
description: Tipo 1 — filtro de fundos imobiliários (FII) descontados, saudáveis e com rendimento constante, para o momento de queda moderada do mercado (sem a crise de desespero do Kairi). Use quando o dono pedir fundos descontados que pagam bem, a lista de hoje do Tipo 1, ou a simulação dessa carteira.
---

# Descontado saudável (Tipo 1) — SITUAÇÃO: NÃO VALIDADO

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

## Limites

- Com 3 operações não há o que concluir; a carteira ficou quase toda no CDI.
- A avaliação de saúde (`estudos/saude_fundo.py`) ainda lê o valor patrimonial sem correção.
- Classe sem informe mensal em 0% a 4% dos fundos negociados por ano (lista em `estudos/classificacao_carteira.py`).
- Afrouxar regras depois de ver este resultado é ajuste ao passado: se o dono quiser, registrar como versão nova e
  mostrar as duas lado a lado.
