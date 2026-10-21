/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024be0 source-selection body. The unusual table-index
 * dependencies and 7/8 gate logic follow the native control-flow graph.
 */
#include <stdint.h>
#include "resident_platform_gate.h"

extern void gx8002_resident_reg_set_val_24a30(
    volatile uint32_t *, uint32_t, uint32_t, uint32_t);

static uint32_t bit_at(uint32_t value, int8_t bit)
{
    return (value >> ((uint8_t)bit & 31u)) & 1u;
}

uint32_t gx8002_resident_clock_module_source_24be0(
    uint32_t module, uint32_t source)
{
    if (module >= 26u) return UINT32_MAX;
    uint32_t mask = 1u;
    if (source == 2u) {
        if (module >= 10u || ((UINT32_C(0x247) >> module) & 1u) == 0u)
            return UINT32_MAX;
    } else if ((int32_t)source > 2) {
        if (module == 7u) source = (uint32_t)((int32_t)source >> 2);
        else if (module == 8u) {
            source -= 5u;
            mask = 3u;
        } else return UINT32_MAX;
    }

    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return UINT32_MAX;
    int8_t source_bit = info.entry->bit_secondary;
    if (source_bit == -1) return UINT32_MAX;
    if (source == 2u && module != 8u) {
        source_bit = (int8_t)(source_bit + 1);
        source = 1u;
    }
    if (((*info.status >> ((uint8_t)source_bit & 31u)) & mask) == source)
        return 0u;

    uint32_t dependency_high;
    if (module < 23u && ((UINT32_C(0x490000) >> module) & 1u) != 0u) {
        uint32_t gate = *info.field18;
        dependency_high = bit_at(gate,
            gx8002_module_table_266e0[module + 1u].bit_secondary) &
            bit_at(gate,
            gx8002_module_table_266e0[module + 2u].bit_secondary);
    } else {
        dependency_high = bit_at(*info.field18,
                                 info.entry->bit_secondary);
    }
    if (dependency_high == 0u) {
        gx8002_resident_reg_set_val_24a30(info.status,
            (uint8_t)source_bit, source, mask);
        return 0u;
    }

    uint32_t primary = UINT32_C(1) <<
        ((uint8_t)info.entry->bit_primary & 31u);
    if (module == 7u || module == 8u) {
        gx8002_resident_reg_set_val_24a30(info.status,
            (uint8_t)source_bit, source, mask);
        *info.enable = primary;
        uint32_t status = *info.status;
        uint32_t gate = *info.field18;
        const struct gx8002_module_entry *table = gx8002_module_table_266e0;
        if (bit_at(status, table[2].dependency_bit) == 0u)
            return 0u;
        if (bit_at(gate, table[2].bit_secondary) == 0u)
            return 0u;
        if (((status >> ((uint8_t)table[8].dependency_bit & 31u)) & 3u) != 0u ||
            bit_at(gate, table[8].bit_secondary) != 0u) {
            if ((bit_at(status, table[7].dependency_bit) |
                 bit_at(gate, table[7].bit_secondary)) != 0u)
                return 0u;
        }
        *info.disable = primary;
        return 0u;
    }
    if (source == 1u) {
        *info.disable = primary;
        gx8002_resident_reg_set_val_24a30(info.status,
            (uint8_t)source_bit, source, mask);
    } else {
        gx8002_resident_reg_set_val_24a30(info.status,
            (uint8_t)source_bit, source, mask);
        *info.enable = primary;
    }
    return 0u;
}
