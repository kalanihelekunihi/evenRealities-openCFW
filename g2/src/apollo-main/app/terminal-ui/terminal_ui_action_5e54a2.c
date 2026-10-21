/* Stock Terminal FSM event-34 action at 0x5e54a2. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint8_t audio_ux_get_system_ble_status(void);
extern uint8_t audio_terminal_runtime_event_from_ble(uint8_t ble_status);
extern int32_t audio_terminal_ui_action_5e583c(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e522e(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e5290(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e52c2(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e6548(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e641c(uint32_t, uint32_t);
extern int32_t audio_terminal_ui_action_5e57c6(uint32_t, uint32_t);

int32_t audio_terminal_ui_action_5e54a2(uint32_t old_state,
                                         uint32_t event_payload) {
    uint32_t old_byte = (uint8_t)old_state;
    if ((uint8_t)event_payload == 1u || (uint8_t)event_payload == 2u) {
        (void)audio_terminal_ui_action_5e583c(old_byte, 0u);
        return 8;
    }
    uint8_t event = audio_terminal_runtime_event_from_ble(
        audio_ux_get_system_ble_status());
    if (event == 2u) {
        (void)audio_terminal_ui_action_5e522e(old_byte, event_payload);
        return 4;
    }
    if (event == 3u) {
        (void)audio_terminal_ui_action_5e5290(old_byte, event_payload);
        return 4;
    }
    if (event == 4u) {
        (void)audio_terminal_ui_action_5e52c2(old_byte, event_payload);
        return 4;
    }
    if (event == 22u) {
        uint32_t session = *(const uint32_t *)(const void *)
            (audio_terminal_ui_state_base + 0x288u);
        (void)audio_terminal_ui_action_5e6548(old_byte, session);
        return 11;
    }
    if (event == 7u) {
        (void)audio_terminal_ui_action_5e641c(old_byte, 1u);
        return 10;
    }
    (void)audio_terminal_ui_action_5e57c6(old_byte, event_payload);
    return 3;
}
