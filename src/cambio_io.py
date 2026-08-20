from datetime import date
from decimal import Decimal


def preparar_cotacoes(dados: dict) -> dict:
    resultado = {}

    for data_texto, taxas in dados["taxas"].items():
        data_cotacao = date.fromisoformat(
            data_texto
        )

        for moeda, taxa in taxas.items():
            resultado.setdefault(
                moeda,
                {},
            )[data_cotacao] = Decimal(
                str(taxa)
            )

    return resultado