import json
import subprocess
import sys
from pathlib import Path


def test_cli_calcular_le_json_e_grava_saida(tmp_path):
    arquivo_entrada = tmp_path / "entrada.json"
    arquivo_saida = tmp_path / "saida.json"

    entrada = {
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

    arquivo_entrada.write_text(
        json.dumps(entrada),
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "calcular",
            "--input",
            str(arquivo_entrada),
            "--output",
            str(arquivo_saida),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0
    assert arquivo_saida.exists()

    conteudo_saida = json.loads(
        arquivo_saida.read_text(encoding="utf-8")
    )

    assert isinstance(conteudo_saida, dict)


def test_cli_calcular_exige_input_e_output():
    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "calcular",
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode != 0
    assert "--input" in resultado.stderr
    assert "--output" in resultado.stderr

def test_cli_resultado_vazio_tem_totais_zero(tmp_path):
    arquivo_entrada = tmp_path / "entrada.json"
    arquivo_saida = tmp_path / "saida.json"

    entrada = {
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

    arquivo_entrada.write_text(
        json.dumps(entrada),
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "calcular",
            "--input",
            str(arquivo_entrada),
            "--output",
            str(arquivo_saida),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0

    saida = json.loads(
        arquivo_saida.read_text(encoding="utf-8")
    )

    assert saida["resumo"] == {
        "total_solicitado": "0.00",
        "total_reembolsavel": "0.00",
        "total_nao_reembolsavel": "0.00",
    }

def test_cli_processa_arquivo_de_exemplo(tmp_path):
    raiz = Path(__file__).resolve().parents[1]

    entrada = raiz / "exemplos" / "despesas-exemplo.json"
    saida = tmp_path / "resultado.json"

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "calcular",
            "--input",
            str(entrada),
            "--output",
            str(saida),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0
    assert saida.exists()

    conteudo = json.loads(
        saida.read_text(encoding="utf-8")
    )

    assert "resumo" in conteudo
    assert "despesas" in conteudo
    assert len(conteudo["despesas"]) > 0

def test_cli_serializa_descricao_legivel_do_motivo(tmp_path):
    arquivo_entrada = tmp_path / "entrada.json"
    arquivo_saida = tmp_path / "saida.json"

    entrada = {
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
        "despesas": [
            {
                "id": "d-001",
                "data": "2026-07-10",
                "categoria": "coworking",
                "descricao": "Sala",
                "fornecedor": "Coworking X",
                "valor": 50,
                "tem_nota_fiscal": True,
            }
        ],
    }

    arquivo_entrada.write_text(
        json.dumps(entrada),
        encoding="utf-8",
    )

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "calcular",
            "--input",
            str(arquivo_entrada),
            "--output",
            str(arquivo_saida),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0

    saida = json.loads(
        arquivo_saida.read_text(encoding="utf-8")
    )

    motivo = saida["despesas"][0]["motivos"][0]

    assert motivo["codigo"] == "CATEGORIA_NAO_REEMBOLSAVEL"
    assert motivo["descricao"] == (
        "A categoria informada não é reembolsável pela política."
    )