"""Regras da dama brasileira: jogadas válidas, aplicação de jogada e fim de jogo.

Este módulo é a FUNÇÃO SUCESSOR do problema de busca: dado o tabuleiro e
de quem é a vez, diz quais jogadas existem e como fica o tabuleiro depois.

Regras implementadas:
- peão anda 1 casa na diagonal, só para a frente;
- captura é obrigatória, e o peão também captura para trás;
- dama anda e captura à distância ("dama voadora");
- lei da maioria: é obrigatório o lance que captura mais peças;
- uma peça não pode ser capturada duas vezes no mesmo lance, e as
  capturadas só saem do tabuleiro quando o lance termina;
- o peão só vira dama se TERMINAR o lance na última linha;
- empate depois de 20 lances seguidos só de damas, sem nenhuma captura.
"""

from dataclasses import dataclass

from . import tipo_peca
from .tabuleiro import TAMANHO
from .tipo_peca import VAZIO

# As 4 direções diagonais: (variação da linha, variação da coluna)
DIAGONAIS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# Lances seguidos só de damas, sem captura, que encerram a partida em empate
LIMITE_EMPATE = 20


@dataclass
class Movimento:
    """Uma jogada completa (pode ter várias capturas em sequência)."""
    origem: tuple       # casa de onde a peça sai
    destinos: list      # casas de pouso, em ordem (a última é a final)
    capturadas: list    # casas das peças capturadas


def dentro(l, c):
    """A casa (l, c) existe no tabuleiro?"""
    return 0 <= l < TAMANHO and 0 <= c < TAMANHO


def inimigo(cor):
    """Cor do adversário."""
    return "preta" if cor == "branca" else "branca"


def copiar(tab):
    """Cópia independente do tabuleiro (a IA simula jogadas na cópia)."""
    return [linha[:] for linha in tab]


def _capturas(tab, origem, peca, cor, pos, capturadas, destinos, resultado):
    """Busca em profundidade de todas as sequências de captura.

    pos é onde a peça está agora durante a sequência. As peças capturadas
    continuam no tabuleiro até o fim do lance (não dá para pular a mesma
    peça duas vezes nem passar por cima dela).
    """
    achou = False  # alguma captura a mais foi possível a partir de pos?
    for dl, dc in DIAGONAIS:
        l, c = pos[0] + dl, pos[1] + dc
        if tipo_peca.e_dama(peca):
            # A dama desliza pelas casas vazias até encontrar uma peça.
            # A casa de origem conta como vazia, porque a dama saiu dela.
            while dentro(l, c) and (tab[l][c] == VAZIO or (l, c) == origem):
                l, c = l + dl, c + dc
        if not dentro(l, c):
            continue
        # Só captura peça do adversário que ainda não foi capturada neste lance
        if tipo_peca.cor_da_peca(tab[l][c]) != inimigo(cor) or (l, c) in capturadas:
            continue
        alvo = (l, c)
        # A peça pousa logo depois da capturada (a dama pode pousar mais longe)
        pouso_l, pouso_c = l + dl, c + dc
        while dentro(pouso_l, pouso_c) and (tab[pouso_l][pouso_c] == VAZIO or (pouso_l, pouso_c) == origem):
            achou = True
            # Continua procurando capturas a partir da casa de pouso
            _capturas(tab, origem, peca, cor, (pouso_l, pouso_c),
                      capturadas + [alvo], destinos + [(pouso_l, pouso_c)], resultado)
            if not tipo_peca.e_dama(peca):
                break  # o peão só pode pousar na casa logo após a capturada
            pouso_l, pouso_c = pouso_l + dl, pouso_c + dc
    # Se não dá para capturar mais nada, a sequência atual é um lance completo
    if not achou and capturadas:
        resultado.append(Movimento(origem, destinos, capturadas))


def _movimentos_simples(tab, origem, peca, cor):
    """Jogadas sem captura: peão 1 casa para a frente, dama quantas quiser."""
    resultado = []
    l0, c0 = origem
    for dl, dc in DIAGONAIS:
        # Peão branco sobe (linha +1) e peão preto desce (linha -1)
        if not tipo_peca.e_dama(peca) and dl != (1 if cor == "branca" else -1):
            continue
        l, c = l0 + dl, c0 + dc
        while dentro(l, c) and tab[l][c] == VAZIO:
            resultado.append(Movimento(origem, [(l, c)], []))
            if not tipo_peca.e_dama(peca):
                break  # o peão anda só uma casa
            l, c = l + dl, c + dc
    return resultado


def movimentos_validos(tab, cor):
    """FUNÇÃO SUCESSOR: lista de jogadas permitidas para a cor."""
    capturas, simples = [], []
    for l in range(TAMANHO):
        for c in range(TAMANHO):
            peca = tab[l][c]
            if tipo_peca.cor_da_peca(peca) != cor:
                continue
            _capturas(tab, (l, c), peca, cor, (l, c), [], [], capturas)
            simples += _movimentos_simples(tab, (l, c), peca, cor)
    if capturas:
        # Captura obrigatória + lei da maioria: só valem as que capturam mais
        maior = max(len(m.capturadas) for m in capturas)
        return [m for m in capturas if len(m.capturadas) == maior]
    return simples


def aplicar_movimento(tab, mov):
    """Executa a jogada ALTERANDO o tabuleiro recebido (use copiar() antes)."""
    l0, c0 = mov.origem
    lf, cf = mov.destinos[-1]
    peca = tab[l0][c0]
    tab[l0][c0] = VAZIO
    # As peças capturadas só saem agora, no fim do lance
    for l, c in mov.capturadas:
        tab[l][c] = VAZIO
    # Promoção: peão que termina o lance na última linha vira dama
    if peca == tipo_peca.TipoPeca.PEAO_BRANCO.value and lf == TAMANHO - 1:
        peca = tipo_peca.TipoPeca.DAMA_BRANCA.value
    elif peca == tipo_peca.TipoPeca.PEAO_PRETO.value and lf == 0:
        peca = tipo_peca.TipoPeca.DAMA_PRETA.value
    tab[lf][cf] = peca


def atualizar_contador(contador, tab, mov):
    """Novo valor do contador de empate depois da jogada.

    Chamar ANTES de aplicar a jogada (precisa saber qual peça se moveu).
    Zera quando há captura ou quando um peão se move; soma 1 quando uma
    dama se move sem capturar.
    """
    peca = tab[mov.origem[0]][mov.origem[1]]
    if mov.capturadas or not tipo_peca.e_dama(peca):
        return 0
    return contador + 1


def resultado(tab, vez, contador):
    """TESTE TERMINAL. Devolve None se o jogo continua, senão:
    "empate" ou a cor vencedora ("branca"/"preta").

    Quem está na vez e não tem jogada (sem peças ou bloqueado) perde.
    """
    if contador >= LIMITE_EMPATE:
        return "empate"
    if not movimentos_validos(tab, vez):
        return inimigo(vez)
    return None
