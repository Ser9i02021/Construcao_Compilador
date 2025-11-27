from lexico import *
from sintatico import *
from semantico import *
from intermediario import *

def entrada():
    codigo = """
def main(int a, float b){
    int x;
    x = a + 10;
    print x;
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

    escopo_por_token = analisador_semantico(tokens, tabela_simbolos)

    analisador_intermediario(tokens, tabela_simbolos, escopo_por_token)

main()

