---
name: analise-grafica
description: Análise gráfica + fundamentos de um fundo imobiliário (FII) - suportes e resistências, médias, IFR, MACD, estocástico, Bollinger, candles, volume, volume por faixa de preço, Fibonacci, força relativa, zonas de liquidez e ondas de Elliott, com classe, desconto, rendimento, cobertura, saúde, Kairi e Papel Padrão. Use quando o dono pedir a análise de um fundo, o gráfico, ou citar a página "Radar Gráfico de FIIs".
---

# Análise gráfica de FII (montada em 18/11/2026)

Responder em português simples, sem jargão. Nunca dizer "funciona" sem mostrar a saída real do programa.
A análise gráfica DESCREVE o momento; não é regra testada. No estudo do Papel Padrão, juntar sinais gráficos não
melhorou o resultado (`estudos/papel_tecnico.py`). Ondas de Elliott são subjetivas: sempre dar a contagem alternativa
possível e o preço que invalida.

## Como usar na conversa

```bash
PYTHONPATH=. python3 estudos/analise_grafica.py TRXF11 [OUTRO11 ...]
```

Mostra os fundamentos e a tabela dos 13 itens (valor, leitura, confiança). Os números são os mesmos da página.
Depois da tabela: dizer onde os itens concordam entre si e com os fundamentos, e o que invalida a leitura.

## Página (artefato)

"Radar Gráfico de FIIs": https://claude.ai/artifact/Mz1Yee5tDKbspNpt42u8yX (privada até o dono compartilhar).
Fonte da página: `radar/radar_grafico.html`. Para atualizar os dados:

```bash
PYTHONPATH=. python3 estudos/atualizar_precos.py COTAHIST_DddmmAAAA.ZIP       # pregões novos (curl --http1.1)
PYTHONPATH=. python3 estudos/atualizar_mercado_cdi.py
PYTHONPATH=. python3 estudos/analise_grafica.py --todos --saida PASTA_DO_SCRATCHPAD/radar
```

e republicar a página com o mesmo endereço, passando os arquivos `dados/*.json` (são 25: um por letra e o índice).

## Os 13 itens

| # | Item | Como é calculado | Confiança |
|---|---|---|---|
| 1 | Suportes e resistências | pivôs de 5% em todo o histórico, agrupados em faixas de 2,5%; nível com 2+ toques | descritivo |
| 2 | Médias 21/50/200 | inclinação de 20 pregões; posição do preço; distância da 200 | descritivo |
| 3 | IFR 14 e 2 | sobrevenda < 30; divergência de alta nos 2 últimos fundos de 5% | descritivo |
| 4 | MACD 12/26/9 | sinal e força do histograma | descritivo |
| 5 | Estocástico 14/3/3 | < 20 / > 80; cruzamento | descritivo |
| 6 | Bollinger 20/2 | posição e largura contra a média de 120 pregões | descritivo |
| 7 | Candles (10 pregões) | martelo, engolfo, piercing, estrela da manhã, estrela cadente, nuvem negra, doji | descritivo |
| 8 | Volume e OBV | dias de volume 2×+ a média de 60; inclinação do OBV | descritivo |
| 9 | Volume por faixa de preço | 252 pregões em 30 faixas; faixa de maior volume; 70% do volume; preço médio pago desde o topo e desde o fundo | descritivo |
| 10 | Fibonacci | da queda (ou alta) de 12 meses | descritivo |
| 11 | Força relativa | contra o índice do mercado de fundos, 20 e 60 pregões | descritivo |
| 12 | Zonas de liquidez | fundos/topos iguais, varridas, vazios de preço não preenchidos, último bloco de alta antes de queda forte; deduzidas do preço, sem livro de ofertas | descritivo |
| 13 | Ondas de Elliott | pivôs de 8%; regras de impulso e A-B-C; alvos e invalidação | SUBJETIVO |

## Fontes e limites

- Fundos da base: preços ajustados por desdobramento (`planilhas/precos_AAAA.csv`). Fundos fora da base (63, ex.:
  TRXF11, XPML11): arquivo da B3 sem ajuste (`planilhas/tecnico/b3_cotahist_fii_2019_2026.csv.gz`); salto de mais
  de 35% num dia é avisado como possível desdobramento; sem rendimento, cobertura e saúde.
- Página: fundos negociados nos últimos 20 dias com 120+ pregões; gráfico dos últimos ~3 anos.
- Dados param no último pregão baixado; dizer sempre a data.
