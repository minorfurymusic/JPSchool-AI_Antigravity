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

## Pendente: decisões do dono

- [ ] Onde usar: só computador ou endereço na internet.
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
