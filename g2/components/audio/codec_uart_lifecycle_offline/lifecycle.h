#ifndef CODEC_UART_LIFECYCLE_OFFLINE_H
#define CODEC_UART_LIFECYCLE_OFFLINE_H
#include <stdint.h>
#include "../uart_rx_consumer_offline/ring.h"
/* Fixed ARM addresses, log-disabled, power-of-two ring initialization only.
 * Peripheral/config/GPIO operations remain external providers. */
void codec_ring_initialize(uart3_ring_t *,uint8_t *,uint32_t);
void codec_channel_callback(uint32_t,uint32_t);
uint32_t codec_channel_enable(uint32_t);
uint32_t codec_channel_disable(uint32_t);
uint32_t codec_channel_baud(uint32_t,uint32_t);
int32_t codec_uart_initialize(void);
int32_t codec_uart_close(void);
int32_t codec_uart_baud(uint32_t);
int32_t codec_host_initialize(void);
void codec_rx_callback(const uint8_t *,uint32_t);
#endif
