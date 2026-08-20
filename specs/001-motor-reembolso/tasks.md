# Tasks — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado na spec:** 2.0 · **Evolução da baseline:** Política v3 → Política v4

> Cada task deve ser pequena o suficiente para virar um commit.
>
> Nenhuma task pode introduzir regra de negócio que não esteja definida na `spec.md`.
>
> As tasks T-001 a T-014 registram a implementação da baseline v3 já concluída.
>
> As tasks T-015 em diante representam o trabalho necessário para absorver a Política v4, conforme D-001 em `DECISIONS.md`.

---

# Baseline concluída — Política v3

## T-001 — Implementar interface CLI e leitura/escrita JSON

**Status:** Concluída na baseline v3.

**Descrição:**  
Criar a interface de linha de comando com a operação `calcular`, recebendo `--input` e `--output`, lendo o JSON de entrada e gravando um JSON de saída.

**Requisitos atendidos na baseline:**

- contrato de interface;
- leitura e escrita JSON;
- operação obrigatória `calcular`.

**Critério de aceite:**

- a operação `calcular` é reconhecida;
- `--input` e `--output` são obrigatórios;
- um arquivo JSON válido pode ser lido;
- o arquivo de saída é criado;
- testes da CLI passam.

---

## T-002 — Validar e normalizar a entrada

**Status:** Concluída na baseline v3; comportamento ampliado pela T-015.

**Descrição:**  
Validar os campos obrigatórios da entrada e produzir as representações normalizadas utilizadas pelo motor.

**Requisitos atendidos na baseline:**

- RN-010;
- RN-011;
- contrato de entrada.

**Critério de aceite da baseline:**

- categorias são normalizadas;
- valores são normalizados;
- datas válidas são convertidas para comparação;
- entradas estruturalmente inválidas são rejeitadas;
- testes de normalização e validação passam.

---

## T-003 — Implementar categorias reembolsáveis

**Status:** Concluída na baseline v3; comportamento substituído pela política parametrizada nas T-016, T-017 e T-023.

**Descrição:**  
Aplicar as categorias contempladas pela política.

**Requisitos atendidos na baseline:**

- RN-009;
- RN-010.

**Critério de aceite da baseline:**

- categorias da baseline são reconhecidas;
- categoria desconhecida recebe reembolso zero;
- normalização da categoria é respeitada;
- testes relacionados passam.

---

## T-004 — Implementar período de competência

**Status:** Concluída e preservada na Política v4.

**Descrição:**  
Verificar se a data da despesa está dentro do período de competência.

**Requisitos atendidos:**

- RN-007.

**Critério de aceite:**

- `periodo.inicio` é inclusivo;
- `periodo.fim` é inclusivo;
- data anterior é recusada;
- data posterior é recusada;
- testes de competência passam.

---

## T-005 — Implementar exigência de nota fiscal

**Status:** Concluída na baseline v3; comportamento cambial ampliado pela T-022.

**Descrição:**  
Aplicar a obrigatoriedade de nota fiscal para despesas acima do limite documental.

**Requisitos atendidos na baseline:**

- RN-005;
- RN-011.

**Critério de aceite da baseline:**

- R$ 99,99 sem nota não é recusado por RN-005;
- R$ 100,00 sem nota não é recusado por RN-005;
- R$ 100,01 sem nota é recusado;
- R$ 100,01 com nota prossegue;
- testes relacionados passam.

---

## T-006 — Implementar limite diário de alimentação

**Status:** Concluída na baseline v3; limite fixo substituído por configuração externa na T-017.

**Descrição:**  
Aplicar limite diário compartilhado para despesas elegíveis de alimentação.

**Requisitos relacionados:**

- RN-001;
- RN-004;
- RN-013;
- RN-014.

**Critério de aceite da baseline:**

- limite diário é compartilhado;
- reembolso parcial é suportado;
- limite reinicia em nova data;
- ordem da entrada é respeitada;
- testes relacionados passam.

---

## T-007 — Implementar limite diário de transporte urbano

**Status:** Concluída na baseline v3; limite fixo substituído por configuração externa na T-017.

**Descrição:**  
Aplicar limite diário compartilhado para despesas elegíveis de transporte urbano.

**Requisitos relacionados:**

- RN-002;
- RN-004;
- RN-013;
- RN-014.

