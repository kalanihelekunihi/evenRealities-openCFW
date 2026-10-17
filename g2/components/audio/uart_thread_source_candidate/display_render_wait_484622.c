/* Apollo Main LVGL render-thread wait bridge, stock 0x484622..0x48462e. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *);

void audio_uart_lv_render_wait_484622(void)
{
    (void)audio_uart_lv_thread_sync_wait_4d46e8(
        audio_uart_display_lv_root + 0x148u);
}
