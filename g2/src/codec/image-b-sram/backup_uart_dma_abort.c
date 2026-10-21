/* SPDX-License-Identifier: MIT
 * Image-B UART TX/RX DMA abort callbacks 0x10004220 and 0x10004238.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_dma_abort_10004c84(uint32_t channel);

static int32_t abort_slot(volatile uint32_t *record, uint32_t slot)
{
    int32_t channel = (int32_t)record[slot];
    if (channel >= 0) {
        (void)gx8002_image_b_dma_abort_10004c84((uint32_t)channel);
        record[slot] = UINT32_MAX;
    }
    return 0;
}

int32_t gx8002_image_b_uart_tx_abort_10004220(volatile uint32_t *record)
{
    return abort_slot(record, 0x1fu);
}

int32_t gx8002_image_b_uart_rx_abort_10004238(volatile uint32_t *record)
{
    return abort_slot(record, 0x1au);
}
