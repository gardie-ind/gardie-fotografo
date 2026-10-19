# Teste do Runway: Classique Lux cromado, ligado (2026-10-19)

Pedido do Thiago (19/10): "Utilize Runway para fazer uma das fotos de produto,
vamos ver qual é a qualidade dele. Teste como se estivesse começando do zero, e
depois teste com o nosso harness."

Receita `mesa-banheiro-bancada`, 1:1, 4 gerações por motor e por condição,
julgadas pelo checklist de `guia/criterios.md`.

## Resultado

**Passaram 3 de 16, todas do Gemini 3 Pro rodando dentro do Runway:**
`do-zero-gemini-4`, `harness-gemini-3` e `harness-gemini-4`.

| Condição | Gen-4 (modelo do Runway) | Gemini 3 Pro (no Runway) |
|---|---|---|
| Do zero | 0 de 4 | 1 de 4 |
| Harness | 0 de 4 | 2 de 4 |

- **Gen-4 erra o suporte em 8 de 8.** Troca o pivô curto e o sino por um
  pescoço ou uma coluna de abajur: pivô → disco de 0,51 a 0,85 (veto acima de
  0,47; capa 0,349) e altura de 1,92 a 2,72 (veto acima de 1,82). Três ainda
  inventam texto ou placa na cúpula, e uma, um botão na coluna. O harness não
  muda isso: é um defeito do modelo, não do pedido.
- **Gemini 3 Pro melhora com o harness.** Do zero, errou forma (placa
  inventada no difusor), estado do LED (apagado) e proporção. Com o harness,
  os dois vetos foram só de altura, justamente nas duas que saíram de frente.
- **Comparação:** no piloto de 11/10, na mesma receita, o Kontext Max passou
  3 de 4 (o Thiago publicaria a A1 e a A4) e o Seedream 4, 3 de 4 (nenhuma
  publicaria).

## Como foi feito

- **Acesso:** conector do Runway, plano grátis (500 créditos). O `ensaio.py`
  não chama o Runway, então o harness foi replicado à mão, com a mesma capa r1,
  a mesma moldura e a mesma receita. O Runway só usa a imagem citada por
  etiqueta, então entrou "(@produto)" depois de "The first attached image".
  Prompts exatos, IDs das tarefas e créditos estão em `manifesto.json`.
- **Do zero:** a still de catálogo ligada, crua, sem preparo, com o prompt
  "Professional product photo of @espelho on a white marble bathroom counter
  next to a window, with a folded towel and an orchid, natural light."
- **Motores:** Gen-4 (1088 px, 8 créditos por imagem) e o nano-banana-pro do
  Runway, que é o Gemini 3 Pro Image do Google (1024 px, 20 créditos).
- **Créditos:** 224 nas 16 gerações e 19 nos recortes para medir; 243 de 500.

## Medição

- **Método:** o mesmo do lote de 11/10 (`medir2.py` e `altura_json.py`, de
  `fotografo/ferramentas-medicao/`). A silhueta veio do recorte de fundo do
  próprio Runway, porque o fal está sem saldo e não há BiRefNet.
- **Calibração do recorte do Runway** na A1 do piloto, contra o BiRefNet:

  | Razão | Recorte do Runway | BiRefNet |
  |---|---|---|
  | disco ÷ cabeça | 0,708 | 0,711 |
  | vidro | 0,720 | 0,715 |
  | difusor | 0,098 | 0,096 |
  | aro | 0,042 | 0,046 |
  | topo do sino | 0,208 | 0,208 |
  | pivô → disco | 0,351 | 0,347 |
  | altura | 1,778 | 1,769 |

  O recorte do Runway fecha cerca de 1% para dentro do cromado: o aro sai
  cerca de 0,004 menor e a altura cerca de 0,01 maior. Levei isso em conta nos
  valores no limite.
- **Vistas espelhadas** (pino à esquerda) foram medidas na imagem desvirada.
- **LED:** B/R mediano no anel e no halo, dividido pelo B/R dos brancos da
  própria cena.

Faixas: disco ÷ cabeça 0,678 a 0,828; vidro 0,63 a 0,77; difusor 0,071 a
0,120; aro 0,037 a 0,058; sino 0,168 a 0,228; pivô → disco até 0,47; altura até
1,82; pinos 0,45 a 0,55; LED a até 0,15 da capa; colagem abaixo de 0,32.

