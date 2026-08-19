from datetime import date
from decimal import Decimal

from src.duplicidade import identidade_duplicidade


def criar_despesa(
    *,
    id="d-001",
    data=date(2026, 7, 10),
    categoria="alimentacao",
    descricao="Almoco",
    fornecedor="Restaurante X",
    valor=Decimal("54.90"),
    tem_nota_fiscal=True,
):
    return {
        "id": id,
        "data": data,
        "categoria_normalizada": categoria,
        "descricao": descricao,
        "fornecedor": fornecedor,
        "valor_normalizado": valor,
        "tem_nota_fiscal": tem_nota_fiscal,
    }


def test_rn008_ids_diferentes_nao_impedem_duplicidade():
    primeira = criar_despesa(id="d-001")
    segunda = criar_despesa(id="d-002")

    assert identidade_duplicidade(
        primeira
    ) == identidade_duplicidade(
        segunda
    )


def test_rn008_fornecedor_diferente_nao_e_duplicata():
    primeira = criar_despesa()
    segunda = criar_despesa(
        id="d-002",
        fornecedor="Restaurante Y",
    )

    assert identidade_duplicidade(
        primeira
    ) != identidade_duplicidade(
        segunda
    )


def test_rn008_descricao_diferente_nao_e_duplicata():
    primeira = criar_despesa()
    segunda = criar_despesa(
        id="d-002",
        descricao="Jantar",
    )

    assert identidade_duplicidade(
        primeira
    ) != identidade_duplicidade(
        segunda
    )


def test_rn008_valor_diferente_nao_e_duplicata():
    primeira = criar_despesa()
    segunda = criar_despesa(
        id="d-002",
        valor=Decimal("54.91"),
    )

    assert identidade_duplicidade(
        primeira
    ) != identidade_duplicidade(
        segunda
    )

def test_rn008_primeira_ocorrencia_e_mantida():
    vistos = set()

    primeira = criar_despesa(id="d-001")
    segunda = criar_despesa(id="d-002")

    identidade_primeira = identidade_duplicidade(
        primeira
    )
    identidade_segunda = identidade_duplicidade(
        segunda
    )

    assert identidade_primeira not in vistos

    vistos.add(identidade_primeira)

    assert identidade_segunda in vistos