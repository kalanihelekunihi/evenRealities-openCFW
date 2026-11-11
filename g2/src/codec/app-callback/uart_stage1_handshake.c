/* SPDX-License-Identifier: MIT
 * UART boot stage-1 handshake at 0x100006d8. Stock literal 0x10001e5c
 * contains "OK\0"; the UART-base and argument words reside at
 * 0x20002014 and 0x20002010 respectively.
 */
#include <stdint.h>
#include "uart_stage1_state.h"

extern void gx8002_uart_stage1_railcfg(void);
extern uint32_t gx8002_uart_stage1_pmu_get_bit0(void);
extern uint32_t gx8002_uart_stage1_pmu_get_bit1(void);
extern void gx8002_uart_stage1_bringup(uint32_t first, uint32_t second);
extern void gx8002_uart_stage1_mdelay(int32_t milliseconds);

void gx8002_uart_stage1_handshake(void)
{
    gx8002_uart_stage1_railcfg();
    if (gx8002_uart_stage1_pmu_get_bit0() == 1u ||
        gx8002_uart_stage1_pmu_get_bit1() == 1u) {
        gx8002_uart_stage1_bringup(0, gx8002_uart_stage1_state.host_word);
    } else {
        gx8002_uart_stage1_bringup(1, 0);
    }

    static const uint8_t gx8002_uart_stage1_expected[] = {'O', 'K', 0};
    uint32_t matched = 0;
    for (;;) {
        volatile uint32_t *const uart =
            (volatile uint32_t *)(uintptr_t)gx8002_uart_stage1_state.uart_base;
        const uint8_t request[] = {'G', 'E', 'T'};
        for (unsigned i = 0; i < 3; ++i) {
            while ((uart[5] & UINT32_C(0x40)) == 0) { }
            uart[0] = request[i];
        }
        while ((uart[5] & 1u) != 0) {
            const uint32_t received = uart[0] & UINT32_C(0xff);
            if (received == gx8002_uart_stage1_expected[matched]) {
                ++matched;
                if (gx8002_uart_stage1_expected[matched] == 0) return;
            } else {
                matched = 0;
            }
        }
        gx8002_uart_stage1_mdelay(1);
    }
}
