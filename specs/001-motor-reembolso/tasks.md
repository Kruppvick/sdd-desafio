# Tasks — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.0 · **Baseado no plan:** 1.0

> Cada task deve ser pequena o suficiente para virar um commit.
> Nenhuma task pode introduzir regra de negócio que não esteja definida na `spec.md`.

## T-001 — Implementar interface CLI e leitura/escrita JSON

**Descrição:**  
Criar a interface de linha de comando com a operação `calcular`, recebendo `--input` e `--output`, lendo o JSON de entrada e gravando um JSON de saída.

**Requisitos atendidos:**

- contrato de interface da seção 9 da spec;
- arquitetura de CLI e I/O definida no plan.

**Critério de aceite:**

- a operação `calcular` é reconhecida;
- `--input` e `--output` são obrigatórios;
- um arquivo JSON válido pode ser lido;
- o arquivo de saída é criado;
- testes da CLI passam.

---

## T-002 — Validar e normalizar a entrada

**Descrição:**  
Validar os campos obrigatórios da entrada e produzir as representações normalizadas utilizadas pelo motor.

**Requisitos atendidos:**

- RN-010;
- RN-011;
- contrato de entrada da seção 4 da spec.

**Critério de aceite:**

- categorias são normalizadas conforme RN-010;
- valores são normalizados conforme RN-011;
- datas válidas são convertidas para comparação;
- entradas estruturalmente inválidas são rejeitadas antes do motor;
- testes de normalização e validação passam.

---

## T-003 — Implementar categorias reembolsáveis

**Descrição:**  
Aplicar a regra que permite somente as categorias previstas pela política.

**Requisitos atendidos:**

- RN-009;
- RN-010.

**Critério de aceite:**

- `alimentacao`, `transporte_urbano` e `hospedagem` são reconhecidas;
- `ALIMENTACAO` é reconhecida após normalização;
- `coworking` recebe reembolso zero e status `RECUSADA`;
- testes relacionados passam.

---

## T-004 — Implementar período de competência

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

**Descrição:**  
Aplicar a obrigatoriedade de nota fiscal para despesas cujo valor normalizado seja superior a R$ 100,00.

**Requisitos atendidos:**

- RN-005;
- RN-011.

**Critério de aceite:**

- R$ 99,99 sem nota não é recusado por RN-005;
- R$ 100,00 sem nota não é recusado por RN-005;
- R$ 100,01 sem nota é recusado;
- R$ 100,01 com nota prossegue;
- teste da interação entre normalização e limite documental passa.

---

## T-006 — Implementar limite diário de alimentação

**Descrição:**  
Aplicar o limite diário compartilhado de R$ 60,00 para despesas elegíveis de alimentação.

**Requisitos atendidos:**

- RN-001;
- RN-004;
- RN-013;
- RN-014.

**Critério de aceite:**

- R$ 59,99 é integralmente reembolsável;
- R$ 60,00 é integralmente reembolsável;
- R$ 60,01 é parcialmente reembolsável;
- R$ 40,00 seguido de R$ 30,00 resulta em R$ 40,00 e R$ 20,00;
- o limite reinicia em nova data;
- testes relacionados passam.

---

## T-007 — Implementar limite diário de transporte urbano

**Descrição:**  
Aplicar o limite diário compartilhado de R$ 80,00 para despesas elegíveis de transporte urbano.

**Requisitos atendidos:**

- RN-002;
- RN-004;
- RN-013;
- RN-014.

**Critério de aceite:**

- R$ 79,99 é integralmente reembolsável;
- R$ 80,00 é integralmente reembolsável;
- R$ 80,01 é parcialmente reembolsável;
- R$ 50,00 seguido de R$ 50,00 resulta em R$ 50,00 e R$ 30,00;
- o limite reinicia em nova data;
- testes relacionados passam.

---

## T-008 — Implementar limite de hospedagem

**Descrição:**  
Aplicar o limite de R$ 250,00 para cada lançamento elegível de hospedagem.

**Requisitos atendidos:**

- RN-003;
- RN-004.

**Critério de aceite:**

- R$ 249,99 é integralmente reembolsável;
- R$ 250,00 é integralmente reembolsável;
- R$ 250,01 é parcialmente reembolsável;
- descrição contendo múltiplas diárias não altera o limite;
- testes relacionados passam.

---

## T-009 — Implementar tratamento de duplicatas

**Descrição:**  
Detectar duplicatas segundo a identidade definida na spec e recusar ocorrências posteriores.

**Requisitos atendidos:**

