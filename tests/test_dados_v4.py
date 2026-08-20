from decimal import Decimal

from src.cambio_io import preparar_cotacoes
from src.politica_io import preparar_politica


def test_prepara_politica_v4():
    dados = {
        "padrao": {
            "alimentacao": {
                "limite": 60.00,
                "periodicidade": "dia",
            }
        },
        "centros_custo": {
            "CC-COMERCIAL": {
                "alimentacao": {
                    "limite": 90.00,
                    "periodicidade": "dia",
                },
                "representacao": {
                    "limite": 300.00,
                    "periodicidade": "dia",
                },
            }
        },
    }

    politica = preparar_politica(dados)

    assert (
        politica["padrao"]["alimentacao"]
        == Decimal("60.0")
    )

    assert (
        politica["centros_custo"]["CC-COMERCIAL"]["alimentacao"]
        == Decimal("90.0")
    )

    assert (
        politica["centros_custo"]["CC-COMERCIAL"]["representacao"]
        == Decimal("300.0")
    )


def test_prepara_cotacoes_v4():
    dados = {
        "taxas": {
            "2026-07-13": {
                "USD": 5.42,
                "EUR": 5.91,
            }
        }
    }

    cotacoes = preparar_cotacoes(dados)

    assert (
        cotacoes["USD"][
            __import__("datetime").date(2026, 7, 13)
        ]
        == Decimal("5.42")
    )

    assert (
        cotacoes["EUR"][
            __import__("datetime").date(2026, 7, 13)
        ]
        == Decimal("5.91")
    )