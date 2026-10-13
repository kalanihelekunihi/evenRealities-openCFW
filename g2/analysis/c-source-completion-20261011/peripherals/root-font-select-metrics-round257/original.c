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

