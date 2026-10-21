import regras
import tabuleiro as tb


def parse_casa(texto):
    if len(texto) != 2 or texto[0] not in "abcdefgh" or texto[1] not in "12345678":
        raise ValueError(f"casa inválida: {texto}")
    return int(texto[1]) - 1, "abcdefgh".index(texto[0])


def nome_casa(casa):
    return "abcdefgh"[casa[1]] + str(casa[0] + 1)


def escolher_movimento(movimentos):
    while True:
        entrada = input("Jogada (ex: c3 d4, ou c3 e5 g7 em capturas; 'sair'): ").strip().lower()
        if entrada == "sair":
            return None
        try:
            casas = [parse_casa(t) for t in entrada.split()]
        except ValueError as erro:
            print(erro)
            continue
        if len(casas) < 2:
            print("Informe origem e destino.")
            continue
        candidatos = [m for m in movimentos
                      if m.origem == casas[0] and m.destinos[:len(casas) - 1] == casas[1:]]
        exatos = [m for m in candidatos if len(m.destinos) == len(casas) - 1]
        if len(exatos) == 1:
            return exatos[0]
        if len(candidatos) == 1:
            return candidatos[0]
        if candidatos:
            print("Jogada ambígua, informe todas as casas do percurso.")
        else:
            print("Jogada inválida. Opções:")
            for m in movimentos:
                print("  " + " ".join(nome_casa(c) for c in [m.origem] + m.destinos))


def main():
    tabuleiro = tb.criar_tabuleiro()
    vez = "branca"
    while True:
        tb.desenhar_tabuleiro(tabuleiro)
        movimentos = regras.movimentos_validos(tabuleiro, vez)
        if not movimentos:
            print(f"Peças {regras.inimigo(vez)}s venceram!")
            return
        print(f"Vez das peças {vez}s" + (" (captura obrigatória)" if movimentos[0].capturadas else ""))
        mov = escolher_movimento(movimentos)
        if mov is None:
            return
        regras.aplicar_movimento(tabuleiro, mov)
        vez = regras.inimigo(vez)


if __name__ == "__main__":
    main()
