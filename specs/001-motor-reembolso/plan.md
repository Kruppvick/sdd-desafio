# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3.12+ | O problema é predominantemente composto por regras de negócio, transformação de dados e uma interface CLI. Python permite implementar esse fluxo com pouco código incidental e possui bom suporte nativo para JSON, datas e valores decimais. | Node.js e Go também atenderiam ao problema, mas não oferecem vantagem necessária para os requisitos atuais que justifique escolhê-los no lugar da linguagem adotada. |
| Testes | pytest | Permite escrever testes unitários, de integração e casos parametrizados de forma simples e legível, facilitando a associação entre testes e os IDs `RN-NNN` da spec. | `unittest` atenderia ao requisito sem dependência externa, mas produziria testes mais verbosos para a quantidade de casos de borda prevista. |
| Parsing/validação | Biblioteca padrão do Python (`json`) com validação explícita da estrutura de entrada | O formato de entrada é pequeno e conhecido. A validação explícita mantém o comportamento visível e evita introduzir uma dependência apenas para modelar poucos campos. | Bibliotecas externas de validação foram descartadas nesta versão porque o formato atual não exige recursos que justifiquem a dependência adicional. |
| CLI | Biblioteca padrão do Python (`argparse`) | A interface exigida possui apenas um comando (`calcular`) e dois argumentos principais (`--input` e `--output`), portanto a biblioteca padrão é suficiente. | Frameworks externos de CLI foram descartados porque adicionariam dependência sem necessidade funcional para a interface atual. |
| Aritmética monetária | `decimal.Decimal` | Valores monetários precisam de representação decimal exata e arredondamento determinístico para centavos. | `float` foi descartado porque sua representação binária pode produzir diferenças indesejadas em comparações, somas e arredondamentos monetários. |
| Datas | `datetime.date` | As regras dependem de comparação entre datas sem necessidade de horário ou fuso horário. | Representar datas apenas como texto foi descartado porque o domínio exige comparações e validação de intervalos. |

---

## 2. Arquitetura

A solução será dividida em blocos com responsabilidades bem separadas, mantendo o núcleo de regras de negócio independente da leitura e escrita de arquivos.

```text
entrada JSON
    ↓
CLI
    ↓
leitura e validação da entrada
    ↓
normalização dos dados
    ↓
motor de cálculo de reembolso
    ↓
montagem do resultado
    ↓
serialização da saída
    ↓
arquivo JSON
```

### 2.1 CLI

Responsável por receber a operação `calcular` e os argumentos:

- `--input`: caminho do arquivo JSON de entrada;
- `--output`: caminho onde o resultado será gravado.

A CLI não contém regras de negócio. Sua responsabilidade é coordenar a execução e transformar falhas de entrada ou processamento em uma resposta apropriada para quem executou o comando.

### 2.2 Leitura e validação da entrada

Responsável por:

- abrir o arquivo informado em `--input`;
- interpretar o conteúdo JSON;
- verificar a presença e o formato dos dados necessários;
- transformar os dados externos em estruturas utilizadas pelo núcleo da aplicação.

Dados estruturalmente inválidos devem ser identificados antes da aplicação das regras de reembolso.

### 2.3 Normalização

Responsável por preparar os valores que serão utilizados pelo motor de cálculo.

Inclui:

- normalização monetária para duas casas decimais;
- normalização da categoria;
- conversão das datas para uma representação adequada para comparação.

A normalização ocorre antes da aplicação das regras que dependem desses valores.

### 2.4 Motor de cálculo de reembolso

É o núcleo da aplicação.

Responsável por avaliar as despesas na ordem original da entrada e aplicar as regras definidas na `spec.md`, incluindo:

- elegibilidade da despesa;
- competência;
- duplicidade;
- exigência de nota fiscal;
- limites de cada categoria;
- consumo dos limites diários;
- cálculo do valor reembolsável;
- definição do status;
- geração dos motivos da decisão.

O motor recebe dados já validados e normalizados e não é responsável por ler ou escrever arquivos.

### 2.5 Controle dos limites

Durante o processamento, o motor mantém o consumo dos limites que dependem de data e categoria.

Para alimentação e transporte urbano, o consumo é identificado pela combinação:

