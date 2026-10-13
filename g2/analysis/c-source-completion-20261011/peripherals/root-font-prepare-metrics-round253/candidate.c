#include <stdint.h>
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t);
static uint32_t word(const void *p,uint32_t o){return *(const uint32_t*)((const uint8_t*)p+o);}
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
