/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024d70 module source query and 0x10025180 gate query.
 * Both consume the authenticated source-owned 26-entry module table through
 * the native six-word module-info ABI.
 */
#include <stdint.h>
#include "resident_platform_gate.h"

extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t state);

/* 0x100251ec: preserve the exact interrupt state around the SNPU gate. */
/* Stock 0x100251EC (gx_clock_set_module_snpu_enable) */
void gx8002_resident_clock_snpu_enable_251ec(uint32_t enabled)
{
    uint32_t state = g2_codec_critical_save();
    volatile uint32_t *const snpu =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300018);
    uint32_t value = *snpu;
    if (enabled == 0u) value |= UINT32_C(0x100);
    else value &= ~UINT32_C(0x100);
    *snpu = value;
    g2_codec_critical_restore(state);
}

/* Stock 0x10024D70 (gx8002_clock_module_query) */
uint32_t gx8002_resident_clock_module_query_24d70(uint32_t module)
{
    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return UINT32_MAX;
    int32_t dependency = info.entry->dependency_bit;
    if (dependency == -1) return UINT32_MAX;
    uint32_t alternate = 0u;
    if (module < 10u && ((UINT32_C(0x243) >> module) & 1u) != 0u)
        alternate = (uint32_t)(dependency + 1);
    uint32_t bits = *info.status;
    if (alternate != 0u && ((bits >> (alternate & 31u)) & 1u) != 0u) {
        if (module == 7u) return 4u;
        if (module == 8u) return 6u;
        return 2u;
    }
    uint32_t selected = (bits >> ((uint32_t)dependency & 31u)) & 1u;
    if (module == 7u) return selected + 3u;
    if (module == 8u) return selected + 5u;
    return selected;
}

/* Stock 0x10025180 (gx8002_clock_gate_query_fixed) */
uint32_t gx8002_resident_clock_gate_query_25180(uint32_t module)
{
    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0 ||
        info.entry->bit_secondary == 0)
        return UINT32_MAX;
    uint32_t word = *info.field18;
    uint32_t enabled;
    if (module < 23u &&
        ((UINT32_C(0x490000) >> module) & 1u) != 0u) {
        uint32_t first = (uint8_t)gx8002_module_table_266e0[module + 1u].bit_secondary & 31u;
        uint32_t second = (uint8_t)gx8002_module_table_266e0[module + 2u].bit_secondary & 31u;
        enabled = ((word >> first) & (word >> second)) & 1u;
    } else {
        enabled = (word >> ((uint8_t)info.entry->bit_secondary & 31u)) & 1u;
    }
    return (~enabled) & 1u;
}
