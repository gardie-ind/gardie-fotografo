# Cena

## Direção

- **Alvo visual:** `referencias/benchmark-ml/10202CR/`. O ponto forte do ML é
  a fidelidade do produto: é esse o nível a alcançar. Os ambientes dele são o
  padrão de ambiente (elegantes, com pouca informação, muito bonitos, com o
  produto como protagonista), nunca a referência do produto.
- **Liberdade criativa no ambiente.** A direção do Thiago: elegante, pouca
  informação, muito bonito, como os do ML. Preferências do agente (padrão —
  confirmar com o Thiago): claro, com luz natural; contemporâneo, minimalismo
  de luxo (pedra clara, porcelanato grande, metais foscos, linhas limpas);
  evitar rústico, casa de campo e madeira pesada; poucos objetos de cena.
- **Lugar coerente com a montagem e com o uso seguro** (`guia/produto.md`):
  - mesa vai em bancada, penteadeira ou aparador; parede, na parede de
    banheiro ou lavabo, na altura de uso; ventosa, no azulejo ou no vidro do
    box;
  - LUX nunca dentro do box nem em contato com água (risco de choque); só os
    modelos sem LED vão ao box, e o Vide foi projetado para isso;
  - nenhum espelho com sol direto no vidro: o côncavo concentra a luz e pode
    causar incêndio.
- **Luz perto do produto:** luz do dia, neutra. Luz âmbar forte faz o cromado
  parecer dourado.
- **Escala:** pelo menos um objeto de tamanho conhecido perto do produto, no
  mesmo plano (torneira, frasco, toalha dobrada, gaveta). É com ele que se
  confere a escala (`guia/criterios.md`, passo 4). Os closes dispensam.
- **Pessoas, texto e marcas:** frascos e cosméticos sem rótulo. Nada de
  pessoas, rostos, texto ou marcas de terceiros, salvo pedido do Thiago. O
  logo do produto faz parte do produto.
- **Tomada:** prefira cenas sem tomada à vista.

## Cenas com pessoa (só quando o Thiago pedir)

A modelo é uma mulher elegante, 35+, de aparência cuidada e roupa neutra e
discreta, sem semelhança com nenhuma pessoa real ou celebridade. As
referências obrigatórias são `classique-lux/IMG_0858`, `IMG_0891`,
`IMG_1039`, `IMG_1151` e `classique-lux/frames-video/` (o frame de 8 s é o
alvo). Nelas se confere a distância menor que 60 cm, o reflexo do rosto
direito e ampliado e a escala produto × rosto.

## Física do reflexo (corrigir se der)

É julgada no resultado e nunca descrita no prompt. Vale para a face de
aumento; a face normal dos modelos dupla-face reflete plano, direito e sem
ampliação.

- **Além de ~60 cm**, o espelho côncavo (foco de 60 cm) mostra o ambiente
  invertido, de cabeça para baixo, suave, desfocado e levemente curvo.
  Curvatura de olho de peixe total é exagero.
- **Rosto a menos de 60 cm:** aparece direito e ampliado.
- **O que o vidro mostra:** o que está à frente do espelho (o lado da câmera e
  acima). Nunca elementos visíveis no próprio quadro, nunca outro cômodo,
  nunca o próprio anel de luz ou o produto.
- Um reflexo cinza, simples e suave é aceitável.

## Formatos por canal

As fotos servem a todos os canais possíveis. Canal novo: acrescente a linha
com a especificação oficial do canal.

- **Proporção:** sempre pelo parâmetro da API (`--aspecto` no `ensaio.py`),
  nunca no texto. Se o motor não oferece a do canal, gere na mais próxima e
  recorte sem cortar o produto (exceto em close).
- **Resolução abaixo da recomendada:** anote. Só amplie depois de combinar com
  o Thiago, porque ampliador generativo também redesenha detalhes.

| Canal | Proporção | Recomendado | Observação |
|---|---|---|---|
| Mercado Livre | 1:1 | 1200 × 1200 (mínimo 500) | capa: ver a seção seguinte |
| Página de produto (Shopify) | 1:1 | 2048 × 2048 | confirmar com o tema da loja |
| Blog (corpo de artigo) | 16:9 | 1600 × 900 | |
| Pinterest | 2:3 | 1000 × 1500 | |
| Instagram e Facebook, feed (orgânico e anúncio) | 4:5 e 1:1 | 1080 × 1350 e 1080 × 1080 | |
| Instagram e Facebook, Stories e Reels | 9:16 | 1080 × 1920 | produto fora dos 14% de cima e de baixo |
| Google, anúncio de imagem | 1,91:1 e 1:1 | 1200 × 628 e 1200 × 1200 | |
| Google Merchant, imagem principal | 1:1 | 1200 × 1200 | capa em fundo branco |
| Catálogo do WhatsApp Business | 1:1 | 1080 × 1080 | confirmar a especificação oficial |
| E-mail | 16:9 ou 1:1 | 1200 de largura | |
| Outros marketplaces | 1:1 | o da plataforma | imagem principal em fundo branco; confirmar com o Thiago onde a Gardie vende |
| Banner do site | a do template do tema | | |

**Capa branca e foto ambientada:** a capa em fundo branco vale para a capa do
Mercado Livre, a página de produto e a imagem principal do Google Merchant e
dos marketplaces. No blog, no Pinterest, nas redes e nos anúncios de imagem,
só foto ambientada.

## Capa do Mercado Livre

**Categoria:** pesquise nos anúncios da Gardie no ML (busca "gardie" em
mercadolivre.com.br; a categoria está no breadcrumb do anúncio ou, pela API,
em `items/<MLB…>` → `category_id` → `categories/<id>` → `path_from_root`) e
registre abaixo, por código, com o link e a data da consulta. Indício: o
"Gerar fotos com IA" do ML gerou fundo ambientado dentro do anúncio da
10202CR. Pergunte ao Thiago só se a pesquisa não for conclusiva ou se a rede
da sessão bloquear o ML.

| Código | Categoria | Link | Consulta |
|---|---|---|---|
| 10202CR | a pesquisar | | |

| Categoria | Regra da capa |
|---|---|
| Casa, Móveis e Decoração | Pode ser ambientada: produto inteiro, de frente, centralizado, bem iluminado, sem texto, logo extra ou marca d'água. Completa-se com fotos em fundo branco (frente, lados, closes). |
| Beleza e Cuidado Pessoal | Fundo branco puro (RGB 255,255,255), produto inteiro, sem sombra dura, sem texto. |

**Enquanto a categoria não for registrada:** todo lote entrega, além do
ensaio ambientado, a capa em fundo branco. Ela é a capa usada no lote:
`refs/ref-1-capa.png` quando o ensaio preparou a capa, ou o arquivo de
`referencias/capa/` quando rodou com `--sem-preparo`. Pixels reais, sem
geração. Antes de publicá-la, confira a máscara em 100% (sem buraco no
cromado).
