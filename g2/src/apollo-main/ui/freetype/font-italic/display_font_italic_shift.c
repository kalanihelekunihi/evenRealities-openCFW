/* Native 0x4b201e: glyph bearing adjustment from 0x366a fixed-point slope. */
#include <stdint.h>
int16_t audio_uart_font_italic_shift(uint16_t bearing,uint16_t width) {
    int32_t delta=((int32_t)width*0x366a)>>16;
    return (int16_t)((uint32_t)bearing+(uint32_t)delta);
}
