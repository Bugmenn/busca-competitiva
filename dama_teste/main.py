"""Janela do jogo: câmera orbital, seleção de peças e movimento animado.

Ainda NÃO há regras de dama aqui. Qualquer peça pode ir para qualquer
casa escura vazia. As regras (e a IA) entram depois, sem mudar a cena.
"""

import math
import sys

from panda3d.core import (
    AntialiasAttrib, Plane, Point3, Vec3, WindowProperties, loadPrcFileData,
)

# Configurações que precisam vir antes de a janela ser criada:
# antisserrilhado (bordas suaves) e, no macOS, um OpenGL moderno (3.2),
# sem o qual o shader de iluminação (GLSL 150) não roda.
loadPrcFileData("", "framebuffer-multisample 1\nmultisamples 4")
if sys.platform == "darwin":
    loadPrcFileData("", "gl-version 3 2")

from direct.gui.OnscreenText import OnscreenText  # noqa: E402
from direct.interval.IntervalGlobal import (  # noqa: E402
    Func, LerpFunc, LerpPosInterval, Sequence,
)
from direct.showbase.ShowBase import ShowBase  # noqa: E402

from dama_teste import cena3d, iluminacao  # noqa: E402
from dama_teste.cena3d import ALTURA_PECA, ALTURA_SELECIONADA, TAMANHO, TOPO_CASA  # noqa: E402

# Duração (em segundos) da animação de uma peça indo de uma casa a outra
DURACAO_MOVIMENTO = 0.45
# Altura máxima do "arco" que a peça faz no ar durante o movimento
ALTURA_ARCO = 1.0

# Limites da câmera orbital
DISTANCIA_INICIAL, DISTANCIA_MIN, DISTANCIA_MAX = 19, 7, 35
INCLINACAO_INICIAL, INCLINACAO_MIN, INCLINACAO_MAX = -55, -88, -12
VELOCIDADE_GIRO = 120  # graus por "largura de tela" arrastada


