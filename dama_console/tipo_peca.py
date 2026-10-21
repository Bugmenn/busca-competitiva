from enum import Enum


class TipoPeca(Enum):
    PEAO_BRANCO = 'b'
    PEAO_PRETO = 'p'
    DAMA_BRANCA = 'B'
    DAMA_PRETA = 'P'


VAZIO = "□"
BRANCAS = (TipoPeca.PEAO_BRANCO.value, TipoPeca.DAMA_BRANCA.value)
PRETAS = (TipoPeca.PEAO_PRETO.value, TipoPeca.DAMA_PRETA.value)
DAMAS = (TipoPeca.DAMA_BRANCA.value, TipoPeca.DAMA_PRETA.value)


def cor_da_peca(peca):
    if peca in BRANCAS:
        return "branca"
    if peca in PRETAS:
        return "preta"
    return None


def e_dama(peca):
    return peca in DAMAS
