# Estudo com a data real do anúncio (avisos de rendimento do FNET, 2017 a 2026)

Feito em 2026-11-11/12 com `estudos/anuncio_real.py`. Para refazer: `PYTHONPATH=. .venv/bin/python estudos/anuncio_real.py`.

## Dados

35.773 avisos de rendimento baixados do FNET (1 com erro: arquivo vazio no próprio FNET), 40.043 rendimentos de 725 fundos. Depois de ligar aos papéis da bolsa: 23.831 anúncios de 455 fundos, de 05/01/2017 a 09/11/2026.

## Método

- **Salto anunciado**: rendimento pelo menos 25% acima da mediana dos 6 anúncios anteriores do mesmo fundo, só em fundos que anunciam todo mês e com liquidez. 394 casos em 177 fundos.
- **Entrada**: fechamento do primeiro pregão em que dava para reagir. Aviso entregue até 17h: mesmo dia. Depois: pregão seguinte.
- **Controle**: até 25 outros fundos com liquidez comprados no mesmo dia, sem salto anunciado nos 6 meses antes ou depois.
- Só preço da cota, ajustado por desdobramento. Sem rendimento recebido, sem custos, sem imposto.
- As classes "isolado", "temporário" e "longo" só se conhecem depois. A seção de entrada tardia usa apenas o que já se sabia na data da entrada.

## O que os dados mostram

### Quando o aviso sai

- 99% dos avisos saem no mesmo dia da data-base; 73% depois das 17h.
- Ou seja: quando o aviso formal sai, o pregão com direito àquele rendimento já fechou.
- Nos 10 pregões antes do aviso de salto, a cota já subiu 1,05% acima do mercado, em 66% dos casos. Parte disso é a alta normal antes de qualquer data-base (0,73%).

### A partir do anúncio (todos os 394 saltos)

| Janela | | Pico | Fundo | Fim | Dia do pico | Tocou +10% | Tocou +15% | Tocou −10% |
|---|---|---|---|---|---|---|---|---|
| 1 mês | salto | +2,4% | −1,4% | +0,4% | 14º | 7% | 4% | 3% |
| 1 mês | controle | +1,5% | −2,1% | −0,7% | | 4% | 1% | 6% |
| 3 meses | salto | +4,0% | −3,1% | +0,2% | 28º | 19% | 9% | 16% |
| 3 meses | controle | +2,6% | −5,0% | −1,8% | | 13% | 5% | 24% |
| 6 meses | salto | +5,7% | −5,6% | −1,8% | 45º | 31% | 18% | 31% |
| 6 meses | controle | +3,7% | −8,5% | −3,9% | | 22% | 11% | 44% |

### O que decide é se o rendimento alto dura

| O que veio depois (só se sabe depois) | Casos | Pico em 6 meses | Controle | Tocou +10% | Controle | Fim em 6 meses | Controle |
|---|---|---|---|---|---|---|---|
| Isolado: voltou no anúncio seguinte | 164 | +5,2% | +4,0% | 28% | 22% | −3,2% | −3,7% |
| Temporário: 2 a 11 anúncios altos e voltou | 137 | +4,8% | +4,2% | 30% | 25% | −1,9% | −3,3% |
| Longo: 12 ou mais anúncios altos | 72 | +7,8% | +2,8% | 40% | 16% | +3,1% | −5,5% |

### Entrar tarde (rendimento ainda alto na data da entrada)

| Entrada | Casos | Pico em 3 meses | Controle | Tocou +5% | Controle | Tocou +10% | Controle | Tocou −5% | Controle |
|---|---|---|---|---|---|---|---|---|---|
| No anúncio | 361 | +4,0% | +2,6% | 42% | 31% | 19% | 13% | 36% | 50% |
| 1 mês depois | 208 | +4,4% | +2,7% | 44% | 32% | 18% | 14% | 35% | 49% |
| 3 meses depois | 147 | +3,1% | +2,6% | 33% | 32% | 10% | 14% | 39% | 51% |
| 5 meses depois | 114 | +2,8% | +2,6% | 26% | 30% | 11% | 12% | 42% | 51% |

### A devolução

- No anúncio em que o rendimento volta: mediana de 1,02 vez o nível antigo; abaixo do nível antigo em 41% dos casos; 10% ou mais abaixo em 22%.
- No mês seguinte à volta: cota termina em −1,6% (controle −0,3%); toca −5% em 34% dos casos (controle 22%).
- Em 3 meses: fundo mediano de −6,4% (controle −4,7%); toca −10% em 30% (controle 23%).
- Do anúncio do salto até o anúncio da volta (140 casos, 82 pregões na mediana): pico mediano de +4,5% no 37º pregão; no dia da volta a cota está em −1,7%; pico de 10% ou mais em 29%; terminou abaixo do preço de entrada em 56%.

## Leitura

