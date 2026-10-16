/* Stock Terminal FSM query-dismiss action 0x5e68b4. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void audio_td_dismiss_query_notification(uint32_t session);
extern int32_t audio_terminal_ui_restore_query_5e6620(uint32_t old_state);

int32_t audio_terminal_ui_action_5e68b4(uint32_t old_state,
                                         uint32_t event_payload) {
    if (event_payload != 1u) {
        uint32_t session = *(const uint32_t *)(const void *)
            (audio_terminal_ui_state_base + 0x288u);
        audio_td_dismiss_query_notification(session);
    }
    return audio_terminal_ui_restore_query_5e6620((uint8_t)old_state);
}
