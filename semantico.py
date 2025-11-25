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


def declara_parametro(nome, tipo, token_ident, pilha_escopos):
    escopo = escopo_atual(pilha_escopos)
    if escopo.contem(nome):
        raise SemanticError(
            f"Redeclaração de parâmetro/variável '{nome}' no mesmo escopo "
            f"(linha {token_ident.l}, coluna {token_ident.c})"
        )
    escopo.simbolos[nome] = SimboloSemantico(
        nome, tipo, "param", escopo, token_ident.l, token_ident.c
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
    # escopo global
    escopo_global = Escopo("global", None, "global")
    pilha_escopos = [escopo_global]

    # para o ponto 5 (break em for)
    pilha_loops = []

    # índice (da tabela do léxico) -> tipo
    tipos_por_indice = {}

    # escopo em que cada token é analisado (posição i -> Escopo)
    escopo_por_token = [None] * len(tokens)

    # 1ª passada: declarações, escopos, break, e preenche escopo_por_token
    processar_declaracoes_e_escopos(
        tokens, tabela_simbolos,
        pilha_escopos, pilha_loops,
        tipos_por_indice,
        escopo_por_token,
    )

    # 2ª passada: expressões, usando o escopo correto por posição
    processar_expressoes(
        tokens, tabela_simbolos,
        escopo_global,
        tipos_por_indice,
        escopo_por_token,
    )

    print("Análise semântica concluída com sucesso!")
    print("Tabela de símbolos com tipos (por índice do léxico):")
    for idx, tipo in tipos_por_indice.items():
        nome = tabela_simbolos[idx][0]
        print(f"{idx}: {nome} : {tipo}")

    return escopo_por_token




def processar_declaracoes_e_escopos(tokens, tabela_simbolos,
                                    pilha_escopos, pilha_loops,
                                    tipos_por_indice,
                                    escopo_por_token):


    i = 0
    n = len(tokens)

    def encontrar_fim_statement(inicio):
        """
        Dado o índice 'inicio' do primeiro token de um STATEMENT,
        devolve o índice logo após o fim desse STATEMENT, seguindo
        aproximadamente a gramática:

        STATEMENT -> VARDECL; | ATRIBSTAT; | PRINTSTAT; | READSTAT; |
                     RETURNSTAT; | IFSTAT; | FORSTAT; | {STATELIST} | break; | ;
        """
        k = inicio
        if k >= n:
            return n

        tok0 = tokens[k]

        # bloco: { STATELIST }
        if tok0.tipo == "{":
            nivel_chaves = 1
            k += 1
            while k < n and nivel_chaves > 0:
                if tokens[k].tipo == "{":
                    nivel_chaves += 1
                elif tokens[k].tipo == "}":
                    nivel_chaves -= 1
                k += 1
            return k  # posição logo após o '}' que fecha o bloco

        # if: IFSTAT -> if( EXPRESSION ) STATEMENT IFSTAT'
        if tok0.tipo == "if":
            j = k + 1
            # acha '('
            while j < n and tokens[j].tipo != "(":
                j += 1
            if j >= n:
                return n
            j += 1  # pula '('
            nivel_paren = 1
            while j < n and nivel_paren > 0:
                if tokens[j].tipo == "(":
                    nivel_paren += 1
                elif tokens[j].tipo == ")":
                    nivel_paren -= 1
                j += 1
            # j está logo após ')'
            body_start = j
            body_end = encontrar_fim_statement(body_start)
            k = body_end

            # IFSTAT' -> else STATEMENT | &
            if k < n and tokens[k].tipo == "else":
                k2 = encontrar_fim_statement(k + 1)
                k = k2

            # STATEMENT -> IFSTAT ;
            while k < n and tokens[k].tipo != ";":
                k += 1
            if k < n:
                return k + 1
            return k

        # for: FORSTAT -> for(ATRIBSTAT;EXPRESSION;ATRIBSTAT) STATEMENT
        # STATEMENT -> FORSTAT ;
        if tok0.tipo == "for":
            j = k + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            if j >= n:
                return n
            j += 1
            nivel_paren = 1
            while j < n and nivel_paren > 0:
                if tokens[j].tipo == "(":
                    nivel_paren += 1
                elif tokens[j].tipo == ")":
                    nivel_paren -= 1
                j += 1
            body_start = j
            body_end = encontrar_fim_statement(body_start)
            k = body_end
            while k < n and tokens[k].tipo != ";":
                k += 1
            if k < n:
                return k + 1
            return k

        # demais statements simples: até o próximo ';'
        while k < n and tokens[k].tipo != ";":
            k += 1
        if k < n:
            return k + 1
        return k

    while i < n:
        # registra o escopo ANTES de processar o token i
        escopo_por_token[i] = escopo_atual(pilha_escopos)

        tok = tokens[i]

        # Antes de tudo: remover laços simples cujo corpo já foi totalmente percorrido
        while pilha_loops and pilha_loops[-1].get("tipo") == "simples" \
                and i >= pilha_loops[-1].get("fim", n+1):
            pilha_loops.pop()

        # 1) Início de função: def ident ( ... ) { ... }
        if tok.tipo == "def" and i + 1 < n and tokens[i + 1].tipo == "ident":
            ident_tok = tokens[i + 1]
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

                    # declara parâmetro como tal no escopo da função
                    declara_parametro(nome_param, tipo, ident_param, pilha_escopos)
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

            # se houver um laço de 'for' cujo corpo é esse bloco, associa o escopo
            if pilha_loops and pilha_loops[-1].get("tipo") == "bloco" \
                    and pilha_loops[-1].get("escopo") is None:
                pilha_loops[-1]["escopo"] = novo

        # 3) Fecha escopo
        elif tok.tipo == "}":
            # topo da pilha sempre deve ser algum escopo
            escopo_top = pilha_escopos[-1]

            if escopo_top.tipo == "bloco":
                escopo_fechado = pilha_escopos.pop()

                # encerra laço 'for' cujo corpo é exatamente este bloco
                if pilha_loops and pilha_loops[-1].get("tipo") == "bloco" \
                        and pilha_loops[-1].get("escopo") is escopo_fechado:
                    pilha_loops.pop()

                # se este bloco é o corpo principal de uma função (pai == func),
                # também fechamos o escopo da função
                if escopo_fechado.pai is not None and escopo_fechado.pai.tipo == "func":
                    pilha_escopos.pop()  # fecha escopo da função

            else:
                # escopo_top não é bloco (pode ser 'func' em algum erro de sintaxe)
                pilha_escopos.pop()


        # 4) Declaração de variável: TIPO ident ...
        elif tok.tipo in ("int", "float", "string") and i + 1 < n and tokens[i+1].tipo == "ident":
            tipo = tok.tipo
            ident_tok = tokens[i + 1]
            idx_ts = ident_tok.valor
            nome = tabela_simbolos[idx_ts][0]

            declara_variavel(nome, tipo, ident_tok, pilha_escopos)
            tipos_por_indice[idx_ts] = tipo

            i += 1  # pulamos o ident

        # 5) Controle de laços 'for'
        elif tok.tipo == "for":
            # achar o '(' do cabeçalho do for
            j = i + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            if j >= n:
                raise SemanticError(
                    f"'(' esperado após 'for' (linha {tok.l}, coluna {tok.c})"
                )

            # achar o ')' que fecha o cabeçalho
            k = j + 1
            nivel_paren = 1
            while k < n and nivel_paren > 0:
                if tokens[k].tipo == "(":
                    nivel_paren += 1
                elif tokens[k].tipo == ")":
                    nivel_paren -= 1
                k += 1
            if nivel_paren != 0:
                raise SemanticError(
                    f"')' esperado para fechar cabeçalho do for "
                    f"(linha {tok.l}, coluna {tok.c})"
                )

            body_start = k  # primeiro token do STATEMENT (corpo do for)

            if body_start >= n:
                i += 1
                continue

            tok_body = tokens[body_start]

            if tok_body.tipo == "{":
                # corpo é um bloco; vamos associar o escopo na próxima '{'
                pilha_loops.append({"tipo": "bloco", "escopo": None})
            else:
                # corpo é um STATEMENT simples: calculamos onde ele termina
                fim = encontrar_fim_statement(body_start)
                pilha_loops.append({"tipo": "simples", "fim": fim})

        # 6) Comando 'break'
        elif tok.tipo == "break":
            if not pilha_loops:
                raise SemanticError(
                    f"Comando 'break' fora de laço de repetição na linha {tok.l}, coluna {tok.c}"
                )

        i += 1


class ExprNode:
    def __init__(self, op, left=None, right=None, valor=None, tipo=None):
        """
        op: '+', '-', '*', '/', '%', 'id', 'int', 'float', 'string', 'null', etc.
        left, right: filhos
        valor: para folhas (nome do ident, valor literal, operador)
        tipo: tipo inferido da expressão ('int', 'float', 'string', ...)
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
    if node.valor is not None:
        print(node.valor, end=" ")
    else:
        print(node.op, end=" ")
    print_preordem(node.left)
    print_preordem(node.right)


# ---------------- PARSER DE EXPRESSÕES ----------------

def parse_expression(tokens, i, tabela_simbolos, escopo):
    node, i = parse_numexpression(tokens, i, tabela_simbolos, escopo)
    # COMPARACAO opcional
    if i < len(tokens) and tokens[i].tipo in ("<", ">", "<=", ">=", "==", "!="):
        op = tokens[i].tipo
        i += 1
        right, i = parse_numexpression(tokens, i, tabela_simbolos, escopo)
        node = combinar_binario(op, node, right, tokens[i-1])
        # tipo da comparação poderia ser 'bool', se você quiser guardar isso
    return node, i


def parse_numexpression(tokens, i, tabela_simbolos, escopo):
    node, i = parse_term(tokens, i, tabela_simbolos, escopo)
    while i < len(tokens) and tokens[i].tipo in ("+", "-"):
        op = tokens[i].tipo
        i += 1
        right, i = parse_term(tokens, i, tabela_simbolos, escopo)
        node = combinar_binario(op, node, right, tokens[i-1])
    return node, i


def parse_term(tokens, i, tabela_simbolos, escopo):
    node, i = parse_unaryexpr(tokens, i, tabela_simbolos, escopo)
    while i < len(tokens) and tokens[i].tipo in ("*", "/", "%"):
        op = tokens[i].tipo
        i += 1
        right, i = parse_unaryexpr(tokens, i, tabela_simbolos, escopo)
        node = combinar_binario(op, node, right, tokens[i-1])
    return node, i


def parse_unaryexpr(tokens, i, tabela_simbolos, escopo):
    # OPERADORES -> + | - | &
    if tokens[i].tipo in ("+", "-"):
        op = tokens[i].tipo
        i += 1
        factor, i = parse_factor(tokens, i, tabela_simbolos, escopo)
        node = ExprNode("unary" + op, factor, None, valor=op)
        node.tipo = factor.tipo
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

        # CHAMADA (função) e índices [ ] podem ser tratados aqui depois
        return node, i

    raise SemanticError(
        f"Token inesperado em fator: {tok.tipo} (linha {tok.l}, coluna {tok.c})"
    )


def combinar_binario(op, left, right, tok):
    if left.tipo != right.tipo:
        raise SemanticError(
            f"Operação '{op}' com tipos incompatíveis: {left.tipo} e {right.tipo} (linha {tok.l}, coluna {tok.c})"
        )
    node = ExprNode(op, left, right, valor=op)
    node.tipo = left.tipo
    return node


def processar_expressoes(tokens, tabela_simbolos,
                         escopo_global, tipos_por_indice,
                         escopo_por_token):


    """
    Percorre a lista de tokens e:
      - constrói árvores de expressão para:
          * atribuições: LVALUE = EXPRESSION ;
          * print EXPRESSION ;
          * if( EXPRESSION ) ...
          * for( ATRIBSTAT ; EXPRESSION ; ATRIBSTAT ) ...
      - faz verificação de tipos dentro das expressões (via parse_expression / combinar_binario)
      - opcionalmente imprime as árvores em pré-ordem.
    """
    pilha_escopos = [escopo_global]
    pilha_loops = []  # pilha de loops para validar 'break'
    
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]

        # escopo correto para este ponto do código
        escopo_corrente = escopo_por_token[i] or escopo_global
        
        # 1) ATRIBUIÇÃO: LVALUE = EXPRESSION ;
        if tok.tipo == "ident":
            j = i + 1

            # pula possíveis [ NUMEXPRESSION ] do LVALUE
            while j < n and tokens[j].tipo == "[":
                j += 1
                while j < n and tokens[j].tipo != "]":
                    j += 1
                j += 1  # pula ']'

            if j < n and tokens[j].tipo == "=":
                idx_ts = tok.valor
                nome = tabela_simbolos[idx_ts][0]
                simbolo = escopo_corrente.procura(nome)
                if simbolo is None:
                    raise SemanticError(
                        f"Variável '{nome}' não declarada na atribuição "
                        f"(linha {tok.l}, coluna {tok.c})"
                    )

                k = j + 1
                while k < n and tokens[k].tipo != ";":
                    k += 1
                if k >= n:
                    raise SemanticError("';' esperado ao final de atribuição")

                expr_tokens = tokens[j+1:k]

                if expr_tokens:
                    node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)

                    if node.tipo is not None and simbolo.tipo is not None and node.tipo != simbolo.tipo:
                        raise SemanticError(
                            f"Tipo da expressão ({node.tipo}) incompatível com variável '{nome}' "
                            f"de tipo {simbolo.tipo} (linha {tok.l}, coluna {tok.c})"
                        )

                    print(f"Árvore da expressão da atribuição a '{nome}':")
                    print_preordem(node)
                    print()

                i = k + 1
                continue

        # 2) PRINT: print EXPRESSION ;
        if tok.tipo == "print":
            start_expr = i + 1
            j = start_expr
            while j < n and tokens[j].tipo != ";":
                j += 1
            if j >= n:
                raise SemanticError(
                    f"';' esperado ao final do comando print (linha {tok.l}, coluna {tok.c})"
                )

            expr_tokens = tokens[start_expr:j]

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
                print(f"Árvore da expressão no print (linha {tok.l}, coluna {tok.c}):")
                print_preordem(node)
                print()

            i = j + 1
            continue

        # 3) IF: if ( EXPRESSION ) STATEMENT ...
        if tok.tipo == "if":
            j = i + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            if j >= n:
                raise SemanticError(
                    f"'(' esperado após 'if' (linha {tok.l}, coluna {tok.c})"
                )

            start_expr = j + 1
            k = start_expr
            nivel_paren = 1
            while k < n and nivel_paren > 0:
                if tokens[k].tipo == "(":
                    nivel_paren += 1
                elif tokens[k].tipo == ")":
                    nivel_paren -= 1
                k += 1

            if nivel_paren != 0:
                raise SemanticError(
                    f"')' esperado para fechar condição do if "
                    f"(linha {tok.l}, coluna {tok.c})"
                )

            end_expr = k - 1
            expr_tokens = tokens[start_expr:end_expr]

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
                print(f"Árvore da expressão da condição do if (linha {tok.l}, coluna {tok.c}):")
                print_preordem(node)
                print()

            i += 1
            continue

        # 4) FOR: for( ATRIBSTAT ; EXPRESSION ; ATRIBSTAT ) STATEMENT
        if tok.tipo == "for":
            j = i + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            if j >= n:
                raise SemanticError(
                    f"'(' esperado após 'for' (linha {tok.l}, coluna {tok.c})"
                )

            k = j + 1
            while k < n and tokens[k].tipo != ";":
                k += 1
            if k >= n:
                raise SemanticError(
                    f"Primeiro ';' esperado no cabeçalho do for "
                    f"(linha {tok.l}, coluna {tok.c})"
                )

            first_semicolon = k

            start_expr = first_semicolon + 1
            k = start_expr
            while k < n and tokens[k].tipo != ";":
                k += 1
            if k >= n:
                raise SemanticError(
                    f"Segundo ';' esperado no cabeçalho do for "
                    f"(linha {tok.l}, coluna {tok.c})"
                )

            second_semicolon = k
            end_expr = second_semicolon

            expr_tokens = tokens[start_expr:end_expr]

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
                print(f"Árvore da expressão-condição do for (linha {tok.l}, coluna {tok.c}):")
                print_preordem(node)
                print()

            i = second_semicolon + 1
            continue

        i += 1
        

