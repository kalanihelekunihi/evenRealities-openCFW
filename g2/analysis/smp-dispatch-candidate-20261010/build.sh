#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
src=g2/components/main/smp_dispatch_candidates_20261010/smp_dispatch.c
out=g2/analysis/smp-dispatch-candidate-20261010
clang --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -ffreestanding -std=c11 -Os -Wall -Wextra -Werror -c "$src" -o "$out/candidate.o"
clang -std=c11 -O2 -Wall -Wextra -Werror -shared -fPIC "$src" -o "$out/candidate.dylib"
python3 "$out/validate.py"
