/* Isolated bridge to static TX state machine. Rename public symbols from the
 * included unit so they cannot collide with selected archive providers. */
#define am_hal_uart_buffer_configure irq_local_am_hal_uart_buffer_configure
#define am_hal_uart_fifo_write irq_local_am_hal_uart_fifo_write
#define am_hal_uart_initialize irq_local_am_hal_uart_initialize
#define write_transaction_save irq_local_write_transaction_save
#include "../uart-tx/am_hal_uart.c"
void uart_irq_write_sm(void *handle) { nonblocking_write_sm(handle); }
