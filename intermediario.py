# intermediario.py
#
# Responsável por gerar código intermediário em forma de
# instruções de 3 endereços, a partir:
#   - das árvores de expressão construídas no semântico
#   - da sequência de tokens do programa
#
# Principais responsabilidades:
#   * Geração de temporários (t0, t1, ...)
#   * Geração de rótulos (L0, L1, ...) para desvios
#   * Tradução de:
#       - atribuições
#       - comandos print
#       - if / else
#       - for (com inicialização, condição, passo e corpo)
#       - break
#       - chamadas de função
#   * Impressão final do código de 3 endereços


from semantico import parse_expression, ExprNode, SemanticError
from lexico import Token  # importado caso seja útil em extensões futuras

# Contadores globais para temporários e rótulos
temporario_counter = 0
label_counter = 0


def novo_temp():
    """
    Gera o nome de um novo registrador temporário (t0, t1, t2, ...).

    O contador é global ao módulo. Cada chamada retorna um identificador único
    durante a execução do analisador intermediário.
    """
    global temporario_counter
    t = f"t{temporario_counter}"
    temporario_counter += 1
    return t


def novo_label():
    """
    Gera o nome de um novo rótulo (L0, L1, L2, ...).

    Usado na geração de código para desvios condicionais e laços.
    """
    global label_counter
    l = f"L{label_counter}"
    label_counter += 1
    return l


def gerar_expr(node, codigo):
    """
    Gera código de 3 endereços para a árvore de expressão 'node'.

    Parâmetros:
        node  : nó ExprNode representando a expressão
        codigo: lista de strings onde as instruções geradas serão acrescentadas

    Retorna:
        O nome da variável (ou temporário) que contém o resultado da expressão.
    """
    if node is None:
        return None

    # --------- chamada de função: node.op == "call" ---------
    if node.op == "call":
        # Gera código para os argumentos (param arg)
        if getattr(node, "args", None):
            for arg in node.args:
                t_arg = gerar_expr(arg, codigo)
                codigo.append(f"param {t_arg}")

        # Call propriamente dito: tmp = call func
        tmp = novo_temp()
        codigo.append(f"{tmp} = call {node.valor}")
        return tmp

    # --------- folhas: literais e identificadores ---------
    if node.op in ("int", "float", "string", "id", "null"):
        # identificador: o valor já está na variável
        if node.op == "id":
            return node.valor
        # literais: coloca em um temporário
        else:
            t = novo_temp()
            codigo.append(f"{t} = {node.valor}")
            return t

    # --------- operador unário (+x, -x) ---------
    if node.op.startswith("unary"):
        t = gerar_expr(node.left, codigo)
        tmp = novo_temp()
        # A forma "unary+" / "unary-" é mantida na string, apenas
        # como representação do operador unário.
        codigo.append(f"{tmp} = {node.op}{t}")
        return tmp

    # --------- operadores binários (+, -, *, /, %, comparações etc.) ---------
    left = gerar_expr(node.left, codigo)
    right = gerar_expr(node.right, codigo)
    tmp = novo_temp()
    codigo.append(f"{tmp} = {left} {node.op} {right}")
    return tmp


