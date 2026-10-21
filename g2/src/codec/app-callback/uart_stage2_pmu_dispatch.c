/* SPDX-License-Identifier: MIT
 * UART stage-2 PMU dispatch at 0x10004a48. The two indirect native jump
 * tables at 0x1000812c and 0x10008174 are expressed as switch cases.
 */
#include <stdint.h>
#include "uart_stage1_pmu.h"

void gx8002_uart_stage2_dispatch_4a48(uint32_t selector, int enable)
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
    if (gx8002_uart_stage2_pmu_fill_desc(first, &view) == 0) {
        const int32_t gate = (int8_t)view.entry[6];
        if (gate != -1) {
            const uint32_t gate_bit = (uint32_t)gate & 31u;
            uint32_t skip_status = 0;
            if (first < 10u && ((UINT32_C(1) << first) & UINT32_C(579)))
                skip_status = (*view.status >> ((gate_bit + 1u) & 31u)) & 1u;
            const uint32_t power_mask = UINT32_C(1) <<
                ((uint32_t)(int8_t)view.entry[4] & 31u);
            if (!skip_status && ((*view.status >> gate_bit) & 1u) && enable)
                *view.enable = power_mask;
            else
                *view.clear = power_mask;
        }
    }

    if (gx8002_uart_stage2_pmu_fill_desc(selector, &view) != 0) return;
    uint32_t mask = UINT32_C(1) << ((uint32_t)(int8_t)view.entry[5] & 31u);
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
