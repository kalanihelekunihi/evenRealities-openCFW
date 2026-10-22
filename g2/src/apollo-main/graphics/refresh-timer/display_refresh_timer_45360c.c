/* Apollo Main LVGL refresh timer 0x45360c..0x453778. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_display_current_44fa1a(void);
extern void audio_uart_lv_timer_pause(void *);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);
extern void audio_uart_page_43f66c(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_lv_refresh_collect_45377a(void);
extern void audio_uart_lv_refresh_layout_45383c(void);
extern void audio_uart_lv_refresh_render_4539b6(void);
extern void *audio_uart_font_path_node_append(void *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";
static const char function[] = "lv_display_refr_timer";





