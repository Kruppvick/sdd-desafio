import json
import subprocess
import sys


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