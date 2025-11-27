from semantico import parse_expression, ExprNode

temporario_counter = 0
label_counter = 0

def novo_temp():
    global temporario_counter
    t = f"t{temporario_counter}"
    temporario_counter += 1
    return t

def novo_label():
    global label_counter
    l = f"L{label_counter}"
    label_counter += 1
    return l

def gerar_expr(node, codigo):
    if node is None:
        return None
    if node.op in ("int", "float", "string", "id", "null"):
        if node.op == "id":
            return node.valor
        else:
            t = novo_temp()
            codigo.append(f"{t} = {node.valor}")
            return t
    if node.op.startswith("unary"):
        t = gerar_expr(node.left, codigo)
        tmp = novo_temp()
        codigo.append(f"{tmp} = {node.op}{t}")
        return tmp
    left = gerar_expr(node.left, codigo)
    right = gerar_expr(node.right, codigo)
    tmp = novo_temp()
    codigo.append(f"{tmp} = {left} {node.op} {right}")
    return tmp

def analisador_intermediario(tokens, tabela_simbolos, escopo_por_token):
    codigo = []
    pilha_loops = []
    i = 0
    n = len(tokens)
    
    while i < n:
        tok = tokens[i]
        escopo_corrente = escopo_por_token[i]
        if tok.tipo == "ident" and i+1 < n and tokens[i+1].tipo == "=":
            nome = tabela_simbolos[tok.valor][0]
            j = i + 2
            expr_tokens = []
            while j < n and tokens[j].tipo != ";":
                expr_tokens.append(tokens[j])
                j += 1
            node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
            t = gerar_expr(node, codigo)
            codigo.append(f"{nome} = {t}")
            i = j + 1
            continue
        if tok.tipo == "print":
            j = i + 1
            expr_tokens = []
            while j < n and tokens[j].tipo != ";":
                expr_tokens.append(tokens[j])
                j += 1
            node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
            t = gerar_expr(node, codigo)
            codigo.append(f"print {t}")
            i = j + 1
            continue
        if tok.tipo == "if":
            j = i + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            start_expr = j + 1
            k = start_expr
            nivel_paren = 1
            while k < n and nivel_paren > 0:
                if tokens[k].tipo == "(":
                    nivel_paren += 1
                elif tokens[k].tipo == ")":
                    nivel_paren -= 1
                k += 1
            end_expr = k - 1
            expr_tokens = tokens[start_expr:end_expr]
            node, _ = parse_expression(expr_tokens, 0, tabela_simbolos, escopo_corrente)
            t = gerar_expr(node, codigo)
            label_fim = novo_label()
            codigo.append(f"if not {t} goto {label_fim}")
            i = k
            nivel_chaves = 0
            if tokens[i].tipo == "{":
                nivel_chaves += 1
                i += 1
            while i < n and nivel_chaves > 0:
                if tokens[i].tipo == "{":
                    nivel_chaves += 1
                elif tokens[i].tipo == "}":
                    nivel_chaves -= 1
                i += 1
            codigo.append(f"{label_fim}:")
            continue
        if tok.tipo == "for":
            j = i + 1
            while j < n and tokens[j].tipo != "(":
                j += 1
            start = j + 1
            k = start
            while k < n and tokens[k].tipo != ";":
                k += 1
            init_tokens = tokens[start:k]
            node, _ = parse_expression(init_tokens, 0, tabela_simbolos, escopo_corrente)
            gerar_expr(node, codigo)
            k1 = k + 1
            k = k1
            while k < n and tokens[k].tipo != ";":
                k += 1
            cond_tokens = tokens[k1:k]
            k2 = k + 1
            while k2 < n and tokens[k2].tipo != ")":
                k2 += 1
            step_tokens = tokens[k+1:k2]
            label_inicio = novo_label()
            label_fim = novo_label()
            codigo.append(f"{label_inicio}:")
            if cond_tokens:
                node, _ = parse_expression(cond_tokens, 0, tabela_simbolos, escopo_corrente)
                t_cond = gerar_expr(node, codigo)
                codigo.append(f"if not {t_cond} goto {label_fim}")
            i = k2 + 1
            if i < n and tokens[i].tipo == "{":
                nivel_chaves = 1
                i += 1
                corpo_tokens = []
                while i < n and nivel_chaves > 0:
                    if tokens[i].tipo == "{":
                        nivel_chaves += 1
                    elif tokens[i].tipo == "}":
                        nivel_chaves -= 1
                    corpo_tokens.append(tokens[i])
                    i += 1
                analisador_intermediario(corpo_tokens, tabela_simbolos, escopo_por_token)
            if step_tokens:
                node, _ = parse_expression(step_tokens, 0, tabela_simbolos, escopo_corrente)
                gerar_expr(node, codigo)
            codigo.append(f"goto {label_inicio}")
            codigo.append(f"{label_fim}:")
            continue
        if tok.tipo == "break":
            if pilha_loops:
                codigo.append(f"goto {pilha_loops[-1]}")
            i += 1
            continue
        i += 1
    
    codigo.append("return")
    if codigo:
        print("\n=== Código Intermediário (3-endereços) ===")
        for c in codigo:
            print(c)
