/* Bounded tracepoint reply RAM at native 0x2037bbc8.
 * Native result constructor clears 0x206 bytes. This reserves that observed
 * span without an initializer; full allocation extent and startup stay open. */
#include <stdint.h>

uint8_t audio_tracepoint_reply_buffer[0x206]
    __attribute__((section(".bss.opencfw.tracepoint.reply"), aligned(4), used));

_Static_assert(sizeof(audio_tracepoint_reply_buffer) == 0x206u,
               "native tracepoint reply clear extent");
