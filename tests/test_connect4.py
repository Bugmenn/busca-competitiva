"""Testes automáticos do Connect 4 (rodar com: python -m unittest -v)."""

import random
import unittest
from unittest import mock

from connect4.ia import escolher_jogada
from connect4.main import ler_coluna_humano
from connect4.tabuleiro import (HUMANO, IA, LINHAS, aplicar_jogada, criar_tabuleiro,
                                fim_de_jogo, jogadas_validas, tabuleiro_cheio, venceu)


def jogar_varias(tabuleiro, jogadas):
    """Aplica uma lista de jogadas (coluna, peça) em sequência."""
    for coluna, peca in jogadas:
        tabuleiro = aplicar_jogada(tabuleiro, coluna, peca)
    return tabuleiro


class TestTabuleiro(unittest.TestCase):

    def test_estado_inicial_vazio_com_7_jogadas(self):
        tab = criar_tabuleiro()
        self.assertEqual(jogadas_validas(tab), list(range(7)))
        self.assertFalse(fim_de_jogo(tab))

    def test_peca_cai_na_linha_mais_baixa(self):
        tab = aplicar_jogada(criar_tabuleiro(), 2, HUMANO)
        self.assertEqual(tab[LINHAS - 1][2], HUMANO)

    def test_aplicar_nao_altera_original(self):
        original = criar_tabuleiro()
        aplicar_jogada(original, 0, IA)
        self.assertEqual(original, criar_tabuleiro())

    def test_coluna_cheia_sai_das_jogadas_e_gera_erro(self):
        tab = jogar_varias(criar_tabuleiro(),
                           [(0, HUMANO if i % 2 == 0 else IA) for i in range(6)])
        self.assertNotIn(0, jogadas_validas(tab))
        with self.assertRaises(ValueError):
            aplicar_jogada(tab, 0, HUMANO)

    def test_vitoria_horizontal(self):
        tab = jogar_varias(criar_tabuleiro(), [(c, HUMANO) for c in range(4)])
        self.assertTrue(venceu(tab, HUMANO))

    def test_vitoria_vertical(self):
        tab = jogar_varias(criar_tabuleiro(), [(5, IA)] * 4)
        self.assertTrue(venceu(tab, IA))

    def test_vitoria_diagonal_subindo(self):
        # Escada: coluna c recebe c peças de apoio e depois a peça da IA
        jogadas = []
        for c in range(4):
            jogadas += [(c, HUMANO)] * c + [(c, IA)]
        tab = jogar_varias(criar_tabuleiro(), jogadas)
        self.assertTrue(venceu(tab, IA))
        self.assertFalse(venceu(tab, HUMANO))

    def test_vitoria_diagonal_descendo(self):
        jogadas = []
        for c in range(4):
            jogadas += [(c, HUMANO)] * (3 - c) + [(c, IA)]
        tab = jogar_varias(criar_tabuleiro(), jogadas)
        self.assertTrue(venceu(tab, IA))

    def test_tres_em_linha_nao_vence(self):
        tab = jogar_varias(criar_tabuleiro(), [(c, HUMANO) for c in range(3)])
        self.assertFalse(venceu(tab, HUMANO))

    def test_empate_tabuleiro_cheio_sem_vencedor(self):
        # Tabuleiro cheio montado à mão, sem nenhuma sequência de 4
        linhas = ["XOXOXOX", "XOXOXOX", "OXOXOXO", "OXOXOXO", "XOXOXOX", "XOXOXOX"]
        simbolo = {"X": HUMANO, "O": IA}
        tab = [[simbolo[ch] for ch in linha] for linha in linhas]
        self.assertEqual(len(tab), LINHAS)
        self.assertTrue(tabuleiro_cheio(tab))
        self.assertFalse(venceu(tab, HUMANO))
        self.assertFalse(venceu(tab, IA))
        self.assertTrue(fim_de_jogo(tab))


class TestEntrada(unittest.TestCase):

    def test_entrada_invalida_e_repetida_ate_coluna_valida(self):
        # "²" passa em isdigit() mas quebra int(); deve só pedir de novo
        respostas = ["²", "abc", "9", "", "4"]
        with mock.patch("builtins.input", side_effect=respostas), \
             mock.patch("builtins.print"):
            coluna = ler_coluna_humano(criar_tabuleiro())
        self.assertEqual(coluna, 3)

    def test_profundidade_zero_e_recusada(self):
        with self.assertRaises(ValueError):
            escolher_jogada(criar_tabuleiro(), 0)


class TestIA(unittest.TestCase):

    def test_ia_vence_quando_pode(self):
        # IA tem 3 peças na coluna 6; jogar ali vence
        tab = jogar_varias(criar_tabuleiro(),
                           [(6, IA), (0, HUMANO), (6, IA), (1, HUMANO), (6, IA), (0, HUMANO)])
        coluna, _ = escolher_jogada(tab, 4)
        self.assertEqual(coluna, 6)

    def test_ia_bloqueia_vitoria_do_humano(self):
        # Humano tem 3 na base (colunas 0,1,2); IA precisa jogar na 3
        tab = jogar_varias(criar_tabuleiro(),
                           [(0, HUMANO), (6, IA), (1, HUMANO), (6, IA), (2, HUMANO)])
        coluna, _ = escolher_jogada(tab, 4)
        self.assertEqual(coluna, 3)

    def test_poda_mesma_decisao_com_menos_nos(self):
        tab = jogar_varias(criar_tabuleiro(), [(3, HUMANO), (3, IA), (2, HUMANO)])
        col_poda, nos_poda = escolher_jogada(tab, 4, usar_poda=True)
        col_sem, nos_sem = escolher_jogada(tab, 4, usar_poda=False)
        self.assertEqual(col_poda, col_sem)
        self.assertLess(nos_poda, nos_sem)

    def test_ia_nao_perde_para_jogador_aleatorio(self):
        gerador = random.Random(42)  # semente fixa: resultado reproduzível
        for partida in range(10):
            tab = criar_tabuleiro()
            vez = HUMANO if partida % 2 == 0 else IA
            while not fim_de_jogo(tab):
                if vez == HUMANO:
                    coluna = gerador.choice(jogadas_validas(tab))
                else:
                    coluna, _ = escolher_jogada(tab, 4)
                tab = aplicar_jogada(tab, coluna, vez)
                vez = IA if vez == HUMANO else HUMANO
            self.assertFalse(venceu(tab, HUMANO), f"IA perdeu a partida {partida}")


if __name__ == "__main__":
    unittest.main()
