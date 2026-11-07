
import numpy as np

# Função de custo (fitness) para o problema do Caixeiro Viajante
def cvfun(pop, x, y):

    # Obtém as dimensões da população
    Npop, Ncidade = pop.shape

    # Gera a matriz de rotas adicionando a primeira cidade
    # ao final de cada indivíduo, garantindo o retorno à origem
    tour = np.column_stack((pop, pop[:, 0]))

    # Matriz de distâncias entre as cidades
    dcidade = np.zeros((Ncidade, Ncidade))

    # Calcula a distância entre todas as cidades
    for i in range(Ncidade):
        for j in range(Ncidade):
            dcidade[i, j] = np.sqrt(
                (x[i] - x[j])**2 + (y[i] - y[j])**2
            )

    # Calcula o custo de cada cromossomo (indivíduo)
    dist = np.zeros(Npop)

    for i in range(Npop):
        dist[i] = 0

        for j in range(Ncidade):
            # Soma as distâncias entre cidades consecutivas
            cidade_atual = int(tour[i, j]) - 1
            proxima_cidade = int(tour[i, j + 1]) - 1

            dist[i] += dcidade[cidade_atual, proxima_cidade]

    return dist