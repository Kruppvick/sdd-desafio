DESCRICOES_MOTIVOS = {
    "LIMITE_DIARIO_ALIMENTACAO": (
        "O limite diário disponível para alimentação foi atingido."
    ),
    "LIMITE_DIARIO_TRANSPORTE": (
        "O limite diário disponível para transporte urbano foi atingido."
    ),
    "LIMITE_HOSPEDAGEM": (
        "O valor da hospedagem ultrapassa o limite reembolsável por diária."
    ),
    "NOTA_FISCAL_OBRIGATORIA": (
        "Despesas acima de R$ 100,00 exigem nota fiscal."
    ),
    "CATEGORIA_NAO_REEMBOLSAVEL": (
        "A categoria informada não é reembolsável pela política."
    ),
    "DUPLICATA": (
        "O lançamento foi identificado como duplicado."
    ),
    "FORA_COMPETENCIA": (
        "A despesa está fora do período de competência."
    ),
    "VALOR_NAO_POSITIVO": (
        "Despesas com valor menor ou igual a zero não são reembolsáveis."
    ),
}


def descricao_motivo(codigo: str) -> str:
    return DESCRICOES_MOTIVOS[codigo]