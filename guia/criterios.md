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
| a2. Botão ou ícone touch inventado no vidro (o produto não tem): defeito local, apagado no retoque | CORRIGIR SE DER (Thiago, calibragem 2026-10-01, `1x1/B5` e `1x1/E13`) |
| b. Acabamento igual ao da referência; cromado lê prata, nunca dourado | VETO (padrão — confirmar com o Thiago) |
| c. LED no mesmo estado (aceso ou apagado) e na mesma cor da referência | VETO (padrão — confirmar com o Thiago) |
| d. Cabo onde a vista real o mostra e ausente onde ela o esconde (`guia/produto.md` › Cabo e plug). De frente ou de 3/4, produto de mesa sem cabo está certo (10202CR-4). Modelo sem cabo à vista (sem LED, Lumière) com cabo também cai aqui | VETO (padrão — confirmar com o Thiago) |
| e. Cabo na rota real do modelo: branco, fino, sem conector inventado, com folga compatível com 1,5 m | VETO (padrão — confirmar com o Thiago) |
| f. Plug, quando aparece, fiel ao NBR 14136 da referência; mostrar o fio ligado na tomada não é exigido | VETO (Thiago) |
| f2. Plug solto na bancada com o LED aceso (contradição física) | VETO (padrão — confirmar com o Thiago) |
| g. Logo com a grafia errada, ou ausente (o Thiago publicaria a 10202CR-4 com "geroie") | CORRIGIR SE DER (padrão — confirmar com o Thiago) |
| g2. Logo fora da posição da capa (no aro, no vidro) | VETO, como a (padrão — confirmar com o Thiago) |
| h. Física do reflexo (`guia/cena.md`) | CORRIGIR SE DER (Thiago) |
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
   | parede: braço ou suporte ÷ cabeça, placa ÷ cabeça | ±10%, depois de medidos na capa do primeiro lote |

   **Escala no ambiente:** meça em px uma dimensão total do produto
   (`guia/produto.md` › Medidas) e um objeto de tamanho conhecido no MESMO
   plano (sobre a mesma bancada, à mesma distância da câmera): frasco de
   perfume de 10 a 15 cm, torneira, toalha de rosto dobrada, gaveta. Compare
   com a razão em cm. Nos closes, a escala é conferida pelas proporções.
5. **Acabamento (b):** os realces do cromado são neutros, sem puxar para
   amarelo ou dourado. Compare com a capa no mesmo tipo de recorte.
6. **LED (c):** mesmo estado da capa. Para a cor, meça o B/R mediano só em
   pixels não saturados (canal máximo entre 60 e 244): no anel ou, se ele
   estourar, numa faixa de ~3% do Ø logo por dentro dele (o halo no vidro),
   em 4 amostras (12, 3, 6 e 9 h). Divida pelo B/R de um branco neutro da
   mesma cena (toalha, parede). Por esse método, as fotos reais dão ≈0,78 em
   4500K e ≈1,07 em 6000K. VETO se a candidata se afastar mais de 0,15 da
   capa, metade dessa distância (padrão — calibrar).
7. **Cabo e plug (d, e, f):** confira a vista contra `guia/produto.md` › Cabo
   e plug, que cita as fotos reais de cada vista. Plug visível: compare a
   forma com `referencias/chicote-eletrico/`.
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
- **Editor de imagem inteira** (Kontext, Seedream ou Gemini em edição):
  recodifica o produto, então a candidata volta ao checklist desde o começo.
- **Depois de toda edição:** rode
  `ferramentas/inspecao_imagem.py diff base nova [máscara]`. Se menos de 2%
  dos pixels mudaram, a edição falhou: não apresente a imagem como corrigida.
