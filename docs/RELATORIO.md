# Relatório — Desafio SDD

**Aluno:** `Victoria Krupp` · **Repositório:** `https://github.com/Kruppvick/sdd-desafio/tree/main` · **Data:** `20/08/26`

> Isto não é redação. São **evidências**. Toda afirmação deve vir acompanhada de
> arquivo, hash de commit ou trecho de sessão exportada. Um parágrafo bonito sem
> evidência vale menos que uma frase curta com um hash.
>
> Vale 20 dos 100 pontos, e é a seção que mais separa notas.

---

## Delegação

## Delegação

A divisão de trabalho buscou manter comigo as decisões e verificações e utilizar o assistente como apoio para estruturar especificação, testes, implementação incremental e revisão.

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Eu + assistente | O assistente ajudou a levantar casos; eu confrontei as propostas com a política, exemplos e comportamento esperado. |
| Decidir as ambiguidades | Eu, com apoio do assistente | As decisões alteravam o comportamento do produto e precisavam ser explicitamente aceitas antes da implementação. |
| Escrever a spec | Eu + assistente | O assistente ajudou a estruturar a redação; eu revisei e incorporei as decisões ao repositório. |
| Desenhar a arquitetura | Eu + assistente | A arquitetura foi discutida a partir da spec e revisada quando o envelope v4 invalidou premissas da baseline. |
| Implementar | Eu + assistente | O assistente propôs alterações incrementais e eu apliquei, executei e corrigi no repositório local. |
| Escrever testes | Eu + assistente | Os testes foram propostos junto das tasks e executados localmente antes de aceitar cada mudança. |
| Absorver o envelope | Eu + assistente | Primeiro atualizei spec, decisões, tasks e plano; somente depois alterei testes e implementação. |

**Onde deleguei e me arrependi:**

Em alguns momentos aceitei sugestões de alteração de arquivos sem antes confrontá-las com o conteúdo completo existente. Um exemplo ocorreu em `DECISIONS.md`: a inclusão inicial da D-001 substituiu parte do conteúdo histórico em vez de apenas acrescentar a nova decisão. O problema foi detectado durante a revisão de `git diff` e o conteúdo anterior foi recuperado antes do commit.

Outro exemplo ocorreu durante a integração da Política v4 na CLI. Uma edição parcial deixou blocos com indentação incorreta e dados de política/câmbio fora da função `executar_calculo`. A correção foi feita substituindo o arquivo de forma controlada e executando novamente a suíte.

**Onde não deleguei e deveria ter delegado:**

Deleguei praticamente toda a produção inicial de spec, testes e código ao assistente. Meu papel ficou principalmente em aplicar as mudanças, executar os testes, trazer os resultados de volta e decidir quando algo precisava ser corrigido.

**Usei subagentes / skills / MCP / hooks?**

Não usei.

---

---

## Descrição

Um exemplo de requisito ambíguo que precisou ser transformado em comportamento verificável foi o limite diário.

**Versão inicial da política:**

> "Alimentação tem limite de R$ 60 por dia."

Essa redação não esclarecia se R$ 60,00 era um limite individual por lançamento ou um limite compartilhado entre todas as despesas de alimentação da mesma data.

**Versão final da decisão:**

> O limite de alimentação definido pela política aplicável é compartilhado por todas as despesas elegíveis de alimentação da mesma data.

Na Política v4, a decisão foi preservada, mas o valor deixou de ser uma constante universal: o limite passou a ser obtido da política aplicável ao centro de custo.

**O que estava ambíguo:**

A expressão "por dia" não definia explicitamente como múltiplos lançamentos deveriam consumir o limite. Na v4 surgiu ainda uma segunda dimensão: o próprio valor do limite passou a variar conforme a política selecionada.

**Como percebi:**

Ao percorrer casos com mais de uma despesa na mesma data, não era possível determinar um único resultado correto sem tomar uma decisão sobre compartilhamento e ordem de consumo. Essa decisão posteriormente permitiu testar explicitamente despesas concorrendo pelo mesmo limite.

**Evidência:**

- `specs/001-motor-reembolso/spec.md` — RN-001, RN-014 e AMB-001.
- `specs/001-motor-reembolso/tasks.md` — T-006 e T-017.
- testes do limite diário no diretório `tests/`.

**Commit da evolução v4:** consulte o commit `docs(spec): evolui especificacao para politica v4` no histórico Git.

---

### Caso 1 — preservação do histórico em DECISIONS.md

**O que o assistente propôs:**

Adicionar a decisão D-001 ao `DECISIONS.md`. Durante a edição, a nova decisão acabou ocupando o lugar de parte do conteúdo introdutório existente.

**Por que estava errado:**

