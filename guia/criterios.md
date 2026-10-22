# Critérios de aprovação

- **VETO:** reprova sozinho. A candidata vai para `_descartados/` e outra é
  gerada. Defeito de estrutura nunca se conserta por edição.
- **CORRIGIR SE DER:** não reprova. O defeito é anotado e corrigido por
  retoque local (ver abaixo), ou se escolhe outra opção equivalente do lote.
- **LIBERDADE CRIATIVA:** escolha do fotógrafo.

"(padrão — confirmar com o Thiago)" marca a classe que o Thiago ainda não
confirmou. A classe de um item só muda com a palavra dele.

## Tabela

| Item | Classe |
|---|---|
| a. Forma do produto inteiro: as mesmas peças da referência, na mesma quantidade; nada inventado, faltando, entortado ou "melhorado"; cabeça circular (elipse coerente com o ângulo) | VETO (Thiago, respostas 5 e 6) |
| b. Acabamento igual ao da referência; cromado lê prata, nunca dourado. Na recoloração em brushed nickel, o metal lê escovado: `ferramentas/medir_escovado.py`, na escala da still de catálogo, dá riscado ≥ 1,2% e borda do reflexo ≥ 3,8 px (`placar.md` › Calibragem, 2026-10-22, brushed nickel: a versão vetada deu 0,8 a 1,1% e 3,0 a 3,6 px; a aprovada, 1,4 a 1,6% e 3,9 a 4,2 px; o gold polido, 0,4% e 2,4 px). No red gold, o tom é o da peça real: `ferramentas/medir_acabamento.py tom`, em cada faixa de L*, dá matiz a até 3° e croma entre 0,75 e 1,3 vez os da foto em `referencias/red-gold/` (69,2/71,6/72,9/74,2° e 12,4/18,0/23,3/27,1; o comando está na docstring) (`placar.md` › Calibragem, 2026-10-22, red gold: o tom Deca vetado deu 58,8 a 70,6° e 1,36 a 2,36 vezes o croma; o aprovado, 68,9 a 74,0° e 0,88 a 1,16 vez). No black matte, a carcaça é pintada de preto: `ferramentas/medir_acabamento.py carcaca <ligada> <desligada>` dá no máximo 0,5% do produto fora da cabeça acima de 180 (`placar.md` › Calibragem, 2026-10-22, black matte: com a carcaça branca, 1,1 a 13,8%; pintada, 0 a 0,05%; Flex e Mobile Lux, sem carcaça branca, 0,07 a 0,10%) | VETO (padrão — confirmar com o Thiago); as medidas do brushed nickel, do red gold e do black matte: VETO (Thiago) |
| c. LED no mesmo estado (aceso ou apagado) e na mesma cor da referência. Nas stills dos LUX, a luz acesa segue o padrão "meio termo" nos 3 tons (`guia/produto.md` › Padrão de luz; `placar.md` › Calibragem, 2026-10-22, lote do logo a laser) | VETO (padrão — confirmar com o Thiago) |
| d. Cabo onde a vista real o mostra e ausente onde ela o esconde (`guia/produto.md` › Cabo e plug). De frente ou de 3/4, produto de mesa sem cabo não reprova (10202CR-4); com o LED aceso, ver d2. Modelo sem cabo à vista (sem LED, Lumière) com cabo também cai aqui | VETO (padrão — confirmar com o Thiago) |
| d2. LED aceso e cabo fora de vista no produto de mesa: o cabo faz falta (`placar.md` › Calibragem, 2026-10-11, `1x1-piloto/A1` e `A4`). Acrescente no retoque o cabo real em cada trecho que a vista mostra: na bancada, saindo de trás da base, e, de 3/4 com vão entre a cabeça e o pivô, a alça da traseira da cabeça até o topo do pivô (`placar.md` › Calibragem, 2026-10-12) | CORRIGIR SE DER (Thiago) |
| e. Cabo na rota real do modelo: branco (preto no black matte), fino, sem conector inventado, com folga compatível com 1,5 m. Nos modelos de parede, o cabo aparece em todo vão entre a cabeça e uma peça que fica na frente dele (a alça do garfo do Mobile Lux), até sumir atrás da cabeça; cabo que termina na alça reprova (`placar.md` › Calibragem, 2026-10-22, 10455CR). Defeito pequeno no trecho da bancada, longe do produto (uma marca escura de braçadeira na volta), não reprova: o Thiago publicaria assim a 10202CR gardie-4 (`placar.md` › Calibragem, 2026-10-16, CR4) | VETO (padrão — confirmar com o Thiago); defeito pequeno longe do produto: CORRIGIR SE DER (Thiago) |
| f. Plug, quando aparece, fiel ao NBR 14136 da referência; mostrar o fio ligado na tomada não é exigido | VETO (Thiago) |
| f2. Plug solto na bancada com o LED aceso (contradição física) | VETO (padrão — confirmar com o Thiago) |
| g. Logo com a grafia errada, ou ausente (o Thiago publicaria a 10202CR-4 com "geroie") | CORRIGIR SE DER (padrão — confirmar com o Thiago) |
| g2. Logo fora da posição da capa (no aro, no vidro). Nos LUX, o logo é gravado a laser no espelho, embaixo e centrado (`guia/produto.md` › Logo); logo impresso na borda jateada, ou logo no difusor ou no aro, reprova. Na still, `ferramentas/verificar_logo.py` confere que o impresso sumiu: o detalhe fino na caixa dele (`impresso_depois`) fica em no máximo 60 (`placar.md` › Calibragem, 2026-10-22, logo a laser: 328 a 648 com o impresso, 10 a 40 sem ele) | VETO, como a (padrão — confirmar com o Thiago); o logo a laser nos LUX: VETO (Thiago) |
| h. Física do reflexo (`guia/cena.md`) | CORRIGIR SE DER (Thiago) |
| h2. Luz de colagem: o cromado repete o reflexo da capa em vez de refletir a cena, e o produto parece recortado do estúdio e colado no ambiente. Medida no passo 5: NCC do detalhe ≥ 0,32 (`placar.md` › Calibragem, 2026-10-11, `1x1-piloto/B5` e `B7`) | VETO (Thiago) |
| i. Escala e proporções: fiel em TODAS as proporções do produto e no tamanho dele no ambiente | VETO (Thiago) |
| j. Ambiente (`guia/cena.md`) | CORRIGIR SE DER, com liberdade criativa (Thiago) |
| k. Montagem e uso reais (`guia/cena.md` › Lugar) | VETO (padrão — confirmar com o Thiago) |
| l. O produto aparece uma vez só; nenhuma cópia dele nem espelho de aumento parecido na cena | VETO (padrão — confirmar com o Thiago) |
| m. Outro espelho comum no ambiente (por exemplo, o espelho de parede do banheiro) | CORRIGIR SE DER (padrão — confirmar com o Thiago) |
| n. Pessoa ou rosto sem pedido; marca de terceiros legível | VETO (padrão — confirmar com o Thiago) |

