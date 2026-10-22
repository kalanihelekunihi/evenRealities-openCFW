/* Apollo Main LVGL async post 0x484014..0x484051 and timer setter 0x4645ac. */
#include <stdint.h>

extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_timer_create_464466(void (*)(void *), uint32_t, void *);
extern void audio_uart_lv_async_dispatch_4840ac(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char timer_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
static const char timer_function[] = "lv_timer_set_repeat_count";
static const char assertion[] = "Asserted at expression: %s (%s)";
static const char expression[] = "timer != NULL";
static const char reason[] = "NULL pointer";


