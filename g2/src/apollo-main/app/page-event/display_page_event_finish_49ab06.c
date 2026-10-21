/* Apollo page event text finalization 0x49ab06..0x49ab75. */
#include <stdint.h>

extern void *audio_settings_copy_text(void *destination, const void *source,
                                      uint32_t count);
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

void audio_uart_page_event_finish_49ab06(void *page, int32_t old_offset) {
    uint8_t *p = (uint8_t *)page;
    if (get32(p + 0x34u) != 0xffffffffu) {
        audio_uart_lvgl_log(3u, (const char *)(uintptr_t)0x006e0a7cu,
                           0x4ccu, (const char *)(uintptr_t)0x00780d8cu,
                           (const char *)(uintptr_t)0x00761bf0u,
                           (const char *)(uintptr_t)0x0073fce4u,
                           (const char *)(uintptr_t)0x0077919cu);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    if (old_offset == -1) return;
    uint8_t *buffer = (uint8_t *)(uintptr_t)get32(p + 0x2cu);
    uint8_t *cursor = buffer + (uint32_t)old_offset;
    (void)audio_settings_copy_text(p + 0x30u, cursor, 4u);
    put32(p + 0x34u, (uint32_t)old_offset);
    uint32_t i = 0u;
    while (i < 3u && cursor[i] != 0u) {
        cursor[i] = (uint8_t)'.';
        ++i;
    }
    cursor[i] = 0u;
}
