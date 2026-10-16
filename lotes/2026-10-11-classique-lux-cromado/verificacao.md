# Verificação do lote · Classique Lux cromado (10202CR), LED ligado · 2026-10-11

Rodada `1x1-piloto`: a réplica do processo do "Gerar fotos com IA" do Mercado
Livre (capa em fundo branco + uma frase de cena), em duas receitas.

## O que preciso de você

1. **Veredito nas duas pranchas:** diga quais você publicaria. Pode ser no
   formato "publicaria tudo, menos B3: motivo". Inclua as vetadas A3 e A5: se
   você publicaria alguma delas, a faixa que as vetou está apertada.
2. **Três respostas que seguem abertas:**
   - o crédito do Gemini (o motor que o ML usa) foi recarregado?
   - o logo gravado a laser já está em produção?
   - "sucesso" quer dizer a qualidade das fotos ou os números de venda no ML?

## Resultado

- **16 geradas** no fal: Kontext Max e Seedream 4, 4 por motor em cada
  receita. Custo: US$ 0,88. O Gemini ficou de fora porque a API respondeu
  402 (sem crédito); refaço essa parte quando o crédito voltar.
- **14 passaram:** bancada 6 de 8, close da base 8 de 8.
- **Vetadas: A3 e A5**, por proporção (item i): disco ÷ cabeça 0,676 e
  0,677, abaixo da faixa (0,678 a 0,828, ±10% da capa). Na sobreposição com a
  capa na mesma escala da base, a cabeça delas fica cerca de 11% maior. É um
  veto no limite. Por isso elas estão na prancha, para você dizer se
  publicaria.
- **Minhas escolhas para uso**, se você aprovar:
  - bancada: A4 e A1, as duas sem nota de "corrigir se der";
  - close da base: B5 e B7, as únicas que fizeram o close pedido. A B5 tem o
    logo certo.
- **Nada foi retocado.** A nota mais comum é a grafia do logo, errada em 9 das
  14. O retoque do logo fica para depois do veredito, só nas que você
  publicaria e depois da resposta sobre o logo a laser.

## Imagens e o que conferir

As aprovadas estão no branch `claude/project-thread-kjpd2a`, em
`lotes/2026-10-11-classique-lux-cromado/1x1-piloto/<receita>/<rótulo>.png`.
As vetadas não vão para o git (regra do `CLAUDE.md`). A cópia delas está na
pasta compartilhada do projeto, em
`fotografo/2026-10-11-classique-lux-cromado/descartadas/`.

| Rótulo | Receita | Situação | O que conferir |
|---|---|---|---|
| A1 | bancada | passou | Nada de forma. Logo quase certo. |
| A2 | bancada | passou | Logo "gurzle". Quase de frente, o anel de luz parece mais largo que na foto real frontal (difusor 0,108 contra 0,086). |
| A3 | bancada | **vetada (i)** | Cabeça cerca de 11% maior que a da capa. |
| A4 | bancada | passou | Sem nota. |
| A5 | bancada | **vetada (i)** | Cabeça cerca de 11% maior. Logo "gercle". |
| A6 | bancada | passou | Logo "Gardie" com G maiúsculo. O pivô fica mais alto que nas outras (pivô → disco 0,403; o limite é 0,47). |
| A7 | bancada | passou | Logo "garde". |
| A8 | bancada | passou | Disco ÷ cabeça 0,682, perto do limite. Logo "Garoie". O quadro no alto à direita pode ser espelho de parede (m). |
| B1 | close da base | passou | Cópia da capa com a luz de estúdio dela (topo do disco branco, vidro vazio): ver se parece colada no ambiente. Logo "gerdie". Não fez o close. |
| B2 | close da base | passou | Logo certo. A moldura no alto à direita pode ser espelho de parede (m). Não fez o close. |
| B3 | close da base | passou | Logo deformado. Não fez o close. |
| B4 | close da base | passou | Logo "gercie". Não fez o close. |
| B5 | close da base | passou | Fez o close. Logo certo. Luz de estúdio da capa. Cabeça 4 a 6% maior na sobreposição, dentro da faixa. |
| B6 | close da base | passou | Disco ÷ cabeça 0,687. Logo certo. Não fez o close. |
| B7 | close da base | passou | Fez o close. Geometria igual à da capa. Logo "geroie". |
| B8 | close da base | passou | Logo "garoe". Frasco branco sem rótulo. Não fez o close. |

**Conferido em todas e dentro da faixa:**
- forma: as mesmas peças da capa, com o sino abrindo logo abaixo do pivô, sem
  coluna; garfo com pinos laterais e disco com anel preto;
