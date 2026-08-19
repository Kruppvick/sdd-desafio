from decimal import Decimal

import pytest

from src.nota_fiscal import nota_fiscal_valida


@pytest.mark.parametrize(
    ("valor", "tem_nota_fiscal", "esperado"),
    [
        (Decimal("99.99"), False, True),
        (Decimal("100.00"), False, True),
        (Decimal("100.01"), False, False),
        (Decimal("100.01"), True, True),
    ],
)
def test_rn005_obrigatoriedade_de_nota_fiscal(
    valor,
    tem_nota_fiscal,
    esperado,
):
    assert nota_fiscal_valida(
        valor,
        tem_nota_fiscal,
    ) is esperado