/* Apollo draw-task opacity helpers, native 0x4525fe and 0x452df0. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_effective_opacity_44c47a(void *, uint32_t);

uint32_t audio_uart_lv_draw_task_style_opacity_4525fe(void *object, uint32_t selector) {
    return (uint8_t)audio_uart_lv_style_property_44bdea(object, selector, 0x62u);
}

uint32_t audio_uart_lv_draw_task_opacity_452df0(void *object, uint32_t selector,
                                                  const void *task) {
    const uint8_t *const p = (const uint8_t *)task;
    uint32_t style = (uint32_t)p[16] | ((uint32_t)p[17] << 8u) |
                     ((uint32_t)p[18] << 16u) | ((uint32_t)p[19] << 24u);
    if (style == 0u) return audio_uart_lv_effective_opacity_44c47a(object, selector);
    uint8_t style_opacity = *(const uint8_t *)(uintptr_t)(style + 0x38u);
    if (selector == 0u) return style_opacity;
    return ((uint32_t)(uint8_t)audio_uart_lv_draw_task_style_opacity_4525fe(object, selector) *
            style_opacity) >> 8u;
}
