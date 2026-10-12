#include <stdint.h>
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern uint32_t audio_uart_lv_draw_buf_size_48b86c(uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_grid_move_45475a(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native48b34e..48b51e; assertions retain native repeated zero-store. */
uint32_t audio_uart_lv_draw_buf_adjust_stride_48b34e(void *buffer,uint32_t stride)
{
    volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_adjust_stride";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,449u,function,"Asserted at expression: %s (%s)","src != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b[4]==0u) {
        audio_uart_lvgl_log(3u,source,450u,function,"Asserted at expression: %s (%s)","src->data != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0 || b[4]==0u) return 0u;
    uint32_t width=(uint16_t)b[1],height=b[1]>>16u;
    if(audio_uart_lv_draw_buf_has_flag_48b73c((void *)b,32u)==0u) return 0u;
    if(stride==0u) stride=audio_uart_font_bitmap_stride(width,(uint8_t)(b[0]>>8u));
    if((uint16_t)b[2]==stride) return 1u;
    uint32_t minimal=(audio_uart_lv_color_bpp_440f44((uint8_t)(b[0]>>8u))*width+7u)>>3u;
    if(stride<minimal) {audio_uart_lvgl_log(2u,source,477u,function,"New stride is too small. min: %d",minimal);return 0u;}
    uint32_t required=audio_uart_lv_draw_buf_size_48b86c(width,height,(uint8_t)(b[0]>>8u),stride);
    if(b[3]<required) return 0u;
    uint32_t palette;
    if((uint8_t)(b[0]>>8u)==7u) palette=2u;
    else if((uint8_t)(b[0]>>8u)==8u) palette=4u;
    else if((uint8_t)(b[0]>>8u)==9u) palette=16u;
    else if((uint8_t)(b[0]>>8u)==10u) palette=256u;
    else palette=0u;
    uint32_t source_data,destination_data;
    if((uint16_t)b[2]<stride) {
        source_data=b[4]+palette*4u+(uint16_t)b[2]*(height-1u);
        destination_data=b[4]+palette*4u+stride*(height-1u);
        for(uint32_t y=0u;y<height;y++) {
            audio_uart_lv_grid_move_45475a((void *)(uintptr_t)destination_data,(void *)(uintptr_t)source_data,minimal);
            source_data-=(uint16_t)b[2];destination_data-=stride;
        }
    } else {
        source_data=b[4]+palette*4u;destination_data=b[4]+palette*4u;
        for(uint32_t y=0u;y<height;y++) {
            audio_uart_lv_grid_move_45475a((void *)(uintptr_t)destination_data,(void *)(uintptr_t)source_data,minimal);
            source_data+=(uint16_t)b[2];destination_data+=stride;
        }
    }
    b[2]=(b[2]&0xffff0000u)|(uint16_t)stride;
    return 1u;
}
