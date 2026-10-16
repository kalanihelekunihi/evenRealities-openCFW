/* Apollo LV hash/space line state, native 0x489652..0x489697. */
#include <stdint.h>

uint32_t audio_uart_text_hash_state_489652(uint8_t *state,
                                            uint32_t glyph) {
    uint32_t result = 0u;
    if (glyph == 0x23u) {
        if (*state == 0u) {
            *state = 1u;
            result = 1u;
        } else if (*state == 2u) {
            *state = 0u;
            result = 1u;
        }
    }
    if (*state == 1u) {
        if (glyph == 0x20u) *state = 2u;
        result = 1u;
    }
    return result;
}
