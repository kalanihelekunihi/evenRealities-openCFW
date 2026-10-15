/* Apollo Nema texture-color command at native 0x4b146c. */
#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
void audio_uart_ambiq_texture_color_4b146c(uint32_t color) {
    audio_uart_nema_child_514846(0x1cu,color);
}