Liberdade criativa: cômodo, materiais, paleta, objetos de cena, hora do dia,
lente, ângulo e enquadramento, desde que a, b, c, i e k continuem intactos.

## Checklist por candidata

**Antes do lote:** meça na capa as razões do passo 4 e a cor do LED do
passo 6. O que o modelo ainda não tem em `guia/produto.md` › Medidas, registre
lá. No primeiro lote de um modelo, rode os passos 4 e 6 também nas fotos reais
dele (`referencias/<modelo>/`, frames de vídeo): toda faixa tem de aprovar as
fotos reais. Se uma foto real reprova, a faixa está errada.

**Em cada candidata**, nesta ordem, parando no primeiro veto:

1. **Comparação lado a lado:** capa e candidata, com o produto na mesma
   escala.
2. **Recortes** em `_crops/`, em resolução nativa, das regiões: cabeça (aro,
   difusor, vidro, logo), junções (garfo, pinos, pivô), base, cabo e pontos
   de saída, plug e tomada. Leia cada recorte com Read, porque a imagem
   inteira reduzida esconde alucinação.
   - `python3 ferramentas/inspecao_imagem.py crops <img> _crops/` gera os
     quadrantes.
   - Para medir, gere a grade fina de cada região:
     `python3 ferramentas/inspecao_imagem.py grade <img> _crops/<rótulo>-<região>.png 10 2 x0,y0,x1,y1`
     (passo de 10 px, zoom 2×, rótulos em px da imagem original). Leia as
     bordas com ±2 px. Faça o mesmo na capa.