**Critério de aceite da baseline:**

- limite diário é compartilhado;
- reembolso parcial é suportado;
- limite reinicia em nova data;
- ordem da entrada é respeitada;
- testes relacionados passam.

---

## T-008 — Implementar limite de hospedagem

**Status:** Concluída na baseline v3; limite fixo e limite zero são adaptados pela T-017.

**Descrição:**  
Aplicar o limite por lançamento elegível de hospedagem.

**Requisitos relacionados:**

- RN-003;
- RN-004.

**Critério de aceite da baseline:**

- hospedagem é limitada por lançamento;
- reembolso parcial é suportado;
- descrição contendo múltiplas diárias não altera o limite;
- testes relacionados passam.

---

## T-009 — Implementar tratamento de duplicatas

**Status:** Concluída na baseline v3; identidade ampliada para múltiplas moedas na T-021.

**Descrição:**  
Detectar duplicatas segundo a identidade definida na spec e recusar ocorrências posteriores.

**Requisitos relacionados:**

- RN-008;
- RN-010;
- RN-011.

**Critério de aceite da baseline:**

- registros que diferem apenas pelo `id` podem ser duplicados;
- primeira ocorrência é avaliada normalmente;
- segunda ocorrência recebe reembolso zero;
- diferenças nos campos da identidade impedem classificação como duplicata;
- testes relacionados passam.

---

## T-010 — Implementar valores não positivos

**Status:** Concluída na baseline v3; preservada com valores considerados em BRL na v4.

**Descrição:**  
Tratar valores zero e negativos conforme a especificação.

**Requisitos relacionados:**

- RN-012;
- RN-015.

**Critério de aceite:**

- valor zero recebe status `RECUSADA`;
- valor negativo recebe status `RECUSADA`;
- valores não positivos não consomem limites;
- valores não positivos não participam dos totais solicitados;
- rastreabilidade do lançamento é preservada;
- testes relacionados passam.

---

## T-011 — Implementar precedência e consumo de limites

**Status:** Concluída na baseline v3; fluxo ampliado pela T-024.

**Descrição:**  
Garantir que despesas inelegíveis sejam recusadas antes do consumo dos limites e que somente valores efetivamente reembolsados consumam limite.

**Requisitos relacionados:**

- RN-013;
- RN-014;
- ordem definida na seção 8.

**Critério de aceite da baseline:**

- despesa sem nota não consome limite;
- duplicata não consome limite novamente;
- categoria não contemplada não consome limite;
- despesa fora da competência não consome limite;
- ordem original da entrada é preservada;
- testes de integração passam.

---

## T-012 — Implementar status, motivos e resumo

**Status:** Concluída na baseline v3; schema e rastreabilidade ampliados pelas T-025 e T-026.

**Descrição:**  
Produzir as decisões individuais e calcular o resumo final.

**Requisitos relacionados:**

- RN-015;
- contrato de saída.

**Critério de aceite:**

- despesas totalmente reembolsadas recebem `APROVADA`;
- despesas parcialmente reembolsadas recebem `PARCIAL`;
- despesas sem reembolso recebem `RECUSADA`;
- toda `PARCIAL` ou `RECUSADA` possui motivo;
- totais são derivados das decisões individuais;
- invariantes monetárias passam.

---

## T-013 — Implementar teste ponta a ponta da baseline

**Status:** Concluída na Política v3; novo cenário v4 coberto pela T-027.

**Descrição:**  
Executar o fluxo completo da CLI utilizando o arquivo de exemplo da baseline.

**Critério de aceite:**

- CLI processa o exemplo sem erro;
- saída é JSON válido;
- existe uma decisão para cada despesa;
- resumo é consistente;
- teste ponta a ponta passa.

---

## T-014 — Documentar execução e testes no README

**Status:** Concluída na baseline v3; documentação será atualizada pela T-028.

**Descrição:**  
Documentar preparação do ambiente, execução do motor e suíte de testes.

**Critério de aceite da baseline:**

- README informa requisitos;
- README mostra o comando da CLI;
- README mostra como executar testes;
- comandos documentados funcionam.

---

# Evolução — Política v4

## T-015 — Adaptar validação e normalização para moeda

