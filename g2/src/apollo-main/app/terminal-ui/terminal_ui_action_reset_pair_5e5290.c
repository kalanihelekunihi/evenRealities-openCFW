/* Stock Terminal FSM reset actions 0x5e5290 and 0x5e5386. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_terminal_reset_first_5e51ba(uint32_t old_state);
extern void audio_terminal_reset_mode_5eae2c(uint32_t mode);
extern void audio_terminal_reset_display_5e4c84(uint32_t enabled);
extern void audio_terminal_reset_subtree_5ea342(void);
extern void audio_lv_object_call_43ded4(uint32_t object, uint32_t value);

static int32_t reset_common(void) {
    audio_terminal_reset_mode_5eae2c(4u);
    audio_terminal_reset_display_5e4c84(1u);
    audio_terminal_reset_subtree_5ea342();
    uint32_t object = *(const uint32_t *)(const void *)
        (audio_terminal_ui_state_base + 0x1ccu);
    if (object != 0u)
        audio_lv_object_call_43ded4(object, 1u);
    return 0;
}

int32_t audio_terminal_ui_action_5e5290(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)event_payload;
    audio_terminal_reset_first_5e51ba((uint8_t)old_state);
    return reset_common();
}

int32_t audio_terminal_ui_action_5e5386(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    return reset_common();
}
