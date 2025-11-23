from lexico import *
from sintatico import *
from semantico import *

def entrada():
    codigo = """
def quebra_certa1(){
    int i;
    i = 0;
    for(i = 0; i < 10; i = i + 1) {
        break;
    }
}
"""
    return codigo

def token_para_string(lista):
    resultado = """"""

    linha_atual = 1

    for token in lista:
        if token.l != linha_atual:
            resultado += '\n'
            linha_atual = token.l
        resultado += token.__repr__() + " "

    return resultado

def main():
    codigo = entrada()
    tokens, tabela_simbolos = analisar(codigo)
    print("Tabela de Símbolos:")
    print(tabela_simbolos)
    print(token_para_string(tokens))

    analisador_sintatico(tokens)

    analisador_semantico(tokens, tabela_simbolos)

main()

