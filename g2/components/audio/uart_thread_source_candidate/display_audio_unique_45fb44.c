/* Audio entry absence check, stock Apollo Main 0x45fb44..0x45fb7a. */
#include <stdint.h>

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

uint32_t audio_uart_display_audio_unique_45fb44(void *state, uint32_t id) {
    if (state == 0 || id == 0u) return 0u;
    uint8_t *s = (uint8_t *)state;
    uint8_t *node = (uint8_t *)(uintptr_t)get32(s + 8u);
    while (node != 0) {
        if (get32(node) == id) return 0u;
        node = (uint8_t *)(uintptr_t)get32(node + 32u);
    }
    node = (uint8_t *)(uintptr_t)get32(s + 12u);
    while (node != 0) {
        if (get32(node) == id) return 0u;
        node = (uint8_t *)(uintptr_t)get32(node + 32u);
    }
    return 1u;
}
