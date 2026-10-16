/* Apollo LV text width with hash-state filtering, native 0x4899a4..0x489a37. */
#include <stdint.h>

extern void audio_uart_text_next_glyph_489b3c(const char *text,
                                               uint32_t *glyph,
                                               uint32_t *next,
                                               uint32_t *position);
extern uint32_t audio_uart_text_hash_state_489652(uint8_t *state,
                                                   uint32_t glyph);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *font,
                                                     uint32_t glyph,
                                                     uint32_t next);

int32_t audio_uart_text_width_4899a4(const char *text, uint32_t length,
                                      const void *font, int32_t spacing,
                                      uint32_t flags) {
    if (text == 0 || font == 0 || *text == '\0' || length == 0u) return 0;
    uint32_t position = 0u;
    uint32_t glyph = 0u;
    uint32_t next = 0u;
    uint8_t state = 0u;
    int32_t width = 0;
    while (text[position] != '\0' && position < length) {
        audio_uart_text_next_glyph_489b3c(text, &glyph, &next, &position);
        if ((flags & 8u) != 0u &&
            audio_uart_text_hash_state_489652(&state, glyph) != 0u)
            continue;
        int32_t advance = audio_uart_font_glyph_advance_4d57f4(font, glyph, next);
        if (advance >= 1)
            width = (int32_t)((uint32_t)width + (uint32_t)advance + (uint32_t)spacing);
    }
    if (width >= 1) width = (int32_t)((uint32_t)width - (uint32_t)spacing);
    return width;
}
