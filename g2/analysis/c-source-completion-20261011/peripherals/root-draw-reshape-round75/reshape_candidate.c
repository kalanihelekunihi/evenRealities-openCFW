#include <stdint.h>
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
/* Full native48b86c..48b8d8; all size arithmetic wraps in 32 bits. */
uint32_t audio_uart_lv_draw_buf_size_48b86c(uint32_t width,uint32_t height,uint32_t cf,uint32_t stride)
{
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t bytes=height*stride;
    uint8_t format=(uint8_t)cf;
    if(format==20u) return bytes+height*(stride>>1u);
    switch(format) {
    case 7: return bytes+8u;
    case 8: return bytes+16u;
    case 9: return bytes+64u;
    case 10: return bytes+1024u;
    default: return bytes;
    }
}
/* Full native48b196..48b216; fresh header loads preserve child mutations. */
void *audio_uart_lv_draw_buf_reshape_48b196(void *draw_buffer,uint32_t cf,uint32_t width,uint32_t height,uint32_t stride)
{
    volatile uint32_t *b=draw_buffer;
    if(b==0) return 0;
    if((uint8_t)cf==0u) cf=b[0]>>8u;
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t size=audio_uart_lv_draw_buf_size_48b86c(width,height,(uint8_t)cf,stride);
    if(b[3]<size) return 0;
    b[0]=(b[0]&0xffff00ffu)|((uint32_t)(uint8_t)cf<<8u);
    b[1]=(b[1]&0xffff0000u)|(uint16_t)width;
    b[1]=(b[1]&0x0000ffffu)|((uint32_t)(uint16_t)height<<16u);
    b[2]=(b[2]&0xffff0000u)|(uint16_t)stride;
    return draw_buffer;
}
