# Alunos: Gustavo Russi, Leonardo Vilain Martins, Maria Fernanda Bittelbrunn Toniasso 
#         e Sergio Bonini

from lexico import *
from sintatico import *
from semantico import *
from intermediario import *

import sys

# ---------------------------------------------------------------------
# Programas de teste internos
# ---------------------------------------------------------------------
# Este dicionário agrupa pequenos programas ConvCC-2025-2 usados para
# testar rapidamente o analisador léxico/sintático/semântico.
#
# ATENÇÃO: vários desses programas possuem erros propositalmente
# (semânticos ou de escopo) para verificar se o compilador detecta
# corretamente as situações inválidas.
TEST_PROGRAMAS = {
    "leonardo": """
def leonardo(float teste, int teste){
    break;
    leonardo = 10;
    int teste;
    leonardo = teste[1];
    string leonardo[10];
    leonardo = teste / leonardo;
    leonardo = teste();
    teste = new string [5];
    if(leonardo() > 10) break;
}
""",

    "main_parametros": """
def main(int a, float b){
    int x;
    x = a + 10;
    print x;
}
""",

    "f_param_repetido": """
def f(int x, float x){
    return;
}
""",

    "test_sombra_tipo": """
def test(){
    int x;
    float x;
}
""",

    "sombra": """
def sombra(){
    int x;
    x = 1;
    {
        float x;
        x = 2.5;
        print x;
    }
    print x;
}
""",

    "usa_nao_declarado": """
def usa_nao_declarado(){
    x = 10;
}
""",

    "tipos_expr": """
def tipos_expr(){
    int a;
    float b;
    a = 1;
    b = 2.0;
    a = a + b;
}
""",

    "tipos_atribuicao": """
def tipos_atribuicao(){
    int a;
    string s;
    s = "ola";
    a = s;
}
""",

    "quebra_errado": """
def quebra_errado(){
    break;
}
""",

    "quebra_certa1": """
def quebra_certa1(){
    int i;
    i = 0;
    for(i = 0; i < 10; i = i + 1)
        break;
}
""",

    "quebra_certa2": """
def quebra_certa2(){
    int i;
    i = 0;
    for(i = 0; i < 10; i = i + 1){
        if(i > 5) break;
    }
}
""",

    "f_sobrecarga": """
def f(int a){
    return;
}

def f(float a){
    return;
}
"""
}


def ler_codigo():
    """
    Lê o código-fonte que será analisado.

    Modos de uso:
      python main.py programa.conv
      python main.py --test NOME_TESTE

    - Se for passado '--test NOME_TESTE', o código é obtido a partir
      do dicionário TEST_PROGRAMAS.
    - Caso contrário, o primeiro argumento é interpretado como o caminho
      de um arquivo .conv a ser aberto.
    """
    # Modo de execução com testes internos
    if len(sys.argv) >= 2 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Uso: python main.py --test NOME_TESTE")
            print("Testes disponíveis:", ", ".join(sorted(TEST_PROGRAMAS.keys())))
            sys.exit(1)

        nome_teste = sys.argv[2]
        prog = TEST_PROGRAMAS.get(nome_teste)
        if prog is None:
            print(f"Teste '{nome_teste}' não encontrado.")
            print("Testes disponíveis:", ", ".join(sorted(TEST_PROGRAMAS.keys())))
            sys.exit(1)

        print(f"=== Executando teste interno: {nome_teste} ===")
        return prog

    # Modo normal: leitura de um arquivo .conv
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py <arquivo-fonte.conv>")
        print("  python main.py --test NOME_TESTE")
        sys.exit(1)

    caminho = sys.argv[1]
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            codigo = f.read()
    except OSError as e:
        print(f"Erro ao abrir arquivo '{caminho}': {e}")
        sys.exit(1)

    return codigo


def token_para_string(lista):
    """
    Converte a lista de tokens em uma string organizada por linhas.

    Cada linha do programa de entrada é impressa em uma linha separada,
    com os tokens correspondentes na ordem em que foram reconhecidos.
    Essa função é usada apenas para depuração e visualização.
    """
    resultado = ""
    linha_atual = 1

    for token in lista:
        # Quebra de linha sempre que o número da linha mudar
        if token.l != linha_atual:
            resultado += "\n"
            linha_atual = token.l
        resultado += token.__repr__() + " "

    return resultado


def main():
    """
    Função principal: coordena todas as fases do compilador.

    1. Lê o código-fonte (arquivo .conv ou teste interno).
    2. Executa o analisador léxico, exibindo tabela de símbolos e tokens.
    3. Executa o analisador sintático.
    4. Executa o analisador semântico.
    5. Gera o código intermediário em três endereços.
    """
    codigo = ler_codigo()

    # Análise léxica
    tokens, tabela_simbolos = analisar(codigo)
    print("Tabela de Símbolos:")
    print(tabela_simbolos)
    print(token_para_string(tokens))

    # Análise sintática
    analisador_sintatico(tokens)

    # Análise semântica
    escopo_por_token = analisador_semantico(tokens, tabela_simbolos)

    # Geração de código intermediário
    analisador_intermediario(tokens, tabela_simbolos, escopo_por_token)


if __name__ == "__main__":
    try:
        # Fluxo principal de compilação:
        #  - análise léxica
        #  - análise sintática
        #  - análise semântica
        #  - geração de código intermediário
        main()
    except SemanticError as e:
        # Erros detectados pela análise semântica (tipos, escopos, break, etc.)
        print("Erro semântico na compilação:")
        print(e)
        sys.exit(1)
    except Exception as e:
        # Demais erros de compilação (léxicos, sintáticos, I/O, etc.)
        # As mensagens geradas nesses pontos já incluem linha e coluna.
        print("Erro na compilação:")
        print(e)
        sys.exit(1)

