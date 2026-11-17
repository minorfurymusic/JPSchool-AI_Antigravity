# Simulação do Kairi em 2026: carteira de R$ 20.000

Programa: `estudos/kairi_carteira_2026.py` (rodada do zero em poucos segundos; comando: `cd /home/user/JPSchool-AI_Antigravity && PYTHONPATH=. python3 estudos/kairi_carteira_2026.py`). Planilha com gráficos: `planilhas/kairi_carteira_2026.xlsx` (abas Resumo, Posições abertas, Patrimônio dia a dia, Quanto estava aplicado, Mês a mês, Operações, Variantes, Fundos bloqueados, Saiu da bolsa, Sinais sem dinheiro, Legenda e avisos).
Gerado automaticamente; os números abaixo vêm da rodada do programa. Este documento tem a **Versão 2** (2026-11-17, regras novas), a **Versão 1** (regras antigas, resumida) e a conferência da queda geral de 26/10/2026.

## Versão 2 (2026-11-17): regras novas decididas pelo dono

### Resultado em uma frase

De 02/01/2026 a 09/11/2026, a carteira total de R$ 20.000 foi para R$ 20.839,66 (4,2%; 3,7% descontando o imposto que seria devido ao vender tudo), contra R$ 22.007,15 (10,0%) de deixar tudo em 105% do CDI e R$ 19.396,19 (-3,0%) do mercado de fundos. Perdeu do CDI nas duas sub-carteiras. Na versão 1 (regras antigas) o total tinha ficado em R$ 20.597,01 (3,0%; 2,7% líquido).

### Regras novas

1. **Não comprar fundo que vai sair da bolsa (as duas sub-carteiras).** No dia do sinal, o fundo é bloqueado se, nos 365 dias corridos até o dia do sinal (inclusive), houve fato relevante do mesmo fundo (`planilhas/tecnico/fatos_textos.csv.gz`, coluna de texto, e `planilhas/anuncios.csv`; os dois têm os mesmos 7962 fatos) tratando de liquidação/dissolução/encerramento do fundo, incorporação, fusão, cisão ou venda da totalidade dos ativos. A busca é por expressões específicas no texto sem acento e em minúsculas, por exemplo: “liquidação do fundo”; “dissolução do fundo”; “encerramento do fundo”; “incorporação do fundo”; “fusão de fundos”; “cisão do fundo”; “venda da totalidade dos ativos”; “alienação dos ativos do fundo”. "Liquidação financeira", "liquidez" e "liquidação de CRI" não casam com nenhuma delas. Só entram fatos com data até o dia do sinal (o programa confere com um assert). Ajustes feitos depois de testar: (a) o fato de XPIN11 de 16/04/2026 diz "alienação dos ativos imobiliários de titularidade do Fundo" e não usa a palavra "totalidade"; sem uma expressão própria para isso a regra deixaria XPIN11 passar, então ela foi acrescentada; (b) "cisão" só conta como "cisão total" ou "cisão do fundo" (a palavra solta casava com "decisão" e "rescisão" e com cisão de outras empresas); "fusão" só como fusão de fundos; (c) trechos com "reprovada", "cancelada", "desistência" por perto não bloqueiam, e um fato de reprovação anula os fatos anteriores (ITIT11: a dissolução proposta em 26/06 foi reprovada em 07/08/2026).
2. **Conservadora:** gatilho de 20% como antes **e** só fundos com volume médio de 60 dias (`volume_medio_60 (R$)`, valor do dia do sinal, só dados até esse dia) de R$ 500.000 ou mais.
3. **Agressiva:** igual à versão 1 (gatilho de 15%), só com a regra 1.
4. **Variante da conservadora com gatilho de 30%**, também com volume de R$ 500.000 ou mais.
5. **Fundo comprado que ainda assim sair da bolsa:** não é vendido em silêncio pelo último preço. A operação é marcada "saiu da bolsa — valor real desconhecido", o cálculo continua pelo último preço e ela aparece na tabela à parte "Fundos comprados que saíram da bolsa".

### O que foi simulado

- **Duas sub-carteiras independentes**, cada uma com caixa próprio de R$ 10.000 em 02/01/2026 (primeiro pregão do ano). Começam vazias: só valem sinais com data a partir de 02/01/2026.
- **Conservadora:** compra quando a cota fecha 20% ou mais abaixo da média dos últimos 200 pregões (o "gatilho"), com rendimento do fundo mantido e volume de 60 dias de R$ 500 mil ou mais. **Agressiva:** gatilho de 15%. **Variante extra:** conservadora com gatilho de 30%.
- **Mesmas regras das ordens já estudadas** (`estudos/auditoria_bloco2.py`, cópia verificada de `kairi_ordens.py`): universo de fundos, filtros (patrimônio, negociado, rendimento, preço sobre valor patrimonial), guarda de dados com saltos e buracos, entrada na abertura do pregão seguinte ao sinal, saída quando a máxima do dia toca a média de 200 pregões (vende pelo preço da média, ou pela abertura se for maior) ou no prazo de 252 pregões.
- **Tamanho da ordem:** R$ 1.000 (testes com R$ 500 e R$ 2.000), cotas inteiras, no máximo 2% do negociado médio do fundo em 60 dias e no máximo o caixa disponível. Abaixo de R$ 200 não compra. O mesmo fundo não pode ser comprado de novo enquanto já está na sub-carteira. Se há mais sinais que dinheiro no mesmo dia, compra primeiro o fundo mais negociado.
- **Taxa:** 0,03% na compra e 0,03% na venda.
- **Rendimentos** (isentos) entram no caixa na **data de pagamento** (`rendimentos_pagamentos.csv`). Tem direito quem estava com a cota no fechamento da data de corte do aviso (a "data-base"), a mesma regra de `kairi_ordens.py`. Pagamento em dia sem pregão entra no pregão seguinte.
- **Caixa parado** rende 105% do CDI com liquidez diária (`cdi.csv`), em lotes: cada entrada de dinheiro é um lote; as compras resgatam do lote mais antigo, com IR regressivo (22,5% até 180 dias corridos; 20% de 181 a 360; 17,5% de 361 a 720; 15% acima) e IOF nos primeiros 29 dias, por lote. O caixa que aparece no patrimônio diário já é líquido de IR e IOF.
- **Imposto do FII:** 20% sobre o ganho líquido das vendas de cada mês (prejuízo abate os ganhos seguintes). O DARF sai do caixa no último dia útil do mês seguinte. Posições abertas no fim ficam a preço de 09/11/2026; mostramos também o valor líquido do imposto que seria devido se fossem vendidas.
- **Comparações:** R$ 20.000 todo em 105% do CDI (líquido de IR, como resgatado em 09/11/2026), o índice "mercado" (`mercado.csv`, fundo imobiliário do meio) e a versão 1.

### Tabela 1. Resumo (ordem de R$ 1.000)

