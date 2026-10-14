# ⚠️ O que falta fazer antes de entregar o T1

O jogo, os testes e o documento já estão prontos. Falta só o que depende do grupo. Sigam na ordem e marquem `[x]` quando terminarem.

## 1. Validar o jogo com a professora
- [ ] Confirmar que o **Connect 4 (Lig 4)** foi aprovado.
  Se ela pedir outro jogo, avisem antes de seguir, porque o código e o documento são todos sobre o Connect 4.

## 2. Testar no seu computador (5 minutos)
Precisa só do Python 3.8 ou mais novo. Não é preciso instalar nenhuma biblioteca. Na pasta do projeto:

```bash
python jogar.py          # joga uma partida contra a IA
python -m unittest -v    # deve terminar com "Ran 16 tests ... OK"
```

- [ ] Joguei uma partida e funcionou.
- [ ] Os testes passaram.

## 3. Ler o documento e preencher os campos em branco
Arquivo: **`docs/T1_BuscaCompetitiva_Connect4.docx`** (abrir no Word).

- [ ] Todo mundo leu o documento e concorda com o texto. Leiam com atenção a seção 6, "Reflexão": a atividade pede a opinião do grupo.
- [ ] **Capa:** trocar `[NOME DO ALUNO 1]`, `[NOME DO ALUNO 2]`, `[NOME DO ALUNO 3]` pelos nomes completos.
- [ ] **Capa:** trocar `[NOME DA PROFESSORA]` e `[CIDADE]`.
- [ ] **Seção 7, "Organização do grupo":** preencher a tabela com o que cada um fez, o prazo e a situação.
- [ ] Procurar por `[` no documento (Ctrl+F) e conferir que não sobrou nenhum campo entre colchetes.
- [ ] Salvar o .docx e depois **Arquivo → Salvar como → PDF**, com o mesmo nome e na mesma pasta: `docs/T1_BuscaCompetitiva_Connect4.pdf`. O novo PDF substitui o antigo.

## 4. Gerar o arquivo de entrega
Usem os nomes **sem espaço e sem acento**, na ordem que vai no nome do arquivo:

```bash
python scripts/empacotar.py Aluno1 Aluno2 Aluno3
```

O comando gera `T1_Aluno1_Aluno2_Aluno3.zip` na pasta do projeto, com o código, os testes, o README e o PDF.

- [ ] Abri o zip e conferi que o PDF dentro dele já tem os nomes preenchidos.

## 5. Entregar
- [ ] **Só uma pessoa** envia o zip, em nome do grupo inteiro.
- [ ] Combinar quem envia e até quando: ______________________

---

**Dúvidas sobre o código?**
- O `README.md` explica como rodar o jogo e o que tem em cada arquivo.
- A IA fica em `connect4/ia.py`. O código é todo comentado.
