"""Montagem da cena 3D: tabuleiro, peças, sombras e marcadores.

Este módulo só DESENHA. Ele não sabe nada de regras: cria os objetos do
Panda3D e converte entre (linha, coluna) do tabuleiro e posição 3D.

No Panda3D o eixo z aponta para cima. O tabuleiro fica no plano xy,
centralizado na origem, com as brancas do lado de y negativo.
"""

from panda3d.core import (
    CardMaker, PNMImage, Point3, TextNode, Texture, TransparencyAttrib, Vec4,
)

from dama_teste import geometria, iluminacao
from dama_teste.iluminacao import definir_material

# Tabuleiro oficial da dama brasileira: 8x8
TAMANHO = 8

# Medidas (1 unidade = largura de uma casa)
TOPO_CASA = 0.1            # face de cima das casas, onde as peças apoiam
RAIO_PECA = 0.4
ALTURA_PECA = 0.16
ALTURA_SELECIONADA = 0.45  # quanto a peça sobe quando é selecionada
LARGURA_MOLDURA = 0.6


def cor(hexadecimal):
    """Converte "#rrggbb" em Vec4 (r, g, b, 1) com valores de 0 a 1."""
    return Vec4(*(int(hexadecimal[i:i + 2], 16) / 255 for i in (1, 3, 5)), 1)


# Paleta de cores da cena
COR_FUNDO = cor("#1b1f24")
COR_MESA = cor("#2a2420")
COR_MOLDURA = cor("#5a3a22")
COR_CASA_CLARA = cor("#e6cfa6")
COR_CASA_ESCURA = cor("#7a4a2a")
COR_LETRAS = cor("#e8d3b0")
COR_DESTAQUE = cor("#5ad17a")
COR_PECA = {"branca": cor("#f4f1ea"), "preta": cor("#2e2e33")}
COR_RELEVO = {"branca": cor("#e2dccd"), "preta": cor("#3e3e45")}
SEM_BRILHO = Vec4(0, 0, 0, 1)


def posicao_3d(linha, coluna):
    """Centro da casa (linha, coluna), na altura em que as peças apoiam."""
    meio = (TAMANHO - 1) / 2
    return Point3(coluna - meio, linha - meio, TOPO_CASA)


def casa_na_posicao(x, y):
    """Inverso de posicao_3d: qual casa contém o ponto (x, y)? None se fora."""
    meio = TAMANHO / 2
    if 0 <= x + meio < TAMANHO and 0 <= y + meio < TAMANHO:
        return (int(y + meio), int(x + meio))
    return None


def casa_escura(linha, coluna):
    """Na dama as peças só ficam nas casas escuras (a casa a1 é escura)."""
    return (linha + coluna) % 2 == 0


def criar_tabuleiro(render):
    """Cria mesa, moldura, casas e coordenadas (a-h, 1-8)."""
    mesa = render.attach_new_node(geometria.caixa("mesa", 60, 60, 0.1))
    mesa.set_z(-0.6)
    definir_material(mesa, COR_MESA, 0.95)

    lado = TAMANHO + 2 * LARGURA_MOLDURA
    moldura = render.attach_new_node(geometria.caixa("moldura", lado, lado, 0.5))
    moldura.set_z(-0.5)
    definir_material(moldura, COR_MOLDURA, 0.45)

    forma_casa = geometria.caixa("casa", 1, 1, TOPO_CASA)
    for linha in range(TAMANHO):
        for coluna in range(TAMANHO):
            casa = render.attach_new_node(forma_casa.make_copy())
            centro = posicao_3d(linha, coluna)
            casa.set_pos(centro.x, centro.y, 0)
            escura = casa_escura(linha, coluna)
            definir_material(casa, COR_CASA_ESCURA if escura else COR_CASA_CLARA, 0.5)

    # Letras (colunas) e números (linhas) gravados na moldura
    borda = TAMANHO / 2 + LARGURA_MOLDURA / 2
    for i in range(TAMANHO):
        meio = i - (TAMANHO - 1) / 2
        _texto_na_moldura(render, "abcdefgh"[i], Point3(meio, -borda, 0.005))
        _texto_na_moldura(render, str(i + 1), Point3(-borda, meio, 0.005))


