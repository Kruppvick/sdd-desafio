# Motor de Cálculo de Reembolso

Motor de cálculo de reembolso desenvolvido com abordagem **Spec Driven Development (SDD)**.

O projeto foi inicialmente implementado para a Política de Reembolso v3 e posteriormente evoluído para atender à **Política de Reembolso v4**, preservando a rastreabilidade entre especificação, decisões, tasks, testes e implementação.

A Política v4 introduz:

- limites definidos externamente e variáveis por centro de custo;
- política padrão para centros de custo sem configuração específica;
- categoria `representacao`;
- despesas em moedas estrangeiras;
- conversão para BRL utilizando cotações históricas;
- preservação do valor e da moeda originais no resultado;
- schema de saída versão `2.0`.

A funcionalidade opcional de aprovação manual não faz parte desta entrega, conforme decisão registrada na especificação.

---

## Requisitos

- Python 3.12 ou superior
- `pytest` para execução dos testes

O projeto utiliza apenas a biblioteca padrão do Python em sua implementação.

---

## Preparar o ambiente

### Windows PowerShell

Crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale o `pytest`:

```powershell
python -m pip install pytest
```

Após a ativação, o terminal deve apresentar algo semelhante a:

```text
(.venv) PS C:\caminho\do\projeto>
```

---

## Executar os testes

Para executar toda a suíte automatizada:

```powershell
python -m pytest -q
```

Para executar apenas um arquivo:

```powershell
python -m pytest tests/test_cli_v4.py -q
```

Alguns grupos relevantes de testes são:

```text
test_normalizacao.py
test_politica.py
test_motor_politica.py
test_cambio.py
test_duplicidade.py
test_nota_fiscal_cambio.py
test_motor_cambio.py
test_dados_v4.py
test_cli_v4.py
```

Além dos testes da Política v4, os testes criados para a baseline v3 foram preservados para detectar regressões.

---

## Executar o motor

A operação disponível na CLI é:

```text
calcular
```

A interface básica é:

```text
python -m src calcular --input <entrada> --output <saida>
```

Para a Política v4, a CLI também aceita:

```text
--politica <arquivo-politica>
--cambio <arquivo-cambio>
```

Portanto, uma execução completa da v4 utiliza:

```text
python -m src calcular \
  --input <entrada> \
  --output <saida> \
  --politica <politica> \
  --cambio <cambio>
```

No PowerShell, utilize crase para quebrar o comando em várias linhas.

---

## Executar o envelope da Política v4

Os arquivos recebidos com a mudança de requisito estão preservados em:

```text
exemplos/envelope/
├── 00-ENVELOPE-LACRADO.md
├── cambio.json
├── despesas-envelope.json
├── despesas-envelope-cc-desconhecido.json
└── politica-v4.json
```

### Cenário CC-COMERCIAL

Execute:

```powershell
python -m src calcular `
  --input .\exemplos\envelope\despesas-envelope.json `
  --output .\resultado-v4.json `
  --politica .\exemplos\envelope\politica-v4.json `
  --cambio .\exemplos\envelope\cambio.json
```

Para visualizar:

```powershell
Get-Content .\resultado-v4.json -Encoding UTF8
```

Nesse cenário, a política específica de `CC-COMERCIAL` é utilizada.

---

## Executar cenário com centro de custo desconhecido

O envelope também contém um colaborador cujo centro de custo, `CC-SUPORTE-N2`, não possui configuração específica.

Execute:

```powershell
python -m src calcular `
  --input .\exemplos\envelope\despesas-envelope-cc-desconhecido.json `
  --output .\resultado-v4-padrao.json `
  --politica .\exemplos\envelope\politica-v4.json `
  --cambio .\exemplos\envelope\cambio.json
```

Nesse caso, o motor utiliza a política `padrao`.

---

## Política por centro de custo

Os limites não são constantes no código.

A Política v4 é carregada de:

```text
exemplos/envelope/politica-v4.json
```

O motor utiliza:

```text
colaborador.centro_custo
        ↓
existe configuração específica?
        ↓
sim  → política específica
não  → política padrao
```

Não é realizada correspondência parcial entre nomes de centros de custo.

Por exemplo, a ausência de `CC-SUPORTE-N2` não faz o sistema utilizar automaticamente uma configuração chamada `CC-SUPORTE`, caso ela exista.

---

## Categorias e limites

As categorias contempladas e seus limites dependem da política selecionada.

Na Política v4 fornecida, por exemplo, `CC-COMERCIAL` possui a categoria:

```text
representacao
```

com limite diário próprio.

Uma categoria ausente da política selecionada é tratada como não contemplada.

Uma categoria presente com limite igual a R$ 0,00 é diferente de uma categoria ausente: ela é reconhecida pela política, mas nenhum valor pode ser reembolsado.

---

## Moedas

Cada despesa pode informar:

```json
"moeda": "EUR"
```

O campo é opcional.

Quando `moeda` estiver ausente:

```text
moeda = BRL
```

O código da moeda é normalizado removendo espaços externos e ignorando diferenças entre letras maiúsculas e minúsculas.

Exemplos:

```text
usd
USD
 USD
```

são tratados como:

```text
USD
```

A moeda não é inferida a partir de fornecedor ou descrição.

---

## Conversão cambial

Os limites da política são sempre aplicados em BRL.

Para uma despesa estrangeira, o fluxo é:

```text
valor original
      ↓
normalização monetária
      ↓
cotação histórica
      ↓
conversão para BRL
      ↓
normalização para centavos
      ↓
nota fiscal
      ↓
limite da categoria
```

