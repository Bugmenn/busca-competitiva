"""Representação do tabuleiro do Connect 4 e regras do jogo.

Este módulo define o ESTADO do problema de busca e as funções que
o manipulam: ações possíveis (função sucessor), aplicação de uma jogada
e o teste de fim de jogo (vitória ou empate).
"""

# Dimensões oficiais do Connect 4: 6 linhas e 7 colunas
LINHAS = 6
COLUNAS = 7

# Valores que cada casa do tabuleiro pode ter
VAZIO = 0   # casa sem peça
HUMANO = 1  # peça do jogador humano
IA = 2      # peça do computador

# Quantidade de peças em linha necessária para vencer
SEQUENCIA_VITORIA = 4

# Símbolos usados para desenhar cada valor no terminal
SIMBOLOS = {VAZIO: ".", HUMANO: "X", IA: "O"}


def criar_tabuleiro():
    """Cria o ESTADO INICIAL: um tabuleiro 6x7 totalmente vazio."""
    # Lista de listas: cada lista interna é uma linha; a linha 0 é a de cima
    return [[VAZIO for _ in range(COLUNAS)] for _ in range(LINHAS)]


def coluna_valida(tabuleiro, coluna):
    """Diz se ainda cabe peça na coluna (a casa do topo está vazia)."""
    # Se a coluna está fora do tabuleiro, a jogada não é válida
    if coluna < 0 or coluna >= COLUNAS:
        return False
    # A coluna aceita peça enquanto a casa da linha de cima estiver vazia
    return tabuleiro[0][coluna] == VAZIO


def jogadas_validas(tabuleiro):
    """FUNÇÃO SUCESSOR (ações): lista das colunas onde é possível jogar."""
    # Percorre as 7 colunas e guarda só as que ainda têm espaço
    return [c for c in range(COLUNAS) if coluna_valida(tabuleiro, c)]


def linha_livre(tabuleiro, coluna):
    """Retorna a linha mais baixa livre da coluna (onde a peça vai cair)."""
    # Começa de baixo (última linha) e sobe até achar uma casa vazia
    for linha in range(LINHAS - 1, -1, -1):
        if tabuleiro[linha][coluna] == VAZIO:
            return linha
    # Coluna cheia: não existe linha livre
    return None


def aplicar_jogada(tabuleiro, coluna, peca):
    """Gera o ESTADO SUCESSOR: novo tabuleiro com a peça solta na coluna.

    O tabuleiro original não é alterado; isso permite à IA simular
    jogadas sem desfazer nada depois.
    """
    # Não deixa jogar em coluna cheia ou inexistente
    if not coluna_valida(tabuleiro, coluna):
        raise ValueError(f"Coluna {coluna + 1} inválida ou cheia")
    # Copia cada linha para criar um tabuleiro independente
    novo = [linha[:] for linha in tabuleiro]
    # A peça "cai" até a casa livre mais baixa (gravidade)
    linha = linha_livre(novo, coluna)
    novo[linha][coluna] = peca
    return novo


def venceu(tabuleiro, peca):
    """Verifica se a peça informada tem 4 em linha em qualquer direção."""
    # Direções verificadas: horizontal, vertical, diagonal \ e diagonal /
    direcoes = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            # Só vale começar a contar a partir de uma casa com a peça
            if tabuleiro[linha][coluna] != peca:
                continue
            for dl, dc in direcoes:
                # Posição da última casa da sequência de 4
                fim_l = linha + dl * (SEQUENCIA_VITORIA - 1)
                fim_c = coluna + dc * (SEQUENCIA_VITORIA - 1)
                # Se a sequência sairia do tabuleiro, ignora essa direção
                if not (0 <= fim_l < LINHAS and 0 <= fim_c < COLUNAS):
                    continue
                # Confere se as 4 casas da sequência têm a mesma peça
                if all(tabuleiro[linha + dl * i][coluna + dc * i] == peca
                       for i in range(SEQUENCIA_VITORIA)):
                    return True
    return False


def tabuleiro_cheio(tabuleiro):
    """Empate acontece quando não há mais nenhuma coluna disponível."""
    return len(jogadas_validas(tabuleiro)) == 0


def fim_de_jogo(tabuleiro):
    """TESTE TERMINAL: alguém venceu ou o tabuleiro encheu."""
    return venceu(tabuleiro, HUMANO) or venceu(tabuleiro, IA) or tabuleiro_cheio(tabuleiro)


def desenhar(tabuleiro):
    """Monta o texto do tabuleiro para mostrar no terminal."""
    linhas_texto = []
    for linha in tabuleiro:
        # Converte cada valor no seu símbolo e separa por espaço
        linhas_texto.append("| " + " ".join(SIMBOLOS[v] for v in linha) + " |")
    # Linha de base e numeração das colunas (1 a 7) para o jogador escolher
    linhas_texto.append("+" + "-" * (COLUNAS * 2 + 1) + "+")
    linhas_texto.append("  " + " ".join(str(c + 1) for c in range(COLUNAS)))
    return "\n".join(linhas_texto)