def _texto_na_moldura(render, texto, posicao):
    """Texto deitado sobre a moldura, legível do lado das brancas."""
    no = TextNode(texto)
    no.set_text(texto)
    no.set_align(TextNode.A_center)
    no.set_text_color(COR_LETRAS)
    caminho = render.attach_new_node(no)
    caminho.set_pos(posicao.x, posicao.y - 0.12, posicao.z)  # centraliza
    caminho.set_p(-90)  # deita o texto sobre o tabuleiro
    caminho.set_scale(0.35)
    caminho.set_shader_off()  # texto usa o desenho padrão do Panda3D (sem luz)


def criar_peca(render, cor_peca, linha, coluna):
    """Cria uma peça: um disco com um anel em relevo no topo.

    `cor_peca` é "branca" ou "preta".
    """
    peca = render.attach_new_node(
        geometria.cilindro("peca", RAIO_PECA, ALTURA_PECA))
    definir_material(peca, COR_PECA[cor_peca], 0.3)
    relevo = peca.attach_new_node(
        geometria.cilindro("relevo", RAIO_PECA * 0.7, 0.02))
    relevo.set_z(ALTURA_PECA)
    relevo.set_shader_input("cor_base", COR_RELEVO[cor_peca])
    peca.set_pos(posicao_3d(linha, coluna))
    return peca


def realcar_peca(peca, ligado):
    """Liga ou desliga um leve brilho verde na peça selecionada."""
    iluminacao.definir_brilho(peca, COR_DESTAQUE * 0.3 if ligado else SEM_BRILHO)


def criar_marcador(render, linha, coluna):
    """Disco verde e brilhante que indica uma casa de destino possível."""
    marcador = render.attach_new_node(geometria.cilindro("marcador", 0.15, 0.01))
    marcador.set_pos(posicao_3d(linha, coluna))
    definir_material(marcador, COR_DESTAQUE * 0.4, 0.8, brilho=COR_DESTAQUE * 0.6)
    return marcador


# ---------- sombras ----------

def _textura_sombra(tamanho=64):
    """Disco escuro que vai ficando transparente do centro para a borda."""
    imagem = PNMImage(tamanho, tamanho, 4)
    meio = (tamanho - 1) / 2
    for x in range(tamanho):
        for y in range(tamanho):
            distancia = ((x - meio) ** 2 + (y - meio) ** 2) ** 0.5 / meio
            opacidade = max(0.0, 1 - distancia) ** 1.5
            imagem.set_xel_a(x, y, 0, 0, 0, opacidade)
    textura = Texture("sombra")
    textura.load(imagem)
    return textura


class Sombras:
    """Uma sombra suave sob cada peça ("blob shadow").

    A sombra fica sempre deitada no tabuleiro, deslocada na direção em
    que a luz viaja. Quando a peça sobe, a sombra se afasta, cresce e
    fica mais clara, como uma sombra de verdade.
    """

    def __init__(self, render):
        self.render = render
        self.textura = _textura_sombra()
        self.sombras = {}  # {peça: NodePath da sombra}

    def adicionar(self, peca):
        cartao = CardMaker("sombra")
        cartao.set_frame(-1, 1, -1, 1)
        sombra = self.render.attach_new_node(cartao.generate())
        sombra.set_p(-90)  # deita o cartão no plano do tabuleiro
        sombra.set_texture(self.textura)
        sombra.set_transparency(TransparencyAttrib.M_alpha)
        sombra.set_depth_write(False)
        sombra.set_shader_off()
        self.sombras[peca] = sombra

    def remover(self, peca):
        self.sombras.pop(peca).remove_node()

    def atualizar(self):
        """Reposiciona as sombras conforme a altura atual de cada peça."""
        direcao = iluminacao.DIRECAO_SOL
        deslocamento = (direcao.x / -direcao.z, direcao.y / -direcao.z)
        for peca, sombra in self.sombras.items():
            altura = peca.get_z() - TOPO_CASA + ALTURA_PECA / 2
            sombra.set_pos(peca.get_x() + deslocamento[0] * altura,
                           peca.get_y() + deslocamento[1] * altura,
                           TOPO_CASA + 0.003)
            sombra.set_scale(RAIO_PECA * (1.25 + altura * 0.5))
            sombra.set_alpha_scale(0.75 / (1 + altura * 1.5))
