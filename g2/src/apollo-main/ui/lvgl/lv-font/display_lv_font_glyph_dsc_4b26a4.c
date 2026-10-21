/* Apollo Main LV font glyph descriptor callback 0x4b26a4..0x4b2773. */
#include <stdint.h>

extern int32_t audio_uart_lv_font_lookup_4b2774(const void *, uint32_t);
extern int8_t audio_uart_lv_font_kerning_4b28ee(const void *, int32_t, int32_t);

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void store16(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
}
static void store32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

uint32_t audio_uart_lv_font_glyph_dsc_4b26a4(const void *font,
                                              void *glyph_descriptor,
                                              uint32_t codepoint,
                                              uint32_t next_codepoint) {
    const uint8_t *f = (const uint8_t *)font;
    uint8_t *out = (uint8_t *)glyph_descriptor;
    uint32_t tab = codepoint == 9u;
    if (tab) codepoint = 0x20u;
    const uint8_t *state = (const uint8_t *)(uintptr_t)load32(f + 0x18u);
    int32_t glyph = audio_uart_lv_font_lookup_4b2774(font, codepoint);
    if (glyph == 0) return 0u;
    int32_t kern = 0;
    if (load32(state + 0x0cu) != 0u) {
        int32_t next = audio_uart_lv_font_lookup_4b2774(font, next_codepoint);
        if (next != 0)
            kern = audio_uart_lv_font_kerning_4b28ee(font, glyph, next);
    }
    const uint8_t *entry = (const uint8_t *)(uintptr_t)load32(state + 4u) +
                           (uint32_t)glyph * 16u;
    int32_t advance = (int32_t)load32(entry + 4u);
    if (tab) advance = (int32_t)((uint32_t)advance << 1u);
    int32_t scaled = ((int32_t)load16(state + 0x10u) * kern) >> 4;
    store16(out + 4u, (uint16_t)((scaled + advance + 8) >> 4));
    store16(out + 8u, load16(entry + 10u));
    store16(out + 6u, load16(entry + 8u));
    store16(out + 10u, load16(entry + 12u));
    store16(out + 12u, load16(entry + 14u));
    uint16_t flags = load16(state + 0x12u);
    uint8_t format = (uint8_t)((flags >> 9u) & 0x0fu);
    if ((flags >> 14u) == 3u) format = (uint8_t)(format + 0x10u);
    out[14] = format;
    out[15] &= 0xfeu;
    store32(out + 0x18u, (uint32_t)glyph);
    if (tab)
        store16(out + 6u, (uint16_t)(load16(out + 6u) << 1u));
    return 1u;
}
