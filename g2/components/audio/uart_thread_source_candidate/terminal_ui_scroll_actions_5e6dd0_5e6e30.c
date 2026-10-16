/* Stock paired Terminal FSM scroll actions 0x5e6dd0 and 0x5e6e30. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_notify_status_5ec190(void);
extern void audio_terminal_display_status_44ea04(uint32_t object,
                                                 uint32_t target,
                                                 uint32_t animation);

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

static int32_t scroll_action(uint32_t event_payload) {
    uint32_t object = word(0x1f4u);
    if (object == 0u)
        return 0;
    uint32_t position = (uint16_t)event_payload;
    uint32_t should_scroll = (event_payload >> 31) & 1u;
    uint8_t old_status = audio_terminal_ui_state_base[0x278u];
    uint8_t status = (event_payload & (1u << 28)) ? 2u :
                     (event_payload & (1u << 29)) ? 1u :
                     (event_payload & (1u << 30)) ? 0u : old_status;
    if (status != old_status) {
        audio_terminal_ui_state_base[0x278u] = status;
        audio_terminal_notify_status_5ec190();
    }
    if (should_scroll != 0u)
        audio_terminal_display_status_44ea04(object, position, 1u);
    return 0;
}

int32_t audio_terminal_ui_action_5e6dd0(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    return scroll_action(event_payload);
}

int32_t audio_terminal_ui_action_5e6e30(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    return scroll_action(event_payload);
}
