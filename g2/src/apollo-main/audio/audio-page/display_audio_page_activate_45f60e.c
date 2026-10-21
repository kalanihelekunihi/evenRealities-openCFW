/* Apollo page audio activation/stop transition 0x45f60e..0x45f668. */
#include <stdint.h>

extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern void audio_uart_display_audio_remove_45f8ba(void *);
extern void audio_uart_display_audio_start_45ef24(void *, uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

void audio_uart_display_audio_activate_45f60e(void *state, uint32_t id) {
    if (state == 0 || id == 0u) return;
    uint8_t *s = (uint8_t *)state;
    uint8_t *entry = (uint8_t *)audio_uart_display_audio_find_45f840(state, id);
    if (entry == 0 || entry[0x1cu] != 1u) return;
    if (entry[11u] == 0u) {
        audio_uart_display_audio_remove_45f8ba(entry);
        if (get32(s + 4u) == (uint32_t)(uintptr_t)entry) put32(s + 4u, 0u);
        return;
    }
    entry[0x1cu] = 2u;
    audio_uart_display_audio_start_45ef24(entry, 0u);
    if (get32(s) == (uint32_t)(uintptr_t)entry && s[20u] == 0u) {
        put32(s, 0u);
        put32(s + 4u, get32(s + 12u));
    }
}
