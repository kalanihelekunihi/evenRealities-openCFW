/* SPDX-License-Identifier: MIT
 * Native serial download helpers at 0x100055e0 and 0x10005604.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_uart_putc_raw_2ea4(uint32_t, uint32_t);

void gx8002_uart_stage2_console_putc_2a60(uint32_t value)
{
    uint32_t port = *(volatile const uint32_t *)(uintptr_t)
        UINT32_C(0x20009840);
    gx8002_uart_stage2_uart_putc_raw_2ea4(port, value);
}

uint32_t gx8002_uart_stage2_serialdown_done_55e0(
    uint32_t port, const char *phase)
{
    (void)port;
    volatile uint32_t *flag = (volatile uint32_t *)(uintptr_t)
        (*phase == 'L' ? UINT32_C(0x2000a154) : UINT32_C(0x2000a150));
    *flag = 1u;
    return 0;
}

void gx8002_uart_stage2_serialdown_finish_token_5604(void)
{
    static const char token[] = "~fin~";
    for (uint32_t i = 0; i < sizeof(token) - 1u; ++i)
        gx8002_uart_stage2_console_putc_2a60((uint8_t)token[i]);
}
