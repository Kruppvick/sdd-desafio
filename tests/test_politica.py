def test_rn016_seleciona_politica_especifica():
    from src.politica import selecionar_politica

    politica = {
        "padrao": {
            "alimentacao": "60.00",
        },
        "centros_custo": {
            "CC-ENG": {
                "alimentacao": "90.00",
            }
        },
    }

    selecionada = selecionar_politica(
        politica=politica,
        centro_custo="CC-ENG",
    )

    assert selecionada == {
        "alimentacao": "90.00",
    }


def test_rn016_usa_politica_padrao_quando_centro_nao_existe():
    from src.politica import selecionar_politica

    politica = {
        "padrao": {
            "alimentacao": "60.00",
        },
        "centros_custo": {
            "CC-ENG": {
                "alimentacao": "90.00",
            }
        },
    }

    selecionada = selecionar_politica(
        politica=politica,
        centro_custo="CC-INEXISTENTE",
    )

    assert selecionada == {
        "alimentacao": "60.00",
    }


def test_rn016_nao_faz_correspondencia_parcial():
    from src.politica import selecionar_politica

    politica = {
        "padrao": {
            "alimentacao": "60.00",
        },
        "centros_custo": {
            "CC-SUPORTE": {
                "alimentacao": "100.00",
            }
        },
    }

    selecionada = selecionar_politica(
        politica=politica,
        centro_custo="CC-SUPORTE-N2",
    )

    assert selecionada == {
        "alimentacao": "60.00",
    }