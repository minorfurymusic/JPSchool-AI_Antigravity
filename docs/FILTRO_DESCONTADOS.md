# Filtro "descontados saudáveis com rendimento constante" — PROPOSTA (18/11/2026, ainda não rodada)

Objetivo do dono: fundos que caíram de forma significativa, mas sem a crise de desespero do Kairi; descontados,
saudáveis, com rendimento constante (de preferência sempre o mesmo valor) e que paguem bem. Expectativa do dono:
juros caindo em 2027 e terminando o ano abaixo de 10%.

Todos os números são escolha inicial, para o dono aprovar ou mudar ANTES de rodar. Depois de rodar, não se mexe
nas regras para melhorar o resultado do passado.

## Regras de entrada (no fim de cada mês, só com dado publicado até o dia)

| # | Grupo | Regra | Hoje na carteira 2 (versão D) |
|---|---|---|---|
| 1 | Tamanho | Patrimônio de R$ 100 milhões ou mais | igual |
| 2 | Negociação | Negociação típica (mediana de 60 pregões) de R$ 250 mil/dia ou mais | igual |
| 3 | Bloqueios | Sem amortização relevante em 12 meses; sem aviso de liquidação, incorporação, fusão, venda de todos os ativos ou ida para o balcão (bloqueios do Kairi) | só a avaliação de saúde |
| 4 | Queda | Cota caiu de 10% a 25% em 6 meses (queda maior é terreno do Kairi) | não existia |
| 5 | Desconto | Preço entre 0,60 e 0,90 do patrimônio | 0,60 a 0,85 |
| 6 | Patrimônio | Patrimônio por cota não caiu mais de 5% em 12 meses | igual |
| 7 | Paga bem | Rendimento do ano sobre o preço pelo menos 2 pontos acima da mediana do tipo de fundo | igual |
| 8 | Constância | Nos 12 meses: pagou em pelo menos 11 meses; no máximo 1 mês com queda de mais de 2%; oscilação (desvio ÷ média) até 0,03; últimos 3 meses não abaixo dos 3 primeiros | oscilação até 0,15, até 2 cortes de 5%, tendência até −10% |
| 9 | Cobertura | Cobertura do rendimento (CVM) de 1,0 ou mais; fundo sem a medida não entra | não existia (testada a 0,90: piorou) |
| 10 | Saúde | Avaliação de saúde diferente de NÃO COMPRAR | igual |
| 11 | Leitura | Antes de comprar de verdade: ler o relatório gerencial mais recente (Skill `avaliar-fundo`, passo 4) | igual |

## Escolha e carteira

- Nota: média das posições em rendimento acima do tipo, desconto e constância. Os 5 melhores, pesos iguais.
- Compra na abertura do primeiro pregão do mês seguinte. Dinheiro parado em 105% do CDI.
- Custos: 0,03% por operação; imposto de 20% sobre ganho de venda, com prejuízo abatendo; rendimento isento.

## Regras de saída

- Doença confirmada em 2 revisões seguidas: rendimento caindo mais de 15% ou 3 cortes em 12 meses, patrimônio por cota
  caindo mais de 5% em 12 meses, ou avaliação de saúde NÃO COMPRAR (igual à versão D).
- Corte de rendimento de mais de 5% num mês: sai na revisão seguinte (novo).
- Preço chega a 0,95 do patrimônio: sai (igual à versão D).

## Como medir

- R$ 10 mil, 2018 a 2026, contra 105% do CDI.
- Resultado separado por fase da Selic (subindo, parada, caindo), sabendo que são poucos ciclos.
- Lista dos fundos que passam hoje, com a leitura do relatório de cada um.
