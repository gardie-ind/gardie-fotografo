# Lumière 22005 a partir do CAD (21/10/2026)

Pedido do Thiago: a Lumière é espelho novo e só existem os arquivos técnicos (pasta
`P&D/Desenharia/Lumière.V3` no Drive). Aqui ela é renderizada direto do CAD da V3, sem IA
generativa: a geometria é a do SolidWorks, só triangulada. O que vem de fora do CAD é material,
luz, câmera e parede. Nada foi publicado nem vai ao Shopify antes do veredito.

## Entregas

Mais recente (27/10): **v7, traseira** (`v7-traseira/`). Pedido do Thiago: "Consegue fazer algumas
posições mostrando a traseira do espelho?" Seis quadros em cromado, LED aceso em 4500K, com o
realismo do v5. A cabeça gira no pino vertical da articulação até 90° em relação ao braço da
cabeça, que é o giro que o próprio CAD mostra entre fechado e esticado, e a câmera fica do lado
da tampa traseira.

| Arquivo (em `v7-traseira/`) | O que é |
|---|---|
| `prancha-traseira.png` | os seis quadros, com o braço, o giro da cabeça e a câmera de cada um |
| `t01.png` … `t06.png` | os quadros finais, 1080×1350 (4:5) |
| `cru/` | aceso e apagado crus e a silhueta de cada vista |
| `medidas.json` | estouro, folga até a borda, pose e giro da cabeça, por vista |

| Vista | Braço (placa / cabeça) | Cabeça | Câmera |
|---|---|---|---|
| t01 | esticado (0° / 360°) | virada 90° à esquerda | 55° à direita, 8° acima |
| t02 | esticado | virada 90° à esquerda | 35° à direita, 12° acima |
| t03 | 20° / dobrado para trás (270°) | virada 90° à direita | 55° à esquerda, 8° acima |
| t04 | 30° / dobrado para trás | virada 90° à direita | 40° à esquerda, 15° acima |
| t05 | esticado | virada 90° à esquerda | 50° à direita, 22° acima |
| t06 | 15° / 345° | virada 75° à esquerda | 50° à direita, 5° abaixo |

Anterior (26/10, aguardando veredito): **v6, braço meio aberto** (`v6-meio-aberto/`). Pedido do Thiago (25/10 23:17):
"Crie mais dez perfis diferentes, de braço meio aberto e angulos de câmera diferentes. Faça com um
acabamento e uma luz só, para aprovação." Dez quadros em cromado, LED aceso em 4500K, com o
realismo do v5. O braço é articulado a partir do CAD fechado (ver "Como foi feito" › Braço meio
aberto); a cabeça fica de frente para fora da parede.

| Arquivo (em `v6-meio-aberto/`) | O que é |
|---|---|
| `prancha-meio-aberto.png` | os dez quadros, com o braço e a câmera de cada um |
| `p01.png` … `p10.png` | os quadros finais, 1080×1350 (4:5) |
| `cru/` | aceso e apagado crus de cada vista e a silhueta (entrada do padrão de luz e das medidas) |
| `medidas.json` | estouro, folga até a borda e a pose medida, por vista |

| Vista | Braço (placa / cabeça) | Câmera |
|---|---|---|
| p01 | 45° / dobrado para trás (270°) | 40° à esquerda, 8° acima |
| p02 | 60° / dobrado para trás | 35° à direita, 10° acima |
| p03 | 30° / dobrado para trás | 60° à esquerda, 5° acima |
| p04 | 30° / 330° | 50° à direita, 8° acima |
| p05 | 45° / 315° | 50° à esquerda, 15° acima |
| p06 | 60° / reto para fora (360°) | 25° à direita, 4° acima |
| p07 | 60° / 300° | 25° à esquerda, 6° abaixo |
| p08 | 45° / dobrado para trás | 60° à direita, 12° acima |
| p09 | 20° / dobrado para trás | 35° à esquerda, 22° acima |
| p10 | 15° / 300° | 55° à esquerda, 4° acima |

Ângulo do braço: direção de cada braço medida a partir da perpendicular à parede (0° = saindo
reto da parede). O CAD fechado é 90° / 270° (braço da placa deitado na parede, braço da cabeça
dobrado de volta) e o esticado é 0° / 360°. Esquerda e direita são de quem olha a parede de frente.

