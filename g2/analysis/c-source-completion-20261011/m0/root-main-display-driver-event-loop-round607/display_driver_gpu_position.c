/* Apollo Ambiq position wrapper 0x4b1b48..0x4b1b83. Candidate. */
#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[1]; /* selected 0x20074efc */
extern void display_driver_nema_float_translate_5228b0(float,float)
    __attribute__((pcs("aapcs-vfp")));
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,uint32_t);
void display_driver_gpu_position_4b1b48(int32_t x,int32_t y) {
    display_driver_nema_float_translate_5228b0((float)x,(float)y);
    volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t width=*(volatile uint32_t *)(void *)(ctx+0x54u);
    uint32_t height=*(volatile uint32_t *)(void *)(ctx+0x58u);
    display_driver_nema_clear_522ae0((uint32_t)x,(uint32_t)y,width,height);
}
