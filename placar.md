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

## Calibragem do agente

Uma linha por imagem em que o agente e o Thiago discordaram, ou que serve de
âncora para o critério.

| Data | Imagem | Agente | Thiago | Motivo do Thiago | Mudança no critério |
|---|---|---|---|---|---|
| premissas (resposta 2) | `benchmark-ml/10202CR/10202CR-4` | — | publicaria | fidelidade do produto; o logo "geroie" e o cabo fora de vista não impedem | âncora: cabo ausente na vista frontal e grafia do logo não são veto (critérios d e g) |
| 24/10 | `lotes/2026-10-21-lumiere-cad/frente-prototipo` (8 quadros, Lumière do CAD, anel aceso pela luz dos LEDs da placa) | entregue como aprovado | vetaria | "A luz deve ficar uniforme, ela não fica com estas sombras internas" | checagem medida de anel aceso por igual em `guia/criterios.md` passo 6 (VETO acima de 8%; os vetados davam 11 a 36%) |
| 25/10 | `lotes/2026-10-21-lumiere-cad/v4-anel-uniforme` (60 quadros) | aprovado | aprovou a direção ("Você acertou") e pediu tirar o aspecto de render | realismo, não fidelidade do produto | nenhuma ainda: realismo não tem medida; o v5 refaz os 60 com estúdio refletido e acabamento de câmera |
| 02/11 | Lumière red gold em 3 banheiros das referências do Thiago (refs 41, 78 e 90), contexto 4:5 (`r?c`: produto a 23–26% da altura, com cuba e torneira) | aprovado pelo agente | não publicaria | "O contexto da foto não ficou bom" (19:44), com as fotos geradas pelo ML como referência de composição e a regra de produzir toda foto em 1:1 primeiro, para o Shopify | formato 1:1 primeiro; composição medida em "Lumière no ambiente" (passo 4 de `guia/criterios.md`) |
| 02/11 | os mesmos 3 refeitos em 1:1 no estilo ML (`r?q`: corte na base da cuba, torneira cortada em 22 cm) | aprovado pelo agente | não publicaria | "Você continua instalando o espelho muito alto na parede" e, no mármore claro e no ondulado, "a montagem do espelho esconde um dos braços" (22:03); altura corrigida às 22:06 para 1,4 a 1,5 m do chão; "mexa-o-braço" passa a pedir outra pose | "Lumière no ambiente" (passo 4): centro do espelho a 1,4–1,5 m, torneira de 30 cm logo abaixo, braços sem esconder um ao outro |
| 03/11 | os 3 refeitos nos cortes do Thiago (`r?p`, 1:1, braços em outra pose), entrega de 23:50 | aprovado pelo agente | método aprovado ("Ficaram ótimas! Você entendeu!", 00:13), mas "Eu estou vendo uma alteração do tom do ambiente nas fotos" (00:15) | a ampliação pelo Gemini deixou a parede mais rosa e mais fria (a* +1,1 a 1,7, b* até −1,6, ΔE até 2,1) | "Lumière no ambiente" (passo 4): tom da sala casado sem IA com o recorte original, VETO acima de ΔE 1,0 |
| 03/11 | `espelho-de-aumento-parede-led-lumiere-red-gold-gardie-16` a `-18` (refs 41, 78 e 90, 1:1, acesas em 4500K, tom casado), no Shopify desde 03/11 20:24, fora do git (repositório público) | aprovado: metal 66–69°, anel L* 99, Lumière a 49–59% da altura do quadro | publicaria ("aprovada, pode subir para o Shopify", 20:14) | — | âncora das faixas de "Lumière no ambiente" |
| 04/11 | `espelho-de-aumento-parede-led-lumiere-black-matte-gardie-16` e `-17` (refs 66 mármore branco e 77 mármore cinza, 1:1, acesas em 4500K), no Shopify desde 04/11 01:05 nas posições 39 e 40, fora do git (repositório público) | aprovado: metal sem o espelho L* 5,1 e 1,6, croma 1,3 e 0,3, anel L* 99, Lumière a 53% da altura do quadro; o 77 entregue com a ressalva de estar abaixo da faixa L* 4–9 das stills black matte | publicaria ("Aprovado, pode subir para o shopify", 00:58, nas duas acesas; as apagadas não) | — | "Lumière no ambiente": black matte aceito de L* 1,6 a 9 |
