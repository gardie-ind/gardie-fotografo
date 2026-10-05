# Placar dos motores

Este placar começa do zero, com o processo atual: capa padronizada, moldura
curta, várias gerações e filtro medido.

## Vencedor claro

Um motor vence quando cumpre os quatro critérios:

1. tem a maior taxa sem veto (passaram ÷ geradas), com pelo menos 25 pontos
   percentuais de margem sobre o 2º colocado (padrão — confirmar com o
   Thiago);
2. tem pelo menos 1 imagem que o Thiago publicaria em cada receita do lote;
3. tem zero alucinação de forma (a) e de proporção (i) em TODAS as imagens
   que gerou no lote, não só nas que passaram. O alvo é o nível do "Gerar
   fotos com IA" do ML, que não alucina a forma;
4. repete os critérios 1 a 3 num 2º espelho de montagem diferente (padrão —
   confirmar com o Thiago).

Enquanto o líder alucinar forma ou proporção, ninguém vence e o teste
continua, com desafiantes ou com mudança de um fator (`guia/prompts.md`).
Quem decide congelar os perdedores é o Thiago.

**Situação após o lote 2026-10-01 (Classique Lux, 1:1, n=4):** ninguém vence.

| Motor | Sem veto | Publicaria | Alucinações de forma/proporção | Receitas sem publicaria |
|---|---|---|---|---|
| kontext (Max) | 23/24 (96%) | 8 | 1 (E8, escala) | banheira, papel de parede |
| gemini-2.5-flash-image | 20/24 (83%) | 8 | 4 (+5 botões touch, retocáveis) | close-detalhe, penteadeira |
| seedream 4 edit | 14/24 (58%) | 0 | 9 | todas |
| gemini-3-pro-image | 13/24 (54%) | 1 | 8 (+3 cópias do produto) | 5 de 6 |

Critério 1 falha (kontext lidera por 13 pontos, não 25), o 2 falha para todos e
o 3 falha para todos.

## Próxima rodada: réplica do processo do ML

| Item | Definição |
|---|---|
| Espelho | Classique Lux cromado (10202CR), capa da still ligada |
| Motores | os candidatos de `guia/prompts.md` |
| Receitas | as 6 de `receitas/` em 1:1, mais a `mesa-banheiro-bancada` em 4:5 para o feed (rodada à parte, `--aspecto 4:5`) |
| Volume | 6 gerações por motor por receita |
| Depois | vencedor e vice repetem a rodada num espelho de parede (Visage Lux ou Mobile Lux) |

## Lotes

Uma linha por motor × receita × formato × lote. "Passaram" significa
aprovadas pelo filtro do agente. "Publicaria" é o veredito do Thiago.
"Alucinações" conta todas as geradas, inclusive as vetadas pelo agente.

