# Verificação · Classique Lux cromado (10202CR), LED ligado · rodada `1x1-ambientes` · 2026-10-12

Ambientes novos para o mesmo espelho, depois de "A1 ficou perfeito! … Consegue
fazer ambientes diferentes?" (2026-10-12). Mesma capa
(`referencias/capa/classique-lux-cromado-ligado-capa-r1.png`) e mesma moldura
do piloto, em três receitas: `mesa-banheiro-banheira` (A),
`mesa-penteadeira-quarto` (B) e `mesa-papel-de-parede` (C).

## O que preciso de você

1. **Veredito nas duas pranchas** (banheira e penteadeira): quais você
   publicaria. Nas vetadas, marque as que publicaria: A3, A4 e B8 estão no
   limite da faixa de proporção, e a A1 no limite da colagem. **Revisão de
   2026-10-16:** pela medida nova de altura, só a A2 passa; A5 e B7 vetam no
   limite e B4 veta (ver Revisão de 2026-10-16).
2. **A4 do piloto:** salvo também em `aprovadas/`?
3. **Shopify:** `SHOPIFY_CLIENT_ID` e `SHOPIFY_CLIENT_SECRET` no ambiente da
   nuvem e a rede liberada para a loja e para `cdn.shopify.com` (o mesmo
   pedido do tópico da limpeza do Shopify).
4. **Saldo do fal:** o papel de parede espera por ele (ver Pendências).

## Resultado

- **24 geradas** no fal: Kontext Max e Seedream 4, 4 por motor em cada
  receita. Custo: cerca de US$ 1,32. O Gemini segue fora (402, sem crédito).
- **4 de 16 passaram** nas duas receitas verificadas:
  - banheira: A2 e A5 (2 de 8);
  - penteadeira: B4 e B7 (2 de 8).
- **Revisão de 2026-10-16: 1 de 16 passa** (A2). A medida nova de altura
  (critério i) veta A5, B4 e B7; a penteadeira fica sem candidata.
- **Motivos das 12 vetadas**, parando no primeiro veto:
  - proporção (i), 7: A3, A4, B2, B3, B6 e B8 pela cabeça grande para a base
    (disco ÷ cabeça de 0,621 a 0,677) e B1 pelo aro grosso (0,075);
  - luz de colagem (h2), 4: A1, A6, A7 e A8;
  - forma (a), 1: B5, com haste reta no lugar do sino.
- **Papel de parede (C1 a C8): sem verificação.** As medidas dependem do
  recorte do produto (BiRefNet, no fal), e o fal está sem saldo.
- **Retoque:** o cabo real (d2) nas quatro, nos dois trechos, como na A1
  aprovada: da traseira da base, pela bancada, até a borda do quadro, e a
  alça da traseira da cabeça até o topo do pivô.
- **Nota comum (g):** logo deformado nas quatro. O retoque do logo fica para
  depois do veredito e da resposta sobre o logo a laser, como no piloto.

## Imagens e o que conferir

As escolhidas estão no branch `claude/project-thread-kjpd2a`, em
`lotes/2026-10-11-classique-lux-cromado/1x1-ambientes/`: a original em
`<receita>/<rótulo>.png` e a final, com o cabo, em
`retoque-cabo/<rótulo>-com-cabo.png`. As vetadas não vão para o git; a cópia
delas está na pasta compartilhada do projeto, em
`fotografo/2026-10-11-classique-lux-cromado/1x1-ambientes/descartadas/`.

| Rótulo | Receita | Situação | O que conferir |
|---|---|---|---|
| A2 | banheira | passou, com cabo | Altura ÷ disco 1,811 (limite 1,82). Logo deformado. Toalhas na mesma bancada dão a escala. |
| A5 | banheira | **vetada (i, altura) em 2026-10-16**, no limite; com cabo | Altura ÷ disco 1,826 (limite 1,82). Logo deformado. Colagem 0,30, perto do limite de 0,32, mas o sino reflete a cena (recorte em `_crops/hp-n-A5.png`). |
| B4 | penteadeira | **vetada (i, altura) em 2026-10-16**; com cabo | Altura ÷ disco 1,883, como a CR2 (1,88). Disco ÷ cabeça 0,680, perto do limite de 0,678. Logo deformado. |
| B7 | penteadeira | **vetada (i, altura) em 2026-10-16**, no limite; com cabo | Altura ÷ disco 1,827 (limite 1,82). Logo deformado. |
| A1 | banheira | **vetada (h2)** | Colagem 0,354: o miolo do sino repete o arco escuro e o filete claro da capa. |
| A3 | banheira | **vetada (i)** | Disco ÷ cabeça 0,674 (−10,5%). |
| A4 | banheira | **vetada (i)** | Disco ÷ cabeça 0,675 (−10,4%). |
| A6, A7, A8 | banheira | **vetadas (h2)** | Colagem de 0,60 a 0,70: cópia do reflexo da capa. |
| B1 | penteadeira | **vetada (i)** | Aro ÷ cabeça 0,075 (faixa 0,037 a 0,058). Também luz âmbar de sol baixo. |
| B2, B3, B6 | penteadeira | **vetadas (i)** | Disco ÷ cabeça 0,666, 0,621 e 0,656. |
| B5 | penteadeira | **vetada (a)** | Haste fina reta no lugar do sino: é outro produto. |
| B8 | penteadeira | **vetada (i)** | Disco ÷ cabeça 0,677 (−10,1%); também colagem 0,458. |

