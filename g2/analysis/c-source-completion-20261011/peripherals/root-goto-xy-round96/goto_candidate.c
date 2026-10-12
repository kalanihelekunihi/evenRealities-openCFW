#include <stdint.h>
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native48b2aa..48b34e; address arithmetic wraps in 32 bits. */
void *audio_uart_lv_draw_buf_goto_xy_48b2aa(const void *buffer,uint32_t x,uint32_t y)
{
    const volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,433u,"lv_draw_buf_goto_xy","Asserted at expression: %s (%s)","buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0) return 0;
    uint32_t data=b[4],palette;
    if((uint8_t)(b[0]>>8u)==7u) palette=2u;
    else if((uint8_t)(b[0]>>8u)==8u) palette=4u;
    else if((uint8_t)(b[0]>>8u)==9u) palette=16u;
    else if((uint8_t)(b[0]>>8u)==10u) palette=256u;
    else palette=0u;
    uint32_t address=data+palette*4u+y*(uint16_t)b[2];
    if(x!=0u) address+=(x*audio_uart_lv_color_bpp_440f44((uint8_t)(b[0]>>8u)))>>3u;
    return (void *)(uintptr_t)address;
}
