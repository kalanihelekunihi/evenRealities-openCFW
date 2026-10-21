/* Stock Terminal query layout/publication child at 0x5ebb96. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_query_items_style_5eb3c6(uint32_t);
extern void audio_terminal_status_publish_5e5498(uint32_t, uint32_t);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_query_layout_5ebb96(void) {
    if (word(0x214u) == 0u || word(0x21cu) == 0u || word(0x220u) == 0u)
        return;
    audio_terminal_query_items_style_5eb3c6(
        (uint32_t)(uintptr_t)audio_terminal_ui_state_base);
    audio_terminal_status_publish_5e5498(
        3u, audio_terminal_ui_state_base[0x279u]);
}
