/* Apollo draw-task conditional color composition, native 0x452e68..0x452ecf. */
#include <stdint.h>

extern uint32_t audio_uart_lv_draw_color_chain_44c582(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_color_composite_44c54a(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_color_with_alpha_440fde(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_color_blend_482ef6(uint32_t, uint32_t);

uint32_t audio_uart_lv_draw_color_variant_452e68(void *object, uint32_t selector,
                                                  const void *task, uint32_t fallback,
                                                  uint32_t fallback_alpha) {
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
    uint8_t alpha = (uint8_t)(color >> 24u);
    if ((uint8_t)fallback_alpha != 0u && alpha != 0u) {
        uint32_t under = audio_uart_lv_color_with_alpha_440fde(fallback, fallback_alpha);
        return audio_uart_lv_color_blend_482ef6(color, under);
    }
    if (alpha == 0u)
        return audio_uart_lv_color_with_alpha_440fde(fallback, fallback_alpha);
    return color;
}
