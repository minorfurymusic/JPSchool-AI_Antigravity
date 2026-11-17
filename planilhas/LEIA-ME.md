# Planilhas dos fundos imobiliários (FIIs)

## O que são estes arquivos

Aqui estão os dados dos fundos imobiliários negociados na bolsa, organizados em planilhas para você analisar ano a ano no Excel.

- **Período dos dados:** de 02/01/2017 até 09/11/2026.
- **Como abrir:** dê dois cliques no arquivo, ou use Excel > Arquivo > Abrir. Os arquivos já estão no formato do Brasil (as colunas são separadas por ponto e vírgula, e os números usam vírgula). Se tudo aparecer em uma coluna só, use Dados > Texto para Colunas e escolha ponto e vírgula como separador.
- **Cada arquivo tem menos de 1 milhão de linhas**, então abre inteiro no Excel.

## Observações importantes

- **Preços ajustados por desdobramento.** Quando um fundo divide suas cotas em partes (por exemplo, uma cota vira duas), o preço antigo é ajustado para continuar comparável com o preço de hoje.
- **Valor patrimonial e patrimônio só aparecem 75 dias depois do mês a que se referem.** Esse é o prazo em que o fundo costuma divulgar essas informações. Antes disso, a célula fica vazia.
- **Valores grandes em reais** (negociado no dia, patrimônio) aparecem sem centavos. Preços e rendimentos por cota aparecem com centavos.

## Pontos conhecidos (conferência de 15/11/2026)

- Em `precos_2020.csv` há 5 linhas em que máxima, mínima e fechamento não combinam entre si.
- Em `rendimentos.csv` há 3 linhas repetidas.
- Em `anuncios.csv`, 1.807 dos 7.962 anúncios estão sem preço de entrada (o fundo não tinha preço naquele dia).
- Em `anuncios.csv`, 14 anúncios têm preço sobre valor patrimonial abaixo de 0,2 e 12 acima de 3. São valores suspeitos; desconfie deles.
- Nos primeiros anos faltam mais dados: em 2017, 25% das linhas de preço estão sem valor patrimonial e 33% sem rendimento.

## Arquivos

### precos_AAAA.csv (um arquivo por ano, de 2017 a 2026)

Uma linha por fundo e por dia. Se o fundo ficou alguns dias sem negociar, ainda aparece a última cotação recente, com "negociou" igual a 0.

| Coluna | O que significa |
|---|---|
| data | Dia de negociação |
| fundo | Código do fundo na bolsa |
| abertura | Preço da primeira negociação do dia (R$ por cota) |
| maxima | Preço mais alto do dia (R$ por cota) |
| minima | Preço mais baixo do dia (R$ por cota) |
| fechamento | Preço do último negócio do dia (R$ por cota) |
| negociou (1/0) | 1 se o fundo negociou naquele dia; 0 se não negociou |
| volume_dia (R$) | Dinheiro negociado no dia |
| volume_medio_60 (R$) | Média diária do dinheiro negociado nos 60 dias anteriores |
| rendimento_mensal (R$/cota) | Rendimento por cota que o fundo já tinha anunciado naquele dia |
| rendimento_ano_sobre_preco (%) | Quanto o rendimento mensal daria em 12 meses, em relação ao preço de fechamento |
| valor_patrimonial_cota | Patrimônio do fundo dividido pelo número de cotas (R$ por cota). Aparece 75 dias depois do mês de referência |
| preco_sobre_valor_patrimonial | Preço de fechamento dividido pelo valor patrimonial por cota. Abaixo de 1 significa cota vendida com desconto |
| patrimonio (R$) | Patrimônio líquido do fundo. Aparece 75 dias depois do mês de referência |
| amortizacao_12m (1/0) | 1 se, nos últimos 12 meses, o fundo devolveu aos cotistas uma parte relevante do patrimônio; 0 se não |

### mercado.csv

Uma linha por dia de negociação, com o resumo de todos os fundos.

| Coluna | O que significa |
|---|---|
| data | Dia de negociação |
| selic_ano (%) | Taxa Selic anual naquele dia |
| selic_liquida_ano (%) | Selic multiplicada por 0,825 (é o cálculo usado no estudo) |
| indice_mercado | Índice acumulado que mostra o desempenho médio dos fundos. Começa em 1 no primeiro dia |
| fundos_negociados | Quantos fundos negociaram naquele dia |
| mediana_preco_sobre_valor_patrimonial | Número do meio: metade dos fundos está acima e metade abaixo. Considera só fundos com pelo menos R$ 10 mil negociados por dia, em média, e deixa de fora valores muito fora do normal (abaixo de 0,2 ou acima de 3) |

### rendimentos.csv

