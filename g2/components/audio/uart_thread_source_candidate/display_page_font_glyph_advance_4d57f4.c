/* Apollo LV font glyph advance, native 0x4d57f4..0x4d5845. */
#include <stdint.h>

extern uint32_t audio_uart_font_glyph_is_missing_4d559c(uint32_t glyph);
extern uint32_t audio_uart_font_glyph_describe_4d56c0(const void *font,
                                                        void *descriptor,
                                                        uint32_t glyph,
                                                        uint32_t next);

int32_t audio_uart_font_glyph_advance_4d57f4(const void *font,
                                               uint32_t glyph,
                                               uint32_t next) {
    if (audio_uart_font_glyph_is_missing_4d559c(glyph) != 0u) return 0;
    uint8_t descriptor[32];
    audio_uart_font_glyph_describe_4d56c0(font, descriptor, glyph, next);
    return (int32_t)((uint32_t)descriptor[4] | ((uint32_t)descriptor[5] << 8u));
}
