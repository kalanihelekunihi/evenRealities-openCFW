/* Complete native48b762..48b7a6; following literal pool excluded.
 * Unselected until native child-contract comparisons pass. */
#include <stdint.h>
extern uint32_t audio_uart_lv_draw_buf_init_48aef8(void *,uint32_t,uint32_t,uint32_t,uint32_t,void *,uint32_t);
uint32_t audio_uart_lv_draw_buf_from_image_48b762(void *draw_buffer,const void *image)
{
    const volatile uint32_t *src=image;
    uint32_t data_size=src[3];
    void *data=(void *)(uintptr_t)src[4];
    uint32_t stride=(uint16_t)src[2];
    uint32_t cf=(uint8_t)(src[0]>>8);
    uint32_t height=src[1]>>16;
    uint32_t width=(uint16_t)src[1];
    uint32_t result=audio_uart_lv_draw_buf_init_48aef8(draw_buffer,width,height,cf,stride,data,data_size);
    if((uint8_t)result!=1u) return (uint8_t)result;
    uint32_t flags=src[0]>>16;
    volatile uint32_t *dst=draw_buffer;
    dst[0]=(dst[0]&0xffffu)|(flags<<16);
    return (uint8_t)result;
}
