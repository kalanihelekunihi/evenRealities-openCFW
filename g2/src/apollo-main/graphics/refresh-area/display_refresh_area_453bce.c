/* Apollo Main LVGL refresh-area scheduling, stock 0x453bce..0x453e10. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_lv_layer_reshape_draw_buf_453b78(void *, uint32_t);
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_lv_area_size_450b80(const void *);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lv_area_set_450b5c(void *, uint32_t, uint32_t,
                                          uint32_t, uint32_t);
extern void audio_uart_lv_render_layer_init_4847c4(void *, uint32_t,
                                                    uint32_t, const void *);
extern void audio_uart_lv_render_layer_453e10(void *);
extern void audio_uart_lv_render_wait_484622(void);
extern void audio_uart_lv_refresh_tasks_484548(void);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";



