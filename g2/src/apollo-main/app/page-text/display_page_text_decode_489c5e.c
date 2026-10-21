/* Apollo LV UTF-8 decoder, native 0x489c5e..0x489dbb. */
#include <stdint.h>

uint32_t audio_uart_text_decode_489c5e(const char *text, uint32_t *offset) {
    uint32_t local = 0;
    if (offset == 0) offset = &local;
    if (text == 0) return 0;
    uint32_t pos = *offset;
    uint8_t first = (uint8_t)text[pos];
    if (first == 0) return 0;
    if (first < 0x80u) {
        *offset = pos + 1u;
        return first;
    }
    uint32_t length, value;
    if ((first & 0xe0u) == 0xc0u) {
        length = 2u;
        value = first & 0x1fu;
    } else if ((first & 0xf0u) == 0xe0u) {
        length = 3u;
        value = first & 0x0fu;
    } else if ((first & 0xf8u) == 0xf0u) {
        length = 4u;
        value = first & 0x07u;
    } else {
        *offset = pos + 1u;
        return 0;
    }
    *offset = ++pos;
    for (uint32_t i = 1u; i < length; ++i) {
        uint8_t next = (uint8_t)text[pos];
        if ((next & 0xc0u) != 0x80u) return 0;
        value = (value << 6u) | (next & 0x3fu);
        *offset = ++pos;
    }
    return value;
}
