"""Testes automáticos das damas (rodar com: python -m unittest -v)."""

import random
import unittest
from unittest import mock

from damas import regras
from damas import tabuleiro as tb
from damas.console import (continuar_captura, escolher_cor, escolher_movimento,
                           escolher_no_menu, jogar, main)
from damas.ia import escolher_jogada
from damas.tipo_peca import VAZIO, TipoPeca

# Letras usadas nos testes para montar posições, traduzidas para os símbolos
# reais das peças (assim os testes não dependem de qual símbolo o jogo usa)
PECA = {
    "b": TipoPeca.PEAO_BRANCO.value,
    "p": TipoPeca.PEAO_PRETO.value,
    "B": TipoPeca.DAMA_BRANCA.value,
    "P": TipoPeca.DAMA_PRETA.value,
}


def vazio():
    """Tabuleiro sem nenhuma peça, para montar posições de teste."""
    return [[VAZIO] * tb.TAMANHO for _ in range(tb.TAMANHO)]


def casa(nome):
    """Converte "c3" em (linha, coluna)."""
    return int(nome[1]) - 1, tb.LETRAS.index(nome[0])


def montar(**pecas):
    """Monta um tabuleiro a partir de casas: montar(c3="b", d4="p")."""
    tab = vazio()
    for nome, peca in pecas.items():
        l, c = casa(nome)
        tab[l][c] = PECA[peca]
    return tab


class TestTabuleiro(unittest.TestCase):

    def test_simbolos_das_pecas_sao_validos(self):
        # Os 4 tipos de peça e a casa vazia precisam ter símbolos diferentes
        # (senão o Enum cria um apelido sem avisar) e de 1 caractere só
        # (senão a casa deixa de ter 3 colunas no desenho)
        simbolos = [t.value for t in TipoPeca] + [VAZIO]
        self.assertEqual(len(TipoPeca.__members__), 4)
        self.assertEqual(len(set(simbolos)), 5)
        for simbolo in simbolos:
            self.assertEqual(len(simbolo), 1, simbolo)

    def test_posicao_inicial_12_pecas_em_casas_escuras(self):
        tab = tb.criar_tabuleiro()
        self.assertEqual(tb.contar_pecas(tab, "branca"), 12)
        self.assertEqual(tb.contar_pecas(tab, "preta"), 12)
        # Regra oficial: a1 é escura e começa com peça branca
        self.assertEqual(tab[0][0], PECA["b"])
        self.assertEqual(tab[7][7], PECA["p"])
        for l in range(8):
            for c in range(8):
                if tab[l][c] != VAZIO:
                    self.assertTrue(tb.casa_escura(l, c))

    def test_desenho_sem_cor_tem_casas_de_3_caracteres(self):
        texto = tb.texto_tabuleiro(tb.criar_tabuleiro(), cor=False)
        linhas = texto.splitlines()
        self.assertEqual(len(linhas), 10)  # cabeçalho + 8 linhas + rodapé
        # " 8 " + 8 casas de 3 caracteres + " 8"
        for linha in linhas[1:9]:
            self.assertEqual(len(linha), 3 + 24 + 2)
        self.assertTrue(linhas[1].startswith(" 8 "))
        self.assertTrue(linhas[8].startswith(" 1 "))

    def test_desenho_destaca_ultimo_lance(self):
        tab = montar(c3="b", d4="p")
        mov = regras.movimentos_validos(tab, "branca")[0]
        regras.aplicar_movimento(tab, mov)
        texto = tb.texto_tabuleiro(tab, mov, cor=False)
        self.assertIn(f"[{PECA['b']}]", texto)  # peça que acabou de jogar
        self.assertIn(" x ", texto)  # peça capturada


