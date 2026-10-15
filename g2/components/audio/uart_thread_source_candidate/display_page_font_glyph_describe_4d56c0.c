/* Apollo LV font chain glyph descriptor, native 0x4d56c0..0x4d57f3. */
#include <stdint.h>

extern void audio_uart_font_resource_enter_46f65e(void);
extern void audio_uart_font_resource_leave_46f674(void);

typedef uint32_t (*glyph_callback_t)(const void *font, void *descriptor,
                                     uint32_t glyph, uint32_t next);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}
static void put16(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
}
static uint32_t call_font(const uint8_t *node, uint8_t *out,
                          uint32_t glyph, uint32_t next) {
    if (get32(node + 0x18u) >= 0x80000001u)
        audio_uart_font_resource_enter_46f65e();
    uint32_t callback_next = (node[0x14u] & 4u) != 0u ? 0u : next;
    glyph_callback_t callback = (glyph_callback_t)(uintptr_t)get32(node);
    uint32_t found = callback(node, out, glyph, callback_next) & 0xffu;
    if (get32(node + 0x18u) >= 0x80000001u)
        audio_uart_font_resource_leave_46f674();
    return found;
}

uint32_t audio_uart_font_glyph_describe_4d56c0(const void *font,
                                                 void *descriptor,
                                                 uint32_t glyph,
                                                 uint32_t next) {
    uint8_t *out = (uint8_t *)descriptor;
    const uint8_t *base = (const uint8_t *)font;
    /* Stock asserts and traps for null font/output before this path. */
    if (base == 0 || out == 0) __builtin_trap();
    for (uint32_t i = 0u; i < 32u; ++i) out[i] = 0;
    const uint8_t *fallback = 0;
    const uint8_t *node = base;
    while (node != 0) {
        uint32_t found = call_font(node, out, glyph, next);
        if (found != 0u) {
            if ((out[0x0fu] & 1u) == 0u) {
                put32(out, (uint32_t)(uintptr_t)node);
                return 1u;
            }
            if (fallback == 0) fallback = node;
        }
        node = (const uint8_t *)(uintptr_t)get32(node + 0x1cu);
        /* Native hangs on a next-node callback pointer below 0x101. */
        if (node != 0 && get32(node) < 0x101u) __builtin_trap();
    }
    if (fallback != 0) {
        (void)call_font(fallback, out, glyph, next);
        put32(out, (uint32_t)(uintptr_t)fallback);
        return 1u;
    }
    put16(out + 6u, 2u);
    put16(out + 4u, 4u);
    put32(out, 0u);
    put16(out + 8u, get32(base + 0x0cu));
    put16(out + 0x0au, 0u);
    put16(out + 0x0cu, 0u);
    out[0x0eu] = 1u;
    out[0x0fu] |= 1u;
    return 0u;
}