`DECISIONS.md` existe justamente para preservar a evolução da especificação. Apagar a explicação da baseline enquanto se registrava a evolução para v4 enfraqueceria a própria trilha histórica que o desafio avalia.

**Como eu detectei:**

Revisei:

```powershell
git diff -- specs/001-motor-reembolso/DECISIONS.md
```

O diff mostrou linhas antigas sendo removidas, em vez de apenas uma nova decisão sendo acrescentada.

**O que eu fiz:**

Consultei a versão anterior com Git, recuperei o conteúdo da baseline, preservei o template de decisões e inseri a D-001 depois do histórico existente. Só depois disso o arquivo foi commitado.

**Onde está a evidência:**

- `specs/001-motor-reembolso/DECISIONS.md`;
- histórico Git do arquivo;


### Caso 2 — integração da CLI

**Padrão que eu notei:**

Alterações grandes ou feitas sem considerar o arquivo completo tinham maior chance de introduzir problemas de estrutura, especialmente indentação e integração entre componentes.

Na integração da v4, uma edição de `src/cli.py` deixou a preparação de política e câmbio fora do escopo correto da função. Ao revisar o arquivo completo antes de executar o envelope, o problema ficou evidente e o arquivo foi corrigido.

Isso reforçou a necessidade de combinar sugestões do assistente com inspeção do código real e execução dos testes.

---

**Onde está a evidência:**

- `specs/001-motor-reembolso/DECISIONS.md`;
- histórico Git do arquivo;
- não houve export de sessão preservado em `docs/sessions/`; a evidência disponível está no histórico Git e nos diffs do repositório.

## Diligência

**Meu procedimento de verificação:**

O fluxo utilizado durante a implementação foi, em geral:

```text
requisito da spec
    ↓
teste da task
    ↓
execução do teste específico
    ↓
implementação mínima
    ↓
execução do teste específico
    ↓
python -m pytest -q
    ↓
git status / git diff
    ↓
commit referenciando a task
```

Durante a evolução v4 também executei manualmente os dois arquivos de despesas fornecidos no envelope e conferi os resultados produzidos.

**Li o diff inteiro em que porcentagem das entregas?**

Sinceramente, confiei na IA. Poucas foram as vezes que percebi o erro, refiz o prompt e enviei. Por não usar nenhuma IA atrelada ao vscode, acabei fazendo tudo via chat. 

**O que aceitei sem verificar direito, e o que me custou:**

A alteração inicial de `DECISIONS.md` é um exemplo concreto. A edição precisou ser refeita porque a primeira versão não preservava todo o conteúdo anterior.

Também houve uma edição intermediária incorreta de `src/cli.py`, detectada antes do commit final da integração.

**Testes: quem escreveu, e como sei que testam a coisa certa?**

Os testes foram construídos com apoio do assistente, mas foram executados incrementalmente contra requisitos identificados por RN e task.

A suíte não foi utilizada apenas como confirmação posterior. Em várias tasks, o teste foi criado antes da implementação correspondente.

Além disso, a Política v4 foi validada em três níveis:

- testes unitários de política, moeda, câmbio e duplicidade;
- testes de integração do motor;
- testes ponta a ponta executando a CLI contra os arquivos reais do envelope.

A baseline v3 também permaneceu na suíte, permitindo detectar regressões durante a evolução.

---

## O envelope

A Política v4 alterou duas premissas arquiteturais importantes da baseline:

```text
política fixa
    ↓
política externa por centro de custo

valores somente em BRL
    ↓
valores em múltiplas moedas
```

**Quantos arquivos toquei na mão:** Não medi.

**Quanto tempo levou:** N/A

**Diff de absorção:** **Diff de absorção:** `30 arquivos, +4541/-921 linhas` (`git diff b482b11 HEAD --shortstat`)

Não medi durante a execução e não consigo reconstruir esse número com segurança.

### Absorveu de graça

Algumas decisões da baseline facilitaram a mudança:

- uso de `Decimal` para valores monetários;
- normalização separada das regras de negócio;
- motor independente da leitura/escrita de arquivos;
- regras de limite isoladas;
- consumo de limites baseado apenas no valor efetivamente reembolsado;
- preservação da ordem original das despesas;
- resumo derivado das decisões individuais;
- motivos representados por códigos estáveis.

Por isso, a introdução de `representacao`, por exemplo, aproveitou o mecanismo já existente de limite diário. Os testes mostraram que a categoria passou a compartilhar limite sem exigir uma reescrita completa do motor.

### Resistiu

A baseline tinha duas decisões que a v4 invalidou diretamente:

1. limites de R$ 60,00, R$ 80,00 e R$ 250,00 estavam representados como configuração fixa;
2. a leitura de política externa havia sido considerada complexidade desnecessária porque a v3 possuía uma política única.

A v4 tornou política externa um requisito obrigatório.

