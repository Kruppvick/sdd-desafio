from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")


def _normalizar_centavos(valor: Decimal) -> Decimal:
    return valor.quantize(
        CENTAVO,
        rounding=ROUND_HALF_UP,
    )


def _buscar_cotacao(
    *,
    moeda: str,
    data,
    cotacoes: dict,
) -> Decimal:
    cotacoes_moeda = cotacoes[moeda]

    if data in cotacoes_moeda:
        return cotacoes_moeda[data]

    datas_anteriores = [
        data_cotacao
        for data_cotacao in cotacoes_moeda
        if data_cotacao < data
    ]

    data_aplicavel = max(datas_anteriores)

    return cotacoes_moeda[data_aplicavel]


def converter_para_brl(
    *,
    valor_original: Decimal,
    moeda: str,
    data,
    cotacoes: dict,
) -> Decimal:
    if moeda == "BRL":
        return _normalizar_centavos(
            valor_original
        )

    taxa = _buscar_cotacao(
        moeda=moeda,
        data=data,
        cotacoes=cotacoes,
    )

    valor_brl = valor_original * taxa

    return _normalizar_centavos(
        valor_brl
    )