#!/bin/bash
# Lote v4 (24/10): anel uniforme (jateado emissivo), 5 acabamentos com cromado, 3 vistas,
# aceso e apagado na mesma amostragem, e os 3 tons do padrão de anel de luz de 22/10.
# Rodar na pasta do estudo: bash ferramentas/lote_v4.sh
set -u
cd "$(dirname "$0")/.."
PY=venv/bin/python
COMUM="--prata-diam 150 --aro-largura 10 --anel-emissao 1.0"
declare -A MODELO=( [frente]=Fechado [tres-quartos]=Fechado [braco-aberto]=Esticado )
declare -A CAM=(
  [frente]="--azimute 4 --elevacao 3"
  [tres-quartos]="--azimute 35 --elevacao 6"
  [braco-aberto]="--azimute 55 --elevacao 8 --halo 90 --halo-forca 0.8 --halo-alvo -0.10 --halo-lado 0.30"
)
VISTAS="${VISTAS:-frente tres-quartos braco-aberto}"
ACABS="${ACABS:-cromado brushed-nickel gold red-gold black-matte}"
for v in $VISTAS; do
  d=renders/v4/$v; mkdir -p $d/tons
  glb=modelo/lumiere-${MODELO[$v]}.glb
  [ -f $d/silhueta.png ] || $PY -I ferramentas/render_lumiere.py $glb $d/silhueta.png --silhueta ${CAM[$v]} $COMUM --amostras 16 > $d/log-silhueta.txt 2>&1
  for a in $ACABS; do
    for estado in aceso apagado; do
      out=$d/lumiere-$a-$estado.png
      [ -f $out ] && continue
      led=1; [ $estado = apagado ] && led=0
      $PY -I ferramentas/render_lumiere.py $glb $out --acabamento $a --led $led ${CAM[$v]} $COMUM > $d/log-$a-$estado.txt 2>&1
      echo "$(date +%H:%M) $v $a $estado $(tail -c 300 $d/log-$a-$estado.txt | grep -o '"render_s": [0-9.]*')"
    done
    for t in 3000 4500 6000; do
      $PY -E -s ferramentas/luz_padrao.py $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png $t $d/tons/lumiere-$a-$t.png > /dev/null 2>&1 || echo "falhou tom $v $a $t"
    done
  done
done
echo FIM
