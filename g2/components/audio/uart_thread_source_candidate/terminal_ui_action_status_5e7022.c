/* Stock Terminal FSM status action 0x5e7022 and payload helpers. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_display_status_44ea04(uint32_t object,
                                                  uint32_t value,
                                                  uint32_t enabled);

uint32_t audio_terminal_status_low_5e4f10(uint32_t payload) {
    return (uint16_t)payload;
}

uint32_t audio_terminal_status_high_5e4f14(uint32_t payload) {
    return payload >> 31;
}

int32_t audio_terminal_ui_action_5e7022(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    uint32_t object = *(const uint32_t *)(const void *)
        (audio_terminal_ui_state_base + 4u);
    if (object == 0u)
        return 0;
    uint32_t value = audio_terminal_status_low_5e4f10(event_payload);
    audio_terminal_ui_state_base[0x28cu] =
        (uint8_t)audio_terminal_status_high_5e4f14(event_payload);
    audio_terminal_display_status_44ea04(object, value, 1u);
    return 0;
}
