/* Stock LVGL one-step scroll-to-view wrapper at 0x44ea2e. */
#include <stdint.h>

extern void audio_uart_page_43f66c(void *object);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_lv_scroll_view_step_44f40c(void *, void *, void *,
                                                   uint32_t);

void audio_terminal_ui_scroll_to_view_44ea2e(void *object,
                                              uint32_t animation) {
    audio_uart_page_43f66c(object);
    uint32_t area[2];
    audio_uart_buffer_zero(area, 8u, 0u);
    audio_uart_lv_scroll_view_step_44f40c((uint8_t *)object + 0x14u,
                                           object, area, (uint8_t)animation);
}
