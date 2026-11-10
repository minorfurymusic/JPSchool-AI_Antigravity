"""Baixa o que falta das fontes oficiais. Nunca apaga o que já foi baixado."""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

from . import b3_cotacoes, b3_fundos, config
from .rede import ErroDeRede, baixar, buscar_bytes


def coletar_cvm(hoje: dt.date, buscar=buscar_bytes, pasta: Path | None = None) -> list[str]:
    """Os arquivos da CVM são regravados pela CVM; os 2 anos mais recentes são sempre baixados de novo."""
    pasta = pasta or config.BRUTO_CVM
    feitos = []
    for grupo, sub in (("inf_mensal_fii", "INF_MENSAL"), ("inf_trimestral_fii", "INF_TRIMESTRAL")):
        for ano in range(config.PRIMEIRO_ANO_CVM, hoje.year + 1):
            nome = f"{grupo}_{ano}.zip"
            if (pasta / nome).exists() and ano < hoje.year - 1:
                continue
            try:
                baixar(config.URL_CVM.format(pasta=sub, nome=nome), pasta / nome, buscar)
                feitos.append(nome)
            except FileNotFoundError:
                pass  # ano ainda sem arquivo
    return feitos


def coletar_cotacoes(hoje: dt.date, buscar=buscar_bytes, pasta: Path | None = None, ultimo_pregao: dt.date | None = None) -> list[str]:
    """Arquivo anual uma vez; depois, um arquivo por dia a partir do último pregão que já temos."""
    pasta = pasta or config.BRUTO_B3
    feitos = []
    for ano in range(config.PRIMEIRO_ANO_PRECO, hoje.year + 1):
        nome = b3_cotacoes.nome_anual(ano)
        if not (pasta / nome).exists():
            baixar(config.URL_COTAHIST.format(nome=nome), pasta / nome, buscar)
            feitos.append(nome)
    dia = (ultimo_pregao or hoje - dt.timedelta(days=7)) + dt.timedelta(days=1)
    while dia <= hoje:
        nome = b3_cotacoes.nome_diario(dia)
        if dia.weekday() < 5 and not (pasta / nome).exists():
            try:
                baixar(config.URL_COTAHIST.format(nome=nome), pasta / nome, buscar)
                feitos.append(nome)
            except FileNotFoundError:
                pass  # feriado ou arquivo do dia ainda não publicado
        dia += dt.timedelta(days=1)
    return feitos


def _buscar_curto(url: str) -> bytes:
    """Consulta pequena: não vale esperar minutos por uma resposta."""
    return buscar_bytes(url, tentativas=2, limite_s=40)


def coletar_fundos_b3(codigos: list[str], buscar=_buscar_curto, pasta: Path | None = None,
                      pausa: float = 0.15, validade_h: float = 12) -> dict:
    """Rendimentos anunciados, desdobramentos e subscrições, por código do papel (4 letras)."""
    pasta = pasta or config.BRUTO_FUNDOS
    pasta.mkdir(parents=True, exist_ok=True)
    ok = falha = pulados = 0
    for cod in codigos:
        arq = pasta / f"{cod}.json"
        if arq.exists() and time.time() - arq.stat().st_mtime < validade_h * 3600:
            pulados += 1
            continue
        try:
            dado = b3_fundos.interpretar(buscar(b3_fundos.url_fundo("0", cod)))
        except (ErroDeRede, ValueError):
            falha += 1
            continue
        arq.write_text(json.dumps(acumular(json.loads(arq.read_text()) if arq.exists() else None, dado), ensure_ascii=False))
        ok += 1
        time.sleep(pausa)
    return {"baixados": ok, "falhas": falha, "ja_tinham": pulados}


def acumular(antigo: dict | None, novo: dict | None) -> dict | None:
    """A B3 só mostra os últimos ~12 meses. O que já foi visto fica guardado:
    o novo entra, o antigo nunca é apagado."""
    if not novo:
        return antigo
    if not antigo:
        return novo
    saida = dict(novo)
    for campo in ("rendimentos", "desdobramentos", "subscricoes"):
        vistos = {json.dumps(x, sort_keys=True) for x in novo.get(campo, [])}
        saida[campo] = list(novo.get(campo, [])) + [x for x in antigo.get(campo, [])
                                                    if json.dumps(x, sort_keys=True) not in vistos]
    return saida


def ler_fundos_b3(pasta: Path | None = None) -> dict:
    pasta = pasta or config.BRUTO_FUNDOS
    saida = {}
    for arq in sorted(pasta.glob("*.json")):
        dado = json.loads(arq.read_text())
        if dado:
            saida[arq.stem] = dado
    return saida
