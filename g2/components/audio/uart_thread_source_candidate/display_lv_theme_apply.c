/* Native 0x482f74 / 0x44fe7e / 0x482f8a theme lookup and application. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);
extern void *audio_uart_lv_display_for_object(void *);
extern void audio_uart_lv_style_remove_44ba9a(void *,void *,uint32_t);
void audio_uart_lv_theme_refresh_44bc3a(void *object) {
    /* ROM literal DAT_0044c828 is 0x000fffff. */
    audio_uart_lv_style_remove_44ba9a(object,0,0x000fffffu);
}
void audio_uart_lv_theme_apply_chain_482fce(void *theme,void *object) {
    uint8_t *t=(uint8_t *)theme;
    void *parent=*(void **)(void *)(t+4u);
    if(parent)audio_uart_lv_theme_apply_chain_482fce(parent,object);
    void (*callback)(void *,void *)=*(void (**)(void *,void *))(void *)t;
    if(callback)callback(theme,object);
}
void audio_uart_lv_theme_walk_482ff2(void *theme,void *object) {
    uint8_t *o=(uint8_t *)object;
    void *child=*(void **)(void *)o;
    /* Native reads the first word of child before checking it; null child
     * therefore faults rather than becoming an empty no-op. */
    void *next=*(void **)(void *)child;
    if(next!=0) {
        uint32_t flags=*(uint32_t *)(void *)((uint8_t *)child+0x20u);
        if((flags&0x00100000u)!=0u) {
            *(void **)(void *)o=next;
            audio_uart_lv_theme_walk_482ff2(theme,object);
        }
    }
    *(void **)(void *)o=child;
    audio_uart_lv_theme_apply_chain_482fce(theme,object);
}

void *audio_uart_lv_theme_lookup_44fe7e(void *display) {
    if(display==0)display=audio_uart_display_default_get();
    return *(void **)(void *)((uint8_t *)display+0x300u);
}
void *audio_uart_lv_theme_display_482f74(void *object) {
    void *display=object==0 ? audio_uart_display_default_get() :
                             audio_uart_lv_display_for_object(object);
    return audio_uart_lv_theme_lookup_44fe7e(display);
}
void audio_uart_lv_theme_apply_482f8a(void *object) {
    void *theme=audio_uart_lv_theme_display_482f74(object);
    if(theme!=0) {
        audio_uart_lv_theme_refresh_44bc3a(object);
        audio_uart_lv_theme_walk_482ff2(theme,object);
    }
}
