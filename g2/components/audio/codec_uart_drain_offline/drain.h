#ifndef CODEC_UART_DRAIN_H
#define CODEC_UART_DRAIN_H
#include "../uart_rx_consumer_offline/ring.h"
uint32_t codec_ring_empty(const uart3_ring_t *);
uint32_t codec_ring_get(uart3_ring_t *,uint8_t *);
uint32_t codec_ring_read(uart3_ring_t *,uint8_t *,uint32_t);
uint32_t codec_uart_read(uint8_t *,uint32_t);
#endif
