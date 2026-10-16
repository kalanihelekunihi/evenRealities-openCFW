/* Stock Terminal processing state clear 0x5ea30c. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_lv_object_release_44d7b8(uint32_t object);

void audio_terminal_processing_prepare_5ea30c(void) {
    uint32_t *state =
        (uint32_t *)(void *)(audio_terminal_ui_state_base + 0x1e0u);
    if (state[0] != 0u)
        audio_lv_object_release_44d7b8(state[0]);
    for (uint32_t i = 0u; i < 5u; ++i)
        state[i] = 0u;
}
