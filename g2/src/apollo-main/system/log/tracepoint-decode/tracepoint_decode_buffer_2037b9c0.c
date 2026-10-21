/* Bounded tracepoint protobuf decode RAM at native 0x2037b9c0.
 * Native 0x5ee8bc clears 0x206 bytes; this reserves that observed span
 * without a startup value. Final allocation extent and sharing are open. */
#include <stdint.h>

uint8_t audio_tracepoint_decode_buffer[0x206]
    __attribute__((section(".bss.opencfw.tracepoint.decode"), aligned(4), used));

_Static_assert(sizeof(audio_tracepoint_decode_buffer) == 0x206u,
               "native tracepoint decode clear extent");
