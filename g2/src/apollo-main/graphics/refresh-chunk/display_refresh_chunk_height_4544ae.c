/* Apollo Main LVGL maximum refresh stripe height, 0x4544ae..0x454572. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_font_bitmap_stride(uint32_t, uint8_t);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";
static const char function[] = "get_max_row";

