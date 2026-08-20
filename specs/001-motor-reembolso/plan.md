# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado na spec:** 2.0

> Esta versão evolui o plano técnico da baseline v3 para suportar a Política v4.
>
> Decisões técnicas da baseline permanecem válidas quando não forem explicitamente
> substituídas nesta versão. A mudança de comportamento está registrada em
> `DECISIONS.md`.

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

A solução continua dividida em blocos com responsabilidades separadas, mantendo o núcleo de regras de negócio independente da leitura e escrita de arquivos.

A Política v4 acrescenta duas novas entradas conceituais ao cálculo:

- política de reembolso parametrizada;
- cotações históricas de moedas.

O fluxo passa a ser:

```text
entrada principal JSON
        +
política v4
        +
cotações
        ↓
CLI / coordenação
        ↓
leitura e validação
        ↓
normalização
        ↓
seleção da política
        ↓
motor de cálculo
        ↓
conversão cambial quando necessária
        ↓
aplicação das regras
        ↓
montagem do resultado
        ↓
serialização
        ↓
arquivo JSON
```

### 2.1 CLI

A CLI continua responsável pela operação `calcular` e pela coordenação da execução.

A interface obrigatória permanece:

```text
calcular --input <entrada> --output <saida>
```

A forma concreta de disponibilização dos dados auxiliares da Política v4 deve preservar essa interface obrigatória.

A CLI não contém regras de negócio.

### 2.2 Leitura e validação

Responsável por:

- interpretar o JSON principal;
- verificar os campos obrigatórios;
- aceitar `moeda` como campo opcional;
- validar os dados auxiliares de política;
- validar os dados auxiliares de câmbio;
- distinguir erro estrutural de dado auxiliar de uma recusa individual de despesa.

Dados estruturalmente inválidos impedem o cálculo antes da execução do motor.

Ausência legítima de cotação para uma despesa não é erro estrutural; é tratada pelo motor conforme RN-021.

### 2.3 Normalização

Responsável por:

- normalização da categoria;
- normalização da moeda;
- normalização do valor original;
- conversão das datas;
- preservação do índice original da despesa.

A normalização não realiza decisões de elegibilidade.

Para moedas:

```text
campo ausente -> BRL
" usd "       -> USD
```

O valor original é normalizado antes de eventual conversão cambial.

### 2.4 Seleção da política

Antes da avaliação das despesas, o centro de custo do colaborador é utilizado para selecionar a configuração aplicável.

Fluxo:

```text
centro_custo
     ↓
existe política específica?
     ↓
 sim ─────────→ política específica
 não ─────────→ política padrao
```

A seleção é exata. Não há busca por prefixo ou similaridade.

O resultado da seleção é uma configuração imutável durante aquele cálculo.

### 2.5 Câmbio

A responsabilidade cambial fica separada das regras de limite.

Ela recebe conceitualmente:

```text
moeda
data da despesa
valor original normalizado
cotações
```

e produz:

```text
valor em BRL
```

ou a indicação de que não existe cotação utilizável.

Para moeda `BRL`, não há conversão.

Para moeda estrangeira:

1. procura cotação da mesma data;
2. se ausente, procura a mais recente anterior;
3. nunca utiliza cotação futura;
4. multiplica o valor original normalizado pela taxa;
5. normaliza o resultado para duas casas decimais.

A busca da cotação e a conversão permanecem independentes das regras de nota fiscal e limite.

### 2.6 Motor de cálculo de reembolso

O motor continua sendo o núcleo da aplicação.

Passa a receber:

- despesas normalizadas;
- período;
- política já selecionada;
- dados de câmbio preparados.

Para cada despesa, aplica a precedência definida na seção 8 da spec.

O motor coordena:

- categoria;
- competência;
- duplicidade;
- conversão cambial;
- valor não positivo;
- nota fiscal;
- limite da categoria;
- consumo do limite;
- valor reembolsável;
- status;
- motivos.

Não lê arquivos e não conhece caminhos da CLI.

### 2.7 Controle dos limites

Os limites deixam de ser constantes globais do código.

O motor consulta a política selecionada.

Para categorias com limite diário, o consumo continua identificado por:

```text
(data, categoria)
```

Somente valores efetivamente reembolsados aumentam o consumo.

Hospedagem continua sendo aplicada por lançamento/diária conforme a spec.

`representacao`, quando configurada como limite diário, utiliza o mesmo mecanismo de consumo por data e categoria.

Uma categoria presente com limite zero continua existindo na política; apenas não possui valor disponível.

### 2.8 Montagem do resultado

A montagem do resultado passa a preservar:

- `valor_original`;
- `moeda_original`;
- `valor_solicitado` em BRL;
- `valor_reembolsavel` em BRL;
- `valor_nao_reembolsavel` em BRL;
- status;
- motivos.

