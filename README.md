# busca-competitiva

Trabalho T1 — Busca Competitiva: **Connect 4 (Lig 4)** contra uma IA que usa **Minimax com poda alfa-beta**.

## Como jogar

Requisito: Python 3.8 ou mais novo. Não é preciso instalar nenhuma biblioteca.

```bash
python jogar.py
```

1. Escolha a dificuldade (`facil`, `medio` ou `dificil`). Ela define a profundidade da busca: 2, 4 ou 6 jogadas à frente.
2. Escolha quem começa (`eu` ou `ia`).
3. Na sua vez, digite o número da coluna (1 a 7). Você joga com `X` e a IA com `O`.

Para cada jogada, a IA mostra quantos estados analisou e quanto tempo levou.

## Testes

```bash
python -m unittest -v
```

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `connect4/tabuleiro.py` | estado, função sucessor (jogadas válidas), aplicação de jogada, teste de vitória/empate |
| `connect4/ia.py` | Minimax com poda alfa-beta e função heurística |
| `connect4/main.py` | partida humano × IA no terminal |
| `jogar.py` | atalho para iniciar o jogo |
| `tests/test_connect4.py` | testes automáticos |
| `docs/` | documento do trabalho (descrição, regras, formulação, análise) |
| `scripts/empacotar.py` | gera o `.zip` de entrega |

## Gerar o arquivo de entrega

```bash
python scripts/empacotar.py Aluno1 Aluno2 Aluno3
```

Gera `T1_Aluno1_Aluno2_Aluno3.zip` com o código, os testes, o README e o PDF de `docs/`.
