/* Native FreeType outline cache initializer 0x529cf8. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void *audio_uart_font_outline_render(void *,void *,uint32_t,uint32_t,
                                             uint32_t,void *); /* 0x529f8e */
uint32_t audio_uart_font_outline_cache_initialize(void *entry,void *font) {
    uint8_t *f=(uint8_t *)font;
    uint8_t *context=*(uint8_t **)(void *)(f+0x34u);
    (void)audio_uart_lv_lock_core(context+0x10u);
    uint32_t hinted=(f[0x2cu]>>1u)&1u;
    uint32_t glyph=*(uint32_t *)(void *)entry;
    void *result=audio_uart_font_outline_render(
        *(void **)(void *)(f+0x30u),*(void **)(void *)(context+0x0cu),
        glyph,*(uint32_t *)(void *)(context+8u),hinted,
        *(void **)(void *)(f+0x40u));
    (void)audio_uart_lv_unlock_core(context+0x10u);
    if(result!=0) *(uint32_t *)(void *)((uint8_t *)entry+4u)=(uint32_t)(uintptr_t)result;
    return result!=0;
}
