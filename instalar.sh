#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if command -v pacman >/dev/null; then
    sudo pacman -S --needed ffmpeg cairo pango pkgconf ttf-dejavu curl
elif command -v apt-get >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg libcairo2-dev libpango1.0-dev pkg-config \
        fonts-dejavu-core build-essential python3-dev curl
elif command -v dnf >/dev/null; then
    sudo dnf install -y ffmpeg cairo-devel pango-devel pkgconf-pkg-config \
        dejavu-sans-fonts dejavu-sans-mono-fonts gcc python3-devel curl
else
    echo "No se reconoce el gestor de paquetes."
    echo "Instalar a mano: ffmpeg, cairo, pango, pkg-config y las fuentes DejaVu."
    exit 1
fi

if ! command -v uv >/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python manim==0.22.0

for fuente in "DejaVu Sans" "DejaVu Sans Mono"; do
    if ! fc-list : family | grep -qx "$fuente"; then
        echo "Falta la fuente $fuente"
        exit 1
    fi
done

.venv/bin/manim --version
echo "Listo. Para generar el video: ./generar.sh"
