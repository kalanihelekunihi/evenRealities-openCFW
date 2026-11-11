/* SPDX-License-Identifier: MIT
 * UART stage-1 _clk_set_div (clk_priv.h, NationalChip lvp_kws 8bf9ee5c) at
 * stock 0x10000a30. The divider is a 16-bit value; 0 clears the field.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

/* Stock 0x10000A30 */
void gx8002_uart_stage1_railb(uint32_t selector, uint32_t setting)
{
    const uint32_t div = setting & 0xffffu;
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0)
        return;
    const volatile struct stage1_pmu_entry *const entry =
        (const volatile struct stage1_pmu_entry *)view.entry;
    const struct stage1_pmu_aux_field *const field = entry->aux;
    if (field == NULL || field->register_offset == 0u)
        return;
    volatile uint32_t *const reg =
        (volatile uint32_t *)((uintptr_t)view.base + field->register_offset);
    const uint32_t offs = field->shift;
    const uint32_t mask = field->mask;
    uint32_t current = (*reg >> offs) & mask;    /* __module_get_div */
    if (current != 0u)
        ++current;
    if (div == current)
        return;

    uint32_t width = 0;
    while ((mask >> width) != 0u)
        ++width;

    const int32_t gate_high = (int8_t)entry->power_bit;
    const int32_t clk_offs = (int8_t)entry->gate_bit;
    const uint32_t gate = gate_high < 0 ? 0u : gx8002_uart_stage1_bit(*view.set, gate_high);
    if (gate != 0u)
        *view.enable = gx8002_uart_stage1_mask(gate_high);
    const uint32_t clk_mask = gx8002_uart_stage1_mask(clk_offs);
    const uint32_t clk = gx8002_uart_stage1_bit(*view.status, clk_offs) != 0u &&
        (selector == 6u || selector >= 10u);    /* SRAM or >= SCPU */
    if (clk)
        *view.status &= ~clk_mask;

    const uint32_t rst = gx8002_uart_stage1_mask((int32_t)(offs + width + 1u));
    const uint32_t load = gx8002_uart_stage1_mask((int32_t)(offs + width));
    *reg &= ~rst;
    *reg |= rst;
    *reg &= ~(mask << offs);
    *reg |= div == 0u ? 0u : (div - 1u) << offs;
    *reg &= ~load;
    *reg |= load;

    if (clk)
        *view.status = (*view.status & ~clk_mask) | clk_mask;
    if (gate != 0u)
        *view.clear = gx8002_uart_stage1_mask(gate_high);
}
