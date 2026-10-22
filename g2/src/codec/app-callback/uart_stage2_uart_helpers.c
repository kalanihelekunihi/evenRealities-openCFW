/* SPDX-License-Identifier: MIT
 * Direct stage-2 UART and shell helpers from retained bodies at
 * 0x10002ea4, 0x10002f20, 0x10002a98, 0x10006170, 0x10006184,
 * 0x10006270, and 0x1000627a. Product descriptor base 0x2000908c
 * and active port 0x20009840 are native data references.
 */
#include <stdint.h>

static volatile uint32_t *port_registers(uint32_t port)
{
    const uintptr_t descriptor = UINT32_C(0x2000908c) + (port << 7);
    return (volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(descriptor + 4u);
}

void gx8002_uart_stage2_uart_putc_raw_2ea4(uint32_t port, uint32_t value)
{
    volatile uint32_t *const uart = port_registers(port);
    while ((uart[5] & UINT32_C(0x20)) == 0) { }
    uart[0] = value & UINT32_C(0xff);
}

uint32_t gx8002_uart_stage2_uart_rx_ready_2f20(uint32_t port)
{
    return port_registers(port)[5] & 1u;
}

uint32_t gx8002_uart_stage2_console_rx_ready_2a98(void)
{
    uint32_t port = *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x20009840);
    return gx8002_uart_stage2_uart_rx_ready_2f20(port);
}

uint32_t gx8002_uart_stage2_console_getc_2a74(void);

uint32_t gx8002_uart_stage2_shell_rx_ready_6170(void)
{
    return gx8002_uart_stage2_console_rx_ready_2a98();
}

uint32_t gx8002_uart_stage2_shell_getc_6184(void)
{
    return gx8002_uart_stage2_console_getc_2a74();
}

int32_t gx8002_uart_stage2_strcmp_627a(const char *a, const char *b)
{
    for (;;) {
        const uint8_t x = (uint8_t)*a++;
        const uint8_t y = (uint8_t)*b++;
        if (x != y) return x < y ? -1 : 1;
        if (x == 0) return 0;
    }
}

/* Stock 0x10006270 (gx8002_stage2_strcmp) */
int32_t gx8002_uart_stage2_strcmp_6270(const char *a, const char *b)
{
    return gx8002_uart_stage2_strcmp_627a(a, b);
}
