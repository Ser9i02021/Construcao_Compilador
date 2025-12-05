================================================================================
EXERCÍCIO PROGRAMA: COMPILADOR
Disciplina de Construção de Compiladores (INE5426)
Semestre: 2025/2
Curso de Ciências da Computação
Professor: Alvaro Junio Pereira Franco
Data: 05/12/2025
================================================================================

1. GRUPO
--------------------------------------------------------------------------------
Grupo 8
Alunos: Maria Fernanda Bittelbrunn Toniasso, Gustavo Russi, Sergio Bonini e
Leonardo Vilain Martins

2. DESCRIÇÃO
--------------------------------------------------------------------------------
Este trabalho implementa um compilador para a linguagem ConvCC-2025-2 capaz de:

- realizar análise léxica, produzindo uma lista de tokens e uma tabela de símbolos;
- realizar análise sintática utilizando uma gramática LL(1);
- realizar análise semântica, verificando:
  - tipos das expressões aritméticas;
  - declarações e usos de variáveis por escopo;
  - uso correto de break apenas dentro de laços for;
- gerar código intermediário de três endereços, seguindo o formato apresentado em aula.

Em caso de sucesso em todas as fases, o compilador produz as saídas abaixo (todas no terminal), conforme exigido na Seção 8 do enunciado:

1. uma árvore de expressão para cada expressão aritmética relevante do programa (atribuições, print, condições de if e de for), impressa em pré-ordem;
2. uma tabela de símbolos com o tipo associado a cada identificador;
3. uma mensagem de sucesso indicando que as expressões aritméticas são válidas quanto a tipos;
4. uma mensagem de sucesso indicando que as declarações de variáveis por escopo são válidas;
5. uma mensagem de sucesso indicando que todos os comandos break estão no escopo de um for;
6. o código intermediário correspondente à entrada.

Em caso de erro (léxico, sintático ou semântico), o compilador interrompe o processo na primeira ocorrência e exibe uma mensagem de insucesso indicando o tipo de erro, bem como linha e coluna onde ele ocorreu.

3. LINGUAGEM
--------------------------------------------------------------------------------
O compilador foi implementado em Python 3.10 (ou superior).

Não foram utilizadas bibliotecas externas específicas para construção de compiladores (como ANTLR), conforme instrução do professor. Todo o analisador (léxico, sintático, semântico) e o gerador de código intermediário foram implementados “na mão”.

4. ESTRUTURA DO CÓDIGO
--------------------------------------------------------------------------------
O projeto está organizado em múltiplos arquivos Python, separando as fases do compilador para facilitar desenvolvimento, depuração e leitura do código:

- main.py
  - Ponto de entrada do compilador.
  - Lê o arquivo fonte (ou um programa de teste interno), chama o analisador léxico, sintático, semântico e o gerador de código intermediário.
  - Centraliza o tratamento de erros, exibindo mensagens amigáveis em caso de falha.

- lexico.py
  - Implementa o analisador léxico, baseado em um AFD, que transforma o código-fonte em uma sequência de tokens.
  - Mantém e atualiza a tabela de símbolos léxica, registrando cada identificador com suas posições de ocorrência.
  - Define a classe Token.

- sintatico.py
  - Implementa o analisador sintático LL(1).
  - Utiliza a tabela precomputada de parsing armazenada em dicionario_tabelall1.py.
  - Em caso de erro sintático, informa a linha, coluna e o token inesperado/esperado.

- dicionario_tabelall1.py
  - Contém o dicionário que representa a tabela LL(1) (não é mostrado aqui, mas está incluído no projeto).

- semantico.py
  - Implementa a análise semântica em duas passadas:
    1. Processa declarações, escopos (global, funções, blocos) e comandos for/break, verificando redeclarações, uso fora de escopo e break fora de laço.
    2. Processa as expressões aritméticas, construindo árvores de expressão e verificando compatibilidade de tipos.
  - Define as classes auxiliares Escopo, SimboloSemantico, ExprNode e a exceção SemanticError.
  - Ao final, imprime a tabela de símbolos enriquecida com os tipos e mensagens de sucesso (itens 3, 4 e 5 da Seção 8).

- intermediario.py
  - Recebe a lista de tokens, a tabela de símbolos e a informação de escopo por token.
  - Percorre o programa e gera o código intermediário de três endereços, usando temporários (t0, t1, ...) e rótulos (L0, L1, ...).
  - Trata atribuições, print, if/else, laços for com break e chamadas de função.

Além destes, há o diretório programas/, contendo os programas de teste principais, e o Makefile que automatiza a execução.

5. GRAMÁTICA
--------------------------------------------------------------------------------
Foi utilizada a gramática em BNF fornecida pelo professor, sem alterações.

