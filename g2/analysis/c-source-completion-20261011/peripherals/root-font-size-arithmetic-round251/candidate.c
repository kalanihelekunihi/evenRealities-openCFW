#include <stdint.h>
static uint32_t word(const void *base,uint32_t off){return *(const uint32_t *)((const uint8_t *)base+off);}
int32_t audio_uart_font_request_size_internal(void *face,const void *request,
                                              uint32_t ignore_width,uint32_t *index) {
    uint8_t *f=(uint8_t *)face;
    const uint8_t *r=(const uint8_t *)request;
    if((f[8u]&2u)==0u) return 0x23;
    if(r[0]!=0u) return 7;
    int32_t x=(int32_t)word(r,4u),y=(int32_t)word(r,8u);
    int32_t x_dpi=(int32_t)word(r,0x0cu),y_dpi=(int32_t)word(r,0x10u);
    if(x_dpi!=0) x=(int32_t)((uint32_t)x_dpi*(uint32_t)x+36u)/72;
    if(y_dpi!=0) y=(int32_t)((uint32_t)y_dpi*(uint32_t)y+36u)/72;
    if(word(r,4u)==0u) x=y;
    if(word(r,8u)==0u) y=x;
    uint32_t x_pixels=((uint32_t)x+0x20u)&~0x3fu;
    uint32_t y_pixels=((uint32_t)y+0x20u)&~0x3fu;
    if(x_pixels==0u || y_pixels==0u) return 0x17;
    uint32_t count=word(f,0x1cu);
    uint8_t *strikes=(uint8_t *)(uintptr_t)word(f,0x20u);
    for(uint32_t i=0u;(int32_t)i<(int32_t)count;i++) {
        uint8_t *strike=strikes+i*0x10u;
        uint32_t sy=(word(strike,0x0cu)+0x20u)&~0x3fu;
        uint32_t sx=(word(strike,8u)+0x20u)&~0x3fu;
        if(y_pixels==sy && (x_pixels==sx || (ignore_width&255u)!=0u)) {
            if(index!=0) *index=i;
            return 0;
        }
    }
    return 0x17;
}
