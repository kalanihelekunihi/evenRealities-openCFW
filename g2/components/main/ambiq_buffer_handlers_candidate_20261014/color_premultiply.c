/* Apollo alpha premultiplication at 0x4b15b4..0x4b1604. */
#include <stdint.h>

uint32_t audio_uart_ambiq_color_premultiply_4b15b4(uint32_t argb) {
    const uint32_t alpha=argb>>24;
    const uint32_t red=(argb>>16)&0xffu;
    const uint32_t green=(argb>>8)&0xffu;
    const uint32_t blue=argb&0xffu;
    return (alpha<<24) |
           (((alpha*red)/255u)<<16) |
           (((alpha*green)/255u)<<8) |
           ((alpha*blue)/255u);
}
