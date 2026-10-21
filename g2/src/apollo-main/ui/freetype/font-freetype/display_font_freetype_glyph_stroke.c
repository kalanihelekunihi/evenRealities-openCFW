/* Native FT_Glyph_Copy0x567e52 and FT_Glyph_StrokeBorder0x569954.
 * Actual stroker parse/count/export and outline storage remain typed lowers. */
#include <stdint.h>
extern const uint32_t audio_uart_font_outline_glyph_class[]; /* authenticated ROM0x7601d0 */
extern int32_t audio_uart_font_glyph_new(void *,const uint32_t *,void **); /* 0x567e24 */
extern void audio_uart_font_done_glyph(void *); /* 0x567f88 */
extern uint32_t audio_uart_font_outline_orientation(void *); /* 0x527e0a */
extern int32_t audio_uart_font_stroker_parse_outline(void *,void *,uint32_t); /* 0x569748 */
extern void audio_uart_font_stroker_get_counts(void *,uint8_t,uint32_t *,uint32_t *); /* 0x5696d4 */
extern int32_t audio_uart_font_outline_new(void *,uint32_t,uint32_t,void *); /* 0x52797a */
extern void audio_uart_font_outline_done(void *,void *); /* 0x527abc */
extern void audio_uart_font_stroker_export(void *,uint8_t,void *); /* 0x569716 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
uint8_t audio_uart_font_outline_inside(void *outline) { /* 0x567fb0 */
    return (uint8_t)(audio_uart_font_outline_orientation(outline)!=0u);
}
int32_t audio_uart_font_glyph_copy(void *source,void **out) {
    if(out==0 || source==0 || word(source,4u)==0u) return 6;
    *out=0;
    const uint32_t *clazz=(const uint32_t *)(uintptr_t)word(source,4u);
    void *glyph=0;
    int32_t error=audio_uart_font_glyph_new((void *)(uintptr_t)word(source,0u),clazz,&glyph);
    if(error!=0) return error;
    store(glyph,0x0cu,word(source,0x0cu));
    store(glyph,0x10u,word(source,0x10u));
    store(glyph,8u,word(source,8u));
    uint32_t callback=clazz[4];
    if(callback!=0u)
        error=((int32_t (*)(void *,void *))(uintptr_t)callback)(source,glyph);
    if(error!=0) audio_uart_font_done_glyph(glyph);
    else *out=glyph;
    return error;
}
int32_t audio_uart_font_stroke_glyph(void **glyph_ref,void *stroker,
                                     uint32_t inside,uint32_t destroy) {
    if(glyph_ref==0 || *glyph_ref==0 ||
       word(*glyph_ref,4u)!=(uint32_t)(uintptr_t)audio_uart_font_outline_glyph_class)
        return 6;
    void *source=*glyph_ref;
    void *target=0;
    int32_t error=audio_uart_font_glyph_copy(source,&target);
    if(error!=0) return error;
    uint8_t *outline=(uint8_t *)target+0x14u;
    uint8_t outward=audio_uart_font_outline_inside(outline);
    if((inside&0xffu)!=0u) outward^=1u;
    error=audio_uart_font_stroker_parse_outline(stroker,outline,0u);
    if(error==0) {
        uint32_t point_count=0u,contour_count=0u;
        audio_uart_font_stroker_get_counts(stroker,outward,&point_count,&contour_count);
        audio_uart_font_outline_done((void *)(uintptr_t)word(target,0u),outline);
        error=audio_uart_font_outline_new((void *)(uintptr_t)word(target,0u),
                                                 point_count,contour_count,outline);
        if(error==0) {
            *(uint16_t *)(void *)((uint8_t *)target+0x16u)=0u;
            *(uint16_t *)(void *)outline=0u;
            audio_uart_font_stroker_export(stroker,outward,outline);
            if((destroy&0xffu)!=0u) audio_uart_font_done_glyph(source);
            *glyph_ref=target;
            return 0;
        }
    }
    audio_uart_font_done_glyph(target);
    if((destroy&0xffu)==0u) *glyph_ref=0;
    return error;
}
