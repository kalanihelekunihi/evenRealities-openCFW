/* Stock Terminal processing-response action at 0x5e583c. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint8_t audio_terminal_output_style_20003f80[]; /* stock RAM */
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_reset_display_5e4c84(uint32_t enabled);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern uint32_t audio_terminal_set_label_style_5e482a(uint32_t object,
                                                       const void *style,
                                                       uint32_t count,
                                                       uint32_t duration);
extern void audio_uart_page_49942e(uint32_t object, uint32_t text);
extern void audio_terminal_elapsed_refresh_5e4902(void);

static const char thinking_text[] = "Thinking...";
static const char stop_response_text[] = "[Tap & hold to stop response]";

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

int32_t audio_terminal_ui_action_5e583c(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_reset_display_5e4c84(0u);
    if (word(0x1ccu) != 0u && word(0x1d0u) != 0u &&
        word(0x1d4u) != 0u && word(0x1dcu) != 0u) {
        audio_uart_page_43dfa4(word(0x1ccu), 1u);
        audio_terminal_processing_prepare_5ea30c();
        (void)audio_terminal_set_label_style_5e482a(
            word(0x1d0u), audio_terminal_output_style_20003f80, 6u, 0x64u);
        audio_uart_page_49942e(word(0x1d4u),
                                (uint32_t)(uintptr_t)thinking_text);
        audio_uart_page_49942e(word(0x1dcu),
                                (uint32_t)(uintptr_t)stop_response_text);
        audio_terminal_elapsed_refresh_5e4902();
    }
    uint32_t root = word(0u);
    if (root != 0u)
        audio_uart_page_43dfa4(root, 1u);
    return 0;
}
