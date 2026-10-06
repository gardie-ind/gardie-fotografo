# ferramentas/ — scripts do Fotógrafo da Gardie

Python 3, com Pillow e numpy. No Windows: `PYTHONUTF8=1 py <script> ...`; no Linux: `python3 <script> ...`.
Credenciais ficam fora do repositório. Vale a variável de ambiente ou o arquivo:

| Serviço | Variável | Arquivo |
|---|---|---|
| Gemini | `GEMINI_API_KEY` | `~/.config/gardie/gemini.json` → `{"api_key": "...", "image_model": "..."}` |
| fal.ai | `FAL_KEY` | `~/.config/gardie/fal.json` → `{"api_key": "..."}` |
| Shopify | `SHOPIFY_*` | `~/.config/gardie/shopify.json` (detalhes em `shopify_auth.py`) |

## Scripts

- **`ensaio.py`**: ensaio no estilo do "Gerar fotos com IA" do Mercado Livre. Ele padroniza a referência como capa (fundo branco puro, quadrada, produto inteiro com ~93% do lado, 1536 px) e monta o prompt pela moldura (`{produto}` + `{cena}`, sem descrever o produto). Depois roda cada motor `--n` vezes por receita e grava, por receita, a prancha CEGA (`prancha-<receita>.png`, com a REF na 1ª célula e os rótulos A1, A2… embaralhados), além de `mapa.json` (rótulo → motor) e `manifesto.json` (prompt exato, refs, parâmetros, falhas e custo estimado).
  - Primeiro passo de todo ensaio: `--so-preparo`, e abrir (Read) `refs/ref-1-conferencia.png` antes de gastar API.
  - `--simular` roda o fluxo inteiro sem API. As imagens fictícias mostram o motor de propósito, para conferir o `mapa.json`.
  - `--listar-modelos` mostra os modelos Gemini que geram imagem com esta chave.
  - Motores: `gemini:<model-id>`, `kontext` (FLUX Kontext Max, usa só a 1ª ref) e `seedream` (Seedream 4 edit, aceita várias refs).
  - Se uma geração falhar, as outras seguem; erros transitórios (429/5xx/rede) têm 1 nova tentativa.
  - Saída padrão: `ensaios/_versoes/<data>-<slug-do-produto>/`.
  - Não abrir `mapa.json` antes do veredito.
- **`gerar_imagem.py`**: uma chamada ao Gemini (texto + refs; as imagens vão antes do texto). `gerar(prompt, out, refs, aspect, model)`.
- **`estudio_fal.py`**: fal.ai. Re-render por referência (`rerender_kontext`, `rerender_seedream` com várias refs) e retoque LOCAL por máscara (`recortar` BiRefNet, `mascara-fundo`, `fundo` FLUX Fill, `relight`). Máscara serve só para defeito local, nunca para criar cena.
- **`inspecao_imagem.py`**: `diff` (a edição mudou algo? <2% = falhou), `crops` (quadrantes em resolução nativa) e `grade` (grade rotulada a cada N px, com zoom e recorte opcionais, para MEDIR proporções contra a referência).
- **`retoque_local.py`**: retoque local SEM IA para área lisa (vidro, parede): preenche a máscara a partir da borda e devolve o grão; pixels fora da máscara intocados. Uso em `guia/criterios.md` › Retoque.
- **`curva_vidro.py`**: warp geométrico do reflexo dentro do vidro, sem IA. É utilitário opcional de retoque.
- **`upload_shopify.py`** / **`shopify_auth.py`**: sobem imagens aprovadas para o Shopify Files e imprimem a URL CDN. Caminhos relativos também são procurados em `aprovadas/`.

## Exemplo

```
py ensaio.py --produto "Espelho de Aumento 5x com Luz LED de Mesa Gardie Classique Lux Cromado" ^
  --ref ../referencias/catalogo/espelho-de-aumento-com-ring-light-5X-cromado-gardie-classique-lux-ligado-em-fundo-cinza.jpg ^
  --so-preparo
py ensaio.py --produto "..." --ref <a mesma> --receitas ../receitas --n 6 --aspecto 1:1
```

## Limites conhecidos do preparo local (`--recorte local`, padrão)

O preparo local não usa API: modelo do fundo de estúdio + inundação + remoção de sombra. Ele nunca altera pixels do produto, só troca o fundo. Na dúvida, mantém o pixel como produto.

- Sombra de contato rente ao pé de borracha pode deixar uma franja fina e suave.
- Sombra de contorno nítido projetada na parede (Flex, Doubler, às vezes Mobile) fica como mancha cinza.
- Foto que não é de estúdio (mesa, parede: as de `referencias/classique-lux/`) ou produto cortado pelo quadro: o preparo RECUSA, porque o recorte encosta na borda da foto (hoje também Beaute branco e Svelte do catálogo). No `--simular`, a ref recusada segue crua, só para testar o fluxo.
- Produto branco em fundo claro pode sair em pedaços (Vide branco): vem AVISO "recorte suspeito".

Nesses casos, use `--recorte birefnet` (fal), ou passe um PNG já recortado com transparência (o alfa do arquivo é usado direto). Confira sempre a conferência.
