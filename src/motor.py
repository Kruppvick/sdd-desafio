from decimal import Decimal

from src.categorias import categoria_reembolsavel
from src.competencia import dentro_da_competencia
from src.duplicidade import identidade_duplicidade
from src.limites import aplicar_limite_diario, aplicar_limite_por_item
from src.nota_fiscal import nota_fiscal_valida


ZERO = Decimal("0.00")

LIMITES = {
    "alimentacao": Decimal("60.00"),
    "transporte_urbano": Decimal("80.00"),
    "hospedagem": Decimal("250.00"),
}


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

        if valor <= ZERO:
            resultado["motivos"].append("VALOR_NAO_POSITIVO")
            resultados.append(resultado)
            continue

        if not categoria_reembolsavel(categoria):
            resultado["motivos"].append("CATEGORIA_NAO_REEMBOLSAVEL")
            resultados.append(resultado)
            continue

        if not dentro_da_competencia(
            despesa["data"],
            inicio,
            fim,
        ):
            resultado["motivos"].append("FORA_COMPETENCIA")
            resultados.append(resultado)
            continue

        identidade = identidade_duplicidade(despesa)

        if identidade in duplicidades_vistas:
            resultado["motivos"].append("DUPLICATA")
            resultados.append(resultado)
            continue

        duplicidades_vistas.add(identidade)

        if not nota_fiscal_valida(
            valor,
            despesa["tem_nota_fiscal"],
        ):
            resultado["motivos"].append("NOTA_FISCAL_OBRIGATORIA")
            resultados.append(resultado)
            continue

        if categoria == "hospedagem":
            reembolsavel = aplicar_limite_por_item(
                valor=valor,
                limite=LIMITES[categoria],
            )

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

        resultado["valor_reembolsavel"] = reembolsavel

        resultados.append(resultado)

    return resultados