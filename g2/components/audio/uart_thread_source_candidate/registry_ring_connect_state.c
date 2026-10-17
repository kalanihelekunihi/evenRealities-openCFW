/* Directly referenced byte at native RAM 0x2010fd1c.
 * Absolute placement and any indirect aliases remain to be established. */
#include <stdint.h>

uint8_t audio_registry_ring_connect_state
    __attribute__((section(".bss.opencfw.registry.ring_connect_state"), used));