- pinos na linha do centro da cabeça: de 0,478 a 0,523;
- acabamento prata, sem puxar para dourado;
- LED aceso, com a cor a menos de 0,15 da capa;
- sem cabo, o que está certo de frente e de 3/4;
- produto uma vez só, sobre a bancada, sem pessoa e sem marca de terceiros.

**Escala no ambiente:** nenhuma tem objeto de tamanho conhecido no mesmo plano
do produto (as toalhas estão atrás). A escala foi julgada a olho e parece
plausível.

## Medidas

Todas medidas pelo mesmo método, na capa, nas três fotos frontais reais
(`referencias/classique-lux/`) e nas candidatas.

| Rótulo | Situação | disco ÷ cabeça | vidro | difusor | aro | topo do sino ÷ disco | pivô → disco | elevação da câmera | LED anel / halo | logo |
|---|---|---|---|---|---|---|---|---|---|---|
| capa | referência | 0,753 | 0,700 | 0,109 | 0,041 | 0,198 | 0,354 | 7° | 0,90 / 0,98 | certo |
| real desligado | foto real | 0,695 | 0,738 | 0,079 | 0,052 | 0,234 | 0,296 | 31° | apagado | — |
| real 4500K | foto real | 0,697 | 0,735 | 0,086 | 0,046 | 0,228 | 0,302 | 30° | — / 0,78 | — |
| real 6000K | foto real | 0,695 | 0,735 | 0,086 | 0,046 | 0,230 | 0,298 | 31° | 1,23 / 1,16 | — |
| A1 | passou | 0,711 | 0,715 | 0,096 | 0,046 | 0,208 | 0,347 | 9° | 0,89 / 0,91 | quase certo |
| A2 | passou | 0,722 | 0,703 | 0,108 | 0,041 | 0,212 | 0,388 | 9° | 0,94 / 1,00 | "gurzle" |
| A3 | **vetada (i)** | 0,676 | 0,730 | 0,094 | 0,041 | 0,205 | 0,359 | 8° | 0,94 / 0,89 | deformado |
| A4 | passou | 0,714 | 0,705 | 0,108 | 0,040 | 0,207 | 0,364 | 10° | 1,03 / 1,02 | certo |
| A5 | **vetada (i)** | 0,677 | 0,715 | 0,103 | 0,040 | 0,215 | 0,355 | 8° | 0,97 / 0,94 | "gercle" |
| A6 | passou | 0,726 | 0,713 | 0,090 | 0,054 | 0,198 | 0,403 | 10° | 0,98 / 0,93 | "Gardie" |
| A7 | passou | 0,720 | 0,725 | 0,094 | 0,044 | 0,210 | 0,379 | 12° | 0,93 / 0,92 | "garde" |
| A8 | passou | 0,682 | 0,718 | 0,096 | 0,045 | 0,214 | 0,365 | 11° | 0,94 / 0,95 | "Garoie" |
| B1 | passou | 0,758 | 0,703 | 0,106 | 0,042 | 0,212 | 0,355 | 9° | 0,93 / 1,00 | "gerdie" |
| B2 | passou | 0,710 | 0,718 | 0,098 | 0,044 | 0,211 | 0,352 | 10° | 1,00 / 0,94 | certo |
| B3 | passou | 0,701 | 0,690 | 0,103 | 0,052 | 0,220 | 0,358 | 12° | 0,98 / 1,04 | deformado |
| B4 | passou | 0,712 | 0,715 | 0,101 | 0,041 | 0,211 | 0,365 | 8° | 1,03 / 0,94 | "gercie" |
| B5 | passou | cabeça 4 a 6% maior* | * | * | * | 0,214 | 0,359 | 5° | 0,99 / 0,98 | certo |
| B6 | passou | 0,687 | 0,698 | 0,113 | 0,039 | 0,212 | 0,363 | 11° | — / 0,96 | certo |
| B7 | passou | igual à capa* | * | * | * | 0,205 | 0,355 | 8° | 1,00 / 0,98 | "geroie" |
| B8 | passou | 0,692 | 0,703 | 0,098 | 0,051 | 0,202 | 0,352 | 14° | 0,96 / 0,99 | "garoe" |

\* B5 e B7 são closes com a cabeça cortada no alto. A elipse ajustada num arco
curto não é estável, então a cabeça foi conferida sobrepondo o contorno da
capa na mesma escala da base. As folhas de sobreposição estão na pasta
compartilhada do projeto, em `fotografo/2026-10-11-classique-lux-cromado/`
(`sobreposicao-A.png` e `sobreposicao-B.png`).

## Método

- **Silhueta:** recorte do produto. Na capa, a máscara manual; nas
  candidatas, BiRefNet.
