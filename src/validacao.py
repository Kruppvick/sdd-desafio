from datetime import date


def validar_entrada(dados: dict) -> None:
    if not isinstance(dados, dict):
        raise ValueError("A entrada deve ser um objeto JSON.")

    _exigir_campo(dados, "colaborador")
    _exigir_campo(dados, "periodo")
    _exigir_campo(dados, "despesas")

    _validar_colaborador(dados["colaborador"])
    _validar_periodo(dados["periodo"])
    _validar_despesas(dados["despesas"])


def _exigir_campo(dados: dict, campo: str) -> None:
    if campo not in dados:
        raise ValueError(
            f"Campo obrigatório ausente: {campo}"
        )


def _validar_colaborador(colaborador: dict) -> None:
    if not isinstance(colaborador, dict):
        raise ValueError(
            "colaborador deve ser um objeto."
        )

    for campo in (
        "id",
        "nome",
        "centro_custo",
    ):
        _exigir_campo(colaborador, campo)


def _validar_periodo(periodo: dict) -> None:
    if not isinstance(periodo, dict):
        raise ValueError(
            "periodo deve ser um objeto."
        )

    for campo in (
        "competencia",
        "inicio",
        "fim",
    ):
        _exigir_campo(periodo, campo)

    try:
        date.fromisoformat(periodo["inicio"])
        date.fromisoformat(periodo["fim"])
    except (TypeError, ValueError) as erro:
        raise ValueError(
            "Datas do período devem usar o formato AAAA-MM-DD."
        ) from erro


def _validar_despesas(despesas: list) -> None:
    if not isinstance(despesas, list):
        raise ValueError(
            "despesas deve ser uma lista."
        )

    campos_obrigatorios = (
        "id",
        "data",
        "categoria",
        "descricao",
        "fornecedor",
        "valor",
        "tem_nota_fiscal",
    )

    for indice, despesa in enumerate(despesas):
        if not isinstance(despesa, dict):
            raise ValueError(
                f"Despesa no índice {indice} deve ser um objeto."
            )

        for campo in campos_obrigatorios:
            if campo not in despesa:
                raise ValueError(
                    f"Campo obrigatório ausente na despesa "
                    f"{indice}: {campo}"
                )

        try:
            date.fromisoformat(despesa["data"])
        except (TypeError, ValueError) as erro:
            raise ValueError(
                f"Data inválida na despesa {indice}."
            ) from erro