# busca-competitiva

Trabalho T1 — Busca Competitiva: **Damas (regra brasileira)** contra uma IA que usa **Minimax com poda alfa-beta**.

## Como jogar

Requisito: Python 3.8 ou mais novo. Não é preciso instalar nenhuma biblioteca.

```bash
python jogar.py
```

1. Escolha a dificuldade pelo número: `1` Fácil, `2` Médio ou `3` Difícil. Ela define quantos lances a IA olha à frente: 2, 4 ou 6.
2. Escolha sua cor pelo número: `1` Brancas (começam), `2` Pretas ou `3` Sortear.
3. Na sua vez, digite as **casas** da jogada, por exemplo `c3 d4` (também vale `c3-d4` ou `c3d4`). Numa captura múltipla, basta digitar o primeiro salto (ex.: `c3 e5`): como a captura é obrigatória, o jogo continua capturando **automaticamente**. Quando só existe um caminho, a peça segue sozinha e o jogo avisa. Se a captura puder seguir por mais de um caminho, o jogo pergunta só a próxima casa; ali, `voltar` refaz a jogada. Também dá para digitar o caminho inteiro de uma vez: `c3 e5 g7`. O jogo não mostra a lista de jogadas possíveis: encontrar o lance faz parte do jogo. Se a jogada for inválida, o jogo explica o motivo (por exemplo, captura obrigatória). Para encerrar, digite `sair`.

### Tabuleiro

- `b` e `p` são peões brancos e pretos. `B` e `P` são damas.
- As casas aparecem coloridas, como num tabuleiro de verdade.
- O último lance fica em **verde**: a casa de onde a peça saiu, as casas onde ela pousou durante as capturas e a casa final. As peças capturadas nesse lance ficam em **vermelho**.
- Acima do tabuleiro aparece quantas peças cada lado já capturou.

Num terminal sem cores, as casas claras aparecem como `░░░`. A peça que acabou de jogar aparece como `[b]`, a casa de saída e os pousos intermediários como `*` e as capturadas como `x`.

### Regras usadas

- Tabuleiro 8×8 com 12 peças de cada lado, só nas casas escuras. A casa a1 é escura.
- O peão anda 1 casa na diagonal para a frente. Ele captura para a frente e para trás.
- A captura é obrigatória. Se houver mais de uma, vale a que captura **mais peças** (lei da maioria).
- O peão vira dama quando **termina** o lance na última fileira. A dama anda e captura à distância.
- Perde quem não tiver jogada, seja por falta de peças ou por estar bloqueado.
- A partida empata depois de 20 lances seguidos **de cada jogador** só com damas, sem captura nem movimento de peão (item 16 das Regras Oficiais da Confederação Brasileira de Damas). As regras de empate de finais específicos, como duas damas contra uma, não foram implementadas.

## Testes

```bash
python -m unittest -v
```

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `damas/tipo_peca.py` | tipos de peça (b, p, B, P) |
| `damas/tabuleiro.py` | posição inicial, contagem de peças e desenho do tabuleiro |
| `damas/regras.py` | jogadas válidas (função sucessor), aplicação de jogada e fim de jogo |
| `damas/ia.py` | Minimax com poda alfa-beta e função de avaliação |
| `damas/console.py` | partida humano × IA no terminal |
| `jogar.py` | atalho para iniciar o jogo |
| `tests/test_damas.py` | testes automáticos |
| `docs/` | documento do trabalho (descrição, regras, formulação, análise) |
| `PENDENCIAS_DO_GRUPO.md` | o que o grupo ainda precisa fazer antes de entregar |
