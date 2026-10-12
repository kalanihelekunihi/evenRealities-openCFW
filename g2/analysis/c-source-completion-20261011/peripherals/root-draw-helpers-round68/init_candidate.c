/* Complete native48aef8..48affa; unselected pending native comparison. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_draw_memzero_48aa54(void *,uint32_t);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern void *audio_uart_lv_draw_align_48ab04(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
uint32_t audio_uart_lv_draw_buf_init_48aef8(void *draw_buffer,uint32_t width,uint32_t height,uint32_t cf,uint32_t stride,void *data,uint32_t data_size)
{
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    if(draw_buffer==0) {
        audio_uart_lvgl_log(3u,source,286u,"lv_draw_buf_init","Asserted at expression: %s (%s)","draw_buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(draw_buffer==0) return 0u;
    audio_uart_lv_draw_memzero_48aa54(draw_buffer,28u);
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)cf);
    uint32_t required=height*stride;
    if(data_size<required) {
        audio_uart_lvgl_log(2u,source,293u,"lv_draw_buf_init","Data size too small, required: %d, provided: %d",required,data_size);return 0u;
    }
    volatile uint32_t *dst=draw_buffer;
    dst[1]=(dst[1]&0xffff0000u)|(uint16_t)width;
    dst[1]=(dst[1]&0xffffu)|((uint32_t)(uint16_t)height<<16);
    dst[0]=(dst[0]&0xffff00ffu)|((uint32_t)(uint8_t)cf<<8);
    dst[2]=(dst[2]&0xffff0000u)|(uint16_t)stride;
    dst[0]=(uint16_t)dst[0];
    dst[0]=(dst[0]&0xffffff00u)|25u;
    dst[4]=(uint32_t)(uintptr_t)data;dst[5]=(uint32_t)(uintptr_t)data;
    dst[6]=(uint32_t)(uintptr_t)(audio_uart_display_lv_root+0xc8u);dst[3]=data_size;
    if((uint32_t)(uintptr_t)audio_uart_lv_draw_align_48ab04(data,(uint8_t)cf)!=dst[5]) {
        audio_uart_lvgl_log(2u,source,310u,"lv_draw_buf_init","Data is not aligned, ignored");
    }
    return 1u;
}