- RN-008;
- RN-010;
- RN-011.

**Critério de aceite:**

- registros que diferem apenas pelo `id` são detectados como duplicados;
- primeira ocorrência é avaliada normalmente;
- segunda ocorrência recebe reembolso zero;
- diferenças em fornecedor, descrição ou valor normalizado impedem classificação como duplicata;
- categoria normalizada participa da comparação;
- testes relacionados passam.

---

## T-010 — Implementar valores não positivos

**Descrição:**  
Tratar valores zero e negativos conforme a regra da baseline v3.

**Requisitos atendidos:**

- RN-012;
- RN-015.

**Critério de aceite:**

- valor zero recebe status `RECUSADA`;
- valor negativo recebe status `RECUSADA`;
- valores não positivos não consomem limites;
- valores não positivos não participam dos totais solicitados;
- valor original normalizado permanece disponível no resultado;
- testes relacionados passam.

---

## T-011 — Implementar precedência e consumo de limites

**Descrição:**  
Garantir que despesas inelegíveis sejam recusadas antes da aplicação dos limites e que somente valores efetivamente reembolsados consumam limite.

**Requisitos atendidos:**

- RN-013;
- RN-014;
- ordem definida na seção 8 da spec.

**Critério de aceite:**

- despesa sem nota não consome limite;
- duplicata não consome limite novamente;
- categoria não contemplada não consome limite;
- despesa fora da competência não consome limite;
- ordem original da entrada é preservada;
- testes de integração de precedência passam.

---

## T-012 — Implementar status, motivos e resumo

**Descrição:**  
Produzir as decisões individuais no schema definido e calcular o resumo final a partir dessas decisões.

**Requisitos atendidos:**

- RN-015;
- contrato de saída da seção 4 da spec.

**Critério de aceite:**

- despesas totalmente reembolsadas recebem `APROVADA`;
- despesas parcialmente reembolsadas recebem `PARCIAL`;
- despesas sem reembolso recebem `RECUSADA`;
- toda `PARCIAL` ou `RECUSADA` possui motivo;
- totais são derivados das decisões individuais;
- invariantes monetárias passam.

---

## T-013 — Implementar teste ponta a ponta com o arquivo de exemplo

**Descrição:**  
Executar o fluxo completo da CLI utilizando `exemplos/despesas-exemplo.json`.

**Requisitos atendidos:**

- interface obrigatória;
- critérios de aceite da seção 9 da spec.

**Critério de aceite:**

- a CLI processa o arquivo de exemplo sem erro;
- o arquivo de saída é JSON válido;
- existe uma decisão para cada despesa;
- resumo é consistente com as decisões;
- teste ponta a ponta passa.

---

## T-014 — Documentar execução e testes no README

**Descrição:**  
Documentar como preparar o ambiente, executar o motor e rodar a suíte de testes.

**Requisitos atendidos:**

- requisito de entrega do desafio.

**Critério de aceite:**

- README informa versão de Python necessária;
- README informa instalação das dependências;
- README mostra o comando da CLI;
- README mostra como executar os testes;
- os comandos documentados funcionam em um ambiente limpo.

## Matriz de rastreabilidade

A tabela abaixo relaciona cada regra de negócio da `spec.md` às tasks responsáveis por implementá-la e aos testes que devem demonstrar seu atendimento.

