# Verificação · alça do cabo nas fotos ambientadas do Classique Lux em uso · 2026-10-16

Pedido do Thiago (2026-10-16): "Vamos continuar arrumando as fotos dos
produtos LUX, colocando o cabo elétrico."

As 4 fotos ambientadas do Classique Lux cromado (10202CR) que estão em uso
(lista de não apagar do Shopify) têm o cabo na bancada, mas não têm a alça da
traseira da cabeça até o topo do pivô, que aparece no vão de 3/4
(`guia/produto.md` › Cabo e plug; `placar.md` › Calibragem, 2026-10-12). Esta
rodada só acrescenta a alça. Nada mais na foto mudou.

## O que preciso de você

1. **Veredito nas 4:** quais você publicaria com a alça.
2. **Cabo da bancada antigo** (ver Notas): fica como está ou eu troco pelo
   cabo real?

## Fotos

| Rótulo | Original (gardie-marketing, `marca/imagens-ml-corrigidas/10202CR/`) | Final |
|---|---|---|
| CR1 | `espelho-de-aumento-bancada-led-classique-lux-cromado-gardie-1.png` | `CR1-com-alca.png` |
| CR2 | `espelho-de-aumento-bancada-led-classique-lux-cromado-gardie-2.png` | `CR2-com-alca.png` |
| CR3 | `espelho-de-aumento-bancada-led-classique-lux-cromado-gardie-3.png` | `CR3-com-alca.png` |
| CR4 | `espelho-de-aumento-bancada-led-classique-lux-cromado-gardie-4.png` | `CR4-com-alca.png` |

Prancha: `prancha-entrega-alca-classique-lux.png` (antes e depois, com o
trecho ampliado em 3×).

## Método

- **Rota:** a que o Thiago marcou na `1x1-piloto/A1` (aprovada), ancorada no
  centro do topo do pivô e escalada pela largura do disco da base (CR1 355 px,
  CR2 354, CR3 322 e CR4 425, contra 375 na A1). Na CR2 a rota foi espelhada:
  a espessura do aro aparece à esquerda, então a traseira da cabeça fica
  desse lado. Nas outras três ela fica à direita, como na A1. O lado bate com
  a saída do cabo da bancada em cada foto.
- **Cabo:** `ferramentas/cabo_real.py`, modo suspenso, sem IA. Largura de
  5 mm na escala da base (7,7 a 10,2 px). Brilho e tinta pelo fundo do vão de
  cada foto, na mesma relação da alça da A1.
- **Máscara do vão** (onde o cabo passa na frente): preenchimento a partir de
  sementes no fundo, com faixa fixa, e crescimento por coluna até a primeira
  borda forte (cabeça, garfo ou pivô), sem IA, porque o recorte do fal está
  sem saldo (`mascaras/<rótulo>-visivel.png`). Na CR4 o crescimento foi só
  para baixo, porque a borda de baixo da cabeça é suave.

## Conferência

- Em 8×, a alça surge de trás da borda de baixo da cabeça, sem ponto de saída
  à vista, e entra no topo do pivô por cima. Na CR4 ela some atrás da raiz do
  braço direito do garfo, logo acima do pivô.
- Em 1× e 2×, ela se lê como cabo branco fino nas 4.
- `inspecao_imagem.py diff`: 0,000% de pixels alterados fora da máscara do
  cabo nas 4. No produto, só a borda suave do vão mudou (20 a 25 px por foto).

## Notas (não mexi)

O cabo da bancada dessas fotos veio do processo antigo e, pelo critério e
(`guia/criterios.md`: branco, fino, sem conector inventado), tem problemas:

- **CR1:** o cabo termina num objeto cinza tipo plugue, ao lado do cilindro
  branco à direita;
- **CR2:** o cabo é uma fita cinza achatada com uma faixa branca embaixo, não
  um cabo redondo branco;
- **CR4:** uma marca escura atravessa o cabo na volta à direita, como uma
  braçadeira.

Trocar o cabo da bancada pelo real exige apagar o antigo da bancada, o que
pede preenchimento (IA ou clonagem). Fica para a sua decisão.
