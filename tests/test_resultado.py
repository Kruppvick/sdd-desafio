from decimal import Decimal

from src.resultado import (
    completar_resultado,
    calcular_resumo,
)


def test_rn015_despesa_aprovada():
    resultado = completar_resultado(
        valor_solicitado=Decimal("50.00"),
        valor_reembolsavel=Decimal("50.00"),
        motivos=[],
    )

    assert resultado["status"] == "APROVADA"
    assert resultado["valor_nao_reembolsavel"] == Decimal("0.00")


def test_rn015_despesa_parcial():
    resultado = completar_resultado(
        valor_solicitado=Decimal("70.00"),
        valor_reembolsavel=Decimal("60.00"),
        motivos=[],
    )

    assert resultado["status"] == "PARCIAL"
    assert resultado["valor_nao_reembolsavel"] == Decimal("10.00")


def test_rn015_despesa_recusada():
    resultado = completar_resultado(
        valor_solicitado=Decimal("150.00"),
        valor_reembolsavel=Decimal("0.00"),
        motivos=["NOTA_FISCAL_OBRIGATORIA"],
    )

    assert resultado["status"] == "RECUSADA"
    assert resultado["valor_nao_reembolsavel"] == Decimal("150.00")


def test_rn012_negativo_nao_entra_como_nao_reembolsavel():
    resultado = completar_resultado(
        valor_solicitado=Decimal("-45.00"),
        valor_reembolsavel=Decimal("0.00"),
        motivos=["VALOR_NAO_POSITIVO"],
    )

    assert resultado["status"] == "RECUSADA"
    assert resultado["valor_nao_reembolsavel"] == Decimal("0.00")


def test_rn015_resumo_fecha_com_decisoes():
    resultados = [
        completar_resultado(
            Decimal("50.00"),
            Decimal("50.00"),
            [],
        ),
        completar_resultado(
            Decimal("70.00"),
            Decimal("10.00"),
            [],
        ),
        completar_resultado(
            Decimal("-45.00"),
            Decimal("0.00"),
            ["VALOR_NAO_POSITIVO"],
        ),
    ]

    resumo = calcular_resumo(resultados)

    assert resumo["total_solicitado"] == Decimal("120.00")
    assert resumo["total_reembolsavel"] == Decimal("60.00")
    assert resumo["total_nao_reembolsavel"] == Decimal("60.00")