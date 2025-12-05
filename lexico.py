# -----------------------------------------------------------------------------
# lexico.py
#
# Analisador léxico da linguagem ConvCC-2025-2.
# Responsável por transformar o código-fonte (string) em uma lista de tokens,
# além de construir a tabela de símbolos com identificadores.
# -----------------------------------------------------------------------------

# Tabela de símbolos global:
# cada entrada é uma lista [lexema, (linha,coluna), (linha,coluna), ...]
tabela_simbolos = []  # Inicializa a tabela de símbolos

# Controle global de posição no código (apenas para o analisador léxico)
linha = 1  # Linha atual
coluna = 1  # Coluna atual


class Token:
    """
    Representa um token léxico da linguagem.

    Atributos:
        tipo  : string que identifica o tipo do token (e.g. "ident", "const_inteiro", "if", "+", ";")
        valor : para constantes, é o lexema; para identificadores, é o índice na tabela de símbolos;
                para palavras reservadas ou símbolos simples, costuma ser None.
        l     : número da linha em que o token aparece (1-based)
        c     : número da coluna (aproximada) em que o lexema do token começa (1-based)
    """

    def __init__(self, tipo, valor, l, c):
        self.tipo = tipo
        self.valor = valor
        self.l = l
        self.c = c

    def __repr__(self):
        """
        Forma compacta de impressão de tokens, usada para debug.
        Exemplo: "ident,valor:3" ou "const_inteiro,valor:10" ou apenas "if".
        """
        if self.valor is not None:
            return f"{self.tipo},valor:{self.valor}"
        else:
            return f"{self.tipo}"


def adicionarsimbolo(valor, linha, coluna):
    """
    Insere um identificador na tabela de símbolos, ou reutiliza a entrada existente.

    Parâmetros:
        valor  : lexema do identificador (string)
        linha  : linha em que o identificador aparece
        coluna : coluna em que o identificador começa

    Retorna:
        índice do identificador na tabela de símbolos (int)
    """
    global tabela_simbolos

    # Procura se o lexema já está na tabela de símbolos
    for simbolos in tabela_simbolos:
        if simbolos[0] == valor:
            simbolos.append((linha, coluna))
            return tabela_simbolos.index(simbolos)

    # Se ainda não existe, adiciona nova entrada
    tabela_simbolos.append([valor, (linha, coluna)])
    return tabela_simbolos.index([valor, (linha, coluna)])


