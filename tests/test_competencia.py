from datetime import date

import pytest

from src.competencia import dentro_da_competencia


@pytest.mark.parametrize(
    ("data_despesa", "inicio", "fim", "esperado"),
    [
        (
            date(2026, 7, 1),
            date(2026, 7, 1),
            date(2026, 7, 31),
            True,
        ),
        (
            date(2026, 7, 31),
            date(2026, 7, 1),
            date(2026, 7, 31),
            True,
        ),
        (
            date(2026, 6, 30),
            date(2026, 7, 1),
            date(2026, 7, 31),
            False,
        ),
        (
            date(2026, 8, 1),
            date(2026, 7, 1),
            date(2026, 7, 31),
            False,
        ),
    ],
)
def test_rn007_verifica_periodo_de_competencia(
    data_despesa,
    inicio,
    fim,
    esperado,
):
    assert dentro_da_competencia(
        data_despesa,
        inicio,
        fim,
    ) is esperado