import argparse
import json
from pathlib import Path

from src.motor import calcular_reembolsos
from src.normalizacao import normalizar_data
from src.preparacao import preparar_despesas
from src.resultado import calcular_resumo
from src.validacao import validar_entrada
from src.motivos import descricao_motivo


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="motor-reembolso"
    )

    subparsers = parser.add_subparsers(
        dest="comando",
        required=True,
    )

    calcular = subparsers.add_parser(
        "calcular",
        help="Calcula o reembolso das despesas.",
    )

    calcular.add_argument(
        "--input",
        required=True,
        help="Caminho do arquivo JSON de entrada.",
    )

    calcular.add_argument(
        "--output",
        required=True,
        help="Caminho do arquivo JSON de saída.",
    )

    return parser


def _formatar_decimal(valor):
    return f"{valor:.2f}"


def _serializar_resumo(resumo):
    return {
        "total_solicitado": _formatar_decimal(
            resumo["total_solicitado"]
        ),
        "total_reembolsavel": _formatar_decimal(
            resumo["total_reembolsavel"]
        ),
        "total_nao_reembolsavel": _formatar_decimal(
            resumo["total_nao_reembolsavel"]
        ),
    }


def _serializar_despesa(resultado):
    return {
        "id": resultado["id"],
        "valor_original": _formatar_decimal(
            resultado["valor_original"]
        ),
        "moeda_original": resultado["moeda_original"],
        "valor_solicitado": _formatar_decimal(
            resultado["valor_solicitado"]
        ),
        "valor_reembolsavel": _formatar_decimal(
            resultado["valor_reembolsavel"]
        ),
        "valor_nao_reembolsavel": _formatar_decimal(
            resultado["valor_nao_reembolsavel"]
        ),
        "status": resultado["status"],
        "motivos": [
            {
                "codigo": motivo,
                "descricao": descricao_motivo(motivo),
            }
            for motivo in resultado["motivos"]
        ],
    }

def executar_calculo(
    caminho_entrada: str,
    caminho_saida: str,
) -> None:
    entrada = Path(caminho_entrada)
    saida = Path(caminho_saida)

    with entrada.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        dados = json.load(arquivo)

    validar_entrada(dados)

    despesas = preparar_despesas(
        dados["despesas"]
    )

    resultados = calcular_reembolsos(
        despesas=despesas,
        inicio=normalizar_data(
            dados["periodo"]["inicio"]
        ),
        fim=normalizar_data(
            dados["periodo"]["fim"]
        ),
    )

    resumo = calcular_resumo(resultados)

    resultado = {
        "schema_version": "2.0",
        "colaborador": {
            "id": dados["colaborador"]["id"],
        },
        "periodo": {
            "competencia": dados["periodo"]["competencia"],
        },
        "resumo": _serializar_resumo(resumo),
        "despesas": [
            _serializar_despesa(item)
            for item in resultados
        ],
    }

    with saida.open(
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )


def main() -> int:
    parser = criar_parser()
    args = parser.parse_args()

    if args.comando == "calcular":
        executar_calculo(
            caminho_entrada=args.input,
            caminho_saida=args.output,
        )
        return 0

    return 1