**Descrição:**  
Evoluir a preparação da entrada para aceitar o campo opcional `moeda`, aplicar `BRL` quando ausente e normalizar códigos monetários.

**Requisitos atendidos:**

- RN-011;
- RN-018;
- contrato de entrada da seção 4.

**Critério de aceite:**

- despesa sem `moeda` resulta em `BRL`;
- `usd`, `USD` e ` USD ` resultam em `USD`;
- valor original continua sendo normalizado na moeda de origem;
- moeda não é inferida de descrição ou fornecedor;
- testes da T-015 passam.

---

## T-016 — Implementar seleção da política por centro de custo

**Descrição:**  
Selecionar os limites e categorias aplicáveis utilizando `colaborador.centro_custo`.

**Requisitos atendidos:**

- RN-016;
- RN-017.

**Critério de aceite:**

- centro com configuração específica utiliza sua própria política;
- centro sem configuração específica utiliza `padrao`;
- não ocorre correspondência parcial entre centros;
- os limites da baseline não funcionam como fallback implícito;
- testes da T-016 passam.

---

## T-017 — Tornar categorias e limites dependentes da política

**Descrição:**  
Substituir categorias globais e limites fixos pelos valores da política selecionada.

**Requisitos atendidos:**

- RN-001;
- RN-002;
- RN-003;
- RN-004;
- RN-009;
- RN-017;
- RN-022.

**Critério de aceite:**

- alimentação utiliza o limite configurado;
- transporte utiliza o limite configurado;
- hospedagem utiliza o limite configurado;
- categoria ausente é recusada como não contemplada;
- categoria presente com limite zero é reconhecida e recebe reembolso zero pelo limite;
- alterar a política altera o cálculo sem alterar a regra no código;
- testes da T-017 passam.

---

## T-018 — Implementar conversão cambial para BRL

**Descrição:**  
Converter despesas em moeda estrangeira para BRL utilizando as cotações fornecidas.

**Requisitos atendidos:**

- RN-011;
- RN-019;
- RN-024.

**Critério de aceite:**

- despesa em `BRL` não sofre conversão;
- despesa estrangeira com cotação na mesma data utiliza essa cotação;
- valor original normalizado é utilizado na conversão;
- resultado convertido é normalizado para duas casas decimais;
- valor convertido é utilizado pelas regras monetárias;
- valor e moeda originais são preservados;
- testes da T-018 passam.

---

## T-019 — Implementar fallback histórico de cotação

**Descrição:**  
Determinar a cotação aplicável quando não existir taxa exatamente na data da despesa.

**Requisitos atendidos:**

- RN-020.

**Critério de aceite:**

- cotação da mesma data possui prioridade;
- na ausência dela, utiliza-se a cotação anterior mais recente;
- entre várias anteriores, utiliza-se a mais recente;
- cotação posterior nunca é utilizada;
- despesa em fim de semana pode utilizar a última cotação anterior;
- testes da T-019 passam.

---

## T-020 — Tratar moeda sem cotação utilizável

**Descrição:**  
Recusar despesas que necessitam de conversão mas não possuem cotação utilizável.

**Requisitos atendidos:**

- RN-021;
- RN-025.

**Critério de aceite:**

- moeda sem cotação utilizável recebe reembolso zero;
- status é `RECUSADA`;
- motivo é `COTACAO_NAO_DISPONIVEL`;
- cotação futura não é utilizada;
- taxa igual a 1 não é utilizada como fallback;
- taxa de outra moeda não é utilizada;
- despesa não consome limite;
- regras monetárias posteriores não são avaliadas;
- testes da T-020 passam.

---

## T-021 — Adaptar duplicidade para múltiplas moedas

**Descrição:**  
Evoluir a identidade de duplicidade para considerar moeda e valor originais normalizados.

**Requisitos atendidos:**

- RN-008;
- RN-011;
- RN-018.

**Critério de aceite:**

- moeda original normalizada participa da identidade;
- valor original normalizado participa da identidade;
- valor convertido para BRL não participa;
- 100 USD e 100 EUR não são duplicatas apenas pelo valor numérico;
- despesas diferentes que convertam para o mesmo BRL não se tornam duplicatas;
- primeira ocorrência continua sendo avaliada normalmente;
- testes da T-021 passam.

---

## T-022 — Aplicar nota fiscal após conversão cambial

