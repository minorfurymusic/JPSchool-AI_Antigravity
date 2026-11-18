# Inventário do projeto Radar de FIIs — para alimentar outra IA (18/11/2026)

Repositório: `minorfurymusic/JPSchool-AI_Antigravity`, branch `claude/happy-bell-a81nvp`.
Tudo abaixo foi conferido nos arquivos do repositório nesta data. Resultados são do passado (2018–2026) e já foram
olhados muitas vezes: risco real de regra ajustada ao passado.

## 1. Objetivo atual do dono

Achar fundos imobiliários (FII) que caíram de forma significativa, mas sem a crise de desespero (essa é a Skill
"Kairi Padrão"); descontados sobre o patrimônio; saudáveis; com rendimento constante (de preferência sempre o mesmo
valor) e que paguem bem. Expectativa do dono: juros começam a cair em 2027 e terminam o ano abaixo de 10%
(Selic hoje: 13,75%, fase de queda). Carteira de R$ 10 mil; comparar sempre com 105% do CDI líquido de imposto.

## 2. Fontes dos dados

| Fonte | O que traz | Situação |
|---|---|---|
| B3 (cotações diárias) | abertura, máxima, mínima, fechamento, volume, por fundo e dia, 2017–09/11/2026 | em `planilhas/precos_AAAA.csv` |
| CVM — informe mensal (dados abertos) | patrimônio, valor patrimonial por cota, cotas, cotistas | já embutido em `precos_AAAA.csv` (75 dias de atraso) |
| CVM — informe trimestral (dados abertos) | resultado em regime de caixa, rendimento declarado, ganho com venda, data de entrega | `planilhas/tecnico/cobertura_trimestral.csv` |
| FNET (B3) — avisos de rendimento estruturados | valor, data-base, data de pagamento e data do anúncio de cada rendimento | 35.773 avisos lidos → `rendimentos.csv`, `rendimentos_pagamentos.csv`, `amortizacoes.csv` |
| FNET — fatos relevantes | texto dos fatos relevantes 2017–2026 (primeiros 3.000 caracteres), todos os fundos | `planilhas/tecnico/fatos_textos.csv.gz` |
| FNET — fatos e comunicados (texto completo) | 30 fundos candidatos, 2017–2026; 43 fundos com sinal do Kairi, 05/2025–11/2026 | `fnet_2017_documentos.csv.gz`, `fnet_2026_documentos.csv.gz` |
| FNET — relatórios gerenciais | texto completo de 5 relatórios (set/2026) | `relatorios_gerenciais_set2026.csv.gz` |
| Banco Central | Selic e CDI diários | `mercado.csv`, `cdi.csv` |

Regras de tempo usadas em todos os estudos (para não usar dado que ainda não existia no dia):
- valor patrimonial e patrimônio só a partir de 75 dias depois do mês de referência;
- informe trimestral só a partir da data de entrega real à CVM;
- rendimento só a partir da data do anúncio;
- compra na abertura do pregão seguinte ao sinal.

## 3. Arquivos de dados (CSV, separador `;`, decimal `,`, UTF-8)

Explicação das colunas principais em `planilhas/LEIA-ME.md`.

