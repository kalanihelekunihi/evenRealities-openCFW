/* SPDX-License-Identifier: MIT
 * Stage-2 UART byte I/O bodies 0x10002ec8/0x10002ee8 and console wrappers
 * 0x10002a74/0x10002a84. Port descriptors in SRAM are product inputs.
 */
#include <stdint.h>

static volatile uint32_t *uart_port(uint32_t port)
{
    const uintptr_t descriptor = UINT32_C(0x2000908c) + (port << 7);
    const uintptr_t base = *(const volatile uint32_t *)(descriptor + 4u);
    return (volatile uint32_t *)base;
}

uint32_t gx8002_uart_stage2_uart_getc_2ec8(uint32_t port)
{
    volatile uint32_t *const uart = uart_port(port);
    while ((uart[5] & 1u) == 0) { }
    return uart[0] & 0xffu;
}

void gx8002_uart_stage2_uart_putc_2ee8(uint32_t port, uint32_t character)
{
    volatile uint32_t *const uart = uart_port(port);
    if (character == 10u) {
        while ((uart[5] & 0x20u) == 0) { }
        uart[0] = 13u;
    }
    while ((uart[5] & 0x20u) == 0) { }
    uart[0] = character & 0xffu;
}

uint32_t gx8002_uart_stage2_console_getc_2a74(void)
{
    const uint32_t port =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x20009840);
    return gx8002_uart_stage2_uart_getc_2ec8(port);
}

void gx8002_uart_stage2_console_putc_2a84(uint32_t character)
{
    const uint32_t port =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x20009840);
    gx8002_uart_stage2_uart_putc_2ee8(port, character);
}

extern void gx8002_uart_stage2_dispatch_4a48(uint32_t selector,
                                               uint32_t enabled);
extern uint32_t gx8002_uart_stage2_clock_rate_4b50(uint32_t selector);
extern uint32_t gx8002_uart_stage2_uart_apply_2c38(
    volatile uint32_t *descriptor);

uint32_t gx8002_uart_stage2_uart_config_2e28(uint32_t port, uint32_t baud)
{
    if (port > 1u) return UINT32_MAX;
    gx8002_uart_stage2_dispatch_4a48((port != 0u) + 17u, 1u);
    uint32_t rate = gx8002_uart_stage2_clock_rate_4b50(16u);
    const uint32_t remainder = rate % 1000000u;
    if (remainder <= 100u) rate -= remainder;
    else if (1000000u - remainder <= 100u)
        rate = rate + 1000000u - remainder;
    volatile uint32_t *const descriptor = (volatile uint32_t *)
        (uintptr_t)(UINT32_C(0x2000908c) + (port << 7));
    descriptor[0x0c / 4] = rate;
    descriptor[0x10 / 4] = baud;
    return gx8002_uart_stage2_uart_apply_2c38(descriptor);
}
