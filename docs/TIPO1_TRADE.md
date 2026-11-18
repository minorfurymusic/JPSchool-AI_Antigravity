# Tipo 1 — descontado saudável como TRADE (registro do que foi descoberto, 18/11/2026)

Skill: `.claude/skills/descontado-saudavel/SKILL.md`. Tudo abaixo foi conferido por execução dos programas citados,
com dados de 01/2018 a 09/11/2026. Resultados do passado; regras de teste fixadas antes de cada rodada.

## 1. Como o dono quer a estratégia (correção de rota, 18/11/2026)

- É **trade**: comprar, receber o rendimento e vender quando subir (ex.: +10% a +15%). Não é carteira parada.
- Não precisa ganhar todo ano nem no período inteiro; precisa dar ganho operação por operação.
- Comparação certa: cada operação contra 105% do CDI líquido **no mesmo período em que o dinheiro ficou no fundo**.
- Os anos de 2021–2025 tiveram juros subindo muito e incerteza política; perder nesses anos é esperado.

## 2. Como as contas são feitas (a partir de `estudos/descontado_classes.py`)

- Resultado da operação = (venda − imposto + rendimentos − custo) ÷ custo. Taxa de 0,03% na compra e na venda.
- Rendimento conta pela **data-com** (estava com o fundo no fim do dia da data-base = rendimento é seu).
- Imposto de 20% sobre o ganho na cota de cada operação com lucro (sem abater prejuízo de outras: um pouco pior que o real).
- CDI de comparação: 105% do CDI, do dia da compra ao da venda, com IR regressivo (22,5% até 6 meses, 20% até 1 ano...).
- "Ganho por mês aplicado" = soma dos resultados ÷ soma dos pregões × 21. Mostra quanto o dinheiro rendeu enquanto
  ficou aplicado, comparável com o CDI no mesmo dinheiro e tempo.

## 3. Tabelas corrigidas nesse caminho

- Classe de cada fundo pela carteira (CVM): `planilhas/classificacao_carteira_mensal.csv`. Antes, 338 de 524 eram "Outros".
- Valor patrimonial: `planilhas/tecnico/valor_patrimonial_correcoes.csv` (94 saltos; aplicado só nos estudos novos).
- Boletim Focus (Selic esperada): `planilhas/focus_selic_fim_de_ano.csv`.
- Cobertura do rendimento (CVM): `planilhas/tecnico/cobertura_trimestral.csv`.

## 4. Escolha dos fundos (sinal)

- Versão 1 (corte em todas as regras): quase não dispara (3 operações em 9 anos). Descartada como gerador de sinais.
- Versão 2 (corte só no essencial + nota): corte = patrimônio ≥ R$ 100 mi, negociação ≥ R$ 250 mil/dia, sem
  amortização nem saída da bolsa, saúde ≠ NÃO COMPRAR, preço 0,50–1,00 do patrimônio, rendimento ≥ Selic esperada
  (Focus) × 0,825. Nota em desconto, rendimento acima da classe, constância, cobertura, patrimônio e queda em 6 meses.
  Em média 37 candidatos por mês. É o sinal usado nos estudos de trade.

## 5. Vendas testadas (todos os fundos, compra na abertura seguinte, prazo de 1 ano; `estudos/descontado_saidas.py`)

| Venda | Com lucro | Ganho por mês aplicado − CDI (pontos) | Perdas de mais de 10% | Prejuízo e 1 ano parado |
|---|---|---|---|---|
| Média 21 cruza abaixo da 70 | 57% | +0,04 | 6% | 2% |
| Alvo +15% | 66% | −0,17 | 12% | 34% |
| Alvo +10% | 71% | −0,28 | 11% | 29% |
| Fibonacci 38,2% / 50% / 61,8% | 69%–73% | −0,32 a −0,44 | 11%–12% | 27%–31% |
| Banda superior de Bollinger | 68% | −0,86 | 10% | 0% |

(Contas corrigidas, `planilhas/descontado_classes.xlsx`, grupo "Todos".)
Comprar só quando o fechamento toca a banda inferior de Bollinger piorou todas as vendas.

## 6. Por classe de fundo — O RESULTADO MAIS IMPORTANTE (`estudos/descontado_classes.py`)

Cada classe com os seus 5 melhores do mês. Ganho por mês aplicado menos o CDI no mesmo período (pontos percentuais):

| Venda | Papel | Tijolo | Fundo de fundos | Híbrido |
|---|---|---|---|---|
| Alvo +10% | **+0,37** | −0,51 | −0,26 | −0,46 |
| Alvo +15% | **+0,26** | −0,52 | −0,25 | −0,41 |
| Média 21 × 70 | **+0,21** | −0,27 | −0,36 | −0,26 |
| Fibonacci 61,8% | +0,15 | −0,44 | −0,35 | −0,34 |
| Fibonacci 38,2% | +0,14 | −0,57 | −0,35 | −0,36 |
| Média 21 × 90 | +0,08 | −0,29 | −0,44 | −0,35 |
| Bollinger superior | −0,16 | −0,99 | −0,73 | −0,60 |

Papel com alvo +10%: 117 operações, **93% com lucro**, 79% bateram o CDI do mesmo período, resultado médio +7,4%
líquido, 137 pregões em média, só 2,6% perderam mais de 10%, 6,8% ficaram 1 ano no prejuízo.
Desenvolvimento: só 5 a 7 operações (sem conclusão).

## 7. O caminho depois da compra (`estudos/descontado_caminho.py`, todos os fundos, contas antigas)

- 85% a 91% das compras caem depois da entrada; queda média de 7% (médias) a 11% (alvos); pior momento entre o 23º e
  o 73º pregão. Comprar no dia seguinte ao sinal é cedo.
- Prejuízo maior com Selic CAINDO (36%–56% das operações) do que parada (10%–32%), em 2018–2026.
- Perdedoras compraram com menos desconto (preço/patrimônio 0,89 contra 0,83) e depois de queda menor em 6 meses.
- Abaixo de −5% com 20 pregões: 64%–91% terminaram no prejuízo; positivas com 20 pregões: 9%–28%.
- Cobertura, tamanho do rendimento e nota não separaram vencedoras de perdedoras.
- Cortes de proteção testados (zero a zero depois de +5%; protege metade depois de +8%; tempo de 60 pregões abaixo de
  −5%) não melhoraram o ganho por mês aplicado.

## 8. Fundos de Papel candidatos em 09/11/2026 (versão 2, os 10 de maior nota dentro de Papel)

HABT11, CYCR11, RZAK11, SPXS11, VGIR11, ICRI11, HGCR11, SNCI11, WHGR11, PORD11. Antes de comprar: ler o relatório
gerencial (Skill `avaliar-fundo`). Leitura de set/2026: HABT11 sem problema; RZAK11 e SPXS11 em atenção.

## 9. Pendências

- Testar formas de compra que esperam a virada (setup 9.1, IFR, médias cruzando para cima, rompimento, reversão,
  recuo à média de 21), principalmente em Papel.
- Refazer os estudos de caminho (seção 7) com as contas corrigidas e só em Papel.
- Decisão do dono: aplicar as correções do valor patrimonial à base inteira.
