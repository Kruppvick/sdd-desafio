CATEGORIAS_REEMBOLSAVEIS = {
    "alimentacao",
    "transporte_urbano",
    "hospedagem",
}


def categoria_reembolsavel(categoria_normalizada: str) -> bool:
    return categoria_normalizada in CATEGORIAS_REEMBOLSAVEIS