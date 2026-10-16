/* Apollo audio event ring enqueue, stock range 0x45fbe6..0x45fc58. */
#include <stdint.h>

extern uint32_t audio_uart_page_event_code_450286(const void *event);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

uint32_t audio_uart_display_audio_gate_event_45fbe6(void *state,
                                                       const void *event) {
    if (state == 0 || event == 0) return 0u;
    uint8_t *ring = (uint8_t *)state + 36u;
    if (ring[194] >= 16u) return 0u;
    uint8_t *slot = ring + (uint32_t)ring[193] * 12u;
    put32(slot, audio_uart_page_event_code_450286(event));
    const uint8_t *e = (const uint8_t *)event;
    uint32_t ptr = get32(e + 16u);
    if (ptr != 0u) {
        put32(slot + 4u, get32((const uint8_t *)(uintptr_t)ptr));
        slot[8] = 1u;
    } else {
        put32(slot + 4u, 0u);
        slot[8] = 0u;
    }
    ring[193] = (uint8_t)((ring[193] + 1u) % 16u);
    ring[194] = (uint8_t)(ring[194] + 1u);
    return 1u;
}
