---
name: papel-padrao
description: Papel Padrão — trade em fundos imobiliários de Papel (CRI) descontados e saudáveis - comprar no sinal do fim do mês, receber o rendimento e vender com +10% (preço + rendimentos). Use quando o dono pedir o "Papel Padrão", os sinais do mês, o acompanhamento das posições ou o histórico dessa estratégia.
---

# Papel Padrão (montada em 18/11/2026)

Responder em português simples, sem jargão. Nunca dizer "funciona" sem mostrar a saída real do programa.
É TRADE (comprar, receber o rendimento, vender com lucro), não carteira parada. Comparar cada operação com 105% do
CDI líquido no MESMO período em que o dinheiro ficou no fundo. Registro completo dos estudos: `docs/TIPO1_TRADE.md`.

## Regras

1. **Sinal** (último pregão de cada mês, só com dado publicado até o dia), corte essencial:
   patrimônio ≥ R$ 100 mi; negociação típica (mediana de 60 pregões) ≥ R$ 250 mil/dia; sem amortização relevante nem
   aviso de saída da bolsa; avaliação de saúde diferente de NÃO COMPRAR; preço de 0,50 a 1,00 do patrimônio;
   rendimento do ano sobre o preço ≥ Selic esperada pelo Focus (fim do ano seguinte) × 0,825.
2. **Só classe Papel** (classe pela carteira, informe mensal da CVM: Papel = 2/3 ou mais em CRI, LCI, LIG, debêntures, FIDC).
3. **Nota** (média das posições entre os candidatos): desconto, rendimento acima da classe, constância do rendimento,
   cobertura, patrimônio por cota em 12 meses, queda de 10% a 25% em 6 meses. **Os 5 de maior nota = sinal.**
4. **Antes de comprar:** Skill `avaliar-fundo` (ler o relatório gerencial: o fundo ganha o que distribui? a reserva está
   caindo? algum título com atraso?). Fundo com problema real nos documentos: não comprar.
5. **Compra:** abertura do pregão seguinte ao sinal.
6. **Venda:** fechamento do dia em que (preço + rendimentos com data-com desde a compra) ≥ +10% sobre o custo.
7. **Prazo:** 1 ano (252 pregões); vende no fechamento do último dia.
8. Imposto de 20% sobre o ganho na cota; rendimento isento; taxa de 0,03% por operação.

## Como rodar

```bash
PYTHONPATH=. python3 estudos/papel_padrao.py sinais            # sinal do último mês fechado + prévia do mês em curso
PYTHONPATH=. python3 estudos/papel_padrao.py sinais 30/11/2026 # sinal de um fim de mês
PYTHONPATH=. python3 estudos/papel_padrao.py posicoes          # acompanha as compras do dono
```

- Saída: `planilhas/papel_padrao.xlsx` (Sinais, Prévia do mês, Cenário do país, Cenário - resultado passado, Posições, Regras).
- Posições do dono: `planilhas/papel_padrao_posicoes.csv` (fundo; data_compra dd/mm/aaaa; preco_compra; cotas). O programa
  mostra resultado bruto e líquido até o último dia com dado, quanto falta para +10% e avisos (alvo atingido, prazo
  vencido, abaixo de −5% com 20+ pregões).
- O programa avisa quando os preços da base estão atrasados. Sinal com dado velho NÃO vale para compra.

## Resultado de referência (02/2018 a 11/2026, contas com data-com e imposto; `estudos/descontado_classes.py`; refeito em 18/11/2026 com a classe corrigida para ISIN repetido)

| | Papel, alvo +10% |
|---|---|
| Operações | 114 |
| Com lucro | 93,9% |
| Bateram o CDI do mesmo período | 79,8% |
| Resultado médio por operação (líquido) | +7,7% |
| Tempo médio | 138 pregões (~6,5 meses) |
| Acima do CDI por mês aplicado | +0,42 ponto |
| Perdas de mais de 10% / 1 ano no prejuízo | 1,8% / 6,1% |

Por cenário do país no mês anterior à compra (`planilhas/descontado_periodos.xlsx`, `planilhas/macro_mensal.csv`):

| Cenário | Com lucro | Bateram o CDI | Acima do CDI por mês |
|---|---|---|---|
| Mercado espera Selic estável | 95% | 91% | +1,04 ponto |
| Mercado espera alta da Selic | 92% | 81% | +0,70 ponto |
| Mercado espera queda forte (Focus <= Selic − 1) | 94% | 76% | +0,18 ponto |
| Dívida bruta subiu 2+ pontos do PIB em 12 meses | 95% | 74% | +0,40 ponto |

Alternativa testada com menos tempo parado: venda quando a média de 21 cruza abaixo da de 70 (+0,10 ponto por mês;
2,5% ficam 1 ano no prejuízo). Fibonacci e banda superior de Bollinger foram piores.

## Formas de comprar testadas (18/11/2026, `estudos/papel_entradas.py`, `planilhas/papel_entradas.xlsx`)

