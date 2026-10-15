/* Apollo terminal candidate-session selector, native 0x5e505a. */
#include <stdint.h>
extern uint8_t *audio_td_active_records_ptr(void);
extern uint32_t audio_terminal_runtime_saved_session;
extern uint32_t audio_td_counter_b_get(void);
extern uint8_t audio_td_record_status_for_session(uint32_t);
extern uint8_t audio_td_session_marked(uint32_t);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_candidate_session_for_runtime(void) {
    uint8_t *records=audio_td_active_records_ptr();
    uint32_t saved=audio_terminal_runtime_saved_session;
    uint32_t current=audio_td_counter_b_get();
    if(saved!=0u && audio_td_record_status_for_session(saved)==2u &&
       audio_td_session_marked(saved)==0u) return saved;
    if(current!=0u && audio_td_record_status_for_session(current)==2u &&
       audio_td_session_marked(current)==0u) return current;
    if(records==0) return 0u;
    uint32_t count=load_u32(records+8u);
    for(uint32_t i=0;i<count;++i) {
        const uint8_t *row=records+i*0x90u;
        if(row[0x122u]!=2u) continue;
        uint32_t session=load_u32(row+0x9cu);
        if(audio_td_session_marked(session)==0u) return session;
    }
    return 0u;
}
