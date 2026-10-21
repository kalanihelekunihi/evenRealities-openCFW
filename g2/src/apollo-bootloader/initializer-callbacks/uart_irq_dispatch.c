/* SPDX-License-Identifier: MIT
 * Locked Apollo510 UART IRQ descendants: 0x42377c dispatch and DMA leaves
 * 0x422d20/4c/7a and 0x422fde. Register effects are source-owned; physical
 * interrupt and DMA timing remains a platform qualification.
 */
#include <stdint.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BYTE(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define UART_BASE UINT32_C(0x40039000)

extern void opencfw_boot_uart_rx_pump(uint32_t context);
extern void opencfw_boot_uart_tx_pump(uint32_t context);
extern uint32_t opencfw_boot_uart_rx_fifo(uint32_t, uint32_t, uint32_t, uint32_t *);
extern uint32_t opencfw_boot_uart_rx_cancel(uint32_t context);
extern void opencfw_boot_delay_us_math(uint32_t microseconds);

static uintptr_t uart_registers(uint32_t context)
{
    return UART_BASE + (WORD(context + 0x28u) << 12);
}

void opencfw_boot_uart_dma_disable(uint32_t context)
{
    const uintptr_t base = uart_registers(context);
    WORD(base + 0x48u) = 0u;
    WORD(base + 4u) &= ~UINT32_C(0x10);
    WORD(base + 4u) &= ~UINT32_C(0x20);
}

void opencfw_boot_uart_dma_rx_stop(uint32_t context)
{
    const uintptr_t base = uart_registers(context);
    WORD(base + 0x48u) = 0u;
    WORD(base + 4u) &= ~UINT32_C(0x20);
    WORD(base + 0x50u) &= ~UINT32_C(0x0fff);
}

uint32_t opencfw_boot_uart_dma_error(uint32_t module, uint32_t status)
{
    status |= WORD(UART_BASE + (module << 12) + 0x3cu);
    if (status & 0x40u) return UINT32_C(0x08000006);
    if (status & 0x80u) return UINT32_C(0x08000007);
    if (status & 0x100u) return UINT32_C(0x08000008);
    if (status & 0x200u) return UINT32_C(0x08000009);
    if (status & 0x400u) return UINT32_C(0x0800000a);
    if (status & 0x1000u) return UINT32_C(0x0800000b);
    return 0u;
}

void opencfw_boot_uart_dma_recover(uint32_t context)
{
    const uintptr_t base = uart_registers(context);
    const uint32_t clock_was_enabled = (WORD(base + 0x30u) & 0x4000u) != 0u;
    if (clock_was_enabled) {
        WORD(base + 0x30u) &= ~UINT32_C(0x4000);
        WORD(base + 0x30u) &= ~UINT32_C(0x0800);
    }
    WORD(base + 0x30u) &= ~UINT32_C(0x0200);
    if (WORD(base + 0x18u) & 8u)
        opencfw_boot_delay_us_math(UINT32_C(10000000) /
                                   WORD(context + 0x30u) + 1u);
    if (BYTE(context + 0x11bu))
        opencfw_boot_uart_dma_rx_stop(context);
    (void)opencfw_boot_uart_rx_fifo(context, 0u, 0x20u, 0);
    (void)opencfw_boot_uart_rx_cancel(context);
    if (clock_was_enabled)
        WORD(base + 0x30u) |= UINT32_C(0x4000);
    WORD(base + 0x30u) |= UINT32_C(0x0200);
}

uint32_t opencfw_boot_uart_irq_dispatch(uint32_t context, uint32_t status)
{
    if (context == 0u ||
        (WORD(context) & UINT32_C(0x01ffffff)) != UINT32_C(0x01ea9e06))
        return 2u;
    const uint32_t module = WORD(context + 0x28u);
    const uintptr_t base = UART_BASE + (module << 12);
    if (BYTE(context + 0x11bu) == 0u) {
        if (status & 0x50u)
            opencfw_boot_uart_rx_pump(context);
        if (status & 0x20u)
            opencfw_boot_uart_tx_pump(context);
        if (status & 1u)
            BYTE(context + 0xdeu) = 1u;
    } else {
        if (WORD(context + 0xe8u))
            WORD(WORD(context + 0xe8u)) = WORD(context + 0xe4u) -
                (WORD(base + 0x50u) & 0x0fffu);
        if (status & 0x40u)
            opencfw_boot_uart_dma_recover(context);
        if (status & 0x1000u)
            opencfw_boot_uart_dma_rx_stop(context);
        if (status & 0x800u) {
            const uintptr_t callback = WORD(context + 0xf0u);
            if (callback) {
                ((void (*)(uint32_t, uint32_t))callback)(
                    opencfw_boot_uart_dma_error(module, status),
                    WORD(context + 0xf4u));
                WORD(context + 0xf0u) = 0u;
            }
            opencfw_boot_uart_dma_disable(context);
        }
        BYTE(context + 0x11bu) = 0u;
    }
    return 1u;
}
