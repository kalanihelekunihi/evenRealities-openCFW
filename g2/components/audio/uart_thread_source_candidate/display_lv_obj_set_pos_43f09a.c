/* LVGL lv_obj_set_pos at Apollo 0x43f09a. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, ...);
extern void audio_uart_page_43f0e0(uint32_t, uint32_t);
extern void audio_uart_page_43f142(uint32_t, uint32_t);

static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char function[] = "lv_obj_set_pos";
static const char asserted[] = "Asserted at expression: %s (%s)";
static const char expression[] = "obj != NULL";
static const char reason[] = "NULL pointer";

void audio_uart_page_43f09a(uint32_t object, uint32_t x, uint32_t y) {
    if (object == 0u) {
        audio_uart_lvgl_log(3u, path, 0x35u, function,
                            asserted, expression, reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    audio_uart_page_43f0e0(object, x);
    audio_uart_page_43f142(object, y);
}
