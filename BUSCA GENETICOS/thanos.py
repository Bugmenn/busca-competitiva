import numpy as np

# Monta a matriz só com os indivíduos sobreviventes (a metade que é mantida)
def thanos(pop, melhores_idx):
    # Quantidade de sobreviventes
    tamanho = len(melhores_idx)
    # Matriz vazia: uma linha por sobrevivente, uma coluna por cidade
    melhores = np.empty((tamanho, pop.shape[1]), dtype=int)
    # Linha da matriz nova que está sendo preenchida
    count = 0
    for i in melhores_idx:
        # i = (índice na população, custo); pega só o índice
        item = i[0]
        # Copia o cromossomo sobrevivente para a matriz nova
        melhores[count] = pop[item]
        count += 1
    return melhores

# Fica com os 10 primeiros da lista ordenada (metade de uma população de 20)
def corta_melhores(individuos):
    return individuos[:10]

# Junta cada indivíduo ao seu custo: lista de (índice, custo)
def atribuir_idx(Npop, fit):
    individuos = [
        (
            i,
            float(fit[i])
        )
        for i in range(Npop)
    ]
    return individuos

# Ordena do menor custo (mais apto) para o maior custo (menos apto)
def ordenar(individuos):
    return sorted(individuos, key=lambda x: x[1])