1. Com a data real, o salto anunciado aumenta sim a chance de alta grande (tocar +10% em 3 meses: 19% contra 13%). O estudo anterior, com data aproximada, dizia que não.
2. Quatro em cada dez saltos são pagamento isolado e não valem nada além do controle. Separar isso na hora exige ler o comunicado.
3. Esperar o segundo anúncio alto não custa: entrar um mês depois rende igual a entrar no anúncio, e já elimina os isolados.
4. Depois de três meses a vantagem nas altas acaba. Sobra só queda menor que a do mercado.
5. O pico costuma vir entre a 5ª e a 9ª semana.
6. A devolução existe e é mensurável: quando o rendimento alto acaba, a cota cai mais que o mercado, e em mais da metade dos casos termina abaixo do preço de entrada.

## Limites

- O aviso formal sai depois do fechamento. Se houve fato relevante antes, o app ainda não lê; a entrada real de quem leu pode ser anterior.
- As classes da tabela do meio usam o futuro.
- O FNET não informa o fuso da hora de entrega; presumido horário de Brasília.
- Controle sorteado com semente fixa.
- Só fundos que anunciam todo mês.
- Sem rendimento recebido, custos ou imposto de 20% sobre ganho na cota.
- Na primeira rodada o controle eram só fundos sem nenhum salto em 10 anos, o que piorava o controle. Corrigido antes de registrar estes números.

## Saída literal

