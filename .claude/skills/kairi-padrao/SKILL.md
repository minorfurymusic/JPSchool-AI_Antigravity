---
name: kairi-padrao
description: Kairi Padrão — estratégia do dono para fundos imobiliários (FII) - comprar fundo bem negociado quando a cota cai 20% a 25% abaixo da média de 200 pregões, só se o fundo estiver saudável, e vender na volta à média. Use quando o dono pedir o "Kairi Padrão", os sinais de hoje, uma simulação ou revisão da carteira nesse molde.
---

# Kairi Padrão (molde fechado em 17/11/2026)

Responder em português simples, sem jargão. Nunca chamar de "funciona" sem mostrar a saída real do programa.

## Regras de entrada

1. **Sinal:** o fechamento cruza para baixo o afastamento da média de 200 pregões:
   - **C1:** 25% abaixo da média, em fundo com negociação típica (mediana de 60 pregões) de R$ 500 mil a R$ 1 milhão por dia;
   - **C2:** 20% abaixo da média, em fundo com negociação típica de R$ 1 milhão ou mais por dia.
2. **Universo:** patrimônio de R$ 50 milhões ou mais; fundo pagando rendimento; rendimento do dia pelo menos 95% do de
   6 meses antes; preço entre 0,30 e 3,0 do patrimônio; sem amortização relevante em 12 meses; XPPR11 e CARE11 fora.
3. **Bloqueios automáticos:** fato relevante ou documento do FNET (12 meses) sobre liquidação, incorporação, fusão, cisão,
   venda de todos os ativos ou ida para o balcão; comunicado de "não haverá distribuição de rendimentos" (6 meses).
4. **Avaliação de saúde** (Skill `avaliar-fundo`): só compra se não for NÃO COMPRAR. Em ATENÇÃO (queda só do fundo sem
   motivo nos dados), dizer ao dono que o motivo é desconhecido.
5. **Compra:** abertura do pregão seguinte ao sinal. Não esperar: esperar 5 pregões baixou o resultado médio de +23% para
   +17%; 10 pregões, para +13%.
6. **Vários sinais no mesmo dia:** o mais saudável primeiro (queda junto com o mercado, rendimento estável); empate, o de
   maior negociação típica.

## Regras de saída

- **Volta à média:** vende no fechamento do primeiro dia em que o fechamento fica igual ou acima da média de 200 pregões
  (média até o dia anterior). Não usar a máxima do dia (dá lucro falso em fundo pouco negociado).
- **Prazo:** 252 pregões.
- **Saída antecipada:** na abertura seguinte a aviso de liquidação, incorporação, ida para o balcão ou rendimento zero.
- **Não vender antes da média** só porque subiu: depois de +15%, 82% chegaram a +20% e esperar a média rendeu em média
  uns 8 pontos a mais (estudos/kairi_alvo_segunda_entrada.py).
- **Troca** (vender para entrar num sinal novo): só com lucro de 15% ou mais e cota a no máximo 5% da média. Na prática
  quase nunca acontece.
- **Segunda entrada:** ao sair de um fundo, se algum sinal perdido ainda estiver 15% ou mais abaixo da média e sem ter
  voltado à média, entra nele.

## Dinheiro

- Dividir o capital em 2 a 5 partes (R$ 10 mil: ordens de R$ 5 mil a R$ 2 mil). Os sinais chegam em ondas: até 22 ao
  mesmo tempo em março de 2020.
- O que não está em fundo fica em 105% do CDI (liquidez diária, IR regressivo e IOF).
- Imposto de 20% sobre o ganho do mês, com prejuízo abatendo; rendimento isento; taxa de 0,03% por operação.

## Como rodar

```bash
PYTHONPATH=. python3 estudos/kairi_sinais_hoje.py 10          # sinais dos últimos 10 pregões, com bloqueio e veredito
PYTHONPATH=. python3 estudos/ficha_fundo.py CODIGO11 dd/mm/aaaa  # ficha de saúde de um sinal (ler os documentos)
PYTHONPATH=. python3 estudos/kairi_oportunidades.py           # validação, oportunidades por ano, carteira dividida
PYTHONPATH=. python3 estudos/kairi_mapa_operacoes.py          # mapa das oportunidades (depois do anterior)
```

## Resultados de referência (02/01/2018 a 09/11/2026, dados de planilhas/)

| Medida | Valor |
|---|---|
| Oportunidades aprovadas | 41 (2018: 1, 2019: 0, 2020: 22, 2021: 6, 2022: 0, 2023: 1, 2024: 8, 2025: 2, 2026: 1) |
| Fechadas com lucro | 39 de 40; única perda TRBL11 −4% |
| Resultado médio por operação | +24,7%; prazo médio 160 dias (mediana 137) |
| Dias sem nenhuma operação | 54% |
| Carteira de R$ 10 mil, ordens de R$ 5 mil | R$ 32.103; maior queda −9,0% (105% do CDI: R$ 20.779) |
| Carteira de R$ 10 mil, ordens de R$ 2 mil | R$ 30.744; maior queda −5,7% |

Planilhas: `planilhas/kairi_oportunidades.xlsx`, `planilhas/kairi_mapa_operacoes.xlsx`, `planilhas/kairi_mapa_operacoes.png`.

## Limites (dizer sempre que relevante)

- Só 3 de 9 anos tiveram 3 ou mais oportunidades; em 2019 e 2022, nenhuma. A estratégia depende de quedas gerais.
- A avaliação de saúde foi montada depois de ver os perdedores (DEVA11, VGHF11, TGAR11). No grupo grande ela ajudou
  (aprovadas +13,3% contra +7,6% das barradas), mas pode estar ajustada ao passado.
- Comunicados do FNET só existem na base a partir de 05/2025 (43 fundos); antes, só fatos relevantes.
- Os anos de 2018 a 2026 já foram olhados várias vezes. O teste de verdade é acompanhar daqui para a frente, sinal a
  sinal, anotando o veredito antes de saber o resultado.
