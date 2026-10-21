/* Native lv_display_is_invalidation_enabled 0x44fed2. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void); /* 0x44fa1a */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
static const char function[]="lv_display_is_invalidation_enabled";
static const char no_display[]="no display registered";
uint32_t audio_uart_lv_display_has_active_window(void *display) {
    if(display==0) display=audio_uart_display_default_get();
    if(display==0) {
        audio_uart_lvgl_log(2u,source_path,943u,function,no_display);
        return 0u;
    }
    return (*(const int32_t *)(const void *)((const uint8_t *)display+0x264u)>0) ? 1u : 0u;
}