```text
data + categoria
```

Somente valores efetivamente reembolsados são adicionados ao consumo do limite.

Hospedagem não compartilha um limite diário entre lançamentos na baseline v3; cada lançamento é tratado como uma diária conforme definido na spec.

### 2.6 Montagem do resultado

Responsável por transformar as decisões individuais produzidas pelo motor no contrato de saída definido na spec.

O resultado contém:

- identificação do colaborador;
- competência;
- resumo financeiro;
- decisão individual de cada despesa;
- valores solicitados, reembolsáveis e não reembolsáveis;
- status;
- motivos.

Os totais do resumo são calculados a partir das decisões individuais, evitando a existência de duas fontes diferentes para o mesmo valor.

### 2.7 Serialização da saída

Responsável por:

- transformar o resultado interno no schema JSON definido pela spec;
- representar valores monetários no formato de saída definido;
- gravar o conteúdo no caminho informado em `--output`.

Essa camada não realiza cálculos de política.

### Fronteiras

A principal fronteira arquitetural separa:

```text
I/O e interface
```

de:

```text
regras de negócio
```

A CLI, leitura de arquivos e escrita do resultado ficam fora do núcleo de cálculo.

O motor de reembolso não conhece caminhos de arquivos, argumentos da CLI ou detalhes de serialização JSON.

Essa separação permite testar as regras de negócio diretamente, sem necessidade de criar arquivos ou executar a CLI em cada teste.

Os testes ponta a ponta exercitam a integração completa:

```text
arquivo de entrada
    ↓
CLI
    ↓
motor
    ↓
arquivo de saída
```

enquanto a maior parte dos testes das regras pode atuar diretamente sobre o núcleo de cálculo.

---

## 3. Modelo de dados

O modelo interno deve representar separadamente os dados recebidos, os dados normalizados e o resultado da avaliação de cada despesa.

O objetivo é impedir que detalhes do JSON de entrada se misturem diretamente com as regras de negócio.

### 3.1 Colaborador

Representa o colaborador associado ao conjunto de despesas.

Campos:

- `id`: identificador do colaborador;
- `nome`: nome do colaborador;
- `centro_custo`: centro de custo informado na entrada.

Na baseline v3, o centro de custo é preservado para rastreabilidade, mas não altera os limites aplicados.

### 3.2 Período

Representa o período de competência utilizado para avaliação das despesas.

Campos:

- `competencia`: competência informada no formato `AAAA-MM`;
- `inicio`: data inicial da competência;
- `fim`: data final da competência.

As datas são convertidas para uma representação que permita comparação cronológica.

### 3.3 Despesa de entrada

Representa os dados recebidos para cada lançamento antes das normalizações.

Campos:

- `id`;
- `data`;
- `categoria`;
- `descricao`;
- `fornecedor`;
- `valor`;
- `tem_nota_fiscal`.

Essa representação preserva os dados originais recebidos e serve como origem para a normalização.

### 3.4 Despesa normalizada

Representa os valores efetivamente utilizados pelo motor de cálculo.

Campos:

- `id`;
- `data`;
- `categoria_original`;
- `categoria_normalizada`;
- `descricao`;
- `fornecedor`;
- `valor_original`;
- `valor_normalizado`;
- `tem_nota_fiscal`;
- `indice_entrada`.

`indice_entrada` preserva a posição original da despesa e permite aplicar de forma determinística as regras que dependem da ordem dos lançamentos.

`categoria_original` e `valor_original` são preservados para rastreabilidade.

`categoria_normalizada` e `valor_normalizado` são utilizados pelas regras de negócio.

### 3.5 Motivo

Representa uma justificativa associada à decisão sobre uma despesa.

Campos:

- `codigo`: identificador estável do motivo;
- `descricao`: explicação legível para quem consultar o resultado.

Exemplos de códigos:

- `LIMITE_DIARIO_ALIMENTACAO`;
- `LIMITE_DIARIO_TRANSPORTE`;
- `LIMITE_HOSPEDAGEM`;
- `NOTA_FISCAL_OBRIGATORIA`;
- `FORA_COMPETENCIA`;
- `DUPLICATA`;
- `CATEGORIA_NAO_REEMBOLSAVEL`;
- `VALOR_NAO_POSITIVO`.

