"""Partida de damas no terminal: humano contra a IA."""

import random
import sys
import time

from . import regras
from . import tabuleiro as tb
from .ia import DIFICULDADES, escolher_jogada

# Cada jogador começa com 12 peças
PECAS_INICIAIS = 12


def parse_casa(texto):
    """Converte "c3" em (linha, coluna) = (2, 2). Erro se a casa não existir."""
    if len(texto) != 2 or texto[0] not in tb.LETRAS or texto[1] not in "12345678":
        raise ValueError(f"Casa inválida: {texto}")
    return int(texto[1]) - 1, tb.LETRAS.index(texto[0])


def nome_casa(casa):
    """Converte (linha, coluna) em texto, por exemplo (2, 2) -> "c3"."""
    return tb.LETRAS[casa[1]] + str(casa[0] + 1)


def descrever(mov):
    """Texto de uma jogada, por exemplo "c3 -> e5 -> g7 (capturou 2)"."""
    texto = " -> ".join(nome_casa(c) for c in [mov.origem] + mov.destinos)
    if mov.capturadas:
        texto += f" (capturou {len(mov.capturadas)})"
    return texto


def escolher_no_menu(titulo, opcoes):
    """Mostra um menu numerado e devolve o valor da opção escolhida.

    opcoes é uma lista de pares (texto mostrado, valor devolvido).
    O jogador digita só o número; qualquer outra coisa repete a pergunta.
    """
    print(titulo)
    for numero, (texto, _) in enumerate(opcoes, start=1):
        print(f"  {numero}) {texto}")
    while True:
        entrada = input(f"Escolha (1-{len(opcoes)}): ").strip()
        try:
            numero = int(entrada)
        except ValueError:
            numero = 0  # texto que não é número: trata como opção inválida
        if 1 <= numero <= len(opcoes):
            return opcoes[numero - 1][1]
        print(f"Digite um número de 1 a {len(opcoes)}.")


def escolher_cor():
    """Pergunta a cor do jogador, com opção de sortear. Devolve "branca" ou "preta"."""
    cor = escolher_no_menu("Sua cor:", [("Brancas (começam)", "branca"),
                                        ("Pretas", "preta"),
                                        ("Sortear", "sortear")])
    if cor == "sortear":
        cor = random.choice(["branca", "preta"])
        print(f"Sorteio: você joga com as {cor}s.")
    return cor


def ler_casas(entrada):
    """Converte o texto digitado em uma lista de casas (linha, coluna).

    Aceita "c3 d4" e também os formatos comuns "c3-d4", "c3xd4", "c3,d4" e "c3d4".
    """
    # Hífen, "x" e vírgula viram espaço ("x" não é letra de coluna, a-h)
    texto = entrada.replace("-", " ").replace("x", " ").replace(",", " ")
    partes = []
    for parte in texto.split():
        # "c3d4" sem separador: corta o texto de 2 em 2 caracteres
        if len(parte) > 2 and len(parte) % 2 == 0:
            partes += [parte[i:i + 2] for i in range(0, len(parte), 2)]
        else:
            partes.append(parte)
    return [parse_casa(p) for p in partes]


# Resposta especial de continuar_captura: o jogador quer refazer a jogada
VOLTAR = "voltar"


def continuar_captura(candidatos, casas):
    """Continua uma captura múltipla a partir de onde a peça parou.

    Enquanto todos os caminhos possíveis seguem para a mesma casa, a peça
    avança sozinha (a captura é obrigatória). Quando o caminho se divide,
    o jogador escolhe só a próxima casa de pouso (ou várias de uma vez).
    Devolve o Movimento completo, VOLTAR para refazer a jogada, ou None
    se o jogador digitar "sair".
    """
    while len(candidatos) > 1:
        # Posição do próximo pouso dentro de m.destinos. Todos os candidatos
        # têm o mesmo tamanho (lei da maioria) e nenhum lance é começo de
        # outro, então esse índice sempre existe enquanto houver 2 ou mais.
        indice = len(casas) - 1
        proximas = {m.destinos[indice] for m in candidatos}
        if len(proximas) == 1:
            # Só existe uma casa para continuar: avança automaticamente
            casas = casas + [proximas.pop()]
            print(f"A captura seguiu sozinha para {nome_casa(casas[-1])} "
                  "(é o único caminho).")
            continue

        atual = nome_casa(casas[-1])
        entrada = input(f"A captura continua a partir de {atual}. Próxima casa "
                        "('voltar' refaz a jogada, 'sair' encerra): ").strip().lower()
        if entrada == "sair":
            return None
        if entrada == VOLTAR:
            return VOLTAR
        if not entrada:
            continue  # Enter sem nada: pergunta de novo
        try:
            seguintes = ler_casas(entrada)
        except ValueError as erro:
            print(f"{erro}. Digite a próxima casa onde a peça pousa.")
            continue
        # Mantém só os caminhos que passam pelas casas digitadas
        seguem = [m for m in candidatos
                  if m.destinos[indice:indice + len(seguintes)] == seguintes]
        if not seguem:
            print(f"A peça não pode continuar a captura de {atual} para {entrada}.")
            continue
        candidatos = seguem
        casas = casas + seguintes
    # Sobrou um único caminho: o resto da captura é feito automaticamente
    return candidatos[0]


