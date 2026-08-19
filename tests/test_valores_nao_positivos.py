from decimal import Decimal

import pytest

from src.valores import valor_reembolsavel_basico
from src.valores import participa_total_solicitado


@pytest.mark.parametrize(
    "valor",
    [
        Decimal("0.00"),
        Decimal("-0.01"),
        Decimal("-45.00"),
    ],
)
def test_rn012_valor_nao_positivo_nao_e_reembolsavel(valor):
    assert valor_reembolsavel_basico(valor) == Decimal("0.00")


@pytest.mark.parametrize(
    "valor",
    [
        Decimal("0.00"),
        Decimal("-0.01"),
        Decimal("-45.00"),
    ],
)
def test_rn012_valor_nao_positivo_nao_participa_total(valor):
    assert participa_total_solicitado(valor) is False


@pytest.mark.parametrize(
    "valor",
    [
        Decimal("0.01"),
        Decimal("10.00"),
        Decimal("100.00"),
    ],
)
def test_rn012_valor_positivo_participa_total(valor):
    assert participa_total_solicitado(valor) is True