3. **Forma (a, g2, k, l):** conte as peças contra a capa, uma a uma. Procure
   peça inventada principalmente onde a capa não mostra: traseira, lado
   oposto, interior do garfo.
4. **Proporções (i):** meça TODAS as razões entre peças visíveis; a tabela é
   o mínimo. Compare cada razão com a da referência de ângulo mais parecido
   (a capa ou uma foto real do modelo), nunca no olho. Fora da faixa: VETO.
   As faixas são ponto de partida (padrão — confirmar com o Thiago) e a
   calibragem as ajusta.

   | Razão (valores em `guia/produto.md`) | Faixa |
   |---|---|
   | Ø vidro, largura do difusor, largura do aro e largura da fita do garfo, cada uma ÷ Ø da cabeça | ±10% |
   | pinos: na linha do centro da cabeça | altura dos pinos ÷ altura da cabeça = 0,50 ± 0,05 |
   | disco ÷ cabeça (eixo maior); espessura do disco ÷ disco | ±10% |
   | topo do sino (ou da coluna) ÷ disco | ±15% |
   | pivô → topo do disco ÷ disco (Classique Lux) | em qualquer altura de câmera, VETO acima de 0,47; abaixo de 0,31, só com câmera alta. Obrigatória na `mesa-close-base`, onde confere também que o sino abre logo abaixo do pivô, sem coluna |
   | altura: topo da cabeça → centro do pé ÷ disco (Classique Lux, câmera baixa, até ~15°) | VETO acima de 1,82, 8% acima da capa r1 (1,68). Pega a cabeça grande somada ao garfo alto, que o disco ÷ cabeça sozinho deixa passar (`placar.md` › Calibragem, 2026-10-16, CR1 a CR3) |
   | parede: braço ou suporte ÷ cabeça, placa ÷ cabeça | ±10%, depois de medidos na capa do primeiro lote |

   **Altura:** o topo é o ponto mais alto da borda da cabeça; o centro do pé
   é o y0 da meia-elipse ajustada à borda de baixo do anel preto,
   y = y0 + b·√(1 − ((x − xc)/a)²), com a = metade do disco. Publicaria: A1
   1,77, CR4 1,79 e A4 1,80. Não publicaria: CR1 1,85, CR3 1,87 e CR2 1,88
   (e A3 1,88 e A5 1,96, já vetadas pelo disco ÷ cabeça).

   **Escala no ambiente:** meça em px uma dimensão total do produto
   (`guia/produto.md` › Medidas) e um objeto de tamanho conhecido no MESMO
   plano (sobre a mesma bancada, à mesma distância da câmera): frasco de
   perfume de 10 a 15 cm, torneira, toalha de rosto dobrada, gaveta. Compare
   com a razão em cm. Nos closes, a escala é conferida pelas proporções.
