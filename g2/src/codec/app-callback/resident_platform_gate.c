/* SPDX-License-Identifier: MIT
 * Platform module lookup/gate, stock 0x10024a44 and 0x10025080. The
 * 26-entry product module table is source-owned; its runtime SRAM placement
 * remains a final linker/scatter-copy contract.
 */
#include <stdint.h>
#include "resident_platform_gate.h"
_Static_assert(sizeof(struct gx8002_module_entry) == 16, "native module entry ABI");

/* Stock 0x10024A44 (__module_get_info) */
int32_t gx8002_resident_module_get_info_24a44(
    uint32_t module, struct gx8002_module_info *info)
{
    if (module >= 26u || info == 0) return -1;
    const struct gx8002_module_entry *const table = gx8002_module_table_266e0;
    info->entry = 0;
    if (table[module].id == module) info->entry = &table[module];
    else {
        for (uint32_t i = 0; i < 26u; ++i) {
            if (table[i].id == module) {
                info->entry = &table[i];
                break;
            }
        }
    }
    if (info->entry == 0) return -1;
    uintptr_t base = module < 10u ? UINT32_C(0xa0010000) :
                                     UINT32_C(0xa0300000);
    info->base = (volatile uint32_t *)base;
    info->status = (volatile uint32_t *)(module < 10u ?
                    UINT32_C(0xa001008c) : UINT32_C(0xa0300088));
    info->field18 = (volatile uint32_t *)(base + 0x18u);
    info->disable = (volatile uint32_t *)(base + 0x1cu);
    info->enable = (volatile uint32_t *)(base + 0x20u);
    return 0;
}

/* Stock 0x10025080 (gx8002_platform_gate) */
void gx8002_resident_platform_gate_25080(uint32_t module, uint32_t enabled)
{
    uint32_t lookup = module;
    if (module == 7u || module == 8u) lookup = 2u;
    else if (module == 17u || module == 18u) lookup = 16u;
    else if (module == 20u || module == 21u) lookup = 19u;
    else if (module == 23u || module == 24u) lookup = 22u;

    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(lookup, &info) == 0 &&
        info.entry->dependency_bit != -1) {
        uint32_t dep = (uint8_t)info.entry->dependency_bit;
        uint32_t alt = 0u;
        if (lookup < 10u && ((UINT32_C(0x243) >> lookup) & 1u) != 0u)
            alt = dep + 1u;
        uint32_t active = *info.status;
        uint32_t primary = UINT32_C(1) <<
            ((uint8_t)info.entry->bit_primary & 31u);
        if (enabled != 0u && ((active >> (dep & 31u)) & 1u) != 0u &&
            (alt == 0u || ((active >> (alt & 31u)) & 1u) == 0u))
            *info.enable = primary;
        else
            *info.disable = primary;
    }

    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return;
    uint32_t secondary = UINT32_C(1) <<
        ((uint8_t)info.entry->bit_secondary & 31u);
    switch (module) {
    case 6: case 14: secondary |= UINT32_C(0x8000); break;
    case 11: secondary |= UINT32_C(8); break;
    case 13: secondary |= UINT32_C(0x2000); break;
    case 17: secondary |= UINT32_C(1) << 16; break;
    case 18: secondary |= UINT32_C(1) << 17; break;
    case 20: secondary |= UINT32_C(1) << 18; break;
    case 21: secondary |= UINT32_C(1) << 19; break;
    case 23: secondary |= UINT32_C(1) << 20; break;
    case 24: secondary |= UINT32_C(1) << 21; break;
    default:
        if ((module & ~UINT32_C(4)) == 1u || secondary == 0u) return;
        break;
    }
    if (enabled != 0u) *info.enable = secondary;
    else *info.disable = secondary;
}
