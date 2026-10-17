#!/usr/bin/env bash
# uso: ./generar.sh [alta|baja]
#   alta: 1080p a 60 fps (por defecto)
#   baja: 480p a 15 fps, para revisar rápido
set -e
cd "$(dirname "$0")"

case "${1:-alta}" in
    alta) OPCIONES=(-qh --fps 60); CALIDAD=1080p60 ;;
    baja) OPCIONES=(-ql);          CALIDAD=480p15 ;;
    *)    echo "uso: $0 [alta|baja]"; exit 1 ;;
esac

MANIM=.venv/bin/manim
[ -x "$MANIM" ] || { echo "Primero hay que correr ./instalar.sh"; exit 1; }

ESCENAS=$(LC_ALL=C ls escenas/*.py)

for archivo in $ESCENAS; do
    clase=$(grep -oP "^class \K\w+" "$archivo")
    echo "Renderizando $(basename "$archivo" .py)"
    $MANIM "${OPCIONES[@]}" --verbosity WARNING --progress_bar none "$archivo" "$clase"
done

LISTA=$(mktemp)
for archivo in $ESCENAS; do
    nombre=$(basename "$archivo" .py)
    clase=$(grep -oP "^class \K\w+" "$archivo")
    echo "file '$PWD/media/videos/$nombre/$CALIDAD/$clase.mp4'" >> "$LISTA"
done
mkdir -p salida
SIN_MARCA="salida/osi_sin_marca_$CALIDAD.mp4"
ffmpeg -v error -y -f concat -safe 0 -i "$LISTA" -c copy "$SIN_MARCA"
rm "$LISTA"

# Marca de agua: cada tramo es "inicio fin esquina", en segundos. Las esquinas
# están elegidas para que en ese momento no haya nada del video debajo.
MARCA="hecho por\\: Sergio Verdugo"
TRAMOS=(
    "3 128 abajo_der"
    "138 225 arriba_der"
    "235 360 abajo_izq"
    "370 495 arriba_izq"
    "505 630 arriba_der"
    "640 765 abajo_izq"
    "775 880 arriba_izq"
    "890 928 abajo_der"
)
FUENTE=$(fc-match -f '%{file}' "DejaVu Sans")
M="h*0.015"

filtro=""
for tramo in "${TRAMOS[@]}"; do
    read -r ini fin esquina <<< "$tramo"
    case $esquina in
        arriba_izq) x=$M;        y=$M ;;
        arriba_der) x="w-tw-$M"; y=$M ;;
        abajo_izq)  x=$M;        y="h-th-$M" ;;
        abajo_der)  x="w-tw-$M"; y="h-th-$M" ;;
    esac
    alfa="if(lt(t,$ini+1),t-$ini,if(gt(t,$fin-1),$fin-t,1))"
    filtro+="drawtext=fontfile=$FUENTE:text='$MARCA':fontsize=h*0.022"
    filtro+=":fontcolor=0x8A8D93:alpha='$alfa':x=$x:y=$y"
    filtro+=":enable='between(t,$ini,$fin)',"
done

ffmpeg -v error -y -i "$SIN_MARCA" -vf "${filtro%,}" -c:v libx264 -crf 18 \
    -pix_fmt yuv420p "salida/osi_$CALIDAD.mp4"

echo "Video: salida/osi_$CALIDAD.mp4"
