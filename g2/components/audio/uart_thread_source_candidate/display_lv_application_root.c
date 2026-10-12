/* Native lv_screen_active getter 0x44fc62 and display application root
 * 0x44ff38. Both use the selected default display getter 0x44fa1a. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
static const char name[]="lv_display_get_screen_active";
static const char missing[]="no display registered to get its active screen";

void *audio_uart_display_active_screen_get(void *display) {
    if(!display)display=audio_uart_display_default_get();
    if(!display) {
        audio_uart_lvgl_log(2u,path,0x245u,name,missing);
        return 0;
    }
    return *(void **)(void *)((uint8_t *)display+0x2c4u);
}
void *audio_uart_display_application_init(void) {
    void *display=audio_uart_display_default_get();
    return audio_uart_display_active_screen_get(display);
}
