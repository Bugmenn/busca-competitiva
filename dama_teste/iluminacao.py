"""Iluminação da cena: um shader próprio, simples e portátil.

O shader calcula três parcelas de luz para cada pixel:
  - ambiente: uma luz fraca que vem de todo lado (nada fica 100% preto);
  - difusa: o "sol", mais forte nas faces viradas para ele;
  - especular: o reflexo brilhante, controlado pela rugosidade.

A direção e a cor do sol são passadas como parâmetros comuns do shader.
(As luzes nativas do Panda3D não chegam ao shader em alguns Macs, então
não dependemos delas.)

As cores são definidas em sRGB (como no "#rrggbb" de sempre), convertidas
para linear antes da conta de luz e de volta para sRGB na saída.
"""

from panda3d.core import Shader, Vec3, Vec4

# Direção em que a luz do sol VIAJA (de cima, vindo de trás e da esquerda,
# assim as sombras caem para a frente e para a direita, à vista do jogador)
DIRECAO_SOL = Vec3(0.35, -0.35, -1).normalized()
COR_SOL = Vec3(1.0, 0.96, 0.9) * 0.95
COR_AMBIENTE = Vec3(0.55, 0.58, 0.68) * 0.5

_VERTICE = """
#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 posicao_mundo;
out vec3 normal_mundo;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    posicao_mundo = (p3d_ModelMatrix * p3d_Vertex).xyz;
    normal_mundo = mat3(p3d_ModelMatrix) * p3d_Normal;
}
"""

_FRAGMENTO = """
#version 150
uniform vec4 cor_base;      // cor do objeto (sRGB)
uniform vec4 brilho;        // cor que o objeto emite sozinho (sRGB)
uniform float rugosidade;   // 0 = espelhado, 1 = fosco
uniform vec3 direcao_sol;
uniform vec3 cor_sol;
uniform vec3 cor_ambiente;
uniform vec3 posicao_camera;
in vec3 posicao_mundo;
in vec3 normal_mundo;
out vec4 cor_final;

vec3 para_linear(vec3 c) { return pow(c, vec3(2.2)); }

void main() {
    vec3 n = normalize(normal_mundo);
    vec3 l = -direcao_sol;                          // aponta PARA o sol
    vec3 v = normalize(posicao_camera - posicao_mundo);
    vec3 h = normalize(l + v);
    vec3 base = para_linear(cor_base.rgb);

    float difusa = max(dot(n, l), 0.0);
    float expoente = mix(120.0, 8.0, rugosidade);
    float especular = pow(max(dot(n, h), 0.0), expoente) * (1.0 - rugosidade) * difusa;

    vec3 luz = base * (cor_ambiente + cor_sol * difusa)
             + cor_sol * especular * 0.5
             + para_linear(brilho.rgb);
    cor_final = vec4(pow(luz, vec3(1.0 / 2.2)), cor_base.a);
}
"""


def aplicar(render):
    """Liga o shader na cena inteira, com valores padrão."""
    render.set_shader(Shader.make(Shader.SL_GLSL, _VERTICE, _FRAGMENTO))
    render.set_shader_input("direcao_sol", DIRECAO_SOL)
    render.set_shader_input("cor_sol", COR_SOL)
    render.set_shader_input("cor_ambiente", COR_AMBIENTE)
    render.set_shader_input("posicao_camera", Vec3(0, 0, 0))
    definir_material(render, Vec4(1, 1, 1, 1))


def definir_material(no, cor, rugosidade=0.6, brilho=Vec4(0, 0, 0, 1)):
    """Define cor, rugosidade e brilho próprio de um objeto (e dos filhos)."""
    no.set_shader_input("cor_base", cor)
    no.set_shader_input("rugosidade", rugosidade)
    no.set_shader_input("brilho", brilho)


def definir_brilho(no, brilho):
    no.set_shader_input("brilho", brilho)


def atualizar_camera(render, camera):
    """O reflexo especular depende de onde a câmera está: chamar todo quadro."""
    render.set_shader_input("posicao_camera", camera.get_pos(render))