Também foi necessário separar:

```text
valor original + moeda original
```

de:

```text
valor considerado em BRL
```

porque a duplicidade usa o primeiro conjunto, enquanto nota fiscal, limites e totais usam o segundo.

### Ordem em que fiz

A mudança foi absorvida seguindo:

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
    ↓
teste ponta a ponta
```

A decisão principal da mudança está registrada como D-001.

### Se eu tivesse escrito a spec original sabendo desta mudança

Eu teria separado desde o início "regra" de "parâmetro".

Por exemplo, a regra poderia ter sido desde a baseline:

> despesas de alimentação compartilham o limite diário definido pela política aplicável.

Em vez de acoplar a descrição da regra ao valor concreto de R$ 60,00.

Também teria modelado desde o início a origem monetária da despesa separadamente do valor utilizado para aplicação da política.

### O que a spec me poupou, em concreto

A spec tornou possível identificar exatamente quais decisões continuavam válidas e quais haviam sido invalidadas.

Por exemplo:

- "limite diário compartilhado" continuou válido;
- "R$ 60,00 é o limite universal" deixou de ser válido.

Isso evitou tratar a v4 como uma reimplementação completa.

A precedência documentada também ajudou a decidir que:

- duplicidade utiliza valor e moeda originais;
- conversão ocorre antes da nota fiscal;
- falha cambial ocorre antes das regras monetárias posteriores;
- despesas recusadas por falha cambial não consomem limite.

---

## Evidências da Política v4

### Política específica

`CC-COMERCIAL` utiliza sua configuração própria, incluindo:

```text
alimentacao = 90
transporte_urbano = 150
hospedagem = 400
representacao = 300
```

Evidência:

- `exemplos/envelope/politica-v4.json`;
- `tests/test_cli_v4.py`.

### Política padrão

`CC-SUPORTE-N2` não existe na tabela e utiliza `padrao`.

No teste ponta a ponta:

```text
f-001 -> 58.00 reembolsável
f-002 -> 250.00 reembolsável
f-003 -> recusada, representação ausente
f-004 -> 65.76 reembolsável após conversão de USD
```

Evidência:

- `exemplos/envelope/despesas-envelope-cc-desconhecido.json`;
- `tests/test_cli_v4.py`.

### Câmbio

O cenário principal comprovou:

- EUR com cotação da mesma data;
- EUR em sábado utilizando a última cotação anterior;
- USD convertido antes da regra de nota fiscal;
- GBP recusada por ausência de cotação.

Evidência:

- `src/cambio.py`;
- `tests/test_cambio.py`;
- `tests/test_motor_cambio.py`;
- `tests/test_cli_v4.py`.

### Contrato de saída

A Política v4 utiliza:

```json
"schema_version": "2.0"
```

e preserva:

```text
valor_original
moeda_original
valor_solicitado em BRL
valor_reembolsavel em BRL
valor_nao_reembolsavel em BRL
```

Evidência:

- seção 4 de `spec.md`;
- `src/cli.py`;
- `tests/test_cli_v4.py`.

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**

Para um projeto em que regras de negócio possuem ambiguidades, interações e consequências financeiras, a abordagem mostrou valor mesmo com uma implementação relativamente pequena.

A maior vantagem não foi produzir mais documentação, mas conseguir responder perguntas como:

```text
por que o sistema faz isso?
qual decisão autorizou esse comportamento?
qual teste prova essa regra?
qual mudança invalidou a decisão anterior?
```

**Para qual não valeria?**

Provavelmente seria excessivo aplicar o mesmo nível de formalidade a uma automação descartável, sem regras ambíguas, baixo impacto e vida útil curta.

Mesmo nesses casos, testes e uma descrição mínima do comportamento ainda poderiam ser úteis, mas não necessariamente toda a estrutura de spec, decisions, plan e rastreabilidade utilizada neste desafio.

**O que eu faria diferente:**

- distinguiria parâmetros de regras já na primeira versão;
- verificaria o conteúdo completo do arquivo antes de aceitar substituições grandes;
- faria checkpoints menores de `git diff`;
- prepararia a estrutura `docs/sessions/` desde o primeiro dia;
- manteria desde o início valor monetário original separado do valor usado pelo domínio.

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**

O assistente consegue produzir rapidamente uma solução que parece coerente localmente, mas isso não significa que ela respeite o histórico do repositório ou todas as decisões anteriores.

Os problemas mais relevantes deste trabalho não apareceram porque o código era sintaticamente difícil. Eles apareceram nas fronteiras entre contexto, especificação, arquivos existentes e mudanças incrementais.

O ganho real veio quando passei a tratar a saída da IA como uma proposta que precisava ser confrontada com diff, testes, exemplos e histórico, e não como a próxima versão automaticamente correta do projeto.