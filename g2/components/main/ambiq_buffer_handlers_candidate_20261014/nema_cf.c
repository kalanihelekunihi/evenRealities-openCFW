/* Apollo LVGL color format to Nema format at 0x4b05a4..0x4b064c. */
#include <stdint.h>

uint32_t audio_uart_ambiq_nema_cf_4b05a4(uint32_t format) {
    switch (format & 0xffu) {
    case 6u: case 10u: return 9u;
    case 7u: return 11u;
    case 8u: return 49u;
    case 9u: return 53u;
    case 11u: return 12u;
    case 12u: return 48u;
    case 13u: return 52u;
    case 14u: return 8u;
    case 15u: return 57u;
    case 16u: return 16u;
    case 17u: return 17u;
    case 18u: case 20u: return 4u;
    case 21u: return 68u;
    case 48u: return 18u;
    case 49u: return 22u;
    case 50u: return 23u;
    case 52u: return 76u;
    case 53u: return 77u;
    default: return 0xffffffffu;
    }
}
