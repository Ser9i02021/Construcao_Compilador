# semantico.py

from lexico import tabela_simbolos, Token

class SemanticError(Exception):
    pass

class SimboloSemantico:
    def __init__(self, nome, tipo, categoria, escopo, linha_decl, coluna_decl):
        self.nome = nome           # string
        self.tipo = tipo           # 'int', 'float', 'string' ou None
        self.categoria = categoria # 'var', 'param', 'func'
        self.escopo = escopo       # referência para Escopo
        self.linha_decl = linha_decl
        self.coluna_decl = coluna_decl

    def __repr__(self):
        return f"{self.categoria} {self.tipo} {self.nome} (decl @ {self.linha_decl},{self.coluna_decl})"


class Escopo:
    def __init__(self, nome, pai=None, tipo="bloco"):
        self.nome = nome
        self.pai = pai
        self.tipo = tipo           # 'global', 'func', 'bloco'
        self.simbolos = {}         # nome -> SimboloSemantico

    def contem(self, nome):
        return nome in self.simbolos

    def procura(self, nome):
        esc = self
        while esc is not None:
            if nome in esc.simbolos:
                return esc.simbolos[nome]
            esc = esc.pai
        return None



def escopo_atual(pilha_escopos):
    return pilha_escopos[-1]


def declara_variavel(nome, tipo, token_ident, pilha_escopos):
    escopo = escopo_atual(pilha_escopos)
    if escopo.contem(nome):
        raise SemanticError(
            f"Redeclaração de variável '{nome}' no mesmo escopo "
            f"(linha {token_ident.l}, coluna {token_ident.c})"
        )
    escopo.simbolos[nome] = SimboloSemantico(
        nome, tipo, "var", escopo, token_ident.l, token_ident.c
    )


def declara_funcao(nome, token_ident, pilha_escopos):
    global_escopo = pilha_escopos[0]
    if global_escopo.contem(nome):
        raise SemanticError(
            f"Redeclaração de função/identificador '{nome}' no escopo global "
            f"(linha {token_ident.l}, coluna {token_ident.c})"
        )
    global_escopo.simbolos[nome] = SimboloSemantico(
        nome, None, "func", global_escopo, token_ident.l, token_ident.c
    )




def analisador_semantico(tokens, tabela_simbolos):
    # criar escopo global
    escopo_global = Escopo("global", None, "global")
    pilha_escopos = [escopo_global]

    # para ponto 5 (break em for)
    pilha_loops = []  # empilha True quando entra em um 'for'

    # dicionário auxiliar: indice da tabela_simbolos -> tipo
    tipos_por_indice = {}

    # 1ª passada: inserir tipos e verificar escopo / break
    processar_declaracoes_e_escopos(
        tokens, tabela_simbolos, pilha_escopos, pilha_loops, tipos_por_indice
    )

    # (depois) 2ª passada: construir árvores de expressão e checar tipos
    # processar_expressoes(tokens, tabela_simbolos, escopo_global, tipos_por_indice)

    print("Análise semântica concluída com sucesso!")
    print("Tabela de símbolos com tipos (por índice do léxico):")
    for idx, tipo in tipos_por_indice.items():
        nome = tabela_simbolos[idx][0]
        print(f"{idx}: {nome} : {tipo}")


