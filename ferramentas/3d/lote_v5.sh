#!/bin/bash
# Lote v5 (25/10): o v4 aprovado pelo Thiago ("Você acertou") com o realismo pedido em seguida
# ("Agora remova o aspecto de render e faça mais realista"): --realismo (estúdio refletido,
# bordas arredondadas, microvariação, parede com textura e um pouco mais clara, como nas stills
# reais), f/16 (f/22 no braço aberto, para a placa não perder nitidez), e o acabamento de câmera
# (foto.py: vazamento de luz do anel no espelho, brilho de lente, vinheta, franja de cor, nitidez
# e grão) depois do padrão de luz.
# Rodar na pasta do estudo: bash ferramentas/lote_v5.sh
set -u
cd "$(dirname "$0")/.."
PY=venv/bin/python
COMUM="--prata-diam 150 --aro-largura 10 --anel-emissao 1.0 --realismo --parede 0.13"
declare -A MODELO=( [frente]=Fechado [tres-quartos]=Fechado [braco-aberto]=Esticado )
declare -A CAM=(
  [frente]="--azimute 4 --elevacao 3 --diafragma 16"
  [tres-quartos]="--azimute 35 --elevacao 6 --diafragma 16"
  [braco-aberto]="--azimute 55 --elevacao 8 --halo 90 --halo-forca 0.8 --halo-alvo -0.10 --halo-lado 0.30 --diafragma 22"
)
declare -A SEMENTE=( [frente]=1 [tres-quartos]=2 [braco-aberto]=3 )
VISTAS="${VISTAS:-frente tres-quartos braco-aberto}"
ACABS="${ACABS:-cromado brushed-nickel gold red-gold black-matte}"
for v in $VISTAS; do
  d=renders/v5/$v; mkdir -p $d/tons $d/final
  glb=modelo/lumiere-${MODELO[$v]}.glb
  [ -f $d/silhueta.png ] || cp renders/v4/$v/silhueta.png $d/silhueta.png
  for a in $ACABS; do
    for estado in aceso apagado; do
      out=$d/lumiere-$a-$estado.png
      [ -f $out ] && continue
      led=1; [ $estado = apagado ] && led=0
      $PY -I ferramentas/render_lumiere.py $glb $out --acabamento $a --led $led ${CAM[$v]} $COMUM > $d/log-$a-$estado.txt 2>&1
      echo "$(date +%H:%M) $v $a $estado $(grep -o '"render_s": [0-9.]*' $d/log-$a-$estado.txt)"
    done
    for t in 3000 4500 6000; do
      $PY -E -s ferramentas/luz_padrao.py $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png $t $d/tons/lumiere-$a-$t.png > /dev/null 2>&1 || echo "falhou tom $v $a $t"
      $PY -I ferramentas/foto.py $d/tons/lumiere-$a-$t.png $d/final/lumiere-$a-$t.png ${SEMENTE[$v]} \
        $d/lumiere-$a-aceso.png $d/lumiere-$a-apagado.png > /dev/null || echo "falhou foto $v $a $t"
    done
    $PY -I ferramentas/foto.py $d/lumiere-$a-apagado.png $d/final/lumiere-$a-apagado.png ${SEMENTE[$v]} > /dev/null || echo "falhou foto $v $a apagado"
  done
done
echo FIM
