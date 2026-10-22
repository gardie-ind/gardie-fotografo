# Produto: a verdade física

Este arquivo serve para **verificar** as imagens. Nada dele vai para o prompt,
porque o motor recebe a imagem e não a descrição (`guia/prompts.md`). Se o
texto divergir da still, vale a still; avise o Thiago para corrigir aqui.

## Linha e montagem

A montagem foi lida nas stills de `referencias/catalogo/`. O detalhe de cada
peça é sempre o da still.

| Modelo | Linha | Montagem | LED e cabo | Stills (acabamento) | Apoio em `referencias/` |
|---|---|---|---|---|---|
| Classique Lux | LUX | mesa | sim | cromado, e gold, red gold, brushed nickel e black matte por recoloração; todos com o logo a laser, desligado e ligado nos 3 tons (aprovadas em 22/10/2026, `aprovadas/10202*`; numeração em Cabeça dos modelos LUX › Stills dos LUX) | `classique-lux/`, vídeo |
| Royale Lux | LUX | mesa | sim | cromado, e gold, red gold, brushed nickel e black matte por recoloração; todos com o logo a laser, desligado e ligado nos 3 tons (aprovadas em 22/10/2026, `aprovadas/10288*`; numeração em Cabeça dos modelos LUX › Stills dos LUX) | `royale-lux/` (cabo e traseira em dourado; `Royale Lux ON/OFF` = cromado real ambientado), vídeo (13 s: cabo saindo de trás da base) |
| Mobile Lux | LUX | parede | sim | cromado, e gold, red gold, brushed nickel e black matte por recoloração; todos com o logo a laser, desligado e ligado nos 3 tons (aprovadas em 22/10/2026, `aprovadas/10455*`; numeração em Cabeça dos modelos LUX › Stills dos LUX) | vídeo (13 s: aceso, cabo pendendo) |
| Visage Lux | LUX | parede | sim | cromado, e gold, red gold, brushed nickel e black matte por recoloração; todos com o logo a laser, desligado e ligado nos 3 tons (aprovadas em 22/10/2026, `aprovadas/10509*`; numeração em Cabeça dos modelos LUX › Stills dos LUX) | `visage-lux/` (cabo e traseira; suporte dourado), vídeo |
| Flex Lux | LUX | parede | sim | cromado, e gold, red gold, brushed nickel e black matte por recoloração; todos com o logo a laser, desligado e ligado nos 3 tons (aprovadas em 22/10/2026, `aprovadas/10554*`; numeração em Cabeça dos modelos LUX › Stills dos LUX) | `flex-lux/` (ambientadas: `ON/OFF`, `IMG_0623h`), vídeo (13 s: cabo pendendo) |
| Lumière | LUX | parede, articulado como o Mobile Lux | sim, fio embutido | nenhuma | nenhum (não fotografar) |
| Flex | Clássica Premium | parede | não | cromado | `flex/` |
| Flex Cristal | Clássica Premium | parede | não | cromado | — |
| Mobile | Clássica Premium | parede | não | cromado | — |
| Royale Cristal | Clássica Premium | mesa | não | cromado | `royale-cristal/` |
| Svelte | Essencial | parede | não | cromado | — |
| Classique | Essencial | mesa | não | cromado | — |
| Doubler | Essencial | parede | não | cromado | — |
| Platine | Essencial | mesa | não | branco, cromado | — |
| Miroir | Essencial | mesa | não | branco, cristal, preto | `miroir/` |
| Jolie | Essencial | mesa | não | branco, cromado | — |
| Beauté | Essencial | mesa: de mão, apoiado no pé | não | branco, cristal, preto | `beaute/` |
| Vide | Box/Ventosa | ventosa | não | branco | — |
| Branche | a confirmar | parede, braço articulado simples, cabeça dupla-face num aro com dois pinos | não | nenhuma em `catalogo/` | `branche/` (foto do Thiago, cromado em fundo branco, 2043 × 1800 px, 21/10/2026: base dos acabamentos) |

- **Pré-lançamento:** Doubler e Lumière.
- **Faces:** os modelos sem LED são dupla-face (um lado normal, plano, e o
  outro de aumento), exceto Svelte e Vide, que têm face única. Na dupla-face,
  o verso é outro espelho com o mesmo aro. Os LUX têm carcaça atrás (ver
  Traseira).
