/* Native LV theme refresh across displays and object children. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_display_next_44fa22(void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern void audio_uart_lv_style_removed_44ce2a(void *, uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *, uint32_t, uint32_t);

static uint32_t read32(const uint8_t *p, uint32_t at) {
    return *(const uint32_t *)(const void *)(p + at);
}

void audio_uart_lv_theme_refresh_node_44c970(void *theme, void *object) {
    uint8_t *const node = (uint8_t *)object;
    const uint32_t rows = (*(const uint16_t *)(const void *)(node + 0x2au) & 0x3ffu) >> 4;
    for (uint32_t index = 0; index < rows; ++index) {
        const uint8_t *const row = (const uint8_t *)(uintptr_t)read32(node, 0x0cu) + index * 8u;
        if (theme == 0 || read32(row, 0u) == (uint32_t)(uintptr_t)theme) {
            const uint32_t selector = audio_uart_page_style_selector_44b860(
                read32(row, 4u) & 0x00ffffffu);
            audio_uart_lv_style_removed_44ce2a(object, selector);
            audio_uart_page_style_refresh_44bc8c(object, 0xf0000u, 0xffu);
            break;
        }
    }
    const uint32_t child_count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t index = 0; index < child_count; ++index) {
        const uint8_t *const spec = (const uint8_t *)(uintptr_t)read32(node, 8u);
        const uint8_t *const entries = (const uint8_t *)(uintptr_t)read32(spec, 0u);
        void *const child = (void *)(uintptr_t)read32(entries, index * 4u);
        audio_uart_lv_theme_refresh_node_44c970(theme, child);
    }
}

void audio_uart_lv_theme_refresh_all_44bc48(void *theme) {
    if (audio_uart_display_lv_state[0x24u] == 0u) return;
    uint8_t *display = (uint8_t *)audio_uart_lv_display_next_44fa22(0);
    while (display != 0) {
        const uint32_t count = read32(display, 0x2d4u);
        for (uint32_t index = 0; index < count; ++index) {
            const uint8_t *const roots = (const uint8_t *)(uintptr_t)read32(display, 0x2b8u);
            void *const root = (void *)(uintptr_t)read32(roots, index * 4u);
            audio_uart_lv_theme_refresh_node_44c970(theme, root);
        }
        display = (uint8_t *)audio_uart_lv_display_next_44fa22(display);
    }
}
