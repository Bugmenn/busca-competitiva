"""Inteligência artificial das damas: Minimax com poda alfa-beta.

A IA é o jogador MAX (quer o maior valor) e o adversário é o jogador MIN
(quer o menor valor). A árvore completa do jogo é grande demais, então a
busca para numa profundidade limite e usa uma função de avaliação
(heurística) para estimar quem está melhor naquele tabuleiro.
"""

import math

from . import tipo_peca
from .regras import (LIMITE_EMPATE, aplicar_movimento, atualizar_contador, copiar,
                     inimigo, movimentos_validos)
from .tabuleiro import TAMANHO
from .tipo_peca import VAZIO

# Valor de uma vitória: maior que qualquer pontuação da heurística
VALOR_VITORIA = 1_000_000

# Pesos da função de avaliação
VALOR_PEAO = 100        # cada peão
VALOR_DAMA = 300        # dama vale 3 peões: anda e captura à distância
BONUS_AVANCO = 5        # por fileira que o peão já avançou (perto de virar dama)
BONUS_CENTRO = 10       # peça nas 4 colunas e 4 linhas centrais controla mais casas

# Profundidade de busca (em lances) para cada nível de dificuldade
DIFICULDADES = {"facil": 2, "medio": 4, "dificil": 6}


def avaliar(tab, cor_ia):
    """Heurística: pontuação do tabuleiro do ponto de vista da IA."""
    pontos = 0
    for l in range(TAMANHO):
        for c in range(TAMANHO):
            peca = tab[l][c]
            if peca == VAZIO:
                continue
            cor = tipo_peca.cor_da_peca(peca)
            if tipo_peca.e_dama(peca):
                valor = VALOR_DAMA
            else:
                # Quantas fileiras o peão já andou desde o seu lado do tabuleiro
                avanco = l if cor == "branca" else (TAMANHO - 1 - l)
                valor = VALOR_PEAO + avanco * BONUS_AVANCO
            # Bônus para peças no centro do tabuleiro
            if 2 <= l <= 5 and 2 <= c <= 5:
                valor += BONUS_CENTRO
            # Peça da IA soma, peça do adversário subtrai
            pontos += valor if cor == cor_ia else -valor
    return pontos


def _ordenar(tab, movimentos):
    """Testa primeiro os lances mais promissores para a poda cortar mais.

    Prioridade: capturar mais peças, depois promover um peão a dama.
    """
    def chave(mov):
        peca = tab[mov.origem[0]][mov.origem[1]]
        linha_final = mov.destinos[-1][0]
        # Última fileira de cada cor: 8 (índice 7) para brancas, 1 (índice 0) para pretas
        fileira_dama = TAMANHO - 1 if tipo_peca.cor_da_peca(peca) == "branca" else 0
        promove = (not tipo_peca.e_dama(peca)) and linha_final == fileira_dama
        # sorted() coloca menores primeiro, então os valores vão negativos
        return (-len(mov.capturadas), -int(promove))
    return sorted(movimentos, key=chave)


def minimax(tab, vez, contador, profundidade, alfa, beta, cor_ia, estatisticas, usar_poda=True):
    """Minimax com poda alfa-beta.

    Parâmetros:
    - tab, vez, contador: o ESTADO (tabuleiro, de quem é a vez, contador de empate);
    - profundidade: quantos lances ainda podemos olhar à frente;
    - alfa: melhor valor que MAX (IA) já tem garantido neste caminho;
    - beta: melhor valor que MIN (adversário) já tem garantido neste caminho;
    - estatisticas: dicionário que conta os nós visitados.

    Devolve (valor, melhor_movimento). Quando alfa >= beta, os filhos que
    faltam não podem mudar a decisão e são podados (não são visitados).
    """
    estatisticas["nos"] += 1

    # TESTE TERMINAL e função UTILIDADE
    if contador >= LIMITE_EMPATE:
        return 0, None  # empate
    movimentos = movimentos_validos(tab, vez)
    if not movimentos:
        # Quem está na vez sem jogadas perde. A profundidade restante faz a IA
        # preferir vencer mais cedo e, se for perder, perder mais tarde.
        if vez == cor_ia:
            return -(VALOR_VITORIA + profundidade), None
        return VALOR_VITORIA + profundidade, None

    # Limite de profundidade: estima o valor com a heurística
    if profundidade == 0:
        return avaliar(tab, cor_ia), None

    maximizando = vez == cor_ia
    melhor_valor = -math.inf if maximizando else math.inf
    movimentos = _ordenar(tab, movimentos)
    melhor_mov = movimentos[0]

    for mov in movimentos:
        # Gera o estado sucessor numa cópia, sem mexer no tabuleiro atual
        novo_contador = atualizar_contador(contador, tab, mov)
        filho = copiar(tab)
        aplicar_movimento(filho, mov)
        valor, _ = minimax(filho, inimigo(vez), novo_contador, profundidade - 1,
                           alfa, beta, cor_ia, estatisticas, usar_poda)

        if maximizando:
            # Vez da IA (MAX): fica com o maior valor
            if valor > melhor_valor:
                melhor_valor, melhor_mov = valor, mov
            alfa = max(alfa, melhor_valor)
        else:
            # Vez do adversário (MIN): fica com o menor valor
            if valor < melhor_valor:
                melhor_valor, melhor_mov = valor, mov
            beta = min(beta, melhor_valor)

        # Poda alfa-beta: o outro jogador já tem opção melhor em outro galho
        if usar_poda and alfa >= beta:
            break

    return melhor_valor, melhor_mov


def escolher_jogada(tab, vez, contador, profundidade, usar_poda=True):
    """Ponto de entrada da IA. Devolve (movimento escolhido, nós visitados).

    A IA joga com a cor `vez`. Deve ser chamada com o jogo em andamento.
    """
    # Sem profundidade a busca não chega a escolher nenhum lance
    if profundidade < 1:
        raise ValueError("A profundidade da busca deve ser pelo menos 1")
    estatisticas = {"nos": 0}
    _, mov = minimax(tab, vez, contador, profundidade, -math.inf, math.inf,
                     vez, estatisticas, usar_poda)
    return mov, estatisticas["nos"]
