/* SPDX-License-Identifier: MIT
 * Native XIP 0x10204080..0x10204125, authenticated direct MMIO and
 * 0x20027330 active-channel literal. NationalChip output record passes
 * five words by value. Native division requires nonzero frame_num.
 */
#include <stdint.h>
#include "resident_xip_audio_output_types.h"

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);
static volatile uint32_t *const active =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027334);

static void replace_bits(volatile uint32_t *reg, uint32_t mask, uint32_t bits)
{
    *reg = (*reg & ~mask) | (bits & mask);
}

int32_t gx8002_xip_audio_output_logfbank_10204080(
    gx8002_logfbank_output output)
{
    if ((output.buffer & 7u) != 0u || output.size % 80u != 0u ||
        output.size % output.frame_num != 0u)
        return -1;
    volatile uint32_t *reg = &ain[0x108u / 4u];
    replace_bits(reg, 0x180000u, output.endian << 19u);
    replace_bits(reg, 0x70000u, output.source << 16u);
    ain[0x15cu / 4u] = output.frame_num;
    ain[0x160u / 4u] = output.buffer & ~UINT32_C(7);
    ain[0x164u / 4u] = output.size;
    ain[0x104u / 4u] = UINT32_C(0x2000);
    replace_bits(reg, 0x400000u, 0x400000u);
    replace_bits(reg, 0x800000u, 0u);
    replace_bits(reg, 0x200000u, 0x200000u);
    *active = *active | 4u;
    return 0;
}