def determinar_token(lexema, posicao, c):
    """
    Dado um lexema (string) e a posição de início (linha = posicao, coluna = c),
    classifica o lexema em um token da linguagem utilizando um AFD (autômato finito
    determinístico implementado com o comando match/case).

    Pode retornar tokens de:
      - Operadores: =, ==, !=, <, <=, >, >=, +, -, *, /, %
      - Delimitadores: (), [], {}, ;, ,
      - Constantes: inteiras, floats, strings
      - Identificadores e palavras reservadas

    Em caso de erro, levanta uma Exception com mensagem indicando linha, coluna e lexema.
    """

    # Palavras reservadas da linguagem
    palavras_reservadas = [
        "def", "int", "float", "string", "break", "print", "read",
        "return", "if", "else", "for", "new", "null"
    ]

    afd = 0        # estado atual do autômato
    atual = 0      # índice do caractere atual dentro de 'lexema'

    while True:
        match afd:
            # -----------------------------------------------------------------
            # Estado inicial: decide que tipo de lexema está começando
            # -----------------------------------------------------------------
            case 0:
                # comparação e atribuição
                if lexema[atual] == '=':
                    afd = 1
                    atual += 1
                    continue

                if lexema[atual] == '!':
                    afd = 2
                    atual += 1
                    continue

                if lexema[atual] == '<':
                    afd = 3
                    atual += 1
                    continue

                if lexema[atual] == '>':
                    afd = 4
                    atual += 1
                    continue

                # operadores aritméticos
                if lexema[atual] == '+':
                    afd = 6
                    atual += 1
                    continue
                if lexema[atual] == '-':
                    afd = 7
                    atual += 1
                    continue
                if lexema[atual] == '*':
                    afd = 8
                    atual += 1
                    continue
                if lexema[atual] == '/':
                    afd = 9
                    atual += 1
                    continue
                if lexema[atual] == '%':
                    afd = 10
                    atual += 1
                    continue

                # delimitadores
                if lexema[atual] == '(':
                    afd = 11
                    atual += 1
                    continue
                if lexema[atual] == ')':
                    afd = 12
                    atual += 1
                    continue
                if lexema[atual] == '[':
                    afd = 13
                    atual += 1
                    continue
                if lexema[atual] == ']':
                    afd = 14
                    atual += 1
                    continue
                if lexema[atual] == '{':
                    afd = 15
                    atual += 1
                    continue
                if lexema[atual] == '}':
                    afd = 16
                    atual += 1
                    continue
                if lexema[atual] == ';':
                    afd = 17
                    atual += 1
                    continue
                if lexema[atual] == ',':
                    afd = 18
                    atual += 1
                    continue

                # início de string (entre aspas)
                if lexema[atual] == '"':
                    afd = 23
                    atual += 1
                    continue

                # início de número
                if lexema[atual].isdigit():
                    afd = 24
                    atual += 1
                    continue

                # início de identificador (ou palavra reservada)
                if lexema[atual].isalpha() or lexema[atual] == '_':
                    afd = 26
                    atual += 1
                    continue

                # Se chegou aqui sem casar nada, vai para o estado de erro
                if afd == 0:
                    afd = 29

            # -----------------------------------------------------------------
            # = ou ==
            # -----------------------------------------------------------------
            case 1:
                if len(lexema) == atual:
                    return Token("=", None, posicao, c)
                elif lexema[atual] == '=':
                    afd = 19
                    atual += 1
                    continue
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # !=
            # -----------------------------------------------------------------
            case 2:
                if lexema[atual] == '=':
                    afd = 20
                    atual += 1
                    continue
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # < ou <=
            # -----------------------------------------------------------------
            case 3:
                if len(lexema) == atual:
                    return Token("<", None, posicao, c)
                elif lexema[atual] == '=':
                    afd = 21
                    atual += 1
                    continue
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # > ou >=
            # -----------------------------------------------------------------
            case 4:
                if len(lexema) == atual:
                    return Token(">", None, posicao, c)
                elif lexema[atual] == '=':
                    afd = 22
                    atual += 1
                    continue
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Operadores aritméticos e delimitadores simples
            # -----------------------------------------------------------------
            case 6:
                return Token("+", None, posicao, c)

            case 7:
                return Token("-", None, posicao, c)

            case 8:
                return Token("*", None, posicao, c)

            case 9:
                return Token("/", None, posicao, c)

            case 10:
                return Token("%", None, posicao, c)

            case 11:
                return Token("(", None, posicao, c)

            case 12:
                return Token(")", None, posicao, c)

            case 13:
                return Token("[", None, posicao, c)

            case 14:
                return Token("]", None, posicao, c)

            case 15:
                return Token("{", None, posicao, c)

            case 16:
                return Token("}", None, posicao, c)

            case 17:
                return Token(";", None, posicao, c)

            case 18:
                return Token(",", None, posicao, c)

            # -----------------------------------------------------------------
            # ==, !=, <=, >=
            # -----------------------------------------------------------------
            case 19:
                if len(lexema) == atual:
                    return Token("==", None, posicao, c)
                else:
                    afd = 29

            case 20:
                if len(lexema) == atual:
                    return Token("!=", None, posicao, c)
                else:
                    afd = 29

            case 21:
                if len(lexema) == atual:
                    return Token("<=", None, posicao, c)
                else:
                    afd = 29

            case 22:
                if len(lexema) == atual:
                    return Token(">=", None, posicao, c)
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Constante string: " ... "
            # lexema chega com as aspas incluídas, ex: "\"ola\""
            # -----------------------------------------------------------------
            case 23:
                if lexema[atual] == '"':
                    # strip('"') remove as duas aspas da ponta
                    return Token("const_string", lexema.strip('"'), posicao, c)
                else:
                    atual += 1

            # -----------------------------------------------------------------
            # Números: estado 24 decide se é inteiro ou se vira float
            # -----------------------------------------------------------------
            case 24:
                if len(lexema) == atual:
                    return Token("const_inteiro", lexema, posicao, c)
                elif lexema[atual] == '.':
                    atual += 1
                    afd = 25
                elif lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Parte fracionária do float: exige pelo menos um dígito após o ponto
            # -----------------------------------------------------------------
            case 25:
                if len(lexema) == atual:
                    afd = 29
                elif lexema[atual].isdigit():
                    atual += 1
                    afd = 28
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Início de identificador ou palavra reservada
            # -----------------------------------------------------------------
            case 26:
                if len(lexema) == atual:
                    # um único caractere já fecha o lexema
                    return Token("ident", adicionarsimbolo(lexema, posicao, c), posicao, c)
                elif lexema[atual].isalpha() or lexema[atual] == '_' or lexema[atual].isdigit():
                    afd = 27
                    atual += 1
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Identificador (lexema >= 2 chars); checa se é palavra reservada
            # -----------------------------------------------------------------
            case 27:
                if len(lexema) == atual:
                    if lexema in palavras_reservadas:
                        return Token(lexema, None, posicao, c)
                    return Token("ident", adicionarsimbolo(lexema, posicao, c), posicao, c)
                elif lexema[atual].isalpha() or lexema[atual] == '_' or lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Parte final do float (após pelo menos 1 dígito na parte fracionária)
            # -----------------------------------------------------------------
            case 28:
                if len(lexema) == atual:
                    return Token("const_float", lexema, posicao, c)
                elif lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # -----------------------------------------------------------------
            # Estado de erro genérico
            # -----------------------------------------------------------------
            case 29:
                raise Exception(
                    "Token não reconhecido pela gramática na linha "
                    + str(posicao)
                    + " coluna "
                    + str(c)
                    + ": "
                    + lexema
                    + ". Tente novamente!"
                )


