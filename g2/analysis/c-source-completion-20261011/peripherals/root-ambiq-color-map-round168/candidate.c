#include <stdint.h>
/* Native4b05a4..4b064e; format input truncated tobyte. */
int32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t format) {
    switch((uint8_t)format) {
    case 6u:return 9;
    case 7u:return 11;
    case 8u:return 49;
    case 9u:return 53;
    case 10u:return 9;
    case 11u:return 12;
    case 12u:return 48;
    case 13u:return 52;
    case 14u:return 8;
    case 15u:return 57;
    case 16u:return 16;
    case 17u:return 17;
    case 18u:return 4;
    case 20u:return 4;
    case 21u:return 68;
    case 48u:return 18;
    case 49u:return 22;
    case 50u:return 23;
    case 52u:return 76;
    case 53u:return 77;
    default:return -1;
    }
}