**Descrição:**  
Adaptar a regra documental para utilizar o valor convertido e normalizado em BRL.

**Requisitos atendidos:**

- RN-005;
- RN-011;
- RN-019;
- RN-024.

**Critério de aceite:**

- R$ 100,00 em BRL não exige nota por RN-005;
- R$ 100,01 em BRL exige nota;
- despesa estrangeira convertida para R$ 100,00 não exige nota;
- despesa estrangeira convertida para R$ 100,01 exige nota;
- valor original estrangeiro não é comparado diretamente com R$ 100,00;
- testes da T-022 passam.

---

## T-023 — Implementar categoria `representacao`

**Descrição:**  
Permitir a avaliação de `representacao` quando a categoria estiver presente na política aplicável.

**Requisitos atendidos:**

- RN-009;
- RN-013;
- RN-014;
- RN-023.

**Critério de aceite:**

- `representacao` configurada é reconhecida;
- `representacao` ausente é recusada como categoria não contemplada;
- limite diário é compartilhado entre lançamentos da mesma data quando aplicável;
- limite é consumido na ordem original;
- despesas recusadas anteriormente não consomem o limite;
- testes da T-023 passam.

---

## T-024 — Integrar precedência da Política v4

**Descrição:**  
Atualizar o fluxo do motor para respeitar a ordem de avaliação definida na seção 8 da spec 2.0.

**Requisitos atendidos:**

- RN-013;
- RN-014;
- RN-016;
- RN-019;
- RN-020;
- RN-021;
- RN-024;
- RN-025.

**Critério de aceite:**

- política é selecionada antes da avaliação;
- categoria, moeda e valor original são normalizados;
- categoria e competência podem eliminar a despesa antes do câmbio;
- duplicidade utiliza dados originais antes da conversão;
- conversão ocorre antes da nota fiscal e dos limites;
- falha cambial interrompe regras monetárias posteriores;
- nota fiscal é avaliada antes do limite;
- somente valor reembolsado consome limite;
- ordem original é preservada;
- testes de integração passam.

---

## T-025 — Evoluir schema de saída para 2.0

**Descrição:**  
Adaptar o resultado para preservar informações da moeda original e manter os valores financeiros do cálculo em BRL.

**Requisitos atendidos:**

- contrato de saída da seção 4;
- RN-015;
- RN-019.

**Critério de aceite:**

- `schema_version` é `"2.0"`;
- cada despesa contém `valor_original`;
- cada despesa contém `moeda_original`;
- `valor_solicitado` representa o valor considerado em BRL;
- `valor_reembolsavel` é expresso em BRL;
- `valor_nao_reembolsavel` é expresso em BRL;
- resumo é expresso em BRL;
- valores estrangeiros originais permanecem auditáveis;
- invariantes financeiras passam;
- testes da T-025 passam.

---

## T-026 — Atualizar motivos da Política v4

**Descrição:**  
Adicionar os motivos necessários aos novos comportamentos sem perder os códigos existentes da baseline.

**Requisitos atendidos:**

- RN-021;
- RN-022;
- contrato de saída da seção 4.

**Critério de aceite:**

- `COTACAO_NAO_DISPONIVEL` possui descrição legível;
- limite zero utiliza motivo de limite e não categoria ausente;
- toda despesa `PARCIAL` possui motivo;
- toda despesa `RECUSADA` possui motivo;
- códigos da baseline permanecem estáveis quando o significado não mudou;
- testes da T-026 passam.

---

## T-027 — Implementar testes ponta a ponta da Política v4

**Descrição:**  
Validar o fluxo completo utilizando os arquivos fornecidos no envelope da Política v4.

**Requisitos atendidos:**

- critérios de aceite da seção 9;
- contrato de entrada e saída da seção 4;
- RN-001 a RN-025 aplicáveis aos cenários do envelope.

**Critério de aceite:**

- despesas da v4 são processadas sem erro com dados auxiliares válidos;
- política específica é aplicada;
- política `padrao` possui cenário automatizado;
- moedas estrangeiras são convertidas;
- fallback de cotação anterior é coberto;
- moeda sem cotação é recusada;
- `representacao` é coberta;
- limite zero é coberto;
- existe uma decisão para cada despesa;
- resumo fecha matematicamente em BRL;
- teste ponta a ponta passa.

---

