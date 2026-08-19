from decimal import Decimal

from src.categorias import categoria_reembolsavel
from src.competencia import dentro_da_competencia
from src.duplicidade import identidade_duplicidade
from src.limites import aplicar_limite_diario, aplicar_limite_por_item
from src.nota_fiscal import nota_fiscal_valida
from src.resultado import completar_resultado


ZERO = Decimal("0.00")

LIMITES = {
    "alimentacao": Decimal("60.00"),
    "transporte_urbano": Decimal("80.00"),
    "hospedagem": Decimal("250.00"),
}


def _finalizar(resultado: dict) -> dict:
    resultado_completo = completar_resultado(
        valor_solicitado=resultado["valor_solicitado"],
        valor_reembolsavel=resultado["valor_reembolsavel"],
        motivos=resultado["motivos"],
    )

    resultado.update(resultado_completo)

    return resultado


def calcular_reembolsos(
    despesas,
    inicio,
    fim,
):
    resultados = []
    duplicidades_vistas = set()
    limites_consumidos = {}

    for despesa in despesas:
        valor = despesa["valor_normalizado"]
        categoria = despesa["categoria_normalizada"]

        resultado = {
            "id": despesa["id"],
            "indice_entrada": despesa["indice_entrada"],
            "valor_solicitado": valor,
            "valor_reembolsavel": ZERO,
            "motivos": [],
        }

        # RN-012 — valores não positivos
        if valor <= ZERO:
            resultado["motivos"].append(
                "VALOR_NAO_POSITIVO"
            )
            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-009 — categoria não contemplada
        if not categoria_reembolsavel(categoria):
            resultado["motivos"].append(
                "CATEGORIA_NAO_REEMBOLSAVEL"
            )
            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-007 — competência
        if not dentro_da_competencia(
            despesa["data"],
            inicio,
            fim,
        ):
            resultado["motivos"].append(
                "FORA_COMPETENCIA"
            )
            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-008 — duplicidade
        identidade = identidade_duplicidade(
            despesa
        )

        if identidade in duplicidades_vistas:
            resultado["motivos"].append(
                "DUPLICATA"
            )
            resultados.append(
                _finalizar(resultado)
            )
            continue

        duplicidades_vistas.add(
            identidade
        )

        # RN-005 — nota fiscal
        if not nota_fiscal_valida(
            valor,
            despesa["tem_nota_fiscal"],
        ):
            resultado["motivos"].append(
                "NOTA_FISCAL_OBRIGATORIA"
            )
            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-003 — hospedagem
        if categoria == "hospedagem":
            reembolsavel = aplicar_limite_por_item(
                valor=valor,
                limite=LIMITES[categoria],
            )

        # RN-001 / RN-002 / RN-014
        else:
            chave_limite = (
                despesa["data"],
                categoria,
            )

            consumido = limites_consumidos.get(
                chave_limite,
                ZERO,
            )

            reembolsavel = aplicar_limite_diario(
                valor=valor,
                limite=LIMITES[categoria],
                consumido=consumido,
            )

            limites_consumidos[chave_limite] = (
                consumido + reembolsavel
            )

        resultado["valor_reembolsavel"] = (
            reembolsavel
        )

        # RN-004 — motivo de reembolso parcial
        if (
            reembolsavel > ZERO
            and reembolsavel < valor
        ):
            if categoria == "alimentacao":
                resultado["motivos"].append(
                    "LIMITE_DIARIO_ALIMENTACAO"
                )
            elif categoria == "transporte_urbano":
                resultado["motivos"].append(
                    "LIMITE_DIARIO_TRANSPORTE"
                )
            elif categoria == "hospedagem":
                resultado["motivos"].append(
                    "LIMITE_HOSPEDAGEM"
                )

        resultados.append(
            _finalizar(resultado)
        )

    return resultados