def encontrar_fim_statement(tokens, inicio, fim):
    """
    Dado o índice 'inicio' do primeiro token de um STATEMENT,
    devolve o índice logo após o fim desse STATEMENT
    (parâmetro 'fim' é exclusivo).

    É análogo à função com o mesmo nome no módulo semântico, mas
    usada aqui especificamente para delimitar regiões de código
    durante a geração intermediária.
    """
    k = inicio
    if k >= fim:
        return fim

    tok0 = tokens[k]

    # Bloco: { STATELIST }
    if tok0.tipo == "{":
        nivel = 1
        k += 1
        while k < fim and nivel > 0:
            if tokens[k].tipo == "{":
                nivel += 1
            elif tokens[k].tipo == "}":
                nivel -= 1
            k += 1
        return k  # logo após '}'

    # if ( EXPRESSION ) STATEMENT [else STATEMENT]
    if tok0.tipo == "if":
        j = k + 1
        # acha '('
        while j < fim and tokens[j].tipo != "(":
            j += 1
        if j >= fim:
            return fim
        j += 1  # pula '('

        # pula a EXPRESSAO até o ')'
        nivel_paren = 1
        while j < fim and nivel_paren > 0:
            if tokens[j].tipo == "(":
                nivel_paren += 1
            elif tokens[j].tipo == ")":
                nivel_paren -= 1
            j += 1

        # STATEMENT do if
        body_start = j
        body_end = encontrar_fim_statement(tokens, body_start, fim)
        k = body_end

        # verifica se tem else
        if k < fim and tokens[k].tipo == "else":
            k2 = encontrar_fim_statement(tokens, k + 1, fim)
            k = k2

        return k

    # for( ATRIBSTAT ; EXPRESSION ; ATRIBSTAT ) STATEMENT
    if tok0.tipo == "for":
        j = k + 1
        while j < fim and tokens[j].tipo != "(":
            j += 1
        if j >= fim:
            return fim
        j += 1

        # pula cabeçalho do for até ')'
        nivel_paren = 1
        while j < fim and nivel_paren > 0:
            if tokens[j].tipo == "(":
                nivel_paren += 1
            elif tokens[j].tipo == ")":
                nivel_paren -= 1
            j += 1

        body_start = j
        body_end = encontrar_fim_statement(tokens, body_start, fim)
        return body_end

    # Comandos simples -> vão até o próximo ';'
    while k < fim and tokens[k].tipo != ";":
        k += 1
    if k < fim:
        return k + 1
    return k


def gerar_atribuicao_fragmento(tokens, inicio, fim, tabela_simbolos, escopo, codigo):
    """
    Gera código para um fragmento que *deveria* ser um ATRIBSTAT (sem ';'),
    típico de cabeçalho de for:  i = 0   ou   i = i + 1.

    Se o fragmento não for exatamente uma atribuição (por exemplo, for apenas
    uma expressão), a função gera o código intermediário correspondente
    chamando parse_expression e gerar_expr.
    """
    if inicio >= fim:
        return

    # Esperando algo do tipo: ident ... = EXPRESSAO
    if tokens[inicio].tipo != "ident":
        # Não é atribuição: trata como expressão "solta"
        node, _ = parse_expression(tokens[inicio:fim], 0, tabela_simbolos, escopo)
        gerar_expr(node, codigo)
        return

    i = inicio
    ident_tok = tokens[i]
    idx_ts = ident_tok.valor
    nome = tabela_simbolos[idx_ts][0]
    i += 1

    # Pula possíveis índices [ NUMEXPRESSION ] (acesso a vetores)
    while i < fim and tokens[i].tipo == "[":
        # Para simplificar, só pulamos até o ']'
        i += 1
        while i < fim and tokens[i].tipo != "]":
            i += 1
        if i < fim:
            i += 1

    if i >= fim or tokens[i].tipo != "=":
        # Não achou '=', trata como expressão simples
        node, _ = parse_expression(tokens[inicio:fim], 0, tabela_simbolos, escopo)
        gerar_expr(node, codigo)
        return

    # RHS (lado direito) da atribuição
    rhs_tokens = tokens[i+1:fim]
    if not rhs_tokens:
        return

    node, _ = parse_expression(rhs_tokens, 0, tabela_simbolos, escopo)
    t = gerar_expr(node, codigo)
    codigo.append(f"{nome} = {t}")


def gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                   inicio, fim, codigo, pilha_loops):
    """
    Gera o código intermediário para o intervalo [inicio, fim) de tokens.

    Parâmetros:
        tokens          : lista de tokens do programa
        tabela_simbolos : tabela léxica (para obter o nome de ident pelo índice)
        escopo_por_token: lista de escopos calculada no semântico
        inicio, fim     : intervalo de tokens a processar
        codigo          : lista de strings onde as instruções serão acumuladas
        pilha_loops     : pilha de labels de saída de laços (para break)
    """

    # Escopo "global"/padrão de fallback:
    # primeiro escopo não-None encontrado em escopo_por_token
    escopo_padrao = None
    for e in escopo_por_token:
        if e is not None:
            escopo_padrao = e
            break

    i = inicio
    while i < fim:
        tok = tokens[i]

        # Se escopo_por_token[i] for None (ex.: cabeçalho de função),
        # usa escopo_padrao (global ou mais externo).
        escopo_corrente = escopo_por_token[i] or escopo_padrao

        # -------------------------------------------------
        # 0) Chamada de função como comando:
        #    func( ... );
        #    (sem precisar de dummy = ...)
        # -------------------------------------------------
        if tok.tipo == "ident" and i + 1 < fim and tokens[i + 1].tipo == "(":
            # Evita confundir 'def nome(...)' com chamada de função
            if i > inicio and tokens[i - 1].tipo == "def":
                i += 1
                continue

            # Junta todos os tokens até o ';' para montar a expressão
            j = i
            expr_tokens = []
            while j < fim and tokens[j].tipo != ";":
                expr_tokens.append(tokens[j])
                j += 1

            if j >= fim:
                raise Exception("';' esperado ao final da chamada de função")

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0,
                                           tabela_simbolos, escopo_corrente)
                # gerar_expr já sabe lidar com node.op == "call"
                gerar_expr(node, codigo)

            i = j + 1   # avança para depois do ';'
            continue

        # -------------------------------------------------
        # 1) ATRIBUIÇÃO simples: ident ... = EXPRESSAO ;
        # -------------------------------------------------
        if tok.tipo == "ident" and i + 1 < fim and tokens[i+1].tipo == "=":
            nome = tabela_simbolos[tok.valor][0]

            j = i + 2
            expr_tokens = []
            while j < fim and tokens[j].tipo != ";":
                expr_tokens.append(tokens[j])
                j += 1

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
                t = gerar_expr(node, codigo)
                codigo.append(f"{nome} = {t}")

            i = j + 1  # após ';'
            continue

        # -------------------------------------------------
        # 2) print EXPRESSAO;
        # -------------------------------------------------
        if tok.tipo == "print":
            j = i + 1
            expr_tokens = []
            while j < fim and tokens[j].tipo != ";":
                expr_tokens.append(tokens[j])
                j += 1

            if expr_tokens:
                node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
                t = gerar_expr(node, codigo)
                codigo.append(f"print {t}")

            i = j + 1
            continue

        # -------------------------------------------------
        # 3) if ( EXPRESSAO ) STATEMENT [else STATEMENT]
        # -------------------------------------------------
        if tok.tipo == "if":
            j = i + 1
            # acha '('
            while j < fim and tokens[j].tipo != "(":
                j += 1
            if j >= fim:
                raise SemanticError(f"'(' esperado após 'if' (linha {tok.l}, coluna {tok.c})")
            j += 1  # pula '('

            # EXPRESSAO até ')'
            start_expr = j
            nivel_paren = 1
            while j < fim and nivel_paren > 0:
                if tokens[j].tipo == "(":
                    nivel_paren += 1
                elif tokens[j].tipo == ")":
                    nivel_paren -= 1
                j += 1
            end_expr = j - 1  # posição do ')'

            expr_tokens = tokens[start_expr:end_expr]
            node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
            t_cond = gerar_expr(node, codigo)

            # Desvio se a condição for falsa
            label_false = novo_label()
            codigo.append(f"if not {t_cond} goto {label_false}")

            # STATEMENT do if começa em j
            body_start = j
            body_end = encontrar_fim_statement(tokens, body_start, fim)

            # Gera código do corpo do if
            gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                           body_start, body_end, codigo, pilha_loops)

            # Verifica se há 'else'
            if body_end < fim and tokens[body_end].tipo == "else":
                label_end = novo_label()
                # Se entrou no if, pula o else
                codigo.append(f"goto {label_end}")
                # Label para o caso de condição falsa
                codigo.append(f"{label_false}:")
                else_start = body_end + 1
                else_end = encontrar_fim_statement(tokens, else_start, fim)
                gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                               else_start, else_end, codigo, pilha_loops)
                codigo.append(f"{label_end}:")
                i = else_end
            else:
                # if sem else
                codigo.append(f"{label_false}:")
                i = body_end
            continue

        # -------------------------------------------------
        # 4) for( ATRIBSTAT ; EXPRESSAO ; ATRIBSTAT ) STATEMENT
        # -------------------------------------------------
        if tok.tipo == "for":
            j = i + 1
            while j < fim and tokens[j].tipo != "(":
                j += 1
            if j >= fim:
                raise SemanticError(f"'(' esperado após 'for' (linha {tok.l}, coluna {tok.c})")
            j += 1  # após '('

            # init: ATRIBSTAT até o primeiro ';'
            init_start = j
            while j < fim and tokens[j].tipo != ";":
                j += 1
            init_end = j  # posição do ';'
            gerar_atribuicao_fragmento(tokens, init_start, init_end,
                                       tabela_simbolos, escopo_corrente, codigo)
            j += 1  # após ';'

            # cond: EXPRESSAO até o segundo ';'
            cond_start = j
            while j < fim and tokens[j].tipo != ";":
                j += 1
            cond_end = j
            cond_tokens = tokens[cond_start:cond_end]

            # step: ATRIBSTAT até ')'
            j += 1  # após ';'
            step_start = j
            nivel_paren = 1
            while j < fim and nivel_paren > 0:
                if tokens[j].tipo == "(":
                    nivel_paren += 1
                elif tokens[j].tipo == ")":
                    nivel_paren -= 1
                j += 1
            step_end = j - 1  # posição antes de ')'
            step_tokens = tokens[step_start:step_end]

            # Labels do laço
            label_ini = novo_label()
            label_fim = novo_label()

            # Início do laço
            codigo.append(f"{label_ini}:")
            if cond_tokens:
                node, _ = parse_expression(cond_tokens, 0, tabela_simbolos, escopo_corrente)
                t_cond = gerar_expr(node, codigo)
                codigo.append(f"if not {t_cond} goto {label_fim}")

            # STATEMENT (corpo) começa em j (logo após ')')
            body_start = j

            # Empilha label de saída para 'break;'
            pilha_loops.append(label_fim)

            # Corpo pode ser bloco ou comando simples
            if body_start < fim and tokens[body_start].tipo == "{":
                # Corpo é um bloco {...}
                k = body_start + 1
                nivel_chaves = 1
                while k < fim and nivel_chaves > 0:
                    if tokens[k].tipo == "{":
                        nivel_chaves += 1
                    elif tokens[k].tipo == "}":
                        nivel_chaves -= 1
                    k += 1
                body_end = k - 1  # índice do '}'
                gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                               body_start + 1, body_end, codigo, pilha_loops)
                i = k  # após '}'
            else:
                # STATEMENT simples
                body_end = encontrar_fim_statement(tokens, body_start, fim)
                gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                               body_start, body_end, codigo, pilha_loops)
                i = body_end

            # Após o corpo: passo (step)
            if step_tokens:
                gerar_atribuicao_fragmento(step_tokens, 0, len(step_tokens),
                                           tabela_simbolos, escopo_corrente, codigo)

            # Volta ao início e depois label de saída
            codigo.append(f"goto {label_ini}")
            codigo.append(f"{label_fim}:")
            pilha_loops.pop()
            continue

        # -------------------------------------------------
        # 5) break;
        # -------------------------------------------------
        if tok.tipo == "break":
            if pilha_loops:
                label_saida = pilha_loops[-1]
                codigo.append(f"goto {label_saida}")
            # pula até o próximo ';'
            j = i + 1
            while j < fim and tokens[j].tipo != ";":
                j += 1
            i = j + 1
            continue

        # -------------------------------------------------
        # Outros comandos (declarações, read, return etc.)
        # por enquanto são ignorados na geração de código.
        # -------------------------------------------------
        i += 1


def analisador_intermediario(tokens, tabela_simbolos, escopo_por_token):
    """
    Função de alto nível para geração do código intermediário.

    Parâmetros:
        tokens          : lista de tokens do programa
        tabela_simbolos : tabela léxica gerada no léxico
        escopo_por_token: mapeamento posição -> Escopo (do semântico)

    A função:
        - inicializa a estrutura de código e pilha de laços
        - invoca gerar_comandos sobre todo o programa
        - insere um 'return' geral ao final
        - imprime o código gerado
    """
    codigo = []
    pilha_loops = []

    gerar_comandos(tokens, tabela_simbolos, escopo_por_token,
                   0, len(tokens), codigo, pilha_loops)

    # Um "return" geral no fim do programa (encerramento)
    codigo.append("return")

    if codigo:
        print("\n=== Código Intermediário (3-endereços) ===")
        for c in codigo:
            print(c)