**Conferido nas quatro que passaram:**
- forma: as mesmas peças da capa, nos recortes da cabeça, do pino, do pivô e
  da base; o sino abre logo abaixo do pivô, sem coluna; disco com anel preto;
- pinos na linha do centro da cabeça: de 0,496 a 0,503 (faixa 0,45 a 0,55);
- acabamento prata, sem puxar para dourado;
- LED aceso, com a cor a menos de 0,15 da capa (0,94 a 1,01);
- reflexo do vidro cinza, simples e suave;
- produto uma vez só, sem outro espelho, sem pessoa e sem marca de terceiros;
  frascos sem rótulo;
- lugar: bancada de banheiro, longe da banheira, e penteadeira; luz do dia
  difusa, sem sol direto no vidro.

**Escala no ambiente:**
- banheira: as duas toalhas dobradas na mesma bancada medem cerca de 10 cm de
  altura na escala do produto (37 cm de altura). Plausível.
- penteadeira: os frascos na mesma penteadeira, um pouco atrás do produto,
  medem de 15 a 17 cm. Grandes para perfume, mas plausíveis.

## Revisão de 2026-10-16: altura sobre a base (critério i novo)

O Thiago não publicaria as fotos em uso CR1 a CR3 do Classique Lux,
"desproporcionais, fora da realidade" (2026-10-16). A medida que pega o erro
entrou em `guia/criterios.md` (passo 4): topo da cabeça → centro do pé ÷
disco, VETO acima de 1,82 (`placar.md` › Calibragem, 2026-10-16, CR1 a CR3).
Mesmo método, aplicado às quatro que tinham passado:

| Rótulo | altura ÷ disco | elevação (pelo pé) | Situação |
|---|---|---|---|
| A2 | 1,811 | 13° | passa |
| A5 | 1,826 | 12° | **vetada (i)**, no limite |
| B7 | 1,827 | 13° | **vetada (i)**, no limite |
| B4 | 1,883 | 13° | **vetada (i)** |

- Âncoras: publicaria A1 1,77, CR4 1,79 e A4 1,80; não publicaria CR1 1,85,
  CR3 1,87 e CR2 1,88; capa 1,68. O mesmo script refaz a capa, a A1 e a A4
  do piloto (1,683, 1,769 e 1,803).
- A5 e B7 passam do limite por 0,006 e 0,007, dentro do ruído da medida
  (±0,01). Ficam vetadas pela regra (ver Para calibrar, item 3).
- Topo da cabeça e bordas do disco conferidos em 4×. Prancha:
  `prancha-altura-ambientes.png`. Medidas e recortes na pasta compartilhada
  do projeto, em `fotografo/2026-10-11-classique-lux-cromado/1x1-ambientes/altura/`;
  script em `fotografo/ferramentas-medicao/altura_json.py`.
- A penteadeira fica sem candidata. Gerar mais depende de crédito no fal ou
  no Gemini.

## Medidas

Mesmo método do piloto (`../verificacao.md` › Método). A câmera ficou entre
6° e 15°, perto da capa (7°), então valem as faixas medidas na capa.

