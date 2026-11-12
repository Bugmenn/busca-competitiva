# CLAUDE.md — busca-competitiva

Guia para o Claude Code neste repositório.

## Leitura obrigatória ao iniciar

Antes de qualquer tarefa, ler nesta ordem:
1. Este `CLAUDE.md`
2. `Memory/busca-competitiva.memory` — memória do projeto (contexto fixo, restrições, decisões)
3. `history/busca-competitiva.history` — só quando precisar do histórico do que já foi feito

Regras gerais de processo estão no `CLAUDE.md` global (`~/.claude/CLAUDE.md`) — não duplicar aqui. O que segue é específico deste repositório.

## Autorização específica deste projeto

Nada além da Regra 05 global por enquanto. Convenção de commit: a definir no primeiro commit de código.

## Comandos essenciais

O repositório tem uma pasta por trabalho (desde `56d00bd`, do Pedro). Os comandos rodam **de dentro da pasta**: os nomes têm espaço e não são pacotes Python, então `python -m unittest` na raiz roda 0 testes.

```
cd "DAMA COMPETITIVA"; python jogar.py         # T1: damas humano x IA (testes: python -m unittest -v → 46)
cd "BUSCA GENETICOS"; python main.py           # T2: AG do caixeiro-viajante (abre o gráfico; ~5 s)
cd "BUSCA GENETICOS"; python -m unittest -v    # T2: 14 testes
```

## Arquitetura — T2 `BUSCA GENETICOS/` (Algoritmos Genéticos, caixeiro-viajante)

20 cidades fixas, população 20, 10.000 gerações. Base do Pedro: `cidades.py` (x = linha 0, y = linha 1), `fitness.cvfun` (tradução fiel do Matlab da professora; recalcula a matriz de distâncias a cada chamada, o que é aceito), `thanos.py` (ordena e mantém a melhor metade; `corta_melhores` tem `[:10]` fixo, e por isso `main.py` fatia por `n_manter`).
- `roleta.py` — pesos lineares inversos ao ranking (10/55…1/55); `crossover.py` — cycle crossover, com a posição recebida como parâmetro (o teste reproduz a Figura 1 do enunciado); `mutacao.py` — troca de 2 posições.
- `main.py` — `executar_ag` (a mutação só nos filhos = elitismo, decisão do plano aprovado), `mostrar_resultados` (os 6 itens do enunciado), `plotar` (rota + curva com eixo log).
- Depende de **numpy + matplotlib** (`requirements.txt`). Nesta máquina estão instalados com `pip --user` (o `C:\Python312` dá erro de permissão).
- Converge por volta da geração 100–900; o custo final varia entre 3,57 e 4,57 (10 execuções com semente, média 3,92; limite do enunciado, não bug). Explicação para a equipe em `BUSCA GENETICOS/EXPLICACAO.md`.

## Arquitetura — T1 `DAMA COMPETITIVA/` (caminhos abaixo relativos a essa pasta)

Trabalho T1 de faculdade (Busca Competitiva): **damas, regra brasileira**, humano × IA com Minimax + poda alfa-beta. O jogo mudou de Connect 4 para damas em 2026-10-21 (outro grupo pegou Connect 4). A versão 3D em Panda3D do Pedro foi **removida a pedido do usuário**; ela e o Connect 4 só existem no histórico do git (`673ffb6`, `211d3c4`).
- `damas/tipo_peca.py` — enum com símbolos Unicode (brancas ⛂ peão/♚ dama, pretas ⛀/♔; troca do Pedro em `f9f2ccd`), VAZIO "□". **Testes não usam o símbolo direto:** `montar(c3="b")` traduz letra→símbolo pelo mapa `PECA` em `tests/test_damas.py`.
- `damas/tabuleiro.py` — a1 escura (`casa_escura` = (l+c) par), brancas nas linhas 0-2 subindo; `texto_tabuleiro(tab, ultimo, cor)` desenha casas grudadas de 3 caracteres com fundo ANSI (fallback sem cor: `░░░`, `[⛂]`, `*`, `x`).
- `damas/regras.py` — DFS de capturas do Pedro (lei da maioria, dama voadora), `aplicar_movimento` **altera no lugar** (usar `copiar`), `atualizar_contador` (chamar ANTES de aplicar) e `resultado` (teste terminal, empate em `LIMITE_EMPATE`=40 = 20 lances de cada jogador, conforme item 16 das regras da CBD).
- `damas/ia.py` — `minimax`/`escolher_jogada(tab, vez, contador, prof)`, avaliação 100/300 + avanço + centro, ordenação capturas/promoção, `DIFICULDADES` 2/4/6 (8 chega a 27 s no pior caso).
- `damas/console.py` — menus numéricos (dificuldade; cor com sorteio), jogada digitada só pelas casas (**sem lista de lances, decisão do usuário**), placar de capturas, destaque do último lance; força stdin/stdout UTF-8.
- `docs/` — documento de entrega (.docx + .pdf), gerado por script docx-js fora do repo; mudanças agora pelo Word.
- Zip de entrega: **adiado a pedido do usuário** — não criar empacotador até ele pedir.

**Stack:** T1 em Python 3.8+ só com biblioteca padrão; T2 com numpy + matplotlib.

## Padrões críticos

- **Setup do Claude só no projeto:** skills, agentes, memória e hooks deste projeto ficam dentro do repositório (`.claude/`, `Memory/`, `history/`), nunca em `~/.claude/`. Só o `CLAUDE.md` global de regras fica fora.

## Pitfalls conhecidos

- **Código comentado é requisito da atividade:** todo código novo leva comentário simples em pt-BR, linha a linha nos trechos de lógica.
- **`tests/__init__.py` é obrigatório:** sem ele `python -m unittest` roda 0 testes e diz OK. Conferir sempre o número de testes executados.
- **Números do documento devem vir do código:** qualquer medição citada no documento (nós com/sem poda, tempo) tem de ser medida com a IA real e refeita se a heurística mudar.

## Skills e agentes deste projeto

Origem: repositório `Bugmenn/claude`. As skills `arquitetura-projeto` e `otimizacao-codigo` já chegam pela sincronização do chat e não foram copiadas para cá.

| Skill / Agente | Quando usar |
|---|---|
| `revisao-final` (skill) | ao terminar qualquer mudança de código, antes de dar como concluída (Regra 08) |
| `frontend-design` (skill) | ao criar ou refazer interface — direção estética, tipografia |
| `revisor-codigo` (agente) | revisar PR, branch, diff ou mudanças recentes, sem modificar código |
| `depurador` (agente) | erro, exception, teste quebrando ou bug relatado — investiga até a causa raiz |
| `testador` (agente) | escrever/rodar testes, teste que reproduz bug, levantar o que falta cobrir |
| `especialista-banco` (agente) | queries SQL, migrations, procedures, schema e índices |
| `documentador` (agente) | README, docstrings, documentação de API, runbooks, onboarding |
| `descritor-pr` (agente) | escrever a descrição de uma Pull Request a partir do diff |

`revisao-final` × `revisor-codigo`: a skill orquestra o fechamento (dispara o `revisor-codigo` duas vezes, uma cega, e corrige tudo numa passada); o agente só revisa.

## Documentação por domínio (`.claude/docs/`)

Nenhum domínio documentado ainda.

## Credenciais locais

Nenhuma credencial usada ainda. Quando houver, registrar aqui só a origem, nunca o valor.
