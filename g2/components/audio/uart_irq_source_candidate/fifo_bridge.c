/* Isolated bridge to the selected RX FIFO source. The public function is
 * renamed locally so this object can coexist with its selected archive unit. */
#define am_hal_uart_fifo_read irq_local_am_hal_uart_fifo_read
#include "../uart_rx_stream_offline/am_hal_uart.c"
uint32_t uart_irq_fifo_drain(void *handle) {
    return irq_local_am_hal_uart_fifo_read(handle, (uint8_t *)0, 32u, (uint32_t *)0);
}
