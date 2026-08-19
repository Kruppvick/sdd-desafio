# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** baseline v3 · **Última alteração:** 2026-08-18

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
- Não trata conversão entre moedas.
- Não aplica regras contábeis, tributárias ou trabalhistas além da política de reembolso fornecida.
- Não modifica a política de reembolso; apenas aplica as interpretações documentadas nesta especificação.

## 4. Entrada e saída

### 4.1 Entrada

A entrada deve seguir o formato definido em `exemplos/despesas-exemplo.json`.

#### Colaborador

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | Identificador único do colaborador | Sim |
| `colaborador.nome` | texto | Nome do colaborador | Sim |
| `colaborador.centro_custo` | texto | Centro de custo ao qual o colaborador pertence | Sim |

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
| `despesas[].valor` | número | Valor informado no lançamento | Sim |
| `despesas[].tem_nota_fiscal` | booleano | Indica se a despesa possui nota fiscal (`true` ou `false`) | Sim |

### 4.2 Saída

A saída deve permitir rastrear cada despesa recebida na entrada até sua respectiva decisão de reembolso.

Valores monetários da saída são representados como texto decimal com exatamente duas casas decimais, no formato `"0.00"`.

| Campo | Tipo | Significado |
|---|---|---|
| `schema_version` | texto | Versão do formato da saída |
| `colaborador.id` | texto | Identificador do colaborador processado |
| `periodo.competencia` | texto | Competência processada |
| `resumo.total_solicitado` | texto monetário | Soma dos valores solicitados positivos, após normalização monetária |
| `resumo.total_reembolsavel` | texto monetário | Soma dos valores reembolsáveis |
| `resumo.total_nao_reembolsavel` | texto monetário | Soma das parcelas não reembolsáveis dos valores solicitados positivos |
| `despesas` | lista | Resultados individuais das despesas avaliadas |
| `despesas[].id` | texto | Identificador da despesa correspondente na entrada |
| `despesas[].valor_solicitado` | texto monetário | Valor informado na despesa após normalização monetária |
| `despesas[].valor_reembolsavel` | texto monetário | Valor que será reembolsado |
| `despesas[].valor_nao_reembolsavel` | texto monetário | Parcela positiva solicitada que não será reembolsada |
| `despesas[].status` | texto | Resultado da avaliação: `APROVADA`, `PARCIAL` ou `RECUSADA` |
| `despesas[].motivos` | lista | Justificativas para a decisão |
| `despesas[].motivos[].codigo` | texto | Código estável que identifica o motivo |
| `despesas[].motivos[].descricao` | texto | Explicação legível do motivo |

Para lançamentos cujo valor normalizado seja menor ou igual a R$ 0,00:

- `valor_solicitado` preserva o valor normalizado informado;
- `valor_reembolsavel` é `"0.00"`;
- `valor_nao_reembolsavel` é `"0.00"`;
- o status é `RECUSADA`;
- o lançamento não participa de `resumo.total_solicitado` nem de `resumo.total_nao_reembolsavel`.

#### Exemplo de saída

Para uma despesa de alimentação de R$ 72,50, considerando a aplicação do limite diário de R$ 60,00:

