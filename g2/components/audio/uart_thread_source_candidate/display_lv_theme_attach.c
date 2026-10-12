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
void audio_uart_page_44fe0e(void *display,void *theme) {
    if(!display)display=audio_uart_display_default_get();
    if(!display) {
        audio_uart_lvgl_log(2u,path,0x371u,name,missing);
        return;
    }
    uint8_t *base=(uint8_t *)display;
    __builtin_memcpy(base+0x300u,&theme,4u);
    uint32_t kind;__builtin_memcpy(&kind,base+0x2d4u,4u);
    if(kind!=4u)return;
    void **layers;__builtin_memcpy(&layers,base+0x2b8u,4u);
    void *first=layers[0];
    if(audio_uart_lv_theme_check_44ddea(first)!=0u)return;
    if(audio_uart_lv_theme_check_44ddea(layers[1])!=0u)return;
    if(audio_uart_lv_theme_check_44ddea(layers[2])!=0u)return;
    audio_uart_lv_theme_apply_482f8a(first);
}
