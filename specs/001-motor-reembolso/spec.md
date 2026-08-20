# Spec — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Status:** Política v4 · **Última alteração:** 2026-08-19

> **Evolução da especificação:** esta versão incorpora as mudanças recebidas
> no envelope da Política de Reembolso v4. A baseline anterior correspondia
> à versão 1.0 desta especificação e à Política de Reembolso v3.
>
> O histórico e os impactos dessa mudança são registrados em `DECISIONS.md`.

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

---

## 1. Problema

O financeiro analisa despesas manualmente, o que torna o processo lento e sujeito a interpretações inconsistentes.

## 2. Objetivo

Dado um conjunto de despesas e um período de competência, determinar quanto de cada despesa é reembolsável e justificar cada decisão.

## 3. Fora de escopo

- Não realiza pagamento ou transferência de valores ao colaborador.
- Não altera, corrige ou complementa os dados das despesas recebidas.
- Não consulta sistemas externos para validar fornecedor ou nota fiscal.
- Não verifica se uma nota fiscal é autêntica; utiliza apenas o campo informado na entrada.
- Não determina se a despesa foi realizada por motivo profissional.
- Não infere se o colaborador está em viagem quando essa informação não estiver explicitamente disponível na entrada.
- Não interpreta a descrição da despesa para descobrir informações ausentes, como quantidade de diárias de hospedagem.
- Não consulta serviços externos para obter cotações de moedas; utiliza exclusivamente as informações de câmbio disponibilizadas para o cálculo.
- Não aplica regras contábeis, tributárias ou trabalhistas além da política de reembolso fornecida.
- Não modifica a política de reembolso recebida; apenas aplica as regras e interpretações documentadas nesta especificação.

### 3.1 Aprovação manual

A funcionalidade de aprovação manual apresentada como opcional na Política v4 está explicitamente fora do escopo desta entrega.

O motor não irá:

- encaminhar despesas para aprovação humana;
- manter estados como `PENDENTE_APROVACAO`;
- registrar aprovador;
- receber decisão posterior de um aprovador;
- implementar fluxo de aprovação ou rejeição manual;
- alterar automaticamente uma decisão com base em aprovação externa.

A decisão de não implementar essa funcionalidade nesta versão foi tomada porque ela é opcional no envelope recebido e não é necessária para atender aos requisitos obrigatórios da Política v4.

Caso a aprovação manual se torne obrigatória futuramente, sua inclusão deverá ocorrer por meio de nova alteração da especificação antes de qualquer mudança na implementação.

## 4. Entrada e saída

### 4.1 Entrada

A entrada principal deve seguir o formato definido nos exemplos fornecidos para o desafio.

A Política v4 mantém a estrutura existente de colaborador, período e despesas e acrescenta suporte a despesas em moeda estrangeira.

#### Colaborador

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | Identificador único do colaborador | Sim |
| `colaborador.nome` | texto | Nome do colaborador | Sim |
| `colaborador.centro_custo` | texto | Centro de custo utilizado para determinar a política de reembolso aplicável | Sim |

Na Política v4, `colaborador.centro_custo` deixa de ser apenas informativo e passa a determinar os limites e categorias aplicáveis ao colaborador.

Quando não existir uma política específica para o centro de custo informado, será utilizada a política padrão.

#### Período

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `periodo.competencia` | texto no formato `AAAA-MM` | Competência à qual o pedido de reembolso se refere | Sim |
| `periodo.inicio` | data no formato `AAAA-MM-DD` | Data inicial do período de competência | Sim |
| `periodo.fim` | data no formato `AAAA-MM-DD` | Data final do período de competência | Sim |

#### Despesas

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `despesas` | lista | Conjunto de despesas que serão avaliadas | Sim |
| `despesas[].id` | texto | Identificador do lançamento da despesa | Sim |
| `despesas[].data` | data no formato `AAAA-MM-DD` | Data associada à despesa | Sim |
| `despesas[].categoria` | texto | Categoria informada para a despesa | Sim |
| `despesas[].descricao` | texto | Descrição fornecida para a despesa | Sim |
| `despesas[].fornecedor` | texto | Nome do fornecedor informado | Sim |
| `despesas[].valor` | número | Valor informado na moeda original da despesa | Sim |
| `despesas[].moeda` | texto | Código da moeda em que `valor` está expresso | Não |
| `despesas[].tem_nota_fiscal` | booleano | Indica se a despesa possui nota fiscal (`true` ou `false`) | Sim |

Quando `despesas[].moeda` estiver ausente, a moeda da despesa será considerada `BRL`.

A moeda não será inferida a partir de descrição, fornecedor ou qualquer outro campo textual.

### 4.2 Dados auxiliares da Política v4

Além da entrada principal de despesas, o cálculo da Política v4 depende de dois conjuntos de dados fornecidos junto à política:

#### Política de reembolso

A política de reembolso contém:

- limites padrão;
- limites e categorias específicos por centro de custo;
- parâmetros gerais aplicáveis ao cálculo.

O centro de custo informado em `colaborador.centro_custo` determina qual política será utilizada.

Quando não existir configuração específica para o centro de custo informado, aplica-se a política padrão.

#### Cotações de moedas

Os dados de câmbio contêm taxas históricas utilizadas para converter despesas em moeda estrangeira para BRL.

Despesas cuja moeda seja `BRL` não necessitam de conversão.

O sistema utiliza exclusivamente os dados de câmbio fornecidos para o cálculo e não consulta serviços externos para obter cotações ausentes.

O comportamento quando uma cotação necessária não estiver disponível é definido nas regras de negócio e ambiguidades desta especificação.

### 4.3 Representação dos valores

Para cada despesa, o sistema distingue:

- o valor original informado;
- a moeda original;
- o valor em BRL utilizado para aplicação da política.

Quando a moeda for `BRL`, o valor considerado em BRL corresponde ao próprio valor monetário normalizado.

Quando a moeda for diferente de `BRL`, o valor considerado em BRL será obtido pela conversão cambial definida nas regras de negócio.

A conversão não substitui nem elimina o valor e a moeda originalmente informados.

### 4.4 Saída

A saída deve permitir rastrear cada despesa recebida na entrada até sua respectiva decisão de reembolso.

Valores monetários da saída são representados como texto decimal com exatamente duas casas decimais, no formato `"0.00"`.

| Campo | Tipo | Significado |
|---|---|---|
| `schema_version` | texto | Versão do formato da saída |
| `colaborador.id` | texto | Identificador do colaborador processado |
| `periodo.competencia` | texto | Competência processada |
| `resumo.total_solicitado` | texto monetário | Soma dos valores positivos considerados em BRL para aplicação da política |
| `resumo.total_reembolsavel` | texto monetário | Soma dos valores reembolsáveis em BRL |
| `resumo.total_nao_reembolsavel` | texto monetário | Soma das parcelas não reembolsáveis em BRL |
| `despesas` | lista | Resultados individuais das despesas avaliadas |
| `despesas[].id` | texto | Identificador da despesa correspondente na entrada |
| `despesas[].valor_original` | texto monetário | Valor normalizado originalmente informado na despesa |
| `despesas[].moeda_original` | texto | Moeda original da despesa |
| `despesas[].valor_solicitado` | texto monetário | Valor em BRL utilizado para aplicação da política |
| `despesas[].valor_reembolsavel` | texto monetário | Valor que será reembolsado em BRL |
| `despesas[].valor_nao_reembolsavel` | texto monetário | Parcela positiva em BRL que não será reembolsada |
| `despesas[].status` | texto | Resultado da avaliação: `APROVADA`, `PARCIAL` ou `RECUSADA` |
| `despesas[].motivos` | lista | Justificativas para a decisão |
| `despesas[].motivos[].codigo` | texto | Código estável que identifica o motivo |
| `despesas[].motivos[].descricao` | texto | Explicação legível do motivo |

Os campos `valor_solicitado`, `valor_reembolsavel`, `valor_nao_reembolsavel` e os totais do resumo são sempre expressos em BRL.

Os campos `valor_original` e `moeda_original` preservam a informação recebida antes da conversão.

Para despesas cuja moeda original seja `BRL`, `valor_original` e `valor_solicitado` possuem o mesmo valor após a normalização monetária.

Para lançamentos cujo valor considerado em BRL seja menor ou igual a R$ 0,00:

- `valor_original` preserva o valor normalizado na moeda original;
- `moeda_original` preserva a moeda informada ou assumida;
- `valor_solicitado` preserva o valor considerado em BRL;
- `valor_reembolsavel` é `"0.00"`;
- `valor_nao_reembolsavel` é `"0.00"`;
- o status é `RECUSADA`;
- o lançamento não participa de `resumo.total_solicitado` nem de `resumo.total_nao_reembolsavel`.

#### Exemplo de saída

Para uma despesa de alimentação originalmente em BRL, com valor de R$ 72,50 e limite aplicável de R$ 60,00:

```json
{
  "schema_version": "2.0",
  "colaborador": {
    "id": "c-0417"
  },
  "periodo": {
    "competencia": "2026-07"
  },
  "resumo": {
    "total_solicitado": "72.50",
    "total_reembolsavel": "60.00",
    "total_nao_reembolsavel": "12.50"
  },
  "despesas": [
    {
      "id": "d-001",
      "valor_original": "72.50",
      "moeda_original": "BRL",
      "valor_solicitado": "72.50",
      "valor_reembolsavel": "60.00",
      "valor_nao_reembolsavel": "12.50",
      "status": "PARCIAL",
      "motivos": [
        {
          "codigo": "LIMITE_DIARIO_ALIMENTACAO",
          "descricao": "O limite diário disponível para alimentação foi atingido."
        }
      ]
    }
  ]
}
```

Os possíveis status continuam sendo:

- `APROVADA`: todo o valor solicitado positivo considerado em BRL é reembolsável.
- `PARCIAL`: apenas parte positiva do valor solicitado considerado em BRL é reembolsável.
- `RECUSADA`: nenhum valor da despesa é reembolsável.

Toda despesa com status `PARCIAL` ou `RECUSADA` deve possuir ao menos um motivo que explique a decisão.

Para cada despesa positiva considerada no cálculo:

```text
valor_solicitado =
valor_reembolsavel + valor_nao_reembolsavel
```

Para o resultado completo:

```text
resumo.total_solicitado =
resumo.total_reembolsavel + resumo.total_nao_reembolsavel
```

---

## 5. Regras de negócio

Cada regra possui um identificador único (`RN-NNN`) para permitir sua rastreabilidade até as ambiguidades, critérios de aceite, tarefas e testes correspondentes.

### RN-001 — Limite diário de alimentação

**Regra:** A soma dos valores reembolsáveis das despesas de alimentação de uma mesma data não pode ultrapassar o limite de `alimentacao` definido pela política aplicável ao centro de custo do colaborador.

Quando houver mais de uma despesa de alimentação na mesma data, todas compartilham o mesmo limite diário e o consomem conforme RN-014.

O valor de R$ 60,00 deixa de ser um limite universal e permanece aplicável apenas quando estiver definido na política selecionada, inclusive na política padrão.

**Origem:** Política v4 — limites parametrizados por centro de custo.

**Aceite:** Se a política aplicável definir limite diário de alimentação de R$ 90,00, duas despesas elegíveis de R$ 60,00 e R$ 50,00, nessa ordem e na mesma data, resultam respectivamente em R$ 60,00 e R$ 30,00 reembolsáveis.

---

### RN-002 — Limite diário de transporte urbano

**Regra:** A soma dos valores reembolsáveis das despesas de `transporte_urbano` de uma mesma data não pode ultrapassar o limite definido pela política aplicável ao centro de custo do colaborador.

Quando houver mais de uma despesa de transporte urbano na mesma data, todas compartilham o mesmo limite diário e o consomem conforme RN-014.

O valor de R$ 80,00 deixa de ser um limite universal e permanece aplicável apenas quando estiver definido na política selecionada.

**Origem:** Política v4 — limites parametrizados por centro de custo.

**Aceite:** Se a política aplicável definir limite diário de transporte urbano de R$ 150,00, duas despesas elegíveis de R$ 100,00, nessa ordem e na mesma data, resultam respectivamente em R$ 100,00 e R$ 50,00 reembolsáveis.

---

### RN-003 — Limite de hospedagem

**Regra:** Hospedagem possui por lançamento o limite definido para `hospedagem` na política aplicável ao centro de custo do colaborador.

Como a entrada não possui campo estruturado que informe a quantidade de diárias, cada lançamento de hospedagem continua sendo considerado uma única diária.

Informações presentes apenas na descrição da despesa não são utilizadas para determinar a quantidade de diárias.

Quando a categoria estiver presente na política com limite igual a R$ 0,00, ela continua contemplada, mas nenhum valor é reembolsável.

**Origem:** Política v4 — limite de hospedagem parametrizado por centro de custo.

**Aceite:** Se a política aplicável definir hospedagem em R$ 400,00, um lançamento elegível de R$ 480,00 resulta em R$ 400,00 reembolsáveis. Se o limite aplicável for R$ 0,00, o mesmo lançamento recebe R$ 0,00.

---

### RN-004 — Reembolso parcial acima do limite

**Regra:** Quando uma despesa elegível ultrapassar o limite disponível aplicável, o sistema deve reembolsar até o limite disponível e considerar somente o excedente positivo como não reembolsável.

Quando o limite disponível já estiver totalmente consumido ou for igual a R$ 0,00, nenhum valor é reembolsado e a despesa recebe motivo correspondente ao limite aplicável.

**Origem:** Política do RH, item 4, mantido pela Política v4.

