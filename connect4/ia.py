"""Inteligência artificial do Connect 4: Minimax com poda alfa-beta.

A IA é o jogador MAX (quer o maior valor) e o humano é o jogador MIN
(quer o menor valor). Como a árvore completa do Connect 4 é enorme,
a busca para numa profundidade limite e usa uma função heurística
para estimar quem está melhor naquele tabuleiro.
"""

import math

from .tabuleiro import (COLUNAS, HUMANO, IA, LINHAS, SEQUENCIA_VITORIA, VAZIO,
                        aplicar_jogada, jogadas_validas, tabuleiro_cheio, venceu)

# Valor de uma vitória. É bem maior que qualquer pontuação heurística,
# para a IA sempre preferir ganhar (ou evitar perder) a qualquer vantagem.
VALOR_VITORIA = 1_000_000

# Ordem em que as colunas são testadas: do centro para as bordas.
# Jogadas centrais costumam ser melhores, então são avaliadas primeiro;
# isso faz a poda alfa-beta cortar mais galhos.
ORDEM_COLUNAS = [3, 2, 4, 1, 5, 0, 6]

# Profundidade de busca para cada nível de dificuldade
DIFICULDADES = {"facil": 2, "medio": 4, "dificil": 6}


def avaliar_janela(janela, peca):
    """Pontua um trecho de 4 casas do ponto de vista da peça informada."""
    # Descobre quem é o adversário
    oponente = HUMANO if peca == IA else IA
    # Conta peças próprias, do adversário e casas vazias na janela
    proprias = janela.count(peca)
    adversarias = janela.count(oponente)
    vazias = janela.count(VAZIO)

    pontos = 0
    if proprias == 3 and vazias == 1:
        pontos += 5   # quase 4 em linha: ameaça forte
    elif proprias == 2 and vazias == 2:
        pontos += 2   # sequência em construção
    if adversarias == 3 and vazias == 1:
        pontos -= 4   # adversário ameaça vencer: é preciso bloquear
    return pontos


def heuristica(tabuleiro, peca):
    """Estima o quanto o tabuleiro é bom para a peça (sem ser fim de jogo)."""
    pontos = 0

    # Peças na coluna central participam de mais sequências possíveis
    coluna_central = [tabuleiro[l][COLUNAS // 2] for l in range(LINHAS)]
    pontos += coluna_central.count(peca) * 3

    # Janelas horizontais de 4 casas
    for l in range(LINHAS):
        for c in range(COLUNAS - SEQUENCIA_VITORIA + 1):
            janela = [tabuleiro[l][c + i] for i in range(SEQUENCIA_VITORIA)]
            pontos += avaliar_janela(janela, peca)

    # Janelas verticais de 4 casas
    for c in range(COLUNAS):
        for l in range(LINHAS - SEQUENCIA_VITORIA + 1):
            janela = [tabuleiro[l + i][c] for i in range(SEQUENCIA_VITORIA)]
            pontos += avaliar_janela(janela, peca)

    # Janelas diagonais descendo para a direita (\)
    for l in range(LINHAS - SEQUENCIA_VITORIA + 1):
        for c in range(COLUNAS - SEQUENCIA_VITORIA + 1):
            janela = [tabuleiro[l + i][c + i] for i in range(SEQUENCIA_VITORIA)]
            pontos += avaliar_janela(janela, peca)

    # Janelas diagonais subindo para a direita (/)
    for l in range(SEQUENCIA_VITORIA - 1, LINHAS):
        for c in range(COLUNAS - SEQUENCIA_VITORIA + 1):
            janela = [tabuleiro[l - i][c + i] for i in range(SEQUENCIA_VITORIA)]
            pontos += avaliar_janela(janela, peca)

    return pontos


def minimax(tabuleiro, profundidade, alfa, beta, maximizando, estatisticas, usar_poda=True):
    """Algoritmo Minimax com poda alfa-beta.

    Retorna uma tupla (valor, coluna):
    - valor: pontuação do tabuleiro do ponto de vista da IA;
    - coluna: melhor jogada encontrada (None em nós folha).

    alfa = melhor valor que MAX (IA) já garantiu no caminho até aqui.
    beta = melhor valor que MIN (humano) já garantiu no caminho até aqui.
    Quando alfa >= beta, o resto dos filhos não muda a decisão e é podado.
    """
    # Conta cada estado visitado, para comparar com e sem poda
    estatisticas["nos"] += 1

    # TESTE TERMINAL e função UTILIDADE
    if venceu(tabuleiro, IA):
        # Soma a profundidade restante: vencer mais cedo vale mais
        return VALOR_VITORIA + profundidade, None
    if venceu(tabuleiro, HUMANO):
        # Subtrai a profundidade restante: perder mais tarde é menos ruim
        return -(VALOR_VITORIA + profundidade), None
    if tabuleiro_cheio(tabuleiro):
        return 0, None  # empate

    # Limite de profundidade: usa a heurística no lugar da utilidade real
    if profundidade == 0:
        return heuristica(tabuleiro, IA), None

    # Ações possíveis, testando primeiro as colunas centrais
    validas = jogadas_validas(tabuleiro)
    colunas = [c for c in ORDEM_COLUNAS if c in validas]
    melhor_coluna = colunas[0]

    if maximizando:
        # Vez da IA (MAX): procura o maior valor
        melhor_valor = -math.inf
        for coluna in colunas:
            filho = aplicar_jogada(tabuleiro, coluna, IA)
            valor, _ = minimax(filho, profundidade - 1, alfa, beta, False,
                               estatisticas, usar_poda)
            if valor > melhor_valor:
                melhor_valor, melhor_coluna = valor, coluna
            # Atualiza o melhor valor garantido para MAX
            alfa = max(alfa, melhor_valor)
            # Poda: MIN já tem opção melhor em outro galho, então para aqui
            if usar_poda and alfa >= beta:
                break
        return melhor_valor, melhor_coluna

    # Vez do humano (MIN): procura o menor valor
    melhor_valor = math.inf
    for coluna in colunas:
        filho = aplicar_jogada(tabuleiro, coluna, HUMANO)
        valor, _ = minimax(filho, profundidade - 1, alfa, beta, True,
                           estatisticas, usar_poda)
        if valor < melhor_valor:
            melhor_valor, melhor_coluna = valor, coluna
        # Atualiza o melhor valor garantido para MIN
        beta = min(beta, melhor_valor)
        # Poda: MAX já tem opção melhor em outro galho, então para aqui
        if usar_poda and alfa >= beta:
            break
    return melhor_valor, melhor_coluna


def escolher_jogada(tabuleiro, profundidade, usar_poda=True):
    """Ponto de entrada da IA: devolve (coluna escolhida, nós visitados).

    Deve ser chamada só com o jogo em andamento e profundidade >= 1;
    caso contrário não há jogada a escolher.
    """
    # Garante o uso correto: sem profundidade a busca não escolhe coluna
    if profundidade < 1:
        raise ValueError("A profundidade da busca deve ser pelo menos 1")
    # Dicionário mutável para o minimax ir somando os nós visitados
    estatisticas = {"nos": 0}
    _, coluna = minimax(tabuleiro, profundidade, -math.inf, math.inf, True,
                        estatisticas, usar_poda)
    return coluna, estatisticas["nos"]
