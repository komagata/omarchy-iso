#!/bin/bash
set -euo pipefail
scripts=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$scripts/.." && pwd)
downloads="$repo/release/jp-downloads"
mkdir -p "$downloads"
curl -fL --retry 3 https://iso.omarchy.org/omarchy-4.0.3.iso -o "$downloads/omarchy-4.0.3.iso"
curl -fL --retry 3 https://huggingface.co/ggerganov/whisper.cpp/resolve/5359861c739e955e79d9a303bcbc70fb988958b1/ggml-small.bin -o "$downloads/ggml-small.bin"
curl -fL --retry 3 https://pkgs.omarchy.org/stable/x86_64/voxtype-bin-1.0.1-1-x86_64.pkg.tar.zst -o "$downloads/voxtype-bin-1.0.1-1-x86_64.pkg.tar.zst"
# build.sh verifies each pinned SHA256 before use.