Quando existe cotação exatamente na data da despesa, ela é utilizada.

Quando não existe cotação naquela data, o motor utiliza a cotação disponível mais recente anterior para a mesma moeda.

Cotações futuras não são utilizadas.

Essa decisão permite tratar, por exemplo, despesas realizadas em fins de semana sem utilizar informação cambial posterior à despesa.

---

## Moeda sem cotação

Quando não existe cotação utilizável para a moeda da despesa, o lançamento é recusado com:

```text
COTACAO_NAO_DISPONIVEL
```

Nesse caso:

- o valor reembolsável é R$ 0,00;
- nenhum limite é consumido;
- não é utilizada taxa igual a 1;
- não é utilizada taxa de outra moeda;
- não é utilizada cotação futura;
- nenhuma consulta externa é realizada.

O valor e a moeda originalmente recebidos permanecem disponíveis no resultado.

---

## Nota fiscal

Nota fiscal é obrigatória quando o valor considerado em BRL for **estritamente superior a R$ 100,00**.

Portanto:

```text
R$ 100,00 → não exige nota por essa regra
R$ 100,01 → exige nota
```

Para despesas estrangeiras, a verificação ocorre depois da conversão e do arredondamento para BRL.

---

## Duplicidade

A identificação de duplicidade utiliza:

- data;
- categoria normalizada;
- descrição;
- fornecedor;
- moeda original normalizada;
- valor original normalizado;
- indicador de nota fiscal.

O `id` não participa da identidade.

O valor convertido para BRL também não participa.

A primeira ocorrência é avaliada normalmente e ocorrências posteriores são recusadas como duplicatas.

---

## Ordem e consumo dos limites

Para limites diários, despesas elegíveis consomem o valor disponível seguindo a ordem original da entrada.

Somente valores efetivamente reembolsados consomem limite.

Portanto, não consomem limite despesas recusadas por motivos como:

- categoria não contemplada;
- fora da competência;
- duplicidade;
- nota fiscal obrigatória ausente;
- valor não positivo;
- cotação indisponível.

---

## Saída

A Política v4 utiliza:

```json
"schema_version": "2.0"
```

Cada despesa possui informações como:

```json
{
  "id": "e-002",
  "valor_original": "22.00",
  "moeda_original": "EUR",
  "valor_solicitado": "130.46",
  "valor_reembolsavel": "90.00",
  "valor_nao_reembolsavel": "40.46",
  "status": "PARCIAL",
  "motivos": []
}
```

`valor_original` representa o valor normalizado na moeda de origem.

`moeda_original` identifica essa moeda.

Os campos:

```text
valor_solicitado
valor_reembolsavel
valor_nao_reembolsavel
```

representam valores em BRL utilizados pelo cálculo.

O resumo também é expresso em BRL.

Os status possíveis são:

- `APROVADA`;
- `PARCIAL`;
- `RECUSADA`.

Toda despesa `PARCIAL` ou `RECUSADA` possui ao menos um motivo.

---

## Estrutura do projeto

```text
.
├── CLAUDE.md
├── README.md
├── exemplos/
│   ├── despesas-exemplo.json
│   └── envelope/
├── specs/
│   └── 001-motor-reembolso/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── DECISIONS.md
├── src/
├── tests/
└── docs/
    ├── sessions/
    └── RELATORIO.md
```

---

## Documentação da especificação

A fonte de verdade para o comportamento é:

```text
specs/001-motor-reembolso/spec.md
```

O plano técnico está em:

```text
specs/001-motor-reembolso/plan.md
```

As tasks e a matriz de rastreabilidade estão em:

```text
specs/001-motor-reembolso/tasks.md
```

Mudanças posteriores à baseline estão registradas em:

```text
specs/001-motor-reembolso/DECISIONS.md
```

O envelope original da mudança de requisito foi preservado em:

```text
exemplos/envelope/
```

---

## Evolução da Política v3 para v4

A baseline inicial implementava a Política v3.

Depois da conclusão e validação dessa baseline, a Política v4 invalidou algumas premissas, principalmente:

```text
limites fixos
      ↓
limites externos por centro de custo

política única
      ↓
política específica + política padrão

somente BRL
      ↓
múltiplas moedas + conversão histórica

categorias globais
      ↓
categorias determinadas pela política
```

A evolução foi realizada seguindo:

```text
envelope
   ↓
spec.md
   ↓
DECISIONS.md
   ↓
tasks.md
   ↓
plan.md
   ↓
testes
   ↓
implementação
```

A mudança está registrada como `D-001` no log de decisões.

---

## Aprovação manual

O envelope da Política v4 apresenta uma fila de aprovação manual como requisito opcional.

Essa funcionalidade **não foi implementada nesta entrega**.

A decisão está explicitamente registrada na especificação como fora de escopo, evitando introduzir estados ou comportamentos opcionais antes da conclusão dos requisitos obrigatórios.

---

## Processo de desenvolvimento

O projeto segue Spec Driven Development.

Mudanças de comportamento devem seguir:

```text
spec
  ↓
DECISIONS.md
  ↓
tasks
  ↓
testes
  ↓
implementação
```

Os commits de teste e implementação referenciam suas respectivas tasks, por exemplo:

```text
test(T-020): cobre ausencia de cotacao utilizavel
feat(T-020): trata ausencia de cotacao utilizavel
```

A Política v4 continua a numeração das tasks da baseline em vez de substituir seu histórico.