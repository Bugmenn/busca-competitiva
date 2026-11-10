import numpy as np


# Calcula a probabilidade de cada indivíduo mantido ser escolhido como pai
# (pesos lineares: o 1º do ranking tem o maior peso e o último, o menor)
def probabilidades(n_manter):
    # Pesos inversos à posição: n_manter, n_manter-1, ..., 1
    pesos = np.arange(n_manter, 0, -1)

    # Divide pela soma (1 + 2 + ... + n_manter) para que tudo some 1
    return pesos / pesos.sum()


# Gira a roleta e devolve o índice (no ranking) do pai sorteado
def sortear_pai(prob):
    # Soma acumulada: cada indivíduo ocupa uma "fatia" da roleta
    acumulada = np.cumsum(prob)

    # Número aleatório entre 0 e 1 (onde a roleta parou)
    r = np.random.rand()

    # Primeira fatia cuja soma acumulada alcança o número sorteado
    idx = int(np.searchsorted(acumulada, r))

    # Proteção contra arredondamento (soma acumulada 0.9999... < r)
    return min(idx, len(prob) - 1)
