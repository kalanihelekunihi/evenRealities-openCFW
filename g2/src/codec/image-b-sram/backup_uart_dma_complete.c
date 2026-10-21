/* SPDX-License-Identifier: MIT
 * Image-B UART DMA completion callbacks 0x10004034 and 0x10004054,
 * plus transmit-empty wait 0x10004584. Native calls stored callback words
 * directly and provides no timeout or null branch.
 */
#include <stdint.h>

extern void gx8002_image_b_dma_release_10004c7c(uint32_t channel);
extern void gx8002_image_b_dcache_clean_invalidate_range_10004f10(
    uint32_t address, int32_t length);

void gx8002_image_b_uart_tx_empty_wait_10004584(uint32_t port)
{
    volatile uint32_t *port_table =
        (volatile uint32_t *)(uintptr_t)(UINT32_C(0x20016b84) + port * 128u);
    volatile uint32_t *status =
        (volatile uint32_t *)(uintptr_t)(port_table[1] + 20u);
    while ((*status & 64u) == 0u) { }
}

typedef void (*uart_callback_t)(uint32_t port, uint32_t context);

void gx8002_image_b_uart_transmit_complete_10004034(volatile uint32_t *record)
{
    gx8002_image_b_dma_release_10004c7c(record[0x1fu]);
    record[0x1fu] = UINT32_MAX;
    gx8002_image_b_uart_tx_empty_wait_10004584(record[0]);
    uart_callback_t callback = (uart_callback_t)(uintptr_t)record[0x1bu];
    callback(record[0], record[0x1cu]);
}

void gx8002_image_b_uart_receive_complete_10004054(volatile uint32_t *record)
{
    gx8002_image_b_dma_release_10004c7c(record[0x1au]);
    record[0x1au] = UINT32_MAX;
    gx8002_image_b_dcache_clean_invalidate_range_10004f10(
        record[0x18u], (int32_t)record[0x19u]);
    uart_callback_t callback = (uart_callback_t)(uintptr_t)record[0x16u];
    callback(record[0], record[0x17u]);
}