class JogoDama(ShowBase):
    """Janela do jogo. Guarda onde cada peça está e responde ao mouse."""

    def __init__(self):
        super().__init__()
        self._configurar_janela()

        iluminacao.aplicar(self.render)
        cena3d.criar_tabuleiro(self.render)
        self.sombras = cena3d.Sombras(self.render)
        self._criar_camera()
        self._criar_ajuda()

        self.pecas = {}      # {(linha, coluna): NodePath da peça}
        self.marcadores = []
        self.selecionada = None  # (linha, coluna) da peça selecionada
        self.animando = False
        self.posicionar_pecas()

        self.accept("mouse1", self.clique)
        self.accept("mouse3", self._comecar_giro)
        self.accept("mouse3-up", self._parar_giro)
        self.accept("wheel_up", self._zoom, [-1])
        self.accept("wheel_down", self._zoom, [1])
        self.accept("r", self.reiniciar)
        self.accept("escape", sys.exit)
        self.task_mgr.add(self._a_cada_quadro, "a_cada_quadro")

    # ---------- montagem ----------

    def _configurar_janela(self):
        propriedades = WindowProperties()
        propriedades.set_title("Dama 3D")
        self.win.request_properties(propriedades)
        self.set_background_color(cena3d.COR_FUNDO)
        self.disable_mouse()  # desliga o controle de câmera padrão do Panda3D
        self.render.set_antialias(AntialiasAttrib.M_multisample)

    def _criar_camera(self):
        """Câmera presa a um pivô no centro do tabuleiro.

        Girar o pivô faz a câmera orbitar; afastar a câmera é o zoom.
        """
        self.pivo = self.render.attach_new_node("pivo_camera")
        self.pivo.set_hpr(0, INCLINACAO_INICIAL, 0)
        self.camera.reparent_to(self.pivo)
        self.camera.set_pos(0, -DISTANCIA_INICIAL, 0)
        self.camera.look_at(self.pivo)
        self.camLens.set_fov(40)
        self.girando_desde = None

    def _criar_ajuda(self):
        OnscreenText(
            text="Esquerdo: selecionar / mover    Direito (arrastar): girar    "
                 "Roda: zoom    R: reiniciar    Esc: sair",
            pos=(0, 0.93), scale=0.045, fg=(1, 1, 1, 0.7),
            parent=self.aspect2d,
        )

    def posicionar_pecas(self):
        """Coloca as 24 peças na posição inicial (3 fileiras de cada lado)."""
        for linha in range(TAMANHO):
            for coluna in range(TAMANHO):
                if not cena3d.casa_escura(linha, coluna):
                    continue
                if linha < 3:
                    cor = "branca"
                elif linha >= TAMANHO - 3:
                    cor = "preta"
                else:
                    continue
                peca = cena3d.criar_peca(self.render, cor, linha, coluna)
                self.pecas[(linha, coluna)] = peca
                self.sombras.adicionar(peca)

    def reiniciar(self):
        if self.animando:
            return
        self.desselecionar()
        for peca in self.pecas.values():
            self.sombras.remover(peca)
            peca.remove_node()
        self.pecas = {}
        self.posicionar_pecas()

    def _a_cada_quadro(self, task):
        """Coisas que dependem da posição atual da câmera e das peças."""
        iluminacao.atualizar_camera(self.render, self.camera)
        self.sombras.atualizar()
        return task.cont

    # ---------- câmera ----------

    def _comecar_giro(self):
        if self.mouseWatcherNode.has_mouse():
            self.girando_desde = Point3(self.mouseWatcherNode.get_mouse())
            self.task_mgr.add(self._girar, "girar_camera")

    def _parar_giro(self):
        self.girando_desde = None
        self.task_mgr.remove("girar_camera")

    def _girar(self, task):
        """Enquanto o botão direito está apertado, gira conforme o mouse anda."""
        if not self.mouseWatcherNode.has_mouse():
            return task.cont
        agora = Point3(self.mouseWatcherNode.get_mouse())
        delta = agora - self.girando_desde
        self.girando_desde = agora
        h = self.pivo.get_h() - delta.x * VELOCIDADE_GIRO
        p = self.pivo.get_p() + delta.y * VELOCIDADE_GIRO
        self.pivo.set_hpr(h, min(max(p, INCLINACAO_MIN), INCLINACAO_MAX), 0)
        return task.cont

    def _zoom(self, direcao):
        distancia = -self.camera.get_y() * (1.1 if direcao > 0 else 1 / 1.1)
        distancia = min(max(distancia, DISTANCIA_MIN), DISTANCIA_MAX)
        self.camera.set_y(-distancia)

    # ---------- seleção ----------

    def selecionar(self, casa):
        """Levanta a peça da casa e marca todas as casas escuras livres."""
        self.desselecionar()
        self.selecionada = casa
        peca = self.pecas[casa]
        cena3d.realcar_peca(peca, True)
        self._subir_descer(peca, TOPO_CASA + ALTURA_SELECIONADA)
        for linha in range(TAMANHO):
            for coluna in range(TAMANHO):
                if cena3d.casa_escura(linha, coluna) and (linha, coluna) not in self.pecas:
                    self.marcadores.append(cena3d.criar_marcador(self.render, linha, coluna))

    def desselecionar(self):
        """Abaixa a peça selecionada (se houver) e apaga os marcadores."""
        if self.selecionada in self.pecas:
            peca = self.pecas[self.selecionada]
            cena3d.realcar_peca(peca, False)
            self._subir_descer(peca, TOPO_CASA)
        self.selecionada = None
        for marcador in self.marcadores:
            marcador.remove_node()
        self.marcadores = []

    def _subir_descer(self, peca, z):
        destino = Point3(peca.get_x(), peca.get_y(), z)
        LerpPosInterval(peca, 0.15, destino, blendType="easeOut").start()

    # ---------- movimento ----------

    def mover(self, destino):
        """Anima a peça selecionada num arco até a casa de destino."""
        peca = self.pecas.pop(self.selecionada)
        self.pecas[destino] = peca
        self.selecionada = None
        self.desselecionar()
        cena3d.realcar_peca(peca, False)

        inicio = peca.get_pos()
        fim = cena3d.posicao_3d(*destino)

        def posicionar(t):
            # t vai de 0 a 1: x e y andam em linha reta, z faz um arco
            suave = t * t * (3 - 2 * t)
            pos = inicio + (fim - inicio) * suave
            pos.z += math.sin(math.pi * t) * ALTURA_ARCO
            peca.set_pos(pos)

        # Bloqueia novos cliques até a peça pousar
        self.animando = True
        Sequence(
            LerpFunc(posicionar, duration=DURACAO_MOVIMENTO),
            Func(setattr, self, "animando", False),
        ).start()

    def recusar(self, peca):
        """A peça "treme" para indicar que o movimento não é permitido."""
        x = peca.get_x()
        tremida = Sequence()
        for deslocamento in (0.08, -0.08, 0.05, -0.05, 0):
            pos = Point3(x + deslocamento, peca.get_y(), peca.get_z())
            tremida.append(LerpPosInterval(peca, 0.04, pos))
        tremida.start()

    # ---------- clique ----------

    def casa_sob_mouse(self):
        """Lança um raio da câmera pelo mouse e vê onde ele cruza o tabuleiro.

        O plano usado fica na meia altura das peças, assim clicar no topo
        de uma peça acerta a casa em que ela está.
        """
        if not self.mouseWatcherNode.has_mouse():
            return None
        return self.casa_no_ponto_da_tela(self.mouseWatcherNode.get_mouse())

    def casa_no_ponto_da_tela(self, ponto_tela):
        """Casa vista no ponto da tela (coordenadas de -1 a 1), ou None."""
        perto, longe = Point3(), Point3()
        self.camLens.extrude(ponto_tela, perto, longe)
        perto = self.render.get_relative_point(self.cam, perto)
        longe = self.render.get_relative_point(self.cam, longe)
        plano = Plane(Vec3(0, 0, 1), Point3(0, 0, TOPO_CASA + ALTURA_PECA / 2))
        ponto = Point3()
        if not plano.intersects_line(ponto, perto, longe):
            return None
        return cena3d.casa_na_posicao(ponto.x, ponto.y)

    def clique(self):
        if self.animando:
            return
        self.clicar_em(self.casa_sob_mouse())

    def clicar_em(self, casa):
        """Reage a um clique na casa (linha, coluna), ou None se fora."""
        if casa is None:
            # Clicou fora do tabuleiro: cancela a seleção
            self.desselecionar()
        elif casa in self.pecas:
            # Clicou numa peça: seleciona (ou solta, se já era a selecionada)
            if casa == self.selecionada:
                self.desselecionar()
            else:
                self.selecionar(casa)
        elif self.selecionada is not None:
            if cena3d.casa_escura(*casa):
                self.mover(casa)
            else:
                # Casa clara não recebe peça
                self.recusar(self.pecas[self.selecionada])


def main():
    JogoDama().run()
