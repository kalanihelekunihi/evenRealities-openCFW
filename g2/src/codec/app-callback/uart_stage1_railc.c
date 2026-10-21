/* SPDX-License-Identifier: MIT
 * PMU rail-C configure body at 0x10000b90. Runtime descriptor fields and
 * aux-register pointer come from the separately initialized product table.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

void gx8002_uart_stage1_railc(uint32_t selector, uint32_t setting,
                               uint32_t mode)
{
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0) return;
    const uintptr_t aux_address = *(const volatile uint32_t *)(view.entry + 12);
    if (aux_address == 0) return;
    const volatile uint8_t *const aux = (const volatile uint8_t *)aux_address;
    if (aux[0] == 0) return;
    volatile uint32_t *const register_word =
        (volatile uint32_t *)((uintptr_t)view.base + aux[0]);
    const uint32_t old = *register_word;
    if ((old & UINT32_C(0xffffff)) == setting &&
        ((old >> 27) & 1u) == mode) return;

    const int32_t power_bit = (int8_t)view.entry[4];
    const uint32_t enable_bit = (uint8_t)view.entry[6] & 31u;
    uint32_t was_powered = 0;
    if (power_bit >= 0) {
        const uint32_t mask = UINT32_C(1) << ((uint32_t)power_bit & 31u);
        was_powered = (*view.status & mask) != 0;
        if (was_powered) *view.enable = mask;
    }
    const uint32_t enable_mask = UINT32_C(1) << enable_bit;
    const uint32_t was_enabled = (*view.status & enable_mask) != 0;
    if (was_enabled) *view.status &= ~enable_mask;

    const uint32_t value = ((uint32_t)(uint8_t)~(mode != 0u) << 27) | setting;
    *register_word = 0;
    *register_word = 0;
    *register_word = 0;
    *register_word = value;
    *register_word = value | UINT32_C(0x6000000);
    *register_word = value | UINT32_C(0x6000000);
    *register_word = value;
    if (was_enabled) *view.status = (*view.status & ~enable_mask) | enable_mask;
    if (was_powered) *view.clear = UINT32_C(1) << ((uint32_t)power_bit & 31u);
}
