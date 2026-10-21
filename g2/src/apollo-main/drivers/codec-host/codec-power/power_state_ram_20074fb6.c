/* Mutable GX8002 power state observed by stock power-on/off children. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.codec.power_state"), used))
uint8_t g2_codec_power_state;

_Static_assert(sizeof(g2_codec_power_state) == 1, "codec power state extent");
