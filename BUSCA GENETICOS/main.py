import numpy as np
import cidades
import fitness
import thanos

x = cidades.CIDADES[0]
y = cidades.CIDADES[1]

Ncidade = cidades.CIDADES.shape[1]

Npop = 20
pop = np.array([
    np.random.permutation(np.arange(1, Ncidade + 1))
    for _ in range(Npop)
])

# Calcula o fitness
fit = fitness.cvfun(pop, x, y)
individuos = thanos.atribuir_idx(Npop, fit)
individuos_ordenados = thanos.ordenar(individuos)
melhores_idx = thanos.corta_melhores(individuos_ordenados)
thanos = thanos.thanos(pop, melhores_idx)
print("TESTE: ", thanos)
