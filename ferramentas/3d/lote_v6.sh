#!/bin/bash
# Lote v6 (25/10, Thiago: "Crie mais dez perfis diferentes, de braço meio aberto e angulos de câmera
# diferentes. Faça com um acabamento e uma luz só, para aprovação."): cromado, 4500K, realismo do v5.
# O braço é posado a partir do modelo Fechado (--braco t1,t2; ver posar() no render) e a cabeça
# fica de frente para fora da parede. Câmera do lado esquerdo (azimute negativo) leva o estúdio
# espelhado. O apagado é renderizado porque o padrão de luz e o vazamento do anel usam o par.
# Rodar na pasta do estudo: bash ferramentas/lote_v6.sh   (VISTAS="p01 p02" para parte do lote)
set -u
cd "$(dirname "$0")/.."
PY=venv/bin/python
COMUM="--prata-diam 150 --aro-largura 10 --anel-emissao 1.0 --realismo --parede 0.13 --halo 90 --halo-forca 0.8 --halo-alvo -0.10 --halo-camera 1.0 --diafragma 22"
# vista: braço (t1,t2), azimute, elevação
declare -A POSE=(
  [p01]="45,270 40 8"   [p02]="60,270 -35 10" [p03]="30,270 60 5"   [p04]="30,330 -50 8"
  [p05]="45,315 50 15"  [p06]="60,360 -25 4"  [p07]="60,300 25 -6"  [p08]="45,270 -60 12"
  [p09]="20,270 35 22"  [p10]="15,300 55 4"
)
# Câmera alta: o estúdio refletido sobe junto (p09 a 22°: sem isso a articulação do cromo lia preta,
# mediana 8/255; com o estúdio 16° acima, 132/255, como nas outras vistas).
declare -A EXTRA=( [p09]="--estudio-inclina 16" )
VISTAS="${VISTAS:-p01 p02 p03 p04 p05 p06 p07 p08 p09 p10}"
a=cromado; t=4500
for v in $VISTAS; do
  read braco az el <<< "${POSE[$v]}"
  CAM="--braco $braco --azimute $az --elevacao $el ${EXTRA[$v]:-}"
  d=renders/v6/$v; mkdir -p $d/tons $d/final
  glb=modelo/lumiere-Fechado.glb
  [ -f $d/silhueta.png ] || $PY -I ferramentas/render_lumiere.py $glb $d/silhueta.png --silhueta $CAM $COMUM --amostras 16 > $d/log-silhueta.txt 2>&1
  for estado in aceso apagado; do
    out=$d/lumiere-$a-$estado.png
    [ -f $out ] && continue
    led=1; [ $estado = apagado ] && led=0
    $PY -I ferramentas/render_lumiere.py $glb $out --acabamento $a --led $led $CAM $COMUM > $d/log-$a-$estado.txt 2>&1
    echo "$(date +%H:%M) $v $estado $(grep -o '"render_s": [0-9.]*' $d/log-$a-$estado.txt)"
  done
  $PY -E -s ferramentas/luz_padrao.py $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png $t $d/tons/lumiere-$a-$t.png > /dev/null 2>&1 || echo "falhou tom $v"
  $PY -I ferramentas/foto.py $d/tons/lumiere-$a-$t.png $d/final/lumiere-$a-$t.png 1${v#p} \
    $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png > /dev/null || echo "falhou foto $v"
done
echo FIM