| Indicador | Conservadora (20%, vol. ≥ R$ 500 mil) | Agressiva (15%) | Total (R$ 20 mil) | 105% do CDI (R$ 20 mil) | Mercado (R$ 20 mil) |
|---|---|---|---|---|---|
| Patrimônio inicial | R$ 10.000,00 | R$ 10.000,00 | R$ 20.000,00 | R$ 20.000,00 | R$ 20.000,00 |
| Patrimônio final (cotas a preço de 09/11) | R$ 10.378,79 | R$ 10.460,87 | R$ 20.839,66 | R$ 22.007,15 | R$ 19.396,19 |
| Retorno no período | 3,8% | 4,6% | 4,2% | 10,0% | -3,0% |
| Patrimônio final líquido do imposto que seria devido | R$ 10.378,79 | R$ 10.367,00 | R$ 20.745,80 | R$ 22.007,15 | R$ 19.396,19 |
| Retorno líquido | 3,8% | 3,7% | 3,7% | 10,0% | -3,0% |
| Retorno líquido contra o CDI (pontos) | -6,2 | -6,4 | -6,3 | 0,0 | -13,1 |
| Maior queda no caminho | -5,7% | -10,8% | -8,1% | 0,0% | -10,5% |
| ... do pico em / até | 23/10/2026 / 09/11/2026 | 09/10/2026 / 03/11/2026 | 22/10/2026 / 03/11/2026 | — | 23/10/2026 / 03/11/2026 |
| Operações abertas / fechadas | 3 / 0 | 12 / 9 | 15 / 9 | — | — |
| Fechadas com lucro | nd | 88,9% | 88,9% | — | — |
| Todas com lucro (abertas a preço de 09/11) | 33,3% | 57,1% | 54,2% | — | — |
| Pior operação | -35,1% TGAR11 | -47,3% MCEM11 | -47,3% MCEM11 | — | — |
| Melhor operação | 2,2% RBRX11 | 21,0% RBRP11 | 21,0% RBRP11 | — | — |
| Rendimentos recebidos | R$ 64,01 | R$ 394,45 | R$ 458,46 | — | — |
| Imposto do FII pago | R$ 0,00 | R$ 39,64 | R$ 39,64 | — | — |
| Imposto do FII devido e não pago | R$ 0,00 | R$ 93,87 | R$ 93,87 | — | — |
| Imposto se vendesse as abertas em 09/11 | R$ 0,00 | R$ 0,00 | R$ 0,00 | — | — |
| IR e IOF retidos do caixa | R$ 53,81 | R$ 162,69 | R$ 216,49 | R$ 501,79 | — |
| Taxas de compra e venda | R$ 0,88 | R$ 8,73 | R$ 9,62 | — | — |
| Sinais bloqueados pela regra 1 (fundo que pode sair da bolsa) | 4 | 15 | 19 | — | — |
| Sinais barrados pelo volume (< R$ 500 mil) | 11 | 0 | 11 | — | — |
| Compras que depois saíram da bolsa | 0 | 1 | 1 | — | — |
| Sinais sem dinheiro | 0 | 22 | 22 | — | — |
| Giro | 0,28 | 1,94 | 1,10 | — | — |
| Tempo médio por operação fechada (dias) | nd | 51,1 | 51,1 | — | — |
| Dinheiro aplicado em fundos, em média | 6,0% | 41,5% | 23,7% | — | — |

**Legenda.** *Patrimônio* = caixa (líquido de IR e IOF) + cotas ao último preço, em R$. *Retorno* = final ÷ inicial − 1, no período todo (não por ano). *Líquido* = patrimônio final menos o imposto do FII devido (de vendas já feitas e do que seria cobrado se as cotas abertas fossem vendidas em 09/11). *Contra o CDI* = retorno líquido menos o retorno líquido do 105% do CDI, em pontos percentuais. *Maior queda* = maior distância, em %, de um valor alto do patrimônio até o ponto mais baixo seguinte. *Operações abertas* = ainda com cotas em 09/11. *Com lucro* = resultado (valorização + rendimentos declarados − taxas) maior que zero. *Pior/melhor* = em % do valor comprado. *Imposto do FII pago* = DARF efetivamente pago até 09/11. *IR e IOF retidos do caixa* = imposto cobrado nos resgates do dinheiro parado (no 105% do CDI de R$ 20 mil, o IR do fim). *Sinais bloqueados* = sinais descartados pela regra 1. *Barrados pelo volume* = sinais descartados por volume médio de 60 dias abaixo de R$ 500 mil (só na conservadora). *Sinais sem dinheiro* = sinais em que a compra era possível pelo negociado, mas o caixa não tinha R$ 200 livres. *Giro* = total comprado em fundos ÷ patrimônio médio. *Dinheiro aplicado em fundos* = média diária de (valor das cotas ÷ patrimônio).

**Leitura prática.** A carteira ficou 6,3 pontos abaixo do CDI: ganhou 3,7% contra 10,0%. Até 22/10/2026 o total chegou a R$ 22.452,93; de 22/10/2026 a 03/11/2026 caiu 8,1%. As 15 posições ainda abertas somam resultado de R$ -1.361,14 contando os rendimentos já declarados (R$ -1.432,44 contando só os já pagos, como na tabela de posições abertas; as piores: TGAR11 (-35,1%), APXM11 (-29,7%), VGHF11 (-28,9%)); as fechadas somam R$ 811,29. Os rendimentos recebidos (R$ 458,46) não cobriram essas perdas.

### Tabela 1b. Versão 2 contra versão 1 (ordem de R$ 1.000)

| Indicador | Conservadora v1 | Conservadora v2 | Agressiva v1 | Agressiva v2 | Total v1 | Total v2 |
|---|---|---|---|---|---|---|
| Patrimônio final (cotas a preço de 09/11) | R$ 10.170,81 | R$ 10.378,79 | R$ 10.426,20 | R$ 10.460,87 | R$ 20.597,01 | R$ 20.839,66 |
| Retorno no período | 1,7% | 3,8% | 4,3% | 4,6% | 3,0% | 4,2% |
| Patrimônio final líquido do imposto | R$ 10.170,81 | R$ 10.378,79 | R$ 10.365,26 | R$ 10.367,00 | R$ 20.536,07 | R$ 20.745,80 |
| Retorno líquido | 1,7% | 3,8% | 3,7% | 3,7% | 2,7% | 3,7% |
| Retorno líquido contra o CDI (pontos) | -8,3 | -6,2 | -6,4 | -6,4 | -7,4 | -6,3 |
| Maior queda no caminho | -10,1% | -5,7% | -12,7% | -10,8% | -11,2% | -8,1% |
| Operações abertas / fechadas | 11 / 2 | 3 / 0 | 12 / 12 | 12 / 9 | 23 / 14 | 15 / 9 |
| Rendimentos recebidos | R$ 157,36 | R$ 64,01 | R$ 421,01 | R$ 394,45 | R$ 578,37 | R$ 458,46 |
| Imposto do FII pago | R$ 60,93 | R$ 0,00 | R$ 22,55 | R$ 39,64 | R$ 83,48 | R$ 39,64 |
| Compras que saíram da bolsa | 1 | 0 | 4 | 1 | 5 | 1 |
| Sinais bloqueados (regra 1) / barrados por volume (regra 2) | 0 / 0 | 4 / 11 | 0 / 0 | 15 / 0 | 0 / 0 | 19 / 11 |
| Sinais sem dinheiro | 0 | 0 | 29 | 22 | 29 | 22 |

**Legenda.** *v1* = regras antigas (gatilhos de 20% e 15%, sem filtro de volume e sem bloqueio por fato), rodadas de novo pelo mesmo programa; o programa confere que os valores finais batem com os do documento antigo (R$ 10.170,81; R$ 10.426,20; R$ 20.597,01). *v2* = regras novas. Demais colunas como na Tabela 1.

**Leitura prática.** O retorno líquido do total foi de 2,7% na versão 1 para 3,7% na versão 2 (1,0 pontos); a conservadora foi de 1,7% para 3,8% e a agressiva de 3,7% para 3,7%. A conservadora passou de 13 para 3 compras (o volume mínimo tirou 11 sinais e a regra 1 mais 4). As duas continuam abaixo do CDI. Atenção: as regras novas foram decididas depois de ver 2026, então a melhora é, em parte, por construção.

### Tabela 2. Retorno mês a mês

| Mês | Conservadora | Agressiva | Total | 105% do CDI | Mercado |
|---|---|---|---|---|---|
| jan/26 | 0,8% | 0,8% | 0,8% | 0,8% | 2,5% |
| fev/26 | 0,9% | 0,9% | 0,9% | 0,9% | 1,1% |
| mar/26 | 1,0% | 1,7% | 1,3% | 1,0% | -0,6% |
| abr/26 | 0,9% | 1,2% | 1,1% | 0,9% | 1,2% |
| mai/26 | 1,6% | -2,3% | -0,4% | 0,9% | -1,3% |
| jun/26 | 0,6% | -1,0% | -0,2% | 0,9% | -0,5% |
| jul/26 | 0,9% | 4,2% | 2,5% | 1,2% | -0,1% |
| ago/26 | 0,2% | -1,8% | -0,8% | 0,9% | -0,9% |
| set/26 | 0,3% | 1,9% | 1,1% | 0,9% | 0,5% |
| out/26 | -1,2% | 0,2% | -0,5% | 0,9% | -3,4% |
| nov/26 (até 09/11) | -2,3% | -1,1% | -1,7% | 0,2% | -1,4% |

**Legenda.** Retorno de cada mês = patrimônio do último pregão do mês ÷ patrimônio do último pregão do mês anterior − 1. Janeiro parte do fechamento de 02/01/2026; novembro vai até 09/11. "Total" = as duas sub-carteiras somadas.

**Leitura prática.** O total ganhou do 105% do CDI em 4 dos 11 meses. O pior mês foi nov/26 (-1,7%), junto com a queda do mercado. Os meses em que ficou abaixo do CDI foram: mai/26, jun/26, ago/26, out/26, nov/26.

### Tabela 3. Variantes (cada linha parte de R$ 10.000)

