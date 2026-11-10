import numpy as np
import matplotlib.pyplot as plt
import cidades
import fitness
import thanos
import roleta
import crossover
import mutacao

# Parâmetros do enunciado
NPOP = 20           # tamanho da população
N_ITER = 10000      # número de iterações (gerações)


# Executa o algoritmo genético e devolve tudo o que precisa ser mostrado
def executar_ag(x, y, Npop=NPOP, n_iter=N_ITER):
    # Número de cidades = número de coordenadas
    Ncidade = len(x)

    # Metade da população que sobrevive (derivada do tamanho recebido)
    n_manter = Npop // 2
    # Precisa de pelo menos 2 mantidos e de um número par de filhos
    if n_manter < 2 or (Npop - n_manter) % 2 != 0:
        raise ValueError("Npop deve ser múltiplo de 4 (ex.: 20)")

    # Cria a população inicial: cada indivíduo é uma permutação de 1 a Ncidade
    pop = np.array([
        np.random.permutation(np.arange(1, Ncidade + 1))
        for _ in range(Npop)
    ])

    # Guarda uma cópia da população inicial para mostrar no final
    pop_inicial = pop.copy()

    # Probabilidades da roleta (pesos lineares), calculadas uma vez só
    prob = roleta.probabilidades(n_manter)

    # Melhor custo de cada geração (para o gráfico de evolução)
    historico = []

    for geracao in range(n_iter):
        # Avalia: custo (distância total) de cada indivíduo
        fit = fitness.cvfun(pop, x, y)

        # Ordena do mais apto (menor distância) para o menos apto
        individuos = thanos.atribuir_idx(Npop, fit)
        individuos_ordenados = thanos.ordenar(individuos)

        # Guarda o melhor custo desta geração
        historico.append(individuos_ordenados[0][1])

        # Thanos: mantém só a melhor metade, já em ordem de aptidão
        melhores_idx = individuos_ordenados[:n_manter]
        mantidos = thanos.thanos(pop, melhores_idx)

        # Gera a outra metade da nova geração com roleta + crossover + mutação
        filhos = []
        while len(filhos) < Npop - n_manter:
            # Roleta escolhe os dois pais entre os mantidos
            pai1 = mantidos[roleta.sortear_pai(prob)]
            pai2 = mantidos[roleta.sortear_pai(prob)]

            # Local aleatório do cromossomo onde começa o cycle crossover
            pos = np.random.randint(Ncidade)
            filho1, filho2 = crossover.cycle_crossover(pai1, pai2, pos)

            # Mutação atua sobre cada membro novo da geração
            filhos.append(mutacao.mutar(filho1))
            filhos.append(mutacao.mutar(filho2))

        # Nova população = metade mantida + filhos
        pop = np.vstack((mantidos, np.array(filhos)))

    # Avaliação da população final, ordenada do melhor para o pior
    custos = fitness.cvfun(pop, x, y)
    ordem = np.argsort(custos)
    pop_final = pop[ordem]
    custos_finais = custos[ordem]

    # Último ponto da curva = melhor custo da população final
    historico.append(float(custos_finais[0]))

    # Custos da população inicial (para comparar no relatório)
    custos_iniciais = fitness.cvfun(pop_inicial, x, y)

    return pop_inicial, custos_iniciais, pop_final, custos_finais, historico


# Imprime uma população, uma linha por indivíduo com o seu custo
def imprimir_populacao(titulo, pop, custos):
    print(titulo)
    for i in range(len(pop)):
        # Cidades separadas por espaço, com largura fixa para alinhar
        rota = " ".join(f"{c:2d}" for c in pop[i])
        print(f"  {i + 1:2d}: [{rota}]  custo = {custos[i]:.4f}")
    print()


# Mostra na janela de comando os resultados pedidos no enunciado
def mostrar_resultados(pop_inicial, custos_iniciais, pop_final, custos_finais, n_iter):
    print("=" * 80)
    print("ALGORITMO GENÉTICO - CAIXEIRO-VIAJANTE")
    print("=" * 80)
    print(f"Tamanho da População: {len(pop_final)}")
    print(f"Número de Cidades: {pop_final.shape[1]}")
    print(f"Número de Iterações: {n_iter}")
    print()
    imprimir_populacao("População Inicial:", pop_inicial, custos_iniciais)
    imprimir_populacao("População Final (do melhor para o pior):", pop_final, custos_finais)
    # A população final está ordenada: o melhor é o primeiro
    print(f"Melhor Custo: {custos_finais[0]:.4f}")
    print("Melhor Solução:", " -> ".join(str(c) for c in pop_final[0]),
          "->", pop_final[0][0])


# Desenha as cidades, o melhor caminho e a evolução do melhor custo
def plotar(x, y, melhor, melhor_custo, historico):
    fig, (ax_rota, ax_evol) = plt.subplots(1, 2, figsize=(13, 6))

    # Fecha o caminho: volta para a cidade inicial (índices começam em 0)
    rota = np.append(melhor, melhor[0]) - 1

    # Linha do melhor caminho e os pontos das cidades
    ax_rota.plot(x[rota], y[rota], "-", color="tab:blue", zorder=1)
    ax_rota.scatter(x, y, color="tab:red", s=40, zorder=2)

    # Escreve o número de cada cidade ao lado do ponto
    for k in range(len(x)):
        ax_rota.annotate(str(k + 1), (x[k], y[k]), xytext=(4, 4),
                         textcoords="offset points")

    # Destaca a cidade inicial da rota
    ax_rota.scatter(x[rota[0]], y[rota[0]], color="tab:green", s=120,
                    marker="*", zorder=3, label="cidade inicial")
    ax_rota.set_title(f"Melhor caminho encontrado (custo = {melhor_custo:.4f})")
    ax_rota.set_xlabel("x")
    ax_rota.set_ylabel("y")
    ax_rota.legend(loc="best")

    # Curva do melhor custo ao longo das gerações (contadas a partir de 1)
    geracoes = np.arange(1, len(historico) + 1)
    ax_evol.plot(geracoes, historico, color="tab:blue")
    # Escala logarítmica: a queda acontece nas primeiras gerações
    ax_evol.set_xscale("log")
    ax_evol.set_title("Evolução do melhor custo")
    ax_evol.set_xlabel("Geração (escala log)")
    ax_evol.set_ylabel("Distância total")
    ax_evol.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    # Coordenadas das cidades (linha 0 = x, linha 1 = y)
    x = cidades.CIDADES[0]
    y = cidades.CIDADES[1]

    # Roda o algoritmo genético
    pop_inicial, custos_iniciais, pop_final, custos_finais, historico = executar_ag(x, y)

    # Resultados na janela de comando
    mostrar_resultados(pop_inicial, custos_iniciais, pop_final, custos_finais, N_ITER)

    # Gráfico com os pontos e o melhor caminho
    plotar(x, y, pop_final[0], custos_finais[0], historico)
    plt.show()
