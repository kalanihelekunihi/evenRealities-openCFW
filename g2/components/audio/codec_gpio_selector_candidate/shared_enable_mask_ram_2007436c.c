/* Shared codec enable mask used by the GPIO selector. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.codec.shared_enable_mask"), used))
volatile uint32_t g2_codec_shared_enable_mask;

_Static_assert(sizeof(g2_codec_shared_enable_mask) == 4, "codec enable mask extent");
