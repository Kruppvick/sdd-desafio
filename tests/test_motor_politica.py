from datetime import date
from decimal import Decimal

from src.motor import calcular_reembolsos


def criar_despesa(
    *,
    id,
    categoria,
    valor,
    indice_entrada=0,
):
    return {
        "id": id,
        "data": date(2026, 7, 10),
        "categoria_normalizada": categoria,
        "descricao": f"Despesa {id}",
        "fornecedor": "Fornecedor",
        "valor_normalizado": Decimal(valor),
        "moeda_original": "BRL",
        "moeda_normalizada": "BRL",
        "tem_nota_fiscal": True,
        "indice_entrada": indice_entrada,
    }


def test_rn001_alimentacao_usa_limite_da_politica():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="alimentacao",
            valor="90.01",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
        "transporte_urbano": Decimal("150.00"),
        "hospedagem": Decimal("400.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("90.00")


def test_rn002_transporte_usa_limite_da_politica():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="transporte_urbano",
            valor="150.01",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
        "transporte_urbano": Decimal("150.00"),
        "hospedagem": Decimal("400.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("150.00")


def test_rn003_hospedagem_usa_limite_da_politica():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="hospedagem",
            valor="480.00",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
        "transporte_urbano": Decimal("150.00"),
        "hospedagem": Decimal("400.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("400.00")


def test_rn009_categoria_ausente_da_politica_e_recusada():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="coworking",
            valor="50.00",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[0]["status"] == "RECUSADA"
    assert "CATEGORIA_NAO_REEMBOLSAVEL" in resultados[0]["motivos"]


def test_rn022_categoria_com_limite_zero_nao_e_categoria_ausente():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="hospedagem",
            valor="100.00",
        )
    ]

    politica = {
        "hospedagem": Decimal("0.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[0]["status"] == "RECUSADA"
    assert "CATEGORIA_NAO_REEMBOLSAVEL" not in resultados[0]["motivos"]
    assert "LIMITE_HOSPEDAGEM" in resultados[0]["motivos"]

def test_rn023_representacao_presente_na_politica_e_reembolsavel():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="representacao",
            valor="200.00",
        )
    ]

    politica = {
        "representacao": Decimal("300.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("200.00")
    assert resultados[0]["status"] == "APROVADA"


def test_rn023_representacao_ausente_da_politica_e_recusada():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="representacao",
            valor="50.00",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[0]["status"] == "RECUSADA"
    assert (
        "CATEGORIA_NAO_REEMBOLSAVEL"
        in resultados[0]["motivos"]
    )


def test_rn023_representacao_compartilha_limite_diario():
    despesas = [
        criar_despesa(
            id="d-001",
            categoria="representacao",
            valor="200.00",
            indice_entrada=0,
        ),
        criar_despesa(
            id="d-002",
            categoria="representacao",
            valor="200.00",
            indice_entrada=1,
        ),
    ]

    # Evita que RN-008 trate os lançamentos como duplicados.
    despesas[1]["descricao"] = "Despesa representacao 2"

    politica = {
        "representacao": Decimal("300.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("200.00")
    assert resultados[1]["valor_reembolsavel"] == Decimal("100.00")
    assert resultados[1]["status"] == "PARCIAL"