import numpy as np


# Mutação por troca: escolhe duas posições diferentes e troca as cidades
def mutar(cromossomo):
    # Cópia para não alterar o cromossomo original
    mutado = np.array(cromossomo, copy=True)

    # Sorteia duas posições distintas do cromossomo
    i, j = np.random.choice(len(mutado), size=2, replace=False)

    # Troca as duas cidades de lugar
    mutado[i], mutado[j] = mutado[j], mutado[i]

    return mutado
