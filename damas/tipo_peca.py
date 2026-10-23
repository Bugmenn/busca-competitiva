"""Tipos de peça do jogo de damas e funções para identificá-las."""

from enum import Enum


class TipoPeca(Enum):
    """Cada peça é guardada no tabuleiro como uma letra."""
    PEAO_BRANCO = 'b'  # peão (pedra comum) das brancas
    PEAO_PRETO = 'p'   # peão das pretas
    DAMA_BRANCA = 'B'  # peão branco que chegou à última linha
    DAMA_PRETA = 'P'   # peão preto que chegou à última linha


# Símbolo de uma casa sem peça
VAZIO = "□"

# Grupos de peças, para perguntar "de que cor é?" e "é dama?"
BRANCAS = (TipoPeca.PEAO_BRANCO.value, TipoPeca.DAMA_BRANCA.value)
PRETAS = (TipoPeca.PEAO_PRETO.value, TipoPeca.DAMA_PRETA.value)
DAMAS = (TipoPeca.DAMA_BRANCA.value, TipoPeca.DAMA_PRETA.value)


def cor_da_peca(peca):
    """Devolve "branca", "preta" ou None (casa vazia)."""
    if peca in BRANCAS:
        return "branca"
    if peca in PRETAS:
        return "preta"
    return None


def e_dama(peca):
    """Diz se a peça é uma dama (anda e captura várias casas na diagonal)."""
    return peca in DAMAS
