# Desafio Prático — Spec Driven Development

Aula bônus de SDD, fechando a trilha:

`AI Fluency` → `Claude 101` → `Claude Code 101` → `Building with the Claude API` → `Claude Code in Action` → `Módulo SDD` → **Desafio**

**Individual · 2 dias · Claude Code**

---

## Comece por aqui

1. **[`DESAFIO.md`](DESAFIO.md)** — o enunciado. Leia inteiro antes de escrever qualquer coisa.
2. **[`RUBRICA.md`](RUBRICA.md)** — como você é avaliado. É pública de propósito; leia antes de começar.
3. **[`exemplos/despesas-exemplo.json`](exemplos/despesas-exemplo.json)** — a entrada de referência. Não é decoração: percorra item por item antes de escrever a spec.
4. **[`FAQ.md`](FAQ.md)** — travou? Comece por aqui. **O instrutor está fora durante o desafio**, então o FAQ é o canal de suporte.

---

## Como participar

**1. Faça um fork deste repositório.** Ele precisa ser público, ou você não conseguirá compartilhar depois.

**2. Clone o seu fork e prepare a estrutura de trabalho:**

```bash
git clone https://github.com/<seu-usuario>/sdd-desafio.git
cd sdd-desafio
cp template/CLAUDE.md .
cp -r template/specs .
cp -r template/docs .
git add -A && git commit -m "chore: estrutura inicial a partir do template"
```

<details>
<summary>PowerShell</summary>

```powershell
git clone https://github.com/<seu-usuario>/sdd-desafio.git
cd sdd-desafio
Copy-Item template\CLAUDE.md .
Copy-Item template\specs . -Recurse
Copy-Item template\docs . -Recurse
git add -A; git commit -m "chore: estrutura inicial a partir do template"
```
</details>

Os arquivos em `template/` são esqueletos com as perguntas que cada documento precisa responder. Deixe a pasta `template/` onde está — ela serve de referência.

**3. Trabalhe no seu fork**, seguindo as três regras do jogo descritas no [`DESAFIO.md`](DESAFIO.md):

- Nenhum commit sem task
- Explicação no chat que não está na spec é bug de spec
- Interações exportadas (`/export`) e commitadas em `docs/sessions/`

**4. No Dia 2, às 10h**, você recebe uma mudança de requisito pelo canal da turma. Ela é obrigatória e vale 20 pontos. Chegue nesse momento com o sistema base funcionando e testado.

> Durante os dois dias o instrutor está de férias e não responde mensagens. Dúvida de processo: [`FAQ.md`](FAQ.md). Dúvida sobre o que a política do RH significa não tem resposta — decidir isso é o exercício.

**5. Entregue** enviando o link do seu fork no formulário. Prazo: **Dia 2, 18h**.

---

## O que o seu fork precisa conter ao final

```
seu-fork/
├── CLAUDE.md                     # convenções do projeto para o agente
├── README.md                     # como rodar e como testar o SEU projeto
├── specs/
│   └── 001-motor-reembolso/
│       ├── spec.md               # o QUÊ e o PORQUÊ
│       ├── plan.md               # o COMO
│       ├── tasks.md              # T-001..T-0NN, com critério de aceite
│       └── DECISIONS.md          # log de mudanças de spec
├── src/
├── tests/
└── docs/
    ├── sessions/                 # exports das suas conversas com o Claude
    └── RELATORIO.md              # o relatório final
```

Sobre o `README.md`: substitua este arquivo pelo README do **seu** projeto — como rodar, como testar, o que você construiu. Um README que não permite rodar o projeto custa pontos.

---

## Antes de começar, confirme que o `/export` funciona

Abra o Claude Code, troque duas mensagens, rode `/export` e confirme que o arquivo foi gerado.

Faça isso **agora**, não no Dia 2. Sem `docs/sessions/`, o critério de relatório vale zero — e já aconteceu de gente que fez tudo certo descobrir no último dia que não tinha registro nenhum do trabalho.

Exporte ao final de **cada** sessão, nomeando `docs/sessions/01-descricao-curta.md`, `02-...`, e assim por diante.

---

## O resumo em um parágrafo

Você vai receber uma política de reembolso escrita por um RH, com a redação ruim que uma política de RH real tem. Ela é ambígua em vários pontos, e você não tem acesso a ninguém para tirar dúvida. O trabalho não é implementar — é **especificar**: encontrar cada ambiguidade, decidir explicitamente, justificar e registrar. O produto funcionando vale **10 dos 100 pontos**. Os outros 90 estão na spec, na rastreabilidade `spec → tasks → commits → testes`, na resposta à mudança de requisito do Dia 2 e no relatório.

Isso é deliberado. Um projeto que roda perfeitamente com spec fraca tira nota baixa; um projeto com bug conhecido, spec impecável e trilha limpa tira nota alta.

# Motor de Cálculo de Reembolso

Motor de cálculo de reembolso desenvolvido a partir da Política de Reembolso v3.

A aplicação recebe um arquivo JSON com despesas de um colaborador, aplica as regras definidas na especificação e produz um arquivo JSON com o valor reembolsável e a justificativa de cada decisão.

## Requisitos

- Python 3.12 ou superior
- `pytest` para execução dos testes

## Criar ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Após a ativação, o terminal deve apresentar algo semelhante a:

```text
(.venv) PS C:\caminho\do\projeto>
```

## Instalar dependências de desenvolvimento

Com o ambiente virtual ativo:

```powershell
python -m pip install pytest
```

## Executar o motor

A interface da aplicação é:

```text
python -m src calcular --input <arquivo-entrada> --output <arquivo-saida>
```

Exemplo utilizando o arquivo fornecido pelo desafio:

```powershell
python -m src calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

O arquivo indicado em `--output` será criado contendo o resultado do cálculo.

## Executar os testes

Para executar toda a suíte:

```powershell
python -m pytest -q
```

Para executar um arquivo de testes específico:

```powershell
python -m pytest tests/test_cli.py -q
```

## Estrutura do projeto

```text
.
├── CLAUDE.md
├── README.md
├── exemplos/
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

## Documentação da especificação

A fonte de verdade para as regras de negócio é:

```text
specs/001-motor-reembolso/spec.md
```

O plano técnico está em:

```text
specs/001-motor-reembolso/plan.md
```

As tarefas e sua rastreabilidade estão em:

```text
specs/001-motor-reembolso/tasks.md
```

Mudanças posteriores à baseline são registradas em:

```text
specs/001-motor-reembolso/DECISIONS.md
```

## Interface de entrada

A entrada deve seguir o formato definido em:

```text
exemplos/despesas-exemplo.json
```

A operação obrigatória é:

```text
calcular
```

Os argumentos são:

- `--input`: caminho do JSON de entrada;
- `--output`: caminho do JSON de saída.

## Saída

A saída contém:

- identificação do colaborador;
- competência processada;
- resumo financeiro;
- uma decisão para cada despesa;
- valor solicitado;
- valor reembolsável;
- valor não reembolsável;
- status;
- motivos da decisão.

Os possíveis status são:

- `APROVADA`;
- `PARCIAL`;
- `RECUSADA`.

## Exemplo de execução

```powershell
python -m src calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

Depois, no PowerShell, o resultado pode ser visualizado com:

```powershell
Get-Content resultado.json
```

## Processo de desenvolvimento

O projeto segue uma abordagem orientada por especificação.

Mudanças de comportamento devem seguir a ordem:

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
```

Commits de implementação e testes referenciam a task correspondente, por exemplo:

```text
test(T-005): cobre obrigatoriedade de nota fiscal
feat(T-005): implementa exigencia de nota fiscal
```