Anterior (25/10, aguardando veredito): **v5, foto** (`v5-foto/`). O Thiago aprovou a direção do v4 ("Você acertou,
parabéns!") e pediu: "Agora remova o aspecto de render e faça mais realista." Os mesmos 60 quadros
do v4 (frente do protótipo, 5 acabamentos, 3 ângulos, apagado e 3 tons), com o realismo descrito em
"Como foi feito" › Realismo. As medidas do produto não mudam.

| Arquivo (em `v5-foto/`) | O que é |
|---|---|
| `prancha-frente.png`, `prancha-tres-quartos.png`, `prancha-braco-aberto.png` | uma por ângulo: 5 acabamentos × LED apagado, 3000K, 4500K e 6000K |
| `prancha-render-x-foto.png` | o mesmo quadro no v4 (render) e no v5 (foto), inteiro e num detalhe em tamanho real |
| `<ângulo>/lumiere-<acabamento>-<apagado\|3000\|4500\|6000>.png` | os quadros finais, 1080×1350 (4:5) |
| `<ângulo>/cru/` | aceso e apagado crus do render (entrada do padrão de luz e do acabamento de câmera) |
| `medidas.json` | as medidas, por ângulo e acabamento, nos quadros finais |

A v4 (`v4-anel-uniforme/`, 24/10) segue como referência do render sem o realismo, só na pasta do projeto; no git ficam a v7, a v6, a v5 e `perfil/` (sem os crus).

Histórico: a vista 3/4 de 28° (`renders/`, `prancha-acabamentos.png`) foi vetada em 22/10; a
frontal (`frontal/`) estourava o flash; a `frontal-v2/` segue a frente do desenho V3; a
`frente-prototipo/` (23/10) tinha o anel com sombras internas e foi substituída pela v4.

| Arquivo (em `v4-anel-uniforme/`) | O que é |
|---|---|
| `prancha-frente.png`, `prancha-tres-quartos.png`, `prancha-braco-aberto.png` | uma por ângulo: 5 acabamentos × LED apagado, 3000K, 4500K e 6000K |
| `prancha-anel-antes-agora.png` | recorte da cabeça: anel de 23/10 contra o de 24/10 |
| `<ângulo>/tons/lumiere-<acabamento>-<3000\|4500\|6000>.png` | os quadros acesos finais, 1080×1350 (4:5) |
| `<ângulo>/lumiere-<acabamento>-apagado.png` | o quadro apagado final |
| `<ângulo>/lumiere-<acabamento>-aceso.png` | o aceso cru do render, entrada do padrão de luz (não é entrega) |
| `<ângulo>/silhueta.png` | máscara do produto para as medidas |
| `medidas.json` | as medidas abaixo, por ângulo e acabamento |

Ângulos: **frente** (braço fechado, câmera a 4° e 3° acima), **3/4** (braço fechado, 35° pela
esquerda e 6° acima, com a sombra na parede) e **braço aberto** (pose esticada do CAD, a cabeça a
36 cm da parede, 55° e 8° acima). Os outros quadros de 23/10 continuam em `frente-prototipo/`, `perfil/` e
`conferencia-desenho.png`; `ferramentas/` tem os scripts.

## O que foi medido

| Conferência | Resultado |
|---|---|
| Caixa do produto no modelo | 252,6 × 270,3 mm de frente e 72,9 mm de profundidade; o A-0001 dá 252,6 × 270,3 e 73 |
| Linhas do A-0001 sobre o render frontal | 90% dos pixels de linha do desenho têm uma borda do render a até 1 mm |
| Frente do protótipo (23/10) | prata Ø150,0 e aro de Ø184,5 a Ø204,5 medidos na vista de medida (pixel de 0,25 mm) |
| Logo a laser (E-0001-V1, subido na proporção da prata, 150/158,75) | 20,0 × 3,25 mm, contra 20 × 2,98 no desenho; topo a 66,4 mm do centro (alvo 66,8; na V3 deu 70,4 contra 70,66) e centrado (desvio de 0,05 mm) |
| Cor do LED a 4500 K (critério do guia, passo 6, B/R normalizado pela parede) | anel com B/R 0,76 (frente V3: 0,78); alvo 0,78, faixa da Lumière 0,63 a 0,93 |
| Estouro (canal no teto, dentro da silhueta) | brushed nickel 3,3%, gold e red gold 4,8%, black matte 0%; só brilhos, nenhum pixel com os três canais em 250 |
| Cor dos acabamentos (CIELAB da cor do metal contra as referências Deca de 21/10) | gold h 88 C 38 (Deca 88/39); red gold h 67 C 33 (67/33); brushed nickel h 90 C 5,8 (90/6,1) |
| Black matte | placa da parede com L 25 no render, contra L 18 na bica Deca (pixels não saturados) |
| Anel apagado | L mediano 29 (p90 40) na vista de frente; na frontal-v2 era 23 |
| **v4 (24/10):** uniformidade do anel aceso, de frente ((p95 − p5) / mediana da luminância em 7 raios de 77 a 90 mm, fora do setor do logo) | 2,6 a 3,3% no render aceso e 0,1 a 0,2% no tom 4500K, nos 5 acabamentos; raio de dentro contra o de fora 0,98. Na frente-prototipo de 23/10 a variação ia de 11 a 36% e a borda de fora caía para 0,72 |
| v4: cor do difusor, de frente (mediana do anel, r 80–88 mm) | 3000K 255,245,229 (black matte 228); 4500K 254,252,249; 6000K 240,245,255. O padrão aprovado em 22/10 dá 255,245,232, 255,253,250 e 240,245,255 |
| v4: estouro com o LED apagado (três canais ≥ 250 na silhueta) | 0% em brushed nickel, gold, red gold e black matte; cromado 4,2% de frente, 2,2% no 3/4 e 4,8% no braço aberto (brilhos do cromo) |
| v4: estouro no 4500K fora da área que o LED ilumina | 0% nos quatro; cromado 5,4%, 2,8% e 5,9% (o aro cromado reflete o anel aceso) |
| **v5 (25/10), nos quadros finais:** uniformidade do anel no 4500K, de frente | 2,7 a 3,2% (o grão e a vinheta do acabamento de câmera somam ~3%; o VETO do guia é 8%); raio de dentro contra o de fora 1,00 |
| v5: cor do difusor, de frente | 3000K 254,244,228; 4500K 253,251,248; 6000K 239,244,254 (−1 da vinheta em relação ao v4) |
| v5: estouro com o LED apagado | 0 a 0,06% nos quatro; cromado 2,1 a 2,9% |
| v5: estouro no 4500K fora da área do LED | gold, red gold e black matte 0 a 0,3%; brushed nickel 0,6 a 2,9%; cromado 4,5 a 7,8% (é o vazamento de luz do anel no lábio do aro, de propósito) |
| v5: espelho apagado, de frente (cinza mediano no centro) | 196, contra 198 no v4: o estúdio refletido não escureceu o espelho |
| **v6 (26/10):** pose do braço | o CAD fechado posado em 0° / 360° bate pixel a pixel com o CAD esticado (silhueta de frente e a 55°, 0 pixels diferentes) |
| v6: colisão entre peças (malhas, em cada uma das dez poses) | nenhum par de peças novo se tocando além dos que já se tocam no fechado e no esticado; na p04 a arruela de nylon do cotovelo encosta na ponteira, que é a facetação do furo girando em volta da arruela redonda (as duas são cilindros no mesmo eixo) |
| v6: estouro com o LED apagado (cromado) | 1,7 a 5,3% (v5 cromado: 2,1 a 2,9%; brilhos do cromo, mais nas vistas mais de lado) |
| v6: estouro no 4500K fora da área do LED | 4,0 a 8,5% (v5 cromado: 4,5 a 7,8%) |
| v6: folga do produto até a borda do quadro | 75 a 197 px (nada cortado) |
| **v7 (27/10):** colisão com a cabeça girada (malhas, nas seis poses) | nenhum par de peças novo se tocando (na t06 e na p04 só a facetação da arruela do cotovelo, como no v6) |
| v7: estouro com o LED apagado (cromado) | 2,2 a 6,9% (a t06, de baixo, tem a placa refletindo o rebatedor claro) |
| v7: estouro no 4500K fora da área do LED | 1,1 a 2,5% |
| v7: folga do produto até a borda do quadro | 82 a 158 px |
| v6: articulação do cotovelo na câmera alta (p09, 22° acima; cinza mediano) | 5/255 com o estúdio parado (o cromo refletia o piso escuro e a peça lia preta: vetada antes da entrega); 132/255 com o estúdio subido 16° |

## Como foi feito

- **Modelo:** `step_para_glb.py` nos dois STEP da montagem (fechado e esticado). Cada malha leva o
  código da peça; o material vem do código (lista em `render_lumiere.py`).
- **Vidro E-0001:** frente lisa (IOR 1,52), verso prateado só na área espelhada Ø158,75, anel e
  logo a laser sem prata e jateados, como no desenho. Normal exata da esfera (R600 na frente,
  R604 no verso), porque a normal da malha ondula o reflexo.
- **LED (v4, 24/10):** o vidro jateado (anel e logo) emite por igual, e os LEDs da placa ficam
  apagados (`--anel-emissao 1.0`). Até 23/10 os 24 LEDs da placa F-0003 iluminavam o anel pelo
  berço branco E-0002, o que deixava manchas e sombras internas que o produto real não tem (o
  difusor real espalha a luz). Depois, o par aceso e apagado do mesmo quadro passa pelo padrão de
  anel de luz aprovado em 22/10 (`luz_padrao.py`: brilho +80%, "meio termo", tons 3000K, 4500K e
  6000K), o mesmo usado nas stills LUX.
- **LED (até 23/10):** os LEDs da placa F-0003 emitem em 4500 K e a luz chega ao anel jateado pelo berço
  branco E-0002, como no produto. Apagado, o anel mostra o berço branco por trás do jateado. O
  render não calcula a luz que atravessa o vidro (cáusticas), então 30% da luz das softboxes passa
  pelo vidro até o berço; sem isso o anel apagado saía preto.
- **Estúdio:** parede cinza com um foco suave que só ilumina a parede (o degradê das stills); softbox principal,
  preenchimento e um cartão grande na frente iluminam só o produto. O espelho reflete uma cúpula
  cinza neutra, para o anel e o logo lerem como nas stills. No black matte as luzes do produto
  ficam a 25%: com a luz cheia o preto fosco lia cinza médio (L 47). No cromado (24/10) o metal
  também reflete a cúpula, senão ele espelhava o fundo preto e lia grafite.
- **Realismo (v5, 25/10):** comparado com as stills reais de catálogo (Mobile Lux e Classique Lux
  ligadas) e com a foto do protótipo. No render (`--realismo`): os metais e o espelho refletem um
  estúdio (fundo escuro, teto claro, piso cinza, um rebatedor branco com degradê do lado oposto ao da
  câmera, duas softboxes verticais e frestas escuras finas, que dão as linhas pretas do cromo real);
  as quinas do CAD ficam levemente quebradas (Bevel de 0,3 mm na normal, sem mudar a geometria); a
  rugosidade varia um pouco na superfície; a parede tem textura de pintura, manchas de ±3% e é um
  pouco mais clara (0,13); lente a f/16 (f/22 no braço aberto, para a placa não perder nitidez).
  Depois do padrão de luz, `foto.py`: a luz do anel vaza pelo vidro para dentro do espelho e para o
  lábio do aro (degradê de ~1 cm, na cor do tom, como nas stills reais), brilho de lente fora da
  fonte, vinheta de 9%, franja de cor de 0,4 px no canto, nitidez de câmera e grão com semente fixa
  por ângulo. Nada disso muda forma, medida ou cor do produto.
- **Braço meio aberto (v6, 26/10):** o CAD vem em duas poses, fechada e esticada. Comparando
  as duas peça a peça: as articulações têm eixo vertical; o braço da placa (D-0003, mancal D-0005
  e a ponteira D-0004 do cotovelo) gira em volta do pino da placa; o braço da cabeça (D-0006 e as
  duas ponteiras) gira em volta do cotovelo; arruelas, buchas e pinos das articulações só se
  deslocam (são redondos: raio igual em todas as direções, medido); a cabeça não gira entre as
  duas poses. `render_lumiere.py --braco t1,t2` leva o CAD fechado para qualquer pose entre as
  duas com esses mesmos movimentos, antes de qualquer outro passo, e só usa poses no caminho entre
  fechado e esticado (as juntas não passam do que o próprio CAD mostra). Comprimentos medidos:
  202,6 mm da placa ao cotovelo e 86,3 mm do cotovelo à cabeça. Nas câmeras do lado direito o
  estúdio vai espelhado junto (sem isso a chave ficava atrás do produto e o espelho refletia o
  lado escuro); o foco da parede fica atrás do produto como a câmera o vê (`--halo-camera`); na
  câmera alta o estúdio refletido sobe junto (`--estudio-inclina`). f/22 em todas.
- **Traseira (v7, 27/10):** `--cabeca` gira a cabeça (vidro, berço, aro, tampa, placa de LED e a
  haste até o pino) no pino vertical da articulação. O giro entra depois do recorte da prata, do
  logo e do aro, que supõem a cabeça de frente, e antes das normais da esfera e do escovado, que
  são calculados com a cabeça já girada. Só giros de 0 a 90° em relação ao braço da cabeça, os
  que o CAD mostra. A tampa traseira em cromado é polida, como no protótipo; o círculo mais claro
  em volta da haste é o assento plano da tampa no CAD (Ø~60 mm plano, depois a tampa abaula até
  o aro; medido na malha do E-0003), e as curvas escuras ao lado da haste são o reflexo da haste
  na tampa abaulada (a malha não tem nenhuma feição ali). Câmeras a 70° ou mais de lado ficaram de fora (a parede longe
  do foco ficava preta).
- **Acabamentos:** metal com a cor de reflexão calibrada nas referências Deca; brushed nickel com
  escovado anisotrópico na direção de cada peça (circular no aro e na tampa, ao longo dos tubos,
  vertical na placa). Black matte é pintura (dielétrico), não metal.
- Tempo: cerca de 2,5 minutos por quadro na CPU desta sessão, sem custo de API.

## O que preciso do Thiago

0. **Veredito da v7** (traseira) e **da v6** (braço meio aberto): publicaria tudo ou as exceções, citando a vista
   (ex.: `p04`). Se gostar de uma pose e câmera, ela pode ser feita nos outros acabamentos e tons.
1. **Veredito da v5**, do jeito de sempre: publicaria tudo ou as exceções, citando
   `<ângulo>/<acabamento>-<tom>` (ex.: `braco-aberto/gold-3000`). São 60 quadros: 3 ângulos ×
   5 acabamentos × (apagado + 3 tons). Se ainda parecer render, apontar onde (metal, espelho,
   anel, parede, luz).
2. **Tampa de trás.** No protótipo ela é polida (reflete o teto); no brushed nickel do render está
   escovada. Aparece um pouco no 3/4 e no braço aberto.
3. **Buchas de nylon.** As arruelas de nylon das articulações aparecem como linhas brancas finas
   nas juntas, em todos os acabamentos. No black matte elas são brancas ou pretas?
4. **Curvatura (aberta desde 15/10).** O desenho diz R600 (foco de 30 cm); o marketing diz foco
   de 60 cm. Só aparece num vídeo com rosto refletido.

## Próximos passos possíveis

- LED acendendo e troca de tom: câmera parada, os quadros já existem (exato).
- Braço abrindo em vídeo: com a articulação do v6 dá para gerar a sequência entre fechado e
  esticado, quadro a quadro, sem IA.
- Ambientadas: o mesmo modelo numa parede de banheiro.

## Como refazer

```
python -m venv venv && venv/bin/pip install bpy==5.2.2 cadquery-ocp numpy pillow
venv/bin/python -I ferramentas/step_para_glb.py "A-0001-V3 Fechado.STEP" modelo/lumiere-Fechado.glb
venv/bin/python -I ferramentas/render_lumiere.py modelo/lumiere-Fechado.glb saida.png \
    --acabamento gold --led 1 --prata-diam 150 --aro-largura 10   # frente do protótipo (decisão de 23/10)
    # --led 0 apaga; --orto --res 1200x1200 para a vista de medida; sem --prata-diam segue o desenho V3
venv/bin/python -I ferramentas/prancha_acabamentos.py renders prancha-acabamentos.png
bash ferramentas/lote_v4.sh            # v4: 3 ângulos × 5 acabamentos × aceso/apagado + 3 tons (~1h35 em 4 CPUs)
bash ferramentas/lote_v5.sh            # v5: o mesmo com --realismo e foto.py (~2h20; VISTAS=... para rodar em partes)
bash ferramentas/lote_v7.sh            # v7: 6 vistas da traseira, cromado 4500K (~35 min)
venv/bin/python -I ferramentas/medir_v6.py renders/v7 renders/v7/medidas.json
venv/bin/python -I ferramentas/prancha_v6.py renders/v7 renders/v7/prancha-traseira.png traseira
bash ferramentas/lote_v6.sh            # v6: 10 vistas de braço meio aberto, cromado 4500K (~1h35; VISTAS="p01 p02" para partes)
venv/bin/python -I ferramentas/medir_v6.py renders/v6 renders/v6/medidas.json
venv/bin/python -I ferramentas/prancha_v6.py renders/v6 renders/v6/prancha-meio-aberto.png
venv/bin/python -I ferramentas/medir_v4.py renders/v5 renders/v5/medidas.json final
venv/bin/python -I ferramentas/prancha_v4.py renders/v5 renders/v5/pranchas final renders/v4
venv/bin/python -I ferramentas/medir_v4.py renders/v4 renders/v4/medidas.json
venv/bin/python -I ferramentas/prancha_v4.py renders/v4 renders/v4/pranchas
venv/bin/python -I ferramentas/casar_desenho.py A-0001-V3-1.png renders/orto-brushed-nickel-aceso.png conferencia-desenho.png
venv/bin/python -I ferramentas/medir_anel.py renders/orto-brushed-nickel-aceso.png
venv/bin/python -I ferramentas/medir_logo.py frente-prototipo/orto-prototipo-aceso.png 503.8 468.4 0.25 150
```

`A-0001-V3-1.png` é a página 1 do PDF do A-0001-V3 a 110 dpi. O CAD fica fora do git e de
qualquer serviço público de render: está no Drive (`P&D/Desenharia/Lumière.V3`).

## Protótipo × CAD (vídeo do Thiago, 23/10)

Pasta `perfil/`. O Thiago mandou um vídeo de dois protótipos NK.BU sobre a mesa (um de frente,
um de costas), pedindo para ignorar o touch no espelho. `prancha-prototipo-x-cad.png` põe lado a
lado a foto de frente do protótipo, o render atual e o render com a frente do protótipo, na mesma
escala da cabeça, e o verso do vídeo contra o CAD visto de trás com a mesma inclinação (~27°).

| Conferência | Protótipo | CAD V3 |
|---|---|---|
| Centro da cabeça até o eixo da placa (vídeo, braço fechado) | 116,6 mm | 116,35 mm |
| Furos dos parafusos da placa (unidade solta, sem tampas) | ±42 mm do braço | ±42,6 mm (tampas E-0013) |
| Aro visto de frente (foto, elipse ajustada, aro Ø204,5) | ~10 mm | 12,8 mm |
| Anel jateado | ~17 mm | 10,1 mm |
| Área espelhada | ~Ø150 (vídeo: Ø148,5) | Ø158,75 |
| Tampa de trás | polida (reflete o teto) | escovada no render brushed nickel |

Braço, placa, articulações e verso batem com o CAD. A frente não: o anel e a prata são do vidro
(a mesma peça do touch) e o aro é o E-0004. Opções novas do `render_lumiere.py`, que por padrão
seguem os desenhos: `--prata-diam 150 --aro-largura 10` (frente do protótipo), `--verso`
(vista de trás, sem parede) e `--esconder` (peças por código).

```
venv/bin/python -I ferramentas/render_lumiere.py modelo/lumiere-Fechado.glb perfil/frente.png --prata-diam 150 --aro-largura 10
venv/bin/python -I ferramentas/render_lumiere.py modelo/lumiere-Fechado.glb perfil/verso.png --led 0 --verso \
    --azimute 180 --elevacao -27 --res 1080x1080 --esconder D-0003,D-0005,E-0010,E-0012,E-0013,E-0014,E-0009,E-0058,F-0008,cross,socket,flat
venv/bin/python -I ferramentas/prancha_perfil.py perfil/prancha-prototipo-x-cad.png perfil/video-6s.jpg
```
