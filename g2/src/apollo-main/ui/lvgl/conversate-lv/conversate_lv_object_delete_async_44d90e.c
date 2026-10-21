/* Apollo Main LVGL asynchronous object delete, native 0x44d90e..0x44d94b. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern uint32_t audio_uart_lv_async_post_484014(void (*)(void *), void *);
extern void audio_uart_lv_delete_event_callback_44df20(void *);

static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c";
static const char function[] = "lv_obj_delete_async";
static const char assertion[] = "Asserted at expression: %s (%s)";
static const char expression[] = "obj != NULL";
static const char reason[] = "NULL pointer";

void audio_conversate_lv_object_delete_44d90e(uint32_t object) {
    if (object == 0u) {
        audio_uart_lvgl_log(3u, path, 0x8fu, function, assertion,
                            expression, reason);
        volatile uint32_t *const fault = (volatile uint32_t *)(uintptr_t)UINT32_MAX;
        for (;;) *fault = 0u;
    }
    (void)audio_uart_lv_async_post_484014(
        audio_uart_lv_delete_event_callback_44df20,
        (void *)(uintptr_t)object);
}
