/* Stock Terminal disconnect actions at 0x5e522e, 0x5e52c2, 0x5e5320 and 0x5e53b8. */
#include <stdint.h>
#include "terminal_fsm_disconnect_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_reset_first_5e51ba(uint32_t old_state);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_reset_display_5e4c84(uint32_t enabled);
extern void audio_uart_page_43dfa4(uint32_t object, uint32_t flag);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(uint32_t object, uint32_t source);
extern void audio_uart_page_49942e(uint32_t object, uint32_t text);
extern void audio_terminal_elapsed_clear_5e4894(void);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

static int32_t display_disconnect(uint32_t first_text, uint32_t second_text,
                                  uint32_t prepare_processing) {
    if (word(0x1ccu) == 0u || word(0x1d0u) == 0u ||
        word(0x1d4u) == 0u || word(0x1dcu) == 0u)
        return 0;
    audio_uart_page_43dfa4(word(0x1ccu), 1u);
    if (prepare_processing != 0u)
        audio_terminal_processing_prepare_5ea30c();
    audio_terminal_image_set_5e47fe(
        word(0x1d0u), (uint32_t)(uintptr_t)&audio_terminal_asset_77300c);
    audio_uart_page_49942e(word(0x1d4u), first_text);
    audio_uart_page_49942e(word(0x1dcu), second_text);
    audio_terminal_elapsed_clear_5e4894();
    return 0;
}

int32_t audio_terminal_ui_action_5e522e(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_first_5e51ba((uint8_t)old_state);
    return display_disconnect(
        (uint32_t)(uintptr_t)audio_terminal_bluetooth_disconnected_77c9dc,
        (uint32_t)(uintptr_t)audio_terminal_empty_5e5550, 1u);
}

int32_t audio_terminal_ui_action_5e52c2(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_first_5e51ba((uint8_t)old_state);
    return display_disconnect(
        (uint32_t)(uintptr_t)audio_terminal_lost_full_739944,
        (uint32_t)(uintptr_t)audio_terminal_empty_5e5550, 0u);
}

int32_t audio_terminal_ui_action_5e5320(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_reset_display_5e4c84(0u);
    return display_disconnect(
        (uint32_t)(uintptr_t)audio_terminal_bluetooth_disconnected_77c9dc,
        (uint32_t)(uintptr_t)audio_terminal_empty_5e5550, 1u);
}

int32_t audio_terminal_ui_action_5e53b8(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_reset_display_5e4c84(0u);
    return display_disconnect(
        (uint32_t)(uintptr_t)audio_terminal_lost_short_77c9f4,
        (uint32_t)(uintptr_t)audio_terminal_check_app_77ca0c, 0u);
}
