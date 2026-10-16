/* Apollo Main LVGL timer iteration 0x4645ec..0x464603 and removal
 * 0x4644ee..0x46450b. Literals 0x4646b4/0x4646b8 resolve to the
 * existing LVGL state at 0x2006f548 and its timer list at +0x74. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern void audio_uart_lv_list_remove(void *, void *);
extern void audio_uart_lv_heap_free(void *);

void *audio_uart_lv_timer_iter_4645ec(void *timer) {
    void *list = audio_uart_display_lv_state + 0x74u;
    return timer == 0 ? audio_uart_lv_list_first(list) :
                        audio_uart_lv_list_next(list, timer);
}

void audio_uart_lv_timer_remove_4644ee(void *timer) {
    void *list = audio_uart_display_lv_state + 0x74u;
    audio_uart_lv_list_remove(list, timer);
    audio_uart_display_lv_state[0x82u] = 1u;
    audio_uart_lv_heap_free(timer);
}
