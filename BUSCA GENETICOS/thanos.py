import numpy as np

def thanos(pop, melhores_idx):
    tamanho = len(melhores_idx)
    melhores = np.empty((tamanho, pop.shape[1]), dtype=int)
    count = 0
    for i in melhores_idx:
        item = i[0]
        melhores[count] = pop[item]
        count += 1
    return melhores

def corta_melhores(individuos):
    return individuos[:10]

def atribuir_idx(Npop, fit):8