def processar_declaracoes_e_escopos(tokens, tabela_simbolos,
                                    pilha_escopos, pilha_loops,
                                    tipos_por_indice):
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]

        # 1) Início de função: def ident ( ... ) { ...
        if tok.tipo == "def" and i + 1 < n and tokens[i+1].tipo == "ident":
            ident_tok = tokens[i+1]
            idx_ts = ident_tok.valor
            nome = tabela_simbolos[idx_ts][0]

            declara_funcao(nome, ident_tok, pilha_escopos)

            # cria escopo da função e empilha
            escopo_func = Escopo(f"func_{nome}", pilha_escopos[-1], "func")
            pilha_escopos.append(escopo_func)

            # tratar parâmetros da função: (TIPO ident, ...)
            # vamos avançar até o ')'
            j = i + 2
            # espera encontrar '('
            while j < n and tokens[j].tipo != "(":
                j += 1
            j += 1  # pula '('

            while j < n and tokens[j].tipo != ")":
                if tokens[j].tipo in ("int", "float", "string") and j + 1 < n and tokens[j+1].tipo == "ident":
                    tipo = tokens[j].tipo
                    ident_param = tokens[j+1]
                    idx_param = ident_param.valor
                    nome_param = tabela_simbolos[idx_param][0]

                    # declara parâmetro como variável no escopo da função
                    declara_variavel(nome_param, tipo, ident_param, pilha_escopos)
                    tipos_por_indice[idx_param] = tipo
                    j += 2
                else:
                    j += 1

            i = j  # continua a partir do ')'
            continue

        # 2) Abre escopo de bloco
        if tok.tipo == "{":
            novo = Escopo(f"bloco_{tok.l}_{tok.c}", pilha_escopos[-1], "bloco")
            pilha_escopos.append(novo)

        # 3) Fecha escopo
        elif tok.tipo == "}":
            # se estamos saindo do escopo de função, só desempilha
            pilha_escopos.pop()

        # 4) Declaração de variável: TIPO ident ...
        elif tok.tipo in ("int", "float", "string") and i + 1 < n and tokens[i+1].tipo == "ident":
            tipo = tok.tipo
            ident_tok = tokens[i+1]
            idx_ts = ident_tok.valor
            nome = tabela_simbolos[idx_ts][0]

            declara_variavel(nome, tipo, ident_tok, pilha_escopos)
            tipos_por_indice[idx_ts] = tipo

            # aqui não precisamos consumir tudo da produção VARDECL,
            # só garantir que o ident está declarado. O parser já garantiu a forma correta.
            i += 1  # pulamos o ident

        # 5) Controle de laços 'for' (para Ponto 5 – break em escopo de 'for')
        elif tok.tipo == "for":
            pilha_loops.append(True)

        # Heurística simples: se vemos ';' logo depois de um for(...),
        # o corpo pode ser um statement simples. Para ficar mais robusto,
        # idealmente usamos informação da árvore sintática.
        elif tok.tipo == "break":
            if not pilha_loops:
                raise SemanticError(
                    f"Comando 'break' fora de laço de repetição na linha {tok.l}, coluna {tok.c}"
                )

        # se encontrar '}' e o token anterior pertencia a um 'for', poderíamos desempilhar pilha_loops
        # mas isso exige acompanhar melhor a estrutura do for. Pode ser refinado depois.

        i += 1



class ExprNode:
    def __init__(self, op, left=None, right=None, valor=None, tipo=None):
        """
        op: '+', '-', '*', '/', '%', 'id', 'int', 'float', 'string', 'null', 'cmp', etc.
        left, right: filhos
        valor: para folhas (nome do ident, valor literal, operador de comparação)
        tipo: tipo inferido da expressão ('int', 'float', 'string')
        """
        self.op = op
        self.left = left
        self.right = right
        self.valor = valor
        self.tipo = tipo

    def __repr__(self):
        if self.left or self.right:
            return f"({self.op} {self.left} {self.right})"
        else:
            return f"{self.valor if self.valor is not None else self.op}"

def print_preordem(node):
    if node is None:
        return
    # raiz
    if node.valor is not None:
        print(node.valor, end=" ")
    else:
        print(node.op, end=" ")
    # esquerda
    print_preordem(node.left)
    # direita
    print_preordem(node.right)




# Cada função recebe tokens e índice inicial, e devolve (node, proximo_indice)

def parse_expression(tokens, i, tabela_simbolos, escopo):
    node, i = parse_numexpression(tokens, i, tabela_simbolos, escopo)
    # COMPARACAO opcional
    if i < len(tokens) and tokens[i].tipo in ("<", ">", "<=", ">=", "==", "!="):
        op = tokens[i].tipo
        i += 1
        right, i = parse_numexpression(tokens, i, tabela_simbolos, escopo)
        #node = ExprNode(op, node, right, valor=op)
        node = combinar_binario(op, node, right)
        # tipo da comparação pode ser, por exemplo, 'bool',
        # mas para o EP basta garantir que os operandos de numexpression têm tipos compatíveis
    return node, i


def parse_numexpression(tokens, i, tabela_simbolos, escopo):
    node, i = parse_term(tokens, i, tabela_simbolos, escopo)
    while i < len(tokens) and tokens[i].tipo in ("+", "-"):
        op = tokens[i].tipo
        i += 1
        right, i = parse_term(tokens, i, tabela_simbolos, escopo)
        #node = ExprNode(op, node, right, valor=op)
        node = combinar_binario(op, node, right)
    return node, i


def parse_term(tokens, i, tabela_simbolos, escopo):
    node, i = parse_unaryexpr(tokens, i, tabela_simbolos, escopo)
    while i < len(tokens) and tokens[i].tipo in ("*", "/", "%"):
        op = tokens[i].tipo
        i += 1
        right, i = parse_unaryexpr(tokens, i, tabela_simbolos, escopo)
        #node = ExprNode(op, node, right, valor=op)
        node = combinar_binario(op, node, right)
    return node, i