```json
{
  "schema_version": "1.0",
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

Os possíveis status são:

- `APROVADA`: todo o valor solicitado positivo é reembolsável.
- `PARCIAL`: apenas parte positiva do valor solicitado é reembolsável.
- `RECUSADA`: nenhum valor da despesa é reembolsável.

Toda despesa com status `PARCIAL` ou `RECUSADA` deve possuir ao menos um motivo que explique a decisão.

---

## 5. Regras de negócio

Cada regra possui um identificador único (`RN-NNN`) para permitir sua rastreabilidade até as ambiguidades, critérios de aceite, tarefas e testes correspondentes.

### RN-001 — Limite diário de alimentação

**Regra:** A soma dos valores reembolsáveis das despesas de alimentação de uma mesma data não pode ultrapassar R$ 60,00.

Quando houver mais de uma despesa de alimentação na mesma data, todas compartilham o mesmo limite diário e o consomem conforme RN-014.

**Origem:** Política do RH, item 1.

**Aceite:** Duas despesas elegíveis de alimentação de R$ 40,00 e R$ 30,00, nessa ordem e na mesma data, resultam respectivamente em R$ 40,00 e R$ 20,00 reembolsáveis, totalizando R$ 60,00 no dia.

---

### RN-002 — Limite diário de transporte urbano

**Regra:** A soma dos valores reembolsáveis das despesas de transporte urbano de uma mesma data não pode ultrapassar R$ 80,00.

Quando houver mais de uma despesa de transporte urbano na mesma data, todas compartilham o mesmo limite diário e o consomem conforme RN-014.

**Origem:** Política do RH, item 2.

**Aceite:** Duas despesas elegíveis de transporte urbano de R$ 50,00, nessa ordem e na mesma data, resultam respectivamente em R$ 50,00 e R$ 30,00 reembolsáveis, totalizando R$ 80,00 no dia.

---

### RN-003 — Limite de hospedagem

**Regra:** Hospedagem possui limite de R$ 250,00 por diária.

Como a entrada atual não possui um campo estruturado que informe a quantidade de diárias, cada lançamento de hospedagem é considerado uma única diária para efeito de cálculo.

Informações presentes apenas na descrição da despesa não são utilizadas para determinar a quantidade de diárias.

**Origem:** Política do RH, item 3.

**Aceite:** Um lançamento elegível de hospedagem de R$ 480,00 é limitado a R$ 250,00, mesmo quando sua descrição informa que corresponde a duas diárias.

---

### RN-004 — Reembolso parcial acima do limite

**Regra:** Quando uma despesa elegível ultrapassar o limite disponível aplicável, o sistema deve reembolsar até o limite disponível e considerar somente o excedente como não reembolsável.

**Origem:** Política do RH, item 4.

**Aceite:** Uma despesa elegível de alimentação de R$ 72,50, quando houver R$ 60,00 disponíveis no limite diário, resulta em R$ 60,00 reembolsáveis, R$ 12,50 não reembolsáveis e status `PARCIAL`.

---

### RN-005 — Obrigatoriedade de nota fiscal

**Regra:** A verificação da obrigatoriedade de nota fiscal utiliza o valor já normalizado conforme RN-011.

Despesas com valor normalizado estritamente superior a R$ 100,00 exigem nota fiscal para serem reembolsáveis.

Uma despesa de exatamente R$ 100,00 não exige nota fiscal por esta regra.

Quando uma despesa superior a R$ 100,00 não possuir nota fiscal, nenhum valor dessa despesa é reembolsável.

**Origem:** Política do RH, item 5.

**Aceite:**

- Uma despesa de R$ 100,00 sem nota fiscal pode prosseguir para avaliação pelas demais regras.
- Uma despesa de R$ 100,01 sem nota fiscal recebe R$ 0,00 de reembolso.
- Uma despesa de R$ 100,01 com nota fiscal pode prosseguir para avaliação pelas demais regras.

---

### RN-006 — Limites ampliados em viagem

**Regra:** A política prevê ampliação de 50% dos limites para colaboradores em viagem.

A entrada atual não possui informação explícita que permita determinar se o colaborador está em viagem. Portanto, nesta versão, o sistema utiliza os limites padrão.

O sistema não deve inferir a condição de viagem a partir da descrição da despesa, fornecedor, existência de hospedagem, corrida para aeroporto ou qualquer outra informação indireta.

**Origem:** Política do RH, item 6.

**Aceite:** Uma despesa cuja descrição mencione aeroporto ou hotel continua sendo avaliada pelos limites padrão quando não existir informação explícita de viagem na entrada.

---

### RN-007 — Período de competência

**Regra:** Uma despesa somente pode ser reembolsada quando `despesas[].data` estiver entre `periodo.inicio` e `periodo.fim`, incluindo as duas datas.

Na ausência de um campo específico para data de lançamento, `despesas[].data` é a data utilizada para verificar a competência.

**Origem:** Política do RH, item 7.

**Aceite:**

- Uma despesa com data igual a `periodo.inicio` está dentro da competência.
- Uma despesa com data igual a `periodo.fim` está dentro da competência.
- Uma despesa anterior a `periodo.inicio` recebe R$ 0,00 de reembolso.
- Uma despesa posterior a `periodo.fim` recebe R$ 0,00 de reembolso.

---

### RN-008 — Tratamento de duplicatas

**Regra:** A verificação de duplicidade utiliza categoria e valor já normalizados conforme RN-010 e RN-011.

Dois lançamentos são considerados duplicados quando possuem simultaneamente:

- mesma data;
- mesma categoria normalizada;
- mesma descrição;
- mesmo fornecedor;
- mesmo valor normalizado;
- mesmo indicador de nota fiscal.

O campo `id` não participa da comparação.

Quando forem encontradas duplicatas, a primeira ocorrência na ordem da entrada é avaliada normalmente e as ocorrências posteriores recebem R$ 0,00 de reembolso com motivo de duplicidade.

**Origem:** Política do RH, item 8.

**Aceite:** Dois lançamentos que diferem somente pelo campo `id` são considerados duplicados. O primeiro é avaliado normalmente e o segundo recebe status `RECUSADA` por duplicidade.

---

### RN-009 — Categorias reembolsáveis

**Regra:** Após a normalização definida em RN-010, somente as seguintes categorias estão contempladas pela política:

- `alimentacao`
- `transporte_urbano`
- `hospedagem`

Categorias diferentes dessas não são reembolsáveis.

**Origem:** Política do RH, item 9.

**Aceite:** Uma despesa da categoria `coworking` recebe R$ 0,00 de reembolso e status `RECUSADA`.

---

### RN-010 — Normalização de categoria

**Regra:** Antes da identificação da categoria e da verificação de duplicidade, são removidos espaços existentes no início e no fim do valor e diferenças entre letras maiúsculas e minúsculas são ignoradas.

**Origem:** Necessidade de definir de forma inequívoca como as categorias previstas no item 9 da política são identificadas.

**Aceite:** `alimentacao`, `ALIMENTACAO` e ` alimentacao ` são reconhecidas como a mesma categoria.

---

### RN-011 — Normalização monetária

**Regra:** Todos os valores de despesas são normalizados para duas casas decimais antes da aplicação das demais regras de negócio.

Quando for necessário arredondamento, utiliza-se o centavo mais próximo. Quando o valor estiver exatamente no ponto médio entre dois centavos, o arredondamento ocorre para cima em magnitude.

O valor normalizado é utilizado para verificação de nota fiscal, duplicidade, limites, totais e valores apresentados na saída.

**Origem:** A política define valores monetários em reais e centavos, mas a entrada permite valores com mais de duas casas decimais.

**Aceite:**

- R$ 33,333 é considerado R$ 33,33.
- R$ 33,335 é considerado R$ 33,34.

---

### RN-012 — Valores não positivos

**Regra:** Lançamentos cujo valor normalizado seja menor ou igual a R$ 0,00 não são reembolsáveis.

Esses lançamentos:

- recebem R$ 0,00 de reembolso;
- recebem status `RECUSADA`;
- não aumentam nem reduzem os limites disponíveis;
- não participam de `resumo.total_solicitado`;
- não participam de `resumo.total_nao_reembolsavel`.

O valor normalizado original continua sendo apresentado em `despesas[].valor_solicitado` para preservar a rastreabilidade do lançamento.

**Origem:** A política trata de reembolso de despesas e não define como créditos, estornos ou valores não positivos devem afetar o cálculo.

**Aceite:** Um lançamento de R$ -45,00 apresenta `valor_solicitado` igual a `"-45.00"`, `valor_reembolsavel` igual a `"0.00"`, `valor_nao_reembolsavel` igual a `"0.00"` e não altera os totais ou limites das demais despesas.

---

### RN-013 — Consumo dos limites

**Regra:** Somente valores efetivamente reembolsados consomem os limites aplicáveis.

Uma despesa que não seja reembolsável por estar fora da competência, ser duplicada, pertencer a categoria não contemplada, não possuir nota fiscal quando obrigatória ou possuir valor não positivo não reduz o limite disponível para outras despesas.

**Origem:** Interação entre os itens 1 a 9 da política.

**Aceite:** Uma despesa de alimentação de R$ 150,00 sem nota fiscal não consome o limite diário. Uma segunda despesa elegível de alimentação de R$ 50,00 na mesma data recebe R$ 50,00 de reembolso.

---

### RN-014 — Ordem de consumo do limite diário

**Regra:** Quando várias despesas elegíveis da mesma categoria compartilham um limite diário, o limite disponível é consumido seguindo a ordem em que as despesas aparecem na entrada.

**Origem:** A política estabelece limites diários, mas não define como distribuir um limite insuficiente entre várias despesas do mesmo dia.

**Aceite:** Para despesas elegíveis de alimentação de R$ 40,00 e R$ 30,00, nessa ordem e na mesma data, a primeira recebe R$ 40,00 e a segunda R$ 20,00. O total reembolsado no dia é R$ 60,00.

---

### RN-015 — Consistência do resultado

**Regra:** Para cada despesa cujo valor normalizado seja positivo:

`valor_solicitado = valor_reembolsavel + valor_nao_reembolsavel`.

Para despesas com valor normalizado menor ou igual a zero, aplica-se RN-012.

Os totais do resumo são calculados somente a partir de valores solicitados positivos e devem corresponder às somas das decisões individuais:

- `resumo.total_solicitado` corresponde à soma dos `valor_solicitado` positivos;
- `resumo.total_reembolsavel` corresponde à soma de todos os `valor_reembolsavel`;
- `resumo.total_nao_reembolsavel` corresponde à soma dos `valor_nao_reembolsavel` das despesas com valor solicitado positivo.

**Origem:** Requisito de rastreabilidade do resultado.

**Aceite:** Para qualquer resultado, `resumo.total_reembolsavel + resumo.total_nao_reembolsavel` é igual a `resumo.total_solicitado`.

---

## 6. Ambiguidades identificadas e decisões

Esta seção registra as ambiguidades encontradas na política original de reembolso e define explicitamente a interpretação adotada pelo sistema.

Cada decisão desta seção está associada a uma ou mais regras de negócio da seção 5.

### AMB-001 — O limite diário de alimentação é por despesa ou pela soma do dia?

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia."

**O que não está claro:** A política não informa se cada despesa de alimentação pode receber até R$ 60,00 ou se todas as despesas de alimentação realizadas no mesmo dia compartilham esse limite.

**Decisão:** O limite de R$ 60,00 é aplicado à soma dos valores reembolsáveis de todas as despesas de alimentação da mesma data.

**Justificativa:** A expressão "por dia" indica um limite diário total, e não um limite individual por lançamento. Essa interpretação também evita que o limite seja contornado pela divisão de uma despesa em vários lançamentos.

**Regra afetada:** RN-001.

---

### AMB-002 — O limite diário de transporte urbano é por despesa ou pela soma do dia?

**Texto original do RH:** "Transporte urbano tem limite de R$ 80 por dia."

**O que não está claro:** A política não informa se cada corrida ou lançamento possui individualmente um limite de R$ 80,00 ou se todas as despesas de transporte urbano do mesmo dia compartilham esse limite.

**Decisão:** O limite de R$ 80,00 é aplicado à soma dos valores reembolsáveis das despesas de transporte urbano da mesma data.

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

**Decisão:** A despesa é reembolsada até o limite disponível e somente o valor excedente deixa de ser reembolsado.

**Justificativa:** Essa interpretação corresponde diretamente ao uso da palavra "parcialmente", permitindo que a parte da despesa dentro do limite continue sendo reembolsada.

**Regra afetada:** RN-004.

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

**O que não está claro:** A política não informa se uma despesa de, por exemplo, R$ 150,00 sem nota deve ser totalmente recusada ou se os primeiros R$ 100,00 ainda podem ser reembolsados.

**Decisão:** Quando a nota fiscal for obrigatória e não estiver presente, toda a despesa recebe R$ 0,00 de reembolso.

**Justificativa:** R$ 100,00 define quando a documentação passa a ser obrigatória; não representa uma parcela que possa ser reembolsada sem documento.

**Regra afetada:** RN-005.

---

### AMB-007 — A obrigatoriedade da nota é verificada antes ou depois do arredondamento?

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."

**O que não está claro:** A entrada permite valores com mais de duas casas decimais. Sem uma ordem definida, um valor como R$ 100,004 poderia ser comparado diretamente com R$ 100,00 ou primeiro convertido para centavos.

**Decisão:** A normalização monetária ocorre antes da verificação da obrigatoriedade de nota fiscal. A comparação com R$ 100,00 utiliza o valor já normalizado para centavos.

**Justificativa:** Todas as decisões financeiras devem utilizar a mesma representação monetária, evitando que a mesma despesa tenha valores diferentes em etapas distintas do cálculo.

**Regra afetada:** RN-005 e RN-011.

---

### AMB-008 — Como determinar se o colaborador está em viagem?

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."

**O que não está claro:** A entrada não possui um campo que indique explicitamente se o colaborador está em viagem. Algumas despesas podem mencionar hotel ou aeroporto, mas isso não comprova de forma estruturada essa condição.

**Decisão:** O sistema não infere que o colaborador está em viagem. Enquanto a entrada não fornecer essa informação explicitamente, são utilizados os limites padrão.

**Justificativa:** Inferir viagem a partir de fornecedor, descrição, hospedagem ou corrida para aeroporto criaria uma condição de negócio que não foi definida pela política nem pelo formato de entrada.

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

**Decisão:** Dois lançamentos são considerados duplicados quando possuem a mesma data, categoria normalizada, descrição, fornecedor, valor normalizado e indicador de nota fiscal. O identificador `id` não participa da comparação.

**Justificativa:** O `id` identifica o lançamento e pode ser diferente mesmo quando a mesma despesa foi registrada mais de uma vez. Utilizá-lo na comparação impediria a identificação desse tipo de duplicidade.

**Regra afetada:** RN-008, RN-010 e RN-011.

---

### AMB-012 — O que fazer quando uma duplicata é encontrada?

**Texto original do RH:** "Duplicatas devem ser tratadas."

**O que não está claro:** A política não informa se todas as ocorrências devem ser recusadas, se devem ser agrupadas ou se uma delas deve ser considerada válida.

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

**Texto original do RH:** A política apresenta todos os limites como valores monetários em reais, mas não define o tratamento de frações inferiores a um centavo.

**O que não está claro:** A entrada permite valores com mais de duas casas decimais, e a política não informa como esses valores devem ser considerados no cálculo.

**Decisão:** O valor é normalizado para duas casas decimais antes da aplicação das demais regras. O arredondamento é feito para o centavo mais próximo e, em caso de valor exatamente no ponto médio, para cima em magnitude.

**Justificativa:** O resultado financeiro precisa ser expresso em centavos e todas as regras devem avaliar o mesmo valor monetário.

**Regra afetada:** RN-005, RN-008 e RN-011.

---

### AMB-015 — Como tratar despesas com valor zero ou negativo?

**Texto original do RH:** A política trata de reembolso de despesas, mas não estabelece uma regra para valores iguais ou inferiores a zero.

**O que não está claro:** Um valor negativo pode representar um estorno, mas não está definido se ele deve reduzir o total solicitado, devolver limite diário ou participar de algum tipo de compensação.

**Decisão:** Valores menores ou iguais a R$ 0,00 não são reembolsáveis, não participam dos totais solicitados e não reembolsáveis e não aumentam nem reduzem os limites disponíveis. O valor original normalizado continua presente no resultado individual para rastreabilidade.

**Justificativa:** Na ausência de uma regra explícita de compensação ou estorno, permitir que valores não positivos alterem totais ou limites criaria um comportamento financeiro não definido pela política.

**Regra afetada:** RN-012 e RN-015.

---

### AMB-016 — Uma despesa recusada consome o limite diário?

**Texto original do RH:** A política define limites e motivos que podem tornar uma despesa não reembolsável, mas não determina como essas regras interagem.

**O que não está claro:** Uma despesa sem nota fiscal, duplicada, fora da competência ou de categoria não reembolsável poderia consumir o limite diário antes de ser recusada.

**Decisão:** Somente valores efetivamente reembolsados consomem os limites. Despesas que recebem R$ 0,00 de reembolso não reduzem o limite disponível para outras despesas.

**Justificativa:** Uma despesa que não gera reembolso não deve reduzir o valor disponível para despesas elegíveis do mesmo dia.

**Regra afetada:** RN-013.

---

### AMB-017 — Como distribuir o limite diário entre várias despesas?

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia." e "Transporte urbano tem limite de R$ 80 por dia."

**O que não está claro:** Quando várias despesas elegíveis concorrem pelo mesmo limite e a soma ultrapassa o teto, a política não define se o valor deve ser dividido proporcionalmente, se alguma despesa possui prioridade ou se deve ser utilizada outra ordem.

**Decisão:** O limite é consumido seguindo a ordem em que as despesas aparecem na entrada.

**Justificativa:** A ordem da entrada fornece um critério determinístico sem criar uma regra adicional de prioridade baseada no valor ou no tipo da despesa.

**Regra afetada:** RN-001, RN-002 e RN-014.

---

## 7. Casos de borda

Os casos abaixo definem comportamentos esperados para valores de fronteira, combinações de regras e situações presentes ou sugeridas pelo arquivo de entrada de exemplo.

Quando o comportamento esperado indicar que uma despesa "prossegue para as demais regras", isso significa que a regra em questão não impede o reembolso, mas outras regras ainda podem reduzir ou recusar o valor.

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Alimentação abaixo do limite | Alimentação de R$ 59,99 | R$ 59,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-001 |
| Alimentação exatamente no limite | Alimentação de R$ 60,00 | R$ 60,00 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-001 |
| Alimentação um centavo acima do limite | Alimentação de R$ 60,01 | R$ 60,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-001, RN-004 |
| Duas despesas de alimentação no mesmo dia | Alimentação de R$ 40,00 seguida de R$ 30,00 na mesma data | Primeira recebe R$ 40,00; segunda recebe R$ 20,00; total reembolsado no dia é R$ 60,00 | RN-001, RN-014 |
| Limite de alimentação reinicia em nova data | Alimentação de R$ 60,00 em uma data e R$ 60,00 na data seguinte | Cada despesa pode receber R$ 60,00; o consumo do primeiro dia não afeta o segundo | RN-001 |
| Transporte abaixo do limite | Transporte urbano de R$ 79,99 | R$ 79,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-002 |
| Transporte exatamente no limite | Transporte urbano de R$ 80,00 | R$ 80,00 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-002 |
| Transporte um centavo acima do limite | Transporte urbano de R$ 80,01 | R$ 80,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-002, RN-004 |
| Duas despesas de transporte no mesmo dia | Transporte urbano de R$ 50,00 seguido de R$ 50,00 na mesma data | Primeira recebe R$ 50,00; segunda recebe R$ 30,00; total reembolsado no dia é R$ 80,00 | RN-002, RN-014 |
| Limite de transporte reinicia em nova data | Transporte urbano de R$ 80,00 em uma data e R$ 80,00 na data seguinte | Cada despesa pode receber R$ 80,00; o consumo do primeiro dia não afeta o segundo | RN-002 |
| Hospedagem abaixo do limite | Hospedagem de R$ 249,99 com nota fiscal | R$ 249,99 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-003, RN-005 |
| Hospedagem exatamente no limite | Hospedagem de R$ 250,00 com nota fiscal | R$ 250,00 reembolsáveis, desde que nenhuma outra regra impeça o reembolso | RN-003, RN-005 |
| Hospedagem um centavo acima do limite | Hospedagem de R$ 250,01 com nota fiscal | R$ 250,00 reembolsáveis, R$ 0,01 não reembolsável e status `PARCIAL` | RN-003, RN-004, RN-005 |
| Quantidade de diárias somente na descrição | Hospedagem de R$ 480,00 com nota fiscal e descrição `"Hotel - 2 diarias"` | A descrição não é interpretada; o lançamento representa uma diária e é limitado a R$ 250,00 | RN-003 |
| Hospedagem sem nota fiscal acima de R$ 100,00 | Hospedagem de R$ 480,00 sem nota fiscal | R$ 0,00 reembolsáveis; o limite de hospedagem não chega a ser consumido | RN-003, RN-005, RN-013 |
| Valor abaixo do limite documental sem nota | Despesa de R$ 99,99 com `tem_nota_fiscal = false` | A ausência de nota fiscal não impede o reembolso por RN-005; a despesa prossegue para as demais regras | RN-005 |
| Valor exatamente no limite documental sem nota | Despesa de R$ 100,00 com `tem_nota_fiscal = false` | A ausência de nota fiscal não impede o reembolso por RN-005; a despesa prossegue para as demais regras | RN-005 |
| Valor um centavo acima do limite documental sem nota | Despesa de R$ 100,01 com `tem_nota_fiscal = false` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-005 |
| Valor um centavo acima do limite documental com nota | Despesa de R$ 100,01 com `tem_nota_fiscal = true` | A regra de nota fiscal é satisfeita e a despesa prossegue para as demais regras | RN-005 |
| Valor arredondado para exatamente R$ 100,00 sem nota | Despesa de R$ 100,004 com `tem_nota_fiscal = false` | Valor normalizado para R$ 100,00; a ausência de nota não impede o reembolso por RN-005 | RN-005, RN-011 |
| Valor arredondado para R$ 100,01 sem nota | Despesa de R$ 100,005 com `tem_nota_fiscal = false` | Valor normalizado para R$ 100,01; R$ 0,00 reembolsáveis por ausência de nota fiscal | RN-005, RN-011 |
| Primeiro dia da competência | `despesas[].data` igual a `periodo.inicio` | A despesa é considerada dentro da competência e prossegue para as demais regras | RN-007 |
| Último dia da competência | `despesas[].data` igual a `periodo.fim` | A despesa é considerada dentro da competência e prossegue para as demais regras | RN-007 |
| Dia anterior à competência | `despesas[].data` um dia antes de `periodo.inicio` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-007 |
| Dia posterior à competência | `despesas[].data` um dia depois de `periodo.fim` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-007 |
| Despesa antiga descrita como lançamento atrasado | Data fora do período, mas descrição informa que a despesa foi lançada posteriormente | A descrição não altera a competência; a verificação utiliza exclusivamente `despesas[].data` e o reembolso é R$ 0,00 | RN-007 |
| Duplicata com identificadores diferentes | Dois registros com mesma data, categoria normalizada, descrição, fornecedor, valor normalizado e indicador de nota fiscal, mas IDs diferentes | Primeiro é avaliado normalmente; segundo recebe R$ 0,00, status `RECUSADA` e motivo de duplicidade | RN-008 |
| Registros com fornecedor diferente | Dois registros iguais nos demais campos usados para duplicidade, mas com fornecedores diferentes | Não são considerados duplicados | RN-008 |
| Registros com descrição diferente | Dois registros iguais nos demais campos usados para duplicidade, mas com descrições diferentes | Não são considerados duplicados | RN-008 |
| Registros com valores diferentes | Dois registros iguais nos demais campos usados para duplicidade, mas com valores normalizados diferentes | Não são considerados duplicados | RN-008 |
| Duplicata com diferença apenas na capitalização da categoria | Um registro usa `alimentacao` e outro `ALIMENTACAO`, com os demais campos de comparação iguais | Após normalização da categoria, os registros são considerados duplicados | RN-008, RN-010 |
| Duplicata com valores que normalizam para o mesmo centavo | Dois registros iguais nos demais campos, com valores que após RN-011 resultam no mesmo valor monetário | Os registros são considerados duplicados após a normalização monetária | RN-008, RN-011 |
| Categoria não contemplada | Categoria `coworking` | R$ 0,00 reembolsáveis e status `RECUSADA` | RN-009 |
| Categoria em letras maiúsculas | Categoria `ALIMENTACAO` | É reconhecida como `alimentacao` e avaliada pelas regras dessa categoria | RN-009, RN-010 |
| Categoria com espaços externos | Categoria ` alimentacao ` | É reconhecida como `alimentacao` e avaliada pelas regras dessa categoria | RN-009, RN-010 |
| Valor com três casas abaixo do ponto médio | Valor R$ 33,333 | Valor normalizado para R$ 33,33 antes da aplicação das demais regras | RN-011 |
| Valor com três casas no ponto médio | Valor R$ 33,335 | Valor normalizado para R$ 33,34 antes da aplicação das demais regras | RN-011 |
| Valor zero | Valor R$ 0,00 | `valor_solicitado` é `"0.00"`, `valor_reembolsavel` é `"0.00"`, `valor_nao_reembolsavel` é `"0.00"`, status `RECUSADA` e nenhum impacto nos limites ou totais | RN-012, RN-015 |
| Valor negativo | Valor R$ -45,00 | `valor_solicitado` é `"-45.00"`, `valor_reembolsavel` é `"0.00"`, `valor_nao_reembolsavel` é `"0.00"`, status `RECUSADA` e nenhum impacto nos limites ou totais | RN-012, RN-015 |
| Despesa sem nota não consome limite | Alimentação de R$ 150,00 sem nota seguida de alimentação de R$ 50,00 válida, na mesma data | Primeira recebe R$ 0,00 e não consome o limite; segunda recebe R$ 50,00 | RN-005, RN-013 |
| Categoria não contemplada não consome limite | `coworking` de R$ 60,00 seguido de alimentação válida de R$ 60,00 na mesma data | O `coworking` recebe R$ 0,00 e não interfere no limite de alimentação; a alimentação pode receber R$ 60,00 | RN-009, RN-013 |
| Duplicata não consome limite novamente | Três lançamentos de alimentação no mesmo dia: R$ 40,00 válido, sua duplicata e outro lançamento válido de R$ 20,00 | Primeiro recebe R$ 40,00; duplicata recebe R$ 0,00; terceiro recebe R$ 20,00; total diário é R$ 60,00 | RN-001, RN-008, RN-013 |
| Ordem dos lançamentos altera a distribuição, mas não o teto diário | Alimentação de R$ 40,00 seguida de R$ 30,00 | Reembolsos individuais são R$ 40,00 e R$ 20,00 | RN-001, RN-014 |
| Ordem inversa dos lançamentos | Alimentação de R$ 30,00 seguida de R$ 40,00 | Reembolsos individuais são R$ 30,00 e R$ 30,00; total diário continua R$ 60,00 | RN-001, RN-014 |
| Indício de viagem na descrição | Descrição contém `"aeroporto"` ou `"hotel"` | A condição de viagem não é inferida; os limites padrão continuam sendo utilizados | RN-006 |
| Existência de hospedagem | Entrada contém uma despesa da categoria `hospedagem` | A existência de hospedagem não caracteriza automaticamente que o colaborador está em viagem | RN-006 |
| Fornecedor relacionado a viagem | Fornecedor é um hotel ou serviço de transporte ligado a aeroporto | A condição de viagem não é inferida pelo fornecedor | RN-006 |
| Total solicitado com apenas valores positivos | Despesas normalizadas de R$ 10,00, R$ 20,00 e R$ 30,00 | `resumo.total_solicitado` é `"60.00"` | RN-015 |
| Total solicitado com valor negativo | Despesas de R$ 50,00, R$ -20,00 e R$ 30,00 | O valor negativo não participa do total; `resumo.total_solicitado` é `"80.00"` | RN-012, RN-015 |
| Total não reembolsável | Despesas positivas que totalizam R$ 100,00, sendo R$ 60,00 reembolsáveis | `resumo.total_nao_reembolsavel` é `"40.00"` | RN-015 |
| Consistência matemática do resumo | Resultado com `"100.00"` solicitado, `"60.00"` reembolsável e `"40.00"` não reembolsável | `resumo.total_reembolsavel + resumo.total_nao_reembolsavel = resumo.total_solicitado` | RN-015 |
| Despesa totalmente aprovada | Valor positivo integralmente reembolsável | `valor_reembolsavel` é igual a `valor_solicitado`, `valor_nao_reembolsavel` é `"0.00"` e status é `APROVADA` | RN-015 |
| Despesa parcialmente aprovada | Apenas parte positiva do valor pode ser reembolsada | `valor_reembolsavel` é maior que `"0.00"` e menor que `valor_solicitado`; status é `PARCIAL` | RN-004, RN-015 |
| Despesa positiva totalmente recusada | Valor positivo que falha em uma regra eliminatória | `valor_reembolsavel` é `"0.00"`, `valor_nao_reembolsavel` é igual ao `valor_solicitado` e status é `RECUSADA` | RN-015 |

## 8. Ordem de aplicação das regras

A ordem de aplicação das regras é parte do comportamento do sistema, pois uma mesma despesa pode estar sujeita a mais de uma regra.

As regras são avaliadas na seguinte ordem:

1. **Normalização monetária**
   - O valor da despesa é normalizado para duas casas decimais conforme RN-011.
   - Todas as verificações monetárias posteriores utilizam esse valor normalizado.

2. **Normalização da categoria**
   - A categoria é normalizada conforme RN-010.
   - A categoria normalizada é utilizada tanto para identificar as categorias reembolsáveis quanto para verificar duplicidade.

3. **Verificação de valor não positivo**
   - Valores normalizados menores ou iguais a R$ 0,00 são tratados conforme RN-012.
   - A despesa recebe status `RECUSADA` e R$ 0,00 de reembolso.
   - O lançamento não consome limites nem participa dos totais solicitados e não reembolsáveis.
   - Nenhuma regra de limite precisa ser aplicada a esse lançamento.

4. **Verificação da categoria**
   - A categoria normalizada é comparada com as categorias contempladas pela política, conforme RN-009.
   - Categorias não contempladas recebem status `RECUSADA` e R$ 0,00 de reembolso.
   - A despesa recusada não consome nenhum limite.

5. **Verificação do período de competência**
   - `despesas[].data` é comparada com `periodo.inicio` e `periodo.fim`, conforme RN-007.
   - As datas inicial e final são inclusivas.
   - Despesas fora do período recebem status `RECUSADA` e R$ 0,00 de reembolso.
   - A despesa recusada não consome nenhum limite.

6. **Verificação de duplicidade**
   - A duplicidade é verificada conforme RN-008, utilizando categoria e valor já normalizados.
   - A primeira ocorrência é mantida para avaliação.
   - Ocorrências posteriores identificadas como duplicadas recebem status `RECUSADA` e R$ 0,00 de reembolso.
   - Uma duplicata recusada não consome novamente o limite aplicável.

7. **Verificação da obrigatoriedade de nota fiscal**
   - O valor já normalizado é utilizado para verificar RN-005.
   - Valores de até R$ 100,00 não exigem nota fiscal por essa regra.
   - Valores estritamente superiores a R$ 100,00 exigem nota fiscal.
   - Quando a nota for obrigatória e estiver ausente, a despesa recebe status `RECUSADA` e R$ 0,00 de reembolso.
   - A despesa recusada não consome o limite aplicável.

8. **Determinação do limite aplicável**
   - Alimentação utiliza o limite diário definido em RN-001.
   - Transporte urbano utiliza o limite diário definido em RN-002.
   - Hospedagem utiliza o limite definido em RN-003.
   - A condição de viagem não é inferida; enquanto essa informação não existir explicitamente na entrada, são utilizados os limites padrão conforme RN-006.

9. **Determinação do limite ainda disponível**
   - Para alimentação e transporte urbano, é considerado quanto do limite da categoria naquela data já foi consumido por despesas anteriores.
   - Somente valores efetivamente reembolsados anteriormente consomem o limite, conforme RN-013.
   - A ordem original das despesas na entrada determina qual lançamento utiliza primeiro o limite disponível, conforme RN-014.

10. **Cálculo do valor reembolsável**
    - Se o valor da despesa estiver integralmente dentro do limite disponível, todo o valor é reembolsável.
    - Se o valor ultrapassar o limite disponível, somente a parcela dentro do limite é reembolsável, conforme RN-004.
    - Se o limite disponível já estiver totalmente consumido, o valor reembolsável da despesa é R$ 0,00.

11. **Determinação do status e dos motivos**
    - `APROVADA`: todo o valor solicitado positivo é reembolsável.
    - `PARCIAL`: parte positiva do valor solicitado é reembolsável e parte não é.
    - `RECUSADA`: nenhum valor da despesa é reembolsável.
    - Toda despesa `PARCIAL` ou `RECUSADA` recebe ao menos um motivo que justifique a decisão.

12. **Atualização do limite consumido**
    - Somente o valor efetivamente reembolsado é acrescentado ao consumo do limite correspondente.
    - Valores não reembolsáveis nunca consomem limite.
    - Uma despesa recusada não altera o limite disponível para despesas posteriores.

13. **Cálculo do resumo**
    - Após a avaliação de todas as despesas, os totais são calculados conforme RN-015.
    - `resumo.total_solicitado` corresponde à soma dos valores solicitados positivos e normalizados.
    - `resumo.total_reembolsavel` corresponde à soma de todos os valores reembolsáveis.
    - `resumo.total_nao_reembolsavel` corresponde à soma das parcelas não reembolsáveis dos valores solicitados positivos.
    - Valores solicitados menores ou iguais a R$ 0,00 não participam desses totais.

### Regras de precedência

Quando uma despesa puder ser recusada por mais de um motivo, a primeira regra eliminatória encontrada na ordem definida acima determina a recusa principal.

Isso significa, por exemplo:

- uma despesa de categoria não contemplada e também sem nota fiscal obrigatória é recusada primeiro por categoria;
- uma despesa fora da competência e também sem nota fiscal obrigatória é recusada primeiro por estar fora da competência;
- uma duplicata que também exigiria nota fiscal é recusada primeiro por duplicidade;
- uma despesa sem nota fiscal obrigatória é recusada antes da aplicação do limite da categoria.

Regras que recusam integralmente uma despesa são aplicadas antes das regras de limite. Dessa forma, despesas que não podem gerar reembolso não consomem valores que poderiam ser utilizados por despesas elegíveis posteriores.

### Exemplo de precedência

Considere, nesta ordem, duas despesas de alimentação na mesma data:

1. R$ 150,00 sem nota fiscal;
2. R$ 50,00 com nota fiscal.

A primeira despesa é recusada pela ausência de nota fiscal obrigatória e recebe R$ 0,00 de reembolso. Como valores recusados não consomem limite, os R$ 60,00 do limite diário de alimentação continuam disponíveis.

A segunda despesa é elegível e recebe R$ 50,00 de reembolso.

O resultado é:

- primeira despesa: R$ 0,00 reembolsáveis;
- segunda despesa: R$ 50,00 reembolsáveis;
- limite diário consumido: R$ 50,00;
- limite diário restante: R$ 10,00.

## 9. Critérios de aceite

O sistema está pronto quando todos os critérios abaixo forem atendidos e puderem ser verificados sem a necessidade de consultar a implementação.

### Entrada e saída

- [ ] O sistema aceita uma entrada válida no formato definido na seção 4.
- [ ] O sistema produz exatamente uma decisão para cada despesa recebida na entrada.
- [ ] Cada decisão permite identificar a despesa original por meio de seu `id`.
- [ ] Todos os valores monetários da saída são apresentados como texto decimal com exatamente duas casas decimais.
- [ ] Cada despesa apresenta `valor_solicitado`, `valor_reembolsavel`, `valor_nao_reembolsavel`, `status` e `motivos`.
- [ ] Os únicos status possíveis são `APROVADA`, `PARCIAL` e `RECUSADA`.
- [ ] Toda despesa com status `PARCIAL` ou `RECUSADA` apresenta ao menos um motivo para a decisão.

### Alimentação

- [ ] O total reembolsável de alimentação em uma mesma data nunca ultrapassa R$ 60,00.
- [ ] Despesas de alimentação em datas diferentes possuem limites independentes.
- [ ] Quando várias despesas de alimentação compartilham o mesmo limite diário, o limite é consumido na ordem em que aparecem na entrada.
- [ ] Uma despesa de alimentação que ultrapassa o limite disponível pode ser parcialmente reembolsada até o valor restante do limite.

### Transporte urbano

- [ ] O total reembolsável de transporte urbano em uma mesma data nunca ultrapassa R$ 80,00.
- [ ] Despesas de transporte urbano em datas diferentes possuem limites independentes.
- [ ] Quando várias despesas de transporte urbano compartilham o mesmo limite diário, o limite é consumido na ordem em que aparecem na entrada.
- [ ] Uma despesa de transporte urbano que ultrapassa o limite disponível pode ser parcialmente reembolsada até o valor restante do limite.

### Hospedagem

- [ ] Cada lançamento elegível de hospedagem possui limite de R$ 250,00.
- [ ] Uma hospedagem elegível acima de R$ 250,00 é parcialmente reembolsada até R$ 250,00.
- [ ] Informações sobre quantidade de diárias presentes somente na descrição da despesa não alteram o limite aplicado.
- [ ] A existência de uma despesa de hospedagem não faz o sistema inferir automaticamente que o colaborador está em viagem.

### Nota fiscal

- [ ] Uma despesa de exatamente R$ 100,00 não é recusada apenas por ausência de nota fiscal.
- [ ] Uma despesa de R$ 100,01 sem nota fiscal recebe R$ 0,00 de reembolso.
- [ ] Uma despesa superior a R$ 100,00 com nota fiscal pode prosseguir para avaliação pelas demais regras.
- [ ] Quando a nota fiscal é obrigatória e está ausente, toda a despesa é não reembolsável.
- [ ] A verificação do limite de R$ 100,00 utiliza o valor já normalizado para duas casas decimais.

### Viagem

- [ ] O sistema não infere a condição de viagem a partir da descrição da despesa.
- [ ] O sistema não infere a condição de viagem a partir do fornecedor.
- [ ] O sistema não infere a condição de viagem pela existência de hospedagem.
- [ ] O sistema não infere a condição de viagem pela existência de despesas relacionadas a aeroporto.
- [ ] Enquanto a entrada não fornecer informação explícita de viagem, são utilizados os limites padrão.

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
- [ ] A comparação de duplicidade utiliza categoria normalizada.
- [ ] A comparação de duplicidade utiliza valor monetário normalizado.

### Categorias

- [ ] `alimentacao`, `transporte_urbano` e `hospedagem` são reconhecidas como categorias contempladas pela política.
- [ ] Categorias diferentes das contempladas pela política recebem R$ 0,00 de reembolso.
- [ ] A categoria `coworking` recebe status `RECUSADA`.
- [ ] Diferenças entre letras maiúsculas e minúsculas não alteram a identificação da categoria.
- [ ] Espaços existentes no início ou no fim da categoria não alteram sua identificação.
- [ ] `alimentacao`, `ALIMENTACAO` e ` alimentacao ` são reconhecidas como a mesma categoria.

### Normalização monetária

- [ ] Todos os valores das despesas são normalizados para duas casas decimais antes da aplicação das demais regras.
- [ ] R$ 33,333 é normalizado para R$ 33,33.
- [ ] R$ 33,335 é normalizado para R$ 33,34.
- [ ] O valor normalizado é utilizado na verificação de nota fiscal.
- [ ] O valor normalizado é utilizado na identificação de duplicatas.
- [ ] O valor normalizado é utilizado na aplicação dos limites.
- [ ] O valor normalizado é utilizado nos totais e valores apresentados na saída.

### Valores não positivos

- [ ] Uma despesa com valor igual a R$ 0,00 recebe status `RECUSADA`.
- [ ] Uma despesa com valor negativo recebe status `RECUSADA`.
- [ ] Despesas com valor menor ou igual a R$ 0,00 recebem R$ 0,00 de reembolso.
- [ ] Despesas com valor menor ou igual a R$ 0,00 não aumentam nem reduzem os limites disponíveis.
- [ ] Despesas com valor menor ou igual a R$ 0,00 não participam de `resumo.total_solicitado`.
- [ ] Despesas com valor menor ou igual a R$ 0,00 não participam de `resumo.total_nao_reembolsavel`.
- [ ] O valor normalizado original de um lançamento não positivo permanece disponível em `despesas[].valor_solicitado` para rastreabilidade.

### Interação e precedência entre regras

- [ ] Uma despesa recusada antes da aplicação dos limites não consome limite.
- [ ] Uma despesa sem nota fiscal obrigatória não consome limite.
- [ ] Uma duplicata recusada não consome limite.
- [ ] Uma despesa de categoria não contemplada não consome limite.
- [ ] Uma despesa fora da competência não consome limite.
- [ ] Uma despesa com valor não positivo não consome limite.
- [ ] A normalização monetária ocorre antes das comparações monetárias.
- [ ] A normalização da categoria ocorre antes da identificação da categoria e da verificação de duplicidade.
- [ ] As regras que recusam integralmente uma despesa são avaliadas antes da aplicação dos limites.
- [ ] Quando várias despesas elegíveis compartilham um limite diário, a ordem original da entrada determina o consumo do limite.

### Status das despesas

- [ ] Uma despesa positiva cujo valor seja integralmente reembolsável recebe status `APROVADA`.
- [ ] Uma despesa positiva cujo valor seja parcialmente reembolsável recebe status `PARCIAL`.
- [ ] Uma despesa cujo valor reembolsável seja R$ 0,00 recebe status `RECUSADA`.
- [ ] Para uma despesa positiva `APROVADA`, `valor_nao_reembolsavel` é `"0.00"`.
- [ ] Para uma despesa positiva `RECUSADA`, `valor_nao_reembolsavel` corresponde ao `valor_solicitado`.
- [ ] Para uma despesa `PARCIAL`, `valor_reembolsavel` é maior que R$ 0,00 e menor que `valor_solicitado`.

### Consistência dos totais

- [ ] `resumo.total_solicitado` corresponde à soma dos valores solicitados positivos após normalização.
- [ ] `resumo.total_reembolsavel` corresponde à soma dos valores reembolsáveis das decisões individuais.
- [ ] `resumo.total_nao_reembolsavel` corresponde à soma dos valores não reembolsáveis das despesas positivas.
- [ ] Valores menores ou iguais a R$ 0,00 não reduzem `resumo.total_solicitado`.
- [ ] Para cada despesa positiva, `valor_solicitado` é igual à soma de `valor_reembolsavel` e `valor_nao_reembolsavel`.
- [ ] Para o resultado completo, `resumo.total_solicitado` é igual à soma de `resumo.total_reembolsavel` e `resumo.total_nao_reembolsavel`.

### Determinismo e rastreabilidade

- [ ] A mesma entrada processada mais de uma vez produz o mesmo resultado.
- [ ] A ordem original das despesas é suficiente para determinar qual despesa consome primeiro um limite compartilhado.
- [ ] Nenhuma informação ausente da entrada é inferida a partir de texto livre para aumentar o valor reembolsável.
- [ ] Todas as regras de negócio RN-001 a RN-015 possuem ao menos um caso verificável associado.
- [ ] Todos os casos de borda definidos na seção 7 possuem cobertura por teste automatizado.
- [ ] Todas as ambiguidades AMB-001 a AMB-017 possuem uma decisão explícita e estão associadas a pelo menos uma regra de negócio.

### Interface obrigatória

- [ ] O sistema pode ser executado por uma CLI com a operação `calcular`.
- [ ] A CLI recebe o caminho do arquivo de entrada por meio de `--input`.
- [ ] A CLI recebe o caminho do arquivo de saída por meio de `--output`.
- [ ] Uma execução válida segue a interface:

```text
<seu-comando> calcular --input despesas.json --output resultado.json
```

- [ ] O arquivo indicado por `--output` contém o resultado no formato definido na seção 4.

## 10. O que fica em aberto

## 10. O que fica em aberto

Esta seção registra limitações da política ou do formato de entrada que não podem ser resolvidas de forma definitiva com as informações atualmente disponíveis.

Para cada ponto em aberto, a especificação define um comportamento provisório para que o sistema continue sendo determinístico.

### ABERTO-001 — Identificação de colaborador em viagem

**Questão:** A política determina que colaboradores em viagem possuem limites ampliados em 50%, mas a entrada atual não informa explicitamente se o colaborador está ou não em viagem.

**Decisão provisória:** O sistema não infere a condição de viagem e aplica sempre os limites padrão.

**Impacto atual:** Nenhuma despesa recebe a ampliação de 50%.

**O que permitiria resolver definitivamente:** Inclusão de uma informação explícita e confiável na entrada que identifique a condição de viagem aplicável ao período ou às despesas.

**Regras relacionadas:** RN-006.

---

### ABERTO-002 — Quantidade de diárias de hospedagem

**Questão:** A política define limite de R$ 250,00 por diária, mas a entrada não possui um campo estruturado com a quantidade de diárias.

Algumas descrições podem mencionar informações como `"2 diarias"` ou `"3 noites"`, porém esse conteúdo está em texto livre.

**Decisão provisória:** Cada lançamento de hospedagem é considerado uma única diária e a descrição não é interpretada para determinar quantidade.

**Impacto atual:** Um lançamento de hospedagem possui limite máximo de R$ 250,00, independentemente de uma quantidade mencionada apenas na descrição.

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

**Decisão provisória:** São considerados duplicados os lançamentos que possuam a mesma data, categoria normalizada, descrição, fornecedor, valor normalizado e indicador de nota fiscal, desconsiderando o campo `id`.

**Impacto atual:** Dois gastos legítimos e distintos que coincidam em todos esses atributos poderão ser classificados como duplicados.

**O que permitiria resolver definitivamente:** Inclusão de um identificador confiável da transação, documento fiscal ou outro atributo de negócio capaz de identificar inequivocamente uma despesa.

**Regras relacionadas:** RN-008.

---

### ABERTO-005 — Valores negativos e estornos

**Questão:** A entrada permite valores negativos e o exemplo contém um lançamento descrito como estorno, mas a política não determina como estornos devem participar do cálculo de reembolso.

Não está definido se um estorno deveria:

- reduzir o total solicitado;
- devolver limite diário anteriormente consumido;
- compensar outra despesa;
- ser processado separadamente.

**Decisão provisória:** Valores menores ou iguais a R$ 0,00 não são reembolsáveis e não alteram totais ou limites.

**Impacto atual:** Estornos são preservados no resultado individual para rastreabilidade, mas não possuem efeito financeiro sobre o cálculo de reembolso.

**O que permitiria resolver definitivamente:** Regra explícita do RH sobre tratamento de estornos, créditos e ajustes negativos.

**Regras relacionadas:** RN-012 e RN-015.

---

### ABERTO-006 — Múltiplos motivos de recusa

**Questão:** Uma mesma despesa pode violar mais de uma regra ao mesmo tempo. A saída permite uma lista em `despesas[].motivos`, mas ainda não existe orientação do RH sobre a necessidade de apresentar todos os motivos detectáveis ou apenas o motivo determinante da decisão.

**Decisão provisória:** A ordem definida na seção 8 determina o motivo principal da recusa. O sistema deve apresentar ao menos esse motivo.

Motivos adicionais poderão ser apresentados desde que sejam verdadeiros e não contradigam o motivo principal.

**Impacto atual:** Não é obrigatório continuar avaliando regras posteriores apenas para produzir motivos adicionais depois que uma regra eliminatória já determinou reembolso de R$ 0,00.

**O que permitiria resolver definitivamente:** Definição do requisito de auditoria indicando se a saída deve registrar apenas a causa determinante ou todas as violações aplicáveis.

**Regras relacionadas:** ordem definida na seção 8 e contrato de saída da seção 4.

---

### ABERTO-007 — Alterações futuras da política

**Questão:** A política fornecida corresponde à versão 3, mas não há definição sobre como futuras versões serão representadas nem sobre a necessidade de recalcular resultados antigos.

**Decisão provisória:** Esta especificação representa exclusivamente as regras e decisões adotadas para a Política de Reembolso de Despesas — v3.

**Impacto atual:** Mudanças futuras de limites, categorias ou critérios exigem nova alteração da especificação antes de qualquer mudança de comportamento do sistema.

**O que permitiria resolver definitivamente:** Processo formal de versionamento da política e definição de como uma versão da política deve ser associada a cada cálculo.

**Regras relacionadas:** RN-001 a RN-015.