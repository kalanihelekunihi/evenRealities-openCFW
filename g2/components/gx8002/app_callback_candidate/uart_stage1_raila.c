/* SPDX-License-Identifier: MIT
 * UART stage-1 rail-A selector control at stock 0x10000860.
 * Descriptor lookup and bit sequencing follow the retained body.
 */
#include <stdint.h>
#include "uart_stage1_pmu.h"

int32_t gx8002_uart_stage1_raila(uint32_t selector, uint32_t setting)
{
    if (selector >= 26u) return -1;
    if (setting == 2u) {
        if (selector > 9u ||
            ((UINT32_C(1) << selector) & UINT32_C(0x247)) == 0)
            return -1;
    } else if ((int32_t)setting > 2) {
        if (selector == 7u) setting = (uint32_t)((int32_t)setting >> 2);
        else if (selector == 8u) setting = (uint32_t)((int32_t)setting / 6);
        else return -1;
    }
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0) return -1;
    const int32_t gate = (int8_t)view.entry[6];
    if (gate == -1) return -1;
    uint32_t gate_bit = (uint32_t)gate & 31u;
    if (setting == 2u) {
        gate_bit = (gate_bit + 1u) & 31u;
        setting = 1u;
    }
    const uint32_t gate_mask = UINT32_C(1) << gate_bit;
    if (((*view.status >> gate_bit) & 1u) == setting) return 0;
    const uint32_t status_bit = (uint32_t)(int8_t)view.entry[5] & 31u;
    const uint32_t powered = (*view.set >> status_bit) & 1u;
    if (powered) {
        *view.status = (*view.status & ~gate_mask) | (setting << gate_bit);
        return 0;
    }
    const uint32_t power_bit = (uint32_t)(int8_t)view.entry[4] & 31u;
    const uint32_t power_mask = UINT32_C(1) << power_bit;
    *view.status = (*view.status & ~gate_mask) | (setting << gate_bit);
    if (selector == 7u || selector == 8u) {
        *view.clear = power_mask;
        /* Native offsets 0x25/26, 0x75/76, and 0x85/86 address
         * status/gate bytes in entries 2, 7, and 8 of the PMU table. */
        const volatile struct stage1_pmu_entry *table =
            (const volatile struct stage1_pmu_entry *)(uintptr_t)UINT32_C(0x20002018);
        const uint32_t both = ((*view.status >> (table[2].gate_bit & 31u)) & 1u) &&
                              ((*view.set >> (table[2].status_bit & 31u)) & 1u);
        const uint32_t peer_7 = ((*view.status >> (table[7].gate_bit & 31u)) & 1u) |
                                ((*view.set >> (table[7].status_bit & 31u)) & 1u);
        const uint32_t peer_8 = ((*view.status >> (table[8].gate_bit & 31u)) & 1u) |
                                ((*view.set >> (table[8].status_bit & 31u)) & 1u);
        if (both && (!peer_7 || !peer_8)) *view.enable = power_mask;
    } else if (setting == 1u) {
        *view.enable = power_mask;
        *view.status = (*view.status & ~gate_mask) | gate_mask;
    } else {
        *view.clear = power_mask;
    }
    return 0;
}
