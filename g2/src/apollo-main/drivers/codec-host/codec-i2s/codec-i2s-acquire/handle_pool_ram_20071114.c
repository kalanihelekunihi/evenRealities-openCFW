/* Two 100-byte mutable I2S handle rows selected by the stock acquire body. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.codec.i2s_handle_pool"), used))
uint8_t g2_codec_i2s_handle_pool[2u * 100u];

_Static_assert(sizeof(g2_codec_i2s_handle_pool) == 200, "I2S handle rows extent");
