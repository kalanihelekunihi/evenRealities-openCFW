/* Apollo Main LV font kerning 0x4b28ee..0x4b299f and its stock pair
 * comparators 0x4b29a0..0x4b29cf. The generic binary search stays explicit. */
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

int32_t audio_uart_lv_font_pair_cmp_u8_4b29a0(const void *key,
                                               const void *entry) {
    const uint8_t *k = (const uint8_t *)key;
    const uint8_t *e = (const uint8_t *)entry;
    uint32_t a = load32(k);
    uint32_t b = e[0];
    if (a == b) return (int32_t)(load32(k + 4u) - e[1]);
    return (int32_t)(a - b);
}

int32_t audio_uart_lv_font_pair_cmp_u16_4b29b8(const void *key,
                                                const void *entry) {
    const uint8_t *k = (const uint8_t *)key;
    const uint8_t *e = (const uint8_t *)entry;
    uint32_t a = load32(k);
    uint32_t b = load16(e);
    if (a == b) return (int32_t)(load32(k + 4u) - load16(e + 2u));
    return (int32_t)(a - b);
}

int8_t audio_uart_lv_font_kerning_4b28ee(const void *font,
                                          int32_t left, int32_t right) {
    const uint8_t *f = (const uint8_t *)font;
    const uint8_t *state = (const uint8_t *)(uintptr_t)load32(f + 0x18u);
    const uint8_t *pairs = (const uint8_t *)(uintptr_t)load32(state + 0x0cu);
    if (((load16(state + 0x12u) & 0x3fffu) >> 13u) == 0u) {
        uint32_t meta = load32(pairs + 8u);
        uint32_t mode = meta >> 30u;
        if (mode < 2u) {
            const uint8_t *base = (const uint8_t *)(uintptr_t)load32(pairs);
            const uint8_t *values = (const uint8_t *)(uintptr_t)load32(pairs + 4u);
            uint32_t key[2] = {(uint32_t)left, (uint32_t)right};
            uint32_t stride = mode == 0u ? 2u : 4u;
            pair_compare_fn cmp = mode == 0u ?
                audio_uart_lv_font_pair_cmp_u8_4b29a0 :
                audio_uart_lv_font_pair_cmp_u16_4b29b8;
            const uint8_t *found = (const uint8_t *)
                audio_uart_lv_font_pair_search_52a284(key, base,
                                                        meta & 0x3fffffffu,
                                                        stride, cmp);
            if (found != 0)
                return (int8_t)values[(uint32_t)(found - base) / stride];
        }
        return 0;
    }
    const uint8_t *values = (const uint8_t *)(uintptr_t)load32(pairs);
    const uint8_t *left_classes = (const uint8_t *)(uintptr_t)load32(pairs + 4u);
    const uint8_t *right_classes = (const uint8_t *)(uintptr_t)load32(pairs + 8u);
    uint8_t lc = left_classes[(uint32_t)left];
    uint8_t rc = right_classes[(uint32_t)right];
    if (lc != 0u && rc != 0u)
        return (int8_t)values[(uint32_t)pairs[0x0du] * (uint32_t)(lc - 1u) +
                              (uint32_t)(rc - 1u)];
    return 0;
}
