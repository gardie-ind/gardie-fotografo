# Prompts

## O pedido

Cada geração recebe a **capa** (imagem) e a **moldura**
`receitas/_moldura.txt`, com `{produto}` e `{cena}` preenchidos. Capa e
moldura são as mesmas em todos os motores, sem instrução extra para nenhum.
É o processo do "Gerar fotos com IA" do Mercado Livre: a imagem carrega o
produto, e o texto, só o nome dele e o lugar.

**Nunca descreva o produto em palavras.** O motor lê o texto como
especificação e redesenha o espelho para combinar com a leitura dele.

A moldura e a cena são escritas em inglês. A exceção é o `{produto}`, que vai
em português, como no anúncio.

## A capa (referência padronizada)

1. **Fonte:** a still de `referencias/catalogo/`, no mesmo estado de LED que a
   foto deve ter, com a pose da still. A referência principal nunca é uma foto
   de celular (a lente e a cor distorcem), uma imagem gerada por IA (inclui
   `benchmark-ml/` e qualquer aprovada) nem uma imagem retocada.
   - **Exceção para modelo sem still de estúdio** (Thiago, 2026-10-06): vale a
     foto da peça física feita no modelo da still (de frente ou em 3/4, produto
     inteiro, estado do LED da foto pedida), recortada e conferida contra o
     desenho técnico. Diferença do protótipo para a versão final que o Thiago
     apontar (ex.: o botão touch do Lumière) é apagada na capa com o retoque
     local de `guia/criterios.md`. Render só entra se bater com a foto da peça.
     Vale até existir a still de estúdio.
2. **O padrão:**
   - fundo branco puro, sem degradê, vinheta, sombra ou reflexo de chão;
   - quadro 1:1, com o produto inteiro e centrado, ocupando cerca de 93% do
     quadro;
   - nenhum pixel do produto retocado.

   Nunca corte o produto. Num close, a capa continua inteira e a região do
   close vai na `{cena}`.
3. **Preparo:** o `ensaio.py` prepara a capa a partir da still passada em
   `--ref`. Rode primeiro com `--so-preparo` e abra, ampliadas, a
   `refs/ref-1-conferencia.png` e a `refs/ref-1-mascara.png` da saída.
   - A máscara tem de ser uma silhueta branca sólida, sem buracos. O cromado
     que reflete o fundo (cúpula e disco da base, fita do garfo) é onde o
     recorte local abre buracos, e esses buracos viram branco na capa.
   - Confira também as bordas do cromado e os pinos.
   - Confira a fronteira entre a sombra do chão e o anel de borracha preto:
     a sombra sai e o anel fica inteiro.
4. **Se a máscara tiver buraco ou corte:** use `--recorte birefnet`. Se ainda
   falhar, recorte à mão para um PNG com transparência (o script usa o alfa do
   arquivo). Capa com buraco não vai para motor nenhum.
5. **Guardar e reutilizar:** guarde a capa conferida em
   `referencias/capa/<modelo>-<acabamento>-<ligado|desligado>-capa-r<n>.png`
   e reutilize com `--sem-preparo`. Quando o produto mudar, faça uma nova
   revisão (`r<n>`).

## {produto}

O título do anúncio: tipo + marca + modelo + acabamento, mais "com luz LED"
e "de mesa" ou "de parede" quando couber. Exemplo:
`Espelho de Aumento 5x com Luz LED de Mesa Gardie Classique Lux Cromado`.
Tire do título as medidas (cm, mm, polegadas) e a voltagem; nada de nomes de
peças nem da cor do LED. O aumento (5x) fica, porque é parte do nome.

## {cena}

Uma linha de até 35 palavras: lugar, objetos de cena, luz, câmera (lente,
altura, ângulo) e a posição do produto ("standing on", "mounted on the
wall"). Não pode conter:

- forma, peças, tamanho, material, cor ou LED do produto;
- medidas de qualquer tipo;
- negativos ("no ...", "without ..."), que plantam o objeto proibido;
- "warm" aplicado ao produto ou à luz dele (use "daylight" ou "soft light");
- "warm", "cozy" ou "lived-in" sem qualificação, que puxam para o rústico;
- pedido de cabo, de plug ou do conteúdo do reflexo;
- a proporção da imagem, que vai pelo parâmetro.

Para um close, nomeie só a região ("upper part of the product").

## Gerações e motores

- **Volume:** cada chamada gera uma opção. Padrão: 4 por motor por receita;
  numa rodada de comparação, 6.
- **Registro:** o `ensaio.py` grava o prompt exato, as referências e os
  parâmetros em `manifesto.json`, e a relação rótulo → motor em `mapa.json`.
  Não abra o `mapa.json` antes do veredito.
- **Candidatos atuais:** `gemini-2.5-flash-image`, `gemini-3-pro-image`, FLUX
  Kontext Max e Seedream 4 edit (os dois últimos no fal). São o padrão do
  `ensaio.py` (sem `--motores`). Confira os IDs e os preços no dia.
- **Gemini:** a imagem vai antes do texto.
- **Kontext:** aceita uma imagem só. Recebe a proporção do `--aspecto`;
  quando não a tem, recebe a mais próxima, com aviso no manifesto.
- **Seedream:** aceita mais de uma imagem.

## Quando um motor alucina

1. **Descarte e gere de novo.** Nunca corrija a forma por edição nem
   acrescentando texto sobre o produto.
2. **Registre no `placar.md`** o tipo de alucinação: forma, proporção,
   acabamento, LED ou cabo.
3. **Se a taxa de veto continuar alta**, mude um fator por vez e registre cada
   mudança como variação:
   1. motor que devolve a própria capa (diff abaixo de 2%): numa cópia
      `receitas/_moldura-place.txt`, troque "Photograph this exact product in
      a new location: {cena}." por "Place this exact product in a new
      location: {cena}." e rode com `--moldura receitas/_moldura-place.txt`
      numa rodada separada, com todos os motores (o `_` faz o `ensaio.py`
      ignorá-la como receita);
   2. use uma cena mais simples ou um enquadramento mais próximo do da capa;
   3. acrescente uma segunda referência, só nos motores que aceitam mais de
      uma imagem. Ela pode ser uma foto real de apoio, com o mesmo preparo da
      capa e o produto inteiro, para mostrar o que a capa não mostra (por
      exemplo, a traseira e a saída do cabo);
   4. use outra capa de estúdio, com outra pose;
   5. traga desafiantes do fal, como FLUX.2 com várias referências,
      Seedream 4.5 ou Qwen-Image-Edit (confira os IDs). Antes, inclua o motor
      em `parse_motores`, `parametros_motor`, `executar` e `custo_unit` do
      `ensaio.py`, que hoje só aceita `gemini:<id>`, `kontext` e `seedream`.
      Nunca rode um desafiante por fora do `ensaio.py`.
4. **Quando parar:** `placar.md` › Vencedor claro.