- **Fotos de apoio** (fotos reais de celular, de campanha e vídeos de
  `referencias/videos/`): mostram o que a still não mostra, como a traseira,
  o cabo e a escala em uso. Para usar um vídeo, extraia o frame para
  `_versoes/`: `pip install imageio-ffmpeg` e rode o executável de
  `imageio_ffmpeg.get_ffmpeg_exe()` com `-ss <segundos> -i <vídeo>
  -frames:v 1 <saída.png>`.
- **Acabamento sem still de estúdio** (qualquer acabamento à venda que a
  coluna Stills não lista): sem lote, até o Thiago aprovar uma referência
  real daquele acabamento. As fotos douradas do Royale Lux e do Visage Lux são
  apoio, não capa.
- **Acabamento por recoloração** (Thiago, 21/10/2026, piloto Flex Lux:
  "Acabamentos aprovados"): sem foto real do acabamento, a versão sai da
  still cromada aprovada, sem IA. Só o metal muda de cor, calibrado nas
  referências de cor Deca; vidro, anel de luz, logo, carcaça de plástico e
  peças de nylon ou borracha ficam com o pixel original, e o cabo só muda no
  black matte, onde fica preto. A recoloração aprovada pelo Thiago, modelo a
  modelo, vale como still daquele acabamento (coluna Stills).
  - Gold, red gold e black matte: `ferramentas/acabamentos.py`, com os números
    do piloto, menos o tom do red gold.
  - Red gold: o tom é o de uma peça real (foto do Thiago, 22/10/2026,
    `referencias/red-gold/foto-real-red-gold-parede-2026-10-22.jpeg`, escolhido
    "igual à foto" no mesmo dia). O tom Deca de 21/10 lia rosa: medido em
    CIELAB por faixa de L*, a peça real tem matiz 69 a 74° e croma 12 a 27,
    contra 59 a 71° e 28 a 37 do Deca (`ferramentas/medir_acabamento.py tom`;
    `ferramentas/novo_tom.py` gira o matiz e reduz o croma da tabela). A
    claridade não foi calibrada: na still, o metal reflete o estúdio branco.
    Medida de veto em `guia/criterios.md`, item b.
  - Black matte: a carcaça também é pintada de preto (Thiago, 22/10/2026:
    "Nos modelos preto fosco, nós pintamos as carcaças de preto também").
    No Classique Lux só o anel de borracha fica como está; no Royale Lux,
    nada; no Visage Lux, só a ponta do cabo.
    Medida de veto em `guia/criterios.md`, item b.
  - Brushed nickel: `ferramentas/escovado.py` (22/10/2026), porque a versão de
    21/10 lia polida ("O níquel escovado não tem acabamento escovado"). O
    reflexo se espalha através da peça (gaussiana de 5 px) e o riscado segue
    cada peça, em duas escalas, sumindo onde o sentido é indefinido e nos 4 px
    junto da silhueta. O tom Deca e a faixa de luminância são os mesmos. A
    medida está em `guia/criterios.md`, item b.

## Cabeça dos modelos LUX

- **Frente**, do centro para fora: vidro → difusor jateado iluminado (o anel
  de luz) → aro cromado externo. Não há anel cromado entre o vidro e o
  difusor. A cabeça é um círculo; em perspectiva, uma elipse coerente com o
  ângulo.
- **Traseira** (nunca cromada, nunca com segundo espelho):
  - **Classique Lux** (`classique-lux/classique-lux-traseira-cabo.jpeg`):
    carcaça de plástico BRANCO com aro cromado fino e interruptor basculante
    branco no centro, marcado "II O I".
  - **Royale Lux** (`royale-lux/royale-lux-cabo-da-base.jpeg`): carcaça
    creme/branca com aletas de ventilação dos dois lados, disco central com
    parafuso e impressão, passa-fio no centro de baixo.
  - **Visage Lux** (`visage-lux/`): carcaça branca com aletas e interruptor
    O/I na lateral (aparece em 3/4); suporte em trompete sobre placa
    retangular de cantos arredondados.
  - **Mobile Lux e Flex Lux:** só nos frames de vídeo. Sem foto parada, não
    enquadre a traseira.
- **Traseira dos modelos sem LED:** na dupla-face, o outro espelho; na face
  única, não há foto real. Não enquadre.
- **LED:** três tons de divulgação, 3000K, 4500K e 6000K. A linha LUX vai sair
  com as 3 cores e dimerizável (Thiago, 22/10/2026). Os nomes são de
  divulgação: o 3000K é o render de 4500K, o 4500K é o de 5150K e o 6000K, o de
  6000K, porque o 3000K real lia laranja demais para divulgação (Thiago,
  22/10/2026). O 4500K tem a cor do difusor das stills de catálogo.
