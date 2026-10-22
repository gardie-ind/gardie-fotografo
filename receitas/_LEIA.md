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
- **Modelos de parede e de ventosa:** as cenas de parede têm o prefixo
  `parede-` e dizem onde o produto está fixado ("the product mounted on the
  wall of a bright powder room ..."). Ventosa ainda não tem receita: crie a
  primeira no primeiro lote, com o prefixo `ventosa-`.
- **Uma cena por modelo e acabamento** (Thiago, 22/10/2026: "Cada modelo e
  cada cor vai ter uma composição diferente"): a grade dos LUX está em
  `/mnt/project-files/fotografo/2026-10-22-lux-ambientadas/plano.json`. A
  torneira da cena acompanha o acabamento do espelho e serve de escala.
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
| `mesa-close-base` | mesa | close baixo da parte de baixo, topo cortado pelo quadro | 10202CR-5 |
| `mesa-carrara-hotel` | mesa | bancada de Carrara em banheiro de hotel, de frente | — |
| `mesa-travertino-banheira` | mesa | bancada de travertino creme, banheira ao fundo, 3/4 | — |
| `mesa-penteadeira-blush` | mesa | penteadeira de mármore rosado, parede nude, de frente | — |
| `mesa-penteadeira-creme` | mesa | penteadeira laqueada creme no quarto, plano aberto | — |
| `mesa-nicho-arco-blush` | mesa | console de ônix rosa num nicho em arco, 3/4 | — |
| `mesa-microcimento-cinza` | mesa | bancada de microcimento cinza com cuba de apoio, 3/4 | — |
| `mesa-calcario-janela-fosca` | mesa | bancada de calcário cinza junto à janela fosca, de frente | — |
| `mesa-terrazzo-canelado` | mesa | bancada de terrazzo, azulejo canelado branco, de frente | — |
| `mesa-japandi-carvalho` | mesa | bancada de carvalho claro, japandi, câmera baixa 3/4 | — |
| `parede-banheiro-bancada` | parede | parede de pedra clara sobre a bancada, de frente | — |
| `parede-lavabo` | parede | lavabo de porcelanato claro, 3/4 | — |
| `parede-banheiro-amplo` | parede | banheiro amplo, bancada suspensa, plano aberto | — |
| `parede-papel-de-parede` | parede | lavabo com papel de parede botânico sálvia, de frente | — |
| `parede-close-fixacao` | parede | close da fixação na parede, topo cortado | — |
| `parede-lavabo-travertino` | parede | lavabo de travertino, torneira de parede, 3/4 | — |
| `parede-papel-de-parede-blush` | parede | lavabo com papel de parede botânico blush, de frente | — |
| `parede-zellige-cinza` | parede | zellige cinza sobre bancada de concreto, 3/4 | — |
| `parede-cal-terrazzo` | parede | parede caiada sobre bancada de terrazzo, plano aberto | — |
| `parede-marmore-creme-hotel` | parede | mármore creme de hotel, janela alta, de frente | — |
| `parede-azulejo-blush` | parede | azulejinho rosa sobre cuba suspensa, de frente | — |
| `parede-microcimento-amplo` | parede | microcimento cinza, plano aberto | — |
| `parede-penteadeira-quarto` | parede | parede sobre penteadeira creme no quarto, 3/4 | — |
| `parede-gesso-rosado` | parede | gesso rosado sobre bancada de pedra, de frente | — |
| `parede-linho-cinza` | parede | papel de parede de linho cinza, 3/4 | — |
| `parede-calcario-janela` | parede | calcário claro junto à janela grande, de frente | — |
| `close-parede-canelada` | parede | close da parte de cima na parede canelada branca | — |
