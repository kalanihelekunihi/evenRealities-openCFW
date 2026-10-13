/* Native FreeType fixed-strike metrics 0x526a9c. */
#include <stdint.h>
extern int32_t audio_uart_font_divide_metric(int32_t,int32_t); /* native 0x524754 */
extern void audio_uart_font_prepare_metrics(void *,void *); /* native 0x526a4e */
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* selected 0x5246f8 */
extern int32_t audio_uart_font_mul_div(int32_t,int32_t,int32_t); /* native 0x524606 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
static uint32_t word(const void *base,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)base+offset);
}
void audio_uart_font_select_size_metrics(void *face,uint32_t index) {
    uint8_t *f=(uint8_t *)face;
    uint8_t *size=(uint8_t *)(uintptr_t)word(f,0x58u);
    uint8_t *strike=(uint8_t *)(uintptr_t)(word(f,0x20u)+index*0x10u);
    uint32_t x=word(strike,8u);
    uint32_t y=word(strike,12u);
    *(uint16_t *)(void *)(size+0x0cu)=(uint16_t)((x+0x20u)>>6u);
    *(uint16_t *)(void *)(size+0x0eu)=(uint16_t)((y+0x20u)>>6u);
    if((f[8u]&1u)!=0u) {
        int16_t upm=*(int16_t *)(void *)(f+0x44u);
        *(uint32_t *)(void *)(size+0x10u)=
            (uint32_t)audio_uart_font_divide_metric((int32_t)x,(int32_t)upm);
        *(uint32_t *)(void *)(size+0x14u)=
            (uint32_t)audio_uart_font_divide_metric((int32_t)y,(int32_t)upm);
        audio_uart_font_prepare_metrics(face,size+0x0cu);
    } else {
        *(uint32_t *)(void *)(size+0x10u)=0x10000u;
        *(uint32_t *)(void *)(size+0x14u)=0x10000u;
        *(uint32_t *)(void *)(size+0x18u)=y;
        *(uint32_t *)(void *)(size+0x1cu)=0u;
        *(uint32_t *)(void *)(size+0x20u)=(uint32_t)((int32_t)*(int16_t *)(void *)strike<<6u);
        *(uint32_t *)(void *)(size+0x24u)=x;
    }
}

void audio_uart_font_prepare_metrics(void *face,void *metrics) { /* native 0x526a4e */
    uint8_t *f=(uint8_t *)face;
    uint8_t *m=(uint8_t *)metrics;
    uint32_t value=(uint32_t)audio_uart_font_scale_metric(
        (uint32_t)(int32_t)*(int16_t *)(void *)(f+0x46u),(int32_t)word(m,8u));
    *(uint32_t *)(void *)(m+0x0cu)=(value+0x3fu)&~0x3fu;
    value=(uint32_t)audio_uart_font_scale_metric(
        (uint32_t)(int32_t)*(int16_t *)(void *)(f+0x48u),(int32_t)word(m,8u));
    *(uint32_t *)(void *)(m+0x10u)=value&~0x3fu;
    value=(uint32_t)audio_uart_font_scale_metric(
        (uint32_t)(int32_t)*(int16_t *)(void *)(f+0x4au),(int32_t)word(m,8u));
    *(uint32_t *)(void *)(m+0x14u)=(value+0x20u)&~0x3fu;
    value=(uint32_t)audio_uart_font_scale_metric(
        (uint32_t)(int32_t)*(int16_t *)(void *)(f+0x4cu),(int32_t)word(m,4u));
    *(uint32_t *)(void *)(m+0x18u)=(value+0x20u)&~0x3fu;
}

