/* Apollo main 0x4e304c, EvenAI heartbeat timer start.
 * State cell 0x20074014 and final RAM placement remain separate providers.
 */
#include <stdint.h>

extern uint32_t audio_settings_device_role(void); /* stock 0x45a568 */
extern uint32_t g2_flashdb_candidate_tick(void);  /* stock 0x4490cc */
extern uint8_t audio_even_ai_heartbeat_state_20074014[10];

void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t timeout) {
    if ((audio_settings_device_role() & 0xffu) != 1u)
        return;
    uint8_t *state = audio_even_ai_heartbeat_state_20074014;
    uint32_t tick = g2_flashdb_candidate_tick();
    for (unsigned i = 0; i < 4; ++i) {
        state[i] = (uint8_t)(tick >> (8u * i));
        state[i + 4] = (uint8_t)(timeout >> (8u * i));
    }
    state[8] = 1u;
    state[9] = 1u;
}
