import numpy as np


# Recombinação "cycle" (Figura 1 do enunciado)
# Recebe os dois pais e a posição sorteada; devolve os dois filhos
def cycle_crossover(pai1, pai2, pos):
    # Os filhos começam como cópias dos pais (não altera os pais)
    filho1 = np.array(pai1, copy=True)
    filho2 = np.array(pai2, copy=True)

    while True:
        # Passo 1: troca os genes dos dois filhos na posição atual
        filho1[pos], filho2[pos] = filho2[pos], filho1[pos]

        # Procura o valor recém-trocado repetido em OUTRA posição do filho 1
        repetidos = np.where(filho1 == filho1[pos])[0]
        outras = repetidos[repetidos != pos]

        # Sem duplicado: os dois filhos já são permutações válidas
        if len(outras) == 0:
            break

        # Passos 2, 3, 4...: a próxima troca é na posição do duplicado
        pos = int(outras[0])

    return filho1, filho2
