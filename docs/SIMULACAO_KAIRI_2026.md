# Simulação do Kairi em 2026, versão 3 (17/11/2026)

Programa: `estudos/kairi_carteira_2026.py`; planilha: `planilhas/kairi_carteira_2026.xlsx`; documentos do FNET: `planilhas/tecnico/fnet_2026_documentos.csv.gz`.

**Regras.** Quatro sub-carteiras de R$ 10.000 cada (o dono escreveu "100 mil" para a Agressiva 2; tratamos como R$ 10 mil, igual às outras), de 02/01/2026 a 09/11/2026, ordem de R$ 1.000.
Gatilho: a cota fecha 15% (Agressivas) ou 20% (Conservadoras) abaixo da média de 200 pregões, com rendimento mantido. Filtro de negociação: **mediana** do volume diário dos 60 pregões até o dia do sinal, inclusive: Agressiva 1 de R$ 100 a 200 mil; Agressiva 2 de R$ 200 a 500 mil; Conservadora 1 de R$ 500 mil a 1 milhão; Conservadora 2 acima de R$ 1 milhão.
Venda no **fechamento** do dia em que o fechamento fica igual ou acima da média de 200 pregões (média até o dia anterior), ou no prazo de 252 pregões. Um fundo por vez em cada sub-carteira; maior mediana de volume primeiro.
**Avisos do FNET:** comunicado de "não haverá distribuição de rendimentos" nos 126 pregões até o sinal corta o rendimento (sem compra); edital, carta consulta, ata, fato ou comunicado sobre liquidação, incorporação, fusão, cisão, venda de todos os ativos ou tombamento para o balcão bloqueia a entrada (regra 1, com os fatos relevantes) e, com a posição aberta, manda vender na abertura do pregão seguinte; comunicado de rendimento zero com posição aberta também.
Caixa parado em 105% do CDI com IR/IOF por lote; imposto do FII (20% sobre o ganho do mês, DARF no mês seguinte); taxa de 0,03% na compra e na venda.

### Tabela 1. Resumo

