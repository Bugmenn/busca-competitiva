import unittest
import numpy as np

import crossover
import fitness
import mutacao
import roleta
import thanos


# Confere se o vetor é uma permutação de 1 a n (cada cidade uma vez só)
def eh_permutacao(v, n):
    return sorted(int(c) for c in v) == list(range(1, n + 1))


class TestCycleCrossover(unittest.TestCase):

    # Reproduz exatamente a Figura 1 do enunciado (posição 4 = índice 3)
    def test_figura_1_do_enunciado(self):
        pai1 = np.array([4, 1, 5, 3, 2, 6])
        pai2 = np.array([3, 4, 6, 2, 1, 5])
        filho1, filho2 = crossover.cycle_crossover(pai1, pai2, 3)
        self.assertEqual(filho1.tolist(), [3, 4, 5, 2, 1, 6])
        self.assertEqual(filho2.tolist(), [4, 1, 6, 3, 2, 5])

    # Os pais não podem ser alterados pelo crossover
    def test_nao_altera_os_pais(self):
        pai1 = np.array([4, 1, 5, 3, 2, 6])
        pai2 = np.array([3, 4, 6, 2, 1, 5])
        crossover.cycle_crossover(pai1, pai2, 3)
        self.assertEqual(pai1.tolist(), [4, 1, 5, 3, 2, 6])
        self.assertEqual(pai2.tolist(), [3, 4, 6, 2, 1, 5])

    # Mesmo gene na posição sorteada: os filhos são cópias dos pais
    def test_genes_iguais_na_posicao(self):
        pai1 = np.array([1, 2, 3, 4])
        pai2 = np.array([4, 2, 1, 3])
        filho1, filho2 = crossover.cycle_crossover(pai1, pai2, 1)
        self.assertEqual(filho1.tolist(), pai1.tolist())
        self.assertEqual(filho2.tolist(), pai2.tolist())

    # Pais iguais geram filhos iguais aos pais
    def test_pais_iguais(self):
        pai = np.random.permutation(np.arange(1, 21))
        filho1, filho2 = crossover.cycle_crossover(pai, pai.copy(), 5)
        self.assertEqual(filho1.tolist(), pai.tolist())
        self.assertEqual(filho2.tolist(), pai.tolist())

    # Muitos cruzamentos aleatórios sempre produzem rotas válidas
    def test_filhos_sempre_validos(self):
        rng = np.random.default_rng(0)
        for _ in range(200):
            pai1 = rng.permutation(np.arange(1, 21))
            pai2 = rng.permutation(np.arange(1, 21))
            pos = int(rng.integers(20))
            filho1, filho2 = crossover.cycle_crossover(pai1, pai2, pos)
            self.assertTrue(eh_permutacao(filho1, 20))
            self.assertTrue(eh_permutacao(filho2, 20))
            # Em cada posição, os filhos têm o mesmo par de genes dos pais
            for k in range(20):
                self.assertEqual({filho1[k], filho2[k]}, {pai1[k], pai2[k]})


class TestRoleta(unittest.TestCase):

    # Pesos lineares 10/55, 9/55, ..., 1/55
    def test_probabilidades_lineares(self):
        prob = roleta.probabilidades(10)
        self.assertAlmostEqual(prob.sum(), 1.0)
        self.assertAlmostEqual(prob[0], 10 / 55)
        self.assertAlmostEqual(prob[-1], 1 / 55)
        self.assertTrue(np.all(np.diff(prob) < 0))

    # O 1º do ranking deve sair mais vezes que o último
    def test_sorteio_favorece_os_melhores(self):
        np.random.seed(1)
        prob = roleta.probabilidades(10)
        contagem = np.bincount([roleta.sortear_pai(prob) for _ in range(20000)],
                               minlength=10)
        self.assertGreater(contagem[0], contagem[9])
        # Frequência do 1º perto de 10/55 (~0,18)
        self.assertAlmostEqual(contagem[0] / 20000, 10 / 55, delta=0.02)

    # O índice sorteado sempre existe
    def test_indice_dentro_do_intervalo(self):
        prob = roleta.probabilidades(10)
        for _ in range(1000):
            self.assertIn(roleta.sortear_pai(prob), range(10))


class TestMutacao(unittest.TestCase):

    # A mutação troca exatamente duas cidades e mantém a rota válida
    def test_troca_duas_posicoes(self):
        for _ in range(200):
            original = np.random.permutation(np.arange(1, 21))
            mutado = mutacao.mutar(original)
            self.assertTrue(eh_permutacao(mutado, 20))
            self.assertEqual(int(np.sum(mutado != original)), 2)

    # O cromossomo original não é alterado
    def test_nao_altera_original(self):
        original = np.arange(1, 21)
        mutacao.mutar(original)
        self.assertEqual(original.tolist(), list(range(1, 21)))


class TestFitness(unittest.TestCase):

    # Quadrado de lado 1: percorrendo os cantos em ordem, o custo é 4
    def test_quadrado_unitario(self):
        x = np.array([0.0, 1.0, 1.0, 0.0])
        y = np.array([0.0, 0.0, 1.0, 1.0])
        pop = np.array([[1, 2, 3, 4], [1, 3, 2, 4]])
        custos = fitness.cvfun(pop, x, y)
        self.assertAlmostEqual(custos[0], 4.0)
        # Rota cruzada: 1 + raiz(2) + 1 + raiz(2)
        self.assertAlmostEqual(custos[1], 2 + 2 * np.sqrt(2))


class TestThanos(unittest.TestCase):

    # Mantém os 10 menores custos, em ordem do melhor para o pior
    def test_mantem_melhor_metade_ordenada(self):
        pop = np.array([np.random.permutation(np.arange(1, 6)) for _ in range(20)])
        fit = np.arange(20, 0, -1, dtype=float)  # o último indivíduo é o melhor
        ordenados = thanos.ordenar(thanos.atribuir_idx(20, fit))
        mantidos = thanos.thanos(pop, thanos.corta_melhores(ordenados))
        self.assertEqual(mantidos.shape, (10, 5))
        for k in range(10):
            self.assertEqual(mantidos[k].tolist(), pop[19 - k].tolist())


class TestExecutarAG(unittest.TestCase):

    # Laço completo curto: forma da população, rotas válidas e elitismo
    def test_laco_completo(self):
        # Backend sem janela, para o teste não abrir gráfico
        import matplotlib
        matplotlib.use("Agg")
        import cidades
        import main
        np.random.seed(0)
        x, y = cidades.CIDADES
        pop_ini, _, pop_fim, custos, historico = main.executar_ag(x, y, n_iter=200)
        self.assertEqual(pop_ini.shape, (20, 20))
        self.assertEqual(pop_fim.shape, (20, 20))
        for rota in pop_fim:
            self.assertTrue(eh_permutacao(rota, 20))
        # O melhor custo nunca piora (os melhores não sofrem mutação)
        self.assertTrue(np.all(np.diff(historico) <= 1e-12))
        # Último ponto da curva = melhor custo final
        self.assertAlmostEqual(historico[-1], custos[0])
        # População final ordenada do melhor para o pior
        self.assertTrue(np.all(np.diff(custos) >= 0))

    # Tamanho que não divide em metades pares é recusado
    def test_npop_invalido(self):
        import cidades
        import main
        x, y = cidades.CIDADES
        with self.assertRaises(ValueError):
            main.executar_ag(x, y, Npop=10, n_iter=1)


if __name__ == "__main__":
    unittest.main()
