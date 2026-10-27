#!/bin/bash
# Lote v7 (27/10, Thiago: "Consegue fazer algumas posições mostrando a traseira do espelho?"):
# cromado, 4500K, realismo do v5, como o v6. A cabeça gira no pino da articulação (--cabeca), só até
# 90° em relação ao braço da cabeça, que é o giro que o próprio CAD mostra entre fechado e esticado.
# Câmeras até 55° de lado: a 70° ou mais a parede longe do foco ficava preta.
# Rodar na pasta do estudo: bash ferramentas/lote_v7.sh   (VISTAS="t01 t02" para parte do lote)
set -u
cd "$(dirname "$0")/.."
PY=venv/bin/python
COMUM="--prata-diam 150 --aro-largura 10 --anel-emissao 1.0 --realismo --parede 0.13 --halo 90 --halo-forca 0.8 --halo-alvo -0.10 --halo-camera 1.0 --diafragma 22"
# vista: braço (t1,t2), giro da cabeça, azimute, elevação, estúdio subido (câmera alta, como a p09)
declare -A POSE=(
  [t01]="0,360 90 -55 8 0"   [t02]="0,360 90 -35 12 0"   [t03]="20,270 270 55 8 0"
  [t04]="30,270 270 40 15 0" [t05]="0,360 90 -50 22 16"  [t06]="15,345 75 -50 -5 0"
)
VISTAS="${VISTAS:-t01 t02 t03 t04 t05 t06}"
a=cromado; t=4500
for v in $VISTAS; do
  read braco cab az el inc <<< "${POSE[$v]}"
  CAM="--braco $braco --cabeca $cab --azimute $az --elevacao $el --estudio-inclina $inc"
  d=renders/v7/$v; mkdir -p $d/tons $d/final
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
  $PY -I ferramentas/foto.py $d/tons/lumiere-$a-$t.png $d/final/lumiere-$a-$t.png 2${v#t} \
    $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png > /dev/null || echo "falhou foto $v"
done
echo FIM
