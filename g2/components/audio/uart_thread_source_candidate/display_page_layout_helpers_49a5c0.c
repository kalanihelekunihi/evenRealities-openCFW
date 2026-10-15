/* Apollo page layout helpers, native 0x49a5c0..0x49a601 and 0x49abea..0x49ac49. */
#include <stdint.h>

extern int32_t audio_uart_page_metric_499360(void *page, uint32_t selector);
extern int32_t audio_uart_page_metric_49936a(void *page, uint32_t selector);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

void audio_uart_page_layout_copy_anim_49a5c0(void *destination,
                                               const void *source,
                                               uint32_t mode) {
    uint8_t *dst = (uint8_t *)destination;
    const uint8_t *src = (const uint8_t *)source;
    if (mode != 2u && mode != 3u) return;
    if ((int32_t)get32(dst + 0x34u) < 1)
        put32(dst + 0x34u, get32(src + 0x34u));
    put32(dst + 0x44u, get32(src + 0x44u));
    put32(dst + 0x40u, get32(src + 0x40u));
    put32(dst + 0x10u, get32(src + 0x10u));
    if (mode == 2u) put32(dst + 0x38u, get32(src + 0x38u));
}

uint64_t audio_uart_page_layout_flags_49abea(void *page,
                                               uint32_t unused1,
                                               uint32_t unused2,
                                               uint32_t high) {
    (void)unused1; (void)unused2;
    const uint8_t *p = (const uint8_t *)page;
    uint32_t flags = (p[0x5cu] & 0x20u) != 0u ? 8u : 0u;
    if ((p[0x5cu] & 0x40u) != 0u) flags |= 1u;
    if (audio_uart_page_metric_499360(page, 0u) == 0x3fffffff &&
        audio_uart_page_metric_49936a(page, 0u) == 0x1fffffff &&
        (p[0x2bu] & 8u) == 0u)
        flags |= 2u;
    return ((uint64_t)high << 32u) | flags;
}
