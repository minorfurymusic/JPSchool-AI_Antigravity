# Plano: app de monitoramento e indicação de FIIs (uso próprio)

Criado em 2026-11-09. Uso pessoal, só com dados oficiais. O app aponta fundos que merecem atenção e explica o porquê; a decisão de comprar ou vender é sua.

## 1. O que foi provado com dados reais (2026-11-09)

Baixei os arquivos oficiais de 2026 e rodei um teste de ligação entre eles. Saída literal:

```
papeis CODBDI=12 no mes: 360
CVM geral linhas: 11785 | CNPJs distintos: 1428 | meses: 2026-01-01 a 2026-10-01
tickers B3 casados com CVM pelo ISIN: 303 de 360
HGLG11 | Multicategoria | fech 20261019 R$ 156.12 | VP/cota R$ 165.48 (ref 2026-09-01) | P/VP 0.94 | DY mes CVM 0.71% | cotistas 613837
MXRF11 | Logística | fech 20261019 R$ 9.38 | VP/cota R$ 9.35 (ref 2026-09-01) | P/VP 1.00 | DY mes CVM 1.06% | cotistas 1570595
KNRI11 | Multicategoria | fech 20261019 R$ 163.70 | VP/cota R$ 163.64 (ref 2026-09-01) | P/VP 1.00 | DY mes CVM 0.67% | cotistas 313851
XPML11 | Shoppings | fech 20261019 R$ 105.80 | VP/cota R$ 107.36 (ref 2026-09-01) | P/VP 0.99 | DY mes CVM -0.11% | cotistas 795394
VISC11 | Shoppings | fech 20261019 R$ 113.90 | VP/cota R$ 115.79 (ref 2026-09-01) | P/VP 0.98 | DY mes CVM 0.73% | cotistas 346772
```

O que isso mostra:

- Dá para fazer o app inteiro sem pagar por dados: a CVM dá os fundamentos e a B3 dá os preços.
- O código do papel na bolsa (ex.: HGLG11) se liga ao cadastro da CVM pelo código ISIN, que existe nos dois arquivos.

Problemas reais que apareceram e que o app precisa tratar:

| Problema | Como tratar |
|---|---|
| 57 dos 360 papéis não casaram pelo ISIN | Segunda tentativa por nome; o que sobrar fica numa lista "sem vínculo" para você conferir. Nunca vincular automático na dúvida |
| A data de fechamento saiu 19/10 num arquivo que vai até 30/10 | Causa confirmada: o arquivo mensal não vem em ordem de data. Os preços desta saída estão errados; ver seção 1A |
| MXRF11 aparece como "Logística" e XPML11 com rendimento negativo no mês | O dado oficial vem com erros de preenchimento do próprio fundo. O app mostra o dado, marca o que parece estranho e não esconde |
| O informe da CVM chega com 1 a 2 meses de atraso | Mostrar sempre a data de referência ao lado de cada número |
| O mesmo mês pode ter várias versões (reapresentação) | Usar sempre a versão mais alta |

## 1A. Preços e dados divulgados pelos fundos (revisão de 2026-11-09)

**Correção.** Os preços da seção 1 estão errados: HGLG11 saiu como R$ 156,12 "em 19/10", e o fechamento real de 30/10 foi R$ 149,50. Causa: o arquivo mensal da B3 não vem em ordem de data, e o teste pegou a última linha lida. A ligação pelo ISIN (303 de 360) continua válida; os preços e o P/VP daquela saída, não.

### Como o preço fica certo

| Camada | Fonte | Quando chega | Para que serve |
|---|---|---|---|
| Fechamento oficial | Arquivo diário da B3 (`COTAHIST_D` + data) | Na noite do mesmo dia. O de 09/11 já estava disponível às 20h39 | Base de todas as contas (P/VP, rendimento, sinais) |
| Durante o pregão | Cotação com atraso da B3 (`cotacao.b3.com.br`) | Com atraso em relação ao pregão; o tamanho do atraso não foi medido, o teste foi com o pregão fechado | Só para mostrar na tela o preço do momento, com a hora ao lado |