- **Cabeça:** elipse ajustada ao contorno (RANSAC), num arco que evita o garfo.
- **Pivô:** a linha mais estreita da silhueta entre a cabeça e a base.
- **Disco:** a largura da primeira linha abaixo do pivô com 97% ou mais da
  largura máxima da base.
- **Topo do sino:** a largura 2% do disco abaixo do pivô.
- **Vidro, difusor e aro:** bordas no perfil radial mediano da cabeça.
- **Elevação da câmera:** pela meia-elipse da borda de baixo do disco,
  sen(elevação) = b/a.
- **LED:** B/R mediano em pixels não saturados no anel ou no halo do vidro,
  dividido pelo B/R de um branco neutro da cena.
- **Ruído da medida:** reduzi a capa para 1024 px e borrei de 1 a 2 px.
  Disco ÷ cabeça, vidro, sino e pivô mudaram menos de 1%. O difusor mudou até
  −5% e o aro de +12 a +15%.
- **Scripts:** pasta compartilhada do projeto, em
  `fotografo/ferramentas-medicao/`. Ainda não estão no repositório.

## Para calibrar (depende da sua palavra)

1. **Difusor e aro: a faixa de ±10% da capa reprova as próprias fotos
   reais.** Nelas, o difusor fica de −21% a −28% e o aro de +12% a +27%. Além
   disso, ±10% fica abaixo do ruído da medida em 1024 px. O guia manda
   corrigir a faixa quando uma foto real reprova. Neste lote, apliquei a faixa
   entre o menor e o maior valor das referências (capa e fotos reais), ±10%:
   - difusor de 0,071 a 0,120;
   - aro de 0,037 a 0,058.

   Com ±10% da capa, cairiam também A1, A6, A7, A8, B2, B3 e B8. O seu
   "publicaria" nelas confirma ou derruba essa faixa.
2. **Por que o veto de A3 e A5 se mantém, embora a foto real tenha 0,695.** Na
   foto real, a câmera está alta (cerca de 30°) e perto, então a cabeça fica
   mais perto da lente que a base e sai maior. A3 e A5 têm câmera baixa
   (cerca de 8°, como a capa). Nessa altura, a perspectiva não reduz o disco ÷
   cabeça.
3. **Divergências com `guia/produto.md` › Medidas.**
   - Disco ÷ cabeça na still: o guia diz 0,78 (lido na grade); este método dá
     0,753.
   - Pivô → topo do disco na foto real: o guia diz cerca de 0,41 "com a câmera
     mais baixa". A elipse do disco mostra a câmera da foto real mais alta que
     a da still (30° contra 7°), e este método dá 0,30.

   Os vetos deste lote usam os valores deste método, medidos do mesmo jeito na
   capa e nas candidatas. Registrei as duas leituras no guia. Diga qual vale.
4. **Topo do sino.** A faixa de ±15% da capa também reprovaria as fotos reais
   (+15% a +18%). Neste lote não muda nada: todas as candidatas têm câmera
   baixa, como a capa, e ficaram entre 0% e +11%.
5. **Cor do LED.**
   - A foto real de 6000K dá 1,16 por este método; o guia diz 1,07.
   - A de 4500K dá 0,78, igual ao guia.
   - A capa (still ligada) dá 0,98, entre as duas. Pela cor, não dá para saber
     qual temperatura a still mostra.
6. **Close da base.** Seis das oito mostram o produto inteiro em vez do close.
   Na próxima rodada, reforço o enquadramento na receita. É ajuste de receita,
   não de critério.
7. **Cópias da capa.** B1, B5 e B7 copiam a capa quase igual, inclusive a luz
   de estúdio. São fiéis, mas podem parecer coladas no ambiente. O seu
   veredito diz se isso incomoda.

## Pendências

- **Resolução:** as candidatas têm 1024 px. O ML recomenda 1200 px (mínimo
  500). O Seedream entrega 1280 px, mas o `ensaio.py` reduz tudo para 1024 px
  para o julgamento ser cego. Só amplio com o seu acordo, porque o ampliador
  redesenha detalhes.
- **Capa em fundo branco:** a categoria do 10202CR no ML ainda não está
  registrada (`guia/cena.md`), então o lote entrega também a capa branca:
  `referencias/capa/classique-lux-cromado-ligado-capa-r1.png`. São pixels
  reais da still, em 1536 px, com a máscara conferida.
- **Gemini:** quando o crédito voltar, rodo o Gemini 2.5 Flash Image (o motor
  do ML) e o Gemini 3 Pro com a mesma capa e a mesma moldura. São 16 imagens,
  cerca de US$ 1,38.
- **Rodada completa:** depois da resposta sobre o logo.
