from datetime import date
from decimal import Decimal

from src.duplicidade import identidade_duplicidade


def criar_despesa(
    *,
    moeda="BRL",
    valor="100.00",
):
    return {
        "data": date(2026, 7, 10),
        "categoria_normalizada": "alimentacao",
        "descricao": "Almoco",
        "fornecedor": "Restaurante X",
        "moeda_normalizada": moeda,
        "valor_normalizado": Decimal(valor),
        "tem_nota_fiscal": True,
    }


def test_rn008_mesmos_dados_mesma_moeda_e_valor_sao_duplicata():
    primeira = criar_despesa(
        moeda="USD",
        valor="20.00",
    )

    segunda = criar_despesa(
        moeda="USD",
        valor="20.00",
    )

    assert identidade_duplicidade(
        primeira
    ) == identidade_duplicidade(
        segunda
    )


def test_rn008_mesmo_valor_moedas_diferentes_nao_sao_duplicata():
    primeira = criar_despesa(
        moeda="USD",
        valor="20.00",
    )

    segunda = criar_despesa(
        moeda="EUR",
        valor="20.00",
    )

    assert identidade_duplicidade(
        primeira
    ) != identidade_duplicidade(
        segunda
    )


def test_rn008_valores_originais_diferentes_nao_sao_duplicata():
    primeira = criar_despesa(
        moeda="USD",
        valor="20.00",
    )

    segunda = criar_despesa(
        moeda="USD",
        valor="21.00",
    )

    assert identidade_duplicidade(
        primeira
    ) != identidade_duplicidade(
        segunda
    )