Os códigos são utilizados nos testes e na rastreabilidade do comportamento. As descrições são destinadas à leitura humana.

### 3.6 Resultado individual da despesa

Representa a decisão final sobre um lançamento.

Campos:

- `id`;
- `indice_entrada`;
- `valor_solicitado`;
- `valor_reembolsavel`;
- `valor_nao_reembolsavel`;
- `status`;
- `motivos`.

Os possíveis valores de `status` são:

- `APROVADA`;
- `PARCIAL`;
- `RECUSADA`.

O valor solicitado corresponde ao valor já normalizado conforme a regra de normalização monetária.

### 3.7 Controle de limite diário

Representa quanto de um limite compartilhado já foi consumido durante o processamento.

A chave conceitual é formada por:

```text
(data, categoria)
```

O valor associado à chave representa o total já reembolsado naquela categoria e data.

Exemplo conceitual:

```text
(2026-07-03, alimentacao) -> 60.00
(2026-07-06, transporte_urbano) -> 80.00
```

Esse controle é atualizado apenas com valores efetivamente reembolsados.

### 3.8 Controle de duplicidade

Durante a avaliação das despesas, é mantido o conjunto de identidades de lançamentos já observados.

A identidade utilizada na baseline v3 é composta por:

```text
(
  data,
  categoria_normalizada,
  descricao,
  fornecedor,
  valor_normalizado,
  tem_nota_fiscal
)
```

O campo `id` não faz parte dessa identidade.

Se uma identidade já tiver sido observada anteriormente, a nova ocorrência é considerada duplicada.

### 3.9 Resumo

Representa os totais consolidados após a avaliação de todas as despesas.

Campos:

- `total_solicitado`;
- `total_reembolsavel`;
- `total_nao_reembolsavel`.

Os totais são derivados dos resultados individuais e não são calculados por um fluxo separado.

### 3.10 Resultado do cálculo

Representa o resultado completo produzido pelo motor.

Contém:

- identificação do colaborador;
- período processado;
- resumo;
- lista de resultados individuais das despesas.

O resultado interno é posteriormente convertido para o schema JSON definido na `spec.md`.

### Fluxo dos dados

```text
JSON de entrada
      ↓
dados de entrada
      ↓
validação
      ↓
despesas normalizadas
      ↓
motor de regras
      ↓
resultados individuais
      ↓
resumo
      ↓
resultado completo
      ↓
JSON de saída
```

A separação entre dados originais, valores normalizados e resultados evita que uma regra altere silenciosamente a informação recebida e facilita a auditoria do cálculo.

---

## 4. Como a política é representada

Na baseline v3, a política de reembolso é representada por uma estrutura central de configuração do domínio.

Essa estrutura concentra:

- categorias reembolsáveis;
- limites monetários;
- periodicidade dos limites;
- valor a partir do qual a nota fiscal é obrigatória;
- percentual de acréscimo previsto para viagem.

Exemplo conceitual:

```text
alimentacao:
  limite: 60.00
  periodicidade: dia

transporte_urbano:
  limite: 80.00
  periodicidade: dia

hospedagem:
  limite: 250.00
  periodicidade: diaria

nota_fiscal_obrigatoria_acima_de:
  100.00

acrescimo_em_viagem_percentual:
  50
```

### Decisão

Os valores da política ficam centralizados em uma única estrutura conhecida pelo motor de cálculo.

O motor consulta essa estrutura para obter limites e parâmetros, em vez de repetir valores monetários em diferentes partes das regras.

### Alternativa descartada — valores espalhados pelo código

Foi descartada a opção de escrever diretamente valores como `60.00`, `80.00` e `250.00` dentro de cada trecho responsável por aplicar uma regra.

**Motivo:** isso criaria múltiplas fontes de verdade e aumentaria o risco de inconsistência quando algum limite precisasse ser alterado.

### Alternativa descartada — arquivo externo na baseline v3

Também foi descartada, para a baseline inicial, a leitura da política a partir de um arquivo externo.

**Motivo:** a Política v3 é fixa para todos os colaboradores e o requisito inicial não exige alteração dinâmica desses valores durante a execução. Introduzir uma fonte externa neste momento aumentaria a complexidade sem atender a uma necessidade existente na baseline.

