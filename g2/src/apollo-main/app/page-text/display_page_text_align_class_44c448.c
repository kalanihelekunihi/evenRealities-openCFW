/* Apollo LVGL style text alignment, native 0x44c448 and its small getters. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

uint32_t audio_uart_lv_text_align_style_44b8ac(void *page, uint32_t part) {
    return audio_uart_lv_style_property_44bdea(page, part, 0x5eu) & 0xffu;
}

uint32_t audio_uart_lv_base_dir_style_44b8f6(void *page, uint32_t part) {
    return audio_uart_lv_style_property_44bdea(page, part, 0x27u) & 0xffu;
}

void audio_uart_lv_bidi_calculate_align_44b7b4(uint8_t *alignment,
                                                 uint8_t *base_direction,
                                                 const char *text) {
    (void)base_direction;
    (void)text;
    if (*alignment == 0u) *alignment = 1u;
}

uint32_t audio_uart_page_text_align_class_44c448(void *page, uint32_t part,
                                                   const char *text) {
    uint8_t alignment = (uint8_t)audio_uart_lv_text_align_style_44b8ac(page, part);
    uint8_t base_direction = (uint8_t)audio_uart_lv_base_dir_style_44b8f6(page, part);
    audio_uart_lv_bidi_calculate_align_44b7b4(&alignment, &base_direction, text);
    return alignment;
}
