import pytest

from src.categorias import categoria_reembolsavel


@pytest.mark.parametrize(
    "categoria",
    [
        "alimentacao",
        "transporte_urbano",
        "hospedagem",
    ],
)
def test_rn009_categorias_previstas_sao_reconhecidas(categoria):
    assert categoria_reembolsavel(categoria) is True


def test_rn009_categoria_desconhecida_e_recusada():
    assert categoria_reembolsavel("coworking") is False


def test_rn010_categoria_normalizada_e_reconhecida():
    assert categoria_reembolsavel("alimentacao") is True