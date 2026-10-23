# ⚠️ O que falta fazer antes de entregar o T1

O jogo de damas, a IA, os testes e o documento já estão prontos. Falta só o que depende do grupo. Sigam na ordem e marquem `[x]` quando terminarem.

## 1. Validar o jogo com a professora
- [ ] Confirmar que **Damas (regra brasileira)** foi aprovado. O Connect 4 já tinha sido escolhido por outro grupo.

## 2. Testar no seu computador (5 minutos)
Precisa só do Python 3.8 ou mais novo. Não é preciso instalar nada. Na pasta do projeto:

```bash
python jogar.py          # joga uma partida contra a IA
python -m unittest -v    # deve terminar com "Ran 43 tests ... OK"
```

- [ ] Joguei uma partida e funcionou, e o tabuleiro aparece colorido.
- [ ] Os testes passaram.

## 3. Ler o documento e preencher os campos em branco
Arquivo: **`docs/T1_BuscaCompetitiva_Damas.docx`** (abrir no Word).

- [ ] Todo mundo leu o documento e concorda com o texto. Leiam com atenção a seção "Reflexão", porque a atividade pede a opinião do grupo.
- [x] **Capa:** nomes dos 5 integrantes já preenchidos (Felipe Boos, Gabriel Bugmann, Matheus Hillesheim, Pedro Godri e Yasmin Victoria Alves de Souza). Conferir a grafia.
- [x] **Capa:** professora (Ligia Ribeiro dos Anjos) e cidade (Blumenau) já preenchidas.
- [ ] **Seção "Organização do grupo":** a tabela já está preenchida com uma divisão de tarefas **sugerida**. Cada um confere a sua linha e corrige se não for o que fez de verdade.
- [ ] Procurar `[` no documento (Ctrl+F) e conferir que não sobrou nenhum campo entre colchetes.
- [ ] Salvar o .docx e depois usar **Arquivo → Salvar como → PDF**, com o mesmo nome e na mesma pasta. O PDF antigo é substituído.

## 4. Gerar o arquivo de entrega
- [x] Zip gerado: `T1_Felipe_Gabriel_Matheus_Pedro_Yasmin.zip`, na pasta do projeto, com `damas/`, `tests/`, `jogar.py`, `README.md` e o PDF. Se alguém mudar o documento ou o código, o zip precisa ser gerado de novo.

## 5. Entregar
- [ ] **Só uma pessoa** envia o zip, em nome do grupo inteiro.
- [ ] Combinar quem envia e até quando: ______________________

---

**Dúvidas sobre o código?** O `README.md` explica como jogar, quais regras foram usadas e o que tem em cada arquivo. A IA está em `damas/ia.py`, com o código todo comentado.
