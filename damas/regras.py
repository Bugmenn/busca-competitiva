from dataclasses import dataclass

import tipo_peca
from tabuleiro import TAMANHO
from tipo_peca import VAZIO

DIAGONAIS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


@dataclass
class Movimento:
    origem: tuple
    destinos: list      # casas de pouso, em ordem
    capturadas: list    # casas das peças capturadas


def dentro(l, c):
    return 0 <= l < TAMANHO and 0 <= c < TAMANHO


def inimigo(cor):
    return "preta" if cor == "branca" else "branca"


def _capturas(tab, origem, peca, cor, pos, capturadas, destinos, resultado):
    """DFS de capturas. Peças capturadas só saem do tabuleiro ao fim do movimento."""
    achou = False
    for dl, dc in DIAGONAIS:
        l, c = pos[0] + dl, pos[1] + dc
        if tipo_peca.e_dama(peca):
            while dentro(l, c) and (tab[l][c] == VAZIO or (l, c) == origem):
                l, c = l + dl, c + dc
        if not dentro(l, c):
            continue
        if tipo_peca.cor_da_peca(tab[l][c]) != inimigo(cor) or (l, c) in capturadas:
            continue
        alvo = (l, c)
        pouso_l, pouso_c = l + dl, c + dc
        while dentro(pouso_l, pouso_c) and (tab[pouso_l][pouso_c] == VAZIO or (pouso_l, pouso_c) == origem):
            achou = True
            _capturas(tab, origem, peca, cor, (pouso_l, pouso_c),
                      capturadas + [alvo], destinos + [(pouso_l, pouso_c)], resultado)
            if not tipo_peca.e_dama(peca):
                break
            pouso_l, pouso_c = pouso_l + dl, pouso_c + dc
    if not achou and capturadas:
        resultado.append(Movimento(origem, destinos, capturadas))


def _movimentos_simples(tab, origem, peca, cor):
    resultado = []
    l0, c0 = origem
    for dl, dc in DIAGONAIS:
        if not tipo_peca.e_dama(peca) and dl != (1 if cor == "branca" else -1):
            continue
        l, c = l0 + dl, c0 + dc
        while dentro(l, c) and tab[l][c] == VAZIO:
            resultado.append(Movimento(origem, [(l, c)], []))
            if not tipo_peca.e_dama(peca):
                break
            l, c = l + dl, c + dc
    return resultado


def movimentos_validos(tab, cor):
    capturas, simples = [], []
    for l in range(TAMANHO):
        for c in range(TAMANHO):
            peca = tab[l][c]
            if tipo_peca.cor_da_peca(peca) != cor:
                continue
            _capturas(tab, (l, c), peca, cor, (l, c), [], [], capturas)
            simples += _movimentos_simples(tab, (l, c), peca, cor)
    if capturas:  # captura obrigatória, vale a lei da maioria
        maior = max(len(m.capturadas) for m in capturas)
        return [m for m in capturas if len(m.capturadas) == maior]
    return simples


def aplicar_movimento(tab, mov):
    l0, c0 = mov.origem
    lf, cf = mov.destinos[-1]
    peca = tab[l0][c0]
    tab[l0][c0] = VAZIO
    for l, c in mov.capturadas:
        tab[l][c] = VAZIO
    if peca == tipo_peca.TipoPeca.PEAO_BRANCO.value and lf == TAMANHO - 1:
        peca = tipo_peca.TipoPeca.DAMA_BRANCA.value
    elif peca == tipo_peca.TipoPeca.PEAO_PRETO.value and lf == 0:
        peca = tipo_peca.TipoPeca.DAMA_PRETA.value
    tab[lf][cf] = peca
