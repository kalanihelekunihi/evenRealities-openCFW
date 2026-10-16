/* Apollo LV effective opacity and style accessor, native 0x44c47a/0x44b8b8. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern void *audio_uart_lv_obj_parent_44dca2(void *);

uint32_t audio_uart_lv_style_opacity_44b8b8(void *object, uint32_t selector) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, 0x62u);
}

uint32_t audio_uart_lv_effective_opacity_44c47a(void *object, uint32_t selector) {
    uint8_t opacity = (uint8_t)audio_uart_lv_style_opacity_44b8b8(object, selector);
    if (opacity < 3u) return 0u;
    uint32_t result = 0xffu;
    if (opacity < 0xfdu) result = ((uint32_t)opacity * result) >> 8u;
    if (selector == 0u) object = audio_uart_lv_obj_parent_44dca2(object);
    while (object != 0) {
        opacity = (uint8_t)audio_uart_lv_style_opacity_44b8b8(object, 0u);
        if (opacity < 3u) return 0u;
        if (opacity < 0xfdu) result = ((uint32_t)opacity * result) >> 8u;
        object = audio_uart_lv_obj_parent_44dca2(object);
    }
    if (result < 3u) return 0u;
    return result > 0xfcu ? 0xffu : result;
}