| Sub-carteira | Gatilho | Volume mínimo | Ordem | Patrimônio final (preço de 09/11) | Patrimônio final líquido | Retorno líquido | Retorno líquido da versão 1 | Maior queda | Operações (v2 / v1) | Giro | Sinais sem dinheiro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservadora | 20% | R$ 500.000 | R$ 500 | R$ 10.701,18 | R$ 10.701,18 | 7,0% | 6,4% | -2,6% | 3 / 13 | 0,14 | 0 |
| Conservadora | 20% | R$ 500.000 | R$ 1.000 | R$ 10.378,79 | R$ 10.378,79 | 3,8% | 1,7% | -5,7% | 3 / 13 | 0,28 | 0 |
| Conservadora | 20% | R$ 500.000 | R$ 2.000 | R$ 9.734,03 | R$ 9.734,03 | -2,7% | -6,7% | -12,0% | 3 / 9 | 0,57 | 0 |
| Agressiva | 15% | — | R$ 500 | R$ 11.073,46 | R$ 10.991,69 | 9,9% | 8,2% | -6,6% | 36 / 39 | 1,64 | 3 |
| Agressiva | 15% | — | R$ 1.000 | R$ 10.460,87 | R$ 10.367,00 | 3,7% | 3,7% | -10,8% | 21 / 24 | 1,94 | 22 |
| Agressiva | 15% | — | R$ 2.000 | R$ 9.506,02 | R$ 9.506,02 | -4,9% | -2,2% | -13,7% | 15 / 14 | 1,62 | 32 |
| Conservadora 30% | 30% | R$ 500.000 | R$ 500 | R$ 10.872,95 | R$ 10.872,95 | 8,7% | 6,3% | -0,9% | 1 / 2 | 0,05 | 0 |
| Conservadora 30% | 30% | R$ 500.000 | R$ 1.000 | R$ 10.742,32 | R$ 10.742,32 | 7,4% | 2,5% | -2,1% | 1 / 2 | 0,09 | 0 |
| Conservadora 30% | 30% | R$ 500.000 | R$ 2.000 | R$ 10.469,20 | R$ 10.469,20 | 4,7% | -0,5% | -4,6% | 1 / 2 | 0,19 | 0 |
| 105% do CDI (R$ 10 mil) | — | — | — | R$ 11.003,58 | R$ 11.003,58 | 10,0% | 10,0% | 0,0% | — | — | — |

**Legenda.** *Gatilho* = queda abaixo da média de 200 pregões que dispara a compra. *Volume mínimo* = volume médio de 60 dias exigido no dia do sinal. *Ordem* = valor pretendido por compra. *Patrimônio final líquido* = descontado o imposto do FII devido e o que seria devido ao vender as posições abertas. *Retorno líquido* = patrimônio final líquido ÷ R$ 10.000 − 1; a coluna seguinte é o mesmo número na versão 1. *Operações (v2 / v1)* = número de compras nas duas versões. *Giro* = total comprado ÷ patrimônio médio. A última linha é R$ 10.000 em 105% do CDI.

**Leitura prática.** Todas as variantes ficaram abaixo do 105% do CDI (10,0%). Quanto maior a ordem, pior o resultado neste ano; ordens maiores esgotam o caixa mais cedo (deixam passar sinais) e fazem as perdas pesarem mais. Com apenas esta amostra, isso não é uma regra. A conservadora de 30% fez 1 compra(s) na versão 2 e 2 na versão 1: o resto do dinheiro ficou parado no CDI.

### Tabela 4. Operações fechadas (ordem de R$ 1.000)

| Sub-carteira | Fundo | Entrada | Saída (ou último preço) | Motivo | Valor da compra | Rendimentos | Resultado | Resultado (%) |
|---|---|---|---|---|---|---|---|---|
| Agressiva | MCEM11 | 09/03/2026 | 17/03/2026 | volta à média | R$ 841,82 | R$ 0,00 | R$ 65,90 | 7,8% |
| Agressiva | MCEM11 | 12/05/2026 | 25/06/2026 | saiu da bolsa — valor real desconhecido | R$ 818,72 | R$ 0,00 | R$ -387,58 | -47,3% |
| Agressiva | VVCR11 | 02/07/2026 | 07/07/2026 | volta à média | R$ 995,52 | R$ 0,00 | R$ 167,05 | 16,8% |
| Agressiva | VVCR11 | 15/07/2026 | 22/07/2026 | volta à média | R$ 997,53 | R$ 15,99 | R$ 180,31 | 18,1% |
| Agressiva | RBRP11 | 05/08/2026 | 30/09/2026 | volta à média | R$ 975,20 | R$ 16,10 | R$ 204,61 | 21,0% |
| Agressiva | VVCR11 | 01/10/2026 | 02/10/2026 | volta à média | R$ 993,28 | R$ 0,00 | R$ 174,23 | 17,5% |
| Agressiva | FIIP11 | 16/03/2026 | 07/10/2026 | volta à média | R$ 930,16 | R$ 69,30 | R$ 99,35 | 10,7% |
| Agressiva | RBHG11 | 14/08/2026 | 09/10/2026 | volta à média | R$ 938,91 | R$ 26,52 | R$ 178,64 | 19,0% |
| Agressiva | VCRR11 | 05/08/2026 | 22/10/2026 | volta à média | R$ 962,64 | R$ 15,84 | R$ 128,78 | 13,4% |

**Legenda.** *Motivo:* volta à média = a cota subiu até a média de 200 pregões; saiu da bolsa — valor real desconhecido = os preços acabaram antes de 09/11 e o cálculo usa o último preço (não é uma venda real). *Rendimentos* = o que o fundo pagou por cota enquanto se tinha a cota (inclui os ainda a receber). *Resultado* = valorização + rendimentos − taxas, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor da compra.

**Leitura prática.** Das 9 operações fechadas, as 8 de volta à média tiveram resultado entre 7,8% e 21,0%; as 1 marcada(s) 'saiu da bolsa' ficaram entre -47,3% e -47,3%. A conservadora não fechou nenhuma operação: as 3 compras dela estão abertas.

### Tabela 5. Posições abertas em 09/11/2026 (ordem de R$ 1.000)

**Conservadora**

| Fundo | Entrada | Preço de entrada | Cotas | Valor de entrada | Último preço | Data do último preço | Valor atual | Rendimentos já pagos | Rendimentos a receber | Resultado (R$) | Resultado (%) | Positivo / negativo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VGHF11 | 19/05/2026 | R$ 5,75 | 173 | R$ 994,75 | R$ 3,99 | 09/11/2026 | R$ 690,27 | R$ 64,01 | R$ 0,00 | R$ -240,77 | -24,2% | negativo |
| TGAR11 | 14/10/2026 | R$ 50,04 | 19 | R$ 950,76 | R$ 32,05 | 09/11/2026 | R$ 608,95 | R$ 0,00 | R$ 8,74 | R$ -342,10 | -36,0% | negativo |
| RBRX11 | 04/11/2026 | R$ 6,26 | 159 | R$ 995,34 | R$ 6,40 | 09/11/2026 | R$ 1.017,60 | R$ 0,00 | R$ 0,00 | R$ 21,96 | 2,2% | positivo |
| **TOTAL Conservadora (3)** |  |  |  | **R$ 2.940,85** |  |  | **R$ 2.316,82** | **R$ 64,01** | **R$ 8,74** | **R$ -560,90** | **-19,1%** | 1 positivas / 2 negativas |

**Agressiva**

