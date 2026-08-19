def identidade_duplicidade(despesa: dict) -> tuple:
    return (
        despesa["data"],
        despesa["categoria_normalizada"],
        despesa["descricao"],
        despesa["fornecedor"],
        despesa["valor_normalizado"],
        despesa["tem_nota_fiscal"],
    )