| Regra | Task(s) | Teste(s) esperado(s) |
|---|---|---|
| RN-001 — Limite diário de alimentação | T-006, T-011 | `test_rn001_limite_diario_alimentacao`, `test_rn001_limite_reinicia_em_nova_data` |
| RN-002 — Limite diário de transporte urbano | T-007, T-011 | `test_rn002_limite_diario_transporte`, `test_rn002_limite_reinicia_em_nova_data` |
| RN-003 — Limite de hospedagem | T-008 | `test_rn003_limite_hospedagem`, `test_rn003_nao_interpreta_diarias_da_descricao` |
| RN-004 — Reembolso parcial acima do limite | T-006, T-007, T-008 | `test_rn004_reembolso_parcial_alimentacao`, `test_rn004_reembolso_parcial_transporte`, `test_rn004_reembolso_parcial_hospedagem` |
| RN-005 — Obrigatoriedade de nota fiscal | T-005 | `test_rn005_99_99_sem_nota`, `test_rn005_100_sem_nota`, `test_rn005_100_01_sem_nota`, `test_rn005_100_01_com_nota` |
| RN-006 — Limites ampliados em viagem | T-011 | `test_rn006_nao_infere_viagem_por_descricao`, `test_rn006_nao_infere_viagem_por_hospedagem` |
| RN-007 — Período de competência | T-004, T-011 | `test_rn007_inicio_competencia_inclusivo`, `test_rn007_fim_competencia_inclusivo`, `test_rn007_data_anterior_recusada`, `test_rn007_data_posterior_recusada` |
| RN-008 — Tratamento de duplicatas | T-009, T-011 | `test_rn008_detecta_duplicata_com_ids_diferentes`, `test_rn008_primeira_ocorrencia_e_mantida`, `test_rn008_diferenca_de_fornecedor_nao_e_duplicata` |
| RN-009 — Categorias reembolsáveis | T-003 | `test_rn009_categorias_previstas_sao_reconhecidas`, `test_rn009_categoria_desconhecida_e_recusada` |
| RN-010 — Normalização de categoria | T-002, T-003, T-009 | `test_rn010_normaliza_maiusculas`, `test_rn010_remove_espacos_externos`, `test_rn010_categoria_normalizada_participa_da_duplicidade` |
| RN-011 — Normalização monetária | T-002, T-005, T-009 | `test_rn011_arredonda_33_333_para_33_33`, `test_rn011_arredonda_33_335_para_33_34`, `test_rn011_normalizacao_ocorre_antes_da_nota_fiscal` |
| RN-012 — Valores não positivos | T-010, T-011 | `test_rn012_valor_zero_e_recusado`, `test_rn012_valor_negativo_e_recusado`, `test_rn012_valor_negativo_nao_afeta_limites` |
| RN-013 — Consumo dos limites | T-006, T-007, T-011 | `test_rn013_sem_nota_nao_consome_limite`, `test_rn013_duplicata_nao_consome_limite`, `test_rn013_categoria_invalida_nao_consome_limite` |
| RN-014 — Ordem de consumo do limite diário | T-006, T-007, T-011 | `test_rn014_respeita_ordem_da_entrada`, `test_rn014_ordem_inversa_altera_distribuicao` |
| RN-015 — Consistência do resultado | T-010, T-012, T-013 | `test_rn015_resultado_individual_fecha`, `test_rn015_resumo_fecha_com_decisoes`, `test_rn015_valores_negativos_nao_reduzem_total_solicitado` |

## Cobertura das ambiguidades

As ambiguidades identificadas na spec também devem permanecer rastreáveis até as regras e tasks responsáveis pelo comportamento adotado.

| Ambiguidade | Regra(s) relacionada(s) | Task(s) |
|---|---|---|
| AMB-001 — Limite de alimentação por despesa ou por dia | RN-001 | T-006 |
| AMB-002 — Limite de transporte por despesa ou por dia | RN-002 | T-007 |
| AMB-003 — Quantidade de diárias | RN-003 | T-008 |
| AMB-004 — Significado de reembolso parcial | RN-004 | T-006, T-007, T-008 |
| AMB-005 — Exatamente R$ 100 exige nota | RN-005 | T-005 |
| AMB-006 — Despesa acima de R$ 100 sem nota | RN-005 | T-005 |
| AMB-007 — Nota antes ou depois do arredondamento | RN-005, RN-011 | T-002, T-005 |
| AMB-008 — Como determinar viagem | RN-006 | T-011 |
| AMB-009 — Fronteiras da competência | RN-007 | T-004 |
| AMB-010 — Qual data usar para competência | RN-007 | T-004 |
| AMB-011 — O que caracteriza duplicata | RN-008, RN-010, RN-011 | T-002, T-009 |
| AMB-012 — O que fazer com duplicata | RN-008 | T-009 |
| AMB-013 — Categoria diferencia maiúsculas/minúsculas | RN-009, RN-010 | T-002, T-003 |
| AMB-014 — Valores com mais de duas casas | RN-005, RN-008, RN-011 | T-002, T-005, T-009 |
| AMB-015 — Valores zero ou negativos | RN-012, RN-015 | T-010, T-012 |
| AMB-016 — Despesa recusada consome limite | RN-013 | T-011 |
| AMB-017 — Distribuição do limite entre várias despesas | RN-001, RN-002, RN-014 | T-006, T-007, T-011 |

## Ordem sugerida de execução

As tasks devem ser executadas na seguinte ordem:

```text
T-001
  ↓
T-002
  ↓
T-003
  ↓
T-004
  ↓
T-005
  ↓
T-006
  ↓
T-007
  ↓
T-008
  ↓
T-009
  ↓
T-010
  ↓
T-011
  ↓
T-012
  ↓
T-013
  ↓
T-014


