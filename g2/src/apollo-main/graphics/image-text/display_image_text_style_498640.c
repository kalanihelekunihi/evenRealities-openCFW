/* Apollo LVGL image text-style getters 0x498640..0x49865d. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

const void *audio_uart_lv_image_text_font_498640(void *object, uint32_t part) {
    return (const void *)(uintptr_t)audio_uart_lv_style_property_44bdea(
        object, part, 0x5au);
}
int32_t audio_uart_lv_image_letter_space_49864a(void *object, uint32_t part) {
    return (int32_t)audio_uart_lv_style_property_44bdea(object, part, 0x5bu);
}
int32_t audio_uart_lv_image_line_space_498654(void *object, uint32_t part) {
    return (int32_t)audio_uart_lv_style_property_44bdea(object, part, 0x5cu);
}