| Fundo | Entrada | Preço de entrada | Cotas | Valor de entrada | Último preço | Data do último preço | Valor atual | Rendimentos já pagos | Rendimentos a receber | Resultado (R$) | Resultado (%) | Positivo / negativo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VGHF11 | 02/06/2026 | R$ 6,03 | 165 | R$ 994,95 | R$ 3,99 | 09/11/2026 | R$ 658,35 | R$ 49,50 | R$ 0,00 | R$ -287,40 | -28,9% | negativo |
| APXM11 | 26/06/2026 | R$ 69,99 | 14 | R$ 979,86 | R$ 48,00 | 06/11/2026 | R$ 672,00 | R$ 17,48 | R$ 0,00 | R$ -290,68 | -29,7% | negativo |
| LIFE11 | 29/06/2026 | R$ 7,08 | 141 | R$ 998,28 | R$ 6,76 | 09/11/2026 | R$ 953,16 | R$ 81,78 | R$ 0,00 | R$ 36,36 | 3,6% | positivo |
| TRBL11 | 03/07/2026 | R$ 57,65 | 17 | R$ 980,05 | R$ 44,38 | 09/11/2026 | R$ 754,46 | R$ 22,44 | R$ 7,48 | R$ -203,44 | -20,8% | negativo |
| MAXR11 | 10/07/2026 | R$ 49,78 | 20 | R$ 995,60 | R$ 55,56 | 09/11/2026 | R$ 1.111,20 | R$ 23,70 | R$ 0,00 | R$ 139,00 | 14,0% | positivo |
| CRFF11 | 13/07/2026 | R$ 67,47 | 14 | R$ 944,58 | R$ 63,03 | 09/11/2026 | R$ 882,42 | R$ 27,30 | R$ 9,10 | R$ -35,14 | -3,7% | negativo |
| RBHY11 | 06/08/2026 | R$ 63,15 | 15 | R$ 947,25 | R$ 55,05 | 09/11/2026 | R$ 825,75 | R$ 28,50 | R$ 13,50 | R$ -93,28 | -9,8% | negativo |
| BCRI11 | 05/10/2026 | R$ 53,04 | 18 | R$ 954,72 | R$ 48,70 | 09/11/2026 | R$ 876,60 | R$ 0,00 | R$ 12,60 | R$ -78,41 | -8,2% | negativo |
| PATC11 | 20/10/2026 | R$ 33,31 | 27 | R$ 899,37 | R$ 34,01 | 09/11/2026 | R$ 918,27 | R$ 0,00 | R$ 2,43 | R$ 18,63 | 2,1% | positivo |
| RBRX11 | 29/10/2026 | R$ 6,68 | 149 | R$ 995,32 | R$ 6,40 | 09/11/2026 | R$ 953,60 | R$ 0,00 | R$ 0,00 | R$ -42,02 | -4,2% | negativo |
| HSLG11 | 30/10/2026 | R$ 74,69 | 13 | R$ 970,97 | R$ 70,99 | 09/11/2026 | R$ 922,87 | R$ 0,00 | R$ 8,45 | R$ -48,39 | -5,0% | negativo |
| INLG11 | 30/10/2026 | R$ 58,30 | 15 | R$ 874,50 | R$ 59,20 | 09/11/2026 | R$ 888,00 | R$ 0,00 | R$ 9,00 | R$ 13,24 | 1,5% | positivo |
| **TOTAL Agressiva (12)** |  |  |  | **R$ 11.535,45** |  |  | **R$ 10.416,68** | **R$ 250,70** | **R$ 62,56** | **R$ -871,53** | **-7,6%** | 4 positivas / 8 negativas |

**Legenda.** *Valor de entrada* = cotas × preço de entrada (sem a taxa). *Último preço* e sua data = último fechamento conhecido do fundo (se a data não é 09/11, o fundo não negociou nos dias seguintes). *Valor atual* = cotas × último preço. *Rendimentos já pagos* = só os de data de pagamento até 09/11/2026 (já estão no caixa). *Rendimentos a receber* = declarados, com pagamento depois de 09/11; **não entram** no resultado desta tabela. *Resultado (R$)* = valor atual − valor de entrada + rendimentos já pagos − taxa de compra, antes do imposto do FII. *Resultado (%)* = resultado ÷ valor de entrada. *Positivo / negativo* = sinal do resultado. O gráfico de colunas do resultado (%) de cada posição está na aba "Posições abertas" da planilha.

**Leitura prática.** Na conservadora, 2 das 3 posições abertas estão no prejuízo; na agressiva, 8 das 12. Juntas, as 15 posições custaram R$ 14.476,30 e valem R$ 12.733,50; já pagaram R$ 314,71 de rendimentos, e há R$ 71,30 a receber. O resultado só vira ganho ou perda de verdade quando as cotas forem vendidas.

### Tabela 6. Fundos comprados que saíram da bolsa — valor real desconhecido

| Sub-carteira | Fundo | Entrada | Último preço (R$) | Data do último preço | Valor da compra | Valor pelo último preço | Resultado simulado | Situação |
|---|---|---|---|---|---|---|---|---|
| Agressiva | MCEM11 | 12/05/2026 | 26,97 | 25/06/2026 | R$ 818,72 | R$ 431,52 | R$ -387,58 (-47,3%) | saiu da bolsa — valor real desconhecido |

**Legenda.** *Último preço* = último fechamento registrado na base (os preços acabam nessa data). *Valor pelo último preço* = cotas × último preço, sem taxa de venda (a taxa de venda de 0,03% entra no resultado). *Resultado simulado* = valor pelo último preço − compra − taxas + rendimentos. O que o cotista realmente recebeu (liquidação, incorporação, leilão) não está na base.

**Leitura prática.** Só 1 compra(s) da versão 2 virou/viraram fundo que saiu da bolsa (na versão 1 eram 5: HCHG11, ITIP11, MCEM11, XPIN11, com R$ 4.206,64 comprados e R$ -783,48 de resultado simulado). O número real do que sobrou pode ser melhor ou pior que o simulado.

### Tabela 7. Fundos bloqueados pela regra 1 em 2026 (todos os gatilhos)

