/* Apollo audio display priority guard, stock range 0x45f706..0x45f738. */
#include <stdint.h>

uint32_t audio_uart_display_audio_priority_45f706(const void *state,
                                                    const void *entry) {
    if (state == 0 || entry == 0) return 0u;
    const uint8_t *s = (const uint8_t *)state;
    const uint8_t *e = (const uint8_t *)entry;
    if (e[11] != 1u) return 1u;
    uint32_t current = (uint32_t)s[0] | ((uint32_t)s[1] << 8u) |
        ((uint32_t)s[2] << 16u) | ((uint32_t)s[3] << 24u);
    if (current == 0u) return 1u;
    return e[22] >= ((const uint8_t *)(uintptr_t)current)[22] ? 1u : 0u;
}