**Aceite:** Uma despesa elegível de R$ 120,00, quando houver R$ 90,00 disponíveis no limite aplicável, resulta em R$ 90,00 reembolsáveis, R$ 30,00 não reembolsáveis e status `PARCIAL`.

---

### RN-005 — Obrigatoriedade de nota fiscal

**Regra:** A verificação da obrigatoriedade de nota fiscal utiliza o valor da despesa já convertido e normalizado em BRL conforme RN-011 e RN-019.

Despesas cujo valor considerado em BRL seja estritamente superior a R$ 100,00 exigem nota fiscal.

Uma despesa de exatamente R$ 100,00 não exige nota fiscal por esta regra.

Quando uma despesa superior a R$ 100,00 em BRL não possuir nota fiscal, nenhum valor dessa despesa é reembolsável.

**Origem:** Política do RH, item 5, combinada com a exigência da Política v4 de conversão para BRL antes da aplicação dos limites monetários.

**Aceite:**

- Uma despesa cujo valor convertido seja R$ 100,00 sem nota fiscal pode prosseguir para avaliação pelas demais regras.
- Uma despesa cujo valor convertido seja R$ 100,01 sem nota fiscal recebe R$ 0,00 de reembolso.
- Uma despesa cujo valor convertido seja R$ 100,01 com nota fiscal pode prosseguir para avaliação pelas demais regras.

---

### RN-006 — Limites ampliados em viagem

**Regra:** A política continua prevendo ampliação de 50% dos limites para colaboradores em viagem.

A entrada não possui informação explícita que permita determinar se o colaborador está em viagem. Portanto, o sistema não aplica o acréscimo enquanto essa condição não estiver explicitamente disponível.

O sistema não deve inferir viagem a partir de descrição, fornecedor, existência de hospedagem, aeroporto, moeda estrangeira ou qualquer outra informação indireta.

**Origem:** Política v4 — parâmetro de acréscimo em viagem permanece em 50%.

**Aceite:** Uma despesa em moeda estrangeira ou cuja descrição mencione aeroporto ou hotel não recebe acréscimo de 50% sem informação explícita de viagem.

---

### RN-007 — Período de competência

**Regra:** Uma despesa somente pode ser reembolsada quando `despesas[].data` estiver entre `periodo.inicio` e `periodo.fim`, incluindo as duas datas.

Na ausência de um campo específico para data de lançamento, `despesas[].data` continua sendo a data utilizada para verificar a competência.

**Origem:** Política do RH, item 7, mantido pela Política v4.

**Aceite:**

- Uma despesa com data igual a `periodo.inicio` está dentro da competência.
- Uma despesa com data igual a `periodo.fim` está dentro da competência.
- Uma despesa anterior a `periodo.inicio` recebe R$ 0,00 de reembolso.
- Uma despesa posterior a `periodo.fim` recebe R$ 0,00 de reembolso.

---

### RN-008 — Tratamento de duplicatas

**Regra:** A verificação de duplicidade utiliza categoria, moeda e valor original já normalizados conforme RN-010, RN-011 e RN-018.

Dois lançamentos são considerados duplicados quando possuem simultaneamente:

- mesma data;
- mesma categoria normalizada;
- mesma descrição;
- mesmo fornecedor;
- mesma moeda original normalizada;
- mesmo valor original normalizado na moeda de origem;
- mesmo indicador de nota fiscal.

O campo `id` não participa da comparação.

O valor convertido para BRL não participa da identidade de duplicidade.

Quando forem encontradas duplicatas, a primeira ocorrência na ordem da entrada é avaliada normalmente e as ocorrências posteriores recebem R$ 0,00 de reembolso com motivo de duplicidade.

**Origem:** Política do RH, item 8, combinada com a introdução de múltiplas moedas na Política v4.

**Aceite:** Dois lançamentos que diferem somente pelo campo `id`, mas possuem a mesma moeda e o mesmo valor original normalizado, são considerados duplicados. Duas despesas com valores e moedas originais diferentes não se tornam duplicatas apenas porque resultam no mesmo valor convertido em BRL.

---

### RN-009 — Categorias reembolsáveis

**Regra:** Após a normalização definida em RN-010, são contempladas as categorias presentes na política aplicável ao centro de custo do colaborador.

A lista de categorias deixa de ser global e fixa.

Uma categoria ausente da política aplicável não é reembolsável.

Uma categoria presente com limite igual a R$ 0,00 continua sendo considerada contemplada, mas nenhum valor é reembolsável.

A categoria `representacao` é válida quando estiver presente na política aplicável.

**Origem:** Política v4 — categorias e limites variam por centro de custo.

**Aceite:** Uma despesa de `representacao` é avaliada normalmente quando a política aplicável possuir essa categoria. A mesma categoria recebe R$ 0,00 por categoria não contemplada quando estiver ausente da política selecionada.

---

### RN-010 — Normalização de categoria

**Regra:** Antes da identificação da categoria e da verificação de duplicidade, são removidos espaços existentes no início e no fim do valor e diferenças entre letras maiúsculas e minúsculas são ignoradas.

A normalização não cria aliases nem corrige nomes semanticamente diferentes.

**Origem:** Necessidade de identificar de forma inequívoca as categorias configuradas na política.

**Aceite:** `alimentacao`, `ALIMENTACAO` e ` alimentacao ` são reconhecidas como a mesma categoria.

---

### RN-011 — Normalização monetária

**Regra:** O valor original da despesa é normalizado para duas casas decimais na moeda de origem.

Quando houver conversão cambial, o resultado convertido para BRL também é normalizado para duas casas decimais antes da aplicação das regras monetárias.

Quando for necessário arredondamento, utiliza-se o centavo mais próximo. Quando o valor estiver exatamente no ponto médio entre dois centavos, o arredondamento ocorre para cima em magnitude.

Para despesas em moeda estrangeira, a sequência é:

```text
valor original
    ↓
normalização na moeda de origem
    ↓
conversão para BRL
    ↓
normalização para duas casas decimais em BRL
    ↓
regras monetárias
```

**Origem:** Regra monetária da baseline combinada com o suporte a moedas estrangeiras da Política v4.

**Aceite:**

- `33.333` é normalizado para `33.33`.
- `33.335` é normalizado para `33.34`.
- O resultado de uma conversão cambial com mais de duas casas decimais é novamente normalizado antes da aplicação da nota fiscal e dos limites.

---

### RN-012 — Valores não positivos

**Regra:** Lançamentos cujo valor considerado em BRL seja menor ou igual a R$ 0,00 não são reembolsáveis.

Esses lançamentos:

- recebem R$ 0,00 de reembolso;
- recebem status `RECUSADA`;
- não aumentam nem reduzem os limites disponíveis;
- não participam de `resumo.total_solicitado`;
- não participam de `resumo.total_nao_reembolsavel`;
- preservam valor e moeda originais para rastreabilidade.

**Origem:** Decisão da baseline mantida na Política v4.

**Aceite:** Um lançamento em BRL de R$ -45,00 apresenta valor reembolsável e não reembolsável iguais a `"0.00"` e não altera os totais ou limites das demais despesas.

---

### RN-013 — Consumo dos limites

**Regra:** Somente valores efetivamente reembolsados consomem os limites aplicáveis.

Não reduzem o limite disponível:

- despesas fora da competência;
- duplicatas;
- categorias não contempladas;
- ausência de nota fiscal quando obrigatória;
- valores não positivos;
- despesas cuja conversão cambial não possa ser realizada.

**Origem:** Interação entre as regras da política, ampliada pela introdução de câmbio na Política v4.

**Aceite:** Uma despesa que não possa ser convertida por ausência de cotação não consome limite. Uma despesa elegível posterior na mesma categoria e data continua tendo acesso ao limite que estaria disponível antes dela.

---

### RN-014 — Ordem de consumo do limite diário

**Regra:** Quando várias despesas elegíveis da mesma categoria compartilham um limite diário, o limite disponível é consumido seguindo a ordem em que as despesas aparecem na entrada.

O sistema não reordena despesas para maximizar o reembolso.

A conversão cambial não altera a posição original do lançamento.

**Origem:** Decisão da baseline mantida na Política v4.

**Aceite:** Se o limite aplicável for R$ 90,00 e existirem despesas elegíveis de R$ 60,00 e R$ 50,00, nessa ordem, a primeira recebe R$ 60,00 e a segunda R$ 30,00.

---

### RN-015 — Consistência do resultado

**Regra:** Para cada despesa cujo valor considerado em BRL seja positivo:

`valor_solicitado = valor_reembolsavel + valor_nao_reembolsavel`.

Para despesas com valor considerado em BRL menor ou igual a zero, aplica-se RN-012.

Os totais do resumo são sempre expressos em BRL e calculados a partir das decisões individuais:

- `resumo.total_solicitado` corresponde à soma dos `valor_solicitado` positivos em BRL;
- `resumo.total_reembolsavel` corresponde à soma de todos os `valor_reembolsavel`;
- `resumo.total_nao_reembolsavel` corresponde à soma dos `valor_nao_reembolsavel` das despesas com valor solicitado positivo.

**Origem:** Requisito de rastreabilidade do resultado, ampliado para múltiplas moedas.

**Aceite:** Para qualquer resultado, `resumo.total_reembolsavel + resumo.total_nao_reembolsavel` é igual a `resumo.total_solicitado`.

---

### RN-016 — Seleção da política por centro de custo

**Regra:** A política aplicável é determinada por `colaborador.centro_custo`.

Quando existir configuração específica para o centro de custo informado, ela é utilizada.

Quando não existir configuração específica, aplica-se integralmente a política `padrao`.

Não são utilizadas correspondências parciais, prefixos ou similaridade textual para procurar outra política.

**Origem:** Política v4 — limites externos por centro de custo.

**Aceite:** Um colaborador de `CC-SUPORTE-N2`, quando esse centro de custo não possuir configuração específica, utiliza a política `padrao`.

---

### RN-017 — Política externa como fonte dos limites

**Regra:** Limites e categorias são obtidos dos dados da Política v4 fornecidos ao cálculo.

Os valores R$ 60,00, R$ 80,00 e R$ 250,00 da baseline v3 não são utilizados como constantes universais.

Quando esses valores forem aplicáveis, isso ocorre porque estão definidos na política selecionada.

**Origem:** Política v4 — externalização dos limites.

**Aceite:** Alterar um limite na política fornecida altera o limite aplicado pelo cálculo sem exigir mudança na regra de negócio correspondente.

---

### RN-018 — Moeda padrão e normalização da moeda

**Regra:** Quando `despesas[].moeda` estiver ausente, a moeda da despesa é considerada `BRL`.

Quando estiver presente, são removidos espaços no início e no fim e o código é convertido para letras maiúsculas.

A moeda não é inferida a partir de descrição ou fornecedor.

**Origem:** Política v4 — `moeda` opcional e ausência equivalente a BRL.

**Aceite:** Ausência de `moeda`, `brl`, `BRL` e ` BRL ` resultam na moeda normalizada `BRL`.

---

### RN-019 — Conversão para BRL

**Regra:** Uma despesa cuja moeda seja diferente de `BRL` deve ser convertida para BRL antes da aplicação das regras monetárias.

A conversão utiliza o valor original normalizado e a taxa aplicável à moeda e à data da despesa.

Conceitualmente:

```text
valor em BRL =
valor original normalizado × taxa para BRL
```

O resultado é normalizado para duas casas decimais conforme RN-011.

O valor convertido é utilizado para:

- obrigatoriedade de nota fiscal;
- limites;
- cálculo do reembolso;
- totais.

**Origem:** Política v4 — suporte obrigatório a moedas estrangeiras.

**Aceite:** Uma despesa em moeda estrangeira com cotação disponível é convertida para BRL antes da avaliação do limite de sua categoria.

---

### RN-020 — Cotação ausente na data da despesa

**Regra:** Quando não existir cotação exatamente na data de uma despesa em moeda estrangeira, utiliza-se a cotação disponível mais recente anterior à data da despesa para a mesma moeda.

Cotações posteriores à data da despesa não são utilizadas.

**Origem:** Os dados de câmbio da Política v4 possuem cotações apenas em determinadas datas, incluindo ausência em dias sem cotação publicada.

**Aceite:** Para uma despesa realizada em um sábado sem cotação própria, havendo cotação na sexta-feira anterior e na segunda-feira posterior, utiliza-se a cotação da sexta-feira.

---

### RN-021 — Moeda sem cotação disponível

**Regra:** Quando não existir nenhuma cotação para a moeda da despesa na data correspondente nem em data anterior, a conversão não pode ser realizada.

Nesse caso:

- o status é `RECUSADA`;
- `valor_reembolsavel` é `"0.00"`;
- nenhum limite é consumido;
- o motivo é `COTACAO_NAO_DISPONIVEL`;
- valor e moeda originais são preservados.

Não são utilizadas taxas de outra moeda, taxa igual a 1, estimativas, cotações futuras ou consultas externas.

**Origem:** Necessidade de definir comportamento determinístico para moedas presentes na entrada sem cotação disponível.

**Aceite:** Uma despesa em `GBP` sem qualquer cotação disponível para GBP recebe status `RECUSADA` e motivo `COTACAO_NAO_DISPONIVEL`.

---

### RN-022 — Limite igual a zero

**Regra:** Uma categoria presente na política com limite de R$ 0,00 continua sendo considerada contemplada, mas nenhum valor dessa categoria é reembolsável.

A recusa ocorre pelo limite da categoria, e não por categoria fora da política.

