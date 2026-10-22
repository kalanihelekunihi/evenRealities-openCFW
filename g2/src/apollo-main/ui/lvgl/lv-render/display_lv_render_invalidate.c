/* Native LVGL display invalidation 0x4534be. Rectangle arithmetic and the
 * 32-entry coalescing threshold follow the product's LVGL 9.3 body. */
#include <stdint.h>

extern void *audio_uart_display_default_get(void); /* 0x44fa1a */
extern uint32_t audio_uart_lv_display_has_active_window(void *); /* 0x44fed2 */
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *,const int32_t *,const int32_t *);
extern uint32_t audio_uart_lv_area_contains_450f28(const int32_t *,const int32_t *,uint32_t);
extern void audio_uart_lv_area_copy_4530fc(int32_t *,const int32_t *);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *,uint32_t,void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";

