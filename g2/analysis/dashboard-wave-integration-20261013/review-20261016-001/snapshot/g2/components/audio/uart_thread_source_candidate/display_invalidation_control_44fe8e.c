/* Apollo LVGL display invalidation nesting control 0x44fe8e..0x44fed0. */
#include <stdint.h>

extern void *audio_uart_display_default_get(void); /* 0x44fa1a */
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);

void audio_uart_lv_display_invalidation_44fe8e(void *display, uint32_t enabled) {
    if (display == 0) display = audio_uart_display_default_get();
    if (display == 0) {
        audio_uart_lvgl_log(2u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c",
            0x3a4u, "lv_display_enable_invalidation", "No display available");
        return;
    }
    uint8_t *bytes = (uint8_t *)display;
    uint32_t *counter = (uint32_t *)(void *)(bytes + 0x264u);
    *counter += (uint8_t)enabled == 0u ? UINT32_MAX : 1u;
}
