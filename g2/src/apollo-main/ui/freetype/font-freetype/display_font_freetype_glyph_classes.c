/* Authenticated FreeType glyph-class vtables ROM0x7601b0/0x7601d0 and
 * native bitmap/outline methods 0x567ca0-0x567e22. */
#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* 0x439c04 */
extern void audio_uart_font_bitmap_init(void *); /* 0x58ed20 */
extern int32_t audio_uart_font_bitmap_copy(void *,const void *,void *); /* 0x58ed2e */
extern int32_t audio_uart_font_bitmap_done(void *,void *); /* 0x58f156 */
extern int32_t audio_uart_font_outline_new(void *,int32_t,int32_t,void *); /* 0x52797a */
extern void audio_uart_font_outline_copy(void *,void *); /* 0x5279e0 */
extern void audio_uart_font_outline_done(void *,void *); /* 0x527abc */
extern void audio_uart_font_outline_transform(void *,void *); /* 0x527ba0 */
extern void audio_uart_font_outline_translate(void *,int32_t,int32_t); /* 0x527b2e */
extern void audio_uart_font_outline_cbox(void *,void *); /* 0x527ace */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
static int16_t sh(const void *p,uint32_t o) {
    return *(const int16_t *)(const void *)((const uint8_t *)p+o);
}
int32_t audio_uart_font_bitmap_glyph_init(void *glyph,void *slot) { /* 0x567ca0 */
    if(word(slot,0x48u)!=0x62697473u) return 0x12;
    store(glyph,0x14u,word(slot,0x64u));
    store(glyph,0x18u,word(slot,0x68u));
    void *bitmap=(void *)(uintptr_t)word(slot,0x9cu);
    if((*(uint8_t *)(void *)((uint8_t *)bitmap+4u)&1u)!=0u) {
        audio_uart_checksum_copy((uint8_t *)glyph+0x1cu,(uint8_t *)slot+0x4cu,0x18u);
        store(bitmap,4u,word(bitmap,4u)&~1u);
        return 0;
    }
    audio_uart_font_bitmap_init((uint8_t *)glyph+0x1cu);
    return audio_uart_font_bitmap_copy((void *)(uintptr_t)word(glyph,0u),
                                       (uint8_t *)slot+0x4cu,(uint8_t *)glyph+0x1cu);
}
int32_t audio_uart_font_bitmap_glyph_copy(void *source,void *target) { /* 0x567d06 */
    store(target,0x14u,word(source,0x14u));
    store(target,0x18u,word(source,0x18u));
    return audio_uart_font_bitmap_copy((void *)(uintptr_t)word(source,0u),
                                       (uint8_t *)source+0x1cu,(uint8_t *)target+0x1cu);
}
void audio_uart_font_bitmap_glyph_done(void *glyph) { /* 0x567d22 */
    (void)audio_uart_font_bitmap_done((void *)(uintptr_t)word(glyph,0u),(uint8_t *)glyph+0x1cu);
}
void audio_uart_font_bitmap_glyph_bbox(void *glyph,void *box) { /* 0x567d32 */
    uint32_t x=(word(glyph,0x14u)<<6u);
    store(box,0u,x);
    store(box,8u,x+(word(glyph,0x20u)<<6u));
    uint32_t y=(word(glyph,0x18u)<<6u);
    store(box,0x0cu,y);
    store(box,4u,y-(word(glyph,0x1cu)<<6u));
}
int32_t audio_uart_font_outline_glyph_init(void *glyph,void *slot) { /* 0x567d54 */
    if(word(slot,0x48u)!=0x6f75746cu) return 0x12;
    int32_t error=audio_uart_font_outline_new((void *)(uintptr_t)word(glyph,0u),
                           sh(slot,0x6cu),sh(slot,0x6eu),(uint8_t *)glyph+0x14u);
    if(error==0) audio_uart_font_outline_copy((uint8_t *)slot+0x6cu,(uint8_t *)glyph+0x14u);
    return error;
}
void audio_uart_font_outline_glyph_done(void *glyph) { /* 0x567d94 */
    audio_uart_font_outline_done((void *)(uintptr_t)word(glyph,0u),(uint8_t *)glyph+0x14u);
}
int32_t audio_uart_font_outline_glyph_copy(void *source,void *target) { /* 0x567da2 */
    int32_t error=audio_uart_font_outline_new((void *)(uintptr_t)word(source,0u),
                            sh(source,0x14u),sh(source,0x16u),(uint8_t *)target+0x14u);
    if(error==0) audio_uart_font_outline_copy((uint8_t *)source+0x14u,(uint8_t *)target+0x14u);
    return error;
}
void audio_uart_font_outline_glyph_transform(void *glyph,void *matrix,void *delta) { /* 0x567dd0 */
    if(matrix!=0) audio_uart_font_outline_transform((uint8_t *)glyph+0x14u,matrix);
    if(delta!=0) audio_uart_font_outline_translate((uint8_t *)glyph+0x14u,
                                      (int32_t)word(delta,0u),(int32_t)word(delta,4u));
}
void audio_uart_font_outline_glyph_bbox(void *glyph,void *box) { /* 0x567df4 */
    audio_uart_font_outline_cbox((uint8_t *)glyph+0x14u,box);
}
int32_t audio_uart_font_outline_glyph_prepare(void *glyph,void *slot) { /* 0x567dfe */
    store(slot,0x48u,0x6f75746cu);
    audio_uart_checksum_copy((uint8_t *)slot+0x6cu,(uint8_t *)glyph+0x14u,0x14u);
    store(slot,0x7cu,word(slot,0x7cu)&~1u);
    return 0;
}
const uintptr_t audio_uart_font_bitmap_glyph_class[8]={
    0x34u,0x62697473u,(uintptr_t)&audio_uart_font_bitmap_glyph_init,
    (uintptr_t)&audio_uart_font_bitmap_glyph_done,
    (uintptr_t)&audio_uart_font_bitmap_glyph_copy,0u,
    (uintptr_t)&audio_uart_font_bitmap_glyph_bbox,0u};
const uintptr_t audio_uart_font_outline_glyph_class[8]={
    0x28u,0x6f75746cu,(uintptr_t)&audio_uart_font_outline_glyph_init,
    (uintptr_t)&audio_uart_font_outline_glyph_done,
    (uintptr_t)&audio_uart_font_outline_glyph_copy,
    (uintptr_t)&audio_uart_font_outline_glyph_transform,
    (uintptr_t)&audio_uart_font_outline_glyph_bbox,
    (uintptr_t)&audio_uart_font_outline_glyph_prepare};
