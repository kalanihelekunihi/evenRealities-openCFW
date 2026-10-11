/* SPDX-License-Identifier: MIT
 * Image-B per-port abort routes 0x10004708 and 0x10004724. Both inspect
 * the same native port-record flag then call their distinct DMA abort path.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_tx_abort_10004220(volatile uint32_t *record);
extern int32_t gx8002_image_b_uart_rx_abort_10004238(volatile uint32_t *record);

static volatile uint32_t *port_record(uint32_t port)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
}

int32_t gx8002_image_b_uart_tx_abort_route_10004708(uint32_t port)
{
    volatile uint32_t *record = port_record(port);
    if (record[0x2cu / 4u] != 0u)
        (void)gx8002_image_b_uart_tx_abort_10004220(record);
    return 0;
}

int32_t gx8002_image_b_uart_rx_abort_route_10004724(uint32_t port)
{
    volatile uint32_t *record = port_record(port);
    if (record[0x2cu / 4u] != 0u)
        (void)gx8002_image_b_uart_rx_abort_10004238(record);
    return 0;
}
