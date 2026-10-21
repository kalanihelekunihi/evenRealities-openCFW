#ifndef UART3_RX_RING_H
#define UART3_RX_RING_H
#include <stdint.h>
typedef struct {uint8_t *storage;uint32_t mask,read,write;} uart3_ring_t;
uint32_t uart3_ring_full(const uart3_ring_t *);
void uart3_ring_put(uart3_ring_t *,uint32_t byte);
void uart3_ring_write(uart3_ring_t *,const uint8_t *,uint32_t);
#endif