def analisar(codigo):
    """
    Função principal do analisador léxico.

    Parâmetros:
        codigo : string com o código-fonte completo em ConvCC-2025-2.

    Retorna:
        (tokens, tabela_simbolos_atualizada)

        tokens           : lista de objetos Token, na ordem em que aparecem
        tabela_simbolos  : lista global contendo os identificadores encontrados
                           e as posições (linha, coluna) de cada ocorrência.
    """
    tokens = []  # Lista de tokens produzidos
    global linha, coluna, tabela_simbolos

    # Reinicia estado global a cada análise
    linha = 1
    coluna = 1
    tabela_simbolos = []

    posicao = 0  # Índice atual no string 'codigo'

    # Conjunto de símbolos que delimitam lexemas
    simbolo = "+-*/%=(){},!<>[];"

    lexema = ""                 # Buffer para o lexema em construção
    coluna_inicio_lexema = None  # Coluna onde o lexema atual começou

    while posicao < len(codigo):
        char = codigo[posicao]

        # -------------------------------------------------------------
        # Quebra de linha: atualiza linha/coluna e reseta o lexema
        # -------------------------------------------------------------
        if char == '\n':
            linha += 1
            coluna = 1
            posicao += 1
            lexema = ""
            coluna_inicio_lexema = None
            continue

        # -------------------------------------------------------------
        # Espaço em branco: encerra o lexema atual, se houver
        # -------------------------------------------------------------
        elif char.isspace():
            if lexema:
                tokens.append(determinar_token(lexema, linha, coluna_inicio_lexema))
                lexema = ""
                coluna_inicio_lexema = None
            posicao += 1
            coluna += 1

        # -------------------------------------------------------------
        # Símbolos que, por si só, formam tokens (operadores/delimitadores)
        # Também encerram qualquer lexema em andamento.
        # -------------------------------------------------------------
        elif char in simbolo:
            if lexema:
                tokens.append(determinar_token(lexema, linha, coluna_inicio_lexema))
                lexema = ""
                coluna_inicio_lexema = None

            # Trata pares como "==", "<=", ">=", "!="
            if char in "<>!=":
                if posicao + 1 < len(codigo) and codigo[posicao + 1] in "<>!=":
                    token_1 = codigo[posicao] + codigo[posicao + 1]
                    tokens.append(determinar_token(token_1, linha, coluna))
                    posicao += 2
                    coluna += 2
                else:
                    tokens.append(determinar_token(char, linha, coluna))
                    posicao += 1
                    coluna += 1
            else:
                tokens.append(determinar_token(char, linha, coluna))
                posicao += 1
                coluna += 1

        # -------------------------------------------------------------
        # Início de string: lê até a próxima aspa dupla
        # -------------------------------------------------------------
        elif char == '"':
            if lexema:
                tokens.append(determinar_token(lexema, linha, coluna_inicio_lexema))
            lexema = ""
            coluna_inicio_lexema = None

            # Inclui as aspas no lexema para que determinar_token reconheça
            while True:
                lexema += codigo[posicao]
                posicao += 1
                coluna += 1
                if codigo[posicao] == '"':
                    lexema += codigo[posicao]
                    posicao += 1
                    coluna += 1
                    break

            tokens.append(determinar_token(lexema, linha, coluna))
            lexema = ""
            coluna_inicio_lexema = None

        # -------------------------------------------------------------
        # Qualquer outro caractere: faz parte de um lexema em construção
        # (identificador, número, etc.)
        # -------------------------------------------------------------
        else:
            if lexema == "":
                coluna_inicio_lexema = coluna
            lexema += codigo[posicao]
            posicao += 1
            coluna += 1

    # Fim do código: se restou um lexema pendente, processa-o
    if lexema:
        tokens.append(determinar_token(lexema, linha, coluna_inicio_lexema))

    return tokens, tabela_simbolos
