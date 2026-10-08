#!/bin/zsh
set -euo pipefail
HERE=/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-handler3-integrated
OUT=/tmp/opencfw-root-pcm22-relocated/handler3-integrated
CC=/usr/bin/clang
CFLAGS=(--target=arm-none-eabi -mcpu=cortex-m33 -mthumb -ffreestanding -fno-builtin -fdata-sections -ffunction-sections -O1 -Wall -Wextra)
"$CC" $CFLAGS -c "$HERE/initialized_data.c" -o "$OUT/rebuild-initialized_data.o"
"$CC" $CFLAGS -c "$HERE/handler3.c" -o "$OUT/rebuild-pcm22_handler3.o"
cmp "$OUT/rebuild-initialized_data.o" "$OUT/inputs/tmp/opencfw-root-pcm22-relocated/handler17-integrated/initialized_data.o"
cmp "$OUT/rebuild-pcm22_handler3.o" "$OUT/inputs/tmp/opencfw-root-pcm22-relocated/handler3-integrated/pcm22_handler3.o"
zsh "$HERE/link-integrated.sh"
/Users/kalani/.local/share/opencfw/venv/bin/python "$HERE/verify_integrated3.py" \
  --candidate "$OUT/candidate3-integrated.elf" \
  --frozen-base "$OUT/frozen-687b0a4e.elf" \
  --output "$OUT/verification.json"
