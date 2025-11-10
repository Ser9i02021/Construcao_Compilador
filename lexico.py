tabela_simbolos = [] # inicaliza a tabela de simbolos
linha = 1 # Controla a linha sendo verificada
coluna = 1 # Controla a coluna sendo verificada

class Token:
    def __init__(self,tipo,valor,l,c):
        self.tipo = tipo
        self.valor = valor
        self.l = l
        self.c = c

    def __repr__(self):
        if self.valor is not None:
            return f"{self.tipo},valor:{self.valor}"
        else:
            return f"{self.tipo}"


def adicionarsimbolo(valor):
    global tabela_simbolos

    for simbolos in tabela_simbolos:
        if simbolos == valor:
            return tabela_simbolos.index(simbolos)

    tabela_simbolos.append(valor)
    return tabela_simbolos.index(valor)


def determinar_token(lexema,posicao,c):

    palavras_reservadas = ["def","int","float","string","break","print","read","return","if","else","for","new","null"]

    afd = 0
    atual = 0

    while True:
        match afd:
            case 0:
                # comparaão e atribuição
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

                # operadores
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
                if lexema[atual] == '"':
                    afd = 23
                    atual += 1
                    continue
                if lexema[atual].isdigit():
                    afd = 24
                    atual += 1
                    continue
                if lexema[atual].isalpha() or lexema[atual] == '_':
                    afd = 26
                    atual += 1
                    continue
                if afd == 0:
                    afd = 29



            # TOKEN: =
            case 1:
                if len(lexema) == atual:
                    return Token("=",None,posicao,c)
                elif lexema[atual] == '=':
                    afd = 19
                    atual += 1
                    continue
                else:
                    afd = 29

            # TOKEN: !
            case 2:
                if lexema[atual] == '=':
                    afd = 20
                    atual += 1
                    continue
                else:
                    afd = 29


            # TOKEN: <
            case 3:
                if len(lexema) == atual:
                    return Token("<", None, posicao,c)
                elif lexema[atual] == '=':
                    afd = 21
                    atual += 1
                    continue
                else:
                    afd = 29

            # TOKEN: >
            case 4:
                if len(lexema) == atual:
                    return Token(">", None, posicao,c)
                elif lexema[atual] == '=':
                    afd = 22
                    atual += 1
                    continue
                else:
                    afd = 29


            # TOKEN: ADD
            case 6:
                return Token("+", None, posicao,c)

            # TOKEN: SUB
            case 7:
                return Token("-", None, posicao,c)

            # TOKEN: MULT
            case 8:
                return Token("*",None,posicao,c)

            # TOKEN: DIV
            case 9:
                return Token("/", None, posicao,c)

            # TOKEN: MOD
            case 10:
                return Token("%",None,posicao,c)

            # TOKEN: PAREN_E
            case 11:
                return Token("(", None, posicao,c)

            # TOKEN: PAREN_D
            case 12:
                return Token(")", None, posicao,c)

            # TOKEN: COLC_E
            case 13:
                return Token("[",None,posicao,c)

            # TOKEN: COLC_D
            case 14:
                return Token("]",None,posicao,c)

            # TOKEN: CHAVE_E
            case 15:
                return Token("{",None,posicao,c)

            # TOKEN: CHAVE_D
            case 16:
                return Token("}",None,posicao,c)

            # TOKEN: PONTO_VIRGULA
            case 17:
                return Token(";",None,posicao,c)

            # TOKEN: VIRGULA
            case 18:
                return Token(",",None,posicao,c)

            # TOKEN: =
            case 19:
                if len(lexema) == atual:
                    return Token("==",None,posicao,c)
                else:
                    afd = 29

            # TOKEN: =
            case 20:
                if len(lexema) == atual:
                    return Token("!=",None,posicao,c)
                else:
                    afd = 29

            # TOKEN: =
            case 21:
                if len(lexema) == atual:
                    return Token("<=", None, posicao,c)
                else:
                    afd = 29

            # TOKEN: =
            case 22:
                if len(lexema) == atual:
                    return Token(">=", None, posicao,c)
                else:
                    afd = 29

            # TOKEN: CONSTANTE STRING
            case 23:
                if lexema[atual] == '"':
                    return Token("const_string", lexema.strip('"'), posicao,c)
                else:
                    atual += 1

            # TOKEN: NUMERO (vai decidir se é inteiro ou não)
            case 24:
                if len(lexema) == atual:
                    return Token("const_inteiro", lexema, posicao,c)
                elif lexema[atual] == '.':
                    atual += 1
                    afd = 25
                elif lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # TOKEN: FLOAT
            case 25:
                if len(lexema) == atual:
                    afd = 29
                elif lexema[atual].isdigit():
                    atual += 1
                    afd = 28
                else:
                    afd = 29

            # TOKEN: LETRA
            case 26:
                if len(lexema) == atual:
                    return Token("ident", adicionarsimbolo(lexema), posicao,c)
                elif lexema[atual].isalpha() or lexema[atual] == '_' or lexema[atual].isdigit():
                    afd = 27
                    atual += 1
                else:
                    afd = 29

            # TOKEN: IDENTIFICADOR
            case 27:
                if len(lexema) == atual:
                    if lexema in palavras_reservadas:
                        return Token(lexema, None, posicao,c)
                    return Token("ident", adicionarsimbolo(lexema), posicao,c)
                elif lexema[atual].isalpha() or lexema[atual] == '_' or lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # TOKEN: FLOAT
            case 28:
                if len(lexema) == atual:
                    return Token("const_float", lexema, posicao,c)
                elif lexema[atual].isdigit():
                    atual += 1
                else:
                    afd = 29

            # TOKEN: SITUAÇÃO DE ERRO
            case 29:
                raise Exception("Token não reconhecido pela gramática na linha " + str(posicao) + " coluna " + str(c) + ": " + lexema + ". Tente novamente!")