| Indicador | Agressiva 1 (15%; mediana R$ 100–200 mil) | Agressiva 2 (15%; R$ 200–500 mil) | Conservadora 1 (20%; R$ 500 mil–1 mi) | Conservadora 2 (20%; > R$ 1 mi) | Total (R$ 40 mil) | 105% do CDI (R$ 40 mil) | Mercado (R$ 40 mil) |
|---|---|---|---|---|---|---|---|
| Patrimônio inicial (R$) | R$ 10.000,00 | R$ 10.000,00 | R$ 10.000,00 | R$ 10.000,00 | R$ 40.000,00 | R$ 40.000,00 | R$ 40.000,00 |
| Patrimônio final, cotas a preço de 09/11 (R$) | R$ 11.137,10 | R$ 10.981,15 | R$ 11.003,58 | R$ 10.378,79 | R$ 43.500,62 | R$ 44.014,31 | R$ 38.792,37 |
| Retorno líquido (após imposto a vencer) | 11,1% | 9,7% | 10,0% | 3,8% | 8,7% | 10,0% | -3,0% |
| Contra o CDI (pontos percentuais do retorno líquido) | 1,1 | -0,3 | 0,0 | -6,2 | -1,4 | 0,0 | -13,1 |
| Maior queda do patrimônio no caminho | -2,3% | -2,5% | 0,0% | -5,7% | -2,5% | 0,0% | -10,5% |
|   ... do pico em | 22/10/2026 | 22/10/2026 | — | 23/10/2026 | 22/10/2026 | — | 23/10/2026 |
|   ... até o ponto mais baixo em | 03/11/2026 | 03/11/2026 | — | 09/11/2026 | 03/11/2026 | — | 03/11/2026 |
| Operações abertas / fechadas | 4 / 1 | 7 / 1 | 0 / 0 | 3 / 0 | 14 / 2 | — | — |
| Fechadas com lucro | 1 de 1 (100%) | 1 de 1 (100%) | nenhuma fechada | nenhuma fechada | 2 de 2 (100%) | — | — |
| Rendimentos recebidos no caixa (R$) | R$ 77,42 | R$ 97,80 | R$ 0,00 | R$ 64,01 | R$ 239,23 | — | — |
| Imposto do FII pago + vencido e não pago (R$) | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | — | — |
| Dinheiro parado no CDI: % médio do patrimônio | 91,6% | 89,7% | 100,0% | 94,1% | 93,8% | 100,0% | — |
| Dinheiro parado no CDI: dias-equivalentes parado (de 311 dias corridos) | 284,7 | 279,0 | 311,0 | 292,6 | 291,8 | 311,0 | — |
| Dinheiro parado no CDI: quanto rendeu, líquido de IR/IOF (R$) | R$ 919,00 | R$ 896,94 | R$ 1.003,58 | R$ 939,70 | R$ 3.759,21 | R$ 4.014,31 | — |
| De onde veio: operações fechadas, valorização + rendimentos (R$) | R$ 161,60 | R$ 109,41 | R$ 0,00 | R$ 0,00 | R$ 271,01 | — | — |
| De onde veio: operações abertas a preço de 09/11, valorização + rendimentos pagos (R$) | R$ 58,30 | R$ -22,60 | R$ 0,00 | R$ -560,02 | R$ -524,32 | — | — |
| De onde veio: rendimento do dinheiro parado (R$) | R$ 919,00 | R$ 896,94 | R$ 1.003,58 | R$ 939,70 | R$ 3.759,21 | R$ 4.014,31 | — |
| De onde veio: − imposto do FII (R$) | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | R$ 0,00 | — | — |
| De onde veio: − taxas de compra e venda (R$) | R$ -1,80 | R$ -2,60 | R$ 0,00 | R$ -0,88 | R$ -5,28 | — | — |
| = Ganho total (patrimônio final − capital) (R$) | R$ 1.137,10 | R$ 981,15 | R$ 1.003,58 | R$ 378,79 | R$ 3.500,62 | R$ 4.014,31 | R$ -1.207,63 |

**Legenda.** *Retorno líquido* = (patrimônio final − imposto do FII a vencer − imposto que seria devido se vendesse tudo) ÷ capital − 1. *Contra o CDI* = retorno líquido menos o do 105% do CDI, em pontos percentuais. *Maior queda* = maior distância, em %, de um pico do patrimônio ao ponto mais baixo seguinte. *Fechadas com lucro* = resultado (venda − compra + rendimentos − taxas) maior que zero. *Dinheiro parado* = caixa sem fundo, no 105% do CDI: % médio = média diária de caixa ÷ patrimônio; dias-equivalentes = esse % × 311 dias corridos; rendeu = rendimento líquido de IR/IOF (resgatado + ainda aplicado em 09/11). *De onde veio* (R$) = fechadas (valorização + rendimentos recebidos) + abertas a preço de 09/11 (valorização + rendimentos pagos) + dinheiro parado − imposto do FII pago ou vencido − taxas = patrimônio final − capital (conferido por assert no programa).

**Leitura prática.** Os R$ 40 mil terminaram em R$ 43.500,62 (retorno líquido 8,7%), 1,4 ponto(s) abaixo do CDI (10,0%). O dinheiro ficou parado em média 94% do tempo e rendeu R$ 3.759,21, 107% do ganho total de R$ 3.500,62; as operações (fechadas e abertas, já com taxas e imposto) contribuíram com R$ -258,59. Melhor sub-carteira: Agressiva 1 (11,1%); pior: Conservadora 2 (3,8%).

### Tabela 2. Operações fechadas

