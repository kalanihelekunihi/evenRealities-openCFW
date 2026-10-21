/* Apollo Ambiq byte color pack at 0x4b15a6 and resolver at 0x4b06a8. */
#include <stdint.h>

uint32_t audio_uart_ambiq_color_pack_4b15a6(uint32_t blue,uint32_t green,
                                              uint32_t red,uint32_t alpha) {
    return blue | (green<<8) | (red<<16) | (alpha<<24);
}

uint32_t audio_uart_ambiq_color_resolve_4b06a8(uint32_t color,
                                                 uint32_t alpha) {
    return audio_uart_ambiq_color_pack_4b15a6(
        (color>>16)&0xffu,(color>>8)&0xffu,color&0xffu,alpha&0xffu);
}
