/* Apollo page text pointer, native 0x4997f8..0x49982f. */
#include <stdint.h>

uint32_t audio_uart_page_text_pointer_4997f8(const void *page) {
    if (page == 0) __builtin_trap();
    const uint8_t *p = (const uint8_t *)page + 0x2cu;
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
