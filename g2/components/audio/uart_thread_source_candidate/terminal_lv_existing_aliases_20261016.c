/* ABI adapters to existing stock-address LVGL C providers. */
#include <stdint.h>

extern void audio_uart_page_43ded4(void *object, uint32_t flags);
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);
extern void audio_uart_page_43f09a(uint32_t object, uint32_t x, uint32_t y);

void audio_lv_object_flag_43ded4(uint32_t object, uint32_t flags) {
    audio_uart_page_43ded4((void *)(uintptr_t)object, flags);
}

void audio_lv_object_clear_flag_43dfa4(uint32_t object, uint32_t flags) {
    audio_uart_page_43dfa4((void *)(uintptr_t)object, flags);
}

void audio_lv_object_position_43f09a(uint32_t object, uint32_t x, uint32_t y) {
    audio_uart_page_43f09a(object, x, y);
}
