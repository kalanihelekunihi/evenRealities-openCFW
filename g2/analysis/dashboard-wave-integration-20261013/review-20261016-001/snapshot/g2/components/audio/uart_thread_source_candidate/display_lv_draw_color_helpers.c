/* Apollo LV draw color leaves, native 0x440fde and 0x44b8d0/0x44b8de. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

uint32_t audio_uart_lv_color_with_alpha_440fde(uint32_t color, uint32_t opacity) {
    return (color & 0x00ffffffu) | ((opacity & 0xffu) << 24u);
}

uint32_t audio_uart_lv_draw_color_style_44b8d0(void *object, uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object, selector, 0x78u);
}

uint32_t audio_uart_lv_draw_color_style_44b8de(void *object, uint32_t selector) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, 0x79u);
}