| Rótulo | Vista | disco÷cabeça | vidro | difusor | aro | sino | pivô→disco | altura | elev. | pinos | LED anel/halo | colagem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| capa r1 | 3/4 | 0,753 | 0,698 | 0,109 | 0,042 | 0,201 | 0,349 | 1,683 | 10° | 0,51 | 0,90 / 0,98 | — |
| A1 piloto (Kontext) | 3/4 | 0,711 | 0,715 | 0,096 | 0,046 | 0,208 | 0,347 | 1,769 | 11° | — | 0,89 / 0,91 | 0,20 |
| do-zero-gen4-1 | 3/4 | 0,735 | 0,728 | 0,090 | 0,046 | 0,168 | **0,520** | **1,920** | 13° | 0,53 | 0,92 / 0,99 | 0,22 |
| do-zero-gen4-2 | 3/4 | 0,704 | 0,735 | 0,090 | 0,042 | 0,168 | **0,674** | **2,151** | 13° | 0,51 | 0,92 / 1,00 | 0,25 |
| do-zero-gen4-3 | 3/4 | **0,655** | 0,730 | 0,100 | 0,035 | 0,190 | **0,850** | **2,515** | 11° | 0,51 | 0,96 / 0,99 | 0,23 |
| do-zero-gen4-4 | 3/4 | 0,769 | 0,725 | 0,105 | 0,032 | 0,201 | **0,620** | **1,936** | 13° | 0,55 | 0,93 / 1,00 | 0,29 |
| do-zero-gemini-1 | 3/4 esp. | 0,703 | 0,750 | 0,084 | 0,041 | 0,200 | 0,389 | **1,935** | 11° | 0,52 | — / 1,00 | 0,17 |
| do-zero-gemini-2 | 3/4 | 0,762 | 0,728 | 0,089 | 0,047 | 0,187 | 0,366 | 1,821 | 12° | 0,52 | 1,00 / 1,02 | 0,24 |
| do-zero-gemini-3 | 3/4 | 0,764 | 0,750 | 0,084 | 0,041 | 0,198 | 0,391 | 1,834 | 12° | 0,52 | 1,01 / 1,02 | 0,16 |
| do-zero-gemini-4 | 3/4 | 0,742 | 0,740 | 0,093 | 0,037 | 0,195 | 0,366 | 1,796 | 12° | 0,53 | 0,97 / 1,01 | 0,23 |
| harness-gen4-1 | frente | 0,706 | 0,730 | 0,086 | 0,049 | 0,209 | **0,768** | **2,310** | 13° | 0,51 | 0,86 / 1,00 | 0,19 |
| harness-gen4-2 | 3/4 | 0,698 | 0,730 | 0,089 | 0,046 | **0,238** | **0,651** | **2,715** | 14° | 0,54 | 0,93 / 1,00 | 0,23 |
| harness-gen4-3 | 3/4 | 0,720 | 0,725 | 0,095 | 0,042 | **0,250** | **0,519** | **2,177** | 12° | 0,52 | 0,94 / 0,98 | 0,22 |
| harness-gen4-4 | 3/4 | 0,691 | 0,743 | 0,090 | 0,039 | 0,182 | **0,506** | **2,296** | 14° | 0,51 | 0,96 / 1,02 | 0,19 |
| harness-gemini-1 | frente | 0,731 | 0,763 | 0,075 | 0,044 | 0,199 | 0,396 | **1,879** | 11° | 0,50 | 0,92 / 0,89 | 0,20 |
| harness-gemini-2 | frente | 0,716 | 0,740 | 0,091 | 0,039 | 0,194 | 0,391 | **1,921** | 10° | 0,51 | 0,95 / 0,87 | 0,20 |
| harness-gemini-3 | 3/4 | 0,754 | 0,743 | 0,094 | 0,035* | 0,189 | 0,354 | 1,732 | 8° | 0,50 | 0,83 / 1,01 | 0,28 |
| harness-gemini-4 | 3/4 esp. | 0,782 | 0,718 | 0,098 | 0,044 | 0,194 | 0,349 | 1,725 | 9° | 0,52 | 0,94 / 1,05 | 0,23 |

Em negrito, o que está fora da faixa. \* 0,035 no recorte do Runway equivale a
cerca de 0,039 no BiRefNet, dentro da faixa; no limite, a conferir com o
BiRefNet quando o fal tiver saldo.

## Candidata por candidata

