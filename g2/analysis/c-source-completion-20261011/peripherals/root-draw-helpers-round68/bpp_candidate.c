#include <stdint.h>
/* Native 0x440f44..0x440fc4, locked s200 2.2.6.10 payload.
 * The native UXTB makes the format ABI explicitly byte-valued. */
uint32_t audio_uart_lv_color_bpp_440f44(uint32_t format)
{
    switch ((uint8_t)format) {
    case 7: case 11: return 1;
    case 8: case 12: return 2;
    case 9: case 13: case 48: return 4;
    case 49: case 50: case 51: return 6;
    case 6: case 10: case 14: case 24: return 8;
    case 52: case 53: return 12;
    case 18: case 20: case 21: case 22: case 23: case 38: return 16;
    case 15: case 19: return 24;
    case 16: case 17: return 32;
    default: return 0;
    }
}
