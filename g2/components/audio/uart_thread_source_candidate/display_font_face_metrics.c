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
void audio_uart_font_select_size_metrics(void *face,uint32_t index) { /* native 0x526a9c */
    uint8_t *f=(uint8_t *)face;
    volatile uint8_t *m=(volatile uint8_t *)(uintptr_t)(word(f,88u)+12u);
    const volatile uint8_t *s=(const volatile uint8_t *)(uintptr_t)(word(f,32u)+index*16u);
    *(volatile uint16_t *)(m+0u)=(uint16_t)((int32_t)(*(const volatile uint32_t *)(s+8u)+32u)>>6u);
    *(volatile uint16_t *)(m+2u)=(uint16_t)((int32_t)(*(const volatile uint32_t *)(s+12u)+32u)>>6u);
    if((f[8u]&1u)!=0u) {
        *(volatile int32_t *)(m+4u)=audio_uart_font_divide_metric((int32_t)*(const volatile uint32_t *)(s+8u),(int32_t)*(uint16_t *)(void *)(f+68u));
        *(volatile int32_t *)(m+8u)=audio_uart_font_divide_metric((int32_t)*(const volatile uint32_t *)(s+12u),(int32_t)*(uint16_t *)(void *)(f+68u));
        audio_uart_font_prepare_metrics(face,(void *)m);
    } else {
        *(volatile uint32_t *)(m+4u)=65536u;
        *(volatile uint32_t *)(m+8u)=65536u;
        *(volatile uint32_t *)(m+12u)=*(const volatile uint32_t *)(s+12u);
        *(volatile uint32_t *)(m+16u)=0u;
        *(volatile uint32_t *)(m+20u)=(uint32_t)(int32_t)*(const volatile int16_t *)s<<6u;
        *(volatile uint32_t *)(m+24u)=*(const volatile uint32_t *)(s+8u);
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
    const volatile uint8_t *r=(const volatile uint8_t *)request;
    volatile uint8_t *m=(volatile uint8_t *)(uintptr_t)(word(f,0x58u)+12u);
    int32_t xb=0,yb=0,x=0,y=0;
    if((f[8u]&1u)==0u) {
        audio_uart_buffer_zero((void *)m,28u,0u);
        *(volatile uint32_t *)(m+4u)=65536u;
        *(volatile uint32_t *)(m+8u)=65536u;
        return;
    }
    uint8_t type=r[0];
    if(type==0u) xb=yb=(int32_t)*(uint16_t *)(void *)(f+68u);
    else if(type==1u) xb=yb=(int32_t)*(int16_t *)(void *)(f+70u)-(int32_t)*(int16_t *)(void *)(f+72u);
    else if(type==2u) {
        xb=(int32_t)(word(f,60u)-word(f,52u));
        yb=(int32_t)(word(f,64u)-word(f,56u));
    } else if(type==3u) {
        xb=(int32_t)*(int16_t *)(void *)(f+76u);
        yb=(int32_t)*(int16_t *)(void *)(f+70u)-(int32_t)*(int16_t *)(void *)(f+72u);
    } else if(type==4u) {
        *(volatile uint32_t *)(m+4u)=*(const volatile uint32_t *)(r+4u);
        *(volatile uint32_t *)(m+8u)=*(const volatile uint32_t *)(r+8u);
        if(*(volatile uint32_t *)(m+4u)==0u)
            *(volatile uint32_t *)(m+4u)=*(volatile uint32_t *)(m+8u);
        else if(*(volatile uint32_t *)(m+8u)==0u)
            *(volatile uint32_t *)(m+8u)=*(volatile uint32_t *)(m+4u);
        goto finish;
    }
    if(xb<0) xb=(int32_t)(0u-(uint32_t)xb);
    if(yb<0) yb=(int32_t)(0u-(uint32_t)yb);
    if(*(const volatile uint32_t *)(r+12u)!=0u)
        x=(int32_t)(*(const volatile uint32_t *)(r+4u)**(const volatile uint32_t *)(r+12u)+36u)/72;
    else x=(int32_t)*(const volatile uint32_t *)(r+4u);
    if(*(const volatile uint32_t *)(r+16u)!=0u)
        y=(int32_t)(*(const volatile uint32_t *)(r+8u)**(const volatile uint32_t *)(r+16u)+36u)/72;
    else y=(int32_t)*(const volatile uint32_t *)(r+8u);
    if(*(const volatile uint32_t *)(r+4u)!=0u) {
        *(volatile int32_t *)(m+4u)=audio_uart_font_divide_metric(x,xb);
        if(*(const volatile uint32_t *)(r+8u)!=0u) {
            *(volatile int32_t *)(m+8u)=audio_uart_font_divide_metric(y,yb);
            if(r[0]==3u) {
                if(*(volatile int32_t *)(m+4u)<*(volatile int32_t *)(m+8u))
                    *(volatile uint32_t *)(m+8u)=*(volatile uint32_t *)(m+4u);
                else *(volatile uint32_t *)(m+4u)=*(volatile uint32_t *)(m+8u);
            }
        } else {
            *(volatile uint32_t *)(m+8u)=*(volatile uint32_t *)(m+4u);
            y=audio_uart_font_mul_div(x,yb,xb);
        }
    } else {
        int32_t scale=audio_uart_font_divide_metric(y,yb);
        *(volatile int32_t *)(m+8u)=scale;
        *(volatile int32_t *)(m+4u)=scale;
        x=audio_uart_font_mul_div(y,xb,yb);
    }
finish:
    if(r[0]!=0u) {
        x=audio_uart_font_scale_metric((uint32_t)*(uint16_t *)(void *)(f+68u),*(volatile int32_t *)(m+4u));
        y=audio_uart_font_scale_metric((uint32_t)*(uint16_t *)(void *)(f+68u),*(volatile int32_t *)(m+8u));
    }
    *(volatile uint16_t *)(m+0u)=(uint16_t)((int32_t)((uint32_t)x+32u)>>6u);
    *(volatile uint16_t *)(m+2u)=(uint16_t)((int32_t)((uint32_t)y+32u)>>6u);
    audio_uart_font_prepare_metrics(face,(void *)m);
}
