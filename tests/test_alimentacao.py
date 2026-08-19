from decimal import Decimal

import pytest

from src.limites import aplicar_limite_diario


@pytest.mark.parametrize(
    ("valor", "consumido", "reembolsavel"),
    [
        (Decimal("59.99"), Decimal("0.00"), Decimal("59.99")),
        (Decimal("60.00"), Decimal("0.00"), Decimal("60.00")),
        (Decimal("60.01"), Decimal("0.00"), Decimal("60.00")),
        (Decimal("30.00"), Decimal("40.00"), Decimal("20.00")),
        (Decimal("10.00"), Decimal("60.00"), Decimal("0.00")),
    ],
)
def test_rn001_limite_diario_alimentacao(
    valor,
    consumido,
    reembolsavel,
):
    assert aplicar_limite_diario(
        valor=valor,
        limite=Decimal("60.00"),
        consumido=consumido,
    ) == reembolsavel


def test_rn014_ordem_da_entrada_distribui_limite():
    consumido = Decimal("0.00")

    primeiro = aplicar_limite_diario(
        valor=Decimal("40.00"),
        limite=Decimal("60.00"),
        consumido=consumido,
    )
    consumido += primeiro

    segundo = aplicar_limite_diario(
        valor=Decimal("30.00"),
        limite=Decimal("60.00"),
        consumido=consumido,
    )

    assert primeiro == Decimal("40.00")
    assert segundo == Decimal("20.00")
    assert primeiro + segundo == Decimal("60.00")


def test_rn014_ordem_inversa_altera_distribuicao():
    consumido = Decimal("0.00")

    primeiro = aplicar_limite_diario(
        valor=Decimal("30.00"),
        limite=Decimal("60.00"),
        consumido=consumido,
    )
    consumido += primeiro

    segundo = aplicar_limite_diario(
        valor=Decimal("40.00"),
        limite=Decimal("60.00"),
        consumido=consumido,
    )

    assert primeiro == Decimal("30.00")
    assert segundo == Decimal("30.00")
    assert primeiro + segundo == Decimal("60.00")