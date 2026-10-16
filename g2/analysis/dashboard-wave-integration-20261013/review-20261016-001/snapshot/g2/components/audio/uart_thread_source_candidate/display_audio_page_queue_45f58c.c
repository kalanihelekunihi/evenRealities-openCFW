/* Apollo audio display queue/start, stock 0x45f58c..0x45f60c. */
#include <stdint.h>

extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern void audio_uart_display_audio_ready_45f8a4(void *);
extern void audio_uart_display_audio_schedule_44228a(uint32_t, uint32_t,
                                                       uint32_t, uint32_t);
extern void audio_uart_display_audio_start_45ef24(void *, uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

void audio_uart_display_audio_queue_45f58c(void *state, uint32_t id) {
    if (state == 0 || id == 0u) return;
    uint8_t *s = (uint8_t *)state;
    uint8_t *entry = (uint8_t *)audio_uart_display_audio_find_45f840(state, id);
    if (entry == 0 || entry[28] == 1u) return;
    if (entry[11] == 0u) {
        audio_uart_display_audio_ready_45f8a4(entry);
        if (get32(s) == 0u) put32(s + 4u, (uint32_t)(uintptr_t)entry);
        return;
    }
    uint32_t prior = get32(s + 4u);
    if (prior != 0u) {
        uint32_t callback = get32((const uint8_t *)(uintptr_t)prior + 24u);
        if (callback != 0u) {
            ((void (*)(void *, void *, uint32_t, void *))(uintptr_t)callback)(
                (void *)(uintptr_t)prior, state, 0x42u, entry);
        }
        put32(s + 4u, 0u);
    }
    audio_uart_display_audio_schedule_44228a(get32(entry), 3u, 0u, 0u);
    entry[28] = 2u;
    audio_uart_display_audio_start_45ef24(entry, 1u);
    put32(s, (uint32_t)(uintptr_t)entry);
}
