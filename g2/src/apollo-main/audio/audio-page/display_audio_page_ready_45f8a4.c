/* Apollo audio display ready transition, stock 0x45f8a4..0x45f8b8. */
#include <stdint.h>

extern void audio_uart_page_43dfa4(uint32_t page, uint32_t enabled);

void audio_uart_display_audio_ready_45f8a4(void *entry) {
    if (entry == 0) return;
    uint8_t *p = (uint8_t *)entry;
    uint32_t page = (uint32_t)p[4] | ((uint32_t)p[5] << 8u) |
        ((uint32_t)p[6] << 16u) | ((uint32_t)p[7] << 24u);
    audio_uart_page_43dfa4(page, 1u);
    p[28] = 1u;
}
