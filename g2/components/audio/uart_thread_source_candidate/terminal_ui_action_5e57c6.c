/* Stock Terminal return-to-input action at 0x5e57c6. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_reset_display_5e4c84(uint32_t enabled);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(uint32_t object, uint32_t source);
extern void audio_uart_page_49942e(uint32_t object, uint32_t text);
extern void audio_terminal_elapsed_clear_5e4894(void);

static const char waiting_input[] = "Waiting input";
static const char tap_and_hold[] = "[Tap & hold to input]";

static uint32_t state_word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

int32_t audio_terminal_ui_action_5e57c6(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_reset_display_5e4c84(0u);
    if (state_word(0x1ccu) != 0u && state_word(0x1d0u) != 0u &&
        state_word(0x1d4u) != 0u && state_word(0x1dcu) != 0u) {
        audio_uart_page_43dfa4(state_word(0x1ccu), 1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe(
            state_word(0x1d0u),
            (uint32_t)(uintptr_t)&audio_terminal_asset_7733a8);
        audio_uart_page_49942e(state_word(0x1d4u),
                                (uint32_t)(uintptr_t)waiting_input);
        audio_uart_page_49942e(state_word(0x1dcu),
                                (uint32_t)(uintptr_t)tap_and_hold);
        audio_terminal_elapsed_clear_5e4894();
    }
    uint32_t root = state_word(0u);
    if (root != 0u)
        audio_uart_page_43dfa4(root, 1u);
    return 0;
}
