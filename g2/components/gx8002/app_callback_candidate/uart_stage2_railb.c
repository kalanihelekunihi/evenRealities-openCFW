/* SPDX-License-Identifier: MIT
 * UART stage-2 rail-B field programmer at stock 0x100047dc.
 * Based on authenticated stage-2 decompilation and descriptor data.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

void gx8002_uart_stage2_gate_47dc(uint32_t selector, uint32_t setting)
{
    struct stage1_pmu_view view;
    if (gx8002_uart_stage2_pmu_fill_desc(selector, &view) != 0) return;
    const volatile struct stage1_pmu_entry *entry =
        (const volatile struct stage1_pmu_entry *)view.entry;
    const volatile struct stage1_pmu_aux_field *aux = entry->aux;
    if (aux == NULL || aux->register_offset == 0) return;

    const uint32_t shift = aux->shift & 31u;
    const uint32_t field_mask = aux->mask;
    volatile uint32_t *reg = (volatile uint32_t *)
        ((uintptr_t)view.base + aux->register_offset);
    uint32_t current = (*reg >> shift) & field_mask;
    if (current != 0) ++current;
    if ((setting & UINT32_C(0x7fff)) == current) return;

    uint32_t width = 0;
    for (uint32_t bits = field_mask; bits != 0; bits >>= 1) ++width;
    const int32_t power_bit = (int8_t)entry->power_bit;
    const uint32_t gate_bit = entry->gate_bit & 31u;
    uint32_t was_powered = 0;
    if (power_bit >= 0) {
        const uint32_t power_mask = UINT32_C(1) << (unsigned)power_bit;
        was_powered = (*view.status & power_mask) != 0;
        if (was_powered) *view.enable = power_mask;
    }
    const uint32_t gate_mask = UINT32_C(1) << gate_bit;
    const uint32_t was_gated = (*view.status & gate_mask) != 0;
    if (was_gated && (selector == 6u || selector > 9u))
        *view.status &= ~gate_mask;

    const uint32_t latch_high = UINT32_C(1) << ((shift + width + 1u) & 31u);
    *reg &= ~latch_high;
    *reg |= latch_high;
    *reg &= ~(field_mask << shift);
    const uint32_t field = (setting & UINT32_C(0xffff)) != 0
        ? ((setting & UINT32_C(0x7fff)) - 1u) << shift : 0u;
    *reg |= field;
    const uint32_t latch_low = UINT32_C(1) << ((shift + width) & 31u);
    *reg &= ~latch_low;
    *reg |= latch_low;
    if (was_gated && (selector == 6u || selector > 9u))
        *view.status = (*view.status & ~gate_mask) | gate_mask;
    if (was_powered)
        *view.clear = UINT32_C(1) << (unsigned)power_bit;
}
