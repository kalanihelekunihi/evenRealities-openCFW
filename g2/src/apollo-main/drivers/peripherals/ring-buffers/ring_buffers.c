/* Native decode 0x200f86bc, encode 0x200f86fc, tx 0x2037c8a0.
 * Product linker placement and memory initialization remain separate gates. */
#include "ring_buffers.h"

struct audio_ring_buffers_layout audio_ring_buffers;
uint8_t audio_ring_tx_buffer[256];
