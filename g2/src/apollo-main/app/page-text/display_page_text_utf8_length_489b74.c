/* Apollo LV UTF-8 leading-byte length, native 0x489b74..0x489bab. */
#include <stdint.h>

uint32_t audio_uart_text_utf8_length_489b74(const char *text) {
    uint8_t first = (uint8_t)*text;
    if (first < 0x80u) return 1u;
    if ((first & 0xe0u) == 0xc0u) return 2u;
    if ((first & 0xf0u) == 0xe0u) return 3u;
    if ((first & 0xf8u) == 0xf0u) return 4u;
    return 0u;
}
