/* Apollo audio page selectors 0x45f66a, 0x45f6a8, 0x45f8e6,
 * and active-list test 0x45fcb2. */
#include <stdint.h>

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void *audio_uart_display_audio_handler_b_45f66a(void *page) {
    return page == 0 ? 0 : (void *)(uintptr_t)get32((const uint8_t *)page);
}
void *audio_uart_display_audio_handler_a_45f6a8(void *page) {
    return page == 0 ? 0 :
        (void *)(uintptr_t)get32((const uint8_t *)page + 4u);
}
void *audio_uart_display_audio_current_45f8e6(void *page) {
    if (page == 0) return 0;
    const uint8_t *p = (const uint8_t *)page;
    uint32_t first = get32(p);
    return (void *)(uintptr_t)(first != 0u ? first : get32(p + 4u));
}
uint32_t audio_uart_display_audio_is_active_45fcb2(void *page) {
    if (page == 0) return 0u;
    uint8_t *entry = (uint8_t *)(uintptr_t)get32((const uint8_t *)page + 8u);
    while (entry != 0) {
        if (entry[0x1cu] == 2u) return 1u;
        entry = (uint8_t *)(uintptr_t)get32(entry + 0x20u);
    }
    return 0u;
}
