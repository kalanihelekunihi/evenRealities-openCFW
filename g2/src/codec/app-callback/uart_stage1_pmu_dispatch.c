/* SPDX-License-Identifier: MIT
 * UART stage-1 PMU dispatch at 0x10000d98. The two indirect native jump
 * tables at 0x10001e60 and 0x10001ea8 are expressed as switch cases.
 */
#include <stdint.h>
#include "uart_stage1_pmu.h"

void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, int enable)
{
    uint32_t first = selector;
    switch (selector) {
    case 7: case 8: first = 2; break;
    case 17: case 18: first = 16; break;
    case 20: case 21: first = 19; break;
    case 23: case 24: first = 22; break;
    default: break;
    }
    struct stage1_pmu_view view;
    if (gx8002_uart_stage1_pmu_fill_desc(first, &view) == 0) {
        /* _clk_set_high_gate: one read of the clock select word. */
        const int32_t gate = (int8_t)view.entry[6];
        if (gate != -1) {
            const uint32_t clk_sel = *view.status;
            uint32_t selected = 0;
            if (!(first < 10u && ((UINT32_C(1) << first) & UINT32_C(579))) ||
                gx8002_uart_stage1_bit(clk_sel, gate + 1) == 0u)
                selected = gx8002_uart_stage1_bit(clk_sel, gate);
            const uint32_t power_mask =
                gx8002_uart_stage1_mask((int8_t)view.entry[4]);
            if (selected && enable)
                *view.enable = power_mask;
            else
                *view.clear = power_mask;
        }
    }

    if (gx8002_uart_stage1_pmu_fill_desc(selector, &view) != 0) return;
    uint32_t mask = gx8002_uart_stage1_mask((int8_t)view.entry[5]);   /* _clk_set_all_gate */
    switch (selector) {
    case 6: case 14: mask |= UINT32_C(0x8000); break;
    case 11: mask |= UINT32_C(8); break;
    case 13: mask |= UINT32_C(0x2000); break;
    case 17: mask |= UINT32_C(1) << 16; break;
    case 18: mask |= UINT32_C(1) << 17; break;
    case 20: mask |= UINT32_C(1) << 18; break;
    case 21: mask |= UINT32_C(1) << 19; break;
    case 23: mask |= UINT32_C(1) << 20; break;
    case 24: mask |= UINT32_C(1) << 21; break;
    default:
        if ((selector & ~UINT32_C(4)) == 1u || mask == 0) return;
        break;
    }
    if (enable) *view.enable = mask;
    else *view.clear = mask;
}
