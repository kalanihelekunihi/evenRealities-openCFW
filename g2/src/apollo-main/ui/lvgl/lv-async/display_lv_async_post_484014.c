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

void audio_uart_lv_timer_repeat_count_4645ac(void *timer, uint32_t count) {
    if (timer == 0) {
        audio_uart_lvgl_log(3u, timer_path, 0xe5u, timer_function,
                            assertion, expression, reason);
        volatile uint32_t *const fault = (volatile uint32_t *)(uintptr_t)UINT32_MAX;
        for (;;) *fault = 0u;
    }
    *(volatile uint32_t *)(void *)((uint8_t *)timer + 0x10u) = count;
}

uint32_t audio_uart_lv_async_post_484014(void (*callback)(void *), void *user) {
    uint32_t *const record = (uint32_t *)audio_uart_lv_malloc(8u);
    if (record == 0) return 0u;
    void *const timer = audio_uart_lv_timer_create_464466(
        audio_uart_lv_async_dispatch_4840ac, 0u, record);
    if (timer == 0) {
        audio_uart_lv_heap_free(record);
        return 0u;
    }
    record[0] = (uint32_t)(uintptr_t)callback;
    record[1] = (uint32_t)(uintptr_t)user;
    audio_uart_lv_timer_repeat_count_4645ac(timer, 1u);
    return 1u;
}
