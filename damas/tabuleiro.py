"""Tabuleiro 8x8: criação da posição inicial, contagem e desenho no terminal.

Coordenadas internas: (linha, coluna), de 0 a 7.
- linha 0 é a fileira "1" (lado das brancas, embaixo no desenho);
- coluna 0 é a coluna "a".
Pela regra oficial, a casa a1 (0, 0) é escura e as peças ficam só nas
casas escuras, que são as que têm linha + coluna par.
"""

import os
import sys

from . import tipo_peca
from .tipo_peca import VAZIO

TAMANHO = 8
LETRAS = "abcdefgh"

# Cores ANSI de fundo (256 cores) para cada tipo de casa
FUNDO_CLARO = "\033[48;5;223m"     # bege
FUNDO_ESCURO = "\033[48;5;130m"    # marrom
FUNDO_JOGADA = "\033[48;5;28m"     # verde: casas por onde a última peça passou
FUNDO_CAPTURA = "\033[48;5;124m"   # vermelho: casas das peças capturadas
TEXTO_BRANCAS = "\033[1;97m"       # símbolo da peça em branco e negrito
TEXTO_PRETAS = "\033[1;30m"        # símbolo da peça em preto e negrito
RESET = "\033[0m"                  # volta às cores normais do terminal


def casa_escura(linha, coluna):
    """As peças só ocupam as casas escuras (a1 é escura)."""
    return (linha + coluna) % 2 == 0


def criar_tabuleiro():
    """ESTADO INICIAL: 12 peças brancas nas linhas 1-3 e 12 pretas nas 6-8."""
    # Começa com todas as casas vazias
    tabuleiro = [[VAZIO for _ in range(TAMANHO)] for _ in range(TAMANHO)]
    for linha in range(TAMANHO):
        for coluna in range(TAMANHO):
            # Casas claras nunca recebem peça
            if not casa_escura(linha, coluna):
                continue
            if linha < 3:
                tabuleiro[linha][coluna] = tipo_peca.TipoPeca.PEAO_BRANCO.value
            elif linha >= TAMANHO - 3:
                tabuleiro[linha][coluna] = tipo_peca.TipoPeca.PEAO_PRETO.value
    return tabuleiro


def contar_pecas(tabuleiro, cor):
    """Quantas peças (peões + damas) a cor ainda tem no tabuleiro."""
    return sum(1 for linha in tabuleiro for casa in linha
               if tipo_peca.cor_da_peca(casa) == cor)


def usar_cores():
    """Usa cores só num terminal de verdade e se o usuário não pediu NO_COLOR."""
    return sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def ativar_cores_windows():
    """No Windows, um comando vazio liga o suporte às cores ANSI no console."""
    if os.name == "nt":
        os.system("")


def _casa_texto(peca, linha, coluna, cor, passou, capturada):
    """Monta os 3 caracteres de uma casa (com ou sem cores)."""
    # Peça no centro da casa, ou espaço se estiver vazia
    simbolo = peca if peca != VAZIO else " "

    if not cor:
        # Sem cores: as casas ainda ficam grudadas, com 3 caracteres cada
        if not casa_escura(linha, coluna):
            return "░░░"                       # casa clara
        if capturada:
            return " x "                       # peça capturada no último lance
        if passou and peca != VAZIO:
            return f"[{simbolo}]"              # peça que acabou de se mover
        if passou:
            return " * "                       # casa de origem / caminho
        return f" {simbolo} "

    # Com cores: o fundo pinta a casa e o símbolo da peça fica por cima
    if not casa_escura(linha, coluna):
        fundo = FUNDO_CLARO
    elif capturada:
        fundo = FUNDO_CAPTURA
    elif passou:
        fundo = FUNDO_JOGADA
    else:
        fundo = FUNDO_ESCURO
    cor_texto = TEXTO_BRANCAS if tipo_peca.cor_da_peca(peca) == "branca" else TEXTO_PRETAS
    return f"{fundo}{cor_texto} {simbolo} {RESET}"


def texto_tabuleiro(tabuleiro, ultimo_movimento=None, cor=None):
    """Devolve o desenho do tabuleiro como texto.

    ultimo_movimento (opcional) destaca a peça que acabou de jogar:
    origem e casas de pouso em verde, peças capturadas em vermelho.
    """
    if cor is None:
        cor = usar_cores()

    # Casas a destacar por causa do último lance
    passou, capturadas = set(), set()
    if ultimo_movimento is not None:
        passou = {ultimo_movimento.origem, *ultimo_movimento.destinos}
        capturadas = set(ultimo_movimento.capturadas)

    # Cabeçalho com as letras das colunas, cada uma no centro da sua casa
    cabecalho = "   " + "".join(f" {letra} " for letra in LETRAS)
    linhas = [cabecalho]
    # A linha 8 é desenhada em cima e a linha 1 embaixo (brancas na frente)
    for linha in range(TAMANHO - 1, -1, -1):
        casas = "".join(
            _casa_texto(tabuleiro[linha][coluna], linha, coluna, cor,
                        (linha, coluna) in passou, (linha, coluna) in capturadas)
            for coluna in range(TAMANHO))
        linhas.append(f" {linha + 1} {casas} {linha + 1}")
    linhas.append(cabecalho)
    return "\n".join(linhas)


def desenhar_tabuleiro(tabuleiro, ultimo_movimento=None):
    """Mostra o tabuleiro no terminal."""
    print()
    print(texto_tabuleiro(tabuleiro, ultimo_movimento))
    print()
