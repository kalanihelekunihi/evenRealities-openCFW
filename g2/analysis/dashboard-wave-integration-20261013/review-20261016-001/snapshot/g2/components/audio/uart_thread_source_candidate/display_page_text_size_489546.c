/* Apollo LV text size calculation, native 0x489546..0x489651. */
#include <stdint.h>

extern uint32_t audio_uart_text_line_length_4897fc(const char *text,
                                                    uint32_t count,
                                                    const void *font,
                                                    int32_t letter_spacing,
                                                    int32_t max_width,
                                                    uint32_t reserved,
                                                    uint32_t flags);
extern int32_t audio_uart_text_line_width_489934(const char *text,
                                                 uint32_t length,
                                                 const void *font,
                                                 int32_t letter_spacing);
extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                               const char *function, const char *message, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u);
    p[3] = (uint8_t)(v >> 24u);
}

void audio_uart_page_event_calculate_489546(void *output, const char *text,
                                             const void *font, int32_t letter_spacing,
                                             int32_t line_spacing, int32_t max_width,
                                             uint32_t flags) {
    uint8_t *out = (uint8_t *)output;
    put32(out, 0u);
    put32(out + 4u, 0u);
    if (text == 0 || font == 0) return;
    if ((flags & 1u) != 0u) max_width = 0x1fffffff;
    uint32_t font_height = get32((const uint8_t *)font + 0x0cu) & 0xffffu;
    uint32_t position = 0u;
    while ((uint8_t)text[position] != 0u) {
        uint32_t length = audio_uart_text_line_length_4897fc(
                text + position, 0xffffffffu, font, letter_spacing,
                max_width, 0u, (uint8_t)flags);
        uint32_t next = get32(out + 4u) + font_height + (uint32_t)line_spacing;
        if (next >= 0x80000000u) {
            audio_uart_lvgl_log(2u, (const char *)(uintptr_t)0x006e898cu,
                               0x70u, (const char *)(uintptr_t)0x00781160u,
                               (const char *)(uintptr_t)0x00735474u);
            return;
        }
        put32(out + 4u, next);
        int32_t width = audio_uart_text_line_width_489934(
                text + position, length, font, letter_spacing);
        if (width > (int32_t)get32(out)) put32(out, (uint32_t)width);
        position += length;
    }
    if (position != 0u &&
        (text[position - 1u] == '\n' || text[position - 1u] == '\r'))
        put32(out + 4u, get32(out + 4u) + font_height + (uint32_t)line_spacing);
    if (get32(out + 4u) == 0u)
        put32(out + 4u, font_height);
    else
        put32(out + 4u, get32(out + 4u) - (uint32_t)line_spacing);
}
