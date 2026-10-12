#include <stdint.h>
/* Complete451598..4515a4: native wraparound width, no signed overflow. */
uint32_t audio_uart_lv_area_width_451598(const void *area)
{
    const volatile uint32_t *a=area;
    uint32_t x2=a[2],x1=a[0];
    return x2-x1+1u;
}
/* Complete48b750..48b762: low16 flag mask merged with existing header. */
void audio_uart_lv_draw_buf_set_flag_48b750(void *buffer,uint32_t flags)
{
    volatile uint32_t *b=buffer;
    uint32_t merged=(uint16_t)flags|(b[0]>>16);
    b[0]=(b[0]&0xffffu)|(merged<<16);
}