### Consequência

A centralização torna simples:

- localizar os parâmetros da política;
- alterar um limite sem procurar o mesmo valor em vários pontos;
- testar o motor com diferentes valores de configuração;
- evitar números monetários duplicados nas regras.

Por outro lado, a baseline v3 ainda pressupõe que a política conhecida pela aplicação é única e está definida junto com o sistema.

Caso surja um requisito para carregar políticas diferentes dinamicamente, essa decisão deverá ser revisitada no `plan.md` e registrada como impacto arquitetural da mudança.

---

## 5. Decisões técnicas

### DT-001 — Representação monetária com Decimal

**Contexto:** O sistema realiza comparações, somas, limites e arredondamentos sobre valores monetários. A entrada também pode conter valores com mais de duas casas decimais.

**Decisão:** Utilizar `decimal.Decimal` para representar valores monetários durante o processamento.

**Alternativa descartada:** Utilizar `float`.

**Motivo da rejeição:** `float` utiliza representação binária e pode introduzir diferenças de precisão em operações monetárias, principalmente em comparações de limites e arredondamentos.

**Consequência:** Os cálculos monetários permanecem determinísticos e compatíveis com a normalização para centavos definida na spec. Em contrapartida, valores recebidos do JSON precisam ser convertidos explicitamente para a representação decimal adotada.

---

### DT-002 — Núcleo de cálculo independente de I/O

**Contexto:** As regras de reembolso precisam ser testadas em muitos casos de borda sem depender da criação de arquivos ou da execução da CLI.

**Decisão:** Manter o motor de cálculo independente da leitura e escrita de arquivos.

A CLI é responsável por receber caminhos, ler a entrada e gravar a saída. O motor recebe estruturas já preparadas para processamento e devolve um resultado estruturado.

**Alternativa descartada:** Fazer o próprio motor abrir o arquivo de entrada e gravar o arquivo de saída.

**Motivo da rejeição:** Misturar I/O e regras de negócio tornaria os testes mais lentos e aumentaria o acoplamento entre a política de reembolso e a interface exigida pelo desafio.

**Consequência:** As regras podem ser testadas diretamente em memória. A integração completa com arquivos fica restrita a testes específicos da CLI.

---

### DT-003 — Validação explícita da entrada

**Contexto:** O formato de entrada é conhecido e relativamente pequeno.

**Decisão:** Validar explicitamente os campos obrigatórios e os formatos necessários antes de executar o motor de cálculo.

**Alternativa descartada:** Permitir que erros de campos ausentes ou formatos inválidos apareçam somente durante a aplicação das regras.

**Motivo da rejeição:** Isso produziria falhas difíceis de interpretar e poderia confundir erro estrutural da entrada com recusa de uma despesa pela política.

**Consequência:** Existe uma fronteira clara entre:

- entrada inválida;
- despesa válida estruturalmente, mas não reembolsável.

---

### DT-004 — Separar normalização de avaliação

**Contexto:** Algumas regras dependem de valores previamente normalizados, como categoria, dinheiro e datas.

**Decisão:** Realizar uma etapa explícita de normalização antes da aplicação das regras de negócio.

**Alternativa descartada:** Normalizar categoria e valores repetidamente dentro de cada regra.

**Motivo da rejeição:** Isso aumentaria duplicação e poderia fazer regras diferentes avaliarem representações diferentes do mesmo dado.

**Consequência:** Todas as regras recebem uma representação consistente da despesa. Os valores originais continuam preservados para rastreabilidade.

---

### DT-005 — Processamento determinístico na ordem da entrada

**Contexto:** Os limites diários podem ser insuficientes para reembolsar integralmente todas as despesas de uma mesma categoria e data.

A spec determina que esses limites são consumidos na ordem dos lançamentos.

**Decisão:** Preservar a ordem original das despesas durante todo o processamento e registrar o índice da entrada.

**Alternativa descartada:** Ordenar despesas por valor, categoria, identificador ou data antes do cálculo.

**Motivo da rejeição:** Qualquer reordenação poderia alterar qual despesa recebe a parcela disponível do limite e produzir comportamento diferente daquele definido na spec.

