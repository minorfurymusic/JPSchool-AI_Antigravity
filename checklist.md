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
- [ ] Entender os 57 papéis que não casaram pelo ISIN.

## Pendente: construção

- [ ] Fase 1: base de dados (CVM mensal, cotações B3, ligação, indicadores).
- [ ] Fase 2: painel (lista com filtros, página do fundo, comparação).
- [ ] Fase 3: minha carteira.
- [ ] Fase 4: sinais e indicação.
- [ ] Fase 5: imóveis e contratos (trimestral).
- [ ] Fase 6: documentos (FNET e IA).
- [ ] Fase 7: atualização e avisos automáticos.
