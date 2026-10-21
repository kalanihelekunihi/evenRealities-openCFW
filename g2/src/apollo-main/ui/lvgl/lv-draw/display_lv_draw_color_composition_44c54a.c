/* Apollo LV color composition and ancestor walk, native 0x44c54a..0x44c5d3. */
#include <stdint.h>

extern uint32_t audio_uart_lv_draw_color_style_44b8d0(void *, uint32_t);
extern uint32_t audio_uart_lv_draw_color_style_44b8de(void *, uint32_t);
extern uint32_t audio_uart_lv_color_with_alpha_440fde(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_color_blend_482ef6(uint32_t, uint32_t);
extern void *audio_uart_lv_obj_parent_44dca2(void *);

uint32_t audio_uart_lv_draw_color_composite_44c54a(void *object, uint32_t selector,
                                                    uint32_t base_color) {
    uint8_t alpha = (uint8_t)audio_uart_lv_draw_color_style_44b8de(object, selector);
    if (alpha == 0u) return base_color;
    uint32_t color = audio_uart_lv_draw_color_style_44b8d0(object, selector);
    uint32_t overlay = audio_uart_lv_color_with_alpha_440fde(color, alpha);
    return audio_uart_lv_color_blend_482ef6(base_color, overlay);
}

uint32_t audio_uart_lv_draw_color_chain_44c582(void *object, uint32_t selector) {
    uint32_t color = audio_uart_lv_draw_color_style_44b8d0(object, selector);
    uint8_t alpha = (uint8_t)audio_uart_lv_draw_color_style_44b8de(object, selector);
    color = audio_uart_lv_color_with_alpha_440fde(color, alpha);
    if (selector == 0u) object = audio_uart_lv_obj_parent_44dca2(object);
    else selector = 0u;
    while (object != 0) {
        color = audio_uart_lv_draw_color_composite_44c54a(object, selector, color);
        object = audio_uart_lv_obj_parent_44dca2(object);
    }
    return color;
}
