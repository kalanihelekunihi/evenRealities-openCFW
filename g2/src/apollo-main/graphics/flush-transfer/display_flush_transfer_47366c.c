/* Apollo Main display transfer 0x47366c..0x4736f3.
 * The stock 0x4738f4 literal references area [0,0,575,287]. */
#include <stdint.h>

extern void *audio_uart_display_instance;
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *, const void *, uint32_t);
extern void audio_uart_display_frame_transfer_5fa13c(const void *, const void *,
                                                     uint32_t, uint32_t);
extern void audio_uart_ambiq_blend_clear_4b075e(void *);
extern uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

void audio_uart_display_flush_transfer_47366c(uint32_t display_index,
                                               const void *pixels,
                                               uint32_t sync) {
    if (display_index != 0u) {
        audio_uart_lvgl_log(3u, "display", 0xa1u,
                            "display_flush_transfer", "invalid display index");
        __builtin_trap();
    }
    static const int32_t full_area[4] = {0, 0, 0x23f, 0x11f};
    int32_t area[4];
    (void)audio_uart_display_area_copy_439c04(area, full_area, sizeof(area));
    int32_t width = audio_uart_lv_area_width_451598(area);
    int32_t height = audio_uart_lv_area_height_4515a4(area);
    if (width <= 0 || height <= 0) return;
    if ((uint8_t)audio_uart_ambiq_bind_buffer_4b092a(audio_uart_display_instance,
                                                      area, 0u) != 1u) return;
    const uint8_t *instance = (const uint8_t *)audio_uart_display_instance;
    const void *output = (const void *)(uintptr_t)*(const uint32_t *)(const void *)(instance + 0x10u);
    audio_uart_display_frame_transfer_5fa13c(pixels, output, 0x240u, 0x120u);
    audio_uart_ambiq_blend_clear_4b075e(0);
    (void)audio_uart_ambiq_submit_4b0c8a((uint8_t)sync);
}