| Rótulo | Situação | disco ÷ cabeça | vidro | difusor | aro | topo do sino ÷ disco | pivô → disco | elevação da câmera | LED | colagem (h2) |
|---|---|---|---|---|---|---|---|---|---|---|
| capa | referência | 0,753 | 0,700 | 0,109 | 0,041 | 0,198 | 0,354 | 7° | 0,90 / 0,98 | — |
| faixa | — | 0,678 a 0,828 | 0,630 a 0,770 | 0,071 a 0,120 | 0,037 a 0,058 | 0,168 a 0,269 | até 0,47 | — | ±0,15 | abaixo de 0,32 |
| A1 | **vetada (h2)** | 0,741 | 0,713 | 0,090 | 0,054 | 0,206 | 0,360 | 11° | — | 0,35 |
| A2 | passou | 0,710 | 0,708 | 0,105 | 0,041 | 0,211 | 0,339 | 12° | 0,94 | 0,23 |
| A3 | **vetada (i)** | 0,674 | 0,703 | 0,109 | 0,040 | 0,205 | 0,357 | 12° | 0,94 | 0,23 |
| A4 | **vetada (i)** | 0,675 | 0,703 | 0,111 | 0,037 | 0,205 | 0,357 | 12° | 0,94 | 0,22 |
| A5 | passou | 0,695 | 0,723 | 0,099 | 0,040 | 0,206 | 0,351 | 12° | 0,96 | 0,30 |
| A6 | **vetada (h2)** | 0,706 | 0,688 | 0,104 | 0,052 | 0,214 | 0,351 | 7° | 0,94 | 0,60 |
| A7 | **vetada (h2)** | 0,693 | 0,693 | 0,111 | 0,042 | 0,208 | 0,382 | 10° | 0,93 | 0,67 |
| A8 | **vetada (h2)** | 0,698 | 0,685 | 0,114 | 0,044 | 0,213 | 0,361 | 8° | 0,94 | 0,70 |
| B1 | **vetada (i)** | 0,709 | 0,675 | 0,088 | 0,075 | 0,190 | 0,363 | 6° | 0,88 | 0,27 |
| B2 | **vetada (i)** | 0,666 | 0,720 | 0,103 | 0,037 | 0,216 | 0,334 | 15° | 0,95 | 0,27 |
| B3 | **vetada (i)** | 0,621 | 0,680 | 0,071 | 0,089 | 0,208 | 0,423 | 9° | 0,91 | 0,27 |
| B4 | passou | 0,680 | 0,718 | 0,100 | 0,041 | 0,211 | 0,349 | 12° | 1,01 | 0,29 |
| B5 | **vetada (a)** | 0,535 | 0,760 | 0,080 | 0,040 | 0,133 | 0,127 | 13° | 0,90 | — |
| B6 | **vetada (i)** | 0,656 | 0,715 | 0,104 | 0,039 | 0,200 | 0,351 | 10° | 0,95 | 0,21 |
| B7 | passou | 0,701 | 0,715 | 0,104 | 0,039 | 0,203 | 0,340 | 12° | 1,01 | 0,19 |
| B8 | **vetada (i)** | 0,677 | 0,703 | 0,100 | 0,049 | 0,199 | 0,348 | 14° | 0,95 | 0,46 |

LED: B/R do anel ou do halo ÷ branco neutro da cena. Colagem: NCC do detalhe
do miolo do sino contra a capa (`guia/criterios.md`, passo 5).

## Método (o que mudou desde o piloto)

- **Colagem (h2):** `ferramentas/inspecao_imagem.py colagem`, com o filtro
  passa-alta. Janela: o sino da candidata, do pivô à junção com o disco;
  escala pela largura do disco.
- **Pinos:** a ponta da silhueta mais distante da elipse da cabeça, no lado
  do pino; altura medida do topo da cabeça ÷ altura da cabeça.
- **Cabo (d2):** `ferramentas/cabo_real.py`, sem IA.
  - A alça usa a rota que você marcou na A1 do piloto, levada a cada
    candidata pelo centro do pivô e pela escala da largura do disco, com o
    início escondido atrás da borda de baixo da cabeça e o fim dentro do pivô.
  - O cabo da bancada sai de trás da base e corre até a borda direita do
    quadro, na frente das toalhas e dos frascos.
  - Largura de 5 mm na escala da base (7 a 9 px).
  - Conferido em 8× na saída de trás da base, na saída da alça e na entrada
    no pivô (`_crops/<rótulo>-cabo-*.png`).
  - `inspecao_imagem.py diff`: nada mudou fora da máscara do cabo. No produto,
    só os pixels de borda suave do vão (20 a 31 px por foto).
- **Recortes de região:** capa e candidata na mesma escala, em
  `_crops/<rótulo>-{cabeca,logo,pino,pivo,base}.png`.

## Para calibrar (depende da sua palavra)

1. **Vetos no limite da proporção.** A3 (−10,5%), A4 (−10,4%) e B8 (−10,1%)
   caem por pouco, como a A3 e a A5 do piloto (−10,2% e −10,1%), que você não
   escolheu. Se publicaria alguma delas agora, a faixa de disco ÷ cabeça passa
   para ±11%.
2. **Colagem perto do limite.** A1 vetada com 0,354 e A5 aprovada com 0,30.
   O seu veredito nas duas confirma ou move o limiar de 0,32.
3. **Altura no limite (2026-10-16).** A5 (1,826) e B7 (1,827) passam do
   limite de 1,82 por menos que o ruído. Se publicaria alguma delas, o limite
   sobe para 1,83.

## Pendências

- **Papel de parede (C1 a C8):** gerado e não verificado. Na triagem visual:
  - C1, C5, C6 e C8 têm sol direto forte na parede, perto do produto. Pode ser
    veto k (sol no vidro côncavo), a confirmar com a medida;
  - na C1, um quadro ou espelho de parede (m);
  - na C4, a cabeça parece grande;
  - C2, C3 e C7 parecem plausíveis.

  Com o saldo do fal de volta, recorto, meço, ponho o cabo e entrego a
  prancha. A cópia das 8 está na pasta compartilhada do projeto, em
  `fotografo/2026-10-11-classique-lux-cromado/1x1-ambientes/papel-de-parede-bruto/`.
- **Resolução:** 1024 px, como no piloto (o ML recomenda 1200 px).
- **Gemini:** sem crédito (402).