def parse_unaryexpr(tokens, i, tabela_simbolos, escopo):
    # OPERADORES -> + | - | &
    if tokens[i].tipo in ("+", "-"):
        op = tokens[i].tipo
        i += 1
        factor, i = parse_factor(tokens, i, tabela_simbolos, escopo)
        node = ExprNode("unary" + op, factor, None, valor=op)
    else:
        node, i = parse_factor(tokens, i, tabela_simbolos, escopo)
    return node, i

def parse_factor(tokens, i, tabela_simbolos, escopo):
    tok = tokens[i]

    # literais
    if tok.tipo == "const_inteiro":
        node = ExprNode("int", None, None, valor=tok.valor)
        node.tipo = "int"
        return node, i + 1

    if tok.tipo == "const_float":
        node = ExprNode("float", None, None, valor=tok.valor)
        node.tipo = "float"
        return node, i + 1

    if tok.tipo == "const_string":
        node = ExprNode("string", None, None, valor=tok.valor)
        node.tipo = "string"
        return node, i + 1

    if tok.tipo == "null":
        node = ExprNode("null", None, None, valor="null")
        node.tipo = None   # ou um tipo especial
        return node, i + 1

    # ( NUMEXPRESSION )
    if tok.tipo == "(":
        node, j = parse_numexpression(tokens, i+1, tabela_simbolos, escopo)
        if tokens[j].tipo != ")":
            raise SemanticError(
                f"Parêntese ')' esperado na linha {tokens[j].l}, coluna {tokens[j].c}"
            )
        return node, j+1

    # ident CHAMADA / LVALUE
    if tok.tipo == "ident":
        idx_ts = tok.valor
        nome = tabela_simbolos[idx_ts][0]
        simbolo = escopo.procura(nome)
        if simbolo is None:
            raise SemanticError(
                f"Uso de identificador '{nome}' não declarado "
                f"(linha {tok.l}, coluna {tok.c})"
            )

        node = ExprNode("id", None, None, valor=nome)
        node.tipo = simbolo.tipo
        i = i + 1

        # Para simplificar agora, vamos ignorar CHAMADA (função) e índices [ ] na árvore.
        # Se quiser ser bem fiel à gramática, basta estender daqui.
        return node, i

    raise SemanticError(
        f"Token inesperado em fator: {tok.tipo} (linha {tok.l}, coluna {tok.c})"
    )



def combinar_binario(op, left, right):
    if left.tipo != right.tipo:
        raise SemanticError(
            f"Operação '{op}' com tipos incompatíveis: {left.tipo} e {right.tipo}"
        )
    node = ExprNode(op, left, right, valor=op)
    node.tipo = left.tipo
    return node



def processar_expressoes(tokens, tabela_simbolos, escopo_global, tipos_por_indice):
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]

        # padrão: LVALUE = EXPRESSION ;
        if tok.tipo == "ident":
            # tenta achar '=' logo depois de um possível LVALUE
            j = i + 1
            # pula possíveis [ ... ] do LVALUE
            while j < n and tokens[j].tipo == "[":
                # pula [ NUMEXPRESSION ]
                # aqui seria bom usar o mesmo parser de expressão para pular adequadamente
                j += 1
                while j < n and tokens[j].tipo != "]":
                    j += 1
                j += 1  # pula ']'

            if j < n and tokens[j].tipo == "=":
                # aqui temos uma atribuição
                idx_ts = tok.valor
                nome = tabela_simbolos[idx_ts][0]
                simbolo = escopo_global.procura(nome)
                if simbolo is None:
                    raise SemanticError(
                        f"Variável '{nome}' não declarada na atribuição "
                        f"(linha {tok.l}, coluna {tok.c})"
                    )

                # expressão vai de j+1 até o ';'
                k = j + 1
                while k < n and tokens[k].tipo != ";":
                    k += 1
                if k >= n:
                    raise SemanticError("';' esperado ao final de atribuição")

                # parse da expressão no intervalo [j+1, k)
                expr_tokens = tokens[j+1:k]
                # cria um escopo atual (aqui usei global, mas idealmente você passa o escopo certo)
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_global)

                # type checking: tipo da expressão deve bater com tipo da variável
                if node.tipo is not None and simbolo.tipo is not None and node.tipo != simbolo.tipo:
                    raise SemanticError(
                        f"Tipo da expressão ({node.tipo}) incompatível com variável '{nome}' "
                        f"de tipo {simbolo.tipo} (linha {tok.l}, coluna {tok.c})"
                    )

                # imprimir árvore em pré-ordem
                print(f"Árvore de expressão para atribuição a '{nome}':")
                print_preordem(node)
                print()

                i = k  # continua depois do ';'
        i += 1