## T-028 — Atualizar documentação de execução para a Política v4

**Descrição:**  
Atualizar a documentação operacional para refletir política externa, câmbio, schema 2.0 e execução da nova versão.

**Requisitos atendidos:**

- requisito de entrega do desafio;
- contrato da versão 2.0.

**Critério de aceite:**

- README explica os dados necessários à v4;
- README documenta `moeda` opcional;
- README informa que ausência de moeda significa BRL;
- README explica que os resultados financeiros são expressos em BRL;
- README informa `schema_version = "2.0"`;
- comandos documentados funcionam;
- suíte documentada passa.

---

# Matriz de rastreabilidade — Política v4

A tabela abaixo relaciona cada regra da `spec.md` às tasks responsáveis pela baseline e/ou por sua evolução na Política v4.

| Regra | Task(s) | Evidência de teste esperada |
|---|---|---|
| RN-001 — Limite diário de alimentação | T-006, T-017, T-024 | limite obtido da política; compartilhamento diário; limite esgotado; ordem da entrada |
| RN-002 — Limite diário de transporte urbano | T-007, T-017, T-024 | limite obtido da política; compartilhamento diário; reembolso parcial |
| RN-003 — Limite de hospedagem | T-008, T-017 | limite externo; uma diária por lançamento; limite zero |
| RN-004 — Reembolso parcial | T-006, T-007, T-008, T-017 | abaixo/no/acima do limite; limite totalmente consumido |
| RN-005 — Nota fiscal | T-005, T-022, T-024 | R$ 100,00; R$ 100,01; conversão antes da verificação |
| RN-006 — Viagem | T-011, T-024 | não inferir por descrição, hospedagem, aeroporto ou moeda estrangeira |
| RN-007 — Competência | T-004, T-024 | início/fim inclusivos; antes/depois recusados |
| RN-008 — Duplicatas | T-009, T-021, T-024 | moeda e valor originais; primeira ocorrência; BRL convertido fora da identidade |
| RN-009 — Categorias reembolsáveis | T-003, T-016, T-017, T-023 | categoria depende da política; ausente versus limite zero; representação |
| RN-010 — Normalização de categoria | T-002, T-003, T-021 | maiúsculas/minúsculas; espaços externos; uso na duplicidade |
| RN-011 — Normalização monetária | T-002, T-015, T-018, T-021, T-022 | valor original; arredondamento; valor convertido normalizado |
| RN-012 — Valores não positivos | T-010, T-024 | zero/negativo; sem impacto em limites/totais |
| RN-013 — Consumo dos limites | T-006, T-007, T-011, T-023, T-024 | somente valor reembolsado consome; falha cambial não consome |
| RN-014 — Ordem de consumo | T-006, T-007, T-011, T-023, T-024 | ordem original determina distribuição |
| RN-015 — Consistência do resultado | T-010, T-012, T-025, T-027 | invariantes individuais e resumo em BRL |
| RN-016 — Seleção da política | T-016, T-024 | política específica; fallback `padrao`; sem correspondência parcial |
| RN-017 — Política externa | T-016, T-017 | alteração externa do limite altera resultado; sem constantes universais |
| RN-018 — Moeda padrão e normalização | T-015, T-021 | ausência = BRL; normalização de código; uso na duplicidade |
| RN-019 — Conversão para BRL | T-018, T-022, T-024, T-025 | conversão; normalização; uso em regras; preservação do original |
| RN-020 — Cotação anterior | T-019, T-024 | mesma data; última anterior; nunca futura |
| RN-021 — Cotação indisponível | T-020, T-024, T-026 | recusa; motivo; sem consumo de limite |
| RN-022 — Limite zero | T-017, T-026 | categoria presente; reembolso zero; motivo de limite |
| RN-023 — Representação | T-023, T-024 | presente/ausente; limite diário; ordem |
| RN-024 — Ordem da conversão | T-018, T-022, T-024 | conversão antes de nota/limite; duplicidade antes da conversão |
| RN-025 — Falha cambial e precedência | T-020, T-024 | falha encerra regras monetárias posteriores e não consome limite |

---

# Cobertura das ambiguidades