Prova de que as duas fontes batem (HGLG11, pregão de 09/11/2026):

```
arquivo diário:   HGLG11 pregao 20261109 abert 146.86 max 147.11 min 144.27 fech 145.1 negocios 18184
cotação atrasada: "dtTm":"2026-11-09 20:40:38" ... "opngPric":146.86,"minPric":144.27,"maxPric":147.11,"curPrc":145.1 ... "ttlQty":18184
```

Regras para não mostrar preço errado:

1. Todo preço aparece com data e hora. Nunca um número solto.
2. A conta usa sempre o fechamento oficial escolhido pela maior data, nunca pela posição no arquivo.
3. Toda noite o app compara o fechamento oficial com a última cotação atrasada. Se não baterem, marca o fundo e avisa.
4. Fundo sem negócio no dia mostra o último fechamento com a data antiga em destaque.
5. Preço com mais de um pregão de atraso fica marcado como desatualizado e não entra em sinal.

Risco: a cotação com atraso é o serviço que o próprio site da B3 usa, sem documentação pública. Pode mudar sem aviso. Por isso ela só serve para a tela; as contas dependem do arquivo de fechamento, que é o histórico oficial.

### Dados divulgados pelos fundos

| O quê | Fonte | Quando chega | Situação |
|---|---|---|---|
| Rendimento anunciado: valor por cota, data limite para ter a cota, data de pagamento | Cadastro de fundos listados da B3 (`sistemaswebb3-listados.b3.com.br`) | Depois do anúncio; o prazo exato não foi medido | Confirmado |
| Patrimônio, valor patrimonial da cota, cotistas, composição | CVM, informe mensal | 1 a 2 meses depois do mês de referência; arquivos regravados em 07/11/2026 | Confirmado |
| Imóveis, vacância, inquilinos, contratos | CVM, informe trimestral | Após o fim do trimestre | Confirmado |
| Relatório gerencial e fato relevante (PDF) | FNET | No dia da publicação | **Não funciona daqui**: tempo esgotado em 2 tentativas. Causa não confirmada |

Prova do rendimento anunciado (HGLG11):

```
"paymentDate":"16/11/2026","rate":"1,17000000000","relatedTo":"OUTUBRO/2026","approvedOn":"30/10/2026","label":"RENDIMENTO","lastDatePrior":"30/10/2026"
```

Com isso o rendimento do app vem do valor anunciado pelo fundo dividido pelo preço de fechamento, e não depende do campo de rendimento do informe da CVM, que tem erros de preenchimento.

Pendências desta parte: a lista geral de fundos desse cadastro voltou vazia nas consultas testadas (a consulta por fundo funciona); o FNET segue sem resposta.

## 2. Fontes de dados

| Fonte | Endereço | O que entrega | Situação |
|---|---|---|---|
| CVM, informe mensal | `dados.cvm.gov.br/dados/FII/DOC/INF_MENSAL/DADOS/` | Patrimônio, valor patrimonial da cota, rendimento do mês, número de cotistas, segmento, composição da carteira | Confirmado, cabeçalho lido |
| CVM, informe trimestral | `dados.cvm.gov.br/dados/FII/DOC/INF_TRIMESTRAL/DADOS/` | Imóveis, vacância, inadimplência, inquilinos, vencimento dos contratos, resultado | Confirmado, cabeçalho lido |
| B3, cotações históricas | `bvmf.bmfbovespa.com.br/InstDados/SerHist/` | Preço de abertura, máxima, mínima, fechamento, volume e número de negócios, por dia | Confirmado, arquivo lido |
| Banco Central | `api.bcb.gov.br` | Selic, CDI, IPCA | Confirmado que responde; séries ainda não escolhidas |
| FNET (B3) | `fnet.bmfbovespa.com.br` | Relatórios gerenciais e fatos relevantes em PDF | **Pendente**: endereço liberado, mas não respondeu (tempo esgotado) no único teste feito. Não sei ainda se é bloqueio do site ou falha passageira |