**Origem:** Política v4 contém configuração em que uma categoria pode possuir limite zero.

**Aceite:** Se `hospedagem` estiver configurada com limite R$ 0,00, uma despesa de hospedagem recebe R$ 0,00 de reembolso com motivo relacionado ao limite de hospedagem, e não `CATEGORIA_NAO_REEMBOLSAVEL`.

---

### RN-023 — Categoria `representacao`

**Regra:** `representacao` é uma categoria válida quando estiver presente na política aplicável ao centro de custo.

Quando configurada com limite diário, múltiplas despesas de `representacao` na mesma data compartilham esse limite e o consomem conforme RN-013 e RN-014.

Quando estiver ausente da política aplicável, a categoria não é reembolsável.

**Origem:** Política v4 — introdução da categoria `representacao` em políticas específicas.

**Aceite:** Quando a política aplicável definir limite diário de R$ 300,00 para `representacao`, duas despesas elegíveis de R$ 200,00 na mesma data recebem respectivamente R$ 200,00 e R$ 100,00.

---

### RN-024 — Ordem da conversão e das regras monetárias

**Regra:** Para despesas em moeda estrangeira, a conversão para BRL ocorre antes de:

1. verificar a obrigatoriedade de nota fiscal;
2. aplicar o limite da categoria;
3. calcular reembolso parcial;
4. consumir limite diário;
5. calcular os totais.

A identificação de duplicidade utiliza valor e moeda originais conforme RN-008.

**Origem:** Necessidade de definir uma única ordem determinística para conversão e aplicação da política.

**Aceite:** Uma despesa cujo valor original esteja abaixo de 100 unidades da moeda estrangeira, mas cuja conversão resulte em valor superior a R$ 100,00, exige nota fiscal.

---

### RN-025 — Falha cambial e precedência

**Regra:** Quando uma despesa exigir conversão cambial e não houver cotação utilizável, não são aplicadas as regras monetárias que dependem do valor em BRL.

Nesse caso:

- não se verifica a obrigatoriedade de nota fiscal com base em valor BRL;
- não se aplica o limite monetário da categoria;
- nenhum limite é consumido;
- a despesa é recusada por `COTACAO_NAO_DISPONIVEL`.

Regras que não dependem do valor convertido continuam sendo avaliadas conforme a ordem de precedência definida nesta especificação.

**Origem:** Interação entre conversão cambial e regras monetárias da Política v4.

**Aceite:** Uma despesa em moeda sem cotação utilizável é recusada por falha cambial sem consumir limite da categoria.

--- 
## 6. Ambiguidades identificadas e decisões

Esta seção registra as ambiguidades encontradas na política original de reembolso e nas mudanças introduzidas pela Política v4, definindo explicitamente a interpretação adotada pelo sistema.

Cada decisão desta seção está associada a uma ou mais regras de negócio da seção 5.

As ambiguidades `AMB-001` a `AMB-017` foram identificadas na construção da baseline v3. Quando a Política v4 alterou o contexto de alguma delas, sua decisão foi atualizada mantendo o mesmo identificador para preservar a rastreabilidade histórica.

As ambiguidades a partir de `AMB-018` surgiram com a Política v4.

### AMB-001 — O limite diário de alimentação é por despesa ou pela soma do dia?

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia."

**O que não está claro:** A política original não informava se cada despesa de alimentação poderia receber individualmente até o limite ou se todas as despesas da mesma data compartilhariam o valor disponível.

A Política v4 torna o valor do limite parametrizável, mas não altera essa ambiguidade sobre sua forma de consumo.

**Decisão:** O limite de alimentação definido pela política aplicável é compartilhado por todas as despesas elegíveis de alimentação da mesma data.

**Justificativa:** A expressão "por dia" indica um limite diário total, e não um limite individual por lançamento. Essa interpretação também evita que o limite seja contornado pela divisão de uma despesa em vários lançamentos.

**Regra afetada:** RN-001.

---

### AMB-002 — O limite diário de transporte urbano é por despesa ou pela soma do dia?

**Texto original do RH:** "Transporte urbano tem limite de R$ 80 por dia."

**O que não está claro:** A política original não informava se cada corrida ou lançamento possuía individualmente o limite ou se todas as despesas de transporte urbano do mesmo dia compartilhariam o valor disponível.

A Política v4 torna o valor do limite parametrizável, mas mantém a definição de limite diário.

**Decisão:** O limite de `transporte_urbano` definido pela política aplicável é compartilhado pelas despesas elegíveis da categoria na mesma data.

**Justificativa:** A política utiliza a expressão "por dia", portanto o limite é interpretado como diário e compartilhado entre os lançamentos daquela categoria.

**Regra afetada:** RN-002.

---

### AMB-003 — Como determinar a quantidade de diárias de hospedagem?

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."

**O que não está claro:** A política estabelece um limite por diária, mas a entrada não possui um campo estruturado que informe quantas diárias estão associadas a uma despesa de hospedagem. Essa informação pode aparecer apenas na descrição em texto livre.

**Decisão:** Cada lançamento de hospedagem é considerado uma única diária. Informações presentes apenas na descrição não são utilizadas para determinar a quantidade de diárias.

**Justificativa:** Interpretar texto livre para obter uma quantidade que altera o valor do reembolso introduziria uma regra não confiável e não prevista no formato de entrada.

**Regra afetada:** RN-003.

---

### AMB-004 — O que significa reembolsar parcialmente uma despesa acima do limite?

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."

**O que não está claro:** A política não esclarece se uma despesa que ultrapassa o limite deve ser recusada integralmente ou se deve ser reembolsada até o limite disponível.

Também não esclarece explicitamente o comportamento quando o limite disponível já é R$ 0,00.

**Decisão:** A despesa é reembolsada até o limite disponível e somente o valor excedente positivo deixa de ser reembolsado. Quando o limite disponível for R$ 0,00, nenhum valor é reembolsado e a decisão é justificada pelo limite aplicável.

**Justificativa:** Essa interpretação corresponde ao uso da palavra "parcialmente" e mantém o mesmo princípio quando o limite já estiver totalmente consumido.

**Regra afetada:** RN-004 e RN-022.

---

### AMB-005 — Uma despesa de exatamente R$ 100,00 exige nota fiscal?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."

**O que não está claro:** A política não exemplifica o comportamento no valor exato de R$ 100,00, o que pode gerar interpretações diferentes entre "acima de R$ 100,00" e "a partir de R$ 100,00".

**Decisão:** Uma despesa de exatamente R$ 100,00 não exige nota fiscal por essa regra. A obrigatoriedade começa em valores estritamente superiores a R$ 100,00.

**Justificativa:** A expressão "acima de" representa uma comparação estrita e não inclui o próprio valor de R$ 100,00.

**Regra afetada:** RN-005.

---

### AMB-006 — O que acontece com uma despesa acima de R$ 100,00 sem nota fiscal?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."

**O que não está claro:** A política não informa se uma despesa acima do limite documental sem nota deve ser totalmente recusada ou se uma parcela poderia ser reembolsada.

**Decisão:** Quando a nota fiscal for obrigatória e não estiver presente, toda a despesa recebe R$ 0,00 de reembolso.

**Justificativa:** R$ 100,00 define quando a documentação passa a ser obrigatória; não representa uma parcela que possa ser reembolsada sem documento.

**Regra afetada:** RN-005.

---

### AMB-007 — A obrigatoriedade da nota é verificada antes ou depois da normalização e da conversão?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."

**O que não está claro:** Na baseline, a dúvida era se a comparação ocorreria antes ou depois do arredondamento. Com a Política v4, uma despesa também pode estar originalmente em moeda estrangeira.

Não estava definido se os R$ 100,00 deveriam ser comparados com:

- o valor original na moeda estrangeira;
- o valor convertido ainda não arredondado;
- o valor convertido e normalizado em BRL.

**Decisão:** A comparação utiliza o valor convertido e normalizado em BRL.

Para despesas em BRL, utiliza-se o valor normalizado em BRL.

Para despesas estrangeiras, a ordem é:

```text
normalização do valor original
    ↓
conversão para BRL
    ↓
normalização para centavos de BRL
    ↓
verificação dos R$ 100,00
```

**Justificativa:** O limite documental é expresso em reais e todas as regras monetárias devem avaliar uma representação comum e determinística.

**Regra afetada:** RN-005, RN-011, RN-019 e RN-024.

---

### AMB-008 — Como determinar se o colaborador está em viagem?

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."

**O que não está claro:** A entrada não possui um campo que indique explicitamente se o colaborador está em viagem.

Com a Política v4, a existência de moeda estrangeira poderia criar uma nova tentativa de inferir viagem.

**Decisão:** O sistema não infere que o colaborador está em viagem.

Não são evidências suficientes:

- descrição;
- fornecedor;
- hospedagem;
- aeroporto;
- moeda estrangeira;
- qualquer outra informação indireta.

Enquanto a entrada não fornecer essa informação explicitamente, não é aplicado o acréscimo de 50%.

**Justificativa:** Inferir viagem criaria uma condição de negócio que não foi definida de forma estruturada na entrada.

**Regra afetada:** RN-006.

---

### AMB-009 — As datas inicial e final pertencem ao período de competência?

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."

**O que não está claro:** A política não informa explicitamente se despesas ocorridas exatamente nas datas de início e fim devem ser consideradas dentro do período.

**Decisão:** As datas `periodo.inicio` e `periodo.fim` são inclusivas.

**Justificativa:** As duas datas representam os limites do próprio período e, na ausência de indicação contrária, são consideradas parte dele.

**Regra afetada:** RN-007.

---

### AMB-010 — Qual data deve ser usada para verificar a competência?

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."

**O que não está claro:** A política utiliza o termo "lançadas", mas a entrada fornece apenas `despesas[].data`. Não existe um campo separado para a data em que a despesa foi efetivamente lançada no sistema.

**Decisão:** O campo `despesas[].data` é utilizado para verificar se a despesa pertence ao período de competência.

**Justificativa:** É a única informação temporal disponível por despesa. Não é possível verificar uma data de lançamento que não existe na entrada.

**Regra afetada:** RN-007.

---

### AMB-011 — O que caracteriza uma duplicata?

**Texto original do RH:** "Duplicatas devem ser tratadas."

**O que não está claro:** A política não define quais atributos devem ser comparados para determinar se dois lançamentos representam a mesma despesa.

A Política v4 acrescenta uma nova dúvida: se o valor utilizado na comparação deve ser o valor original ou o valor convertido para BRL.

**Decisão:** Dois lançamentos são considerados duplicados quando possuem:

- mesma data;
- mesma categoria normalizada;
- mesma descrição;
- mesmo fornecedor;
- mesma moeda original normalizada;
- mesmo valor original normalizado na moeda de origem;
- mesmo indicador de nota fiscal.

O `id` e o valor convertido para BRL não participam da comparação.

**Justificativa:** A identidade deve representar o lançamento originalmente recebido. Utilizar o valor convertido poderia fazer despesas originalmente distintas coincidirem após conversão e arredondamento.

**Regra afetada:** RN-008, RN-010, RN-011 e RN-018.

---

### AMB-012 — O que fazer quando uma duplicata é encontrada?

**Texto original do RH:** "Duplicatas devem ser tratadas."

**O que não está claro:** A política não informa se todas as ocorrências devem ser recusadas, agrupadas ou se uma delas deve ser considerada válida.

**Decisão:** A primeira ocorrência, considerando a ordem da entrada, é avaliada normalmente. As ocorrências posteriores identificadas como duplicadas recebem R$ 0,00 de reembolso.

**Justificativa:** Essa decisão evita reembolso repetido sem descartar automaticamente o primeiro lançamento potencialmente legítimo.

**Regra afetada:** RN-008.

---

### AMB-013 — A identificação da categoria diferencia letras maiúsculas e minúsculas?

**Texto original do RH:** "Categorias fora da política não são reembolsáveis."

**O que não está claro:** A política não informa se variações de escrita como `alimentacao` e `ALIMENTACAO` representam categorias diferentes.

**Decisão:** A identificação da categoria ignora diferenças entre letras maiúsculas e minúsculas e espaços existentes antes ou depois do valor.

**Justificativa:** Diferenças de capitalização ou espaços externos não alteram o significado da categoria informada.

**Regra afetada:** RN-009 e RN-010.

---

### AMB-014 — Como tratar valores com mais de duas casas decimais?

**Texto original do RH:** A política apresenta limites monetários, mas não define o tratamento de frações inferiores à menor unidade da moeda.

**O que não está claro:** A entrada pode conter valores com mais de duas casas decimais. Com a Política v4, a conversão cambial também pode produzir valores em BRL com mais de duas casas.

**Decisão:** O valor original é normalizado para duas casas decimais na moeda de origem. Quando houver conversão, o resultado em BRL também é normalizado para duas casas antes das regras monetárias.

O arredondamento é feito para a unidade monetária de duas casas mais próxima e, no ponto médio, para cima em magnitude.

**Justificativa:** Todas as regras financeiras devem utilizar valores monetários determinísticos.

**Regra afetada:** RN-005, RN-008, RN-011, RN-019 e RN-024.

---

### AMB-015 — Como tratar despesas com valor zero ou negativo?

**Texto original do RH:** A política trata de reembolso de despesas, mas não estabelece uma regra para valores iguais ou inferiores a zero.

**O que não está claro:** Um valor negativo pode representar estorno, mas não está definido se deve reduzir o total solicitado, devolver limite ou participar de compensação.

**Decisão:** Valores cujo montante considerado em BRL seja menor ou igual a R$ 0,00 não são reembolsáveis, não participam dos totais solicitados e não reembolsáveis e não aumentam nem reduzem limites.