| Sub-carteira | Fundo | Entrada | Saída | Valor de entrada | Valor de saída | Motivo | Dias | Maior queda (menor fechamento) | Maior alta (maior fechamento) | Rendimentos | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Agressiva 1 | FIIP11 | 28/08/2026 a R$ 121,25 | 09/10/2026 a R$ 138,61 | R$ 970,00 | R$ 1.108,88 | volta à média | 42 | -0,1% (02/09/2026) | 14,3% (09/10/2026) | R$ 22,72 | R$ 160,98 (16,6%) |
| Agressiva 2 | FIIP11 | 16/03/2026 a R$ 132,88 | 09/10/2026 a R$ 138,61 | R$ 930,16 | R$ 970,27 | volta à média | 207 | -8,9% (02/09/2026) | 8,9% (09/04/2026) | R$ 69,30 | R$ 108,84 (11,7%) |

**Legenda.** Valores em R$. *Maior queda* e *maior alta* = menor e maior fechamento da operação em % do preço de entrada, com a data (0% e sem data se o fundo nunca passou do preço de entrada). *Resultado* = valor de saída − valor de entrada + rendimentos recebidos − taxas (% do valor de entrada).

**Leitura prática.** 2 operações fechadas (2 com lucro), resultado somado de R$ 269,82; duração média de 124 dias. As saídas pelo fechamento acontecem no dia em que o preço volta à média, então o preço de saída é o fechamento daquele dia.

### Tabela 3. Posições abertas em 09/11/2026

| Sub-carteira | Fundo | Entrada | Cotas | Valor de entrada | Último preço | Valor atual | Rendimentos pagos | A receber | Resultado | +/− | Maior queda até agora | Maior alta até agora |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agressiva 1 | VCRR11 | 05/08/2026 a R$ 53,48 | 18 | R$ 962,64 | R$ 52,49 (09/11/2026) | R$ 944,82 | R$ 15,84 | R$ 7,20 | R$ -2,27 (-0,2%) | negativo | -4,6% (04/11/2026) | 8,9% (22/10/2026) |
| Agressiva 1 | TRXY11 | 14/08/2026 a R$ 7,49 | 133 | R$ 996,17 | R$ 7,47 (09/11/2026) | R$ 993,51 | R$ 29,26 | R$ 14,63 | R$ 26,30 (2,6%) | positivo | -2,3% (18/08/2026) | 3,2% (21/08/2026) |
| Agressiva 1 | INLG11 | 11/09/2026 a R$ 60,28 | 16 | R$ 964,48 | R$ 59,20 (09/11/2026) | R$ 947,20 | R$ 9,60 | R$ 9,60 | R$ -7,97 (-0,8%) | negativo | -4,5% (03/11/2026) | 8,8% (13/10/2026) |
| Agressiva 1 | VGRI11 | 04/11/2026 a R$ 5,30 | 188 | R$ 996,40 | R$ 5,52 (09/11/2026) | R$ 1.037,76 | R$ 0,00 | R$ 0,00 | R$ 41,06 (4,1%) | positivo | 0,0% | 4,2% (06/11/2026) |
| Agressiva 2 | RBHY11 | 06/08/2026 a R$ 63,15 | 15 | R$ 947,25 | R$ 55,05 (09/11/2026) | R$ 825,75 | R$ 28,50 | R$ 13,50 | R$ -93,28 (-9,8%) | negativo | -15,7% (04/11/2026) | 3,8% (07/08/2026) |
| Agressiva 2 | BCRI11 | 05/10/2026 a R$ 53,04 | 18 | R$ 954,72 | R$ 48,70 (09/11/2026) | R$ 876,60 | R$ 0,00 | R$ 12,60 | R$ -78,41 (-8,2%) | negativo | -9,7% (04/11/2026) | 11,0% (07/10/2026) |
| Agressiva 2 | KIVO11 | 04/11/2026 a R$ 50,02 | 19 | R$ 950,38 | R$ 49,51 (09/11/2026) | R$ 940,69 | R$ 0,00 | R$ 0,00 | R$ -9,98 (-1,0%) | negativo | -1,0% (09/11/2026) | 0,4% (06/11/2026) |
| Agressiva 2 | RBRL11 | 04/11/2026 a R$ 67,65 | 14 | R$ 947,10 | R$ 69,65 (09/11/2026) | R$ 975,10 | R$ 0,00 | R$ 0,00 | R$ 27,72 (2,9%) | positivo | -0,8% (05/11/2026) | 3,2% (06/11/2026) |
| Agressiva 2 | RECT11 | 04/11/2026 a R$ 30,51 | 32 | R$ 976,32 | R$ 32,32 (09/11/2026) | R$ 1.034,24 | R$ 0,00 | R$ 0,00 | R$ 57,63 (5,9%) | positivo | 0,0% | 8,0% (06/11/2026) |
| Agressiva 2 | VINO11 | 04/11/2026 a R$ 3,85 | 259 | R$ 997,15 | R$ 4,03 (09/11/2026) | R$ 1.043,77 | R$ 0,00 | R$ 0,00 | R$ 46,32 (4,6%) | positivo | 0,0% | 4,7% (09/11/2026) |
| Agressiva 2 | LIFE11 | 05/11/2026 a R$ 6,59 | 151 | R$ 995,09 | R$ 6,76 (09/11/2026) | R$ 1.020,76 | R$ 0,00 | R$ 0,00 | R$ 25,37 (2,5%) | positivo | -0,6% (05/11/2026) | 2,6% (09/11/2026) |
| Conservadora 2 | VGHF11 | 19/05/2026 a R$ 5,75 | 173 | R$ 994,75 | R$ 3,99 (09/11/2026) | R$ 690,27 | R$ 64,01 | R$ 0,00 | R$ -240,77 (-24,2%) | negativo | -30,6% (09/11/2026) | 8,7% (28/05/2026) |
| Conservadora 2 | TGAR11 | 14/10/2026 a R$ 50,04 | 19 | R$ 950,76 | R$ 32,05 (09/11/2026) | R$ 608,95 | R$ 0,00 | R$ 8,74 | R$ -342,10 (-36,0%) | negativo | -36,0% (05/11/2026) | 3,8% (22/10/2026) |
| Conservadora 2 | RBRX11 | 04/11/2026 a R$ 6,26 | 159 | R$ 995,34 | R$ 6,40 (09/11/2026) | R$ 1.017,60 | R$ 0,00 | R$ 0,00 | R$ 21,96 (2,2%) | positivo | 0,0% | 4,2% (06/11/2026) |

