/* SPDX-License-Identifier: MIT
 * UART stage-1 _clk_set_dto (clk_priv.h, NationalChip lvp_kws 8bf9ee5c) at
 * stock 0x10000b90: program a DTO divider word with bypass = !enable.
 */
#include <stdint.h>
#include <stddef.h>
#include "uart_stage1_pmu.h"

/* Stock 0x10000B90 */
void gx8002_uart_stage1_railc(uint32_t selector, uint32_t setting,
                               uint32_t mode)
{
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0)
        return;
    const volatile struct stage1_pmu_entry *const entry =
        (const volatile struct stage1_pmu_entry *)view.entry;
    const uint8_t *const dto = entry->special;
    if (dto == NULL || dto[0] == 0u)
        return;
    volatile uint32_t *const reg =
        (volatile uint32_t *)((uintptr_t)view.base + dto[0]);
    const uint32_t old = *reg;                /* __module_get_dto */
    if ((old & UINT32_C(0x01ffffff)) == setting &&
        mode == (((old >> 27) & 1u) ^ 1u))
        return;                               /* same dto, same enable */

    const int32_t gate_high = (int8_t)entry->power_bit;
    const int32_t clk_offs = (int8_t)entry->gate_bit;
    const uint32_t gate = gate_high < 0 ? 0u : gx8002_uart_stage1_bit(*view.set, gate_high);
    if (gate != 0u)
        *view.enable = gx8002_uart_stage1_mask(gate_high);
    const uint32_t clk_mask = gx8002_uart_stage1_mask(clk_offs);
    const uint32_t clk = gx8002_uart_stage1_bit(*view.status, clk_offs);
    if (clk != 0u)
        *view.status &= ~clk_mask;

    const uint32_t value = ((uint32_t)(mode == 0u) << 27) | setting;
    *reg = UINT32_C(1) << 26;
    *reg = 0;
    *reg = UINT32_C(1) << 26;
    *reg = value | (UINT32_C(1) << 26);
    *reg = value | (UINT32_C(1) << 26) | (UINT32_C(1) << 25);
    *reg = value | (UINT32_C(1) << 26) | (UINT32_C(1) << 25);
    *reg = value | (UINT32_C(1) << 26);

    if (clk != 0u)
        *view.status = (*view.status & ~clk_mask) | clk_mask;
    if (gate != 0u)
        *view.clear = gx8002_uart_stage1_mask(gate_high);
}
