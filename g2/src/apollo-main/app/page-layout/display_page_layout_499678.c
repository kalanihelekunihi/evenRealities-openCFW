/* Apollo page layout mode 0x499678..0x499715 and registered field setters
 * 0x49abbc..0x49abd3. The full layout update remains a lower import. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_unlink_450500(void *page, void *setter);
extern void audio_uart_page_layout_update_49a602(void *page);
extern void audio_uart_display_size_changed(void *page);
extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                               const char *function, const char *message, ...);

void audio_uart_page_width_setter_49abbc(void *page, uint32_t value) {
    uint8_t *p = (uint8_t *)page;
    p[0x54u] = (uint8_t)value;
    p[0x55u] = (uint8_t)(value >> 8u);
    p[0x56u] = (uint8_t)(value >> 16u);
    p[0x57u] = (uint8_t)(value >> 24u);
    audio_uart_display_size_changed(page);
}

void audio_uart_page_height_setter_49abc8(void *page, uint32_t value) {
    uint8_t *p = (uint8_t *)page;
    p[0x58u] = (uint8_t)value;
    p[0x59u] = (uint8_t)(value >> 8u);
    p[0x5au] = (uint8_t)(value >> 16u);
    p[0x5bu] = (uint8_t)(value >> 24u);
    audio_uart_display_size_changed(page);
}

void *audio_uart_page_layout_499678(void *page, uint32_t mode) {
    if (page == 0) {
        audio_uart_lvgl_log(3u, (const char *)(uintptr_t)0x006e0a7cu,
                           0xdfu, (const char *)(uintptr_t)0x00779124u,
                           (const char *)(uintptr_t)0x00761bf0u,
                           (const char *)(uintptr_t)0x0078b39cu,
                           (const char *)(uintptr_t)0x00787550u);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    uint8_t *p = (uint8_t *)page;
    (void)audio_uart_lv_style_unlink_450500(page,
            (void *)(uintptr_t)&audio_uart_page_width_setter_49abbc);
    (void)audio_uart_lv_style_unlink_450500(page,
            (void *)(uintptr_t)&audio_uart_page_height_setter_49abc8);
    for (uint32_t i = 0u; i < 8u; ++i) p[0x54u+i] = 0u;
    if ((uint8_t)mode == 2u || (uint8_t)mode == 3u || (uint8_t)mode == 4u)
        p[0x5cu] |= 0x40u;
    else
        p[0x5cu] &= 0xbfu;
    p[0x5cu] = (uint8_t)((p[0x5cu] & 0xf0u) | ((uint8_t)mode & 0x0fu));
    audio_uart_page_layout_update_49a602(page);
    return page;
}
