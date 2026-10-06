# Produto: a verdade física

Este arquivo serve para **verificar** as imagens. Nada dele vai para o prompt,
porque o motor recebe a imagem e não a descrição (`guia/prompts.md`). Se o
texto divergir da still, vale a still; avise o Thiago para corrigir aqui.

## Linha e montagem

A montagem foi lida nas stills de `referencias/catalogo/`. O detalhe de cada
peça é sempre o da still.

| Modelo | Linha | Montagem | LED e cabo | Stills (acabamento) | Apoio em `referencias/` |
|---|---|---|---|---|---|
| Classique Lux | LUX | mesa | sim | cromado, ligado e desligado | `classique-lux/`, vídeo |
| Royale Lux | LUX | mesa | sim | cromado, ligado e desligado | `royale-lux/` (cabo e traseira em dourado; `Royale Lux ON/OFF` = cromado real ambientado), vídeo (13 s: cabo saindo de trás da base) |
| Mobile Lux | LUX | parede | sim | cromado, ligado e desligado | vídeo (13 s: aceso, cabo pendendo) |
| Visage Lux | LUX | parede | sim | cromado, ligado e desligado | `visage-lux/` (cabo e traseira; suporte dourado), vídeo |
| Flex Lux | LUX | parede | sim | cromado, ligado e desligado | `flex-lux/` (ambientadas: `ON/OFF`, `IMG_0623h`), vídeo (13 s: cabo pendendo) |
| Lumière | LUX | parede: placa, braço longo e braço curto articulados | sim, fio embutido | nenhuma de estúdio; capa de foto da peça física (exceção abaixo) | `lumiere/` (protótipo em níquel escovado, ligado; desenhos V3) |
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

## Lumière (pré-lançamento)

Capa por exceção (Thiago, 2026-10-06): `referencias/capa/lumiere-nk-bu-ligado-capa-r3.png`
(vidro limpo; a r2 tinha a sujeira do protótipo; a r1 tinha o reflexo verde da lente sobre o braço, que os motores copiaram
como uma luva inventada; a r2 neutraliza essa cor),
feita de `lumiere/lumiere-nk-bu-ligado-frontal-aberto.jpg` (foto de celular do
protótipo, ligado), recortada localmente, com o botão touch apagado.

- **Peças, da parede para fora** (desenhos `lumiere/desenhos/`, V3; conte uma a
  uma, de frente):
  1. placa de parede E-0010: retângulo de 68 × 119,6 mm, cantos R8,5, chapa de
     2 mm com a borda dobrada (6,1 mm de espessura total). Rente à parede.
  2. 2 tampas redondas (E-0013), uma em cima e uma embaixo, centradas na placa.
  3. articulação da placa, no meio dela, entre as tampas: mancal superior
     (E-0014), barril do braço longo e mancal inferior (E-0009), empilhados.
  4. braço longo: tubo reto Ø 12,7 mm (haste de 192 mm).
  5. cotovelo: 2 cilindros empilhados (ponteiras do braço longo e do curto).
  6. braço curto: tubo Ø 12,7 mm (haste de 74 mm), na horizontal.
  7. rótula central: cilindro vertical preso no CENTRO DA TRASEIRA da cabeça
     (B-0001), que desce até perto da borda de baixo. De frente fica quase
     todo escondido atrás da cabeça.
  8. cabeça: Ø 204,5 mm, aro de lado reto e traseira em cúpula rasa; 43 mm de
     profundidade sem a rótula (65 mm com ela).

  Nada além disso: garfo, pinos laterais, poste, roseta, segunda placa ou
  terceira tampa é peça inventada (veto a). Faltar qualquer item visível na
  vista também é veto a.
- **Razões (vista de frente, braço paralelo à parede; desenho A-0001):**

  | Razão | Valor | Faixa |
  |---|---|---|
  | altura da placa ÷ Ø da cabeça | 0,585 | ±10% |
  | largura ÷ altura da placa | 0,57 | ±10% |
  | Ø do tubo do braço ÷ Ø da cabeça | 0,062 | ±20% (tubo fino) |
  | eixo da placa → eixo do cotovelo ÷ Ø da cabeça | ≈0,99 | ±10%; menor só com o braço girado para a câmera |
  | Ø da tampa ÷ largura da placa | ≈0,30 | ±15% |

  Em 3/4 ou de lado, meça as alturas (que não encurtam): altura da placa ÷
  altura da cabeça = 0,585 ±10%.
