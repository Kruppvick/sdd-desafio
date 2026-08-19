from decimal import Decimal


ZERO = Decimal("0.00")


def aplicar_limite_diario(
    valor: Decimal,
    limite: Decimal,
    consumido: Decimal,
) -> Decimal:
    disponivel = limite - consumido

    if disponivel <= ZERO:
        return ZERO

    if valor <= disponivel:
        return valor

    return disponivel