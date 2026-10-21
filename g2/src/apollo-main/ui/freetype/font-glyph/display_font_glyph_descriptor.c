/* Native LVGL FreeType glyph descriptor callback 0x4b26a4. */
#include <stdint.h>
extern uint32_t audio_uart_font_glyph_index(void *,uint32_t); /* 0x4b2774 */
extern int32_t audio_uart_font_glyph_kerning(void *,uint32_t,uint32_t); /* 0x4b28ee */
static uint16_t glyph_half(const uint8_t *p,uint32_t offset) {
    return *(const uint16_t *)(const void *)(p+offset);
}
uint32_t audio_uart_font_glyph_descriptor(void *font,void *destination,
                                          uint32_t codepoint,uint32_t previous_codepoint) {
    uint8_t *f=(uint8_t *)font;
    uint8_t *d=(uint8_t *)destination;
    uint8_t *inner=*(uint8_t **)(void *)(f+0x18u);
    uint32_t space=(codepoint==9u);
    if(space) codepoint=0x20u;
    uint32_t glyph=audio_uart_font_glyph_index(font,codepoint);
    if(glyph==0u) return 0u;
    int8_t kerning=0;
    if(*(const uint32_t *)(const void *)(inner+0xcu)!=0u) {
        uint32_t previous=audio_uart_font_glyph_index(font,previous_codepoint);
        if(previous!=0u)
            kerning=(int8_t)audio_uart_font_glyph_kerning(font,glyph,previous);
    }
    const uint8_t *metrics=(const uint8_t *)(uintptr_t)
        (*(const uint32_t *)(const void *)(inner+4u)+glyph*16u);
    uint32_t advance=*(const uint32_t *)(const void *)(metrics+4u);
    if(space) advance<<=1u;
    int32_t advance_fraction=((int32_t)glyph_half(inner,0x10u)*(int32_t)kerning)>>4u;
    *(uint16_t *)(void *)(d+4u)=
        (uint16_t)((advance_fraction+(int32_t)advance+8)>>4u);
    *(uint16_t *)(void *)(d+8u)=glyph_half(metrics,10u);
    *(uint16_t *)(void *)(d+6u)=glyph_half(metrics,8u);
    *(uint16_t *)(void *)(d+10u)=glyph_half(metrics,12u);
    *(uint16_t *)(void *)(d+12u)=glyph_half(metrics,14u);
    uint16_t mode=glyph_half(inner,0x12u);
    d[0xeu]=(uint8_t)((mode>>9u)&0x0fu);
    if((mode>>14u)==3u) d[0xeu]=(uint8_t)(d[0xeu]+0x10u);
    d[0xfu]&=0xfeu;
    *(uint32_t *)(void *)(d+0x18u)=glyph;
    if(space)
        *(uint16_t *)(void *)(d+6u)=
            (uint16_t)(*(uint16_t *)(void *)(d+6u)<<1u);
    return 1u;
}