- **Placa na parede (veto a):** a face da placa fica no plano da parede. Em
  3/4, as bordas de cima e de baixo da placa convergem para o mesmo ponto de
  fuga das juntas horizontais da parede (±3°), e as bordas laterais ficam
  paralelas às verticais da parede. A espessura visível da placa não passa de
  0,09 da largura dela (6,1 ÷ 68). Placa girada em relação à parede, saltada
  dela, em pé como uma caixa ou com sombra de vão por trás: veto.
- **Cabeça:** espelho côncavo 7,5" com aro jateado; o anel de luz é o aro
  jateado do próprio vidro, por dentro de um aro metálico fino. Vidro claro ÷
  cabeça ≈ 0,73 na foto frontal; vidro ÷ diâmetro externo do anel de luz = 0,81 (capa r1, ±10%).
- **Logo:** impresso no vidro, embaixo, com uma linha de texto pequena sob ele.
- **Touch:** o protótipo tem um botão touch no vidro, acima do logo; a versão
  final tem o touch no toque da própria estrutura metálica, sem botão visível
  (Thiago, 2026-10-06). Na foto: nenhum botão no vidro (critério a2, apagado
  no retoque) e nenhum botão na estrutura.
- **Suporte (a região que mais alucina no Lumière):** o braço curto prende na
  rótula central, atrás da cabeça. Não há garfo em U nem pinos laterais
  (garfo = veto a; 10 de 24 no lote 2026-10-06 r1), nem poste ou torneira.
- **LED:** 4500K, branco neutro (Thiago, 2026-10-06). A foto do protótipo não tem
  branco de referência; confira a cor nas candidatas pelo passo 6 de
  `guia/criterios.md` com alvo 0,78 (faixa 0,63 a 0,93).
- **Vidro:** limpo. A foto do protótipo tinha sujeira, que os motores copiaram
  (rodada r2); a capa r3 tem o vidro limpo, preenchido com o tom do próprio
  vidro, logo preservado.
- **Cabo:** embutido; cabo à vista é veto (d).
- **Acabamento da capa:** níquel escovado (NK.BU): metal acetinado, sem o
  espelhamento do cromado. Os outros acabamentos não têm referência.
- **Medidas do desenho V3:** conjunto fechado 252,6 × 270,3 mm, cabeça Ø ≈ 205 mm,
  profundidade 73 mm, 362 mm com o braço esticado. Cabeça ÷ altura da placa: 1,71
  no desenho e 1,99 na foto frontal (perspectiva do celular perto, a confirmar
  se o protótipo segue a V3). A tabela de códigos abaixo (152 mm, 33 × 26,5 cm)
  é anterior à V3.

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
- **LED:** duas temperaturas, quente (4500K) e fria (6000K) (catálogo; fotos
  `classique-lux-frontal-luz-4500k/-6000k.jpeg`). A foto segue o estado e a
  cor da still usada (cada LUX tem still ligada e desligada). Confirmar com o
  Thiago qual temperatura as stills mostram e se o interruptor II/O/I alterna
  as duas. A medida da cor está em `guia/criterios.md`, passo 6.
- **Logo:** vale a posição da still. Nos LUX, "gardie" em minúsculas
  estilizadas, cinza, impresso no difusor iluminado, na parte de baixo do anel,
  nunca no aro. No Flex, impresso no vidro, embaixo.
- **Mudança do logo (confirmar com o Thiago antes do próximo lote LUX):**
  segundo ele, a marca deixa (ou já deixou) a borda de luz e passa a ser
  gravada a laser no espelho, formando uma janela de luz no formato da marca.
  Não está confirmado se isso já está em produção. Até a confirmação, vale a
  still. Se já estiver em produção, as stills atuais estão desatualizadas
  nesse ponto: é preciso uma still real nova antes de novas capas, e então se
  atualizam este item e o critério g.

## Suportes (a região que mais alucina)

- **Classique Lux:** garfo em U de fita única que abraça a metade de baixo da
  cabeça, com pinos nas laterais na altura do centro. O garfo se fixa num
  pivô cromado curto, no topo do sino; o cabo entra por trás dele. Logo
  abaixo do pivô nasce o sino cromado, sem coluna e sem pescoço. O sino abre
  numa cúpula sobre o disco cromado, que tem um anel fino de borracha preta
  embaixo.
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
  espelho ao plug.
