/* SPDX-License-Identifier: MIT
 * Stage-2 native 0x10002fb4 maps one-hot request masks to indices.
 * Native 0x10005a7c polls the shell for control-C and sets a RAM flag.
 * The RAM address is the literal at stock 0x10005aa4.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage2_mask_index_2fb4(uint32_t value,
                                               const uint32_t *fallback,
                                               uint32_t explicit_value)
{
    if (explicit_value == 0) value = *fallback;
    switch (value) {
    case 0x004: return 1;
    case 0x008: return 2;
    case 0x010: return 3;
    case 0x020: return 4;
    case 0x040: return 5;
    case 0x080: return 6;
    case 0x100: return 7;
    case 0x200: return 8;
    case 0x400: return 9;
    default: return 0;
    }
}

uint32_t gx8002_uart_stage2_shell_rx_ready_6170(void);
uint32_t gx8002_uart_stage2_shell_getc_6184(void);

uint32_t gx8002_uart_stage2_poll_interrupt_5a7c(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2000997c);
    if (state[0] == 0 && gx8002_uart_stage2_shell_rx_ready_6170() != 0) {
        if (gx8002_uart_stage2_shell_getc_6184() == 3) {
            state[1] = 1;
            return 1;
        }
    }
    return 0;
}