| Fundo | Sinal | Gatilho(s) | Sub-carteira afetada | Fato que bloqueou (data) | Expressão | Trecho do fato | A v1 comprou? | Leitura (manual) |
|---|---|---|---|---|---|---|---|---|
| XPIN11 | 23/06/2026 | 15% | Agressiva | 16/04/2026 (id 1165727; +0) | alienação dos ativos do fundo | …em 11 de março de 2026 e apurada em 27 de março de 2026, na qual os Cotistas aprovaram a alienação dos ativos imobiliários de titularidade do Fundo (“ imóvei s ”) , comunicamos a lavratura da Escritura Pública de Venda e Compra dos refer… | Agressiva (entrada 24/06/2026) | verdadeiro: saída aprovada ou concluída. Venda de todos os imóveis concluída em 14/04/2026; preços acabam em 13/07/2026. |
| XPIN11 | 02/07/2026 | 15% | Agressiva | 30/06/2026 (id 1236212; +1) | encerramento do fundo | …28.516.325/0001-40 / Código de Negociação: XPIN11 Amortização Parcial, Liquidação Final e Encerramento do Fundo A VÓRTX DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA., inscrita no CNPJ/MF sob o n… | — | verdadeiro: saída aprovada ou concluída. Fato de 30/06: liquidação final e encerramento do fundo. |
| ITIT11 | 03/07/2026 | 15%, 20% | Agressiva, Conservadora (já fora pelo volume) | 26/06/2026 (id 1231353; +0) | liquidação do fundo | …s Fundos pelo INHF e subsequente migração de seus cotistas para o INHF, com a consequente liquidação dos Fundos, conforme estrutura proposta pelos Prestadores de Serviços Essenciais (“Reorganização”).… | Conservadora (entrada 06/07/2026); Agressiva (entrada 06/07/2026) | proposta na data, reprovada depois. Fato de 26/06: proposta de consolidar o fundo no INHF, com liquidação, 'caso aprovada'. Reprovada em 07/08/2026; o fundo segue negociando. |
| ITIP11 | 07/07/2026 | 15% | Agressiva | 26/06/2026 (id 1231351; +0) | liquidação do fundo | …s Fundos pelo INHF e subsequente migração de seus cotistas para o INHF, com a consequente liquidação dos Fundos, conforme estrutura proposta pelos Prestadores de Serviços Essenciais (“Reorganização”).… | Agressiva (entrada 08/07/2026) | proposta na data, aprovada depois. Fato de 26/06: mesma proposta de reorganização com liquidação; aprovada em 27/07/2026; preços acabam em 03/09/2026. |
| HCHG11 | 14/07/2026 | 15% | Agressiva | 09/07/2026 (id 1243078; +3) | liquidação do fundo | ….027/0001 - 13 (“VVCR” e “Alienação”, respectivamente), e (ii) A consequente dissolução e liquidação do Fundo, nos termos do plano de liquidação do Fundo (“ Consulta Formal ”). Referida Consulta Form… | Agressiva (entrada 15/07/2026) | verdadeiro: saída aprovada ou concluída. Consulta formal aprovada em 11/2025: venda de 100% dos ativos ao VVCR e liquidação do fundo; fato de 09/07/2026 inicia a liquidação. |
| HCHG11 | 15/07/2026 | 20% | Conservadora (já fora pelo volume) | 09/07/2026 (id 1243078; +3) | liquidação do fundo | ….027/0001 - 13 (“VVCR” e “Alienação”, respectivamente), e (ii) A consequente dissolução e liquidação do Fundo, nos termos do plano de liquidação do Fundo (“ Consulta Formal ”). Referida Consulta Form… | — | verdadeiro: saída aprovada ou concluída. Mesmo fato de 09/07/2026 (liquidação do fundo). |
| ITIP11 | 05/08/2026 | 15% | Agressiva | 27/07/2026 (id 1265524; +1) | liquidação do fundo | …io da Consulta Formal, divulgados nesta data, foi APROVADA, sem ressalvas, a dissolução e liquidação do Fundo, a ser operacionalizada mediante a prévia alienação da totalidade dos ativos integrantes… | — | verdadeiro: saída aprovada ou concluída. Fato de 27/07: aprovada a dissolução e liquidação do fundo. |
| ITIP11 | 07/08/2026 | 15% | Agressiva | 07/08/2026 (id 1280623; +2) | liquidação do fundo | …io da Consulta Formal, divulgados nesta data, foi APROVADA, sem ressalvas, a dissolução e liquidação do Fundo, a ser operacionalizada mediante a prévia alienação da totalidade dos ativos integrantes… | — | verdadeiro: saída aprovada ou concluída. Idem (fatos de 27/07 e 07/08). |
| OUJP11 | 11/08/2026 | 15% | Agressiva | 01/06/2026 (id 1210050; +0) | liquidação do fundo | …reorganização, em decorrência dos quais a estrutura foi novamente ajustada, de modo que a liquidação do Fundo somente ocorrerá caso as aquisições sejam aprovadas e implementadas por ambos os fundos a… | — | proposta ainda pendente em 09/11/2026. Fato de 01/06: a liquidação 'somente ocorrerá caso as aquisições sejam aprovadas'. Fatos de outubro tratam só de troca de administradora; o fundo negocia até 09/11. |
| OUJP11 | 27/08/2026 | 15% | Agressiva | 01/06/2026 (id 1210050; +0) | liquidação do fundo | …reorganização, em decorrência dos quais a estrutura foi novamente ajustada, de modo que a liquidação do Fundo somente ocorrerá caso as aquisições sejam aprovadas e implementadas por ambos os fundos a… | — | proposta ainda pendente em 09/11/2026. Idem. |
| RBRR11 | 18/09/2026 | 15% | Agressiva | 21/08/2026 (id 1298668; +0) | liquidação do fundo | …ndos pelo PCIP11 e subsequente migração de seus cotistas para o PCIP11, com a consequente liquidação dos Fundos, conforme estrutura proposta pela Gestora (“Reorganização”). A Reorganização tem por obje… | — | proposta na data, aprovada depois. Fato de 21/08: reorganização com liquidação, 'caso aprovada'; aprovada em 28/10/2026. |
| RBRR11 | 22/09/2026 | 15% | Agressiva | 21/08/2026 (id 1298668; +0) | liquidação do fundo | …ndos pelo PCIP11 e subsequente migração de seus cotistas para o PCIP11, com a consequente liquidação dos Fundos, conforme estrutura proposta pela Gestora (“Reorganização”). A Reorganização tem por obje… | Agressiva (entrada 23/09/2026) | proposta na data, aprovada depois. Idem. |
| RBRR11 | 02/10/2026 | 15% | Agressiva | 21/08/2026 (id 1298668; +0) | liquidação do fundo | …ndos pelo PCIP11 e subsequente migração de seus cotistas para o PCIP11, com a consequente liquidação dos Fundos, conforme estrutura proposta pela Gestora (“Reorganização”). A Reorganização tem por obje… | — | proposta na data, aprovada depois. Idem. |
| RBRR11 | 27/10/2026 | 15% | Agressiva | 21/08/2026 (id 1298668; +0) | liquidação do fundo | …ndos pelo PCIP11 e subsequente migração de seus cotistas para o PCIP11, com a consequente liquidação dos Fundos, conforme estrutura proposta pela Gestora (“Reorganização”). A Reorganização tem por obje… | — | proposta na data, aprovada depois. Idem (aprovada no dia seguinte). |
| OUJP11 | 28/10/2026 | 15% | Agressiva | 01/06/2026 (id 1210050; +0) | liquidação do fundo | …reorganização, em decorrência dos quais a estrutura foi novamente ajustada, de modo que a liquidação do Fundo somente ocorrerá caso as aquisições sejam aprovadas e implementadas por ambos os fundos a… | Agressiva (entrada 29/10/2026) | proposta ainda pendente em 09/11/2026. Idem. |
| RBRR11 | 03/11/2026 | 20% | Conservadora | 28/10/2026 (id 1360898; +1) | liquidação do fundo | …de aquisição das cotas pela Administradora 01/12/2026 a 09/12/2026 Divulgação do valor de liquidação do Fundo e parcela em cotas do PCIP11 01/12/2026 Entrega cotas do PCIP11 para os cotistas do Fundo… | Conservadora (entrada 04/11/2026) | verdadeiro: saída aprovada ou concluída. Fato de 28/10: aquisição dos ativos pelo PCIP11 aprovada; cronograma de liquidação do fundo em dezembro. |
| RPRI11 | 03/11/2026 | 15% | Agressiva | 21/08/2026 (id 1298559; +0) | liquidação do fundo | …ndos pelo PCIP11 e subsequente migração de seus cotistas para o PCIP11, com a consequente liquidação dos Fundos, conforme estrutura proposta pelo Gestor (“Reorganização”). A Reorganização tem por objet… | — | verdadeiro: saída aprovada ou concluída. Fato de 21/08 (proposta com liquidação); aprovada em 28/10/2026, antes do sinal (a regra mostra o fato de 21/08, mas o de 28/10 já confirmava). |
| OUJP11 | 04/11/2026 | 20% | Conservadora | 01/06/2026 (id 1210050; +0) | liquidação do fundo | …reorganização, em decorrência dos quais a estrutura foi novamente ajustada, de modo que a liquidação do Fundo somente ocorrerá caso as aquisições sejam aprovadas e implementadas por ambos os fundos a… | Conservadora (entrada 05/11/2026) | proposta ainda pendente em 09/11/2026. Idem. |

**Legenda.** *Sinal* = dia em que a cota cruzou o gatilho. *Gatilho(s)* = gatilhos de 15%, 20% ou 30% que deram sinal no mesmo dia. *Sub-carteira afetada* = onde o sinal seria comprado ("já fora pelo volume" = a conservadora também o descartaria pelo volume de 60 dias abaixo de R$ 500 mil). *Fato que bloqueou* = o mais recente dentro da janela, com data, número (id) do fato e quantos outros fatos também casaram (+N). *Expressão* = qual expressão da busca casou. *Trecho* = texto do fato em volta da expressão. *A v1 comprou?* = a versão 1 comprou esse fundo com sinal nesse dia (e em que sub-carteira, com a data de entrada). *Leitura (manual)* = minha leitura do trecho e dos fatos seguintes: "verdadeiro" = saída aprovada ou concluída; "proposta..." = a saída ainda era uma proposta na data.

| Leitura dos bloqueios de 2026 | Quantos | Quais |
|---|---|---|
| verdadeiro: saída aprovada ou concluída | 8 | HCHG11 14/07, HCHG11 15/07, ITIP11 05/08, ITIP11 07/08, RBRR11 03/11, RPRI11 03/11, XPIN11 02/07, XPIN11 23/06 |
| proposta na data, aprovada depois | 5 | ITIP11, RBRR11 |
| proposta na data, reprovada depois | 1 | ITIT11 |
| proposta ainda pendente em 09/11/2026 | 4 | OUJP11 |
| trecho que não trata de saída do próprio fundo (erro de leitura) | 0 | nenhum |
| Total de bloqueios (fundo × dia do sinal) | 18 | 7 fundos |

**Legenda.** Contagem das leituras da tabela anterior (fundo × dia do sinal).

**Leitura prática.** Li os 18 bloqueios de 2026 (todos). Nenhum trecho fugia do assunto (erro de leitura: 0), mas 5 de 18 eram só propostas que não se concretizaram até 09/11 (ITIT11 foi reprovado em 07/08; OUJP11 ainda depende de aprovação). 5 eram propostas depois aprovadas e 8 eram saídas já aprovadas ou concluídas. Bloquear proposta é a leitura mais cautelosa: se a proposta passa, o fundo sai; se não passa, perdeu-se uma compra.