O resumo continua derivado exclusivamente das decisões individuais.

Todos os totais são expressos em BRL.

### 2.9 Serialização

A serialização produz o schema `"2.0"` definido na spec.

Valores monetários continuam sendo representados como texto decimal com duas casas.

Essa camada não executa conversão nem regras de política.

### Fronteiras

A separação arquitetural passa a ser:

```text
I/O / CLI
    ↓
validação e preparação
    ↓
política + câmbio
    ↓
motor de domínio
    ↓
resultado
    ↓
serialização
```

Política e câmbio são dados do cálculo, não regras codificadas na CLI.

O motor continua testável diretamente em memória.

## 3. Modelo de dados

O modelo interno representa separadamente dados originais, dados normalizados, política aplicável, câmbio e resultado.

### 3.1 Colaborador

Campos:

- `id`;
- `nome`;
- `centro_custo`.

Na v4, `centro_custo` participa da seleção da política.

### 3.2 Período

Campos:

- `competencia`;
- `inicio`;
- `fim`.

As datas utilizam representação própria para comparação cronológica.

### 3.3 Despesa de entrada

Campos:

- `id`;
- `data`;
- `categoria`;
- `descricao`;
- `fornecedor`;
- `valor`;
- `moeda`, opcional;
- `tem_nota_fiscal`.

Essa representação preserva exatamente os dados recebidos.

### 3.4 Despesa normalizada

Campos conceituais:

- `id`;
- `data`;
- `categoria_original`;
- `categoria_normalizada`;
- `descricao`;
- `fornecedor`;
- `valor_original`;
- `valor_original_normalizado`;
- `moeda_original`;
- `moeda_normalizada`;
- `tem_nota_fiscal`;
- `indice_entrada`.

Após conversão bem-sucedida, a avaliação também possui:

- `valor_brl`.

`valor_brl` não substitui `valor_original_normalizado`.

### 3.5 Política

Representa os dados externos da política.

Conceitualmente contém:

- configuração `padrao`;
- configurações por centro de custo;
- categorias;
- limites;
- parâmetros gerais.

O núcleo recebe a política já validada.

### 3.6 Política aplicável

Representa a configuração selecionada para um cálculo após RN-016.

Ela fornece ao motor:

```text
categoria -> configuração de limite
```

O motor não precisa saber se aquela configuração veio da política específica ou da política padrão depois da seleção.

### 3.7 Cotação

Representa uma taxa de conversão para BRL associada a:

```text
moeda + data -> taxa
```

As taxas são mantidas com sua precisão original em `Decimal`.

O arredondamento ocorre sobre o valor convertido, não sobre a taxa.

### 3.8 Motivo

Campos:

- `codigo`;
- `descricao`.

Além dos códigos da baseline, a v4 acrescenta:

```text
COTACAO_NAO_DISPONIVEL
```

Os códigos permanecem estáveis para testes e consumidores.

### 3.9 Resultado individual

Campos:

- `id`;
- `indice_entrada`;
- `valor_original`;
- `moeda_original`;
- `valor_solicitado`;
- `valor_reembolsavel`;
- `valor_nao_reembolsavel`;
- `status`;
- `motivos`.

Os três últimos valores financeiros são expressos em BRL conforme o contrato da spec.

### 3.10 Controle de limite diário

A chave continua:

```text
(data, categoria)
```

e o valor representa quanto já foi efetivamente reembolsado em BRL.

Exemplo:

```text
(2026-07-03, alimentacao) -> 90.00
(2026-07-03, representacao) -> 300.00
```

### 3.11 Controle de duplicidade

A identidade passa a ser:

```text
(
    data,
    categoria_normalizada,
    descricao,
    fornecedor,
    moeda_normalizada,
    valor_original_normalizado,
    tem_nota_fiscal
)
```

O `id` não participa.

O valor convertido para BRL também não participa.

### 3.12 Resumo

Campos:

- `total_solicitado`;
- `total_reembolsavel`;
- `total_nao_reembolsavel`.

Todos são expressos em BRL e derivados dos resultados individuais.

### 3.13 Resultado do cálculo

Contém:

- colaborador;
- período;
- resumo;
- resultados individuais.

### Fluxo dos dados

```text
entrada
  ↓
validação
  ↓
normalização
  ↓
seleção da política
  ↓
despesas normalizadas
  ↓
motor
  ├── duplicidade
  ├── câmbio
  ├── nota fiscal
  └── limites
  ↓
resultados individuais
  ↓
resumo
  ↓
schema 2.0
```

## 4. Como a política é representada

Na Política v4, a política de reembolso deixa de ser uma estrutura fixa embutida no sistema e passa a ser um dado externo fornecido ao cálculo.

