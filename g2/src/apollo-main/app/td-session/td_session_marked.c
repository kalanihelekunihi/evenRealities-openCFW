/* Apollo marked-session predicate, native 0x597544. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];
extern uint32_t audio_td_find_record_index(uint32_t,uint32_t *);

/* Stock 0x597544 (td_record_in_use_get) */
uint8_t audio_td_session_marked(uint32_t session) {
    uint32_t index=0u;
    if(audio_td_find_record_index(session,&index)==0u) return 0u;
    return audio_td_state[0x9688u+index*0x90u]!=0u ? 1u : 0u;
}
