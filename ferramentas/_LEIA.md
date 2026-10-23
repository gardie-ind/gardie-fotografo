# ferramentas/ — scripts do Fotógrafo da Gardie

Python 3, com Pillow e numpy. No Windows: `PYTHONUTF8=1 py <script> ...`; no Linux: `python3 <script> ...`.
Credenciais ficam fora do repositório. Vale a variável de ambiente ou o arquivo:

| Serviço | Variável | Arquivo |
|---|---|---|
| Gemini | `GEMINI_API_KEY` | `~/.config/gardie/gemini.json` → `{"api_key": "...", "image_model": "..."}` |
| fal.ai | `FAL_KEY` | `~/.config/gardie/fal.json` → `{"api_key": "..."}` |
| Google Drive (backup) | `N8N_BACKUP_TOKEN` | — (o envio passa pelo n8n; o token está no filtro do webhook do fluxo) |
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
- **`inspecao_imagem.py`**: `diff` (a edição mudou algo? <2% = falhou), `crops` (quadrantes em resolução nativa), `grade` (grade rotulada a cada N px, com zoom e recorte opcionais, para MEDIR proporções contra a referência) e `colagem` (NCC entre um trecho cromado da capa e o mesmo trecho da candidata: alto = reflexo da capa colado na cena, item h2).
- **`curva_vidro.py`**: warp geométrico do reflexo dentro do vidro, sem IA. É utilitário opcional de retoque.
- **`cabo_real.py`**: desenha o cabo branco do espelho na rota real (sai de trás da base e corre rente à bancada), sem IA, com o perfil medido num cabo aprovado. O produto passa na frente (alfa do recorte do `estudio_fal.py recortar`) e sai com 0 pixel alterado. Com `"suspenso": true`, desenha a alça no ar, da traseira da cabeça ao topo do pivô, como um cilindro iluminado pela luz da cena, só no vão em que ela passa na frente do fundo. `python3 cabo_real.py foto.png recorte.png rota.json saida.png`; o formato do `rota.json` está na docstring.
- **`acabamentos.py`**, **`escovado.py`** e **`medir_escovado.py`**: acabamentos por recoloração da still cromada, sem IA (`guia/produto.md` › Acabamento por recoloração). `acabamentos.py` faz gold, red gold e black matte; `escovado.py`, o brushed nickel (`recolorir_nk`); `medir_escovado.py <png> <w-met-k.npy>` mede riscado e borda do reflexo para o item b de `guia/criterios.md`. Os pesos de metal por pixel e o recorte de cada modelo saem do pipeline em `/mnt/project-files/fotografo/2026-10-21-acabamentos/ferramentas/` (`recortar.py`, `acabamento_modelo.py`).
- **`medir_acabamento.py`**: medidas do item b de `guia/criterios.md`. `tom` dá matiz e croma do metal por faixa de L* (red gold contra a peça real de `referencias/red-gold/`; aceita foto de celular em Display P3, `--papel` e `--mascara`). `carcaca <ligada> <desligada>` dá a parte do produto fora da cabeça acima de 180 de luminância (black matte com a carcaça pintada). **`novo_tom.py`** refaz a tabela do red gold da peça real a partir da Deca de 21/10.
- **`luz_padrao.py`** (com **`luz_anel.py`**): o padrão de luz "meio termo" dos LUX, sem IA (`guia/produto.md` › Padrão de luz). A luz do LED é a diferença entre a still ligada e a apagada, recolorida por Planck nos 3 tons (`RENDER`: 3000K = render 4500K, 4500K = 5150K, 6000K = 6000K).
- **`logo_laser.py`**, **`lote_logo.py`**, **`prancha_logo.py`**, **`verificar_logo.py`** e **`medir_contraste_logo.py`**: o logo gravado a laser no espelho, pelo desenho `logo-laser/E-0001-V1.pdf` (máscara em `logo-laser/`). `logo_laser.py` tira o logo impresso da borda jateada e grava o novo num par ligada e apagada; `lote_logo.py` faz um LUX nos 5 acabamentos com logo e luz nos 3 tons (fontes e cuidados na docstring: não rode sobre as aprovadas atuais); `verificar_logo.py` confere que nada mudou fora da luz do LED e dos logos e que o impresso sumiu; `prancha_logo.py` monta a prancha; `medir_contraste_logo.py` mede o traço do logo contra o vidro.
- **`backup_drive.py`**: backup de `aprovadas/` no Google Drive, em imagens › Cloud › aprovadas (drive compartilhado do marketing), pelo fluxo "Fotógrafo: backup das fotos no Drive" do n8n da Gardie, que usa o login do Google Drive de lá. Pastas em `drive-cloud-pastas.json`; o que já subiu, com o MD5 conferido, em `drive-cloud-enviados.json`. Precisa de `N8N_BACKUP_TOKEN` (o token do filtro do webhook, lido no fluxo) e de `n8n.gardie.com.br` liberado na rede da sessão; `--simular` só lista. O fluxo fica desligado entre um backup e outro: ligue (publicar) no n8n antes e desligue depois. Primeiro backup: 23/10/2026, 105 arquivos, 583 MB.
- **`upload_shopify.py`** / **`shopify_auth.py`**: sobem imagens aprovadas para o Shopify Files e imprimem a URL CDN. Caminhos relativos também são procurados em `aprovadas/`. O lote das 100 stills LUX de 22/10/2026 está pronto em `shopify-lote-2026-10-22-lux.json` (`--lote`).

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
