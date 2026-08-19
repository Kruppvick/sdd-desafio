from decimal import Decimal

import pytest

from src.limites import aplicar_limite_por_item


@pytest.mark.parametrize(
    ("valor", "reembolsavel"),
    [
        (Decimal("249.99"), Decimal("249.99")),
        (Decimal("250.00"), Decimal("250.00")),
        (Decimal("250.01"), Decimal("250.00")),
        (Decimal("480.00"), Decimal("250.00")),
    ],
)
def test_rn003_limite_hospedagem(
    valor,
    reembolsavel,
):
    assert aplicar_limite_por_item(
        valor=valor,
        limite=Decimal("250.00"),
    ) == reembolsavel


def test_rn003_descricao_nao_altera_quantidade_de_diarias():
    valor = Decimal("480.00")

    reembolsavel = aplicar_limite_por_item(
        valor=valor,
        limite=Decimal("250.00"),
    )

    assert reembolsavel == Decimal("250.00")