**Confirmação dos três fundos que a versão 1 comprou e saíram da bolsa** (confirmado por execução: o programa tem um assert para cada um):

- HCHG11: a versão 1 comprou (sub-carteira Agressiva, sinal 14/07/2026, entrada 15/07/2026); a regra bloqueia por 4 fato(s) de saída até o sinal (31/10/2025 (id 1026158, liquidação do fundo); 31/10/2025 (id 1026159, liquidação do fundo); 13/11/2025 (id 1037231, liquidação do fundo); 09/07/2026 (id 1243078, liquidação do fundo)). Trecho do mais recente (09/07/2026): “….027/0001 - 13 (“VVCR” e “Alienação”, respectivamente), e (ii) A consequente dissolução e liquidação do Fundo, nos termos do plano de liquidação do Fundo (“ Consulta Formal ”). Referida Consulta Form…” Fatos de saída posteriores ao sinal, ignorados: 31/07/2026.
- XPIN11: a versão 1 comprou (sub-carteira Agressiva, sinal 23/06/2026, entrada 24/06/2026); a regra bloqueia por 1 fato(s) de saída até o sinal (16/04/2026 (id 1165727, alienação dos ativos do fundo)). Trecho do mais recente (16/04/2026): “…em 11 de março de 2026 e apurada em 27 de março de 2026, na qual os Cotistas aprovaram a alienação dos ativos imobiliários de titularidade do Fundo (“ imóvei s ”) , comunicamos a lavratura da Escritura Pública de Venda e Compra dos refer…” Fatos de saída posteriores ao sinal, ignorados: 30/06/2026, 23/07/2026.
- ITIP11: a versão 1 comprou (sub-carteira Agressiva, sinal 07/07/2026, entrada 08/07/2026); a regra bloqueia por 1 fato(s) de saída até o sinal (26/06/2026 (id 1231351, liquidação do fundo)). Trecho do mais recente (26/06/2026): “…s Fundos pelo INHF e subsequente migração de seus cotistas para o INHF, com a consequente liquidação dos Fundos, conforme estrutura proposta pelos Prestadores de Serviços Essenciais (“Reorganização”).…” Fatos de saída posteriores ao sinal, ignorados: 27/07/2026, 07/08/2026, 11/08/2026, 13/08/2026, 06/10/2026, 15/10/2026, 16/10/2026.

Nenhum dos três aparece em compra da versão 2.

### Tabela 8. A regra 1 no período todo, 2018 a 2026 (informativo)

| Gatilho | Sinais | Fundos com sinal | Sinais bloqueados | % bloqueado | Fundos bloqueados | Bloqueados cujos preços acabam em até 252 pregões | Não bloqueados cujos preços acabam em até 252 pregões |
|---|---|---|---|---|---|---|---|
| 15% | 809 | 193 | 27 | 3,3% | 13 | 13 de 18 | 68 de 716 |
| 20% | 332 | 133 | 8 | 2,4% | 8 | 3 de 5 | 24 de 310 |
| 30% | 46 | 36 | 0 | 0,0% | 0 | 0 de 0 | 9 de 45 |

| Ano (gatilho 20%) | Sinais | Sinais bloqueados | Fundos bloqueados | Sinais com volume ≥ R$ 500 mil | ... dos quais bloqueados |
|---|---|---|---|---|---|
| 2018 | 11 | 0 | 0 | 6 | 0 |
| 2019 | 4 | 0 | 0 | 2 | 0 |
| 2020 | 107 | 0 | 0 | 48 | 0 |
| 2021 | 54 | 0 | 0 | 17 | 0 |
| 2022 | 15 | 0 | 0 | 2 | 0 |
| 2023 | 12 | 0 | 0 | 3 | 0 |
| 2024 | 64 | 4 | 4 | 34 | 2 |
| 2025 | 46 | 0 | 0 | 18 | 0 |
| 2026 | 19 | 4 | 4 | 6 | 2 |

**Legenda.** *Sinais* = dias de sinal com os mesmos filtros de universo (sem o filtro de volume, sem caixa limitado). *Sinais bloqueados* = os que a regra 1 descartaria. *Fundos bloqueados* = fundos distintos. *Preços acabam em até 252 pregões* = "X de Y": dos sinais cujo desfecho dá para saber (o fundo ainda tinha 252 pregões pela frente ou parou de ter preço), quantos viraram fundo sem preço depois. Esse desfecho só serve para avaliar a regra; ela mesma usa apenas fatos até o dia do sinal.

**Leitura prática.** A regra bloqueia pouco: 3,3% dos sinais de 15% e 2,4% dos de 20%. Entre os sinais bloqueados de 15%, 13 de 18 acabaram sem preço em até 252 pregões, contra 68 de 716 entre os não bloqueados: o bloqueio pega uma parte relevante das saídas, mas não todas.

**Leitura dos 16 bloqueios de 2018 a 2025 (todos, pares fundo × dia do sinal):**

| Fundo | Sinal | Gatilho(s) | Fato (data) | Expressão | Leitura | Observação |
|---|---|---|---|---|---|---|
| SAAG11 | 15/04/2020 | 15% | 15/04/2020 | incorporação do fundo | acerto: os preços do fundo acabam depois | Cotistas aprovam a incorporação do fundo pelo RBVA. |
| ABCP11 | 26/11/2021 | 15% | 19/02/2021 | cisão do fundo | falso: o fundo continuou negociando (preços até 09/11/2026) | Cisão do fundo (parcial); o fundo segue negociando. |
| ABCP11 | 01/12/2021 | 15% | 19/02/2021 | cisão do fundo | falso: o fundo continuou negociando (preços até 09/11/2026) | Idem. |
| BRCR11 | 01/10/2024 | 15% | 12/04/2024 | liquidação do fundo | falso: o fundo continuou negociando (preços até 09/11/2026) | Texto fala de saldo da 'liquidação do Fundo' por amortização de caixa e entrega de cotas do CENESP; mesmo assim o BRCR11 segue com preços até 09/11/2026 (operação parcial ou código reaproveitado: não dá para saber pela base). |
| VRTM11 | 01/10/2024 | 20% | 02/04/2024 | venda da totalidade dos ativos | falso: o fundo continuou negociando (preços até 09/11/2026) | O VRTM seria o comprador da totalidade dos ativos (de outro fundo); o VRTM11 segue negociando. |
| RBED11 | 04/11/2024 | 15% | 14/10/2024 | venda da totalidade dos ativos | acerto: os preços do fundo acabam depois | Venda de 100% dos ativos do fundo ao RBVA11. |
| RBED11 | 11/11/2024 | 20% | 14/10/2024 | venda da totalidade dos ativos | acerto: os preços do fundo acabam depois | Idem. |
| BRCR11 | 28/11/2024 | 15% | 12/04/2024 | liquidação do fundo | falso: o fundo continuou negociando (preços até 09/11/2026) | Idem BRCR11 de 01/10/2024. |
| RVBI11 | 04/12/2024 | 15% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Texto sobre leilão de frações e liquidação dos fundos BLMR, BLMC, MORC e MORE, não sobre o próprio RVBI11 (cujos preços acabam em 30/10/2025). |
| BRCR11 | 09/12/2024 | 20% | 12/04/2024 | liquidação do fundo | falso: o fundo continuou negociando (preços até 09/11/2026) | Idem BRCR11 de 01/10/2024. |
| RVBI11 | 16/12/2024 | 20% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Idem. |
| RVBI11 | 08/01/2025 | 15% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Idem. |
| RVBI11 | 10/01/2025 | 15% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Idem. |
| RVBI11 | 17/01/2025 | 15% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Idem. |
| RVBI11 | 07/02/2025 | 15% | 05/07/2024 | liquidação do fundo | trecho fala de outros fundos (os preços do fundo acabam depois, por outro motivo) | Idem. |
| VRTM11 | 17/03/2025 | 15% | 02/04/2024 | venda da totalidade dos ativos | falso: o fundo continuou negociando (preços até 09/11/2026) | Idem VRTM11 de 01/10/2024. |

**Legenda.** *Leitura* = minha leitura do trecho (230 caracteres de cada lado, completo na aba "Fundos bloqueados") e do que aconteceu com os preços do fundo.

**Leitura prática.** De 16 bloqueios, só 3 eram saídas reais confirmadas; 7 eram falsos (o fundo continuou negociando: cisão parcial, fundo que seria o comprador de outro, pagamento de saldo) e 6 vinham de texto sobre outros fundos, embora o fundo tenha saído depois por outro motivo. Ou seja, a regra de palavras erra bastante nos anos antigos, mas também bloqueia poucos sinais.

