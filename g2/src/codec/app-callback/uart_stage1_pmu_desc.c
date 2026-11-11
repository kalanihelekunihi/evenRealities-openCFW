/* SPDX-License-Identifier: MIT
 * PMU descriptor lookup at 0x10000780. The 26-entry, 16-byte table
 * (stock 0x20002018) is g2_uart_stage1_pmu_table in uart_stage1_pmu_data.c.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

int32_t gx8002_uart_stage1_pmu_fill_desc(uint32_t selector,
                                           struct stage1_pmu_view *out)
{
    if (selector >= 26u || out == NULL) return -1;
    const volatile struct stage1_pmu_entry *const entries = STAGE1_CLOCK_TABLE;
    out->entry = NULL;
    unsigned index = selector;
    if (entries[index].selector != selector) {
        for (index = 0; index < 26u; ++index) {
            if (entries[index].selector == selector) break;
        }
        if (index == 26u) return -1;
    }
    out->entry = (const volatile uint8_t *)&entries[index];
    const uintptr_t base = selector < 10u ? UINT32_C(0xa0010000)
                                           : UINT32_C(0xa0300000);
    out->base = (volatile uint32_t *)base;
    out->status = (volatile uint32_t *)(base + (selector < 10u ? 0x8cu : 0x88u));
    out->set = (volatile uint32_t *)(base + 0x18u);
    out->clear = (volatile uint32_t *)(base + 0x1cu);
    out->enable = (volatile uint32_t *)(base + 0x20u);
    return 0;
}
