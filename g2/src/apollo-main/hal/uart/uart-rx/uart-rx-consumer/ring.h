#ifndef UART3_RX_RING_H
#define UART3_RX_RING_H
#include <stdint.h>
typedef struct {uint8_t *storage;uint32_t mask,read,write;} uart3_ring_t;
/* Same layout as upstream ring_buffer_t {buffer, buffer_mask, tail_index, head_index};
 * operate on it with third-party/upstream/ring-buffer/ringbuffer.c. */
#endif
