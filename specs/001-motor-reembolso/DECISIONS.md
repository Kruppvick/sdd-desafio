# Log de Decisões — Motor de Cálculo de Reembolso

Este arquivo registra **mudanças na especificação após a baseline inicial**.

As decisões tomadas durante a construção da primeira versão da Política de Reembolso v3 não são registradas aqui como mudanças, pois fazem parte da própria baseline documentada em `spec.md`.

Cada alteração posterior deve registrar:

- o que mudou;
- o gatilho da mudança;
- por que a mudança foi necessária;
- quais requisitos ou decisões anteriores foram invalidados;
- quais tasks foram afetadas;
- quais testes foram afetados;
- qual foi o impacto observado da mudança.

---

## Baseline

**Versão da spec:** 1.0  
**Política:** Política de Reembolso v3  
**Status:** baseline estabelecida

A baseline contém as decisões iniciais sobre as ambiguidades da Política v3.

Essas decisões estão documentadas diretamente em:

`specs/001-motor-reembolso/spec.md`

Nenhuma mudança de especificação foi registrada até este ponto.

---

## Formato das próximas decisões

### D-NNN — Título da decisão

**Data:** AAAA-MM-DD

**Gatilho:**  
O que aconteceu para tornar necessária uma revisão da especificação.

**O que mudou:**  
Descrição objetiva da mudança realizada na spec.

**Por quê:**  
Justificativa para a nova decisão.

**O que foi invalidado:**  
Regras, critérios de aceite, ambiguidades ou comportamentos anteriores que deixaram de ser válidos.

**Tasks afetadas:**  
Lista das tasks existentes que precisam ser alteradas ou das novas tasks criadas.

**Testes afetados:**  
Testes que precisam ser criados, alterados ou removidos.

**Impacto observado:**  
Arquivos alterados, esforço necessário e outras consequências relevantes da mudança.

---

## D-001 — Evolução da Política v3 para a Política v4

**Data:** 2026-08-20

**Gatilho:**  
Recebimento do envelope da Política de Reembolso v4 após a conclusão, implementação e validação da baseline v3.

O envelope introduziu novos dados e comportamentos que invalidam parte das premissas utilizadas pela especificação 1.0.

**O que mudou:**  

A especificação foi atualizada da versão 1.0, correspondente à Política v3, para a versão 2.0, correspondente à Política v4.

As principais mudanças são:

- os limites de alimentação, transporte urbano e hospedagem deixam de ser valores universais fixos;
- os limites e categorias passam a ser determinados pela política aplicável ao centro de custo do colaborador;
- `colaborador.centro_custo` deixa de ser apenas informativo e passa a participar do cálculo;
- quando não existir política específica para o centro de custo, utiliza-se a política `padrao`;
- despesas passam a aceitar o campo opcional `moeda`;
- ausência de `moeda` significa `BRL`;
- despesas em moeda estrangeira são convertidas para BRL antes da aplicação das regras monetárias;
- a conversão utiliza cotação da data da despesa ou, quando ausente, a cotação disponível mais recente anterior;
- moeda estrangeira sem cotação utilizável resulta em recusa com motivo `COTACAO_NAO_DISPONIVEL`;
- a obrigatoriedade de nota fiscal passa a considerar o valor convertido e normalizado em BRL;
- a identidade de duplicidade passa a considerar moeda e valor originais normalizados, antes da conversão;
- a categoria `representacao` passa a ser suportada quando estiver presente na política aplicável;
- categoria presente com limite R$ 0,00 passa a ser distinguida de categoria ausente;
- valor e moeda originais passam a ser preservados na saída;
- o schema de saída evolui de `"1.0"` para `"2.0"`;
- a aprovação manual apresentada como opcional permanece fora do escopo desta entrega.

**Por quê:**  

A baseline v3 assumia uma política única, com limites fixos e todos os valores tratados em BRL.

O envelope v4 tornou essas premissas inválidas ao introduzir políticas parametrizadas por centro de custo e suporte a moedas estrangeiras.

Manter o comportamento anterior produziria resultados incompatíveis com a nova política.

**O que foi invalidado:**  

Foram invalidadas ou alteradas as seguintes premissas da baseline:

- R$ 60,00 como limite universal de alimentação;
- R$ 80,00 como limite universal de transporte urbano;
- R$ 250,00 como limite universal de hospedagem;
- lista global fixa de categorias reembolsáveis;
- `centro_custo` sem influência sobre o cálculo;
- todos os valores de entrada tratados diretamente como BRL;
- conversão entre moedas explicitamente fora de escopo;
- duplicidade definida sem considerar moeda original;
- schema de saída `"1.0"` como contrato atual.

