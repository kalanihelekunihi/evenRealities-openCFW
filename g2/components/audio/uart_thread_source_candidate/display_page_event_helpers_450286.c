/* Apollo event code, extent, and pending text preparation helpers. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                               const char *function, const char *message, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

uint32_t audio_uart_page_event_code_450286(const void *event) {
    return get32((const uint8_t *)event + 8u) & ~0x8000u;
}

void audio_uart_page_event_extent_4519fa(void *event, int32_t value) {
    uint8_t *e = (uint8_t *)event;
    if (get32(e + 8u) == 0x1bu) {
        uint8_t *extent = (uint8_t *)(uintptr_t)get32(e + 0x10u);
        if (value >= (int32_t)get32(extent)) put32(extent, (uint32_t)value);
    } else {
        audio_uart_lvgl_log(2u, (const char *)(uintptr_t)0x006e4010u,
                           0x11cu, (const char *)(uintptr_t)0x0076dcb4u,
                           (const char *)(uintptr_t)0x0074b07cu);
    }
}

void audio_uart_page_event_prepare_49aacc(void *page) {
    uint8_t *p = (uint8_t *)page;
    uint32_t offset = get32(p + 0x34u);
    if (offset == 0xffffffffu) return;
    uint8_t *buffer = (uint8_t *)(uintptr_t)get32(p + 0x2cu);
    for (uint32_t i = 0u; i < 4u; ++i) {
        uint8_t ch = p[0x30u + i];
        if (ch == 0u) break;
        buffer[offset + i] = ch;
    }
    put32(p + 0x34u, 0xffffffffu);
}