### Cabeçalhos reais conferidos

Informe mensal, três arquivos por ano, todos ligados por `CNPJ_Fundo_Classe` + `Data_Referencia` + `Versao`:

- `inf_mensal_fii_geral` (37 colunas): `Tipo_Fundo_Classe`, `CNPJ_Fundo_Classe`, `Data_Referencia`, `Versao`, `Data_Entrega`, `Nome_Fundo_Classe`, `Codigo_ISIN`, `Segmento_Atuacao`, `Mandato`, `Tipo_Gestao`, `Nome_Administrador`, entre outras.
- `inf_mensal_fii_complemento` (30 colunas): `Total_Numero_Cotistas`, `Valor_Ativo`, `Patrimonio_Liquido`, `Cotas_Emitidas`, `Valor_Patrimonial_Cotas`, `Percentual_Rentabilidade_Efetiva_Mes`, `Percentual_Rentabilidade_Patrimonial_Mes`, `Percentual_Dividend_Yield_Mes`, `Percentual_Amortizacao_Cotas_Mes`, entre outras.
- `inf_mensal_fii_ativo_passivo` (52 colunas): quanto o fundo tem em imóveis, CRI, cotas de outros FIIs, caixa, valores a receber e dívidas.

Informe trimestral, 16 arquivos por ano. Os mais úteis: `imovel` (vacância, inadimplência e peso de cada imóvel), `imovel_renda_acabado_inquilino` (concentração por inquilino), `complemento` (vencimento e indexador dos contratos), `aquisicao_imovel` e `alienacao_imovel` (compras e vendas), `resultado_contabil_financeiro` (receitas e despesas).

Cotações da B3: arquivo de texto de largura fixa, sem cabeçalho. Fundos imobiliários são as linhas com código 12 na posição 11-12. O ISIN fica nas posições 231-242.

Formato: arquivos da CVM separados por ponto e vírgula, codificação latin-1, número com ponto decimal.

## 3. Como o app funciona

```
CVM + B3 + Banco Central
        |
   coleta diária (baixa só o que mudou)
        |
   banco de dados local (um arquivo)
        |
   cálculo dos indicadores e dos sinais
        |
   painel na tela  +  avisos
```

Ferramentas escolhidas, pela simplicidade:

| Parte | Escolha | Por quê |
|---|---|---|
| Linguagem | Python | Todos os projetos pesquisados usam; é o padrão para esse tipo de dado |
| Banco de dados | DuckDB (um arquivo só) | Não precisa instalar nem manter servidor |
| Tela | Streamlit | Vira painel com pouco código; usado em 4 dos projetos pesquisados |
| Atualização automática | GitHub Actions (agendado) | Gratuito em repositório público, sem servidor |

Versões e licenças das bibliotecas serão conferidas e registradas no momento da instalação, não agora.

## 4. Funções

Coluna "Origem": de qual projeto pesquisado a ideia veio (ver `PESQUISA.md`). Nenhum código será copiado dos projetos sem licença.

### Fase 1: base de dados
| Função | Origem |
|---|---|
| Baixar e guardar informes mensais da CVM, sem duplicar ao rodar de novo | fii-intelligence, fiispider |
| Baixar e guardar cotações diárias da B3 | fii-intelligence |
| Ligar papel da bolsa ao cadastro da CVM, com lista de "sem vínculo" para revisão manual | fii-intelligence |
| Calcular P/VP, rendimento do mês e dos últimos 12 meses, liquidez, variação de preço | fii-intelligence, dashboard-fiis |

### Fase 2: painel
| Função | Origem |
|---|---|
| Lista de todos os fundos com filtros (segmento, P/VP, rendimento, liquidez, patrimônio) | FIIGuru, protótipo IFSC |
| Página de cada fundo: preço, rendimentos pagos, valor patrimonial, cotistas, composição | dashboard-fiis |
| Comparar fundos lado a lado, com preço na mesma base | dashboard-fiis |
| Marca visível em dado estranho ou desatualizado | fii-offer-radar (relatório de qualidade) |

