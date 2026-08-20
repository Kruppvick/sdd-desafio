from decimal import Decimal


def preparar_politica(dados: dict) -> dict:
    def preparar_configuracao(configuracao: dict) -> dict:
        return {
            categoria: Decimal(str(dados_categoria["limite"]))
            for categoria, dados_categoria in configuracao.items()
        }

    return {
        "padrao": preparar_configuracao(
            dados["padrao"]
        ),
        "centros_custo": {
            centro_custo: preparar_configuracao(configuracao)
            for centro_custo, configuracao
            in dados.get("centros_custo", {}).items()
        },
    }