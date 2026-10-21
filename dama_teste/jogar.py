"""Atalho para iniciar o jogo: python jogar.py"""

try:
    from dama_teste.main import main
except ImportError as erro:
    if erro.name not in ("panda3d", "direct"):
        raise
    raise SystemExit("O jogo precisa do Panda3D. Instale com: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