### Fase 3: minha carteira
| Função | Origem |
|---|---|
| Informar quantas cotas tenho de cada fundo | dashboard-fiis |
| Patrimônio, renda mensal média e renda anual estimada | dashboard-fiis |
| Lista de fundos que quero acompanhar | myFII_B3 |

### Fase 4: sinais e indicação
| Função | Origem |
|---|---|
| "O que mudou hoje": preço, volume ou número de negócios fora do normal | fii-intelligence (Score de Atenção) |
| Mudança nos fundamentos: queda de rendimento, queda do valor patrimonial, saída de cotistas | própria |
| Nota de 0 a 100 por fundo, com o motivo escrito em texto | fii-intelligence, fii-offer-radar |
| Nota de confiança: quais dados existem, quais faltam, quais se contradizem | fii-offer-radar |
| Comparação com Selic, CDI e IPCA | fii-offer-radar, CVM-FII-Data |
| Registrar minha decisão sobre cada sinal (vi, ignorei, comprei) | fii-offer-radar |

### Fase 5: imóveis e contratos (informe trimestral)
| Função | Origem |
|---|---|
| Vacância e inadimplência por imóvel, com histórico | CVM-FII-Data |
| Concentração por imóvel e por inquilino | CVM-FII-Data |
| Calendário de vencimento dos contratos | própria |
| Aviso de compra ou venda de imóvel | própria |

### Fase 6: documentos
| Função | Origem |
|---|---|
| Baixar relatórios gerenciais e fatos relevantes do FNET | fii-fnet, kowalski |
| Ler o PDF com IA e extrair resumo, riscos e comentário do gestor | deepFIIs, fii-offer-radar |
| Aviso de documento novo dos fundos que acompanho | própria |

Depende de duas coisas ainda abertas: o FNET responder e uma chave de IA paga.

### Fase 7: automático
| Função | Origem |
|---|---|
| Atualização diária sem eu precisar abrir nada | fii-offer-radar, CVM-FII-Data |
| Aviso dos sinais importantes por e-mail ou mensagem | fii-offer-radar |

## 5. Riscos conhecidos

- A CVM muda nomes de colunas (mudou em jan/2026). A coleta precisa conferir o cabeçalho e parar com aviso claro se mudar, em vez de gravar dado errado.
- Repositório público: a sua carteira não pode ser gravada nele. Fica só no seu aparelho ou num repositório privado.
- Fase 6 tem custo (IA) e uma dependência não confirmada (FNET).
- Nota e sinais são contas sobre dados passados. Servem para priorizar o que olhar, não para prever preço.

## 6. Decisões que são suas

1. **Onde você vai usar**: só no computador, ou por um endereço na internet que abre no celular?
2. **Carteira**: o repositório é público. Mudo para privado, ou a carteira fica só no seu aparelho?
3. **IA para ler PDFs (Fase 6)**: tem custo por uso. Só precisa decidir quando chegar lá.
4. **Nome do repositório**: `JPSchool-AI_Antigravity` não tem relação com FIIs. Sigo aqui, ou você cria outro?

As fases 1 e 2 não dependem de nenhuma dessas respostas.

## 7. Entrega 1: app construído (2026-11-10)

Fases 1, 2, 4 e parte da 5 feitas. Fase 3 (carteira), 6 (documentos) e 7 (automático) não foram feitas.

### O que mudou em relação ao plano

