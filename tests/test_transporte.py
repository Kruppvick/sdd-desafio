from decimal import Decimal

import pytest

from src.limites import aplicar_limite_diario


@pytest.mark.parametrize(
    ("valor", "consumido", "reembolsavel"),
    [
        (Decimal("79.99"), Decimal("0.00"), Decimal("79.99")),
        (Decimal("80.00"), Decimal("0.00"), Decimal("80.00")),
        (Decimal("80.01"), Decimal("0.00"), Decimal("80.00")),
        (Decimal("50.00"), Decimal("50.00"), Decimal("30.00")),
        (Decimal("10.00"), Decimal("80.00"), Decimal("0.00")),
    ],
)
def test_rn002_limite_diario_transporte(
    valor,
    consumido,
    reembolsavel,
):
    assert aplicar_limite_diario(
        valor=valor,
        limite=Decimal("80.00"),
        consumido=consumido,
    ) == reembolsavel


def test_rn014_transporte_respeita_ordem_da_entrada():
    consumido = Decimal("0.00")

    primeiro = aplicar_limite_diario(
        valor=Decimal("50.00"),
        limite=Decimal("80.00"),
        consumido=consumido,
    )
    consumido += primeiro

    segundo = aplicar_limite_diario(
        valor=Decimal("50.00"),
        limite=Decimal("80.00"),
        consumido=consumido,
    )

    assert primeiro == Decimal("50.00")
    assert segundo == Decimal("30.00")
    assert primeiro + segundo == Decimal("80.00")