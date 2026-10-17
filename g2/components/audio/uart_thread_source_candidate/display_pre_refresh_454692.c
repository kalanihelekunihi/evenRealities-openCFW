/* Apollo Main LVGL display pre-refresh hook, native 0x454692..0x4546cc. */
#include <stdint.h>

extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);

void audio_uart_lv_display_pre_refresh_454692(void *display)
{
    uint8_t *const bytes = (uint8_t *)display;
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3fu, 0);
    const uint32_t callback = *(const uint32_t *)(const void *)(bytes + 0x2cu);
    const uint32_t pending = *(const uint32_t *)(const void *)(bytes + 0x30u);
    if (callback != 0u) {
        if (pending != 0u) {
            ((void (*)(void *))(uintptr_t)callback)(display);
            *(uint32_t *)(void *)(bytes + 0x30u) = 0u;
        }
    } else if (pending != 0u) {
        /* Native branch at 0x4546b8 loops while this invalid state persists. */
        for (;;) { }
    }
    *(uint32_t *)(void *)(bytes + 0x34u) = 0u;
    (void)audio_uart_lv_display_event_44fdbe(display, 0x40u, 0);
}
