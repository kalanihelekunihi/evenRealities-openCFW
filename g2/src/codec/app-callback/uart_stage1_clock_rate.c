/* SPDX-License-Identifier: MIT
 * UART stage-1 PMU clock-rate body at 0x10000ea0..0x1000107f.
 * The 0x10001ef4 selector jump table is reduced to switch cases; register
 * arithmetic follows the authenticated native instruction sequence.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

static uint32_t native_divu(uint32_t numerator, uint32_t denominator)
{
    uint32_t result;
    __asm__ volatile("divu %0, %1, %2" : "=r"(result)
                     : "r"(numerator), "r"(denominator) : "cc");
    return result;
}

int32_t gx8002_uart_stage1_pmu_clock_rate(uint32_t selector)
{
    uint32_t lookup = selector;
    if (selector == 7u || selector == 8u) return 0;
    if (selector == 17u || selector == 18u) lookup = 16u;
    else if (selector == 20u || selector == 21u) lookup = 19u;
    else if (selector == 23u || selector == 24u) lookup = 22u;
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(lookup, &view) != 0) return 0;
    const int32_t gate = (int8_t)view.entry[6];
    if (gate == -1) return 0;
    const uint32_t gate_bit = (uint32_t)gate & 31u;
    uint32_t rate;
    if (lookup < 10u && ((UINT32_C(1) << lookup) & UINT32_C(579)) &&
        ((*view.status >> ((gate_bit + 1u) & 31u)) & 1u)) {
        rate = 32000u;
        goto divide_by_aux;
    }

    const uint32_t control = *(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
    if (((*view.status >> gate_bit) & 1u) == 0) {
        rate = (control & UINT32_C(0x40000)) ? 1024000u : 12288000u;
        if (lookup > 9u || lookup == 9u || (lookup & ~UINT32_C(4)) == 2u)
            return 0;
        goto divide_by_aux;
    }
    if ((control & 1u) == 0) {
        rate = 24576000u;
        goto calibrate;
    }

    volatile uint32_t *const pll = (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    const uint32_t divider = (pll[0x1c / 4] & 63u) + 1u;
    const uint32_t factor = (pll[0x20 / 4] | ((pll[0x24 / 4] << 8) & 7936u)) + 1u;
    const uint32_t postdivider = pll[0x28 / 4];
    const uint32_t mode = (pll[0x30 / 4] >> 4) & 3u;
    uint32_t base = 61440000u;
    if (mode == 1u) base = 73728000u;
    else if (mode == 2u) base = 86016000u;
    else if (mode == 3u) base = 98304000u;
    const uint32_t scaled = native_divu(base * divider, factor);
    if (scaled - 16000u <= 31999u) rate = 32000u;
    else if (scaled - 512000u <= 1023999u) rate = 1024000u;
    else if (scaled - 153600u <= 2918399u) rate = 2048000u;
    else return -1;
    rate = native_divu(rate, divider) * factor;
    rate = native_divu(rate, 2u * ((postdivider & 7u) + 1u));

calibrate:
    if (view.entry != NULL) {
        const uintptr_t calibration = *(const volatile uint32_t *)(view.entry + 12);
        if (calibration != 0) {
            const uint32_t offset = *(const volatile uint8_t *)calibration;
            const uint32_t word = *(const volatile uint32_t *)((uintptr_t)view.base + offset);
            if ((word & UINT32_C(0x08000000)) == 0)
                rate = (uint32_t)(((uint64_t)(word & UINT32_C(0x00ffffff)) *
                                   UINT64_C(24576000)) >> 25);
        }
    }
divide_by_aux:
    {
        const uintptr_t aux_address = *(const volatile uint32_t *)(view.entry + 8);
        if (aux_address == 0) return 0;
        const volatile struct stage1_pmu_aux_field *aux =
            (const volatile struct stage1_pmu_aux_field *)aux_address;
        const uint32_t field = (*(const volatile uint32_t *)
            ((uintptr_t)view.base + aux->register_offset) >> (aux->shift & 31u)) &
            aux->mask;
        if (field == 0) return 0;
        return (int32_t)native_divu(rate, field + 1u);
    }
}