```
Anúncios de rendimento com data real: 23831 de 455 fundos, de 05/01/2017 a 09/11/2026
Hora de entrega: até 10h 3% | 10h às 17h 24% | 17h em diante 73%
Dias entre o anúncio e a data-base: mediana 0 | no mesmo dia 99% | 1 a 5 dias depois 0% | anúncio depois da data-base 0%

Saltos anunciados (>= 25% sobre a mediana dos 6 anúncios anteriores), fundos com liquidez: 394 em 177 fundos
                                             casos  salto_mediano  anuncios_altos
classe                                                                           
ainda sem dados para classificar                21           80.0             0.0
isolado (voltou no anúncio seguinte)           164           66.3             0.0
longo (12 ou mais anúncios altos)               72           40.3            18.0
temporário (2 a 11 anúncios altos e voltou)    137           36.4             3.0

=== 1. A PARTIR DO DIA DO ANÚNCIO ===
   10 pregões antes até a véspera: média +1.05% acima do mercado, mediana +0.78%, positivos 66% (381 casos)
   da véspera ao fechamento de entrada: média -0.25% acima do mercado, mediana -0.19%, positivos 41% (381 casos)

--- todos os saltos anunciados: 394 casos ---
  janela de 1 mês:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       367.0             2.393             -1.421                      0.438                   14.0      0.204       0.068       0.038      0.153       0.033               0.068
controle  9215.0             1.458             -2.140                     -0.709                    9.0      0.154       0.038       0.012      0.231       0.060               0.037
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       361.0             4.015              -3.07                      0.225                   28.0      0.418       0.188       0.091      0.363       0.155               0.188
controle  8987.0             2.606              -5.00                     -1.770                   18.0      0.312       0.127       0.052      0.500       0.239               0.125
  janela de 6 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       342.0             5.686             -5.636                     -1.783                   45.0      0.526       0.313       0.175      0.547       0.310                0.31
controle  8534.0             3.694             -8.513                     -3.905                   31.0      0.419       0.219       0.105      0.686       0.439                0.21

--- classe (só se sabe depois): ainda sem dados para classificar: 21 casos ---
  janela de 3 meses:
          casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso        6.0             2.663             -3.926                      0.742                   16.0      0.333       0.167       0.167      0.167       0.167               0.167
controle  282.0             3.109             -4.248                     -1.509                   30.0      0.280       0.099       0.028      0.447       0.199               0.096
  janela de 6 meses:
          casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso        2.0             4.887             -3.234                      0.829                   19.0       0.50       0.000       0.000      0.500       0.000               0.000
controle  230.0             3.739             -6.788                     -3.722                   37.5       0.37       0.191       0.074      0.565       0.391               0.178

--- classe (só se sabe depois): isolado (voltou no anúncio seguinte): 164 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       152.0             3.606             -4.320                     -0.742                   19.0      0.401       0.158       0.053      0.447       0.191               0.158
controle  3785.0             2.874             -4.968                     -1.530                   19.0      0.332       0.131       0.048      0.497       0.246               0.129
  janela de 6 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       141.0             5.151             -7.702                     -3.209                   31.0      0.511       0.284       0.156      0.638       0.383               0.277
controle  3559.0             4.023             -8.600                     -3.737                   34.0      0.435       0.221       0.107      0.676       0.439               0.211

--- classe (só se sabe depois): longo (12 ou mais anúncios altos): 72 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso        72.0             5.352             -2.174                      3.848                   49.5      0.514       0.194       0.083      0.250       0.069               0.194
controle  1697.0             2.126             -5.572                     -2.792                   14.0      0.263       0.088       0.032      0.548       0.240               0.085
  janela de 6 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso        72.0             7.781             -3.261                      3.099                   79.0      0.625       0.403       0.222      0.347       0.125               0.403
controle  1674.0             2.752             -9.512                     -5.548                   18.0      0.343       0.162       0.073      0.729       0.478               0.152

--- classe (só se sabe depois): temporário (2 a 11 anúncios altos e voltou): 137 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       131.0             3.709             -3.046                      -0.54                   33.0      0.389       0.221       0.137      0.336       0.160               0.221
controle  3213.0             2.778             -4.926                      -1.66                   18.0      0.322       0.145       0.065      0.493       0.231               0.143
  janela de 6 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       127.0             4.844             -6.004                     -1.888                   44.0      0.488       0.299       0.173      0.559       0.339               0.299
controle  3067.0             4.155             -8.294                     -3.252                   34.0      0.445       0.251       0.131      0.672       0.426               0.239

--- salto de 25 a 50%: 202 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       193.0             3.964             -2.802                      0.335                   32.0      0.420       0.202       0.088      0.326       0.140               0.202
controle  4643.0             2.632             -5.094                     -1.889                   18.0      0.313       0.129       0.055      0.508       0.225               0.126

--- salto acima de 50%: 192 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       168.0             4.139             -3.735                      0.127                   23.5      0.417       0.173       0.095      0.405       0.173               0.173
controle  4301.0             2.636             -4.837                     -1.832                   19.0      0.312       0.123       0.046      0.492       0.240               0.121

--- até 2021: 177 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       172.0             4.155             -3.217                      0.148                   29.5      0.413       0.203       0.087      0.366       0.198               0.203
controle  4185.0             2.549             -6.154                     -2.849                   15.0      0.314       0.134       0.059      0.575       0.308               0.132

--- 2022 em diante: 217 casos ---
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       189.0             3.804             -2.913                      0.426                   28.0      0.423       0.175       0.095      0.360       0.116               0.175
controle  4762.0             2.646             -4.214                     -1.320                   20.0      0.308       0.115       0.038      0.434       0.176               0.114

=== 2. ENTRAR TARDE: o rendimento continua alto N anúncios depois. E a cota, dali em diante? ===

--- entrada 1 mês depois (rendimento alto em todos os 1 anúncios seguintes): 218 casos ---
  janela de 1 mês:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       211.0             1.951             -1.622                      0.244                   15.0      0.223       0.062       0.009      0.133       0.047               0.062
controle  5191.0             1.444             -2.228                     -0.663                    9.0      0.160       0.042       0.014      0.223       0.065               0.042
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       208.0             4.370             -3.303                      0.803                   37.0      0.442       0.183       0.087      0.346       0.154               0.178
controle  5103.0             2.697             -4.827                     -1.589                   19.0      0.319       0.143       0.064      0.487       0.232               0.138

--- entrada 3 meses depois (rendimento alto em todos os 3 anúncios seguintes): 153 casos ---
  janela de 1 mês:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       150.0             1.665             -1.757                     -0.084                   14.0       0.16       0.033       0.007      0.120       0.040               0.033
controle  3650.0             1.439             -2.252                     -0.636                    9.0       0.17       0.050       0.018      0.211       0.048               0.050
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       147.0             3.133             -3.948                     -0.889                   23.0      0.327       0.102       0.034      0.388       0.190               0.102
controle  3561.0             2.639             -5.118                     -2.029                   19.0      0.318       0.137       0.062      0.513       0.212               0.133

--- entrada 5 meses depois (rendimento alto em todos os 5 anúncios seguintes): 118 casos ---
  janela de 1 mês:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       116.0             1.952             -1.858                      0.017                   15.0      0.129       0.052       0.000      0.216       0.034               0.052
controle  2814.0             1.521             -2.129                     -0.581                    9.0      0.149       0.030       0.009      0.220       0.042               0.030
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       114.0             2.787             -4.476                     -1.109                   20.0      0.263       0.114       0.035      0.421       0.149               0.114
controle  2749.0             2.605             -5.067                     -2.130                   19.0      0.300       0.121       0.054      0.509       0.220               0.119

=== 3. A DEVOLUÇÃO: a partir do anúncio em que o rendimento voltou ao nível antigo ===
Rendimento no anúncio da volta, em relação ao nível anterior ao salto: mediana 1.02 | abaixo do nível antigo em 41% | 10% ou mais abaixo em 22%

--- depois que o rendimento alto acabou (salto durou 2 anúncios ou mais): 148 casos ---
  janela de 1 mês:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       140.0             1.110             -3.029                     -1.636                    8.0      0.114       0.050       0.036      0.336       0.079               0.050
controle  3470.0             1.624             -2.156                     -0.347                    9.0      0.169       0.052       0.016      0.217       0.048               0.052
  janela de 3 meses:
           casos  pico (mediana) %  fundo (mediana) %  fim da janela (mediana) %  dia do pico (mediano)  tocou +5%  tocou +10%  tocou +15%  tocou -5%  tocou -10%  +10% antes de -10%
caso       131.0             2.029             -6.372                     -2.554                   17.0      0.252       0.130       0.061      0.557       0.298               0.122
controle  3212.0             2.656             -4.688                     -1.869                   20.0      0.310       0.147       0.079      0.475       0.233               0.146
Do anúncio do salto até o anúncio da volta (140 casos, 82 pregões na mediana): pico mediano +4.5% no 37º pregão | cota no dia da volta -1.7% | pico de 10% ou mais em 29% | terminou abaixo da entrada em 56%
```
