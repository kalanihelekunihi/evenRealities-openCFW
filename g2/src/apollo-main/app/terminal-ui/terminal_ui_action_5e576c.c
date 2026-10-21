/* Stock Terminal FSM action 0x5e576c: request display after BLE event. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_fsm_prepare_5eae94(void);
extern uint8_t audio_ux_get_system_ble_status(void);
extern uint8_t audio_terminal_runtime_event_from_ble(uint8_t ble_status);
extern uint32_t audio_terminal_request_display(uint8_t event, uint32_t value);
extern uint32_t audio_terminal_display_fallback_5ecafa(void);

int32_t audio_terminal_ui_action_5e576c(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_fsm_prepare_5eae94();
    uint8_t event = audio_terminal_runtime_event_from_ble(
        audio_ux_get_system_ble_status());
    if (event == 2u || event == 3u || event == 4u) {
        (void)audio_terminal_request_display(event, 0u);
    } else if (event == 22u) {
        uint32_t session = *(const uint32_t *)(const void *)
            (audio_terminal_ui_state_base + 0x288u);
        (void)audio_terminal_request_display(event, session);
    } else {
        uint32_t fallback = audio_terminal_display_fallback_5ecafa();
        (void)audio_terminal_request_display(27u, fallback);
    }
    return 0;
}