Permanecem válidas, com adaptações quando necessário:

- interpretação de limites diários como compartilhados por categoria e data;
- reembolso parcial até o limite disponível;
- fronteira estrita de R$ 100,00 para obrigatoriedade de nota fiscal;
- competência com datas inicial e final inclusivas;
- primeira ocorrência de duplicata avaliada normalmente;
- preservação da ordem original das despesas;
- somente valores efetivamente reembolsados consomem limites;
- não inferência da condição de viagem;
- tratamento de valores não positivos;
- invariantes de consistência dos totais.

**Requisitos afetados:**  

Foram revisadas as regras:

- RN-001;
- RN-002;
- RN-003;
- RN-004;
- RN-005;
- RN-006;
- RN-008;
- RN-009;
- RN-011;
- RN-012;
- RN-013;
- RN-014;
- RN-015.

Foram preservadas sem mudança conceitual relevante:

- RN-007;
- RN-010.

Foram adicionadas:

- RN-016 — seleção da política por centro de custo;
- RN-017 — política externa como fonte dos limites;
- RN-018 — moeda padrão e normalização da moeda;
- RN-019 — conversão para BRL;
- RN-020 — cotação ausente na data da despesa;
- RN-021 — moeda sem cotação disponível;
- RN-022 — limite igual a zero;
- RN-023 — categoria `representacao`;
- RN-024 — ordem da conversão e das regras monetárias;
- RN-025 — falha cambial e precedência.

**Ambiguidades afetadas:**  

As ambiguidades AMB-001 a AMB-017 foram preservadas e revisadas quando a Política v4 alterou seu contexto.

Foram adicionadas AMB-018 a AMB-030 para registrar decisões relacionadas a:

- seleção da política;
- limites externos;
- moeda padrão;
- normalização de moeda;
- fallback de cotação;
- moeda sem cotação;
- nota fiscal após conversão;
- duplicidade em múltiplas moedas;
- limite zero;
- categoria `representacao`;
- ordem entre conversão e regras;
- moeda estrangeira e condição de viagem;
- aprovação manual opcional.

**Tasks afetadas:**  

As tasks da baseline que possuem comportamento impactado deverão ser revisadas antes da implementação da v4.

Em especial:

- T-002 — validação e normalização da entrada;
- T-003 — categorias reembolsáveis;
- T-005 — obrigatoriedade de nota fiscal;
- T-006 — limite diário de alimentação;
- T-007 — limite diário de transporte urbano;
- T-008 — limite de hospedagem;
- T-009 — tratamento de duplicatas;
- T-010 — valores não positivos;
- T-011 — precedência e consumo de limites;
- T-012 — status, motivos e resumo;
- T-013 — fluxo ponta a ponta;
- T-014 — documentação de execução.

Novas tasks deverão ser criadas para os comportamentos introduzidos pela Política v4, especialmente seleção de política, normalização de moeda, conversão cambial, fallback histórico de cotação e categoria `representacao`.

**Testes afetados:**  

Testes da baseline que assumem limites fixos globais precisarão ser adaptados para trabalhar com a política aplicável.

Também serão necessários testes para:

- política específica por centro de custo;
- fallback para política `padrao`;
- moeda ausente considerada `BRL`;
- normalização de código de moeda;
- conversão com cotação da mesma data;
- conversão com última cotação anterior;
- rejeição de cotação futura;
- moeda sem cotação;
- conversão antes da nota fiscal;
- duplicidade usando moeda e valor originais;
- limite igual a zero;
- categoria `representacao`;
- preservação de valor e moeda originais;
- schema de saída `"2.0"`;
- precedência de falha cambial;
- totais com despesas em múltiplas moedas.

**Impacto observado:**  

A mudança afeta transversalmente especificação, plano técnico, tasks, testes, motor de cálculo, normalização, contrato de saída e CLI.

A implementação da baseline v3 não pode simplesmente receber novos valores de limite: ela precisa deixar de tratar categorias e limites como configuração fixa e incorporar política externa e conversão cambial.

A quantidade exata de arquivos de implementação alterados e o esforço necessário serão registrados após a conclusão da adaptação para a v4, para uso também na seção "O envelope" do relatório final.

---