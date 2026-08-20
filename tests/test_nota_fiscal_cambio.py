from datetime import date
from decimal import Decimal

from src.cambio import converter_para_brl
from src.nota_fiscal import nota_fiscal_valida


def test_rn005_valor_convertido_100_nao_exige_nota():
    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.00"),
        }
    }

    valor_brl = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor_brl == Decimal("100.00")
    assert nota_fiscal_valida(
        valor_brl,
        False,
    )


def test_rn005_valor_convertido_100_01_exige_nota():
    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.0005"),
        }
    }

    valor_brl = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor_brl == Decimal("100.01")
    assert not nota_fiscal_valida(
        valor_brl,
        False,
    )


def test_rn024_valor_original_nao_define_limite_documental():
    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.10"),
        }
    }

    valor_original = Decimal("20.00")

    valor_brl = converter_para_brl(
        valor_original=valor_original,
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor_original < Decimal("100.00")
    assert valor_brl == Decimal("102.00")
    assert not nota_fiscal_valida(
        valor_brl,
        False,
    )