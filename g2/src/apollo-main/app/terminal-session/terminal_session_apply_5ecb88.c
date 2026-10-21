/* Stock Terminal direct session-list selection application at 0x5ecb88. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_session_count_5eca48(void);
extern void audio_terminal_session_row_style_5ecb08(uint32_t, uint32_t);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

void audio_terminal_session_apply_5ecb88(int32_t index) {
    const int16_t selected = (int16_t)index;
    const uint32_t count = audio_terminal_session_count_5eca48();
    const uint32_t special = word(0x248u);
    if (special != 0u)
        audio_terminal_session_row_style_5ecb08(special, selected == -1);
    for (uint32_t row = 0; row < count; ++row)
        audio_terminal_session_row_style_5ecb08(
            word(0x24cu + row * 4u), selected == (int16_t)row);
    *(int16_t *)(void *)(audio_terminal_ui_state_base + 0x27au) = selected;
}
