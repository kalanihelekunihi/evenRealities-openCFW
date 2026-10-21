/* Apollo Main LV font glyph-id lookup 0x4b2774..0x4b28ed and stock
 * 16-bit comparator 0x4b29d0..0x4b29d7. */
#include <stdint.h>

typedef int32_t (*pair_compare_fn)(const void *, const void *);
extern void *audio_uart_lv_font_pair_search_52a284(const void *, const void *,
                                                    uint32_t, uint32_t,
                                                    pair_compare_fn);

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

int32_t audio_uart_lv_font_u16_compare_4b29d0(const void *key,
                                               const void *entry) {
    return (int32_t)((uint32_t)load16((const uint8_t *)key) -
                     (uint32_t)load16((const uint8_t *)entry));
}

int32_t audio_uart_lv_font_lookup_4b2774(const void *font, uint32_t codepoint) {
    if (codepoint == 0u) return 0;
    const uint8_t *f = (const uint8_t *)font;
    const uint8_t *state = (const uint8_t *)(uintptr_t)load32(f + 0x18u);
    const uint8_t *ranges = (const uint8_t *)(uintptr_t)load32(state + 8u);
    uint32_t count = load16(state + 0x12u) & 0x1ffu;
    for (uint32_t index = 0u; index < count; ++index) {
        const uint8_t *range = ranges + index * 0x14u;
        uint32_t start = load32(range);
        uint32_t offset = codepoint - start;
        if (offset >= load16(range + 4u)) continue;
        uint32_t first_glyph = load16(range + 6u);
        uint8_t mode = range[0x12u];
        if (mode == 2u) return (int32_t)(first_glyph + offset);
        if (mode == 0u) {
            const uint8_t *map = (const uint8_t *)(uintptr_t)load32(range + 0x0cu);
            uint32_t mapped = map[offset];
            if (mapped != 0u || codepoint == start)
                return (int32_t)(first_glyph + mapped);
            continue;
        }
        if (mode == 1u || mode == 3u) {
            uint16_t key = (uint16_t)offset;
            const uint8_t *list = (const uint8_t *)(uintptr_t)load32(range + 8u);
            const uint8_t *found = (const uint8_t *)
                audio_uart_lv_font_pair_search_52a284(
                    &key, list, load16(range + 0x10u), 2u,
                    audio_uart_lv_font_u16_compare_4b29d0);
            if (found == 0) return 0;
            uint32_t pos = (uint32_t)(found - list);
            if (mode == 3u) return (int32_t)(first_glyph + (pos >> 1u));
            const uint8_t *map = (const uint8_t *)(uintptr_t)load32(range + 0x0cu);
            return (int32_t)(first_glyph + load16(map + pos));
        }
        return 0;
    }
    return 0;
}
