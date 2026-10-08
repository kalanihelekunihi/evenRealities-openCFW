#!/bin/sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
cc=${ARM_CC:-/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc}
out=${TOUCH_SCAN_BUILD:-/tmp/opencfw-touch-saturated-scan}
mkdir -p "$out"
cat > "$out/link.ld" <<'LINK'
SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
LINK
"$cc" -mcpu=cortex-m0plus -mthumb -Og -ffreestanding -fno-builtin -ffunction-sections -nostdlib -Wl,--gc-sections -Wl,-u,touch_execute_saturated -T "$out/link.ld" "$repo/g2/components/touch/saturated_scan_offline/scan.c" "$repo/g2/components/touch/max_raw_offline/max_raw.c" "$repo/g2/components/touch/scan_watchdog_offline/watchdog.c" "$repo/g2/components/touch/scan_frame_offline/frame.c" -lgcc -o "$out/scan.elf"
