/* Apollo audio event ring predicates/dequeue, stock 0x45fbba..0x45fcb0. */
#include <stdint.h>

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

uint32_t audio_uart_display_audio_ring_empty_45fbba(const void *ring) {
    return ring != 0 && ((const uint8_t *)ring)[194] == 0u ? 1u : 0u;
}

uint32_t audio_uart_display_audio_ring_full_45fbd0(const void *ring) {
    return ring != 0 && ((const uint8_t *)ring)[194] >= 16u ? 1u : 0u;
}

uint32_t audio_uart_display_audio_dequeue_45fc5a(void *state, void *output) {
    if (state == 0 || output == 0) return 0u;
    uint8_t *ring = (uint8_t *)state + 36u;
    if (audio_uart_display_audio_ring_empty_45fbba(ring) != 0u) return 0u;
    uint8_t *slot = ring + (uint32_t)ring[192] * 12u;
    uint8_t *out = (uint8_t *)output;
    put32(out, get32(slot));
    put32(out + 4u, get32(slot + 4u));
    put32(out + 8u, get32(slot + 8u));
    ring[192] = (uint8_t)((ring[192] + 1u) % 16u);
    ring[194] = (uint8_t)(ring[194] - 1u);
    return 1u;
}
