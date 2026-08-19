import argparse
import json
from pathlib import Path


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

    resultado = {
        "schema_version": "1.0",
        "colaborador": {
            "id": dados["colaborador"]["id"],
        },
        "periodo": {
            "competencia": dados["periodo"]["competencia"],
        },
        "resumo": {
            "total_solicitado": "0.00",
            "total_reembolsavel": "0.00",
            "total_nao_reembolsavel": "0.00",
        },
        "despesas": [],
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