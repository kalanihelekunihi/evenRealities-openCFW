/* Apollo terminal runtime-event mapper, native 0x5e50ea. */
#include <stdint.h>

extern uint8_t *audio_td_state_ptr_alias1(void);
extern uint8_t *audio_td_session_struct_ptr(void);
extern uint32_t audio_terminal_candidate_session_for_runtime(void);
extern uint8_t audio_td_record_status_read(void);
extern uint32_t audio_terminal_runtime_saved_session;

/* Stock 0x5E50EA (terminal_runtime_event_from_ble) */
uint8_t audio_terminal_runtime_event_from_ble(uint8_t ble_status) {
    uint8_t *state=audio_td_state_ptr_alias1();
    uint8_t *session=audio_td_session_struct_ptr();
    if(ble_status==0u) return 2u;
    uint8_t host=state[0xa1d8u];
    if(host==1u) return 4u;
    if(host!=2u) return 3u;
    if(session!=0 && (session[0x406u]!=0u || session[0x407u]!=0u)) return 7u;
    uint32_t selected=audio_terminal_candidate_session_for_runtime();
    if(selected!=0u) {
        audio_terminal_runtime_saved_session=selected;
        return 22u;
    }
    uint8_t status=audio_td_record_status_read();
    return (status==1u || status==2u) ? 6u : 5u;
}