| Data | Lote (modelo, acabamento) | Receita | Formato | Motor | Variação | Geradas | Passaram | Publicaria | Alucinações (tipo: n) | Observação |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | close-detalhe | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 4 | 0 | 0 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | close-detalhe | 1:1 | gemini-3-pro-image | capa r1 | 4 | 3 | 1 | forma: 1 | publicaria: 1x1/A11 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | close-detalhe | 1:1 | kontext (Max) | capa r1 | 4 | 4 | 3 | 0 | publicaria: 1x1/A3 1x1/A5 1x1/A13 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | close-detalhe | 1:1 | seedream 4 edit | capa r1 | 4 | 4 | 0 | 0 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-bancada | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 3 | 2 | forma: 1 | publicaria: 1x1/B5 1x1/B12; botão touch inventado (retocável): B5 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-bancada | 1:1 | gemini-3-pro-image | capa r1 | 4 | 3 | 0 | proporção: 1 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-bancada | 1:1 | kontext (Max) | capa r1 | 4 | 4 | 2 | 0 | publicaria: 1x1/B4 1x1/B15 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-bancada | 1:1 | seedream 4 edit | capa r1 | 4 | 2 | 0 | forma: 2 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-banheira | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 4 | 3 | 0 | publicaria: 1x1/C1 1x1/C7 1x1/C11 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-banheira | 1:1 | gemini-3-pro-image | capa r1 | 4 | 2 | 0 | proporção: 2 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-banheira | 1:1 | kontext (Max) | capa r1 | 4 | 4 | 0 | 0 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-banheiro-banheira | 1:1 | seedream 4 edit | capa r1 | 4 | 1 | 0 | forma: 3 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-close-base | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 3 | 1 | proporção: 1 | publicaria: 1x1/D6 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-close-base | 1:1 | gemini-3-pro-image | capa r1 | 4 | 0 | 0 | proporção: 2, forma: 2 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-close-base | 1:1 | kontext (Max) | capa r1 | 4 | 4 | 1 | 0 | publicaria: 1x1/D15 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-close-base | 1:1 | seedream 4 edit | capa r1 | 4 | 3 | 0 | forma: 1 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-papel-de-parede | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 3 | 2 | proporção: 1 | publicaria: 1x1/E3 1x1/E13; botão touch inventado (retocável): E13 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-papel-de-parede | 1:1 | gemini-3-pro-image | capa r1 | 4 | 4 | 0 | 0 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-papel-de-parede | 1:1 | kontext (Max) | capa r1 | 4 | 3 | 0 | proporção: 1 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-papel-de-parede | 1:1 | seedream 4 edit | capa r1 | 4 | 1 | 0 | forma: 3 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-penteadeira-quarto | 1:1 | gemini-2.5-flash-image | capa r1 | 4 | 3 | 0 | proporção: 1 | botão touch inventado (retocável): F2 F5 F6 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-penteadeira-quarto | 1:1 | gemini-3-pro-image | capa r1 | 4 | 1 | 0 | cópia do produto: 3 | — |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-penteadeira-quarto | 1:1 | kontext (Max) | capa r1 | 4 | 4 | 2 | 0 | publicaria: 1x1/F3 1x1/F9 |
| 2026-10-01 | Classique Lux cromado ligado (10202CR) | mesa-penteadeira-quarto | 1:1 | seedream 4 edit | capa r1 | 4 | 3 | 0 | cabo: 1 | — |

## Calibragem do agente

Uma linha por imagem em que o agente e o Thiago discordaram, ou que serve de
âncora para o critério.

| Data | Imagem | Agente | Thiago | Motivo do Thiago | Mudança no critério |
|---|---|---|---|---|---|
| premissas (resposta 2) | `benchmark-ml/10202CR/10202CR-4` | — | publicaria | fidelidade do produto; o logo "geroie" e o cabo fora de vista não impedem | âncora: cabo ausente na vista frontal e grafia do logo não são veto (critérios d e g) |
| 2026-10-01 | `1x1/B5`, `1x1/E13` (gemini-2.5-flash-image) | veto a (botão touch inventado no vidro) | publicaria, com o botão apagado | o botão é defeito local; tamanho e formato estão entre os melhores do lote | critério a2 criado: botão ou ícone touch inventado no vidro é CORRIGIR SE DER |
| 2026-10-01 | `1x1/A3`, `1x1/A13` (kontext) | 1ª leitura: veto i (anel descentrado na horizontal); refeito na vertical: passa | publicaria | entre os melhores em tamanho e formato | âncora: medir a largura do difusor na vertical; na horizontal o vidro claro se confunde com o difusor (passo 4) |
| 2026-10-01 | as 50 que o agente aprovou fora da lista do Thiago (kontext 15, seedream 14, gemini-3-pro 12, gemini-2.5-flash 9) | passa | removeria | não detalhado: ficaram fora das melhores em tamanho e formato | PENDENTE: o agente não achou a medida que separa as 17 escolhidas das 50 (as notas "no limite" aparecem em 24% das escolhidas e 26% das removidas). Pedido ao Thiago o motivo em 3 pares de exemplo |
| 2026-10-01 | reflexo (h): A1 A5 A6 A11 A14, B4 B8 B9 B12 B14, C2 C5 C6 C12, D1, E9 E10 E15, F11 F16 | — | melhores em reflexo | — | âncora de reflexo bom (h); C12, F11 e F16 seguem vetadas por i, l e e |