| Arquivo | Linhas | Fundos | Período | Tamanho | Colunas |
|---|---|---|---|---|---|
| `planilhas/amortizacoes.csv` | 2147 | 299 | 06/01/2017–10/11/2026 | 109 KB | fundo, tipo, data_base, data_pagamento, valor_sem_ajuste (R$/cota) |
| `planilhas/anuncios.csv` | 7962 | 431 | 02/01/2017–06/11/2026 | 3288 KB | id, fundo, data_anuncio, data_entrada, tipo, sentido, repetido (1/0), continuacao (1/0), declarou_efeito, efeito_percentual, valor_por_cota_citado, preco_entrada, negociou_na_entrada (1/0), volume_medio_60 (R$), ordem_maxima (R$), rendimento_mensal_na_entrada (R$/cota), rendimento_ano_sobre_preco (%), selic_ano (%), regua_selic_liquida_mais_3 (%), valor_patrimonial_cota, preco_sobre_valor_patrimon |
| `planilhas/auditoria_bloco1_correlacao_grupos.csv` | 388 |  |  | 33 KB | fundos no grupo, pares com 20+ dias juntos, correlação média dos pares, correlação média de pares sorteados, primeira entrada, primeiro sinal, carteira, periodo, agrupamento |
| `planilhas/auditoria_bloco1_episodios.csv` | 429 |  |  | 39 KB | janela_pregoes, carteira, periodo, episodio, primeira_entrada, ultima_entrada, ordens, ordens_fechadas, soma_res_antes_imposto_rs, res_pct_medio, excesso_pct_medio, excesso_rs |
| `planilhas/auditoria_bloco1_indicadores.csv` | 270 |  |  | 22 KB | carteira, medida, periodo, indicador, valor |
| `planilhas/auditoria_bloco1_lacunas.csv` | 15 |  |  | 2 KB | dado, situacao, efeito |
| `planilhas/auditoria_bloco1_ordens.csv` | 808 | 197 | 09/05/2018–05/11/2026 | 162 KB | carteira, fundo, sinal, entrada, saida, motivo, situacao, periodo, cotas, valor, valorizacao_rs, rendimentos_calculados_rs, rendimentos_planilha_rs, dif_rendimentos_rs, taxa_compra_rs, taxa_venda_rs, resultado_antes_imposto_rs, resultado_antes_imposto_frac, cdi105_bruto_frac, excesso_frac, excesso_rs, dif_resultado_vs_saidas_rs |
| `planilhas/auditoria_bloco1_patrimonio_mensal.csv` | 321 |  |  | 24 KB | carteira, mes, data_fim, patrimonio_carteira, patrimonio_espelho, retorno_carteira, retorno_espelho, excesso |
| `planilhas/auditoria_bloco1_pico.csv` | 3 |  |  | 0 KB | carteira, dinheiro_inicial, ordens_em_aberto_a_mercado, saldo_liquido_de_IR, rendimentos_a_receber, DARF_a_pagar, valor_final_carteira, valor_final_espelho, retorno_aa_carteira, retorno_aa_espelho, diferenca_pp, diferenca_rs, faltas_de_caixa |
| `planilhas/auditoria_bloco1_risco.csv` | 6 |  |  | 0 KB | carteira, serie, retorno_aa, vol_mensal, excesso_mensal_medio, sharpe, sortino, calmar, maior_queda, inicio_queda, fundo_queda |
| `planilhas/auditoria_bloco1_significancia.csv` | 72 |  |  | 9 KB | carteira, periodo, metodo, n, media, t, p, ic_lo, ic_hi, unidade, rep_nao_positivas |
| `planilhas/auditoria_bloco1_tir.csv` | 18 |  |  | 2 KB | carteira, periodo, base, ordens, investido_rs, rendimentos_rs, vendas_liq_rs, imposto_fii_rs, imposto_espelho_rs, tir_ordens, tir_espelho_105, diferenca_pp |
| `planilhas/auditoria_bloco2_duas_partes.csv` | 6 |  |  | 1 KB | gatilho, periodo, ordens, segunda_comprada, segunda_nao, parado, cdi_parado, res_com_cdi, base, pct_pretendido, res_antes, exc |
| `planilhas/auditoria_bloco2_faixas.csv` | 21 |  |  | 3 KB | gatilho, periodo, faixa, ordens, media, mediana, pos, exc_pp, exc, res, abertas |
| `planilhas/auditoria_bloco2_funil.csv` | 6 |  |  | 0 KB | gatilho, periodo, sinais_com_ordem, chegou_15, chegou_20, chegou_30 |
| `planilhas/auditoria_bloco2_gatilhos.csv` | 12 |  |  | 3 KB | gatilho, periodo, ordens, abertas, aplicado, res, res_pct, cdi, exc, exc_pp, pos, pior, pior_rs, dias, pico, imp, exc_imp, n_exc_pos |
| `planilhas/auditoria_bloco2_ordens_gatilhos.csv` | 1135 |  |  | 159 KB | Gatilho, Fundo, Data do sinal, Data de entrada, Período, Preço de entrada (R$), Cotas, Valor (R$), Data de saída, Preço de saída (R$), Motivo, Dias, Resultado antes do imposto (R$), Resultado (%), 105% CDI líquido (R$), Excesso (R$), Maior queda abaixo da entrada (%), Profundidade máxima no episódio (%) |
| `planilhas/auditoria_bloco2_perdidas.csv` | 9 |  |  | 1 KB | de, para, periodo, ordens, nunca_chegou, luc_perdidas_n, luc_perdidas_rs, prej_evitados_n, prej_evitados_rs, saldo_rs, luc_perdidas_exc, prej_evitados_exc, exc_nunca, chegou_n, chegou_rs, chegou_com_ordem_sup, nunca_com_ordem_sup |
| `planilhas/auditoria_bloco2_virada_evitadas.csv` | 6 |  |  | 2 KB | gatilho, periodo, ordens_diretas, sem_ordem_na_virada, nao_virou, sem_negociacao, bloqueado, menor_1000, perda_evitada_n, perda_evitada_rs, perda_evitada_exc, ganho_perdido_n, ganho_perdido_rs, ganho_perdido_exc, saldo_sem_ordem_rs, exc_sem_ordem, pos_sem_ordem, ordens_virada_sem_direta, direta_nos_sinais_com_virada_rs, virada_nos_sinais_com_direta_rs, direta_nos_sinais_com_virada_exc, virada_nos_ |
| `planilhas/auditoria_bloco2_virada_ordens.csv` | 1516 |  |  | 209 KB | Gatilho, Método, Fundo, Data do sinal, Data da entrada direta (chave do período), Período, Preço médio de entrada (R$), Fechamento do sinal (R$), Valor aplicado (R$), Data de saída, Motivo, Resultado antes do imposto (R$), Resultado (%), 105% CDI líquido (R$), Excesso (R$), Maior queda abaixo da entrada (%) |
| `planilhas/auditoria_bloco2_virada_resumo.csv` | 24 |  |  | 10 KB | metodo, ordens, sinais_sem_ordem, preco_vs_fech_sinal, res, res_pct, cdi, exc, exc_pp, pos, dp, dp_perdas, pior, pior10, queda_med, queda_pior, q05, q95, dias, aplicado, imp, exc_imp, abertas, media, gatilho, periodo |
| `planilhas/auditoria_bloco3_6a_grupos.csv` | 162 |  |  | 24 KB | definição de fato negativo, janela (dias), carteira, período, grupo, ordens, média (%), mediana (%), % positivas, excesso médio s/ 105% CDI bruto (p.p.), excesso médio s/ 105% CDI líquido (p.p.), pior ordem (%), maior queda média abaixo da entrada (%), dias corridos médios, % saiu por prazo, % em aberto |
| `planilhas/auditoria_bloco3_6a_sensibilidade_definicao.csv` | 9 |  |  | 1 KB | definição, carteira, ordens grupo 0, média (%) grupo 0, excesso (p.p.) grupo 0, ordens grupo 1, média (%) grupo 1, excesso (p.p.) grupo 1, ordens grupo 2 ou mais, média (%) grupo 2 ou mais, excesso (p.p.) grupo 2 ou mais |
| `planilhas/auditoria_bloco3_6a_testes.csv` | 108 |  |  | 14 KB | definição de fato negativo, janela (dias), carteira, período, medida, ordens sem, ordens com, média sem, média com, diferença (sem − com), IC95 inferior, IC95 superior, p Mann-Whitney |
| `planilhas/auditoria_bloco3_6b_grupos.csv` | 81 |  |  | 16 KB | janela, carteira, período, grupo, ordens, média (%), mediana (%), % positivas, excesso médio s/ 105% CDI bruto (p.p.), excesso médio s/ 105% CDI líquido (p.p.), pior ordem (%), maior queda média abaixo da entrada (%), dias corridos médios, % saiu por prazo, % em aberto |
| `planilhas/auditoria_bloco3_6b_testes.csv` | 54 |  |  | 9 KB | janela, carteira, período, medida, ordens sem, ordens com, média sem, média com, diferença (sem − com), IC95 inferior, IC95 superior, p Mann-Whitney |
| `planilhas/auditoria_bloco3_6c_por_tipo.csv` | 36 |  |  | 5 KB | carteira, tipo, ordens esc, média (%) esc, ordens conf, média (%) conf, ordens tot, média (%) tot, mediana (%) tot, % positivas tot, excesso s/ 105% CDI (p.p.) tot, pode concluir? |
| `planilhas/auditoria_bloco3_6d_grupos.csv` | 135 |  |  | 29 KB | subconjunto, visão, período, grupo, ordens, média (%), mediana (%), % positivas, excesso médio s/ 105% CDI bruto (p.p.), excesso médio s/ 105% CDI líquido (p.p.), pior ordem (%), maior queda média abaixo da entrada (%), dias corridos médios, % saiu por prazo, % em aberto |
| `planilhas/auditoria_bloco3_6d_testes.csv` | 45 |  |  | 7 KB | subconjunto, visão, período, ordens sem, ordens com, média sem, média com, diferença (sem − com), IC95 inferior, IC95 superior, p Mann-Whitney |
| `planilhas/auditoria_bloco3_amostra_leitura.csv` | 40 | 34 | 02/06/2017–30/10/2026 | 4 KB | sentido sorteado, id, fundo, data, tipo (palavras), veredito da leitura, motivo |
| `planilhas/auditoria_bloco3_cobertura.csv` | 4 |  |  | 0 KB | carteira, ordens, ordens de fundo sem nenhum fato na planilha |
| `planilhas/auditoria_bloco3_fatos_ignorados.csv` | 10 |  |  | 0 KB | grupo de fatos, fatos |
| `planilhas/auditoria_bloco3_lacunas_medidas.csv` | 6 |  |  | 0 KB | medida, valor |
| `planilhas/auditoria_bloco3_ordens_com_fatos.csv` | 808 |  | 09/05/2018–05/11/2026 | 302 KB | Carteira, Fundo, Tipo do fundo, sinal, entrada, Preço de entrada (R$), Cotas, valor, Situação, saida, Preço de saída (ou atual) (R$), motivo, dias, Pregões, Valorização (R$), Valorização (%), Rendimentos recebidos (R$), Rendimentos (%), Taxas (R$), Imposto (R$), res_rs, res_col, Selic líquida no mesmo período (R$), Selic líquida (%), Diferença para a Selic (R$), Ganhou da Selic (sim/não), maxqueda |
| `planilhas/cdi.csv` | 2476 |  | 02/01/2017–13/11/2026 | 113 KB | data, cdi_ao_dia (%), cdi_ao_ano (%), indice_100_do_cdi, indice_105_do_cdi |
| `planilhas/cobertura_teste_faixas.csv` | 6 |  |  | 0 KB | faixa, casos, fundos, corte_rend_10pct, var_rend_mediana, cota_contra_mercado_media, cota_contra_mercado_mediana |
| `planilhas/estudo_agressivo.csv` | 37 |  |  | 10 KB | Perfil, Faixa de ordem que o fundo aguenta, Tipo do fundo, Fundo, Tipo do anúncio, Data do anúncio, Data de entrada, Preço de entrada (R$), Situação, Data de saída (ou do último preço), Preço de saída (ou atual) (R$), Motivo da saída, Pregões entre entrada e saída, Cota sobre valor patrimonial na entrada, Patrimônio do fundo (R$ milhões), Maior ordem que o fundo aguenta (R$), Valorização da cota ( |
| `planilhas/fundos.csv` | 524 | 524 |  | 22 KB | fundo, nome, segmento, mandato, tipo |
| `planilhas/kairi_cortes.csv` | 140 |  |  | 27 KB | Carteira, Fundo, Tipo do fundo, Data de entrada, Rendimento mensal na entrada (R$/cota), Data do corte (aviso), Valor do corte (R$/cota), Queda do rendimento no corte (%), Aviso seguinte 1 (R$/cota), Aviso seguinte 2 (R$/cota), Aviso seguinte 3 (R$/cota), Aviso seguinte 4 (R$/cota), Aviso seguinte 5 (R$/cota), Aviso seguinte 6 (R$/cota), Voltou a 95% do rendimento nos 6 avisos seguintes (sim/não), |
| `planilhas/kairi_cruzamento.csv` | 2064 |  |  | 408 KB | Carteira, Regra de saída (por extenso), Fundo, Data de entrada, Preço de entrada (R$), Valor da ordem (R$), Data em que cruzou a média, Preço do cruzamento (R$), Situação, Data de saída (ou do último preço), Preço de saída (ou atual) (R$), Motivo da saída, Dias corridos, Valorização (%), Rendimentos (%), Resultado antes do imposto (%), Resultado antes do imposto (R$), Selic líquida no mesmo períod |
| `planilhas/kairi_escada.csv` | 2064 |  |  | 378 KB | Carteira, Regra de saída, Fundo, Data de entrada, Preço de entrada (R$), Valor da ordem (R$), Piso no dia da entrada (R$), Teto (R$), Data em que tocou o piso pela primeira vez, Situação, Data de saída (ou do último preço), Preço de saída (ou atual) (R$), Motivo da saída, Dias corridos, Valorização (%), Rendimentos (%), Resultado antes do imposto (%), Resultado antes do imposto (R$), Selic líquida |
| `planilhas/kairi_ordens.csv` | 808 |  |  | 161 KB | Carteira, Fundo, Tipo do fundo, Data do sinal, Data de entrada, Preço de entrada (R$), Cotas, Valor da ordem (R$), Situação, Data de saída (ou do último preço), Preço de saída (ou atual) (R$), Motivo da saída, Dias corridos, Pregões, Valorização (R$), Valorização (%), Rendimentos recebidos (R$), Rendimentos (%), Taxas (R$), Imposto (R$), Resultado (R$), Resultado (%), Selic líquida no mesmo períod |
| `planilhas/kairi_ordens_saidas.csv` | 3612 |  |  | 898 KB | Carteira, Regra de saída, Fundo, Tipo do fundo, Data do sinal, Data de entrada, Preço de entrada (R$), Cotas, Valor da ordem (R$), Cota sobre valor patrimonial na entrada, Alvo da saída no dia da entrada (R$), Distância do alvo (%), Situação, Data de saída (ou do último preço), Preço de saída (ou atual) (R$), Cota sobre valor patrimonial na saída, Motivo da saída, Dias corridos, Pregões, Valorizaç |
| `planilhas/mercado.csv` | 2447 |  | 02/01/2017–09/11/2026 | 97 KB | data, selic_ano (%), selic_liquida_ano (%), indice_mercado, fundos_negociados, mediana_preco_sobre_valor_patrimonial |
| `planilhas/precos_2017.csv` | 22305 | 123 | 02/01/2017–28/12/2017 | 1915 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2018.csv` | 26140 | 134 | 02/01/2018–28/12/2018 | 2396 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2019.csv` | 32362 | 180 | 02/01/2019–30/12/2019 | 2989 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2020.csv` | 44571 | 232 | 02/01/2020–30/12/2020 | 4098 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2021.csv` | 55522 | 280 | 04/01/2021–30/12/2021 | 5094 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2022.csv` | 63445 | 309 | 03/01/2022–29/12/2022 | 5808 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2023.csv` | 65272 | 333 | 02/01/2023–28/12/2023 | 5959 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2024.csv` | 69818 | 364 | 02/01/2024–30/12/2024 | 6345 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2025.csv` | 69298 | 356 | 02/01/2025–30/12/2025 | 6256 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/precos_2026.csv` | 56068 | 340 | 02/01/2026–09/11/2026 | 5051 KB | data, fundo, abertura, maxima, minima, fechamento, negociou (1/0), volume_dia (R$), volume_medio_60 (R$), rendimento_mensal (R$/cota), rendimento_ano_sobre_preco (%), valor_patrimonial_cota, preco_sobre_valor_patrimonial, patrimonio (R$), amortizacao_12m (1/0) |
| `planilhas/renda_descontada_elegiveis_hoje.csv` | 6 | 6 |  | 1 KB | fundo, cobertura_cvm, janela_cvm, resultado_sobre_distribuido_ultimos_3_meses, reserva_caindo, problema_nos_documentos, veredito |
| `planilhas/renda_descontada_relatorios_set2026.csv` | 78 | 5 |  | 4 KB | fundo, documento_fnet, relatorio, mes, item, valor, unidade |
| `planilhas/rendimentos.csv` | 23800 | 455 | 02/01/2017–06/11/2026 | 800 KB | fundo, data_conhecido, data_base, valor (R$/cota) |
| `planilhas/rendimentos_pagamentos.csv` | 23800 | 455 | 02/01/2017–06/11/2026 | 1055 KB | fundo, data_conhecido, data_base, data_pagamento, valor (R$/cota) |
| `planilhas/tecnico/busca_celulas.csv` | 480 |  |  | 63 KB | grupo, faixa_pvp, acima_mm200, selic_regime, n_treino, excesso_medio_treino, excesso_mediano_treino, pct_positivo_treino, n_teste, excesso_medio_teste, excesso_mediano_teste, pct_positivo_teste |
| `planilhas/tecnico/busca_operacoes.csv` | 184 | 71 | 11/06/2018–21/10/2026 | 36 KB | cid, fundo, entrada, saida, pregoes, motivo, ent, preco_saida, valorizacao, rendimento, liquido, selic, excesso, dias, ik, modelo, periodo, grupo, faixa, acima, regime |
| `planilhas/tecnico/busca_saidas.csv` | 360 |  |  | 86 KB | celula, alvo, limite, prazo, sair_no_corte, n_treino, exc_medio_treino, exc_mediano_treino, pct_pos_treino, pregoes_treino, em_aberto_treino, n_teste, exc_medio_teste, exc_mediano_teste, pct_pos_teste, pregoes_teste, em_aberto_teste |
| `planilhas/tecnico/caminho_agressivo.csv` | 37 | 29 | 02/07/2021–28/10/2026 | 6 KB | fundo, entrada, preco_entrada, pvp, origem, pregoes_observados, completa, primeiro_fechamento_acima, dias_fechando_acima, maior_alta, dia_maior_alta, maior_queda, dia_maior_queda, padrao, dia_primeiro_toque, pico, dia_pico, voltou_ao_preco_de_entrada, dia_da_volta, maior_queda_depois_do_pico, tocou_menos5_depois, fechamento_d20, fechamento_d60, fechamento_d120, dia_fundo, maior_alta_depois_do_fund |
| `planilhas/tecnico/cobertura_teste_passado.csv` | 11582 | 266 | 31/01/2019–29/05/2026 | 1513 KB | fundo, dia, cobertura, var_rend, cota_6m, mercado_6m, corte_10, cota_contra_mercado, faixa |
| `planilhas/tecnico/cobertura_trimestral.csv` | 15158 | 818 | 30/03/2017–30/09/2026 | 1965 KB | fundo, cnpj, nome, data_ref, entrega, resultado_acumulado, ganho_venda_semestre, rendimento_declarado, resultado_trimestre |
| `planilhas/tecnico/dividendo_alto_rapido.csv` | 11096 | 286 | 31/01/2018–31/10/2025 | 1942 KB | data, fundo, tipo, dy, ret, preco, cdi, tend, rendimento_ano_sobre_preco (%), preco_sobre_valor_patrimonial, pvp, grupo, saude |
| `planilhas/tecnico/estudo_agressivo_completo.csv` | 37 |  | 02/07/2021–28/10/2026 | 15 KB | origem, ticker, entrada, saida, preco_entrada, preco_saida, div0, maior, motivo, pregoes, valorizacao, rendimento, total, liquido, selic, subiu, aumento_max, aberta, perfil, pl, pvp, vol60, ordem_max, dy, regua, passa_regua, tipo, faixa_ordem, faixa_desconto, val_liquida, dif_selic, fundo_preco, mercado_preco, tipo_preco, mm200, mm50, acima_mm200, acima_mm50, ret60, dist_max252, data_anuncio, perd |
| `planilhas/tecnico/fatos_textos.csv.gz` | 7962 | 431 | 02/01/2017–06/11/2026 | 4463 KB | id, fundo, data_anuncio, tipo, texto (primeiros 3.000 caracteres) |
| `planilhas/tecnico/fnet_2017_documentos.csv.gz` | 1746 | 30 | 06/02/2017–13/11/2026 | 1648 KB | id, fundo, cnpj, data de entrega, categoria, tipo, formato, leitura, texto completo |
| `planilhas/tecnico/fnet_2026_documentos.csv.gz` | 755 | 43 | 02/05/2025–13/11/2026 | 483 KB | id, fundo, cnpj, data de entrega, categoria, tipo, especie, situacao_doc, versao, formato, leitura, classe, padrao, trecho, sem_rend_padrao, sem_rend_trecho, leitura_manual, texto (primeiros 5.000 caracteres) |
| `planilhas/tecnico/kairi_carteira_operacoes.csv` | 921 | 136 | 09/05/2018–05/11/2026 | 141 KB | simulacao, carteira, ordem, fundo, sinal, entrada, saida, motivo, pregoes, cotas, preco_entrada, valor_compra, taxa_compra, preco_saida, valor_venda, taxa_venda, rendimentos, ganho_tributavel, resultado, em_aberto, media_saida |
| `planilhas/tecnico/kairi_carteira_patrimonio.csv` | 107 |  | 31/01/2018–09/11/2026 | 11 KB | data, A-1000, A-2000, A-3300, B-1000, B-2000, B-3300, C-1000, C-2000, C-3300, Tudo na Selic, Mercado |
| `planilhas/tecnico/kairi_carteira_resumo.csv` | 9 |  |  | 2 KB | simulacao, carteira, ordem, patrimonio_final, retorno_total, retorno_ao_ano, selic_total, mercado_total, selic_ao_ano, mercado_ao_ano, maior_queda, data_pico, data_fundo, max_posicoes, operacoes, pct_com_ganho, resultado_medio_op, pregoes_medios, sinais_nao_atendidos, abertas_fim, retorno_2018_2022, retorno_2023_fim, selic_2018_2022, selic_2023_fim, mercado_2018_2022, mercado_2023_fim |
| `planilhas/tecnico/kairi_configuracoes.csv` | 72 |  |  | 29 KB | N, X, mantido, saida, E_n, E_preg, E_alta, E_val, E_rend, E_liq, E_selic, E_exc, E_exc_med, E_pos, E_menor, E_abertas, E_descart, C_n, C_preg, C_alta, C_val, C_rend, C_liq, C_selic, C_exc, C_exc_med, C_pos, C_menor, C_abertas, C_descart |
| `planilhas/tecnico/kairi_constancia_rendimento.csv` | 453 | 180 | 09/05/2018–04/09/2026 | 160 KB | fundo, sinal, entrada, saida, motivo, status, res, tipo, pvp, dy, dy_menos_cdi, vp_12m, rend_12m, patrimonio_mi, depois_rend, depois_vp, grupo, meses, oscilacao, cortes, pior_queda, tendencia, planilha, fundo_6m, merc_6m, individual |
| `planilhas/tecnico/kairi_cruzamento_comparacao.csv` | 30 |  |  | 5 KB | Carteira, Regra de saída, ordens, fechadas, em aberto, dias corridos médios das fechadas, resultado líquido (R$), Selic do mesmo dinheiro (R$), diferença (R$), retorno ao ano TOTAL (%), retorno ao ano ESCOLHA (%), retorno ao ano CONFERÊNCIA (%), resultado médio por ordem fechada (%), % das fechadas com resultado > 0, % que ganharam da Selic, pico de dinheiro aplicado (R$) |
| `planilhas/tecnico/kairi_escada_comparacao.csv` | 126 |  |  | 16 KB | Carteira, Período, Saída, Regra de saída, ordens, fechadas, em aberto, dias corridos médios, resultado líquido (R$), Selic líquida no mesmo dinheiro (R$), diferença para a Selic (R$), retorno ao ano sobre o dinheiro aplicado (%), Selic ao ano na mesma conta (%), resultado médio por ordem fechada (%), % fechadas com resultado > 0, % fechadas que ganharam da Selic, pior ordem (%), pico de dinheiro a |
| `planilhas/tecnico/kairi_exp_grade.csv` | 40 |  |  | 16 KB | N, X, mantido, E.n, E.preg, E.%alta, E.valor, E.rend, E.liq, E.selic, E.exc, E.excmed, E.%ganh, E.menor, C.n, C.preg, C.%alta, C.valor, C.rend, C.liq, C.selic, C.exc, C.excmed, C.%ganh, C.menor |
| `planilhas/tecnico/kairi_exp_operacoes.csv` | 511 | 195 | 09/05/2018–05/11/2026 | 174 KB | fundo, sinal, entrada, saida_data, motivo, pregoes, preco_entrada, preco_saida, valorizacao, rendimento, liquido, selic, excesso, menor_preco, descartada, dias, pvp_sinal, amplitude, kairi_mercado, queda_relativa, faixa_pvp, tipo, selic_regime, faixa_ordem, rendimento_sobre_preco, N, X, mantido, saida, regra, fechada, periodo, ano, config |
| `planilhas/tecnico/kairi_operacoes.csv` | 264 | 151 | 28/05/2018–05/11/2026 | 74 KB | N, X, mantido, saida, fundo, kairi_sinal, pvp_sinal, sinal, entrada, saida_data, motivo, pregoes, preco_entrada, preco_saida, valorizacao, rendimento, liquido, selic, excesso, menor_preco, descartada, dias, fechada, periodo, ano, tipo_fundo, faixa_pvp, escolha |
| `planilhas/tecnico/kairi_ordens_por_ano.csv` | 1276 |  |  | 51 KB | Carteira, Ano, Indicador, Valor |
| `planilhas/tecnico/kairi_saidas_comparacao.csv` | 108 |  |  | 23 KB | Carteira, Período, Saída, Regra de saída, ordens, fechadas, em aberto, pregões médios das fechadas, dias corridos médios, total aplicado (R$), valorização (R$), rendimentos (R$), taxas (R$), imposto (R$), resultado líquido (R$), Selic líquida no mesmo dinheiro (R$), diferença para a Selic (R$), dinheiro x dias (milhões R$.dia), retorno ao ano sobre o dinheiro aplicado (%), Selic ao ano na mesma co |
| `planilhas/tecnico/kairi_troca_pares.csv` | 268 |  |  | 34 KB | seg, ent_seg, novo, sinal_novo, dias_no_seg, lucro_agora, resto_seg, novo_res, fim, vantagem_troca |
| `planilhas/tecnico/relatorios_gerenciais_set2026.csv.gz` | 5 | 5 |  | 63 KB | id, fundo, tipo, referencia, texto_completo |
### Planilhas de resultado (Excel)

| Planilha | Abas |
|---|---|
| `planilhas/kairi_alvo_segunda_entrada.xlsx` | A - depois de subir X%, B - segunda entrada |
| `planilhas/kairi_ano_a_ano_skill.xlsx` | Resumo, Por ano 1, Operações 1, Barrados 1, Por ano 2, Operações 2, Barrados 2, Por ano 3, Operações 3, Por ano 4, Operações 4 |
| `planilhas/kairi_carteira_2026.xlsx` | Resumo, Operações fechadas, Posições abertas, Patrimônio dia a dia, Saídas antecipadas e bloqueios, Legenda |
| `planilhas/kairi_carteira_anos.xlsx` | Ano a ano, Contínua, Operações fechadas, Posições abertas no fim do ano, Legenda |
| `planilhas/kairi_fundamentos_entrada.xlsx` | Conservadoras (C1 25% + C2 20%), Conservadoras (C1 25% + C2 15%), Todos os fundos, gatilho 15%, Um fundo C2 20%, Um fundo C2 15% |
| `planilhas/kairi_gatilhos.xlsx` | Resumo, Dados dos gráficos, Funil, Até onde caiu, Subir o gatilho, Legenda e avisos |
| `planilhas/kairi_mapa_operacoes.xlsx` | Por ano, Entradas por mês, Saídas por mês, Ativas ao mesmo tempo, Operações |
| `planilhas/kairi_operacao_a_operacao.xlsx` | Resumo, Operações, Acumulado |
| `planilhas/kairi_oportunidades.xlsx` | Validação e oportunidades, Aprovadas por ano, Carteira dividida, Operações 1, Operações 2, Operações 3, Operações 4, Operações 5, Operações 6, Operações 7, Operações 8 |
| `planilhas/kairi_sinais_conservadora2.xlsx` | Sinais por mês, Entradas por ano e mês, Saídas por ano e mês, Operações |
| `planilhas/kairi_sinais_conservadoras.xlsx` | Resumo, Por mês - Conservadora 1, Por mês - Conservadora 2, Por mês - As duas juntas, Entradas C1, Saídas C1, Entradas C2, Saídas C2, Entradas Juntas, Saídas Juntas, Operações |
| `planilhas/kairi_um_fundo.xlsx` | Resumo, Ano a ano, Operações 1, Operações 2, Operações 3, Operações 4, Operações 5, Operações 6, Operações 7, Operações 8, Patrimônio dia a dia |
| `planilhas/renda_descontada.xlsx` | Resumo, Por fase da Selic, Por ano A, Operações A, Em aberto A, Por ano B, Operações B, Em aberto B, Por ano C, Operações C, Em aberto C, Por ano D, Operações D, Em aberto D, Por ano E, Operações E, Em aberto E, Por ano F, Operações F, Em aberto F, Por ano G, Operações G, Em aberto G, Por ano H, Ope |
### Problemas conhecidos nos dados

- 334 variações de mais de 25% num dia em 128 fundos (base de preços não limpa); CARE11 salta sem ajuste
  (17/08/2021 → 14/03/2022); PRSV11 sem preço de 07/2020 a 02/2021; BRIM11 a conferir; TORD11 último preço R$ 0,97.
- Em 2017, 25% das linhas sem valor patrimonial e 33% sem rendimento.
- Classificação automática dos fatos relevantes por palavras erra muito (amostra: 10 de 20 negativos errados).
- Comunicados ao mercado antes de 05/2025 só existem para os 30 fundos candidatos da renda descontada.
- Reserva de lucros não existe em dado estruturado; só no relatório gerencial em PDF (formato muda por gestora).
- No informe trimestral da CVM, "resultado acumulado" e "rendimento declarado" do 2º e 4º trimestres são do semestre.

## 4. Estratégias e filtros já testados (R$ 10 mil, 2018–09/11/2026; 105% do CDI líquido = R$ 20.779)

### 4.1 Kairi Padrão (aprovada; Skill `.claude/skills/kairi-padrao/SKILL.md`)

- Entrada: cota 25% abaixo da média de 200 pregões em fundo com negociação típica (mediana de 60 pregões) de
  R$ 500 mil a R$ 1 mi/dia; ou 20% abaixo em fundo acima de R$ 1 mi/dia. Patrimônio ≥ R$ 50 mi; rendimento do dia
  ≥ 95% do de 6 meses antes; preço 0,30–3,0 do patrimônio; sem amortização relevante; avaliação de saúde.
- Saída: fechamento igual ou acima da média de 200 pregões; prazo 252 pregões; saída antecipada por liquidação/
  incorporação/rendimento zero.
- Resultado: 41 oportunidades, 39 de 40 fechadas com lucro, +24,7% por operação; R$ 10 mil → R$ 32.103 (queda
  máxima −9%). Mas só 3 de 9 anos com 3+ oportunidades (2019 e 2022: nenhuma).

### 4.2 Avaliação de saúde (Skill `.claude/skills/avaliar-fundo/SKILL.md`, `estudos/saude_fundo.py`)

- Queda só do fundo = 10 pontos ou mais pior que o mercado de fundos em 6 meses.
- Sinais de doença: rendimento caindo mais de 10% em 12 meses; 3+ cortes em 12 meses; valor patrimonial por cota
  caindo mais de 5% em 12 meses; documento negativo (calote, recuperação judicial, remarcação negativa, ofício da
  B3/CVM, rescisão de inquilino).
- Veredito: NÃO COMPRAR (queda só do fundo + doença); ATENÇÃO (queda só do fundo de 20+ pontos sem motivo nos dados);
  SAUDÁVEL (o resto).

### 4.3 Renda descontada saudável (NÃO aprovada; `estudos/renda_descontada.py`, `planilhas/renda_descontada.xlsx`)

Base comum: revisão no fim do mês; patrimônio ≥ R$ 100 mi; negociação típica ≥ R$ 250 mil/dia; preço 0,60–0,85 do
patrimônio; patrimônio por cota em 12 meses ≥ −5%; rendimento constante (tendência ≥ −10%, até 2 cortes de 5%,
oscilação ≤ 0,15); avaliação de saúde ≠ NÃO COMPRAR; 5 fundos; nota por rendimento, desconto, constância e patrimônio.

| Versão | Diferença | Valor final | Maior queda | Operações / com lucro |
|---|---|---|---|---|
| A | rendimento ≥ CDI + 1; sai por doença ou preço justo (0,95 do patrimônio ou rendimento no CDI) | R$ 15.103 | −20,2% | 35 / 51% |
| B | A + doença confirmada em 2 meses; preço justo só por 0,95 | R$ 14.682 | −24,8% | 22 / 50% |
| C | B + não compra com Selic subindo | R$ 15.435 | −21,3% | 16 / 38% |
| **D** | B + rendimento 2 pontos acima da mediana do próprio tipo de fundo | **R$ 20.810** | −10,9% | 13 / 69% |
| E | C + rendimento comparado ao tipo | R$ 16.741 | −17,7% | 11 / 55% |
| F | D + cobertura do rendimento ≥ 0,90 | R$ 19.731 | −14,1% | 13 / 69% |
| G | D + sem documento negativo em 12 meses | R$ 18.344 | −17,7% | 6 / 50% |
| H | D + F + G | R$ 19.449 | −12,1% | 8 / 75% |

Versão D por fase da Selic (média ao mês): Selic subindo +1,16% (CDI +0,73%); parada +0,91% (CDI +0,64%);
caindo +0,16% (CDI +0,56%). Poucos ciclos (40 meses de queda).

### 4.4 Estudos antigos (docs/ESTRATEGIAS.md e docs/ESTUDO_*.md)

- Estratégia 1 — anúncio de aumento de rendimento: em 2026, moderado +10,1% e agressivo +23,0% contra +9,0% da
  Selic; metade do ganho veio do mercado e das regras de saída, não do anúncio.
- Estratégia 2 — desconto com renda estável (docs/ESTUDO_DESCONTO.md): só o agressivo (preço 0,30–0,75; rendimento
  ≥ Selic + 4) foi bem: típico +12,5%, 75% com ganho. Quando sai porque a cota subiu, +10,9%, mas só 1 em 4
  operações. Caminho duro: −13% típico abaixo da entrada; −25% a −30% em 1 de cada 10.
- Relações que separam os fundos que rendem mais (docs/ESTUDO_RELACOES.md, corrigido): rendimento do mês acima do
  nível dos 6 meses anteriores (+1,51% no mês seguinte, t 8,0); rendimento alto sobre o preço (+1,37%, t 5,0);
  valor patrimonial crescendo (+0,91%, t 3,5). Tendência de 12 meses NÃO se sustentou.
- Saltos trimestrais de rendimento (docs/ESTUDO_TRIMESTRAL.md): sem vantagem clara (+0,55%, t 1,1).

### 4.5 Cobertura do rendimento (`estudos/cobertura_rendimento.py`)

Cobertura = (resultado em dinheiro − ganho com venda) ÷ rendimento declarado, do último semestre fechado mais o
trimestre seguinte, só com informes já entregues. Teste em 11.582 casos (2019–2026): abaixo de 0,90 → 27% cortaram o
rendimento em 6 meses (contra 20%); abaixo de 0,70 → 32%. Atraso: pode levar ~2 meses para mostrar um trimestre ruim.
Melhor como alerta para ler o relatório do que como bloqueio.

## 5. Proposta em aberto (não rodada): `docs/FILTRO_DESCONTADOS.md`

Queda de 10% a 25% em 6 meses; preço 0,60–0,90 do patrimônio; rendimento 2 pontos acima do tipo; constância dura
(11 de 12 meses pagos, oscilação ≤ 0,03, no máximo 1 queda de 2%); cobertura ≥ 1,0; saúde; saída por corte de mais
de 5%, doença confirmada ou preço a 0,95 do patrimônio.

## 6. Fundos elegíveis hoje na versão D, lidos nos relatórios de set/2026

| Fundo | Cobertura (CVM) | Leitura do relatório | Veredito |
|---|---|---|---|
| HABT11 | 1,00 | ganha o que distribui | pode comprar |
| RZAK11 | 0,92 | pagou 2,5% a mais do que ganhou em 2026; CRI com atraso parcial desde 05/2026 | atenção |
| SPXS11 | 0,95 | reserva caiu de R$ 627 mil para R$ 173 mil em 3 meses; CRI em renegociação | atenção |
| RBRX11 | 0,68 | ganha R$ 0,064, paga R$ 0,090 por cota; reserva quase zerada; incorporação do PSEC11 | não comprar |
| RCRB11 | 0,79 | rendimento de R$ 1,30 temporário; recorrente projetado R$ 1,17 | não comprar pelo rendimento atual |
| LIFE11 | 0,82 | receitas R$ 2,70 mi contra R$ 4,57 mi distribuídos (set/2026); rendimento já caiu de 0,120 para 0,115 | não comprar (o dono discorda em parte: paga ~23% ao ano) |

## 7. Lições aprendidas

- Regra fixada antes de rodar; nada de ajustar ao passado depois de ver o resultado.
- Toda conta de "rendimento sobre o preço" precisa comparar com o CDI/Selic líquido de imposto (rendimento de FII é isento).
- Filtros automáticos de documentos por palavras barram fundos bons (GTWR11 barrado 15 vezes; deu lucro).
- Comparar o rendimento com o do próprio tipo de fundo (papel, tijolo...) foi o que mais melhorou a carteira 2.
- Cortes de rendimento são o principal motivo das perdas na carteira 2 (5 das 7 operações ruins).
- Sinais de oportunidade chegam em ondas de crise (2020, 2021, 2024).

## 8. Programas principais

| Programa | Faz |
|---|---|
| `estudos/kairi_sinais_hoje.py` | sinais recentes do Kairi Padrão |
| `estudos/ficha_fundo.py FUNDO11 dd/mm/aaaa` | ficha de saúde de um fundo num dia |
| `estudos/renda_descontada.py` | carteira 2, versões A–H, elegíveis hoje |
| `estudos/cobertura_rendimento.py` | tabela de cobertura e teste no passado |
| `estudos/fnet_documentos_2017.py FUNDO11 ...` | baixa fatos e comunicados do FNET em tabela |
| `estudos/kairi_fnet_2026.py` | funções de coleta do FNET |