O valor e a moeda originais permanecem no resultado para rastreabilidade.

**Justificativa:** Na ausência de regra explícita de compensação ou estorno, permitir que valores não positivos alterem totais ou limites criaria comportamento financeiro não definido.

**Regra afetada:** RN-012 e RN-015.

---

### AMB-016 — Uma despesa recusada consome limite?

**Texto original do RH:** A política define limites e condições que podem tornar uma despesa não reembolsável, mas não determina como essas regras interagem.

**O que não está claro:** Uma despesa recusada poderia consumir limite antes de sua inelegibilidade ser determinada.

Na Política v4, isso também inclui despesas sem conversão cambial possível.

**Decisão:** Somente valores efetivamente reembolsados consomem limites.

**Justificativa:** Uma despesa que não gera reembolso não deve reduzir o valor disponível para outras despesas elegíveis.

**Regra afetada:** RN-013 e RN-025.

---

### AMB-017 — Como distribuir o limite diário entre várias despesas?

**Texto original do RH:** A política estabelece limites diários, mas não define como distribuir um limite insuficiente entre vários lançamentos.

**O que não está claro:** Quando várias despesas elegíveis concorrem pelo mesmo limite e a soma ultrapassa o teto, não está definido se o valor deve ser dividido proporcionalmente ou se alguma despesa possui prioridade.

**Decisão:** O limite é consumido seguindo a ordem em que as despesas aparecem na entrada.

**Justificativa:** A ordem da entrada fornece um critério determinístico sem criar prioridade adicional baseada em valor ou tipo da despesa.

**Regra afetada:** RN-001, RN-002, RN-013, RN-014 e RN-023.

---

## Ambiguidades introduzidas pela Política v4

### AMB-018 — Qual política utilizar quando o centro de custo não possui configuração específica?

**Texto recebido na Política v4:** Existem políticas específicas por centro de custo e uma política `padrao`.

**O que não está claro:** Poderia haver interpretação de que um centro desconhecido constitui erro ou de que deve ser procurada alguma política semelhante.

**Decisão:** Quando não existir configuração específica para `colaborador.centro_custo`, utiliza-se integralmente a política `padrao`.

**Justificativa:** A existência explícita de uma política padrão fornece um fallback determinístico e evita inferência baseada no nome do centro de custo.

**Regra afetada:** RN-016 e RN-017.

---

### AMB-019 — Os limites da v3 continuam valendo quando a política externa possui outros valores?

**Texto recebido na Política v4:** Os limites passam a ser definidos externamente e podem variar por centro de custo.

**O que não está claro:** Poderia ser interpretado que os limites da v3 continuam como valores-base e a política externa apenas os complementa.

**Decisão:** A política externa aplicável é a fonte dos limites. Os valores fixos da v3 deixam de ser universais.

**Justificativa:** Manter simultaneamente valores fixos e parametrizados criaria duas fontes de verdade para o mesmo limite.

**Regra afetada:** RN-001, RN-002, RN-003 e RN-017.

---

### AMB-020 — O que significa a ausência do campo `moeda`?

**Texto recebido na Política v4:** O campo `moeda` é opcional e sua ausência representa BRL.

**O que não está claro:** É necessário definir se outros campos podem alterar essa interpretação, como fornecedor estrangeiro ou descrição em outro idioma.

**Decisão:** A ausência de `despesas[].moeda` significa sempre `BRL`.

Nenhum outro campo é utilizado para inferir moeda.

**Justificativa:** O próprio contrato define o significado da ausência do campo, portanto inferências adicionais tornariam o comportamento imprevisível.

**Regra afetada:** RN-018.

---

### AMB-021 — Como normalizar o código da moeda?

**Texto recebido na Política v4:** A despesa pode possuir um código de moeda.

**O que não está claro:** Não está definido se `usd`, `USD` e ` USD ` devem ser tratados como moedas diferentes.

**Decisão:** Espaços externos são removidos e o código é convertido para letras maiúsculas.

**Justificativa:** Capitalização e espaços externos não alteram semanticamente o código da moeda.

**Regra afetada:** RN-018.

---

### AMB-022 — Qual cotação utilizar quando não existe taxa exatamente na data da despesa?

**Texto recebido na Política v4:** As taxas de câmbio são históricas e associadas a datas.

**O que não está claro:** Uma despesa pode ocorrer em data sem cotação, como fim de semana. Não está definido se deve ser utilizada cotação anterior, posterior ou se a despesa deve ser recusada.

**Decisão:** Utiliza-se a cotação disponível mais recente anterior à data da despesa para a mesma moeda.

Cotações posteriores não são utilizadas.

**Justificativa:** A última cotação anterior evita utilizar informação futura e fornece comportamento determinístico para dias sem cotação publicada.

**Regra afetada:** RN-019 e RN-020.

---

### AMB-023 — O que fazer quando a moeda não possui nenhuma cotação utilizável?

**Texto recebido na Política v4:** A entrada pode conter moeda que não aparece nos dados de câmbio fornecidos.

**O que não está claro:** Não está definido se o sistema deve estimar uma taxa, assumir paridade, buscar cotação externa ou recusar a despesa.

**Decisão:** A despesa é recusada com motivo `COTACAO_NAO_DISPONIVEL`.

Não são utilizadas estimativas, taxa igual a 1, moeda alternativa, cotação futura ou consulta externa.

**Justificativa:** Sem taxa fornecida não existe base confiável para produzir um valor em BRL, e inventar uma conversão alteraria financeiramente o reembolso.

**Regra afetada:** RN-021 e RN-025.

---

### AMB-024 — A nota fiscal é verificada sobre o valor original ou sobre o valor convertido?

**Texto recebido na Política v4:** A conversão deve ocorrer antes da aplicação dos limites.

**O que não está claro:** O limite documental de R$ 100,00 também é uma regra monetária, mas poderia ser interpretado separadamente dos limites de categoria.

**Decisão:** A obrigatoriedade de nota fiscal é verificada sobre o valor convertido e normalizado em BRL.

**Justificativa:** O limiar é expresso em reais e deve ser aplicado sobre uma base monetária comum.

**Regra afetada:** RN-005, RN-019 e RN-024.

---

### AMB-025 — A duplicidade utiliza o valor original ou o valor convertido?

**Texto recebido na Política v4:** Despesas estrangeiras são convertidas para BRL antes da aplicação das regras monetárias.

**O que não está claro:** Não está definido se a conversão deve alterar também a identidade utilizada para detectar duplicatas.

**Decisão:** A duplicidade utiliza moeda original normalizada e valor original normalizado antes da conversão.

**Justificativa:** A duplicidade procura identificar repetição do lançamento originalmente recebido. Conversão e arredondamento poderiam fazer despesas diferentes coincidirem artificialmente em BRL.

**Regra afetada:** RN-008, RN-011 e RN-018.

---

### AMB-026 — Categoria com limite zero está fora da política?

**Texto recebido na Política v4:** Uma política pode conter categoria com limite igual a R$ 0,00.

**O que não está claro:** Limite zero poderia ser interpretado como ausência da categoria ou como categoria válida sem valor disponível para reembolso.

**Decisão:** Categoria presente com limite zero está contemplada pela política, mas possui R$ 0,00 disponível para reembolso.

**Justificativa:** Presença e valor do limite são informações distintas. Tratar limite zero como categoria ausente eliminaria essa distinção da configuração recebida.

**Regra afetada:** RN-009 e RN-022.

---

### AMB-027 — Como tratar a nova categoria `representacao`?

**Texto recebido na Política v4:** `representacao` aparece nas configurações da nova política.

**O que não está claro:** A categoria poderia ser interpretada como globalmente reembolsável ou apenas válida nas políticas em que estiver explicitamente configurada.

**Decisão:** `representacao` é contemplada somente quando estiver presente na política aplicável ao centro de custo.

Quando possuir limite diário, esse limite é compartilhado pelas despesas da categoria na mesma data.

**Justificativa:** Na v4, a elegibilidade de categorias é determinada pela política aplicável, e não por uma lista global.

**Regra afetada:** RN-009 e RN-023.

---

### AMB-028 — Qual é a ordem entre conversão cambial e aplicação das demais regras?

**Texto recebido na Política v4:** A conversão deve ocorrer antes da aplicação dos limites.

**O que não está claro:** Nem todas as regras dependem de valor monetário. Não estava definido em que momento competência, duplicidade, nota fiscal e limites deveriam ser avaliados.

**Decisão:** Regras que não dependem do valor convertido podem ser avaliadas antes da conversão. Regras monetárias dependentes de BRL são avaliadas somente depois de uma conversão bem-sucedida.

A duplicidade utiliza os valores originais conforme AMB-025.

**Justificativa:** Evita conversões desnecessárias e garante que todas as decisões monetárias utilizem a mesma base em BRL.

**Regra afetada:** RN-008, RN-019, RN-024 e RN-025.

---

### AMB-029 — A moeda estrangeira indica que o colaborador está em viagem?

**Texto recebido na Política v4:** A entrada passa a aceitar despesas em moeda estrangeira, enquanto a política mantém o acréscimo de 50% para viagem.

**O que não está claro:** Poderia ser inferido que uma despesa em USD, EUR ou outra moeda comprova que o colaborador está em viagem.

**Decisão:** Moeda estrangeira não caracteriza viagem.

**Justificativa:** Uma despesa pode estar denominada em moeda estrangeira sem que a condição de viagem esteja comprovada. A entrada continua sem um indicador explícito dessa condição.

**Regra afetada:** RN-006 e RN-018.

---

### AMB-030 — A aprovação manual opcional faz parte desta entrega?

**Texto recebido na Política v4:** A aprovação manual é apresentada como funcionalidade opcional.

**O que não está claro:** Uma funcionalidade opcional poderia ser implementada nesta versão ou explicitamente deixada para evolução futura.

**Decisão:** A aprovação manual não faz parte desta entrega.

**Justificativa:** O requisito é opcional e não é necessário para atender às regras obrigatórias da Política v4. Incluí-lo aumentaria o escopo sem necessidade.

**Regra afetada:** Nenhuma regra de cálculo. A decisão está registrada também na seção 3 — Fora de escopo.

---

## 7. Casos de borda

Os casos abaixo definem comportamentos esperados para valores de fronteira, combinações de regras e situações presentes ou sugeridas pelos arquivos de entrada da Política v4.

Quando o comportamento esperado indicar que uma despesa "prossegue para as demais regras", isso significa que a regra em questão não impede o reembolso, mas outras regras ainda podem reduzir ou recusar o valor.