def escolher_movimento(movimentos):
    """Lê a jogada do humano digitada pelas casas (ex: c3 d4).

    Numa captura múltipla, basta digitar o começo (ex: c3 e5): a captura
    obrigatória continua automaticamente. Se ela puder seguir por mais de
    um caminho, o jogo pergunta só a próxima casa (ou "voltar"). A lista de jogadas não
    é mostrada: o jogador precisa encontrar o lance.
    Devolve o Movimento escolhido, ou None se o jogador digitar "sair".
    """
    # Se houver captura, todas as jogadas válidas são capturas (é obrigatório)
    captura_obrigatoria = bool(movimentos[0].capturadas)
    # Casas das peças que podem jogar agora
    origens = {m.origem for m in movimentos}
    while True:
        entrada = input("Sua jogada (ex: c3 d4; captura múltipla: c3 e5 g7; "
                        "'sair' encerra): ").strip().lower()
        if entrada == "sair":
            return None

        # Converte cada casa digitada em (linha, coluna)
        try:
            casas = ler_casas(entrada)
        except ValueError as erro:
            print(f"{erro}. Digite as casas, por exemplo: c3 d4")
            continue
        if len(casas) < 2:
            print("Informe a casa de origem e a de destino, por exemplo: c3 d4")
            continue
        # Jogadas que começam na origem e passam pelas casas digitadas
        candidatos = [m for m in movimentos
                      if m.origem == casas[0] and m.destinos[:len(casas) - 1] == casas[1:]]
        exatos = [m for m in candidatos if len(m.destinos) == len(casas) - 1]
        if len(exatos) == 1:
            return exatos[0]
        if len(candidatos) == 1:
            return candidatos[0]  # começo do caminho já é único: completa sozinho
        if candidatos:
            # A captura é obrigatória e continua por mais de um caminho:
            # segue a partir de onde a peça parou, pedindo só a próxima casa
            mov = continuar_captura(candidatos, casas)
            if mov == VOLTAR:
                continue  # o jogador quer digitar a jogada de novo
            return mov  # Movimento escolhido, ou None se digitou "sair"

        # Explica o erro sem entregar a jogada
        origem = nome_casa(casas[0])
        if casas[0] not in origens and captura_obrigatoria:
            print("Jogada inválida: a captura é obrigatória e só valem as que pegam o "
                  f"maior número de peças; a partir de {origem} não há nenhuma dessas.")
        elif casas[0] not in origens:
            print(f"Jogada inválida: não há peça sua que possa jogar a partir de {origem}.")
        elif captura_obrigatoria:
            print("Caminho incorreto: digite a origem e cada casa onde a peça pousa "
                  "(não a casa da peça capturada), com o maior número de capturas.")
        else:
            print(f"Jogada inválida: a peça em {origem} não pode ir para essa casa.")


def mostrar_placar(tabuleiro):
    """Quantas peças cada lado já capturou do adversário."""
    brancas = PECAS_INICIAIS - tb.contar_pecas(tabuleiro, "preta")
    pretas = PECAS_INICIAIS - tb.contar_pecas(tabuleiro, "branca")
    print(f"Capturas  ->  Brancas: {brancas}  |  Pretas: {pretas}")


def jogar():
    """Laço principal da partida."""
    print("=== DAMAS (regra brasileira) — Humano x IA ===")
    print("Brancas (b/B) começam. Letra maiúscula = dama.\n")

    nivel = escolher_no_menu("Dificuldade:", [("Fácil", "facil"),
                                              ("Médio", "medio"),
                                              ("Difícil", "dificil")])
    profundidade = DIFICULDADES[nivel]
    print()
    humano = escolher_cor()

    # ESTADO INICIAL: posição de partida, brancas na vez, contador de empate zerado
    tabuleiro = tb.criar_tabuleiro()
    vez = "branca"
    contador = 0
    ultimo = None  # última jogada, para destacar no desenho

    while True:
        print()
        mostrar_placar(tabuleiro)
        tb.desenhar_tabuleiro(tabuleiro, ultimo)
        if ultimo is not None:
            quem = "Você jogou" if vez != humano else "IA jogou"
            print(f"{quem}: {descrever(ultimo)}\n")

        # TESTE TERMINAL
        fim = regras.resultado(tabuleiro, vez, contador)
        if fim == "empate":
            print(f"Empate: {regras.LIMITE_EMPATE} lances seguidos só de damas, sem captura.")
            return
        if fim is not None:
            print("Você venceu!" if fim == humano else "A IA venceu!")
            return

        movimentos = regras.movimentos_validos(tabuleiro, vez)
        aviso = " (captura obrigatória)" if movimentos[0].capturadas else ""
        if vez == humano:
            print(f"Sua vez ({vez}s){aviso}:")
            mov = escolher_movimento(movimentos)
            if mov is None:
                print("Jogo encerrado.")
                return
        else:
            print(f"IA pensando ({vez}s)...")
            inicio = time.perf_counter()
            mov, nos = escolher_jogada(tabuleiro, vez, contador, profundidade)
            tempo = time.perf_counter() - inicio
            print(f"IA analisou {nos} estados em {tempo:.2f}s")

        # Gera o próximo estado: contador de empate, tabuleiro e vez
        contador = regras.atualizar_contador(contador, tabuleiro, mov)
        regras.aplicar_movimento(tabuleiro, mov)
        ultimo = mov
        vez = regras.inimigo(vez)


def main():
    """Prepara o terminal e roda o jogo, saindo sem erro com Ctrl+C."""
    # Entrada e saída em UTF-8: acentos e símbolos do tabuleiro funcionam
    # também quando o jogo é usado por pipe ou arquivo
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    tb.ativar_cores_windows()
    try:
        jogar()
    except (KeyboardInterrupt, EOFError):
        print("\nJogo encerrado.")


if __name__ == "__main__":
    main()
