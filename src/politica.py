def selecionar_politica(
    politica: dict,
    centro_custo: str,
) -> dict:
    centros_custo = politica.get(
        "centros_custo",
        {},
    )

    if centro_custo in centros_custo:
        return centros_custo[centro_custo]

    return politica["padrao"]