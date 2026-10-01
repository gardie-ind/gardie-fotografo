# Referências de produto

Índice do que existe aqui. As regras de uso ficam em `guia/` (identidade e
capa em `guia/prompts.md`; fatos de produto em `guia/produto.md`).

| Pasta | O que tem | Uso |
|---|---|---|
| `catalogo/` | stills de estúdio em fundo cinza, uma por modelo e acabamento; os modelos com LED têm versão ligado e desligado | identidade do produto: é daqui que o `ensaio.py` prepara a capa |
| `capa/` | capas já preparadas e conferidas (criada no primeiro lote) | reutilizar com `--sem-preparo` |
| `classique-lux/` | fotos reais: frontal desligado, frontal 4500K e 6000K, lateral, diagonal (×2), traseira com cabo, virado para cima; `IMG_0858/0891/1039/1151.jpg` (produto em uso por modelo); `frames-video/` | apoio: traseira, rota do cabo, escala com pessoa |
| `royale-lux/` | ligado, desligado e o cabo na base (entrada no topo, saída na traseira) | apoio: rota do cabo dos modelos de mesa com LED |
| `visage-lux/` | cabo saindo da traseira da cabeça | apoio: cabo dos modelos de parede com LED |
| `flex-lux/` | ligado, desligado e uma foto real | apoio |
| `flex/`, `beaute/`, `miroir/`, `royale-cristal/` | fotos reais desses modelos | apoio |
| `chicote-eletrico/` | plug solto, plug na tomada e o desenho com as medidas do plug | conferir o plug quando ele aparece |
| `videos/` | vídeos reais dos modelos com LED em uso | extrair quadros quando um detalhe só aparece em movimento |
| `benchmark-ml/` | fotos geradas pelo "Gerar fotos com IA" do Mercado Livre | padrão de qualidade e de ambiente; **nunca** referência do produto |

Foto de celular, imagem gerada por IA e imagem retocada nunca são a
referência principal: elas só apoiam detalhes que a still não mostra.
