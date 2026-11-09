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
