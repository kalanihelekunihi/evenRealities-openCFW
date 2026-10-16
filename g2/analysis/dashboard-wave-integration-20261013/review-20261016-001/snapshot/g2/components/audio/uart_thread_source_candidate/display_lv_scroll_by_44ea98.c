/* LVGL scroll-by body at Apollo Main 0x44ea98..0x44eaf1. */
#include <stdint.h>

extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern void audio_uart_lv_obj_move_children_44035e(void *, int32_t, int32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_display_size_changed(void *);

uint32_t audio_uart_lv_scroll_by_44ea98(void *object, int32_t dx, int32_t dy) {
    if ((dx | dy) == 0) return 1u;
    audio_uart_lv_obj_setup_layer_43e1fa(object);
    uint8_t *const spec = *(uint8_t **)((uint8_t *)object + 8u);
    *(uint32_t *)(spec + 0x20u) += (uint32_t)dx;
    *(uint32_t *)(spec + 0x24u) += (uint32_t)dy;
    audio_uart_lv_obj_move_children_44035e(object, dx, dy, 1u);
    const uint32_t result = (uint8_t)audio_uart_lv_obj_event_451670(object, 0x0fu, 0);
    if (result != 1u) return result;
    audio_uart_display_size_changed(object);
    return 1u;
}
