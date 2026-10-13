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
