/* Fixture-only bridge to the already selected pinned UART TX source body. */
#include "../../components/audio/uart_tx_offline/am_hal_uart.c"
void uart_irq_write_sm(void *handle) { nonblocking_write_sm(handle); }
