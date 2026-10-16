/* Apollo LVGL page update dispatch 0x44d5f8..0x44d639. */
#include <stdint.h>

extern void audio_uart_page_update_unbound_44d45c(void *);
extern void audio_uart_page_update_bound_44d4b6(void *);

void audio_uart_page_notify_44d5f8(void *page) {
    uint8_t *const flags = (uint8_t *)page + 0x1cu;
    const uint8_t original = *flags;
    *flags = (uint8_t)(original | 8u);
    if (((*flags & 7u) >> 2u) == 0u)
        audio_uart_page_update_unbound_44d45c(page);
    else
        audio_uart_page_update_bound_44d4b6(page);
    *flags = (uint8_t)((*flags & 0xf7u) | (original & 8u));
}
