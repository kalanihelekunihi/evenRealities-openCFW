/* Small LVGL scroll providers at Apollo Main 0x44e2a4 and 0x44e4aa. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);

uint32_t audio_uart_lv_scroll_mode_44e2a4(void *object, uint32_t selector) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, 0x27u);
}

int32_t audio_uart_lv_scroll_top_44e4aa(void *object) {
    const uint8_t *const spec = *(const uint8_t *const *)((const uint8_t *)object + 8u);
    if (spec == 0) return 0;
    const uint32_t value = *(const uint32_t *)(spec + 0x24u);
    return (int32_t)(0u - value);
}
