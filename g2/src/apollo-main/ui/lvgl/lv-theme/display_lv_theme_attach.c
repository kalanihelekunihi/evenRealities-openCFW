/* Native lv_display_set_theme 0x44fe0e. The upstream caller ignores its
 * incidental fourth-register return; memory and child effects are retained. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void); /* selected 0x44fa1a */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern uint32_t audio_uart_lv_theme_check_44ddea(void *);
extern void audio_uart_lv_theme_apply_482f8a(void *);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
static const char name[]="lv_display_set_theme";
static const char missing[]="no display registered";
