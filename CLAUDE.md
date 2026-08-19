# CLAUDE.md

## Objetivo

Este projeto implementa um motor de cálculo de reembolso orientado por especificação.

A fonte de verdade para regras de negócio é:

`specs/001-motor-reembolso/spec.md`

O plano técnico está em:

`specs/001-motor-reembolso/plan.md`

As tarefas executáveis estão em:

`specs/001-motor-reembolso/tasks.md`

Mudanças posteriores da especificação devem ser registradas em:

`specs/001-motor-reembolso/DECISIONS.md`

---

## Regra principal

Nunca implementar uma regra de negócio que não esteja definida na `spec.md`.

Se durante a implementação surgir a necessidade de explicar uma regra, decisão, exceção ou comportamento que não esteja documentado na spec:

1. parar a implementação;
2. identificar a ambiguidade ou lacuna;
3. atualizar a spec;
4. registrar a mudança em `DECISIONS.md`, quando for posterior à baseline;
5. atualizar as tasks afetadas;
6. somente depois continuar a implementação.

Conhecimento de negócio não deve existir apenas no chat, em comentários ou no código.

---

## Spec antes de código

A ordem obrigatória para mudanças de comportamento é:

```text
spec
  ↓
DECISIONS.md
  ↓
tasks.md
  ↓
testes
  ↓
implementação