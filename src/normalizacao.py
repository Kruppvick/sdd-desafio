from datetime import date
from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")


def normalizar_categoria(categoria: str) -> str:
    return categoria.strip().lower()


def normalizar_valor(valor) -> Decimal:
    decimal = Decimal(str(valor))

    return decimal.quantize(
        CENTAVO,
        rounding=ROUND_HALF_UP,
    )


def normalizar_data(valor: str) -> date:
    return date.fromisoformat(valor)