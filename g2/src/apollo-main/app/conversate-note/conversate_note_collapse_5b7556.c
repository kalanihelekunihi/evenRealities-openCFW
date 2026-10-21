/* Apollo Main Conversate note collapse route, 0x5b7556..0x5b7603. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_terminal_fade_out_58c426(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(uint32_t, uint32_t);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_width_43fd9e(uint32_t);
extern uint32_t audio_uart_lv_obj_height_43fdda(uint32_t);
extern void audio_conversate_expand_animation_5b7704(
    uint32_t, const void *, void (*)(void));
extern uint32_t audio_conversate_note_collapse_complete_5b7518(
    uint32_t, uint32_t, uint32_t, uint32_t);

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}

uint32_t audio_conversate_ui_route_5b7556(uint32_t ignored, uint32_t arg) {
    (void)ignored;
    (void)arg;
    volatile uint8_t *const state = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    uint32_t config[9];
    audio_uart_buffer_zero(config, 0x24u, 0u);
    const uint32_t root = word(state, 0x1cu);
    const uint32_t note = word(state, 0x24u);
    if (root == 0u || note == 0u)
        return UINT32_MAX;
    audio_terminal_fade_out_58c426(note, 200u, 0u);
    const uint32_t expanded = word(state, 0x2cu);
    if (expanded != 0u && audio_uart_lv_obj_has_flag_43e0e0(expanded, 1u) == 0u)
        audio_terminal_fade_out_58c426(expanded, 200u, 0u);
    audio_uart_page_58c238(word(state, 8u), 200u, 0u);
    if (state[0x8du] != 0u)
        audio_uart_page_43dfa4(word(state, 0x20u), 1u);
    config[0] = 300u;
    config[1] = 0u;
    config[2] = 0u;
    config[3] = 0u;
    config[4] = 0u;
    config[5] = 0x240u;
    config[6] = audio_uart_lv_obj_width_43fd9e(word(state, 0x7cu));
    config[7] = 0x120u;
    config[8] = audio_uart_lv_obj_height_43fdda(word(state, 0x7cu));
    audio_conversate_expand_animation_5b7704(
        root, config,
        (void (*)(void))(uintptr_t)audio_conversate_note_collapse_complete_5b7518);
    state[0x98u] = 1u;
    return 0u;
}