**Legenda.** Valor atual = cotas × último fechamento. *Rendimentos pagos* já entraram no caixa; *a receber* foram declarados e não entram no resultado. *Resultado* = valor atual − valor de entrada + rendimentos pagos − taxa de compra.

**Leitura prática.** 14 posições abertas somam resultado de R$ -528,41 (7 positivas e 7 negativas); as piores são TGAR11 (-36,0%), VGHF11 (-24,2%), RBHY11 (-9,8%). Muitas entraram em 03-05/11/2026, na queda geral do fim de outubro, e ainda não tiveram tempo de voltar à média.

### Tabela 4. Saídas antecipadas e sinais barrados por documento do FNET

| Tipo | Sub-carteira(s) | Fundo | Documento do FNET (data de entrega) | Expressão | Efeito | Trecho |
|---|---|---|---|---|---|---|
| Sinal barrado (regra 1) | Agressiva 2 | RBHG11 | 18/06/2026 (id 1223810) | venda da totalidade dos ativos | 2 sinal(is): 13/08/2026, 17/08/2026 | “…ndições precedentes (“Proposta de Aquisição Inicial”), para (1) aquisição dos ativos indicados no Anexo I à Proposta de Aquisição, os quais……” |
| Sinal barrado (regra 1) | Agressiva 2 | OUJP11 | 05/10/2026 (id 1340487) | liquidação do fundo | 1 sinal(is): 28/10/2026 | “…os documentos referentes a esta AGE, no Regulamento ou nos documentos da operação; (xiii) A dissolução, com consequente liquidação do Fundo, na forma……” |
| Sinal barrado (regra 1) | Conservadora 2 | RBRR11 | 28/10/2026 (id 1360898) | liquidação do fundo | 1 sinal(is): 03/11/2026 | “…do de apuração do custo médio de aquisição das cotas pela 01/12/2026 a 09/12/2026 Administradora Divulgação do valor de liquidação do Fundo e parcela……” |

