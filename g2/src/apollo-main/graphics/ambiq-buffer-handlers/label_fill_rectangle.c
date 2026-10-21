/* Apollo Ambiq label fill rectangle at native 0x4b1ab0. */
#include <stdint.h>
extern void display_driver_nema_select_522a16(uint32_t);
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,
                                             uint32_t);
void audio_uart_ambiq_label_fill_rectangle_4b1ab0(uint32_t x,uint32_t y,
                                                      uint32_t width,uint32_t height,
                                                      uint32_t color) {
    display_driver_nema_select_522a16(color);
    display_driver_nema_clear_522ae0(x,y,width,height);
}
