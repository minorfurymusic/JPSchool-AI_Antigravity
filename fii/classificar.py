"""Classifica o texto de um fato relevante ou comunicado por palavras, sem IA.

É a primeira peneira: barata, igual toda vez, e dá para conferir. Diz o TIPO do
anúncio e tenta achar o valor em reais por cota que o próprio fundo informa.
A leitura por IA entra depois, para os casos que esta peneira marcar como dúvida.
"""
from __future__ import annotations

import re
import unicodedata


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


IMOVEL = r"(imove|ativo|galpa|laje|loja|edific|empreendimento|fracao ideal|participacao|shopping|terreno|unidade|conjunto|andar|predio|condominio)"
VENDA = r"(alienac|alienou|alienar|\bvenda\b|\bvendeu\b|vender\b|compromisso de (compra e )?venda|promessa de (compra e )?venda|desinvestimento)"
REGRAS = [
    # (tipo, padrão, sentido para o rendimento)
    ("rendimento_reducao", r"(reduc|redu[cz]ir|diminu|queda|suspens|suspend|interromp)\w*[^.]{0,90}(rendimento|distribuic|provento)", "queda"),
    ("rendimento_aumento", r"(aument|elev|increment|acrescim|major|ampli)\w*[^.]{0,90}(rendimento|distribuic|provento)s?"
                           r"|(rendimento|distribuic)\w*[^.]{0,30}extraordinari|impacto positivo[^.]{0,120}(distribuic|rendimento|por cota)"
                           r"|(guidance|patamar|expectativa|projec|estimativa)[^.]{0,80}(rendimento|distribuic)", "alta"),
    ("venda", VENDA + r"[^.]{0,160}" + IMOVEL + "|" + IMOVEL + r"[^.]{0,120}" + VENDA, "alta"),
    ("recebimento", r"(multa|indenizac|premio de locacao|luvas|sinal|parcela)[^.]{0,120}(receb|pag)\w*|receb\w*[^.]{0,120}(multa|indenizac)", "alta"),
    ("locacao_nova", r"(nov[oa]s? (contrato|locac|locatari|inquilin)|celebr\w+[^.]{0,80}(contrato|instrumento)[^.]{0,60}locac|locou\b|assin\w+[^.]{0,60}contrato de locac"
                     r"|reduc\w*[^.]{0,40}vacancia|aditamento[^.]{0,80}locac|renovac\w*[^.]{0,60}(contrato|locac)|revisional)", "alta"),
    ("saida_inquilino", r"(rescis|rescind|desocupac|devoluc\w*[^.]{0,40}(imovel|area|espaco)|denuncia\w*[^.]{0,40}contrato|nao renovac|notificac\w*[^.]{0,80}(desocup|rescis)"
                        r"|inadimpl|recuperacao judicial|atraso\w*[^.]{0,40}(aluguel|pagamento))", "queda"),
    ("aquisicao", r"(aquisic|adquir)\w*[^.]{0,160}" + IMOVEL, "neutro"),
    ("emissao", r"(emissao de (novas )?cotas|oferta (publica|restrita)|direito de preferencia|subscric)", "neutro"),
    ("reorganizacao", r"(incorporac|cisao|fusao|liquidac\w* do fundo|substituic\w*[^.]{0,40}(administrador|gestor)|desdobramento|grupamento)", "neutro"),
]
REGRAS = [(t, re.compile(p), s) for t, p, s in REGRAS]
CONTINUACAO = re.compile(r"em (continuidade|complemento|aditamento|referencia) a[o]? (fato relevante|comunicado)")
# valor por cota: "R$ 2,49 (dois reais...) por cota", "R$ 0,12/cota", "R$0,05 por cota"
POR_COTA = re.compile(r"r\$ ?(\d{1,3}(?:\.\d{3})*(?: ?, ?\d{1,6})?|\d+(?: ?, ?\d{1,6})?)\s*(?:\([^)]{0,120}\))?\s*(?:/|por|a cada|p/)\s*cota")
BOM = re.compile(r"(lucro|ganho|resultado|impacto|increment|acrescim|distribu|rendimento|receita|adicional|extraordin|amortiz)")
RUIM = re.compile(r"(preco de emissao|valor patrimonial|valor de mercado|cotacao|negociac|subscric|custo de aquisicao|preco por cota|taxa)")


def valores_por_cota(norm: str) -> list[dict]:
    """Valores em R$ por cota citados no texto, com o trecho em volta. Marca os que falam de resultado/rendimento."""
    achados = []
    for m in POR_COTA.finditer(norm):
        bruto = m.group(1).replace(" ", "").replace(".", "").replace(",", ".")
        try:
            v = float(bruto)
        except ValueError:
            continue
        antes = norm[max(0, m.start() - 220):m.start()]
        depois = norm[m.end():m.end() + 80]
        frase = antes.rsplit(". ", 1)[-1]  # só a frase em que o valor aparece
        ruim = RUIM.search(frase[-110:]) is not None
        bom = BOM.search(frase) is not None or BOM.search(depois) is not None
        achados.append({"valor": v, "de_resultado": bool(bom and not ruim), "trecho": norm[max(0, m.start() - 120):m.end() + 40]})
    return achados