### Tabela 9. O que aconteceu com cada sinal (ordem de R$ 1.000)

| Sub-carteira (ordem R$ 1.000) | bloqueado: pode sair da bolsa | comprado | comprado (reduzido pelo caixa) | fundo já em carteira | sem dinheiro | volume abaixo de R$ 500 mil | Total de sinais |
|---|---|---|---|---|---|---|---|
| Agressiva | 15 | 19 | 2 | 21 | 22 | 0 | 79 |
| Conservadora | 4 | 3 | 0 | 1 | 0 | 11 | 19 |
| Conservadora 30% | 0 | 1 | 0 | 0 | 0 | 2 | 3 |

**Legenda.** *Comprado* = ordem executada com o valor pretendido. *Reduzido pelo caixa* = comprou menos que o pretendido, mas pelo menos R$ 200. *Fundo já em carteira* = o mesmo fundo já estava na sub-carteira. *Sem dinheiro* = faltou caixa. *Sem negociação na abertura* = o fundo não negociou no dia da entrada. *Bloqueado: pode sair da bolsa* = regra 1. *Volume abaixo de R$ 500 mil* = regra 2.

**Leitura prática.** A agressiva ficou sem dinheiro em 22 sinais, o primeiro em 14/08/2026. A conservadora recebeu 19 sinais: 11 foram barrados pelo volume, 4 pela regra 1 e 3 viraram compra; não faltou dinheiro para nenhum.

### Conferências feitas pelo programa

Todas passaram (asserts dentro do programa; veja a saída impressa):

- O caixa nunca ficou negativo em nenhum dia, nas 9 simulações da versão 2 (menor caixa: R$ 2,32).
- Nenhuma compra no dia do sinal (84 compras, todas depois) e nenhum sinal anterior a 02/01/2026.
- Nenhum fato posterior ao dia do sinal entra na regra 1 (assert dentro de `bloqueio`); todo bloqueio de 2026 tem fato entre 0 e 365 dias antes do sinal.
- A versão 1 rodada de novo no mesmo programa bate com o documento antigo (R$ 10.170,81; R$ 10.426,20; R$ 20.597,01; variante de 30%: R$ 10.246,71; 5 ordens que saíram da bolsa, R$ 4.206,64 comprados e R$ -783,48 de resultado).
- O valor atual das posições abertas, somado, é igual ao valor das cotas no patrimônio de 09/11 de cada sub-carteira.
- O imposto do FII refeito por fora (mês a mês, com prejuízo abatendo) bate com o do programa; devido = pago + pendente + a vencer.
- R$ 20.000 em 105% do CDI refeitos à mão: R$ 22.007,15 líquido (IR de 20%, 311 dias).
- Conservadora, VGHF11 (sinal 18/05/2026, entrada 19/05/2026, em aberto em 09/11/2026): compra 173 cotas × R$ 5,75 = R$ 994,75; rendimentos R$ 64,01; valor atual R$ 690,27; taxas R$ 0,30; resultado R$ -240,77 (-24,2%). O programa deu o mesmo valor.
- Agressiva, FIIP11 (sinal 13/03/2026, entrada 16/03/2026, saída 07/10/2026): compra 7 cotas × R$ 132,88 = R$ 930,16; rendimentos R$ 69,30; venda R$ 960,77; taxas R$ 0,57; resultado R$ 99,35 (10,7%). O programa deu o mesmo valor.
- Resgate do caixa (Agressiva), só IR: compra em 09/03/2026; lote de 02/01/2026 (66 dias corridos); parte resgatada R$ 825,94; rendimento bruto R$ 20,81; IOF R$ 0,00; IR de 22,5% = R$ 4,68; líquido R$ 842,07. O programa deu o mesmo valor.
- Resgate do caixa (Agressiva), IOF + IR: compra em 05/08/2026; lote de 07/07/2026 (29 dias corridos); parte resgatada R$ 524,06; rendimento bruto R$ 5,81; IOF R$ 0,17; IR de 22,5% = R$ 1,27; líquido R$ 528,43. O programa deu o mesmo valor.

### O que foi confirmado por execução e o que é interpretação

**Confirmado por execução (rodou e conferiu):** todos os números das tabelas; o caixa nunca negativo; entrada sempre depois do sinal; nenhum fato futuro na regra 1; HCHG11, XPIN11 e ITIP11 bloqueados nas datas em que a versão 1 os comprou; a versão 1 recalculada igual à do documento antigo; compra, rendimento, valor, taxa e resultado de uma operação de cada sub-carteira refeitos a partir dos arquivos de entrada; um resgate do caixa com IR (e outro com IOF + IR) refeitos com `cdi.csv`; imposto do FII refeito por fora; valor das posições abertas igual ao do patrimônio.

**Interpretação (decisão minha, onde o pedido não dizia):**
- "Um fundo por vez" foi lido como: o mesmo fundo não pode ser comprado duas vezes ao mesmo tempo na mesma sub-carteira (como em `kairi_carteira.py`). Cada sub-carteira pode ter vários fundos diferentes.
- Compras na abertura resgatam o caixa com o índice do CDI do pregão anterior (o dia de hoje ainda não rendeu); os dias corridos para IR/IOF contam até a data do resgate. A venda de um fundo vira um lote novo no mesmo dia.
- Direito ao rendimento: data-base entre a entrada e a saída (inclusive a data de saída só quando a saída é no fechamento, no prazo ou posição aberta), como em `kairi_ordens.py`.
- Pagamento em fim de semana ou feriado entra no pregão seguinte. Avisos sem data de pagamento não entram (nada foi estimado).
- Para o retorno e a comparação, usei o patrimônio líquido do imposto do FII que seria devido ao vender tudo (o CDI também está líquido). O patrimônio diário não desconta imposto ainda não vencido.
- Resultado de cada operação (Tabelas 1 e 4) = valorização + rendimentos declarados (inclusive os ainda a receber) − taxas, antes do imposto. Na Tabela 5 (posições abertas), por pedido, só contam os rendimentos já pagos.
- Regra 1: "dia do fato" é a data de divulgação (`data_anuncio`); um fato divulgado no próprio dia do sinal, mesmo à noite, conta (a entrada é na abertura do dia seguinte). A janela é de 365 dias corridos para trás, inclusive o dia do sinal. A regra olha o texto dos fatos do próprio fundo (coluna `fundo`), não os que citam o fundo.
- Regra 1: um fato de reprovação ou cancelamento anula os fatos de saída anteriores a ele (ajuste meu, feito ao ler o caso de ITIT11); sem isso, ITIT11 continuaria bloqueado em outubro e novembro mesmo depois de a saída ter sido reprovada.
- Regra 2: o volume é o `volume_medio_60 (R$)` da linha do dia do sinal (média até aquele dia, sem olhar o futuro). O mesmo número já limitava a ordem a 2% do volume.
- A leitura manual dos bloqueios (verdadeiro / proposta / falso) é minha, feita depois de ver o texto e os fatos posteriores; não é dado da base.

### Lacunas

