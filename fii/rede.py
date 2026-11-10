"""Acesso à internet. As funções de coleta recebem `buscar` como parâmetro,
para que os testes rodem sem rede."""
from __future__ import annotations

import time
from pathlib import Path

import requests


class ErroDeRede(Exception):
    pass


def buscar_bytes(url: str, tentativas: int = 3, espera: float = 2.0, limite_s: int = 300) -> bytes:
    ultimo = None
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=limite_s)
            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise FileNotFoundError(url)
            ultimo = f"resposta {r.status_code}"
        except FileNotFoundError:
            raise
        except requests.RequestException as e:  # falha de rede, não do código
            ultimo = repr(e)
        time.sleep(espera * (2 ** i))
    raise ErroDeRede(f"{url}: {ultimo}")


def baixar(url: str, destino: Path, buscar=buscar_bytes) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(destino.suffix + ".part")
    parcial.write_bytes(buscar(url))
    parcial.replace(destino)
    return destino
