# Lumière 22005 a partir do CAD (21/10/2026)

Pedido do Thiago: a Lumière é espelho novo e só existem os arquivos técnicos (pasta
`P&D/Desenharia/Lumière.V3` no Drive). Aqui ela é renderizada direto do CAD da V3, sem IA
generativa: a geometria é a do SolidWorks, só triangulada. O que vem de fora do CAD é material,
luz, câmera e parede. Nada foi publicado nem vai ao Shopify antes do veredito.

## Entregas

| Arquivo | O que é |
|---|---|
| `prancha-acabamentos.png` | os 8 quadros lado a lado: 4 acabamentos, LED aceso e apagado |
| `renders/lumiere-<acabamento>-<aceso\|apagado>.png` | os quadros em 1080×1350 (4:5), Lumière fechada, vista 3/4 em parede cinza |
| `conferencia-desenho.png` | vista frontal do A-0001-V3, render ortográfico na mesma escala e as linhas do desenho em vermelho por cima do render |
| `renders/orto-brushed-nickel-*.png` | render ortográfico de frente, 0,25 mm por pixel (base das medidas) |
| `ferramentas/` | scripts para refazer tudo (comandos abaixo) |

## O que foi medido

| Conferência | Resultado |
|---|---|
| Caixa do produto no modelo | 252,6 × 270,3 mm de frente e 72,9 mm de profundidade; o A-0001 dá 252,6 × 270,3 e 73 |
| Linhas do A-0001 sobre o render frontal | 90% dos pixels de linha do desenho têm uma borda do render a até 1 mm |
| Logo a laser (E-0001-V1) | 20,25 × 3,25 mm no render, contra 20 × 2,98 no desenho; topo a 70,4 mm do centro do vidro (desenho 70,66) e centrado (desvio de 0,1 mm). O pixel do render tem 0,25 mm |
| Cor do LED a 4500 K (critério do guia, passo 6, B/R normalizado pela parede) | anel com B/R 0,78; alvo 0,78, faixa da Lumière 0,63 a 0,93 |
| Cor dos acabamentos (CIELAB da cor do metal contra as referências Deca de 21/10) | gold h 88 C 38 (Deca 88/39); red gold h 67 C 33 (67/33); brushed nickel h 90 C 5,8 (90/6,1) |
| Black matte | placa da parede com L 25 no render, contra L 18 na bica Deca (pixels não saturados) |
| Anel apagado | L 35 a 50 em volta do anel, contra L 45 a 51 no Flex Lux desligado do catálogo |

## Como foi feito

- **Modelo:** `step_para_glb.py` nos dois STEP da montagem (fechado e esticado). Cada malha leva o
  código da peça; o material vem do código (lista em `render_lumiere.py`).
- **Vidro E-0001:** frente lisa (IOR 1,52), verso prateado só na área espelhada Ø158,75, anel e
  logo a laser sem prata e jateados, como no desenho. Normal exata da esfera (R600 na frente,
  R604 no verso), porque a normal da malha ondula o reflexo.
- **LED:** os LEDs da placa F-0003 emitem em 4500 K e a luz chega ao anel jateado pelo berço
  branco E-0002, como no produto. Apagado, o anel mostra o berço branco por trás do jateado. O
  render não calcula a luz que atravessa o vidro (cáusticas), então 30% da luz das softboxes passa
  pelo vidro até o berço; sem isso o anel apagado saía preto.
- **Estúdio:** parede cinza com um foco suave que só ilumina a parede (o degradê das stills); softbox principal,
  preenchimento e um cartão grande na frente iluminam só o produto. O espelho reflete uma cúpula
  cinza neutra, para o anel e o logo lerem como nas stills. No black matte as luzes do produto
  ficam a 25%: com a luz cheia o preto fosco lia cinza médio (L 47).
- **Acabamentos:** metal com a cor de reflexão calibrada nas referências Deca; brushed nickel com
  escovado anisotrópico na direção de cada peça (circular no aro e na tampa, ao longo dos tubos,
  vertical na placa). Black matte é pintura (dielétrico), não metal.
- Tempo: cerca de 2,5 minutos por quadro na CPU desta sessão, sem custo de API.

## O que preciso do Thiago

1. **Veredito dos 8 quadros**, do jeito de sempre: publicaria tudo ou as exceções.
2. **Largura do anel.** Na V3 o aro E-0004 cobre o vidro até Ø179, então o anel aceso visível vai
   de Ø158,75 a Ø179. No protótipo NK.BU das fotos o anel é mais largo (espelho/anel 0,81, contra
   0,887 na V3). O render segue a V3. Se a peça de venda for outra, muda o anel.
3. **Buchas de nylon.** As arruelas de nylon das articulações (E-0006, E-0011, E-0058, E-0061,
   E-0062, E-0064) aparecem como linhas brancas finas nas juntas, em todos os acabamentos. No black
   matte elas destoam: são brancas no produto real ou pretas?
4. **Curvatura (aberta desde 15/10).** O desenho diz R600 (foco de 30 cm); o marketing diz foco
   de 60 cm. Na still com reflexo neutro isso não aparece, mas num vídeo com rosto refletido
   aparece.

## Próximos passos possíveis

- LED acendendo e troca 4500 K → 6000 K: câmera parada, dois renders e a mistura (exato).
- Braço abrindo, com as duas poses do CAD (fechado e esticado).
- Ambientadas: o mesmo modelo numa parede de banheiro.

## Como refazer

```
python -m venv venv && venv/bin/pip install bpy==5.2.2 cadquery-ocp numpy pillow
venv/bin/python -I ferramentas/step_para_glb.py "A-0001-V3 Fechado.STEP" modelo/lumiere-Fechado.glb
venv/bin/python -I ferramentas/render_lumiere.py modelo/lumiere-Fechado.glb saida.png \
    --acabamento gold --led 1            # --led 0 apaga; --orto --res 1200x1200 para a vista de medida
venv/bin/python -I ferramentas/prancha_acabamentos.py renders prancha-acabamentos.png
venv/bin/python -I ferramentas/casar_desenho.py A-0001-V3-1.png renders/orto-brushed-nickel-aceso.png conferencia-desenho.png
venv/bin/python -I ferramentas/medir_anel.py renders/orto-brushed-nickel-aceso.png
venv/bin/python -I ferramentas/medir_logo.py renders/orto-brushed-nickel-aceso.png
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
