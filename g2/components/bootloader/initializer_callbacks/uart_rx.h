#ifndef OPENCFW_BOOT_UART_RX_H
#define OPENCFW_BOOT_UART_RX_H
#include <stdint.h>
/* Stock32-bit pointer representation; caller retains pointed-to storage. */
typedef struct {
 uint32_t destination, requested_bytes, transferred_out, timeout_poll_count;
 uint32_t callback, callback_context, reserved;
 uint32_t tail[6];
 uint8_t mode, padding[3];
} opencfw_boot_uart_rx_descriptor;
_Static_assert(sizeof(opencfw_boot_uart_rx_descriptor)==56,"stock transfer descriptor");
uint32_t opencfw_boot_uart_rx_claim(uint32_t,uint32_t);
uint32_t opencfw_boot_uart_rx_cancel(uint32_t);
uint32_t opencfw_boot_uart_rx_fifo(uint32_t,uint32_t,uint32_t,uint32_t *);
uint32_t opencfw_boot_uart_rx_collect(uint32_t);
void opencfw_boot_uart_rx_pump(uint32_t);
uint32_t opencfw_boot_uart_rx_start(uint32_t,uint32_t);
uint32_t opencfw_boot_uart_rx_blocking(uint32_t,uint32_t);
#endif
