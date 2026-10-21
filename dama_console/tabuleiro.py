import tipo_peca
from tipo_peca import VAZIO

TAMANHO = 8


def criar_tabuleiro():
    tabuleiro = [[VAZIO for _ in range(TAMANHO)] for _ in range(TAMANHO)]
    for linha in range(3):
        for coluna in range(TAMANHO):
            if (linha + coluna) % 2 == 1:
                tabuleiro[linha][coluna] = tipo_peca.TipoPeca.PEAO_BRANCO.value
    for linha in range(TAMANHO - 3, TAMANHO):
        for coluna in range(TAMANHO):
            if (linha + coluna) % 2 == 1:
                tabuleiro[linha][coluna] = tipo_peca.TipoPeca.PEAO_PRETO.value
    return tabuleiro


def desenhar_tabuleiro(tabuleiro):
    print("\n   a b c d e f g h")
    for i, linha in enumerate(tabuleiro):
        print(f"{i + 1}  " + " ".join(linha) + f"  {i + 1}")
    print("   a b c d e f g h\n")


def contar_pecas(tabuleiro, cor):
    return sum(1 for linha in tabuleiro for casa in linha
               if tipo_peca.cor_da_peca(casa) == cor)
