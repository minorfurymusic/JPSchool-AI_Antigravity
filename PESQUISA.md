# Pesquisa: app de monitoramento de FIIs (uso próprio)

Data da pesquisa: 2026-11-09. Nada aqui foi instalado nem testado; é levantamento por busca na web e no GitHub.

## Fontes de dados oficiais

| Fonte | O que tem | Situação |
|---|---|---|
| CVM Dados Abertos, Informe Mensal de FII: https://dados.cvm.gov.br/dataset/fii-doc-inf_mensal | Um arquivo ZIP por ano, de 2016 em diante, com dicionário de dados | Gratuito. Em jan/2026 a CVM renomeou a coluna `CNPJ_Fundo` para `CNPJ_Fundo_Classe` e criou `Tipo_Fundo_Classe` (segundo a página de novidades do portal) |
| CVM Dados Abertos, Informe Trimestral de FII: https://dados.cvm.gov.br/dados/FII/DOC/INF_TRIMESTRAL/DADOS/ | Dados trimestrais (imóveis, inquilinos, vacância) | Gratuito |
| FNET da B3: https://fnet.bmfbovespa.com.br/ | Relatórios gerenciais e fatos relevantes em PDF | Gratuito; algumas funções pedem cadastro |
| brapi.dev: https://brapi.dev/docs/fiis | Cotações e dados de FIIs por API | Plano gratuito só dá cotação básica. Dividendos, indicadores e relatórios de FII são do plano Pro (pago) |

Pendente: o cabeçalho real dos arquivos da CVM não foi conferido. Deste ambiente o acesso a `dados.cvm.gov.br` está bloqueado pela regra de rede (`CONNECT tunnel failed, response 403`).

## Projetos abertos parecidos (para aprender)

"Sem licença" significa que dá para ler e aprender, mas não para copiar o código.

| Projeto | O que faz | Linguagem | Licença | Última atualização |
|---|---|---|---|---|
| https://github.com/JonatasDS/fii-intelligence | Coleta CVM e B3, guarda em banco e monta painel de monitoramento de FIIs | Python | sem licença | 2026-09-17 |
| https://github.com/Isaacpk1/fii-offer-radar | Coleta dados da CVM e usa IA para triar ofertas de FIIs, com nota de confiança | Python | MIT | 2026-11-09 |
| https://github.com/esscova/deepFIIs | Lê relatórios de FIIs com IA | Python | sem licença | 2025-04-17 |
| https://github.com/VBGVictor/CVM-FII-Data | Coleta de dados de FII da CVM | Python | sem licença | 2026-10-06 |
| https://github.com/marcelovitorls-rgb/dashboard-fiis | Painel de cotações, dividendos e rendimento de uma carteira | Python (Streamlit) | MIT | 2026-08-03 |
| https://github.com/geeksilva97/kowalski | Extensão de navegador que organiza relatórios do FNET/CVM | TypeScript | sem licença | 2026-03-20 |
| https://github.com/dude333/fiispider | Coleta de informes mensais de FIIs | Python | sem licença | 2021-01-05 (antigo) |
| https://github.com/vmeazevedo/myFII_B3 | Monitoramento de preços de FIIs e ações (86 estrelas) | Python | GPL-3.0 | 2023-01-17 (antigo) |
| https://github.com/k4l1sh/FIIGuru | Ranqueador de FIIs | HTML | MIT | 2021-08-09 (antigo) |

Protótipo acadêmico de painel de FIIs (IFSC): https://repositorio.ifsc.edu.br/handle/1/294

## Leitura

- Tutorial de filtro de FIIs por P/VP e DY em Python: https://brapi.dev/blog/fii-screener-python-filtrar-fundos-imobiliarios-pvp-dy
- Como a brapi lê os relatórios da CVM: https://brapi.dev/blog/relatorios-cvm-fii-composicao-patrimonial-vacancia-api
