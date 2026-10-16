/* Apollo audio event dispatch, stock 0x45fd06..0x45fe02. */
#include <stdint.h>

extern uint32_t audio_uart_display_audio_dequeue_45fc5a(void *, void *);
extern uint32_t audio_uart_display_audio_ring_full_45fbd0(const void *);
extern uint32_t audio_uart_display_audio_is_active_45fcb2(void *);
extern void audio_uart_display_audio_queue_45f58c(void *, uint32_t);
extern void audio_uart_display_audio_activate_45f60e(void *, uint32_t);
extern void *audio_uart_display_audio_current_45f8e6(void *);
extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern uint32_t audio_uart_display_audio_complete_45f73a(void *, void *);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

void audio_uart_display_audio_dispatch_45fd06(void *state) {
    if (state == 0) return;
    uint8_t *s = (uint8_t *)state;
    for (;;) {
        uint32_t event[3];
        if (audio_uart_display_audio_dequeue_45fc5a(state, event) == 0u) return;
        if (audio_uart_display_audio_is_active_45fcb2(state) != 0u) {
            uint8_t *ring = s + 36u;
            if (audio_uart_display_audio_ring_full_45fbd0(ring) == 0u) {
                uint8_t index = (uint8_t)((ring[192] + 15u) % 16u);
                ring[192] = index;
                uint8_t *slot = ring + (uint32_t)index * 12u;
                put32(slot, event[0]);
                put32(slot + 4u, event[1]);
                put32(slot + 8u, event[2]);
                ring[194] = (uint8_t)(ring[194] + 1u);
            }
            return;
        }
        uint8_t flagged = (uint8_t)event[2];
        switch (event[0]) {
        case 0x3cu:
            if (flagged != 0u && event[1] != 0u)
                audio_uart_display_audio_queue_45f58c(state, event[1]);
            break;
        case 0x3du:
            if (flagged != 0u && event[1] != 0u) {
                audio_uart_display_audio_activate_45f60e(state, event[1]);
            } else {
                const uint8_t *entry =
                    (const uint8_t *)audio_uart_display_audio_current_45f8e6(state);
                if (entry != 0)
                    audio_uart_display_audio_activate_45f60e(state, get32(entry));
            }
            break;
        case 0x3eu:
            if (flagged != 0u && event[1] != 0u) {
                uint8_t *entry = (uint8_t *)audio_uart_display_audio_find_45f840(
                    state, event[1]);
                if (entry != 0 && entry[11] == 1u)
                    (void)audio_uart_display_audio_complete_45f73a(state, entry);
                else
                    audio_uart_display_audio_queue_45f58c(state, event[1]);
            }
            break;
        default:
            break;
        }
        if (audio_uart_display_audio_is_active_45fcb2(state) != 0u) return;
    }
}
