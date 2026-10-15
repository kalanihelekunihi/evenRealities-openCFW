/* Apollo LV text line width, native 0x489934..0x4899a3. */
#include <stdint.h>

extern void audio_uart_text_next_glyph_489b3c(const char *text,
                                               uint32_t *glyph,
                                               uint32_t *next,
                                               uint32_t *position);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *font,
                                                     uint32_t glyph,
                                                     uint32_t next);

int32_t audio_uart_text_line_width_489934(const char *text, uint32_t length,
                                          const void *font, int32_t letter_spacing) {
    if (text == 0 || font == 0 || *text == '\0' || length == 0u) return 0;
    uint32_t position = 0u;
    uint32_t glyph = (uint32_t)(uintptr_t)font;
    uint32_t next = length;
    int32_t width = 0;
    while (position < length) {
        audio_uart_text_next_glyph_489b3c(text, &glyph, &next, &position);
        int32_t advance = audio_uart_font_glyph_advance_4d57f4(font, glyph, next);
        if (advance > 0)
            width = (int32_t)((uint32_t)width + (uint32_t)letter_spacing +
                              (uint32_t)advance);
    }
    if (width > 0)
        width = (int32_t)((uint32_t)width - (uint32_t)letter_spacing);
    return width;
}