| Dado ou regra | Situação | Efeito no resultado |
|---|---|---|
| Fundos cujos preços acabam depois da compra (MCEM11) | Em 1 ordem(ns) da versão 2 o fundo parou de ter preço antes de 09/11 (as últimas linhas têm 'negociou = 0'). O cálculo mantém o último preço registrado, mas a operação está marcada 'saiu da bolsa — valor real desconhecido'. Não há dado do que realmente aconteceu (liquidação, incorporação, suspensão). | Comprado nessas ordens: R$ 818,72; resultado simulado: R$ -387,58. O resultado real pode ser pior ou melhor. |
| Regra 1 (fatos de saída da bolsa) | Só os primeiros 3.000 caracteres de cada fato estão na base (7962 fatos); uma saída anunciada só mais adiante no texto, ou escrita com outras palavras, passa. Fato que fala de outro fundo (comprador dos ativos, fundo incorporador) também bloqueia por engano. | Medido: 7 falsos e 6 de texto sobre outros fundos nos 16 bloqueios de 2018 a 2025; nenhum erro de leitura nos 18 de 2026. Saídas que passaram: não medido. |
| Amortizações (devolução de capital) | 0 eventos nas posições de 2026; não são creditadas no caixa se existirem. | Hoje: R$ 0,00. |
| Rendimentos sem data de pagamento | 5 avisos de 2026 (todos os fundos) sem data de pagamento; nas posições simuladas, R$ 0,00. Não foi estimada data. | Esse dinheiro não entra no caixa. |
| Rendimentos que vão ser pagos depois de 09/11 | R$ 71,30 já declarados nas posições (conservadora + agressiva). | Não entram no patrimônio de 09/11 (entrariam nos dias seguintes) nem no resultado da tabela de posições abertas. |
| Compra na abertura e venda pelo preço da média | Ninguém garante esses preços em fundo pouco negociado; o limite de 2% do negociado médio reduz, mas não elimina, o problema. | Resultado otimista, não medido. |
| Dinheiro da venda usado na mesma abertura | O motor usa o dinheiro de uma venda do dia para comprar na abertura do mesmo dia. | Pequeno ganho de tempo a favor da carteira; não medido. |
| Preço de 09/11 de fundos sem negociação no dia | 1 posições abertas (conservadora + agressiva) não tiveram negociação em 09/11; usa-se o último fechamento (veja a data do último preço na tabela de posições abertas). | Valor das posições pode estar defasado. |
| Outros custos | Só a taxa de 0,03% por compra e por venda. Não há corretagem, custódia nem diferença entre preço de compra e de venda. | Resultado real um pouco menor. |
| Prejuízo de anos anteriores | A carteira nasce vazia em 02/01/2026; não há prejuízo acumulado de 2025 para abater. | Nenhum. |
| Mercado (índice do fundo do meio) | Índice sem custos nem imposto, calculado a partir do fechamento de 02/01/2026. | Comparação apenas de referência. |
| Sinais de 20% e de 15% repetem | Um fundo que cai 20% abaixo da média antes passou pelos 15%, então os mesmos fundos podem aparecer nas duas sub-carteiras (2 fundos em comum: RBRX11, VGHF11); 0 compras são idênticas (mesmo fundo e mesmo dia). | As duas sub-carteiras não são apostas independentes; a mesma perda conta duas vezes no total. |

### Avisos

- **2026 não é um teste novo.** O período de conferência (2023 a 2026) já foi visto em estudos anteriores; esta simulação usa dados que já entraram nas escolhas.
- **As regras novas foram escolhidas depois de ver 2026.** O volume mínimo e o bloqueio por fato melhoram o número de 2026 por construção; não é um teste fora da amostra.
- **Um ano só não prova nada.** São 213 pregões e 24 compras no total; a conservadora fez 3 e nenhuma fechou. Dois ou três fundos explicam quase toda a diferença para o CDI.
- **Compras na abertura e vendas pelo preço da média são otimistas** em fundo pouco negociado.
- **A regra 1 é uma busca por palavras**: pode bloquear fundo que não sai (cisão parcial, fundo comprador) e deixar passar saída escrita de outro jeito. Medimos isso acima, mas só com leitura manual.

## Versão 1 (regras antigas)

Resumo da simulação anterior, feita sem as regras novas e rodada de novo no mesmo programa (os números abaixo são os do documento antigo, conferidos por assert). Regras: conservadora com gatilho de 20% e agressiva de 15%, sem filtro de volume e sem bloqueio por fato relevante; variante de 30%; ordem de R$ 1.000 (testes com R$ 500 e R$ 2.000). Demais regras (caixa em 105% do CDI, imposto, taxas, prioridade por volume) iguais às da versão 2.

De 02/01/2026 a 09/11/2026, o total foi para R$ 20.597,01 (3,0%; 2,7% líquido), contra R$ 22.007,15 (10,0%) do 105% do CDI. Perdeu do CDI nas duas sub-carteiras. A versão 1 comprou 5 vezes fundos que saíram da bolsa antes de 09/11 (HCHG11, ITIP11, MCEM11, XPIN11; R$ 4.206,64 comprados, resultado simulado de R$ -783,48), o que motivou a regra 1.

| Indicador (versão 1) | Conservadora (20%) | Agressiva (15%) | Total (R$ 20 mil) |
|---|---|---|---|
| Patrimônio final (cotas a preço de 09/11) | R$ 10.170,81 | R$ 10.426,20 | R$ 20.597,01 |
| Retorno no período | 1,7% | 4,3% | 3,0% |
| Patrimônio final líquido do imposto | R$ 10.170,81 | R$ 10.365,26 | R$ 20.536,07 |
| Retorno líquido | 1,7% | 3,7% | 2,7% |
| Retorno líquido contra o CDI (pontos) | -8,3 | -6,4 | -7,4 |
| Maior queda no caminho | -10,1% | -12,7% | -11,2% |
| Operações abertas / fechadas | 11 / 2 | 12 / 12 | 23 / 14 |
| Fechadas com lucro | 50,0% | 83,3% | 78,6% |
| Pior operação | -47,3% MCEM11 | -47,3% MCEM11 | -47,3% MCEM11 |
| Melhor operação | 51,3% RBRS11 | 21,0% RBRP11 | 51,3% RBRS11 |
| Rendimentos recebidos | R$ 157,36 | R$ 421,01 | R$ 578,37 |
| Imposto do FII pago / devido e não pago | R$ 60,93 / R$ 0,00 | R$ 22,55 / R$ 102,67 | R$ 83,48 / R$ 102,67 |
| Sinais sem dinheiro | 0 | 29 | 29 |

**Legenda.** Mesmas definições da Tabela 1 da versão 2. Todos os valores são da ordem de R$ 1.000.

| Sub-carteira | Gatilho | Ordem | Patrimônio final líquido | Retorno líquido | Maior queda | Operações |
|---|---|---|---|---|---|---|
| Conservadora | 20% | R$ 500 | R$ 10.643,44 | 6,4% | -4,8% | 13 |
| Conservadora | 20% | R$ 1.000 | R$ 10.170,81 | 1,7% | -10,1% | 13 |
| Conservadora | 20% | R$ 2.000 | R$ 9.327,87 | -6,7% | -19,7% | 9 |
| Agressiva | 15% | R$ 500 | R$ 10.818,64 | 8,2% | -8,5% | 39 |
| Agressiva | 15% | R$ 1.000 | R$ 10.365,26 | 3,7% | -12,7% | 24 |
| Agressiva | 15% | R$ 2.000 | R$ 9.775,70 | -2,2% | -13,9% | 14 |
| Conservadora 30% | 30% | R$ 500 | R$ 10.625,14 | 6,3% | -1,6% | 2 |
| Conservadora 30% | 30% | R$ 1.000 | R$ 10.246,71 | 2,5% | -3,8% | 2 |
| Conservadora 30% | 30% | R$ 2.000 | R$ 9.948,80 | -0,5% | -4,8% | 2 |

**Legenda.** Variantes da versão 1: cada linha parte de R$ 10.000; *retorno líquido* = patrimônio final líquido do imposto ÷ R$ 10.000 − 1.

**Leitura prática.** Na versão 1 todas as variantes ficaram abaixo do 105% do CDI (10,0%), e quanto maior a ordem, pior o resultado. As perdas de fundos que saíram da bolsa, principalmente MCEM11, pesaram nas duas sub-carteiras.


## Queda geral de 26/10/2026 (conferência feita depois da simulação)

Nas planilhas de preços, 153 dos 221 fundos que negociaram em 26/10/2026 caíram mais de 3% no dia. Só 1 subiu mais de 3%, e a variação do fundo do meio foi −5,0%. A queda continuou até 03/11/2026 (o fundo do meio caiu −2,4% nesse dia). Exemplos: HGLG11 foi de R$ 159,66 a R$ 144,62 e MXRF11 de R$ 9,44 a R$ 8,47.

| Data | Fundos que negociaram | Variação do fundo do meio | Caíram mais de 3% | Subiram mais de 3% |
|---|---|---|---|---|
| 23/10/2026 | 218 | +0,1% | 7 | 12 |
| 26/10/2026 | 221 | −5,0% | 153 | 1 |
| 28/10/2026 | 228 | −1,4% | 42 | 7 |
| 03/11/2026 | 220 | −2,4% | 92 | 10 |

Leitura prática: até 22/10/2026 a carteira total estava em R$ 22.771 (+13,9%), à frente do CDI. A queda geral do fim de outubro levou o resultado para baixo do CDI. **Não conferi essa queda em outra fonte.** Se for erro de dado, o resultado muda.

Nota da versão 2: o valor de R$ 22.771 (+13,9%) acima é o pico da carteira total da versão 1. Na versão 2 o pico do total foi R$ 22.452,93 em 22/10/2026 e a queda de 22/10/2026 a 03/11/2026 foi de -8,1%.