| Rótulo | Veredito | Motivo |
|---|---|---|
| do-zero-gen4-1 | vetada (a, i) | pescoço entre o pivô e o sino |
| do-zero-gen4-2 | vetada (a, i) | coluna; texto inventado na cúpula |
| do-zero-gen4-3 | vetada (a, i) | coluna longa; cabeça grande para a base |
| do-zero-gen4-4 | vetada (a, i) | pescoço |
| do-zero-gemini-1 | vetada (i) | altura 1,94: a cabeça fica alta (pino → pé ÷ disco 1,21, contra 1,08 na capa); sem logo |
| do-zero-gemini-2 | vetada (a) | placa cromada inventada no difusor, no lugar do logo |
| do-zero-gemini-3 | vetada (c) | LED apagado, com a referência ligada; logo "geroie"; altura 1,83 |
| do-zero-gemini-4 | **passou** | logo certo; falta o cabo (d2) |
| harness-gen4-1 | vetada (a, i) | pescoço; placa dourada com texto na cúpula |
| harness-gen4-2 | vetada (a, i) | coluna alta com botão inventado e "gardie" gravado nela; anel branco sob a base |
| harness-gen4-3 | vetada (a, i) | pescoço; sino largo demais no topo |
| harness-gen4-4 | vetada (a, i) | pescoço; texto na cúpula |
| harness-gemini-1 | vetada (i) | altura 1,88, de frente (pino → pé ÷ disco 1,21) |
| harness-gemini-2 | vetada (i) | altura 1,92, de frente (pino → pé ÷ disco 1,23) |
| harness-gemini-3 | **passou** | logo certo; colagem 0,285, a mais perto do limite, com o sino ainda refletindo a janela da cena; falta o cabo (d2) |
| harness-gemini-4 | **passou** | logo certo; vista espelhada, com o logo à direita, coerente com o giro; falta o cabo (d2) |

**Conferido nas três que passaram:** as mesmas peças da capa (garfo de fita
única com pinos na linha do centro, pivô curto, sino abrindo logo abaixo dele,
cúpula sobre o disco e anel preto); acabamento prata; LED aceso, com cor a até
0,07 da capa; logo "gardie" no difusor, embaixo; produto uma vez só, de pé na
bancada; sem pessoa, sem marca, sem outro espelho; reflexo cinza e suave no
vidro. Recortes lado a lado com a capa em `detalhes-aprovadas.png`.

**Vista de frente e altura.** Com a cabeça em pé, a foto de frente fica
naturalmente mais alta que a capa, que tem a cabeça inclinada. Por isso medi
também a altura do pino (o centro da cabeça) até o centro do pé, ÷ disco, que
não depende da inclinação: 1,08 na capa, de 1,09 a 1,12 nas três que passaram,
1,21 e 1,23 nas duas de frente vetadas. O suporte cresceu de 12% a 14%; o veto
não vem só da pose.

## O que falta nas três que passaram

- **Cabo (d2):** LED aceso sem cabo à vista. Não fiz o retoque com o
  `cabo_real.py`, porque o pedido era medir a qualidade do Runway. Faço nas que
  o Thiago publicar.
- **Escala:** julgada a olho. Nas do harness, a toalha está atrás do produto;
  na `do-zero-gemini-4`, toalha e orquídea estão na bancada, em tamanho
  plausível.
- **Resolução:** 1024 px. O ML recomenda 1200 px e a página do Shopify, 2048 px.

## Custo e vídeo

- **Foto:** o único motor que passou no Runway é o Gemini 3 Pro, que já é
  candidato no `ensaio.py` pela API do Google. Pelas tabelas de terceiros
  (conferir no dia), sai cerca de US$ 0,13 por imagem direto no Google, contra
  20 créditos no Runway (cerca de US$ 0,48 no plano Standard, de US$ 15 por
  625 créditos ao mês).
- **Vídeo:** o plano grátis não gera vídeo. O que o Runway tem de diferente
  para a meta nº 1 é a edição de vídeo (Aleph 2.0), que parte de um vídeo real
  e muda só o que se pede, como o ambiente, mantendo produto, movimento e o
  reflexo real. É o caminho "real + IA em volta" do diagnóstico. Custa 28
  créditos por segundo (10 s = 280 créditos) e exige plano pago.

## Arquivos

- `prancha-comparativa-runway.png`: as 16 com o veredito, a capa, a still e a
  A1 do piloto.
- `detalhes-aprovadas.png`: cabeça e logo, junção e base das três que
  passaram, lado a lado com a capa na mesma escala.
- `aprovadas-pelo-agente/`: as três que passaram, em resolução cheia.
- `geradas/`: as 16, em resolução cheia (na pasta do projeto).
- `manifesto.json` (prompts, referências, motores, IDs e créditos), `mapa.json`
  e `medidas.json`.
