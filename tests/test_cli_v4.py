import json
import subprocess
import sys
from pathlib import Path


def test_cli_processa_envelope_v4(tmp_path):
    raiz = Path(__file__).resolve().parents[1]

    entrada = raiz / "exemplos" / "envelope" / "despesas-envelope.json"
    politica = raiz / "exemplos" / "envelope" / "politica-v4.json"
    cambio = raiz / "exemplos" / "envelope" / "cambio.json"
    saida = tmp_path / "resultado-v4.json"

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
            "--politica",
            str(politica),
            "--cambio",
            str(cambio),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0
    assert saida.exists()

    dados = json.loads(
        saida.read_text(encoding="utf-8")
    )

    assert dados["schema_version"] == "2.0"

    assert dados["resumo"] == {
        "total_solicitado": "2457.52",
        "total_reembolsavel": "1143.26",
        "total_nao_reembolsavel": "1314.26",
    }

    por_id = {
        item["id"]: item
        for item in dados["despesas"]
    }

    assert por_id["e-001"]["valor_reembolsavel"] == "300.00"
    assert por_id["e-001"]["status"] == "PARCIAL"

    assert por_id["e-002"]["valor_solicitado"] == "130.46"
    assert por_id["e-002"]["moeda_original"] == "EUR"

    assert por_id["e-004"]["valor_solicitado"] == "178.80"

    assert por_id["e-005"]["status"] == "RECUSADA"
    assert (
        por_id["e-005"]["motivos"][0]["codigo"]
        == "NOTA_FISCAL_OBRIGATORIA"
    )

    assert por_id["e-006"]["status"] == "RECUSADA"
    assert (
        por_id["e-006"]["motivos"][0]["codigo"]
        == "COTACAO_NAO_DISPONIVEL"
    )

    assert por_id["e-010"]["moeda_original"] == "BRL"


def test_cli_usa_politica_padrao_para_centro_desconhecido(tmp_path):
    raiz = Path(__file__).resolve().parents[1]

    entrada = (
        raiz
        / "exemplos"
        / "envelope"
        / "despesas-envelope-cc-desconhecido.json"
    )

    politica = raiz / "exemplos" / "envelope" / "politica-v4.json"
    cambio = raiz / "exemplos" / "envelope" / "cambio.json"
    saida = tmp_path / "resultado-v4-padrao.json"

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
            "--politica",
            str(politica),
            "--cambio",
            str(cambio),
        ],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0
    assert saida.exists()

    dados = json.loads(
        saida.read_text(encoding="utf-8")
    )

    assert dados["resumo"] == {
        "total_solicitado": "623.76",
        "total_reembolsavel": "373.76",
        "total_nao_reembolsavel": "250.00",
    }

    por_id = {
        item["id"]: item
        for item in dados["despesas"]
    }

    assert por_id["f-001"]["valor_reembolsavel"] == "58.00"
    assert por_id["f-002"]["valor_reembolsavel"] == "250.00"

    assert por_id["f-003"]["status"] == "RECUSADA"
    assert (
        por_id["f-003"]["motivos"][0]["codigo"]
        == "CATEGORIA_NAO_REEMBOLSAVEL"
    )

    assert por_id["f-004"]["valor_solicitado"] == "65.76"
    assert por_id["f-004"]["valor_reembolsavel"] == "65.76"