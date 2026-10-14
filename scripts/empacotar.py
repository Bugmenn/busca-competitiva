"""Gera o arquivo de entrega T1_Aluno1_Aluno2_Aluno3.zip.

Uso: python scripts/empacotar.py Aluno1 Aluno2 Aluno3
"""

import re
import sys
import zipfile
from pathlib import Path

# Pasta raiz do projeto (um nível acima desta pasta scripts/)
RAIZ = Path(__file__).resolve().parent.parent

# Arquivos e pastas que vão para dentro do zip
ITENS = ["connect4", "tests", "jogar.py", "README.md"]


def main():
    # Os nomes dos alunos vêm da linha de comando
    nomes = sys.argv[1:]
    if not nomes:
        print("Uso: python scripts/empacotar.py Aluno1 Aluno2 Aluno3")
        sys.exit(1)

    # Cada nome vira parte do nome do arquivo: só letras, números, _ e -
    for nome in nomes:
        if not re.fullmatch(r"[\w-]+", nome):
            print(f"Nome inválido para arquivo: {nome!r}. Use só letras, números, _ ou -.")
            sys.exit(1)

    # Confere se todos os itens da entrega existem antes de gerar o zip
    faltando = [item for item in ITENS if not (RAIZ / item).exists()]
    if faltando:
        print(f"Itens não encontrados: {', '.join(faltando)}")
        sys.exit(1)

    # O PDF do documento é obrigatório na entrega
    pdfs = sorted((RAIZ / "docs").glob("*.pdf"))
    if not pdfs:
        print("Nenhum PDF encontrado em docs/. Gere o documento antes de empacotar.")
        sys.exit(1)

    # Nome do arquivo no padrão pedido: T1_Aluno1_Aluno2_Aluno3.zip
    destino = RAIZ / ("T1_" + "_".join(nomes) + ".zip")

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in ITENS:
            caminho = RAIZ / item
            # Uma pasta entra com todos os arquivos dela, exceto cache do Python
            arquivos = caminho.rglob("*") if caminho.is_dir() else [caminho]
            for arquivo in arquivos:
                if arquivo.is_file() and "__pycache__" not in arquivo.parts:
                    zf.write(arquivo, arquivo.relative_to(RAIZ))
        # O PDF vai na raiz do zip, fácil de achar
        for pdf in pdfs:
            zf.write(pdf, pdf.name)

    print(f"Arquivo gerado: {destino.name}")


if __name__ == "__main__":
    main()