5. **Acabamento e luz (b, h2):** os realces do cromado são neutros, sem
   puxar para amarelo ou dourado. Compare com a capa no mesmo tipo de recorte.
   Nas recolorações, meça o item b: brushed nickel com `medir_escovado.py`,
   red gold com `medir_acabamento.py tom` e black matte com
   `medir_acabamento.py carcaca`.
   Depois meça se o cromado repete o reflexo da capa:
   `python3 ferramentas/inspecao_imagem.py colagem <capa> <caixa na capa> <img> <janela> <escala> _crops/<rótulo>-colagem.png`.
   - Caixa na capa: um trecho cromado de reflexo marcante. Na capa r1 do
     Classique Lux cromado, o miolo do sino, `700,1110,870,1320`.
   - Janela: o mesmo trecho na candidata, com folga, lido na grade.
   - Escala: Ø da base na candidata ÷ Ø da base na capa (802 px na r1).
   - A ferramenta compara o detalhe (passa-alta), não a mancha escura que
     todo sino reflete: sem o filtro, sinos refeitos com a luz da cena deram
     até 0,82 e se confundiam com as cópias.
   - NCC ≥ 0,32: VETO h2. No piloto de 2026-10-11, as cópias da capa deram
     0,40 a 0,84 (B5 0,83 e B7 0,84) e as que refletiam a cena, 0,20 a 0,25
     (A1 0,20 e A4 0,21) (padrão — calibrar).
6. **LED (c):** mesmo estado da capa. Para a cor, meça o B/R mediano só em
   pixels não saturados (canal máximo entre 60 e 244): no anel ou, se ele
   estourar, numa faixa de ~3% do Ø logo por dentro dele (o halo no vidro),
   em 4 amostras (12, 3, 6 e 9 h). Divida pelo B/R de um branco neutro da
   mesma cena (toalha, parede). Por esse método, as fotos reais dão ≈0,78 em
   4500K e ≈1,07 em 6000K. VETO se a candidata se afastar mais de 0,15 da
   capa, metade dessa distância (padrão — calibrar).
7. **Cabo e plug (d, d2, e, f):** confira a vista contra `guia/produto.md` ›
   Cabo e plug, que cita as fotos reais de cada vista. Plug visível: compare a
   forma com `referencias/chicote-eletrico/`. LED aceso sem cabo à vista, na
   bancada ou na alça do vão entre a cabeça e o pivô: anote d2. De 3/4, o
   cabo da bancada sai de trás da base do mesmo lado do pivô em que aparece a
   alça (`placar.md` › Calibragem, 2026-10-19). Na parede, com uma peça na
   frente do cabo (alça do garfo do Mobile Lux): conte, no vão entre essa peça
   e a cabeça, as linhas que caem no corredor da rota do cabo; todas têm de
   mostrar cabo. Na 10455CR de 16/10, vetada, deu 0 de 82 linhas; na
   corrigida, 82 de 82 (`placar.md` › Calibragem, 2026-10-22).
8. **Notas (g, h, j, m):** logo, reflexo, ambiente e outros espelhos.
9. **Registro:** vetada vai para `_descartados/` com o item da tabela e a
   medida que reprovou; aprovada vira candidata ao lote, com as notas.

## Aprovação do lote

- **Uso final:** para cada receita e formato, escolha 1 ou 2 entre as que
  passaram. No empate, prefira a que tem menos notas de "corrigir se der" e,
  depois, o ambiente mais próximo do benchmark.
- **Prancha de entrega:** as escolhidas e mais 3 ou 4 reprovadas, com o
  motivo de cada uma. Na rodada de comparação de motores, ela leva TODAS as
  que passaram, cegas, mais as 3 ou 4 reprovadas: o "publicaria" do Thiago
  por rótulo é o que alimenta a coluna Publicaria do `placar.md`.
- **Receita sem nenhuma aprovada:** gere mais (`guia/prompts.md`). Se ainda
  não fechar, entregue o lote sem ela e explique o motivo.

## Retoque (corrigir se der)

- **Foto em uso que volta para retoque** é candidata como as outras: passa
  pelo checklist inteiro antes da prancha, não só pelo item retocado. As
  10202CR gardie-1 a -3 ganharam a alça sem a medida de proporção, e o Thiago
  não as publicaria (`placar.md` › Calibragem, 2026-10-16, CR1 a CR3).
- **Só defeito local:** logo com grafia errada (corrija a grafia; remover o
  logo só depois de o Thiago confirmar que logo ausente é aceito), texto
  fantasma, objeto pequeno espúrio, um trecho do reflexo. Defeito de forma,
  proporção, escala, acabamento ou LED: regenerar.
