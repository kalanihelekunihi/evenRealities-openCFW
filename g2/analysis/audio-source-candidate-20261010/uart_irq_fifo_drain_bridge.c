/* Fixture bridge to selected Ambiq RX FIFO source, stock 0x58e352. */
#include "../../components/audio/uart_rx_stream_offline/am_hal_uart.c"
uint32_t uart_irq_fifo_drain(void *handle)
{
    return am_hal_uart_fifo_read(handle, (void *)0, 32u, (void *)0);
}
