/* Stock registry ring-connect buffer at 0x2010f4cc.
 * The 0x850-byte reservation reaches, but does not include, the state byte. */
#include <stdint.h>

uint8_t audio_registry_ring_connect_buffer[0x850]
    __attribute__((section(".bss.opencfw.registry.ring_connect_buffer"), used, aligned(4)));
_Static_assert(sizeof audio_registry_ring_connect_buffer == 0x850u,
               "stock buffer-to-state interval");
