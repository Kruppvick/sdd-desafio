from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")


def _normalizar_centavos(valor: Decimal) -> Decimal:
    return valor.quantize(
        CENTAVO,
        rounding=ROUND_HALF_UP,
    )


def converter_para_brl(
    *,
    valor_original: Decimal,
    moeda: str,
    data,
    cotacoes: dict,
) -> Decimal:
    if moeda == "BRL":
        return _normalizar_centavos(valor_original)

    taxa = cotacoes[moeda][data]

    valor_brl = valor_original * taxa

    return _normalizar_centavos(valor_brl)