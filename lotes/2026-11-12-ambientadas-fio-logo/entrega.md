# Fio real e "gardie" a laser nas ambientadas LUX publicadas

Lote 2026-11-12, pedido do Thiago: "Precisamos colocar o fio nas fotos
ambientadas que já existem e o Gardie gravado à laser".

## Resultado

Fiz o levantamento das fotos LUX publicadas no site: são 42 (32 ambientadas e
10 detalhes) dos cinco modelos, Classique 10202, Royale 10288, Mobile 10455,
Visage 10509 e Flex 10554. A Lumière ficou fora.

- **32 passaram e estão aqui**, todas com o "gardie" a laser no vidro:
  - 29 com o fio real desenhado;
  - 3 só com o logo, porque o fio delas não precisa de mudança (C4, R5 e M1,
    o motivo está na tabela).
- **7 reprovadas**: estão publicadas, mas não passam no critério, por defeito
  do produto que já estava na foto. Não retoquei nenhuma. O motivo medido
  está abaixo, e a prancha é `reprovadas.png`.
- **3 sem nada a fazer**:
  - 10455CR-AMB-01 e 10455GL-AMB-01 já têm o logo e o fio real (aprovadas em
    22/10);
  - 10288CR-DET-01 não mostra o vidro com o logo nem o fio.

Nada foi gerado por IA no produto:
- o fio sai do `ferramentas/cabo_real.py`, que desenha um cilindro branco com
  a luz e a cor da cena e não toca nos pixels do espelho;
- o logo é o mesmo "gardie" a laser das stills, na cor do anel (aceso) ou
  cinza escuro (LED apagado).

**Aviso:** a chave do fal no ambiente devolveu 401 (recusada). As máscaras do
produto (BiRefNet, que só recorta e não muda pixel) saíram pelo conector do
fal no claude.ai. Vale conferir a chave `FAL_KEY` do ambiente.

## Como conferir

Por modelo, uma letra (C, R, M, V, F), duas pranchas:

- `prancha-<letra>.png`: as fotos inteiras depois do retoque, com a REF (a
  still aprovada com o fio) na primeira célula;
- `detalhe-<letra>.png`: antes e depois lado a lado, num recorte ampliado do
  trecho que mudou (fio e logo).

O arquivo final de cada rótulo é `final/<ID>.png`, com o mesmo ID da foto
canônica do site. O `mapa.json` liga rótulo e ID. O `manifesto.json` guarda,
por foto, o original (link do CDN e md5), o logo, a conferência e o md5 do
arquivo final.

### Classique Lux 10202 (C)

| Rótulo | ID | O que mudou e o que conferir |
|---|---|---|
| C1 | 10202CR-AMB-01 | Fio na bancada saindo de trás da base. O espelho de parede no fundo já estava na foto (m) |
| C2 | 10202CR-AMB-02 | Fio na bancada |
| C3 | 10202CR-AMB-03 | Fio na bancada e alça no vão entre a cabeça e o pivô |
| C4 | 10202CR-DET-01 | Só o logo: a base fica fora do quadro, então o fio não aparece |
| C5 | 10202CR-DET-02 | Fio na bancada e alça no vão. Os pixels do vão que mudaram são de parede (p95 de 16 níveis da cor da parede) |
| C6 | 10202GL-AMB-01 | Fio na bancada e alça; o objeto da frente cobre o fio |
| C7 | 10202GL-AMB-02 | Fio na bancada e alça |
| C8 | 10202GL-DET-01 | Alça no vão |
| C9 | 10202GL.RD-DET-01 | Alça no vão |

### Royale Lux 10288 (R)

| Rótulo | ID | O que mudou e o que conferir |
|---|---|---|
| R1 a R4 | 10288CR-AMB-01 a 04 | Fio na bancada saindo de trás da base; na R2, o objeto da frente cobre o fio |
| R5 | 10288CR-AMB-05 | Só o logo: é foto real, então o fio e a alça já são os de verdade |
| R6 a R8 | 10288GL-AMB-01 a 03 | Fio na bancada. Na R7, o espelho de parede já estava na foto (m) |
| R9 | 10288GL.RD-AMB-01 | Fio na bancada, com o reflexo dele no tampo polido |
| R10 | 10288GL.RD-DET-01 | Fio na bancada |

### Mobile Lux 10455 (M)