- **Painel**: página única gerada pelo próprio app, em vez de Streamlit. Abre em qualquer navegador, sem servidor.
- **Rendimento por cota**: o informe da CVM não tem esse número pronto, e cada fundo preenche de um jeito. O app faz duas contas (rendimentos a distribuir ÷ cotas; rendimento percentual × valor patrimonial) e só usa a que bate com o valor anunciado na B3 em pelo menos 85% dos meses. Fundo que não bate fica sem histórico antigo.
- **Fundos que trocaram de CNPJ** (viraram "classe"): o app junta os dois históricos pelo ISIN. Se os dois CNPJs informam os mesmos meses por mais de 6 meses, o papel é tratado como ambíguo e sai.
- **Desdobramento**: salto de preço só é ajustado quando o número de cotas na CVM muda na mesma proporção ou a B3 lista o desdobramento.
- **A B3 só mostra ~12 meses de rendimentos**: o app guarda o que já viu e acumula.

### Bibliotecas (nome, versão, licença conferidos na instalação)

duckdb 2.0.0 (MIT), pandas 3.1.1 (BSD-3-Clause), pyarrow 26.0.1 (Apache-2.0), requests 2.34.2 (Apache-2.0), pytest 9.2.0 (MIT).

### Saída real da rotina completa (`python -m fii.atualizar`, 2026-11-10)

```
"base": {"cotacoes": 527834, "papeis": 761, "vinculados": 524, "sem_vinculo": 237, "quebras": 466,
         "quebras_confirmadas": 87, "mensal": 26166, "fundos_no_mensal": 524, "vendas": 2151,
         "primeiro_pregao": "2017-01-02", "ultimo_pregao": "2026-11-09"},
"eventos": {"queda sem venda": 164, "queda com venda": 17, "salto sem venda": 226, "salto com venda": 33,
            "salto mantido sem venda": 100, "salto mantido com venda": 7, "venda com venda": 46},
"oportunidades": {"rendimento já voltou ao nível anterior": 38, "queda": 21, "passou da janela: rever": 12,
                  "queda recente": 9, "em andamento": 8, "venda de imóvel informada": 7, "novo": 4}
real    0m19.517s
```

Origem do rendimento antigo, por fundo:

```
sem B3 e as contas da CVM não concordam: sem histórico     220
                                           CVM conta A     182
    histórico da CVM não bate com a B3: só meses da B3      78
                                           CVM conta B      44
```

### O que o histórico mostrou (2017 a 2026)

Retorno acima do mercado de FIIs (mediana), comprando no pregão seguinte ao fim do mês do evento:

```
       evento               grupo  casos  1 mês  3 meses  6 meses  12 meses  só cota 3m  acerto 3m  cota +10% em 6m  meses até voltar
        salto      todos os casos    259   1,5%     2,4%     3,0%      5,6%        1,3%        69%              12%                 3
        salto com venda de imóvel     33   0,9%     1,5%     2,0%      4,0%        0,9%        63%               4%                 0
        salto               papel     43   2,5%     5,2%     8,0%      9,7%        3,5%        86%              12%                 9
        salto              tijolo    123   0,8%     1,7%     2,4%      4,3%        1,0%        66%              13%                 3
salto mantido      todos os casos    107   0,9%     2,0%     2,9%      5,9%        0,2%        65%               8%                10
        venda      todos os casos     46   0,5%     0,3%     1,4%      0,6%       -0,6%        58%              17%                 0
```

Comprando dez pregões depois, o ganho do primeiro mês cai de 1,5% para 0,8%.

Leitura: o efeito existe e é consistente (cerca de 70% dos casos), mas a mediana é pequena. A alta de 10 a 15% na cota aconteceu em cerca de 1 caso em 8. Com venda de imóvel há só 33 casos, o que é pouco para concluir.

### Limitações reais

- A data do evento no histórico é o fim do mês de referência, não a data do comunicado. O app não lê comunicados (FNET não responde deste ambiente).
- Venda de imóvel só é vista quando sai no informe trimestral da CVM, semanas depois.
- 220 fundos ficaram sem histórico de rendimento por falta de dado confiável; 237 papéis sem vínculo com a CVM.
- 379 saltos de preço sem explicação confirmada; os períodos afetados ficam fora da conta.
- Custos e imposto não descontados.
- Os testes cobrem leitura de formato e as contas; não há teste automático do painel além da abertura em navegador sem erros.