Os valores de limites utilizados nos exemplos abaixo são valores hipotéticos quando não houver referência explícita a uma configuração concreta. O comportamento deve ser o mesmo para qualquer limite definido pela política aplicável.

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Alimentação abaixo do limite aplicável | Política define alimentação em R$ 90,00; despesa de R$ 89,99 | R$ 89,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-001 |
| Alimentação exatamente no limite aplicável | Política define alimentação em R$ 90,00; despesa de R$ 90,00 | R$ 90,00 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-001 |
| Alimentação um centavo acima do limite aplicável | Política define alimentação em R$ 90,00; despesa de R$ 90,01 | R$ 90,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-001, RN-004 |
| Duas despesas de alimentação no mesmo dia | Limite aplicável de R$ 90,00; alimentação de R$ 60,00 seguida de R$ 50,00 | Primeira recebe R$ 60,00; segunda recebe R$ 30,00; total reembolsado no dia é R$ 90,00 | RN-001, RN-014 |
| Limite de alimentação totalmente consumido | Limite aplicável de R$ 90,00 já consumido; nova alimentação de R$ 30,00 | R$ 0,00 reembolsáveis, status `RECUSADA` e motivo de limite diário | RN-001, RN-004 |
| Limite de alimentação reinicia em nova data | Limite aplicável de R$ 90,00 consumido em uma data e nova despesa no dia seguinte | O consumo do primeiro dia não reduz o limite disponível no segundo | RN-001 |
| Transporte abaixo do limite aplicável | Limite de transporte de R$ 150,00; despesa de R$ 149,99 | R$ 149,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-002 |
| Transporte exatamente no limite aplicável | Limite de transporte de R$ 150,00; despesa de R$ 150,00 com documentação exigida satisfeita | R$ 150,00 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-002, RN-005 |
| Transporte um centavo acima do limite aplicável | Limite de R$ 150,00; despesa de R$ 150,01 com documentação exigida satisfeita | R$ 150,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-002, RN-004, RN-005 |
| Duas despesas de transporte no mesmo dia | Limite de R$ 150,00; transporte de R$ 100,00 seguido de R$ 100,00 | Primeira recebe R$ 100,00; segunda recebe R$ 50,00 | RN-002, RN-014 |
| Limite de transporte reinicia em nova data | Limite consumido integralmente em uma data e nova despesa no dia seguinte | O consumo do primeiro dia não afeta o segundo | RN-002 |
| Hospedagem abaixo do limite aplicável | Limite de hospedagem de R$ 400,00; despesa de R$ 399,99 com nota | R$ 399,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-003, RN-005 |
| Hospedagem exatamente no limite aplicável | Limite de hospedagem de R$ 400,00; despesa de R$ 400,00 com nota | R$ 400,00 reembolsáveis | RN-003, RN-005 |
| Hospedagem um centavo acima do limite aplicável | Limite de R$ 400,00; hospedagem de R$ 400,01 com nota | R$ 400,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-003, RN-004, RN-005 |
| Quantidade de diárias somente na descrição | Hospedagem acima do limite com descrição `"Hotel - 2 diarias"` | A descrição não é interpretada; o lançamento representa uma diária e utiliza apenas um limite de hospedagem | RN-003 |
| Hospedagem com limite zero | Política aplicável contém `hospedagem` com limite R$ 0,00 | A categoria é reconhecida, mas a despesa recebe R$ 0,00, status `RECUSADA` e motivo de limite de hospedagem | RN-003, RN-009, RN-022 |
| Categoria ausente versus limite zero | `hospedagem` ausente da política em um caso e presente com R$ 0,00 em outro | No primeiro caso, motivo de categoria não contemplada; no segundo, motivo relacionado ao limite | RN-009, RN-022 |
| Valor abaixo do limite documental sem nota | Valor considerado em BRL igual a R$ 99,99 e `tem_nota_fiscal = false` | A ausência de nota não impede o reembolso por RN-005 | RN-005 |
| Valor exatamente no limite documental sem nota | Valor considerado em BRL igual a R$ 100,00 e `tem_nota_fiscal = false` | A ausência de nota não impede o reembolso por RN-005 | RN-005 |
| Valor um centavo acima do limite documental sem nota | Valor considerado em BRL igual a R$ 100,01 e `tem_nota_fiscal = false` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-005 |
| Valor um centavo acima do limite documental com nota | Valor considerado em BRL igual a R$ 100,01 e `tem_nota_fiscal = true` | A regra documental é satisfeita e a despesa prossegue | RN-005 |
| Valor arredondado para exatamente R$ 100,00 | Conversão ou valor em BRL resulta em R$ 100,004 sem nota | Normalizado para R$ 100,00; nota não é obrigatória por RN-005 | RN-005, RN-011 |
| Valor arredondado para R$ 100,01 | Conversão ou valor em BRL resulta em R$ 100,005 sem nota | Normalizado para R$ 100,01; despesa é recusada pela ausência da nota | RN-005, RN-011 |
| Primeiro dia da competência | `despesas[].data` igual a `periodo.inicio` | A despesa está dentro da competência e prossegue | RN-007 |
| Último dia da competência | `despesas[].data` igual a `periodo.fim` | A despesa está dentro da competência e prossegue | RN-007 |
| Dia anterior à competência | Data um dia antes de `periodo.inicio` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-007 |
| Dia posterior à competência | Data um dia depois de `periodo.fim` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-007 |
| Despesa antiga descrita como lançamento atrasado | Data fora da competência, mas descrição informa lançamento posterior | A descrição não altera a competência; utiliza-se `despesas[].data` | RN-007 |
| Duplicata com identificadores diferentes | Mesmos campos da identidade de duplicidade, mas IDs diferentes | Primeiro lançamento é avaliado; segundo é recusado como duplicata | RN-008 |
| Duplicata com diferença apenas na capitalização da categoria | `alimentacao` e `ALIMENTACAO`, demais campos iguais | Após normalização, os registros podem ser duplicados | RN-008, RN-010 |
| Duplicata com diferença apenas na capitalização da moeda | `usd` e `USD`, demais campos iguais | Após normalização da moeda, os registros podem ser duplicados | RN-008, RN-018 |
| Mesmo valor original, moedas diferentes | Um lançamento de 100 USD e outro de 100 EUR | Não são duplicatas, mesmo que os demais campos coincidam | RN-008, RN-018 |
| Valores originais diferentes que convertem para o mesmo BRL | Duas despesas distintas cujo valor convertido e arredondado coincide | Não são duplicatas apenas por coincidirem em BRL | RN-008, RN-019 |
| Valores originais que normalizam para o mesmo centavo | Mesma moeda e demais campos iguais; valores originais normalizam para o mesmo valor | Os registros são considerados duplicados | RN-008, RN-011 |
| Categoria ausente da política aplicável | Categoria `coworking` não está presente na política selecionada | R$ 0,00 reembolsáveis, status `RECUSADA` e motivo de categoria não contemplada | RN-009 |
| Categoria em letras maiúsculas | Categoria `ALIMENTACAO` | É normalizada e consultada na política como `alimentacao` | RN-009, RN-010 |
| Categoria com espaços externos | Categoria ` alimentacao ` | É normalizada para `alimentacao` | RN-009, RN-010 |
| Valor com três casas abaixo do ponto médio | Valor `33.333` | Valor original normalizado para `33.33` | RN-011 |
| Valor com três casas no ponto médio | Valor `33.335` | Valor original normalizado para `33.34` | RN-011 |
| Conversão produz mais de duas casas | Conversão resulta em `123.456...` BRL | O valor considerado em BRL é normalizado para `123.46` antes das regras monetárias | RN-011, RN-019 |
| Valor zero em BRL | Valor considerado em BRL igual a R$ 0,00 | Reembolso e não reembolso são `"0.00"`, status `RECUSADA`, sem impacto nos totais ou limites | RN-012, RN-015 |
| Valor negativo em BRL | Valor considerado em BRL igual a R$ -45,00 | Reembolso e não reembolso são `"0.00"`, status `RECUSADA`, sem impacto nos totais ou limites | RN-012, RN-015 |
| Despesa sem nota não consome limite | Despesa acima de R$ 100,00 em BRL sem nota seguida de despesa elegível da mesma categoria/data | Primeira recebe R$ 0,00 e não consome limite; segunda utiliza o limite normalmente | RN-005, RN-013 |
| Categoria não contemplada não consome limite | Categoria ausente da política seguida de despesa válida | A primeira recebe R$ 0,00 e não reduz limite da segunda | RN-009, RN-013 |
| Duplicata não consome limite novamente | Lançamento válido, sua duplicata e outro lançamento válido no mesmo limite diário | A duplicata recebe R$ 0,00 e não reduz novamente o limite | RN-008, RN-013 |
| Falha cambial não consome limite | Despesa estrangeira sem cotação seguida de despesa elegível da mesma categoria/data | Primeira é recusada sem consumir limite; segunda continua com o limite disponível | RN-013, RN-021, RN-025 |
| Ordem dos lançamentos altera distribuição | Limite diário de R$ 90,00; despesas de R$ 60,00 e R$ 50,00 | Reembolsos são R$ 60,00 e R$ 30,00 | RN-014 |
| Ordem inversa altera distribuição | Limite diário de R$ 90,00; despesas de R$ 50,00 e R$ 60,00 | Reembolsos são R$ 50,00 e R$ 40,00; teto diário continua R$ 90,00 | RN-014 |
| Indício de viagem na descrição | Descrição contém `"aeroporto"` ou `"hotel"` | A condição de viagem não é inferida | RN-006 |
| Existência de hospedagem | Entrada possui despesa de `hospedagem` | Isso não caracteriza automaticamente viagem | RN-006 |
| Moeda estrangeira como indício de viagem | Despesa em USD ou EUR | A condição de viagem não é inferida pela moeda | RN-006, RN-018 |
| Centro de custo com política específica | `centro_custo` possui configuração própria | São utilizados os limites e categorias dessa configuração | RN-016, RN-017 |
| Centro de custo sem política específica | `centro_custo` não existe entre as configurações específicas | É utilizada integralmente a política `padrao` | RN-016 |
| Centro parecido com outro configurado | `CC-SUPORTE-N2` não existe, mas `CC-SUPORTE` existe | Não ocorre correspondência parcial; utiliza-se a política `padrao` | RN-016 |
| Alteração do limite externo | O mesmo cenário é executado com políticas que possuem limites diferentes | O resultado acompanha os valores da política aplicável sem depender dos antigos limites fixos da v3 | RN-017 |
| Campo moeda ausente | Despesa sem `moeda` | Moeda original considerada `BRL` | RN-018 |
| Moeda em minúsculas | `moeda = "usd"` | Moeda normalizada para `USD` | RN-018 |
| Moeda com espaços | `moeda = " USD "` | Moeda normalizada para `USD` | RN-018 |
| Despesa em BRL | `moeda = "BRL"` | Não ocorre conversão cambial | RN-018, RN-019 |
| Despesa estrangeira com cotação na mesma data | Moeda diferente de BRL e cotação disponível exatamente na data | Utiliza-se a cotação daquela data | RN-019 |
| Despesa em fim de semana | Não existe cotação na data, mas existe em data anterior | Utiliza-se a cotação disponível mais recente anterior | RN-020 |
| Cotação anterior e posterior disponíveis | Não existe cotação na data da despesa | Utiliza-se somente a anterior; a cotação futura não é considerada | RN-020 |
| Mais de uma cotação anterior | Existem várias cotações anteriores para a moeda | Utiliza-se a de data mais recente entre as anteriores | RN-020 |
| Moeda completamente ausente do câmbio | Despesa em `GBP` sem nenhuma taxa GBP disponível | R$ 0,00 reembolsáveis, status `RECUSADA` e motivo `COTACAO_NAO_DISPONIVEL` | RN-021 |
| Cotação existe somente no futuro | Primeira cotação disponível da moeda ocorre depois da despesa | A cotação futura não é utilizada; despesa é recusada por ausência de cotação utilizável | RN-020, RN-021 |
| Categoria presente com limite zero | Política contém a categoria com valor R$ 0,00 | Categoria é reconhecida, mas a despesa recebe R$ 0,00 pelo limite | RN-022 |
| Representação presente na política | Política aplicável contém `representacao` | Categoria é reconhecida e avaliada conforme seu limite | RN-023 |
| Representação ausente da política | Política aplicável não contém `representacao` | R$ 0,00 reembolsáveis por categoria não contemplada | RN-009, RN-023 |
| Duas representações no mesmo dia | Limite de representação R$ 300,00; despesas de R$ 200,00 e R$ 200,00 | Primeira recebe R$ 200,00 e segunda R$ 100,00 | RN-023, RN-014 |
| Conversão eleva valor acima de R$ 100,00 | Valor original menor que 100 unidades da moeda, mas conversão resulta em R$ 100,01 ou mais | Nota fiscal torna-se obrigatória | RN-005, RN-019, RN-024 |
| Conversão mantém valor em R$ 100,00 | Despesa estrangeira convertida e normalizada para R$ 100,00 sem nota | Nota não é obrigatória por RN-005 | RN-005, RN-024 |
| Falha cambial ocorre antes da nota fiscal | Despesa sem nota em moeda sem cotação utilizável | A recusa ocorre por `COTACAO_NAO_DISPONIVEL`; não se calcula o limiar documental em BRL | RN-021, RN-025 |
| Valor original preservado após conversão | Despesa de 20,00 USD com conversão para outro valor em BRL | Saída preserva `valor_original = "20.00"` e `moeda_original = "USD"` juntamente com o valor solicitado em BRL | RN-019 |
| Total solicitado com moedas diferentes | Despesas válidas em BRL e moedas estrangeiras convertidas | `resumo.total_solicitado` soma somente os valores positivos considerados em BRL | RN-015, RN-019 |
| Total solicitado com valor negativo | Valores considerados em BRL de R$ 50,00, R$ -20,00 e R$ 30,00 | O negativo não participa; total solicitado é R$ 80,00 | RN-012, RN-015 |
| Total não reembolsável | Valores positivos em BRL totalizam R$ 100,00 e R$ 60,00 são reembolsáveis | `resumo.total_nao_reembolsavel` é `"40.00"` | RN-015 |
| Consistência matemática do resumo | Resultado com `"100.00"` solicitado, `"60.00"` reembolsável e `"40.00"` não reembolsável | A soma dos dois últimos é igual ao total solicitado | RN-015 |
| Despesa totalmente aprovada | Valor positivo em BRL integralmente reembolsável | `valor_reembolsavel` é igual a `valor_solicitado`, não reembolsável é `"0.00"` e status é `APROVADA` | RN-015 |
| Despesa parcialmente aprovada | Apenas parte positiva em BRL pode ser reembolsada | Reembolsável é maior que zero e menor que solicitado; status `PARCIAL` e existe motivo | RN-004, RN-015 |
| Despesa positiva totalmente recusada | Valor positivo em BRL falha em regra eliminatória | Reembolsável é `"0.00"`, não reembolsável é igual ao solicitado, status `RECUSADA` e existe motivo | RN-015 |

## 8. Ordem de aplicação das regras

A ordem de aplicação das regras é parte do comportamento do sistema, pois uma mesma despesa pode estar sujeita a mais de uma regra.

Na Política v4, a seleção da política por centro de custo e a conversão de moedas passam a fazer parte dessa ordem.

As regras são avaliadas na seguinte sequência.

### 1. Seleção da política aplicável

- `colaborador.centro_custo` é utilizado para selecionar a política conforme RN-016.
- Quando existir configuração específica para o centro de custo, ela é utilizada.
- Quando não existir configuração específica, utiliza-se a política `padrao`.
- Os limites fixos da baseline v3 não são utilizados como valores universais, conforme RN-017.

A política selecionada permanece a mesma durante o processamento de todas as despesas daquele conjunto de entrada.

### 2. Normalização da categoria

- A categoria é normalizada conforme RN-010.
- São removidos espaços externos e diferenças entre letras maiúsculas e minúsculas.
- A categoria normalizada é utilizada para consultar a política aplicável e para verificar duplicidade.

### 3. Normalização da moeda

- A moeda é determinada e normalizada conforme RN-018.
- Quando `despesas[].moeda` estiver ausente, considera-se `BRL`.
- Quando estiver presente, são removidos espaços externos e o código é convertido para letras maiúsculas.
- A moeda não é inferida a partir de descrição, fornecedor ou outros campos.

### 4. Normalização do valor original

