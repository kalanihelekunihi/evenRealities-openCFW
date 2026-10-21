/* Native ASCII classification leaves at 0x4d4368, 0x4d436c, 0x4d436e. */
#include <stdint.h>

uint32_t audio_uart_locale_ascii_lowercase_4d4368(uint32_t value) {
    return (value - 0x61u) < 0x1au;
}

uint32_t audio_uart_locale_ascii_uppercase_4d436c(uint32_t value) {
    return (value - 0x41u) < 0x1au;
}

uint32_t audio_uart_locale_ascii_alpha_4d436e(uint32_t value) {
    if ((value - 0x61u) < 0x1au)
        return 1u;
    return (value - 0x41u) < 0x1au;
}