**Consequência:** A mesma entrada sempre produz a mesma distribuição individual dos limites.

---

### DT-006 — Controle de limite por chave de data e categoria

**Contexto:** Alimentação e transporte urbano possuem limites compartilhados entre despesas da mesma categoria e data.

**Decisão:** Manter durante o cálculo uma estrutura associando cada combinação de data e categoria ao valor já reembolsado.

Exemplo conceitual:

```text
(data, categoria) -> valor_consumido
```

**Alternativa descartada:** Recalcular a soma das despesas anteriores toda vez que uma nova despesa for avaliada.

**Motivo da rejeição:** O recálculo repetido aumenta a complexidade e torna menos explícito o estado do limite disponível durante o processamento.

**Consequência:** O motor consegue obter diretamente quanto do limite já foi consumido e atualizar esse valor somente quando houver reembolso efetivo.

---

### DT-007 — Identidade de duplicidade separada do ID do lançamento

**Contexto:** A política exige tratamento de duplicatas, mas lançamentos duplicados podem possuir identificadores diferentes.

**Decisão:** Construir uma identidade de duplicidade com os campos definidos pela spec e manter as identidades já encontradas durante o processamento.

A identidade considera:

```text
data
categoria_normalizada
descricao
fornecedor
valor_normalizado
tem_nota_fiscal
```

**Alternativa descartada:** Utilizar `despesas[].id` como identificador da duplicidade.

**Motivo da rejeição:** Dois registros da mesma despesa podem ter IDs distintos, como ocorre no arquivo de exemplo.

**Consequência:** O sistema consegue detectar lançamentos repetidos mesmo quando os identificadores são diferentes.

---

### DT-008 — Códigos estáveis para motivos

**Contexto:** O resultado precisa justificar recusas e reembolsos parciais, e os testes automatizados precisam verificar essas decisões.

**Decisão:** Cada motivo possui um código estável destinado ao contrato e uma descrição destinada à leitura humana.

Exemplo:

```text
codigo: NOTA_FISCAL_OBRIGATORIA
descricao: Despesas acima de R$ 100,00 exigem nota fiscal.
```

**Alternativa descartada:** Utilizar somente textos livres como justificativa.

**Motivo da rejeição:** Alterações de redação poderiam quebrar testes e consumidores da saída mesmo quando a regra permanecesse igual.

**Consequência:** Testes podem validar os códigos enquanto as descrições permanecem livres para melhorias de clareza.

---

### DT-009 — Resumo derivado das decisões individuais

**Contexto:** A saída apresenta tanto decisões por despesa quanto totais consolidados.

**Decisão:** Calcular o resumo a partir dos resultados individuais produzidos pelo motor.

**Alternativa descartada:** Manter um cálculo independente para os totais durante a execução.

**Motivo da rejeição:** Dois mecanismos distintos para calcular os mesmos valores poderiam divergir e criar inconsistência entre itens e resumo.

**Consequência:** As decisões individuais constituem a única fonte para os totais finais.

---

### DT-010 — Biblioteca padrão para CLI e JSON

**Contexto:** A interface exigida é pequena: uma operação `calcular`, um arquivo de entrada e um arquivo de saída.

**Decisão:** Utilizar recursos da biblioteca padrão do Python para CLI e JSON.

**Alternativa descartada:** Adotar frameworks adicionais de CLI ou serialização.

**Motivo da rejeição:** Não existe requisito atual que justifique o aumento de dependências e complexidade.

**Consequência:** A aplicação possui poucas dependências externas e o ambiente necessário para execução permanece simples.

---

### DT-011 — Não implementar um motor genérico de regras

**Contexto:** A baseline v3 possui um conjunto pequeno e conhecido de regras de reembolso.

**Decisão:** Implementar explicitamente o fluxo de avaliação da política, mantendo funções e responsabilidades pequenas, sem criar uma infraestrutura genérica de rule engine.

**Alternativa descartada:** Criar registro dinâmico de regras, plugins, DSL de política ou pipeline genérico configurável.

**Motivo da rejeição:** Essas abstrações aumentariam a complexidade sem atender a um requisito existente na baseline.

**Consequência:** A implementação inicial permanece simples e fácil de auditar. Caso uma mudança futura exija políticas altamente dinâmicas, essa decisão deverá ser reavaliada.

