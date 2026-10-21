/* Apollo LV CJK line-break classification, native 0x4894d0..0x489545. */
#include <stdint.h>

uint32_t audio_uart_text_is_cjk_4894d0(uint32_t glyph) {
    return (glyph - 0x4e00u < 0x5200u) ||
           (glyph - 0xff01u < 0x5eu) ||
           (glyph - 0x3000u < 0x40u) ||
           (glyph - 0x2e80u < 0x80u) ||
           (glyph - 0x31c0u < 0x30u) ||
           (glyph - 0x3040u < 0xc0u) ||
           (glyph - 0xfe10u < 0x10u) ||
           (glyph - 0xfe30u < 0x20u);
}
