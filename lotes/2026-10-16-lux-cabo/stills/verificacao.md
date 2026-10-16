# Verificação · cabo real nas stills de estúdio LUX · 2026-10-16

Pedido do Thiago (2026-10-16): "Vamos continuar arrumando as fotos dos
produtos LUX, colocando o cabo elétrico."

As 10 stills de estúdio dos LUX cromados (`referencias/catalogo/espelho-de-aumento-com-ring-light-5X-cromado-gardie-<modelo>-<estado>-em-fundo-cinza.jpg`)
não têm cabo, e com o LED aceso o cabo faz falta (`guia/criterios.md` › d2).
Esta rodada só acrescenta o cabo, na rota real de cada modelo
(`guia/produto.md` › Cabo e plug). Nada mais na foto mudou.

## O que preciso de você

1. **Veredito nas 10:** quais você publicaria.
2. **Lado do cabo nas de mesa (S7 a S10):** pus à direita, como na A1
   aprovada e no vídeo do Royale. Se preferir à esquerda, como na foto
   frontal real do Classique, eu espelho a rota.

## Fotos

| Rótulo | Foto | Final |
|---|---|---|
| S1 | Mobile Lux ligado | `S1-mobile-lux-ligado-com-cabo.jpg` |
| S2 | Mobile Lux desligado | `S2-mobile-lux-desligado-com-cabo.jpg` |
| S3 | Flex Lux ligado | `S3-flex-lux-ligado-com-cabo.jpg` |
| S4 | Flex Lux desligado | `S4-flex-lux-desligado-com-cabo.jpg` |
| S5 | Visage Lux ligado | `S5-visage-lux-ligado-com-cabo.jpg` |
| S6 | Visage Lux desligado | `S6-visage-lux-desligado-com-cabo.jpg` |
| S7 | Classique Lux ligado | `S7-classique-lux-ligado-com-cabo.jpg` |
| S8 | Classique Lux desligado | `S8-classique-lux-desligado-com-cabo.jpg` |
| S9 | Royale Lux ligado | `S9-royale-lux-ligado-com-cabo.jpg` |
| S10 | Royale Lux desligado | `S10-royale-lux-desligado-com-cabo.jpg` |

Pranchas: `prancha-stills-parede.png` (S1 a S6) e `prancha-stills-mesa.png`
(S7 a S10), com antes e depois e o trecho da saída do cabo em 100%.

## Rotas

- **Parede (Mobile, Flex e Visage):** o cabo sai de trás da cabeça (no
  Visage, do verso, ao lado do pé do suporte) e pende solto até a borda de
  baixo do quadro. No Mobile ele passa atrás do braço, que fica na frente; não
  corre pelo braço nem pela placa. Mobile e Flex seguem os vídeos (13 s, cabo
  pendendo); o Visage, o vídeo do Visage Lux (cabo entre o centro da cabeça e
  o lado da parede).
- **Mesa (Classique e Royale):** o cabo sai de trás da base e corre pela
  superfície até a borda direita. A alça cabeça → pivô fica escondida atrás da
  cabeça, como o guia prevê para a foto de frente. No Royale, o vão entre a
  borda da cabeça e o garfo tem cerca de 3 mm, menos que o cabo, e o vídeo do
  Royale de frente também não mostra a alça.
- **Por que o cabo de mesa aparece afastado da base:** a câmera dessas stills
  está a cerca de 7° de altura (elipse do topo do disco do Classique: 127 ÷
  1.062 px). Desse ângulo, o chão logo atrás da base fica escondido por ela, e
  o cabo só aparece onde passa a uns 10 cm da borda de trás. Por isso ele surge
  do flanco da cúpula (Classique) ou da base (Royale), acima da borda de trás.

## Método

- `ferramentas/cabo_real.py`, modo suspenso (cilindro iluminado), sem IA.
- **Largura de 5 mm** pela escala de cada foto: Mobile 53 px, Flex 32 px,
  Visage 50 px, Classique 48 a 46 px (base de 200 mm = 2.160 px, menor ao
  fundo pela perspectiva) e Royale 56 a 53 px (base de ~145 mm = 1.790 px).
- **Brilho por ponto**, medido no fundo junto do cabo: lado da sombra 0,92 ×
  fundo e lado da luz 1,45 × fundo, até 248. A referência é a carcaça branca do
  Visage Lux, que lê cerca de 1,7× o fundo cinza ao lado.
- **Grão** medido no fundo, por ponto (passa-alta de 3 px, longe das bordas),
  aplicado depois do desfoque e igual nos três canais (fundo neutro).
- **Luz:** nas de parede, de cima e da esquerda, pela frente
  ([-0,55, -0,35, -0,75]); nas de mesa, de cima ([-0,2, -0,85, -0,3]), porque
  o cabo deitado recebe a luz no topo. Com a câmera a 7°, a sombra de contato
  fica escondida atrás do próprio cabo.
- **Máscara do que fica na frente do cabo** (`mascaras/<foto>-visivel.png`):
  preenchimento a partir de sementes no fundo, com faixa fixa, crescimento por
  coluna até a primeira borda forte e transição fracionária nas bordas suaves,
  sem IA. Furos isolados da transição foram tapados pela média dos vizinhos
  (ou pela mistura objeto/fundo, nos pixels de borda). No Mobile, a faixa de
  cima do braço reflete o fundo e foi cortada à mão na linha da borda (y 3938).
- Ligado e desligado usam a mesma rota. Mobile, Visage e Royale usam a mesma
  máscara nos dois estados (as fotos são iguais na região do cabo); Flex e
  Classique têm uma máscara por estado.
- O recorte que o script pede é a foto com alfa = 255 − visível.
- **Saída em JPEG** com as mesmas tabelas de quantização da foto do catálogo,
  4:4:4, EXIF e 300 dpi.

## Conferência

- Em 1×, 100% e 6× (10× nas saídas), o cabo surge de trás da cabeça, do braço
  ou da base sem ponto de saída à vista, e a borda do objeto da frente fica
  inteira.
- Diff contra a foto do catálogo, antes do JPEG: 0 pixel alterado a mais de
  meia largura do cabo + 8 px do eixo dele, nas 10. A área alterada vai de
  0,14% (Visage) a 0,56% (Mobile) do quadro.
- Pontos soltos no corpo do cabo (furos da máscara): nenhum, conferido por
  script e em 10×.
- JPEG: a recompressão muda até 7 níveis (99,9% dos pixels até 2).

## Notas

- As stills de `referencias/catalogo/` continuam sem cabo: são a identidade
  do produto para gerar e conferir. As versões com cabo vão para `aprovadas/`
  depois do veredito.
