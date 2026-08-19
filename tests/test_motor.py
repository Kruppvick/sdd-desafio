from datetime import date
from decimal import Decimal

from src.motor import calcular_reembolsos


def criar_despesa(
    *,
    id="d-001",
    data=date(2026, 7, 10),
    categoria="alimentacao",
    descricao="Almoco",
    fornecedor="Restaurante",
    valor=Decimal("50.00"),
    tem_nota_fiscal=True,
):
    return {
        "id": id,
        "data": data,
        "categoria_original": categoria,
        "categoria_normalizada": categoria,
        "descricao": descricao,
        "fornecedor": fornecedor,
        "valor_original": valor,
        "valor_normalizado": valor,
        "tem_nota_fiscal": tem_nota_fiscal,
        "indice_entrada": 0,
    }


def test_rn013_sem_nota_nao_consome_limite():
    despesas = [
        criar_despesa(
            id="d-001",
            valor=Decimal("150.00"),
            tem_nota_fiscal=False,
        ),
        criar_despesa(
            id="d-002",
            valor=Decimal("50.00"),
        ),
    ]

    despesas[1]["indice_entrada"] = 1

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[1]["valor_reembolsavel"] == Decimal("50.00")


def test_rn013_duplicata_nao_consome_limite_novamente():
    despesas = [
        criar_despesa(
            id="d-001",
            valor=Decimal("40.00"),
        ),
        criar_despesa(
            id="d-002",
            valor=Decimal("40.00"),
        ),
        criar_despesa(
            id="d-003",
            valor=Decimal("20.00"),
            descricao="Jantar",
        ),
    ]

    for indice, despesa in enumerate(despesas):
        despesa["indice_entrada"] = indice

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("40.00")
    assert resultados[1]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[2]["valor_reembolsavel"] == Decimal("20.00")

def test_rn001_limite_totalmente_consumido_gera_motivo():
    despesas = [
        criar_despesa(
            id="d-001",
            valor=Decimal("60.00"),
            descricao="Almoco",
        ),
        criar_despesa(
            id="d-002",
            valor=Decimal("38.00"),
            descricao="Jantar",
        ),
    ]

    despesas[1]["indice_entrada"] = 1

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("60.00")

    assert resultados[1]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[1]["status"] == "RECUSADA"
    assert "LIMITE_DIARIO_ALIMENTACAO" in resultados[1]["motivos"]


def test_rn014_ordem_original_define_consumo():
    despesas = [
        criar_despesa(
            id="d-001",
            valor=Decimal("40.00"),
        ),
        criar_despesa(
            id="d-002",
            valor=Decimal("30.00"),
            descricao="Jantar",
        ),
    ]

    despesas[1]["indice_entrada"] = 1

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("40.00")
    assert resultados[1]["valor_reembolsavel"] == Decimal("20.00")