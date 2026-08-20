from datetime import date
from decimal import Decimal

from src.cambio import converter_para_brl


def test_rn019_brl_nao_sofre_conversao():
    valor = converter_para_brl(
        valor_original=Decimal("100.00"),
        moeda="BRL",
        data=date(2026, 7, 10),
        cotacoes={},
    )

    assert valor == Decimal("100.00")


def test_rn019_converte_usd_com_cotacao_da_data():
    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.20"),
        }
    }

    valor = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor == Decimal("104.00")


def test_rn019_normaliza_resultado_para_centavos():
    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.123"),
        }
    }

    valor = converter_para_brl(
        valor_original=Decimal("10.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor == Decimal("51.23")