**Legenda.** Só documentos do FNET (data de entrega até o dia do sinal para barrar; posterior à entrada para vender). Venda sempre na abertura do primeiro pregão depois da publicação. O trecho é o pedaço do documento onde a expressão foi achada.

**Leitura prática.** 0 saída(s) antecipada(s) e 4 sinal(is) barrado(s) por documento do FNET. MCEM11: gatilho em 11/05/2026 (mediana de volume R$ 20.732, abaixo de R$ 100 mil: nenhuma faixa compra). Mesmo sem o filtro de volume, o comunicado de 30/04/2026 (doc 1173773: “não haverá distribuição de rendimentos”) está nos 126 pregões antes do sinal, então a regra b barra a compra de 12/05/2026. Se fosse comprado, o edital de 22/05/2026 (doc 1201756, tombamento das cotas para o balcão) mandaria vender na abertura de 25/05/2026 a R$ 44,79. VVCR11: 6 sinais em 2026, mediana de volume entre R$ 5.018 e R$ 8.309 (a média de 60, inflada por negócios isolados, ia de R$ 61.009 a R$ 224.376); nenhuma faixa compra (mínimo R$ 100 mil). Barrado em todos.

### Tabela 5. Lacunas

| Dado | Situação | Efeito |
|---|---|---|
| Documentos do FNET antes de 01/05/2025 | a coleta vai de 01/05/2025 a 13/11/2026; só os 43 fundos que deram sinal em 2026 | a regra 1 olha 365 dias para trás: para sinais antes de 01/05/2026 a janela só tem os fatos relevantes da planilha (fatos_textos.csv.gz); um aviso que só existisse como comunicado/assembleia antes de 05/2025 não seria visto |
| Leitura dos documentos | 755 documentos lidos por expressões no texto completo (sem leitura humana de todos); 12 sem texto legível (PDF escaneado, em geral atas: ver a coluna 'leitura' do arquivo); 41 cancelados no FNET foram ignorados | pode haver aviso de liquidação/rendimento zero escrito de forma que as expressões não pegam (não barrado/vendido), e trecho que casa sem tratar do fundo. Todos os documentos que casaram foram lidos (trechos nas tabelas) |
| Documentos publicados depois de 09/11/2026 | o FNET foi consultado até 13/11/2026, mas os preços acabam em 09/11/2026 | nenhum aviso de posição aberta cai depois do fim dos preços; posições abertas seguem a preço de 09/11/2026 |
| Rendimentos declarados e ainda não pagos | R$ 66,27 a receber e R$ 0,00 sem data de pagamento | não entram no caixa nem no resultado; se pagos, o resultado das posições abertas sobe |
| Imposto do FII ainda não vencido | R$ 35,56 a vencer depois de 09/11 e R$ 0,25 se vendesse tudo | entram só no retorno líquido, não no patrimônio final |
| Compras de fundo que saiu da bolsa | 0 compra(s) com preços que acabam antes do prazo (valor real de saída desconhecido) | se houver, o cálculo continua pelo último preço (pode estar errado para mais ou para menos) |

**Histórico.** Versão 1: total 2,7% líquido; versão 2: 3,7%; CDI 10,0%.
A versão 3 muda as regras (quatro sub-carteiras de R$ 10 mil, filtro pela mediana do volume, venda no fechamento, avisos do FNET), então não é comparável diretamente com as versões 1 e 2.
