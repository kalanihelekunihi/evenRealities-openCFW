/* Apollo audio display completion/selection, stock 0x45f73a..0x45f7bc. */
#include <stdint.h>

extern uint32_t audio_uart_display_audio_priority_45f706(const void *, const void *);
extern void audio_uart_display_audio_queue_45f58c(void *, uint32_t);
extern void audio_uart_display_audio_activate_45f60e(void *, uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

uint32_t audio_uart_display_audio_complete_45f73a(void *state, void *entry) {
    if (state == 0 || entry == 0) return 0u;
    uint8_t *s = (uint8_t *)state;
    uint8_t *e = (uint8_t *)entry;
    if (e[11] != 1u) return 0u;
    if (audio_uart_display_audio_priority_45f706(state, entry) == 0u) return 0u;
    if (s[20] != 0u) {
        uint32_t pending = get32(s + 16u);
        if (pending == 0u || ((const uint8_t *)(uintptr_t)pending)[22] < e[22])
            put32(s + 16u, (uint32_t)(uintptr_t)entry);
        return 1u;
    }
    uint32_t current = get32(s);
    if (current == 0u) {
        audio_uart_display_audio_queue_45f58c(state, get32(e));
        return 1u;
    }
    if (current == (uint32_t)(uintptr_t)entry) return 1u;
    s[20] = 1u;
    put32(s + 16u, (uint32_t)(uintptr_t)entry);
    audio_uart_display_audio_activate_45f60e(state, get32((const uint8_t *)(uintptr_t)current));
    return 1u;
}
