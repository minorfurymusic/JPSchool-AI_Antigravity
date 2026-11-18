# Checklist do app de FIIs

Histórico de pendências. Atualizar a cada entrega, sem apagar o que já foi feito.

## Feito

- [x] 2026-11-09 — Repositório conferido: já estava vazio, nada apagado.
- [x] 2026-11-09 — Pesquisa de projetos parecidos e fontes oficiais (`PESQUISA.md`, commit `2e0a32c`).
- [x] 2026-11-09 — Ambiente próprio criado com acesso a `dados.cvm.gov.br`, `bvmf.bmfbovespa.com.br`, `api.bcb.gov.br`, `fnet.bmfbovespa.com.br`.
- [x] 2026-11-09 — Cabeçalhos reais da CVM (mensal e trimestral) e formato das cotações da B3 conferidos.
- [x] 2026-11-09 — Prova de ligação B3 x CVM pelo ISIN: 303 de 360 papéis casados (saída no `PLANO.md`).
- [x] 2026-11-09 — Plano escrito (`PLANO.md`, commit `085508c`).
- [x] 2026-11-09 — Erro de preço do primeiro teste explicado e corrigido no plano (arquivo mensal da B3 fora de ordem de data).
- [x] 2026-11-09 — Fechamento oficial diário da B3 conferido: disponível na noite do mesmo dia.
- [x] 2026-11-09 — Cotação com atraso da B3 conferida contra o fechamento oficial: valores iguais.
- [x] 2026-11-09 — Rendimento anunciado pelo fundo conferido no cadastro de fundos listados da B3.
- [x] 2026-11-09 — Ambiente: liberados também `cotacao.b3.com.br` e `sistemaswebb3-listados.b3.com.br`.

- [x] 2026-11-10 — Coleta completa: cotações B3 2017–2026, informes CVM 2016–2026, rendimentos anunciados de 390 códigos.
- [x] 2026-11-10 — Fase 1 (base de dados) e Fase 2 (painel em página única).
- [x] 2026-11-10 — Fase 4 (eventos, estudo do histórico, lista de oportunidades, registro de sinais).
- [x] 2026-11-10 — Fase 5, parte: venda de imóvel como evento. Vacância e contratos ficaram na base, sem tela.
- [x] 2026-11-10 — 32 testes automáticos passando.

- [x] 2026-11-10 — Estudo de relações (13 sinais, data limite, juros, bolsa): `docs/ESTUDO_RELACOES.md`.

- [x] 2026-11-11 — Erro corrigido: rendimento zero para fundos sem histórico mensal inflava os retornos. Resultados refeitos.
- [x] 2026-11-11 — Rendimentos declarados por trimestre (CVM) para todos os fundos; ganho com venda de ativos.
- [x] 2026-11-11 — Diagnóstico dos fundos sem histórico e estudo por trimestre: `docs/ESTUDO_TRIMESTRAL.md`.
- [x] 2026-11-11 — 36 testes automáticos passando.

- [x] 2026-11-11 — Estudo do caminho diário da cota depois do salto, com grupo de controle: `docs/ESTUDO_CAMINHO_DIARIO.md`.

- [x] 2026-11-11 — FNET destravado: travava com HTTP/2, funciona com HTTP/1.1, sem login. Lista, PDF, XML de rendimento e histórico desde 2017 testados (PLANO.md, seção 9).
- [x] 2026-11-11 — Decidido pelo dono: roda em computador de casa; todos os fundos; erros viram pendência reprocessável; estimativas em faixas.

- [x] 2026-11-12 — Coletor do FNET com fila de pendências e reprocessamento (commit `b510b5a`).
- [x] 2026-11-12 — Histórico de avisos de rendimento desde 2017: 35.773 avisos lidos, 40.043 rendimentos, 1 erro (arquivo vazio no FNET).
- [x] 2026-11-12 — Estudo com a data real do anúncio: `docs/ESTUDO_ANUNCIO_REAL.md`.
- [x] 2026-11-12 — Decidido pelo dono: Windows 11 Pro, rodar às 20h.

- [x] 2026-11-12 — Lista de 10.813 fatos relevantes e 14.938 comunicados desde 2017.
- [x] 2026-11-12 — Classificação por palavras e leitura da frase em que o fundo declara o efeito no rendimento (`fii/classificar.py`).
- [x] 2026-11-12 — Estudo em dias, em reais sobre cota de R$ 10: aviso de rendimento e primeira amostra de 2.969 fatos relevantes (`docs/ESTUDO_DIAS.md`).
- [x] 2026-11-11 — Fatos relevantes completos: 10.696 com texto, 111 sem texto (imagem), 6 com erro. Estudo refeito no formato novo (`docs/ESTUDO_DIAS.md`, parte 3).
- [ ] Baixar os 14.929 comunicados ao mercado (só listados).
- [ ] Ler os 111 fatos relevantes que são imagem e melhorar a leitura da declaração de efeito no rendimento (IA).
- [ ] Grade de regras de entrada e saída (alvo, limite de perda, prazo), escolhida numa parte dos anos e conferida na outra.
- [x] PDFs protegidos: biblioteca `cryptography` instalada; relidos.