- O valor original da despesa é normalizado para duas casas decimais conforme RN-011.
- Essa normalização ocorre na moeda original da despesa.
- O valor e a moeda originais normalizados são preservados para rastreabilidade e identificação de duplicidade.

### 5. Verificação da categoria

- A categoria normalizada é procurada na política selecionada, conforme RN-009.
- Categoria ausente da política aplicável recebe status `RECUSADA` e R$ 0,00 de reembolso.
- Uma categoria presente com limite R$ 0,00 não é considerada ausente; ela prossegue até a aplicação do limite conforme RN-022.
- A despesa recusada por categoria não contemplada não consome nenhum limite.

### 6. Verificação do período de competência

- `despesas[].data` é comparada com `periodo.inicio` e `periodo.fim`, conforme RN-007.
- As datas inicial e final são inclusivas.
- Despesas fora do período recebem status `RECUSADA` e R$ 0,00 de reembolso.
- A despesa recusada não consome nenhum limite.

### 7. Verificação de duplicidade

- A duplicidade é verificada conforme RN-008.
- São utilizados categoria normalizada, moeda original normalizada e valor original normalizado, além dos demais campos definidos na identidade de duplicidade.
- O valor convertido para BRL não participa da identificação.
- A primeira ocorrência é mantida para avaliação.
- Ocorrências posteriores recebem status `RECUSADA` e R$ 0,00 de reembolso.
- Uma duplicata recusada não consome limite.

### 8. Conversão para BRL

Quando a moeda original for `BRL`:

- não é realizada conversão;
- o valor normalizado em BRL passa a ser o valor considerado pelas regras monetárias.

Quando a moeda original for diferente de `BRL`:

- procura-se a cotação aplicável conforme RN-019 e RN-020;
- se existir cotação na data da despesa, ela é utilizada;
- se não existir, utiliza-se a cotação disponível mais recente anterior à data da despesa;
- cotações futuras não são utilizadas.

O resultado da conversão é normalizado para duas casas decimais em BRL conforme RN-011.

### 9. Tratamento de cotação indisponível

Quando uma despesa em moeda estrangeira não possuir cotação utilizável:

- a despesa recebe status `RECUSADA`;
- `valor_reembolsavel` é R$ 0,00;
- o motivo é `COTACAO_NAO_DISPONIVEL`;
- nenhum limite é consumido;
- não são aplicadas regras monetárias posteriores que dependam de valor em BRL.

Não são utilizadas:

- taxas de outras moedas;
- taxa igual a 1;
- estimativas;
- consultas externas;
- cotações posteriores à data da despesa.

Aplica-se RN-021 e RN-025.

### 10. Verificação de valor não positivo

- O valor considerado em BRL é verificado conforme RN-012.
- Valores menores ou iguais a R$ 0,00 recebem status `RECUSADA` e R$ 0,00 de reembolso.
- O lançamento não consome limites.
- O lançamento não participa de `resumo.total_solicitado` nem de `resumo.total_nao_reembolsavel`.
- Nenhuma regra monetária de limite precisa ser aplicada ao lançamento.

### 11. Verificação da obrigatoriedade de nota fiscal

- O valor convertido e normalizado em BRL é utilizado para verificar RN-005.
- Valores de até R$ 100,00 inclusive não exigem nota fiscal por essa regra.
- Valores estritamente superiores a R$ 100,00 exigem nota fiscal.
- Quando a nota for obrigatória e estiver ausente, a despesa recebe status `RECUSADA` e R$ 0,00 de reembolso.
- A despesa recusada não consome limite.

### 12. Determinação do limite aplicável

- O limite da categoria é obtido da política selecionada conforme RN-016 e RN-017.
- Alimentação utiliza o limite configurado para `alimentacao`.
- Transporte urbano utiliza o limite configurado para `transporte_urbano`.
- Hospedagem utiliza o limite configurado para `hospedagem`.
- `representacao`, quando presente, utiliza o limite configurado para essa categoria.
- Outras categorias configuradas seguem a periodicidade explicitamente definida pela política aplicável.
- Um limite igual a R$ 0,00 é tratado conforme RN-022.
- A condição de viagem não é inferida; o acréscimo de 50% não é aplicado sem informação explícita conforme RN-006.

### 13. Determinação do limite ainda disponível

Para categorias com limite diário:

- é considerado quanto do limite daquela categoria e data já foi consumido por despesas anteriores;
- somente valores efetivamente reembolsados anteriormente consomem o limite, conforme RN-013;
- a ordem original das despesas determina qual lançamento utiliza primeiro o limite disponível, conforme RN-014.

Para hospedagem, o limite é aplicado individualmente ao lançamento, conforme RN-003.

### 14. Cálculo do valor reembolsável

- Se o valor considerado em BRL estiver integralmente dentro do limite disponível, todo o valor é reembolsável.
- Se ultrapassar o limite disponível, somente a parcela dentro do limite é reembolsável, conforme RN-004.
- Se o limite disponível estiver totalmente consumido ou for R$ 0,00, o valor reembolsável é R$ 0,00.
- Uma recusa causada por limite deve possuir motivo correspondente ao limite da categoria.

### 15. Determinação do status e dos motivos

- `APROVADA`: todo o valor solicitado positivo considerado em BRL é reembolsável.
- `PARCIAL`: parte positiva do valor solicitado em BRL é reembolsável e parte não é.
- `RECUSADA`: nenhum valor da despesa é reembolsável.
- Toda despesa `PARCIAL` ou `RECUSADA` recebe ao menos um motivo que justifique a decisão.

Quando a despesa estiver em moeda estrangeira, valor e moeda originais permanecem disponíveis na saída independentemente do status.

### 16. Atualização do limite consumido

- Somente o valor efetivamente reembolsado é acrescentado ao consumo do limite correspondente.
- Valores não reembolsáveis nunca consomem limite.
- Uma despesa recusada não altera o limite disponível para despesas posteriores.
- A atualização ocorre somente depois da decisão sobre o valor efetivamente reembolsável da despesa atual.

### 17. Cálculo do resumo

Após a avaliação de todas as despesas, os totais são calculados conforme RN-015.

Todos os totais são expressos em BRL.

- `resumo.total_solicitado` corresponde à soma dos valores positivos considerados em BRL.
- `resumo.total_reembolsavel` corresponde à soma dos valores efetivamente reembolsáveis em BRL.
- `resumo.total_nao_reembolsavel` corresponde à soma das parcelas positivas em BRL que não serão reembolsadas.
- Valores considerados em BRL menores ou iguais a R$ 0,00 não participam de `total_solicitado` nem de `total_nao_reembolsavel`.

### Regras de precedência

Quando uma despesa puder ser recusada por mais de um motivo, a primeira regra eliminatória encontrada na ordem definida acima determina a recusa principal.

Isso significa, por exemplo:

- uma despesa de categoria não contemplada e também sem nota fiscal é recusada primeiro por categoria;
- uma despesa fora da competência e também sem nota fiscal é recusada primeiro por estar fora da competência;
- uma duplicata que também exigiria conversão cambial é recusada primeiro por duplicidade;
- uma despesa em moeda estrangeira sem cotação utilizável e também sem nota fiscal é recusada primeiro por `COTACAO_NAO_DISPONIVEL`;
- uma despesa com cotação válida, mas sem nota fiscal obrigatória, é recusada antes da aplicação do limite da categoria;
- uma categoria presente com limite R$ 0,00 não é recusada como categoria não contemplada; ela chega à etapa de limite e é recusada pelo limite aplicável.

Regras que recusam integralmente uma despesa são aplicadas antes do consumo dos limites.

Dessa forma, despesas que não podem gerar reembolso não consomem valores que poderiam ser utilizados por despesas elegíveis posteriores.

### Exemplo de precedência

Considere uma política que defina limite diário de alimentação de R$ 90,00 e, nesta ordem, duas despesas de alimentação na mesma data:

1. despesa cujo valor considerado em BRL é R$ 150,00, sem nota fiscal;
2. despesa de R$ 50,00 em BRL, com nota fiscal.

A primeira despesa é recusada pela ausência de nota fiscal obrigatória e recebe R$ 0,00 de reembolso.

Como valores recusados não consomem limite, os R$ 90,00 do limite diário continuam disponíveis.

A segunda despesa é elegível e recebe R$ 50,00 de reembolso.

O resultado é:

- primeira despesa: R$ 0,00 reembolsáveis;
- segunda despesa: R$ 50,00 reembolsáveis;
- limite diário consumido: R$ 50,00;
- limite diário restante: R$ 40,00.

### Exemplo de precedência com câmbio

Considere uma despesa de alimentação em moeda estrangeira que:

- esteja dentro da competência;
- não seja duplicada;
- pertença a uma categoria contemplada;
- não possua nota fiscal;
- não possua nenhuma cotação utilizável para sua moeda.

A despesa é recusada por `COTACAO_NAO_DISPONIVEL`.

Como não existe valor confiável em BRL:

- a obrigatoriedade de nota fiscal baseada no limite de R$ 100,00 não é avaliada;
- o limite de alimentação não é consumido;
- nenhuma cotação futura ou estimada é utilizada.

## 9. Critérios de aceite

O sistema está pronto quando todos os critérios abaixo forem atendidos e puderem ser verificados sem a necessidade de consultar a implementação.

### Entrada e saída

- [ ] O sistema aceita uma entrada válida no formato definido na seção 4.
- [ ] O sistema produz exatamente uma decisão para cada despesa recebida na entrada.
- [ ] Cada decisão permite identificar a despesa original por meio de seu `id`.
- [ ] Todos os valores monetários da saída são apresentados como texto decimal com exatamente duas casas decimais.
- [ ] Cada despesa apresenta `valor_original`, `moeda_original`, `valor_solicitado`, `valor_reembolsavel`, `valor_nao_reembolsavel`, `status` e `motivos`.
- [ ] `valor_original` preserva o valor normalizado na moeda de origem.
- [ ] `moeda_original` preserva a moeda informada ou assumida para a despesa.
- [ ] `valor_solicitado`, `valor_reembolsavel` e `valor_nao_reembolsavel` são expressos em BRL.
- [ ] Os únicos status possíveis são `APROVADA`, `PARCIAL` e `RECUSADA`.
- [ ] Toda despesa com status `PARCIAL` ou `RECUSADA` apresenta ao menos um motivo para a decisão.
- [ ] O `schema_version` da saída da Política v4 é `"2.0"`.

### Seleção da política

- [ ] O sistema utiliza `colaborador.centro_custo` para determinar a política aplicável.
- [ ] Quando existir configuração específica para o centro de custo, essa configuração é utilizada.
- [ ] Quando não existir configuração específica, é utilizada a política `padrao`.
- [ ] Não ocorre correspondência parcial ou por similaridade entre centros de custo.
- [ ] Os limites fixos da baseline v3 não são tratados como valores universais.
- [ ] Alterar um limite na política fornecida altera o comportamento do cálculo sem exigir alteração da regra correspondente.

### Alimentação

- [ ] O total reembolsável de alimentação em uma mesma data nunca ultrapassa o limite definido pela política aplicável.
- [ ] Despesas de alimentação em datas diferentes possuem limites independentes.
- [ ] Quando várias despesas de alimentação compartilham o mesmo limite diário, o limite é consumido na ordem em que aparecem na entrada.
- [ ] Uma despesa de alimentação que ultrapassa o limite disponível pode ser parcialmente reembolsada até o valor restante do limite.
- [ ] Quando o limite diário já estiver totalmente consumido, uma nova despesa de alimentação recebe R$ 0,00 e motivo de limite diário.

### Transporte urbano

- [ ] O total reembolsável de transporte urbano em uma mesma data nunca ultrapassa o limite definido pela política aplicável.
- [ ] Despesas de transporte urbano em datas diferentes possuem limites independentes.
- [ ] Quando várias despesas de transporte urbano compartilham o mesmo limite diário, o limite é consumido na ordem em que aparecem na entrada.
- [ ] Uma despesa de transporte urbano que ultrapassa o limite disponível pode ser parcialmente reembolsada até o valor restante do limite.
- [ ] Quando o limite diário já estiver totalmente consumido, uma nova despesa recebe R$ 0,00 e motivo correspondente ao limite.

### Hospedagem

- [ ] Cada lançamento elegível de hospedagem utiliza o limite definido pela política aplicável.
- [ ] Uma hospedagem elegível acima do limite aplicável é parcialmente reembolsada até esse limite.
- [ ] Informações sobre quantidade de diárias presentes somente na descrição da despesa não alteram o limite aplicado.
- [ ] A existência de uma despesa de hospedagem não faz o sistema inferir automaticamente que o colaborador está em viagem.
- [ ] Uma categoria `hospedagem` presente com limite R$ 0,00 continua sendo reconhecida como contemplada.
- [ ] Hospedagem com limite R$ 0,00 recebe R$ 0,00 de reembolso por limite, e não por categoria não contemplada.

### Nota fiscal

- [ ] Uma despesa cujo valor considerado em BRL seja exatamente R$ 100,00 não é recusada apenas por ausência de nota fiscal.
- [ ] Uma despesa cujo valor considerado em BRL seja R$ 100,01 sem nota fiscal recebe R$ 0,00 de reembolso.
- [ ] Uma despesa superior a R$ 100,00 em BRL com nota fiscal pode prosseguir para avaliação pelas demais regras.
- [ ] Quando a nota fiscal é obrigatória e está ausente, toda a despesa é não reembolsável.
- [ ] Para despesas em BRL, a verificação utiliza o valor normalizado.
- [ ] Para despesas estrangeiras, a verificação utiliza o valor convertido e normalizado em BRL.
- [ ] Uma despesa cujo valor original seja inferior a 100 unidades da moeda estrangeira pode exigir nota caso sua conversão resulte em valor superior a R$ 100,00.

