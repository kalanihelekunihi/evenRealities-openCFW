/* Stock LVGL image opacity/radius style getters, 0x498634 and 0x49865e. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t,
                                                      uint32_t);

uint32_t audio_uart_lv_image_style_opa_498634(void *object, uint32_t part) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, part, 0x44u);
}

uint32_t audio_uart_lv_image_style_radius_49865e(void *object,
                                                  uint32_t part) {
    return audio_uart_lv_style_property_44bdea(object, part, 0x0cu);
}
