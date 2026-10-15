/* Apollo LV UTF-8 packed encoder, native 0x489bac..0x489c5d. */
#include <stdint.h>

uint32_t audio_uart_text_utf8_encode_489bac(uint32_t glyph) {
    if (glyph < 0x80u) return glyph;
    if (glyph < 0x800u)
        return (0xc0u | (glyph >> 6u)) |
               ((0x80u | (glyph & 0x3fu)) << 8u);
    if (glyph < 0x10000u)
        return (0xe0u | (glyph >> 12u)) |
               ((0x80u | ((glyph >> 6u) & 0x3fu)) << 8u) |
               ((0x80u | (glyph & 0x3fu)) << 16u);
    if (glyph < 0x110000u)
        return (0xf0u | (glyph >> 18u)) |
               ((0x80u | ((glyph >> 12u) & 0x3fu)) << 8u) |
               ((0x80u | ((glyph >> 6u) & 0x3fu)) << 16u) |
               ((0x80u | (glyph & 0x3fu)) << 24u);
    return 0u;
}
