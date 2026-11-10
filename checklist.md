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

## Pendente: decisões do dono

- [ ] Onde usar: só computador ou endereço na internet.
- [ ] Carteira: repositório privado ou dado só no aparelho.
- [ ] IA paga para ler PDFs (só na Fase 6).
- [ ] Seguir neste repositório ou criar outro.

## Pendente: verificação

- [ ] FNET: tempo esgotado em 2 tentativas. Causa não confirmada. Testar de fora deste ambiente antes de concluir.
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