- **Padrão de luz** (Thiago, 22/10/2026, 18:44: "O meio termo está perfeito.
  Vamos seguir com ele como padrão para todos os outros espelhos"): sem IA,
  `ferramentas/luz_padrao.py`. A luz do LED é a diferença entre a still ligada e
  a apagada. Ela é recolorida pela curva de Planck, ajustada às fotos reais
  `classique-lux-frontal-luz-4500k/-6000k.jpeg`, com +80% de brilho e metade
  da compressão dos realces (ganho 1,8, joelho 0,8, mistura 0,5).
- **Logo:** "gardie" gravado a laser no espelho, e não mais impresso no
  difusor (Thiago, 22/10/2026, 19:08: "Só a logomarca da Gardi no espelho e
  não na borda jateada. Ele brilha na cor do anel fosco de luz"; aprovado às
  20:12). Desenho E-0001-V1 (`ferramentas/logo-laser/E-0001-V1.pdf`): 20 mm
  de largura, 2,98 mm de altura, topo a 8,71 mm da borda de baixo da área
  espelhada, centrado. Desligado, fica cinza escuro, da cor do difusor
  apagado. Ligado, tem a cor do anel naquele tom e um brilho leve em volta dos
  traços. Nas stills do Visage Lux e do Royale Lux, o vidro em volta do logo
  já sai branco, e o logo aceso quase some. Nenhum logo no difusor nem no
  aro. No Flex (sem LED), o logo segue impresso no vidro, embaixo.
- **Stills dos LUX:** as de `referencias/catalogo/` mostram o logo impresso
  antigo e servem só para a forma. Para capa e verificação, valem as
  aprovadas de 22/10/2026, feitas sem IA (`ferramentas/lote_logo.py`): em
  cada pasta `aprovadas/<código><acabamento>/`, -1 ligado em 4500K, -2
  desligado, -3 ligado em 3000K e -4 ligado em 6000K. No Classique Lux
  cromado (10202CR), por causa das ambientadas, são -3 (4500K), -4
  (desligado), -8 (3000K) e -9 (6000K).

## Suportes (a região que mais alucina)

- **Classique Lux:** garfo em U de fita única que abraça a metade de baixo da
  cabeça, com pinos nas laterais na altura do centro. O garfo se fixa num
  pivô cromado curto, no topo do sino; o cabo entra nele por cima, vindo de
  trás da cabeça. Logo abaixo do pivô nasce o sino cromado, sem coluna e sem
  pescoço. O sino abre numa cúpula sobre o disco cromado, que tem um anel
  fino de borracha preta embaixo.
- **Royale Lux:** coluna cilíndrica fina e reta com colarinhos perto do topo e
  da base, garfo em U com pinos laterais e base em cúpula rasa.
- **Mobile Lux:** placa retangular cromada de parede com 2 tampas redondas,
  braço articulado duplo de dois segmentos tubulares e garfo com pinos
  laterais.
- **Visage Lux:** a cabeça fica presa direto num suporte curto de parede, sem
  braço.
- **Flex Lux, Flex e Flex Cristal:** braço pantográfico (sanfona) cromado,
  preso à parede.
- **Demais modelos:** vale a still.

## Cabo e plug

- **Quem tem cabo à vista:** os LUX, exceto o Lumière (fio embutido, sem cabo
  aparente; cabo pendurado é invenção). Nenhum modelo sem LED tem cabo.
- **O cabo:** branco, fino (cerca de 5 mm, tipo fio de abajur), com 1,5 m do
  espelho ao plug. No black matte (BL.MT), o cabo é preto (Thiago,
  21/10/2026).
- **Rota no Classique Lux e no Royale Lux (mesa):** sai do meio da traseira
  da cabeça, logo abaixo do interruptor → desce numa alça curta → entra no
  pivô, por cima → corre por dentro do suporte → sai por um furo na traseira
  da base, rente à mesa → segue pela superfície até a tomada
  (`classique-lux-traseira-cabo`, `-diagonal`, `-diagonal-2`).
  - **De frente, com a borda da cabeça quase encostada no pivô:** a alça fica
    escondida atrás da cabeça, e a junção cabeça/sino aparece sem cabo
    (still; `classique-lux-frontal-*`; 10202CR-1, -4 e -5).
  - **De 3/4, com vão à vista entre a borda de baixo da cabeça e o pivô:** a
    alça aparece nesse vão. Ela surge de trás da borda da cabeça, sem ponto
    de saída à vista, e desce em curva até o topo do pivô, onde entra por
    cima (Thiago, 2026-10-12, com a rota marcada na `1x1-piloto/A1`).
  - **Sobre a superfície, de frente ou de 3/4:** o cabo sai de TRÁS da base,
    rente a ela (`classique-lux-frontal-*`; vídeo do Royale Lux, 13 s). Sem
    cabo à vista também é real, quando ele segue reto para trás da base, mas
    com o LED aceso o cabo faz falta (`guia/criterios.md` › d2).
  - **Para que lado, na superfície:** de 3/4, o cabo sai de trás da base
    para o lado da traseira da cabeça, que é o lado em que aparece a alça
    (`classique-lux-diagonal`, `-diagonal-2`). Numa vista espelhada, cabo e
    alça trocam de lado juntos (Thiago, 2026-10-19, na 10202CR-7). De frente,
    os dois lados são reais (`classique-lux-frontal-*`, para a esquerda).
  - **De lado, de trás ou com câmera alta:** a alça cabeça → pivô aparece
    inteira (`classique-lux-lateral`, `-traseira-cabo`, `-virado-para-cima`).
  - Rotas que não existem: cabo por fora do suporte até a tomada; cabo saindo
    do topo da base direto para a parede; cabo na frente do balcão.
- **Rota nos modelos de parede (Mobile, Visage e Flex Lux):** o cabo sai de
  trás da cabeça (no Visage, do verso, ao lado do pé do suporte) e pende
  solto, abaixo dela, até a tomada ou a borda do quadro. Aparece mesmo de
  frente (vídeos do Mobile Lux e do Flex Lux, 13 s). Não passa pela placa nem
  pelo braço. Mostrar a tomada é opcional.
  - **Peça na frente do cabo** (no Mobile Lux, a alça do garfo, embaixo da
    cabeça): o cabo sobe por trás dela e aparece no vão entre ela e a cabeça,
    até sumir atrás da cabeça. Nunca termina na alça (Thiago, 22/10/2026, na
    `aprovadas/10455CR` de 16/10; vídeo do Mobile Lux, 12 a 13 s). No Visage e
    no Flex Lux, o cabo sai direto de baixo da cabeça, sem peça na frente.
- **Plug** (`referencias/chicote-eletrico/`): padrão NBR 14136, 2 pinos,
  branco, corpo chato com alívio de tensão nervurado. Face hexagonal achatada
  de 35,5 × 14 mm, pinos a 19 mm, cantos R5. É fino: cerca de 14 mm de
  espessura, menos de 3× o diâmetro do cabo.

## Medidas e proporções (só para verificação)

- **Classique Lux:** cabeça Ø 250 mm (com aro) e base Ø 200 mm. Razões lidas
  com grade (±3%):
  - disco ÷ cabeça (eixo maior): 0,78 na still ligada; ≈0,70 na foto
    frontal real (`classique-lux-frontal-desligado.jpeg`), porque a
    perspectiva muda as razões;
  - topo do sino ÷ disco: 0,19;
  - pivô → topo do disco (onde a cúpula encontra o disco) ÷ disco: 0,36 na
    still; ≈0,41 com a câmera mais baixa (foto frontal real).
  - Medidas por contorno (lote 2026-10-11, método em
    `/mnt/project-files/fotografo/2026-10-11-classique-lux-cromado/lote-git/verificacao.md`,
    a cópia do lote que saiu do git), na capa
    `classique-lux-cromado-ligado-capa-r1` (câmera a ≈7°) e nas três fotos
    frontais reais de `referencias/classique-lux/` (câmera a ≈30°):

    | Razão | Capa | Fotos reais |
    |---|---|---|
    | disco ÷ cabeça (eixo maior) | 0,753 | 0,695 a 0,697 |
    | Ø vidro ÷ cabeça | 0,700 | 0,735 a 0,738 |
    | difusor ÷ cabeça | 0,109 | 0,079 a 0,086 |
    | aro ÷ cabeça | 0,041 | 0,046 a 0,052 |
    | topo do sino (2% do disco abaixo do pivô) ÷ disco | 0,198 | 0,228 a 0,234 |
    | pivô → disco (1ª linha com ≥97% da base) ÷ disco | 0,354 | 0,296 a 0,302 |
    | altura dos pinos ÷ altura da cabeça | 0,51 | — |
    | LED, B/R do halo ÷ branco neutro | 0,98 | 0,78 (4500K) e 1,16 (6000K) |

    Fita do garfo e espessura do disco ainda não foram medidas. Divergências
    com a leitura em grade, a confirmar com o Thiago: disco ÷ cabeça na still
    (0,78 na grade, 0,753 aqui) e pivô → disco na foto real (≈0,41 na grade,
    0,30 aqui; a elipse do disco mostra a câmera da foto real mais alta que a
    da still, não mais baixa).
- **Demais razões e modelos:** meça na capa no primeiro lote (vidro,
  difusor, aro, fita do garfo, pinos, espessura do disco; braço e placa nos de
  parede) e registre aqui.
- **Escala com pessoa:** a cabeça de Ø 25 cm tem cerca de 1,5× a largura de um
  rosto adulto.
- **Óptica:** espelho côncavo, foco de 60 cm; ampliação de 5x a 48 cm, 10x a
  54 cm e 15x a 56 cm. As consequências para o reflexo estão em
  `guia/cena.md`.

**Códigos, acabamentos à venda e medidas** (catálogo operacional e loja). O
código do ML é o código-base + sufixo (10202CR = Classique Lux cromado).
Sufixos: CR cromado, GL dourado, GL.RD red gold, BL.MT black matte, BL.NO
black noir, BR branco, CL cristal, NK.BU brushed nickel. Nos 12 códigos com
†, gold, red gold, brushed nickel e black matte valem para todos, à venda ou a
lançar (Thiago, 21/10/2026: "Estes acabamentos são para todos os espelhos lux,
se não tiver, devemos criar"). O Ø espelhado é o nominal do catálogo e pode
não ser o vidro visível; para conferir a escala, use as dimensões totais
(mesa: altura × largura × profundidade).

| Modelo | Código | Acabamentos à venda | Ø espelhado | Dimensões totais (alcance) |
|---|---|---|---|---|
| Classique Lux | 10202 † | CR, GL, GL.RD, NK.BU, BL.MT | 203 mm | 37 × 28 × 20,5 cm |
| Royale Lux | 10288 † | CR, GL, GL.RD, NK.BU, BL.MT | 152 mm | 32 × 22 × 14,5 cm |
| Mobile Lux | 10455 † | CR, GL, GL.RD, NK.BU, BL.MT | 152 mm | 33 × 26,5 cm (braço até 42 cm) |
| Visage Lux | 10509 † | CR, GL, GL.RD, NK.BU, BL.MT | 203 mm | 26,5 × 26,5 cm (projeção até 16 cm) |
| Flex Lux | 10554 † | CR, GL, GL.RD, NK.BU, BL.MT | 203 mm | 35 × 26 cm (até 56,5 cm) |
| Lumière | 22005 † | CR, GL, GL.RD, NK.BU, BL.MT | 152 mm | 33 × 26,5 cm |
| Flex | 10578 † | CR, GL, GL.RD, NK.BU, BL.MT | 170 mm | 35 × 26 cm (até 56,5 cm) |
| Flex Cristal | 10639 † | CR, GL, GL.RD, NK.BU, BL.MT | 145 mm | 35 × 26 cm (até 56,5 cm) |
| Mobile | 10431 † | CR, GL, GL.RD, NK.BU, BL.MT | 170 mm | 33 × 26,5 cm (até 42 cm) |
| Royale Cristal | 10271 † | CR, GL, GL.RD, NK.BU, BL.MT | 145 mm | 31 × 23,5 × 17 cm |
| Svelte | 10479 † | CR, GL, GL.RD, NK.BU, BL.MT | 175 mm | 17,5 × 25 cm (até 45 cm) |
| Classique | 10233 | CR, BL.MT, BR, GL, GL.RD | 220 mm | 37 × 28 × 20,5 cm |
| Doubler | 10486 | CR, BL.MT | 145 mm | 20,1 × 25 cm |
| Platine | 10240 | CR, BR, GL, GL.RD | 145 mm | 29 × 21,5 × 17 cm |
| Miroir | 20201 | BR, BL.NO, CL | 145 mm | 25 × 18,5 × 9 cm |
| Jolie | 10301 | CR, BR, GL, GL.RD | 115 mm | 20,5 × 15 × 14 cm |
| Beauté | 20102 | CL, BR, BL.NO | 125 mm | 26 × 16 × 12,5 cm |
| Vide | 10103 | BR, BL.NO | 120 mm | 14,5 × 14,5 × 7,5 cm |
| Branche | 10448 † | CR, GL, GL.RD, NK.BU, BL.MT | a confirmar | a confirmar (cadastrado no Tiny) |
