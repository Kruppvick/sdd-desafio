from decimal import Decimal


LIMITE_SEM_NOTA = Decimal("100.00")


def nota_fiscal_valida(
    valor_normalizado: Decimal,
    tem_nota_fiscal: bool,
) -> bool:
    if valor_normalizado <= LIMITE_SEM_NOTA:
        return True

    return tem_nota_fiscal