- **Rota no Classique Lux e no Royale Lux (mesa):** sai da carcaça atrás da
  cabeça, pelo passa-fio no centro de baixo → faz uma alça curta → entra no
  pivô, por trás → corre por dentro do suporte → sai por um furo na traseira
  da base, rente à mesa → segue pela superfície até a tomada.
  - **De frente ou de 3/4 frontal:** a alça fica escondida atrás da cabeça, e
    a junção cabeça/sino aparece sem cabo (still; `classique-lux-frontal-*`;
    10202CR-1, -4 e -5). O que pode aparecer é o cabo sobre a superfície,
    saindo de TRÁS da base, rente a ela (`classique-lux-frontal-*`; vídeo do
    Royale Lux, 13 s). Sem cabo à vista também é real, quando ele segue reto
    para trás da base.
  - **De lado, de trás ou com câmera alta:** a alça cabeça → pivô aparece
    (`classique-lux-lateral`, `-traseira-cabo`, `-virado-para-cima`).
  - Rotas que não existem: cabo por fora do suporte até a tomada; cabo saindo
    do topo da base direto para a parede; cabo na frente do balcão.
- **Rota nos modelos de parede (Mobile, Visage e Flex Lux):** o cabo sai de
  trás da cabeça (no Visage, do verso, ao lado do pé do suporte) e pende
  solto, abaixo dela, até a tomada ou a borda do quadro. Aparece mesmo de
  frente (vídeos do Mobile Lux e do Flex Lux, 13 s). Não passa pela placa nem
  pelo braço. Mostrar a tomada é opcional.
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
  - cabeça (lidas na `capa/classique-lux-cromado-ligado-capa-r1`, linha
    horizontal pelo centro, lote de 2026-10-01): Ø vidro ÷ Ø cabeça 0,73;
    largura do difusor ÷ Ø cabeça 0,092 (81 e 78 px dos dois lados, centrado);
    aro ÷ Ø cabeça ≈0,044. Na vertical da capa (cabeça em 3/4), o difusor de
    cima é mais largo que o de baixo (≈0,087 e ≈0,070): a perspectiva desloca
    o anel, então compare cada lado com a referência de ângulo parecido.
  - LED da still ligada (halo logo por dentro do anel, B/R ÷ fundo neutro):
    ≈0,91 a 0,93, entre os 0,78 (4500K) e 1,07 (6000K) das fotos reais.
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
black noir, BR branco, CL cristal, NK.BU brushed nickel. O Ø espelhado é o
nominal do catálogo e pode não ser o vidro visível; para conferir a escala,
use as dimensões totais (mesa: altura × largura × profundidade).

| Modelo | Código | Acabamentos à venda | Ø espelhado | Dimensões totais (alcance) |
|---|---|---|---|---|
| Classique Lux | 10202 | CR, GL, GL.RD | 203 mm | 37 × 28 × 20,5 cm |
| Royale Lux | 10288 | CR, GL, GL.RD | 152 mm | 32 × 22 × 14,5 cm |
| Mobile Lux | 10455 | CR, GL, GL.RD | 152 mm | 33 × 26,5 cm (braço até 42 cm) |
| Visage Lux | 10509 | CR, GL, GL.RD | 203 mm | 26,5 × 26,5 cm (projeção até 16 cm) |
| Flex Lux | 10554 | CR, GL, GL.RD, BL.MT | 203 mm | 35 × 26 cm (até 56,5 cm) |
| Lumière | 22005 | CR, GL, GL.RD, NK.BU | 152 mm | 33 × 26,5 cm |
| Flex | 10578 | CR, GL, GL.RD | 170 mm | 35 × 26 cm (até 56,5 cm) |
| Flex Cristal | 10639 | CR, GL, GL.RD | 145 mm | 35 × 26 cm (até 56,5 cm) |
| Mobile | 10431 | CR, GL, GL.RD | 170 mm | 33 × 26,5 cm (até 42 cm) |
| Royale Cristal | 10271 | CR, GL, GL.RD | 145 mm | 31 × 23,5 × 17 cm |
| Svelte | 10479 | CR, GL, GL.RD | 175 mm | 17,5 × 25 cm (até 45 cm) |
| Classique | 10233 | CR, BL.MT, BR, GL, GL.RD | 220 mm | 37 × 28 × 20,5 cm |
| Doubler | 10486 | CR, BL.MT | 145 mm | 20,1 × 25 cm |
| Platine | 10240 | CR, BR, GL, GL.RD | 145 mm | 29 × 21,5 × 17 cm |
| Miroir | 20201 | BR, BL.NO, CL | 145 mm | 25 × 18,5 × 9 cm |
| Jolie | 10301 | CR, BR, GL, GL.RD | 115 mm | 20,5 × 15 × 14 cm |
| Beauté | 20102 | CL, BR, BL.NO | 125 mm | 26 × 16 × 12,5 cm |
| Vide | 10103 | BR, BL.NO | 120 mm | 14,5 × 14,5 × 7,5 cm |
