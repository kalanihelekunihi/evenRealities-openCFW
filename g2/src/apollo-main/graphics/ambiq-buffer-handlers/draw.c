/* Apollo Ambiq buffer draw wrapper at 0x4b1b0e. */
#include <stdint.h>

extern void display_driver_nema_float_translate_5228b0(float,float)
    __attribute__((pcs("aapcs-vfp")));
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,uint32_t);

void audio_uart_ambiq_buffer_draw_4b1b0e(
        int32_t x,int32_t y,uint32_t width,uint32_t height,
        int32_t origin_x,int32_t origin_y) {
    display_driver_nema_float_translate_5228b0(
        (float)(int32_t)((uint32_t)x-(uint32_t)origin_x),
        (float)(int32_t)((uint32_t)y-(uint32_t)origin_y));
    display_driver_nema_clear_522ae0((uint32_t)x,(uint32_t)y,width,height);
}
