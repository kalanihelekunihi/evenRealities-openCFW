/* Native FT_Get_Glyph 0x567ec8 and glyph-new 0x567e24, using the authenticated
 * bitmap/outline glyph-class table roles at ROM 0x7601b0/0x7601d0. */
#include <stdint.h>
extern const uint32_t audio_uart_font_bitmap_glyph_class[]; /* ROM 0x7601b0 */
extern const uint32_t audio_uart_font_outline_glyph_class[]; /* ROM 0x7601d0 */
extern void *audio_uart_font_lookup_renderer(void *,uint32_t,void *); /* 0x52705a */
extern void audio_uart_font_done_glyph(void *); /* 0x567f88 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
void *audio_uart_font_mem_alloc(void *memory,int32_t size,int32_t *error) { /* 0x529148/0x529176 */
    void *result=0;
    int32_t status=0;
    if(size>=1) {
        uint32_t callback=word(memory,4u);
        result=((void *(*)(void *,int32_t))(uintptr_t)callback)(memory,size);
        if(result==0) status=0x40;
        else audio_uart_buffer_zero(result,(uint32_t)size,0u);
    } else if(size<0) status=6;
    *error=status;
    return result;
}
int32_t audio_uart_font_glyph_new(void *library,const uint32_t *clazz,void **out) { /* 0x567e24 */
    void *memory=(void *)(uintptr_t)word(library,0u);
    *out=0;
    int32_t error=0;
    void *glyph=audio_uart_font_mem_alloc(memory,(int32_t)clazz[0],&error);
    if(error==0) {
        store(glyph,0u,(uint32_t)(uintptr_t)library);
        store(glyph,4u,(uint32_t)(uintptr_t)clazz);
        store(glyph,8u,clazz[1]);
        *out=glyph;
    }
    return error;
}
int32_t audio_uart_font_get_glyph(void *slot,void **out) {
    if(slot==0) return 0x25;
    void *library=(void *)(uintptr_t)word(slot,0u);
    if(out==0) return 6;
    uint32_t format=word(slot,0x48u);
    const uint32_t *clazz=0;
    if(format==0x62697473u) clazz=audio_uart_font_bitmap_glyph_class;
    else if(format==0x6f75746cu) clazz=audio_uart_font_outline_glyph_class;
    else {
        void *renderer=audio_uart_font_lookup_renderer(library,format,0);
        if(renderer!=0) clazz=(const uint32_t *)(const void *)((const uint8_t *)renderer+0x14u);
    }
    if(clazz==0) return 0x12;
    void *glyph=0;
    int32_t error=audio_uart_font_glyph_new(library,clazz,&glyph);
    if(error!=0) return error;
    uint32_t advance_x=word(slot,0x40u),advance_y=word(slot,0x44u);
    if(advance_x+0x1fffffu>=0x3fffffu || advance_y+0x1fffffu>=0x3fffffu) error=6;
    else {
        store(glyph,0x0cu,advance_x<<10u);
        store(glyph,0x10u,advance_y<<10u);
        uint32_t callback=clazz[2];
        error=((int32_t (*)(void *,void *))(uintptr_t)callback)(glyph,slot);
    }
    if(error!=0) audio_uart_font_done_glyph(glyph);
    else *out=glyph;
    return error;
}
