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
