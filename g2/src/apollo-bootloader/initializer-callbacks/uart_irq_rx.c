/* SPDX-License-Identifier: MIT
 * Locked Apollo510 UART IRQ receive drain at 0x41f776. The four platform
 * rows begin at 0x20000454 and are 0x1c bytes each. The native routine does
 * not validate the row index or child status; callers own those conditions.
 */
#include <stdint.h>

extern uint32_t opencfw_boot_uart_rx_fifo(uint32_t context, uint32_t destination,
                                          uint32_t maximum, uint32_t *received);
extern uint32_t opencfw_boot_uart_interrupt_status(uint32_t context,
                                                   uint32_t *status, uint8_t enabled);
extern uint32_t opencfw_boot_uart_interrupt_clear(uint32_t context, uint32_t status);
extern uint32_t opencfw_boot_uart_irq_dispatch(uint32_t context, uint32_t status);

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))

uint32_t opencfw_boot_uart_irq_rx_drain(uint32_t row_index,
                                        uint32_t maximum,
                                        uint8_t notify)
{
    const uintptr_t row = UINT32_C(0x20000454) + row_index * 0x1cu;
    const uintptr_t state = WORD(row + 0x10u);
    uint32_t received = 0u;
    (void)opencfw_boot_uart_rx_fifo(WORD(row + 4u),
                                    WORD(state + 0x0cu) + WORD(state + 8u),
                                    maximum, &received);
    WORD(state + 8u) += received;
    if (notify != 0u) {
        const uintptr_t callback = WORD(row + 0x14u);
        if (callback != 0u) {
            ((void (*)(uint32_t, uint32_t))callback)(WORD(state + 0x0cu),
                                                       WORD(state + 8u));
        }
        WORD(state + 8u) = 0u;
    }
    return received;
}

/* Stock 0x41f558 IRQ row wrapper. The caller supplies a byte-sized row index;
 * the returned value is the captured interrupt status, not a child status. */
uint32_t opencfw_boot_uart_irq_row(uint32_t row_index)
{
    row_index = (uint8_t)row_index;
    const uintptr_t row = UINT32_C(0x20000454) + row_index * 0x1cu;
    const uint32_t context = WORD(row + 4u);
    uint32_t status = 0u;
    (void)opencfw_boot_uart_interrupt_status(context, &status, 1u);
    (void)opencfw_boot_uart_interrupt_clear(context, status);
    (void)opencfw_boot_uart_irq_dispatch(context, status);
    if (status & 0x10u)
        (void)opencfw_boot_uart_irq_rx_drain(row_index, 0x0fu, 0u);
    if (status & 0x40u)
        (void)opencfw_boot_uart_irq_rx_drain(row_index, 0x10u, 1u);
    if (status & 1u)
        *(volatile uint8_t *)(row + 0x19u) = 1u;
    return status;
}
