/* SPDX-License-Identifier: MIT
 * UART boot stage-1 bringup at 0x100005c4. The stock literal pool names
 * 0x20002008 (state) and 0x20002014 (UART base storage). The latter is
 * initialized here before the UART I/O helpers use it.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled);
extern void gx8002_uart_stage1_beacon(uint32_t first, uint32_t second);

void gx8002_uart_stage1_bringup(uint32_t first, uint32_t second)
{
    const volatile uint32_t *const state =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002008);
    if (state[0] != 0) {
        gx8002_uart_stage1_beacon(UINT32_C(0x1c200), 0);
        return;
    }
    const uint32_t mode = state[1];
    volatile uint32_t *const uart_base_storage =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20002014);
    *uart_base_storage = mode != 1u ? UINT32_C(0xa0100000) : UINT32_C(0xa0200000);
    gx8002_uart_stage1_pmu_dispatch(0x10u, 1u);
    gx8002_uart_stage1_pmu_dispatch(0x11u, 1u);
    gx8002_uart_stage1_pmu_dispatch(0x12u, 1u);
    gx8002_uart_stage1_beacon(second, first);
}
