/* Apollo page class context-bit lookup 0x44d1cc..0x44d1fb. */
#include <stdint.h>

uint32_t audio_uart_page_needs_context_44d1cc(const void *page) {
    const uint8_t *descriptor = *(const uint8_t *const *)page;
    while (descriptor != 0) {
        const uint32_t flags = *(const uint32_t *)(const void *)(descriptor + 32u);
        const uint32_t kind = (flags & 0x0fu) >> 2u;
        if (kind != 0u)
            return kind == 1u;
        descriptor = *(const uint8_t *const *)(const void *)descriptor;
    }
    return 0u;
}