void audio_uart_font_request_size_metrics(void *face,const void *request) { /* native 0x526b04 */
    uint8_t *f=(uint8_t *)face;
    const uint8_t *r=(const uint8_t *)request;
    uint8_t *size=(uint8_t *)(uintptr_t)word(f,0x58u);
    uint8_t *metrics=size+0x0cu;
    if((f[8u]&1u)==0u) {
        audio_uart_buffer_zero(metrics,0x1cu,0u);
        *(uint32_t *)(void *)(size+0x10u)=0x10000u;
        *(uint32_t *)(void *)(size+0x14u)=0x10000u;
        return;
    }
    int32_t x_base=0,y_base=0,x_request=0,y_request=0;
    uint8_t type=r[0];
    if(type==0u) {
        x_base=(int32_t)(uint16_t)*(uint16_t *)(void *)(f+0x44u);
        y_base=x_base;
    } else if(type==1u) {
        x_base=(int32_t)*(int16_t *)(void *)(f+0x46u)-
               (int32_t)*(int16_t *)(void *)(f+0x48u);
        y_base=x_base;
    } else if(type==2u) {
        x_base=(int32_t)word(f,0x3cu)-(int32_t)word(f,0x34u);
        y_base=(int32_t)word(f,0x40u)-(int32_t)word(f,0x38u);
    } else if(type==3u) {
        x_base=(int32_t)*(int16_t *)(void *)(f+0x4cu);
        y_base=(int32_t)*(int16_t *)(void *)(f+0x46u)-
               (int32_t)*(int16_t *)(void *)(f+0x48u);
    } else if(type==4u) {
        uint32_t x=word(r,4u),y=word(r,8u);
        if(x==0u) x=y;
        else if(y==0u) y=x;
        *(uint32_t *)(void *)(size+0x10u)=x;
        *(uint32_t *)(void *)(size+0x14u)=y;
        goto finish;
    }
    if(x_base<0) x_base=-x_base;
    if(y_base<0) y_base=-y_base;
    int32_t x_dpi=(int32_t)word(r,0x0cu),y_dpi=(int32_t)word(r,0x10u);
    x_request=x_dpi==0?(int32_t)word(r,4u):
        ((int32_t)((uint32_t)x_dpi*word(r,4u)+36u)/72);
    y_request=y_dpi==0?(int32_t)word(r,8u):
        ((int32_t)((uint32_t)y_dpi*word(r,8u)+36u)/72);
    if(word(r,4u)==0u) {
        int32_t scale=audio_uart_font_divide_metric(y_request,y_base);
        *(int32_t *)(void *)(size+0x10u)=scale;
        *(int32_t *)(void *)(size+0x14u)=scale;
        x_request=audio_uart_font_mul_div(y_request,x_base,y_base);
    } else {
        int32_t xscale=audio_uart_font_divide_metric(x_request,x_base);
        *(int32_t *)(void *)(size+0x10u)=xscale;
        if(word(r,8u)==0u) {
            *(int32_t *)(void *)(size+0x14u)=xscale;
            y_request=audio_uart_font_mul_div(x_request,y_base,x_base);
        } else {
            int32_t yscale=audio_uart_font_divide_metric(y_request,y_base);
            if(type==3u) { if(xscale<yscale) yscale=xscale; else xscale=yscale; }
            *(int32_t *)(void *)(size+0x10u)=xscale;
            *(int32_t *)(void *)(size+0x14u)=yscale;
        }
    }
finish:
    if(type!=0u) {
        int16_t upm=*(int16_t *)(void *)(f+0x44u);
        x_request=audio_uart_font_scale_metric((uint32_t)(int32_t)upm,
                    *(int32_t *)(void *)(size+0x10u));
        y_request=audio_uart_font_scale_metric((uint32_t)(int32_t)upm,
                    *(int32_t *)(void *)(size+0x14u));
    }
    *(uint16_t *)(void *)(size+0x0cu)=(uint16_t)((x_request+0x20)>>6u);
    *(uint16_t *)(void *)(size+0x0eu)=(uint16_t)((y_request+0x20)>>6u);
    audio_uart_font_prepare_metrics(face,metrics);
}
