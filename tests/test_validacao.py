import pytest

from src.validacao import validar_entrada


def entrada_valida():
    return {
        "colaborador": {
            "id": "c-001",
            "nome": "Teste",
            "centro_custo": "CC-TESTE",
        },
        "periodo": {
            "competencia": "2026-07",
            "inicio": "2026-07-01",
            "fim": "2026-07-31",
        },
        "despesas": [],
    }


def test_valida_entrada_minima():
    validar_entrada(entrada_valida())


def test_rejeita_entrada_sem_colaborador():
    dados = entrada_valida()
    del dados["colaborador"]

    with pytest.raises(ValueError):
        validar_entrada(dados)


def test_rejeita_entrada_sem_periodo():
    dados = entrada_valida()
    del dados["periodo"]

    with pytest.raises(ValueError):
        validar_entrada(dados)


def test_rejeita_entrada_sem_despesas():
    dados = entrada_valida()
    del dados["despesas"]

    with pytest.raises(ValueError):
        validar_entrada(dados)

def test_rejeita_data_invalida_no_periodo():
    dados = entrada_valida()
    dados["periodo"]["inicio"] = "2026-99-99"

    with pytest.raises(ValueError):
        validar_entrada(dados)


def test_rejeita_data_invalida_na_despesa():
    dados = entrada_valida()
    dados["despesas"] = [
        {
            "id": "d-001",
            "data": "2026-99-99",
            "categoria": "alimentacao",
            "descricao": "Almoco",
            "fornecedor": "Restaurante",
            "valor": 50,
            "tem_nota_fiscal": True,
        }
    ]

    with pytest.raises(ValueError):
        validar_entrada(dados)


def test_rejeita_despesa_sem_campo_obrigatorio():
    dados = entrada_valida()
    dados["despesas"] = [
        {
            "id": "d-001",
            "data": "2026-07-10",
            "categoria": "alimentacao",
            "descricao": "Almoco",
            "fornecedor": "Restaurante",
            "valor": 50,
        }
    ]

    with pytest.raises(ValueError):
        validar_entrada(dados)