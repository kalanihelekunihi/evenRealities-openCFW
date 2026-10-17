/* Mutable I2S handle acquired by the stock codec initialization path. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.codec.i2s_handle"), used))
void *g2_codec_i2s_handle;

_Static_assert(sizeof(g2_codec_i2s_handle) == 4, "codec I2S handle extent");
