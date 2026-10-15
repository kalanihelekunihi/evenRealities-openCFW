/* Apollo Ambiq mask texture position at 0x4b1ad4..0x4b1b0c. */
#include <stdint.h>

extern void audio_uart_nema_float_position_5228b0(float,float)
    __attribute__((pcs("aapcs-vfp")));
extern uint32_t audio_uart_nema_mask_rectangle_522ae0(int32_t,int32_t,
                                                        int32_t,int32_t);

uint32_t audio_uart_ambiq_mask_position_4b1ad4(int32_t x,int32_t y,
                                                 int32_t width,int32_t height) {
    audio_uart_nema_float_position_5228b0((float)x,(float)y);
    return audio_uart_nema_mask_rectangle_522ae0(x,y,width,height);
}
