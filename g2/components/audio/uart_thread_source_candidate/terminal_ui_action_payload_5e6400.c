/* Stock Terminal FSM payload actions 0x5e6400 and 0x5e6410. */
#include <stdint.h>

extern void audio_terminal_control_flags_5e4a6e(uint32_t low_nibble,
                                                 uint32_t high_bits);
extern void audio_terminal_elapsed_text_5e48b8(uint32_t seconds);

int32_t audio_terminal_ui_action_5e6400(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    audio_terminal_control_flags_5e4a6e(event_payload & 0xfu,
                                         event_payload >> 4);
    return 0;
}

int32_t audio_terminal_ui_action_5e6410(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    audio_terminal_elapsed_text_5e48b8(event_payload);
    return 0;
}
