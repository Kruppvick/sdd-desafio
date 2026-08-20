from decimal import Decimal

import pytest

from src.normalizacao import (
    normalizar_categoria,
    normalizar_valor,
)


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("alimentacao", "alimentacao"),
        ("ALIMENTACAO", "alimentacao"),
        (" alimentacao ", "alimentacao"),
        ("Transporte_Urbano", "transporte_urbano"),
    ],
)
def test_rn010_normaliza_categoria(entrada, esperado):
    assert normalizar_categoria(entrada) == esperado


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("33.333", Decimal("33.33")),
        ("33.335", Decimal("33.34")),
        ("100", Decimal("100.00")),
        ("60.0", Decimal("60.00")),
    ],
)
def test_rn011_normaliza_valor(entrada, esperado):
    assert normalizar_valor(entrada) == esperado

def test_rn018_moeda_ausente_assume_brl():
    from src.normalizacao import normalizar_moeda

    assert normalizar_moeda(None) == "BRL"


def test_rn018_normaliza_moeda_minuscula():
    from src.normalizacao import normalizar_moeda

    assert normalizar_moeda("usd") == "USD"


def test_rn018_normaliza_moeda_com_espacos():
    from src.normalizacao import normalizar_moeda

    assert normalizar_moeda(" USD ") == "USD"


def test_rn018_preserva_brl():
    from src.normalizacao import normalizar_moeda

    assert normalizar_moeda("BRL") == "BRL"   