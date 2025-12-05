# Interpretador Python a ser usado
PYTHON = python3

# Arquivo principal do compilador
MAIN   = main.py

# Programas de teste em ConvCC-2025-2
P1 = programas/programa1.conv
P2 = programas/programa2.conv
P3 = programas/programa3.conv

# ---------------------------------------------------------------------
# Alvo padrão: executa os três programas de teste principais em sequência
# ---------------------------------------------------------------------
all: p1 p2 p3

# Executa o analisador no Programa 1
p1: $(MAIN) $(P1)
	$(PYTHON) $(MAIN) $(P1)

# Executa o analisador no Programa 2
p2: $(MAIN) $(P2)
	$(PYTHON) $(MAIN) $(P2)

# Executa o analisador no Programa 3
p3: $(MAIN) $(P3)
	$(PYTHON) $(MAIN) $(P3)

# ---------------------------------------------------------------------
# Alvo genérico: permite escolher o arquivo-fonte pela linha de comando
# Exemplo de uso:
#   make run ARQ=programas/outro_prog.conv
# ---------------------------------------------------------------------
run: $(MAIN)
	$(PYTHON) $(MAIN) $(ARQ)

# ---------------------------------------------------------------------
# Alvo para executar um dos programas de teste internos definidos em main.py
# Exemplo de uso:
#   make test T=leonardo
#   make test T=tipos_expr
# ---------------------------------------------------------------------
test: $(MAIN)
	$(PYTHON) $(MAIN) --test $(T)

# ---------------------------------------------------------------------
# Limpeza: remove arquivos gerados pelo Python (__pycache__, .pyc)
# ---------------------------------------------------------------------
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

.PHONY: all p1 p2 p3 run test clean
