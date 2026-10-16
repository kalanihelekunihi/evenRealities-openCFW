/* Stock LVGL image style field accessors 0x4524a4/0x4524b0/0x4524d0/0x45260a. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
uint32_t audio_uart_lv_style_image_opa_4524a4(void *object, uint32_t part) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, part, 0x44u);
}
uint32_t audio_uart_lv_style_image_recolor_4524b0(void *object, uint32_t part) {
    return audio_uart_lv_style_property_44bdea(object, part, 0x45u);
}
uint32_t audio_uart_lv_style_image_recolor_opa_4524d0(void *object, uint32_t part) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, part, 0x46u);
}
uint32_t audio_uart_lv_style_image_blend_45260a(void *object, uint32_t part) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, part, 0x69u);
}
