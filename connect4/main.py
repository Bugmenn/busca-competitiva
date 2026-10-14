"""Partida de Connect 4 no terminal: humano (X) contra a IA (O)."""

import time

from .ia import DIFICULDADES, escolher_jogada
from .tabuleiro import (COLUNAS, HUMANO, IA, aplicar_jogada, coluna_valida,
                        criar_tabuleiro, desenhar, tabuleiro_cheio, venceu)


def perguntar_opcao(mensagem, opcoes):
    """Repete a pergunta até o usuário digitar uma das opções válidas."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes:
            return resposta
        print(f"Opção inválida. Digite uma destas: {', '.join(opcoes)}")


def ler_coluna_humano(tabuleiro):
    """Lê a coluna escolhida pelo humano e valida a entrada."""
    while True:
        texto = input(f"Sua vez (X). Escolha a coluna de 1 a {COLUNAS}: ").strip()
        # Rejeita texto que não seja número (int() falha com letras ou símbolos)
        try:
            # O jogador vê colunas 1..7; internamente usamos 0..6
            coluna = int(texto) - 1
        except ValueError:
            print("Digite apenas o número da coluna.")
            continue
        if not 0 <= coluna < COLUNAS:
            print(f"A coluna precisa estar entre 1 e {COLUNAS}.")
            continue
        if not coluna_valida(tabuleiro, coluna):
            print("Essa coluna está cheia. Escolha outra.")
            continue
        return coluna


def jogar():
    """Laço principal da partida."""
    print("=== CONNECT 4 — Humano (X) x IA (O) ===")
    print("Vence quem alinhar 4 peças na horizontal, vertical ou diagonal.\n")

    # Configurações da partida
    nivel = perguntar_opcao("Dificuldade (facil/medio/dificil): ", list(DIFICULDADES))
    profundidade = DIFICULDADES[nivel]
    quem_comeca = perguntar_opcao("Quem começa? (eu/ia): ", ["eu", "ia"])
    vez = HUMANO if quem_comeca == "eu" else IA

    # ESTADO INICIAL: tabuleiro vazio
    tabuleiro = criar_tabuleiro()

    # Alterna as jogadas até o teste terminal ser verdadeiro
    while True:
        print("\n" + desenhar(tabuleiro) + "\n")

        if vez == HUMANO:
            coluna = ler_coluna_humano(tabuleiro)
            tabuleiro = aplicar_jogada(tabuleiro, coluna, HUMANO)
        else:
            print("IA pensando...")
            inicio = time.perf_counter()
            coluna, nos = escolher_jogada(tabuleiro, profundidade)
            tempo = time.perf_counter() - inicio
            tabuleiro = aplicar_jogada(tabuleiro, coluna, IA)
            print(f"IA jogou na coluna {coluna + 1} "
                  f"({nos} estados analisados em {tempo:.2f}s)")

        # Verifica se a última jogada encerrou o jogo
        if venceu(tabuleiro, vez):
            print("\n" + desenhar(tabuleiro) + "\n")
            print("Você venceu!" if vez == HUMANO else "A IA venceu!")
            return
        if tabuleiro_cheio(tabuleiro):
            print("\n" + desenhar(tabuleiro) + "\n")
            print("Empate! O tabuleiro encheu.")
            return

        # Passa a vez para o outro jogador
        vez = IA if vez == HUMANO else HUMANO


def main():
    """Executa o jogo tratando Ctrl+C e fim de entrada sem mostrar erro."""
    try:
        jogar()
    except (KeyboardInterrupt, EOFError):
        print("\nJogo encerrado.")


if __name__ == "__main__":
    main()
