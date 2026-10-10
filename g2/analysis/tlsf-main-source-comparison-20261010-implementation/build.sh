#!/bin/sh
set -eu
cd "$(dirname "$0")"
R=$(git rev-parse --show-toplevel)
INC="$R/g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi/arm-none-eabi/include"
/usr/bin/clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -O1 -g -ffreestanding -fno-builtin -isystem "$INC" -c comparator.c -o comparator.o
/usr/bin/clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -O1 -ffreestanding -fno-builtin -isystem "$INC" -c providers.c -o providers.o
arm-none-eabi-ld -T link.ld comparator.o providers.o -o comparator.elf
