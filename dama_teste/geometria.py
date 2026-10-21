"""Formas 3D simples (caixa e cilindro) geradas por código.

Assim o jogo não depende de nenhum arquivo de modelo. Cada função
devolve um GeomNode com vértices e normais (as normais são usadas no
cálculo da iluminação). O eixo z aponta para cima, como no Panda3D.
"""

import math

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, Vec3,
)


class _Malha:
    """Acumula vértices e triângulos e no fim gera o GeomNode."""

    def __init__(self, nome):
        self.nome = nome
        self.dados = GeomVertexData(nome, GeomVertexFormat.get_v3n3(), Geom.UH_static)
        self.vertice = GeomVertexWriter(self.dados, "vertex")
        self.normal = GeomVertexWriter(self.dados, "normal")
        self.triangulos = GeomTriangles(Geom.UH_static)
        self.total = 0

    def ponto(self, posicao, normal):
        """Adiciona um vértice e devolve o índice dele."""
        self.vertice.add_data3(posicao)
        self.normal.add_data3(normal)
        self.total += 1
        return self.total - 1

    def quadrado(self, a, b, c, d, normal):
        """Quadrilátero a-b-c-d em sentido anti-horário visto de fora."""
        i = [self.ponto(p, normal) for p in (a, b, c, d)]
        self.triangulos.add_vertices(i[0], i[1], i[2])
        self.triangulos.add_vertices(i[0], i[2], i[3])

    def no(self):
        geom = Geom(self.dados)
        geom.add_primitive(self.triangulos)
        no = GeomNode(self.nome)
        no.add_geom(geom)
        return no


def caixa(nome, largura, profundidade, altura):
    """Caixa centrada em x e y, com a base em z=0 e o topo em z=altura."""
    malha = _Malha(nome)
    centro = Vec3(0, 0, altura / 2)
    meia = Vec3(largura / 2, profundidade / 2, altura / 2)
    x, y, z = Vec3(meia.x, 0, 0), Vec3(0, meia.y, 0), Vec3(0, 0, meia.z)
    # Cada face: (normal, u, v) com u x v = normal, para manter a orientação
    for normal, u, v in ((x, y, z), (-x, -y, z), (y, z, x),
                         (-y, x, z), (z, x, y), (-z, y, x)):
        c = centro + normal
        malha.quadrado(c - u - v, c + u - v, c + u + v, c - u + v, normal.normalized())
    return malha.no()


def cilindro(nome, raio, altura, segmentos=48):
    """Cilindro em pé, com a base em z=0 e o topo em z=altura."""
    malha = _Malha(nome)
    cima, baixo = Vec3(0, 0, 1), Vec3(0, 0, -1)
    for i in range(segmentos):
        a0 = 2 * math.pi * i / segmentos
        a1 = 2 * math.pi * (i + 1) / segmentos
        p0 = Vec3(math.cos(a0) * raio, math.sin(a0) * raio, 0)
        p1 = Vec3(math.cos(a1) * raio, math.sin(a1) * raio, 0)
        h = Vec3(0, 0, altura)
        # Lateral: normal apontando para fora, suavizada entre os segmentos
        n0, n1 = p0.normalized(), p1.normalized()
        i0, i1 = malha.ponto(p0, n0), malha.ponto(p1, n1)
        i2, i3 = malha.ponto(p1 + h, n1), malha.ponto(p0 + h, n0)
        malha.triangulos.add_vertices(i0, i1, i2)
        malha.triangulos.add_vertices(i0, i2, i3)
        # Tampa de cima e de baixo (leque de triângulos a partir do centro)
        t = [malha.ponto(p, cima) for p in (h, p0 + h, p1 + h)]
        malha.triangulos.add_vertices(*t)
        b = [malha.ponto(p, baixo) for p in (Vec3(0, 0, 0), p1, p0)]
        malha.triangulos.add_vertices(*b)
    return malha.no()
