# Busca de um modelo lucrativo

Data: 2026-11-16. Programa: `estudos/busca_modelo.py` (escrito e rodado por agente auxiliar; lê só das planilhas). Resultados completos em `planilhas/tecnico/busca_celulas.csv`, `busca_saidas.csv` e `busca_operacoes.csv`.

## Resultado em uma frase

**Não achei modelo que ganhe da Selic líquida fora do período em que foi escolhido.** Tudo que foi bom de 2018 a 2022 foi ruim de 2023 a 2026.

## Como a busca foi feita

- **Todos os fatos relevantes**, bons e ruins: 7.962 anúncios, dos quais 3.839 passaram nos filtros fixos.
- **Filtros fixos (regras do dono):** patrimônio de R$ 50 milhões ou mais; ordem de R$ 500 ou mais (2% do negociado por dia); fundo pagando rendimento; sem amortização relevante; XPPR11 fora.
- **Entrada:** abertura do pregão seguinte ao anúncio.
- **Combinações de entrada testadas:** tipo do anúncio (7 grupos, mais a soma dos "bons") x desconto (4 faixas) x cota acima ou abaixo da média de 200 pregões x Selic nos 6 meses anteriores (subiu, caiu, parada). São 480 combinações; 194 têm 20 casos ou mais no período de escolha.
- **Saídas testadas nas 3 melhores entradas:** 120 combinações de alvo (+5%, +7%, +10%, +15%, nenhum), limite de perda (−7%, −10%, −15%, nenhum), prazo (60, 120, 252 pregões) e saída quando o rendimento cai.
- **Conta completa:** valorização, rendimento, taxa de 0,03%, imposto de 20% e Selic líquida no mesmo período.
- **Trava:** a regra é escolhida só com entradas até 31/12/2022 (escolha) e medida nas entradas de 2023 em diante (conferência).
- **Sorteio:** a mesma saída aplicada a outro fundo parecido, na mesma data, sem anúncio.

"Acima da Selic" abaixo quer dizer: resultado depois de custos e imposto, menos a Selic líquida do mesmo período.

## O que foi bom na escolha foi ruim na conferência

Entre as 171 combinações com casos suficientes nos dois períodos, a relação entre o resultado na escolha e na conferência é **negativa** (−0,25, numa escala de −1 a +1). Quanto melhor no passado, pior depois.

As 3 melhores entradas do período de escolha, cada uma com a sua melhor saída:

| Modelo | Entrada | Saída | Escolha: operações | Escolha: acima da Selic | Conferência: operações | Conferência: acima da Selic | Conferência: ganharam da Selic |
|---|---|---|---|---|---|---|---|
| 1 | Venda de imóvel, cota abaixo da média de 200 pregões, Selic parada | limite de −10%, prazo de 252 | 16 | +33,4% | 33 | −8,6% | 18% |
| 2 | Outros assuntos, cota de 0,30 a 0,60 do valor patrimonial | limite de −10%, prazo de 60, sai se o rendimento cai | 22 | +21,4% | 59 | −1,5% | 39% |
| 3 | Anúncios bons, cota de 0,30 a 0,60, abaixo da média de 200 pregões | limite de −15%, prazo de 252 | 16 | +23,7% | 32 | −2,4% | 41% |

Das 120 formas de sair, quantas ficaram acima da Selic:

| Modelo | Na escolha | Na conferência |
|---|---|---|
| 1 | 102 de 120 | 1 de 120 |
| 2 | 60 de 120 | 0 de 120 |
| 3 | 58 de 120 | 0 de 120 |

Contra o sorteio, na conferência: modelo 1, −8,6% contra −2,5% do sorteio; modelo 2, −1,5% contra +0,3%; modelo 3, −2,4% contra −3,5%. O anúncio não rendeu mais que comprar um fundo parecido no mesmo dia sem anúncio.

## Por que os números da escolha eram tão altos

**Um erro de dados no CARE11.** A cota salta de cerca de R$ 2,6 para cerca de R$ 9,2 em 14/03/2022 sem ajuste (provável grupamento de cotas). Operações que atravessam essa data aparecem com +300% a +480%, falsos. Tirando o CARE11:

| Modelo | Escolha, com o CARE11 | Escolha, sem o CARE11 |
|---|---|---|
| 1 | +33,4% | +5,2% |
| 2 | +21,4% | +0,5% |
| 3 | +23,7% | −4,8% |

A conferência não muda, porque o CARE11 não aparece nela. A planilha de preços precisa dessa correção.

## O que os dados mostram de consistente

Anúncios bons, segurando 120 pregões, acima da Selic líquida, por ano de entrada:

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| +4,9% | −0,3% | −0,7% | −4,4% | −3,2% | +1,2% | −7,2% | +1,9% | −8,3% |

- **O ano manda mais que o anúncio.** O resultado acompanha o mercado e a Selic, não o tipo de notícia.
- **Na média, comprar no anúncio e segurar perdeu da Selic líquida** em 6 de 9 anos.
- **A régua de rendimento (Selic líquida + 3) piorou nos dois períodos:** −3,1% e −5,1% com ela, −0,7% e −1,9% sem.
- **Locação nova com a Selic caindo foi ruim nos dois períodos:** −8,4% e −7,1%. Serve como exclusão.
- **Nenhum tipo de fundo ganhou nos dois períodos.** Lajes: −2,2% e −0,1%. Logística: −2,0% e −2,3%. Shoppings: −2,1% e −4,1%.
- **Nenhuma faixa de liquidez ganhou nos dois períodos.**
- **"Casos estranhos" (notícia ruim, fundo muito descontado, muito abaixo do maior preço) não deram lucro consistente.** Cota mais de 30% abaixo do maior preço: +4,1% na escolha, −7,2% na conferência.

## Conclusão

- Com o anúncio lido por palavras e os dados diários que temos, **o gatilho de anúncio não dá vantagem mensurável sobre a Selic líquida**.
- Os achados do Estudo Agressivo (laje corporativa, cota acima da média de 200 pregões, fundo declarando aumento) eram de 34 a 37 casos. No conjunto grande e com período de conferência, **não se sustentaram**.
- Isso não prova que a ideia do dono é errada. Prova que **esta leitura dos anúncios não a captura**: ela não sabe o tamanho do aumento, quanto tempo dura, nem se é de verdade.

## Limites

- A conferência (2023 a 2026) é um período de Selic alta. Um modelo pode ser ruim nele e bom em outro.
- O programa do agente não foi revisado linha a linha. O agente refez 3 operações à mão e os números bateram. Eu confirmei o salto do CARE11 na planilha.
- CACR11 caiu 42% num dia (04/05/2026); não se sabe se é real ou erro de dados.
- 179 operações em aberto ficaram fora das contas.

## Caminhos possíveis (decisão do dono)

1. **Ler os anúncios com IA** (chave do Gemini, pelo formulário seguro), para saber tamanho, duração e origem do aumento. É o único caminho que ataca a causa.
2. **Corrigir os dados** (CARE11 e outros saltos sem ajuste) antes de qualquer novo teste.
3. **Testar com o mesmo rigor a base do conservador** (fundo bom que caiu 15% a 20% com rendimento mantido), que foi o melhor resultado até agora e ainda não passou por conferência em período separado.
4. **O dono listar operações reais que fez e deram certo.** Com 10 a 20 casos concretos dá para ver o que eles têm em comum e que os programas não estão enxergando.