| Ambiguidade | Regra(s) relacionada(s) | Task(s) |
|---|---|---|
| AMB-001 — Limite de alimentação por despesa ou por dia | RN-001 | T-006, T-017 |
| AMB-002 — Limite de transporte por despesa ou por dia | RN-002 | T-007, T-017 |
| AMB-003 — Quantidade de diárias | RN-003 | T-008, T-017 |
| AMB-004 — Significado de reembolso parcial | RN-004, RN-022 | T-017 |
| AMB-005 — Exatamente R$ 100 exige nota | RN-005 | T-005, T-022 |
| AMB-006 — Acima de R$ 100 sem nota | RN-005 | T-005, T-022 |
| AMB-007 — Nota após normalização/conversão | RN-005, RN-011, RN-019, RN-024 | T-018, T-022 |
| AMB-008 — Como determinar viagem | RN-006 | T-024 |
| AMB-009 — Fronteiras da competência | RN-007 | T-004 |
| AMB-010 — Qual data usar para competência | RN-007 | T-004 |
| AMB-011 — O que caracteriza duplicata | RN-008, RN-010, RN-011, RN-018 | T-021 |
| AMB-012 — O que fazer com duplicata | RN-008 | T-009, T-021 |
| AMB-013 — Categoria e capitalização | RN-009, RN-010 | T-002, T-017 |
| AMB-014 — Mais de duas casas decimais | RN-005, RN-008, RN-011, RN-019 | T-015, T-018, T-022 |
| AMB-015 — Valores zero ou negativos | RN-012, RN-015 | T-010, T-025 |
| AMB-016 — Despesa recusada consome limite | RN-013, RN-025 | T-024 |
| AMB-017 — Distribuição do limite | RN-001, RN-002, RN-013, RN-014, RN-023 | T-017, T-023, T-024 |
| AMB-018 — Centro sem política específica | RN-016, RN-017 | T-016 |
| AMB-019 — Limites v3 versus política externa | RN-001, RN-002, RN-003, RN-017 | T-016, T-017 |
| AMB-020 — Ausência de moeda | RN-018 | T-015 |
| AMB-021 — Normalização da moeda | RN-018 | T-015 |
| AMB-022 — Data sem cotação | RN-019, RN-020 | T-018, T-019 |
| AMB-023 — Moeda sem cotação | RN-021, RN-025 | T-020 |
| AMB-024 — Nota sobre original ou convertido | RN-005, RN-019, RN-024 | T-022 |
| AMB-025 — Duplicidade original ou convertido | RN-008, RN-011, RN-018 | T-021 |
| AMB-026 — Limite zero | RN-009, RN-022 | T-017, T-026 |
| AMB-027 — Representação | RN-009, RN-023 | T-023 |
| AMB-028 — Ordem da conversão | RN-008, RN-019, RN-024, RN-025 | T-024 |
| AMB-029 — Moeda estrangeira indica viagem | RN-006, RN-018 | T-015, T-024 |
| AMB-030 — Aprovação manual | Fora de escopo | Nenhuma task de implementação |

---

# Ordem sugerida de execução

As tasks T-001 a T-014 já foram concluídas na baseline v3.

A evolução para a Política v4 deve seguir:

```text
T-015 — moeda e normalização
   ↓
T-016 — seleção da política
   ↓
T-017 — categorias e limites parametrizados
   ↓
T-018 — conversão cambial
   ↓
T-019 — fallback histórico de cotação
   ↓
T-020 — cotação indisponível
   ↓
T-021 — duplicidade em múltiplas moedas
   ↓
T-022 — nota fiscal após conversão
   ↓
T-023 — representação
   ↓
T-024 — precedência integrada v4
   ↓
T-025 — schema de saída 2.0
   ↓
T-026 — motivos v4
   ↓
T-027 — ponta a ponta v4
   ↓
T-028 — README v4
```

## Regra de execução

Cada task da evolução deve seguir o ciclo:

```text
requisito já definido na spec
    ↓
teste automatizado
    ↓
falha esperada quando aplicável
    ↓
implementação mínima
    ↓
suíte completa
    ↓
revisão do diff
    ↓
commit referenciando a task
```

Nenhuma mudança de regra descoberta durante a implementação deve ser resolvida apenas no código ou no chat.

Se surgir nova decisão de negócio:

```text
spec.md
   ↓
DECISIONS.md
   ↓
tasks.md
   ↓
teste
   ↓
implementação
```