/* Apollo RGB mix and draw-task RGB selection, native 0x482dd8 and 0x452e22.
 * Stock 0x482dd8 writes only return bytes 0..2; its top byte is scratch-stack
 * dependent. Callers in the draw-task builder copy only the three RGB bytes. */
#include <stdint.h>

extern uint32_t audio_uart_lv_draw_color_chain_44c582(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_color_composite_44c54a(void *, uint32_t, uint32_t);

uint32_t audio_uart_lv_color_rgb_mix_482dd8(uint32_t first, uint32_t second,
                                             uint32_t opacity) {
    uint32_t alpha = (uint8_t)opacity;
    uint32_t result = 0u;
    for (unsigned shift = 0; shift < 24u; shift += 8u) {
        uint32_t a = (first >> shift) & 0xffu;
        uint32_t b = (second >> shift) & 0xffu;
        uint32_t weighted = alpha * a + (0xffu - alpha) * b;
        result |= (((weighted * 0x8081u) >> 23u) & 0xffu) << shift;
    }
    return result;
}

uint32_t audio_uart_lv_draw_rgb_mix_452e22(void *object, uint32_t selector,
                                            const void *task, uint32_t fallback) {
    const uint8_t *p = (const uint8_t *)task;
    uint32_t style = (uint32_t)p[16] | ((uint32_t)p[17] << 8u) |
                     ((uint32_t)p[18] << 16u) | ((uint32_t)p[19] << 24u);
    uint32_t color;
    if (style == 0u) {
        color = audio_uart_lv_draw_color_chain_44c582(object, selector);
    } else {
        const uint8_t *s = (const uint8_t *)(uintptr_t)(style + 0x39u);
        color = (uint32_t)s[0] | ((uint32_t)s[1] << 8u) |
                ((uint32_t)s[2] << 16u) | ((uint32_t)s[3] << 24u);
        if (selector != 0u)
            color = audio_uart_lv_draw_color_composite_44c54a(object, selector, color);
    }
    return audio_uart_lv_color_rgb_mix_482dd8(color & 0x00ffffffu, fallback,
                                               color >> 24u);
}
