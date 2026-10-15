/* Apollo Main display flush callback 0x4736f4..0x473781.
 * Stock literal 0x473908 is Thumb pointer 0x4736f5. */
#include <stdint.h>

extern void *audio_uart_display_surface;
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern int32_t audio_uart_display_area_x_44fb4e(void *);
extern int32_t audio_uart_display_area_y_44fb9a(void *);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern void audio_uart_lv_draw_flush_cache_48abb8(void *, uint32_t);
extern uint32_t audio_uart_display_flush_ready_44fc42(void *);
extern void audio_uart_display_flush_begin_47381e(void);
extern void audio_uart_display_flush_transfer_47366c(uint32_t, const void *, uint32_t);
extern void audio_uart_display_flush_end_47386a(void);
extern void audio_uart_display_flush_view_474066(uint32_t, uint32_t,
                                                 uint32_t, uint32_t,
                                                 uint32_t, uint32_t);

void audio_uart_display_flush_callback_4736f4(void *buffer, const void *area,
                                               const void *pixels) {
    uint8_t moved_area[16];
    (void)audio_uart_display_area_copy_439c04(moved_area, area, sizeof(moved_area));
    int32_t x = audio_uart_display_area_x_44fb4e(buffer);
    int32_t y = audio_uart_display_area_y_44fb9a(buffer);
    audio_uart_ambiq_area_move_450bb2(moved_area, -x, -y);
    audio_uart_lv_draw_flush_cache_48abb8(audio_uart_display_surface, 0u);
    uint32_t ready = (uint8_t)audio_uart_display_flush_ready_44fc42(buffer);
    if (ready != 0u) {
        audio_uart_display_flush_begin_47381e();
        audio_uart_display_flush_transfer_47366c(0u, pixels, 1u);
        audio_uart_display_flush_end_47386a();
    }
    *(uint32_t *)(void *)((uint8_t *)buffer + 0x30u) = 0u;
    if (ready != 0u) {
        audio_uart_display_flush_begin_47381e();
        audio_uart_display_flush_view_474066(0u, 0u, 0u, 0u, 0x240u, 0x120u);
    }
}

const void *audio_uart_display_flush_callback =
    (const void *)audio_uart_display_flush_callback_4736f4;
