#!/bin/sh
set -eu
cd "$(dirname "$0")/../../.."
D=g2/analysis/flashdb-c-wrapper-20261010
I=g2/components/main/flashdb_candidates_20261010
clang --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -O1 -ffreestanding -fno-builtin -Wall -Wextra -Werror -I "$I" -c "$I/blob_read.c" -o "$D/blob_read.o"
# M33 fixture avoids unsupported low-overhead M55 loop instructions in Unicorn.
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -O1 -ffreestanding -fno-builtin -Wall -Wextra -Werror -I "$I" -c "$D/fixture.c" -o "$D/fixture.o"
arm-none-eabi-ld -T "$D/link.ld" "$D/blob_read.o" "$D/fixture.o" -o "$D/candidate.elf"
arm-none-eabi-objdump -dr "$D/blob_read.o" > "$D/source.disasm.txt"
arm-none-eabi-readelf -sWr "$D/blob_read.o" > "$D/source.relocations.txt"
