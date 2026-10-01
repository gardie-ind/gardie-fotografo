# Fotógrafo da Gardie

Agente do Claude Code que faz, por IA, o ensaio fotográfico dos espelhos
Gardie. A foto de estúdio do espelho real entra como referência, e o espelho é
levado a ambientes decorados, como se um fotógrafo fizesse o ensaio no local.
Para usar, abra o Claude Code nesta pasta: a sessão já é o fotógrafo (veja
`CLAUDE.md`).

## Estrutura

- `CLAUDE.md`: identidade e processo do agente.
- `guia/`: regras vigentes. São quatro arquivos:
  - `produto.md`: verdade física do produto;
  - `criterios.md`: critérios de aprovação;
  - `cena.md`: direção de cena e canais;
  - `prompts.md`: como escrever o prompt.
- `receitas/`: a moldura do prompt e as cenas (`receitas/_LEIA.md`).
- `referencias/`: stills de catálogo, capas conferidas, fotos reais de apoio,
  vídeos e o benchmark do Mercado Livre.
- `ensaios/`: saída dos ensaios.
- `aprovadas/`: só imagens com o veredito "publicaria" do Thiago.
- `placar.md`: placar dos motores e calibragem do agente.

## Requisitos e credenciais

Python 3 com `pip install pillow numpy` (e `imageio-ffmpeg` para extrair
frames de vídeo).

As credenciais ficam fora do repositório, em `~/.config/gardie/` (no Windows,
`%USERPROFILE%\.config\gardie\`):

- `gemini.json`: `{"api_key": "...", "image_model": "..."}` (`image_model` é
  opcional; teste a chave com `ensaio.py --listar-modelos`)
- `fal.json`: `{"api_key": "..."}`
- `shopify.json`: `{"store": "...myshopify.com", "client_id": "...", "client_secret": "..."}`

Também é possível usar as variáveis de ambiente `GEMINI_API_KEY` e `FAL_KEY`.
No Shopify, as alternativas são `SHOPIFY_STORE`, `SHOPIFY_CLIENT_ID` e
`SHOPIFY_CLIENT_SECRET`, ou `SHOPIFY_ADMIN_TOKEN`.

## Rodar um ensaio

A partir da raiz do repositório:

```
py ferramentas/ensaio.py --produto "<título do anúncio>" --ref <capa> --sem-preparo --receitas <receitas compatíveis> --n 4 [--aspecto 4:5] [--saida <pasta do lote>/<aspecto>] [--simular]
```

No Windows, defina antes `PYTHONUTF8=1`. No Linux, use `python3`. Sem
`--motores`, rodam os candidatos de `guia/prompts.md`. O `ensaio.py` não
filtra por montagem: sem `--receitas`, ele roda a pasta inteira. Passe só as
receitas compatíveis com a montagem (`receitas/_LEIA.md`).

| Opção | O que faz |
|---|---|
| `--produto` | título do anúncio (preenche `{produto}`; regras em `guia/prompts.md`) |
| `--ref` | still de `referencias/catalogo/` (o script prepara a capa) ou capa de `referencias/capa/`, sempre com `--sem-preparo`; repetida, vira 2ª referência (o Kontext usa só a 1ª) |
| `--receitas` | pastas e/ou arquivos `.txt` de cena; a `_moldura.txt` é encontrada sozinha |
| `--motores` | `gemini:<modelo>`, `kontext`, `seedream`, separados por vírgula (`--listar-modelos` mostra os modelos Gemini de imagem) |
| `--n` | gerações por motor por receita (padrão 4) |
| `--aspecto` | proporção pedida à API, por exemplo 1:1, 4:5, 16:9 (padrão 1:1) |
| `--so-preparo` | só prepara e confere a capa, sem chamar API |
| `--simular` | fluxo inteiro sem API, com imagens fictícias |
| `--recorte birefnet` | recorte pelo fal, quando o recorte local falha |
| `--sem-preparo` | usa a referência como está (capa já conferida) |

Exemplo, conferindo a capa antes de gastar:

```
py ferramentas/ensaio.py --produto "Espelho de Aumento 5x com Luz LED de Mesa Gardie Classique Lux Cromado" --ref referencias/catalogo/espelho-de-aumento-com-ring-light-5X-cromado-gardie-classique-lux-ligado-em-fundo-cinza.jpg --so-preparo
```

Sem `--saida`, a saída vai para `ensaios/_versoes/<data>-<produto>/` (lote
com vários formatos: uma subpasta por formato, como no `CLAUDE.md`). Lá ficam
a capa e a conferência (`refs/`), as candidatas por receita, as pranchas
brutas, o `manifesto.json` e o `mapa.json` (rótulo → motor). Não abra o `mapa.json`
antes do veredito.

## Outras ferramentas

- `estudio_fal.py`:
  - `recortar` (BiRefNet), para o preparo da capa;
  - `fundo` (FLUX Fill com máscara), para retoque local;
  - chamadas avulsas ao Kontext e ao Seedream.
- `gerar_imagem.py`: chamada avulsa ao Gemini.
- `inspecao_imagem.py`:
  - `diff`, que detecta edição que não mudou nada;
  - `crops`, que gera recortes em resolução nativa;
  - `grade`, que desenha a grade rotulada, com recorte e zoom, para medir
    proporções.
- `upload_shopify.py`: sobe as imagens para o Shopify Files e imprime o link
  CDN.
- `curva_vidro.py`: curva o reflexo dentro do vidro, sem IA (retoque do item
  h de `guia/criterios.md`).

Se uma docstring divergir de `guia/`, vale o guia.

## Arquivos de trabalho

As pastas `_versoes/`, `_crops/` e `_descartados/` são material de trabalho:
ficam fora do git, e a limpeza segue o `CLAUDE.md`.
