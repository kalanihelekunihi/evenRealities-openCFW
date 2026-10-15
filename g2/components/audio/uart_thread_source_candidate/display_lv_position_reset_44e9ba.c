/* LVGL two-axis scroll position reset 0x44e9ba..0x44e9d9. */
#include <stdint.h>

extern void audio_uart_lv_scroll_to_x_44e9da(void *, int32_t, uint8_t);
extern void audio_uart_lv_scroll_to_y_44ea04(void *, int32_t, uint8_t);

void audio_uart_lv_position_reset_44e9ba(void *object, uint32_t x,
                                          uint32_t y, uint32_t animated) {
    audio_uart_lv_scroll_to_x_44e9da(object, (int32_t)x, (uint8_t)animated);
    audio_uart_lv_scroll_to_y_44ea04(object, (int32_t)y, (uint8_t)animated);
}