---

## 6. Estratégia de testes

A estratégia de testes deve garantir que cada regra de negócio definida na `spec.md` possua pelo menos uma verificação automatizada e que as interações entre regras também sejam testadas.

A suíte será dividida em três níveis:

- testes unitários para regras e normalizações;
- testes de integração para o fluxo completo do motor;
- testes ponta a ponta para a interface CLI.

### 6.1 Testes unitários

A maior parte da suíte será composta por testes unitários.

Eles exercitam diretamente o núcleo de cálculo, sem leitura ou escrita de arquivos.

Devem cobrir:

- normalização monetária;
- normalização de categoria;
- competência;
- nota fiscal;
- duplicidade;
- limites de alimentação;
- limites de transporte urbano;
- limite de hospedagem;
- reembolso parcial;
- valores não positivos;
- consumo de limites;
- ordem dos lançamentos;
- cálculo dos totais;
- geração de status e motivos.

Os testes unitários devem utilizar entradas pequenas, contendo somente os dados necessários para demonstrar o comportamento da regra testada.

### 6.2 Testes de integração

Os testes de integração verificam a interação entre múltiplas regras dentro do motor.

Casos importantes incluem:

- despesa sem nota fiscal que também ultrapassaria o limite diário;
- duplicata que não deve consumir novamente o limite;
- categoria não reembolsável junto de despesas válidas;
- múltiplas despesas da mesma categoria concorrendo pelo mesmo limite;
- normalização monetária antes da verificação da obrigatoriedade de nota fiscal;
- normalização da categoria antes da verificação de duplicidade;
- valores não positivos junto de despesas positivas;
- fechamento dos totais do resumo.

O objetivo é verificar não apenas cada regra isoladamente, mas também a precedência definida na seção 8 da spec.

### 6.3 Testes ponta a ponta

Os testes ponta a ponta exercitam a interface completa exigida pelo desafio:

```text
arquivo JSON
    ↓
CLI
    ↓
validação
    ↓
motor de cálculo
    ↓
arquivo JSON de saída
```

Devem verificar pelo menos:

- execução do comando `calcular`;
- leitura do arquivo informado em `--input`;
- criação do arquivo informado em `--output`;
- saída em JSON válido;
- presença das decisões individuais;
- presença do resumo;
- código de saída de sucesso para uma entrada válida.

Também deve existir pelo menos um teste ponta a ponta utilizando `exemplos/despesas-exemplo.json`.

### 6.4 Cobertura das regras da spec

Cada regra `RN-NNN` deve estar associada a pelo menos um teste automatizado.

A rastreabilidade será feita por meio do nome dos testes e da matriz existente em `tasks.md`.

Exemplos de nomes:

```text
test_rn001_limite_diario_alimentacao
test_rn002_limite_diario_transporte
test_rn003_limite_hospedagem
test_rn005_exatamente_100_sem_nota
test_rn005_100_01_sem_nota
test_rn007_inicio_competencia_inclusivo
test_rn008_detecta_duplicata_com_ids_diferentes
test_rn010_normaliza_categoria_maiuscula
test_rn011_arredonda_33_335_para_33_34
test_rn012_valor_negativo_nao_afeta_totais
test_rn013_despesa_recusada_nao_consome_limite
test_rn014_respeita_ordem_da_entrada
test_rn015_resumo_fecha_com_decisoes
```

Quando um teste cobre mais de uma regra, o nome pode destacar o comportamento principal e a task deve registrar todas as regras relacionadas.

### 6.5 Casos de borda

Todos os casos definidos na seção 7 da `spec.md` devem possuir cobertura automatizada.

Os casos de fronteira devem receber atenção especial, incluindo:

- R$ 59,99, R$ 60,00 e R$ 60,01 para alimentação;
- R$ 79,99, R$ 80,00 e R$ 80,01 para transporte urbano;
- R$ 249,99, R$ 250,00 e R$ 250,01 para hospedagem;
- R$ 99,99, R$ 100,00 e R$ 100,01 para nota fiscal;
- primeiro e último dia da competência;
- dia anterior e posterior à competência;
- valores com mais de duas casas decimais;
- valor igual a zero;
- valor negativo;
- duplicatas e não duplicatas semelhantes;
- categoria em caixa diferente;
- múltiplas despesas concorrendo pelo mesmo limite.

