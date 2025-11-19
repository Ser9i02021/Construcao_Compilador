from lexico import *
from dicionario_tabelall1 import *

"""
GRAMÁTICA EM LL(1):

PROGRAM -> STATEMENT | FUNCLIST | &
FUNCLIST -> FUNCDEF FUNCLIST'
FUNCLIST' -> FUNCDEF FUNCLIST' | &
FUNCDEF -> def ident(PARAMLIST){STATELIST}
PARAMLIST -> PARAMETRO PARAMLIST' | &
PARAMETRO -> int ident | float ident | string ident
PARAMLIST' -> , PARAMETRO PARAMLIST' | &
STATEMENT -> VARDECL; | ATRIBSTAT; | PRINTSTAT; | READSTAT; | RETURNSTAT; | IFSTAT; | FORSTAT; | {STATELIST} | break; | ;
VARDECL -> int ident CONSTANTE | float ident CONSTANTE | string ident CONSTANTE
CONSTANTE -> [const_inteiro] CONSTANTE | &
ATRIBSTAT -> LVALUE = ATRIBSTAT'
ATRIBSTAT' -> EXPRESSION | ALLOCEXPRESSION
FUNCCALL -> (PARAMLISTCALL)
PARAMLISTCALL -> ident PARAMLISTCALL' | &
PARAMLISTCALL' -> , ident PARAMLISTCALL' | &
PRINTSTAT -> print EXPRESSION
READSTAT -> read LVALUE
RETURNSTAT -> return
IFSTAT -> if( EXPRESSION ) STATEMENT IFSTAT'
IFSTAT' -> else STATEMENT | &
FORSTAT -> for(ATRIBSTAT; EXPRESSION; ATRIBSTAT) STATEMENT
STATELIST -> STATEMENT STATELIST | &
ALLOCEXPRESSION -> new TIPO [NUMEXPRESSION] ALLOCEXPRESSION'
TIPO -> int | float | string
ALLOCEXPRESSION' -> [NUMEXPRESSION] | &
EXPRESSION -> NUMEXPRESSION COMPARACAO
COMPARACAO -> < NUMEXPRESSION | > NUMEXPRESSION | <= NUMEXPRESSION | >= NUMEXPRESSION | == NUMEXPRESSION | != NUMEXPRESSION | &
NUMEXPRESSION -> TERM NUMEXPRESSION'
NUMEXPRESSION' -> + TERM NUMEXPRESSION' | - TERM NUMEXPRESSION' | &
TERM -> UNARYEXPR TERM'
TERM' -> * UNARYEXPR TERM' | / UNARYEXPR TERM' | % UNARYEXPR TERM' | &
UNARYEXPR -> OPERADORES FACTOR
OPERADORES -> + | - | &
FACTOR -> const_inteiro | const_float | const_string | null | (NUMEXPRESSION) | ident CHAMADA
CHAMADA -> FUNCCALL | LVALUE'
LVALUE -> ident LVALUE'
LVALUE' -> [NUMEXPRESSION] LVALUE' | &
"""

class Nodo:
    def __init__(self,token,pai):
        self.Token = token
        self.pai = pai
        self.filhos = []

def analisador_sintatico(tokens):
    tokens.append(Token("$","None",0,0))
    tabela_ll1 = dicionario()
    token_atual = 0
    pilha = ["PROGRAM"]

    terminais = ['!=', '%', '(', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==', '>', '>=', '[', ']', 'break', 'const_float', 'const_inteiro', 'const_string', 'def', 'else', 'float', 'for', 'ident', 'if', 'int', 'new', 'null', 'print', 'read', 'return', 'string', '{', '}']

    while True :
        if tokens[token_atual].tipo == "$" and len(pilha) == 0:
            print("Análise sintática ocorreu com sucesso!")
            break

        if len(pilha) == 0:
            tok = tokens[token_atual]
            raise Exception(
                f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                f"esperado '{pilha[-1]}', encontrado '{tok.tipo}'."
            )


        if pilha[-1] in terminais:
            if pilha[-1] == tokens[token_atual].tipo:
                pilha.pop()
                token_atual += 1
            else:
                tok = tokens[token_atual]
                raise Exception(
                    f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                    f"esperado '{pilha[-1]}', encontrado '{tok.tipo}'."
                )

        else:
            producao = tabela_ll1.get(pilha[-1], {}).get(tokens[token_atual].tipo)
            if producao:
                pilha.pop()
                for especifico in reversed(producao):
                    if especifico != "&":
                     pilha.append(especifico)
            else:
                tok = tokens[token_atual]
                raise Exception(
                    f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                    f"token inesperado '{tok.tipo}'."
                )

    return

