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

