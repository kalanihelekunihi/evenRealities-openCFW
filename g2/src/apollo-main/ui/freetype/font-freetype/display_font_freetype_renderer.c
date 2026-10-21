/* Native FreeType renderer list lookup 0x52705a and render dispatch 0x5271c0. */
#include <stdint.h>
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
void *audio_uart_font_lookup_renderer(void *library,uint32_t format,void **cursor) {
    if(library==0) return 0;
    uint32_t node=word(library,0x94u);
    if(cursor!=0) {
        if(*cursor!=0) node=word(*cursor,4u);
        *cursor=0;
    }
    while(node!=0u) {
        uint32_t renderer=word((void *)(uintptr_t)node,8u);
        if(word((void *)(uintptr_t)renderer,0x10u)==format) {
            if(cursor!=0) *cursor=(void *)(uintptr_t)node;
            return (void *)(uintptr_t)renderer;
        }
        node=word((void *)(uintptr_t)node,4u);
    }
    return 0;
}
int32_t audio_uart_font_render_glyph_internal(void *library,void *slot,uint8_t mode) {
    uint32_t format=word(slot,0x48u);
    if(format==0x62697473u) return 0;
    void *cursor=0;
    void *renderer;
    if(format==0x6f75746cu) {
        cursor=(void *)(uintptr_t)word(library,0x94u);
        renderer=(void *)(uintptr_t)word(library,0x9cu);
    } else renderer=audio_uart_font_lookup_renderer(library,format,&cursor);
    int32_t error=7;
    while(renderer!=0) {
        uint32_t callback=word(renderer,0x3cu);
        error=((int32_t (*)(void *,void *,uint8_t,void *))(uintptr_t)callback)(
            renderer,slot,mode,0);
        if(error==0 || (error&0xff)!=0x13) break;
        renderer=audio_uart_font_lookup_renderer(library,format,&cursor);
    }
    return error;
}
