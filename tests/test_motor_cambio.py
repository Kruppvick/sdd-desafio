from datetime import date
from decimal import Decimal

from src.motor import calcular_reembolsos


def criar_despesa(
    *,
    id="d-001",
    valor="20.00",
    moeda="USD",
    categoria="alimentacao",
    tem_nota_fiscal=True,
    indice_entrada=0,
):
    return {
        "id": id,
        "data": date(2026, 7, 10),
        "categoria_normalizada": categoria,
        "descricao": f"Despesa {id}",
        "fornecedor": "Fornecedor",
        "valor_normalizado": Decimal(valor),
        "moeda_original": moeda,
        "moeda_normalizada": moeda,
        "tem_nota_fiscal": tem_nota_fiscal,
        "indice_entrada": indice_entrada,
    }


def test_rn024_motor_converte_antes_de_aplicar_limite():
    despesas = [
        criar_despesa(
            valor="20.00",
            moeda="USD",
        )
    ]

    politica = {
        "alimentacao": Decimal("90.00"),
    }

    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.00"),
        }
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
        cotacoes=cotacoes,
    )

    assert resultados[0]["valor_solicitado"] == Decimal("100.00")
    assert resultados[0]["valor_reembolsavel"] == Decimal("90.00")
    assert resultados[0]["status"] == "PARCIAL"


def test_rn024_motor_converte_antes_da_nota_fiscal():
    despesas = [
        criar_despesa(
            valor="20.00",
            moeda="USD",
            tem_nota_fiscal=False,
        )
    ]

    politica = {
        "alimentacao": Decimal("200.00"),
    }

    cotacoes = {
        "USD": {
            date(2026, 7, 10): Decimal("5.10"),
        }
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
        cotacoes=cotacoes,
    )

    assert resultados[0]["valor_solicitado"] == Decimal("102.00")
    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[0]["status"] == "RECUSADA"
    assert (
        "NOTA_FISCAL_OBRIGATORIA"
        in resultados[0]["motivos"]
    )


def test_rn025_sem_cotacao_recusa_antes_da_nota_e_limite():
    despesas = [
        criar_despesa(
            valor="50.00",
            moeda="GBP",
            tem_nota_fiscal=False,
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
        cotacoes={},
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert resultados[0]["status"] == "RECUSADA"

    assert (
        "COTACAO_NAO_DISPONIVEL"
        in resultados[0]["motivos"]
    )

    assert (
        "NOTA_FISCAL_OBRIGATORIA"
        not in resultados[0]["motivos"]
    )


def test_rn025_falha_cambial_nao_consome_limite():
    despesas = [
        criar_despesa(
            id="d-001",
            valor="20.00",
            moeda="GBP",
            indice_entrada=0,
        ),
        criar_despesa(
            id="d-002",
            valor="50.00",
            moeda="BRL",
            indice_entrada=1,
        ),
    ]

    politica = {
        "alimentacao": Decimal("60.00"),
    }

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=date(2026, 7, 1),
        fim=date(2026, 7, 31),
        politica=politica,
        cotacoes={},
    )

    assert resultados[0]["valor_reembolsavel"] == Decimal("0.00")
    assert (
        "COTACAO_NAO_DISPONIVEL"
        in resultados[0]["motivos"]
    )

    assert resultados[1]["valor_reembolsavel"] == Decimal("50.00")
    assert resultados[1]["status"] == "APROVADA"
    assert resultados[0]["motivos"] == [
    "COTACAO_NAO_DISPONIVEL"
]