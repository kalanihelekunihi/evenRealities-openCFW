/* Apollo LV line segment search, native 0x489698..0x4897f5. */
#include <stdint.h>

extern uint32_t audio_uart_text_decode_489c5e(const char *text,
                                               uint32_t *offset);
extern uint32_t audio_uart_text_hash_state_489652(uint8_t *state,
                                                  uint32_t glyph);
extern int32_t audio_uart_font_glyph_advance_4d57f4(const void *font,
                                                     uint32_t glyph,
                                                     uint32_t next);
extern uint32_t audio_uart_text_is_break_char_4894a4(uint32_t glyph);
extern uint32_t audio_uart_text_is_cjk_4894d0(uint32_t glyph);

uint32_t audio_uart_text_line_segment_489698(const char *text,
                                              const void *font,
                                              int32_t letter_spacing,
                                              int32_t max_width,
                                              uint32_t flags,
                                              int32_t *out_width,
                                              uint8_t *state) {
    if (text == 0 || *text == '\0' || font == 0) return 0u;
    if ((flags & 1u) != 0u) max_width = 0x1fffffffu;
    uint32_t current_after = 0u;
    uint32_t current = audio_uart_text_decode_489c5e(text, &current_after);
    uint32_t next_after = current_after;
    uint32_t current_pos = 0u;
    uint32_t next = 0u;
    uint32_t seen = 0u;
    uint32_t last_break = 0xffffffffu;
    int32_t cumulative = 0;
    while (text[current_pos] != '\0') {
        next = audio_uart_text_decode_489c5e(text, &next_after);
        seen++;
        if ((flags & 8u) != 0u &&
            audio_uart_text_hash_state_489652(state, current) != 0u) {
            current_pos = current_after;
            current_after = next_after;
            current = next;
            continue;
        }
        int32_t advance = audio_uart_font_glyph_advance_4d57f4(font,
                                                                  current, next);
        cumulative = (int32_t)((uint32_t)cumulative + (uint32_t)advance);
        if (advance > 0)
            cumulative = (int32_t)((uint32_t)cumulative +
                                   (uint32_t)letter_spacing);
        if (last_break == 0xffffffffu &&
            max_width < (int32_t)((uint32_t)cumulative -
                                  (uint32_t)letter_spacing)) {
            last_break = current_pos;
            if ((flags & 4u) != 0u) break;
        }
        if (current == '\n' || current == '\r' ||
            audio_uart_text_is_break_char_4894a4(current) != 0u) {
            seen--;
            if (current_pos == 0u && last_break == 0xffffffffu &&
                out_width != 0)
                *out_width = cumulative;
            break;
        }
        if (audio_uart_text_is_cjk_4894d0(next) != 0u ||
            audio_uart_text_is_cjk_4894d0(current) != 0u) {
            *out_width = cumulative; /* Native dereferences this on CJK path. */
            current_pos = current_after;
            break;
        }
        if (out_width != 0 && last_break == 0xffffffffu)
            *out_width = cumulative;
        current_pos = current_after;
        current_after = next_after;
        current = next;
    }
    if (last_break == 0xffffffffu) {
        if (seen == 0u || (current == '\r' && next == '\n'))
            current_pos = current_after;
        return current_pos;
    }
    if ((flags & 4u) != 0u) return last_break;
    if (out_width != 0) *out_width = 0;
    return 0u;
}
