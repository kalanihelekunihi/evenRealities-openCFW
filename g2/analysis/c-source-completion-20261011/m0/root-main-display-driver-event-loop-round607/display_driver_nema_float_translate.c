/* Apollo NEMA float translation 0x5228b0..0x522915. Candidate. */
#include <stdint.h>
extern void *audio_uart_nema_cl_get_space_514aec(uint32_t); /* selected */
extern void audio_uart_nema_child_514846(uint32_t,uint32_t); /* selected */
static uint32_t bits(float value) {
    union { float f; uint32_t u; } word={.f=value};
    return word.u;
}
void display_driver_nema_float_translate_5228b0(float x,float y)
    __attribute__((pcs("aapcs-vfp")));
void display_driver_nema_float_translate_5228b0(float x,float y) {
    float nx=-x,ny=-y;
    uint32_t *command=audio_uart_nema_cl_get_space_514aec(2u);
    if(command==0) return;
    command[0]=0x174u;
    command[1]=bits(ny);
    command[2]=0x168u;
    command[3]=bits(nx);
    if(nx < -2048.0f || ny < -2048.0f)
        audio_uart_nema_child_514846(0x118u,0x80000000u);
}
