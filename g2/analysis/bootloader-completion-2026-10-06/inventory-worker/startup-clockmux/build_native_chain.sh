#!/bin/sh
set -eu

ROOT_DIR=$(git rev-parse --show-toplevel)
HERE="$ROOT_DIR/g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux"
BASE="$ROOT_DIR/g2/analysis/bootloader-completion-2026-10-06"
OUT_DIR=${CLOCKMUX_CHAIN_BUILD_DIR:-/tmp/clockmux-chain}
mkdir -p "$OUT_DIR"
CC=${CC:-clang}
LD=${LD:-arm-none-eabi-ld}
TARGET='--target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -fshort-enums'
CFLAGS="$TARGET -std=c11 -O2 -ffunction-sections -fdata-sections -ffreestanding -fno-builtin -Wall -Wextra -Werror"
INCLUDES="-I$ROOT_DIR/g2/components/bootloader/clock_manager -I$ROOT_DIR/g2/components/bootloader/platform_control -I$ROOT_DIR/g2/components/bootloader/nor_mspi_init -I$ROOT_DIR/g2/components/foundation/cache_maintenance -I$BASE/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include -I$BASE/upstream-worker/ambiqhal-apollo510/cmsis-5-590/CMSIS/Core/Include"

compile() {
    name=$1
    source=$2
    # Intentional word splitting for compiler flags and include directories.
    # shellcheck disable=SC2086
    $CC $CFLAGS $INCLUDES -c "$source" -o "$OUT_DIR/$name.o"
}

compile clockmux_carried "$BASE/inventory-worker/startup-initialize/clockmux_carried.c"
compile native_adapters "$HERE/native_adapters.c"
compile native_pll_access "$HERE/native_pll_access.c"
compile power_register_read "$HERE/power_register_read.c"
compile power_domain_test_services "$HERE/power_domain_test_services.c"
compile clock_manager "$ROOT_DIR/g2/components/bootloader/clock_manager/clock_manager.c"
compile clock_class_providers "$ROOT_DIR/g2/components/bootloader/clock_manager/clock_class_providers.c"
compile clock_class_provider2 "$ROOT_DIR/g2/components/bootloader/clock_manager/clock_class_provider2.c"
compile clock_class_provider4 "$ROOT_DIR/g2/components/bootloader/clock_manager/clock_class_provider4.c"
compile clock_class_provider5 "$ROOT_DIR/g2/components/bootloader/clock_manager/clock_class_provider5.c"
compile status_poll "$ROOT_DIR/g2/components/bootloader/nor_mspi_init/status_poll.c"
compile cache_maintenance "$ROOT_DIR/g2/components/foundation/cache_maintenance/cache_maintenance.c"
compile power_domains "$ROOT_DIR/g2/components/bootloader/platform_control/power_domains.c"
compile runtime_query "$ROOT_DIR/g2/components/bootloader/platform_control/runtime_query.c"

# shellcheck disable=SC2086
$CC $TARGET -c "$BASE/inventory-worker/startup-initialize/clockmux_entry.S" -o "$OUT_DIR/clockmux_entry.o"
# shellcheck disable=SC2086
$CC $TARGET -c "$ROOT_DIR/g2/components/bootloader/platform_control/critical_save.S" -o "$OUT_DIR/critical_save.o"

$LD -T "$HERE/native-chain.ld" \
    "$OUT_DIR/clockmux_entry.o" "$OUT_DIR/clockmux_carried.o" \
    "$OUT_DIR/native_adapters.o" "$OUT_DIR/native_pll_access.o" \
    "$OUT_DIR/power_register_read.o" "$OUT_DIR/power_domain_test_services.o" \
    "$OUT_DIR/clock_manager.o" "$OUT_DIR/clock_class_providers.o" \
    "$OUT_DIR/clock_class_provider2.o" "$OUT_DIR/clock_class_provider4.o" \
    "$OUT_DIR/clock_class_provider5.o" "$OUT_DIR/status_poll.o" \
    "$OUT_DIR/cache_maintenance.o" "$OUT_DIR/power_domains.o" \
    "$OUT_DIR/runtime_query.o" "$OUT_DIR/critical_save.o" \
    -o "$OUT_DIR/clockmux-native-chain.elf"
printf '%s\n' "$OUT_DIR/clockmux-native-chain.elf"
