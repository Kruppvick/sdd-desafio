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

def test_rn020_usa_cotacao_anterior_mais_recente():
    cotacoes = {
        "USD": {
            date(2026, 7, 9): Decimal("5.10"),
            date(2026, 7, 11): Decimal("5.30"),
        }
    }

    valor = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor == Decimal("102.00")


def test_rn020_escolhe_a_mais_recente_entre_cotacoes_anteriores():
    cotacoes = {
        "USD": {
            date(2026, 7, 7): Decimal("5.00"),
            date(2026, 7, 8): Decimal("5.05"),
            date(2026, 7, 9): Decimal("5.10"),
        }
    }

    valor = converter_para_brl(
        valor_original=Decimal("10.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor == Decimal("51.00")

def test_rn021_moeda_sem_cotacao_retorna_none():
    valor = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="GBP",
        data=date(2026, 7, 10),
        cotacoes={},
    )

    assert valor is None


def test_rn021_nao_utiliza_cotacao_futura():
    cotacoes = {
        "USD": {
            date(2026, 7, 11): Decimal("5.30"),
        }
    }

    valor = converter_para_brl(
        valor_original=Decimal("20.00"),
        moeda="USD",
        data=date(2026, 7, 10),
        cotacoes=cotacoes,
    )

    assert valor is None