A gramática em forma LL(1) foi construída a partir dessa BNF e está codificada na estrutura de dados utilizada pelo analisador sintático (dicionario_tabelall1.py).

No arquivo sintatico.py há comentários documentando:

- a gramática utilizada em alto nível;
- como as produções são mapeadas para a tabela LL(1).

As SDTs e SDDs utilizadas foram incorporadas principalmente nos módulos semântico e intermediário, responsáveis por:

- construir as árvores de expressão;
- verificar tipos;
- associar identificadores a tipos e escopos;
- gerar o código intermediário correspondente.

6. COMO EXECUTAR
--------------------------------------------------------------------------------

Requisitos

- Python 3.10 ou superior instalado e acessível como python3.
- Estar no diretório raíz do projeto (onde se encontra o Makefile).

Programas principais (programas/programa1.conv, programa2.conv, programa3.conv)

O Makefile automatiza a execução do compilador para os três programas obrigatórios (cada um com pelo menos 100 linhas) localizados em programas/:

- Alvo padrão (roda os 3 em sequência):

  make

- Rodar somente um dos programas:

  make p1   # roda em programas/programa1.conv
  make p2   # roda em programas/programa2.conv
  make p3   # roda em programas/programa3.conv

- Rodar em qualquer outro arquivo .conv:

  make run ARQ=programas/outro_prog.conv

Programas de teste internos (casos menores com ou sem erros)

O compilador também inclui alguns programas de teste internos (pequenos), úteis para testar casos específicos de erro semântico (uso de variável não declarada, tipos incompatíveis, break fora de for, etc.).

Eles podem ser executados via Makefile com o alvo test:

  make test T=leonardo
  make test T=usa_nao_declarado
  make test T=tipos_expr
  ...

Onde T é o nome de uma chave do dicionário TEST_PROGRAMAS definido em main.py (por exemplo: leonardo, usa_nao_declarado, tipos_expr, quebra_errado, etc.).

Também é possível chamá-los diretamente, sem make:

  python3 main.py --test usa_nao_declarado
  python3 main.py programas/programa1.conv

Comportamento em sucesso e erro

- Se houver erro léxico, sintático ou semântico, o compilador:
  - interrompe imediatamente a execução na primeira ocorrência;
  - exibe uma mensagem no terminal indicando o tipo de erro, a linha e a coluna.

- Se não houver erros, o compilador exibe, nesta ordem:
  1. a tabela de símbolos léxica e a lista de tokens;
  2. a confirmação de sucesso da análise sintática;
  3. árvores das expressões aritméticas (impressas em pré-ordem), com mensagens indicando em que contexto foram geradas (atribuição, print, condição de if/for);
  4. mensagens de sucesso da análise semântica (tipos, escopos, break);
  5. a tabela de símbolos enriquecida com tipos;
  6. o código intermediário de três endereços para o programa.

7. ARQUIVOS ENTREGUES
--------------------------------------------------------------------------------

- Conjunto de arquivos .py que implementam o compilador:
  - main.py, lexico.py, sintatico.py, semantico.py, intermediario.py, dicionario_tabelall1.py, entre outros auxiliares.
- Três programas de teste principais em ConvCC-2025-2, cada qual com pelo menos 100 linhas:
  - programas/programa1.conv
  - programas/programa2.conv
  - programas/programa3.conv
- Makefile para facilitar a execução das fases do compilador e geração do código intermediário.

8. CONSIDERAÇÕES FINAIS
--------------------------------------------------------------------------------
O desenvolvimento deste compilador envolveu diversas etapas (léxico, sintático, semântico e código intermediário) e demandou um esforço significativo de projeto e depuração.

A separação em módulos (lexico.py, sintatico.py, semantico.py, intermediario.py) foi importante para:

- isolar responsabilidades;
- facilitar o teste de cada fase;
- tornar o código mais legível para futuros desenvolvedores.

Houve desafios especialmente na:

- adaptação da gramática para a forma LL(1);
- implementação correta dos escopos e da verificação de tipos;
- geração de código intermediário com controle de fluxo (if, for, break).

Ao final, o compilador atende aos itens especificados na Seção 8 do enunciado:

- gera árvores de expressão em pré-ordem para as expressões aritméticas;
- produz tabela de símbolos com tipos;
- verifica declarações e usos de variáveis por escopo;
- verifica o uso adequado de break dentro de for;
- gera código intermediário de três endereços;
- e, em caso de erro, informa claramente ao usuário o que ocorreu e onde, interrompendo o processo na primeira falha.

Embora sempre haja espaço para melhorias e extensões, o grupo entende que o objetivo proposto pelo exercício-programa foi atingido de forma satisfatória.
