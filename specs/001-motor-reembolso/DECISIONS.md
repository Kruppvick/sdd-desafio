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