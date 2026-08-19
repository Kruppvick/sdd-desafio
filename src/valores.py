from decimal import Decimal


ZERO = Decimal("0.00")


def valor_reembolsavel_basico(
    valor_normalizado: Decimal,
) -> Decimal:
    if valor_normalizado <= ZERO:
        return ZERO

    return valor_normalizado


def participa_total_solicitado(
    valor_normalizado: Decimal,
) -> bool:
    return valor_normalizado > ZERO