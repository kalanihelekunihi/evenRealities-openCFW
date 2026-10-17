/* Native ASCII locale callbacks at 0x4d4384 and 0x4d4398.
 * Arguments are full 32-bit values; arithmetic follows native unsigned tests. */
#include <stdint.h>

uint32_t audio_uart_locale_ascii_space_4d4384(uint32_t value) {
    if ((value - 9u) < 5u || value == 0x20u)
        return 1u;
    return 0u;
}

uint32_t audio_uart_locale_ascii_lower_4d4398(uint32_t value) {
    if ((value - 0x41u) < 0x1au)
        return value + 0x20u;
    return value;
}
