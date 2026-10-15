/* Apollo Main display flush lock/unlock, native 0x47381e..0x4738a7.
 * Stock literal 0x47390c identifies the existing lock cell at 0x200746bc. */
#include <stdint.h>

extern void *audio_uart_display_lock;
extern int32_t xQueueSemaphoreTake(void *, uint32_t);
extern int32_t audio_uart_queue_send(void *, const void *, uint32_t, uint32_t);
extern int32_t xQueueGiveFromISR(void *, int32_t *);
extern uint32_t audio_uart_display_in_isr_442228(void);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

void audio_uart_display_flush_begin_47381e(void) {
    void *lock = audio_uart_display_lock;
    if (lock == 0) {
        audio_uart_lvgl_log(3u, "display", 0x124u,
                            "display_buffer_lock", "lock missing");
        return;
    }
    if (xQueueSemaphoreTake(lock, 1000u) == 0)
        audio_uart_lvgl_log(3u, "display", 0x12au,
                            "display_buffer_lock", "lock timeout");
}

void audio_uart_display_flush_end_47386a(void) {
    void *lock = audio_uart_display_lock;
    if (lock == 0) {
        audio_uart_lvgl_log(3u, "display", 0x131u,
                            "display_buffer_unlock", "lock missing");
        return;
    }
    if (audio_uart_display_in_isr_442228() == 0u)
        (void)audio_uart_queue_send(lock, 0, 0u, 0u);
    else
        (void)xQueueGiveFromISR(lock, 0);
}
