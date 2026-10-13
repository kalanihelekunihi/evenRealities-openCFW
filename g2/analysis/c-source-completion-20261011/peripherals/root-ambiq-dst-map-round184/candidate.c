#include <stdint.h>
/* Native4b064e..4b06a8; destination formats differ from source map. */
int32_t audio_uart_ambiq_color_format_dst_4b064e(uint32_t format) {
    switch((uint8_t)format) {
    case 6:return 9;
    case 11:return 11;
    case 12:return 49;
    case 13:return 53;
    case 14:return 9;
    case 15:return 57;
    case 16:return 16;
    case 17:return 17;
    case 18:return 4;
    case 21:return 68;
    default:return -1;
    }
}
