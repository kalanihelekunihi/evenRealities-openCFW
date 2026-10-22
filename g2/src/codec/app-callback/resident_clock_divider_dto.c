/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024df8 and 0x10024f44. Direct native instruction and
 * retained decomp control-flow reconstruction. MMIO writes remain volatile.
 */
#include <stdint.h>
#include "resident_platform_gate.h"

extern uint32_t gx8002_resident_module_div_read_24ae8(
    const struct gx8002_module_entry *, volatile uint8_t *);
extern void gx8002_resident_reg_set_val_24a30(
    volatile uint32_t *, uint32_t, uint32_t, uint32_t);

/* Stock 0x10024DF8 (gx8002_clock_module_divider_set) */
void gx8002_resident_clock_module_divider_24df8(
    uint32_t module, uint32_t divider)
{
    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return;
    const uint8_t *packed = (const uint8_t *)info.entry->config;
    if (packed == 0 || packed[0] == 0)
        return;
    if ((divider & 0x7fffu) == gx8002_resident_module_div_read_24ae8(
                                  info.entry, (volatile uint8_t *)info.base))
        return;

    uint32_t shift = packed[1];
    uint32_t mask = (uint32_t)packed[2] | ((uint32_t)packed[3] << 8);
    uint32_t width = 0;
    while ((mask >> width) != 0u) ++width;
    uint32_t primary = (uint8_t)info.entry->bit_primary;
    uint32_t secondary = (uint8_t)info.entry->bit_secondary;
    uint32_t primary_active = 0;
    if (info.entry->bit_primary >= 0) {
        primary_active = (*info.field18 >> (primary & 31u)) & 1u;
        if (primary_active) *info.enable = UINT32_C(1) << (primary & 31u);
    }
    uint32_t secondary_active = (*info.status >> (secondary & 31u)) & 1u;
    uint32_t toggle_secondary = module == 6u || module >= 10u;
    if (secondary_active && toggle_secondary)
        gx8002_resident_reg_set_val_24a30(info.status, secondary, 0u, 1u);

    volatile uint32_t *reg = (volatile uint32_t *)
        ((volatile uint8_t *)info.base + packed[0]);
    uint32_t clear_latch = UINT32_C(1) << ((width + shift + 1u) & 31u);
    *reg = *reg & ~clear_latch;
    *reg = *reg | clear_latch;
    *reg = *reg & ~(mask << (shift & 31u));
    uint32_t value = (divider & 0xffffu) == 0u ? 0u : (divider & 0x7fffu) - 1u;
    *reg = *reg | (value << (shift & 31u));
    uint32_t set_latch = UINT32_C(1) << ((width + shift) & 31u);
    *reg = *reg & ~set_latch;
    *reg = *reg | set_latch;
    if (secondary_active && toggle_secondary)
        gx8002_resident_reg_set_val_24a30(info.status, secondary, 1u, 1u);
    if (primary_active) *info.disable = UINT32_C(1) << (primary & 31u);
}

/* Stock 0x10024F44 (gx8002_clock_module_dto_set) */
void gx8002_resident_clock_module_dto_24f44(
    uint32_t module, uint32_t numerator, uint32_t mode)
{
    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return;
    const uint8_t *offset = info.entry->mode;
    if (offset == 0 || *offset == 0)
        return;
    volatile uint32_t *reg = (volatile uint32_t *)
        ((volatile uint8_t *)info.base + *offset);
    uint32_t previous = *reg;
    if (numerator == (previous & 0xffffffu) &&
        mode == (((previous ^ UINT32_C(0x08000000)) >> 27) & 1u))
        return;

    uint32_t primary = (uint8_t)info.entry->bit_primary;
    uint32_t secondary = (uint8_t)info.entry->bit_secondary;
    uint32_t primary_active = 0;
    if (info.entry->bit_primary >= 0) {
        primary_active = (*info.field18 >> (primary & 31u)) & 1u;
        if (primary_active) *info.enable = UINT32_C(1) << (primary & 31u);
    }
    uint32_t secondary_active = (*info.status >> (secondary & 31u)) & 1u;
    if (secondary_active)
        gx8002_resident_reg_set_val_24a30(info.status, secondary, 0u, 1u);

    uint32_t payload = numerator | ((mode == 0u ? 1u : 0u) << 27);
    uint32_t stage_a = payload | UINT32_C(0x04000000);
    uint32_t stage_b = payload | UINT32_C(0x06000000);
    *reg = UINT32_C(0x04000000);
    *reg = 0u;
    *reg = UINT32_C(0x04000000);
    *reg = stage_a;
    *reg = stage_b;
    *reg = stage_b;
    *reg = stage_a;
    if (secondary_active)
        gx8002_resident_reg_set_val_24a30(info.status, secondary, 1u, 1u);
    if (primary_active) *info.disable = UINT32_C(1) << (primary & 31u);
}
