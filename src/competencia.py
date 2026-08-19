from datetime import date


def dentro_da_competencia(
    data_despesa: date,
    inicio: date,
    fim: date,
) -> bool:
    return inicio <= data_despesa <= fim