| Rótulo | ID | O que mudou e o que conferir |
|---|---|---|
| M1 | 10455CR-AMB-02 | Só o logo: o fio da foto já segue a rota real (vão, atrás do anel, ao lado do pivô, atrás dos braços) e ficou. Vidro ÷ difusor dá 0,88, contra 0,79 a 0,85 nas outras Mobile: o difusor está mais fino |
| M2 | 10455GL.RD-AMB-01 | Fio pendurado: aparece no vão entre a alça do garfo e a cabeça e desce pela parede |
| M3 | 10455GL.RD-DET-01 | Igual à M2, com o LED apagado (logo cinza escuro) |

### Visage Lux 10509 (V)

| Rótulo | ID | O que mudou e o que conferir |
|---|---|---|
| V1 a V3 | 10509CR-AMB-01 a 03 | Fio pendurado saindo de baixo da cabeça, com uma sombra suave na parede do lado oposto à luz |
| V4 | 10509GL-AMB-01 | Igual |
| V5 | 10509GL.RD-AMB-01 | Igual |

Nas frontais, o sombreado esquisito da parede já estava na foto publicada.

### Flex Lux 10554 (F)

| Rótulo | ID | O que mudou e o que conferir |
|---|---|---|
| F1 | 10554CR-AMB-01 | O fio desce atrás do bloco da presilha, à esquerda da barra vertical, e deita na bancada atrás do vaso |
| F2 | 10554GL-AMB-01 | Fio pendurado, com luz de frente |
| F3 | 10554GL-AMB-02 | Fio pendurado numa parede branca ao sol, com a sombra do fio. Tem pouco contraste, que é o real (branco sobre branco) |
| F4 | 10554GL-DET-01 | Fio pendurado, LED apagado |
| F5 | 10554GL.RD-AMB-01 | Fio pendurado, LED apagado. O reflexo do vidro é plano (h, corrigir se der): não mexi |

No Flex, o fio sai à esquerda da barra vertical, 0,36 da largura da barra
fora dela. A largura do fio é 0,33 da barra.

## Reprovadas (`reprovadas.png`)

Estão no site hoje e não passam no critério. Não retoquei nenhuma.

| Rótulo | ID | Motivo |
|---|---|---|
| X1 | 10202GL.RD-AMB-01 | l: um segundo espelho de aumento red gold na cena |
| X2 | 10288GL.RD-AMB-02 | a/i: coluna arredondada, sem o colar, 11% mais alta |
| X3 | 10509GL-AMB-02 | a: suporte com moldura vazada, que o real não tem |
| X4 | 10554CR-AMB-02 | i: barra 12% curta, cabeça ÷ barra 18% acima |
| X5 | 10554GL.RD-AMB-02 | l: espelho oval fantasma na parede |
| X6 | 10554CR-DET-01 | a: pantógrafo com 5 cruzamentos |
| X7 | 10554GL.RD-DET-01 | l: arco fantasma |

## Conferência medida (29 com fio novo)

| Medida | Resultado |
|---|---|
| Corredor (linhas da rota no fundo visível que mostram o fio) | 100% em todas |
| Produto intocado | No máximo 10 px do corpo sólido mudaram, com até 6 níveis de diferença (o fio passa rente) |
| Nitidez | O sigma do fio fica abaixo do das bordas do espelho junto da rota, em todas |
| Olhar em 1× | Todas |

Sobre a nitidez: na primeira passada, o fio de 11 fotos saiu até 0,22 px mais
mole que as bordas do espelho. Desenhei de novo, e o critério ("não fica mais
mole") passou sem tolerância.

## Para o critério

Duas medidas estão sem regra no guia:

- **Largura do fio.** O guia diz "5 mm na escala do Ø da base". Nas fotos de
  IA, a escala do vidro e a da ferragem junto do fio às vezes discordam.
  Nesses casos, usei a da ferragem vizinha, porque é com ela que o olho
  compara.
- **Diferença mínima de 2%.** A regra de que menos de 2% dos pixels mudados
  é edição que falhou não serve para fio fino: aqui o fio muda de 0,1% a 2%
  do quadro. Usei o corredor e a máscara do produto.

Depois do seu veredito, registro as duas no `placar.md` e no
`guia/criterios.md`.

## O que preciso de você

1. **Veredito** por rótulo, ou só as exceções ("publicaria tudo, menos V3").
2. **As 7 reprovadas**: tiro do site, ou ficam até haver substitutas?

Com o veredito, monto um zip só com as aprovadas, com os nomes `<ID>.png`.
Você solta os arquivos na pasta Fotos canônicas e o robô troca no site.
Depois disso, levo as aprovadas para `aprovadas/` e abro o PR.