def analisar(codigo):
    tokens = [] # inicializa a lista de tokens
    global linha, coluna, tabela_simbolos
    linha = 1
    coluna = 1
    posicao = 0 # Controla a posicao sendo verificada
    simbolo = "+-*/%=(){},!<>[];" # operadores que irão concluir um lexema
    tabela_simbolos = []
    lexema = ""

    while posicao < len(codigo):
        char = codigo[posicao]

        # caso exista uma quebra de linha (aumenta "linha" em 1)
        if char == '\n':
            linha += 1
            coluna = 1
            posicao += 1
            continue

        # caso seja um espaço (conclui o lexema)
        elif char.isspace():
            if lexema:
                tokens.append(determinar_token(lexema,linha,coluna))
                lexema = ""
            posicao += 1
            coluna += 1

        # caso seja um simbolo (conclui o lexema, além de processar o simbolo)
        elif char in simbolo:
            if lexema:
                tokens.append(determinar_token(lexema,linha,coluna))
                lexema = ""
            if char == '<' or char == '>' or char == '=' or char == '!':
                char_1 = codigo[posicao + 1]
                if char_1 == '<' or char_1 == '>' or char_1 == '=' or char_1 == '!':
                    token_1 = codigo[posicao] + codigo[posicao + 1]
                    tokens.append(determinar_token(token_1, linha,coluna))
                    posicao += 2
                    coluna += 2
                else:
                    tokens.append(determinar_token(char, linha,coluna))
                    posicao += 1
                    coluna += 1
            else:
                tokens.append(determinar_token(char, linha,coluna))
                posicao += 1

        # caso seja um " (indicando inicio de String), deve gerar o token inteiro dentro de um loop
        elif char == '"':
            if lexema:
                tokens.append(determinar_token(lexema, linha,coluna))
            lexema = ""
            while True:
                lexema += codigo[posicao]
                posicao += 1
                coluna += 1
                if codigo[posicao] == '"':
                    lexema += codigo[posicao]
                    posicao += 1
                    coluna += 1
                    break

            tokens.append(determinar_token(lexema, linha,coluna))
            lexema = ""

        else:
            lexema += codigo[posicao]
            posicao += 1
            coluna += 1

    return tokens