# frases de rodapé que falam em "venda" sem ser notícia (aviso legal, canal de atendimento)
RODAPE = re.compile(r"(nao (constitui|representa|deve ser)[^.]{0,120}(oferta|recomendac|solicitac)[^.]*\.?"
                    r"|(oferta|recomendac|solicitac|decisao)[^.]{0,80}(compra|venda)[^.]{0,80}(cotas|valores mobiliarios|ativos financeiros)[^.]*\.?"
                    r"|compra (e|ou) venda de (cotas|valores mobiliarios)"
                    r"|rentabilidade (passada|obtida no passado)[^.]*\.?|fundo garantidor de creditos[^.]*\.?)")
DESAGIO = re.compile(r"(venda|alienac)\w*[^.]{0,60}(com desagio|com prejuizo|abaixo do (custo|valor (contabil|patrimonial)))|prejuizo (apurado|na (venda|operacao))")
GANHO = re.compile(r"(lucro|ganho de capital|ganho estimado|resultado (liquido|positivo|estimado|da (venda|transacao|operacao))|\btir\b|taxa interna de retorno|acima do (custo|valor (contabil|patrimonial|de aquisicao|de avaliacao|do laudo)))")


# o fundo diz o efeito no rendimento: "a receita será impactada positivamente em 6,80%, gerando um impacto
# positivo na distribuição de rendimentos de aproximadamente 10,58%" / "impactada negativamente em R$ 1,90 por cota"
FRASE_IMPACTO = re.compile(r"[^.;]{0,260}\bimpact\w+[^.;]{0,320}")
ASSUNTO = re.compile(r"(distribuic|rendimento|provento|receita|resultado|renda mensal)")
SEM_EFEITO = re.compile(r"(\bnao\b|\bsem\b|nenhum|qualquer)[^.;]{0,50}impact|impact\w+[^.;]{0,90}(apenas poder|somente poder|nao e possivel|oportunamente|ainda nao|serao (informad|divulgad)|a ser (apurad|determinad))"
                        r"|(eventua(l|is)|possive(l|is)|potencia(l|is)) impact")
SOBE = re.compile(r"(positiv|increment|aument|acrescim|elev|adicional)")
DESCE = re.compile(r"(negativ|reduc|reduz|queda|diminu|perda)")
PCT = re.compile(r"(\d{1,4}(?: ?, ?\d{1,4})?) ?%")


def _num(txt: str) -> float | None:
    try:
        return float(txt.replace(" ", "").replace(".", "").replace(",", "."))
    except ValueError:
        return None


def impacto_declarado(norm: str) -> dict | None:
    """Primeira frase em que o fundo declara efeito no rendimento. Devolve direção (+1/-1),
    percentual (se disser) e valor por cota (se disser). None quando não declara ou diz que não sabe."""
    for m in FRASE_IMPACTO.finditer(norm):
        frase = m.group(0)
        if not ASSUNTO.search(frase) or SEM_EFEITO.search(frase):
            continue
        apos = frase[frase.find("impact"):]
        sobe, desce = SOBE.search(apos[:120]), DESCE.search(apos[:120])
        if bool(sobe) == bool(desce):
            if sobe and desce:  # os dois aparecem: vale o que vem primeiro depois de "impact"
                direcao = 1 if sobe.start() < desce.start() else -1
            else:
                continue
        else:
            direcao = 1 if sobe else -1
        # percentual: de preferência o que vem depois de "distribuição/rendimento" (o da receita costuma vir antes)
        pos = min((x.start() for x in re.finditer(r"distribuic|rendimento|provento", apos)), default=-1)
        pcts = [(x.start(), _num(x.group(1))) for x in PCT.finditer(apos)]
        pcts = [(i, v) for i, v in pcts if v is not None and 0 < v <= 2000]
        depois = [v for i, v in pcts if i > pos >= 0]
        pct = (depois[0] if depois else pcts[0][1] if pcts else None)
        vals = [v["valor"] for v in valores_por_cota(apos) if 0 < v["valor"] < 1000]
        return {"direcao": direcao, "pct": pct / 100 if pct is not None else None, "valor_por_cota": vals[0] if vals else None,
                "frase": frase.strip()[:400]}
    return None


def classificar(texto: str) -> dict:
    """Devolve tipos encontrados (em ordem de prioridade), sentido provável para o rendimento,
    valor por cota informado (se houver) e se é continuação de anúncio anterior."""
    norm = RODAPE.sub(" ", normalizar(texto))
    tipos = [(t, s) for t, p, s in REGRAS if p.search(norm)]
    nomes = [t for t, _ in tipos]
    if "venda" in nomes and DESAGIO.search(norm):
        nomes[nomes.index("venda")] = "venda_com_perda"
    elif "venda" in nomes and GANHO.search(norm):
        nomes[nomes.index("venda")] = "venda_com_ganho"
    sentidos = {s for _, s in tipos}
    if "rendimento_reducao" in nomes and "rendimento_aumento" not in nomes:
        sentido = "queda"
    elif "alta" in sentidos and "queda" not in sentidos:
        sentido = "alta"
    elif "queda" in sentidos and "alta" not in sentidos:
        sentido = "queda"
    elif "alta" in sentidos and "queda" in sentidos:
        sentido = "misto"
    else:
        sentido = "neutro"
    vals = valores_por_cota(norm)
    bons = [v["valor"] for v in vals if v["de_resultado"] and 0 < v["valor"] < 1000]
    return {"tipos": nomes, "tipo": nomes[0] if nomes else "outro", "sentido": sentido, "impacto": impacto_declarado(norm),
            "valor_por_cota": max(bons) if bons else None, "valores_citados": len(vals),
            "continuacao": CONTINUACAO.search(norm[:2500]) is not None, "tamanho": len(norm)}
