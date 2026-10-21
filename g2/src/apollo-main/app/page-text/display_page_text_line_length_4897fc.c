/* Apollo LV text line selection, native 0x4897fc..0x489933. */
#include <stdint.h>

extern uint32_t audio_uart_text_line_segment_489698(const char *text,
                                                     const void *font,
                                                     int32_t letter_spacing,
                                                     int32_t max_width,
                                                     uint32_t flags,
                                                     int32_t *width,
                                                     uint8_t *scratch);
extern uint32_t audio_uart_text_decode_489c5e(const char *text,
                                               uint32_t *bytes);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *font,
                                                     uint32_t glyph,
                                                     uint32_t next);

uint32_t audio_uart_text_line_length_4897fc(const char *text,
                                             uint32_t count,
                                             const void *font,
                                             int32_t letter_spacing,
                                             int32_t max_width,
                                             int32_t *out_width,
                                             uint32_t flags) {
    if (out_width != 0) *out_width = 0;
    if (text == 0 || *text == '\0' || font == 0) return 0;

    uint32_t position = 0;
    if ((flags & 3u) != 0u) {
        while (position < count && text[position] != '\n' &&
               text[position] != '\r' && text[position] != '\0')
            position++;
        if (position < count && text[position] != '\0') position++;
        if (out_width != 0) *out_width = -1;
        return position;
    }

    if ((flags & 1u) != 0u) max_width = 0x1fffffff;
    uint8_t scratch[4];
    scratch[0] = 0;
    int32_t width = 0;
    while (position < count && text[position] != '\0' && max_width > 0) {
        int32_t segment_width = 0;
        uint32_t consumed = audio_uart_text_line_segment_489698(
            text + position, font, letter_spacing, max_width,
            (uint8_t)(flags | (position == 0u ? 4u : 0u)),
            &segment_width, scratch);
        max_width = (int32_t)((uint32_t)max_width - (uint32_t)segment_width);
        width = (int32_t)((uint32_t)width + (uint32_t)segment_width);
        if (consumed == 0u) break;
        position += consumed;
        if (*text == '\n' || *text == '\r') break;
        if (text[position] == '\n' || text[position] == '\r') {
            position++;
            break;
        }
    }
    if (position == 0u) {
        uint32_t glyph = audio_uart_text_decode_489c5e(text, &position);
        if (out_width != 0)
            width = audio_uart_font_glyph_advance_4d57f4(font, glyph, 0u);
    }
    if (out_width != 0) *out_width = width;
    return position;
}
