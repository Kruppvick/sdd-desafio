from decimal import Decimal


ZERO = Decimal("0.00")


def completar_resultado(
    valor_solicitado,
    valor_reembolsavel,
    motivos,
):
    if valor_solicitado <= ZERO:
        valor_nao_reembolsavel = ZERO
    else:
        valor_nao_reembolsavel = (
            valor_solicitado - valor_reembolsavel
        )

    if valor_reembolsavel == ZERO:
        status = "RECUSADA"
    elif valor_reembolsavel == valor_solicitado:
        status = "APROVADA"
    else:
        status = "PARCIAL"

    return {
        "valor_solicitado": valor_solicitado,
        "valor_reembolsavel": valor_reembolsavel,
        "valor_nao_reembolsavel": valor_nao_reembolsavel,
        "status": status,
        "motivos": motivos,
    }


def calcular_resumo(resultados):
    total_solicitado = ZERO
    total_reembolsavel = ZERO
    total_nao_reembolsavel = ZERO

    for resultado in resultados:
        solicitado = resultado["valor_solicitado"]

        if solicitado > ZERO:
            total_solicitado += solicitado
            total_nao_reembolsavel += (
                resultado["valor_nao_reembolsavel"]
            )

        total_reembolsavel += resultado["valor_reembolsavel"]

    return {
        "total_solicitado": total_solicitado,
        "total_reembolsavel": total_reembolsavel,
        "total_nao_reembolsavel": total_nao_reembolsavel,
    }