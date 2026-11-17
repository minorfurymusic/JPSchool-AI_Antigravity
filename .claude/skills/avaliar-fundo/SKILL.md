---
name: avaliar-fundo
description: Avalia se um fundo imobiliário (FII) está saudável antes de comprar num sinal do Kairi (ou durante a operação). Use quando sair um sinal de compra, quando o dono perguntar se um fundo é bom/ruim/saudável, ou ao rever uma posição aberta.
---

# Avaliar a saúde de um fundo antes da compra

Objetivo: separar o fundo que caiu junto com o mercado (compra) do fundo que caiu porque está doente (não compra).
Só vale o que era público até o dia do sinal. Responder em português simples, sem jargão.

## Passo 1 — Ficha automática

```bash
PYTHONPATH=. python3 estudos/ficha_fundo.py CODIGO11 dd/mm/aaaa
```

A ficha (estudos/saude_fundo.py) traz: queda do fundo contra o mercado de fundos (3, 6, 12 meses), preço sobre
valor patrimonial, rendimento sobre o preço, valor patrimonial por cota em 12 meses, rendimento mês a mês (24 meses)
com tendência, cortes e oscilação, todos os fatos relevantes e comunicados dos 12 meses anteriores e um veredito
automático.

## Passo 2 — A queda foi do fundo ou do mercado?

- Fundo caiu junto com o mercado (diferença menor que 10 pontos em 6 meses): queda geral. Em geral, compra.
- Fundo caiu 10 pontos ou mais além do mercado: queda só dele. Obrigatório achar o motivo nos passos 3 e 4.
  Nas 283 operações do grupo grande (2018–2026), quando a queda foi 20+ pontos pior que o mercado, 26% deram prejuízo;
  quando foi menor que a do mercado, 5%.

## Passo 3 — Números do fundo

Sinais de doença (qualquer um, junto com queda só do fundo, = não comprar):
- rendimento caindo mais de 10% em 12 meses (média dos 3 últimos meses contra os 3 primeiros);
- 3 ou mais cortes de rendimento em 12 meses;
- valor patrimonial por cota caindo mais de 5% em 12 meses (reavaliação de imóveis ou de papéis);
- preço muito abaixo do patrimônio (0,5 ou menos) sem explicação: o mercado desconfia do patrimônio.

## Passo 4 — Ler TODOS os documentos dos 12 meses anteriores

Não confiar só na busca por palavras do programa (ela erra). Procurar:
- calote ou atraso de devedor (CRI), recuperação judicial de inquilino ou devedor;
- saída, rescisão, renegociação ou desconto de inquilino importante (pior se for inquilino único ou imóvel único);
- reavaliação negativa do patrimônio, remarcação de cotas;
- ofício da B3 ou da CVM pedindo explicação de oscilação (o mercado sabe de algo);
- comunicado de "não haverá distribuição de rendimentos";
- liquidação, incorporação, venda de todos os ativos, ida para o balcão (a regra 1 já barra);
- troca de gestor ou administrador, briga entre cotistas e gestão, emissão de cotas muito abaixo do patrimônio.
Se a base não tiver os comunicados do período, baixar do FNET (estudos/kairi_fnet_2026.py mostra como).

## Passo 5 — Veredito (sempre com o motivo)

- SAUDÁVEL: queda geral, ou queda só do fundo sem nenhum sinal de doença e com explicação conhecida. Compra.
- ATENÇÃO: queda só do fundo (20+ pontos) sem explicação nos dados. Dizer ao dono que o motivo é desconhecido;
  ele decide. Exemplo: TRBL11 em 25/10/2024 (rendimento e patrimônio estáveis, −27% contra −4% do mercado; depois
  cortou o rendimento em 29%).
- NÃO COMPRAR: queda só do fundo E sinal de doença nos números ou nos documentos.

## Casos que ensinaram a regra (conferidos com dados até o dia do sinal)

| Fundo | Sinal | O que se via | Veredito | O que aconteceu |
|---|---|---|---|---|
| DEVA11 | 17/05/2023 | −27% contra +6% do mercado; rendimento −42%, 6 cortes; calote dos CRI Circuito das Compras (fatos de 06/03, 29/03, 05/05/2023) | não comprar | −18,5% |
| VGHF11 | 18/05/2026 | −20% contra 0%; rendimento de 0,09 para 0,07; ofício da B3 sobre oscilação em 12/05/2026 | não comprar | cerca de −30% em aberto |
| TGAR11 | 13/10/2026 | −41% em 12 meses contra +10%; rendimento −29%; remarcação de −49% (fev/2026); 2 ofícios da B3; preço 0,47 do patrimônio | não comprar | −36% em aberto |
| XPCM11 | 10/07/2019 | Petrobras, única inquilina do único prédio, avisou a saída em 08/07/2019 | não comprar (risco real) | deu +27% mesmo assim |
| FIGS11, CACR11, JSRE11 | 2018, 2025, 2023 | queda só do fundo, mas rendimento e patrimônio estáveis, sem documento negativo | atenção → compra | +13%, +29%, +22% |

## Limites

- Os comunicados ao mercado e editais só estão na base de 05/2025 em diante (43 fundos). Antes disso, só fatos relevantes.
- A regra foi montada depois de ver esses perdedores. Pode estar ajustada ao passado; acompanhar daqui para a frente.
- Na simulação de 2018–2026 (R$ 10 mil, um fundo de cada vez), a avaliação melhorou a versão com Conservadora 2 a 20%
  (R$ 22.191 → R$ 35.797) e piorou um pouco a versão a 15% (R$ 25.314 → R$ 24.652), porque também barrou fundos que
  deram lucro (estudos/kairi_ano_a_ano_skill.py).
