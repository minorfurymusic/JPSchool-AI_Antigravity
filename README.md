# Radar de FIIs

Monitor de fundos imobiliários para uso próprio. Usa só dados oficiais (B3 e CVM), detecta saltos e quedas de rendimento e vendas de imóvel, e mede o que aconteceu depois de cada caso parecido desde 2017.

Não é recomendação de investimento.

## Como rodar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m fii.atualizar              # baixa o que falta, refaz as contas e gera dados/painel.html
.venv/bin/python -m fii.atualizar --sem-rede   # só refaz as contas
.venv/bin/python -m pytest -q
```

A primeira rodada baixa cerca de 700 MB (cotações desde 2017) e demora. As seguintes baixam só o dia.

O painel é um arquivo único (`dados/painel.html`) que abre em qualquer navegador.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `fii/coleta.py` | Baixa da B3 e da CVM o que ainda não tem. Nunca apaga o que já baixou |
| `fii/b3_cotacoes.py`, `fii/cvm.py`, `fii/b3_fundos.py` | Leitura de cada fonte, com conferência de formato |
| `fii/base.py` | Liga papel da bolsa ao fundo na CVM, ajusta desdobramentos, monta o histórico mensal |
| `fii/aprendizado.py` | Detecta eventos e mede o que veio depois |
| `fii/oportunidades.py` | Lista do que olhar hoje e registro dos sinais |
| `fii/painel.py`, `fii/painel_molde.html` | Painel |
| `PLANO.md`, `checklist.md`, `PESQUISA.md` | Plano, pendências e pesquisa inicial |

`dados/` (arquivos baixados, banco e painel) não vai para o repositório.
