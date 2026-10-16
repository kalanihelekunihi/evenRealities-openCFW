/* Stock Terminal ancillary reset at 0x5e65f8. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */

void audio_terminal_reset_ancillary_5e65f8(void) {
    uint8_t *state = audio_terminal_ui_state_base;
    *(uint32_t *)(void *)(state + 0x288u) = 0u;
    state[0x277u] = 2u;
    state[0x27fu] = 0u;
}