### 6.6 Testes parametrizados

Casos com a mesma estrutura e diferentes valores de entrada devem preferencialmente ser representados como testes parametrizados.

Exemplos:

```text
59.99 -> 59.99
60.00 -> 60.00
60.01 -> 60.00
```

e:

```text
99.99 sem nota  -> nota não obrigatória
100.00 sem nota -> nota não obrigatória
100.01 sem nota -> recusada
```

Isso reduz repetição sem esconder o comportamento esperado de cada fronteira.

### 6.7 Invariantes

Além dos exemplos específicos, a suíte deve verificar propriedades que precisam permanecer verdadeiras para qualquer cálculo válido.

Para despesas com valor solicitado positivo:

```text
valor_solicitado =
valor_reembolsavel + valor_nao_reembolsavel
```

Também deve ser sempre verdadeiro:

```text
valor_reembolsavel >= 0
```

e:

```text
valor_reembolsavel <= valor_solicitado
```

Para o resultado completo:

```text
resumo.total_solicitado =
resumo.total_reembolsavel + resumo.total_nao_reembolsavel
```

Os totais do resumo também devem ser exatamente iguais às somas dos valores apresentados nas decisões individuais.

### 6.8 Testes de regressão

Quando um erro for encontrado durante a implementação, a correção deve ser acompanhada de um teste que reproduza o comportamento incorreto antes da alteração.

Esse teste passa a fazer parte permanente da suíte para impedir que o mesmo problema reapareça.

Quando o erro exigir mudança da especificação, a `spec.md` deve ser atualizada antes da implementação da correção e a mudança registrada em `DECISIONS.md`.

### 6.9 Critério para concluir uma task

Uma task de implementação só pode ser considerada concluída quando:

1. os testes diretamente relacionados à task passam;
2. a suíte completa existente continua passando;
3. o comportamento implementado corresponde às regras da `spec.md`;
4. nenhum comportamento de negócio novo foi introduzido apenas no código.

A execução dos testes relevantes deve ocorrer antes do commit da task.

### 6.10 Proporção esperada

A maior parte dos testes ficará no nível unitário, onde as regras podem ser verificadas de forma rápida e isolada.

Os testes de integração serão utilizados para combinações e precedência entre regras.

Uma quantidade menor de testes ponta a ponta será utilizada para verificar a interface CLI e o contrato completo de entrada e saída.

A intenção é obter uma pirâmide aproximadamente nesta proporção:

```text
muitos testes unitários
        ↓
alguns testes de integração
        ↓
poucos testes ponta a ponta
```

Essa distribuição permite alta cobertura das regras sem tornar toda a suíte dependente de arquivos e execução da CLI.

---

## 7. Riscos

