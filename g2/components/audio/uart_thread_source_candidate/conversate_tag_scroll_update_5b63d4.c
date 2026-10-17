/* Native Conversate tag selection scroll helper, 0x5b63d4..0x5b6425. */
#include <stdint.h>

extern int32_t audio_conversate_tag_visible_index_5b0b58(void);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(uint32_t, uint32_t);

static uint32_t word(const volatile uint8_t *p, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(p + offset);
}
static void put_word(volatile uint8_t *p, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(p + offset) = value;
}

void audio_conversate_tag_scroll_update_5b63d4(volatile uint8_t *ui) {
    const int32_t visible_index = audio_conversate_tag_visible_index_5b0b58();
    uint32_t index = word(ui, 0x84u);
    if (index != UINT32_MAX) {
        ++index;
        put_word(ui, 0x84u, index);
    }
    const uint32_t selected = word(ui, 0x80u);
    if (visible_index >= 0 && selected != 0u) {
        const uint32_t delta = index - (uint32_t)visible_index;
        audio_terminal_display_status_44ea04(word(ui, 0x64u),
                                            delta * 0x28u, 0u);
    } else if (selected != 0u) {
        audio_terminal_ui_scroll_to_view_44ea2e(selected, 0u);
    }
}
