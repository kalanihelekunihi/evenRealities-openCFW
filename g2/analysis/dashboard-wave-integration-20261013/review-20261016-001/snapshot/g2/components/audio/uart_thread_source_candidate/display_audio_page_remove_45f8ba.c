/* Apollo audio display removal, stock range 0x45f8ba..0x45f8ce. */
#include <stdint.h>

extern void audio_uart_page_43ded4(uint32_t page, uint32_t enabled);

void audio_uart_display_audio_remove_45f8ba(void *entry) {
    if (entry == 0) return;
    uint8_t *p = (uint8_t *)entry;
    uint32_t page = (uint32_t)p[4] | ((uint32_t)p[5] << 8u) |
        ((uint32_t)p[6] << 16u) | ((uint32_t)p[7] << 24u);
    audio_uart_page_43ded4(page, 1u);
    p[28] = 0u;
}
