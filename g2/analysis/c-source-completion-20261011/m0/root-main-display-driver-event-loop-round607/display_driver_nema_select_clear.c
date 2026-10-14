/* Apollo NEMA select 0x522a16 and clear 0x522ae0. Candidate. */
#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t); /* selected */
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t); /* selected */
extern volatile uint32_t audio_uart_nema_context_cell[1]; /* selected 0x20074efc */
void display_driver_nema_select_522a16(uint32_t unit) {
    audio_uart_nema_child_514846(0x12cu,unit);
}
void display_driver_nema_clear_522ae0(uint32_t x,uint32_t y,uint32_t width,
                                      uint32_t height) {
    if((int32_t)width<1 || (int32_t)height<1) return;
    uint32_t *command=audio_uart_nema_cl_get_space_514aec(3u);
    if(command==0) return;
    command[0]=0x104u;
    command[1]=(x&0xffffu)|((y&0xffffu)<<16);
    command[2]=0x108u;
    command[3]=((x+width)&0xffffu)|(((y+height)&0xffffu)<<16);
    command[4]=0xff000100u;
    volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    command[5]=*(volatile uint32_t *)(void *)(ctx+0x18u)|2u;
}
