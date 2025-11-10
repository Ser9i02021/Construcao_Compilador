from lexico import *
from sintatico import *

def entrada():
    codigo = """
    def leonardo(float teste, int teste){
    break;
    leonardo = 10;
    int teste;
    leonardo = teste[1];
    string leonardo[10];
    leonardo = teste / leonardo;
    leonardo = teste();
    teste = new string [5];
    if(leonardo() > 10) break;;
    }
    """
    return codigo

def token_para_string(lista):
    resultado = """"""

    linha_atual = 1

    for token in lista:
        if token.l is not linha_atual:
            resultado += '\n'
            linha_atual = token.l
        resultado += token.__repr__() + " "

    return resultado

def main():
    codigo = entrada()
    tokens = analisar(codigo)
    print(token_para_string(tokens))
    print("O código é reconhecido pela gramática!")

    analisador_sintatico(tokens)

main()

