/* Native LV scroll reconciliation and two spec-attribute mode readers. */
#include <stdint.h>

extern int32_t audio_uart_lv_scroll_top_44e4aa(void *);
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *);
extern int32_t audio_uart_lv_scroll_left_44e586(void *);
extern int32_t audio_uart_lv_scroll_right_44e67a(void *);
extern uint32_t audio_uart_lv_scroll_mode_44e2a4(void *, uint32_t);
extern void audio_uart_lv_scroll_dispatch_44e884(void *, int32_t, int32_t,
                                                  uint32_t);

static uint32_t spec_mode(void *object, uint32_t shift) {
    uint8_t *spec = *(uint8_t **)(void *)((uint8_t *)object + 8u);
    if (spec == 0) return 0u;
    return (*(const uint16_t *)(const void *)(spec + 0x32u) >> shift) & 3u;
}

uint32_t audio_uart_lv_scroll_x_spec_mode_44e45a(void *object) {
    return spec_mode(object, 2u);
}

uint32_t audio_uart_lv_scroll_y_spec_mode_44e470(void *object) {
    return spec_mode(object, 4u);
}

void audio_uart_lv_obj_scroll_reconcile_44f316(void *object,
                                                uint32_t animated) {
    if (audio_uart_lv_scroll_y_spec_mode_44e470(object) == 0u) {
        int32_t top = audio_uart_lv_scroll_top_44e4aa(object);
        int32_t bottom = audio_uart_lv_scroll_bottom_44e4bc(object);
        if (bottom < 0 && top >= 1) {
            int32_t delta = ((int64_t)top + (int64_t)bottom < 0)
                                ? top : (int32_t)(0u - (uint32_t)bottom);
            audio_uart_lv_scroll_dispatch_44e884(object, 0, delta,
                                                   (uint8_t)animated);
        }
    }
    if (audio_uart_lv_scroll_x_spec_mode_44e45a(object) != 0u) return;
    int32_t left = audio_uart_lv_scroll_left_44e586(object);
    int32_t right = audio_uart_lv_scroll_right_44e67a(object);
    if (audio_uart_lv_scroll_mode_44e2a4(object, 0u) == 1u) {
        if (left < 0 && right >= 1)
            audio_uart_lv_scroll_dispatch_44e884(object, left, 0,
                                                   (uint8_t)animated);
    } else if (right < 0 && left >= 1) {
        int32_t delta = ((int64_t)left + (int64_t)right < 0)
                            ? left : (int32_t)(0u - (uint32_t)right);
        audio_uart_lv_scroll_dispatch_44e884(object, delta, 0,
                                               (uint8_t)animated);
    }
}
