/* SPDX-License-Identifier: MIT
 * Stock UART receive drain: discard up to 32 bytes from the RX FIFO. */
#include <stdint.h>

extern uint32_t am_hal_uart_fifo_read(void *pHandle, uint8_t *pui8Data, uint32_t ui32NumBytes,
                                      uint32_t *pui32NumBytesRead);

uint32_t opencfw_boot_uart_rx_drain32_abi(void *handle)
{
    return am_hal_uart_fifo_read(handle, 0, 32u, 0);
}