- [x] 2026-11-13 — Simulação de carteira (R$ 10.000, 2026, três perfis), mesmas regras em 2018–2025 e teste de sorteio: `docs/SIMULACAO_2026.md`.
- [ ] Refazer o perfil conservador (o atual rende menos que o caixa) e rever o gatilho de aviso confirmado.
- [ ] Simulação com execução mais dura (ordem só executa se o preço passar do alvo; limite pelo volume do dia).

- [x] 2026-11-13 — Estratégia 2 (desconto com renda estável), dia a dia, três perfis: `docs/ESTUDO_DESCONTO.md`.
- [x] 2026-11-13 — Decidido pelo dono: perfil se define pela qualidade do fundo; piso de patrimônio de R$ 50, 100 e 400 milhões; ordem até 2% do volume do dia; excluir fundos em encerramento; saída da estratégia 2 pelo rendimento encostar na Selic.
- [ ] Estratégia 3 (inquilino inadimplente que se recupera, caso SPTW11): pendência registrada pelo dono, sem estudo.
- [ ] Nota de qualidade dos fundos e nova simulação da estratégia 1 com filtros de armadilha.

- [x] 2026-11-13 — Perfil conservador como base: queda com rendimento mantido, vender só no corte, compra em data fixa; pesquisa na internet por três agentes: `docs/ESTUDO_CONSERVADOR.md`.
- [x] 2026-11-13 — Estratégias separadas num documento só, com glossário (queda = preço, corte = rendimento): `docs/ESTRATEGIAS.md`.
- [ ] Estratégia 1: medir 120 e 250 pregões depois do anúncio (o exemplo original do dono); ler duração e tamanho do aumento.
- [x] 2026-11-13 — `docs/ESTRATEGIAS.md` refeito: termos entrada/saída, regras rodadas e quadro padrão em cada estratégia.
- [ ] Rodar de novo as estratégias 1, 2 e o conservador no quadro padrão (entradas, saídas, em aberto, pregões, valorização, rendimento, Selic líquida, custos e imposto).
- [x] 2026-11-13 — Estratégia 1 medida da entrada até a saída (saída quando o rendimento cai), no formato pedido pelo dono: `estudos/anuncio_saida.py`, `docs/ESTRATEGIAS.md`.
- [x] 2026-11-13 — Decidido pelo dono: execução de estudos por agentes auxiliares (modelo menor); preço em D+5/D+10/D+20 sai do documento; resultados em média, separando cota em alta e em queda.
- [x] 2026-11-13 — Estratégia 1 separada em moderado e agressivo, com em aberto na mesma tabela e fundos que saíram da bolsa corrigidos (`docs/ESTRATEGIAS.md`, Estudo 1.1b).
- [x] 2026-11-13 — Decidido pelo dono: agressivo = cota de 30% a 75% do valor patrimonial, patrimônio de R$ 50 milhões ou mais; moderado começa em 60%; usar sempre o preço sobre valor patrimonial do fundo, sem ajuste pela média do mercado. Tabela do agressivo em `docs/ESTRATEGIAS.md` (Estudo 1.1c).
- [x] 2026-11-14 — Decidido pelo dono: foco na Estratégia 1 (gatilho de aumento) para moderado e agressivo; régua de rendimento igual para os dois (Selic líquida + 3 pontos); o que separa os perfis é só o preço sobre valor patrimonial; declaração de redução vale só como saída. Tabela em `docs/ESTRATEGIAS.md` (Estudo 1.1d).
- [x] 2026-11-14 — Corrigido: piso fixo de R$ 200 mil por dia trocado pela regra do dono (ordem até 2% do negociado por dia); estudo por faixa de ordem de R$ 200 em R$ 200 (`docs/ESTRATEGIAS.md`, Estudo 1.1e).
- [x] 2026-11-14 — Banco em planilhas, 2017 a 2026, na pasta `planilhas/` (preços por ano, mercado, rendimentos, anúncios, LEIA-ME); gerado por `estudos/planilhas.py`. Pedido do dono, para analisar ano a ano sem reler os dados brutos.
- [x] 2026-11-16 — Estudo Agressivo: por faixa e tipo de fundo, mercado e Selic, análise gráfica, data do dividendo; planilha de operações no final (`docs/ESTUDO_AGRESSIVO.md`, `planilhas/estudo_agressivo.csv`, `planilhas/fundos.csv`). XPPR11 fora por decisão do dono.
- [x] 2026-11-16 — Caminho da cota dia a dia depois da entrada (subiu ou caiu primeiro, picos, fundos, alvo fixo): `docs/ESTUDO_AGRESSIVO.md`, Pergunta 5; `estudos/caminho_agressivo.py`.
- [x] 2026-11-16 — Busca de modelo com período de escolha (até 2022) e de conferência (2023 em diante): nenhum modelo ganhou da Selic líquida na conferência (`docs/BUSCA_MODELO.md`).
- [x] 2026-11-16 — Índice de Kairi (ideia do dono): primeiro gatilho acima da Selic líquida na escolha e na conferência (média de 200 pregões, 15% a 20% abaixo, rendimento mantido). Ganho concentrado em 2020 e 2024 (`docs/ESTUDO_KAIRI.md`).
- [x] 2026-11-16 — Kairi: regras expandidas (40 vizinhas, cortes, saídas, entradas, perdas grandes) e carteira de R$ 10.000 com dinheiro limitado, 9 simulações (`docs/ESTUDO_KAIRI.md`, partes 2 e 3).
- [x] 2026-11-16 — Kairi com carteira infinita, balanço ano a ano em reais, 12 regras de saída (Fibonacci e projeções), imposto com abatimento, preço sobre valor patrimonial na entrada e na saída, análise dos cortes de rendimento (`docs/ESTUDO_KAIRI.md`, parte 4; planilhas `kairi_ordens.csv`, `kairi_ordens_saidas.csv`, `kairi_cortes.csv`).
- [x] 2026-11-16 — Kairi: saída em escada (10 variações, ideia do dono). Nenhuma superou a volta à média nos dois períodos (`docs/ESTUDO_KAIRI.md`, parte 5; `planilhas/kairi_escada.csv`).
- [x] 2026-11-16 — Kairi: saída pelo cruzamento das médias de 7 e 21 pregões (9 variações, ideia do dono). Nenhuma superou a volta à média (`docs/ESTUDO_KAIRI.md`, parte 6). Total de 31 saídas alternativas testadas, nenhuma melhor nos dois períodos.
- [x] 2026-11-17 — Decidido pelo dono: régua passa a ser 105% do CDI em liquidez diária, com os impostos.
- [x] 2026-11-17 — Preparação da auditoria: CDI diário, datas de pagamento dos rendimentos, amortizações e textos dos fatos relevantes exportados para `planilhas/` (`docs/AUDITORIA_PEDIDO.md`).
- [x] 2026-11-17 — Auditoria do Kairi rodada em três blocos por agentes auxiliares, contra 105% do CDI com impostos: tabela mestra e lacunas em `docs/AUDITORIA_KAIRI.md`; programas `estudos/auditoria_bloco1.py`, `auditoria_bloco2.py`, `auditoria_bloco3.py`; planilhas `planilhas/auditoria_bloco*_*.csv`. Resultado: ganha do CDI (carteira do pico 10,2% a 11,1% ao ano contra 8,6%), mas sem prova contra sorte (IC inclui zero; 24 episódios na A; conferência 2023–2026 quase igual ao CDI). Gatilho maior, virada e duas partes pioram; fato negativo antes da queda não fez diferença.
- [ ] Decisão do dono sobre o resultado da auditoria (`docs/AUDITORIA_KAIRI.md`).
- [x] 2026-11-17 — Planilha com gráficos dos gatilhos 10/15/20/30% (`planilhas/kairi_gatilhos.xlsx`, `estudos/kairi_gatilhos_planilha.py`).
- [x] 2026-11-17 — Simulação de R$ 20 mil em 2026 (R$ 10 mil no gatilho de 20% e R$ 10 mil no de 15%, ordens de R$ 1.000): 2,7% líquido contra 10,0% do 105% do CDI (`docs/SIMULACAO_KAIRI_2026.md`, `planilhas/kairi_carteira_2026.xlsx`).
- [x] 2026-11-17 — Simulação 2026, versão 2: regra de não comprar fundo que vai sair da bolsa (fatos relevantes de 12 meses), conservadora só com volume ≥ R$ 500 mil/dia, aba de posições abertas. Total 3,7% líquido contra 10,0% do CDI (`docs/SIMULACAO_KAIRI_2026.md`).
- [x] 2026-11-17 — Simulação 2026, versão 3: 4 carteiras de R$ 10 mil por faixa de negociação típica (mediana de 60 dias), venda pelo fechamento, documentos do FNET (rendimento zero barra compra; aviso de saída vende). Total 8,7% líquido contra 10,0% do CDI; 94% do dinheiro ficou parado (`docs/SIMULACAO_KAIRI_2026.md`).
- [x] 2026-11-17 — As 4 carteiras da versão 3 rodadas de 2018 a 2025 (ano a ano) e contínua 2018–2026: ganhou do CDI em 7 de 9 anos; contínua R$ 40 mil → R$ 102.944 contra R$ 83.115 do CDI; 69% do ganho veio do dinheiro parado (`docs/SIMULACAO_KAIRI_ANOS.md`). Sem documentos do FNET antes de 05/2025.
- [x] 2026-11-17 — Carteira de R$ 10 mil com um fundo de cada vez (C1 25% + C2 20% ou 15%), segurar com segunda entrada e troca com lucro: nenhuma troca aconteceu; C2 20% R$ 19.484, C2 15% R$ 21.442, CDI R$ 20.780; queda de até −49% no caminho (`estudos/kairi_um_fundo.py`, `planilhas/kairi_um_fundo.xlsx`).
- [x] 2026-11-17 — Skill "avaliar-fundo" (`.claude/skills/avaliar-fundo/SKILL.md`, `estudos/saude_fundo.py`, `estudos/ficha_fundo.py`) e carteira de um fundo só com a avaliação, ano a ano (`estudos/kairi_ano_a_ano_skill.py`): C2 20% R$ 35.797, C2 15% R$ 24.652, CDI R$ 20.779.
- [x] 2026-11-17 — Corrigido: na carteira de um fundo só os rendimentos pagos durante a operação só entravam no fim; agora entram no caixa no dia do pagamento (números de `planilhas/kairi_um_fundo.xlsx` refeitos).
- [x] 2026-11-17 — Validação da avaliação de saúde e contagem de oportunidades por configuração; carteira dividida em 1, 2 e 5 partes (`estudos/kairi_oportunidades.py`, `planilhas/kairi_oportunidades.xlsx`). Melhor: atual (C1 25% + C2 20%) com ordem de R$ 5 mil, R$ 32.103, queda máxima −9%; mas só 3 de 9 anos com 3+ oportunidades.
- [x] 2026-11-17 — Skill "kairi-padrao" com o molde fechado (`.claude/skills/kairi-padrao/SKILL.md`) e programa dos sinais recentes (`estudos/kairi_sinais_hoje.py`).
- [ ] Kairi Padrão: acompanhar daqui para a frente, sinal a sinal, anotando o veredito antes do resultado.
- [x] 2026-11-17 — Estratégia "renda descontada saudável" (rendimento >= CDI + 1, preço 0,60–0,85 do patrimônio, rendimento constante, avaliação de saúde, 5 fundos): três variantes, todas abaixo do CDI (R$ 13,8 mil a R$ 16,0 mil contra R$ 20,8 mil) (`estudos/renda_descontada.py`, `planilhas/renda_descontada.xlsx`).
- [x] 2026-11-17 — Renda descontada: fase da Selic, saídas corrigidas e rendimento comparado ao tipo de fundo. Melhor versão (D: saídas corrigidas + rendimento acima da mediana do tipo) empatou com o CDI (R$ 20.810 contra R$ 20.779), queda máxima −10,9%. Não comprar com a Selic subindo não ajudou (`estudos/renda_descontada.py`).
- [x] 2026-11-17 — Cobertura do rendimento (resultado em dinheiro ÷ rendimento declarado, informe trimestral da CVM, 818 fundos, 2017–2026; `estudos/cobertura_rendimento.py`, `planilhas/tecnico/cobertura_trimestral.csv`). Teste no passado (11.582 casos): cobertura < 0,90 → 27% cortaram o rendimento em 6 meses contra 20%; < 0,70 → 32% (`planilhas/cobertura_teste_faixas.csv`). Sinal real, mas moderado. Usado o informe trimestral no lugar do relatório gerencial em PDF (formato diferente por gestora); a reserva de lucros só existe no relatório.
- [x] 2026-11-17 — FNET 2017–2026 dos 30 fundos candidatos da renda descontada: 1.746 fatos relevantes e comunicados ao mercado com texto completo, em tabela (`planilhas/tecnico/fnet_2017_documentos.csv.gz`, `estudos/fnet_documentos_2017.py`). 28 são PDF só de imagem, sem texto.
- [x] 2026-11-17 — Renda descontada com filtros novos (regras fixadas antes de rodar): F cobertura >= 0,90 R$ 19.731; G sem documento negativo em 12 meses R$ 18.344; H os dois R$ 19.449. Todas abaixo da D (R$ 20.810) e do CDI (R$ 20.779). Das 7 operações ruins da D, G e H evitaram XPCM11, BLMR11, KORE11 e VRTM11, mas compraram FIGS11, TOPP11 e LIFE11 e barraram fundos que deram lucro (ex.: GTWR11, 15 vezes). Aba "7 operações ruins" em `planilhas/renda_descontada.xlsx`. Carteira 2 continua NÃO aprovada.
- [x] 2026-11-17 — Leitura dos relatórios de set/2026 dos elegíveis de hoje, em tabela (`planilhas/renda_descontada_elegiveis_hoje.csv`, `planilhas/renda_descontada_relatorios_set2026.csv`, textos em `planilhas/tecnico/relatorios_gerenciais_set2026.csv.gz`): HABT11 pode comprar; RZAK11 e SPXS11 atenção; RBRX11, RCRB11 e LIFE11 não comprar.
- [ ] OBJETIVO ATUAL (dono, 18/11/2026): filtro para o momento de mercado de agora: fundos com queda significativa, mas sem a crise de desespero do Kairi; descontados, saudáveis, rendimento constante (de preferência sempre o mesmo valor, zero oscilação) e que paguem bem. Expectativa do dono: juros começam a cair em 2027 e terminam o ano abaixo de 10%. Kairi fica de lado, mas avisar o dono quando algo descoberto servir para a Skill `kairi-padrao`.
- [x] 2026-11-18 — Boletim Focus (expectativa da Selic) 2017–13/11/2026 em tabela, sem buracos: `planilhas/focus_selic_fim_de_ano.csv`, `planilhas/focus_selic_reuniao.csv` (`estudos/focus.py`; liberado olinda.bcb.gov.br no ambiente). Em 13/11/2026 a mediana para o fim de 2027 é 12,75% (mínimo 10,25%); abaixo de 10% só aparece para 2030.
- [ ] REGRA DO DONO (18/11/2026): o dono lê tabelas; toda informação tem de virar tabela completa e sem falha de extração. Pendente: 28 documentos do FNET em PDF só com imagem, sem texto (precisa de leitura por imagem).
- [ ] REGRA DO DONO (18/11/2026): o modelo do Kairi Padrão está certo; só acrescentar informações e funções à Skill.
- [x] 2026-11-18 — Classe de cada fundo pela carteira (informe mensal da CVM, 2017–2026): `planilhas/classificacao_carteira_mensal.csv` (`estudos/classificacao_carteira.py`). Antes, 338 de 524 fundos eram "Outros". Cobertura: 96% a 100% dos fundos negociados por ano.
- [x] 2026-11-18 — Correções do valor patrimonial (94 saltos em 69 fundos: 9 erros que voltam, 11 desdobramentos não ajustados, 9 valores absurdos, 65 mantidos para conferir): `planilhas/tecnico/valor_patrimonial_correcoes.csv` (`estudos/vp_correcoes.py`). NÃO aplicado às tabelas de preços.
- [ ] DECISÃO DO DONO: aplicar as correções do valor patrimonial às tabelas `planilhas/precos_AAAA.csv` (muda o Kairi e os outros estudos) ou só usar nos estudos novos.
- [ ] Conferir os 65 saltos de valor patrimonial mantidos (tipo D em `valor_patrimonial_correcoes.csv`).
- [x] 2026-11-18 — Tipo 1 (descontado saudável), Skill `descontado-saudavel`: regras fixadas antes; 3 operações em 2018–2026, R$ 18.860 contra R$ 20.779 do CDI; nenhum fundo hoje. NÃO validado: filtro quase não dispara (a constância elimina quase tudo).
- [x] 2026-11-18 — Tipo 1 versão 2 (corte só no essencial + nota): 152 operações, R$ 13.642 contra R$ 20.779 do CDI, queda máxima −37%. Pior que a v1. Corrigido erro na nota (fundo sem medida levava nota máxima).
- [x] 2026-11-18 — CORREÇÃO DE ROTA DO DONO: o Tipo 1 é TRADE (comprar, receber rendimento, vender com +10% a +15%), não carteira parada nem comparação no período todo. Estudo por operação: `estudos/descontado_trade.py`, `planilhas/descontado_trade.xlsx`. Alvo +10%: 61% chegam (mediana 76 pregões); as 39% que não chegam terminam o ano em −8,3% em média. Alvo +15%: 53% chegam (mediana 114 pregões).
- [x] 2026-11-18 — Tipo 1 trade, 2 compras × 8 vendas (`estudos/descontado_saidas.py`, `planilhas/descontado_saidas.xlsx`): melhor venda = média de 21 cruzando abaixo da de 70 (0,79% por mês aplicado contra 0,66% do CDI; só 6% das operações perdem mais de 10%). Alvo +10%: 0,47% por mês (as que travam seguram o dinheiro 1 ano). Banda superior de Bollinger: negativa. Comprar na banda inferior piorou todas as vendas.
- [x] 2026-11-18 — Tipo 1 trade, caminho de cada operação por venda (`estudos/descontado_caminho.py`, `planilhas/descontado_caminho.xlsx`): 85%–91% caem depois da compra (queda média de 7% a 11%; pior momento entre 23 e 73 pregões). Prejuízo maior com Selic CAINDO (41%–56%) do que parada (10%–32%); menor em Papel e Híbrido; perdedoras compraram com menos desconto e depois de queda menor. Abaixo de −5% com 20 pregões: 64%–91% terminam no prejuízo. Cortes de proteção (zero a zero, protege metade, tempo) não melhoraram o ganho por mês aplicado.
- [x] 2026-11-18 — Tipo 1 trade por classe de fundo, contas corrigidas (rendimento pela data-com, 20% de IR sobre ganho na cota): só Papel ganha do CDI do mesmo período (7 de 8 vendas; alvo +10%: 93% com lucro, +0,37 ponto/mês). Tijolo perde em todas. `estudos/descontado_classes.py`, `planilhas/descontado_classes.xlsx`. Registro consolidado: `docs/TIPO1_TRADE.md`.
- [x] 2026-11-18 — Quadro mensal do país (Selic, IPCA, dólar, dívida bruta, déficit primário, Focus): `planilhas/macro_mensal.csv` (`estudos/macro_mensal.py`). Tipo 1 trade por período e cenário: `estudos/descontado_periodos.py`, `planilhas/descontado_periodos.xlsx`. Papel positivo em todos os cenários (melhor com Selic esperada estável: +1,03 ponto/mês; pior com queda forte esperada: +0,14); Tijolo negativo em todos; dívida subindo piora tudo.
- [x] 2026-11-18 — Skill `papel-padrao` (trade em fundos de Papel: sinal no fim do mês, venda com +10%, prazo de 1 ano) e programa `estudos/papel_padrao.py` (sinais, prévia do mês, cenário do país, posições do dono em `planilhas/papel_padrao_posicoes.csv`). Sinal de 30/10/2026: HABT11, SAPI11, RZAK11, SPXS11, CLIN11. Skill `descontado-saudavel` virou registro de pesquisa.
- [x] 2026-11-18 — Base de preços atualizada até 17/11/2026 pelo COTAHIST da B3 (`estudos/atualizar_precos.py`; mercado e CDI: `estudos/atualizar_mercado_cdi.py`). 18/11 ainda não publicado. Rendimentos anunciados depois de 06/11 não entram por esse caminho.
- [x] 2026-11-18 — CORRIGIDO o erro de ligação abaixo: a classe pela carteira usa um CNPJ principal por começo de ISIN (o de maior carteira no próprio último informe). Papel Padrão refeito: 114 operações, 93,9% com lucro, +0,42 ponto/mês (antes 117, 93,2%, +0,38).
- [x] (histórico) ERRO DE LIGAÇÃO: na CVM, 37 começos de ISIN aparecem em mais de um CNPJ em 2026 (ex.: TRXF = TRX Real Estate e Liquidez Projetos GD; XPML = XP Malls e Península). A classe pela carteira e a cobertura ligam pelo começo do ISIN e podem pegar o fundo errado. Negociados na base afetados: HSAF11, IRIM11, JPPA11, URPR11, VRTA11. Corrigir escolhendo o CNPJ certo (o de maior patrimônio ou o do cadastro da B3).
- [x] 2026-11-18 — Skill `analise-grafica` e página "Radar Gráfico de FIIs" (https://claude.ai/artifact/Mz1Yee5tDKbspNpt42u8yX; fonte `radar/radar_grafico.html`; motor `estudos/analise_grafica.py`): 13 itens (suportes, médias, IFR, MACD, estocástico, Bollinger, candles, volume, volume por faixa, Fibonacci, força relativa, zonas de liquidez, Elliott) + fundamentos, 298 fundos. Preços da B3 2019–2026 só de FII em `planilhas/tecnico/b3_cotahist_fii_2019_2026.csv.gz`.
- [ ] Radar Gráfico: rotina para atualizar os dados e republicar (hoje é manual, ver a Skill).
- [x] 2026-11-18 — TRXF11: sinal C2 do Kairi pelo preço em 20/08/2026 (compra 21/08 a R$ 73,44; −26% em 17/11). Leitura de 59 documentos do FNET (08–11/2026, `planilhas/tecnico/fnet_trxf11_2026.csv.gz`): rendimento R$ 0,93 estável, mas pago com reserva em out/26; 27,9 mi cotas (29% do fundo) entregues a vendedores de imóveis na 13ª emissão, 82% ainda com eles; ajuste de preço de ~10% previsto; dívida de R$ 4,6 bi (32% do ativo, metade no CDI). Veredito: ATENÇÃO, não comprar por enquanto.
- [ ] TRXF11: conferir no relatório gerencial de nov/2026 (sai no começo de dez) quantas cotas os vendedores de imóveis ainda têm (eram 23,0 mi em 30/10) e se o rendimento de R$ 0,93 foi pago sem usar reserva. Estimativa de 18/11 pelo volume da B3: vendiam ~234 mil cotas/pregão em out (confere com o oficial) e o excesso de volume subiu para ~550 mil/pregão em nov; nesse ritmo, a venda acabaria entre jan e abr/2027.
- [x] 2026-11-18 — Análise dos 14 fundos da lista do Luis Hack (`estudos/analise_fundos.py`, `planilhas/analise_fundos_2026-11-18.csv`).
- [ ] PRIORIDADE: 63 fundos negociados na B3 nunca entraram na base (ex.: XPML11, TRXF11, BTCI11, PSEC11, HCTR11, PMLL11). Montar o histórico deles desde 2017 (preços, rendimentos, patrimônio) — afeta Kairi e Papel Padrão.
- [ ] DECISÃO DO DONO: o programa do Kairi (`estudos/kairi_carteira_anos.py`, usado por `kairi_sinais_hoje.py`) tem uma conferência presa aos dados até 09/11/2026 (2026 = R$ 43.500,62) e PARA com dados mais novos. Proposta: rodar essa conferência só quando a base terminar em 09/11/2026. Os estudos novos usam a cópia da regra de bloqueio em `estudos/bloqueio_saida.py`.
- [x] 2026-11-18 — Papel Padrão: os 30 primeiros pregões depois do sinal (`estudos/papel_30dias.py`, `planilhas/papel_30dias.xlsx`, `docs/TIPO1_TRADE.md` seção 10): só 17% caem mais de 5% em 30 pregões (30%–36% em 2024 e 2026); a queda acompanha o mercado de fundos; esperar cair 3/5/8% perde os sinais que sobem direto.
- [x] 2026-11-18 — Papel Padrão com análise gráfica (6 confirmações de compra e 6 de venda: candles, suporte/resistência, IFR, estocástico, MACD, volume), `estudos/papel_tecnico.py`: não superou a regra atual nos dois períodos; a venda gráfica faz trades curtos (~2–3 meses) com 97% de acerto mas ganho pequeno. Indicador para TradingView não feito (só valeria se ganhasse).
- [x] 2026-11-18 — Papel Padrão: gatilho em dois passos (cair 3%/5% desde o sinal, com ou sem repique) testado: não melhorou (ganho total menor; mesmo depois de cair 5%, caiu mais 8% em média).
- [ ] Kairi: medir o resultado por classe de fundo (Papel, Tijolo...) com a classificação nova (só informação, sem mudar regra).
- [x] 2026-11-18 — Papel Padrão: 5 formas de comprar (`estudos/papel_entradas.py`). A regra atual (abertura seguinte) ganhou mais no total; duas partes rende um pouco mais por mês aplicado; 9.1, IFR 2 e reversão pioraram.
- [x] 2026-11-18 — ERRO DE DADOS achado: 77 avisos de rendimento maiores que 10% do preço; 25 suspeitos (ex.: VCRI11 R$ 36,85 numa cota de R$ 6), 33 sem preço depois, 19 prováveis reais. `planilhas/tecnico/rendimentos_suspeitos.csv` (`estudos/rendimentos_suspeitos.py`). Ignorados só no estudo de entradas; nos estudos anteriores do Papel com alvo +10% não houve contaminação (maior resultado +11,6%).
- [ ] Dono conferir os 25 avisos suspeitos e os 33 sem preço depois; decidir se corrige a tabela de rendimentos (afeta todos os estudos e o Kairi).
- [ ] Tipo 1 trade: testar formas de compra que esperam a virada (setup 9.1, IFR, cruzamento para cima, rompimento) — a maioria cai depois da compra.
- [ ] Tipo 1 trade: descobrir o que separa as operações que chegam ao alvo das que não chegam (para filtrar melhor) e testar regra para as que travam.
- [ ] Renda descontada: os filtros novos não ajudaram. Decisão do dono: abandonar a carteira 2, seguir só com o Kairi Padrão, ou testar outra ideia.
- [ ] Baixar os fatos e comunicados de 2017–2025 dos fundos com sinal do Kairi (209 fundos; ~1 h a cada 30 fundos).
- [ ] Conferir a queda geral de 26/10/2026 em outra fonte (o dono informou: segundo turno das eleições em 25/10/2026; a base mostra −5,3% no mercado de fundos em 26/10, coerente).
- [ ] Regra de saída da bolsa: decidir se bloqueia só saída aprovada ou também proposta (5 de 18 bloqueios de 2026 foram propostas que não viraram saída até 09/11).
- [ ] Conferir em outra fonte a queda geral de 26/10/2026 a 03/11/2026 nos preços (153 de 221 fundos caíram mais de 3% em 26/10).
- [ ] Melhorar a classificação dos fatos relevantes (amostra lida: 10 de 20 negativos e 7 de 20 positivos errados).
- [ ] Dono ler `planilhas/kairi_cortes.csv` e avaliar o motivo de cada corte de rendimento.
- [ ] Limpar a base de preços: 334 variações de mais de 25% num dia em 128 fundos; conferir TORD11 (último preço R$ 0,97).
- [ ] Kairi: colocar o sinal diário no app e acompanhar daqui para a frente, sem dinheiro de verdade.
- [ ] Conferir a série de preços do BRIM11 em outra fonte; MCEM11 sem negócio.
- [ ] PRSV11 tem buraco de 7 meses nos preços (21/07/2020 a 17/02/2021).
- [ ] ERRO DE DADOS: CARE11 salta de R$ 3,53 (17/08/2021) para R$ 12,63 (14/03/2022) sem ajuste, com buraco no meio; corrigir nas planilhas e procurar outros saltos (CACR11 em 04/05/2026 a conferir).
- [ ] Decisão do dono sobre os 4 caminhos de `docs/BUSCA_MODELO.md`.
- [ ] Testar saída por alvo fixo com rendimento, imposto, Selic e regra para as que não executam.
- [ ] Decisão do dono sobre os 6 testes propostos em `docs/ESTUDO_AGRESSIVO.md`.
- [ ] Investigar: 3 operações sem rendimento em 252 pregões (ALMI11, TRNT11) e 5 com sinal diferente entre as duas medidas de valorização.
- [ ] Passar os estudos a ler de `planilhas/` em vez de `dados/`.
- [ ] Saída por declaração de redução ainda usa a lista com piso de R$ 200 mil; trocar para a lista sem piso.
- [ ] Decisão do dono: manter ou tirar a régua de rendimento na Estratégia 1 (piorou o resultado em dois estudos).
- [ ] Decisão do dono: a faixa de 0,60 a 0,75 é do agressivo ou do moderado.
- [ ] Estratégia 2: tirar a trava de entrada por declaração de redução (decisão do dono), quando voltar a ela.
- [ ] Ideia do dono a testar: em fundos muito descontados (0,30 a 0,40), saída em valor fixo (ex.: +7%) e regra de retorno depois de queda.
- [ ] Conferir a saída "fundo saiu da bolsa" (pode pegar trecho de preço descartado).
- [ ] Estratégia 2: saída em anúncios muito sérios (pendência do dono, levantar dados).
- [ ] Dono rever o perfil conservador (seção final de `docs/ESTRATEGIAS.md`).
- [ ] Decisão do dono sobre as 7 mudanças propostas em `docs/ESTUDO_CONSERVADOR.md`.
- [ ] Separar fundo de papel de fundo de imóveis nos estudos.
- [ ] Refazer a estratégia 2 com a Selic líquida como régua.

## Pendente: decisões do dono

- [x] Onde usar: computador de casa (Windows 11 Pro), rodando às 20h.
- [x] 2026-11-13 — Régua do rendimento: Selic líquida de imposto.
- [ ] Carteira: repositório privado ou dado só no aparelho.
- [ ] IA paga para ler PDFs (só na Fase 6).
- [ ] Seguir neste repositório ou criar outro.

## Pendente: verificação

- [x] FNET: causa achada (HTTP/2). Resolvido.
- [ ] FNET: confirmar fuso da hora de entrega e limite de requisições.
- [ ] Medir o atraso real da cotação com atraso, com o pregão aberto.
- [ ] Lista geral de fundos no cadastro da B3 voltou vazia; achar a consulta certa (a consulta por fundo funciona).
- [ ] Escolher as séries do Banco Central (Selic, CDI, IPCA) e conferir o formato da resposta.
- [ ] Conferir o dicionário de dados da CVM (`META/meta_inf_mensal_fii.zip`) para o significado exato de cada coluna.
- [x] Papéis que não casaram pelo ISIN: parte trocou de ISIN ou de CNPJ na CVM. Com todo o histórico de ISINs, 524 papéis ligados e 237 sem vínculo (a maioria recibos e direitos; 67 fundos ativos de final 11).
- [ ] Ler o motivo do salto (comunicado do fundo). Depende do FNET ou de outra fonte.
- [x] Fundos sem histórico mensal: resolvido para retorno e para estudo trimestral com o informe trimestral da CVM. Para salto mensal, 67 fundos ativos seguem só com os meses da B3 (o histórico cresce sozinho a cada mês).
- [ ] Conferir a rotina diária num dia com pregão novo (arquivo diário da B3).

- [ ] Testar juro longo (títulos do Tesouro): falta liberar a fonte.
- [ ] Medir expectativa em eleições: sem fonte de dado.

## Pendente: construção

- [x] Coletor do FNET (lista diária, download, guarda do original).
- [ ] Leitura: XML de rendimento direto; PDF com IA (chave Gemini do dono, pelo formulário seguro).
- [x] Fila de pendências com reprocessamento em lote ou um a um (por comando).
- [ ] Tela de pendências no painel, com resultado por documento.
- [ ] Usar os rendimentos do FNET como fonte principal do app (hoje o painel ainda usa CVM e B3).
- [ ] Listar todas as categorias do FNET desde 2017 para ligar cada salto ao fato relevante do mesmo período.
- [x] Carga do histórico de avisos de rendimento desde 2017 (datas reais de anúncio).
- [ ] Instalação nos computadores de casa: disparo em horários definidos e retomada depois de queda de luz.

- [ ] Mostrar no painel, para cada oportunidade, o pico e o fundo desde a entrada e o que casos parecidos fizeram dia a dia.
- [ ] Refazer o estudo do caminho com a data real do anúncio (só existe para os últimos ~12 meses, na B3).

- [ ] Levar para o painel a nota combinada dos 3 sinais que passaram no estudo corrigido (a tendência de 12 meses caiu).
- [ ] Separar, em cada fundo, o que foi movimento do mercado do que foi do fundo.
- [ ] Ler comunicados com IA (o dono tem chave Gemini; pedir pelo formulário seguro, nunca no chat).

- [x] Fase 1: base de dados (CVM mensal, cotações B3, ligação, indicadores).
- [x] Fase 2: painel (lista com filtros, página do fundo). Comparação lado a lado não feita.
- [ ] Fase 3: minha carteira.
- [x] Fase 4: sinais e indicação. Falta: comparação com Selic/CDI/IPCA e registrar a decisão do dono em cada sinal.
- [ ] Fase 5: imóveis e contratos (trimestral). Feito só o evento de venda de imóvel.
- [ ] Fase 6: documentos (FNET e IA).
- [ ] Fase 7: atualização e avisos automáticos.
