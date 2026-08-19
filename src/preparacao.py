from src.normalizacao import (
    normalizar_categoria,
    normalizar_data,
    normalizar_valor,
)


def preparar_despesas(despesas):
    preparadas = []

    for indice, despesa in enumerate(despesas):
        preparadas.append(
            {
                "id": despesa["id"],
                "data": normalizar_data(despesa["data"]),
                "categoria_original": despesa["categoria"],
                "categoria_normalizada": normalizar_categoria(
                    despesa["categoria"]
                ),
                "descricao": despesa["descricao"],
                "fornecedor": despesa["fornecedor"],
                "valor_original": despesa["valor"],
                "valor_normalizado": normalizar_valor(
                    despesa["valor"]
                ),
                "tem_nota_fiscal": despesa["tem_nota_fiscal"],
                "indice_entrada": indice,
            }
        )

    return preparadas