Os riscos abaixo representam situações que podem comprometer a correção, a rastreabilidade ou a capacidade de evolução do motor de reembolso.

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Regra de negócio ser implementada com interpretação diferente da spec | Média | Alto | Toda implementação deve referenciar uma `RN-NNN`; qualquer dúvida ou mudança de comportamento deve ser resolvida primeiro na `spec.md` |
| Uso incorreto de ponto flutuante em valores monetários | Baixa | Alto | Utilizar `Decimal` em todos os cálculos monetários e manter testes específicos de arredondamento e fronteiras |
| Ordem de avaliação das regras alterar o resultado | Média | Alto | Seguir explicitamente a precedência definida na seção 8 da spec e criar testes de integração para combinações de regras |
| Despesas recusadas consumirem limite indevidamente | Média | Alto | Atualizar o consumo de limite somente após o cálculo do valor efetivamente reembolsado e manter testes de regressão para esse comportamento |
| Identificação de duplicatas gerar falso positivo | Média | Médio/Alto | Utilizar somente os campos definidos em RN-008 e manter documentada a limitação da heurística na spec |
| Identificação de duplicatas deixar passar lançamentos repetidos | Média | Médio/Alto | Normalizar categoria e valor antes da comparação e testar duplicatas com IDs diferentes e pequenas variações nos campos |
| Alteração acidental da ordem original das despesas | Baixa | Alto | Preservar `indice_entrada` e não ordenar as despesas antes do cálculo |
| Divergência entre valores individuais e resumo | Baixa | Alto | Derivar o resumo exclusivamente dos resultados individuais e validar invariantes nos testes |
| Entrada inválida ser confundida com despesa não reembolsável | Média | Médio | Separar validação estrutural da aplicação da política e tratar falha estrutural antes da execução do motor |
| Texto livre ser usado indevidamente para inferir dados de negócio | Média | Alto | Não utilizar `descricao` ou `fornecedor` para inferir viagem, quantidade de diárias ou outras informações ausentes da entrada |
| Testes escritos reproduzirem o mesmo erro da implementação | Média | Alto | Derivar casos esperados da spec, utilizar casos de borda explícitos e revisar manualmente os testes mais relevantes |
| Alteração de regra não ser refletida nos testes | Média | Alto | Manter rastreabilidade entre `RN-NNN`, task e teste na matriz de cobertura do `tasks.md` |
| Alteração de regra não ser registrada no histórico da spec | Média | Alto | Toda mudança posterior à baseline deve possuir entrada correspondente em `DECISIONS.md` |
| Complexidade arquitetural desnecessária dificultar manutenção | Média | Médio | Preferir funções e estruturas explícitas e evitar rule engine genérico, plugins ou abstrações sem requisito concreto |
| Política mudar e os valores ficarem difíceis de localizar | Baixa na baseline | Médio | Manter todos os parâmetros da política centralizados em uma única estrutura em vez de espalhados pelo código |
| Dependência excessiva da CLI dificultar testes | Baixa | Médio | Manter o motor independente de I/O e concentrar testes das regras diretamente no núcleo |
| Arquivo de saída ser gerado parcialmente em caso de erro | Baixa | Médio | Validar e calcular o resultado antes de concluir a gravação do arquivo de saída |
| Código funcionar para o exemplo fornecido, mas falhar em casos de fronteira | Média | Alto | Cobrir sistematicamente os casos da seção 7 da spec e não utilizar apenas `despesas-exemplo.json` como teste |
| Nova funcionalidade ser adicionada pelo agente sem estar na spec | Média | Alto | Incluir a proibição no `CLAUDE.md`, revisar diffs e rejeitar alterações de negócio que não tenham requisito correspondente |
| Uma mudança futura exigir alteração em muitos pontos do sistema | Média | Médio/Alto | Manter política centralizada, motor isolado de I/O e decisões individuais como fonte única para o resumo |

### Riscos aceitos na baseline v3

Alguns riscos são conhecidos e aceitos conscientemente porque não podem ser eliminados com os dados disponíveis.

#### Identificação de duplicidade

Dois gastos legítimos podem coincidir em todos os campos utilizados para detectar duplicatas.

Esse risco é aceito porque a entrada não possui um identificador de transação ou documento que permita distinguir inequivocamente duas despesas.

A limitação está registrada na `spec.md`.

#### Quantidade de diárias

O sistema pode aplicar apenas uma diária a um lançamento cuja descrição mencione várias noites.

Esse risco é aceito porque a entrada não fornece uma quantidade estruturada de diárias e a baseline proíbe inferir valores financeiros a partir de texto livre.

#### Condição de viagem

O sistema pode aplicar limites padrão a uma despesa que, no mundo real, ocorreu durante uma viagem.

Esse risco é aceito porque a entrada não contém um indicador estruturado de viagem.

#### Data de lançamento

O sistema utiliza `despesas[].data` para verificar competência, embora a política utilize o termo "lançada".

Esse risco é aceito porque não existe uma data específica de submissão ou lançamento na entrada.

### Critério de reação a riscos encontrados durante a implementação

Se um risco se materializar e revelar que o comportamento definido na spec é insuficiente ou incorreto, a correção deve seguir esta ordem:

```text
problema identificado
        ↓
revisão da spec
        ↓
registro em DECISIONS.md
        ↓
atualização ou criação de tasks
        ↓
teste que demonstra o comportamento esperado
        ↓
alteração da implementação
        ↓
execução da suíte completa
```

Um problema de regra de negócio não deve ser corrigido apenas no código.