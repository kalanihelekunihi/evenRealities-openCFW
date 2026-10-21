/* Native display previous/top/system/bottom screen getters at
 * 0x44fc90/0x44fcbe/0x44fcfc/0x44fd38. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
static void *screen_field(void *display,uint32_t offset,uint32_t line,const char *name,const char *message) {
    if(display==0)display=audio_uart_display_default_get();
    if(display==0) {audio_uart_lvgl_log(2u,path,line,name,message);return 0;}
    return *(void **)(void *)((uint8_t *)display+offset);
}
void *audio_uart_lv_display_previous_screen_44fc90(void *d) {
    return screen_field(d,0x2ccu,0x250u,"lv_display_get_screen_prev",
                        "no display registered to get its previous screen");
}
void *audio_uart_lv_display_top_layer_44fcbe(void *d) {
    return screen_field(d,0x2c0u,0x25bu,"lv_display_get_layer_top",
                        "lv_layer_top: no display registered to get its top layer");
}
void *audio_uart_lv_display_system_layer_44fcfc(void *d) {
    return screen_field(d,0x2bcu,0x266u,"lv_display_get_layer_sys",
                        "lv_layer_sys: no display registered to get its sys. layer");
}
void *audio_uart_lv_display_bottom_layer_44fd38(void *d) {
    return screen_field(d,0x2c8u,0x271u,"lv_display_get_layer_bottom",
                        "lv_layer_bottom: no display registered to get its bottom layer");
}
