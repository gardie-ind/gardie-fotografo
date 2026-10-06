# Receitas de cena

- **`_moldura.txt`:** a moldura do prompt, com os marcadores `{produto}` e
  `{cena}`. O `ensaio.py` exige os dois.
- **Cada `.txt` sem `_` no início é uma cena:** uma linha em inglês, de até 35
  palavras, com o lugar, os objetos, a luz, a câmera e a posição do produto.
  As regras de escrita estão em `guia/prompts.md`. O `ensaio.py` ignora
  arquivos que começam com `_` e linhas que começam com `#`.
- **Nome:** kebab-case, uma cena por arquivo. Com o prefixo `mesa-`, a cena só
  serve a modelos de mesa (o Beauté conta como mesa, apoiado no pé). Sem
  prefixo, serve a qualquer montagem.
- **Modelos de parede:** `parede-lavabo` e `parede-banheiro-3-4` (lote do Lumière, 2026-10-06). **Ventosa:** ainda não tem receita. Crie a primeira
  no primeiro lote, com o prefixo `parede-` ou `ventosa-`, dizendo onde
  o produto está fixado (por exemplo, "the product mounted on the wall of a
  bright powder room ...").
- **Seleção por lote:** o `ensaio.py` não filtra por montagem. Passe só as
  receitas compatíveis com a montagem do modelo, por exemplo `--receitas
  receitas/close-detalhe.txt receitas/mesa-banheiro-bancada.txt`. A moldura é
  encontrada sozinha.
- **Formatos:** um formato de canal não vira receita nova. É a mesma cena
  numa rodada à parte, com outro `--aspecto` (pastas e rótulos: `CLAUDE.md` ›
  Onde fica cada coisa).

| Receita | Montagem | Foto | Benchmark |
|---|---|---|---|
| `mesa-banheiro-bancada` | mesa | bancada de banheiro, produto inteiro, câmera de frente | 10202CR-1 |
| `mesa-banheiro-banheira` | mesa | bancada com banheira e janela ao fundo, câmera 3/4 | 10202CR-2 |
| `mesa-penteadeira-quarto` | mesa | plano aberto, penteadeira inteira no quadro (testa a escala no ambiente) | 10202CR-3 |
| `mesa-papel-de-parede` | mesa | aparador diante de um papel de parede elegante | — |
| `close-detalhe` | qualquer | close da parte de cima, produto cortado pelo quadro | 10202CR-4 |
| `parede-lavabo` | parede | lavabo, produto inteiro na parede, câmera de frente | — |
| `parede-banheiro-3-4` | parede | parede de banheiro ao lado da bancada, câmera 3/4 | — |
| `mesa-close-base` | mesa | close baixo da parte de baixo, topo cortado pelo quadro | 10202CR-5 |
