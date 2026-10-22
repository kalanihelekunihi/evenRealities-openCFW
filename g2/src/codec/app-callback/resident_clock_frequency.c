/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025210 clock frequency. The 19-entry native jump table
 * at 0x10025460 is expressed as module cases; arithmetic follows direct
 * instructions at 0x1002529c..0x100253b6. This is a C candidate, not a
 * claim of native runtime or final placement equivalence.
 */
#include <stdint.h>
#include "resident_platform_gate.h"

extern uint32_t gx8002_resident_module_div_read_24ae8(
    const struct gx8002_module_entry *, volatile uint8_t *);

static volatile uint32_t *const pmu_clock =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
static volatile uint32_t *const pll =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);

static uint32_t bit(uint32_t word, uint32_t position)
{
    return (word >> (position & 31u)) & 1u;
}

/* Stock 0x10025210 (gx8002_clock_frequency) */
uint32_t gx8002_resident_clock_frequency_25210(uint32_t module)
{
    /* Native dispatch selects the parent module or the zero result. */
    if (module == 7u || module == 8u) return 0u;
    if (module == 17u || module == 18u) module = 16u;
    else if (module == 20u || module == 21u) module = 19u;
    else if (module == 23u || module == 24u) module = 22u;
    else if (module == 25u) module = 10u;

    struct gx8002_module_info info;
    if (gx8002_resident_module_get_info_24a44(module, &info) != 0)
        return 0u;
    int32_t dependency = info.entry->dependency_bit;
    if (dependency == -1) return 0u;

    uint32_t alternate = 0u;
    if (module < 10u && bit(UINT32_C(0x243), module) != 0u)
        alternate = (uint32_t)(dependency + 1);
    uint32_t status = *info.status;
    uint32_t rate;
    if (alternate != 0u && bit(status, alternate) != 0u) {
        rate = 32000u;
    } else if (bit(status, (uint32_t)dependency) == 0u) {
        rate = bit(*pmu_clock, 18u) != 0u ? 1024000u : 12288000u;
        if (module >= 9u || (module & ~UINT32_C(4)) == 2u)
            return rate;
    } else {
        uint32_t clock_status = *pmu_clock;
        rate = 0u;
        if ((clock_status & 1u) != 0u) {
            uint32_t numerator = (pll[0x1cu / 4u] & 63u) + 1u;
            uint32_t multiplier =
                (((pll[0x24u / 4u] << 8u) & UINT32_C(0x1f00)) |
                 pll[0x20u / 4u]) + 1u;
            uint32_t mode = (pll[0x30u / 4u] >> 4u) & 3u;
            uint32_t reference;
            switch (mode) {
            case 2u: reference = 86016000u; break;
            case 3u: reference = 98304000u; break;
            case 1u: reference = 73728000u; break;
            default: reference = 61440000u; break;
            }
            uint32_t measured = (numerator * reference) / multiplier;
            uint32_t target;
            if ((uint32_t)(measured - 16000u) < 32000u)
                target = 32000u;
            else if ((uint32_t)(measured + UINT32_C(0xfff83000)) <=
                     UINT32_C(0x000f9fff))
                target = 1024000u;
            else if ((uint32_t)(measured + UINT32_C(0xfffda800)) <=
                     UINT32_C(0x002c87ff))
                target = 2048000u;
            else
                return UINT32_MAX;
            rate = ((target / numerator) * multiplier) /
                   (((pll[0x28u / 4u] & 7u) + 1u) * 2u);
        } else {
            rate = 24576000u;
        }

        /* Native 0x1002531a applies the DTO only on this PLL path. */
        if (info.entry->mode != 0) {
            volatile uint8_t *base = (volatile uint8_t *)(void *)info.base;
            uint32_t word = *(volatile uint32_t *)(void *)(base + info.entry->mode[0]);
            if ((word & UINT32_C(0x08000000)) == 0u) {
                uint64_t scaled = (uint64_t)(word & UINT32_C(0x00ffffff)) * rate;
                rate = (uint32_t)(scaled >> 25u) | (module << 7u);
            }
        }
    }

    uint32_t divider = gx8002_resident_module_div_read_24ae8(
        info.entry, (volatile uint8_t *)(void *)info.base);
    return divider != 0u ? rate / divider : rate;
}
