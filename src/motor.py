from decimal import Decimal

from src.cambio import converter_para_brl
from src.competencia import dentro_da_competencia
from src.duplicidade import identidade_duplicidade
from src.limites import aplicar_limite_diario, aplicar_limite_por_item
from src.nota_fiscal import nota_fiscal_valida
from src.resultado import completar_resultado


ZERO = Decimal("0.00")

POLITICA_BASELINE = {
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
    politica=None,
    cotacoes=None,
):
    if politica is None:
        politica = POLITICA_BASELINE

    if cotacoes is None:
        cotacoes = {}

    resultados = []
    duplicidades_vistas = set()
    limites_consumidos = {}

    for despesa in despesas:
        valor_original = despesa["valor_normalizado"]
        categoria = despesa["categoria_normalizada"]
        moeda = despesa.get(
            "moeda_normalizada",
            "BRL",
        )

        resultado = {
            "id": despesa["id"],
            "indice_entrada": despesa["indice_entrada"],
            "valor_solicitado": valor_original,
            "valor_reembolsavel": ZERO,
            "motivos": [],
        }

        # RN-009 — categoria não contemplada
        #
        # A categoria é verificada antes do câmbio.
        if categoria not in politica:
            resultado["motivos"].append(
                "CATEGORIA_NAO_REEMBOLSAVEL"
            )

            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-007 — competência
        #
        # A competência também pode eliminar a despesa
        # antes de qualquer conversão monetária.
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
        #
        # A identidade usa moeda e valor originais
        # normalizados, antes da conversão para BRL.
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

        # RN-019 / RN-020 — conversão para BRL
        #
        # BRL não sofre conversão.
        # Moeda estrangeira utiliza cotação da mesma data
        # ou a última cotação anterior disponível.
        valor_brl = converter_para_brl(
            valor_original=valor_original,
            moeda=moeda,
            data=despesa["data"],
            cotacoes=cotacoes,
        )

        # RN-021 / RN-025 — cotação indisponível
        #
        # Sem valor confiável em BRL, nenhuma regra
        # monetária posterior é aplicada.
        if valor_brl is None:
            resultado["valor_solicitado"] = ZERO
            resultado["motivos"].append(
                "COTACAO_NAO_DISPONIVEL"
            )

            resultados.append(
                _finalizar(resultado)
            )
            continue

        # A partir deste ponto, todas as regras monetárias
        # trabalham com o valor convertido/normalizado em BRL.
        resultado["valor_solicitado"] = valor_brl

        # RN-012 — valores não positivos
        if valor_brl <= ZERO:
            resultado["motivos"].append(
                "VALOR_NAO_POSITIVO"
            )

            resultados.append(
                _finalizar(resultado)
            )
            continue

        # RN-005 / RN-024 — nota fiscal
        #
        # O limite documental de R$ 100,00 é avaliado
        # sobre o valor em BRL.
        if not nota_fiscal_valida(
            valor_brl,
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
        #
        # Hospedagem utiliza limite por lançamento.
        if categoria == "hospedagem":
            reembolsavel = aplicar_limite_por_item(
                valor=valor_brl,
                limite=politica[categoria],
            )

        # RN-001 / RN-002 / RN-013 / RN-014 / RN-023
        #
        # Demais categorias configuradas neste momento
        # utilizam limite diário compartilhado.
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
                valor=valor_brl,
                limite=politica[categoria],
                consumido=consumido,
            )

            limites_consumidos[chave_limite] = (
                consumido + reembolsavel
            )

        resultado["valor_reembolsavel"] = (
            reembolsavel
        )

        # RN-004 — motivo quando o limite reduz o reembolso
        if reembolsavel < valor_brl:
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