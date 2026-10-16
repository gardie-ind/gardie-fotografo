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
| 2026-10-11 | Classique Lux cromado (10202CR), ligado | mesa-banheiro-bancada | 1x1-piloto | Kontext Max | capa r1, 1 ref | 4 | 3 | 2 (A1, A4) | proporção (i): 1 (A3) | A1 e A4: "o cabo elétrico faz falta"; cabo real acrescentado no retoque (bancada em 2026-10-11, alça cabeça → pivô em 2026-10-12) |
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
| 2026-10-11 | `1x1-piloto/B5` e `1x1-piloto/B7` | escolhidas para o close | não usaria | "o jogo de luzes muito artificial, parece uma colagem" (2026-10-12) | h2 (nova): o cromado repete o reflexo da capa, medido por `inspecao_imagem.py colagem` (NCC do detalhe do miolo do sino); NCC ≥ 0,32 = VETO. No lote, as cópias da capa: B7 0,84, B5 0,83, B3 0,79, A2 0,58, B1 0,49, A6 0,40; A1 0,20 e A4 0,21; as demais, 0,21 a 0,25 |
| 2026-10-12 | `1x1-piloto/A1` e `1x1-piloto/A4`, com o cabo da bancada | cabo só na bancada | cabo da base correto; falta o trecho espelho → base | "O cabo sai do espelho e se conecta com a base … de forma escondida (não aparente), e entra na base por cima" (marcou a rota na A1) | d2 e `guia/produto.md` › Cabo e plug: de 3/4, com vão entre a cabeça e o pivô, a alça da traseira da cabeça ao topo do pivô aparece e entra no retoque |
| 2026-10-16 | stills de catálogo LUX cromado com o cabo real (S1 a S10: Mobile, Flex, Visage, Classique e Royale Lux, ligado e desligado) | aprovadas; nas de mesa, cabo saindo de trás da base para a direita e alça escondida atrás da cabeça | publicaria as 10, sem subir ao Shopify por enquanto | "Pode publicar todas, mas não vai para o Shopify, por enquanto fica no repositório para outros materiais" | nenhuma; âncora de d2 e e nas stills de estúdio. Em `aprovadas/`: 10455CR, 10554CR, 10509CR e 10288CR -1 (ligado) e -2 (desligado); 10202CR -3 (ligado) e -4 (desligado) |
| 2026-10-16 | 10202CR gardie-4 em uso (processo antigo), com a alça cabeça → pivô (CR4) | alça aprovada; o cabo antigo da bancada ficou fora do retoque, com a marca escura de braçadeira na volta apontada (e) e a pergunta se trocava pelo cabo real | publicaria e canonizaria | "CR1 e CR4 estão excelentes, eu publicaria no Shopify e canonizaria elas"; depois, "Na verdade, ficaria só com a CR4" | e: defeito pequeno no trecho da bancada, longe do produto, passa a CORRIGIR SE DER. Versão canônica: `aprovadas/10202CR/` -2 |
| 2026-10-16 | 10202CR gardie-1, -2 e -3 em uso, com a alça (CR1, CR2 e CR3) | alça aprovada; a proporção não foi medida, porque as fotos já estavam em uso | não publicaria | "As outras 3 (CR1-2-3) parecem desproporcionais, fora da realidade" | i (razão nova): topo da cabeça → centro do pé ÷ disco, VETO acima de 1,82. CR1 1,85, CR3 1,87 e CR2 1,88, contra A1 1,77, CR4 1,79 e A4 1,80 (capa 1,68). O disco ÷ cabeça não pegou: 0,695 a 0,707, dentro dos ±10% da capa. E foto em uso que volta para retoque passa pelo checklist inteiro |
