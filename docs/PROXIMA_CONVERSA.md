# Prompt para a próxima conversa (preparado em 17/11/2026)

Copiar e colar o bloco abaixo no início da próxima conversa.

---

Continuação do projeto de fundos imobiliários (repositório minorfurymusic/JPSchool-AI_Antigravity, branch
`claude/auditoria-pedido-ci6sd5`). Antes de tudo: confirme `git remote -v`, `git log --oneline -10` e `git status`;
o último commit da conversa anterior foi `32c77e5`. Leia `checklist.md` (seção "Feito" do fim, de 17/11/2026) e as
duas Skills: `.claude/skills/kairi-padrao/SKILL.md` e `.claude/skills/avaliar-fundo/SKILL.md`. Trate o resumo abaixo
como hipótese a conferir nos arquivos, não como fato.

## Onde paramos

**Carteira 1 — Kairi Padrão (R$ 10 mil), molde fechado:** C1 = cota 25% abaixo da média de 200 pregões em fundo com
negociação típica (mediana de 60 pregões) de R$ 500 mil a R$ 1 mi/dia; C2 = 20% abaixo em fundo acima de R$ 1 mi/dia;
avaliação de saúde antes da compra; compra na abertura seguinte; venda no fechamento acima da média; dinheiro em 2 a 5
partes; resto em 105% do CDI. Referência 2018–2026: 41 oportunidades, 39 de 40 com lucro, +24,7% por operação; R$ 10 mil
→ R$ 32.103 com ordens de R$ 5 mil (queda máxima −9%), contra R$ 20.779 do CDI. Oportunidades vêm em ondas de crise
(2020, 2021, 2024); anos como 2019 e 2022 sem nenhuma. Sinais recentes: `estudos/kairi_sinais_hoje.py`.

**Carteira 2 — Renda descontada saudável (R$ 10 mil), ainda não aprovada:** fundos com rendimento alto e desconto.
Melhor versão até agora (D, em `estudos/renda_descontada.py`): rendimento 2 pontos acima da mediana do próprio tipo de
fundo, preço de 0,60 a 0,85 do patrimônio, rendimento constante, patrimônio por cota estável, avaliação de saúde,
5 fundos, venda só com doença confirmada em 2 meses ou preço a 0,95 do patrimônio. Resultado: R$ 20.810 contra
R$ 20.779 do CDI (empate), queda máxima −10,9%, 13 operações, 69% com lucro. Das 7 operações abaixo do CDI, 5 foram
problema do próprio fundo (corte de rendimento ou patrimônio caindo); XPCM11 e LIFE11 eram evitáveis lendo os
documentos; VRTM11 talvez. Não comprar com a Selic subindo NÃO ajudou.

**LIFE11:** não comprar. Relatório gerencial de set/2026 (FNET, publicado em 12/11/2026): receitas R$ 2,70 mi e despesas
R$ 0,34 mi no mês contra R$ 4,57 mi distribuídos; reserva de lucros caindo; FIDC investido subiu 281% num dia sem
explicação (03/06/2026). Cota a R$ 5,91 em 17/11/2026.

**Queda de 26/10/2026:** real; o dono informou que foi o segundo turno das eleições (25/10/2026). A base mostra −5,3% no
mercado de fundos no dia seguinte e −8,9% em um mês.

## O que fazer agora (com créditos para baixar dados)

1. Baixar do FNET (fnet.bmfbovespa.com.br, liberado; ver `estudos/kairi_fnet_2026.py`) os relatórios gerenciais e os
   informes mensais estruturados de 2018 a 2026 dos fundos candidatos da renda descontada (os que passaram nos filtros
   da versão D em algum mês) e dos sinais do Kairi Padrão.
2. Medir a **cobertura do rendimento**: resultado em dinheiro do mês (receitas − despesas, sem correção monetária nem
   apreciação de ativo) dividido pelo rendimento distribuído; e a evolução da reserva de lucros. Testar no passado se
   cobertura baixa antecipa corte de rendimento e queda da cota.
3. Refazer a versão D com dois filtros novos: (a) cobertura do rendimento; (b) não comprar fundo com documento negativo
   nos 12 meses anteriores. Ver quantas das 7 operações ruins somem (FIGS11, XPCM11, BLMR11, KORE11, TOPP11, VRTM11,
   LIFE11) e se a carteira passa a ganhar do CDI. Fixar as regras ANTES de rodar, para não ajustar ao passado.
4. Ler os documentos (Skill `avaliar-fundo`, passo 4) dos fundos elegíveis hoje antes de qualquer indicação de compra.
5. Atualizar `checklist.md` e as Skills com o que for confirmado.

Regras de trabalho do dono: responder em pt-BR, simples, sem jargão; nunca dizer "funciona/pronto" sem saída real;
separar o que foi confirmado por execução do que é dedução; não mudar nada fora do pedido sem avisar; commit e push só
na branch de trabalho.
