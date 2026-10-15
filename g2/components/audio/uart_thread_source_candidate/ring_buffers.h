#ifndef OPENCFW_RING_BUFFERS_H
#define OPENCFW_RING_BUFFERS_H
#include <stdint.h>
#include <stddef.h>

struct audio_ring_buffers_layout {
    uint8_t decode[64];
    uint8_t encode[64];
};
_Static_assert(sizeof(struct audio_ring_buffers_layout)==128u,"ring buffer size");
_Static_assert(offsetof(struct audio_ring_buffers_layout,encode)==64u,"ring buffer adjacency");

extern struct audio_ring_buffers_layout audio_ring_buffers;
extern uint8_t audio_ring_tx_buffer[256];
#endif
