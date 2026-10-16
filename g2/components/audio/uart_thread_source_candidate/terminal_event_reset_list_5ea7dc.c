/* Stock Terminal list reset at 0x5ea7dc. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_object_flag_43ded4(uint32_t object, uint32_t flag);

void audio_terminal_event_reset_list_5ea7dc(void) {
    uint8_t *state = audio_terminal_ui_state_base;
    for (uint32_t index = 0; index < 12u; ++index) {
        uint32_t object = *(const uint32_t *)(const void *)(state + 0xcu + index * 4u);
        if (object != 0u)
            audio_lv_object_flag_43ded4(object, 1u);
    }
    *(uint16_t *)(void *)(state + 0x1c0u) = 0u;
    state[0x1c2u] = 0u;
}
