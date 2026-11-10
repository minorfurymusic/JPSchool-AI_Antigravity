"""Dados que a B3 publica por fundo listado: rendimentos anunciados,
desdobramentos e subscrições. Serviço usado pelo site da B3, sem documentação
pública: pode mudar, por isso toda leitura é conferida."""
from __future__ import annotations

import base64
import json
from datetime import datetime

from . import config
from .rede import buscar_bytes


def _data(txt):
    try:
        return datetime.strptime(txt, "%d/%m/%Y").date().isoformat()
    except (ValueError, TypeError):
        return None


def _num(txt):
    try:
        return float(str(txt).replace(".", "").replace(",", "."))
    except ValueError:
        return None


def so_digitos(cnpj: str) -> str:
    return "".join(ch for ch in cnpj if ch.isdigit())


def url_fundo(cnpj: str, codigo: str) -> str:
    corpo = json.dumps({"cnpj": so_digitos(cnpj), "identifierFund": codigo, "typeFund": 7}, separators=(",", ":"))
    return config.URL_B3_FUNDO.format(param=base64.b64encode(corpo.encode()).decode())


def interpretar(bruto: bytes) -> dict | None:
    """Converte a resposta da B3. None quando a B3 não reconhece o par CNPJ + código."""
    if not bruto.strip():
        return None
    d = json.loads(bruto)
    if not isinstance(d, dict) or not d.get("code"):
        return None
    rend = [{"isin": x.get("isinCode"), "tipo": x.get("label"), "valor": _num(x.get("rate")),
             "referencia": x.get("relatedTo"), "anuncio": _data(x.get("approvedOn")),
             "data_com": _data(x.get("lastDatePrior")), "pagamento": _data(x.get("paymentDate"))}
            for x in d.get("cashDividends") or []]
    desd = [{"isin": x.get("isinCode"), "tipo": x.get("label"), "fator": _num(x.get("factor")),
             "data_com": _data(x.get("lastDatePrior"))} for x in d.get("stockDividends") or []]
    subs = [{"isin": x.get("isinCode"), "percentual": _num(x.get("percentage")), "preco": _num(x.get("priceUnit")),
             "anuncio": _data(x.get("approvedOn")), "data_com": _data(x.get("lastDatePrior"))}
            for x in d.get("subscriptions") or []]
    return {"codigo": d.get("code"), "nome": d.get("fund"), "rendimentos": rend,
            "desdobramentos": desd, "subscricoes": subs}


def consultar(cnpj: str, codigo: str, buscar=buscar_bytes) -> dict | None:
    return interpretar(buscar(url_fundo(cnpj, codigo)))
