/* LVGL style property wrappers used by the query-permission dialog. */
#include <stdint.h>
extern void audio_uart_page_style_apply_44be4c(void *, uint8_t, uint32_t,
                                                uint32_t);
void audio_uart_page_441180(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 5u, value, selector);
}
void audio_uart_page_44119c(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 6u, value, selector);
}