A aplicação mantém uma representação interna validada da política recebida.

Conceitualmente:

```text
politica
├── padrao
│   └── categorias / limites
└── centros_custo
    ├── CC-A
    │   └── categorias / limites
    └── CC-B
        └── categorias / limites
```

A estrutura concreta deve refletir o formato recebido no envelope, sem criar parâmetros de negócio inexistentes na fonte.

### Seleção

A seleção ocorre uma vez por cálculo:

```text
colaborador.centro_custo
          ↓
configuração específica existe?
       ↙              ↘
     sim               não
      ↓                 ↓
específica            padrao
```

Depois da seleção, o motor trabalha apenas com a política aplicável.

### Limites

O motor não mantém:

```text
alimentacao = 60.00
transporte_urbano = 80.00
hospedagem = 250.00
```

como constantes universais.

Os valores são obtidos da política selecionada.

### Categorias

A existência de uma categoria também é determinada pela política.

Portanto:

```text
categoria ausente
```

é diferente de:

```text
categoria presente com limite 0.00
```

### Decisão substituída da baseline

Na baseline v3, a leitura de política externa foi deliberadamente descartada porque existia apenas uma política fixa.

A Política v4 invalida essa premissa.

A nova decisão é carregar e validar a política externa antes da execução do motor.

Essa mudança corresponde à D-001 em `DECISIONS.md`.

### Alternativa descartada — manter defaults da v3 no código

Não serão mantidos R$ 60,00, R$ 80,00 e R$ 250,00 como fallback silencioso.

**Motivo:** isso criaria uma segunda fonte de verdade e poderia mascarar política v4 ausente ou inválida.

### Alternativa descartada — motor consultar diretamente o JSON bruto

O motor não acessa diretamente a estrutura JSON original da política.

**Motivo:** isso acoplaria regras de negócio ao formato externo e espalharia parsing e validação pelo núcleo.

### Consequência

A arquitetura passa a separar:

```text
formato externo da política
          ↓
validação / preparação
          ↓
representação interna
          ↓
seleção
          ↓
motor
```

Isso permite testar o motor com diferentes políticas em memória sem alterar código de regra.

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

**Contexto:** A Política v4 torna limites e categorias parametrizáveis, mas a sequência e a semântica das regras continuam explicitamente definidas na spec.

**Decisão:** Manter um fluxo explícito de avaliação, sem criar rule engine genérico, DSL, sistema de plugins ou execução arbitrária de regras configuradas.

A política externa fornece dados de configuração, não código nem novas regras executáveis.

**Alternativa descartada:** Transformar cada regra em plugin ou expressão dinâmica carregada da política.

**Motivo da rejeição:** A v4 exige parametrização de dados, não uma linguagem dinâmica de regras. Um rule engine aumentaria a complexidade sem requisito correspondente.

**Consequência:** Limites e categorias podem variar por política, enquanto a ordem e a semântica de RN-001 a RN-025 permanecem explícitas e auditáveis.

---

### DT-012 — Política externa validada antes do motor

**Contexto:** A v4 depende de uma política externa para selecionar categorias e limites.

**Decisão:** Converter o documento externo em uma representação interna validada antes de iniciar o cálculo.

**Alternativa descartada:** Consultar o JSON bruto dentro de cada regra.

**Motivo da rejeição:** Misturaria parsing, validação e domínio.

**Consequência:** O motor trabalha com uma estrutura previsível e testes podem fornecer políticas diretamente em memória.

---

### DT-013 — Serviço de conversão cambial isolado

**Contexto:** Conversão de moeda possui busca temporal de cotação, multiplicação decimal e possibilidade de ausência de taxa.

**Decisão:** Isolar seleção de cotação e conversão em responsabilidade própria, independente dos limites e da nota fiscal.

**Alternativa descartada:** Implementar conversão diretamente dentro do fluxo de cada categoria.

**Motivo da rejeição:** Duplicaria comportamento e aumentaria risco de categorias utilizarem regras cambiais diferentes.

**Consequência:** Toda despesa estrangeira utiliza o mesmo mecanismo determinístico de conversão.

---

### DT-014 — Índice de cotações por moeda e data

**Contexto:** Para encontrar a cotação da mesma data ou a mais recente anterior, o sistema precisa consultar histórico por moeda.

**Decisão:** Preparar as cotações em uma estrutura agrupada por moeda e ordenada cronologicamente, permitindo selecionar a taxa aplicável sem misturar essa busca ao motor.

Conceitualmente:

```text
USD -> [
    (data_1, taxa_1),
    (data_2, taxa_2),
    ...
]
```

**Alternativa descartada:** Percorrer todo o documento bruto de câmbio para cada despesa.