### Viagem

- [ ] O sistema não infere a condição de viagem a partir da descrição da despesa.
- [ ] O sistema não infere a condição de viagem a partir do fornecedor.
- [ ] O sistema não infere a condição de viagem pela existência de hospedagem.
- [ ] O sistema não infere a condição de viagem pela existência de despesas relacionadas a aeroporto.
- [ ] O sistema não infere a condição de viagem pela existência de moeda estrangeira.
- [ ] Enquanto a entrada não fornecer informação explícita de viagem, o acréscimo de 50% não é aplicado.

### Período de competência

- [ ] Uma despesa cuja data seja igual a `periodo.inicio` é considerada dentro da competência.
- [ ] Uma despesa cuja data seja igual a `periodo.fim` é considerada dentro da competência.
- [ ] Uma despesa anterior a `periodo.inicio` recebe R$ 0,00 de reembolso.
- [ ] Uma despesa posterior a `periodo.fim` recebe R$ 0,00 de reembolso.
- [ ] A verificação de competência utiliza `despesas[].data`.
- [ ] Informações presentes somente na descrição não alteram a data utilizada para verificar a competência.

### Duplicidade

- [ ] Dois lançamentos que possuam os mesmos campos definidos em RN-008 são considerados duplicados mesmo quando possuem IDs diferentes.
- [ ] A primeira ocorrência de uma duplicata é avaliada normalmente.
- [ ] As ocorrências posteriores da mesma duplicata recebem R$ 0,00 de reembolso.
- [ ] Uma duplicata recusada não consome novamente o limite da categoria.
- [ ] Registros que diferem em pelo menos um dos campos utilizados na comparação de duplicidade não são considerados duplicados.
- [ ] A comparação utiliza categoria normalizada.
- [ ] A comparação utiliza moeda original normalizada.
- [ ] A comparação utiliza valor original normalizado na moeda de origem.
- [ ] O valor convertido para BRL não participa da identidade de duplicidade.
- [ ] Duas despesas originalmente diferentes não se tornam duplicatas apenas porque resultam no mesmo valor convertido em BRL.

### Categorias

- [ ] A lista de categorias contempladas é determinada pela política aplicável.
- [ ] Categorias ausentes da política aplicável recebem R$ 0,00 de reembolso.
- [ ] Categoria presente com limite R$ 0,00 é distinguida de categoria ausente.
- [ ] Diferenças entre letras maiúsculas e minúsculas não alteram a identificação da categoria.
- [ ] Espaços existentes no início ou no fim da categoria não alteram sua identificação.
- [ ] `alimentacao`, `ALIMENTACAO` e ` alimentacao ` são reconhecidas como a mesma categoria.
- [ ] `representacao` é reconhecida quando estiver presente na política aplicável.
- [ ] `representacao` é recusada como categoria não contemplada quando estiver ausente da política aplicável.

### Representação

- [ ] Quando `representacao` possuir limite diário, despesas da categoria na mesma data compartilham esse limite.
- [ ] O limite de `representacao` é consumido na ordem original da entrada.
- [ ] Uma despesa de `representacao` acima do limite disponível pode ser parcialmente reembolsada.
- [ ] Uma despesa de `representacao` não consome limite quando for recusada por regra eliminatória anterior.

### Normalização monetária

- [ ] O valor original da despesa é normalizado para duas casas decimais na moeda de origem.
- [ ] `33.333` é normalizado para `33.33`.
- [ ] `33.335` é normalizado para `33.34`.
- [ ] Quando houver conversão cambial, o resultado em BRL também é normalizado para duas casas decimais.
- [ ] A verificação de nota fiscal utiliza o valor normalizado em BRL.
- [ ] A aplicação dos limites utiliza o valor normalizado em BRL.
- [ ] Os totais utilizam valores normalizados em BRL.
- [ ] A identificação de duplicidade utiliza o valor original normalizado, e não o valor convertido.

### Moeda

- [ ] Quando `despesas[].moeda` estiver ausente, a moeda considerada é `BRL`.
- [ ] `brl`, `BRL` e ` BRL ` são normalizados para `BRL`.
- [ ] `usd`, `USD` e ` USD ` são normalizados para `USD`.
- [ ] A moeda não é inferida a partir de descrição, fornecedor ou qualquer outro texto livre.
- [ ] Despesas em `BRL` não passam por conversão cambial.
- [ ] A moeda original permanece disponível na saída.

### Conversão cambial

- [ ] Despesas em moeda diferente de `BRL` são convertidas para BRL antes da aplicação das regras monetárias.
- [ ] A conversão utiliza a taxa correspondente à moeda e à data da despesa quando ela existir.
- [ ] O valor convertido é normalizado para duas casas decimais antes da aplicação da política monetária.
- [ ] O valor convertido é utilizado para nota fiscal.
- [ ] O valor convertido é utilizado para limites.
- [ ] O valor convertido é utilizado para reembolso parcial.
- [ ] O valor convertido é utilizado nos totais.
- [ ] Valor e moeda originais permanecem preservados após a conversão.

### Cotação em data sem taxa

- [ ] Quando existir cotação exatamente na data da despesa, essa cotação é utilizada.
- [ ] Quando não existir cotação na data, é utilizada a cotação disponível mais recente anterior para a mesma moeda.
- [ ] Uma cotação posterior à data da despesa nunca é utilizada.
- [ ] Quando existirem várias cotações anteriores, utiliza-se a de data mais recente.
- [ ] Uma despesa de fim de semana pode utilizar a cotação da última data anterior disponível.

### Cotação indisponível

- [ ] Quando não existir nenhuma cotação utilizável para a moeda, a despesa recebe status `RECUSADA`.
- [ ] A despesa recusada por falha cambial recebe motivo `COTACAO_NAO_DISPONIVEL`.
- [ ] A despesa recusada por falha cambial recebe R$ 0,00 de reembolso.
- [ ] A despesa recusada por falha cambial não consome limite.
- [ ] Não é utilizada taxa igual a 1 como fallback.
- [ ] Não é utilizada taxa de outra moeda.
- [ ] Não é utilizada cotação futura.
- [ ] O sistema não consulta fonte externa para obter uma cotação ausente.
- [ ] O valor e a moeda originais permanecem disponíveis para rastreabilidade.

### Valores não positivos

- [ ] Uma despesa cujo valor considerado em BRL seja R$ 0,00 recebe status `RECUSADA`.
- [ ] Uma despesa cujo valor considerado em BRL seja negativo recebe status `RECUSADA`.
- [ ] Valores menores ou iguais a R$ 0,00 em BRL recebem R$ 0,00 de reembolso.
- [ ] Valores menores ou iguais a R$ 0,00 em BRL não aumentam nem reduzem os limites disponíveis.
- [ ] Valores menores ou iguais a R$ 0,00 em BRL não participam de `resumo.total_solicitado`.
- [ ] Valores menores ou iguais a R$ 0,00 em BRL não participam de `resumo.total_nao_reembolsavel`.
- [ ] Valor e moeda originais permanecem disponíveis para rastreabilidade.

### Interação e precedência entre regras

- [ ] Uma despesa recusada antes da aplicação dos limites não consome limite.
- [ ] Uma despesa sem nota fiscal obrigatória não consome limite.
- [ ] Uma duplicata recusada não consome limite.
- [ ] Uma despesa de categoria não contemplada não consome limite.
- [ ] Uma despesa fora da competência não consome limite.
- [ ] Uma despesa com valor não positivo não consome limite.
- [ ] Uma despesa recusada por falha cambial não consome limite.
- [ ] A categoria é normalizada antes da consulta à política e da verificação de duplicidade.
- [ ] A moeda é normalizada antes da duplicidade e da conversão.
- [ ] O valor original é normalizado antes da duplicidade e da conversão.
- [ ] A duplicidade é verificada com os valores originais antes da conversão.
- [ ] A conversão ocorre antes das regras monetárias dependentes de BRL.
- [ ] A nota fiscal é verificada depois da conversão e antes da aplicação do limite.
- [ ] As regras que recusam integralmente uma despesa são avaliadas antes do consumo dos limites.
- [ ] Quando várias despesas elegíveis compartilham um limite diário, a ordem original da entrada determina o consumo.

### Status das despesas

- [ ] Uma despesa positiva cujo valor em BRL seja integralmente reembolsável recebe status `APROVADA`.
- [ ] Uma despesa positiva cujo valor em BRL seja parcialmente reembolsável recebe status `PARCIAL`.
- [ ] Uma despesa cujo valor reembolsável seja R$ 0,00 recebe status `RECUSADA`.
- [ ] Para uma despesa positiva `APROVADA`, `valor_nao_reembolsavel` é `"0.00"`.
- [ ] Para uma despesa positiva `RECUSADA`, `valor_nao_reembolsavel` corresponde ao `valor_solicitado` em BRL.
- [ ] Para uma despesa `PARCIAL`, `valor_reembolsavel` é maior que R$ 0,00 e menor que `valor_solicitado`.
- [ ] Toda despesa `PARCIAL` possui motivo.
- [ ] Toda despesa `RECUSADA` possui motivo.

### Consistência dos totais

- [ ] `resumo.total_solicitado` corresponde à soma dos valores positivos considerados em BRL.
- [ ] `resumo.total_reembolsavel` corresponde à soma dos valores reembolsáveis das decisões individuais.
- [ ] `resumo.total_nao_reembolsavel` corresponde à soma dos valores não reembolsáveis das despesas positivas.
- [ ] Valores menores ou iguais a R$ 0,00 em BRL não reduzem `resumo.total_solicitado`.
- [ ] Para cada despesa positiva, `valor_solicitado` é igual à soma de `valor_reembolsavel` e `valor_nao_reembolsavel`.
- [ ] Para o resultado completo, `resumo.total_solicitado` é igual à soma de `resumo.total_reembolsavel` e `resumo.total_nao_reembolsavel`.
- [ ] Os totais do resumo são sempre expressos em BRL.

### Aprovação manual

- [ ] Nenhum fluxo de aprovação manual é necessário para que esta versão seja considerada concluída.
- [ ] O sistema não introduz status adicional como `PENDENTE_APROVACAO`.
- [ ] A ausência dessa funcionalidade está explicitamente registrada como fora de escopo.

### Determinismo e rastreabilidade

- [ ] A mesma entrada, política e conjunto de cotações processados mais de uma vez produzem o mesmo resultado.
- [ ] A ordem original das despesas é suficiente para determinar qual despesa consome primeiro um limite compartilhado.
- [ ] Nenhuma informação ausente da entrada é inferida a partir de texto livre para aumentar o valor reembolsável.
- [ ] Nenhuma cotação ausente é inventada.
- [ ] A seleção de política é determinística para um mesmo centro de custo.
- [ ] Todas as regras de negócio RN-001 a RN-025 possuem ao menos um caso verificável associado.
- [ ] Todos os casos de borda definidos na seção 7 possuem cobertura por teste automatizado.
- [ ] Todas as ambiguidades AMB-001 a AMB-030 possuem uma decisão explícita e, quando aplicável, estão associadas a pelo menos uma regra de negócio.

### Compatibilidade da Política v4

- [ ] O sistema processa despesas em BRL sem exigir o campo `moeda`.
- [ ] Uma entrada da baseline sem `moeda` continua sendo interpretada como BRL.
- [ ] O centro de custo deixa de ser apenas informativo e influencia os limites aplicáveis.
- [ ] Uma política específica pode produzir resultado diferente da política `padrao` para as mesmas despesas.
- [ ] A saída preserva informação suficiente para auditar uma conversão de moeda estrangeira.
- [ ] Limite igual a zero é distinguido de categoria ausente.
- [ ] A categoria `representacao` é tratada conforme a política selecionada.

### Interface obrigatória

- [ ] O sistema pode ser executado por uma CLI com a operação `calcular`.
- [ ] A CLI recebe o caminho do arquivo principal de entrada por meio de `--input`.
- [ ] A CLI recebe o caminho do arquivo de saída por meio de `--output`.
- [ ] Os dados auxiliares necessários à Política v4 são disponibilizados ao cálculo de forma determinística conforme o contrato definido para esta versão.
- [ ] Uma execução válida preserva a interface obrigatória:

```text
<seu-comando> calcular --input despesas.json --output resultado.json
```

- [ ] O arquivo indicado por `--output` contém o resultado no formato definido na seção 4.


## 10. O que fica em aberto

Esta seção registra limitações da política ou do formato de entrada que não podem ser resolvidas de forma definitiva com as informações atualmente disponíveis.

Para cada ponto em aberto, a especificação define um comportamento provisório para que o sistema continue sendo determinístico.

### ABERTO-001 — Identificação de colaborador em viagem

**Questão:** A política determina que colaboradores em viagem possuem limites ampliados em 50%, mas a entrada atual não informa explicitamente se o colaborador está ou não em viagem.

A Política v4 acrescenta despesas em moeda estrangeira, mas isso também não comprova a condição de viagem.

**Decisão provisória:** O sistema não infere a condição de viagem e não aplica o acréscimo de 50% enquanto não existir uma informação explícita e confiável na entrada.

**Impacto atual:** Nenhuma despesa recebe a ampliação de 50% apenas por descrição, fornecedor, hospedagem, aeroporto ou moeda estrangeira.

**O que permitiria resolver definitivamente:** Inclusão de uma informação explícita e confiável na entrada que identifique a condição de viagem aplicável ao período ou às despesas.