class TestRegras(unittest.TestCase):

    def test_peao_anda_so_para_frente(self):
        tab = montar(d4="b")
        destinos = {m.destinos[0] for m in regras.movimentos_validos(tab, "branca")}
        self.assertEqual(destinos, {casa("c5"), casa("e5")})

    def test_captura_obrigatoria(self):
        tab = montar(c3="b", g3="b", d4="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertTrue(movs)
        self.assertTrue(all(m.capturadas for m in movs))

    def test_peao_captura_para_tras(self):
        tab = montar(d4="b", c3="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0].destinos, [casa("b2")])

    def test_lei_da_maioria(self):
        # Por d4 captura 1; pela outra diagonal dá para capturar 2 em sequência
        tab = montar(c3="b", d4="p", b4="p", b6="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertEqual({len(m.capturadas) for m in movs}, {2})

    def test_dama_voadora_captura_de_longe(self):
        tab = montar(a1="B", e5="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertEqual({m.destinos[-1] for m in movs}, {casa("f6"), casa("g7"), casa("h8")})

    def test_nao_captura_a_mesma_peca_duas_vezes(self):
        movs = regras.movimentos_validos(montar(a1="B", c3="p", e5="p"), "branca")
        self.assertEqual({len(m.capturadas) for m in movs}, {2})
        for mov in movs:
            self.assertEqual(len(mov.capturadas), len(set(mov.capturadas)))

    def test_dama_passa_pela_propria_casa_de_origem(self):
        # A dama sai de d4; no meio da sequência ela atravessa d4, que já está vazia
        tab = montar(d4="B", c5="p", c7="p", e7="p", c3="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertEqual({len(m.capturadas) for m in movs}, {4})

    def test_peca_capturada_bloqueia_o_caminho(self):
        # Golpe turco: a peça já capturada continua no tabuleiro até o fim do
        # lance, e a dama não pode passar por cima dela de novo
        tab = montar(f6="B", f8="p", g7="p", e5="p", g3="p", f4="p", a3="p")
        movs = regras.movimentos_validos(tab, "branca")
        self.assertEqual({len(m.capturadas) for m in movs}, {1})

    def test_peao_preto_anda_para_baixo_e_promove_na_linha_1(self):
        tab = montar(d2="p")
        movs = regras.movimentos_validos(tab, "preta")
        self.assertEqual({m.destinos[0] for m in movs}, {casa("c1"), casa("e1")})
        regras.aplicar_movimento(tab, movs[0])
        self.assertEqual(tab[0][movs[0].destinos[0][1]], PECA["P"])

    def test_promocao_so_no_fim_do_lance(self):
        # Peão passa pela última linha (d8) e continua capturando: não vira dama
        tab = montar(b6="b", c7="p", e7="p")
        mov = regras.movimentos_validos(tab, "branca")[0]
        self.assertEqual(mov.destinos, [casa("d8"), casa("f6")])
        regras.aplicar_movimento(tab, mov)
        self.assertEqual(tab[5][5], PECA["b"])

    def test_promocao_ao_terminar_na_ultima_linha(self):
        tab = montar(c7="b")
        mov = regras.movimentos_validos(tab, "branca")[0]
        regras.aplicar_movimento(tab, mov)
        self.assertEqual(tab[7][mov.destinos[0][1]], PECA["B"])

    def test_aplicar_em_copia_nao_altera_original(self):
        original = tb.criar_tabuleiro()
        copia = regras.copiar(original)
        regras.aplicar_movimento(copia, regras.movimentos_validos(copia, "branca")[0])
        self.assertEqual(original, tb.criar_tabuleiro())

    def test_contador_de_empate(self):
        tab = montar(a1="B", h8="P", c3="b")
        dama = [m for m in regras.movimentos_validos(tab, "branca") if m.origem == casa("a1")][0]
        peao = [m for m in regras.movimentos_validos(tab, "branca") if m.origem == casa("c3")][0]
        self.assertEqual(regras.atualizar_contador(5, tab, dama), 6)   # dama sem captura soma
        self.assertEqual(regras.atualizar_contador(5, tab, peao), 0)   # peão zera
        self.assertEqual(regras.resultado(tab, "branca", regras.LIMITE_EMPATE), "empate")

    def test_empate_e_20_lances_de_cada_jogador(self):
        # Regra da CBD (item 16): 20 lances de cada jogador = 40 jogadas no total
        tab = montar(a1="B", h8="P")
        self.assertEqual(regras.LIMITE_EMPATE, 40)
        self.assertIsNone(regras.resultado(tab, "branca", 39))
        self.assertEqual(regras.resultado(tab, "branca", 40), "empate")

    def test_partida_com_so_damas_empata_apos_20_lances_de_cada(self):
        # Dama branca vai e volta entre a1 e b2; a preta entre h2 e g1.
        # Nenhuma captura é possível, então o contador sobe 1 por jogada.
        tab = montar(a1="B", h2="P")
        vez, contador = "branca", 0
        ida_volta = {"branca": (casa("a1"), casa("b2")), "preta": (casa("h2"), casa("g1"))}
        for jogada in range(1, 41):
            self.assertIsNone(regras.resultado(tab, vez, contador), f"empatou cedo, na jogada {jogada}")
            a, b = ida_volta[vez]
            origem = a if tab[a[0]][a[1]] != VAZIO else b
            destino = b if origem == a else a
            mov = [m for m in regras.movimentos_validos(tab, vez)
                   if m.origem == origem and m.destinos == [destino]][0]
            contador = regras.atualizar_contador(contador, tab, mov)
            regras.aplicar_movimento(tab, mov)
            vez = regras.inimigo(vez)
        # Depois de 40 jogadas (20 de cada jogador) a partida está empatada
        self.assertEqual(contador, 40)
        self.assertEqual(regras.resultado(tab, vez, contador), "empate")

    def test_sem_jogadas_perde(self):
        # Pretas sem nenhuma peça: brancas vencem
        self.assertEqual(regras.resultado(montar(c3="b"), "preta", 0), "branca")
        # Peão preto bloqueado: a casa da frente (b2) está ocupada e a captura
        # não é possível porque a casa depois dela (c1) também está ocupada
        tab = montar(a3="p", b2="b", c1="b")
        self.assertEqual(regras.movimentos_validos(tab, "preta"), [])
        self.assertEqual(regras.resultado(tab, "preta", 0), "branca")


def digitar(funcao, entradas, *args):
    """Roda a função simulando o que o jogador digita.

    Devolve (resultado, texto de tudo que foi impresso e perguntado).
    """
    with mock.patch("builtins.input", side_effect=entradas) as pergunta, \
         mock.patch("builtins.print") as saida:
        resultado = funcao(*args)
    # Junta as mensagens impressas e as perguntas feitas pelo input()
    chamadas = saida.call_args_list + pergunta.call_args_list
    impresso = "\n".join(" ".join(str(a) for a in c.args) for c in chamadas)
    return resultado, impresso


class TestEntrada(unittest.TestCase):

    def test_entrada_invalida_e_repetida_ate_jogada_valida(self):
        movs = regras.movimentos_validos(tb.criar_tabuleiro(), "branca")
        mov, texto = digitar(escolher_movimento, ["²", "z9 a1", "c3", "c3 c5", "C3 D4"], movs)
        self.assertEqual((mov.origem, mov.destinos), (casa("c3"), [casa("d4")]))
        self.assertIn("Casa inválida: ²", texto)
        self.assertIn("Casa inválida: z9", texto)
        self.assertIn("Informe a casa de origem e a de destino", texto)
        self.assertIn("a peça em c3 não pode ir para essa casa", texto)

    def test_formatos_de_jogada_aceitos(self):
        movs = regras.movimentos_validos(tb.criar_tabuleiro(), "branca")
        for digitado in ("c3 d4", "c3-d4", "c3xd4", "c3,d4", "c3d4", "  c3   d4 "):
            mov, _ = digitar(escolher_movimento, [digitado], movs)
            self.assertEqual(mov.destinos, [casa("d4")], digitado)

    def test_numero_nao_escolhe_jogada(self):
        # Não existe lista de jogadas: "1" é recusado, só casas valem
        movs = regras.movimentos_validos(tb.criar_tabuleiro(), "branca")
        mov, texto = digitar(escolher_movimento, ["1", "sair"], movs)
        self.assertIsNone(mov)
        self.assertNotIn("->", texto)  # nenhuma jogada pronta foi mostrada

    def test_peca_que_nao_e_sua(self):
        movs = regras.movimentos_validos(tb.criar_tabuleiro(), "branca")
        _, texto = digitar(escolher_movimento, ["f6 e5", "d4 e5", "sair"], movs)
        self.assertIn("não há peça sua que possa jogar a partir de f6", texto)
        self.assertIn("não há peça sua que possa jogar a partir de d4", texto)

    def test_aviso_de_captura_obrigatoria(self):
        tab = montar(c3="b", d4="p", g3="b")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["g3 h4", "c3 e5"], movs)
        self.assertEqual(mov.capturadas, [casa("d4")])
        self.assertIn("a partir de g3 não há nenhuma dessas", texto)

    def test_captura_multipla_digitada_e_caminho_errado(self):
        tab = montar(c3="b", d4="p", f6="p")
        movs = regras.movimentos_validos(tab, "branca")
        # c3 g7 pula o pouso do meio; c3 d4 aponta a peça capturada
        mov, texto = digitar(escolher_movimento, ["c3 g7", "c3 d4", "c3 e5 g7"], movs)
        self.assertEqual(len(mov.capturadas), 2)
        self.assertEqual(texto.count("Caminho incorreto"), 2)
        self.assertNotIn("não há nenhuma dessas", texto)

    def test_comeco_do_caminho_unico_e_completado(self):
        tab = montar(c3="b", d4="p", d6="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, _ = digitar(escolher_movimento, ["c3 e5"], movs)
        self.assertEqual(mov.destinos, [casa("e5"), casa("c7")])

    def test_captura_com_dois_caminhos_pede_so_a_proxima_casa(self):
        # De e5 a captura obrigatória pode seguir para c7 ou para g7:
        # o jogo continua de e5 e pergunta só a próxima casa
        tab = montar(c3="b", d4="p", d6="p", f6="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["c3 e5", "a1", "z9", "g7"], movs)
        self.assertIn("continua a partir de e5", texto)
        self.assertIn("não pode continuar a captura de e5 para a1", texto)
        self.assertIn("Casa inválida: z9", texto)
        self.assertEqual(mov.destinos, [casa("e5"), casa("g7")])

    def test_sair_no_meio_da_captura(self):
        tab = montar(c3="b", d4="p", d6="p", f6="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["c3 e5", "sair"], movs)
        self.assertIsNone(mov)
        self.assertIn("continua a partir de e5", texto)  # o "sair" veio no meio da captura

    def test_voltar_no_meio_da_captura_refaz_a_jogada(self):
        tab = montar(c3="b", d4="p", d6="p", f6="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["c3 e5", "voltar", "c3 e5 c7"], movs)
        self.assertEqual(texto.count("continua a partir de e5"), 1)
        self.assertEqual(mov.destinos, [casa("e5"), casa("c7")])

    def test_resto_do_caminho_de_uma_vez_e_enter_vazio(self):
        # Dois caminhos de a1 que se separam em c3: c3-e5-g7 ou c3-a5-c7
        dois = [regras.Movimento(casa("a1"), [casa("c3"), casa("e5"), casa("g7")], []),
                regras.Movimento(casa("a1"), [casa("c3"), casa("a5"), casa("c7")], [])]
        mov, _ = digitar(continuar_captura, ["", "a5 c7"], dois, [casa("a1"), casa("c3")])
        self.assertIs(mov, dois[1])

    def test_dama_com_varios_pousos_pede_a_proxima_casa(self):
        # Depois de capturar c3 e e5 a dama pode pousar em f6, g7 ou h8
        tab = montar(a1="B", c3="p", e5="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["a1 d4", "h8"], movs)
        self.assertIn("continua a partir de d4", texto)
        self.assertEqual(len(mov.capturadas), 2)
        self.assertEqual(mov.destinos, [casa("d4"), casa("h8")])

    def test_dama_completa_captura_sozinha(self):
        # Só há um caminho depois de d4: o jogador digita o primeiro salto e pronto
        tab = montar(a1="B", c3="p", e5="p", g7="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["a1 d4"], movs)
        self.assertEqual(mov.destinos, [casa("d4"), casa("f6"), casa("h8")])
        self.assertNotIn("continua a partir", texto)

    def test_casa_obrigatoria_no_meio_avanca_sozinha(self):
        # g1 -> b6: dali a única casa é d8 (avança sem perguntar);
        # só em d8 o caminho se divide entre g5 e h4
        tab = montar(g1="B", f6="p", d4="p", a3="p", h8="p", c7="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, texto = digitar(escolher_movimento, ["g1 b6", "g5"], movs)
        self.assertNotIn("continua a partir de b6", texto)
        self.assertIn("seguiu sozinha para d8", texto)
        self.assertIn("continua a partir de d8", texto)
        self.assertEqual(mov.destinos, [casa("b6"), casa("d8"), casa("g5")])

    def test_lei_da_maioria_mensagem_correta(self):
        # h4 pode capturar 1, mas a1 captura 2: a de h4 não vale
        tab = montar(a1="b", b2="p", d4="p", h4="b", g5="p")
        movs = regras.movimentos_validos(tab, "branca")
        _, texto = digitar(escolher_movimento, ["h4 f6", "sair"], movs)
        self.assertIn("maior número de peças", texto)
        self.assertNotIn("não pode capturar", texto)

    def test_formatos_misturados(self):
        tab = montar(c3="b", d4="p", f6="p")
        movs = regras.movimentos_validos(tab, "branca")
        mov, _ = digitar(escolher_movimento, ["c3e5 g7"], movs)
        self.assertEqual(len(mov.capturadas), 2)

    def test_menu_aceita_so_numero_valido(self):
        valor, texto = digitar(escolher_no_menu, ["abc", "²", "0", "4", "", "2"],
                               "?", [("A", "a"), ("B", "b"), ("C", "c")])
        self.assertEqual(valor, "b")
        self.assertEqual(texto.count("Digite um número de 1 a 3"), 5)

    def test_sortear_cor(self):
        for sorteada in ("branca", "preta"):
            with mock.patch("damas.console.random.choice", return_value=sorteada) as sorteio:
                cor, texto = digitar(escolher_cor, ["3"])
            self.assertEqual(cor, sorteada)
            sorteio.assert_called_once_with(["branca", "preta"])
            self.assertIn(f"você joga com as {sorteada}s", texto)

    def test_partida_ia_joga_e_jogador_sai(self):
        # Fácil, pretas: a IA (brancas) joga primeiro e depois o jogador sai
        _, texto = digitar(jogar, ["1", "2", "sair"])
        self.assertIn("IA jogou:", texto)
        self.assertIn("Jogo encerrado.", texto)
        self.assertNotIn("Você jogou", texto)

    def test_fim_da_entrada_encerra_sem_erro(self):
        with mock.patch("builtins.input", side_effect=EOFError), \
             mock.patch("builtins.print") as saida, \
             mock.patch("damas.console.sys") as falso_sys:
            main()
        falso_sys.stdout.reconfigure.assert_called_once()
        self.assertIn("Jogo encerrado.", str(saida.call_args_list[-1]))


class TestIA(unittest.TestCase):

    def test_ia_escolhe_a_captura_que_nao_entrega_a_peca(self):
        # Duas capturas de 1 peça. A primeira da lista (f3xe4, pousa em d5) é
        # recapturada por c6; a segunda (f3xg4, pousa em h5) é segura.
        tab = montar(f3="b", e4="p", g4="p", c6="p", b7="p")
        primeira = regras.movimentos_validos(tab, "branca")[0]
        self.assertEqual(primeira.destinos, [casa("d5")])  # o lance ruim vem primeiro
        mov, _ = escolher_jogada(tab, "branca", 0, 2)
        self.assertEqual(mov.destinos, [casa("h5")])

    def test_ia_nao_entrega_peca_a_toa(self):
        # d4->c5 (primeiro da lista) é capturado por b6; d4->e5 é seguro
        tab = montar(d4="b", b6="p", h8="p")
        primeira = regras.movimentos_validos(tab, "branca")[0]
        self.assertEqual(primeira.destinos, [casa("c5")])
        mov, _ = escolher_jogada(tab, "branca", 0, 2)
        self.assertEqual(mov.destinos, [casa("e5")])

    def test_empate_vale_zero_na_busca(self):
        from damas.ia import minimax
        tab = montar(a1="B", h8="P")
        valor, _ = minimax(tab, "branca", regras.LIMITE_EMPATE, 4, -1e9, 1e9,
                           "branca", {"nos": 0})
        self.assertEqual(valor, 0)

    def test_poda_mesma_decisao_com_menos_nos(self):
        tab = tb.criar_tabuleiro()
        mov_poda, nos_poda = escolher_jogada(tab, "branca", 0, 4, usar_poda=True)
        mov_sem, nos_sem = escolher_jogada(tab, "branca", 0, 4, usar_poda=False)
        self.assertEqual(mov_poda, mov_sem)
        self.assertLess(nos_poda, nos_sem)

    def test_profundidade_zero_e_recusada(self):
        with self.assertRaises(ValueError):
            escolher_jogada(tb.criar_tabuleiro(), "branca", 0, 0)

    def test_ia_vence_jogador_aleatorio(self):
        gerador = random.Random(42)  # semente fixa: resultado reproduzível
        for partida in range(6):
            tab = tb.criar_tabuleiro()
            cor_ia = "branca" if partida % 2 == 0 else "preta"
            vez, contador = "branca", 0
            for _ in range(300):  # limite de segurança
                if regras.resultado(tab, vez, contador) is not None:
                    break
                if vez == cor_ia:
                    mov, _ = escolher_jogada(tab, vez, contador, 2)
                else:
                    mov = gerador.choice(regras.movimentos_validos(tab, vez))
                contador = regras.atualizar_contador(contador, tab, mov)
                regras.aplicar_movimento(tab, mov)
                vez = regras.inimigo(vez)
            fim = regras.resultado(tab, vez, contador)
            # A partida tem de terminar de verdade (não pelo limite) e com vitória da IA
            self.assertEqual(fim, cor_ia, f"IA não venceu a partida {partida}")


if __name__ == "__main__":
    unittest.main()
