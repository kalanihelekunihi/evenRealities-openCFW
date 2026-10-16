/* LVGL scroll-to axis wrappers 0x44e9da/0x44ea04 and their native
 * transition callbacks 0x44f3b8/0x44f3d4. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern void audio_uart_lv_scroll_move_44e79e(void *, int32_t, int32_t, uint8_t);
extern uint32_t audio_uart_lv_scroll_by_44ea98(void *, int32_t, int32_t);

void audio_uart_lv_scroll_anim_x_44f3b8(void *object, int32_t value) {
    const int32_t current = audio_uart_lv_obj_x_44e486(object);
    (void)audio_uart_lv_scroll_by_44ea98(object, current + value, 0);
}

void audio_uart_lv_scroll_anim_y_44f3d4(void *object, int32_t value) {
    const int32_t current = audio_uart_lv_obj_y_44e498(object);
    (void)audio_uart_lv_scroll_by_44ea98(object, 0, current + value);
}

void audio_uart_lv_scroll_to_x_44e9da(void *object, int32_t target,
                                       uint32_t animated) {
    (void)audio_uart_lv_style_unlink_450500(
        object, (void *)audio_uart_lv_scroll_anim_x_44f3b8);
    const int32_t current = audio_uart_lv_obj_x_44e486(object);
    audio_uart_lv_scroll_move_44e79e(object, current - target, 0,
                                     (uint8_t)animated);
}

void audio_uart_lv_scroll_to_y_44ea04(void *object, int32_t target,
                                       uint32_t animated) {
    (void)audio_uart_lv_style_unlink_450500(
        object, (void *)audio_uart_lv_scroll_anim_y_44f3d4);
    const int32_t current = audio_uart_lv_obj_y_44e498(object);
    audio_uart_lv_scroll_move_44e79e(object, 0, current - target,
                                     (uint8_t)animated);
}
