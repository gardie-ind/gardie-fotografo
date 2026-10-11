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
| 2026-10-11 | Classique Lux cromado (10202CR), ligado | mesa-banheiro-bancada | 1x1-piloto | Kontext Max | capa r1, 1 ref | 4 | 3 | 2 (A1, A4) | proporção (i): 1 (A3) | A1 e A4: "o cabo elétrico faz falta"; cabo real acrescentado no retoque |
| 2026-10-11 | Classique Lux cromado (10202CR), ligado | mesa-banheiro-bancada | 1x1-piloto | Seedream 4 | capa r1, 1 ref | 4 | 3 | 0 | proporção (i): 1 (A5) | A2 quase de frente |
| 2026-10-11 | Classique Lux cromado (10202CR), ligado | mesa-close-base | 1x1-piloto | Kontext Max | capa r1, 1 ref | 4 | 4 | 0 | 0 | nenhuma fez o close |
| 2026-10-11 | Classique Lux cromado (10202CR), ligado | mesa-close-base | 1x1-piloto | Seedream 4 | capa r1, 1 ref | 4 | 4 | 0 | 0 | só B5 e B7 fizeram o close, as duas com a luz de estúdio da capa |

## Calibragem do agente

Uma linha por imagem em que o agente e o Thiago discordaram, ou que serve de
âncora para o critério.

| Data | Imagem | Agente | Thiago | Motivo do Thiago | Mudança no critério |
|---|---|---|---|---|---|
| premissas (resposta 2) | `benchmark-ml/10202CR/10202CR-4` | — | publicaria | fidelidade do produto; o logo "geroie" e o cabo fora de vista não impedem | âncora: cabo ausente na vista frontal e grafia do logo não são veto (critérios d e g) |
| 2026-10-11 | `1x1-piloto/A1` e `1x1-piloto/A4` | escolhidas, sem nota | publicaria | "O cabo elétrico faz falta" | d2: LED aceso com o cabo fora de vista não é veto, mas vira corrigir se der, com o cabo real acrescentado no retoque |
| 2026-10-11 | `1x1-piloto/B5` e `1x1-piloto/B7` | escolhidas para o close | não usaria | a perguntar | — |