Uma linha por aviso de rendimento que os fundos publicaram.

| Coluna | O que significa |
|---|---|
| fundo | Código do fundo na bolsa |
| data_conhecido | Dia em que o aviso passou a ser conhecido pelo mercado |
| data_base | Data de referência do rendimento. Quem tinha a cota nessa data tem direito ao valor |
| valor (R$/cota) | Valor do rendimento por cota |

### anuncios.csv

Uma linha por fato relevante (comunicado importante) publicado por um fundo, com o que aconteceu no preço logo depois do anúncio.

| Coluna | O que significa |
|---|---|
| id | Número de identificação do comunicado |
| fundo | Código do fundo na bolsa |
| data_anuncio | Dia e hora em que o comunicado foi publicado |
| data_entrada | Primeiro dia de negociação em que o mercado pôde reagir ao comunicado |
| tipo | Tipo de comunicado, classificado automaticamente (venda, locação, emissão, rendimento etc.) |
| sentido | Se o comunicado parece positivo (alta), negativo (queda), misto ou neutro |
| repetido (1/0) | 1 se o mesmo assunto já tinha sido comunicado antes |
| continuacao (1/0) | 1 se o comunicado é continuação de outro |
| declarou_efeito | Se o fundo disse que o rendimento vai aumentar, diminuir, ou se não disse nada sobre isso |
| efeito_percentual | Percentual de efeito declarado no comunicado, quando existe |
| valor_por_cota_citado | Valor por cota citado no comunicado (R$) |
| preco_entrada | Preço de abertura no dia de entrada (R$ por cota) |
| negociou_na_entrada (1/0) | 1 se o fundo negociou no dia de entrada |
| volume_medio_60 (R$) | Média diária do dinheiro negociado nos 60 dias anteriores |
| ordem_maxima (R$) | 2% do volume_medio_60: um valor de referência para o tamanho de uma ordem sem mexer muito no preço |
| rendimento_mensal_na_entrada (R$/cota) | Rendimento mensal por cota já conhecido no dia de entrada |
| rendimento_ano_sobre_preco (%) | Quanto o rendimento mensal daria em 12 meses, em relação ao preço de abertura da entrada |
| selic_ano (%) | Taxa Selic anual no dia de entrada |
| regua_selic_liquida_mais_3 (%) | Selic líquida (Selic x 0,825) mais 3 pontos percentuais: uma referência de rendimento |
| valor_patrimonial_cota | Valor patrimonial por cota no dia de entrada (R$) |
| preco_sobre_valor_patrimonial | Preço de abertura da entrada dividido pelo valor patrimonial por cota |
| patrimonio (R$) | Patrimônio líquido do fundo no dia de entrada |
| frase_do_efeito | Trecho do comunicado que diz qual é o efeito |
| inicio_do_texto | Começo do texto do comunicado |

### estudo_agressivo.csv

As 37 operações do Estudo Agressivo (`docs/ESTUDO_AGRESSIVO.md`), uma por linha. Todas são do perfil agressivo: cota entre 0,30 e 0,60 do valor patrimonial na entrada.

- Colunas com (%) já estão em porcentagem: 5,3 quer dizer 5,3%.
- "Pontos" é diferença entre duas porcentagens: 2,0 quer dizer 2 pontos percentuais.
- Nas operações em aberto, a data e o preço de saída são os do último pregão da base, e os resultados são parciais.
- "Valorização do mercado" é a do fundo imobiliário do meio, nas mesmas datas.

### tecnico/estudo_agressivo_completo.csv

A mesma lista com 57 colunas e nomes abreviados, usada pelo programa. Não é para leitura; a coluna "perfil" desse arquivo é uma classificação antiga, pelo patrimônio, e deve ser ignorada.

### cdi.csv

Taxa do CDI de cada dia útil, de 02/01/2017 a 13/11/2026, do Banco Central. Traz a taxa do dia, a taxa equivalente ao ano e dois índices acumulados: um para 100% do CDI e outro para 105%. Para saber quanto 105% do CDI rendeu entre duas datas, divida o índice da data final pelo da data inicial. Os índices são antes do imposto.

### rendimentos_pagamentos.csv

Os mesmos avisos de `rendimentos.csv`, com a data em que o dinheiro foi pago. Em 58 dos 23.800 a data de pagamento não foi encontrada e a célula fica vazia.

### amortizacoes.csv

Devoluções de patrimônio aos cotistas (não são rendimento). Os valores estão como o fundo informou, sem ajuste por desdobramento.

### tecnico/fatos_textos.csv.gz

Os primeiros 3.000 caracteres de cada fato relevante da planilha de anúncios. Arquivo compactado, para uso dos programas.