- **Ferramenta:** `ferramentas/estudio_fal.py fundo` (FLUX Fill), só com a
  máscara do defeito; os pixels fora da máscara não mudam. `mascara-fundo`
  (máscara do fundo inteiro) e `relight` (reilumina a imagem inteira) não
  fazem parte do processo.
  - Antes da API, valide a máscara com uma sobreposição vermelha (abrindo com
    Read).
  - O prompt descreve, em positivo e literalmente, o único conteúdo permitido
    na máscara. Negativos não funcionam.
  - O Fill recusa objeto fino em máscara pequena e, em área aberta, costuma
    inventar outro objeto no lugar.
- **Reflexo (h):** `ferramentas/curva_vidro.py` curva o reflexo existente,
  sem IA, só dentro do círculo do vidro.
- **Cabo (d2):** `ferramentas/cabo_real.py` desenha o cabo sem IA e não toca
  no produto. Na bancada, use `"deitado": true`: cilindro branco de borda
  definida, com sombra de contato. O perfil antigo, medido no cabo da A1 de
  2026-10-11, lia mole sobre mármore claro (`placar.md` › Calibragem,
  2026-10-19).
  - Rota de `guia/produto.md` › Cabo e plug: o 1º ponto fica escondido atrás
    da base, na direção da saída, e o cabo corre rente à bancada até a borda
    do quadro, com folga (curva leve, nunca reta esticada).
  - Lado: de 3/4, a saída na bancada fica do mesmo lado do pivô que a alça;
    na vista espelhada, os dois trocam de lado juntos (`placar.md` ›
    Calibragem, 2026-10-19). Fique no tampo: nem a borda de cima do cabo
    encosta na linha da parede.
  - Nitidez: a borda do cabo (sigma do degrau ajustado ao perfil) não fica
    mais mole que as bordas da foto junto da base. No teste do Runway, o cabo
    deitado deu 0,4 a 0,9 px, contra 0,7 a 1,1 px nas bordas da base.
  - Alça no vão entre a cabeça e o pivô: rota com `"suspenso": true`, do 1º
    ponto escondido atrás da borda de baixo da cabeça ao último escondido no
    topo do pivô, descendo em curva como na marcação do Thiago na
    `1x1-piloto/A1` (`placar.md` › Calibragem, 2026-10-12). Se o recorte do
    produto engolir o vão (o BiRefNet preenche furos), passe em `visivel` a
    máscara do vão e confira que os pixels "do produto" alterados são só fundo
    (cor da parede, sem cromado).
  - Cabo pendurado na parede, com peça na frente (alça do garfo do Mobile
    Lux): rota `"suspenso": true` cujo 1º ponto fica escondido atrás da
    cabeça, acima da alça, e máscara `visivel` com o vão entre a alça e a
    cabeça aberto (do alfa do produto), para o cabo aparecer nele. Começar a
    rota na alça foi o erro da 10455CR de 16/10 (`placar.md` › Calibragem,
    2026-10-22).
  - Largura: 5 mm na escala do Ø da base junto dela, diminuindo para o fundo.
  - Confira em 8× a saída de trás da base (sem ponta solta nem vão), a saída
    da alça sob a borda da cabeça e a entrada dela no pivô e, em 1×, se o cabo
    se lê como cabo.
  - Em 2026-10-11, o FLUX Fill numa faixa da rota acertou 1 de 16 tentativas
    (a A1, e com a ponta solta a 10 px da base), e o Kontext em edição pôs
    plug solto (f2) e mexeu no enquadramento.
- **Editor de imagem inteira** (Kontext, Seedream ou Gemini em edição):
  recodifica o produto, então a candidata volta ao checklist desde o começo.
- **Depois de toda edição:** rode
  `ferramentas/inspecao_imagem.py diff base nova [máscara]`. Se menos de 2%
  dos pixels mudaram, a edição falhou: não apresente a imagem como corrigida.
