/* Audio route-to-queue helper, stock Apollo Main 0x45f876..0x45f8a2. */
#include <stdint.h>

extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern void audio_uart_display_audio_queue_45f58c(void *, uint32_t);

uint32_t audio_uart_display_audio_route_45f876(void *state, uint32_t id) {
    if (state == 0 || id == 0u) return 0u;
    if (audio_uart_display_audio_find_45f840(state, id) == 0) return 0u;
    audio_uart_display_audio_queue_45f58c(state, id);
    return 1u;
}
