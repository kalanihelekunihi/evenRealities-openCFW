/* Apollo Main LVGL scroll movement, native span 0x44e79e..0x44e883. */
#include <stdint.h>

extern void audio_uart_page_43f66c(void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_uart_lv_scroll_mode_44e2a4(void *, uint32_t);
extern int32_t audio_uart_lv_scroll_left_44e586(void *);
extern int32_t audio_uart_lv_scroll_right_44e67a(void *);
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *);
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *);
extern void audio_uart_lv_scroll_dispatch_44e884(void *, int32_t, int32_t, uint32_t);

static int32_t add32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a + (uint32_t)b);
}
static int32_t neg32(int32_t value) {
    return (int32_t)(0u - (uint32_t)value);
}

void audio_uart_lv_scroll_move_44e79e(void *object, int32_t x, int32_t y,
                                        uint32_t animated) {
    if ((x | y) == 0) return;
    audio_uart_page_43f66c(object);
    const int32_t old_x = audio_uart_lv_obj_x_44e486(object);
    int32_t move_x = add32(x, neg32(old_x));
    if ((uint8_t)audio_uart_lv_scroll_mode_44e2a4(object, 0u) == 1u) {
        if (move_x < 0) move_x = 0;
        if (move_x > 0) {
            int32_t limit = add32(audio_uart_lv_scroll_left_44e586(object),
                                  audio_uart_lv_scroll_right_44e67a(object));
            if (limit < 0) limit = 0;
            if (limit < move_x) move_x = limit;
        }
    } else {
        if (move_x > 0) move_x = 0;
        if (move_x < 0) {
            int32_t limit = add32(audio_uart_lv_scroll_left_44e586(object),
                                  audio_uart_lv_scroll_right_44e67a(object));
            if (limit < 0) limit = 0;
            if ((int64_t)move_x + limit < 0) move_x = neg32(limit);
        }
    }
    const int32_t old_y = audio_uart_lv_obj_y_44e498(object);
    int32_t move_y = add32(y, neg32(old_y));
    if (move_y > 0) move_y = 0;
    if (move_y < 0) {
        int32_t limit = add32(audio_uart_lv_scroll_top_44e4aa(object),
                              audio_uart_lv_scroll_bottom_44e4bc(object));
        if (limit < 0) limit = 0;
        if ((int64_t)move_y + limit < 0) move_y = neg32(limit);
    }
    const int32_t next_x = add32(move_x, old_x);
    const int32_t next_y = add32(move_y, old_y);
    if ((next_x | next_y) != 0)
        audio_uart_lv_scroll_dispatch_44e884(object, next_x, next_y,
                                               (uint8_t)animated);
}
