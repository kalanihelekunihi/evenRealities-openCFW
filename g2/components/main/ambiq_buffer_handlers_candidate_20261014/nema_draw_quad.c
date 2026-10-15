/* Apollo Nema float quadrilateral command at native 0x522db4. */
#include <stdint.h>
extern int32_t audio_uart_nema_float_fixed_5242cc(float)
    __attribute__((pcs("aapcs-vfp")));
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t);
extern volatile uint32_t audio_uart_nema_context_cell[1];
void audio_uart_nema_draw_quad_522db4(float x0,float y0,float x1,float y1,
                                      float x2,float y2,float x3,float y3)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_draw_quad_522db4(float x0,float y0,float x1,float y1,
                                      float x2,float y2,float x3,float y3) {
    const float values[8]={x0,y0,x1,y1,x2,y2,x3,y3};
    int32_t fixed[8];
    for(uint32_t i=0u;i<8u;i++)
        fixed[i]=audio_uart_nema_float_fixed_5242cc(values[i]);
    uint32_t *command=audio_uart_nema_cl_get_space_514aec(9u);
    if(command==0) return;
    static const uint16_t addresses[8]={0x120u,0x124u,0x130u,0x134u,
                                        0x140u,0x144u,0x150u,0x154u};
    for(uint32_t i=0u;i<8u;i++) {
        command[i*2u]=addresses[i];
        command[i*2u+1u]=(uint32_t)fixed[i];
    }
    command[16]=0xff000100u;
    volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    command[17]=*(volatile uint32_t *)(void *)(ctx+0x18u)|5u;
}