Mesmo sinal e mesma venda (alvo +10%). Gatilho procurado até o fim do mês seguinte; sem gatilho, não compra.

| Compra | Operações | Com lucro | Chegaram ao alvo | Acima do CDI por mês | Ganho total por R$ 1.000 em cada sinal |
|---|---|---|---|---|---|
| **Abertura seguinte ao sinal (regra atual)** | 117 | 93% | 79% | +0,38 ponto | **R$ 8.604** |
| Duas partes (metade no sinal, metade se cair 5%) | 118 | 93% | 81% | **+0,41 ponto** | R$ 5.673 |
| Setup 9.1 (média de 9 virando para cima) | 117 | 90% | 75% | +0,29 ponto | R$ 7.972 |
| IFR 2 abaixo de 10 | 97 | 92% | 73% | +0,19 ponto | R$ 6.348 |
| Reversão (fecha acima da máxima de ontem após mínima de 20) | 83 | 84% | 70% | +0,04 ponto | R$ 4.679 |

Gatilho em dois passos (atenção = fundo no sinal; compra só depois de cair 3% ou 5% desde o fechamento do sinal, com ou
sem repique de 1%; até 60 pregões): 57 a 77 operações, 91%–92% com lucro, +0,25 a +0,30 ponto por mês; mesmo depois de
cair 5%, a cota caiu em média mais 8%; e 100 a 170 sinais ficaram sem compra. Ganho total de R$ 3.716 a R$ 5.114 por
R$ 1.000 em cada sinal, contra R$ 8.604 da regra atual.

Esperar a virada NÃO melhorou: perde as que sobem logo e pega as que seguem caindo. Duas partes rende um pouco mais
por mês aplicado, mas ganha menos no total (metade do dinheiro fica no CDI quando não cai 5%). Regra mantida.

## Análise gráfica: confluência para entrar e sair (18/11/2026, `estudos/papel_tecnico.py`, `planilhas/papel_tecnico.xlsx`)

6 confirmações de compra (candle de reversão de alta, suporte, IFR 14 saindo de 35, estocástico cruzando abaixo de 30,
MACD virando, volume em dia de alta) e 6 de venda (espelho). Indicadores diários em
`planilhas/tecnico/papel_indicadores_diarios.csv.gz`. Acima do CDI por mês aplicado (pontos):

| Compra / venda | 2018–2022 | 2023–11/2026 | Completo | Operações | Com lucro | Pregões médios |
|---|---|---|---|---|---|---|
| **Sinal / alvo +10% (regra atual)** | **+0,46** | **+0,31** | **+0,38** | 117 | 93% | 137 |
| 4 confirmações / venda gráfica | +0,21 | +0,25 | +0,23 | 69 | 97% | 57 |
| 3 confirmações / alvo ou venda gráfica | +0,14 | +0,18 | +0,17 | 128 | 98% | 53 |
| Sinal / venda gráfica | +0,33 | −0,22 | −0,01 | 226 | 97% | 46 |
| 2 confirmações / alvo | +0,23 | +0,03 | +0,12 | 107 | 89% | 154 |

A venda gráfica faz operações curtas (~2 a 3 meses) com quase sempre lucro, mas pequeno (+1,5% a +2,6%). A compra
por confluência perde sinais (de 17 a 253) e não melhorou. A regra atual continua a melhor nos dois períodos.

## Análise gráfica de um fundo

Skill `analise-grafica` (motor `estudos/analise_grafica.py`; página "Radar Gráfico de FIIs": https://claude.ai/artifact/Mz1Yee5tDKbspNpt42u8yX).

## Limites (dizer sempre que relevante)

- Resultados do passado, com regras escolhidas depois de muitos testes nos mesmos anos: risco de ajuste ao passado.
  O teste de verdade é acompanhar daqui para a frente, sinal a sinal.
- Histórico por fundo é pequeno (2 a 7 operações).
- Só Papel: Tijolo, Fundo de fundos e Híbrido perderam do CDI neste modelo (para eles, usar o Kairi Padrão nas quedas fortes).
- Atualizar a base antes de usar: baixar o COTAHIST da B3 (`curl --http1.1`, diário COTAHIST_DddmmAAAA.ZIP ou anual
  COTAHIST_AAAA.ZIP) e rodar `PYTHONPATH=. python3 estudos/atualizar_precos.py ARQUIVO.ZIP` e depois
  `PYTHONPATH=. python3 estudos/atualizar_mercado_cdi.py`. Rendimentos anunciados depois de 06/11/2026 ainda não entram
  (a tabela de avisos do FNET não é atualizada por esse caminho).
- 63 fundos negociados na B3 nunca entraram na base (ex.: XPML11, TRXF11, BTCI11, PSEC11, HCTR11): não aparecem nos sinais.
- Valor patrimonial corrigido só nos estudos novos (`estudos/vp_correcoes.py`); a avaliação de saúde lê o valor sem correção.