**Regras relacionadas:** RN-006.

---

### ABERTO-002 — Quantidade de diárias de hospedagem

**Questão:** A política define limite por diária, mas a entrada não possui um campo estruturado com a quantidade de diárias.

Algumas descrições podem mencionar informações como `"2 diarias"` ou `"3 noites"`, porém esse conteúdo está em texto livre.

**Decisão provisória:** Cada lançamento de hospedagem é considerado uma única diária e a descrição não é interpretada para determinar quantidade.

**Impacto atual:** Um lançamento de hospedagem possui, no máximo, um limite de hospedagem da política aplicável, independentemente de uma quantidade mencionada apenas na descrição.

**O que permitiria resolver definitivamente:** Inclusão de uma quantidade de diárias ou de datas estruturadas de início e fim da hospedagem na entrada.

**Regras relacionadas:** RN-003.

---

### ABERTO-003 — Data efetiva de lançamento

**Questão:** A política exige que as despesas sejam "lançadas dentro do período de competência", mas a entrada fornece apenas `despesas[].data`.

Não existe informação que permita distinguir:

- data em que a despesa ocorreu;
- data em que foi paga;
- data em que foi registrada no sistema;
- data em que foi submetida para reembolso.

**Decisão provisória:** `despesas[].data` é utilizada como referência para verificar a competência.

**Impacto atual:** Uma despesa cuja `data` esteja fora de `periodo.inicio` e `periodo.fim` é recusada, independentemente do que sua descrição informe sobre eventual lançamento posterior.

**O que permitiria resolver definitivamente:** Inclusão de um campo explícito de data de lançamento ou submissão e esclarecimento do RH sobre qual data deve ser considerada pela política.

**Regras relacionadas:** RN-007.

---

### ABERTO-004 — Critério definitivo de identificação de duplicatas

**Questão:** A política determina que duplicatas sejam tratadas, mas não fornece um identificador externo de transação nem estabelece formalmente quais atributos tornam dois lançamentos a mesma despesa.

Com a Política v4, também existe a necessidade de distinguir despesas realizadas em moedas diferentes.

**Decisão provisória:** São considerados duplicados os lançamentos que possuam:

- mesma data;
- mesma categoria normalizada;
- mesma descrição;
- mesmo fornecedor;
- mesma moeda original normalizada;
- mesmo valor original normalizado na moeda de origem;
- mesmo indicador de nota fiscal.

O campo `id` e o valor convertido para BRL não participam da identidade.

**Impacto atual:** Dois gastos legítimos e distintos que coincidam em todos esses atributos poderão ser classificados como duplicados.

Por outro lado, despesas originalmente diferentes não serão classificadas como duplicadas apenas por resultarem no mesmo valor convertido para BRL.

**O que permitiria resolver definitivamente:** Inclusão de um identificador confiável da transação, documento fiscal ou outro atributo de negócio capaz de identificar inequivocamente uma despesa.

**Regras relacionadas:** RN-008.

---

### ABERTO-005 — Valores negativos e estornos

**Questão:** A entrada permite valores negativos e pode conter lançamentos descritos como estorno, mas a política não determina como estornos devem participar do cálculo de reembolso.

Não está definido se um estorno deveria:

- reduzir o total solicitado;
- devolver limite anteriormente consumido;
- compensar outra despesa;
- ser processado separadamente;
- ser convertido quando estiver originalmente em moeda estrangeira.

**Decisão provisória:** Após a determinação do valor considerado em BRL, valores menores ou iguais a R$ 0,00 não são reembolsáveis e não alteram totais ou limites.

Valor e moeda originais permanecem disponíveis para rastreabilidade.

**Impacto atual:** Estornos são preservados no resultado individual, mas não possuem efeito financeiro sobre o cálculo de reembolso.

**O que permitiria resolver definitivamente:** Regra explícita do RH sobre tratamento de estornos, créditos e ajustes negativos, inclusive em moeda estrangeira.

**Regras relacionadas:** RN-012 e RN-015.

---

### ABERTO-006 — Múltiplos motivos de recusa

**Questão:** Uma mesma despesa pode violar mais de uma regra ao mesmo tempo.

A saída permite uma lista em `despesas[].motivos`, mas não existe orientação definitiva sobre a necessidade de apresentar:

- apenas o motivo determinante;
- todos os motivos detectáveis;
- apenas motivos avaliados até a primeira regra eliminatória.

**Decisão provisória:** A ordem definida na seção 8 determina o motivo principal da recusa.

O sistema deve apresentar ao menos esse motivo.

Motivos adicionais podem ser apresentados desde que:

- sejam verdadeiros;
- tenham sido efetivamente avaliados;
- não contradigam o motivo principal;
- não exijam executar etapas que a precedência explicitamente impede.

**Impacto atual:** Não é obrigatório continuar avaliando regras posteriores somente para produzir motivos adicionais depois que uma regra eliminatória já determinou R$ 0,00 de reembolso.

Por exemplo, uma despesa sem cotação utilizável pode ser recusada por `COTACAO_NAO_DISPONIVEL` sem verificar posteriormente o limite documental de R$ 100,00.

**O que permitiria resolver definitivamente:** Definição de requisito de auditoria indicando se a saída deve registrar apenas a causa determinante ou todas as violações aplicáveis.

**Regras relacionadas:** RN-025, ordem definida na seção 8 e contrato de saída da seção 4.

---

### ABERTO-007 — Versionamento das políticas

**Questão:** A especificação já evoluiu da Política v3 para a Política v4, mas ainda não existe uma definição formal sobre:

- como versões futuras da política serão identificadas nos dados fornecidos;
- como uma versão específica será associada a cada cálculo;
- se resultados antigos deverão ser recalculados quando uma política mudar;
- por quanto tempo políticas históricas deverão permanecer disponíveis.

**Decisão provisória:** Esta versão da especificação representa a Política de Reembolso v4.

Um cálculo é realizado com os dados de política fornecidos para essa execução, sem recalcular automaticamente resultados produzidos por versões anteriores.

**Impacto atual:** Mudanças futuras de comportamento exigem nova alteração da especificação e registro correspondente em `DECISIONS.md` antes de mudança na implementação.

**O que permitiria resolver definitivamente:** Processo formal de versionamento da política, incluindo identificador de versão, vigência e regra de associação entre cálculo e política.

**Regras relacionadas:** RN-016, RN-017 e processo de evolução da especificação.

---

### ABERTO-008 — Origem e governança das cotações

**Questão:** A Política v4 fornece dados de câmbio para o cálculo, mas não define:

- qual é a fonte oficial dessas taxas;
- quem é responsável por atualizar o conjunto de cotações;
- se as taxas podem ser corrigidas retroativamente;
- se existe uma versão ou identificador do conjunto de câmbio;
- qual taxa deve ser utilizada caso diferentes fontes apresentem valores distintos.

**Decisão provisória:** O motor considera os dados de câmbio recebidos como fonte de verdade para a execução.

Não consulta fontes externas nem tenta validar a taxa fornecida.

**Impacto atual:** Dois conjuntos diferentes de cotações podem produzir resultados diferentes para as mesmas despesas em moeda estrangeira.

**O que permitiria resolver definitivamente:** Definição de uma fonte oficial de câmbio e de um processo de versionamento e vigência das cotações.

**Regras relacionadas:** RN-019, RN-020 e RN-021.

---

### ABERTO-009 — Ausência de cotação histórica anterior

**Questão:** A especificação definiu que, quando não houver cotação exatamente na data da despesa, utiliza-se a cotação disponível mais recente anterior.

Entretanto, pode ocorrer uma despesa cuja moeda exista no conjunto de câmbio, mas cuja primeira cotação disponível seja posterior à data da despesa.

**Decisão provisória:** Uma cotação futura não é utilizada.

Se não existir cotação na data nem em nenhuma data anterior para a moeda, a despesa é recusada com motivo `COTACAO_NAO_DISPONIVEL`.

**Impacto atual:** Uma despesa pode ser recusada mesmo quando exista cotação para a mesma moeda em data posterior.

**O que permitiria resolver definitivamente:** Regra formal da política sobre fallback cambial quando não houver histórico anterior, caso o RH deseje comportamento diferente.

**Regras relacionadas:** RN-020 e RN-021.

---

### ABERTO-010 — Periodicidade de categorias futuras

**Questão:** A Política v4 introduz categorias parametrizadas por centro de custo e inclui `representacao`.

A especificação atual define explicitamente:

- alimentação como limite diário;
- transporte urbano como limite diário;
- hospedagem por lançamento/diária;
- representação como limite diário quando configurada dessa forma.

Não existe regra geral que determine automaticamente a periodicidade de uma categoria futura desconhecida.

**Decisão provisória:** Somente categorias e periodicidades explicitamente definidas pela política e por esta especificação são aplicadas.

O sistema não infere que uma nova categoria deve ser diária, por item, mensal ou de qualquer outro tipo apenas pelo nome.

**Impacto atual:** Uma nova categoria com semântica de limite diferente exigirá evolução da especificação antes de ser suportada corretamente.

**O que permitiria resolver definitivamente:** A política externa passar a informar de forma estruturada a periodicidade ou unidade de consumo de cada categoria.

**Regras relacionadas:** RN-009, RN-017 e RN-023.

---

### ABERTO-011 — Política externa inválida ou incompleta

**Questão:** A Política v4 passa a depender de dados externos de política, mas ainda não foi definido de forma completa o comportamento quando esses dados estiverem estruturalmente inválidos.

Exemplos:

- ausência da política `padrao`;
- limite com formato inválido;
- centro de custo com configuração incompleta;
- categoria sem informação necessária para determinar seu limite;
- política vazia.

**Decisão provisória:** Dados de política estruturalmente inválidos não devem ser tratados como simples recusa individual de despesas.

Eles impedem que o cálculo seja realizado de forma confiável e devem ser tratados como erro de entrada/configuração do cálculo.

**Impacto atual:** Não existe fallback para valores da v3 quando a política v4 recebida for inválida.

**O que permitiria resolver definitivamente:** Definição formal de um schema obrigatório para a política externa e dos erros esperados para cada violação estrutural.

**Regras relacionadas:** RN-016 e RN-017.

---

### ABERTO-012 — Dados de câmbio estruturalmente inválidos

**Questão:** A Política v4 define comportamento para cotação ausente, mas isso é diferente de receber um conjunto de câmbio estruturalmente inválido.

Exemplos:

- data em formato inválido;
- taxa não numérica;
- taxa zero ou negativa;
- moeda sem código válido;
- registros conflitantes para a mesma moeda e data.

**Decisão provisória:** Um conjunto de câmbio estruturalmente inválido é tratado como erro de entrada/configuração, e não como `COTACAO_NAO_DISPONIVEL` de uma despesa individual.

`COTACAO_NAO_DISPONIVEL` é reservado para dados de câmbio estruturalmente válidos que simplesmente não contenham uma cotação utilizável para aquela despesa.

**Impacto atual:** O sistema distingue erro dos dados auxiliares de ausência legítima de cotação.

**O que permitiria resolver definitivamente:** Definição formal do schema e das validações obrigatórias do conjunto de câmbio.

**Regras relacionadas:** RN-019, RN-020 e RN-021.

---

### ABERTO-013 — Precisão da taxa de câmbio

**Questão:** A política não define se a taxa de câmbio deve ser arredondada antes da multiplicação nem qual precisão mínima deve ser preservada.

**Decisão provisória:** A taxa fornecida é utilizada com a precisão disponível.

O arredondamento para duas casas decimais ocorre no valor monetário convertido para BRL, e não na taxa antes da multiplicação.

**Impacto atual:** Reduz-se a perda de precisão intermediária durante a conversão.

**O que permitiria resolver definitivamente:** Definição formal da precisão, escala e arredondamento das taxas de câmbio.

**Regras relacionadas:** RN-011 e RN-019.

---

### ABERTO-014 — Código de moeda desconhecido

**Questão:** Um lançamento pode informar um código de moeda que não exista nas cotações e que também não corresponda a um código reconhecido de moeda.

Não está definido se o motor deve validar semanticamente códigos monetários contra um catálogo externo.

**Decisão provisória:** O sistema normaliza o código informado, mas não consulta catálogo externo de moedas.

Se o código for diferente de `BRL` e não possuir cotação utilizável, aplica-se `COTACAO_NAO_DISPONIVEL`.

**Impacto atual:** Um código digitado incorretamente pode ser tratado como moeda sem cotação, desde que passe pela validação estrutural do campo.

**O que permitiria resolver definitivamente:** Definição de uma lista fechada de moedas aceitas ou adoção de catálogo oficial explicitamente exigido pela política.

**Regras relacionadas:** RN-018 e RN-021.

---

### ABERTO-015 — Evolução do schema de saída

**Questão:** A Política v4 introduz `valor_original` e `moeda_original` para garantir rastreabilidade cambial, alterando o contrato de saída da baseline v3.

Ainda não existe uma política geral de compatibilidade entre versões do schema de saída.

**Decisão provisória:** A Política v4 utiliza `schema_version = "2.0"`.

Consumidores da saída devem utilizar `schema_version` para distinguir o contrato da baseline v3 do contrato atual.

**Impacto atual:** Consumidores que dependiam estritamente do schema `"1.0"` precisam ser adaptados para os novos campos da versão `"2.0"`.

**O que permitiria resolver definitivamente:** Política formal de versionamento e compatibilidade do contrato de saída.

**Regras relacionadas:** contrato de saída da seção 4 e RN-015.

---