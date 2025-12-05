from lexico import *
from dicionario_tabelall1 import *

def analisador_sintatico(tokens):
    """
    Implementa um analisador sintático preditivo LL(1) baseado em tabela.

    Entrada:
        tokens: lista de objetos Token produzidos pelo analisador léxico.

    Comportamento:
        - Usa uma pilha de símbolos (terminais e não-terminais);
        - Consulta a tabela LL(1) (dicionário em dicionario_tabelall1.py);
        - Em caso de erro, lança Exception com mensagem clara de linha/coluna;
        - Em caso de sucesso, imprime "Análise sintática ocorreu com sucesso!".

    Saída:
        Nenhuma estrutura é retornada (reconhecimento apenas). Em caso de erro,
        uma exceção é lançada.
    """

    # Adiciona símbolo de fim de entrada na lista de tokens
    tokens.append(Token("$", "None", 0, 0))

    # Carrega tabela LL(1) (não-terminais x terminais -> produção)
    tabela_ll1 = dicionario()

    # Índice do token atual na lista
    token_atual = 0

    # Pilha de análise: começa com o símbolo inicial da gramática
    pilha = ["PROGRAM"]

    # Conjunto de terminais conhecidos pela gramática
    terminais = [
        '!=', '%', '(', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==',
        '>', '>=', '[', ']', 'break', 'const_float', 'const_inteiro',
        'const_string', 'def', 'else', 'float', 'for', 'ident', 'if', 'int',
        'new', 'null', 'print', 'read', 'return', 'string', '{', '}'
    ]

    while True:
        # Caso de sucesso: esgotou a pilha e chegou ao fim da entrada
        if tokens[token_atual].tipo == "$" and len(pilha) == 0:
            print("Análise sintática ocorreu com sucesso!")
            break

        # Se a pilha acabou, mas ainda há tokens, temos erro
        if len(pilha) == 0:
            tok = tokens[token_atual]
            raise Exception(
                f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                f"token inesperado '{tok.tipo}' após fim da análise."
            )

        topo = pilha[-1]
        lookahead = tokens[token_atual].tipo

        # ---------------------------------------------------------------------
        # Caso 1: o topo da pilha é um terminal
        #         -> deve casar exatamente com o token corrente.
        # ---------------------------------------------------------------------
        if topo in terminais:
            if topo == lookahead:
                # Consome o terminal e avança no input
                pilha.pop()
                token_atual += 1
            else:
                tok = tokens[token_atual]
                raise Exception(
                    f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                    f"esperado '{topo}', encontrado '{tok.tipo}'."
                )

        # ---------------------------------------------------------------------
        # Caso 2: o topo da pilha é um não-terminal
        #         -> consulta a tabela LL(1) para decidir qual produção usar.
        # ---------------------------------------------------------------------
        else:
            producao = tabela_ll1.get(topo, {}).get(lookahead)

            if producao:
                # Remove o não-terminal do topo
                pilha.pop()

                # Empilha a produção correspondente em ordem reversa
                # (pois a pilha é LIFO)
                for simbolo in reversed(producao):
                    if simbolo != "&":  # & representa epsilon (produção vazia)
                        pilha.append(simbolo)
            else:
                tok = tokens[token_atual]
                raise Exception(
                    f"Erro sintático na linha {tok.l}, coluna {tok.c}: "
                    f"token inesperado '{tok.tipo}'."
                )

    return