**Motivo da rejeição:** Mistura parsing com regra temporal e repete trabalho desnecessariamente.

**Consequência:** A regra de fallback histórico fica concentrada e testável isoladamente.

---

### DT-015 — Preservar valor original e valor em BRL separadamente

**Contexto:** A v4 exige conversão sem perder rastreabilidade da informação recebida.

**Decisão:** Manter campos internos distintos para valor original normalizado e valor convertido em BRL.

**Alternativa descartada:** Sobrescrever o valor original após conversão.

**Motivo da rejeição:** Isso impediria auditar a conversão e quebraria a identidade de duplicidade definida na spec.

**Consequência:** O modelo possui mais campos, mas preserva claramente origem e resultado da transformação.

---

### DT-016 — Câmbio ausente como resultado de domínio, não exceção estrutural

**Contexto:** Uma moeda pode estar corretamente informada e ainda não possuir cotação utilizável.

**Decisão:** Diferenciar:

```text
dados de câmbio inválidos
```

de:

```text
cotação válida estruturalmente, porém inexistente para a despesa
```

O primeiro caso interrompe o cálculo como erro de entrada/configuração.

O segundo é devolvido ao motor como ausência de cotação e produz `COTACAO_NAO_DISPONIVEL`.

**Alternativa descartada:** Tratar ambos como a mesma exceção.

**Motivo da rejeição:** Confundiria falha estrutural com uma decisão de negócio prevista pela spec.

**Consequência:** Testes e mensagens de erro podem distinguir claramente os dois cenários.

---

## 6. Estratégia de testes

A estratégia de testes deve garantir que cada regra de negócio definida na `spec.md` possua pelo menos uma verificação automatizada e que as interações entre regras também sejam testadas.

A suíte será dividida em três níveis:

- testes unitários para regras e normalizações;
- testes de integração para o fluxo completo do motor;
- testes ponta a ponta para a interface CLI.

### 6.1 Testes unitários

Na Política v4, também devem ser cobertos:
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
- geração de status e motivos;
- normalização de moeda;
- seleção da política por centro de custo;
- fallback para política `padrao`;
- categorias e limites parametrizados;
- conversão para BRL;
- busca da cotação da mesma data;
- busca da última cotação anterior;
- ausência de cotação utilizável;
- duplicidade com moeda e valor originais;
- limite zero;
- categoria `representacao`;
- preservação de valor e moeda originais.

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
- fechamento dos totais do resumo;
- conversão antes da nota fiscal;
- falha cambial antes das regras monetárias posteriores;
- política específica produzindo limites diferentes da política padrão;
- despesa recusada por câmbio sem consumir limite;
- duplicidade detectada antes da conversão;
- `representacao` concorrendo por limite diário;
- categoria presente com limite zero;
- resumo combinando BRL e despesas estrangeiras convertidas.

O objetivo é verificar não apenas cada regra isoladamente, mas também a precedência definida na seção 8 da spec.

### 6.3 Testes ponta a ponta

Além do exemplo da baseline, deve existir teste ponta a ponta com os dados fornecidos no envelope da Política v4.

Esse teste deve exercitar política externa, câmbio e schema de saída `"2.0"`.
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

- um centavo abaixo, exatamente no limite e um centavo acima do limite configurado para cada categoria relevante;
- R$ 99,99, R$ 100,00 e R$ 100,01 para nota fiscal;
- conversão que resulte exatamente em R$ 100,00 e R$ 100,01;
- primeiro e último dia da competência;
- dia anterior e posterior à competência;
- valor original com mais de duas casas;
- valor convertido com mais de duas casas;
- valor zero e negativo;
- moeda ausente;
- moeda com diferenças de capitalização;
- cotação na mesma data;
- cotação somente em data anterior;
- cotação somente em data futura;
- moeda sem cotação;
- limite zero;
- categoria `representacao`;
- duplicatas em mesma moeda;
- despesas semelhantes em moedas diferentes;
- múltiplas despesas concorrendo pelo mesmo limite parametrizado.

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

### Riscos aceitos e limitações conhecidas

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

#### Dependência dos dados de política

Um arquivo de política incorreto pode produzir limites incorretos mesmo quando o motor estiver funcionando conforme especificado.

Esse risco é mitigado pela validação estrutural, mas a aplicação considera os valores fornecidos como fonte de verdade.

#### Dependência das cotações fornecidas

O motor não valida as taxas contra uma fonte externa.

Uma taxa incorreta no conjunto recebido produzirá conversão incorreta de forma determinística.

#### Cotação histórica ausente

Uma despesa pode ser recusada mesmo existindo uma cotação futura para sua moeda.

Esse risco é aceito porque a spec proíbe utilizar informação cambial posterior à data da despesa.

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